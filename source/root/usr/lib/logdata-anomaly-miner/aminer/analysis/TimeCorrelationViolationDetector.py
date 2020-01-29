"""This module defines a detector for time correlation rules."""

import time

from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.input import AtomHandlerInterface
from aminer.util import LogarithmicBackoffHistory
from aminer.util import PersistencyUtil
from aminer.util import TimeTriggeredComponentInterface
from aminer.analysis import Rules
from datetime import datetime

class TimeCorrelationViolationDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
  """This class creates events when one of the given time correlation
  rules is violated. This is used to implement checks as depicted
  in http://dx.doi.org/10.1016/j.cose.2014.09.006"""

  def __init__(self, aminerConfig, ruleset, anomalyEventHandlers, persistenceId='Default'):
    """Initialize the detector. This will also trigger reading
    or creation of persistence storage location.
    @param ruleset a list of MatchRule rules with appropriate
    CorrelationRules attached as actions."""
    self.eventClassificationRuleset = ruleset
    self.anomalyEventHandlers = anomalyEventHandlers
    self.nextPersistTime = time.time()+600.0
    self.historyAEvents = []
    self.historyBEvents = []

    eventCorrelationSet = set()
    for rule in self.eventClassificationRuleset:
      if rule.matchAction.artefactARules is not None:
        eventCorrelationSet |= set(rule.matchAction.artefactARules)
      if rule.matchAction.artefactBRules is not None:
        eventCorrelationSet |= set(rule.matchAction.artefactBRules)
    self.eventCorrelationRuleset = list(eventCorrelationSet)

    PersistencyUtil.addPersistableComponent(self)
    self.persistenceFileName = AMinerConfig.buildPersistenceFileName(
        aminerConfig, 'TimeCorrelationViolationDetector', persistenceId)
#    persistenceData = PersistencyUtil.loadJson(self.persistenceFileName)
#   if persistenceData is None:
#     self.knownPathSet = set()
#   else:
#     self.knownPathSet = set(persistenceData)


  def receiveAtom(self, logAtom):
    """Receive a parsed atom and check all the classification
    rules, that will trigger correlation rule evaluation and event
    triggering on violations."""
    self.lastLogAtom = logAtom
    for rule in self.eventClassificationRuleset:
      rule.match(logAtom)


  def getTimeTriggerClass(self):
    """Get the trigger class this component should be registered
    for. This trigger is used mainly for persistency, so real-time
    triggering is needed. Use also real-time triggering for analysis:
    usually events for violations (timeouts) are generated when
    receiving newer atoms. This is just the fallback periods of
    input silence."""
    return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

  def doTimer(self, triggerTime):
    """Check for any rule violations and if the current ruleset
    should be persisted."""
# Persist the state only quite infrequently: As most correlation
# rules react in timeline of seconds, the persisted data will most
# likely be unsuitable to catch lost events. So persistency is
# mostly to capture the correlation rule context, e.g. the history
# of loglines matched before.
    if self.nextPersistTime-triggerTime < 0:
      self.doPersist()

# Check all correlation rules, generate single events for each
# violated rule, possibly containing multiple records. As we might
# be processing historic data, the timestamp last seen is unknown
# here. Hence rules not receiving newer events might not notice
# for a long time, that they hold information about correlation
# impossible to fulfil. Take the newest timestamp of any rule
# and use it for checking.
    eventData = dict()
    newestTimestamp = 0.0
    for rule in self.eventCorrelationRuleset:
      newestTimestamp = max(newestTimestamp, rule.lastTimestampSeen)

    for rule in self.eventCorrelationRuleset:
      checkResult = rule.checkStatus(newestTimestamp)
      if checkResult is None:
        continue
      self.lastLogAtom.atomTime = triggerTime
      for listener in self.anomalyEventHandlers:
        listener.receiveEvent('Analysis.%s' % self.__class__.__name__, \
            'Correlation rule "%s" violated' % rule.ruleId, [checkResult[0]], \
            eventData, self.lastLogAtom, self)
    return 10.0


  def doPersist(self):
    """Immediately write persistence data to storage."""
#   PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
    self.nextPersistTime = time.time()+600.0


