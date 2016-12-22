import time

from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events import EventSourceInterface
from aminer.input import AtomHandlerInterface
from aminer.util import PersistencyUtil
from aminer.util import TimeTriggeredComponentInterface

class MissingMatchPathValueDetector(AtomHandlerInterface,
    TimeTriggeredComponentInterface, EventSourceInterface):
  """This class creates events when an expected value is not seen
  within a given timespan, e.g. because the service was deactivated
  or logging disabled unexpectedly. This is complementary to the
  function provided by NewMatchPathValueDetector.

  The persistency data structure stores three numbers per expected
  value: the timestamp the value was last seen, the maximum gap
  between observations and the last alerting time."""

  def __init__(self, aminerConfig, targetPath, anomalyEventHandlers, peristenceId='Default', autoIncludeFlag=False, defaultInterval=3600):
    """Initialize the detector. This will also trigger reading
    or creation of persistence storage location."""
    self.targetPath=targetPath
    self.anomalyEventHandlers=anomalyEventHandlers
    self.autoIncludeFlag=autoIncludeFlag
    self.defaultInterval=defaultInterval
# Timestamps from log atoms for activation of check logic.
    self.nextCheckTimestamp=0
    self.lastSeenTimestamp=0
    self.nextPersistTime=None

    PersistencyUtil.addPersistableComponent(self)
    self.persistenceFileName=AMinerConfig.buildPersistenceFileName(
        aminerConfig, self.__class__.__name__, peristenceId)
    persistenceData=PersistencyUtil.loadJson(self.persistenceFileName)
    if persistenceData==None:
      self.expectedValuesDict={}
    else:
      self.expectedValuesDict=persistenceData


  def receiveAtom(self, logAtom):
    matchElement=logAtom.parserMatch.getMatchDictionary().get(
        self.targetPath, None)
    if matchElement==None: return(False)
    value=matchElement.matchObject
    timeStamp=logAtom.getTimestamp()
    detectorInfo=self.expectedValuesDict.get(value, None)
    if detectorInfo!=None:
# Just update the last seen value and switch from non-reporting
# error state to normal state.
      detectorInfo[0]=timeStamp
      if detectorInfo[2]!=0:
        detectorInfo[2]=0
# Delta of this detector might be lower than the default maximum
# recheck time.
        self.nextCheckTimestamp=min(self.nextCheckTimestamp,
            timeStamp+detectorInfo[1])

    elif self.autoIncludeFlag:
      self.expectedValuesDict[value]=[timeStamp, self.defaultInterval, 0]
      self.nextCheckTimestamp=min(self.nextCheckTimestamp, timeStamp+self.defaultInterval)

# Always enforce persistency syncs from time to time, the timestamps
# in the records change even when no new hosts are added.
    if self.nextPersistTime==None:
      self.nextPersistTime=time.time()+600

    self.lastSeenTimestamp=max(self.lastSeenTimestamp, timeStamp)
    if self.lastSeenTimestamp>self.nextCheckTimestamp:
      missingValueList=[]
      self.nextCheckTimestamp=self.lastSeenTimestamp+86400;
      for value, detectorInfo in self.expectedValuesDict.iteritems():
        if detectorInfo[2]!=0:
# Already alerted but problem not yet fixed. No realerting.
          continue

        nextCheckDelta=detectorInfo[0]+detectorInfo[1]-self.lastSeenTimestamp
        if nextCheckDelta>=0:
          self.nextCheckTimestamp=min(self.nextCheckTimestamp,
              nextCheckDelta+self.lastSeenTimestamp)
          continue
        missingValueList.append([value, -nextCheckDelta, detectorInfo[1]])
# Set the last alerting time to current timestamp.
        detectorInfo[2]=self.lastSeenTimestamp
      if len(missingValueList)!=0:
        messagePart=''
        for value, overdueTime, interval in missingValueList:
          messagePart='\n  %s overdue %ss (interval %s)' % (value, overdueTime, interval)
        for listener in self.anomalyEventHandlers:
          listener.receiveEvent('Analysis.%s' % self.__class__.__name__,
              'Interval too large between values for path %s:%s ' % (self.targetPath, messagePart),
              [logAtom.rawData], missingValueList, self)
    return(True)


  def setCheckValue(self, value, interval):
    """Add or overwrite a value to be monitored by the detector."""
    self.expectedValuesDict[value]=[self.lastSeenTimestamp, interval, 0]
    self.nextCheckTimestamp=0
# Explicitely trigger a persistency sync to avoid staying in unsynced
# state too long when no new received atoms trigger it. But do
# not sync immediately, that would make bulk calls to this method
# quite inefficient.
    if self.nextPersistTime==None:
      self.nextPersistTime=time.time()+600


  def removeCheckValue(self, value):
    """Remove checks for given value."""
    del self.expectedValuesDict[value]


  def getTimeTriggerClass(self):
    """Get the trigger class this component can be registered
    for. This detector only needs persisteny triggers in real
    time."""
    return(AnalysisContext.TIME_TRIGGER_CLASS_REALTIME)


  def doTimer(self, time):
    """Check current ruleset should be persisted"""
    if self.nextPersistTime==None: return(600)
    delta=self.nextPersistTime-time
    if(delta<=0):
      PersistencyUtil.storeJson(self.persistenceFileName, self.expectedValuesDict)
      self.nextPersistTime=None
      delta=600
    return(delta)


  def doPersist(self):
    """Immediately write persistence data to storage."""
    PersistencyUtil.storeJson(self.persistenceFileName, self.expectedValuesDict)
    self.nextPersistTime=None


  def whitelistEvent(self, eventType, sortedLogLines, eventData,
      whitelistingData):
    """Whitelist an event generated by this source using the information
    emitted when generating the event.
    @return a message with information about whitelisting
    @throws Exception when whitelisting of this special event
    using given whitelistingData was not possible."""
    if eventType!='Analysis.%s' % self.__class__.__name__:
      raise Exception('Event not from this source')
    if not(isinstance(whitelistData, int)):
      raise Exception('Whitelisting data has to integer with new interval, -1 to reset to defaults, other negative value to remove the entry')
    newInterval=whitelistingData
    if newInterval==-1: newInterval=self.defaultInterval
    for keyName, delta, detectorInfo in eventData:
      if newInterval<0:
        self.removeCheckValue(keyName)
      else:
        self.setCheckValue(keyName, newInterval)
    return('Updated %d entries' % len(eventData))
