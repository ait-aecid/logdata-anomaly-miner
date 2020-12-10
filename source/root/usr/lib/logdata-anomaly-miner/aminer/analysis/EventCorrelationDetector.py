"""
This module defines an evaluator and generator for event rules.
The overall idea of generation is
1) For each processed event A, randomly select another event B occurring within queue_delta_time.
2) If B chronologically occurs after A, create the hypothesis A => B (observing event A implies that event B must be observed within
current_time+queue_delta_time). If B chronologically occurs before A, create the hypothesis B <= A (observing event A implies that event B
must be observed within currentTime-queueDeltaTime).
3) Observe for a long time (max_observations) whether the hypothesis holds.
4) If the hypothesis holds, transform it to a rule. Otherwise, discard the hypothesis.

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

from collections import deque
import random
import math
import time
import logging

from aminer import AMinerConfig
from aminer.AMinerConfig import STAT_LEVEL, STAT_LOG_NAME
from aminer.AnalysisChild import AnalysisContext
from aminer.input import AtomHandlerInterface
from aminer.util import PersistenceUtil
from aminer.util import TimeTriggeredComponentInterface
from aminer.analysis import CONFIG_KEY_LOG_LINE_PREFIX


class EventCorrelationDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """This class tries to find time correlation patterns between different log atom events."""

    def __init__(self, aminer_config, anomaly_event_handlers, paths=None, max_hypotheses=1000, hypothesis_max_delta_time=5.0,
                 generation_probability=1.0, generation_factor=1.0, max_observations=500, p0=0.9, alpha=0.05, candidates_size=10,
                 hypotheses_eval_delta_time=120.0, delta_time_to_discard_hypothesis=180.0, check_rules_flag=False,
                 auto_include_flag=True, ignore_list=None, persistence_id='Default', output_log_line=True, constraint_list=None):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param max_hypotheses maximum amount of hypotheses and rules hold in memory.
        @param hypothesis_max_delta_time time span of events considered for hypothesis generation.
        @param generation_probability probability in [0, 1] that currently processed log line is considered for hypothesis with each of the
        candidates.
        @param generation_factor likelihood in [0, 1] that currently processed log line is added to the set of candidates for hypothesis
        generation.
        @param max_observations maximum amount of evaluations before hypothesis is transformed into a rule or discarded or rule is
        evaluated.
        @param p0 expected value for hypothesis evaluation distribution.
        @param alpha confidence value for hypothesis evaluation.
        @param candidates_size maximum number of stored candidates used for hypothesis generation.
        @param hypotheses_eval_delta_time duration between hypothesis evaluation phases that remove old hypotheses that are likely to remain
        unused.
        @param delta_time_to_discard_hypothesis time span required for old hypotheses to be discarded.
        @param check_rules_flag specifies whether existing rules are evaluated.
        @param auto_include_flag specifies whether new hypotheses are generated.
        @param ignore_list list of paths that are not considered for correlation, i.e., events that contain one of these paths are
        omitted. The default value is [] as None is not iterable.
        @param persistence_id name of persitency document.
        """
        self.anomaly_event_handlers = anomaly_event_handlers
        self.paths = paths
        self.last_unhandled_match = None
        self.next_persist_time = None
        self.total_records = 0
        self.max_hypotheses = max_hypotheses
        self.hypothesis_max_delta_time = hypothesis_max_delta_time
        self.generation_probability = generation_probability
        self.generation_factor = generation_factor
        self.max_observations = max_observations
        self.p0 = p0
        self.alpha = alpha
        self.candidates_size = candidates_size
        self.forward_hypotheses = {}
        self.back_hypotheses = {}
        self.forward_hypotheses_inv = {}
        self.back_hypotheses_inv = {}
        self.hypotheses_eval_delta_time = hypotheses_eval_delta_time
        self.last_hypotheses_eval_timestamp = -1.0
        self.delta_time_to_discard_hypothesis = delta_time_to_discard_hypothesis
        self.check_rules_flag = check_rules_flag
        self.auto_include_flag = auto_include_flag
        self.ignore_list = ignore_list
        if self.ignore_list is None:
            self.ignore_list = []
        self.constraint_list = constraint_list
        if self.constraint_list is None:
            self.constraint_list = []
        self.forward_rule_queue = deque([])
        self.back_rule_queue = deque([])
        self.forward_hypotheses_queue = deque([])
        self.back_hypotheses_queue = deque([])
        self.hypothesis_candidates = deque([])
        self.sum_unstable_unknown_hypotheses = 0
        self.last_event_occurrence = {}
        self.min_eval_true_dict = {}
        self.min_eval_true_dict_max_size = 1000
        self.sample_events = {}
        self.back_rules = {}
        self.forward_rules = {}
        self.back_rules_inv = {}
        self.forward_rules_inv = {}

        # Compute the initial minimum amount of positive evaluations for hypotheses to become rules.
        # For rules, this value can be different and will be computed based on the sample observations.
        self.min_eval_true = self.get_min_eval_true(self.max_observations, self.p0, self.alpha)

        self.aminer_config = aminer_config
        self.output_log_line = output_log_line

        self.log_success = 0
        self.log_total = 0
        self.log_forward_rules_learned = 0
        self.log_back_rules_learned = 0
        self.log_new_forward_rules = []
        self.log_new_back_rules = []

        PersistenceUtil.add_persistable_component(self)
        self.persistence_file_name = AMinerConfig.build_persistence_file_name(aminer_config, 'EventCorrelationDetector', persistence_id)
        self.persistence_id = persistence_id
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)

        if persistence_data is not None:
            for record in persistence_data:
                implication_direction = record[0]
                trigger_event = tuple(record[1])
                implied_event = tuple(record[2])
                max_obs = record[3]
                min_eval_t = record[4]
                rule = Implication(trigger_event, implied_event, None, max_obs, min_eval_t)
                rule.stable = 1
                if implication_direction == 'back':
                    if trigger_event in self.back_rules:
                        self.back_rules[trigger_event].append(rule)
                    else:
                        self.back_rules[trigger_event] = [rule]
                    if implied_event in self.back_rules_inv:
                        self.back_rules_inv[implied_event].append(rule)
                    else:
                        self.back_rules_inv[implied_event] = [rule]
                elif implication_direction == 'forward':
                    if trigger_event in self.forward_rules:
                        self.forward_rules[trigger_event].append(rule)
                    else:
                        self.forward_rules[trigger_event] = [rule]
                    if implied_event in self.forward_rules_inv:
                        self.forward_rules_inv[implied_event].append(rule)
                    else:
                        self.forward_rules_inv[implied_event] = [rule]
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).debug('%s loaded persistence data.', self.__class__.__name__)

    # skipcq: PYL-R1710
    def get_min_eval_true(self, max_observations, p0, alpha):
        """
        Compute the critical value (minimal amount of true evaluations) for a hypothesis.
        The form of the hypothesis is <eventA> implies <eventB> with at least probability p0 to be accepted.
        This method tries to be efficient by
        - Storing already computed critical values in a dictionary
        - Swapping (1 - p0) and p0 and replace alpha with (1 - alpha) to reduce loops
        """
        if (max_observations, p0, alpha) in self.min_eval_true_dict:
            return self.min_eval_true_dict[(max_observations, p0, alpha)]

        sum1 = 0.0
        max_observations_factorial = math.factorial(max_observations)
        i_factorial = 1
        for i in range(max_observations + 1):
            i_factorial = i_factorial * max(i, 1)
            # No float conversion possible for huge numbers; use integer division.
            sum1 = sum1 + max_observations_factorial / (i_factorial * math.factorial(max_observations - i)) * ((1 - p0) ** i) * (
                      p0 ** (max_observations - i))
            if sum1 > (1 - alpha):
                if len(self.min_eval_true_dict) <= self.min_eval_true_dict_max_size:
                    # Store common values for fast retrieval
                    self.min_eval_true_dict[(max_observations, p0, alpha)] = max_observations - i
                return max_observations - i

    def receive_atom(self, log_atom):
        """Receive a log atom from a source."""
        self.log_total += 1
        timestamp = log_atom.get_timestamp()
        if timestamp is None:
            log_atom.atom_time = time.time()
            timestamp = log_atom.atom_time

        parser_match = log_atom.parser_match
        self.total_records += 1

        # Skip paths from ignore_list.
        for ignore_path in self.ignore_list:
            if ignore_path in parser_match.get_match_dictionary().keys():
                return
        if self.paths is None or len(self.paths) == 0:
            # Event is defined by the full path of log atom.
            constraint_path = False
            for constraint_path in self.constraint_list:
                if parser_match.get_match_dictionary().get(constraint_path) is not None:
                    constraint_path = True
                    break
            if not constraint_path and self.constraint_list != []:
                return
            log_event = tuple(parser_match.get_match_dictionary().keys())
        else:
            # Event is defined by value combos in paths
            values = []
            all_values_none = True
            for path in self.paths:
                match = parser_match.get_match_dictionary().get(path)
                if match is None:
                    continue
                if isinstance(match.match_object, bytes):
                    value = match.match_object.decode()
                else:
                    value = str(match.match_object)
                if value is not None:
                    all_values_none = False
                values.append(value)
            if all_values_none is True:
                return
            log_event = tuple(values)

        # Store last seen sample event to improve output.
        self.sample_events[log_event] = log_atom.raw_data

        if self.check_rules_flag:
            # Only check rules without generating new hypotheses.

            # Trigger implication A => B when A occurs.
            if log_event in self.forward_rules:
                for rule in self.forward_rules[log_event]:
                    rule.rule_trigger_timestamps.append(log_atom.atom_time)
                    self.forward_rule_queue.append(rule)

            # Resolve triggered implication A => B when B occurs.
            if log_event in self.forward_rules_inv:
                for rule in self.forward_rules_inv[log_event]:
                    # Find first non-observed trigger timestamp
                    trigger_timestamp_index = -1
                    for trigger_timestamp in rule.rule_trigger_timestamps:
                        trigger_timestamp_index += 1
                        if trigger_timestamp != 'obs':
                            break
                    if trigger_timestamp_index != -1 and \
                            rule.rule_trigger_timestamps[trigger_timestamp_index] != 'obs' and \
                            rule.rule_trigger_timestamps[trigger_timestamp_index] >= log_atom.atom_time - self.hypothesis_max_delta_time:
                        # Implication was triggered; append positive evaluation and mark as seen.
                        rule.add_rule_observation(1)
                        rule.rule_trigger_timestamps[trigger_timestamp_index] = 'obs'

            # Clean up triggered/resolved implications.
            while len(self.forward_rule_queue) > 0:
                rule = self.forward_rule_queue[0]
                if len(rule.rule_trigger_timestamps) == 0:
                    # Triggered timestamp was already deleted somewhere else.
                    self.forward_rule_queue.popleft()
                    continue
                if rule.rule_trigger_timestamps[0] == 'obs':
                    # Remove triggered timestamp.
                    rule.rule_trigger_timestamps.popleft()
                    self.forward_rule_queue.popleft()
                    continue
                if rule.rule_trigger_timestamps[0] < log_atom.atom_time - self.hypothesis_max_delta_time:
                    # Too much time has elapsed; append negative evaluation.
                    rule.add_rule_observation(0)
                    rule.rule_trigger_timestamps.popleft()
                    self.forward_rule_queue.popleft()
                    if not rule.evaluate_rule():
                        original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX)
                        if original_log_line_prefix is None:
                            original_log_line_prefix = ''
                        tmp_string = 'Rule: %s -> %s\n  Expected: %s/%s\n  Observed: %s/%s' % (
                                        str(rule.trigger_event), str(rule.implied_event), str(rule.min_eval_true),
                                        str(rule.max_observations), str(sum(rule.rule_observations)),
                                        str(len(rule.rule_observations)))
                        if self.output_log_line:
                            sorted_log_lines = [tmp_string + '\n' + original_log_line_prefix + repr(log_atom.raw_data)]
                        else:
                            sorted_log_lines = [tmp_string + repr(log_atom.raw_data)]
                        for listener in self.anomaly_event_handlers:
                            implied_event = None
                            trigger_event = None
                            if rule.implied_event in self.sample_events.keys():
                                implied_event = self.sample_events[rule.implied_event]
                            if rule.trigger_event in self.sample_events.keys():
                                trigger_event = self.sample_events[rule.trigger_event]
                            listener.receive_event(
                                'analysis.EventCorrelationDetector',
                                'Correlation rule violated! Event %s is missing, but should follow event %s' % (
                                    repr(implied_event), repr(trigger_event)),
                                sorted_log_lines,
                                {'RuleInfo': {'Rule': str(rule.trigger_event) + '->' + str(rule.implied_event),
                                              'Expected': str(rule.min_eval_true) + '/' + str(rule.max_observations),
                                              'Observed': str(sum(rule.rule_observations)) + '/' + str(len(rule.rule_observations))}},
                                log_atom, self)
                        rule.rule_observations = deque([])
                    continue
                break

            # Trigger implication B <= A when B occurs.
            if log_event in self.back_rules_inv:
                for rule in self.back_rules_inv[log_event]:
                    rule.rule_trigger_timestamps.append(log_atom.atom_time)
                    self.back_rule_queue.append(rule)

            # Resolve triggered implication B <= A when A occurs.
            if log_event in self.back_rules:
                for rule in self.back_rules[log_event]:
                    # Find first non-observed trigger timestamp
                    trigger_timestamp_index = -1
                    for trigger_timestamp in rule.rule_trigger_timestamps:
                        trigger_timestamp_index += 1
                        if trigger_timestamp != 'obs':
                            break
                    if trigger_timestamp_index != -1 and \
                            rule.rule_trigger_timestamps[trigger_timestamp_index] != 'obs' and \
                            rule.rule_trigger_timestamps[trigger_timestamp_index] >= log_atom.atom_time - self.hypothesis_max_delta_time:
                        rule.add_rule_observation(1)
                        rule.rule_trigger_timestamps[trigger_timestamp_index] = 'obs'
                    else:
                        rule.add_rule_observation(0)
                        if not rule.evaluate_rule():
                            original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX)
                            if original_log_line_prefix is None:
                                original_log_line_prefix = ''
                            tmp_string = 'Rule: %s <- %s\n  Expected: %s/%s\n  Observed: %s/%s' % (
                                            str(rule.implied_event), str(rule.trigger_event), str(rule.min_eval_true),
                                            str(rule.max_observations), str(sum(rule.rule_observations)),
                                            str(len(rule.rule_observations)))
                            if self.output_log_line:
                                sorted_log_lines = [tmp_string + '\n' + original_log_line_prefix + repr(log_atom.raw_data)]
                            else:
                                sorted_log_lines = [tmp_string + repr(log_atom.raw_data)]
                            for listener in self.anomaly_event_handlers:
                                implied_event = None
                                trigger_event = None
                                if rule.implied_event in self.sample_events.keys():
                                    implied_event = self.sample_events[rule.implied_event]
                                if rule.trigger_event in self.sample_events.keys():
                                    trigger_event = self.sample_events[rule.trigger_event]
                                listener.receive_event(
                                    'analysis.EventCorrelationDetector',
                                    'Correlation rule violated! Event %s is missing, but should precede event %s' % (
                                        repr(implied_event), repr(trigger_event)),
                                    sorted_log_lines,
                                    {'RuleInfo': {'Rule': str(rule.implied_event) + '<-' + str(rule.trigger_event),
                                                  'Expected': str(rule.min_eval_true) + '/' + str(rule.max_observations),
                                                  'Observed': str(sum(rule.rule_observations)) + '/' + str(len(rule.rule_observations))}},
                                    log_atom, self)
                            rule.rule_observations = deque([])

            # Clean up triggered/resolved implications.
            while len(self.back_rule_queue) > 0:
                rule = self.back_rule_queue[0]
                if len(rule.rule_trigger_timestamps) == 0:
                    self.back_rule_queue.popleft()
                    continue
                if rule.rule_trigger_timestamps[0] == 'obs':
                    rule.rule_trigger_timestamps.popleft()
                    self.back_rule_queue.popleft()
                    continue
                if rule.rule_trigger_timestamps[0] < log_atom.atom_time - self.hypothesis_max_delta_time:
                    rule.rule_trigger_timestamps.popleft()
                    self.back_rule_queue.popleft()
                    continue
                break

        if self.auto_include_flag:
            # Generate new hypotheses and rules.

            # Keep track of event occurrences, relevant for removing old hypotheses.
            self.last_event_occurrence[log_event] = log_atom.atom_time

            # Trigger implication A => B when A occurs.
            if log_event in self.forward_hypotheses:
                for implication in self.forward_hypotheses[log_event]:
                    if implication.stable == 0:
                        implication.hypothesis_trigger_timestamps.append(log_atom.atom_time)
                        self.forward_hypotheses_queue.append(implication)

            # Resolve triggered implication A => B when B occurs.
            if log_event in self.forward_hypotheses_inv:
                delete_hypotheses = []
                for implication in self.forward_hypotheses_inv[log_event]:
                    # Find first non-observed trigger timestamp
                    trigger_timestamp_index = -1
                    for trigger_timestamp in implication.hypothesis_trigger_timestamps:
                        trigger_timestamp_index += 1
                        if trigger_timestamp != 'obs':
                            break
                    if trigger_timestamp_index != -1 and \
                            str(implication.hypothesis_trigger_timestamps[trigger_timestamp_index]) != 'obs' and \
                            implication.hypothesis_trigger_timestamps[trigger_timestamp_index] >= log_atom.atom_time - \
                            self.hypothesis_max_delta_time and \
                            implication.stable == 0:
                        implication.add_hypothesis_observation(1, log_atom.atom_time)
                        # Mark this timestamp as observed
                        implication.hypothesis_trigger_timestamps[trigger_timestamp_index] = 'obs'
                        # Since only true observations occur here, check for instability not necessary.
                        if implication.compute_hypothesis_stability() == 1:
                            # Update p and min_eval_true according to the results in the sample.
                            p = implication.hypothesis_evaluated_true / implication.hypothesis_observations
                            implication.min_eval_true = self.get_min_eval_true(self.max_observations, p, self.alpha)
                            # Add hypothesis to rules.
                            if implication.trigger_event in self.forward_rules:
                                self.forward_rules[implication.trigger_event].append(implication)
                                self.log_forward_rules_learned += 1
                                self.log_new_forward_rules.append(implication)
                            else:
                                self.forward_rules[implication.trigger_event] = [implication]
                                self.log_forward_rules_learned += 1
                                self.log_new_forward_rules.append(implication)
                            if implication.implied_event in self.forward_rules_inv:
                                self.forward_rules_inv[implication.implied_event].append(implication)
                            else:
                                self.forward_rules_inv[implication.implied_event] = [implication]
                            # Drop time stamps of previous observations, start new observations for rule.
                            implication.hypothesis_trigger_timestamps.clear()
                            self.sum_unstable_unknown_hypotheses = self.sum_unstable_unknown_hypotheses - 1
                            # Remove implication from list of hypotheses.
                            self.forward_hypotheses[implication.trigger_event].remove(implication)
                            delete_hypotheses.append(implication)
                for delete_hypothesis in delete_hypotheses:
                    self.forward_hypotheses_inv[log_event].remove(delete_hypothesis)

            # Clean up triggered/resolved implications.
            while len(self.forward_hypotheses_queue) > 0:
                implication = self.forward_hypotheses_queue[0]
                if len(implication.hypothesis_trigger_timestamps) == 0:
                    # Triggered timestamp was already deleted somewhere else.
                    self.forward_hypotheses_queue.popleft()
                    continue
                if implication.hypothesis_trigger_timestamps[0] == 'obs':
                    # Remove triggered timestamp.
                    implication.hypothesis_trigger_timestamps.popleft()
                    self.forward_hypotheses_queue.popleft()
                    continue
                if implication.hypothesis_trigger_timestamps[0] < log_atom.atom_time - self.hypothesis_max_delta_time:
                    # Too much time has elapsed; append negative evaluation.
                    implication.hypothesis_trigger_timestamps.popleft()
                    implication.add_hypothesis_observation(0, log_atom.atom_time)
                    if implication.compute_hypothesis_stability() == -1:
                        if implication.trigger_event in self.forward_hypotheses and implication in self.forward_hypotheses[
                                implication.trigger_event]:
                            # This check is required if a hypothesis was already removed, but triggered hypotheses are still in the queue.
                            self.sum_unstable_unknown_hypotheses = self.sum_unstable_unknown_hypotheses - 1
                            self.forward_hypotheses[implication.trigger_event].remove(implication)
                            self.forward_hypotheses_inv[implication.implied_event].remove(implication)
                            if len(self.forward_hypotheses[implication.trigger_event]) == 0:
                                del self.forward_hypotheses[implication.trigger_event]
                            if len(self.forward_hypotheses_inv[implication.implied_event]) == 0:
                                del self.forward_hypotheses_inv[implication.implied_event]
                    self.forward_hypotheses_queue.popleft()
                    continue
                break

            # Trigger implication B <= A when B occurs.
            if log_event in self.back_hypotheses_inv:
                for implication in self.back_hypotheses_inv[log_event]:
                    if implication.stable == 0:
                        implication.hypothesis_trigger_timestamps.append(log_atom.atom_time)
                        self.back_hypotheses_queue.append(implication)

            # Resolve triggered implication B <= A when A occurs.
            if log_event in self.back_hypotheses:
                delete_hypotheses = []
                for implication in self.back_hypotheses[log_event]:
                    if implication.stable == 0:
                        # Find first non-observed trigger timestamp
                        trigger_timestamp_index = -1
                        for trigger_timestamp in implication.hypothesis_trigger_timestamps:
                            trigger_timestamp_index += 1
                            if trigger_timestamp != 'obs':
                                break
                        if trigger_timestamp_index != -1 and \
                                str(implication.hypothesis_trigger_timestamps[trigger_timestamp_index]) != 'obs' and \
                                implication.hypothesis_trigger_timestamps[trigger_timestamp_index] >= log_atom.atom_time - \
                                self.hypothesis_max_delta_time:
                            implication.add_hypothesis_observation(1, log_atom.atom_time)
                            implication.hypothesis_trigger_timestamps[trigger_timestamp_index] = 'obs'
                            # Since only true observations occur here, check for instability not necessary.
                            if implication.compute_hypothesis_stability() == 1:
                                # Update p and min_eval_true according to the results in the sample.
                                p = implication.hypothesis_evaluated_true / implication.hypothesis_observations
                                implication.min_eval_true = self.get_min_eval_true(self.max_observations, p, self.alpha)
                                # Add hypothesis to rules.
                                if implication.trigger_event in self.back_rules:
                                    self.back_rules[implication.trigger_event].append(implication)
                                    self.log_back_rules_learned += 1
                                    self.log_new_back_rules.append(implication)
                                else:
                                    self.back_rules[implication.trigger_event] = [implication]
                                    self.log_back_rules_learned += 1
                                    self.log_new_back_rules.append(implication)
                                if implication.implied_event in self.back_rules_inv:
                                    self.back_rules_inv[implication.implied_event].append(implication)
                                else:
                                    self.back_rules_inv[implication.implied_event] = [implication]
                                # Drop time stamps of previous observations, start new observations for rule.
                                implication.hypothesis_trigger_timestamps.clear()
                                self.sum_unstable_unknown_hypotheses = self.sum_unstable_unknown_hypotheses - 1
                                # Remove implication from list of hypotheses.
                                delete_hypotheses.append(implication)
                                self.back_hypotheses_inv[implication.implied_event].remove(implication)
                        else:
                            implication.add_hypothesis_observation(0, log_atom.atom_time)
                            if implication.compute_hypothesis_stability() == -1:
                                self.sum_unstable_unknown_hypotheses = self.sum_unstable_unknown_hypotheses - 1
                                delete_hypotheses.append(implication)
                                self.back_hypotheses_inv[implication.implied_event].remove(implication)
                                if len(self.back_hypotheses_inv[implication.implied_event]) == 0:
                                    del self.back_hypotheses_inv[implication.implied_event]
                for delete_hypothesis in delete_hypotheses:
                    self.back_hypotheses[log_event].remove(delete_hypothesis)
                if len(self.back_hypotheses[log_event]) == 0:
                    del self.back_hypotheses[log_event]

            # Clean up triggered/resolved implications.
            while len(self.back_hypotheses_queue) > 0:
                implication = self.back_hypotheses_queue[0]
                if len(implication.hypothesis_trigger_timestamps) == 0:
                    self.back_hypotheses_queue.popleft()
                    continue
                if implication.hypothesis_trigger_timestamps[0] == 'obs':
                    implication.hypothesis_trigger_timestamps.popleft()
                    self.back_hypotheses_queue.popleft()
                    continue
                if implication.hypothesis_trigger_timestamps[0] < log_atom.atom_time - self.hypothesis_max_delta_time:
                    implication.hypothesis_trigger_timestamps.popleft()
                    self.back_hypotheses_queue.popleft()
                    continue
                break

            # Generate new hypotheses
            if len(self.hypothesis_candidates) > 0 and random.uniform(0.0, 1.0) < self.generation_factor:
                implication_direction = random.randint(0, 1)
                if self.sum_unstable_unknown_hypotheses >= self.max_hypotheses:
                    # If too many hypotheses exist, do nothing.
                    implication_direction = -1
                if implication_direction == 0:
                    for candidate in self.hypothesis_candidates:
                        candidate_event = candidate[0]
                        # Chronological implication is: candidate_event <= log_event
                        implication = Implication(log_event, candidate_event, log_atom.atom_time, self.max_observations, self.min_eval_true)
                        if log_event in self.back_hypotheses:
                            # Only add hypotheses that are not already present as hypotheses.
                            continue_outer = False
                            for imp in self.back_hypotheses[log_event]:
                                if candidate_event == imp.implied_event:
                                    continue_outer = True
                                    break
                            if continue_outer:
                                continue
                        if log_event in self.back_rules:
                            # Only add hypotheses that are not already present as rules.
                            continue_outer = False
                            for imp in self.back_rules[log_event]:
                                if candidate_event == imp.implied_event:
                                    continue_outer = True
                                    break
                            if continue_outer:
                                continue
                        # At this point it is known that the implication is new, otherwise a continue statement would have been reached
                        if log_event in self.back_hypotheses:
                            self.back_hypotheses[log_event].append(implication)
                        else:
                            self.back_hypotheses[log_event] = [implication]
                        if candidate_event in self.back_hypotheses_inv:
                            self.back_hypotheses_inv[candidate_event].append(implication)
                        else:
                            self.back_hypotheses_inv[candidate_event] = [implication]
                        self.sum_unstable_unknown_hypotheses = self.sum_unstable_unknown_hypotheses + 1
                elif implication_direction == 1:
                    for candidate in self.hypothesis_candidates:
                        candidate_event = candidate[0]
                        # Chronological implication is: candidate_event => log_event
                        # Skip event A => event A since already covered by back hypotheses
                        if log_event != candidate_event:
                            implication = Implication(candidate_event, log_event, log_atom.atom_time, self.max_observations,
                                                      self.min_eval_true)
                            if candidate_event in self.forward_hypotheses:
                                # Only add hypotheses that are not already present as hypotheses.
                                continue_outer = False
                                for imp in self.forward_hypotheses[candidate_event]:
                                    if log_event == imp.implied_event:
                                        continue_outer = True
                                        break
                                if continue_outer:
                                    continue
                            if candidate_event in self.forward_rules:
                                # Only add hypotheses that are not already present as rules.
                                continue_outer = False
                                for imp in self.forward_rules[candidate_event]:
                                    if log_event == imp.implied_event:
                                        continue_outer = True
                                        break
                                if continue_outer:
                                    continue
                            # At this point it is known that the implication is new, otherwise a continue statement would have been reached
                            if candidate_event in self.forward_hypotheses:
                                self.forward_hypotheses[candidate_event].append(implication)
                            else:
                                self.forward_hypotheses[candidate_event] = [implication]
                            if log_event in self.forward_hypotheses_inv:
                                self.forward_hypotheses_inv[log_event].append(implication)
                            else:
                                self.forward_hypotheses_inv[log_event] = [implication]
                            self.sum_unstable_unknown_hypotheses = self.sum_unstable_unknown_hypotheses + 1

            # Periodically remove old or unstable hypotheses.
            if log_atom.atom_time >= self.last_hypotheses_eval_timestamp + self.hypotheses_eval_delta_time:
                self.last_hypotheses_eval_timestamp = log_atom.atom_time
                empty_back_events = []
                for event in self.back_hypotheses:
                    outdated_hypotheses_indexes = []
                    i = 0
                    for implication in self.back_hypotheses[event]:
                        if implication.stable == 0 and self.last_event_occurrence[
                                event] < log_atom.atom_time - self.delta_time_to_discard_hypothesis:
                            self.sum_unstable_unknown_hypotheses = self.sum_unstable_unknown_hypotheses - 1
                            outdated_hypotheses_indexes.append(i)
                            self.back_hypotheses_inv[implication.implied_event].remove(implication)
                            if len(self.back_hypotheses_inv[implication.implied_event]) == 0:
                                del self.back_hypotheses_inv[implication.implied_event]
                        i = i + 1
                    # Reverse list to avoid index changes after deletions.
                    for outdated_hypothesis_index in reversed(outdated_hypotheses_indexes):
                        del self.back_hypotheses[event][outdated_hypothesis_index]
                    if len(self.back_hypotheses[event]) == 0:
                        empty_back_events.append(event)
                for empty_back_event in empty_back_events:
                    del self.back_hypotheses[empty_back_event]
                empty_forward_events = []
                for event in self.forward_hypotheses:
                    outdated_hypotheses_indexes = []
                    i = 0
                    for implication in self.forward_hypotheses[event]:
                        if implication.stable == 0 and implication.most_recent_observation_timestamp < log_atom.atom_time -\
                                self.delta_time_to_discard_hypothesis:
                            self.sum_unstable_unknown_hypotheses = self.sum_unstable_unknown_hypotheses - 1
                            outdated_hypotheses_indexes.append(i)
                            self.forward_hypotheses_inv[implication.implied_event].remove(implication)
                            if len(self.forward_hypotheses_inv[implication.implied_event]) == 0:
                                del self.forward_hypotheses_inv[implication.implied_event]
                        i = i + 1
                    # Reverse list to avoid index changes after deletions.
                    for outdated_hypothesis_index in reversed(outdated_hypotheses_indexes):
                        del self.forward_hypotheses[event][outdated_hypothesis_index]
                    if len(self.forward_hypotheses[event]) == 0:
                        empty_forward_events.append(event)
                for empty_forward_event in empty_forward_events:
                    del self.forward_hypotheses[empty_forward_event]

            # Remove old hypothesis candidates
            while len(self.hypothesis_candidates) > 0:
                candidate = self.hypothesis_candidates[0]
                if candidate[1] < log_atom.atom_time - self.hypothesis_max_delta_time:
                    self.hypothesis_candidates.popleft()
                    continue
                break

            # Add new hypothesis candidates
            if len(self.hypothesis_candidates) < self.candidates_size:
                if random.uniform(0.0, 1.0) < self.generation_probability:
                    self.hypothesis_candidates.append((log_event, log_atom.atom_time))
        self.log_success += 1

    def get_time_trigger_class(self):
        """
        Get the trigger class this component should be registered for.
        This trigger is used only for persistence, so real-time triggering is needed.
        """
        return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def do_timer(self, trigger_time):
        """Check if current ruleset should be persisted."""
        if self.next_persist_time is None:
            return self.aminer_config.config_properties.get(AMinerConfig.KEY_PERSISTENCE_PERIOD, AMinerConfig.DEFAULT_PERSISTENCE_PERIOD)

        delta = self.next_persist_time - trigger_time
        if delta < 0:
            self.do_persist()
            delta = self.aminer_config.config_properties.get(AMinerConfig.KEY_PERSISTENCE_PERIOD, AMinerConfig.DEFAULT_PERSISTENCE_PERIOD)
        return delta

    def do_persist(self):
        """Immediately write persistence data to storage."""
        known_path_set = set()
        for event_a in self.back_rules:
            for implication in self.back_rules[event_a]:
                known_path_set.add(
                    ('back', tuple(event_a), tuple(implication.implied_event), implication.max_observations, implication.min_eval_true))
        for event_a in self.forward_rules:
            for implication in self.forward_rules[event_a]:
                known_path_set.add(
                    ('forward', tuple(event_a), tuple(implication.implied_event), implication.max_observations, implication.min_eval_true))
        PersistenceUtil.store_json(self.persistence_file_name, list(known_path_set))
        self.next_persist_time = None
        logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).debug('%s persisted data.', self.__class__.__name__)

    def log_statistics(self, component_name):
        """
        Log statistics of an AtomHandler. Override this method for more sophisticated statistics output of the AtomHandler.
        @param component_name the name of the component which is printed in the log line.
        """
        if STAT_LEVEL == 1:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %d new forward rules and %d new back rules in the last 60 "
                "minutes.", component_name, self.log_success, self.log_total, self.log_forward_rules_learned, self.log_back_rules_learned)
        elif STAT_LEVEL == 2:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %d new forward rules and %d new back rules in the last "
                "60 minutes. Following new forward rules were learned: %d. Following new back rules were learned: %d", component_name,
                self.log_success, self.log_total, self.log_forward_rules_learned, self.log_back_rules_learned,
                self.log_forward_rules_learned, self.log_back_rules_learned)
        self.log_success = 0
        self.log_total = 0
        self.log_forward_rules_learned = 0
        self.log_back_rules_learned = 0
        self.log_new_forward_rules = []
        self.log_new_back_rules = []

    def allowlist_event(self, event_type, sorted_log_lines, event_data, allowlisting_data):
        """
        Allowlist an event generated by this source using the information emitted when generating the event.
        @return a message with information about allowlisting
        @throws Exception when allowlisting of this special event using given allowlisting_data was not possible.
        """
        if event_type != 'Analysis.%s' % self.__class__.__name__:
            msg = 'Event not from this source'
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if allowlisting_data is not None:
            msg = 'Allowlisting data not understood by this detector'
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if event_data[1] not in self.constraint_list:
            self.constraint_list.append(event_data[1])
        return 'Allowlisted path %s in %s' % (event_data[1], sorted_log_lines[0])

    def blocklist_event(self, event_type, sorted_log_lines, event_data, blocklisting_data):
        """
        Blocklist an event generated by this source using the information emitted when generating the event.
        @return a message with information about blocklisting
        @throws Exception when blocklisting of this special event using given blocklisting_data was not possible.
        """
        if event_type != 'Analysis.%s' % self.__class__.__name__:
            msg = 'Event not from this source'
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if blocklisting_data is not None:
            msg = 'Blocklisting data not understood by this detector'
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if event_data[1] not in self.ignore_list:
            self.ignore_list.append(event_data[1])
        return 'Blocklisted path %s in %s' % (event_data[1], sorted_log_lines[0])


