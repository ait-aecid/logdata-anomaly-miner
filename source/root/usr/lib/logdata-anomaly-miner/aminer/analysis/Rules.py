import datetime
import sys

from ParsedAtomFilters import SubhandlerFilter

"""This package contains various classes to build check rulesets.
The ruleset also supports parallel rule evaluation, e.g. the two
rules "A and B and C" and "A and B and D" will only peform the
checks for A and B once, then performs check C and D and trigger
a match action."""


class MatchAction:
  """This is the interface of all match actions."""
  def matchAction(self, parserMatch):
    """This method is invoked if a rule rule has matched.
    @param parserMatch the parser MatchElement that was also matching
    the rules."""
    raise Exception('Interface called')


class EventGenerationMatchAction(MatchAction):
  """This generic match action forwards information about a rule
  match on parsed data to a list of event handlers."""
  def __init__(self, eventType, eventMessage, eventHandlers):
    self.eventType=eventType
    self.eventMessage=eventMessage
    self.eventHandlers=eventHandlers

  def matchAction(self, parserMatch):
    for handler in self.eventHandlers:
      handler.receiveEvent(self.eventType, self.eventMessage,
          [parserMatch.matchElement.matchString], parserMatch, self)


class ParsedAtomFilterMatchAction(MatchAction, SubhandlerFilter):
  """This generic match rule forwards all rule matches to a list
  of ParsedAtomHandlerInterface instaces using the
  analysis.ParsedAtomFilters.SubhandlerFilter."""
  def __init__(self, subhandlerList, stopWhenHandledFlag=False):
    SubhandlerFilter.__init__(self, subhandlerList, stopWhenHandledFlag)

  def matchAction(self, parserMatch):
    self.receiveParsedAtom(parserMatch.matchElement.matchString, parserMatch)


class MatchRule:
  """This is the interface of all match rules."""
  def match(self, parserMatch):
    """Check if this rule matches. On match an optional matchAction
    could be triggered."""
    raise Exception('Interface called on %s' % self)


class AndMatchRule(MatchRule):
  """This class provides a rule to match all subRules (logical
  and)"""

  def __init__(self, subRules, matchAction=None):
    """Create the rule.
    @param matchAction if None, no action is performed."""
    self.subRules=subRules
    self.matchAction=matchAction

  def match(self, parserMatch):
    """Check if this rule matches. Rule evaluation will stop when
    the first match fails. If a matchAction is attached to this
    rule, it will be invoked at the end of all checks.
    @return True when all subrules matched."""
    for rule in self.subRules:
      if not(rule.match(parserMatch)): return(False)
    if self.matchAction!=None: self.matchAction.matchAction(parserMatch)
    return(True)

  def __str__(self):
    result=''
    preamble=''
    for matchElement in self.subRules:
      result+='%s(%s)' % (preamble, matchElement)
      preamble=' and '
    return(result)

class OrMatchRule(MatchRule):
  """This class provides a rule to match any subRules (logical
  or)"""

  def __init__(self, subRules, matchAction=None):
    """Create the rule.
    @param matchAction if None, no action is performed."""
    self.subRules=subRules
    self.matchAction=matchAction

  def match(self, parserMatch):
    """Check if this rule matches. Rule evaluation will stop when
    the first match succeeds. If a matchAction is attached to
    this rule, it will be invoked after the first match.
    @return True when any subrule matched."""
    for rule in self.subRules:
      if rule.match(parserMatch):
        if self.matchAction!=None: self.matchAction.matchAction(parserMatch)
        return(True)
    return(False)

  def __str__(self):
    result=''
    preamble=''
    for matchElement in self.subRules:
      result+='%s(%s)' % (preamble, matchElement)
      preamble=' or '
    return(result)


class ParallelMatchRule(MatchRule):
  """This class is a rule testing all the subrules in parallel.
  From the behaviour it is similar to the OrMatchRule, returning
  true if any subrule matches. The difference is that matching
  will not stop after the first positive match. This does only
  make sense when all subrules have match actions associated."""

  def __init__(self, subRules, matchAction=None):
    """Create the rule.
    @param matchAction if None, no action is performed."""
    self.subRules=subRules
    self.matchAction=matchAction

  def match(self, parserMatch):
    """Check if any of the subrules rule matches. The matching
    procedure will not stop after the first positive match. If
    a matchAction is attached to this rule, it will be invoked
    at the end of all checks.
    @return True when any subrule matched."""
    matchFlag=False
    for rule in self.subRules:
      if rule.match(parserMatch): matchFlag=True
    if (matchFlag) and (self.matchAction!=None):
      self.matchAction.matchAction(parserMatch)
    return(matchFlag)

  def __str__(self):
    result=''
    preamble=''
    for matchElement in self.subRules:
      result+='%s(%s)' % (preamble, matchElement)
      preamble=' por '
    return(result)


class NegationMatchRule(MatchRule):
  """Match elements of this class return true when the subrule
  did not match."""

  def __init__(self, subRule, matchAction=None):
    self.subRule=subRule
    self.matchAction=matchAction

  def match(self, parserMatch):
    if subRule.match(parserMatch): return(False)
    if self.matchAction!=None: self.matchAction.matchAction(parserMatch)
    return(True)

  def __str__(self):
    return('not %s' % subRule)


