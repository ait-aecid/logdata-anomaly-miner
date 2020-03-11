"""This module defines a detector for time correlation between atoms."""

from datetime import datetime
import random
import time

import aminer
from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.analysis import Rules
from aminer.input import AtomHandlerInterface
from aminer.util import getLogInt
from aminer.util import PersistencyUtil
from aminer.util import TimeTriggeredComponentInterface

class TimeCorrelationDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
  """This class tries to find time correlation patterns between
  different log atoms. When a possible correlation rule is detected,
  it creates an event including the rules. This is useful to implement
  checks as depicted in http://dx.doi.org/10.1016/j.cose.2014.09.006."""

  def __init__(self, aminerConfig, parallelCheckCount, correlationTestCount, \
    maxFailCount, anomalyEventHandlers, persistenceId='Default', recordCountBeforeEvent=0x10000):
    """Initialize the detector. This will also trigger reading
    or creation of persistence storage location.
    @param parallelCheckCount number of rule detection checks
    to run in parallel.
    @param correlationTestCount number of unit to perform on a rule under
    test.
    @param maxFailCount maximal number of test failures so that
    rule is still eligible for reporting."""
    self.lastTimestamp = 0.0
    self.parallelCheckCount = parallelCheckCount
    self.correlationTestCount = correlationTestCount
    self.maxFailCount = maxFailCount
    self.anomalyEventHandlers = anomalyEventHandlers
    self.maxRuleAttributes = 5
    self.lastUnhandledMatch = None
    self.nextPersistTime = None
    self.totalRecords = 0
    self.recordCountBeforeEvent = recordCountBeforeEvent
    self.persistenceId = persistenceId

    PersistencyUtil.addPersistableComponent(self)
    self.persistenceFileName = AMinerConfig.build_persistence_file_name(
        aminerConfig, 'TimeCorrelationDetector', persistenceId)
    persistenceData = PersistencyUtil.loadJson(self.persistenceFileName)
    if persistenceData is None:
      self.featureList = []
      self.eventCountTable = [0]*parallelCheckCount*parallelCheckCount*2
      self.eventDeltaTable = [0]*parallelCheckCount*parallelCheckCount*2
#   else:
#     self.knownPathSet = set(persistenceData)


  def receiveAtom(self, logAtom):
    eventData = dict()
    timestamp = logAtom.getTimestamp()
    if timestamp is None:
      timestamp = datetime.utcnow()
    if isinstance(timestamp, datetime):
      timestamp = (timestamp.utcnow()-datetime.fromtimestamp(0)).total_seconds()
    if timestamp < self.lastTimestamp:
      for listener in self.anomalyEventHandlers:
        listener.receiveEvent('Analysis.%s' % self.__class__.__name__, \
            'Logdata not sorted: last %s, current %s' % (self.lastTimestamp, timestamp), \
            [logAtom.parserMatch.matchElement.annotateMatch('')], eventData, logAtom, self)
      return
    self.lastTimestamp = timestamp

    self.totalRecords += 1
    featuresFoundList = []

    for feature in self.featureList:
      if feature.rule.match(logAtom):
        feature.triggerCount += 1
        self.updateTablesForFeature(feature, timestamp)
        featuresFoundList.append(feature)

    if len(self.featureList) < self.parallelCheckCount:
      if (random.randint(0, 1) != 0) and (self.lastUnhandledMatch is not None):
        logAtom = self.lastUnhandledMatch
      newRule = self.createRandomRule(logAtom)
      if newRule is not None:
        newFeature = CorrelationFeature(newRule, len(self.featureList), timestamp)
        self.featureList.append(newFeature)
        newFeature.triggerCount = 1
        self.updateTablesForFeature(newFeature, timestamp)
        featuresFoundList.append(newFeature)

    for feature in featuresFoundList:
      feature.lastTriggerTime = timestamp

    if not featuresFoundList:
      self.lastUnhandledMatch = logAtom
    elif self.nextPersistTime is None:
      self.nextPersistTime = time.time()+600

    if (self.totalRecords%self.recordCountBeforeEvent) == 0:
      result = self.totalRecords * ['']
      result[0] = self.analysisStatusToString()

      featureList = []
      for feature in self.featureList:
        l = {}
        r = self.ruleToDict(feature.rule)
        l['Rule'] = r
        l['Index'] = feature.index
        l['CreationTime'] = feature.creationTime
        l['LastTriggerTime'] = feature.lastTriggerTime
        l['TriggerCount'] = feature.triggerCount
        featureList.append(l)

      analysisComponent = dict()
      analysisComponent['FeatureList'] = featureList
      analysisComponent['AnalysisStatus'] = result[0]
      analysisComponent['TotalRecords'] = self.totalRecords

      eventData['AnalysisComponent'] = analysisComponent
      for listener in self.anomalyEventHandlers:
        listener.receiveEvent('Analysis.%s' % self.__class__.__name__, \
            'Correlation report', result, \
            eventData, logAtom, self)
      self.resetStatistics()

  def ruleToDict(self, rule):
    r = {}
    r['Type'] = str(rule.__class__.__name__)
    for var in vars(rule):
      attr = getattr(rule, var)
      if isinstance(attr, list):
        l = []
        for v in attr:
          d = self.ruleToDict(v)
          d['Type'] = str(v.__class__.__name__)
          l.append(d)
        r['subRules'] = l
      else:
        r[var] = getattr(rule, var)
    return r

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
#     PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
      self.nextPersistTime = None
      delta = 600
    return delta


  def doPersist(self):
    """Immediately write persistence data to storage."""
