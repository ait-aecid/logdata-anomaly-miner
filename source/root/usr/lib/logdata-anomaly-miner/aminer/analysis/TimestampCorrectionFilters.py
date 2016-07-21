# This file collects various classes useful to filter and correct
# the timestamp associated with a received parsed atom.

from aminer.parsing import ParsedAtomHandlerInterface


class SimpleMonotonicTimestampAdjust(ParsedAtomHandlerInterface):
  """Handlers of this class compare the timestamp of a newly received
  atom with the largest timestamp seen so far. When below, the
  timestamp of this atom is adjusted to the largest value seen,
  otherwise the largest value seen is updated."""
  def __init__(self, subhandlerList, stopWhenHandledFlag=False):
    self.subhandlerList=subhandlerList
    self.stopWhenHandledFlag=stopWhenHandledFlag
    self.latestTimestampSeen=0

  def receiveParsedAtom(self, atomData, match):
    """Pass the atom to the subhandlers.
    @return false when no subhandler was able to handle the atom."""
    timestamp=parserMatch.getDefaultTimestamp()
    if timestamp<self.latestTimestampSeen:
      parserMatch.setDefaultTimestamp(self.latestTimestampSeen)
    else:
      self.latestTimestampSeen=timestamp

    result=False
    for handler in self.subhandlerList:
      handlerResult=handler.receiveParsedAtom(atomData, match)
      if handlerResult==True:
        result=True
        if self.stopWhenHandledFlag:
          break
    return(result)
