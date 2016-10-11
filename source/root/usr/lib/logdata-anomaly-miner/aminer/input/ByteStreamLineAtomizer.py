from aminer.input import StreamAtomizer
from aminer.parsing import MatchContext
from aminer.parsing import ParserMatch

class ByteStreamLineAtomizer(StreamAtomizer):
  """This atomizer consumes binary data from a stream to break
  it into lines, removing the line separator at the end. With
  a parsing model, it will also perform line parsing. Failures
  in atomizing or parsing will cause events to be generated and
  sent to event handler.
  Data will be consumed only when there was no downstream handler
  registered (the data will be discarded in that case) or when
  at least one downstream consumed the data."""

  def __init__(self, parsingModel, parsedAtomHandlers, unparsedAtomHandlers,
      eventHandlerList, maxLineLength, defaultTimestampPath):
    """Create the atomizer.
    @param eventHandlerList when not None, send events to those
    handlers. The list might be empty at invocation and populated
    later on.
    @param maxLineLength the maximal line length including the
    final line separator."""
    self.parsingModel=parsingModel
    self.parsedAtomHandlers=parsedAtomHandlers
    self.unparsedAtomHandlers=unparsedAtomHandlers
    self.eventHandlerList=eventHandlerList
    self.maxLineLength=maxLineLength
    self.defaultTimestampPath=defaultTimestampPath

    self.inOverlongLineFlag=False
# If consuming of data was already attempted but the downstream
# handlers refused to handle it, keep the data and the parsed
# object to avoid expensive duplicate parsing operation. The data
# does not include the line separators any more.
    self.lastUnconsumedData=None
    self.lastUncosumedParserMatch=None

  def consumeData(self, streamData, endOfStreamFlag=False):
    """Consume data from the underlying stream for atomizing.
    @return the number of consumed bytes, 0 if the atomizer would
    need more data for a complete atom or -1 when no data was
    consumed at the moment but data might be consumed later on."""
# Loop until as much streamData as possible was processed and
# then return a result. The correct processing of endOfStreamFlag
# is tricky: by default, even when all data was processed, do
# one more iteration to handle also the flag.
    consumedLength=0
    while True:
      if self.lastUnconsumedData!=None:
# Keep length before dispatching: dispatch will reset the field.
        dataLength=len(self.lastUnconsumedData)
        if self.dispatchData(self.lastUnconsumedData, self.lastUncosumedParserMatch):
          consumedLength+=dataLength+1
          continue
# Nothing consumed, tell upstream to wait if appropriate.
        if consumedLength==0: consumedLength=-1
        break

      lineEnd=streamData.find('\n', consumedLength)
      if self.inOverlongLineFlag:
        if(lineEnd<0):
          consumedLength=length(streamData)
          if endOfStreamFlag:
            self.dispatchEvent('Overlong line terminated by end of stream', streamData)
            self.inOverlongLineFlag=False
          break
        consumedLength=lineEnd+1
        self.inOverlongLineFlag=False
        continue

# This is the valid start of a normal/incomplete/overlong line.
      if lineEnd<0:
        tailLength=len(streamData)-consumedLength
        if tailLength>self.maxLineLength:
          self.dispatchEvent('Start of overlong line detected' ,streamData[consumedLength:])
          self.inOverlongLineFlag=True
          consumedLength=len(streamData)
# Stay in loop to handle also endOfStreamFlag!
          continue
        if endOfStreamFlag and (tailLength!=0):
          self.dispatchEvent('Incomplete last line', streamData[consumedLength:])
          consumedLength=len(streamData)
        break

# This is at least a complete/overlong line.
      lineLength=lineEnd+1-consumedLength
      if lineLength>self.maxLineLength:
        self.dispatchEvent('Overlong line detected', streamData[consumedLength:lineEnd])
        consumedLength=lineEnd+1
        continue

# This is a normal line.
      lineData=streamData[consumedLength:lineEnd]
      parsedAtom=None
      if self.parsingModel!=None:
        matchContext=MatchContext(lineData)
        matchElement=self.parsingModel.getMatchElement('', matchContext)
        if matchElement!=None:
          parsedAtom=ParserMatch(matchElement)
          if self.defaultTimestampPath!=None:
            tsMatch=parsedAtom.getMatchDictionary().get(self.defaultTimestampPath, None)
            if tsMatch!=None:
              parsedAtom.setDefaultTimestamp(tsMatch.matchObject[1])
      if self.dispatchData(lineData, parsedAtom):
        consumedLength=lineEnd+1
        continue
      if consumedLength==0:
# Downstream did not want the data, so tell upstream to block
# for a while.
        consumedLength=-1
      break
    return(consumedLength)

  def dispatchData(self, lineData, parserMatch):
    """Dispatch the data using the appropriate handlers. Also clean
    or set lastUnconsumed fields depending on outcome of dispatching."""
    wasConsumedFlag=False
    if parserMatch==None:  
      if len(self.unparsedAtomHandlers)==0: wasConsumedFlag=True
      else:
        for handler in self.unparsedAtomHandlers:
          if handler.receiveUnparsedAtom('Unparsed data', lineData, lineData, None):
            wasConsumedFlag=True
    else:
      if len(self.parsedAtomHandlers)==0: wasConsumedFlag=True
      else:
        for handler in self.parsedAtomHandlers:
          if handler.receiveParsedAtom(lineData, parserMatch): wasConsumedFlag=True
    if wasConsumedFlag:
      self.lastUnconsumedData=None
      self.lastUncosumedParserMatch=None
    else:
      self.lastUnconsumedData=lineData
      self.lastUncosumedParserMatch=parserMatch
    return(wasConsumedFlag)

  def dispatchEvent(self, message, lineData):
    if self.eventHandlerList==None: return
    for handler in self.eventHandlerList:
      handler.receiveEvent('Input.%s' % self.__class__.__name__,
          message, [lineData], None, self)
