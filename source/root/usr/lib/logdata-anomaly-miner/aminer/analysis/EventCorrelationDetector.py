"""This module defines an evaluator and generator for event rules. The overall idea of generation is
1) For each processed event A, randomly select another event B occurring within queue_delta_time.
2) If B chronologically occurs after A, create the hypothesis A => B (observing event A implies that event B must be observed within
current_time+queue_delta_time). If B chronologically occurs before A, create the hypothesis B <= A (observing event A implies that event B
must be observed within currentTime-queueDeltaTime).
3) Observe for a long time (max_observations) whether the hypothesis holds.
4) If the hypothesis holds, transform it to a rule. Otherwise, discard the hypothesis."""

from collections import deque
import random
import math
import time

from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.input import AtomHandlerInterface
from aminer.util import PersistencyUtil
from aminer.util import TimeTriggeredComponentInterface


class EventCorrelationDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """This class tries to find time correlation patterns between different log atom events."""

    def __init__(self, aminer_config, anomaly_event_handlers, max_hypotheses=1000, hypothesis_max_delta_time=5.0,
                 generation_probability=1.0, generation_factor=1.0, max_observations=500, p0=0.9, alpha=0.05, candidates_size=10,
                 hypotheses_eval_delta_time=120.0, delta_time_to_discard_hypothesis=180.0, check_rules_flag=False,
                 auto_include_flag=True, whitelisted_paths=None, persistence_id='Default'):
        """Initialize the detector. This will also trigger reading or creation of persistence storage location.
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
        @param whitelisted_paths list of paths that are not considered for correlation, i.e., events that contain one of these paths are
        omitted. The default value is [] as None is not iterable.
        @param persistence_id name of persitency document."""
        self.last_timestamp = 0.0
        self.anomaly_event_handlers = anomaly_event_handlers
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
        self.whitelisted_paths = whitelisted_paths
        if self.whitelisted_paths is None:
            self.whitelisted_paths = []
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

        PersistencyUtil.add_persistable_component(self)
        self.persistence_file_name = AMinerConfig.build_persistence_file_name(aminer_config, 'EventCorrelationDetector', persistence_id)
        self.persistence_id = persistence_id
        persistence_data = PersistencyUtil.load_json(self.persistence_file_name)

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

    # skipcq: PYL-R1710
    def get_min_eval_true(self, max_observations, p0, alpha):
        """Compute the critical value (minimal amount of true evaluations) for a hypothesis of form <eventA> implies <eventB> with at least
        probability p0 to be accepted. This method tries to be efficient by
        - Storing already computed critical values in a dictionary
        - Swapping (1 - p0) and p0 and replace alpha with (1 - alpha) to reduce loops"""
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
        timestamp = log_atom.get_timestamp()
        if timestamp is None:
            log_atom.atom_time = time.time()
            timestamp = log_atom.atom_time
        if timestamp < self.last_timestamp:
            for listener in self.anomaly_event_handlers:
                listener.receive_event('Analysis.%s' % self.__class__.__name__, 'Logdata not sorted: last %s, current %s' % (
                    self.last_timestamp, timestamp), [log_atom.raw_data], {}, log_atom, self)
            return
        self.last_timestamp = log_atom.atom_time
        parser_match = log_atom.parser_match

        self.total_records += 1

        event_data = {}
        sorted_log_lines = []

        # Event is defined by the full path of log atom.
        log_event = tuple(parser_match.get_match_dictionary())

        # Skip whitelisted paths.
        for whitelisted in self.whitelisted_paths:
            if whitelisted in log_event:
                return

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
                    if len(rule.rule_trigger_timestamps) != 0 and rule.rule_trigger_timestamps[0] >= log_atom.atom_time - \
                            self.hypothesis_max_delta_time:
                        # Implication was triggered; append positive evaluation and mark as seen.
                        rule.add_rule_observation(1)
                        rule.rule_trigger_timestamps[0] = 'obs'

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
                        rule.rule_observations = deque([])
                        for listener in self.anomaly_event_handlers:
                            listener.receive_event('analysis.EventCorrelationDetector', 'Correlation rule violated!', [
                                'Event %s is missing, but should follow event %s' % (
                                    repr(self.sample_events[rule.implied_event]), repr(self.sample_events[rule.trigger_event]))],
                                {'rule': rule.get_dictionary_repr()}, log_atom, self)
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
                    if len(rule.rule_trigger_timestamps) != 0 and rule.rule_trigger_timestamps[0] >= log_atom.atom_time - \
                            self.hypothesis_max_delta_time:
                        rule.add_rule_observation(1)
                        rule.rule_trigger_timestamps[0] = 'obs'
                    else:
                        rule.add_rule_observation(0)
                        if not rule.evaluate_rule():
                            rule.rule_observations = deque([])
                            for listener in self.anomaly_event_handlers:
                                listener.receive_event(
                                    'analysis.EventCorrelationDetector', 'Correlation rule violated!', [
                                        'Event %s is missing, but should precede event %s' % (
                                            repr(self.sample_events[rule.implied_event]), repr(self.sample_events[rule.trigger_event]))],
                                    {'rule': rule.get_dictionary_repr()}, log_atom, self)

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
                    if len(implication.hypothesis_trigger_timestamps) != 0 and (
                            str(implication.hypothesis_trigger_timestamps[0]) == 'obs' or implication.hypothesis_trigger_timestamps[
                            0] >= log_atom.atom_time - self.hypothesis_max_delta_time) and implication.stable == 0:
                        implication.add_hypothesis_observation(1, log_atom.atom_time)
                        # Mark this timestamp as observed
                        implication.hypothesis_trigger_timestamps[0] = 'obs'
                        # Since only true observations occur here, check for instability not necessary.
                        if implication.compute_hypothesis_stability() == 1:
                            # Update p and min_eval_true according to the results in the sample.
                            p = implication.hypothesis_evaluated_true / implication.hypothesis_observations
                            implication.min_eval_true = self.get_min_eval_true(self.max_observations, p, self.alpha)
                            # Add hypothesis to rules.
                            if implication.trigger_event in self.forward_rules:
                                self.forward_rules[implication.trigger_event].append(implication)
                            else:
                                self.forward_rules[implication.trigger_event] = [implication]
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
                            sorted_log_lines.append(str(implication.trigger_event).split('/')[-1][:-3] + ' -> ' + str(
                                implication.implied_event).split('/')[-1][:-3])
                            event_data['rule'] = implication.get_dictionary_repr()
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
                        if len(implication.hypothesis_trigger_timestamps) != 0 and str(
                                implication.hypothesis_trigger_timestamps[0]) != 'obs' and implication.hypothesis_trigger_timestamps[
                                0] >= log_atom.atom_time - self.hypothesis_max_delta_time:
                            implication.add_hypothesis_observation(1, log_atom.atom_time)
                            implication.hypothesis_trigger_timestamps[0] = 'obs'
                            # Since only true observations occur here, check for instability not necessary.
                            if implication.compute_hypothesis_stability() == 1:
                                # Update p and min_eval_true according to the results in the sample.
                                p = implication.hypothesis_evaluated_true / implication.hypothesis_observations
                                implication.min_eval_true = self.get_min_eval_true(self.max_observations, p, self.alpha)
                                # Add hypothesis to rules.
                                if implication.trigger_event in self.back_rules:
                                    self.back_rules[implication.trigger_event].append(implication)
                                else:
                                    self.back_rules[implication.trigger_event] = [implication]
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
                                sorted_log_lines.append(str(implication.implied_event).split('/')[-1][:-3] + ' <- ' + str(
                                    implication.trigger_event).split('/')[-1][:-3])
                                event_data['rule'] = implication.get_dictionary_repr()
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

            if sorted_log_lines:
                for listener in self.anomaly_event_handlers:
                    listener.receive_event('Analysis.%s' % self.__class__.__name__, 'New rule(s) detected', sorted_log_lines, event_data,
                                           log_atom, self)

    def get_time_trigger_class(self):
        """Get the trigger class this component should be registered for. This trigger is used only for persistency, so real-time
        triggering is needed."""
        return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def do_timer(self, trigger_time):
        """Check current ruleset should be persisted"""
        if self.next_persist_time is None:
            return 600

        delta = self.next_persist_time - trigger_time
        if delta < 0:
            known_path_set = set()
            for event_a in self.back_rules:
                for implication in self.back_rules[event_a]:
                    known_path_set.add(
                        ('back', tuple(event_a), tuple(implication.implied_event), implication.max_observations, implication.min_eval_true))
            for event_a in self.forward_rules:
                for implication in self.forward_rules[event_a]:
                    known_path_set.add(
                        ('forward', tuple(event_a), tuple(implication.implied_event), implication.max_observations,
                         implication.min_eval_true))
            PersistencyUtil.store_json(self.persistence_file_name, list(known_path_set))
            self.next_persist_time = None
            delta = 600
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
        PersistencyUtil.store_json(self.persistence_file_name, list(known_path_set))
        self.next_persist_time = None


