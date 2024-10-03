import unittest
import sys
import os
import socket
import subprocess
from _io import StringIO
import fcntl

from aminer.util import SecureOSFunctions
from aminer.input.LogStream import UnixSocketLogDataResource
from unit.TestBase import TestBase


class SecureOSFunctionsTestLocal(TestBase):
    """This test class must be run locally due to import problems."""

    def setUp(self):
        super().setUp()
        if SecureOSFunctions.base_dir_fd is not None:
            SecureOSFunctions.close_base_directory()
        SecureOSFunctions.base_dir_fd = None
        SecureOSFunctions.tmp_base_dir_fd = None
        SecureOSFunctions.log_dir_fd = None
        SecureOSFunctions.base_dir_path = None
        SecureOSFunctions.tmp_base_dir_path = None
        SecureOSFunctions.log_dir_path = None

    def tearDown(self):
        """Reset all global variables."""
        super().tearDown()
        SecureOSFunctions.base_dir_fd = None
        SecureOSFunctions.tmp_base_dir_fd = None
        SecureOSFunctions.log_dir_fd = None
        SecureOSFunctions.base_dir_path = None
        SecureOSFunctions.tmp_base_dir_path = None
        SecureOSFunctions.log_dir_path = None

    def test1secure_open_close_base_directory(self):
        self.assertRaises(ValueError, SecureOSFunctions.secure_open_base_directory)
        self.assertRaises(ValueError, SecureOSFunctions.secure_open_base_directory, "base/directory")
        base_dir_fd = SecureOSFunctions.secure_open_base_directory("/tmp/lib/aminer")
        self.assertIsNotNone(SecureOSFunctions.base_dir_fd)
        self.assertIsNotNone(SecureOSFunctions.tmp_base_dir_fd)
        self.assertIsNotNone(SecureOSFunctions.base_dir_path)
        self.assertIsNotNone(SecureOSFunctions.tmp_base_dir_path)
        self.assertEqual(base_dir_fd, SecureOSFunctions.secure_open_base_directory("/tmp/lib/aminer"))
        self.assertEqual(os.O_NOFOLLOW | os.O_DIRECTORY, fcntl.fcntl(SecureOSFunctions.base_dir_fd, fcntl.F_GETFL) & (os.O_NOFOLLOW | os.O_NOCTTY | os.O_DIRECTORY))  # os.O_NOCTTY is not included, because it is no terminal controlling device.
        self.assertEqual(os.O_NOFOLLOW | os.O_DIRECTORY, fcntl.fcntl(SecureOSFunctions.tmp_base_dir_fd, fcntl.F_GETFL) & (os.O_NOFOLLOW | os.O_NOCTTY | os.O_DIRECTORY))  # os.O_NOCTTY is not included, because it is no terminal controlling device.

        self.assertIsNotNone(SecureOSFunctions.base_dir_fd)
        self.assertIsNotNone(SecureOSFunctions.tmp_base_dir_fd)
        self.assertIsNotNone(SecureOSFunctions.base_dir_path)
        self.assertIsNotNone(SecureOSFunctions.tmp_base_dir_path)
        SecureOSFunctions.close_base_directory()
        self.assertIsNone(SecureOSFunctions.base_dir_fd)
        self.assertIsNone(SecureOSFunctions.tmp_base_dir_fd)
        self.assertIsNone(SecureOSFunctions.base_dir_path)
        SecureOSFunctions.close_base_directory()  # no exception should be raised

    def test2secure_open_close_log_directory(self):
        self.assertRaises(ValueError, SecureOSFunctions.secure_open_log_directory)
        self.assertRaises(ValueError, SecureOSFunctions.secure_open_log_directory, "base/directory")
        SecureOSFunctions.secure_open_log_directory("/tmp/lib/aminer/util/log")
        self.assertIsNotNone(SecureOSFunctions.log_dir_fd)
        self.assertIsNotNone(SecureOSFunctions.log_dir_path)
        self.assertEqual(os.O_NOFOLLOW | os.O_DIRECTORY, fcntl.fcntl(SecureOSFunctions.log_dir_fd, fcntl.F_GETFL) & (os.O_NOFOLLOW | os.O_NOCTTY | os.O_DIRECTORY))  # os.O_NOCTTY is not included, because it is no terminal controlling device.
        SecureOSFunctions.close_log_directory()
        self.assertIsNone(SecureOSFunctions.log_dir_fd)
        self.assertIsNone(SecureOSFunctions.log_dir_path)

        SecureOSFunctions.secure_open_base_directory("/tmp/lib/aminer/util")
        SecureOSFunctions.secure_open_log_directory("/tmp/lib/aminer/util/log")
        SecureOSFunctions.close_log_directory()
        SecureOSFunctions.close_base_directory()

    def test3secure_open_file(self):
        file = open("/tmp/lib/aminer/util/log/test.log", "w")
        file.close()
        self.assertRaises(ValueError, SecureOSFunctions.secure_open_file, "base/directory", os.O_NOFOLLOW | os.O_NOCTTY)
        self.assertRaises(Exception, SecureOSFunctions.secure_open_file, "/tmp/lib/aminer/util/log", os.O_NOFOLLOW | os.O_NOCTTY)
        fd = SecureOSFunctions.secure_open_file("/tmp/lib/aminer/util/log", os.O_NOFOLLOW | os.O_NOCTTY | os.O_DIRECTORY)
        self.assertEqual(os.O_NOFOLLOW | os.O_DIRECTORY, fcntl.fcntl(fd, fcntl.F_GETFL) & (os.O_NOFOLLOW | os.O_NOCTTY | os.O_DIRECTORY))  # os.O_NOCTTY is not included, because it is no terminal controlling device.
        os.close(fd)
        fd = SecureOSFunctions.secure_open_file("/tmp/lib/aminer/util/log/test.log", os.O_NOFOLLOW | os.O_NOCTTY)
        self.assertEqual(os.O_NOFOLLOW, fcntl.fcntl(fd, fcntl.F_GETFL) & (os.O_NOFOLLOW | os.O_NOCTTY))  # os.O_NOCTTY is not included, because it is no terminal controlling device.
        os.close(fd)

        SecureOSFunctions.secure_open_base_directory("/tmp/lib/aminer/util")
        fd = SecureOSFunctions.secure_open_file("/tmp/lib/aminer/util/log/test.log", os.O_NOFOLLOW | os.O_NOCTTY)
        self.assertEqual(os.O_NOFOLLOW, fcntl.fcntl(fd, fcntl.F_GETFL) & (os.O_NOFOLLOW | os.O_NOCTTY))  # os.O_NOCTTY is not included, because it is no terminal controlling device.
        os.close(fd)
        SecureOSFunctions.close_base_directory()

    def test4send_annotated_file_descriptor(self):
        """A valid annotated file descriptor is to be sent by a socket."""
        sock_name = '/tmp/test4unixSocket.sock'
        data = b'readmeStream' + b'\x00' + b'You should read these README instructions for better understanding.'
        proc = subprocess.Popen(['python3', 'unit/util/clientTest4.py'])
        if os.path.exists(sock_name):
            os.remove(sock_name)
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(sock_name)
        server.listen(1)
        connection = server.accept()[0]
        unix_socket_log_data_resource = UnixSocketLogDataResource(b'unix:///tmp/test4unixSocket.sock', connection.fileno())
        unix_socket_log_data_resource.fill_buffer()
        self.assertEqual(unix_socket_log_data_resource.buffer, data)
        unix_socket_log_data_resource.update_position(len(unix_socket_log_data_resource.buffer))
        self.assertEqual(unix_socket_log_data_resource.total_consumed_length, 80)
        self.assertEqual(unix_socket_log_data_resource.buffer, b'')
        proc.wait()
        connection.close()
        server.close()

    def test5send_annotated_file_descriptor_invalid_parameters(self):
        """Invalid access is to be performed by using a closed socket."""
        fd = SecureOSFunctions.secure_open_file(b'/etc/aminer/conf-enabled/Readme.txt', os.O_RDONLY)
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.assertRaises(OSError, SecureOSFunctions.send_annotated_file_descriptor, client, fd, b'readmeStream', b'You should read these README instructions for better understanding.')
        client.close()

    def test6send_logstream_descriptor(self):
        """A valid logstream descriptor is to be sent."""
        sock_name = '/tmp/test6unixSocket.sock'
        data = b'logstream' + b'\x00' + b'/var/log/syslog'
        proc = subprocess.Popen(['python3', 'unit/util/clientTest6.py'])
        if os.path.exists(sock_name):
            os.remove(sock_name)
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(sock_name)
        server.listen(1)
        connection = server.accept()[0]
        unix_socket_log_data_resource = UnixSocketLogDataResource(b'unix:///tmp/test6unixSocket.sock', connection.fileno())
        unix_socket_log_data_resource.fill_buffer()
        self.assertEqual(unix_socket_log_data_resource.buffer, data)
        unix_socket_log_data_resource.update_position(len(unix_socket_log_data_resource.buffer))
        self.assertEqual(unix_socket_log_data_resource.total_consumed_length, 25)
        self.assertEqual(unix_socket_log_data_resource.buffer, b'')
        proc.wait()
        connection.close()
        server.close()

    def test7receive_annotated_file_descriptor(self):
        """A valid annotated file descriptor is to be received by a socket."""
        sock_name = '/tmp/test6unixSocket.sock'
        type_info = b'logstream'
        path = b'/var/log/syslog'
        data = (type_info, path)
        proc = subprocess.Popen(['python3', 'unit/util/clientTest6.py'])
        if os.path.exists(sock_name):
            os.remove(sock_name)
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(sock_name)
        server.listen(1)
        connection = server.accept()[0]
        data_tuple = SecureOSFunctions.receive_annotated_file_descriptor(connection)
        self.assertEqual(data_tuple[1], data[0])
        self.assertEqual(data_tuple[2], data[1])
        self.assertEqual(len(data_tuple[1]) + len(data_tuple[2]), 24)
        proc.wait()
        connection.close()
        server.close()


if __name__ == "__main__":
    unittest.main()
