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
  def match_action(self, log_atom):
    """This method is invoked if a rule rule has matched.
    @param log_atom the LogAtom matching the rules."""
    raise Exception('Interface called')


class EventGenerationMatchAction(MatchAction):
  """This generic match action forwards information about a rule
  match on parsed data to a list of event handlers."""
  def __init__(self, event_type, event_message, event_handlers):
    self.event_type = event_type
    self.event_message = event_message
    self.event_handlers = event_handlers

  def match_action(self, log_atom):
    event_data = dict()
    for handler in self.event_handlers:
      handler.receiveEvent(
          self.event_type, self.event_message, [log_atom.parserMatch.matchElement.annotateMatch('')], event_data, log_atom, self)


class AtomFilterMatchAction(MatchAction, SubhandlerFilter):
  """This generic match rule forwards all rule matches to a list
  of AtomHandlerInterface instaces using the analysis.AtomFilters.SubhandlerFilter."""
  def __init__(self, subhandler_list, stop_when_handled_flag=False):
    SubhandlerFilter.__init__(self, subhandler_list, stop_when_handled_flag)

  def match_action(self, log_atom):
    self.receive_atom(log_atom)


class MatchRule(object):
  """This is the interface of all match rules."""
  def match(self, log_atom):
    """Check if this rule matches. On match an optional matchAction
    could be triggered."""
    raise Exception('Interface called on %s' % self)


class AndMatchRule(MatchRule):
  """This class provides a rule to match all subRules (logical
  and)"""

  def __init__(self, sub_rules, match_action=None):
    """Create the rule.
    @param match_action if None, no action is performed."""
    self.sub_rules = sub_rules
    self.match_action = match_action

  def match(self, log_atom):
    """Check if this rule matches. Rule evaluation will stop when
    the first match fails. If a matchAction is attached to this
    rule, it will be invoked at the end of all checks.
    @return True when all subrules matched."""
    for rule in self.sub_rules:
      if not rule.match(log_atom):
        return False
    if self.match_action != None:
      self.match_action.match_action(log_atom)
    return True

  def __str__(self):
    result = ''
    preamble = ''
    for match_element in self.sub_rules:
      result += '%s(%s)' % (preamble, match_element)
      preamble = ' and '
    return result

class OrMatchRule(MatchRule):
  """This class provides a rule to match any subRules (logical
  or)"""

  def __init__(self, sub_rules, match_action=None):
    """Create the rule.
    @param match_action if None, no action is performed."""
    self.sub_rules = sub_rules
    self.match_action = match_action

  def match(self, log_atom):
    """Check if this rule matches. Rule evaluation will stop when
    the first match succeeds. If a matchAction is attached to
    this rule, it will be invoked after the first match.
    @return True when any subrule matched."""
    for rule in self.sub_rules:
      if rule.match(log_atom):
        if self.match_action != None:
          self.match_action.match_action(log_atom)
        return True
    return False

  def __str__(self):
    result = ''
    preamble = ''
    for match_element in self.sub_rules:
      result += '%s(%s)' % (preamble, match_element)
      preamble = ' or '
    return result


class ParallelMatchRule(MatchRule):
  """This class is a rule testing all the subrules in parallel.
  From the behaviour it is similar to the OrMatchRule, returning
  true if any subrule matches. The difference is that matching
  will not stop after the first positive match. This does only
  make sense when all subrules have match actions associated."""

  def __init__(self, sub_rules, match_action=None):
    """Create the rule.
    @param match_action if None, no action is performed."""
    self.sub_rules = sub_rules
    self.match_action = match_action

  def match(self, log_atom):
    """Check if any of the subrules rule matches. The matching
    procedure will not stop after the first positive match. If
    a matchAction is attached to this rule, it will be invoked
    at the end of all checks.
    @return True when any subrule matched."""
    match_flag = False
    for rule in self.sub_rules:
      if rule.match(log_atom):
        match_flag = True
    if match_flag and (self.match_action != None):
      self.match_action.match_action(log_atom)
    return match_flag

  def __str__(self):
    result = ''
    preamble = ''
    for match_element in self.sub_rules:
      result += '%s(%s)' % (preamble, match_element)
      preamble = ' por '
    return result


