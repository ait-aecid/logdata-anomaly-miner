import unittest
from aminer.input.LogStream import FileLogDataResource, \
  UnixSocketLogDataResource, LogStream
import os
import base64
import socket
import hashlib
import subprocess
from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
from aminer.input.ByteStreamLineAtomizer import ByteStreamLineAtomizer
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from unit.TestBase import TestBase


class LogStreamTest(TestBase):
    logfile = b'/tmp/log.txt'
    
    file = b'file://'
    
    def setUp(self):
      super().setUp()
      with open(self.logfile, "w+") as f:
        for i in range(150):
          f.write("%d %s\r\n" % (i+1, "d"*1000))
    
    def tearDown(self):
      super().tearDown()
      os.remove(self.logfile)

    '''
    In this case the logResourceName does not start with b'file://'
    '''
    def test1file_log_data_resource_no_file(self):
      self.assertRaises(Exception, FileLogDataResource, b'/var/log/syslog', -1)
    
    '''
    In this case the logStreamFd is -1 and repositioningData is None
    The next step is to open the stream successfully.
    Afterwards the buffer object is filled with data and the position is updated.
    '''
    def test2file_log_data_resource_log_stream_closed_no_repositioning(self):
      self.file_log_data_resource = FileLogDataResource(self.file + self.logfile, -1)
      self.file_log_data_resource.open(False)
      self.assertEqual(self.file_log_data_resource.buffer, b'')
      
      self.len = self.file_log_data_resource.fill_buffer()
      self.assertEqual(self.len, self.file_log_data_resource.default_buffer_size)
      
      self.file_log_data_resource.update_position(self.len)
      self.assertEqual(self.file_log_data_resource.buffer, b'')
      self.assertEqual(self.file_log_data_resource.total_consumed_length, self.file_log_data_resource.default_buffer_size)
      
      # repeat to see if totalConsumedLength was changed.
      self.len = self.file_log_data_resource.fill_buffer()
      self.assertEqual(self.len, self.file_log_data_resource.default_buffer_size)
      
      self.file_log_data_resource.update_position(self.len)
      self.assertEqual(self.file_log_data_resource.buffer, b'')
      self.assertEqual(self.file_log_data_resource.total_consumed_length, 2 * self.file_log_data_resource.default_buffer_size)
      
      self.file_log_data_resource.close()
    
    '''
    In this case the logStreamFd is > 0 and repositioningData is not None.
    The stream should be repositioned to the right position.
    '''
    def test3file_log_data_resource_log_stream_already_open_repositioning(self):
      self.fd = os.open('/tmp/log.txt', os.O_RDONLY)
      self.length = 65536
      self.data = os.read(self.fd, self.length)
      self.md5 = hashlib.md5()
      self.md5.update(self.data)
      self.hash = self.md5.digest()
      os.close(self.fd)
      
      self.fd = os.open('/tmp/log.txt', os.O_RDONLY)
      self.file_log_data_resource = FileLogDataResource(self.file + self.logfile, self.fd, 65536, [os.fstat(self.fd).st_ino, self.length, base64.b64encode(self.hash)])
      self.file_log_data_resource.fill_buffer()
      self.assertTrue(not self.file_log_data_resource.buffer == self.data)
      os.close(self.fd)
    
    '''
    In this case the logResourceName does not start with b'unix://'
    '''
    def test4unix_socket_log_data_resource_no_unix_socket(self):
      self.assertRaises(Exception, UnixSocketLogDataResource, b'/tmp/log', -1)
    
    '''
    In this case the logStreamFd is -1
    The next step is to open the stream successfully.
    Therefor a server socket is set up listen to data to the server.
    Afterwards the buffer object is filled with data and the position is updated.
    '''
    def test5unix_socket_log_data_resource(self):
      self.sockName = b'/tmp/test5unixSocket.sock'
      proc = subprocess.Popen(['python3', 'unit/input/client.py'])
      
      if os.path.exists(self.sockName):
        os.remove(self.sockName)

      print("Opening socket...")
      server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
      server.bind(self.sockName)
      server.listen(1)
      connection = server.accept()[0]
      self.unix_socket_log_data_resource = UnixSocketLogDataResource(b'unix://' + self.sockName, connection.fileno())

      print("Listening...")
      self.unix_socket_log_data_resource.fill_buffer()
      self.assertEqual("%s" % self.unix_socket_log_data_resource.buffer, repr(b'data'))
      print('Data received: %s' % self.unix_socket_log_data_resource.buffer)
      
      self.unix_socket_log_data_resource.update_position(len(self.unix_socket_log_data_resource.buffer))
      self.assertEqual(self.unix_socket_log_data_resource.total_consumed_length, 4)
      self.assertEqual(self.unix_socket_log_data_resource.buffer, b'')
      
      print("Shutting down...")
      self.unix_socket_log_data_resource.close()
      server.close()
      proc.terminate()
      proc.wait()
      print("Done")
    
    '''
    This unit case verifies the functionality of the LogStream class.
    Different FileLogDataResources are added to the stream.
    The handling of not existing sources is also tested.
    '''
    def test6_log_stream_handle_streams(self):
      self.stream_printer_event_handler = StreamPrinterEventHandler(self.analysis_context, self.output_stream)
      self.any_byte_data_me = AnyByteDataModelElement('a1')
      
      self.byte_stream_line_atomizer = ByteStreamLineAtomizer(self.any_byte_data_me, [],
          [self.stream_printer_event_handler], 300, None)
      
      self.file_log_data_resource = FileLogDataResource(self.file + self.logfile, -1)
      self.assertEqual(self.file_log_data_resource.buffer, b'')

      self.log_stream = LogStream(self.file_log_data_resource, self.byte_stream_line_atomizer)
      self.file_log_data_resource.open(False)
      self.log_stream.handle_stream()
      self.assertEqual(self.file_log_data_resource.total_consumed_length + len(self.file_log_data_resource.buffer), self.file_log_data_resource.default_buffer_size)
      
      self.log_stream.handle_stream()
      self.assertEqual(self.file_log_data_resource.total_consumed_length + len(self.file_log_data_resource.buffer), self.file_log_data_resource.default_buffer_size)

      self.fileLogDataResource2 = FileLogDataResource(b'file:///var/log/auth.log', -1)
      self.assertEqual(self.fileLogDataResource2.buffer, b'')
      self.fileLogDataResource2.open(False)
      self.log_stream.add_next_resource(self.fileLogDataResource2)
      
      self.log_stream.roll_over()
      self.log_stream.handle_stream()
      self.assertTrue(self.file_log_data_resource.total_consumed_length > 0)
      self.assertEqual(self.file_log_data_resource.total_consumed_length, self.file_log_data_resource.default_buffer_size)
      self.assertTrue(self.fileLogDataResource2.total_consumed_length > 0)
      self.log_stream.roll_over()
      
      self.fileLogDataResource3 = FileLogDataResource(b'file:///var/log/123example.log', -1)
      self.fileLogDataResource3.open(False)
      self.log_stream.add_next_resource(self.fileLogDataResource3)
      self.assertRaises(OSError, self.log_stream.roll_over)

    
if __name__ == "__main__":
    unittest.main()
