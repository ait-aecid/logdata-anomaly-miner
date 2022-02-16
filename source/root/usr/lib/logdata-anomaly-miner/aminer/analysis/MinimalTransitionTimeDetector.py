"""
This module defines an detector for minimal transition times between states
(e.g. value combinations of stated paths).
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

import os
import logging
import sys
import time

from aminer.AminerConfig import DEBUG_LOG_NAME, build_persistence_file_name, CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX,\
    KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD
from aminer import AminerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events.EventInterfaces import EventSourceInterface
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util import PersistenceUtil
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface


class MinimalTransitionTimeDetector(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface):
    """This class creates events when minimal transition times between states (e.g. value combinations of stated paths) are undercut."""

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, anomaly_event_handlers, path_list=None, id_path_list=None, ignore_list=None, allow_missing_id=False,
                 num_log_lines_solidify_matrix=100, time_output_threshold=0, anomaly_threshold=0.05, persistence_id='Default',
                 auto_include_flag=False, output_log_line=True):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param path_list parser paths of values to be analyzed. Multiple paths mean that values are analyzed by their combined
        occurrences. When no paths are specified, the events given by the full path list are analyzed.
        @param id_path_list the list of paths where id values can be stored in all relevant log event types.
        @param ignore_list list of paths that are not considered for analysis, i.e., events that contain one of these paths are
        omitted. The default value is [] as None is not iterable.
        @param allow_missing_id when set to True, the detector will also use matches, where one of the pathes from target_path_list
        does not refer to an existing parsed data object.
        @param num_log_lines_solidify_matrix number of processed log lines after which the matrix is solidified.
        This process is periodically repeated.
        @param time_output_threshold threshold for the tested minimal transition time which has to be exceeded to be tested.
        @param anomaly_threshold threshold for the confidence which must be exceeded to raise an anomaly.
        @param persistence_id name of persistency document.
        @param auto_include_flag specifies whether newly observed sequences should be added to the learned model
        @param output_log_line specifies whether the full parsed log atom should be provided in the output.
        """
        # Input parameters
        self.aminer_config = aminer_config
        self.anomaly_event_handlers = anomaly_event_handlers
        self.path_list = path_list
        if self.path_list is None:
            self.path_list = []
        self.id_path_list = id_path_list
        if self.id_path_list is None:
            self.id_path_list = []
        self.ignore_list = ignore_list
        if self.ignore_list is None:
            self.ignore_list = []
        self.allow_missing_id = allow_missing_id
        self.num_log_lines_solidify_matrix = num_log_lines_solidify_matrix
        self.time_output_threshold = time_output_threshold
        self.anomaly_threshold = anomaly_threshold
        self.persistence_id = persistence_id
        self.auto_include_flag = auto_include_flag
        self.output_log_line = output_log_line
        self.next_persist_time = time.time() + self.aminer_config.config_properties.get(KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)

        # Test if both path_list and id_path_list are not empty
        if [] in (self.path_list, self.id_path_list):
            msg = 'Both paths and id_path_list must not be empty.'
            logging.getLogger(DEBUG_LOG_NAME).warning(msg)
            print('WARNING: ' + msg, file=sys.stderr)

        # Initialization auxiliary variables
        self.time_matrix = {}
        self.last_value = {}
        self.last_time = {}
        self.log_total = 0

        # Load persistency
        self.persistence_file_name = build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        if persistence_data is not None:
            return_matrix = persistence_data[0]
            keys_1 = [tuple(key) for key in persistence_data[1]]
            keys_2 = [[tuple(key) for key in persistence_data[2][i]] for i in range(len(persistence_data[2]))]
            self.time_matrix = {keys_1[i]: {keys_2[i][j]: return_matrix[i][j] for j in range(len(keys_2[i]))} for i in range(len(keys_1))}

    def receive_atom(self, log_atom):
        """Receive a log atom from a source and analyzes minimal times between transitions."""
        parser_match = log_atom.parser_match

        # Do not analyze the log line if path_list or id_path_list is empty
        if [] in (self.path_list, self.id_path_list):
            return False

        # Skip paths from ignore list.
        if any(ignore_path in parser_match.get_match_dictionary().keys() for ignore_path in self.ignore_list):
            return False

        # Skip line if atom_time is not defined.
        if log_atom.atom_time is None:
            return False

        # Increase the count by one and check if the matrix should be solidified.
        self.log_total += 1
        if self.log_total % self.num_log_lines_solidify_matrix == 0:
            self.solidify_matrix()

        # Use path_list to differentiate sequences by their id.
        event_value = ()
        for path in self.path_list:
            match = log_atom.parser_match.get_match_dictionary().get(path)
            if match is None:
                if self.allow_missing_id is True:
                    # Insert placeholder for path that is not available
                    event_value += ('',)
                else:
                    # Omit log atom if one of the id paths is not found.
                    return False
            else:
                if isinstance(match.match_object, bytes):
                    event_value += (match.match_object.decode(AminerConfig.ENCODING),)
                else:
                    event_value += (match.match_object,)

        # Get current index from combination of values of paths of id_path_list
        id_tuple = ()
        for id_path in self.id_path_list:
            id_match = log_atom.parser_match.get_match_dictionary().get(id_path)
            if id_match is None:
                if self.allow_missing_id is True:
                    # Insert placeholder for id_path that is not available
                    id_tuple += ('',)
                else:
                    # Omit log atom if one of the id paths is not found.
                    return False
            else:
                if isinstance(id_match.match_object, bytes):
                    id_tuple += (id_match.match_object.decode(AminerConfig.ENCODING),)
                else:
                    id_tuple += (id_match.match_object,)

        # Check if id_tuple has already appeared.
        if id_tuple not in self.last_value:
            # Initialize the last value and time
            self.last_value[id_tuple] = event_value
            self.last_time[id_tuple] = log_atom.atom_time
        else:
            # Check if the event_value changed or if the times are not strictly ascending and skip the line in that cases.
            if self.last_value[id_tuple] == event_value:
                self.last_time[id_tuple] = log_atom.atom_time
                return True
            if log_atom.atom_time - self.last_time[id_tuple] <= 0:
                additional_information = {'AffectedLogAtomValues': [list(self.last_value[id_tuple]), list(event_value)],
                                          'AffectedIdValues': list(id_tuple), 'PreviousTime': self.last_time[id_tuple],
                                          'NewTime': log_atom.atom_time}
                self.print('Anomaly in log line order: %s - %s (%s): %s - %s' % (list(self.last_value[id_tuple]), list(event_value),
                           list(id_tuple), self.last_time[id_tuple], log_atom.atom_time), log_atom, self.path_list, confidence=1,
                           additional_information=additional_information)
                return True

            # Check in which order the event_values appear in the time matrix
            event_value_1 = None
            event_value_2 = None
            if event_value in self.time_matrix and self.last_value[id_tuple] in self.time_matrix[event_value]:
                event_value_1 = event_value
                event_value_2 = self.last_value[id_tuple]
            elif self.last_value[id_tuple] in self.time_matrix and event_value in self.time_matrix[self.last_value[id_tuple]]:
                event_value_1 = self.last_value[id_tuple]
                event_value_2 = event_value

            if event_value_1 is None:
                # Initialize the entry in the time matrix
                if event_value not in self.time_matrix:
                    self.time_matrix[event_value] = {}

                additional_information = {'AffectedLogAtomValues': [list(self.last_value[id_tuple]), list(event_value)],
                                          'AffectedIdValues': list(id_tuple),
                                          'NewMinimalTime': log_atom.atom_time - self.last_time[id_tuple]}
                message = 'First Appearance: %s - %s (%s), %s' % (list(self.last_value[id_tuple]),
                                                                  list(event_value), list(id_tuple),
                                                                  log_atom.atom_time - self.last_time[id_tuple])
                self.print(message, log_atom, self.path_list, additional_information=additional_information)
                if self.auto_include_flag:
                    self.time_matrix[event_value][self.last_value[id_tuple]] = log_atom.atom_time - self.last_time[id_tuple]
            else:
                # Check and update if the time was under cut
                if self.time_matrix[event_value_1][event_value_2] > log_atom.atom_time - self.last_time[id_tuple] and\
                        self.time_matrix[event_value_1][event_value_2] > self.time_output_threshold:
                    if 1 - (log_atom.atom_time - self.last_time[id_tuple]) / self.time_matrix[event_value_1][event_value_2] >\
                            self.anomaly_threshold:
                        additional_information = {'AffectedLogAtomValues': [list(self.last_value[id_tuple]), list(event_value)],
                                                  'AffectedIdValues': list(id_tuple),
                                                  'PreviousMinimalTime': self.time_matrix[event_value_1][event_value_2],
                                                  'NewMinimalTime': log_atom.atom_time - self.last_time[id_tuple]}
                        message = 'Undercut transition time: %s - %s (%s), %s -> %s' % (
                                list(self.last_value[id_tuple]), list(event_value), list(id_tuple),
                                self.time_matrix[event_value_1][event_value_2], log_atom.atom_time - self.last_time[id_tuple])
                        confidence = 1 - (log_atom.atom_time - self.last_time[id_tuple]) / self.time_matrix[event_value_1][event_value_2]
                        self.print(message, log_atom, self.path_list, confidence=confidence, additional_information=additional_information)

                    if self.auto_include_flag:
                        self.time_matrix[event_value_1][event_value_2] = log_atom.atom_time - self.last_time[id_tuple]

            # Update the last_value and time
            self.last_value[id_tuple] = event_value
            self.last_time[id_tuple] = log_atom.atom_time

        return True

    def solidify_matrix(self):
        """Solidify minimal time matrix with the trianlge inequality."""
        # Initialize list old_pairs with all transitions and a list of all values
        # The list of old_pairs includes the minimal times which can be used to reduce the minimal ransition times of other transitions
        values = list(self.time_matrix.keys())
        for key1 in self.time_matrix:
            values += [key for key in self.time_matrix[key1] if key not in values]
        old_pairs = [[key1, key2] for key1 in self.time_matrix for key2 in self.time_matrix[key1]]

        # Check the triangle inequality as long as values are corrected
        while len(old_pairs) > 0:
            new_pairs = []
            for old_pair in old_pairs:
                # Check triangle inequality value - old_pair[0] - old_pair[1] > value - old_pair[1] and
                # old_pair[0] - old_pair[1] - value > value - old_pair[0]
                for value in values:
                    if value in (old_pair[0], old_pair[1]):
                        continue

                    # Check value - old_pair[0] - old_pair[1] > value - old_pair[1]
                    if (old_pair[0] in self.time_matrix and value in self.time_matrix[old_pair[0]]) or (
                           value in self.time_matrix and old_pair[0] in self.time_matrix[value]):

                        if old_pair[0] in self.time_matrix and value in self.time_matrix[old_pair[0]]:
                            key_1_1 = old_pair[0]
                            key_1_2 = value
                        else:
                            key_1_1 = value
                            key_1_2 = old_pair[0]

                        if old_pair[1] in self.time_matrix and value in self.time_matrix[old_pair[1]]:
                            key_2_1 = old_pair[1]
                            key_2_2 = value
                        else:
                            key_2_1 = value
                            key_2_2 = old_pair[1]

                        if key_2_1 not in self.time_matrix:
                            self.time_matrix[key_2_1] = {}
                        if (key_2_2 not in self.time_matrix[key_2_1] or self.time_matrix[key_1_1][key_1_2] +
                                self.time_matrix[old_pair[0]][old_pair[1]] < self.time_matrix[key_2_1][key_2_2]):
                            self.time_matrix[key_2_1][key_2_2] = self.time_matrix[key_1_1][key_1_2] +\
                                    self.time_matrix[old_pair[0]][old_pair[1]]
                            if [key_2_1, key_2_2] not in new_pairs:
                                new_pairs += [[key_2_1, key_2_2]]

                    # Check old_pair[0] - old_pair[1] - value > value - old_pair[0]
                    if (old_pair[1] in self.time_matrix and value in self.time_matrix[old_pair[1]]) or (
                           value in self.time_matrix and old_pair[1] in self.time_matrix[value]):

                        if old_pair[1] in self.time_matrix and value in self.time_matrix[old_pair[1]]:
                            key_1_1 = old_pair[1]
                            key_1_2 = value
                        else:
                            key_1_1 = value
                            key_1_2 = old_pair[1]

                        if old_pair[0] in self.time_matrix and value in self.time_matrix[old_pair[0]]:
                            key_2_1 = old_pair[0]
                            key_2_2 = value
                        else:
                            key_2_1 = value
                            key_2_2 = old_pair[0]

                        if key_2_1 not in self.time_matrix:
                            self.time_matrix[key_2_1] = {}
                        if (key_2_2 not in self.time_matrix[key_2_1] or self.time_matrix[key_1_1][key_1_2] +
                                self.time_matrix[old_pair[0]][old_pair[1]] < self.time_matrix[key_2_1][key_2_2]):
                            self.time_matrix[key_2_1][key_2_2] = self.time_matrix[key_1_1][key_1_2] +\
                                    self.time_matrix[old_pair[0]][old_pair[1]]
                            if [key_2_1, key_2_2] not in new_pairs:
                                new_pairs += [[key_2_1, key_2_2]]

            old_pairs = new_pairs

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
        keys_1 = list(self.time_matrix.keys())
        keys_2 = [list(self.time_matrix[key].keys()) for key in keys_1]
        return_matrix = [[self.time_matrix[keys_1[i]][keys_2[i][j]] for j in range(len(keys_2[i]))] for i in range(len(keys_1))]
        persist_data.append(return_matrix)
        persist_data.append(keys_1)
        persist_data.append(keys_2)
        PersistenceUtil.store_json(self.persistence_file_name, persist_data)
        logging.getLogger(DEBUG_LOG_NAME).debug('%s persisted data.', self.__class__.__name__)

    def allowlist_event(self, event_type, event_data, allowlisting_data):
        """
        Allowlist an event generated by this source using the information emitted when generating the event.
        @return a message with information about allowlisting
        @throws Exception when allowlisting of this special event using given allowlisting_data was not possible.
        """
        if event_type != 'Analysis.%s' % self.__class__.__name__:
            msg = 'Event not from this source'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if allowlisting_data is not None:
            msg = 'Allowlisting data not understood by this detector'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if event_data not in self.constraint_list:
            self.constraint_list.append(event_data)
        return 'Allowlisted path %s.' % event_data

    def add_to_persistency_event(self, event_type, event_data):
        """
        Add or overwrite the information of event_data to the persistency of component_name.
        @return a message with information about the addition to the persistency.
        @throws Exception when the addition of this special event using given event_data was not possible.
        """
        if event_type != 'Analysis.%s' % self.__class__.__name__:
            msg = 'Event not from this source'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)

        if not isinstance(event_data, list) or len(event_data) != 3 or not isinstance(event_data[0], list) or\
                not isinstance(event_data[1], list) or len(event_data[0]) != len(self.path_list) or\
                len(event_data[1]) != len(self.path_list) or not all(isinstance(value, str) for value in event_data[0]) or\
                not all(isinstance(value, str) for value in event_data[1]) or not isinstance(event_data[2], (int, float)):
            msg = 'Event_data has the wrong format.' \
                'The supported format is [path_value_list_1, path_value_list_2, new_transition_time], ' \
                'where the path value lists are lists of strings with the same length as paths defined in the config.'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)

        event_data[0] = tuple(event_data[0])
        event_data[1] = tuple(event_data[1])

        # Check in which order the event_values appear in the time matrix
        event_value_1 = None
        event_value_2 = None

        if event_data[0] in self.time_matrix and event_data[1] in self.time_matrix[event_data[0]]:
            event_value_1 = event_data[0]
            event_value_2 = event_data[1]
        elif event_data[1] in self.time_matrix and event_data[0] in self.time_matrix[event_data[1]]:
            event_value_1 = event_data[1]
            event_value_2 = event_data[0]

        if event_value_1 is None:
            # Initialize the entry in the time matrix
            if event_data[0] not in self.time_matrix:
                self.time_matrix[event_data[0]] = {}

            self.time_matrix[event_data[0]][event_data[1]] = float(event_data[2])

            return 'Added transition time: %s - %s, %s' % (list(event_data[0]), list(event_data[1]), float(event_data[2]))

        old_transition_time = self.time_matrix[event_value_1][event_value_2]
        self.time_matrix[event_value_1][event_value_2] = float(event_data[2])
        return 'Changed transition time %s - %s from %s to %s' % (list(event_data[0]), list(event_data[1]), old_transition_time,
                                                                  float(event_data[2]))

    def blocklist_event(self, event_type, event_data, blocklisting_data):
        """
        Blocklist an event generated by this source using the information emitted when generating the event.
        @return a message with information about blocklisting
        @throws Exception when blocklisting of this special event using given blocklisting_data was not possible.
        """
        if event_type != 'Analysis.%s' % self.__class__.__name__:
            msg = 'Event not from this source'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if blocklisting_data is not None:
            msg = 'Blocklisting data not understood by this detector'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if event_data not in self.ignore_list:
            self.ignore_list.append(event_data)
        return 'Blocklisted path %s.' % event_data

    def print(self, message, log_atom, affected_path, confidence=None, additional_information=None):
        """Print the message."""
        if isinstance(affected_path, str):
            affected_path = [affected_path]
        if additional_information is None:
            additional_information = {}

        original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
        if original_log_line_prefix is None:
            original_log_line_prefix = ''

        if self.output_log_line:
            tmp_str = ''
            for x in list(log_atom.parser_match.get_match_dictionary().keys()):
                tmp_str += '  ' + x + os.linesep
            tmp_str = tmp_str.lstrip('  ')
            sorted_log_lines = [tmp_str + original_log_line_prefix + log_atom.raw_data.decode()]
            analysis_component = {'AffectedLogAtomPaths': list(log_atom.parser_match.get_match_dictionary().keys())}
        else:
            tmp_str = ''
            for x in affected_path:
                tmp_str += '  ' + x + os.linesep
            tmp_str = tmp_str.lstrip('  ')
            sorted_log_lines = [tmp_str + log_atom.raw_data.decode()]
            analysis_component = {'AffectedLogAtomPaths': affected_path}

        for key, value in additional_information.items():
            analysis_component[key] = value

        event_data = {'AnalysisComponent': analysis_component, 'TypeInfo': {}}
        if confidence is not None:
            event_data['TypeInfo']['Confidence'] = confidence
        for listener in self.anomaly_event_handlers:
            listener.receive_event('Analysis.%s' % self.__class__.__name__, message, sorted_log_lines, event_data, log_atom, self)
