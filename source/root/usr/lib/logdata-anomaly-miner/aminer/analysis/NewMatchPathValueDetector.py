"""This module defines a detector for new values in a data path."""

import time

from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.input import AtomHandlerInterface
from aminer.util import PersistencyUtil
from aminer.util import TimeTriggeredComponentInterface
from aminer.analysis import CONFIG_KEY_LOG_LINE_PREFIX

class NewMatchPathValueDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
  """This class creates events when new values for a given data
  path were found."""

  def __init__(self, aminerConfig, targetPathList, anomalyEventHandlers, \
    persistenceId='Default', autoIncludeFlag=False, outputLogLine=True):
    """Initialize the detector. This will also trigger reading
    or creation of persistence storage location."""
    self.targetPathList = targetPathList
    self.anomalyEventHandlers = anomalyEventHandlers
    self.autoIncludeFlag = autoIncludeFlag
    self.nextPersistTime = None
    self.outputLogLine = outputLogLine
    self.aminerConfig = aminerConfig

    PersistencyUtil.addPersistableComponent(self)
    self.persistenceFileName = AMinerConfig.buildPersistenceFileName(
        aminerConfig, self.__class__.__name__, persistenceId)
    persistenceData = PersistencyUtil.loadJson(self.persistenceFileName)
    if persistenceData is None:
      self.knownPathSet = set()
    else:
      self.knownPathSet = set(persistenceData)


  def receiveAtom(self, logAtom):
    matchDict = logAtom.parserMatch.getMatchDictionary()
    for targetPath in self.targetPathList:
      match = matchDict.get(targetPath, None)
      if match is None:
        continue
      if match.matchObject not in self.knownPathSet:
        if self.autoIncludeFlag:
          self.knownPathSet.add(match.matchObject)
          if self.nextPersistTime is None:
            self.nextPersistTime = time.time()+600
        if self.outputLogLine:
          sortedLogLines = [logAtom.parserMatch.matchElement.annotateMatch(''), 
            self.aminerConfig.configProperties.get(CONFIG_KEY_LOG_LINE_PREFIX)+repr(logAtom.rawData)]
        else:
          sortedLogLines = [logAtom.parserMatch.matchElement.annotateMatch('')]
        for listener in self.anomalyEventHandlers:
          listener.receiveEvent('Analysis.%s' % self.__class__.__name__, 'New value(s) detected', \
              sortedLogLines, logAtom, self)


  def getTimeTriggerClass(self):
    """Get the trigger class this component should be registered
    for. This trigger is used only for persistency, so real-time
    triggering is needed."""
    return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

  def doTimer(self, triggerTime):
    """Check current ruleset should be persisted"""
    if self.nextPersistTime is None:
      return 600

    delta = self.nextPersistTime-triggerTime
    if delta < 0:
      PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
      self.nextPersistTime = None
      delta = 600
    return delta


  def doPersist(self):
    """Immediately write persistence data to storage."""
    PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
    self.nextPersistTime = None
