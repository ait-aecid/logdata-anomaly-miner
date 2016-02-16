import ctypes
import errno
import os
import socket
import struct
import sys
import time

class LogDataResource:
  """This class defines a single log data resource under monitoring
  of aminer. The resource does not need to exist at the time of
  creation of this record."""
  def __init__(self, logFileName, logFileFd):
    self.logFileName=logFileName
    self.logFileFd=logFileFd
    self.statData=None
    if logFileFd>=0:
      self.statData=os.fstat(logFileFd)

noSecureOpenWarnOnceFlag=True

def secureOpenFile(fileName, flags, trustedRoot='/'):
  """Secure opening of a file with given flags. This call will
  refuse to open files where any path component is a symlink.
  As operating system does not provide any means to do that, open
  the fileName directory by directory.
  It also adds O_NOCTTY to the flags as controlling TTY logics
  as this is just an additional risk and does not make sense for
  opening of log files.
  @param trustedRoot Opening this directory is deemed safe by
  default."""

  if fileName[0]!='/':
    raise Exception('Secure open on relative path not supported')
  if (fileName[-1]=='/') and ((flags&os.O_DIRECTORY)==0):
    raise Exception('Opening directory but O_DIRECTORY flag missing')

  """
  if trustedRoot=='/':
    fileName=fileName[1:]
  else:
    if (not fileName.startswith(trustedRoot)) or (fileName[len(trustedRoot)]!='/'):
      raise Exception('File name not within trusted root')
    fileName=fileName[len(trustedRoot)+1:]

  dirFd=os.open(trustedRoot, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_NOCTTY)
# Get rid of duplicated slashes
  pathParts=[]
  for part in fileName.split['/']:
    if len(part): pathParts.append(part)
  
  for dirPart in pathParts[:-1]:
    nextFd=os.openat(dirFd, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_NOCTTY)
    os.close(dirFd)
    dirFd=nextFd
  return(os.openat(dirFd, pathParts[-1], flags|os.O_NOFOLLOW|os.O_NOCTTY))
  """

  global noSecureOpenWarnOnceFlag
  if noSecureOpenWarnOnceFlag:
    print >>sys.stderr, 'WARNING: SECURITY: No secure open yet due to missing openat in python!'
    noSecureOpenWarnOnceFlag=False
  return(os.open(fileName, flags|os.O_NOFOLLOW|os.O_NOCTTY))


def openPersistenceFile(fileName, flags):
  """This function opens the given persistence file. When O_CREAT
  was specified, the function will attempt to create the directories
  too."""

  try:
    fd=secureOpenFile(fileName, flags)
    return(fd)
  except OSError as openOsError:
    if ((flags&os.O_CREAT)==0) or (openOsError.errno!=errno.ENOENT):
      raise openOsError

# Find out, which directory is missing by stating our way up.
  dirNameLength=fileName.rfind('/')
  if(dirNameLength>0): os.makedirs(fileName[:dirNameLength])
  return(secureOpenFile(fileName, flags))


def createTemporaryPersistenceFile(fileName):
  """Create a temporary file within persistence directory to write
  new persistence data to it. Thus the old data is not modified,
  any error creating or writing the file will not harm the old
  state."""

  fd=None
  while True:
# FIXME: This should use O_TMPFILE, but not yet available. That would
# obsolete the loop also.
    fd=openPersistenceFile('%s.tmp-%f' % (fileName, time.time()), os.O_WRONLY|os.O_CREAT|os.O_EXCL)
    break
  return(fd)


def replacePersistenceFile(fileName, newFileHandle):
  """Replace the named file with the file refered by the handle."""
  print >>sys.stderr, 'WARNING: SECURITY: unsafe unlink (unavailable unlinkat/linkat should be used, but not available in python)'
  try:
    os.unlink(fileName)
  except OSError as openOsError:
    if openOsError.errno!=errno.ENOENT:
      raise openOsError

  tmpFileName=os.readlink('/proc/self/fd/%d' % newFileHandle)
  os.link(tmpFileName, fileName)
  os.unlink(tmpFileName)


# Define workaround structures to implement the missing sendmsg
# library call.
class WorkaroundControlMsgHeader(ctypes.Structure):
  _fields_=[('cmsgLen', ctypes.c_size_t),
      ('cmsgLevel', ctypes.c_int),
      ('cmsgType', ctypes.c_int)]