class ValueDependentDelegatedMatchRule(MatchRule):
  """This class is a rule delegating rule checking to subrules
  depending on values found within the parserMatch. The result
  of this rule is the result of the selected delegation rule."""

  def __init__(
      self, value_path_list, rule_lookup_dict, default_rule=None,
      match_action=None):
    """Create the rule.
    @param list with value pathes that are used to extract the
    lookup keys for ruleLookupDict. If value lookup fails, None
    will be used for lookup.
    @param rule_lookup_dict dicitionary with tuple containing values
    for valuePathList as key and target rule as value.
    @param default_rule when not none, this rule will be executed
    as default. Otherwise when rule lookup failed, False will
    be returned unconditionally.
    @param match_action if None, no action is performed."""
    self.value_path_list = value_path_list
    self.rule_lookup_dict = rule_lookup_dict
    self.default_rule = default_rule
    self.match_action = match_action

  def match(self, log_atom):
    """Try to locate a rule for delegation or use the default
    rule.
    @return True when selected delegation rule matched."""
    match_dict = log_atom.parserMatch.getMatchDictionary()
    value_list = []
    for path in self.value_path_list:
      value_element = match_dict.get(path, None)
      if value_element is None:
        value_list.append(None)
      else: value_list.append(value_element.matchObject)
    rule = self.rule_lookup_dict.get(tuple(value_list), self.default_rule)
    if rule is None:
      return False
    if rule.match(log_atom):
      if self.match_action != None:
        self.match_action.match_action(log_atom)
      return True
    return False

  def __str__(self):
    result = 'ValueDependentDelegatedMatchRule'
    return result


class NegationMatchRule(MatchRule):
  """Match elements of this class return true when the subrule
  did not match."""

  def __init__(self, sub_rule, match_action=None):
    self.sub_rule = sub_rule
    self.match_action = match_action

  def match(self, log_atom):
    if self.sub_rule.match(log_atom):
      return False
    if self.match_action != None:
      self.match_action.match_action(log_atom)
    return True

  def __str__(self):
    return 'not %s' % self.sub_rule


class PathExistsMatchRule(MatchRule):
  """Match elements of this class return true when the given path
  was found in the parsed match data."""

  def __init__(self, path, matchAction=None):
    self.path = path
    self.match_action = matchAction

  def match(self, log_atom):
    if self.path in log_atom.parserMatch.getMatchDictionary():
      if self.match_action != None:
        self.match_action.match_action(log_atom)
      return True
    return False

  def __str__(self):
    return 'hasPath(%s)' % self.path


class ValueMatchRule(MatchRule):
  """Match elements of this class return true when the given path
  exists and has exactly the given parsed value."""

  def __init__(self, path, value, match_action=None):
    self.path = path
    self.value = value
    self.match_action = match_action

  def match(self, log_atom):
    test_value = log_atom.parserMatch.getMatchDictionary().get(self.path, None)
    if test_value is not None:
      if isinstance(self.value, bytes) and not isinstance(test_value.match_object, bytes) and test_value.match_object is not None:
        test_value.match_object = test_value.match_object.encode()
      elif not isinstance(self.value, bytes) and isinstance(test_value.match_object, bytes) and self.value is not None:
        self.value = self.value.encode()
    if (test_value != None) and (test_value.matchObject == self.value):
      if self.match_action != None:
        self.match_action.match_action(log_atom)
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

  def __init__(self, path, value_list, match_action=None):
    self.path = path
    self.value_list = value_list
    self.match_action = match_action

  def match(self, log_atom):
    test_value = log_atom.parserMatch.getMatchDictionary().get(self.path, None)
    if (test_value != None) and (test_value.matchObject in self.value_list):
      if self.match_action != None:
        self.match_action.match_action(log_atom)
      return True
    return False

  def __str__(self):
    return 'value(%s) in %s' % (self.path, ' '.join(self.value_list))


