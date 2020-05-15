import unittest
from aminer.input.LogStream import FileLogDataResource, \
  UnixSocketLogDataResource, LogStream
import os
import base64
import socket
import hashlib
# skipcq: BAN-B404
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
      file_log_data_resource = FileLogDataResource(self.file + self.logfile, -1)
      file_log_data_resource.open(False)
      self.assertEqual(file_log_data_resource.buffer, b'')
      
      length = file_log_data_resource.fill_buffer()
      self.assertEqual(length, file_log_data_resource.default_buffer_size)
      
      file_log_data_resource.update_position(length)
      self.assertEqual(file_log_data_resource.buffer, b'')
      self.assertEqual(file_log_data_resource.total_consumed_length, file_log_data_resource.default_buffer_size)
      
      # repeat to see if totalConsumedLength was changed.
      length = file_log_data_resource.fill_buffer()
      self.assertEqual(length, file_log_data_resource.default_buffer_size)
      
      file_log_data_resource.update_position(length)
      self.assertEqual(file_log_data_resource.buffer, b'')
      self.assertEqual(file_log_data_resource.total_consumed_length, 2 * file_log_data_resource.default_buffer_size)
      
      file_log_data_resource.close()
    
    '''
    In this case the logStreamFd is > 0 and repositioningData is not None.
    The stream should be repositioned to the right position.
    '''
    def test3file_log_data_resource_log_stream_already_open_repositioning(self):
      fd = os.open('/tmp/log.txt', os.O_RDONLY)
      length = 65536
      data = os.read(fd, length)
      # skipcq: PTC-W1003
      md5 = hashlib.md5()
      md5.update(data)
      hash_digest = md5.digest()
      os.close(fd)
      
      fd = os.open('/tmp/log.txt', os.O_RDONLY)
      file_log_data_resource = FileLogDataResource(self.file + self.logfile, fd, 65536, [os.fstat(fd).st_ino, length, base64.b64encode(hash_digest)])
      file_log_data_resource.fill_buffer()
      self.assertTrue(not file_log_data_resource.buffer == data)
      os.close(fd)
    
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
      sockName = b'/tmp/test5unixSocket.sock'
      # skipcq: BAN-B607, BAN-B603
      proc = subprocess.Popen(['python3', 'unit/input/client.py'])
      
      if os.path.exists(sockName):
        os.remove(sockName)

      print("Opening socket...")
      server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
      server.bind(sockName)
      server.listen(1)
      connection = server.accept()[0]
      unix_socket_log_data_resource = UnixSocketLogDataResource(b'unix://' + sockName, connection.fileno())

      print("Listening...")
      unix_socket_log_data_resource.fill_buffer()
      self.assertEqual("%s" % unix_socket_log_data_resource.buffer, repr(b'data'))
      print('Data received: %s' % unix_socket_log_data_resource.buffer)
      
      unix_socket_log_data_resource.update_position(len(unix_socket_log_data_resource.buffer))
      self.assertEqual(unix_socket_log_data_resource.total_consumed_length, 4)
      self.assertEqual(unix_socket_log_data_resource.buffer, b'')
      
      print("Shutting down...")
      unix_socket_log_data_resource.close()
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
      stream_printer_event_handler = StreamPrinterEventHandler(self.analysis_context, self.output_stream)
      any_byte_data_me = AnyByteDataModelElement('a1')
      
      byte_stream_line_atomizer = ByteStreamLineAtomizer(any_byte_data_me, [],
          [stream_printer_event_handler], 300, None)
      
      file_log_data_resource = FileLogDataResource(self.file + self.logfile, -1)
      self.assertEqual(file_log_data_resource.buffer, b'')

      log_stream = LogStream(file_log_data_resource, byte_stream_line_atomizer)
      file_log_data_resource.open(False)
      log_stream.handle_stream()
      self.assertEqual(file_log_data_resource.total_consumed_length + len(file_log_data_resource.buffer), file_log_data_resource.default_buffer_size)
      
      log_stream.handle_stream()
      self.assertEqual(file_log_data_resource.total_consumed_length + len(file_log_data_resource.buffer), file_log_data_resource.default_buffer_size)

      fileLogDataResource2 = FileLogDataResource(b'file:///var/log/auth.log', -1)
      self.assertEqual(fileLogDataResource2.buffer, b'')
      fileLogDataResource2.open(False)
      log_stream.add_next_resource(fileLogDataResource2)
      
      log_stream.roll_over()
      log_stream.handle_stream()
      self.assertTrue(file_log_data_resource.total_consumed_length > 0)
      self.assertEqual(file_log_data_resource.total_consumed_length, file_log_data_resource.default_buffer_size)
      self.assertTrue(fileLogDataResource2.total_consumed_length > 0)
      log_stream.roll_over()
      
      fileLogDataResource3 = FileLogDataResource(b'file:///var/log/123example.log', -1)
      fileLogDataResource3.open(False)
      log_stream.add_next_resource(fileLogDataResource3)
      self.assertRaises(OSError, log_stream.roll_over)

    
if __name__ == "__main__":
    unittest.main()
