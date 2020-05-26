"""This module defines a detector for time correlation rules."""

import time

from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.input import AtomHandlerInterface
from aminer.util import LogarithmicBackoffHistory
from aminer.util import PersistencyUtil
from aminer.util import TimeTriggeredComponentInterface
from aminer.analysis import Rules


class TimeCorrelationViolationDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """This class creates events when one of the given time correlation rules is violated. This is used to implement checks as depicted
    in http://dx.doi.org/10.1016/j.cose.2014.09.006"""

    def __init__(self, aminer_config, ruleset, anomaly_event_handlers, persistence_id='Default', output_log_line=True):
        """Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param ruleset a list of MatchRule rules with appropriate CorrelationRules attached as actions."""
        self.event_classification_ruleset = ruleset
        self.anomaly_event_handlers = anomaly_event_handlers
        self.next_persist_time = time.time() + 600.0
        self.persistence_id = persistence_id
        self.output_log_line = output_log_line
        self.last_log_atom = None

        event_correlation_set = set()
        for rule in self.event_classification_ruleset:
            if rule.match_action.artefact_a_rules is not None:
                event_correlation_set |= set(rule.match_action.artefact_a_rules)
            if rule.match_action.artefact_b_rules is not None:
                event_correlation_set |= set(rule.match_action.artefact_b_rules)
        self.event_correlation_ruleset = list(event_correlation_set)

        PersistencyUtil.add_persistable_component(self)
        self.persistence_file_name = AMinerConfig.build_persistence_file_name(aminer_config, 'TimeCorrelationViolationDetector',
                                                                              persistence_id)

    #    persistenceData = PersistencyUtil.loadJson(self.persistence_file_name)
    #   if persistenceData is None:
    #     self.knownPathSet = set()
    #   else:
    #     self.knownPathSet = set(persistenceData)

    def receive_atom(self, log_atom):
        """Receive a parsed atom and check all the classification rules, that will trigger correlation rule evaluation and event
        triggering on violations."""
        self.last_log_atom = log_atom
        for rule in self.event_classification_ruleset:
            rule.match(log_atom)

    def get_time_trigger_class(self):
        """Get the trigger class this component should be registered for. This trigger is used mainly for persistency, so real-time
        triggering is needed. Use also real-time triggering for analysis: usually events for violations (timeouts) are generated when
        receiving newer atoms. This is just the fallback periods of input silence."""
        return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def do_timer(self, trigger_time):
        """Check for any rule violations and if the current ruleset should be persisted."""
        # Persist the state only quite infrequently: As most correlation rules react in timeline of seconds, the persisted data will most
        # likely be unsuitable to catch lost events. So persistency is mostly to capture the correlation rule context, e.g. the history
        # of loglines matched before.
        if self.next_persist_time - trigger_time < 0:
            self.do_persist()

        # Check all correlation rules, generate single events for each violated rule, possibly containing multiple records. As we might
        # be processing historic data, the timestamp last seen is unknown here. Hence rules not receiving newer events might not notice
        # for a long time, that they hold information about correlation impossible to fulfil. Take the newest timestamp of any rule
        # and use it for checking.
        newest_timestamp = 0.0
        for rule in self.event_correlation_ruleset:
            newest_timestamp = max(newest_timestamp, rule.last_timestamp_seen)

        for rule in self.event_correlation_ruleset:
            check_result = rule.check_status(newest_timestamp)
            if check_result is None:
                continue
            self.last_log_atom.set_timestamp(trigger_time)
            r = {'RuleId': rule.rule_id, 'MinTimeDelta': rule.min_time_delta, 'MaxTimeDelta': rule.max_time_delta,
                 'MaxArtefactsAForSingleB': rule.max_artefacts_a_for_single_b, 'ArtefactMatchParameters': rule.artefact_match_parameters,
                 'HistoryAEvents': rule.history_a_events, 'HistoryBEvents': rule.history_b_events,
                 'LastTimestampSeen': rule.last_timestamp_seen}
            history = {'MaxItems': rule.correlation_history.max_items}
            h = []
            for item in rule.correlation_history.history:
                h.append(repr(item))
            history['History'] = h
            r['correlation_history'] = history
            analysis_component = {'Rule': r, 'CheckResult': check_result, 'NewestTimestamp': newest_timestamp}
            event_data = {'AnalysisComponent': analysis_component}
            for listener in self.anomaly_event_handlers:
                listener.receive_event('Analysis.%s' % self.__class__.__name__, 'Correlation rule "%s" violated' % rule.rule_id,
                                       [check_result[0]], event_data, self.last_log_atom, self)
        return 10.0

    def do_persist(self):
        """Immediately write persistence data to storage."""
        # PersistencyUtil.storeJson(self.persistence_file_name, list(self.knownPathSet))
        self.next_persist_time = time.time() + 600.0