class ValueRangeMatchRule(MatchRule):
  """Match elements of this class return true when the given path
  exists and the value is included in [lower, upper] range."""

  def __init__(self, path, lower_limit, upper_limit, match_action=None):
    self.path = path
    self.lower_limit = lower_limit
    self.upper_limit = upper_limit
    self.match_action = match_action

  def match(self, log_atom):
    test_value = log_atom.parserMatch.getMatchDictionary().get(self.path, None)
    if test_value is None:
      return False
    test_value = test_value.matchObject
    if (test_value >= self.lower_limit) and (test_value <= self.upper_limit):
      if self.match_action != None:
        self.match_action.match_action(log_atom)
      return True
    return False

  def __str__(self):
    return 'value(%s) inrange (%s, %s)' % (
      self.path, self.lower_limit, self.upper_limit)


class StringRegexMatchRule(MatchRule):
  """Match elements of this class return true when the given path
  exists and the string representation of the value matches the
  given compiled regular expression."""

  def __init__(self, path, match_regex, match_action=None):
    self.path = path
    self.match_regex = match_regex
    self.match_action = match_action

  def match(self, log_atom):
# Use the class object as marker for nonexisting entries
    test_value = log_atom.parserMatch.getMatchDictionary().get(self.path, None)
    if ((test_value is None) or
        (self.match_regex.match(test_value.matchString) is None)):
      return False
    if self.match_action != None:
      self.match_action.match_action(log_atom)
    return True

  def __str__(self):
    return 'string(%s) =regex= %s' % (self.path, self.match_regex.pattern)


class ModuloTimeMatchRule(MatchRule):
  """Match elements of this class return true when the given path
  exists, denotes a datetime object and the seconds since 1970
  from that date modulo the given value are included in [lower,
  upper] range."""

  def __init__(self, path, seconds_modulo, lower_limit, upper_limit, match_action=None, tzinfo=None):
    """@param path the path to the datetime object to use to evaluate
    the modulo time rules on. When None, the default timestamp associated
    with the match is used."""
    self.path = path
    self.seconds_modulo = seconds_modulo
    self.lower_limit = lower_limit
    self.upper_limit = upper_limit
    self.match_action = match_action
    self.tzinfo = tzinfo
    if tzinfo is None:
      self.tzinfo = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

  def match(self, log_atom):
    test_value = None
    if self.path is None:
      test_value = log_atom.getTimestamp()
    else:
      time_match = log_atom.parserMatch.getMatchDictionary().get(self.path, None)
      if ((time_match is None) or not isinstance(time_match.matchObject, tuple) or
          not isinstance(time_match.matchObject[0], datetime.datetime)):
        return False
      test_value = time_match.matchObject[1] + datetime.datetime.now(self.tzinfo).utcoffset().total_seconds()
    
    if test_value is None:
      return False
    test_value %= self.seconds_modulo
    if (test_value >= self.lower_limit) and (test_value <= self.upper_limit):
      if self.match_action != None:
        self.match_action.match_action(log_atom)
      return True
    return False


