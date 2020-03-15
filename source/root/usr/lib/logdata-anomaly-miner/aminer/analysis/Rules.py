"""This package contains various classes to build check rulesets.
The ruleset also supports parallel rule evaluation, e.g. the two
rules "A and B and C" and "A and B and D" will only peform the
checks for A and B once, then performs check C and D and trigger
a match action."""

import datetime
import sys

from aminer.util import LogarithmicBackoffHistory
from aminer.util import ObjectHistory

from aminer.analysis.AtomFilters import SubhandlerFilter


class MatchAction(object):
  """This is the interface of all match actions."""
  def matchAction(self, logAtom):
    """This method is invoked if a rule rule has matched.
    @param logAtom the LogAtom matching the rules."""
    raise Exception('Interface called')


class EventGenerationMatchAction(MatchAction):
  """This generic match action forwards information about a rule
  match on parsed data to a list of event handlers."""
  def __init__(self, eventType, eventMessage, eventHandlers):
    self.eventType = eventType
    self.eventMessage = eventMessage
    self.eventHandlers = eventHandlers

  def matchAction(self, logAtom):
    eventData = dict()
    for handler in self.eventHandlers:
      handler.receiveEvent(
          self.eventType, self.eventMessage, [logAtom.parserMatch.matchElement.annotateMatch('')], eventData, logAtom, self)


class AtomFilterMatchAction(MatchAction, SubhandlerFilter):
  """This generic match rule forwards all rule matches to a list
  of AtomHandlerInterface instaces using the analysis.AtomFilters.SubhandlerFilter."""
  def __init__(self, subhandlerList, stop_when_handled_flag=False):
    SubhandlerFilter.__init__(self, subhandlerList, stop_when_handled_flag)

  def matchAction(self, logAtom):
    self.receive_atom(logAtom)


class MatchRule(object):
  """This is the interface of all match rules."""
  def match(self, logAtom):
    """Check if this rule matches. On match an optional matchAction
    could be triggered."""
    raise Exception('Interface called on %s' % self)


class AndMatchRule(MatchRule):
  """This class provides a rule to match all subRules (logical
  and)"""

  def __init__(self, subRules, matchAction=None):
    """Create the rule.
    @param matchAction if None, no action is performed."""
    self.subRules = subRules
    self.matchAction = matchAction

  def match(self, logAtom):
    """Check if this rule matches. Rule evaluation will stop when
    the first match fails. If a matchAction is attached to this
    rule, it will be invoked at the end of all checks.
    @return True when all subrules matched."""
    for rule in self.subRules:
      if not rule.match(logAtom):
        return False
    if self.matchAction != None:
      self.matchAction.matchAction(logAtom)
    return True

  def __str__(self):
    result = ''
    preamble = ''
    for matchElement in self.subRules:
      result += '%s(%s)' % (preamble, matchElement)
      preamble = ' and '
    return result

class OrMatchRule(MatchRule):
  """This class provides a rule to match any subRules (logical
  or)"""

  def __init__(self, subRules, matchAction=None):
    """Create the rule.
    @param matchAction if None, no action is performed."""
    self.subRules = subRules
    self.matchAction = matchAction

  def match(self, logAtom):
    """Check if this rule matches. Rule evaluation will stop when
    the first match succeeds. If a matchAction is attached to
    this rule, it will be invoked after the first match.
    @return True when any subrule matched."""
    for rule in self.subRules:
      if rule.match(logAtom):
        if self.matchAction != None:
          self.matchAction.matchAction(logAtom)
        return True
    return False

  def __str__(self):
    result = ''
    preamble = ''
    for matchElement in self.subRules:
      result += '%s(%s)' % (preamble, matchElement)
      preamble = ' or '
    return result


class ParallelMatchRule(MatchRule):
  """This class is a rule testing all the subrules in parallel.
  From the behaviour it is similar to the OrMatchRule, returning
  true if any subrule matches. The difference is that matching
  will not stop after the first positive match. This does only
  make sense when all subrules have match actions associated."""

  def __init__(self, subRules, matchAction=None):
    """Create the rule.
    @param matchAction if None, no action is performed."""
    self.subRules = subRules
    self.matchAction = matchAction

  def match(self, logAtom):
    """Check if any of the subrules rule matches. The matching
    procedure will not stop after the first positive match. If
    a matchAction is attached to this rule, it will be invoked
    at the end of all checks.
    @return True when any subrule matched."""
    matchFlag = False
    for rule in self.subRules:
      if rule.match(logAtom):
        matchFlag = True
    if matchFlag and (self.matchAction != None):
      self.matchAction.matchAction(logAtom)
    return matchFlag

  def __str__(self):
    result = ''
    preamble = ''
    for matchElement in self.subRules:
      result += '%s(%s)' % (preamble, matchElement)
      preamble = ' por '
    return result


