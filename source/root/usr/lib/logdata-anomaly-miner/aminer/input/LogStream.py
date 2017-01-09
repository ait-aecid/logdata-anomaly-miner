"""This module contains interfaces and classes for logdata resource
handling and combining them to resumable virtual LogStream objects.""" 

import base64
import errno
import hashlib
import os
import socket
import stat
import sys

from aminer.util import SecureOSFunctions

class LogDataResource(object):
  """This is the superinterface of each logdata resource monitored
  by AMiner. The interface is designed in a way, that instances
  of same subclass can be used both on AMiner parent process side
  for keeping track of the resources and forwarding the file descriptors
  to the child, but also on child side for the same purpose. The
  only difference is, that on child side, the stream reading and
  read continuation features are used also. After creation on
  child side, this is the sole place for reading and closing the
  streams. An external process may use the file descriptor only
  to wait for input via select."""

  def __init__(
      self, logResourceName, logStreamFd, defaultBufferSize=1<<16,
      repositioningData=None):
    """Create a new LogDataResource. Object creation must not
    touch the logStreamFd or read any data, unless repositioningData
    was given. In the later case, the stream has to support seek
    operation to reread data.
    @param logResourceName the unique name of this source
    @param logStreamFd the stream for reading the resource or
    -1 if not yet opened.
    @param repositioningData if not None, attemt to position the
    the stream using the given data."""
    raise Exception('Interface method called')

  def open(self, reopenFlag=False):
    """Open the given resource.
    @param reopenFlag when True, attempt to reopen the same resource
    and check if it differs from the previously opened one.
    @raise Exception if valid logStreamFd was already provided,
    is still open and reopenFlag is False.
    @raise OSError when opening failed with unexpected error.
    @return True if the resource was really opened or False if
    opening was not yet possible but should be attempted again."""
    raise Exception('Interface method called')

  def getResourceName(self):
    """Get the name of this log resoruce."""
    raise Exception('Interface method called')

  def getFileDescriptor(self):
    """Get the file descriptor of this open resource."""
    raise Exception('Interface method called')

  def fillBuffer(self):
    """Fill the buffer data of this resource. The repositioning
    information is not updated, updatePosition() has to be used.
    @return the number of bytes read or -1 on error or end."""
    raise Exception('Interface method called')

  def updatePosition(self, length):
    """Update the positioning information and discard the buffer
    data afterwards."""
    raise Exception('Interface method called')

  def getRepositioningData(self):
    """Get the data for repositioning the stream. The returned
    structure has to be JSON serializable."""
    raise Exception('Interface method called')

  def close(self):
    """Close this logdata resource. Data access methods will not
    work any more afterwards."""
    raise Exception('Interface method called')


class FileLogDataResource(LogDataResource):
  """This class defines a single log data resource using an underlying
  file accessible via the file descriptor. The characteristics
  of this type of resource is, that reopening and repositioning
  of the stream has to be possible."""

  def __init__(
      self, logResourceName, logStreamFd, defaultBufferSize=1<<16,
      repositioningData=None):
    """Create a new file type resource.
    @param logResourceName the unique name of this source, has to
    start with "file://" before the file path.
    @param logStreamFd the stream for reading the resource or
    -1 if not yet opened.
    @param repositioningData if not None, attemt to position the
    the stream using the given data."""
    if not logResourceName.startswith('file://'):
      raise Exception('Attempting to create different type resource as file')
    self.logResourceName = logResourceName
    self.logFileFd = logStreamFd
    self.statData = None
    if self.logFileFd >= 0:
      self.statData = os.fstat(logStreamFd)
    self.buffer = ''
    self.defaultBufferSize = defaultBufferSize
    self.totalConsumedLength = 0
# Create a hash for repositioning. There is no need to be cryptographically
# secure here: if upstream can manipulate the content, to provoke
# hash collisions, correct positioning would not matter anyway.
    self.repositioningDigest = hashlib.md5()

    if (logStreamFd != -1) and (repositioningData != None):
      if repositioningData[0] != self.statData.st_ino:
        print >>sys.stderr, 'Not attempting to reposition on %s,' \
            'inode number mismatch' % self.logResourceName
      elif repositioningData[1] > self.statData.st_size:
        print >>sys.stderr, 'Not attempting to reposition on %s,' \
            'file size too small' % self.logResourceName
      else:
        hashAlgo = hashlib.md5()
        length = repositioningData[1]
        while length != 0:
          block = None
          if length < defaultBufferSize:
            block = os.read(self.logFileFd, length)
          else:
            block = os.read(self.logFileFd, defaultBufferSize)
          if len(block) == 0:
            print >>sys.stderr, 'Not attempting to reposition ' \
                'on %s, file shrunk while reading' % self.logResourceName
            break
          hashAlgo.update(block)
          length -= len(block)
        digest = hashAlgo.digest()
        if length == 0:
          if digest == base64.b64decode(repositioningData[2]):
