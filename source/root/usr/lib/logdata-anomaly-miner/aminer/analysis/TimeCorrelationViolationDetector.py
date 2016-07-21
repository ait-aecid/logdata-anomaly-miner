import time

from aminer import AMinerConfig
from aminer.AMinerUtils import AnalysisContext
from aminer.parsing import ParsedAtomHandlerInterface
from aminer.util import LogarithmicBackoffHistory
from aminer.util import PersistencyUtil
from aminer.util import TimeTriggeredComponentInterface
import Rules

class TimeCorrelationViolationDetector(ParsedAtomHandlerInterface, TimeTriggeredComponentInterface):
  """This class creates events when one of the given time correlation
  rules is violated. This is used to implement checks as depicted
  in http://dx.doi.org/10.1016/j.cose.2014.09.006"""

  def __init__(self, aminerConfig, ruleset, anomalyEventHandlers, peristenceId='Default'):
    """Initialize the detector. This will also trigger reading
    or creation of persistence storage location.
    @param ruleset a list of MatchRule rules with appropriate
    CorrelationRules attached as actions."""
    self.eventClassificationRuleset=ruleset
    self.anomalyEventHandlers=anomalyEventHandlers
    self.nextPersistTime=time.time()+600.0
    self.historyAEvents=[]
    self.historyBEvents=[]

    eventCorrelationSet=set()
    for rule in self.eventClassificationRuleset:
      if rule.matchAction.artefactARules!=None:
        eventCorrelationSet|=set(rule.matchAction.artefactARules)
      if rule.matchAction.artefactBRules!=None:
        eventCorrelationSet|=set(rule.matchAction.artefactBRules)
    self.eventCorrelationRuleset=list(eventCorrelationSet)

    PersistencyUtil.addPersistableComponent(self)
    self.persistenceFileName=AMinerConfig.buildPersistenceFileName(
        aminerConfig, 'TimeCorrelationViolationDetector', peristenceId)
    persistenceData=PersistencyUtil.loadJson(self.persistenceFileName)
#   if persistenceData==None:
#     self.knownPathSet=set()
#   else:
#     self.knownPathSet=set(persistenceData)


  def receiveParsedAtom(self, atomData, match):
    """Receive a parsed atom and check all the classification
    rules, that will trigger correlation rule evaluation and event
    triggering on violations."""
    for rule in self.eventClassificationRuleset:
       rule.match(match)


  def getTimeTriggerClass(self):
    """Get the trigger class this component should be registered
    for. This trigger is used mainly for persistency, so real-time
    triggering is needed. Use also real-time triggering for analysis:
    usually events for violations (timeouts) are generated when
    receiving newer atoms. This is just the fallback periods of
    input silence."""
    return(AnalysisContext.TIME_TRIGGER_CLASS_REALTIME)

  def doTimer(self, time):
    """Check for any rule violations and if the current ruleset
    should be persisted."""
# Persist the state only quite infrequently: As most correlation
# rules react in timeline of seconds, the persisted data will most
# likely be unsuitable to catch lost events. So persistency is
# mostly to capture the correlation rule context, e.g. the history
# of loglines matched before.
    if(self.nextPersistTime-time<0): self.doPersist()

# Check all correlation rules, generate single events for each
# violated rule, possibly containing multiple records. As we might
# be processing historic data, the timestamp last seen is unknown
# here. Hence rules not receiving newer events might not notice
# for a long time, that they hold information about correlation
# impossible to fulfil. Take the newest timestamp of any rule
# and use it for checking.
    newestTimestamp=0.0
    for rule in self.eventCorrelationRuleset:
      newestTimestamp=max(newestTimestamp, rule.lastTimestampSeen)

    for rule in self.eventCorrelationRuleset:
      checkResult=rule.checkStatus(newestTimestamp)
      if checkResult==None: continue
      for listener in self.anomalyEventHandlers:
        listener.receiveEvent('Analysis.TimeCorrelationViolationDetector', 'Correlation rule "%s" violated' % rule.id, checkResult[1], checkResult[0])
    return(10.0)


  def doPersist(self):
    """Immediately write persistence data to storage."""
#   PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
    self.nextPersistTime=time.time()+600.0


class EventClassSelector(Rules.MatchAction):
  """This match action selects one event class by adding it to
  to a MatchRule. Itthen triggers the appropriate CorrelationRules."""
  def __init__(self, id, artefactARules, artefactBRules):
    self.id=id
    self.artefactARules=artefactARules
    self.artefactBRules=artefactBRules

  def matchAction(self, parserMatch):
    """This method is invoked if a rule rule has matched.
    @param parserMatch the parser MatchElement that was also matching
    the rules."""
    if self.artefactARules!=None:
      for aRule in self.artefactARules:
        aRule.updateArtefactA(self, parserMatch)
    if self.artefactBRules!=None:
      for bRule in self.artefactBRules:
        bRule.updateArtefactB(self, parserMatch)


