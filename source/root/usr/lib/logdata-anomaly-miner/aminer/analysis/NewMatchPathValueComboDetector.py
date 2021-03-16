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

import time
import os
import logging

from aminer import AminerConfig
from aminer.AminerConfig import STAT_LEVEL, STAT_LOG_NAME, CONFIG_KEY_LOG_LINE_PREFIX
from aminer.AnalysisChild import AnalysisContext
from aminer.events.EventInterfaces import EventSourceInterface
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util import PersistenceUtil
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface


class NewMatchPathValueComboDetector(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface):
    """This class creates events when a new value combination for a given list of match data pathes were found."""

    def __init__(self, aminer_config, target_path_list, anomaly_event_handlers, persistence_id='Default', allow_missing_values_flag=False,
                 auto_include_flag=False, output_log_line=True):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param target_path_list the list of values to extract from each match to create the value combination to be checked.
        @param allow_missing_values_flag when set to True, the detector will also use matches, where one of the pathes from target_path_list
        does not refer to an existing parsed data object.
        @param auto_include_flag when set to True, this detector will report a new value only the first time before including it
        in the known values set automatically.
        """
        self.target_path_list = target_path_list
        self.anomaly_event_handlers = anomaly_event_handlers
        self.allow_missing_values_flag = allow_missing_values_flag
        self.auto_include_flag = auto_include_flag
        self.output_log_line = output_log_line
        self.aminer_config = aminer_config
        self.persistence_id = persistence_id

        self.log_success = 0
        self.log_total = 0
        self.log_learned_path_value_combos = 0
        self.log_new_learned_values = []

        self.persistence_file_name = AminerConfig.build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        self.next_persist_time = None
        self.known_values_set = set()
        self.load_persistence_data()
        PersistenceUtil.add_persistable_component(self)

    def load_persistence_data(self):
        """Load the persistence data from storage."""
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        if persistence_data is not None:
            # Set and tuples were stored as list of lists. Transform the inner lists to tuples to allow hash operation needed by set.
            self.known_values_set = {tuple(record) for record in persistence_data}
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug('%s loaded persistence data.', self.__class__.__name__)

    def receive_atom(self, log_atom):
        """
        Receive on parsed atom and the information about the parser match.
        @return True if a value combination was extracted and checked against the list of known combinations, no matter if the checked
        values were new or not.
        """
        self.log_total += 1
        match_dict = log_atom.parser_match.get_match_dictionary()
        match_value_list = []
        for target_path in self.target_path_list:
            match_element = match_dict.get(target_path, None)
            if match_element is None:
                if not self.allow_missing_values_flag:
                    return False
                match_value_list.append(None)
            else:
                match_value_list.append(match_element.match_object)

        match_value_tuple = tuple(match_value_list)
        affected_log_atom_values = []
        for match_value in match_value_list:
            if isinstance(match_value, bytes):
                match_value = match_value.decode()
            affected_log_atom_values.append(str(match_value))
        if match_value_tuple not in self.known_values_set:
            if self.auto_include_flag:
                self.known_values_set.add(match_value_tuple)
                self.log_learned_path_value_combos += 1
                self.log_new_learned_values.append(match_value_tuple)
                if self.next_persist_time is None:
                    self.next_persist_time = time.time() + self.aminer_config.config_properties.get(
                        AminerConfig.KEY_PERSISTENCE_PERIOD, AminerConfig.DEFAULT_PERSISTENCE_PERIOD)

            analysis_component = {'AffectedLogAtomPaths': self.target_path_list, 'AffectedLogAtomValues': affected_log_atom_values}
            event_data = {'AnalysisComponent': analysis_component}
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
                    match_value_tuple) + os.linesep + original_log_line_prefix + repr(log_atom.raw_data)]
            else:
                sorted_log_lines = [str(match_value_tuple) + os.linesep + original_log_line_prefix + repr(log_atom.raw_data)]
            for listener in self.anomaly_event_handlers:
                listener.receive_event('Analysis.%s' % self.__class__.__name__, 'New value combination(s) detected', sorted_log_lines,
                                       event_data, log_atom, self)
        self.log_success += 1
        return True

    def get_time_trigger_class(self):  # skipcq: PYL-R0201
        """
        Get the trigger class this component should be registered for.
        This trigger is used only for persistence, so real-time triggering is needed.
        """
        return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def do_timer(self, trigger_time):
        """Check current ruleset should be persisted."""
        if self.next_persist_time is None:
            return self.aminer_config.config_properties.get(AminerConfig.KEY_PERSISTENCE_PERIOD, AminerConfig.DEFAULT_PERSISTENCE_PERIOD)

        delta = self.next_persist_time - trigger_time
        if delta < 0:
            self.do_persist()
            delta = self.aminer_config.config_properties.get(AminerConfig.KEY_PERSISTENCE_PERIOD, AminerConfig.DEFAULT_PERSISTENCE_PERIOD)
        return delta

    def do_persist(self):
        """Immediately write persistence data to storage."""
        PersistenceUtil.store_json(self.persistence_file_name, list(self.known_values_set))
        self.next_persist_time = None
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug('%s persisted data.', self.__class__.__name__)

    def allowlist_event(self, event_type, event_data, allowlisting_data):
        """
        Allowlist an event generated by this source using the information emitted when generating the event.
        @return a message with information about allowlisting
        @throws Exception when allowlisting of this special event using given allowlisting_data was not possible.
        """
        if event_type != 'Analysis.%s' % self.__class__.__name__:
            msg = 'Event not from this source'
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if allowlisting_data is not None:
            msg = 'Allowlisting data not understood by this detector'
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        self.known_values_set.add(event_data)
        return 'Allowlisted path(es) %s with %s.' % (', '.join(self.target_path_list), event_data)

    def log_statistics(self, component_name):
        """
        Log statistics of an AtomHandler. Override this method for more sophisticated statistics output of the AtomHandler.
        @param component_name the name of the component which is printed in the log line.
        """
        if STAT_LEVEL == 1:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %d new value combinations in the last 60"
                " minutes.", component_name, self.log_success, self.log_total, self.log_learned_path_value_combos)
        elif STAT_LEVEL == 2:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %d new value combinations in the last 60"
                " minutes. Following new value combinations were learned: %s", component_name, self.log_success, self.log_total,
                self.log_learned_path_value_combos, self.log_new_learned_values)
        self.log_success = 0
        self.log_total = 0
        self.log_learned_path_value_combos = 0
        self.log_new_learned_values = []