# Repositioning is OK, keep current digest and length data.
            self.totalConsumedLength = repositioningData[1]
            self.repositioningDigest = hashAlgo
          else:
            print >>sys.stderr, 'Not attempting to reposition ' \
                'on %s, digest changed' % self.logResourceName
            length = -1
        if length != 0:
# Repositioning failed, go back to the beginning of the stream.
          os.lseek(self.logFileFd, 0, os.SEEK_SET)

  def open(self, reopenFlag=False):
    """Open the given resource.
    @param reopenFlag when True, attempt to reopen the same resource
    and check if it differs from the previously opened one.
    @raise Exception if valid logStreamFd was already provided,
    is still open and reopenFlag is False.
    @raise OSError when opening failed with unexpected error.
    @return True if the resource was really opened or False if
    opening was not yet possible but should be attempted again."""
    if not reopenFlag and (self.logFileFd != -1):
      raise Exception('Cannot reopen stream still open when not instructed to do so')
    logFileFd = -1
    statData = None
    try:
      logFileFd = SecureOSFunctions.secureOpenFile(
          self.logResourceName[7:], os.O_RDONLY)
      statData = os.fstat(logFileFd)
    except OSError as openOsError:
      if logFileFd != -1:
        os.close(logFileFd)
      if openOsError.errno == errno.ENOENT:
        return False
      raise
    if not stat.S_ISREG(statData.st_mode):
      os.close(logFileFd)
      raise Exception('Attempting to open non-regular file %s ' \
          'as file' % self.logResourceName)

    if (reopenFlag and (self.statData != None) and
        (statData.st_ino == self.statData.st_ino) and
        (statData.st_dev == self.statData.st_dev)):
# Reopening was requested, but we would reopen the file already
# opened, which is of no use.
      os.close(logFileFd)
      return False
# This is a new file or a successful reopen attempt.
    self.logFileFd = logFileFd
    self.statData = statData
    return True

  def getResourceName(self):
    """Get the name of this log resoruce."""
    return self.logResourceName

  def getFileDescriptor(self):
    """Get the file descriptor of this open resource."""
    return self.logFileFd

  def fillBuffer(self):
    """Fill the buffer data of this resource. The repositioning
    information is not updated, updatePosition() has to be used.
    @return the number of bytes read or -1 on error or end."""
    data = os.read(self.logFileFd, self.defaultBufferSize)
    self.buffer += data
    return len(data)

  def updatePosition(self, length):
    """Update the positioning information and discard the buffer
    data afterwards."""
    self.repositioningDigest.update(self.buffer[:length])
    self.totalConsumedLength += length
    self.buffer = self.buffer[length:]

  def getRepositioningData(self):
    """Get the data for repositioning the stream. The returned
    structure has to be JSON serializable."""
    return [
        self.statData.st_ino, self.totalConsumedLength,
        base64.b64encode(self.repositioningDigest.digest())]

  def close(self):
    os.close(self.logFileFd)
    self.logFileFd = -1


class UnixSocketLogDataResource(LogDataResource):
  """This class defines a single log data resource connecting
  to a local UNIX socket. The characteristics of this type of
  resource is, that reopening works only after end of stream of
  was reached."""

  def __init__(
      self, logResourceName, logStreamFd, defaultBufferSize=1<<16,
      repositioningData=None):
    """Create a new unix socket type resource.
    @param logResourceName the unique name of this source, has to
    start with "unix://" before the file path.
    @param logStreamFd the stream for reading the resource or
    -1 if not yet opened.
    @param repositioningData has to be None for this type of resource."""
    if not logResourceName.startswith('unix://'):
      raise Exception('Attempting to create different type resource as unix')
    self.logResourceName = logResourceName
    self.logStreamFd = logStreamFd
    self.buffer = ''
    self.defaultBufferSize = defaultBufferSize
    self.totalConsumedLength = 0

  def open(self, reopenFlag=False):
    """Open the given resource.
    @param reopenFlag when True, attempt to reopen the same resource
    and check if it differs from the previously opened one.
    @raise Exception if valid logStreamFd was already provided,
    is still open and reopenFlag is False.
    @raise OSError when opening failed with unexpected error.
    @return True if the resource was really opened or False if
    opening was not yet possible but should be attempted again."""
    if reopenFlag:
      if self.logStreamFd != -1:
        return False
    elif self.logStreamFd != -1:
      raise Exception('Cannot reopen stream still open when not instructed to do so')
    logSocket = None
    try:
      logSocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
      logSocket.connect(self.logResourceName[7:])
    except socket.error as socketError:
      if logSocket != None:
        logSocket.close()
      if (socketError.errno == errno.ENOENT) or (socketError.errno == errno.ECONNREFUSED):
        return False
