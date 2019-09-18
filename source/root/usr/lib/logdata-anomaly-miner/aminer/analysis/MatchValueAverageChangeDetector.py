"""This module defines a detector that reports diverges from
an average."""

import time
import os

from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.input import AtomHandlerInterface
from aminer.util import PersistencyUtil
from aminer.util import TimeTriggeredComponentInterface

class MatchValueAverageChangeDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
  """This detector calculates the average of a given list of values
  to monitor and reports if the average of the latest diverges
  significantly from the values observed before."""

  def __init__(self, aminerConfig, anomalyEventHandlers, timestampPath,
               analyzePathList, minBinElements, minBinTime, syncBinsFlag=True,
               debugMode=False, persistenceId='Default'):
    """Initialize the detector. This will also trigger reading
    or creation of persistence storage location.
    @param timestampPath if not None, use this path value for
    timestamp based bins.
    @param analyzePathList list of match pathes to analyze in
    this detector.
    @param minBinElements evaluate the latest bin only after at
    least that number of elements was added to it.
    @param minBinTime evaluate the latest bin only when the first
    element is received after minBinTime has elapsed.
    @param syncBinsFlag if true the bins of all analyzed path values
    have to be filled enough to trigger analysis.
    @param debugMode if true, generate an analysis report even
    when average of last bin was within expected range."""
    self.anomalyEventHandlers = anomalyEventHandlers
    self.timestampPath = timestampPath
    self.minBinElements = minBinElements
    self.minBinTime = minBinTime
    self.syncBinsFlag = syncBinsFlag
    self.debugMode = debugMode
    self.nextPersistTime = None

    PersistencyUtil.addPersistableComponent(self)
    self.persistenceFileName = AMinerConfig.buildPersistenceFileName(aminerConfig, \
      'MatchValueAverageChangeDetector', persistenceId)
    persistenceData = PersistencyUtil.loadJson(self.persistenceFileName)
    if persistenceData is None:
      self.statData = []
      for path in analyzePathList:
        self.statData.append((path, [],))
#   else:
#     self.knownPathSet = set(persistenceData)


  def receiveAtom(self, logAtom):
    """Sends summary to all event handlers."""
    parserMatch = logAtom.parserMatch
    valueDict = parserMatch.getMatchDictionary()

    timestampValue = logAtom.getTimestamp()
    if self.timestampPath is not None:
      matchValue = valueDict.get(self.timestampPath)
      if matchValue is None:
        return
      timestampValue = matchValue.matchObject[1]

    analysisSummary = ''
    if self.syncBinsFlag:
      readyForAnalysisFlag = True
      for (path, statData) in self.statData:
        match = valueDict.get(path, None)
        if match is None:
          readyForAnalysisFlag = (readyForAnalysisFlag and self.update(statData, \
            timestampValue, None))
        else:
          readyForAnalysisFlag = (readyForAnalysisFlag and self.update(statData, \
            timestampValue, match.matchObject))

      if readyForAnalysisFlag:
        for (path, statData) in self.statData:
          analysisData = self.analyze(statData)
          if analysisData is not None:
            if analysisSummary == '':
              analysisSummary += '"%s": %s' % (path, analysisData)
            else:
              analysisSummary += os.linesep
              analysisSummary += '  "%s": %s' % (path, analysisData)
            

        if self.nextPersistTime is None:
          self.nextPersistTime = time.time()+600
    else:
      raise Exception('FIXME: not implemented')

    if analysisSummary:
      res = [''] * statData[2][0]
      res[0] = analysisSummary
      for listener in self.anomalyEventHandlers:
        listener.receiveEvent('Analysis.%s' % self.__class__.__name__, \
            'Statistical data report', res, logAtom, \
            self)


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


  def update(self, statData, timestampValue, value):
    """Update the collected statistics data.
    @param value if value not None, check only conditions if current
    bin is full enough.
    @return true if the bin is full enough to perform an analysis."""

    if value is not None:
      if not statData:
# Append timestamp, k-value, old-bin (n, sum, sum2, avg, variance),
# current-bin (n, sum, sum2)
        statData.append(timestampValue)
        statData.append(value)
        statData.append(None)
        statData.append((1, 0.0, 0.0,))
      else:
        delta = value-statData[1]
        binValues = statData[3]
        statData[3] = (binValues[0]+1, binValues[1]+delta, binValues[2]+delta*delta)

    if not statData:
      return False
    if statData[3][0] < self.minBinElements:
      return False
    if self.timestampPath is not None:
      return timestampValue-statData[0] >= self.minBinTime
    return True


  def analyze(self, statData):
    """Perform the analysis and progress from the last bin to
    the next one.
    @return None when statistical data was as expected and debugging
    is disabled."""

    currentBin = statData[3]
    currentAverage = currentBin[1]/currentBin[0]
    currentVariance = (currentBin[2]-(currentBin[1]*currentBin[1])/currentBin[0])/(currentBin[0]-1)
# Append timestamp, k-value, old-bin (n, sum, sum2, avg, variance),
# current-bin (n, sum, sum2)

    oldBin = statData[2]
    if oldBin is None:
      statData[2] = (currentBin[0], currentBin[1], currentBin[2], currentAverage, currentVariance,)
      statData[3] = (0, 0.0, 0.0)
      if self.debugMode:
        return 'Initial: n = %d, avg = %s, var = %s' % (currentBin[0], \
          currentAverage+statData[1], currentVariance)
    else:
      totalN = oldBin[0]+currentBin[0]
      totalSum = oldBin[1]+currentBin[1]
      totalSum2 = oldBin[2]+currentBin[2]

      statData[2] = (totalN, totalSum, totalSum2, totalSum/totalN, \
          (totalSum2-(totalSum*totalSum)/totalN)/(totalN-1))
      statData[3] = (0, 0.0, 0.0)

      if (currentVariance > 2*oldBin[4]) or (abs(currentAverage-oldBin[3]) > oldBin[4]) \
         or self.debugMode:
        return 'Change: new: n = %d, avg = %s, var = %s; old: n = %d, avg = %s, var = %s' % \
               (currentBin[0], currentAverage+statData[1], currentVariance, oldBin[0], \
                oldBin[3]+statData[1], oldBin[4])
    return None