# CAVEAT: In C, flexible amount of data would have been allocated
# after end of the header. This structure should have only space
# for exactly one file descriptor. To mitigage message buffer
# overflows on architectures, where CMSG_ALIGN in libc may skip
# too many bytes for alignment compared to python implementation,
# add some slack to the end.
class WorkaroundControlMsg(ctypes.Structure):
  _fields_=[('controlMsgHeader', WorkaroundControlMsgHeader),
      ('controlMsgData', ctypes.c_byte*ctypes.sizeof(ctypes.c_int)),
      ('alignmentBuffer', ctypes.c_byte*ctypes.sizeof(ctypes.c_int)*4)]

class WorkaroundIoVec(ctypes.Structure):
  _fields_=[('iovBase', ctypes.c_char_p),
      ('iovLength', ctypes.c_size_t)]

# CAVEAT: msgNameLen is socklen_t and seems to be 4 bytes on both
# 32 and 64bit Linux platforms tested so far. Not clear, if this
# holds true for all of those running.
class WorkaroundMsgHeader(ctypes.Structure):
  _fields_=[('msgName', ctypes.c_char_p),
      ('msgNameLen', ctypes.c_uint32),
      ('msgIov', ctypes.POINTER(WorkaroundIoVec)),
      ('msgIovLen', ctypes.c_size_t),
      ('msgControl', ctypes.POINTER(WorkaroundControlMsg)),
      ('msgControlLen', ctypes.c_size_t),
      ('msgFlags', ctypes.c_int)]

def CMSG_ALIGN(x):
  return ((x + ctypes.sizeof(ctypes.c_size_t) - 1) & ~(ctypes.sizeof(ctypes.c_size_t) - 1))

def CMSG_SPACE(x):
  return CMSG_ALIGN(x) + CMSG_ALIGN(ctypes.sizeof(WorkaroundControlMsgHeader))

def CMSG_LEN(x):
  return CMSG_ALIGN(ctypes.sizeof(WorkaroundControlMsgHeader)) + x

workaroundSocketLibcBindingSendmsg=None
workaroundSocketLibcBindingRecvmsg=None
def workaroundCreateSocketLibcBindings():
  libc=ctypes.CDLL('libc.so.6', use_errno=True)
  if libc==None:
    raise RuntimeError('Failed to load libc.so.6')
  global workaroundSocketLibcBindingSendmsg
  workaroundSocketLibcBindingSendmsg=libc.sendmsg
  workaroundSocketLibcBindingSendmsg.argtypes=(ctypes.c_int, ctypes.POINTER(WorkaroundMsgHeader), ctypes.c_int)
  workaroundSocketLibcBindingSendmsg.restype=ctypes.c_int
  global workaroundSocketLibcBindingRecvmsg
  workaroundSocketLibcBindingRecvmsg=libc.recvmsg
  workaroundSocketLibcBindingRecvmsg.argtypes=(ctypes.c_int, ctypes.POINTER(WorkaroundMsgHeader), ctypes.c_int)
  workaroundSocketLibcBindingRecvmsg.restype=ctypes.c_int


def sendFileDescriptor(sendSocket, sendFd, sendFileName):
  """Send file descriptor and associated file name via SCM_RIGHTS."""
# Bad luck: only most recent Python versions from 3.3 on support
# the sendSocket.sendmsg call. If available, call it.
  if hasattr(sendSocket, 'sendmsg'):
    sendSocket.sendmsg(sendFileName,
        [(socket.SOL_SOCKET, socket.SCM_RIGHTS, struct.pack('i', sendFd))])
    return

  global workaroundSocketLibcBindingSendmsg
  if workaroundSocketLibcBindingSendmsg==None:
    workaroundCreateSocketLibcBindings()

  ioVec=WorkaroundIoVec()
  ioVec.iovBase=sendFileName
  ioVec.iovLength=len(sendFileName)

  controlMsg=WorkaroundControlMsg()
# controlMsg.controlMsgHeader.cmsgLen=ctypes.sizeof(WorkaroundControlMsgHeader)
  controlMsg.controlMsgHeader.cmsgLen=CMSG_LEN(ctypes.sizeof(ctypes.c_int))
  controlMsg.controlMsgHeader.cmsgLevel=socket.SOL_SOCKET
