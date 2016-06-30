import os
import sys

class LogStream:
  """This class defines a continuous stream of logging data from
  a given source. This class also handles rollover from one file
  descriptor to a new one and performs the resynchronization after
  a restart."""

  def __init__(self, logDataResource):
    self.logDataResource=logDataResource
    self.byteLineReader=ByteLineReader.ByteLineReader(logDataResource.logFileFd, 1<<16)
    self.nextResources=[]

  def rollOver(self, logDataResource):
    """Roll over from one fd to another one pointing to the newer
    version of the same file. The method will query the size of
    the old file to see how many bytes are left for reading. When
    those were processed also, real roll over will be completed."""
# Just append the resource to the list of next resources. The
# next read operation without any input from the primary resource
# will pick it up automatically.
    self.nextResources.append(logDataResource)

  def readLine(self):
    result=self.byteLineReader.readLine()
    if result!=None: return(result)

    if len(self.nextResources)!=0:
# The old one seems to have been read till the end of the file.
# Signal the end of the stream here.
      self.byteLineReader.markEndOfStream()
# Try to read again: this will report errors due to incomplete
# records.
      result=self.byteLineReader.readLine()
      if result!=None:
        raise Exception('Unexpected read result: %s' % repr(result))

      os.close(self.logDataResource.logFileFd)
      self.logDataResource=self.nextResources[0]
      self.nextResources=self.nextResources[1:]
      self.byteLineReader=ByteLineReader.ByteLineReader(self.logDataResource.logFileFd, 1<<16)
