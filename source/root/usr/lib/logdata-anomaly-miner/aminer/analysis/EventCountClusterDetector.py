"""
This module defines an detector for clustering event and value count vectors..
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
import math
import sys

from aminer.AminerConfig import DEBUG_LOG_NAME, build_persistence_file_name, KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD,\
    STAT_LOG_NAME, CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX
from aminer import AminerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events.EventInterfaces import EventSourceInterface
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util import PersistenceUtil
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface


class EventCountClusterDetector(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface):
    """This class creates events when dissimilar event or value count vectors occur."""

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, anomaly_event_handlers, target_path_list=None, window_size=600, id_path_list=None,
                 num_windows=50, confidence_factor=0.33, idf=False, norm=False, add_normal=False, check_empty_windows=True,
                 persistence_id='Default', learn_mode=False, output_logline=True,
                 ignore_list=None, constraint_list=None, stop_learning_time=None, stop_learning_no_anomaly_time=None):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that values are analyzed by their combined
               occurrences. When no paths are specified, the events given by the full path list are analyzed.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param window_size the length of the time window for counting in seconds.
        @param id_path_list parser paths of values for which separate count vectors should be generated.
        @param num_windows the number of vectors stored in the models.
        @param confidence_factor minimum similarity threshold for detection
        @param idf when true, value counts are weighted higher when they occur with fewer id_paths (requires that id_path_list is set).
        @param norm when true, count vectors are normalized so that only relative occurrence frequencies matter for detection.
        @param add_normal when true, count vectors are also added to the model when they exceed the similarity threshold.
        @param check_empty_windows when true, empty count vectors are generated for time windows without event occurrences.
        @param persistence_id name of persistence document.
        @param output_logline specifies whether the full parsed log atom should be provided in the output.
        @param ignore_list list of paths that are not considered for analysis, i.e., events that contain one of these paths are omitted.
               The default value is [] as None is not iterable.
        @param constraint_list list of paths that have to be present in the log atom to be analyzed.
        @param stop_learning_time switch the learn_mode to False after the time.
        @param stop_learning_no_anomaly_time switch the learn_mode to False after no anomaly was detected for that time.
        """
        # avoid "defined outside init" issue
        self.learn_mode, self.stop_learning_timestamp, self.next_persist_time, self.log_success, self.log_total = [None]*5
        super().__init__(
            mutable_default_args=["target_path_list", "scoring_path_list", "ignore_list", "constraint_list", "id_path_list"],
            aminer_config=aminer_config,
            anomaly_event_handlers=anomaly_event_handlers, target_path_list=target_path_list, id_path_list=id_path_list,
            window_size=window_size,  num_windows=num_windows, confidence_factor=confidence_factor,
            persistence_id=persistence_id, learn_mode=learn_mode,
            output_logline=output_logline, ignore_list=ignore_list, constraint_list=constraint_list, stop_learning_time=stop_learning_time,
            stop_learning_no_anomaly_time=stop_learning_no_anomaly_time, idf=idf, norm=norm, add_normal=add_normal,
            check_empty_windows=check_empty_windows
        )
        self.next_check_time = {}
        self.counts = {}
        self.known_counts = {}
        if self.idf and not self.id_path_list:
            msg = 'Omitting IDF weighting as required id_path_list is not set.'
            logging.getLogger(DEBUG_LOG_NAME).warning(msg)
            print('WARNING: ' + msg, file=sys.stderr)
        self.idf_total = set()
        self.idf_counts = {}
        self.log_windows = 0

        self.persistence_file_name = build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)

        # Persisted data contains known count vectors, i.e., [[[<id_1>, [[[<val_1>,1],[<val_2>,1]], [[<val_1>,2],[<val_3>,1]], ...]],
        #                                                      [<id_2>,[[[<val_1>,1]]]]],
        # 2) list of known id used for idf computation, i.e., [<id_1>,<id_2>],
        # 3) list of id observed for each value, i.e., [[<val_1>,[<id_1>,<id_2>]],[<val_2>,[<id_1>]]]]
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        if persistence_data is not None:
            for elem in persistence_data[0]:
                window_list = []
                for log_ev_elem_list in elem[1]:
                    elem_dict = {}
                    for log_ev_elem in log_ev_elem_list:
                        elem_dict[tuple(log_ev_elem[0])] = int(log_ev_elem[1])
                    window_list.append(elem_dict)
                self.known_counts[tuple(elem[0])] = window_list
            for elem in persistence_data[1]:
                self.idf_total.add(tuple(elem))
            for elem in persistence_data[2]:
                id_elem_set = set()
                for id_elem in elem[1]:
                    id_elem_set.add(tuple(id_elem))
                self.idf_counts[tuple(elem[0])] = id_elem_set
            logging.getLogger(DEBUG_LOG_NAME).debug('%s loaded persistence data.', self.__class__.__name__)

    def receive_atom(self, log_atom):
        """Receive a log atom from a source."""
        parser_match = log_atom.parser_match
        self.log_total += 1

        if self.learn_mode is True and self.stop_learning_timestamp is not None and \
                self.stop_learning_timestamp < log_atom.atom_time:
            logging.getLogger(DEBUG_LOG_NAME).info("Stopping learning in the %s.", self.__class__.__name__)
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

        # Update statistics for idf computation
        if self.idf and self.id_path_list:
            self.idf_total.add(id_tuple)
            if log_event in self.idf_counts:
                self.idf_counts[log_event].add(id_tuple)
            else:
                self.idf_counts[log_event] = set([id_tuple])  # skipcq: PTC-W0018

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
                self.next_check_time[id_tuple] = self.next_check_time[id_tuple] + skipped_windows * self.window_size
                if self.check_empty_windows:
                    self.detect(log_atom, id_tuple, {})  # Empty count vector
            self.detect(log_atom, id_tuple, self.counts[id_tuple])
            # Reset counts vector
            self.counts[id_tuple] = {}
        # Increase count for observed events
        if id_tuple in self.counts:
            if log_event in self.counts[id_tuple]:
                self.counts[id_tuple][log_event] += 1
            else:
                self.counts[id_tuple][log_event] = 1
        else:
            self.counts[id_tuple] = {log_event: 1}
        self.log_success += 1

    def add_to_model(self, id_tuple, count_vector):
        """Adds a count vector to the model (a fifo list of count vectors)"""
        if count_vector in self.known_counts[id_tuple]:
            # Avoid that model has identical count vectors multiple times
            return
        if len(self.known_counts[id_tuple]) >= self.num_windows:
            # Drop first (= oldest) count vector
            self.known_counts[id_tuple] = self.known_counts[id_tuple][1:]
        self.known_counts[id_tuple].append(count_vector)

    def detect(self, log_atom, id_tuple, count_vector):
        """Create anomaly event when anomaly score is too high."""
        score = self.check(id_tuple, count_vector)
        if score == -1:
            # Sample is normal, only add to known values when add_normal is set
            if self.learn_mode and self.add_normal:
                self.add_to_model(id_tuple, count_vector)
        else:
            # Sample is anomalous, add to model when training and create event
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
            analysis_component = {'AffectedLogAtomPaths': self.target_path_list, 'AffectedLogAtomValues': list(count_vector.keys()),
                                  'AffectedLogAtomFrequencies': list(count_vector.values())}
            if self.id_path_list is not None:
                analysis_component['AffectedIdValues'] = list(id_tuple)
            count_info = {'ConfidenceFactor': self.confidence_factor,
                          'Confidence': score}
            event_data = {'AnalysisComponent': analysis_component, 'CountData': count_info}
            for listener in self.anomaly_event_handlers:
                listener.receive_event(f'Analysis.{self.__class__.__name__}', 'Frequency anomaly detected', sorted_log_lines,
                                       event_data, log_atom, self)

    def check(self, id_tuple, count_vector):
        """Computes the manhattan metric for the count vector and each count vector present in the model."""
        min_score = 1
        for known_count in self.known_counts[id_tuple]:
            # Iterate over all count vectors in the model
            manh = 0
            manh_max = 0
            for element in set(list(known_count.keys()) + list(count_vector.keys())):
                # Iterate over each val that occurs in one of the vectors
                idf_fact = 1
                if self.idf and self.id_path_list:
                    # Compute idf (weight rare value higher than ones that occur with many id_values)
                    idf_fact = math.log10((1 + len(self.idf_total)) / len(self.idf_counts[element]))
                norm_sum_known = 1
                norm_sum_count = 1
                if self.norm:
                    # Normalize vectors by dividing through sum
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
                    manh_max += max(count_vector[element] * idf_fact / norm_sum_count, known_count[element] * idf_fact / norm_sum_known)
            score = 0
            if manh_max != 0:
                # manh_max is zero when both vectors are empty, in this case, score remains at default 0, and normalize in all other cases
                score = manh / manh_max
            if score <= self.confidence_factor:
                # Found similar vector; abort early to avoid spending time on more checks
                # Return -1 since "true" score is unknown as not all vectors in the model were checked
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
        print(self.known_counts)
        known_counts_data = []
        for id_tuple, vec_list in self.known_counts.items():
            id_tuple_data = []
            for vec_elem in vec_list:
                window_data = []
                for log_ev, freq in vec_elem.items():
                    window_data.append((log_ev, freq))
                id_tuple_data.append(window_data)
            known_counts_data.append((id_tuple, id_tuple_data))
        idf_total_data = []
        idf_counts_data = []
        if self.idf and self.id_path_list:
            idf_total_data = list(self.idf_total)
            for log_ev, id_list in self.idf_counts.items():
                idf_counts_data.append((log_ev, id_list))
        persist_data = [known_counts_data, idf_total_data, idf_counts_data]
        PersistenceUtil.store_json(self.persistence_file_name, persist_data)
        logging.getLogger(DEBUG_LOG_NAME).debug('%s persisted data.', self.__class__.__name__)

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
                "'%s' processed %d out of %d log atoms successfully in %d "
                "time windows in the last 60 minutes.", component_name, self.log_success, self.log_total, self.log_windows)
        elif AminerConfig.STAT_LEVEL == 2:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully in %d "
                "time windows in the last 60 minutes.", component_name, self.log_success, self.log_total, self.log_windows)
        self.log_success = 0
        self.log_total = 0
        self.log_windows = 0
