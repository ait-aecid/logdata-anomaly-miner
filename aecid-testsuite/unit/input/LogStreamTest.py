import unittest
import os
import base64
import socket
import hashlib
import subprocess
from aminer.input.LogStream import FileLogDataResource, UnixSocketLogDataResource, LogStream
from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
from aminer.input.ByteStreamLineAtomizer import ByteStreamLineAtomizer
from unit.TestBase import TestBase, DummyFixedDataModelElement


class LogStreamTest(TestBase):
    """Unittests for the LogStream."""

    logfile = b"/tmp/log.txt"
    file = b"file://"

    def setUp(self):
        """Set up the logfile."""
        super().setUp()
        with open(self.logfile, "w+") as f:
            for i in range(150):
                f.write("%d %s\r\n" % (i + 1, "d" * 1000))

    def tearDown(self):
        """Remove the logfile."""
        super().tearDown()
        os.remove(self.logfile)

    def test1file_log_data_resource_log_stream_closed_no_repositioning(self):
        """
        In this case the log_stream_fd is -1 and repositioning_data is None.
        The next step is to open the stream successfully. Afterwards the buffer object is filled with data and the position is updated.
        """
        fldr = FileLogDataResource(self.file + self.logfile, -1)
        fldr.open(False)
        self.assertEqual(fldr.buffer, b"")

        length = fldr.fill_buffer()
        self.assertEqual(length, fldr.default_buffer_size)

        fldr.update_position(length)
        self.assertEqual(fldr.buffer, b"")
        self.assertEqual(fldr.total_consumed_length, fldr.default_buffer_size)

        # repeat to see if total_consumed_length was changed.
        length = fldr.fill_buffer()
        self.assertEqual(length, fldr.default_buffer_size)

        fldr.update_position(length)
        self.assertEqual(fldr.buffer, b"")
        self.assertEqual(fldr.total_consumed_length, 2 * fldr.default_buffer_size)

        fldr.close()

    def test2unix_socket_log_data_resource(self):
        """
        In this case the log_stream_fd is -1. The next step is to open the stream successfully.
        Therefor a server socket is set up listen to data to the server. Afterwards, the buffer object is filled with data and the position
        is updated.
        """
        sock_name = b"/tmp/test5unixSocket.sock"
        proc = subprocess.Popen(["python3", "unit/input/client.py"])

        if os.path.exists(sock_name):
            os.remove(sock_name)

        print("Opening socket...")
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(sock_name)
        server.listen(1)
        connection = server.accept()[0]
        unix_socket_log_data_resource = UnixSocketLogDataResource(b"unix://" + sock_name, connection.fileno())

        print("Listening...")
        unix_socket_log_data_resource.fill_buffer()
        self.assertEqual(repr(unix_socket_log_data_resource.buffer), repr(b"data"))
        print("Data received: %s" % unix_socket_log_data_resource.buffer.decode())

        unix_socket_log_data_resource.update_position(len(unix_socket_log_data_resource.buffer))
        self.assertEqual(unix_socket_log_data_resource.total_consumed_length, 4)
        self.assertEqual(unix_socket_log_data_resource.buffer, b"")

        print("Shutting down...")
        unix_socket_log_data_resource.close()
        server.close()
        proc.terminate()
        proc.wait()
        print("Done")

    def test3_log_stream_handle_streams(self):
        """
        This unit case verifies the functionality of the LogStream class. Different FileLogDataResources are added to the stream.
        The handling of not existing sources is also tested.
        """
        fdme = DummyFixedDataModelElement("fdme", b"a1")
        bstla = ByteStreamLineAtomizer(fdme, [], [self.stream_printer_event_handler], 300, [])
        fldr = FileLogDataResource(self.file + self.logfile, -1)
        self.assertEqual(fldr.buffer, b"")

        ls = LogStream(fldr, bstla)
        fldr.open(False)
        ls.handle_stream()
        self.assertEqual(fldr.total_consumed_length + len(fldr.buffer), fldr.default_buffer_size)

        ls.handle_stream()
        self.assertEqual(fldr.total_consumed_length + len(fldr.buffer), fldr.default_buffer_size)

        fldr2 = FileLogDataResource(b"file:///var/log/auth.log", -1)
        self.assertEqual(fldr2.buffer, b"")
        fldr2.open(False)
        ls.add_next_resource(fldr2)

        ls.roll_over()
        ls.handle_stream()
        self.assertTrue(fldr.total_consumed_length > 0)
        self.assertEqual(fldr.total_consumed_length, fldr.default_buffer_size)
        self.assertTrue(fldr2.total_consumed_length > 0)
        ls.roll_over()

        fldr3 = FileLogDataResource(b"file:///var/log/123example.log", -1)
        fldr3.open(False)
        ls.add_next_resource(fldr3)
        self.assertRaises(OSError, ls.roll_over)

    def test4file_log_data_resource_log_stream_already_open_repositioning(self):
        """
        In this case the logStreamFd is > 0 and repositioning_data is not None.
        The stream should be repositioned to the right position.
        """
        fd = os.open("/tmp/log.txt", os.O_RDONLY)
        length = 65536
        data = os.read(fd, length)
        md5 = hashlib.md5()
        md5.update(data)
        hash_digest = md5.digest()
        os.close(fd)

        fd = os.open("/tmp/log.txt", os.O_RDONLY)
        fldr = FileLogDataResource(self.file + self.logfile, fd, length, [os.fstat(fd).st_ino, length, base64.b64encode(hash_digest)])
        fldr.fill_buffer()
        self.assertNotEqual(fldr.buffer, data)
        self.assertNotEqual(fldr.total_consumed_length, 0)

        # wrong inode number
        fldr = FileLogDataResource(self.file + self.logfile, fd, length, [os.fstat(fd).st_ino + 1, length, base64.b64encode(hash_digest)])
        self.assertEqual(fldr.total_consumed_length, 0)

        # wrong size of repositioning data number
        FileLogDataResource(self.file + self.logfile, fd, length, [os.fstat(fd).st_ino, length + 1, base64.b64encode(hash_digest)])
        self.assertEqual(fldr.total_consumed_length, 0)
        os.close(fd)

    def test4validate_parameters(self):
        """Test all initialization parameters. Input parameters must be validated in the class."""
        fd = os.open("/tmp/log.txt", os.O_RDONLY)
        length = 65536
        data = os.read(fd, length)
        md5 = hashlib.md5()
        md5.update(data)
        hash_digest = md5.digest()
        self.assertRaises(TypeError, FileLogDataResource, "file:///tmp/log.txt", fd, 65536)
        self.assertRaises(TypeError, FileLogDataResource, ["file:///tmp/log.txt"], fd, 65536)
        self.assertRaises(TypeError, FileLogDataResource, None, fd, 65536)
        self.assertRaises(TypeError, FileLogDataResource, True, fd, 65536)
        self.assertRaises(TypeError, FileLogDataResource, 123, fd, 65536)
        self.assertRaises(TypeError, FileLogDataResource, 123.23, fd, 65536)
        self.assertRaises(TypeError, FileLogDataResource, {"id": "Default"}, fd, 65536)
        self.assertRaises(TypeError, FileLogDataResource, (), fd, 65536)
        self.assertRaises(TypeError, FileLogDataResource, set("file:///tmp/log.txt"), fd, 65536)
        self.assertRaises(ValueError, FileLogDataResource, b"", fd, 65536)
        self.assertRaises(ValueError, FileLogDataResource, b"file://", -1)
        self.assertRaises(ValueError, FileLogDataResource, b"/var/log/syslog", -1)

        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", "123", 65536)
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", b"123", 65536)
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", None, 65536)
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", 123.3, 65536)
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", True, 65536)
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", {"id": "Default"}, 65536)
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", (), 65536)
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", set("123"), 65536)

        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", fd, "123")
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", fd,  b"123")
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", fd, None)
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", fd, True)
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", fd, {"id": "Default"})
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", fd, ())
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", fd, set("123"))
        self.assertRaises(ValueError, FileLogDataResource, b"file:///tmp/log.txt", fd, -1)
        self.assertRaises(ValueError, FileLogDataResource, b"file:///tmp/log.txt", fd, 0)

        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", fd, 65536, "123")
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", fd, 65536,  b"123")
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", fd, 65536, True)
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", fd, 65536, {"id": "Default"})
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", fd, 65536, ())
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", fd, 65536, set("123"))
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", fd, 65536, [os.fstat(fd).st_ino])
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", fd, 65536, [os.fstat(fd).st_ino, length])
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", fd, 65536, [os.fstat(fd).st_ino, length, base64.b64encode(hash_digest), 4])
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", fd, 65536, ["d", length, base64.b64encode(hash_digest)])
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", fd, 65536, [os.fstat(fd).st_ino, True, base64.b64encode(hash_digest)])
        self.assertRaises(TypeError, FileLogDataResource, b"file:///tmp/log.txt", fd, 65536, [os.fstat(fd).st_ino, length, 1])
        fldr = FileLogDataResource(b"file:///tmp/log.txt", fd, 65536, [os.fstat(fd).st_ino, length, base64.b64encode(hash_digest)])
        FileLogDataResource(b"file:///tmp/log.txt", fd, 65536, None)

        self.assertRaises(ValueError, UnixSocketLogDataResource, b"/tmp/log", -1)

        self.assertRaises(TypeError, UnixSocketLogDataResource, "unix:///tmp/log.txt", fd, 65536)
        self.assertRaises(TypeError, UnixSocketLogDataResource, ["unix:///tmp/log.txt"], fd, 65536)
        self.assertRaises(TypeError, UnixSocketLogDataResource, None, fd, 65536)
        self.assertRaises(TypeError, UnixSocketLogDataResource, True, fd, 65536)
        self.assertRaises(TypeError, UnixSocketLogDataResource, 123, fd, 65536)
        self.assertRaises(TypeError, UnixSocketLogDataResource, 123.23, fd, 65536)
        self.assertRaises(TypeError, UnixSocketLogDataResource, {"id": "Default"}, fd, 65536)
        self.assertRaises(TypeError, UnixSocketLogDataResource, (), fd, 65536)
        self.assertRaises(TypeError, UnixSocketLogDataResource, set("file:///tmp/log.txt"), fd, 65536)
        self.assertRaises(ValueError, UnixSocketLogDataResource, b"", fd, 65536)
        self.assertRaises(ValueError, UnixSocketLogDataResource, b"unix://", -1)
        self.assertRaises(ValueError, UnixSocketLogDataResource, b"/var/log/syslog", -1)

        self.assertRaises(TypeError, UnixSocketLogDataResource, b"unix:///tmp/log.txt", "123", 65536)
        self.assertRaises(TypeError, UnixSocketLogDataResource, b"unix:///tmp/log.txt", b"123", 65536)
        self.assertRaises(TypeError, UnixSocketLogDataResource, b"unix:///tmp/log.txt", None, 65536)
        self.assertRaises(TypeError, UnixSocketLogDataResource, b"unix:///tmp/log.txt", 123.3, 65536)
        self.assertRaises(TypeError, UnixSocketLogDataResource, b"unix:///tmp/log.txt", True, 65536)
        self.assertRaises(TypeError, UnixSocketLogDataResource, b"unix:///tmp/log.txt", {"id": "Default"}, 65536)
        self.assertRaises(TypeError, UnixSocketLogDataResource, b"unix:///tmp/log.txt", (), 65536)
        self.assertRaises(TypeError, UnixSocketLogDataResource, b"unix:///tmp/log.txt", set("123"), 65536)

        self.assertRaises(TypeError, UnixSocketLogDataResource, b"unix:///tmp/log.txt", fd, "123")
        self.assertRaises(TypeError, UnixSocketLogDataResource, b"unix:///tmp/log.txt", fd,  b"123")
        self.assertRaises(TypeError, UnixSocketLogDataResource, b"unix:///tmp/log.txt", fd, None)
        self.assertRaises(TypeError, UnixSocketLogDataResource, b"unix:///tmp/log.txt", fd, True)
        self.assertRaises(TypeError, UnixSocketLogDataResource, b"unix:///tmp/log.txt", fd, {"id": "Default"})
        self.assertRaises(TypeError, UnixSocketLogDataResource, b"unix:///tmp/log.txt", fd, ())
        self.assertRaises(TypeError, UnixSocketLogDataResource, b"unix:///tmp/log.txt", fd, set("123"))
        self.assertRaises(ValueError, UnixSocketLogDataResource, b"unix:///tmp/log.txt", fd, -1)
        self.assertRaises(ValueError, UnixSocketLogDataResource, b"unix:///tmp/log.txt", fd, 0)

        fdme = DummyFixedDataModelElement("fdme", b"a1")
        bstla = ByteStreamLineAtomizer(fdme, [], [self.stream_printer_event_handler], 300, [])
        self.assertRaises(TypeError, LogStream, "123", bstla)
        self.assertRaises(TypeError, LogStream, b"123", bstla)
        self.assertRaises(TypeError, LogStream, None, bstla)
        self.assertRaises(TypeError, LogStream, 123, bstla)
        self.assertRaises(TypeError, LogStream, 123.3, bstla)
        self.assertRaises(TypeError, LogStream, True, bstla)
        self.assertRaises(TypeError, LogStream, {"id": "Default"}, bstla)
        self.assertRaises(TypeError, LogStream, (), bstla)
        self.assertRaises(TypeError, LogStream, set("123"), bstla)
        self.assertRaises(TypeError, LogStream, fldr, "123")
        self.assertRaises(TypeError, LogStream, fldr, b"123")
        self.assertRaises(TypeError, LogStream, fldr, None)
        self.assertRaises(TypeError, LogStream, fldr, 123)
        self.assertRaises(TypeError, LogStream, fldr, 123.3)
        self.assertRaises(TypeError, LogStream, fldr, True)
        self.assertRaises(TypeError, LogStream, fldr, {"id": "Default"})
        self.assertRaises(TypeError, LogStream, fldr, ())
        self.assertRaises(TypeError, LogStream, fldr, set("123"))
        LogStream(fldr, bstla)
        os.close(fd)


if __name__ == "__main__":
    unittest.main()
