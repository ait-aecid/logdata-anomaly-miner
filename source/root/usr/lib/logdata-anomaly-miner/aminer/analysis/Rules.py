"""
This package contains various classes to build check rulesets.
The ruleset also supports parallel rule evaluation, e.g. the two
rules "A and B and C" and "A and B and D" will only peform the
checks for A and B once, then performs check C and D and trigger
a match action.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

import datetime
import sys
import abc
import logging

from aminer.util.History import LogarithmicBackoffHistory
from aminer.util.History import ObjectHistory

from aminer.analysis.AtomFilters import SubhandlerFilter
from aminer.AminerConfig import DEBUG_LOG_NAME, STAT_LOG_NAME
from aminer import AminerConfig

result_string = '%s(%s)'


class MatchAction(metaclass=abc.ABCMeta):
    """This is the interface of all match actions."""

    @abc.abstractmethod
    def match_action(self, log_atom):
        """
        Invoke this method if a rule has matched.
        @param log_atom the LogAtom matching the rules.
        """


class EventGenerationMatchAction(MatchAction):
    """This generic match action forwards information about a rule match on parsed data to a list of event handlers."""

    def __init__(self, event_type, event_message, event_handlers):
        self.event_type = event_type
        self.event_message = event_message
        self.event_handlers = event_handlers

    def match_action(self, log_atom):
        """
        Invoke this method if a rule has matched.
        @param log_atom the LogAtom matching the rules.
        """
        event_data = {}
        for handler in self.event_handlers:
            handler.receive_event(self.event_type, self.event_message, [log_atom.parser_match.match_element.annotate_match('')], event_data,
                                  log_atom, self)


class AtomFilterMatchAction(MatchAction, SubhandlerFilter):
    """This generic match rule forwards all rule matches to a list of AtomHandlerInterface instances using the SubhandlerFilter."""

    def __init__(self, subhandler_list, stop_when_handled_flag=False):
        SubhandlerFilter.__init__(self, subhandler_list, stop_when_handled_flag)

    def match_action(self, log_atom):
        """
        Invoke this method if a rule has matched.
        @param log_atom the LogAtom matching the rules.
        """
        self.receive_atom(log_atom)


class MatchRule(metaclass=abc.ABCMeta):
    """This is the interface of all match rules."""

    log_success = 0
    log_total = 0

    @abc.abstractmethod
    def match(self, log_atom):
        """Check if this rule matches. On match an optional match_action could be triggered."""

    def log_statistics(self, rule_id):
        """Log statistics of an MatchRule. Override this method for more sophisticated statistics output of the MatchRule."""
        if AminerConfig.STAT_LEVEL > 0:
            logging.getLogger(STAT_LOG_NAME).info("Rule '%s' processed %d out of %d log atoms successfully in the last 60"
                                                  " minutes.", rule_id, self.log_success, self.log_total)
        self.log_success = 0
        self.log_total = 0
        if hasattr(self, 'sub_rules'):
            for i, rule in enumerate(self.sub_rules):
                rule.log_statistics(rule_id + '.' + rule.__class__.__name__ + str(i))
        if hasattr(self, 'rule_lookup_dict'):
            for i, rule_key in enumerate(self.rule_lookup_dict):
                rule = self.rule_lookup_dict[rule_key]
                rule.log_statistics(rule_id + '.' + rule.__class__.__name__ + str(i))
        if hasattr(self, 'default_rule'):
            self.default_rule.log_statistics(rule_id + '.default_rule.' + self.default_rule.__class__.__name__)
        if hasattr(self, 'sub_rule'):
            self.sub_rule.log_statistics(rule_id + '.' + self.sub_rule.__class__.__name__)


class AndMatchRule(MatchRule):
    """This class provides a rule to match all subRules (logical and)."""

    def __init__(self, sub_rules, match_action=None):
        """
        Create the rule.
        @param match_action if None, no action is performed.
        """
        self.sub_rules = sub_rules
        self.match_action = match_action

    def match(self, log_atom):
        """
        Check if this rule matches. Rule evaluation will stop when the first match fails.
        If a matchAction is attached to this rule, it will be invoked at the end of all checks.
        @return True when all subrules matched.
        """
        self.log_total += 1
        for rule in self.sub_rules:
            if not rule.match(log_atom):
                return False
        if self.match_action is not None:
            self.match_action.match_action(log_atom)
        self.log_success += 1
        return True

    def __str__(self):
        result = ''
        preamble = ''
        for match_element in self.sub_rules:
            result += result_string % (preamble, match_element)
            preamble = ' and '
        return result


class OrMatchRule(MatchRule):
    """This class provides a rule to match any subRules (logical or)."""

    def __init__(self, sub_rules, match_action=None):
        """
        Create the rule.
        @param match_action if None, no action is performed.
        """
        self.sub_rules = sub_rules
        self.match_action = match_action

    def match(self, log_atom):
        """
        Check if this rule matches. Rule evaluation will stop when the first match succeeds.
        If a matchAction is attached to this rule, it will be invoked after the first match.
        @return True when any subrule matched.
        """
        self.log_total += 1
        for rule in self.sub_rules:
            if rule.match(log_atom):
                if self.match_action is not None:
                    self.match_action.match_action(log_atom)
                self.log_success += 1
                return True
        return False

    def __str__(self):
        result = ''
        preamble = ''
        for match_element in self.sub_rules:
            result += result_string % (preamble, match_element)
            preamble = ' or '
        return result


class ParallelMatchRule(MatchRule):
    """
    This class is a rule testing all the subrules in parallel.
    From the behaviour it is similar to the OrMatchRule, returning true if any subrule matches. The difference is that matching will not
    stop after the first positive match. This does only make sense when all subrules have match actions associated.
    """

    def __init__(self, sub_rules, match_action=None):
        """
        Create the rule.
        @param match_action if None, no action is performed.
        """
        self.sub_rules = sub_rules
        self.match_action = match_action

    def match(self, log_atom):
        """
        Check if any of the subrules rule matches. The matching procedure will not stop after the first positive match.
        If a matchAction is attached to this rule, it will be invoked at the end of all checks.
        @return True when any subrule matched.
        """
        self.log_total += 1
        match_flag = False
        for rule in self.sub_rules:
            if rule.match(log_atom):
                match_flag = True
        if match_flag and (self.match_action is not None):
            self.match_action.match_action(log_atom)
        if match_flag:
            self.log_success += 1
        return match_flag

    def __str__(self):
        result = ''
        preamble = ''
        for match_element in self.sub_rules:
            result += result_string % (preamble, match_element)
            preamble = ' por '
        return result


class ValueDependentDelegatedMatchRule(MatchRule):
    """
    This class is a rule delegating rule checking to subrules depending on values found within the parser_match.
    The result of this rule is the result of the selected delegation rule.
    """

    def __init__(self, value_path_list, rule_lookup_dict, default_rule=None, match_action=None):
        """
        Create the rule.
        @param list with value paths that are used to extract the lookup keys for ruleLookupDict. If value lookup fails, None
        will be used for lookup.
        @param rule_lookup_dict dictionary with tuple containing values for valuePathList as key and target rule as value.
        @param default_rule when not none, this rule will be executed as default. Otherwise when rule lookup failed, False will
        be returned unconditionally.
        @param match_action if None, no action is performed.
        """
        self.value_path_list = value_path_list
        self.rule_lookup_dict = rule_lookup_dict
        self.default_rule = default_rule
        self.match_action = match_action

    def match(self, log_atom):
        """
        Try to locate a rule for delegation or use the default rule.
        @return True when selected delegation rule matched.
        """
        self.log_total += 1
        match_dict = log_atom.parser_match.get_match_dictionary()
        value_list = []
        for path in self.value_path_list:
            value_element = match_dict.get(path)
            if value_element is not None:
                value_list.append(value_element.match_object)
        if len(value_list) > 0:
            value = tuple(value_list)
        else:
            value = None
        rule = self.rule_lookup_dict.get(value, self.default_rule)
        if rule is None:
            return False
        if rule.match(log_atom):
            if self.match_action is not None:
                self.match_action.match_action(log_atom)
            self.log_success += 1
            return True
        return False

    def __str__(self):
        result = 'ValueDependentDelegatedMatchRule'
        return result


class NegationMatchRule(MatchRule):
    """Match elements of this class return true when the subrule did not match."""

    def __init__(self, sub_rule, match_action=None):
        self.sub_rule = sub_rule
        self.match_action = match_action

    def match(self, log_atom):
        """Check if this rule matches. On match an optional match_action could be triggered."""
        self.log_total += 1
        if self.sub_rule.match(log_atom):
            return False
        if self.match_action is not None:
            self.match_action.match_action(log_atom)
        self.log_success += 1
        return True

    def __str__(self):
        return 'not %s' % self.sub_rule


class PathExistsMatchRule(MatchRule):
    """Match elements of this class return true when the given path was found in the parsed match data."""

    def __init__(self, path, match_action=None):
        self.path = path
        self.match_action = match_action

    def match(self, log_atom):
        """Check if this rule matches. On match an optional match_action could be triggered."""
        self.log_total += 1
        if self.path in log_atom.parser_match.get_match_dictionary():
            if self.match_action is not None:
                self.match_action.match_action(log_atom)
            self.log_success += 1
            return True
        return False

    def __str__(self):
        return 'hasPath(%s)' % self.path


class ValueMatchRule(MatchRule):
    """Match elements of this class return true when the given path exists and has exactly the given parsed value."""

    def __init__(self, path, value, match_action=None):
        self.path = path
        self.value = value
        self.match_action = match_action

    def match(self, log_atom):
        """Check if this rule matches. On match an optional match_action could be triggered."""
        self.log_total += 1
        test_value = log_atom.parser_match.get_match_dictionary().get(self.path, None)
        if test_value is not None:
            if isinstance(self.value, bytes) and isinstance(test_value.match_object, str) and test_value.match_object is not None:
                test_value.match_object = test_value.match_object.encode()
            elif isinstance(self.value, str) and isinstance(test_value.match_object, bytes) and self.value is not None:
                self.value = self.value.encode()
            elif not isinstance(self.value, type(test_value.match_object)):
                raise TypeError(f"The type of the value of the ValueMatchRule does not match the test_value. value: {type(self.value)}, "
                                f"test_value: {type(test_value.match_object)}")
        if (test_value is not None) and (test_value.match_object == self.value):
            if self.match_action is not None:
                self.match_action.match_action(log_atom)
            self.log_success += 1
            return True
        return False

    def __str__(self):
        if isinstance(self.value, bytes):
            self.value = self.value.decode()
        return 'value(%s)==%s' % (self.path, self.value)


class ValueListMatchRule(MatchRule):
    """Match elements of this class return true when the given path exists and has exactly one of the values included in the value list."""

    def __init__(self, path, value_list, match_action=None):
        self.path = path
        self.value_list = value_list
        self.match_action = match_action

    def match(self, log_atom):
        """Check if this rule matches. On match an optional match_action could be triggered."""
        self.log_total += 1
        test_value = log_atom.parser_match.get_match_dictionary().get(self.path)
        if (test_value is not None) and (test_value.match_object in self.value_list):
            if self.match_action is not None:
                self.match_action.match_action(log_atom)
            self.log_success += 1
            return True
        return False

    def __str__(self):
        return 'value(%s) in %s' % (' '.join([str(value) for value in self.value_list]), self.path)


class ValueRangeMatchRule(MatchRule):
    """Match elements of this class return true when the given path exists and the value is included in [lower, upper] range."""

    def __init__(self, path, lower_limit, upper_limit, match_action=None):
        self.path = path
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.match_action = match_action

    def match(self, log_atom):
        """Check if this rule matches. On match an optional match_action could be triggered."""
        self.log_total += 1
        test_value = log_atom.parser_match.get_match_dictionary().get(self.path, None)
        if test_value is None:
            return False
        test_value = test_value.match_object
        if self.lower_limit <= test_value <= self.upper_limit:
            if self.match_action is not None:
                self.match_action.match_action(log_atom)
            self.log_success += 1
            return True
        return False

    def __str__(self):
        return 'value(%s) inrange (%s, %s)' % (self.path, self.lower_limit, self.upper_limit)


class StringRegexMatchRule(MatchRule):
    """Elements of this class return true when the given path exists and the string repr of the value matches the regular expression."""

    def __init__(self, path, match_regex, match_action=None):
        self.path = path
        self.match_regex = match_regex
        self.match_action = match_action

    def match(self, log_atom):
        """Check if this rule matches. On match an optional match_action could be triggered."""
        self. log_total += 1
        # Use the class object as marker for nonexisting entries
        test_value = log_atom.parser_match.get_match_dictionary().get(self.path, None)
        if (test_value is None) or (self.match_regex.match(test_value.match_string) is None):
            return False
        if self.match_action is not None:
            self.match_action.match_action(log_atom)
        self.log_success += 1
        return True

    def __str__(self):
        return 'string(%s) =regex= %s' % (self.path, self.match_regex.pattern)


class ModuloTimeMatchRule(MatchRule):
    """
    Match elements of this class return true when the following conditions are met.
    The given path exists, denotes a datetime object and the seconds since 1970 from that date modulo the given value are included in
    [lower, upper] range.
    """

    def __init__(self, path, seconds_modulo, lower_limit, upper_limit, match_action=None, tzinfo=None):
        """
        @param path the path to the datetime object to use to evaluate the modulo time rules on.
        When None, the default timestamp associated with the match is used.
        """
        self.path = path
        self.seconds_modulo = seconds_modulo
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.match_action = match_action
        self.tzinfo = tzinfo
        if tzinfo is None:
            self.tzinfo = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

    def match(self, log_atom):
        """Check if this rule matches. On match an optional match_action could be triggered."""
        self.log_total += 1
        test_value = None
        if self.path is None:
            test_value = log_atom.get_timestamp()
        else:
            time_match = log_atom.parser_match.get_match_dictionary().get(self.path, None)
            if time_match is None:
                return False
            test_value = time_match.match_object + datetime.datetime.now(self.tzinfo).utcoffset().total_seconds()

        if test_value is None:
            return False
        test_value %= self.seconds_modulo
        if self.lower_limit <= test_value <= self.upper_limit:
            if self.match_action is not None:
                self.match_action.match_action(log_atom)
            self.log_success += 1
            return True
        return False


class ValueDependentModuloTimeMatchRule(MatchRule):
    """
    Match elements of this class return true when the following conditions are met.
    The given path exists, denotes a datetime object and the seconds since 1970 rom that date modulo the given value are included in a
    [lower, upper] range selected by values from the match.
    """

    def __init__(self, path, seconds_modulo, value_path_list, limit_lookup_dict, default_limit=None, match_action=None, tzinfo=None):
        """
        @param path the path to the datetime object to use to evaluate the modulo time rules on.
        When None, the default timestamp associated with the match is used.
        @param default_limit use this default limit when limit lookup failed. Without a default limit, a failed lookup will cause
        the rule not to match.
        """
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
        """Check if this rule matches. On match an optional match_action could be triggered."""
        self.log_total += 1
        match_dict = log_atom.parser_match.get_match_dictionary()
        value_list = []
        for path in self.value_path_list:
            value_element = match_dict.get(path)
            if value_element is not None:
                value_list.append(value_element.match_object)

        if len(value_list) > 0:
            value = value_list[0]
        else:
            value = None
        limits = self.limit_lookup_dict.get(value, self.default_limit)
        if limits is None:
            return False

        test_value = None
        if self.path is None:
            test_value = log_atom.get_timestamp()
        else:
            time_match = log_atom.parser_match.get_match_dictionary().get(self.path, None)
            if time_match is None:
                return False
            test_value = time_match.match_object + datetime.datetime.now(self.tzinfo).utcoffset().total_seconds()

        if test_value is None:
            return False
        test_value %= self.seconds_modulo
        if limits[0] <= test_value <= limits[1]:
            if self.match_action is not None:
                self.match_action.match_action(log_atom)
            self.log_success += 1
            return True
        return False


class IPv4InRFC1918MatchRule(MatchRule):
    """
    Match elements of this class return true when the path matches and contains a valid IPv4 address from the RFC1918 private IP ranges.
    This could also be done by distinct range match elements, but as this kind of matching is common, have an own element for it.
    """

    def __init__(self, path, match_action=None):
        self.path = path
        self.match_action = match_action

    def match(self, log_atom):
        """Check if this rule matches. On match an optional match_action could be triggered."""
        self.log_total += 1
        match_element = log_atom.parser_match.get_match_dictionary().get(self.path)
        if (match_element is None) or not isinstance(match_element.match_object, int):
            return False
        value = match_element.match_object
        if ((value & 0xff000000) == 0xa000000) or ((value & 0xfff00000) == 0xac100000) or ((value & 0xffff0000) == 0xc0a80000):
            if self.match_action is not None:
                self.match_action.match_action(log_atom)
            self.log_success += 1
            return True
        return False

    def __str__(self):
        return 'hasPath(%s)' % self.path


class DebugMatchRule(MatchRule):
    """
    This rule can be inserted into a normal ruleset just to see when a match attempt is made.
    It just prints out the current log_atom that is evaluated. The match action is always invoked when defined, no matter which match
    result is returned.
    """

    def __init__(self, debug_match_result=False, match_action=None):
        self.debug_match_result = debug_match_result
        self.match_action = match_action

    def match(self, log_atom):
        """Check if this rule matches. On match an optional match_action could be triggered."""
        self.log_total += 1
        print('Rules.DebugMatchRule: triggered while handling "%s"' % repr(log_atom.parser_match.match_element.match_string),
              file=sys.stderr)
        if self.match_action is not None:
            self.match_action.match_action(log_atom)
        self.log_success += 1
        return self.debug_match_result

    def __str__(self):
        return '%s' % self.debug_match_result


class DebugHistoryMatchRule(MatchRule):
    """
    This rule can be inserted into a normal ruleset just to see when a match attempt is made.
    It just adds the evaluated log_atom to a ObjectHistory.
    """

    def __init__(self, object_history=None, debug_match_result=False, match_action=None):
        """
        Create a DebugHistoryMatchRule object.
        @param object_history use this ObjectHistory to collect the LogAtoms. When None, a default LogarithmicBackoffHistory for 10 items.
        """
        if object_history is None:
            object_history = LogarithmicBackoffHistory(10)
        elif not isinstance(object_history, ObjectHistory):
            msg = 'object_history is not an instance of ObjectHistory'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        self.object_history = object_history
        self.debug_match_result = debug_match_result
        self.match_action = match_action

    def match(self, log_atom):
        """Check if this rule matches. On match an optional match_action could be triggered."""
        self.log_total += 1
        self.object_history.add_object(log_atom)
        if self.match_action is not None:
            self.match_action.match_action(log_atom)
        self.log_success += 1
        return self.debug_match_result

    def get_history(self):
        """Get the history object from this debug rule."""
        return self.object_history
