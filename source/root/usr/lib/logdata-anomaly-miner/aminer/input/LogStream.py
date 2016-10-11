import base64
import hashlib
import os
import sys

class LogDataResource:
  """This class defines a single log data resource monitored by
  AMiner. After creation, it is the sole place for reading from
  the file descriptor and also closing it at the end. An external
  process may use it only to wait for input via select after being
  explicitely advised to to so."""

  def __init__(self, logFileName, logFileFd, defaultBufferSize=1<<16,
      repositioningData=None):
    """Create a resource with a given filename.
    @param repositioningData if not none, attempt to reposition
    the stream. When repositioning fails, just start from beginning.
    The repositioningData is a list with inode number, position
    and digest data for repositioning."""
    self.logFileName=logFileName
    self.logFileFd=logFileFd
    self.statData=os.fstat(logFileFd)

    self.buffer=''
    self.defaultBufferSize=defaultBufferSize
    self.totalConsumedLength=0
# Create a hash for repositioning. There is no need to be cryptographically
# secure here: if upstream can manipulate the content, to provoke
# hash collisions, correct positioning would not matter anyway.
    self.repositioningDigest=hashlib.md5()

    if repositioningData!=None:
      if repositioningData[0]!=self.statData.st_ino:
        print >>sys.stderr, 'Not attempting to reposition on %s, inode number mismatch' % self.logFileName
      elif repositioningData[1]>self.statData.st_size:
        print >>sys.stderr, 'Not attempting to reposition on %s, file size too small' % self.logFileName
      else:
        hashAlgo=hashlib.md5()
        length=repositioningData[1]
        while length!=0:
          block=None
          if length<defaultBufferSize:
            block=os.read(self.logFileFd, length)
          else:
            block=os.read(self.logFileFd, defaultBufferSize)
          if len(block)==0:
            print >>sys.stderr, 'Not attempting to reposition on %s, file shrunk while reading' % self.logFileName
            break
          hashAlgo.update(block)
          length-=len(block)
        digest=hashAlgo.digest()
        if length==0:
          if digest==base64.b64decode(repositioningData[2]):
# Repositioning is OK, keep current digest and length data.
            self.totalConsumedLength=repositioningData[1]
            self.repositioningDigest=hashAlgo
          else:
            print >>sys.stderr, 'Not attempting to reposition on %s, digest changed' % self.logFileName
            length=-1
        if length!=0:
# Repositioning failed, go back to the beginning of the stream.
          os.lseek(self.logFileFd, 0, os.SEEK_SET)

  def fillBuffer(self):
    """Fill the buffer data of this resource. The repositioning
    information is not updated, updatePosition() has to be used.
    @return the number of bytes read or -1 on error or end."""
    data=os.read(self.logFileFd, self.defaultBufferSize)
    self.buffer+=data
    return(len(data))

  def updatePosition(self, length):
    """Update the positioning information and discard the buffer
    data afterwards."""
    self.repositioningDigest.update(self.buffer[:length])
    self.totalConsumedLength+=length
    self.buffer=self.buffer[length:]

  def getRepositioningData(self):
    """Get the data for repositioning the stream. The returned
    structure has to be JSON serializable."""
    return([self.statData.st_ino, self.totalConsumedLength,
        base64.b64encode(self.repositioningDigest.digest())])

  def close(self):
    os.close(self.logFileFd)
    self.logFileFd=-1


class LogStream:
  """This class defines a continuous stream of logging data from
  a given source. This class also handles rollover from one file
  descriptor to a new one."""

  def __init__(self, logDataResource, streamAtomizer):
    """Create a new logstream with an initial logDataResource.
    @param streamAtomizer the atomizer to forward data to."""
# The resource currently processed. Might also be None when previous
# resource was read till end and no rollover to new one had occured.
    self.logDataResource=logDataResource
    self.streamAtomizer=streamAtomizer
# Last reading state, those are the same as returned by StreamAtomizer
# consumeData() method. Start with state 0 (more data required).
    self.lastConsumeState=0
    self.nextResources=[]

  def addNextResource(self, nextLogDataResource):
    """Roll over from one fd to another one pointing to the newer
    version of the same file. This will also change reading behaviour
    of current resource to await EOF or stop as soon as first
    blocking read does not return any data."""
# Just append the resource to the list of next resources. The
# next read operation without any input from the primary resource
# will pick it up automatically.
    if self.logDataResource==None:
      self.logDataResource=nextLogDataResource
    else:
      self.nextResources.append(nextLogDataResource)

  def handleStream(self):
    """Handle data from this stream by forwarding it to the atomizer.
    @return the file descriptor to monitoring for new input or
    -1 if there is no new data or atomizer was not yet ready to
    consume data. Handling should be tried again later on."""

    if self.logDataResource==None: return(-1)
    if self.lastConsumeState==0:
# We need more data, read it.
      readLength=self.logDataResource.fillBuffer()
      if readLength==-1:
        self.lastConsumeState=self.rollOver()
        return(self.lastConsumeState)

      if readLength==0:
        if len(self.nextResources)==0:
# There is just no input, but we still need more since last round
# as indicated by lastConsumeState. We would not have been called
# if this is a blocking stream, so this must be the preliminiary
# end of the file. Tell caller to wait and retry read later on.
# Keep lastConsumeState value, consume still wants more data.
          return(-1)

# This seems to EOF for rollover.
        self.lastConsumeState=self.rollOver()
        return(self.lastConsumeState)

# So there was something read, process it the same way as if data
# was already available in previous round.
      pass
    self.lastConsumeState=self.streamAtomizer.consumeData(
        self.logDataResource.buffer, False)
    if self.lastConsumeState<0: return(-1)
    if self.lastConsumeState!=0:
      self.logDataResource.updatePosition(self.lastConsumeState)
    return(self.logDataResource.logFileFd)


  def rollOver(self):
    """End reading of the current resource and switch to the next.
    This method does not handle lastConsumeState, that has to
    be done outside.
    @return state in same manner as handleStream()"""
    consumedLength=self.streamAtomizer.consumeData(
        self.logDataResource.buffer, True)
    if consumedLength<0:
# Consumer is not ready to consume yet. Retry later on.
      return(-1)
    if consumedLength!=len(self.logDataResource.buffer):
      if consumedLength!=0:
# Some data consumed, unclear why not all when already at end
# of stream. Retry again immediately to find out why.
        self.logDataResource.updatePosition(consumedLength)
        return(self.logDataResource.logFileFd)

# This is a clear protocol violation (see StreamAtomizer documentaion):
# When at EOF, 0 is no valid return value.
      print >>sys.stderr, 'FATAL: Procotol violation by %s detected, flushing data' % repr(self.streamAtomizer.__class__.__name__)
      consumedLength=len(self.logDataResource.buffer)

# Everything consumed, so now ready for rollover.
    self.logDataResource.updatePosition(consumedLength)
    self.logDataResource.close()
    if len(self.nextResources)==0:
      self.logDataResource=None
      return(-1)
    self.logDataResource=self.nextResources[0]
    del self.nextResources[0]
    return(self.logDataResource.logFileFd)


  def getCurrentFd(self):
    if self.logDataResource==None: return(-1)
    return(self.logDataResource.logFileFd)


  def getRepositioningData(self):
    if self.logDataResource==None: return(None)
    return(self.logDataResource.getRepositioningData())