class Implication:
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
        # Reset counters when max_observations is reached.
        self.most_recent_observation_timestamp = timestamp
        if self.hypothesis_observations >= self.max_observations:
            pass
        else:
            self.hypothesis_observations = self.hypothesis_observations + 1
            self.hypothesis_evaluated_true = self.hypothesis_evaluated_true + result

    def compute_hypothesis_stability(self):
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
        if len(self.rule_observations) >= self.max_observations:
            self.rule_observations.popleft()
        self.rule_observations.append(result)

    def evaluate_rule(self):
        ones = 0
        for obs in self.rule_observations:
            ones = ones + obs
        return (len(self.rule_observations) - ones) <= (self.max_observations - self.min_eval_true)

    def __repr__(self):
        return str(self.trigger_event[-1]).split('/')[-1] + '->' + str(self.implied_event[-1]).split('/')[-1] + ', eval=' + str(
            self.hypothesis_evaluated_true) + '/' + str(self.hypothesis_observations) + ', rule=' + str(
            self.rule_observations) + ', ruletriggerts=' + str(self.rule_trigger_timestamps)

    def get_dictionary_repr(self):
        return {'trigger_event': self.trigger_event, 'implied_event': self.implied_event, 'stable': self.stable,
                'max_observations': self.max_observations, 'min_eval_true': self.min_eval_true,
                'most_recent_observation_timestamp': self.most_recent_observation_timestamp,
                'hypothesis_trigger_timestamps': list(self.hypothesis_trigger_timestamps),
                'rule_trigger_timestamps': list(self.rule_trigger_timestamps), 'rule_observations': list(self.rule_observations),
                'hypothesis_observations': self.hypothesis_observations, 'hypothesis_evaluated_true': self.hypothesis_evaluated_true}
