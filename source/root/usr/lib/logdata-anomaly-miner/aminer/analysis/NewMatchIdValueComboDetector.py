"""
This file defines the NewMatchIdValueComboDetector.
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

import os
import logging

from aminer.AminerConfig import build_persistence_file_name, DEBUG_LOG_NAME, KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD,\
    STAT_LOG_NAME, CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX
from aminer import AminerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events.EventInterfaces import EventSourceInterface
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util import PersistenceUtil
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface


class NewMatchIdValueComboDetector(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface):
    """
    This class creates events when a new value combination for a given list of match data.
    Paths need to be found in log atoms with the same id value in a specific path.
    """

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, target_path_list, anomaly_event_handlers, id_path_list, min_allowed_time_diff,
                 persistence_id='Default', allow_missing_values_flag=False, learn_mode=False, output_logline=True,
                 stop_learning_time=None, stop_learning_no_anomaly_time=None, log_resource_ignore_list=None):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param target_path_list the list of values to extract from each match to create the value combination to be checked.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param id_path_list the list of paths where id values can be stored in all relevant log event types.
        @param min_allowed_time_diff the minimum amount of time in seconds after the first appearance of a log atom with a specific id
               that is waited for other log atoms with the same id to occur. The maximum possible time to keep an incomplete combo
               is 2*min_allowed_time_diff
        @param persistence_id name of persistence file.
        @param allow_missing_values_flag when set to True, the detector will also use matches, where one of the paths from target_path_list
               does not refer to an existing parsed data object.
        @param learn_mode when set to True, this detector will report a new value only the first time before including it
               in the known values set automatically.
        @param output_logline specifies whether the full parsed log atom should be provided in the output.
        @param stop_learning_time switch the learn_mode to False after the time.
        @param stop_learning_no_anomaly_time switch the learn_mode to False after no anomaly was detected for that time.
        """
        # avoid "defined outside init" issue
        self.learn_mode, self.stop_learning_timestamp, self.next_persist_time, self.log_success, self.log_total = [None]*5
        super().__init__(
            aminer_config=aminer_config, target_path_list=target_path_list, anomaly_event_handlers=anomaly_event_handlers,
            id_path_list=id_path_list, min_allowed_time_diff=min_allowed_time_diff, persistence_id=persistence_id,
            allow_missing_values_flag=allow_missing_values_flag, learn_mode=learn_mode, output_logline=output_logline,
            stop_learning_time=stop_learning_time, stop_learning_no_anomaly_time=stop_learning_no_anomaly_time,
            log_resource_ignore_list=log_resource_ignore_list, mutable_default_args=["log_resource_ignore_list"]
        )
        if not self.target_path_list:
            msg = "target_path_list must not be None or empty."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        if not self.id_path_list:
            msg = "id_path_list must not be None or empty."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)

        self.log_learned_path_value_combos = 0
        self.log_new_learned_values = []

        self.known_values = []
        self.persistence_file_name = build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        self.load_persistence_data()

        self.id_dict_current = {}
        self.id_dict_old = {}
        self.next_shift_time = None

    def receive_atom(self, log_atom):
        """
        Receive on parsed atom and the information about the parser match.
        @return True if a value combination was extracted and checked against the list of known combinations, no matter if the checked
                values were new or not.
        """
        for source in self.log_resource_ignore_list:
            if log_atom.source.resource_name == source.decode():
                return False
        self.log_total += 1
        match_dict = log_atom.parser_match.get_match_dictionary()
        if self.learn_mode is True and self.stop_learning_timestamp is not None and \
                self.stop_learning_timestamp < log_atom.atom_time:
            logging.getLogger(DEBUG_LOG_NAME).info("Stopping learning in the %s.", self.__class__.__name__)
            self.learn_mode = False

        id_match_element = None
        for id_path in self.id_path_list:
            # Get the id value and return if not found in this log atom.
            id_match_element = match_dict.get(id_path)
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

        if isinstance(id_match_element, list):
            id_match_object = []
            for match_element in id_match_element:
                id_match_object.append(match_element.match_object)
            id_match_object = tuple(id_match_object)
        else:
            id_match_object = id_match_element.match_object

        # Find dictionary containing id and create ref to old or current dict (side effects)
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
            match_element = match_dict.get(target_path)
            if match_element is not None:
                if isinstance(match_element, list):
                    values = []
                    matches = match_element
                    for match_element in matches:
                        if isinstance(match_element.match_object, bytes):
                            values.append(match_element.match_object.decode(AminerConfig.ENCODING))
                        else:
                            values.append(id_dict[id_match_object][target_path])
                    id_dict[id_match_object][target_path] = values
                else:
                    if isinstance(match_element.match_object, bytes):
                        id_dict[id_match_object][target_path] = match_element.match_object.decode(AminerConfig.ENCODING)
                    else:
                        id_dict[id_match_object][target_path] = match_element.match_object

        if len(id_dict[id_match_object]) == len(self.target_path_list):
            # Found value for all target paths. No need to wait more.
            self.process_id_dict_entry(id_dict[id_match_object], log_atom)
            del id_dict[id_match_object]
        self.log_success += 1
        return True

    def process_id_dict_entry(self, id_dict_entry, log_atom):
        """Process an entry from the id_dict."""
        if id_dict_entry not in self.known_values:
            # Combo is unknown, process and raise anomaly
            if self.learn_mode:
                self.known_values.append(id_dict_entry)
                self.log_learned_path_value_combos += 1
                self.log_new_learned_values.append(id_dict_entry)
                if self.stop_learning_timestamp is not None and self.stop_learning_no_anomaly_time is not None:
                    self.stop_learning_timestamp = max(
                        self.stop_learning_timestamp, log_atom.atom_time + self.stop_learning_no_anomaly_time)

            analysis_component = {'AffectedLogAtomValues': [str(i) for i in list(id_dict_entry.values())]}
            event_data = {'AnalysisComponent': analysis_component}
            try:
                data = log_atom.raw_data.decode(AminerConfig.ENCODING)
            except UnicodeError:
                data = repr(log_atom.raw_data)
            original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
            if self.output_logline:
                sorted_log_lines = [log_atom.parser_match.match_element.annotate_match('') + os.linesep + repr(
                    id_dict_entry) + os.linesep + original_log_line_prefix + data]
            else:
                sorted_log_lines = [repr(id_dict_entry)]
            for listener in self.anomaly_event_handlers:
                listener.receive_event(f'Analysis.{self.__class__.__name__}', 'New value combination(s) detected', sorted_log_lines,
                                       event_data, log_atom, self)

    def do_timer(self, trigger_time):
        """Check if current ruleset should be persisted."""
        if self.next_persist_time is None:
            return self.aminer_config.config_properties.get(KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)

        delta = self.next_persist_time - trigger_time
        if delta <= 0:
            self.do_persist()
            delta = self.aminer_config.config_properties.get(KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)
            self.next_persist_time = trigger_time + delta
        return delta

    def do_persist(self):
        """Immediately write persistence data to storage."""
        PersistenceUtil.store_json(self.persistence_file_name, self.known_values)
        logging.getLogger(DEBUG_LOG_NAME).debug("%s persisted data.", self.__class__.__name__)

    def load_persistence_data(self):
        """Load the persistence data from storage."""
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        if persistence_data is not None:
            # Combinations are stored as list of dictionaries
            for record in persistence_data:
                self.known_values.append(record)
            logging.getLogger(DEBUG_LOG_NAME).debug("%s loaded persistence data.", self.__class__.__name__)
        PersistenceUtil.add_persistable_component(self)

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
        if not isinstance(event_data, dict) or len(event_data) != len(self.target_path_list) or \
                not all(x in self.target_path_list for x in event_data.keys()) or \
                not all(not isinstance(x, bytes) for x in event_data.values()):
            msg = "event_data has to be of type dict and the values should not be bytes."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if not self.allow_missing_values_flag and None in event_data.values():
            msg = "event_data must not have None values if allow_missing_values_flag is False."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if event_data not in self.known_values:
            self.known_values.append(event_data)
        return f"Allowlisted path(es) {', '.join(self.target_path_list)} with {event_data}."

    def log_statistics(self, component_name):
        """
        Log statistics of an AtomHandler. Override this method for more sophisticated statistics output of the AtomHandler.
        @param component_name the name of the component which is printed in the log line.
        """
        if AminerConfig.STAT_LEVEL == 1:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %s new value combinations in the last 60 minutes.",
                component_name, self.log_success, self.log_total, self.log_learned_path_value_combos)
        elif AminerConfig.STAT_LEVEL == 2:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %d new value combinations in the last 60 minutes. Following"
                " new value combinations were learned: %s", component_name, self.log_success, self.log_total,
                self.log_learned_path_value_combos, self.log_new_learned_values)
        self.log_success = 0
        self.log_total = 0
        self.log_learned_path_value_combos = 0
        self.log_new_learned_values = []