#   PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
    self.nextPersistTime = None


  def createRandomRule(self, logAtom):
    """Create a random existing path rule or value match rule."""
    parserMatch = logAtom.parserMatch
    subRules = []
    allKeys = list(parserMatch.getMatchDictionary().keys())
    attributeCount = getLogInt(self.maxRuleAttributes)+1
    while attributeCount > 0:
      keyPos = random.randint(0, len(allKeys)-1)
      keyName = allKeys[keyPos]
      allKeys = allKeys[:keyPos]+allKeys[keyPos+1:]
      keyValue = parserMatch.getMatchDictionary().get(keyName).matchObject
# Not much sense handling parsed date values in this implementation,
# so just ignore this attribute.
      if (isinstance(keyValue, tuple)) and (isinstance(keyValue[0], datetime)):
        if not allKeys:
          break
        continue

      attributeCount -= 1
      ruleType = random.randint(0, 1)
      if ruleType == 0:
        subRules.append(Rules.PathExistsMatchRule(keyName))
      elif ruleType == 1:
        subRules.append(Rules.ValueMatchRule(keyName, keyValue))
      else:
        raise Exception('Invalid rule type')
      if not allKeys:
        break

    if len(subRules) > 1:
      return Rules.AndMatchRule(subRules)
    if len(subRules) > 0:
      return subRules[0]
    return None
    


  def updateTablesForFeature(self, targetFeature, timestamp):
    """Assume that this event was the effect of a previous cause-related
    event. Loop over all cause-related features (rows) to search
    for matches."""
    featureTablePos = (targetFeature.index << 1)
    for feature in self.featureList:
      delta = timestamp-feature.lastTriggerTime
      if delta <= 10.0:
        self.eventCountTable[featureTablePos] += 1
        self.eventDeltaTable[featureTablePos] += int(delta*1000)
      featureTablePos += (self.parallelCheckCount << 1)

    featureTablePos = ((targetFeature.index*self.parallelCheckCount) << 1)+1
    for feature in self.featureList:
      delta = timestamp-feature.lastTriggerTime
      if delta <= 10.0:
        self.eventCountTable[featureTablePos] += 1
        self.eventDeltaTable[featureTablePos] -= int(delta*1000)
      featureTablePos += 2


  def analysisStatusToString(self):
    """Get a string representation of all features."""
    result = ''
    for feature in self.featureList:
      triggerCount = feature.triggerCount
      result += '%s (%d) e = %d:' % (feature.rule, feature.index, triggerCount)
      statPos = (self.parallelCheckCount*feature.index) << 1
      for featurePos in range(0, len(self.featureList)):
        eventCount = self.eventCountTable[statPos]
        ratio = '-'
        if triggerCount != 0:
          ratio = '%.2e' % (float(eventCount)/triggerCount)
        delta = '-'
        if eventCount != 0:
          delta = '%.2e' % (float(self.eventDeltaTable[statPos])*0.001/eventCount)
        result += '\n  %d: {c = %#6d r = %s dt = %s' % (featurePos, eventCount, ratio, delta)
        statPos += 1
        eventCount = self.eventCountTable[statPos]
        ratio = '-'
        if triggerCount != 0:
          ratio = '%.2e' % (float(eventCount)/triggerCount)
        delta = '-'
        if eventCount != 0:
          delta = '%.2e' % (float(self.eventDeltaTable[statPos])*0.001/eventCount)
        result += ' c = %#6d r = %s dt = %s}' % (eventCount, ratio, delta)
        statPos += 1
      result += '\n'
    return result

  def resetStatistics(self):
    """Reset all features."""
    for feature in self.featureList:
      feature.creationTime = 0
      feature.lastTriggerTime = 0
      feature.triggerCount = 0
    self.eventCountTable = [0]*self.parallelCheckCount*self.parallelCheckCount*2
    self.eventDeltaTable = [0]*self.parallelCheckCount*self.parallelCheckCount*2


class CorrelationFeature:
  """This class defines a correlation feature."""
  def __init__(self, rule, index, creationTime):
    self.rule = rule
    self.index = index
    self.creationTime = creationTime
    self.lastTriggerTime = 0.0
    self.triggerCount = 0
