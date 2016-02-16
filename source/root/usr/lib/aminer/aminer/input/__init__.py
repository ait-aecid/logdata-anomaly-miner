import sys

class LogStream:
  """This class defines a continuous stream of logging data from
  a given source. This class also handles rollover from one file
  descriptor to a new one and performs the resynchronization after
  a restart."""

  def __init__(self, logDataResource):
    self.logDataResource=logDataResource
    self.byteLineReader=ByteLineReader.ByteLineReader(logDataResource.logFileFd, 1<<16)

  def rollOver(self, logDataResource):
    """Roll over from one fd to another one pointing to the newer
    version of the same file. The method will query the size of
    the old file to see how many bytes are left for reading. When
    those were processed also, real roll over will be completed."""
    print >>sys.stderr, 'FIXME: No soft rollover for %s' % logDataResource.logFileName
    os.close(self.logDataResource.logFileFd)
    self.logDataResource=logDataResource
    self.byteLineReader=ByteLineReader.ByteLineReader(logDataResource.logFileFd, 1<<16)

  def readLine(self):
    return(self.byteLineReader.readLine())
