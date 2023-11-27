import unittest
import sys
import io
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
from unit.TestBase import TestBase


class PersistenceUtilTest(TestBase):
    """Unittests for the PersistenceUtil class."""

    def test1add_persistable_component(self):
        """
        Add a component to the registry of all persistable components.
        Also test the type of the component, as this task is only performed once for each component.
        """
        pass

    def test2open_persistence_file(self):
        """Test opening a persistence file. Also check if the type of the file_name is string or bytes."""
        # test type checks
        # path does not exist (O_CREAT flag not set)
        # path does not exist (O_CREAT flag set) - repeat if it exists and check if fd is returned
        # path exists
        pass

    def test3replace_persistence_file(self):
        """Test replacing the name of the persistence file."""
        # test if file name is tested for forbidden characters.
        # path does not exist
        # path exists
        pass

    def test4load_json(self):
        """Load persisted json data."""
        # path does not exist
        # json data corrupted
        # working example
        pass

    def test5store_json(self):
        """Store json data into the persistence file."""
        pass

    def test6create_missing_directories(self):
        """Test if all missing directories are created."""
        # only base directory exists
        # path already exists
        pass

    def test7clear_persistence(self):
        """Test if clearing the persistence data works properly."""
        pass

    def test8copytree(self):
        """Test if our copytree is working as expected even when the destination directory is existing."""
        # destination directory not existing
        # destination directory existing
        # some subdirectories are existing in the destination directory
        pass

























    string = b'25537 uid=2'

    match_context_fixed_dme = MatchContext(b' pid=')
    fixed_dme = FixedDataModelElement('s1', b' pid=')
    match_element_fixed_dme = fixed_dme.get_match_element("", match_context_fixed_dme)

    match_context_decimal_integer_value_me = MatchContext(string)
    decimal_integer_value_me = DecimalIntegerValueModelElement('d1', DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                                                               DecimalIntegerValueModelElement.PAD_TYPE_NONE)
    match_element_decimal_integer_value_me = decimal_integer_value_me.get_match_element("", match_context_decimal_integer_value_me)

    fixed_dme = FixedDataModelElement('s1', string)

    decimal_integer_value_me = DecimalIntegerValueModelElement('d1', DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                                                               DecimalIntegerValueModelElement.PAD_TYPE_NONE)

    match_context_first_match_me = MatchContext(string)
    first_match_me = FirstMatchModelElement('f1', [fixed_dme, decimal_integer_value_me])
    match_element_first_match_me = first_match_me.get_match_element('first', match_context_first_match_me)

    match_context_first_match_me2 = MatchContext(string)
    first_match_me2 = FirstMatchModelElement('f2', [decimal_integer_value_me, fixed_dme])
    match_element_first_match_me2 = first_match_me2.get_match_element('second', match_context_first_match_me2)

    def test1persist_multiple_objects_of_single_class(self):
        """In this test case multiple instances of one class are to be persisted and loaded."""
        description = "Test1PersistenceUtil"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', True)
        self.analysis_context.register_component(new_match_path_detector, description)

        t = time.time()
        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)
        log_atom_decimal_integer_value_me = LogAtom(self.match_context_decimal_integer_value_me.match_data,
                                                    ParserMatch(self.match_element_decimal_integer_value_me), t, new_match_path_detector)
        new_match_path_detector.receive_atom(log_atom_fixed_dme)
        new_match_path_detector.receive_atom(log_atom_decimal_integer_value_me)

        other_new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'otherDetector', True)
        self.analysis_context.register_component(other_new_match_path_detector, description + "2")
        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, other_new_match_path_detector)
        other_new_match_path_detector.receive_atom(log_atom_fixed_dme)

        PersistenceUtil.persist_all()
        persistence_data = PersistenceUtil.load_json(new_match_path_detector.persistence_file_name)
        self.assertTrue(
            persistence_data in ([self.match_element_fixed_dme.get_path(), self.match_element_decimal_integer_value_me.get_path()], [
                self.match_element_decimal_integer_value_me.get_path(), self.match_element_fixed_dme.get_path()]))
        self.assertEqual(PersistenceUtil.load_json(other_new_match_path_detector.persistence_file_name), [
            self.match_element_fixed_dme.get_path()])

    def test2persist_multiple_objects_of_multiple_class(self):
        """In this test case multiple instances of multiple classes are to be persisted and loaded."""
        description = "Test2PersistenceUtil"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default2', True)
        self.analysis_context.register_component(new_match_path_detector, description)

        t = time.time()
        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)
        log_atom_decimal_integer_value_me = LogAtom(self.match_context_decimal_integer_value_me.match_data,
                                                    ParserMatch(self.match_element_decimal_integer_value_me), t, new_match_path_detector)
        new_match_path_detector.receive_atom(log_atom_fixed_dme)
        new_match_path_detector.receive_atom(log_atom_decimal_integer_value_me)

        other_new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'otherDetector2',
                                                             True)
        self.analysis_context.register_component(other_new_match_path_detector, description + "2")
        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, other_new_match_path_detector)
        other_new_match_path_detector.receive_atom(log_atom_fixed_dme)

        new_match_path_value_combo_detector = NewMatchPathValueComboDetector(self.aminer_config, ['first/f1/s1'],
                                                                             [self.stream_printer_event_handler], 'Default', False, True)
        self.analysis_context.register_component(new_match_path_value_combo_detector, description + "3")
        log_atom_sequence_me = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_first_match_me), t,
                                       new_match_path_value_combo_detector)
        new_match_path_value_combo_detector.receive_atom(log_atom_sequence_me)

        PersistenceUtil.persist_all()
        persistence_data = PersistenceUtil.load_json(new_match_path_detector.persistence_file_name)
        self.assertTrue(
            persistence_data in ([self.match_element_fixed_dme.get_path(), self.match_element_decimal_integer_value_me.get_path()], [
                self.match_element_decimal_integer_value_me.get_path(), self.match_element_fixed_dme.get_path()]))
        self.assertEqual(PersistenceUtil.load_json(other_new_match_path_detector.persistence_file_name),
                         [self.match_element_fixed_dme.get_path()])
        self.assertEqual(PersistenceUtil.load_json(new_match_path_value_combo_detector.persistence_file_name),
                         ([[log_atom_sequence_me.raw_data]]))

    def test3_no_unique_persistence_id(self):
        """Check if a warning is printed if the same persistence_id is used for the same component type."""
        old_stderr = sys.stderr
        new_stderr = io.StringIO()
        sys.stderr = new_stderr
        PersistenceUtil.SKIP_PERSISTENCE_ID_WARNING = False

        NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', True)
        NewMatchPathValueComboDetector(self.aminer_config, ['first/f1/s1'], [self.stream_printer_event_handler], 'Default', False, True)
        self.assertEqual('', new_stderr.getvalue())

        NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', True)
        self.assertEqual('Warning: Detectors of type NewMatchPathDetector use the persistence_id "Default" multiple times. Please assign a'
                         ' unique persistence_id for every component.\n', new_stderr.getvalue())
        new_stderr.seek(0)
        new_stderr.truncate(0)

        NewMatchPathValueComboDetector(self.aminer_config, ['first/f1/s1'], [self.stream_printer_event_handler], 'Default', False, True)
        self.assertEqual('Warning: Detectors of type NewMatchPathValueComboDetector use the persistence_id "Default" multiple times. Please'
                         ' assign a unique persistence_id for every component.\n', new_stderr.getvalue())
        sys.stderr = old_stderr


if __name__ == "__main__":
    unittest.main()
