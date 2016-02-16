import datetime

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
    for matchElement in self.subRules:
      if not(matchElement.match(parserMatch)): return(False)
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
    for matchElement in self.subRules:
      if matchElement.match(parserMatch):
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
    for matchElement in self.subRules:
      if matchElement.match(parserMatch): matchFlag=True
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


class NegationMatchElement(MatchRule):
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


class PathExistsMatchElement(MatchRule):
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


class ValueMatchElement(MatchRule):
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


class ValueListMatchElement(MatchRule):
  """Match elements of this class return true when the given path
  exists and has exactly one of the values included in the value
  list."""

  def __init__(self, path, valueList, matchAction=None):
    self.path=path
    self.valueList=valueList
    self.matchAction=matchAction

  def match(self, parserMatch):
    testValue=parserMatch.getMatchDictionary().get(self.path, None)
    if (testValue!=None) and (testValue in self.valueList):
      if self.matchAction!=None: self.matchAction.matchAction(parserMatch)
      return(True)
    return(False)

  def __str__(self):
    return('value(%s) in %s' % (self.path, ' '.join(self.valueList)))


class ValueRangeMatchElement(MatchRule):
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


class ModuloTimeMatchElement(MatchRule):
  """Match elements of this class return true when the given path
  exists, denotes a datetime object and the seconds on that day
  modulo the given value are included in [lower, upper] range."""

  def __init__(self, path, secondsModulo, lowerLimit, upperLimit, matchAction=None):
    self.path=path
    self.secondsModulo=secondsModulo
    self.lowerLimit=lowerLimit
    self.upperLimit=upperLimit
    self.matchAction=matchAction

  def match(self, parserMatch):
# Use the class object as marker for nonexisting entries
    testValue=parserMatch.getMatchDictionary().get(self.path, None)
    if (testValue==None) or not(isinstance(testValue.matchObject, datetime.datetime)): return(False)
    testValue=testValue.matchObject
    testValue=((testValue.hour*60+testValue.minute)*60+testValue.second)%self.secondsModulo
    if (testValue>=self.lowerLimit) and (testValue<=self.upperLimit):
      if self.matchAction!=None: self.matchAction.matchAction(parserMatch)
      return(True)
    return(False)
