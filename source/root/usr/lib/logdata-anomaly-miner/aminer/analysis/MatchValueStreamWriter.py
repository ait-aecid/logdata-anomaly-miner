"""This module dfines a writer that forwards match information
to a stream."""

from aminer.AnalysisChild import AnalysisContext
from aminer.input import AtomHandlerInterface
from aminer.util import TimeTriggeredComponentInterface
import _io

class MatchValueStreamWriter(AtomHandlerInterface, TimeTriggeredComponentInterface):
  """This class extracts values from a given match and writes
  them to a stream. This can be used to forward these values to
  another program (when stream is a wrapped network socket) or
  to a file for further analysis. A stream is used instead of
  a file descriptor to increase performance. To flush it from
  time to time, add the writer object also to the time trigger
  list."""

  def __init__(self, stream, matchValuePathList, separatorString, missingValueString):
    """Initialize the writer."""
    self.stream = stream
    self.matchValuePathList = matchValuePathList
    self.separatorString = separatorString
    self.missingValueString = missingValueString

  def receive_atom(self, logAtom):
    """Forward match value information to the stream."""
    matchDict = logAtom.parserMatch.getMatchDictionary()
    addSepFlag = False
    containsData = False
    result = b''
    for path in self.matchValuePathList:
      if addSepFlag:
        result += self.separatorString
      match = matchDict.get(path, None)
      if match is None:
        result += self.missingValueString
      else:
        result += match.matchString
        containsData = True
      addSepFlag = True
    if containsData:
      if not isinstance(self.stream, _io.BytesIO):
        self.stream.buffer.write(result)
        self.stream.buffer.write(b'\n')
      else:
        self.stream.write(result)
        self.stream.write(b'\n')


  def get_time_trigger_class(self):
    """Get the trigger class this component should be registered
    for. This trigger is used only for persistency, so real-time
    triggering is needed."""
    return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

  def do_timer(self, triggerTime):
    """Flush the timer."""
    self.stream.flush()
    return 10

  def doPersist(self):
    """Flush the timer."""
    self.stream.flush()
