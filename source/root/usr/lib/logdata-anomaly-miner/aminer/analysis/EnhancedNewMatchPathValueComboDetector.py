"""This file defines the EnhancedNewMatchPathValueComboDetector
detector to extract values from LogAtoms and check, if the value
combination was already seen before.

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

from aminer.analysis.NewMatchPathValueComboDetector import NewMatchPathValueComboDetector
from aminer.util import PersistencyUtil
from aminer.analysis import CONFIG_KEY_LOG_LINE_PREFIX


class EnhancedNewMatchPathValueComboDetector(NewMatchPathValueComboDetector):
    """This class creates events when a new value combination for a given list of match data pathes were found. It is similar
    to the NewMatchPathValueComboDetector basic detector but also provides support for storing meta information about each detected
    value combination, e.g.
    * the first time a tuple was detected using the LogAtom default timestamp.
    * the last time a tuple was seen
    * the number of times the tuple was seen
    * user data for annotation.
    Due to the additional features, this detector is slower than the basic detector."""

    def __init__(self, aminer_config, target_path_list, anomaly_event_handlers, persistence_id='Default', allow_missing_values_flag=False,
                 auto_include_flag=False, tuple_transformation_function=None, output_log_line=True):
        """Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param target_path_list the list of values to extract from each match to create the value combination to be checked.
        @param allow_missing_values_flag when set to True, the detector will also use matches, where one of the pathes from target_path_list
        does not refer to an existing parsed data object.
        @param auto_include_flag when set to True, this detector will report a new value only the first time before including it
        in the known values set automatically.
        @param tuple_transformation_function when not None, this function will be invoked on each extracted value combination list to
        transform it. It may modify the list directly or create a new one to return it."""
        self.known_values_dict = {}
        super(EnhancedNewMatchPathValueComboDetector, self).__init__(aminer_config, target_path_list, anomaly_event_handlers,
                                                                     persistence_id, allow_missing_values_flag, auto_include_flag)
        self.tuple_transformation_function = tuple_transformation_function
        self.output_log_line = output_log_line
        self.aminer_config = aminer_config
        self.date_string = "%Y-%m-%d %H:%M:%S"

    def load_persistency_data(self):
        """Load the persistency data from storage."""
        persistence_data = PersistencyUtil.load_json(self.persistence_file_name)
        if persistence_data is not None:
            # Dictionary and tuples were stored as list of lists. Transform
            # the first lists to tuples to allow hash operation needed by set.
            for value_tuple, extra_data in persistence_data:
                self.known_values_dict[tuple(value_tuple)] = extra_data

    def receive_atom(self, log_atom):
        """Receive on parsed atom and the information about the parser match.
        @return True if a value combination was extracted and checked against the list of known combinations, no matter if the checked
        values were new or not."""
        match_dict = log_atom.parser_match.get_match_dictionary()
        timestamp = log_atom.get_timestamp()
        if timestamp is None:
            timestamp = time.time()
        timestamp = round(timestamp, 3)
        match_value_list = []
        for target_path in self.target_path_list:
            match_element = match_dict.get(target_path, None)
            if match_element is None:
                if not self.allow_missing_values_flag:
                    return False
                match_value_list.append(None)
            else:
                match_value_list.append(match_element.match_object)

        if self.tuple_transformation_function is not None:
            match_value_list = self.tuple_transformation_function(match_value_list)
        match_value_tuple = tuple(match_value_list)

        if self.known_values_dict.get(match_value_tuple, None) is None:
            self.known_values_dict[match_value_tuple] = [timestamp, timestamp, 1]
        else:
            extra_data = self.known_values_dict.get(match_value_tuple, None)
            extra_data[1] = timestamp
            extra_data[2] += 1

        affected_log_atom_values = []
        metadata = {}
        for match_value in list(match_value_tuple):
            if isinstance(match_value, bytes):
                match_value = match_value.decode()
            affected_log_atom_values.append(str(match_value))
        values = self.known_values_dict.get(match_value_tuple, None)
        metadata['TimeFirstOccurrence'] = str(values[0])
        metadata['TimeLastOccurence'] = str(values[1])
        metadata['NumberOfOccurences'] = str(values[2])

        analysis_component = {'AffectedLogAtomPaths': self.target_path_list, 'AffectedLogAtomValues': affected_log_atom_values,
                              'Metadata': metadata}
        event_data = {'AnalysisComponent': analysis_component}
        if (self.auto_include_flag and self.known_values_dict.get(match_value_tuple, None)[2] == 1) or not self.auto_include_flag:
            for listener in self.anomaly_event_handlers:
                original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX)
                if original_log_line_prefix is None:
                    original_log_line_prefix = ''
                if self.output_log_line:
                    match_paths_values = {}
                    for match_path, match_element in match_dict.items():
                        match_value = match_element.match_object
                        if isinstance(match_value, bytes):
                            match_value = match_value.decode()
                        match_paths_values[match_path] = match_value
                    analysis_component['ParsedLogAtom'] = match_paths_values
                    sorted_log_lines = [log_atom.parser_match.match_element.annotate_match('') + os.linesep + str(
                        self.known_values_dict) + os.linesep + original_log_line_prefix + repr(log_atom.raw_data)]
                else:
                    sorted_log_lines = [str(self.known_values_dict) + os.linesep + original_log_line_prefix + repr(log_atom.raw_data)]
                listener.receive_event('Analysis.%s' % self.__class__.__name__, 'New value combination(s) detected', sorted_log_lines,
                                       event_data, log_atom, self)
        if self.auto_include_flag:
            if self.next_persist_time is None:
                self.next_persist_time = time.time() + 600
        return True

    def do_persist(self):
        """Immediately write persistence data to storage."""
        persistency_data = []
        for dict_record in self.known_values_dict.items():
            persistency_data.append(dict_record)
        PersistencyUtil.store_json(self.persistence_file_name, persistency_data)
        self.next_persist_time = None

    def whitelist_event(self, event_type, sorted_log_lines, event_data, whitelisting_data):
        """Whitelist an event generated by this source using the information emitted when generating the event.
        @return a message with information about whitelisting
        @throws Exception when whitelisting of this special event using given whitelistingData was not possible."""
        if event_type != 'Analysis.%s' % self.__class__.__name__:
            raise Exception('Event not from this source')
        if whitelisting_data is not None:
            raise Exception('Whitelisting data not understood by this detector')
        current_timestamp = event_data[0].get_timestamp()
        self.known_values_dict[event_data[1]] = [current_timestamp, current_timestamp, 1]
        return 'Whitelisted path(es) %s with %s in %s' % (', '.join(self.target_path_list), event_data[1], sorted_log_lines[0])
