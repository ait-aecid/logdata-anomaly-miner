from time import sleep
import socket
from os.path import sys
sys.path.append('./')
sys.path.append('../../')
from aminer.util.SecureOSFunctions import secure_open_file, send_annotated_file_descriptor
import os

sock_name = '/tmp/test4unixSocket.sock'
fd = secure_open_file(b'/etc/aminer/conf-enabled/Readme.txt', os.O_RDONLY)
sleep(0.5)
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(sock_name)
send_annotated_file_descriptor(client, fd, b'readmeStream',
    b'You should read these README instructions for better understanding.')
