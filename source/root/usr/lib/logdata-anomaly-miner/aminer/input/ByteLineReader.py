import os

class ByteLineReader:
  """This class reads byte based input data from an operating
  system stream without performing any charset conversions."""
  def __init__(self, inputFd, maxLineLength):
    self.inputFd=inputFd
    self.maxLineLength=maxLineLength
    self.streamData=b''
    self.inOverlongLineFlag=False
    self.endOfStreamReached=False


  def readLine(self):
    """Read one line from the input stream including the final
    newline. This method may block if the file descriptor is configured
    for blocking read behaviour. 
    @throws Error when read from stream fails, overlong line or
    incomplete last line is encountered.
    @return the next line or None if read returned no data or
    EOF was reached."""
    while (self.inOverlongLineFlag):
# Error on overlong line was already reported, so just flush
# data till newline or EOF is reached.
# FIXME: No handling of EOF errors on pipes/sockets
      chunk=os.read(self.inputFd, self.maxLineLength)
      if len(chunk)==0: return(None)
      endPos=chunk.find('\n')
      if (endPos>=0):
        self.inOverlongLineFlag=False;
        self.streamData=chunk[endPos+1:]
        break

    while True:
      lineEndPos=self.streamData.find('\n')
      if (lineEndPos>=0):
# Something was found in normal line, return it.
        result=self.streamData[0:lineEndPos]
        self.streamData=self.streamData[lineEndPos+1:]
        return(result);

# See if there is room to read more data.
      if (len(self.streamData)==self.maxLineLength):
# This line must be too long. Enter the error mode and throw
# exception. Next read operation will discard all data belonging
# to this overlong line.
        self.inOverlongLineFlag=True;
        raise Error("Line longer than input buffer size encountered");

      if(not(self.endOfStreamReached)):
        chunk=os.read(self.inputFd, self.maxLineLength-len(self.streamData))
        if (len(chunk)!=0):
          self.streamData+=chunk
          continue

        if (len(chunk)==0):
# So this is a file, we are at the end of it, but more data might
# become available. Reading from closed sockets or pipes would
# have caused an exception.
          return(None)

      if(self.endOfStreamReached):
        if (len(self.streamData)==0): return(None)
        self.streamData=None
        raise Error("Incomplete last line");

  def isEndOfStream(self):
    """Check if the end of stream was reached, all data was processed
    and this state now is permanent. Reading from normal files
    will never reach this state as there could always data be
    appended to it. For sockets, reaching EOF is always permanent."""
    return(self.endOfStreamReached)


  def markEndOfStream(self):
    """Mark this stream as being read till the end, no matter
    if really is. This is required for file streams, where reading
    just does not return any data indefinitely but does no report
    any errors."""
    self.endOfStreamReached=True