class Implication:
    """Define the shape of an implication rule."""

    def __init__(self, trigger_event, implied_event, generation_time, max_observations, min_eval_true):
        self.trigger_event = trigger_event
        self.implied_event = implied_event
        self.stable = 0  # 0 .. unknown, 1 .. stable, -1 .. unstable
        self.max_observations = max_observations
        self.min_eval_true = min_eval_true
        self.most_recent_observation_timestamp = generation_time
        self.hypothesis_trigger_timestamps = deque([])
        self.rule_trigger_timestamps = deque([])
        self.rule_observations = deque([])
        # Hypothesis is only generated for observed implication. Thus, initialized with 1.
        self.hypothesis_observations = 1
        self.hypothesis_evaluated_true = 1

    def add_hypothesis_observation(self, result, timestamp):
        """Update the observation counts for a hypothesis."""
        # Reset counters when max_observations is reached.
        self.most_recent_observation_timestamp = timestamp
        if self.hypothesis_observations >= self.max_observations:
            pass
        else:
            self.hypothesis_observations = self.hypothesis_observations + 1
            self.hypothesis_evaluated_true = self.hypothesis_evaluated_true + result

    def compute_hypothesis_stability(self):
        """Compute the stability of a hypothesis."""
        if self.hypothesis_evaluated_true >= self.min_eval_true:
            # Known that hypothesis is stable.
            self.stable = 1
        elif (self.hypothesis_observations - self.hypothesis_evaluated_true) > (self.max_observations - self.min_eval_true):
            # Known that hypothesis will never be stable.
            self.stable = -1
        else:
            # Stability is still unknown, more observations required.
            self.stable = 0
        return self.stable

    def add_rule_observation(self, result):
        """Add a new rule to the observations."""
        if len(self.rule_observations) >= self.max_observations:
            self.rule_observations.popleft()
        self.rule_observations.append(result)

    def evaluate_rule(self):
        """Evaluate a rule."""
        ones = 0
        for obs in self.rule_observations:
            ones = ones + obs
        return (len(self.rule_observations) - ones) <= (self.max_observations - self.min_eval_true)

    def __repr__(self):
        return str(self.trigger_event[-1]).split('/')[-1] + '->' + str(self.implied_event[-1]).split('/')[-1] + ', eval=' + str(
            self.hypothesis_evaluated_true) + '/' + str(self.hypothesis_observations) + ', rule=' + str(
            self.rule_observations) + ', ruletriggerts=' + str(self.rule_trigger_timestamps)

    def get_dictionary_repr(self):
        """Return the dictionary representation of an Implication."""
        return {'trigger_event': self.trigger_event, 'implied_event': self.implied_event, 'stable': self.stable,
                'max_observations': self.max_observations, 'min_eval_true': self.min_eval_true,
                'most_recent_observation_timestamp': self.most_recent_observation_timestamp,
                'hypothesis_trigger_timestamps': list(self.hypothesis_trigger_timestamps),
                'rule_trigger_timestamps': list(self.rule_trigger_timestamps), 'rule_observations': list(self.rule_observations),
                'hypothesis_observations': self.hypothesis_observations, 'hypothesis_evaluated_true': self.hypothesis_evaluated_true}


def set_random_seed(seed):
    """Set the random seed for testing purposes."""
    random.seed(seed)