class EventClassSelector(Rules.MatchAction):
    """This match action selects one event class by adding it to a MatchRule. It then triggers the appropriate CorrelationRules."""

    def __init__(self, action_id, artefact_a_rules, artefact_b_rules):
        self.action_id = action_id
        self.artefact_a_rules = artefact_a_rules
        self.artefact_b_rules = artefact_b_rules

    def match_action(self, log_atom):
        """This method is invoked if a rule rule has matched.
        @param log_atom the parser match_element that was also matching the rules."""
        if self.artefact_a_rules is not None:
            for a_rule in self.artefact_a_rules:
                a_rule.update_artefact_a(self, log_atom)
        if self.artefact_b_rules is not None:
            for b_rule in self.artefact_b_rules:
                b_rule.update_artefact_b(self, log_atom)


class CorrelationRule:
    """This class defines a correlation rule to match artefacts A and B, where a hidden event A* always triggers at least one
    artefact A and the the hidden event B*, thus triggering also at least one artefact B."""

    def __init__(self, rule_id, min_time_delta, max_time_delta, max_artefacts_a_for_single_b=1, artefact_match_parameters=None):
        """Create the correlation rule.
        @param artefact_match_parameters if not none, two artefacts A and B will be only treated as correlated when all the
        parsed artefact attributes identified by the list of attribute path tuples match.
        @param min_time_delta minimal delta in seconds, that artefact B may be observed after artefact A. Negative values are allowed
        as artefact B may be found before A. """
        self.rule_id = rule_id
        self.min_time_delta = min_time_delta
        self.max_time_delta = max_time_delta
        self.max_artefacts_a_for_single_b = max_artefacts_a_for_single_b
        self.artefact_match_parameters = artefact_match_parameters
        self.history_a_events = []
        self.history_b_events = []
        self.last_timestamp_seen = 0.0
        self.correlation_history = LogarithmicBackoffHistory(10)

    def update_artefact_a(self, selector, log_atom):
        """Append entry to the event history A."""
        history_entry = self.prepare_history_entry(selector, log_atom)
        # Check if event A could be discarded immediately.
        self.history_a_events.append(history_entry)

    def update_artefact_b(self, selector, log_atom):
        """Append entry to the event history B."""
        history_entry = self.prepare_history_entry(selector, log_atom)
        # Check if event B could be discarded immediately.
        self.history_b_events.append(history_entry)

    def check_status(self, newest_timestamp, max_violations=20):
        """@return None if status is OK. Returns a tuple containing a descriptive message and a list of violating log data lines
        on error."""

        # This part of code would be good target to be implemented as native library with optimized algorithm in future.
        a_pos = 0
        check_range = len(self.history_a_events)
        violation_logs = []
        violation_message = ''
        num_violations = 0
        while a_pos < check_range:
            deleted = False
            check_range = len(self.history_a_events)
            a_event = self.history_a_events[a_pos]
            if a_event is None:
                continue
            a_event_time = a_event[0]
            b_pos = 0
            while b_pos < len(self.history_b_events):
                b_event = self.history_b_events[b_pos]
                if b_event is None:
                    continue
                b_event_time = b_event[0]
                delta = b_event_time - a_event_time
                if delta < self.min_time_delta:
                    # See if too early, if yes go to next element. As we will not check again any older aEvents in this loop, skip
                    # all bEvents up to this position in future runs.
                    if b_pos < len(self.history_b_events):
                        violation_line = a_event[3].match_element.match_string
                        if isinstance(violation_line, bytes):
                            violation_line = violation_line.decode()
                            if num_violations <= max_violations:
                                violation_message += 'FAIL: B-Event for \"%s\" (%s) was found too early!\n' % (
                                                     violation_line, a_event[2].action_id)
                            violation_logs.append(violation_line)
                            del self.history_a_events[a_pos]
                            del self.history_b_events[b_pos]
                            deleted = True
                            check_range = check_range - 1
                            num_violations = num_violations + 1
                            break
                    continue
                # Too late, no other b_event may match this a_event
                if delta > self.max_time_delta:
                    violation_line = a_event[3].match_element.match_string
                    if isinstance(violation_line, bytes):
                        violation_line = violation_line.decode()
                        if num_violations <= max_violations:
                            violation_message += 'FAIL: B-Event for \"%s\" (%s) was not found in time!\n' % (
                                                 violation_line, a_event[2].action_id)
                        violation_logs.append(violation_line)
                        del self.history_a_events[a_pos]
                        del self.history_b_events[b_pos]
                        deleted = True
                        check_range = check_range - 1
                        num_violations = num_violations + 1
                    break
                # So time range is OK, see if match parameters are also equal.
                violation_found = False
                for check_pos in range(4, len(a_event)):
                    if a_event[check_pos] != b_event[check_pos]:
                        violation_line = a_event[3].match_element.match_string
                        if isinstance(violation_line, bytes):
                            violation_line = violation_line.decode()
                            if num_violations <= max_violations:
                                violation_message += 'FAIL: \"%s\" (%s) %s is not equal %s\n' % (
                                    violation_line, a_event[2].action_id, a_event[check_pos], b_event[check_pos])
                            violation_logs.append(violation_line)
                            del self.history_a_events[a_pos]
                            del self.history_b_events[b_pos]
                            deleted = True
                            check_range = check_range - 1
                            num_violations = num_violations + 1
                            violation_found = True
                        break
                check_pos = check_pos + 1
                if violation_found:
                    continue

                # We want to keep a history of good matches to ease diagnosis of correlation failures. Keep information about current line
                # for reference.
                self.correlation_history.add_object((a_event[3].match_element.match_string, a_event[2].action_id,
                                                     b_event[3].match_element.match_string, b_event[2].action_id))
                del self.history_a_events[a_pos]
                del self.history_b_events[b_pos]
                deleted = True
                check_range = check_range - 1
                b_pos = b_pos + 1
            if deleted is False:
                a_pos = a_pos + 1
        # After checking all aEvents before a_pos were cleared, otherwise they violate a correlation rule.
        for a_pos in range(0, check_range):
            a_event = self.history_a_events[a_pos]
            if a_event is None:
                continue
            delta = newest_timestamp - a_event[0]
            if delta > self.max_time_delta:
                violation_line = a_event[3].match_element.match_string
                if isinstance(violation_line, bytes):
                    violation_line = violation_line.decode()
                    if num_violations <= max_violations:
                        violation_message += 'FAIL: B-Event for \"%s\" (%s) was not found in time!\n' % (
                                             violation_line, a_event[2].action_id)
                    violation_logs.append(violation_line)
                    del self.history_a_events[a_pos]
                    deleted = True
                    check_range = check_range - 1
                    num_violations = num_violations + 1
                break

        if num_violations > max_violations:
            violation_message += '... (%d more)\n' % (num_violations - max_violations)
        if num_violations != 0 and len(self.correlation_history.get_history()) > 0:
            violation_message += 'Historic examples:\n'
            for record in self.correlation_history.get_history():
                violation_message += '  "%s" (%s) ==> "%s" (%s)\n' % (record[0].decode(), record[1], record[2].decode(), record[3])

        if num_violations == 0:
            return None
        return violation_message, violation_logs

    def prepare_history_entry(self, selector, log_atom):
        """Return a history entry for a parser match."""
        parser_match = log_atom.parser_match
        timestamp = log_atom.get_timestamp()
        if timestamp is None:
            timestamp = time.time()
        length = 4
        if self.artefact_match_parameters is not None:
            length += len(self.artefact_match_parameters)
        result = [None] * length
        result[0] = timestamp
        result[1] = 0
        result[2] = selector
        result[3] = parser_match

        if result[0] < self.last_timestamp_seen:
            raise Exception('Unsorted!')
        self.last_timestamp_seen = result[0]

        if self.artefact_match_parameters is not None:
            pos = 4
            v_dict = parser_match.get_match_dictionary()
            for artefact_match_parameter in self.artefact_match_parameters:
                for param_path in artefact_match_parameter:
                    match_element = v_dict.get(param_path, None)
                    if match_element is not None:
                        result[pos] = match_element.match_object
                        pos += 1
        return result
