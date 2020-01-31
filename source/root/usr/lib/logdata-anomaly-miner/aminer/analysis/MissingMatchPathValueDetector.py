"""This module provides the MissingMatchPathValueDetector to generate
events when expected values were not seen for an extended period
of time."""

import time

from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events import EventSourceInterface
from aminer.input import AtomHandlerInterface
from aminer.util import PersistencyUtil
from aminer.util import TimeTriggeredComponentInterface
from aminer.analysis import CONFIG_KEY_LOG_LINE_PREFIX
from datetime import datetime

class MissingMatchPathValueDetector(
    AtomHandlerInterface, TimeTriggeredComponentInterface,
    EventSourceInterface):
  """This class creates events when an expected value is not seen
  within a given timespan, e.g. because the service was deactivated
  or logging disabled unexpectedly. This is complementary to the
  function provided by NewMatchPathValueDetector.

  For each unique value extracted by targetPath, a tracking record
  is added to expectedValuesDict. It stores three numbers: the
  timestamp the extracted value was last seen, the maximum allowed
  gap between observations and the next alerting time when currently
  in error state. When in normal (alerting) state, the value is
  zero."""

  def __init__(
      self, aminerConfig, targetPath, anomalyEventHandlers,
      persistenceId='Default', autoIncludeFlag=False, defaultInterval=3600,
      realertInterval=86400, outputLogLine=True):
    """Initialize the detector. This will also trigger reading
    or creation of persistence storage location.
    @param targetPath to extract a source identification value
    from each logatom."""
    self.targetPath = targetPath
    self.anomalyEventHandlers = anomalyEventHandlers
    self.autoIncludeFlag = autoIncludeFlag
    self.defaultInterval = defaultInterval
    self.realertInterval = realertInterval
# This timestamps is compared with timestamp values from log atoms
# for activation of alerting logic. The first timestamp from logs
# above this value will trigger alerting.
    self.nextCheckTimestamp = 0
    self.lastSeenTimestamp = 0
    self.nextPersistTime = None
    self.outputLogLine = outputLogLine
    self.aminerConfig = aminerConfig

    PersistencyUtil.addPersistableComponent(self)
    self.persistenceFileName = AMinerConfig.buildPersistenceFileName(
        aminerConfig, self.__class__.__name__, persistenceId)
    persistenceData = PersistencyUtil.loadJson(self.persistenceFileName)
    if persistenceData is None:
      self.expectedValuesDict = {}
    else:
      self.expectedValuesDict = persistenceData


  def receiveAtom(self, logAtom):
    """Receive a log atom from a source.
    @param atomData binary raw atom data
    @return True if this handler was really able to handle and
    process the atom. Depending on this information, the caller
    may decide if it makes sense passing the atom also to other
    handlers or to retry later. This behaviour has to be documented
    at each source implementation sending LogAtoms."""
    value = self.getChannelKey(logAtom)
    if value is None:
      return False
    timeStamp = logAtom.getTimestamp()
    if isinstance(timeStamp, datetime):
      timeStamp = timeStamp.timestamp()
    if timeStamp is None:
      timeStamp = round(time.time())
    detectorInfo = self.expectedValuesDict.get(value, None)
    if detectorInfo != None:
# Just update the last seen value and switch from non-reporting
# error state to normal state.
      detectorInfo[0] = timeStamp
      if detectorInfo[2] != 0:
        if timeStamp >= detectorInfo[2]:
          detectorInfo[2] = 0
# Delta of this detector might be lower than the default maximum
# recheck time.
        self.nextCheckTimestamp = min(
            self.nextCheckTimestamp, timeStamp+detectorInfo[1])

    elif self.autoIncludeFlag:
      self.expectedValuesDict[value] = [timeStamp, self.defaultInterval, 0]
      self.nextCheckTimestamp = min(self.nextCheckTimestamp, timeStamp+self.defaultInterval)

# Always enforce persistency syncs from time to time, the timestamps
# in the records change even when no new hosts are added.
    if self.nextPersistTime is None:
      self.nextPersistTime = time.time()+600
    self.checkTimeouts(timeStamp, logAtom)

    return True

  def getChannelKey(self, logAtom):
    """Get the key identifying the channel this logAtom is coming
    from."""
    matchElement = logAtom.parserMatch.getMatchDictionary().get(
        self.targetPath, None)
    if matchElement is None:
      return None
    return matchElement.matchObject


  def checkTimeouts(self, timeStamp, logAtom):
    """Check if there was any timeout on a channel, thus triggering
    event dispatching."""
    eventData = dict()
    self.lastSeenTimestamp = max(self.lastSeenTimestamp, timeStamp)
    if self.lastSeenTimestamp > self.nextCheckTimestamp:
      missingValueList = []
# Start with a large recheck interval. It will be lowered if any
# of the expectation intervals is below that.
      if not self.nextCheckTimestamp:
        self.nextCheckTimestamp = self.lastSeenTimestamp+86400
      for value, detectorInfo in self.expectedValuesDict.items():
        valueOverdueTime = self.lastSeenTimestamp-detectorInfo[0]-detectorInfo[1]
        if detectorInfo[2] != 0:
          nextCheckDelta = detectorInfo[2]-self.lastSeenTimestamp
          if nextCheckDelta > 0:
# Already alerted but not ready for realerting yet.
            self.nextCheckTimestamp = min(
                self.nextCheckTimestamp, detectorInfo[2])
            continue
        else:
