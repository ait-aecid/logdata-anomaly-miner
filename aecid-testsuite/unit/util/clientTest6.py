from time import sleep
import socket
from os.path import sys
sys.path.append('../../')
sys.path.append('./')
from aminer.util.SecureOSFunctions import secure_open_file,\
  send_logstream_descriptor
import os

sock_name = '/tmp/test6unixSocket.sock'
fd = secure_open_file(b'/var/log/syslog', os.O_RDONLY)
sleep(0.5)
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(sock_name)
send_logstream_descriptor(client, fd, b'/var/log/syslog')