# Transform exception to OSError as caller does not expect something
# else.
      raise OSError(socketError[0], socketError[1])
    self.logStreamFd = os.dup(logSocket.fileno())
    logSocket.close()
    return True

  def getResourceName(self):
    """Get the name of this log resoruce."""
    return self.logResourceName

  def getFileDescriptor(self):
    """Get the file descriptor of this open resource."""
    return self.logStreamFd

  def fillBuffer(self):
    """Fill the buffer data of this resource. The repositioning
    information is not updated, updatePosition() has to be used.
    @return the number of bytes read or -1 on error or end."""
    data = os.read(self.logStreamFd, self.defaultBufferSize)
    self.buffer += data
    return len(data)

  def updatePosition(self, length):
    """Update the positioning information and discard the buffer
    data afterwards."""
    self.totalConsumedLength += length
    self.buffer = self.buffer[length:]

  def getRepositioningData(self):
    """Get the data for repositioning the stream. The returned
    structure has to be JSON serializable."""
    return None

  def close(self):
    os.close(self.logStreamFd)
    self.logStreamFd = -1


class LogStream(object):
  """This class defines a continuous stream of logging data from
  a given source. This class also handles rollover from one file
  descriptor to a new one."""

  def __init__(self, logDataResource, streamAtomizer):
    """Create a new logstream with an initial logDataResource.
    @param streamAtomizer the atomizer to forward data to."""
# The resource currently processed. Might also be None when previous
# resource was read till end and no rollover to new one had occured.
    self.logDataResource = logDataResource
    self.streamAtomizer = streamAtomizer
# Last reading state, those are the same as returned by StreamAtomizer
# consumeData() method. Start with state 0 (more data required).
    self.lastConsumeState = 0
    self.nextResources = []

  def addNextResource(self, nextLogDataResource):
    """Roll over from one fd to another one pointing to the newer
    version of the same file. This will also change reading behaviour
    of current resource to await EOF or stop as soon as first
    blocking read does not return any data."""
# Just append the resource to the list of next resources. The
# next read operation without any input from the primary resource
# will pick it up automatically.
    if self.logDataResource is None:
      self.logDataResource = nextLogDataResource
    else:
      self.nextResources.append(nextLogDataResource)

  def handleStream(self):
    """Handle data from this stream by forwarding it to the atomizer.
    @return the file descriptor to monitoring for new input or
    -1 if there is no new data or atomizer was not yet ready to
    consume data. Handling should be tried again later on."""

    if self.logDataResource is None:
      return -1
    if self.lastConsumeState == 0:
# We need more data, read it.
      readLength = self.logDataResource.fillBuffer()
      if readLength == -1:
        self.lastConsumeState = self.rollOver()
        return self.lastConsumeState

      if readLength == 0:
        if len(self.nextResources) == 0:
# There is just no input, but we still need more since last round
# as indicated by lastConsumeState. We would not have been called
# if this is a blocking stream, so this must be the preliminiary
# end of the file. Tell caller to wait and retry read later on.
# Keep lastConsumeState value, consume still wants more data.
          return -1

# This seems to EOF for rollover.
        self.lastConsumeState = self.rollOver()
        return self.lastConsumeState

# So there was something read, process it the same way as if data
# was already available in previous round.
      pass
    self.lastConsumeState = self.streamAtomizer.consumeData(
        self.logDataResource.buffer, False)
    if self.lastConsumeState < 0:
      return -1
    if self.lastConsumeState != 0:
      self.logDataResource.updatePosition(self.lastConsumeState)
    return self.logDataResource.getFileDescriptor()


  def rollOver(self):
    """End reading of the current resource and switch to the next.
    This method does not handle lastConsumeState, that has to
    be done outside.
    @return state in same manner as handleStream()"""
    consumedLength = self.streamAtomizer.consumeData(
        self.logDataResource.buffer, True)
    if consumedLength < 0:
# Consumer is not ready to consume yet. Retry later on.
      return -1
    if consumedLength != len(self.logDataResource.buffer):
      if consumedLength != 0:
# Some data consumed, unclear why not all when already at end
# of stream. Retry again immediately to find out why.
        self.logDataResource.updatePosition(consumedLength)
        return self.logDataResource.getFileDescriptor()

# This is a clear protocol violation (see StreamAtomizer documentaion):
# When at EOF, 0 is no valid return value.
      print >>sys.stderr, 'FATAL: Procotol violation by %s detected, ' \
          'flushing data' % repr(self.streamAtomizer.__class__.__name__)
      consumedLength = len(self.logDataResource.buffer)

# Everything consumed, so now ready for rollover.
    self.logDataResource.updatePosition(consumedLength)
    self.logDataResource.close()
    if len(self.nextResources) == 0:
      self.logDataResource = None
      return -1
    self.logDataResource = self.nextResources[0]
    del self.nextResources[0]
    return self.logDataResource.getFileDescriptor()


  def getCurrentFd(self):
    """Get the file descriptor for reading the currently active
    logdata resource."""
    if self.logDataResource is None:
      return -1
    return self.logDataResource.getFileDescriptor()


  def getRepositioningData(self):
    """Get the respositioning information from the currently active
    underlying logdata resource."""
    if self.logDataResource is None:
      return None
    return self.logDataResource.getRepositioningData()
