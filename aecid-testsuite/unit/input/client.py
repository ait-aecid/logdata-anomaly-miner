from time import sleep
import socket
sock_name = '/tmp/test5unixSocket.sock'

sleep(0.5)
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(sock_name)
client.send(b'data')
client.close()