class EventClassSelector(Rules.MatchAction):
  """This match action selects one event class by adding it to
  to a MatchRule. Itthen triggers the appropriate CorrelationRules."""
  def __init__(self, actionId, artefactARules, artefactBRules):
    self.actionId = actionId
    self.artefactARules = artefactARules
    self.artefactBRules = artefactBRules

  def matchAction(self, logAtom):
    """This method is invoked if a rule rule has matched.
    @param logAtom the parser MatchElement that was also matching
    the rules."""
    if self.artefactARules is not None:
      for aRule in self.artefactARules:
        aRule.updateArtefactA(self, logAtom)
    if self.artefactBRules is not None:
      for bRule in self.artefactBRules:
        bRule.updateArtefactB(self, logAtom)


class CorrelationRule:
  """This class defines a correlation rule to match artefacts
  A and B, where a hidden event A* always triggers at least one
  artefact A and the the hidden event B*, thus triggering also
  at least one artefact B."""
  def __init__(self, ruleId, minTimeDelta, maxTimeDelta, maxArtefactsAForSingleB=1,
               artefactMatchParameters=None):
    """Create the correlation rule.
    @param artefactMatchParameters if not none, two artefacts
    A and B will be only treated as correlated when all the
    parsed artefact attributes identified by the list of attribute
    path tuples match.
    @param minTimeDelta minimal delta in seconds, that artefact
    B may be observed after artefact A. Negative values are allowed
    as artefact B may be found before A.
    """
    self.ruleId = ruleId
    self.minTimeDelta = minTimeDelta
    self.maxTimeDelta = maxTimeDelta
    self.maxArtefactsAForSingleB = maxArtefactsAForSingleB
    self.artefactMatchParameters = artefactMatchParameters
    self.historyAEvents = []
    self.historyBEvents = []
    self.lastTimestampSeen = 0.0
    self.correlationHistory = LogarithmicBackoffHistory(10)


  def updateArtefactA(self, selector, logAtom):
    """Append entry to the event history A."""
    historyEntry = self.prepareHistoryEntry(selector, logAtom)
# FIXME: Check if event A could be discarded immediately.
    self.historyAEvents.append(historyEntry)


  def updateArtefactB(self, selector, logAtom):
    """Append entry to the event history B."""
    historyEntry = self.prepareHistoryEntry(selector, logAtom)
# FIXME: Check if event B could be discarded immediately.
    self.historyBEvents.append(historyEntry)


  def checkStatus(self, newestTimestamp, maxViolations=20):
    """@return None if status is OK. Returns a tuple containing
    a descriptive message and a list of violating log data lines
    on error."""

# FIXME: This part of code would be good target to be implemented
# as native library with optimized algorithm in future.
    aPos = 0
    checkRange = len(self.historyAEvents)
    violationLogs = []
    violationMessage = ''
    numViolations = 0
    while aPos < checkRange:
      deleted = False
      checkRange = len(self.historyAEvents)
      aEvent = self.historyAEvents[aPos]
      if aEvent is None:
        continue
      aEventTime = aEvent[0]
      bPos = 0
      while bPos < len(self.historyBEvents):
        bEvent = self.historyBEvents[bPos]
        if bEvent is None:
          continue
        bEventTime = bEvent[0]
        delta = bEventTime-aEventTime
        if delta < self.minTimeDelta:
# See if too early, if yes go to next element. As we will not
# check again any older aEvents in this loop, skip all bEvents
# up to this position in future runs.
          if bPos < len(self.historyBEvents):
            violationLine = aEvent[3].matchElement.matchString
            if isinstance(violationLine, bytes):
              violationLine = violationLine.decode("utf-8")
              if numViolations <= maxViolations:
                violationMessage += 'FAIL: B-Event for \"%s\" (%s) was found too early!\n' % (violationLine, aEvent[2].actionId)
              violationLogs.append(violationLine)
              del self.historyAEvents[aPos]
              del self.historyBEvents[bPos]
              deleted = True
              checkRange = checkRange - 1
              numViolations = numViolations + 1
              break
          continue
