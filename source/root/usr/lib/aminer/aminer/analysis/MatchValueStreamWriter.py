import time

class MatchValueStreamWriter:
  """This class extracts values from a given match and writes
  them to a stream. This can be used to forward this values to
  another program (when stream is a wrapped network socket) or
  to a file for further analysis. A stream is used instead of
  a file descriptor to increase performance. To flush it from
  time to time, add the writer object also to the time trigger
  list."""

  def __init__(self, stream, matchValuePathList, separatorString, missingValueString):
    """Initialize the writer."""
    self.stream=stream
    self.matchValuePathList=matchValuePathList
    self.separatorString=separatorString
    self.missingValueString=missingValueString

  def receiveParsedAtom(self, atomData, match):
    matchDict=match.getMatchDictionary()
    addSepFlag=False
    result=b''
    for path in self.matchValuePathList:
      if addSepFlag: result+=self.separatorString
      match=matchDict.get(path, None)
      if match==None: result+=self.missingValueString
      else: result+=match.matchString
      addSepFlag=True
    self.stream.write(result)
    self.stream.write('\n')

  def checkTriggers(self):
    self.stream.flush()
    return(10)

  def doPersist(self):
    self.stream.flush()
