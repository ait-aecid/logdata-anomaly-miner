"""This module provides support for splitting a data stream into
atoms, perform parsing and forward the results."""

from aminer.input import LogAtom
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

  def __init__(
      self, parsingModel, atomHandlerList, eventHandlerList,
      maxLineLength, defaultTimestampPath):
    """Create the atomizer.
    @param eventHandlerList when not None, send events to those
    handlers. The list might be empty at invocation and populated
    later on.
    @param maxLineLength the maximal line length including the
    final line separator."""
    self.parsingModel = parsingModel
    self.atomHandlerList = atomHandlerList
    self.eventHandlerList = eventHandlerList
    self.maxLineLength = maxLineLength
    self.defaultTimestampPath = defaultTimestampPath

    self.inOverlongLineFlag = False
# If consuming of data was already attempted but the downstream
# handlers refused to handle it, keep the data and the parsed
# object to avoid expensive duplicate parsing operation. The data
# does not include the line separators any more.
    self.lastUnconsumedLogAtom = None

  def consumeData(self, streamData, endOfStreamFlag=False):
    """Consume data from the underlying stream for atomizing.
    @return the number of consumed bytes, 0 if the atomizer would
    need more data for a complete atom or -1 when no data was
    consumed at the moment but data might be consumed later on."""
# Loop until as much streamData as possible was processed and
# then return a result. The correct processing of endOfStreamFlag
# is tricky: by default, even when all data was processed, do
# one more iteration to handle also the flag.
    consumedLength = 0
    while True:
      if self.lastUnconsumedLogAtom != None:
# Keep length before dispatching: dispatch will reset the field.
        dataLength = len(self.lastUnconsumedLogAtom.rawData)
        if self.dispatchAtom(self.lastUnconsumedLogAtom):
          consumedLength += dataLength+1
          continue
# Nothing consumed, tell upstream to wait if appropriate.
        if consumedLength == 0:
          consumedLength = -1
        break

      lineEnd = streamData.find('\n', consumedLength)
      if self.inOverlongLineFlag:
        if lineEnd < 0:
          consumedLength = len(streamData)
          if endOfStreamFlag:
            self.dispatchEvent('Overlong line terminated by end of stream', streamData)
            self.inOverlongLineFlag = False
          break
        consumedLength = lineEnd+1
        self.inOverlongLineFlag = False
        continue

# This is the valid start of a normal/incomplete/overlong line.
      if lineEnd < 0:
        tailLength = len(streamData)-consumedLength
        if tailLength > self.maxLineLength:
          self.dispatchEvent(
              'Start of overlong line detected', streamData[consumedLength:])
          self.inOverlongLineFlag = True
          consumedLength = len(streamData)
# Stay in loop to handle also endOfStreamFlag!
          continue
        if endOfStreamFlag and (tailLength != 0):
          self.dispatchEvent('Incomplete last line', streamData[consumedLength:])
          consumedLength = len(streamData)
        break

# This is at least a complete/overlong line.
      lineLength = lineEnd+1-consumedLength
      if lineLength > self.maxLineLength:
        self.dispatchEvent('Overlong line detected', streamData[consumedLength:lineEnd])
        consumedLength = lineEnd+1
        continue

# This is a normal line.
      lineData = streamData[consumedLength:lineEnd]
      logAtom = LogAtom.LogAtom(lineData, None, None, self)
      if self.parsingModel != None:
        matchContext = MatchContext(lineData)
        matchElement = self.parsingModel.getMatchElement('', matchContext)
        if (matchElement != None) and (len(matchContext.matchData) == 0):
          logAtom.parserMatch = ParserMatch(matchElement)
          if self.defaultTimestampPath != None:
            tsMatch = logAtom.parserMatch.getMatchDictionary().get(self.defaultTimestampPath, None)
            if tsMatch != None:
              logAtom.setTimestamp(tsMatch.matchObject[1])
      if self.dispatchAtom(logAtom):
        consumedLength = lineEnd+1
        continue
      if consumedLength == 0:
# Downstream did not want the data, so tell upstream to block
# for a while.
        consumedLength = -1
      break
    return consumedLength

  def dispatchAtom(self, logAtom):
    """Dispatch the data using the appropriate handlers. Also clean
    or set lastUnconsumed fields depending on outcome of dispatching."""
    wasConsumedFlag = False
    if len(self.atomHandlerList) == 0:
      wasConsumedFlag = True
    else:
      for handler in self.atomHandlerList:
        if handler.receiveAtom(logAtom):
          wasConsumedFlag = True

    if wasConsumedFlag:
      self.lastUnconsumedLogAtom = None
    else:
      self.lastUnconsumedLogAtom = logAtom
    return wasConsumedFlag

  def dispatchEvent(self, message, lineData):
    """Dispatch an event with given message and line data to all
    event handlers."""
    if self.eventHandlerList is None:
      return
    for handler in self.eventHandlerList:
      handler.receiveEvent(
          'Input.%s' % self.__class__.__name__, message, [lineData],
          None, self)
