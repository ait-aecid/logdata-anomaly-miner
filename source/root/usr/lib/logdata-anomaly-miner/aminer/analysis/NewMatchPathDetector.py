"""
This module defines a detector for new data paths.

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
from aminer.events import EventSourceInterface
from aminer.input import AtomHandlerInterface
from aminer.util import TimeTriggeredComponentInterface
from aminer.util import PersistencyUtil
from aminer.analysis import CONFIG_KEY_LOG_LINE_PREFIX


class NewMatchPathDetector(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface):
    """This class creates events when new data path was found in a parsed atom."""

    def __init__(self, aminer_config, anomaly_event_handlers, persistence_id='Default', auto_include_flag=False, output_log_line=True):
        """Initialize the detector. This will also trigger reading or creation of persistence storage location."""
        self.anomaly_event_handlers = anomaly_event_handlers
        self.auto_include_flag = auto_include_flag
        self.next_persist_time = None
        self.output_log_line = output_log_line
        self.aminer_config = aminer_config
        self.persistence_id = persistence_id

        self.log_success = 0
        self.log_total = 0
        self.log_learned_paths = 0
        self.log_new_learned_paths = []

        PersistencyUtil.add_persistable_component(self)
        self.persistence_file_name = AMinerConfig.build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        persistence_data = PersistencyUtil.load_json(self.persistence_file_name)
        if persistence_data is None:
            self.known_path_set = set()
        else:
            self.known_path_set = set(persistence_data)
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).debug('%s loaded persistence data.', self.__class__.__name__)

    def receive_atom(self, log_atom):
        """
        Receive on parsed atom and the information about the parser match.
        @param log_atom the parsed log atom
        @return True if this handler was really able to handle and process the match. Depending on this information, the caller
        may decide if it makes sense passing the parsed atom also to other handlers.
        """
        self.log_total += 1
        unknown_path_list = []
        for path in log_atom.parser_match.get_match_dictionary().keys():
            if path not in self.known_path_set:
                unknown_path_list.append(path)
                if self.auto_include_flag:
                    self.known_path_set.add(path)
                    self.log_learned_paths += 1
                    self.log_new_learned_paths.append(path)
        if unknown_path_list:
            if self.next_persist_time is None:
                self.next_persist_time = time.time() + 600
            original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX)
            if original_log_line_prefix is None:
                original_log_line_prefix = ''
            if self.output_log_line:
                sorted_log_lines = [log_atom.parser_match.match_element.annotate_match('') + os.linesep + repr(
                    unknown_path_list) + os.linesep + original_log_line_prefix + repr(log_atom.raw_data)]
            else:
                sorted_log_lines = [repr(unknown_path_list) + os.linesep + original_log_line_prefix + repr(log_atom.raw_data)]
            analysis_component = {'AffectedLogAtomPaths': list(unknown_path_list)}
            if self.output_log_line:
                match_paths_values = {}
                for match_path, match_element in log_atom.parser_match.get_match_dictionary().items():
                    match_value = match_element.match_object
                    if isinstance(match_value, bytes):
                        match_value = match_value.decode()
                    match_paths_values[match_path] = match_value
                analysis_component['ParsedLogAtom'] = match_paths_values
            event_data = {'AnalysisComponent': analysis_component}
            for listener in self.anomaly_event_handlers:
                listener.receive_event('Analysis.%s' % self.__class__.__name__, 'New path(es) detected', sorted_log_lines, event_data,
                                       log_atom, self)
        self.log_success += 1
        return True

    def get_time_trigger_class(self):
        """Get the trigger class this component can be registered for. This detector only needs persisteny triggers in real time."""
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
        PersistencyUtil.store_json(self.persistence_file_name, list(self.known_path_set))
        self.next_persist_time = None
        logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).debug('%s persisted data.', self.__class__.__name__)

    def whitelist_event(self, event_type, sorted_log_lines, event_data, whitelisting_data):
        """
        Whitelist an event generated by this source using the information emitted when generating the event.
        @return a message with information about whitelisting
        @throws Exception when whitelisting of this special event using given whitelistingData was not possible.
        """
        if event_type != 'Analysis.%s' % self.__class__.__name__:
            raise Exception('Event not from this source')
        if whitelisting_data is not None:
            raise Exception('Whitelisting data not understood by this detector')
        whitelisted_str = ''
        for path_name in event_data[1]:
            if path_name in self.known_path_set:
                continue
            self.known_path_set.add(path_name)
            if whitelisted_str:
                whitelisted_str += ', '
            whitelisted_str += path_name
        return 'Whitelisted path(es) %s in %s' % (whitelisted_str, sorted_log_lines[0])

    def log_statistics(self, component_name):
        """log statistics of an AtomHandler. Override this method for more sophisticated statistics output of the AtomHandler.
        @param component_name the name of the component which is printed in the log line."""
        if STAT_LEVEL == 1:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %d new paths in the last 60"
                " minutes.", component_name, self.log_success, self.log_total, self.log_learned_paths)
        elif STAT_LEVEL == 2:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %d new paths in the last 60"
                " minutes. Following new paths were learned: %s", component_name, self.log_success, self.log_total, self.log_learned_paths,
                self.log_new_learned_paths)
        self.log_success = 0
        self.log_total = 0
        self.log_learned_paths = 0
        self.log_new_learned_paths = []
