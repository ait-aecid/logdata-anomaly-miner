"""
This module defines a detector for new values in a data path.

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

from aminer import AMinerConfig
from aminer.AMinerConfig import STAT_LEVEL, STAT_LOG_NAME
from aminer.AnalysisChild import AnalysisContext
from aminer.input import AtomHandlerInterface
from aminer.util import PersistenceUtil
from aminer.util import TimeTriggeredComponentInterface
from aminer.analysis import CONFIG_KEY_LOG_LINE_PREFIX


class NewMatchPathValueDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """This class creates events when new values for a given data path were found."""

    def __init__(self, aminer_config, target_path_list, anomaly_event_handlers, persistence_id='Default', auto_include_flag=False,
                 output_log_line=True):
        """Initialize the detector. This will also trigger reading or creation of persistence storage location."""
        self.target_path_list = target_path_list
        self.anomaly_event_handlers = anomaly_event_handlers
        self.auto_include_flag = auto_include_flag
        self.next_persist_time = None
        self.output_log_line = output_log_line
        self.aminer_config = aminer_config
        self.persistence_id = persistence_id

        self.log_success = 0
        self.log_total = 0
        self.log_learned_path_values = 0
        self.log_new_learned_values = []

        PersistenceUtil.add_persistable_component(self)
        self.persistence_file_name = AMinerConfig.build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        if persistence_data is None:
            self.known_path_set = set()
        else:
            self.known_path_set = set(persistence_data)
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).debug('%s loaded persistence data.', self.__class__.__name__)

    def receive_atom(self, log_atom):
        """Receive a log atom from a source."""
        self.log_total += 1
        match_dict = log_atom.parser_match.get_match_dictionary()
        for target_path in self.target_path_list:
            match = match_dict.get(target_path, None)
            if match is None:
                continue
            if match.match_object not in self.known_path_set:
                if self.auto_include_flag:
                    self.known_path_set.add(match.match_object)
                    self.log_learned_path_values += 1
                    self.log_new_learned_values.append(match.match_object)
                    if self.next_persist_time is None:
                        self.next_persist_time = time.time() + self.aminer_config.config_properties.get(
                            AMinerConfig.KEY_PERSISTENCE_PERIOD, AMinerConfig.DEFAULT_PERSISTENCE_PERIOD)

                if isinstance(match.match_object, bytes):
                    affected_log_atom_values = [match.match_object.decode()]
                else:
                    affected_log_atom_values = [str(match.match_object)]
                analysis_component = {'AffectedLogAtomPaths': [target_path], 'AffectedLogAtomValues': affected_log_atom_values}
                if isinstance(match.match_object, bytes):
                    res = {target_path: match.match_object.decode()}
                else:
                    res = {target_path: match.match_object}
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
                        res) + os.linesep + original_log_line_prefix + repr(log_atom.raw_data)]
                else:
                    sorted_log_lines = [str(res) + os.linesep + original_log_line_prefix + repr(log_atom.raw_data)]
                event_data = {'AnalysisComponent': analysis_component}
                for listener in self.anomaly_event_handlers:
                    listener.receive_event('Analysis.%s' % self.__class__.__name__, 'New value(s) detected', sorted_log_lines, event_data,
                                           log_atom, self)
                self.log_success += 1

    def get_time_trigger_class(self):
        """
        Get the trigger class this component should be registered for.
        This trigger is used only for persistence, so real-time triggering is needed.
        """
        return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def do_timer(self, trigger_time):
        """Check current ruleset should be persisted."""
        if self.next_persist_time is None:
            return 600

        delta = self.next_persist_time - trigger_time
        if delta < 0:
            self.do_persist()
            delta = 600
        return delta

    def do_persist(self):
        """Immediately write persistence data to storage."""
        PersistenceUtil.store_json(self.persistence_file_name, list(self.known_path_set))
        self.next_persist_time = None
        logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).debug('%s persisted data.', self.__class__.__name__)

    def log_statistics(self, component_name):
        """
        Log statistics of an AtomHandler. Override this method for more sophisticated statistics output of the AtomHandler.
        @param component_name the name of the component which is printed in the log line.
        """
        if STAT_LEVEL == 1:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %d new value combinations in the last 60"
                " minutes.", component_name, self.log_success, self.log_total, self.log_learned_path_values)
        elif STAT_LEVEL == 2:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %d new value combinations in the last 60"
                " minutes. Following new value combinations were learned: %s", component_name, self.log_success, self.log_total,
                self.log_learned_path_values, self.log_new_learned_values)
        self.log_success = 0
        self.log_total = 0
        self.log_learned_path_values = 0
        self.log_new_learned_values = []