class ValueDependentModuloTimeMatchRule(MatchRule):
  """Match elements of this class return true when the given path
  exists, denotes a datetime object and the seconds since 1970
  from that date modulo the given value are included in a [lower,
  upper] range selected by values from the match."""

  def __init__(
      self, path, seconds_modulo, value_path_list, limit_lookup_dict,
      default_limit=None, match_action=None, tzinfo=None):
    """@param path the path to the datetime object to use to evaluate
    the modulo time rules on. When None, the default timestamp associated
    with the match is used.
    @param default_limit use this default limit when limit lookup
    failed. Without a default limit, a failed lookup will cause
    the rule not to match."""
    self.path = path
    self.seconds_modulo = seconds_modulo
    self.value_path_list = value_path_list
    self.limit_lookup_dict = limit_lookup_dict
    self.default_limit = default_limit
    self.match_action = match_action
    self.tzinfo = tzinfo
    if tzinfo is None:
      self.tzinfo = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

  def match(self, log_atom):
    match_dict = log_atom.parserMatch.getMatchDictionary()
    value_list = []
    for path in self.value_path_list:
      value_element = match_dict.get(path, None)
      if value_element is None:
        value_list.append(None)
      else:
        value_list.append(value_element.matchObject)
    limits = self.limit_lookup_dict.get(tuple(value_list)[0], self.default_limit)
    if limits is None:
      return False

    test_value = None
    if self.path is None:
      test_value = log_atom.getTimestamp()
    else:
      time_match = log_atom.parserMatch.getMatchDictionary().get(self.path, None)
      if ((time_match is None) or not isinstance(time_match.matchObject, tuple) or
          not isinstance(time_match.matchObject[0], datetime.datetime)):
        return False
      test_value = time_match.matchObject[1] + datetime.datetime.now(self.tzinfo).utcoffset().total_seconds()

    if test_value is None:
      return False
    test_value %= self.seconds_modulo
    if (test_value >= limits[0]) and (test_value <= limits[1]):
      if self.match_action != None:
        self.match_action.match_action(log_atom)
      return True
    return False


class IPv4InRFC1918MatchRule(MatchRule):
  """Match elements of this class return true when the given path
  was found, contains a valid IPv4 address from the RFC1918 private
  IP ranges. This could also be done by distinct range match elements,
  but as this kind of matching is common, have an own element
  for it."""

  def __init__(self, path, match_action=None):
    self.path = path
    self.match_action = match_action

  def match(self, log_atom):
    match_element = log_atom.parserMatch.getMatchDictionary().get(self.path, None)
    if (match_element is None) or not isinstance(match_element.matchObject, int):
      return False
    value = match_element.matchObject
    if (((value&0xff000000) == 0xa000000) or
        ((value&0xfff00000) == 0xac100000) or
        ((value&0xffff0000) == 0xc0a80000)):
      if self.match_action != None:
        self.match_action.match_action(log_atom)
      return True
    return False

  def __str__(self):
    return 'hasPath(%s)' % self.path


class DebugMatchRule(MatchRule):
  """This rule can be inserted into a normal ruleset just to see
  when a match attempt is made. It just prints out the current
  logAtom that is evaluated. The match action is always invoked
  when defined, no matter which match result is returned."""

  def __init__(self, debug_match_result=False, match_action=None):
    self.debug_match_result = debug_match_result
    self.matchAction = match_action

  def match(self, log_atom):
    print('Rules.DebugMatchRule: triggered while ' \
        'handling "%s"' % repr(log_atom.parserMatch.matchElement.matchString), file=sys.stderr)
    if self.matchAction != None:
      self.matchAction.match_action(log_atom)
    return self.debug_match_result

  def __str__(self):
    return '%s' % self.debug_match_result


class DebugHistoryMatchRule(MatchRule):
  """This rule can be inserted into a normal ruleset just to see
  when a match attempt is made. It just adds the evaluated logAtom
  to a ObjectHistory."""

  def __init__(
      self, object_history=None, debug_match_result=False, match_action=None):
    """Create a DebugHistoryMatchRule object.
    @param object_history use this ObjectHistory to collect the
    LogAtoms. When None, a default LogarithmicBackoffHistory for
    10 items."""
    if object_history is None:
      object_history = LogarithmicBackoffHistory(10)
    elif not isinstance(object_history, ObjectHistory):
      raise Exception('objectHistory is not an instance of ObjectHistory')
    self.object_history = object_history
    self.debug_match_result = debug_match_result
    self.match_action = match_action

  def match(self, log_atom):
    self.object_history.addObject(log_atom)
    if self.match_action != None:
      self.match_action.match_action(log_atom)
    return self.debug_match_result

  def get_history(self):
    """Get the history object from this debug rule."""
    return self.object_history
