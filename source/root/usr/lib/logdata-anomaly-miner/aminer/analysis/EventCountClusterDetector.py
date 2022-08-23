"""
This module defines an detector for event and value frequency deviations.
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
import time
import os
import logging
import numpy as np

from aminer.AminerConfig import DEBUG_LOG_NAME, build_persistence_file_name, KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD,\
    STAT_LOG_NAME, CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX
from aminer import AminerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events.EventInterfaces import EventSourceInterface
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util import PersistenceUtil
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface


class EventCountClusterDetector(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface):
    """This class creates events when event or value frequencies change."""

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, anomaly_event_handlers, target_path_list=None, window_size=600, id_path_list=None,
                 num_windows=50, confidence_factor=0.33, idf=False, norm=False, update_at_retrain=False, check_empty_windows=True,
                 persistence_id='Default', learn_mode=False, output_logline=True,
                 ignore_list=None, constraint_list=None, stop_learning_time=None, stop_learning_no_anomaly_time=None):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that values are analyzed by their combined
               occurrences. When no paths are specified, the events given by the full path list are analyzed.
        @param scoring_path_list parser paths of values to be analyzed by following event handlers like the ScoringEventHandler.
               Multiple paths mean that values are analyzed by their combined occurrences.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param window_size the length of the time window for counting in seconds.
        @param num_windows the number of previous time windows considered for expected frequency estimation.
        @param confidence_factor defines range of tolerable deviation of measured frequency from expected frequency according to
               occurrences_mean +- occurrences_std / self.confidence_factor. Default value is 0.33 = 3*sigma deviation. confidence_factor
               must be in range [0, 1].
        @param empty_window_warnings whether anomalies should be generated for too small window sizes.
        @param early_exceeding_anomaly_output states if an anomaly should be raised the first time the appearance count exceeds the range.
        @param set_lower_limit sets the lower limit of the frequency test to the specified value.
        @param set_upper_limit sets the upper limit of the frequency test to the specified value.
        @param persistence_id name of persistence document.
        @param learn_mode specifies whether new frequency measurements override ground truth frequencies.
        @param output_logline specifies whether the full parsed log atom should be provided in the output.
        @param ignore_list list of paths that are not considered for analysis, i.e., events that contain one of these paths are omitted.
               The default value is [] as None is not iterable.
        @param constraint_list list of paths that have to be present in the log atom to be analyzed.
        @param stop_learning_time switch the learn_mode to False after the time.
        @param stop_learning_no_anomaly_time switch the learn_mode to False after no anomaly was detected for that time.
        """
        # avoid "defined outside init" issue
        self.learn_mode, self.stop_learning_timestamp, self.next_persist_time, self.log_success, self.log_total = [None]*5
        #self.idf = idf
        #self.norm = norm
        #self.update_at_retrain = update_at_retrain
        #self.check_empty_windows = check_empty_windows
        super().__init__(
            mutable_default_args=["target_path_list", "scoring_path_list", "ignore_list", "constraint_list", "id_path_list"],
            aminer_config=aminer_config,
            anomaly_event_handlers=anomaly_event_handlers, target_path_list=target_path_list,
            window_size=window_size,  num_windows=num_windows, confidence_factor=confidence_factor,
            persistence_id=persistence_id, learn_mode=learn_mode,
            output_logline=output_logline, ignore_list=ignore_list, constraint_list=constraint_list, stop_learning_time=stop_learning_time,
            stop_learning_no_anomaly_time=stop_learning_no_anomaly_time, idf=idf, norm=norm, update_at_retrain=update_at_retrain,
            check_empty_windows = check_empty_windows
        )
        self.next_check_time = {}
        self.counts = {}
        self.known_counts = {}
        self.log_windows = 0

        self.persistence_file_name = build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)

        # Persisted data contains lists of event-frequency pairs, i.e., [[<ev>, [<freq1, freq2>]], [<ev>, [<freq1, freq2>]], ...]
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        if persistence_data is not None:
            for entry in persistence_data:
                log_event = entry[0]
                freqs = entry[1]
                # In case that num_windows differ, only take as many as possible
                self.counts[tuple(log_event)] = freqs[max(0, len(freqs) - num_windows - 1):] + [0]
                if len(self.scoring_path_list) > 0:
                    self.scoring_value_list[tuple(log_event)] = []
            logging.getLogger(DEBUG_LOG_NAME).debug(f'{self.__class__.__name__} loaded persistence data.')

    def receive_atom(self, log_atom):
        """Receive a log atom from a source."""
        parser_match = log_atom.parser_match
        self.log_total += 1

        if self.learn_mode is True and self.stop_learning_timestamp is not None and \
                self.stop_learning_timestamp < log_atom.atom_time:
            logging.getLogger(DEBUG_LOG_NAME).info(f"Stopping learning in the {self.__class__.__name__}.")
            self.learn_mode = False

        # Skip paths from ignore list.
        for ignore_path in self.ignore_list:
            if ignore_path in parser_match.get_match_dictionary().keys():
                return

        if self.target_path_list is None or len(self.target_path_list) == 0:
            # Event is defined by the full path of log atom.
            constraint_path_flag = False
            for constraint_path in self.constraint_list:
                if parser_match.get_match_dictionary().get(constraint_path) is not None:
                    constraint_path_flag = True
                    break
            if not constraint_path_flag and self.constraint_list != []:
                return
            log_event = tuple(parser_match.get_match_dictionary().keys())
        else:
            # Event is defined by value combos in target_path_list
            values = []
            all_values_none = True
            for path in self.target_path_list:
                match = parser_match.get_match_dictionary().get(path)
                if match is None:
                    continue
                matches = []
                if isinstance(match, list):
                    matches = match
                else:
                    matches.append(match)
                for match in matches:
                    if isinstance(match.match_object, bytes):
                        value = match.match_object.decode(AminerConfig.ENCODING)
                    else:
                        value = str(match.match_object)
                    if value is not None:
                        all_values_none = False
                    values.append(value)
            if all_values_none is True:
                return
            log_event = tuple(values)

        # In case that id_path_list is set, use it to differentiate sequences by their id.
        # Otherwise, the empty tuple () is used as the only key of the current_sequences dict.
        id_tuple = ()
        for id_path in self.id_path_list:
            id_match = parser_match.get_match_dictionary().get(id_path)
            if id_match is None:
                if self.allow_missing_id is True:
                    # Insert placeholder for id_path that is not available
                    id_tuple += ('',)
                else:
                    # Omit log atom if one of the id paths is not found.
                    return
            else:
                matches = []
                if isinstance(id_match, list):
                    matches = id_match
                else:
                    matches.append(id_match)
                for match in matches:
                    if isinstance(match.match_object, bytes):
                        id_tuple += (match.match_object.decode(AminerConfig.ENCODING),)
                    else:
                        id_tuple += (match.match_object,)

        # Create entry for the id_tuple in the current_sequences dict if it did not occur before.
        if id_tuple not in self.known_counts:
            self.known_counts[id_tuple] = []

        if id_tuple not in self.next_check_time:
            # First processed log atom, initialize next check time.
            self.next_check_time[id_tuple] = log_atom.atom_time + self.window_size
            self.log_windows += 1
        elif log_atom.atom_time >= self.next_check_time[id_tuple]:
            # Log atom exceeded next check time; time window is complete.
            self.next_check_time[id_tuple] = self.next_check_time[id_tuple] + self.window_size
            self.log_windows += 1

            # Update next_check_time if a time window was skipped
            skipped_windows = 0
            if log_atom.atom_time >= self.next_check_time[id_tuple]:
                skipped_windows = 1 + int((log_atom.atom_time - self.next_check_time[id_tuple]) / self.window_size)
                self.next_check_time[id_tuple] = self.next_check_time + skipped_windows * self.window_size
                if self.check_empty_windows:
                    self.detect(log_atom, id_tuple, {}) # Empty count vector
            print(self.counts)
            result = self.detect(log_atom, id_tuple, self.counts[id_tuple])
            # Reste counts vector
            self.counts[id_tuple] = {}
        # Increase count for observed events
        if id_tuple in self.counts:
            if log_event in self.counts[id_tuple]:
                self.counts[id_tuple][log_event] += 1
            else:
                self.counts[id_tuple][log_event] = 1
        else:
            self.counts[id_tuple] = {}
        self.log_success += 1

    def add_to_model(self, id_tuple, count_vector):
        if count_vector in self.known_counts[id_tuple]:
            # Avoid that model has identical count vectors multiple times
            return
        if len(self.known_counts[id_tuple]) >= self.num_windows:
            # Drop first (= oldest) count vector
            self.known_counts[id_tuple] = self.known_counts[id_tuple][1:]
        self.known_counts[id_tuple].append(count_vector)

    def detect(self, log_atom, id_tuple, count_vector):
        score = self.check(id_tuple, self.counts[id_tuple])
        if score == -1:
            # Sample is normal, only add to known values when update_at_retrain is set
            if self.learn_mode and self.update_at_retrain:
                self.add_to_model(id_tuple, count_vector)
        else:
            if self.learn_mode:
                self.add_to_model(id_tuple, count_vector)
            try:
                data = log_atom.raw_data.decode(AminerConfig.ENCODING)
            except UnicodeError:
                data = repr(log_atom.raw_data)
            if self.output_logline:
                original_log_line_prefix = self.aminer_config.config_properties.get(
                    CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
                sorted_log_lines = [log_atom.parser_match.match_element.annotate_match('') + os.linesep + original_log_line_prefix +
                                    data]
            else:
                sorted_log_lines = [data]
            print(count_vector)
            analysis_component = {'AffectedLogAtomPaths': self.target_path_list, 'AffectedLogAtomValues': list(count_vector.keys()),
                                  'AffectedLogAtomFrequencies': list(count_vector.values())}
            count_info = {'ConfidenceFactor': self.confidence_factor,
                          'Confidence': score}
            event_data = {'AnalysisComponent': analysis_component, 'CountData': count_info}
            for listener in self.anomaly_event_handlers:
                listener.receive_event(f'Analysis.{self.__class__.__name__}', 'Frequency anomaly detected', sorted_log_lines,
                                       event_data, log_atom, self)

    def check(self, id_tuple, count_vector):
        min_score = 1
        for known_count in self.known_counts[id_tuple]:
            manh = 0
            manh_max = 0
            for element in set(list(known_count.keys()) + list(count_vector.keys())):
                idf_fact = 1
                if self.idf:
                    idf_fact = math.log10((1 + len(users)) / len(idf[action_element]))
                norm_sum_known = 1
                norm_sum_count = 1
                if self.norm:
                    norm_sum_known = sum(known_count.values())
                    norm_sum_count = sum(count_vector.values())
                if element not in known_count:
                    manh += count_vector[element] * idf_fact / norm_sum_count
                    manh_max += count_vector[element] * idf_fact / norm_sum_count
                elif element not in count_vector:
                    manh += known_count[element] * idf_fact / norm_sum_known
                    manh_max += known_count[element] * idf_fact / norm_sum_known
                else:
                    manh += abs(count_vector[element] * idf_fact / norm_sum_count - known_count[element] * idf_fact / norm_sum_known)
                    manh_max += max(count_vector[element] * idf_fact / norm_sum_count, known_count[element]* idf_fact / norm_sum_known)
            score = manh / manh_max
            if score <= self.confidence_factor:
                # Found similar vector; abort early to avoid spending time on more checks
                return -1
            if min_score is None:
                min_score = score
            else:
                min_score = min(min_score, score)
        return min_score

    def do_timer(self, trigger_time):
        """Check if current ruleset should be persisted."""
        if self.next_persist_time is None:
            return self.aminer_config.config_properties.get(KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)

        delta = self.next_persist_time - trigger_time
        if delta <= 0:
            self.do_persist()
            delta = self.aminer_config.config_properties.get(KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)
            self.next_persist_time = time.time() + delta
        return delta

    def do_persist(self):
        """Immediately write persistence data to storage."""
        persist_data = []
        for log_ev, freqs in self.counts.items():
            # Skip last count as the time window may not be complete yet and count thus too low
            persist_data.append((log_ev, freqs[:-1]))
        PersistenceUtil.store_json(self.persistence_file_name, persist_data)
        logging.getLogger(DEBUG_LOG_NAME).debug(f'{self.__class__.__name__} persisted data.')

    def allowlist_event(self, event_type, event_data, allowlisting_data):
        """
        Allowlist an event generated by this source using the information emitted when generating the event.
        @return a message with information about allowlisting
        @throws Exception when allowlisting of this special event using given allowlisting_data was not possible.
        """
        if event_type != f'Analysis.{self.__class__.__name__}':
            msg = 'Event not from this source'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if allowlisting_data is not None:
            msg = 'Allowlisting data not understood by this detector'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if event_data not in self.constraint_list:
            self.constraint_list.append(event_data)
        return f'Allowlisted path {event_data}.'

    def blocklist_event(self, event_type, event_data, blocklisting_data):
        """
        Blocklist an event generated by this source using the information emitted when generating the event.
        @return a message with information about blocklisting
        @throws Exception when blocklisting of this special event using given blocklisting_data was not possible.
        """
        if event_type != f'Analysis.{self.__class__.__name__}':
            msg = 'Event not from this source'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if blocklisting_data is not None:
            msg = 'Blocklisting data not understood by this detector'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if event_data not in self.ignore_list:
            self.ignore_list.append(event_data)
        return f'Blocklisted path {event_data}.'

    def log_statistics(self, component_name):
        """
        Log statistics of an AtomHandler. Override this method for more sophisticated statistics output of the AtomHandler.
        @param component_name the name of the component which is printed in the log line.
        """
        if AminerConfig.STAT_LEVEL == 1:
            logging.getLogger(STAT_LOG_NAME).info(
                f"'{component_name}' processed {self.log_success} out of {self.log_total} log atoms successfully in {self.log_windows} "
                f"time windows in the last 60 minutes.")
        elif AminerConfig.STAT_LEVEL == 2:
            logging.getLogger(STAT_LOG_NAME).info(
                f"'{component_name}' processed {self.log_success} out of {self.log_total} log atoms successfully in {self.log_windows} "
                f"time windows in the last 60 minutes.")
        self.log_success = 0
        self.log_total = 0
        self.log_windows = 0