class ValueDependentDelegatedMatchRule(MatchRule):
  """This class is a rule delegating rule checking to subrules
  depending on values found within the parserMatch. The result
  of this rule is the result of the selected delegation rule."""

  def __init__(
      self, valuePathList, ruleLookupDict, defaultRule=None,
      matchAction=None):
    """Create the rule.
    @param list with value pathes that are used to extract the
    lookup keys for ruleLookupDict. If value lookup fails, None
    will be used for lookup.
    @param ruleLookupDict dicitionary with tuple containing values
    for valuePathList as key and target rule as value.
    @param defaultRule when not none, this rule will be executed
    as default. Otherwise when rule lookup failed, False will
    be returned unconditionally.
    @param matchAction if None, no action is performed."""
    self.valuePathList = valuePathList
    self.ruleLookupDict = ruleLookupDict
    self.defaultRule = defaultRule
    self.matchAction = matchAction

  def match(self, logAtom):
    """Try to locate a rule for delegation or use the default
    rule.
    @return True when selected delegation rule matched."""
    matchDict = logAtom.parserMatch.getMatchDictionary()
    valueList = []
    for path in self.valuePathList:
      valueElement = matchDict.get(path, None)
      if valueElement is None:
        valueList.append(None)
      else: valueList.append(valueElement.matchObject)
    rule = self.ruleLookupDict.get(tuple(valueList), self.defaultRule)
    if rule is None:
      return False
    if rule.match(logAtom):
      if self.matchAction != None:
        self.matchAction.matchAction(logAtom)
      return True
    return False

  def __str__(self):
    result = 'ValueDependentDelegatedMatchRule'
    return result


class NegationMatchRule(MatchRule):
  """Match elements of this class return true when the subrule
  did not match."""

  def __init__(self, subRule, matchAction=None):
    self.subRule = subRule
    self.matchAction = matchAction

  def match(self, logAtom):
    if self.subRule.match(logAtom):
      return False
    if self.matchAction != None:
      self.matchAction.matchAction(logAtom)
    return True

  def __str__(self):
    return 'not %s' % self.subRule


class PathExistsMatchRule(MatchRule):
  """Match elements of this class return true when the given path
  was found in the parsed match data."""

  def __init__(self, path, matchAction=None):
    self.path = path
    self.matchAction = matchAction

  def match(self, logAtom):
    if self.path in logAtom.parserMatch.getMatchDictionary():
      if self.matchAction != None:
        self.matchAction.matchAction(logAtom)
      return True
    return False

  def __str__(self):
    return 'hasPath(%s)' % self.path


class ValueMatchRule(MatchRule):
  """Match elements of this class return true when the given path
  exists and has exactly the given parsed value."""

  def __init__(self, path, value, matchAction=None):
    self.path = path
    self.value = value
    self.matchAction = matchAction

  def match(self, logAtom):
    testValue = logAtom.parserMatch.getMatchDictionary().get(self.path, None)
    if testValue is not None:
      if isinstance(self.value, bytes) and not isinstance(testValue.matchObject, bytes) and testValue.matchObject is not None:
        testValue.matchObject = testValue.matchObject.encode()
      elif not isinstance(self.value, bytes) and isinstance(testValue.matchObject, bytes) and self.value is not None:
        self.value = self.value.encode()
    if (testValue != None) and (testValue.matchObject == self.value):
      if self.matchAction != None:
        self.matchAction.matchAction(logAtom)
      return True
    return False

  def __str__(self):
    if isinstance(self.value, bytes):
      self.value = self.value.decode("utf-8")
    return 'value(%s)==%s' % (self.path, self.value)