class CorrelationRule:
  """This class defines a correlation rule to match artefacts
  A and B, where a hidden event A* always triggers at least one
  artefact A and the the hidden event B*, thus triggering also
  at least one artefact B."""
  def __init__(self, id, minTimeDelta, maxTimeDelta, maxArtefactsAForSingleB=1,
      artefactMatchParameters=None):
    """Create the correlation rule.
    @param artefactMatchParameters if not none, two artefacts
    A and B will be only treated as correlated when the all the
    parsed artefact attributes identified by the list of attribute
    path tuples match.
    @param minTimeDelta minimal delta in seconds, that artefact
    B may be observed after artefact A. Negative values are allowed
    as artefact B may be found before A.
    """
    self.id=id
    self.minTimeDelta=minTimeDelta
    self.maxTimeDelta=maxTimeDelta
    self.maxArtefactsAForSingleB=maxArtefactsAForSingleB
    self.artefactMatchParameters=artefactMatchParameters
    self.historyAEvents=[]
    self.historyBEvents=[]
    self.lastTimestampSeen=0.0
    self.correlationHistory=LogarithmicBackoffHistory(10)


  def updateArtefactA(self, selector, parserMatch):
    historyEntry=self.prepareHistoryEntry(selector, parserMatch)
# FIXME: Check if event A could be discarded immediately.
    self.historyAEvents.append(historyEntry)


  def updateArtefactB(self, selector, parserMatch):
    historyEntry=self.prepareHistoryEntry(selector, parserMatch)
# FIXME: Check if event B could be discarded immediately.
    self.historyBEvents.append(historyEntry)


  def checkStatus(self, newestTimestamp, maxViolations=20):
    """@return None if status is OK. Returns a tuple containing
    a descriptive message and a list of violating log data lines
    on error."""

# FIXME: This part of code would be good target to be implemented
# as native library with optimized algorithm in future.
    aPos=0
    bPosStart=0
    for aPos in range(0, len(self.historyAEvents)):
      aEvent=self.historyAEvents[aPos]
      aEventTime=aEvent[0]
      if newestTimestamp-aEventTime<=self.maxTimeDelta:
# This event is so new, that timewindow for related event has
# not expired yet.
        break

      matchFoundFlag=False
      for bPos in range(bPosStart, len(self.historyBEvents)):
        bEvent=self.historyBEvents[bPos]
        if bEvent==None: continue
        bEventTime=bEvent[0]
        delta=bEvent[0]-aEventTime
        if delta<self.minTimeDelta:
# See if too early, if yes go to next element. As we will not
# check again any older aEvents in this loop, skip all bEvents
# up to this position in future runs.
          bPosStart=bPos+1
          continue
# Too late, no other bEvent may match this aEvent
        if delta>self.maxTimeDelta: break
# So time range is OK, see if match parameters are also equal.
        checkPos=4
        for checkPos in range(4, len(aEvent)):
          if aEvent[checkPos]!=bEvent[checkPos]: break
        if checkPos!=len(aEvent): continue
# We found the match. Mark aEvent as done.
        self.historyAEvents[aPos]=None
# See how many eEvents this bEvent might collect. Clean it also
# when limit was reached.
        bEvent[1]+=1
        if bEvent[1]==self.maxArtefactsAForSingleB:
          self.historyBEvents[bPos]=None

# We want to keep a history of good matches to ease diagnosis
# of correlation failures. Keep information about current line
# for reference.
        self.correlationHistory.addObject((aEvent[3].matchElement.matchString, aEvent[2].id, bEvent[3].matchElement.matchString, bEvent[2].id))
        aPos+=1
        break

# After checking all aEvents before aPos were cleared, otherwise
# they violate a correlation rule.
    checkRange=aPos
    violationLogs=[]
    violationMessage=''
    numViolations=0
    for aPos in range(0, checkRange):
      aEvent=self.historyAEvents[aPos]
      if aEvent==None: continue
      numViolations+=1
      if numViolations>maxViolations: continue
      violationLine=aEvent[3].matchElement.matchString
      violationMessage+='FAIL: \"%s\" (%s)\n' % (violationLine, aEvent[2].id)
      violationLogs.append(violationLine)
    if numViolations>maxViolations:
      violationMessage+='... (%d more)\n' % (numViolations-maxViolations)
    if numViolations!=0:
      violationMessage+='Historic examples:\n'
      for record in self.correlationHistory.getHistory():
        violationMessage+='  "%s" (%s) ==> "%s" (%s)\n' % record

# Prune out all handled event records
    self.historyAEvents=self.historyAEvents[checkRange:]
    self.historyBEvents=self.historyBEvents[bPosStart:]
    if numViolations==0: return(None)
    return((violationMessage, violationLogs))


  def prepareHistoryEntry(self, selector, parserMatch):
    length=4
    if self.artefactMatchParameters!=None:
      length+=len(artefactMatchParameters)
    result=[None]*length
    result[0]=parserMatch.getDefaultTimestamp()
    result[1]=0
    result[2]=selector
    result[3]=parserMatch

    if result[0]<self.lastTimestampSeen:
      raise Exception('Unsorted!')
    self.lastTimestampSeen=result[0]

    if self.artefactMatchParameters!=None:
      pos=4
      vDict=parserMatch.getMatchDictionary()
      for paramPath in artefactMatchParameters:
        matchElement=vDict.get(paramPath, None)
        if matchElement!=None: 
          result[pos]=matchElement.matchObject
        pos+=1
    return(result)
