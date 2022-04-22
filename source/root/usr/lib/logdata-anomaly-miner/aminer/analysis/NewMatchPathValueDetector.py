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

from aminer.AminerConfig import build_persistence_file_name, DEBUG_LOG_NAME, KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD,\
    STAT_LOG_NAME, CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX
from aminer import AminerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events.EventInterfaces import EventSourceInterface
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util import PersistenceUtil
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface


class NewMatchPathValueDetector(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface):
    """This class creates events when new values for a given data path were found."""

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, target_path_list, anomaly_event_handlers, persistence_id='Default', auto_include_flag=False,
                 output_log_line=True):
        """Initialize the detector. This will also trigger reading or creation of persistence storage location."""
        self.target_path_list = target_path_list
        self.anomaly_event_handlers = anomaly_event_handlers
        self.auto_include_flag = auto_include_flag
        self.output_log_line = output_log_line
        self.aminer_config = aminer_config
        self.next_persist_time = time.time() + self.aminer_config.config_properties.get(KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)
        self.persistence_id = persistence_id

        self.log_success = 0
        self.log_total = 0
        self.log_learned_path_values = 0
        self.log_new_learned_values = []

        self.persistence_file_name = build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        if persistence_data is None:
            self.known_values_set = set()
        else:
            self.known_values_set = set(persistence_data)
            logging.getLogger(DEBUG_LOG_NAME).debug('%s loaded persistence data.', self.__class__.__name__)

    def receive_atom(self, log_atom):
        """Receive a log atom from a source."""
        self.log_total += 1
        match_dict = log_atom.parser_match.get_match_dictionary()
        for target_path in self.target_path_list:
            match = match_dict.get(target_path)
            if match is None:
                continue
            matches = []
            if isinstance(match, list):
                matches = match
            else:
                matches.append(match)
            affected_log_atom_values = []
            for match in matches:
                if match.match_object not in self.known_values_set:
                    if self.auto_include_flag:
                        self.known_values_set.add(match.match_object)
                        self.log_learned_path_values += 1
                        self.log_new_learned_values.append(match.match_object)

                    if isinstance(match.match_object, bytes):
                        affected_log_atom_values.append(match.match_object.decode(AminerConfig.ENCODING))
                    else:
                        affected_log_atom_values.append(str(match.match_object))
            if len(affected_log_atom_values) > 0:
                analysis_component = {'AffectedLogAtomPaths': [target_path], 'AffectedLogAtomValues': affected_log_atom_values}
                if isinstance(match_dict.get(target_path), list):
                    res = {target_path: affected_log_atom_values}
                else:
                    res = {target_path: match_dict.get(target_path).match_object}
                    if isinstance(res[target_path], bytes):
                        res[target_path] = res[target_path].decode(AminerConfig.ENCODING)
                try:
                    data = log_atom.raw_data.decode(AminerConfig.ENCODING)
                except UnicodeError:
                    data = repr(log_atom.raw_data)
                original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
                sorted_log_lines = [str(res) + os.linesep + original_log_line_prefix + data]
                event_data = {'AnalysisComponent': analysis_component}
                for listener in self.anomaly_event_handlers:
                    listener.receive_event('Analysis.%s' % self.__class__.__name__, 'New value(s) detected', sorted_log_lines, event_data,
                                           log_atom, self)
                self.log_success += 1

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
        PersistenceUtil.store_json(self.persistence_file_name, list(self.known_values_set))
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
        self.known_values_set.add(event_data)
        return 'Allowlisted path(es) %s with %s.' % (', '.join(self.target_path_list), event_data.decode())

    def log_statistics(self, component_name):
        """
        Log statistics of an AtomHandler. Override this method for more sophisticated statistics output of the AtomHandler.
        @param component_name the name of the component which is printed in the log line.
        """
        if AminerConfig.STAT_LEVEL == 1:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %d new value combinations in the last 60"
                " minutes.", component_name, self.log_success, self.log_total, self.log_learned_path_values)
        elif AminerConfig.STAT_LEVEL == 2:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %d new value combinations in the last 60"
                " minutes. Following new value combinations were learned: %s", component_name, self.log_success, self.log_total,
                self.log_learned_path_values, self.log_new_learned_values)
        self.log_success = 0
        self.log_total = 0
        self.log_learned_path_values = 0
        self.log_new_learned_values = []
