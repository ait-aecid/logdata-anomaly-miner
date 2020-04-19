import unittest
from os.path import sys
sys.path.append('../../')
from aminer.util.SecureOSFunctions import secure_open_file, \
  send_annotated_file_descriptor, receive_annoted_file_descriptor
import os
from _io import StringIO
from aminer.util import SecureOSFunctions
import socket
import subprocess
from aminer.input.LogStream import UnixSocketLogDataResource


class SecureOSFunctionsTestLocal(unittest.TestCase):
    '''
    This test class must be run locally due to import problems
    '''
    
    opening_socket = 'Opening socket...'
    listening = 'Listening...'

    '''
    This test case is commented out, because it is still not implemented.
    '''
    # '''
    # A file is tried to be opened by using the secure function.
    # '''
    # def test1_secure_open_file(self):
    #   error = sys.stderr = StringIO()
    #   # if an exception is thrown, the test fails.
    #   secure_open_file(b'/etc/aminer/conf-enabled/Readme.txt', os.O_RDONLY)
    #   SecureOSFunctions.no_secure_open_warn_once_flag = True
    #   self.assertEqual(error.getvalue(), '')
    
    '''
    A file is tried to be opened by using a relative path.
    '''
    def test2_secure_open_file_relative_path(self):
      self.assertRaises(Exception, secure_open_file, 'JsonUtilTest.py', os.O_RDONLY)
    
    '''
    A directory is tried to be opened without using the O_Directory flag.
    '''
    def test3_secure_open_directory(self):
      error = sys.stderr = StringIO()
      directory = b'/etc/'
      self.assertRaises(Exception, secure_open_file, directory, os.O_RDONLY)
      secure_open_file(directory, os.O_DIRECTORY)
      SecureOSFunctions.no_secure_open_warn_once_flag = True
      self.assertTrue(error.getvalue() == 
        'WARNING: SECURITY: No secure open yet due to missing openat in python!\n' 
        or error.getvalue() == '')
    
    '''
    A valid annotated file descriptor is to be sent by a socket.
    '''
    def test4sendAnnotatedFileDescriptor(self):
      self.sock_name = '/tmp/test4unixSocket.sock'
      data = b'readmeStream' + b'\x00' + b'You should read these README instructions for better understanding.'
      
      proc = subprocess.Popen(['python3', 'unit/util/clientTest4.py'])
      
      if os.path.exists(self.sock_name):
        os.remove(self.sock_name)

      print(self.opening_socket)
      server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
      server.bind(self.sock_name)
      server.listen(1)
      connection = server.accept()[0]
      self.unix_socket_log_data_resource = UnixSocketLogDataResource(b'unix:///tmp/test4unixSocket.sock', connection.fileno())

      print(self.listening)
      self.unix_socket_log_data_resource.fill_buffer()
      self.assertEqual(self.unix_socket_log_data_resource.buffer, data)
      print('Data received: %s' % self.unix_socket_log_data_resource.buffer)
      
      self.unix_socket_log_data_resource.update_position(len(self.unix_socket_log_data_resource.buffer))
      self.assertEqual(self.unix_socket_log_data_resource.total_consumed_length, 80)
      self.assertEqual(self.unix_socket_log_data_resource.buffer, b'')
      
      print("Shutting down...")
      self.unix_socket_log_data_resource.close()
      proc.terminate()
      proc.wait()
      print("Done")
    
    '''
    An invalid access is to be performed by using a closed socket.
    '''
    def test5send_annotated_file_descriptor_invalid_parameters(self):
      # socket is closed
      fd = secure_open_file(b'/etc/aminer/conf-enabled/Readme.txt', os.O_RDONLY)
      client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
      self.assertRaises(OSError, send_annotated_file_descriptor, client, fd, b'readmeStream',
          b'You should read these README instructions for better understanding.')
    
    '''
    A valid logstream descriptor is to be sent.
    '''
    def test6send_logstream_descriptor(self):
      self.sock_name = '/tmp/test6unixSocket.sock'
      data = b'logstream' + b'\x00' + b'/var/log/syslog'
      
      subprocess.Popen(['python3', 'unit/util/clientTest6.py'])
      
      if os.path.exists(self.sock_name):
        os.remove(self.sock_name)

      print(self.opening_socket)
      server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
      server.bind(self.sock_name)
      server.listen(1)
      connection = server.accept()[0]
      self.unix_socket_log_data_resource = UnixSocketLogDataResource(b'unix:///tmp/test6unixSocket.sock', connection.fileno())

      print(self.listening)
      self.unix_socket_log_data_resource.fill_buffer()
      self.assertEqual(self.unix_socket_log_data_resource.buffer, data)
      print('Data received: %s' % self.unix_socket_log_data_resource.buffer)
      
      self.unix_socket_log_data_resource.update_position(len(self.unix_socket_log_data_resource.buffer))
      self.assertEqual(self.unix_socket_log_data_resource.total_consumed_length, 25)
      self.assertEqual(self.unix_socket_log_data_resource.buffer, b'')
      
      print("Shutting down...")
      self.unix_socket_log_data_resource.close()
      print("Done")
    
    '''
    A valid annotated file descriptor is to be received by a socket.
    '''
    def test7receive_annotated_file_descriptor(self):
      self.sock_name = '/tmp/test6unixSocket.sock'
      type_info = b'logstream'
      path = b'/var/log/syslog'
      data = (type_info, path)
      
      subprocess.Popen(['python3', 'unit/util/clientTest6.py'])
      
      if os.path.exists(self.sock_name):
        os.remove(self.sock_name)

      print(self.opening_socket)
      server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
      server.bind(self.sock_name)
      server.listen(1)
      connection = server.accept()[0]
      data_tuple = receive_annoted_file_descriptor(connection)
      
      print(self.listening)
      self.assertEqual(data_tuple[1], data[0])
      self.assertEqual(data_tuple[2], data[1])
      print('Data received: (%i, %s, %s)' % data_tuple)
      self.assertEqual(len(data_tuple[1]) + len(data_tuple[2]), 24)
      print("Done")

    
if __name__ == "__main__":
    unittest.main()
