"""
This file defines the basic NewMatchPathValueComboDetector detector.
It extracts values from LogAtoms and check, if the value combination was already seen before.

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
from aminer.input.InputInterfaces import AtomHandlerInterface, PersistableComponentInterface
from aminer.util import PersistenceUtil
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface


class NewMatchPathValueComboDetector(
        AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface, PersistableComponentInterface):
    """This class creates events when a new value combination for a given list of match data paths were found."""

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, target_path_list, anomaly_event_handlers, persistence_id="Default", allow_missing_values_flag=False,
                 learn_mode=False, output_logline=True, stop_learning_time=None, stop_learning_no_anomaly_time=None,
                 log_resource_ignore_list=None):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that all values occurring in these paths are
               considered for value range generation.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
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
            persistence_id=persistence_id, allow_missing_values_flag=allow_missing_values_flag, learn_mode=learn_mode,
            output_logline=output_logline, stop_learning_time=stop_learning_time,
            stop_learning_no_anomaly_time=stop_learning_no_anomaly_time, log_resource_ignore_list=log_resource_ignore_list,
            mutable_default_args=["log_resource_ignore_list"]
        )
        if not self.target_path_list:
            msg = "target_path_list must not be None or empty."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.log_learned_path_value_combos = 0
        self.log_new_learned_values = []

        self.persistence_file_name = build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        self.known_values_set = set()
        self.load_persistence_data()
        PersistenceUtil.add_persistable_component(self)

    def load_persistence_data(self):
        """Load the persistence data from storage."""
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        if persistence_data is not None:
            # Set and tuples were stored as list of lists. Transform the inner lists to tuples to allow hash operation needed by set.
            self.known_values_set = {tuple(record) for record in persistence_data}
            logging.getLogger(DEBUG_LOG_NAME).debug("%s loaded persistence data.", self.__class__.__name__)

    def receive_atom(self, log_atom):
        """
        Receive on parsed atom and the information about the parser match.
        @return True if a value combination was extracted and checked against the list of known combinations, no matter if the checked
        values were new or not.
        """
        for source in self.log_resource_ignore_list:
            if log_atom.source.resource_name.decode() == source:
                return False
        self.log_total += 1
        if self.learn_mode is True and self.stop_learning_timestamp is not None and \
                self.stop_learning_timestamp < log_atom.atom_time:
            logging.getLogger(DEBUG_LOG_NAME).info("Stopping learning in the %s.", self.__class__.__name__)
            self.learn_mode = False
        match_dict = log_atom.parser_match.get_match_dictionary()
        match_value_list = []
        for target_path in self.target_path_list:
            match_element = match_dict.get(target_path)
            if match_element is None:
                if not self.allow_missing_values_flag:
                    return False
                match_value_list.append(None)
            else:
                matches = []
                if isinstance(match_element, list):
                    matches = match_element
                else:
                    matches.append(match_element)
                for match_element in matches:
                    match_value_list.append(match_element.match_object)

        match_value_tuple = tuple(match_value_list)
        affected_log_atom_values = []
        for match_value in match_value_list:
            if isinstance(match_value, bytes):
                match_value = match_value.decode(AminerConfig.ENCODING)
            affected_log_atom_values.append(str(match_value))
        if match_value_tuple not in self.known_values_set:
            if self.learn_mode:
                self.known_values_set.add(match_value_tuple)
                self.log_learned_path_value_combos += 1
                self.log_new_learned_values.append(match_value_tuple)
                if self.stop_learning_timestamp is not None and self.stop_learning_no_anomaly_time is not None:
                    self.stop_learning_timestamp = max(
                        self.stop_learning_timestamp, log_atom.atom_time + self.stop_learning_no_anomaly_time)

            analysis_component = {"AffectedLogAtomPaths": self.target_path_list, "AffectedLogAtomValues": affected_log_atom_values}
            event_data = {"AnalysisComponent": analysis_component}
            try:
                data = log_atom.raw_data.decode(AminerConfig.ENCODING)
            except UnicodeError:
                data = repr(log_atom.raw_data)
            if self.output_logline:
                original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
                sorted_log_lines = [str(match_value_tuple) + os.linesep + original_log_line_prefix + data]
            else:
                sorted_log_lines = [str(match_value_tuple)]
            for listener in self.anomaly_event_handlers:
                listener.receive_event(f"Analysis.{self.__class__.__name__}", "New value combination(s) detected", sorted_log_lines,
                                       event_data, log_atom, self)
        self.log_success += 1
        return True

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
        PersistenceUtil.store_json(self.persistence_file_name, sorted(list(self.known_values_set)))
        logging.getLogger(DEBUG_LOG_NAME).debug("%s persisted data.", self.__class__.__name__)

    def allowlist_event(self, event_type, event_data, allowlisting_data):
        """
        Allowlist an event generated by this source using the information emitted when generating the event.
        @return a message with information about allowlisting
        @throws Exception when allowlisting of this special event using given allowlisting_data was not possible.
        """
        if event_type != f"Analysis.{self.__class__.__name__}":
            msg = "Event not from this source"
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if allowlisting_data is not None:
            msg = "Allowlisting data not understood by this detector"
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if not isinstance(event_data, tuple) or len(event_data) != len(self.target_path_list):
            msg = "event_data has to be of type tuple."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if not self.allow_missing_values_flag and None in event_data:
            msg = "event_data must not have None values if allow_missing_values_flag is False."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        self.known_values_set.add(event_data)
        return f"Allowlisted path(es) {', '.join(self.target_path_list)} with {event_data}."

    def add_to_persistency_event(self, event_type, event_data):
        """
        Add or overwrite the information of event_data to the persistence of component_name.
        @return a message with information about the addition to the persistence.
        @throws Exception when the addition of this special event using given event_data was not possible.
        """
        if event_type != f"Analysis.{self.__class__.__name__}":
            msg = "Event not from this source"
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if not isinstance(event_data, list) or len(event_data) != len(self.target_path_list):
            msg = "Event_data has the wrong format." \
                "The supported format is [value_1, value_2, ..., value_n] where n is the number of analyzed paths."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)

        match_value_list = []
        for match_element in event_data:
            if match_element is None:
                if not self.allow_missing_values_flag:
                    msg = "Empty entry detected in event_data." \
                        "Please fill entry or set parameter allow_missing_values_flag to true."
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise Exception(msg)
                match_value_list.append(None)
            else:
                match_value_list.append(bytes(match_element, "utf-8"))

        match_value_tuple = tuple(match_value_list)
        if match_value_tuple not in self.known_values_set:
            self.known_values_set.add(match_value_tuple)
            self.log_learned_path_value_combos += 1
            self.log_new_learned_values.append(match_value_tuple)
        return f"Added values [{', '.join(event_data)}] of paths [{', '.join(self.target_path_list)}] to the persistence."

    def log_statistics(self, component_name):
        """
        Log statistics of an AtomHandler. Override this method for more sophisticated statistics output of the AtomHandler.
        @param component_name the name of the component which is printed in the log line.
        """
        if AminerConfig.STAT_LEVEL == 1:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %d new value combinations in the last 60 minutes.",
                component_name, self.log_success, self.log_total, self.log_learned_path_value_combos)
        elif AminerConfig.STAT_LEVEL == 2:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %d new value combinations in the last 60 minutes."
                " Following new value combinations were learned: %s",
                component_name, self.log_success, self.log_total, self.log_learned_path_value_combos, self.log_new_learned_values)
        self.log_success = 0
        self.log_total = 0
        self.log_learned_path_value_combos = 0
        self.log_new_learned_values = []
