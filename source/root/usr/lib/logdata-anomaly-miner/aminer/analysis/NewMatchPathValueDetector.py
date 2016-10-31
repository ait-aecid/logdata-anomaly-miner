import time

from aminer import AMinerConfig
from aminer.AMinerUtils import AnalysisContext
from aminer.input import AtomHandlerInterface
from aminer.util import PersistencyUtil
from aminer.util import TimeTriggeredComponentInterface

class NewMatchPathValueDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
  """This class creates events when new values for a given data
  path were found."""

  def __init__(self, aminerConfig, targetPathList, anomalyEventHandlers, peristenceId='Default', autoIncludeFlag=False):
    """Initialize the detector. This will also trigger reading
    or creation of persistence storage location."""
    self.targetPathList=targetPathList
    self.anomalyEventHandlers=anomalyEventHandlers
    self.autoIncludeFlag=autoIncludeFlag
    self.nextPersistTime=None

    PersistencyUtil.addPersistableComponent(self)
    self.persistenceFileName=AMinerConfig.buildPersistenceFileName(
        aminerConfig, self.__class__.__name__, peristenceId)
    persistenceData=PersistencyUtil.loadJson(self.persistenceFileName)
    if persistenceData==None:
      self.knownPathSet=set()
    else:
      self.knownPathSet=set(persistenceData)


  def receiveAtom(self, logAtom):
    matchDict=logAtom.parserMatch.getMatchDictionary()
    for targetPath in self.targetPathList:
      match=matchDict.get(targetPath, None)
      if match==None: continue
      if not(match.matchObject in self.knownPathSet):
        if self.autoIncludeFlag:
          self.knownPathSet.add(match.matchObject)
          if self.nextPersistTime==None:
            self.nextPersistTime=time.time()+600
        for listener in self.anomalyEventHandlers:
          listener.receiveEvent('Analysis.%s' % self.__class__.__name__,
              'New value for path %s: %s ' % (targetPath, match.matchObject),
              [logAtom.rawData], logAtom, self)


  def getTimeTriggerClass(self):
    """Get the trigger class this component should be registered
    for. This trigger is used only for persistency, so real-time
    triggering is needed."""
    return(AnalysisContext.TIME_TRIGGER_CLASS_REALTIME)

  def doTimer(self, time):
    """Check current ruleset should be persisted"""
    if self.nextPersistTime==None: return(600)

    delta=self.nextPersistTime-time
    if(delta<0):
      PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
      self.nextPersistTime=None
      delta=600
    return(delta)


  def doPersist(self):
    """Immediately write persistence data to storage."""
    PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
    self.nextPersistTime=None
