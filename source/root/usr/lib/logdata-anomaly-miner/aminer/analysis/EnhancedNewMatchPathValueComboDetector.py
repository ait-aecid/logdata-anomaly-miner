"""This file defines the EnhancedNewMatchPathValueComboDetector
detector to extract values from LogAtoms and check, if the value
combination was already seen before."""

import time
import os

from aminer.analysis.NewMatchPathValueComboDetector import NewMatchPathValueComboDetector
from aminer.util import PersistencyUtil
from datetime import datetime
from aminer.analysis import CONFIG_KEY_LOG_LINE_PREFIX

class EnhancedNewMatchPathValueComboDetector(NewMatchPathValueComboDetector):
  """This class creates events when a new value combination for
  a given list of match data pathes were found. It is similar
  to the NewMatchPathValueComboDetector basic detector but also
  provides support for storing meta information about each detected
  value combination, e.g.
  * the first time a tuple was detected using the LogAtom default
    timestamp.
  * the last time a tuple was seen
  * the number of times the tuple was seen
  * user data for annotation.
  Due to the additional features, this detector is slower than
  the basic detector."""

  def __init__(
      self, aminerConfig, targetPathList, anomalyEventHandlers,
      persistenceId='Default', allowMissingValuesFlag=False,
      autoIncludeFlag=False, tupleTransformationFunction=None, outputLogLine=True):
    """Initialize the detector. This will also trigger reading
    or creation of persistence storage location.
    @param targetPathList the list of values to extract from each
    match to create the value combination to be checked.
    @param allowMissingValuesFlag when set to True, the detector
    will also use matches, where one of the pathes from targetPathList
    does not refer to an existing parsed data object.
    @param autoIncludeFlag when set to True, this detector will
    report a new value only the first time before including it
    in the known values set automatically.
    @param tupleTransformationFunction when not None, this function
    will be invoked on each extracted value combination list to
    transform it. It may modify the list directly or create a
    new one to return it."""
    super(EnhancedNewMatchPathValueComboDetector, self).__init__(
        aminerConfig, targetPathList, anomalyEventHandlers, persistenceId,
        allowMissingValuesFlag, autoIncludeFlag)
    self.tupleTransformationFunction = tupleTransformationFunction
    self.outputLogLine = outputLogLine
    self.aminerConfig = aminerConfig


  def loadPersistencyData(self):
    """Load the persistency data from storage."""
    self.knownValuesDict = {}
    persistenceData = PersistencyUtil.loadJson(self.persistenceFileName)
    if persistenceData != None:
# Dictionary and tuples were stored as list of lists. Transform
# the first lists to tuples to allow hash operation needed by set.
      for valueTuple, extraData in persistenceData:
        self.knownValuesDict[tuple(valueTuple)] = extraData


  def receiveAtom(self, logAtom):
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

    if self.tupleTransformationFunction != None:
      matchValueList = self.tupleTransformationFunction(matchValueList)
    matchValueTuple = tuple(matchValueList)
    matchValList = []
    for matchValue in matchValueList:
      if isinstance(matchValue, bytes):
        matchValue = matchValue.decode()
      matchValList.append(matchValue)
    eventData['matchValueList'] = matchValList
    currentTimestamp = logAtom.getTimestamp()
    if currentTimestamp is None:
      currentTimestamp = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
    if not isinstance(currentTimestamp, datetime) and not isinstance(currentTimestamp, str):
      currentTimestamp = datetime.fromtimestamp(currentTimestamp).strftime("%Y-%m-%d %H:%M:%S")
    extraData = self.knownValuesDict.get(matchValueTuple, None)
    if isinstance(currentTimestamp, datetime):
      currentTimestamp = currentTimestamp.strftime("%Y-%m-%d %H:%M:%S")
    if extraData != None:
      extraData[1] = currentTimestamp
      extraData[2] += 1
      eventData['extraData'] = extraData
    else:
      if isinstance(currentTimestamp, datetime):
        self.knownValuesDict[matchValueTuple] = [currentTimestamp.strftime("%Y-%m-%d %H:%M:%S"), currentTimestamp.strftime("%Y-%m-%d %H:%M:%S"), 1]
      else:
        self.knownValuesDict[matchValueTuple] = [currentTimestamp, currentTimestamp, 1]
    knownVals = []
    for knownVal in self.knownValuesDict:
      l = {}
      l['matchValue'] = str(knownVal)
      values = self.knownValuesDict[knownVal]
      l['timeFirstOccurrence'] = values[0]
      l['timeLastOccurence'] = values[1]
      l['numberOfOccurences'] = values[2]
      knownVals.append(l)
    eventData['knownValuesList'] = knownVals
    eventData['autoIncludeFlag'] = self.autoIncludeFlag
    eventData['persistenceId'] = self.persistenceId
    if (self.autoIncludeFlag and self.knownValuesDict.get(matchValueTuple, None)[2] is 1) or not self.autoIncludeFlag:
      for listener in self.anomalyEventHandlers:
        originalLogLinePrefix = self.aminerConfig.configProperties.get(CONFIG_KEY_LOG_LINE_PREFIX)
        if originalLogLinePrefix is None:
          originalLogLinePrefix = ''
        if self.outputLogLine:
          sortedLogLines = [str(self.knownValuesDict)+os.linesep+ 
          originalLogLinePrefix+repr(logAtom.rawData)]
        else:
          sortedLogLines = [str(self.knownValuesDict)]
        listener.receiveEvent(
          'Analysis.%s' % self.__class__.__name__, 'New value combination(s) detected',
          sortedLogLines, eventData, logAtom, self)
    if self.autoIncludeFlag:
      if self.nextPersistTime is None:
        self.nextPersistTime = time.time() + 600
    return True

  def doPersist(self):
    """Immediately write persistence data to storage."""
    persistencyData = []
    for dictRecord in self.knownValuesDict.items():
      persistencyData.append(dictRecord)
    PersistencyUtil.storeJson(self.persistenceFileName, persistencyData)
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
    currentTimestamp = datetime.fromtimestamp(eventData[0].getTimestamp()).strftime("%Y-%m-%d %H:%M:%S")
    self.knownValuesDict[eventData[1]] = [
        currentTimestamp, currentTimestamp, 1]
    return 'Whitelisted path(es) %s with %s in %s' % (
        ', '.join(self.targetPathList), eventData[1], sortedLogLines[0])

