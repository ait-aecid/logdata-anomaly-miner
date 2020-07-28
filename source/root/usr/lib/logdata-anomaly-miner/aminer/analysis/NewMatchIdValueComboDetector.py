"""This file defines the NewMatchIdValueComboDetector
detector to extract values from multiple LogAtoms and check, if the value
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

from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events import EventSourceInterface
from aminer.input import AtomHandlerInterface
from aminer.util import PersistencyUtil
from aminer.util import TimeTriggeredComponentInterface
from aminer.analysis import CONFIG_KEY_LOG_LINE_PREFIX


class NewMatchIdValueComboDetector(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface):
    """This class creates events when a new value combination for
    a given list of match data pathes were found in log atoms with
    the same id value in a specific path."""

    def __init__(self, aminer_config, target_path_list, anomaly_event_handlers, id_path_list, min_allowed_time_diff,
                 persistence_id='Default', allow_missing_values_flag=False, auto_include_flag=False, output_log_line=True):
        """Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param target_path_list the list of values to extract from each match to create the value combination to be checked.
        @param id_path_list the list of pathes where id values can be stored in all relevant log event types.
        @param min_allowed_time_diff the minimum amount of time in seconds after the first appearance of a log atom with a specific id
        that is waited for other log atoms with the same id to occur. The maximum possible time to keep an incomplete combo
        is 2*min_allowed_time_diff
        @param allow_missing_values_flag when set to True, the detector will also use matches, where one of the pathes from target_path_list
        does not refer to an existing parsed data object.
        @param auto_include_flag when set to True, this detector will report a new value only the first time before including it
        in the known values set automatically."""
        self.target_path_list = target_path_list
        self.anomaly_event_handlers = anomaly_event_handlers
        self.id_path_list = id_path_list
        self.min_allowed_time_diff = min_allowed_time_diff
        self.allow_missing_values_flag = allow_missing_values_flag
        self.auto_include_flag = auto_include_flag
        self.output_log_line = output_log_line
        self.aminer_config = aminer_config
        self.persistence_id = persistence_id

        self.persistence_file_name = AMinerConfig.build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        self.next_persist_time = None
        self.load_persistency_data()
        PersistencyUtil.add_persistable_component(self)

        self.id_dict_current = {}
        self.id_dict_old = {}
        self.next_shift_time = None

    def load_persistency_data(self):
        """Load the persistency data from storage."""
        persistence_data = PersistencyUtil.load_json(self.persistence_file_name)
        self.known_values = []
        if persistence_data is not None:
            # Combinations are stored as list of dictionaries
            for record in persistence_data:
                self.known_values.append(record)

    def receive_atom(self, log_atom):
        """Receive on parsed atom and the information about the parser match.
        @return True if a value combination was extracted and checked against the list of known combinations, no matter if the checked
        values were new or not."""
        match_dict = log_atom.parser_match.get_match_dictionary()

        id_match_element = None
        for id_path in self.id_path_list:
            # Get the id value and return if not found in this log atom.
            id_match_element = match_dict.get(id_path, None)
            if id_match_element is not None:
                break
        if id_match_element is None:
            return False

        timestamp = log_atom.get_timestamp()
        if timestamp is not None:
            if self.next_shift_time is None:
                self.next_shift_time = timestamp + self.min_allowed_time_diff
            if timestamp > self.next_shift_time:
                # Every min_allowed_time_diff seconds, process all combinations from id_dict_old and then override id_dict_old with
                # id_dict_current. This guarantees that incomplete combos are hold for at least min_allowed_time_diff seconds before
                # proceeding.
                self.next_shift_time = timestamp + self.min_allowed_time_diff
                if self.allow_missing_values_flag:
                    for id_old in self.id_dict_old:
                        self.process_id_dict_entry(self.id_dict_old[id_old], log_atom)
                self.id_dict_old = self.id_dict_current
                self.id_dict_current = {}

        id_match_object = id_match_element.match_object

        # Find dictionary containing id and create ref to old or current dict (side-effects)
        id_dict = None
        if id_match_object in self.id_dict_current:
            id_dict = self.id_dict_current
        elif id_match_object in self.id_dict_old:
            id_dict = self.id_dict_old
        else:
            id_dict = self.id_dict_current
            id_dict[id_match_object] = {}

        for target_path in self.target_path_list:
            # Append values to the combo.
            match_element = match_dict.get(target_path, None)
            if match_element is not None:
                if isinstance(match_element.match_object, bytes):
                    id_dict[id_match_object][target_path] = match_element.match_object.decode()
                else:
                    id_dict[id_match_object][target_path] = match_element.match_object
                break

        if len(id_dict[id_match_object]) == len(self.target_path_list):
            # Found value for all target paths. No need to wait more.
            self.process_id_dict_entry(id_dict[id_match_object], log_atom)
            del id_dict[id_match_object]

        return True

    def process_id_dict_entry(self, id_dict_entry, log_atom):
        if id_dict_entry not in self.known_values:
            # Combo is unknown, process and raise anomaly
            if self.auto_include_flag:
                self.known_values.append(id_dict_entry)
                if self.next_persist_time is None:
                    self.next_persist_time = time.time() + 600

            analysis_component = {'AffectedLogAtomValues': [str(i) for i in list(id_dict_entry.values())]}
            event_data = {'AnalysisComponent': analysis_component}
            original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX)
            if original_log_line_prefix is None:
                original_log_line_prefix = ''
            if self.output_log_line:
                sorted_log_lines = [log_atom.parser_match.match_element.annotate_match('') + os.linesep + repr(
                    id_dict_entry) + os.linesep + original_log_line_prefix + repr(log_atom.raw_data)]
            else:
                sorted_log_lines = [repr(id_dict_entry) + os.linesep + original_log_line_prefix + repr(log_atom.raw_data)]
            for listener in self.anomaly_event_handlers:
                listener.receive_event('Analysis.%s' % self.__class__.__name__, 'New value combination(s) detected', sorted_log_lines,
                                       event_data, log_atom, self)

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
            self.do_persist()
            delta = 600
        return delta

    def do_persist(self):
        """Immediately write persistence data to storage."""
        PersistencyUtil.store_json(self.persistence_file_name, self.known_values)
        self.next_persist_time = None

    def whitelist_event(self, event_type, sorted_log_lines, event_data, whitelisting_data):
        """Whitelist an event generated by this source using the information emitted when generating the event.
        @return a message with information about whitelisting
        @throws Exception when whitelisting of this special event using given whitelistingData was not possible."""
        if event_type != 'Analysis.%s' % self.__class__.__name__:
            raise Exception('Event not from this source')
        if whitelisting_data is not None:
            raise Exception('Whitelisting data not understood by this detector')
        if event_data[1] not in self.known_values:
            self.known_values.append(event_data[1])
        return 'Whitelisted path(es) %s with %s in %s' % (', '.join(self.target_path_list), event_data[1], sorted_log_lines[0])