# SCM_RIGHTS=1
  controlMsg.controlMsgHeader.cmsgType=1
  struct.pack_into('i', controlMsg.controlMsgData, 0, sendFd)

  msgHeader=WorkaroundMsgHeader()
  msgHeader.msgName=None
  msgHeader.msgNameLen=0
  msgHeader.msgIov=(ioVec,)
  msgHeader.msgIovLen=1
  msgHeader.msgControl=ctypes.pointer(controlMsg)
  print >>sys.stderr, 'INFO: Difference between c and pyhton impl: C: 20 bytes, python 24 bytes with CMSG_SPACE'
  msgHeader.msgControlLen=controlMsg.controlMsgHeader.cmsgLen
# msgHeader.msgControlLen=CMSG_SPACE(ctypes.sizeof(ctypes.c_int))
  msgHeader.msgFlags=0

  result=workaroundSocketLibcBindingSendmsg(sendSocket.fileno(), ctypes.pointer(msgHeader), 0)
  if result==-1:
    callErrno=ctypes.get_errno()
    raise OSError(callErrno, 'Socket sendmsg failed: %d' % callErrno)
  if result!=len(sendFileName):
    raise Error('Sendfd short write, abort for security reasons')


def receiveFileDescriptor(receiveSocket):
  """Receive a single file descriptor via SCM_RIGHTS via the given
  socket.
  @return a tuple containing the received file descriptor and
  the data content of the received message as file name or None
  when recvmsg was performed on non-blocking socket."""
  if hasattr(receiveSocket, 'recvmsg'):
    fileName, ancData, flags, remoteAddress=receiveSocket.recvmsg(1<<16,
        socket.CMSG_LEN(struct.calcsize('i')))
    cmsg_level, cmsg_type, cmsg_data = ancdata[0]
    if (cmsg_level!=socket.SOL_SOCKET) or (cmsg_type!=socket.SCM_RIGHTS):
      raise Error('Received invalid message from remote side')
    return (struct.unpack('i', cmsg_data)[0], fileName)

  global workaroundSocketLibcBindingRecvmsg
  if workaroundSocketLibcBindingRecvmsg==None:
    workaroundCreateSocketLibcBindings()

  ioVec=WorkaroundIoVec()
  ioVec.iovBase=b'A'*(1<<16)
  ioVec.iovLength=len(ioVec.iovBase)

  controlMsg=WorkaroundControlMsg()
# controlMsg.controlMsgHeader.cmsgLen=ctypes.sizeof(WorkaroundControlMsgHeader)
  controlMsg.controlMsgHeader.cmsgLen=CMSG_LEN(ctypes.sizeof(ctypes.c_int))
  controlMsg.controlMsgHeader.cmsgLevel=0
  controlMsg.controlMsgHeader.cmsgType=0

  msgHeader=WorkaroundMsgHeader()
  msgHeader.msgName=None
  msgHeader.msgNameLen=0
  msgHeader.msgIov=(ioVec,)
  msgHeader.msgIovLen=1
  msgHeader.msgControl=ctypes.pointer(controlMsg)
  msgHeader.msgControlLen=CMSG_SPACE(ctypes.sizeof(ctypes.c_int))
  msgHeader.msgFlags=0

  result=workaroundSocketLibcBindingRecvmsg(receiveSocket.fileno(), ctypes.pointer(msgHeader), 0)
  if result==-1:
    callErrno=ctypes.get_errno()
    if callErrno==errno.EAGAIN: return None
    raise OSError(callErrno, 'Socket recvmsg failed: %d' % callErrno)

  if msgHeader.msgFlags!=0:
    raise Exception('Unexpected flags receiving message: 0x%x' % msgHeader.msgFlags)

  if msgHeader.msgControlLen!=CMSG_SPACE(ctypes.sizeof(ctypes.c_int)):
    raise Exception('Received invalid control message data length %d' % msgHeader.msgControlLen)
  if (controlMsg.controlMsgHeader.cmsgLevel!=socket.SOL_SOCKET) or (controlMsg.controlMsgHeader.cmsgType!=1):
    raise Exception('Received invalid message from remote side: level %d, type %d' % (controlMsg.controlMsgHeader.cmsgLevel, controlMsg.controlMsgHeader.cmsgType))

  logFileName=ioVec.iovBase[:result]
  logFd=struct.unpack_from('i', controlMsg.controlMsgData)[0]
  if logFd<=2:
    print >>sys.stderr, 'WARNING: received "reserved" fd %d' % logFd
  return(logFd, logFileName)