class ValueListMatchRule(MatchRule):
  """Match elements of this class return true when the given path
  exists and has exactly one of the values included in the value
  list."""

  def __init__(self, path, valueList, matchAction=None):
    self.path = path
    self.valueList = valueList
    self.matchAction = matchAction

  def match(self, logAtom):
    testValue = logAtom.parserMatch.getMatchDictionary().get(self.path, None)
    if (testValue != None) and (testValue.matchObject in self.valueList):
      if self.matchAction != None:
        self.matchAction.matchAction(logAtom)
      return True
    return False

  def __str__(self):
    return 'value(%s) in %s' % (self.path, ' '.join(self.valueList))


class ValueRangeMatchRule(MatchRule):
  """Match elements of this class return true when the given path
  exists and the value is included in [lower, upper] range."""

  def __init__(self, path, lowerLimit, upperLimit, matchAction=None):
    self.path = path
    self.lowerLimit = lowerLimit
    self.upperLimit = upperLimit
    self.matchAction = matchAction

  def match(self, logAtom):
    testValue = logAtom.parserMatch.getMatchDictionary().get(self.path, None)
    if testValue is None:
      return False
    testValue = testValue.matchObject
    if (testValue >= self.lowerLimit) and (testValue <= self.upperLimit):
      if self.matchAction != None:
        self.matchAction.matchAction(logAtom)
      return True
    return False

  def __str__(self):
    return 'value(%s) inrange (%s, %s)' % (
        self.path, self.lowerLimit, self.upperLimit)


class StringRegexMatchRule(MatchRule):
  """Match elements of this class return true when the given path
  exists and the string representation of the value matches the
  given compiled regular expression."""

  def __init__(self, path, matchRegex, matchAction=None):
    self.path = path
    self.matchRegex = matchRegex
    self.matchAction = matchAction

  def match(self, logAtom):
# Use the class object as marker for nonexisting entries
    testValue = logAtom.parserMatch.getMatchDictionary().get(self.path, None)
    if ((testValue is None) or
        (self.matchRegex.match(testValue.matchString) is None)):
      return False
    if self.matchAction != None:
      self.matchAction.matchAction(logAtom)
    return True

  def __str__(self):
    return 'string(%s) =regex= %s' % (self.path, self.matchRegex.pattern)


class ModuloTimeMatchRule(MatchRule):
  """Match elements of this class return true when the given path
  exists, denotes a datetime object and the seconds since 1970
  from that date modulo the given value are included in [lower,
  upper] range."""

  def __init__(self, path, secondsModulo, lowerLimit, upperLimit, matchAction=None, tzinfo=None):
    """@param path the path to the datetime object to use to evaluate
    the modulo time rules on. When None, the default timestamp associated
    with the match is used."""
    self.path = path
    self.secondsModulo = secondsModulo
    self.lowerLimit = lowerLimit
    self.upperLimit = upperLimit
    self.matchAction = matchAction
    self.tzinfo = tzinfo
    if tzinfo is None:
      self.tzinfo = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

  def match(self, logAtom):
    testValue = None
    if self.path is None:
      testValue = logAtom.getTimestamp()
    else:
      timeMatch = logAtom.parserMatch.getMatchDictionary().get(self.path, None)
      if ((timeMatch is None) or not isinstance(timeMatch.matchObject, tuple) or
          not isinstance(timeMatch.matchObject[0], datetime.datetime)):
        return False
      testValue = timeMatch.matchObject[1] + datetime.datetime.now(self.tzinfo).utcoffset().total_seconds()
    
    if testValue is None:
      return False
    testValue %= self.secondsModulo
    if (testValue >= self.lowerLimit) and (testValue <= self.upperLimit):
      if self.matchAction != None:
        self.matchAction.matchAction(logAtom)
      return True
    return False


