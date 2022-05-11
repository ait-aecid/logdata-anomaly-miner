import unittest
import sys
import os
import socket
from _io import StringIO
# skipcq: BAN-B404
import subprocess

from aminer.util.SecureOSFunctions import secure_open_file, send_annotated_file_descriptor, receive_annoted_file_descriptor
from aminer.util import SecureOSFunctions
from aminer.input.LogStream import UnixSocketLogDataResource
from unit.TestBase import TestBase


class SecureOSFunctionsTestLocal(TestBase):
    """This test class must be run locally due to import problems."""

    opening_socket = 'Opening socket...'
    listening = 'Listening...'

    """This test case is commented out, because it is still not implemented."""

    def test2_secure_open_file_relative_path(self):
        """A file is tried to be opened by using a relative path."""
        self.assertRaises(Exception, secure_open_file, 'JsonUtilTest.py', os.O_RDONLY)

    def test3_secure_open_directory(self):
        """A directory is tried to be opened without using the O_Directory flag."""
        error = sys.stderr = StringIO()
        directory = b'/etc/'
        self.assertRaises(Exception, secure_open_file, directory, os.O_RDONLY)
        secure_open_file(directory, os.O_DIRECTORY)
        SecureOSFunctions.no_secure_open_warn_once_flag = True
        self.assertTrue(
            error.getvalue() in ['WARNING: SECURITY: No secure open yet due to missing openat in python!\n', ''])

    def test4sendAnnotatedFileDescriptor(self):
        """A valid annotated file descriptor is to be sent by a socket."""
        sock_name = '/tmp/test4unixSocket.sock'  # skipcq: BAN-B108
        data = b'readmeStream' + b'\x00' + b'You should read these README instructions for better understanding.'

        # skipcq: BAN-B607, BAN-B603
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

        unix_socket_log_data_resource.close()
        proc.terminate()
        proc.wait()

    def test5send_annotated_file_descriptor_invalid_parameters(self):
        """An invalid access is to be performed by using a closed socket."""
        # socket is closed
        fd = secure_open_file(b'/etc/aminer/conf-enabled/Readme.txt', os.O_RDONLY)
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.assertRaises(OSError, send_annotated_file_descriptor, client, fd, b'readmeStream',
                          b'You should read these README instructions for better understanding.')

    def test6send_logstream_descriptor(self):
        """A valid logstream descriptor is to be sent."""
        sock_name = '/tmp/test6unixSocket.sock'  # skipcq: BAN-B108
        data = b'logstream' + b'\x00' + b'/var/log/syslog'

        # skipcq: BAN-B607, BAN-B603
        subprocess.Popen(['python3', 'unit/util/clientTest6.py'])

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

        unix_socket_log_data_resource.close()

    def test7receive_annotated_file_descriptor(self):
        """A valid annotated file descriptor is to be received by a socket."""
        sock_name = '/tmp/test6unixSocket.sock'  # skipcq: BAN-B108
        type_info = b'logstream'
        path = b'/var/log/syslog'
        data = (type_info, path)

        # skipcq: BAN-B607, BAN-B603
        subprocess.Popen(['python3', 'unit/util/clientTest6.py'])

        if os.path.exists(sock_name):
            os.remove(sock_name)

        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(sock_name)
        server.listen(1)
        connection = server.accept()[0]
        data_tuple = receive_annoted_file_descriptor(connection)

        self.assertEqual(data_tuple[1], data[0])
        self.assertEqual(data_tuple[2], data[1])
        self.assertEqual(len(data_tuple[1]) + len(data_tuple[2]), 24)


if __name__ == "__main__":
    unittest.main()
