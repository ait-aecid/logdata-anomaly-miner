"""This file defines the basic NewMatchPathValueComboDetector
detector to extract values from LogAtoms and check, if the value
combination was already seen before."""

import time
import os

from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events import EventSourceInterface
from aminer.input import AtomHandlerInterface
from aminer.util import PersistencyUtil
from aminer.util import TimeTriggeredComponentInterface
from aminer.analysis import CONFIG_KEY_LOG_LINE_PREFIX

class NewMatchPathValueComboDetector(
    AtomHandlerInterface, TimeTriggeredComponentInterface,
    EventSourceInterface):
  """This class creates events when a new value combination for
  a given list of match data pathes were found."""

  def __init__(
      self, aminerConfig, targetPathList, anomalyEventHandlers,
      persistenceId='Default', allowMissingValuesFlag=False,
      autoIncludeFlag=False, outputLogLine=True):
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
    self.targetPathList = targetPathList
    self.anomalyEventHandlers = anomalyEventHandlers
    self.allowMissingValuesFlag = allowMissingValuesFlag
    self.autoIncludeFlag = autoIncludeFlag
    self.outputLogLine = outputLogLine
    self.aminerConfig = aminerConfig
    self.persistenceId = persistenceId

    self.persistenceFileName = AMinerConfig.build_persistence_file_name(
        aminerConfig, self.__class__.__name__, persistenceId)
    self.nextPersistTime = None
    self.loadPersistencyData()
    PersistencyUtil.addPersistableComponent(self)


  def loadPersistencyData(self):
    """Load the persistency data from storage."""
    persistenceData = PersistencyUtil.loadJson(self.persistenceFileName)
    if persistenceData is None:
      self.knownValuesSet = set()
    else:
# Set and tuples were stored as list of lists. Transform the inner
# lists to tuples to allow hash operation needed by set.
      self.knownValuesSet = set([tuple(record) for record in persistenceData])


  def receive_atom(self, logAtom):
    """Receive on parsed atom and the information about the parser
    match.
    @return True if a value combination was extracted and checked
    against the list of known combinations, no matter if the checked
    values were new or not."""
    matchDict = logAtom.parserMatch.getMatchDictionary()
    matchValueList = []
    eventData = dict()
    for targetPath in self.targetPathList:
      matchElement = matchDict.get(targetPath, None)
      if matchElement is None:
        if not self.allowMissingValuesFlag:
          return False
        matchValueList.append(None)
      else:
        matchValueList.append(matchElement.matchObject)

    matchValueTuple = tuple(matchValueList)
    affectedLogAtomValues = []
    for matchValue in matchValueList:
      if isinstance(matchValue, bytes):
        matchValue = matchValue.decode()
      affectedLogAtomValues.append(matchValue)
    if matchValueTuple not in self.knownValuesSet:
      if self.autoIncludeFlag:
        self.knownValuesSet.add(matchValueTuple)
        if self.nextPersistTime is None:
          self.nextPersistTime = time.time()+600

      analysisComponent = dict()
      analysisComponent['AffectedLogAtomValues'] = affectedLogAtomValues
      eventData['AnalysisComponent'] = analysisComponent
      if self.outputLogLine:
        originalLogLinePrefix = self.aminerConfig.configProperties.get(CONFIG_KEY_LOG_LINE_PREFIX)
        if originalLogLinePrefix is None:
          originalLogLinePrefix = ''
        sortedLogLines = [str(matchValueTuple)+os.linesep+originalLogLinePrefix+repr(logAtom.rawData)]
      else:
        sortedLogLines = [str(matchValueTuple)]
      for listener in self.anomalyEventHandlers:
        listener.receiveEvent(
            'Analysis.%s' % self.__class__.__name__, 'New value combination(s) detected',
            sortedLogLines, eventData, logAtom, self)
    return True


  def get_time_trigger_class(self):
    """Get the trigger class this component should be registered
    for. This trigger is used only for persistency, so real-time
    triggering is needed."""
    return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

  def do_timer(self, triggerTime):
    """Check current ruleset should be persisted"""
    if self.nextPersistTime is None:
      return 600

    delta = self.nextPersistTime-triggerTime
    if delta < 0:
      self.doPersist()
      delta = 600
    return delta


  def doPersist(self):
    """Immediately write persistence data to storage."""
    PersistencyUtil.storeJson(
        self.persistenceFileName, list(self.knownValuesSet))
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
    if whitelistingData != None:
      raise Exception('Whitelisting data not understood by this detector')
    self.knownValuesSet.add(eventData[1])
    return 'Whitelisted path(es) %s with %s in %s' % (
        ', '.join(self.targetPathList), eventData[1], sortedLogLines[0])