class ValueDependentModuloTimeMatchRule(MatchRule):
  """Match elements of this class return true when the given path
  exists, denotes a datetime object and the seconds since 1970
  from that date modulo the given value are included in a [lower,
  upper] range selected by values from the match."""

  def __init__(
      self, path, secondsModulo, valuePathList, limitLookupDict,
      defaultLimit=None, matchAction=None, tzinfo=None):
    """@param path the path to the datetime object to use to evaluate
    the modulo time rules on. When None, the default timestamp associated
    with the match is used.
    @param defaultLimit use this default limit when limit lookup
    failed. Without a default limit, a failed lookup will cause
    the rule not to match."""
    self.path = path
    self.secondsModulo = secondsModulo
    self.valuePathList = valuePathList
    self.limitLookupDict = limitLookupDict
    self.defaultLimit = defaultLimit
    self.matchAction = matchAction
    self.tzinfo = tzinfo
    if tzinfo is None:
      self.tzinfo = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

  def match(self, logAtom):
    matchDict = logAtom.parserMatch.getMatchDictionary()
    valueList = []
    for path in self.valuePathList:
      valueElement = matchDict.get(path, None)
      if valueElement is None:
        valueList.append(None)
      else:
        valueList.append(valueElement.matchObject)
    limits = self.limitLookupDict.get(tuple(valueList)[0], self.defaultLimit)
    if limits is None:
      return False

    testValue = None
    if self.path is None:
      testValue = logAtom.getTimestamp()
    else:
      timeMatch = logAtom.parserMatch.getMatchDictionary().get(self.path, None)
      if ((timeMatch is None) or not isinstance(timeMatch.matchObject, tuple) or
          not isinstance(timeMatch.matchObject[0], datetime.datetime)):
        return False
      testValue = timeMatch.matchObject[1] + datetime.datetime.now(self.tzinfo).utcoffset().total_seconds()

    if testValue is None:
      return False
    testValue %= self.secondsModulo
    if (testValue >= limits[0]) and (testValue <= limits[1]):
      if self.matchAction != None:
        self.matchAction.matchAction(logAtom)
      return True
    return False


class IPv4InRFC1918MatchRule(MatchRule):
  """Match elements of this class return true when the given path
  was found, contains a valid IPv4 address from the RFC1918 private
  IP ranges. This could also be done by distinct range match elements,
  but as this kind of matching is common, have an own element
  for it."""

  def __init__(self, path, matchAction=None):
    self.path = path
    self.matchAction = matchAction

  def match(self, logAtom):
    matchElement = logAtom.parserMatch.getMatchDictionary().get(self.path, None)
    if (matchElement is None) or not isinstance(matchElement.matchObject, int):
      return False
    value = matchElement.matchObject
    if (((value&0xff000000) == 0xa000000) or
        ((value&0xfff00000) == 0xac100000) or
        ((value&0xffff0000) == 0xc0a80000)):
      if self.matchAction != None:
        self.matchAction.matchAction(logAtom)
      return True
    return False

  def __str__(self):
    return 'hasPath(%s)' % self.path


class DebugMatchRule(MatchRule):
  """This rule can be inserted into a normal ruleset just to see
  when a match attempt is made. It just prints out the current
  logAtom that is evaluated. The match action is always invoked
  when defined, no matter which match result is returned."""

  def __init__(self, debugMatchResult=False, matchAction=None):
    self.debugMatchResult = debugMatchResult
    self.matchAction = matchAction

  def match(self, logAtom):
    print('Rules.DebugMatchRule: triggered while ' \
        'handling "%s"' % repr(logAtom.parserMatch.matchElement.matchString), file=sys.stderr)
    if self.matchAction != None:
      self.matchAction.matchAction(logAtom)
    return self.debugMatchResult

  def __str__(self):
    return '%s' % self.debugMatchResult


class DebugHistoryMatchRule(MatchRule):
  """This rule can be inserted into a normal ruleset just to see
  when a match attempt is made. It just adds the evaluated logAtom
  to a ObjectHistory."""

  def __init__(
      self, objectHistory=None, debugMatchResult=False, matchAction=None):
    """Create a DebugHistoryMatchRule object.
    @param objectHistory use this ObjectHistory to collect the
    LogAtoms. When None, a default LogarithmicBackoffHistory for
    10 items."""
    if objectHistory is None:
      objectHistory = LogarithmicBackoffHistory(10)
    elif not isinstance(objectHistory, ObjectHistory):
      raise Exception('objectHistory is not an instance of ObjectHistory')
    self.objectHistory = objectHistory
    self.debugMatchResult = debugMatchResult
    self.matchAction = matchAction

  def match(self, logAtom):
    self.objectHistory.addObject(logAtom)
    if self.matchAction != None:
      self.matchAction.matchAction(logAtom)
    return self.debugMatchResult

  def getHistory(self):
    """Get the history object from this debug rule."""
    return self.objectHistory
