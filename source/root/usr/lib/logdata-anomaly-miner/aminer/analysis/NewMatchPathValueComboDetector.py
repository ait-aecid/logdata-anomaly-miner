import time

from aminer import AMinerConfig
from aminer.AMinerUtils import AnalysisContext
from aminer.parsing import ParsedAtomHandlerInterface
from aminer.util import PersistencyUtil
from aminer.util import TimeTriggeredComponentInterface

class NewMatchPathValueComboDetector(ParsedAtomHandlerInterface, TimeTriggeredComponentInterface):
  """This class creates events when a new value combination for
  a given list of match data pathes were found."""

  def __init__(self, aminerConfig, targetPathList, anomalyEventHandlers,
      peristenceId='Default', allowMissingValuesFlag=False,
      autoIncludeFlag=False):
    """Initialize the detector. This will also trigger reading
    or creation of persistence storage location.
    @param targetPathList the list of values to extract from each
    match to create the value combination to be checked.
    @param allowMissingValuesFlag when set to True, the detector
    will also use matches, where one of the pathes from targetPathList
    does not refer to an existing parsed data object.
    @param autoIncludeFlag when set to True, this detector will
    report a new value only the first time before including it
    in the known values set automatically."""
    self.targetPathList=targetPathList
    self.anomalyEventHandlers=anomalyEventHandlers
    self.autoIncludeFlag=autoIncludeFlag
    self.allowMissingValuesFlag=allowMissingValuesFlag
    self.nextPersistTime=None

    PersistencyUtil.addPersistableComponent(self)
    self.persistenceFileName=AMinerConfig.buildPersistenceFileName(
        aminerConfig, self.__class__.__name__, peristenceId)
    persistenceData=PersistencyUtil.loadJson(self.persistenceFileName)
    if persistenceData==None:
      self.knownValuesSet=set()
    else:
# Set and tuples were stored as list of lists. Transform the inner
# lists to tuples to allow hash operation needed by set.
      self.knownValuesSet=set([tuple(record) for record in persistenceData])


  def receiveParsedAtom(self, atomData, match):
    """Receive on parsed atom and the information about the parser
    match.
    @return True if a value combination was extracted and checked
    against the list of known combinations, no matter if the checked
    values were new or not."""
    matchDict=match.getMatchDictionary()
    matchValueList=[]
    for targetPath in self.targetPathList:
      match=matchDict.get(targetPath, None)
      if match==None:
        if not(self.allowMissingValuesFlag): return(False)
        matchValueList.append(None)
      else:
        matchValueList.append(match.matchObject)

    matchValueTuple=tuple(matchValueList)
    if not(matchValueTuple in self.knownValuesSet):
      if self.autoIncludeFlag:
        self.knownValuesSet.add(matchValueTuple)
        if self.nextPersistTime==None:
          self.nextPersistTime=time.time()+600
      for listener in self.anomalyEventHandlers:
        listener.receiveEvent('Analysis.%s' % self.__class__.__name__,
            'New value combination for path(es) %s: %s' % (', '.join(self.targetPathList), repr(matchValueTuple)),
            [atomData], (match, matchValueTuple), self)
    return(True)


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
      PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownValuesSet))
      self.nextPersistTime=None
      delta=600
    return(delta)


  def doPersist(self):
    """Immediately write persistence data to storage."""
    PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownValuesSet))
    self.nextPersistTime=None
