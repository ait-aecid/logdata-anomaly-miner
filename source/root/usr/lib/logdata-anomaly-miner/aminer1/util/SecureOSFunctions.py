"""This module defines functions for secure file handling."""

import os
import socket
import struct
import sys

# Those should go away as soon as Python (or aminer via libc)
# provides those functions.
noSecureOpenWarnOnceFlag = True

def secureOpenFile(fileName, flags, trustedRoot='/'):
  """Secure opening of a file with given flags. This call will
  refuse to open files where any path component is a symlink.
  As operating system does not provide any means to do that, open
  the fileName directory by directory.
  It also adds O_NOCTTY to the flags as controlling TTY logics
  as this is just an additional risk and does not make sense for
  opening of log files.
  @param fileName is the fileName as byte string
  @param trustedRoot Opening this directory is deemed safe by
  default."""

  if not fileName.startswith(b'/'):
    raise Exception('Secure open on relative path not supported')
  if (fileName.endswith(b'/')) and ((flags&os.O_DIRECTORY) == 0):
    raise Exception('Opening directory but O_DIRECTORY flag missing')

# This code would allow secure open but openat is not available
# in python2 series. A long way to go, but keep it here for the
# python3 port to come.
# if trustedRoot=='/':
#   fileName = fileName[1:]
# else:
#   if (not fileName.startswith(trustedRoot)) or (fileName[len(trustedRoot)] != '/'):
#     raise Exception('File name not within trusted root')
#   fileName = fileName[len(trustedRoot)+1:]
#
# dirFd = os.open(trustedRoot, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_NOCTTY)
# lastPathPart = None
# Open all path parts excluding the last one only as directory.
# This will prevent us from opening something unexpected if a
# user would move around directories while traversing.
# for part in fileName.split['/']:
#   if len(part)==0: continue
#   if lastPathPart is not None:
#     nextFd = os.openat(dirFd, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_NOCTTY)
#     os.close(dirFd)
#     dirFd = nextFd
#   lastPathPart = part
# if lastPathPart is None: lastPathPart = '.'
# result = os.openat(dirFd, lastPathPart, flags|os.O_NOFOLLOW|os.O_NOCTTY)
# os.close(dirFd)
# return(result)

  global noSecureOpenWarnOnceFlag
  if noSecureOpenWarnOnceFlag:
    print('WARNING: SECURITY: No secure open yet due to missing openat in python!', file=sys.stderr)
    noSecureOpenWarnOnceFlag = False
  return os.open(fileName, flags|os.O_NOFOLLOW|os.O_NOCTTY)

def sendAnnotatedFileDescriptor(sendSocket, sendFd, typeInfo, annotationData):
  """Send file descriptor and associated annotation data via SCM_RIGHTS.
  @param typeInfo has to be a null-byte free string to inform
  the receiver how to handle the file descriptor and how to interpret
  the annotationData.
  @param annotationData this optional byte array  may convey
  additional information about the file descriptor."""
# Construct the message data first
  if isinstance(typeInfo, str):
    typeInfo = typeInfo.encode()
  if isinstance(annotationData, str):
    annotationData = annotationData.encode()
  if typeInfo.find(b'\x00') >= 0:
    raise Exception('Null bytes not supported in typeInfo')
  messageData = b'%s\x00%s' % (typeInfo, annotationData)
  sendSocket.sendmsg(
      [messageData],
      [(socket.SOL_SOCKET, socket.SCM_RIGHTS, struct.pack('i', sendFd))])

def sendLogstreamDescriptor(sendSocket, sendFd, sendFileName):
  """Send a file descriptor to be used as standard log data stream
  source for the analysis pipeline."""
  sendAnnotatedFileDescriptor(sendSocket, sendFd, b'logstream', sendFileName)

def receiveAnnotedFileDescriptor(receiveSocket):
  """Receive a single file descriptor and attached annotation
  information via SCM_RIGHTS via the given socket. The method
  may raise an Exception when invoked on non-blocking sockets
  and no messages available.
  @return a tuple containing the received file descriptor, type
  information (see sendAnnotatedFileDescriptor) and the annotation
  information."""
  messageData, ancData, flags, remoteAddress = receiveSocket.recvmsg(
      1<<16, socket.CMSG_LEN(struct.calcsize('i')))
  if len(ancData) != 1:
    raise Exception(
        'Received %d sets of ancillary data instead of 1' % len(ancData))
  cmsg_level, cmsg_type, cmsg_data = ancData[0]
  if (cmsg_level != socket.SOL_SOCKET) or (cmsg_type != socket.SCM_RIGHTS):
    raise Exception('Received invalid message from remote side')
# Do not accept multiple or unaligned FDs.
  if len(cmsg_data) != 4:
    raise Exception(
        'Unsupported control message length %d' % len(cmsg_data))
  receivedFd = struct.unpack('i', cmsg_data)[0]

  splitPos = messageData.find(b'\x00')
  if splitPos < 0:
    raise Exception('No null byte in received message')
  typeInfo = messageData[:splitPos]
  annotationData = messageData[splitPos+1:]
  if receivedFd <= 2:
    print('WARNING: received "reserved" fd %d' % receivedFd, file=sys.stderr)
  if isinstance(typeInfo, str):
    typeInfo = typeInfo.encode()
  if isinstance(annotationData, str):
    annotationData = annotationData.encode()
  return(receivedFd, typeInfo, annotationData)