# No alerting yet, see if alerting is required.
          if valueOverdueTime < 0:
            old = self.nextCheckTimestamp
            self.nextCheckTimestamp = min(
                self.nextCheckTimestamp,
                self.lastSeenTimestamp-valueOverdueTime)
            if old > self.nextCheckTimestamp or self.nextCheckTimestamp < detectorInfo[2]:
              continue
            
        missingValueList.append([value, valueOverdueTime, detectorInfo[1]])
# Set the next alerting time.
        detectorInfo[2] = self.lastSeenTimestamp+self.realertInterval
        self.expectedValuesDict[value] = detectorInfo
      if missingValueList:
        messagePart = []
        for value, overdueTime, interval in missingValueList:
          if self.__class__.__name__ == 'MissingMatchPathValueDetector':
            messagePart.append('  %s: %s overdue %ss (interval %s)' % (self.targetPath, repr(value), overdueTime, interval))
          else:
            targetPaths = ''
            for targetPath in self.targetPathList:
              targetPaths += targetPath + ', '
            messagePart.append('  %s: %s overdue %ss (interval %s)' % (targetPaths[:-2], repr(value), overdueTime, interval))
        if self.outputLogLine:
          originalLogLinePrefix = self.aminerConfig.configProperties.get(CONFIG_KEY_LOG_LINE_PREFIX)
          if originalLogLinePrefix is None:
            originalLogLinePrefix = ''
          messagePart.append(originalLogLinePrefix+repr(logAtom.rawData))
        for listener in self.anomalyEventHandlers:
          self.sendEventToHandlers(listener, eventData, logAtom, [''.join(messagePart)], missingValueList)
    return True


  def sendEventToHandlers(self, anomalyEventHandler, eventData, logAtom, messagePart, missingValueList):
    anomalyEventHandler.receiveEvent('Analysis.%s' % self.__class__.__name__,
        'Interval too large between values', messagePart, eventData, logAtom, self)


  def setCheckValue(self, value, interval):
    """Add or overwrite a value to be monitored by the detector."""
    self.expectedValuesDict[value] = [self.lastSeenTimestamp, interval, 0]
    self.nextCheckTimestamp = 0
# Explicitely trigger a persistency sync to avoid staying in unsynced
# state too long when no new received atoms trigger it. But do
# not sync immediately, that would make bulk calls to this method
# quite inefficient.
    if self.nextPersistTime is None:
      self.nextPersistTime = time.time()+600


  def removeCheckValue(self, value):
    """Remove checks for given value."""
    del self.expectedValuesDict[value]


  def getTimeTriggerClass(self):
    """Get the trigger class this component can be registered
    for. This detector only needs persisteny triggers in real
    time."""
    return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME


  def doTimer(self, triggerTime):
    """Check current ruleset should be persisted"""
    if self.nextPersistTime is None:
      return 600
    delta = self.nextPersistTime-triggerTime
    if delta <= 0:
      PersistencyUtil.storeJson(self.persistenceFileName, self.expectedValuesDict)
      self.nextPersistTime = None
      delta = 600
    return delta


  def doPersist(self):
    """Immediately write persistence data to storage."""
    PersistencyUtil.storeJson(self.persistenceFileName, self.expectedValuesDict)
    self.nextPersistTime = None


  def whitelistEvent(
      self, eventType, sortedLogLines, eventData, whitelistingData):
    """Whitelist an event generated by this source using the information
    emitted when generating the event.
    @return a message with information about whitelisting
    @throws Exception when whitelisting of this special event
    using given whitelistingData was not possible."""
    if eventType != 'Analysis.%s' % self.__class__.__name__:
      raise Exception('Event not from this source')
    if not isinstance(whitelistingData, int):
      raise Exception('Whitelisting data has to integer with ' \
          'new interval, -1 to reset to defaults, other negative ' \
          'value to remove the entry')
    newInterval = whitelistingData
    if newInterval == -1:
      newInterval = self.defaultInterval
    for keyName, in eventData:
      if newInterval < 0:
        self.removeCheckValue(keyName)
      else:
        self.setCheckValue(keyName, newInterval)
    return 'Updated %d entries' % len(eventData)



class MissingMatchPathListValueDetector(MissingMatchPathValueDetector):
  """This detector works similar to the MissingMatchPathValueDetector.
  It only can lookup values from a list of pathes until one path
  really exists. It then uses this value as key to detect logAtoms
  belonging to the same data stream. This is useful when e.g.
  due to different log formats, the hostname, servicename or any
  other relevant channel identifier has alternative pathes."""

  def __init__(
      self, aminerConfig, targetPathList, anomalyEventHandlers,
      persistenceId='Default', autoIncludeFlag=False, defaultInterval=3600,
      realertInterval=86400):
    """Initialize the detector. This will also trigger reading
    or creation of persistence storage location.
    @param targetPath to extract a source identification value
    from each logatom."""
    super(MissingMatchPathListValueDetector, self).__init__(
        aminerConfig, None, anomalyEventHandlers, persistenceId,
        autoIncludeFlag, defaultInterval, realertInterval)
    self.targetPathList = targetPathList


  def getChannelKey(self, logAtom):
    """Get the key identifying the channel this logAtom is coming
    from."""
    for targetPath in self.targetPathList:
      matchElement = logAtom.parserMatch.getMatchDictionary().get(
          targetPath, None)
      if matchElement is None:
        continue
      return matchElement.matchObject
    return None


  def sendEventToHandlers(self, anomalyEventHandler, eventData, logAtom, messagePart, missingValueList):
    targetPaths = ''
    for targetPath in self.targetPathList:
      targetPaths += targetPath + ', '
    anomalyEventHandler.receiveEvent('Analysis.%s' % self.__class__.__name__, 
        'Interval too large between values', messagePart, eventData, logAtom, self)