# Too late, no other bEvent may match this aEvent
        if delta > self.maxTimeDelta:
          violationLine = aEvent[3].matchElement.matchString
          if isinstance(violationLine, bytes):
            violationLine = violationLine.decode("utf-8")
            if numViolations <= maxViolations:
              violationMessage += 'FAIL: B-Event for \"%s\" (%s) was not found in time!\n' % (violationLine, aEvent[2].actionId)
            violationLogs.append(violationLine)
            del self.historyAEvents[aPos]
            del self.historyBEvents[bPos]
            deleted = True
            checkRange = checkRange - 1
            numViolations = numViolations + 1
          break
# So time range is OK, see if match parameters are also equal.
        checkPos = 4
        violationFound = False
        for checkPos in range(4, len(aEvent)):
          if aEvent[checkPos] != bEvent[checkPos]:
            violationLine = aEvent[3].matchElement.matchString
            if isinstance(violationLine, bytes):
              violationLine = violationLine.decode("utf-8")
              if numViolations <= maxViolations:
                violationMessage += 'FAIL: \"%s\" (%s) %s is not equal %s\n' % (
                  violationLine, aEvent[2].actionId, aEvent[checkPos], bEvent[checkPos])
              violationLogs.append(violationLine)
              del self.historyAEvents[aPos]
              del self.historyBEvents[bPos]
              deleted = True
              checkRange = checkRange - 1
              numViolations = numViolations + 1
              violationFound = True
            break
        checkPos = checkPos+1
        if violationFound:
          continue

# We want to keep a history of good matches to ease diagnosis
# of correlation failures. Keep information about current line
# for reference.
        self.correlationHistory.addObject((aEvent[3].matchElement.matchString, aEvent[2].actionId, \
          bEvent[3].matchElement.matchString, bEvent[2].actionId))
        del self.historyAEvents[aPos]
        del self.historyBEvents[bPos]
        deleted = True
        checkRange = checkRange - 1
        bPos = bPos + 1
      if deleted == False:
        aPos = aPos + 1
# After checking all aEvents before aPos were cleared, otherwise
# they violate a correlation rule.
    for aPos in range(0, checkRange):
      aEvent = self.historyAEvents[aPos]
      if aEvent is None:
        continue
      delta = newestTimestamp - aEvent[0]
      if delta > self.maxTimeDelta:
        violationLine = aEvent[3].matchElement.matchString
        if isinstance(violationLine, bytes):
          violationLine = violationLine.decode("utf-8")
          if numViolations <= maxViolations:
            violationMessage += 'FAIL: B-Event for \"%s\" (%s) was not found in time!\n' % (violationLine, aEvent[2].actionId)
          violationLogs.append(violationLine)
          del self.historyAEvents[aPos]
          deleted = True
          checkRange = checkRange - 1
          numViolations = numViolations + 1
        break
      
    if numViolations > maxViolations:
      violationMessage += '... (%d more)\n' % (numViolations-maxViolations)
    if numViolations != 0 and len(self.correlationHistory.getHistory()) > 0:
      violationMessage += 'Historic examples:\n'
      for record in self.correlationHistory.getHistory():
        violationMessage += '  "%s" (%s) ==> "%s" (%s)\n' % (record[0].decode(), 
        record[1], record[2].decode(), record[3])

    if numViolations == 0:
      return None
    return (violationMessage, violationLogs)


  def prepareHistoryEntry(self, selector, logAtom):
    """Return a history entry for a parser match."""
    parserMatch = logAtom.parserMatch
    length = 4
    if self.artefactMatchParameters is not None:
      length += len(self.artefactMatchParameters)
    result = [None]*length
    result[0] = logAtom.getTimestamp()
    result[1] = 0
    result[2] = selector
    result[3] = parserMatch

    if result[0] is None:
      result[0] = datetime.fromtimestamp(time.time())
    if isinstance(result[0], datetime):
      result[0] = (result[0]-datetime.fromtimestamp(0)).total_seconds()

    if result[0] < self.lastTimestampSeen:
      raise Exception('Unsorted!')
    self.lastTimestampSeen = result[0]

    if self.artefactMatchParameters is not None:
      pos = 4
      vDict = parserMatch.getMatchDictionary()
      for artefactMatchParameter in self.artefactMatchParameters:
        for paramPath in artefactMatchParameter:
          matchElement = vDict.get(paramPath, None)
          if matchElement is not None:
            result[pos] = matchElement.matchObject
            pos += 1
    return result
