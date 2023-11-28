import unittest
import sys
import os
import tempfile
from io import StringIO
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
import time
from aminer.util import PersistenceUtil
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.analysis.NewMatchPathValueComboDetector import NewMatchPathValueComboDetector
from aminer.util import SecureOSFunctions
from unit.TestBase import TestBase


class PersistenceUtilTest(TestBase):
    """Unittests for the PersistenceUtil class."""

    def test1add_persistable_component(self):
        """
        Add a component to the registry of all persistable components.
        Also test the type of the component, as this task is only performed once for each component.
        """
        old_stderr = sys.stderr
        sys.stderr = StringIO()

        # component is not PersistableComponentInterface (raise TypeError)
        some_object = {"key": "this is not working"}
        self.assertRaises(TypeError, PersistenceUtil.add_persistable_component(some_object))

        # working example - the component is added implicitly.
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Test", True)

        # check persistence ID warning
        PersistenceUtil.SKIP_PERSISTENCE_ID_WARNING = False
        PersistenceUtil.add_persistable_component(nmpd)
        self.assertEqual(sys.stderr.getvalue(), 'Warning: Detectors of type NewMatchPathDetector use the persistence_id "Test" multiple'
            ' times. Please assign a unique persistence_id for every component.\n')
        self.reset_output_stream()
        PersistenceUtil.SKIP_PERSISTENCE_ID_WARNING = True
        PersistenceUtil.add_persistable_component(nmpd)
        self.assertEqual(self.output_stream.getvalue(), "")
        sys.stderr = old_stderr

    def test2open_persistence_file(self):
        """Test opening a persistence file. Also check if the type of the file_name is string or bytes."""
        # test type checks
        file = "/tmp/persistence"
        PersistenceUtil.open_persistence_file(file, os.O_RDONLY | os.O_NOFOLLOW | os.O_CREAT)
        os.remove(file)
        PersistenceUtil.open_persistence_file(file.encode(), os.O_RDONLY | os.O_NOFOLLOW | os.O_CREAT)
        os.remove(file)
        self.assertRaises(TypeError, PersistenceUtil.open_persistence_file, 123, os.O_RDONLY | os.O_NOFOLLOW)
        self.assertRaises(TypeError, PersistenceUtil.open_persistence_file, 123.22, os.O_RDONLY | os.O_NOFOLLOW)
        self.assertRaises(TypeError, PersistenceUtil.open_persistence_file, True, os.O_RDONLY | os.O_NOFOLLOW)
        self.assertRaises(TypeError, PersistenceUtil.open_persistence_file, None, os.O_RDONLY | os.O_NOFOLLOW)
        self.assertRaises(TypeError, PersistenceUtil.open_persistence_file, {"id": "Default"}, os.O_RDONLY | os.O_NOFOLLOW)
        self.assertRaises(TypeError, PersistenceUtil.open_persistence_file, ["Default"], os.O_RDONLY | os.O_NOFOLLOW)

        # path does not exist (O_CREAT flag not set)
        self.assertRaises(FileNotFoundError, PersistenceUtil.open_persistence_file, file, os.O_RDONLY | os.O_NOFOLLOW)

        # path does not exist (O_CREAT flag set) - repeat if it exists and check if fd is returned
        fd = PersistenceUtil.open_persistence_file(file, os.O_RDONLY | os.O_NOFOLLOW | os.O_CREAT)
        self.assertIsNotNone(fd)

        # path exists
        fd = PersistenceUtil.open_persistence_file(file, os.O_RDONLY | os.O_NOFOLLOW)
        self.assertIsNotNone(fd)
        os.remove(file)

    def test3replace_persistence_file(self):
        """Test replacing the name of the persistence file."""
        # path does not exist
        file = "/tmp/persistence"
        fd, _ = tempfile.mkstemp(dir=SecureOSFunctions.tmp_base_dir_path)
        os.write(fd, b"file2")
        PersistenceUtil.replace_persistence_file(file, fd)
        fd = PersistenceUtil.open_persistence_file(file, os.O_RDONLY)
        self.assertEqual(os.read(fd, 50), b"file2")
        os.close(fd)

        # path exists
        fd = PersistenceUtil.open_persistence_file(file, os.O_WRONLY | os.O_CREAT)
        os.write(fd, b"file1")
        os.close(fd)
        fd = PersistenceUtil.open_persistence_file(file, os.O_RDONLY)
        self.assertEqual(os.read(fd, 50), b"file1")
        os.close(fd)
        fd, _ = tempfile.mkstemp(dir=SecureOSFunctions.tmp_base_dir_path)
        os.write(fd, b"file2")
        PersistenceUtil.replace_persistence_file(file, fd)
        fd = PersistenceUtil.open_persistence_file(file, os.O_RDONLY | os.O_NOFOLLOW)
        self.assertEqual(os.read(fd, 50), b"file2")
        os.remove(file)

    def test4load_json(self):
        """Load persisted json data."""
        # path does not exist
        file = "/tmp/persistence"
        self.assertEqual(PersistenceUtil.load_json(file), None)

        # json data corrupted
        fd = PersistenceUtil.open_persistence_file(file, os.O_WRONLY | os.O_CREAT)
        os.write(fd, b"file1")
        os.close(fd)
        self.assertRaises(ValueError, PersistenceUtil.load_json, file)

        # working example
        fd = PersistenceUtil.open_persistence_file(file, os.O_WRONLY)
        os.write(fd, b'{"key": "value"}')
        os.close(fd)
        data = PersistenceUtil.load_json(file)
        self.assertEqual(data, {"key": "value"})
        os.remove(file)

    def test5store_json(self):
        """Store json data into the persistence file."""
        # json data corrupted
        file = "/tmp/persistence"
        PersistenceUtil.store_json(file, b"file")
        fd = PersistenceUtil.open_persistence_file(file, os.O_RDONLY)
        self.assertEqual(os.read(fd, 50), b'"bytes:file"')
        os.close(fd)
        os.remove(file)

    def test6create_missing_directories(self):
        """Test if all missing directories are created."""
        # only base directory exists
        file = "/tmp/persistence/data1/data2"
        PersistenceUtil.create_missing_directories(file)
        self.assertTrue(os.path.exists("/tmp/persistence/data1"))
        self.assertFalse(os.path.exists("/tmp/persistence/data1/data2"))

        # path already exists
        PersistenceUtil.create_missing_directories(file)
        self.assertTrue(os.path.exists("/tmp/persistence/data1"))
        self.assertFalse(os.path.exists("/tmp/persistence/data1/data2"))
        os.rmdir("/tmp/persistence/data1")
        os.rmdir("/tmp/persistence")

    def test7clear_persistence(self):
        """Test if clearing the persistence data works properly."""
        base_path = "/tmp/persistence"
        os.mkdir(base_path)
        os.mkdir(os.path.join(base_path, "backup"))
        os.mkdir(os.path.join(base_path, "data1"))
        os.mkdir(os.path.join(base_path, "data2"))
        fd = PersistenceUtil.open_persistence_file(os.path.join(base_path, "data1", "file1.txt"), os.O_WRONLY | os.O_CREAT)
        os.close(fd)
        PersistenceUtil.clear_persistence(base_path)
        self.assertTrue(os.path.exists(os.path.join(base_path, "backup")))
        self.assertFalse(os.path.exists(os.path.join(base_path, "data1")))
        self.assertFalse(os.path.exists(os.path.join(base_path, "data2")))
        self.assertFalse(os.path.exists(os.path.join(base_path, "data1", "file1.txt")))
        os.rmdir(os.path.join(base_path, "backup"))
        os.rmdir(base_path)

    def test8copytree(self):
        """Test if our copytree is working as expected even when the destination directory is existing."""
        # destination directory not existing
        base_path = "/tmp/persistence"
        new_base_path = "/tmp/persistence1"
        os.mkdir(base_path)
        os.mkdir(os.path.join(base_path, "backup"))
        PersistenceUtil.copytree(base_path, new_base_path)
        self.assertTrue(os.path.exists(os.path.join(base_path, "backup")))
        self.assertTrue(os.path.exists(os.path.join(new_base_path, "backup")))

        # destination directory existing
        self.assertRaises(FileExistsError, PersistenceUtil.copytree, base_path, new_base_path)
        PersistenceUtil.clear_persistence(base_path)
        PersistenceUtil.copytree(os.path.join(base_path, "backup"), os.path.join(new_base_path, "backup"))

        os.rmdir(os.path.join(base_path, "backup"))
        os.rmdir(base_path)
        os.rmdir(os.path.join(new_base_path, "backup"))
        os.rmdir(new_base_path)


if __name__ == "__main__":
    unittest.main()