class PathExistsMatchRule(MatchRule):
  """Match elements of this class return true when the given path
  was found in the parsed match data."""

  def __init__(self, path, matchAction=None):
    self.path=path
    self.matchAction=matchAction

  def match(self, parserMatch):
    if parserMatch.getMatchDictionary().has_key(self.path):
      if self.matchAction!=None: self.matchAction.matchAction(parserMatch)
      return(True)
    return(False)

  def __str__(self):
    return('hasPath(%s)' % self.path)


class ValueMatchRule(MatchRule):
  """Match elements of this class return true when the given path
  exists and has exactly the given parsed value."""

  def __init__(self, path, value, matchAction=None):
    self.path=path
    self.value=value
    self.matchAction=matchAction

  def match(self, parserMatch):
# Use the class object as marker for nonexisting entries
    testValue=parserMatch.getMatchDictionary().get(self.path, None)
    if (testValue!=None) and (testValue.matchObject==self.value):
      if self.matchAction!=None: self.matchAction.matchAction(parserMatch)
      return(True)
    return(False)

  def __str__(self):
    return('value(%s)==%s' % (self.path, self.value))


class ValueListMatchRule(MatchRule):
  """Match elements of this class return true when the given path
  exists and has exactly one of the values included in the value
  list."""

  def __init__(self, path, valueList, matchAction=None):
    self.path=path
    self.valueList=valueList
    self.matchAction=matchAction

  def match(self, parserMatch):
    testValue=parserMatch.getMatchDictionary().get(self.path, None)
    if (testValue!=None) and (testValue.matchObject in self.valueList):
      if self.matchAction!=None: self.matchAction.matchAction(parserMatch)
      return(True)
    return(False)

  def __str__(self):
    return('value(%s) in %s' % (self.path, ' '.join(self.valueList)))


class ValueRangeMatchRule(MatchRule):
  """Match elements of this class return true when the given path
  exists and the value is included in [lower, upper] range."""

  def __init__(self, path, lowerLimit, upperLimit, matchAction=None):
    self.path=path
    self.lowerLimit=lowerLimit
    self.upperLimit=upperLimit
    self.matchAction=matchAction

  def match(self, parserMatch):
    testValue=parserMatch.getMatchDictionary().get(self.path, None)
    if testValue==None: return(False)
    testValue=testValue.matchObject
    if (testValue>=self.lowerLimit) and (testValue<=self.upperLimit):
      if self.matchAction!=None: self.matchAction.matchAction(parserMatch)
      return(True)
    return(False)

  def __str__(self):
    return('value(%s) inrange (%s, %s)' % (self.path, lowerLimit, upperLimit))


class ModuloTimeMatchRule(MatchRule):
  """Match elements of this class return true when the given path
  exists, denotes a datetime object and the seconds since 1970
  from that date modulo the given value are included in [lower,
  upper] range."""

  def __init__(self, path, secondsModulo, lowerLimit, upperLimit, matchAction=None):
    """@param path the path to the datetime object to use to evaluate
    the modulo time rules on. When None, the default timestamp associated
    with the match is used."""
    self.path=path
    self.secondsModulo=secondsModulo
    self.lowerLimit=lowerLimit
    self.upperLimit=upperLimit
    self.matchAction=matchAction

  def match(self, parserMatch):
    testValue=None
    if self.path==None:
      testValue=parserMatch.getDefaultTimestamp()
    else:
      timeMatch=parserMatch.getMatchDictionary().get(self.path, None)
      if (timeMatch==None) or not(isinstance(timeMatch.matchObject, tuple)) or not(isinstance(timeMatch.matchObject[0], datetime.datetime)):
        return(False)
      testValue=timeMatch.matchObject[1]

    if testValue==None: return(False)
    testValue%=self.secondsModulo
    if (testValue>=self.lowerLimit) and (testValue<=self.upperLimit):
      if self.matchAction!=None: self.matchAction.matchAction(parserMatch)
      return(True)
    return(False)


class IPv4InRFC1918MatchRule(MatchRule):
  """Match elements of this class return true when the given path
  was found, contains a valid IPv4 address from the RFC1918 private
  IP ranges. This could also be done by distinct range match elements,
  but as this kind of matching is common, have an own element
  for it."""

  def __init__(self, path, matchAction=None):
    self.path=path
    self.matchAction=matchAction

  def match(self, parserMatch):
    matchElement=parserMatch.getMatchDictionary().get(self.path, None)
    if (matchElement==None) or not(isinstance(matchElement.matchObject, int)):
      return(False)
    value=matchElement.matchObject
    if ((value&0xff000000)==0xa000000) or ((value&0xfff00000)==0xac100000) or ((value&0xffff0000)==0xc0a80000):
      if self.matchAction!=None: self.matchAction.matchAction(parserMatch)
      return(True)
    return(False)

  def __str__(self):
    return('hasPath(%s)' % self.path)


class DebugMatchRule(MatchRule):
  """This rule can be inserted into a normal ruleset just to see
  when a match attempt is made. It just prints out the current
  parserMatch that is evaluated. The match action is always invoked
  when defined, no matter which match result is returned."""

  def __init__(self, debugMatchResult=False, matchAction=None):
    self.debugMatchResult=debugMatchResult
    self.matchAction=matchAction

  def match(self, parserMatch):
    print >>sys.stderr, 'Rules.DebugMatchRule: triggered while handling "%s"' % (parserMatch.matchElement.matchString)
    if self.matchAction!=None: self.matchAction.matchAction(parserMatch)
    return(self.debugMatchResult)

  def __str__(self):
    return('%s' % self.debugMatchResult)
