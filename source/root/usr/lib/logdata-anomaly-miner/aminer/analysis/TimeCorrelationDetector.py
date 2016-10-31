from datetime import datetime
import random
import time

from aminer import AMinerConfig
from aminer.AMinerUtils import AnalysisContext
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

  def __init__(self, aminerConfig, parallelCheckCount, correlationTestCount, maxFailCount, anomalyEventHandlers, peristenceId='Default'):
    """Initialize the detector. This will also trigger reading
    or creation of persistence storage location.
    @param parallelCheckCount number of rule detection checks
    to run in parallel.
    @param correlationTestCount number of tests to perform on a rule under
    test.
    @param maxFailCount maximal number of test failures so that
    rule is still eligible for reporting."""
    self.lastTimestamp=0.0
    self.parallelCheckCount=parallelCheckCount
    self.correlationTestCount=correlationTestCount
    self.maxFailCount=maxFailCount
    self.anomalyEventHandlers=anomalyEventHandlers
    self.maxRuleAttributes=5
    self.lastUnhandledMatch=None
    self.nextPersistTime=None
    self.totalRecords=0

    PersistencyUtil.addPersistableComponent(self)
    self.persistenceFileName=AMinerConfig.buildPersistenceFileName(
        aminerConfig, 'TimeCorrelationDetector', peristenceId)
    persistenceData=PersistencyUtil.loadJson(self.persistenceFileName)
    if persistenceData==None:
      self.featureList=[]
      self.eventCountTable=[0]*parallelCheckCount*parallelCheckCount*2
      self.eventDeltaTable=[0]*parallelCheckCount*parallelCheckCount*2
#   else:
#     self.knownPathSet=set(persistenceData)


  def receiveAtom(self, logAtom):
    timestamp=logAtom.getTimestamp()
    if timestamp==None: timestamp=time.time()
    if timestamp<self.lastTimestamp:
      for listener in self.anomalyEventHandlers:
        listener.receiveEvent('Analysis.%s' % self.__class__.__name__,
            'Logdata not sorted: last %s, current %s' % (self.lastTimestamp, timestamp),
            [logAtom.rawData], logAtom, self)
      return
    self.lastTimestamp=timestamp
    parserMatch=logAtom.parserMatch

    self.totalRecords+=1
    featuresFoundList=[]

    for feature in self.featureList:
      if feature.rule.match(parserMatch):
        feature.triggerCount+=1
        self.updateTablesForFeature(feature, timestamp)
        featuresFoundList.append(feature)

    if len(self.featureList)<self.parallelCheckCount:
      if (random.randint(0, 1)!=0) and (self.lastUnhandledMatch!=None):
        parserMatch=self.lastUnhandledMatch
      newRule=self.createRandomRule(parserMatch)
      newFeature=CorrelationFeature(newRule, len(self.featureList), timestamp)
      self.featureList.append(newFeature)
      newFeature.triggerCount=1
      self.updateTablesForFeature(newFeature, timestamp)
      featuresFoundList.append(newFeature)

    for feature in featuresFoundList:
      feature.lastTriggerTime=timestamp

    if len(featuresFoundList)==0:
      self.lastUnhandledMatch=parserMatch
    elif self.nextPersistTime==None:
      self.nextPersistTime=time.time()+600

    if (self.totalRecords%0x10000)==0:
      for listener in self.anomalyEventHandlers:
        listener.receiveEvent('Analysis.%s' % self.__class__.__name__,
            'Correlation report', [self.analysisStatusToString()],
            parserMatch, self)
      self.resetStatistics()


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
#     PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
      self.nextPersistTime=None
      delta=600
    return(delta)


  def doPersist(self):
    """Immediately write persistence data to storage."""
#   PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
    self.nextPersistTime=None


  def createRandomRule(self, parserMatch):
    subRules=[]
    allKeys=parserMatch.getMatchDictionary().keys()
    attributeCount=getLogInt(self.maxRuleAttributes)+1
    while attributeCount>0:
      keyPos=random.randint(0, len(allKeys)-1)
      keyName=allKeys[keyPos]
      allKeys=allKeys[:keyPos]+allKeys[keyPos+1:]
      keyValue=parserMatch.getMatchDictionary().get(keyName).matchObject
# Not much sense handling parsed date values in this implementation,
# so just ignore this attribute.
      if (isinstance(keyValue, tuple)) and (isinstance(keyValue[0], datetime)):
        if len(allKeys)==0: break
        continue

      attributeCount-=1
      ruleType=random.randint(0, 1)
      if ruleType==0:
        subRules.append(Rules.PathExistsMatchRule(keyName))
      elif ruleType==1:
        subRules.append(Rules.ValueMatchRule(keyName, keyValue))
      else:
        raise Exception('Invalid rule type')
      if len(allKeys)==0: break

    if len(subRules)>1: return(Rules.AndMatchRule(subRules))
    return(subRules[0])


  def updateTablesForFeature(self, targetFeature, timestamp):
    """Assume that this event was the effect of a previous cause-related
    event. Loop over all cause-related features (rows) to search
    for matches."""
    featureTablePos=(targetFeature.index<<1)
    for feature in self.featureList:
      delta=timestamp-feature.lastTriggerTime
      if delta<=10.0:
        self.eventCountTable[featureTablePos]+=1
        self.eventDeltaTable[featureTablePos]+=int(delta*1000)
      featureTablePos+=(self.parallelCheckCount<<1)

    featureTablePos=((targetFeature.index*self.parallelCheckCount)<<1)+1
    for feature in self.featureList:
      delta=timestamp-feature.lastTriggerTime;
      if delta<=10.0:
        self.eventCountTable[featureTablePos]+=1
        self.eventDeltaTable[featureTablePos]-=int(delta*1000)
      featureTablePos+=2


  def analysisStatusToString(self):
    result=''
    for feature in self.featureList:
      triggerCount=feature.triggerCount
      result+='%s (%d) e=%d:' % (feature.rule, feature.index, triggerCount)
      statPos=(self.parallelCheckCount*feature.index)<<1
      for featurePos in range(0, len(self.featureList)):
        eventCount=self.eventCountTable[statPos]
        ratio='-'
        if triggerCount!=0:
          ratio='%.2e' % (float(eventCount)/triggerCount)
        delta='-'
        if eventCount!=0:
          delta='%.2e' % (float(self.eventDeltaTable[statPos])*0.001/eventCount)
        result+='\n  %d: {c=%#6d r=%s dt=%s' % (featurePos, eventCount, ratio, delta)
        statPos+=1
        eventCount=self.eventCountTable[statPos]
        ratio='-'
        if triggerCount!=0:
          ratio='%.2e' % (float(eventCount)/triggerCount)
        delta='-'
        if eventCount!=0:
          delta='%.2e' % (float(self.eventDeltaTable[statPos])*0.001/eventCount)
        result+=' c=%#6d r=%s dt=%s}' % (eventCount, ratio, delta)
        statPos+=1
      result+='\n'
    return(result)

  def resetStatistics(self):
    for feature in self.featureList:
      feature.creationTime=0
      feature.lastTriggerTime=0
      feature.triggerCount=0
    self.eventCountTable=[0]*self.parallelCheckCount*self.parallelCheckCount*2
    self.eventDeltaTable=[0]*self.parallelCheckCount*self.parallelCheckCount*2


class CorrelationFeature:
  def __init__(self, rule, index, creationTime):
    self.rule=rule
    self.index=index
    self.creationTime=creationTime
    self.lastTriggerTime=0.0
    self.triggerCount=0
