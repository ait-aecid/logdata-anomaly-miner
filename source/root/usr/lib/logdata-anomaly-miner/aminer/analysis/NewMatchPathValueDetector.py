import time

from aminer import AMinerConfig
from aminer.util import PersistencyUtil

class NewMatchPathValueDetector:
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
    self.persistenceFileName=AMinerConfig.buildPersistenceFileName(aminerConfig, 'NewMatchPathValueDetector', peristenceId)
    persistenceData=PersistencyUtil.loadJson(self.persistenceFileName)
    if persistenceData==None:
      self.knownPathSet=set()
    else:
      self.knownPathSet=set(persistenceData)


  def receiveParsedAtom(self, atomData, match):
    matchDict=match.getMatchDictionary()
    for targetPath in self.targetPathList:
      match=matchDict.get(targetPath, None)
      if match==None: continue
      if not(match.matchObject in self.knownPathSet):
        if self.autoIncludeFlag:
          self.knownPathSet.add(match.matchObject)
          if self.nextPersistTime==None:
            self.nextPersistTime=time.time()+600
        for listener in self.anomalyEventHandlers:
          listener.receiveEvent('Analysis.NewMatchPathValueDetector', 'New value for path %s: %s ' % (targetPath, match.matchObject), [atomData], match)


  def checkTriggers(self):
    """Check current ruleset should be persisted"""
    if self.nextPersistTime==None: return(600)

    delta=self.nextPersistTime-time.time()
    if(delta<0):
      PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
      self.nextPersistTime=None
      delta=600
    return(delta)


  def doPersist(self):
    """Immediately write persistence data to storage."""
    PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
    self.nextPersistTime=None
