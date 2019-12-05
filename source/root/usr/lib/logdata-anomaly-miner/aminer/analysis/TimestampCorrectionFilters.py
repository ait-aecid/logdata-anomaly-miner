"""This file collects various classes useful to filter and correct
the timestamp associated with a received parsed atom."""

import time
from datetime import datetime

from aminer.input import AtomHandlerInterface

class SimpleMonotonicTimestampAdjust(AtomHandlerInterface):
  """Handlers of this class compare the timestamp of a newly received
  atom with the largest timestamp seen so far. When below, the
  timestamp of this atom is adjusted to the largest value seen,
  otherwise the largest value seen is updated."""
  def __init__(self, subhandlerList, stopWhenHandledFlag=False):
    self.subhandlerList = subhandlerList
    self.stopWhenHandledFlag = stopWhenHandledFlag
    self.latestTimestampSeen = 0

  def receiveAtom(self, logAtom):
    """Pass the atom to the subhandlers.
    @return false when no subhandler was able to handle the atom."""
    timestamp = logAtom.getTimestamp()
    if timestamp is None:
      timestamp = time.time()
    if isinstance(timestamp, datetime):
      timestamp = (datetime.fromtimestamp(0)-timestamp).total_seconds()
    if timestamp < self.latestTimestampSeen:
      logAtom.setTimestamp(self.latestTimestampSeen)
    else:
      self.latestTimestampSeen = timestamp

    result = False
    for handler in self.subhandlerList:
      handlerResult = handler.receiveAtom(logAtom)
      if handlerResult is True:
        result = True
        if self.stopWhenHandledFlag:
          break
    return result
