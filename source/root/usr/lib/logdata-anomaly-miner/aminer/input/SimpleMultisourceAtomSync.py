"""This module defines a handler that synchronizes different
streams."""

import time
from aminer.input import AtomHandlerInterface

class SimpleMultisourceAtomSync(AtomHandlerInterface):
  """This class synchronizes different atom streams by forwarding
  the atoms only from the source delivering the oldest ones. This
  is done using the atom timestamp value. Atoms without a timestamp
  are forwarded immediately. When no atoms are received from a
  source for some time, no more atoms are expected from that
  source. This will allow forwarding of blocked atoms from
  other sources afterwards."""

  def __init__(self, atomHandlerList, syncWaitTime=5):
    """@param atomHandlerList forward atoms to all handlers in
    the list, no matter if the logAtom was handled or not.
    @return true as soon as forwarding was attempted, no matter
    if one downstream handler really consumed the atom."""
    self.atomHandlerList = atomHandlerList
    self.syncWaitTime = syncWaitTime
# Last forwarded log atom timestamp
    self.lastForwardTimestamp = 0
# The dictionary containing the currently active sources. Each
# entry is a list with two values:
# * the largest timestamp of a LogAtom forwarded from this source
#   so far.
# * the current LogAtom pending to be forwarded or None if all
#   atoms were forwarded
    self.sourcesDict = {}
# The local clock time when blocking was enabled for any source.
# Start in blocking mode to have chance to see atom from each
# available source before forwarding the first ones.
    self.blockingEndTime = time.time()+self.syncWaitTime
    self.blockingSources = 0
    self.timestampsUnsortedFlag = False
    self.lastForwardedSource = None
    self.bufferEmptyCounter = 0

  def receiveAtom(self, logAtom):
    if self.lastForwardedSource is not None and logAtom.source != self.lastForwardedSource and \
            self.bufferEmptyCounter < (2 * len(self.sourcesDict.keys())):
      self.bufferEmptyCounter += 1
      return False
    else:
      self.bufferEmptyCounter = 0
      self.lastForwardedSource = None

    timestamp = logAtom.atomTime
    if timestamp is None:
      self.forwardAtom(logAtom)
      self.lastForwardedSource = logAtom.source
      return True

    sourceInfo = self.sourcesDict.get(logAtom.source, None)
    if sourceInfo is None:
      sourceInfo = [timestamp, logAtom]
      self.sourcesDict[logAtom.source] = sourceInfo
    else:
      if timestamp < sourceInfo[0]:
# Atoms not sorted, not our problem. Forward it immediately.
        self.timestampsUnsortedFlag = True
        self.forwardAtom(logAtom)
        self.lastForwardedSource = logAtom.source
        return True
      if sourceInfo[1] is None:
        sourceInfo[1] = logAtom

# Source information with the oldest pending atom.
    oldestSourceInfo = None
    hasIdleSourcesFlag = False
    for sourceInfo in self.sourcesDict.values():
      if sourceInfo[1] is None:
        hasIdleSourcesFlag = True
        continue
      if oldestSourceInfo is None:
        oldestSourceInfo = sourceInfo
        continue
      if sourceInfo[1].atomTime < oldestSourceInfo[1].atomTime:
        oldestSourceInfo = sourceInfo
    if self.blockingEndTime != 0:
# We cannot do anything while blocking to catch more atoms.
      if self.blockingEndTime > time.time():
        return False
# Blocking has expired, cleanup the blockers.
      expiredSources = []
      for source, sourceInfo in self.sourcesDict.items():
        if sourceInfo[1] is None:
          expiredSources.append(source)
      for source in expiredSources:
        del self.sourcesDict[source]
      self.blockingEndTime = 0
      self.blockingSources = 0
      hasIdleSourcesFlag = False

    if hasIdleSourcesFlag:
# We cannot let this item pass. Before entering blocking state,
# give all other sources also the chance to submit an atom.
      if self.blockingSources == len(self.sourcesDict):
        self.blockingEndTime = time.time()+self.syncWaitTime
      else:
        self.blockingSources += 1
      return False

# No idle sources, just forward atom from the oldest one if that
# is really the currently active source.
    if logAtom != oldestSourceInfo[1]:
      return False
    self.forwardAtom(logAtom)
    self.lastForwardedSource = logAtom.source
    oldestSourceInfo[1] = None
    if timestamp > oldestSourceInfo[0]:
      oldestSourceInfo[0] = timestamp
    self.blockingSources = 0
    return True


  def forwardAtom(self, logAtom):
    """Forward atom to all atom handlers."""
    for handler in self.atomHandlerList:
      handler.receiveAtom(logAtom)
