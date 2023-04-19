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

import os
import logging

from aminer.AminerConfig import build_persistence_file_name, DEBUG_LOG_NAME, KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD,\
    STAT_LOG_NAME, CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX
from aminer import AminerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events.EventInterfaces import EventSourceInterface
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface
from aminer.util import PersistenceUtil


class NewMatchPathDetector(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface):
    """This class creates events when new data path was found in a parsed atom."""

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, anomaly_event_handlers, persistence_id="Default", learn_mode=False, output_logline=True,
                 stop_learning_time=None, stop_learning_no_anomaly_time=None):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param persistence_id name of persistence file.
        @param learn_mode specifies whether new values should be learned.
        @param output_logline specifies whether the full parsed log atom should be provided in the output.
        @param stop_learning_time switch the learn_mode to False after the time.
        @param stop_learning_no_anomaly_time switch the learn_mode to False after no anomaly was detected for that time.
        """
        # avoid "defined outside init" issue
        self.learn_mode, self.stop_learning_timestamp, self.next_persist_time, self.log_success, self.log_total = [None]*5
        super().__init__(
            aminer_config=aminer_config, anomaly_event_handlers=anomaly_event_handlers, persistence_id=persistence_id,
            learn_mode=learn_mode, output_logline=output_logline,  stop_learning_time=stop_learning_time,
            stop_learning_no_anomaly_time=stop_learning_no_anomaly_time
        )
        self.log_learned_paths = 0
        self.log_new_learned_paths = []
        self.known_path_set = set()

        self.persistence_file_name = build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)
        self.load_persistence_data()

    def receive_atom(self, log_atom):
        """
        Receive on parsed atom and the information about the parser match.
        @param log_atom the parsed log atom
        @return True if this handler was really able to handle and process the match. Depending on this information, the caller
                may decide if it makes sense passing the parsed atom also to other handlers.
        """
        self.log_total += 1
        unknown_path_list = []
        if self.learn_mode is True and self.stop_learning_timestamp is not None and \
                self.stop_learning_timestamp < log_atom.atom_time:
            logging.getLogger(DEBUG_LOG_NAME).info("Stopping learning in the %s.", self.__class__.__name__)
            self.learn_mode = False

        for path in log_atom.parser_match.get_match_dictionary().keys():
            if path not in self.known_path_set:
                unknown_path_list.append(path)
                if self.learn_mode:
                    self.known_path_set.add(path)
                    self.log_learned_paths += 1
                    self.log_new_learned_paths.append(path)
                    if self.stop_learning_timestamp is not None and self.stop_learning_no_anomaly_time is not None:
                        self.stop_learning_timestamp = max(
                            self.stop_learning_timestamp, log_atom.atom_time + self.stop_learning_no_anomaly_time)
        if unknown_path_list:
            original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
            try:
                data = log_atom.raw_data.decode(AminerConfig.ENCODING)
            except UnicodeError:
                data = repr(log_atom.raw_data)
            if self.output_logline:
                sorted_log_lines = [log_atom.parser_match.match_element.annotate_match('') + os.linesep + repr(
                    unknown_path_list) + os.linesep + original_log_line_prefix + data]
            else:
                sorted_log_lines = [repr(unknown_path_list) + os.linesep + original_log_line_prefix + data]
            analysis_component = {'AffectedLogAtomPaths': list(unknown_path_list)}
            event_data = {'AnalysisComponent': analysis_component}
            for listener in self.anomaly_event_handlers:
                listener.receive_event(f'Analysis.{self.__class__.__name__}', 'New path(es) detected', sorted_log_lines, event_data,
                                       log_atom, self)
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
        PersistenceUtil.store_json(self.persistence_file_name, sorted(list(self.known_path_set)))
        logging.getLogger(DEBUG_LOG_NAME).debug("%s persisted data.", self.__class__.__name__)

    def load_persistence_data(self):
        """Load the persistence data from storage."""
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        if persistence_data is not None:
            self.known_path_set = set(persistence_data)
            logging.getLogger(DEBUG_LOG_NAME).debug("%s loaded persistence data.", self.__class__.__name__)

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
        self.known_path_set.add(event_data)
        return f'Allowlisted path(es) {event_data} in {event_type}.'

    def log_statistics(self, component_name):
        """
        Log statistics of an AtomHandler. Override this method for more sophisticated statistics output of the AtomHandler.
        @param component_name the name of the component which is printed in the log line.
        """
        if AminerConfig.STAT_LEVEL == 1:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %d new paths in the last 60 minutes.",
                component_name, self.log_success, self.log_total, self.log_learned_paths)
        elif AminerConfig.STAT_LEVEL == 2:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %d new paths in the last 60 minutes. Following new paths"
                " were learned: %s", component_name, self.log_success, self.log_total, self.log_learned_paths, self.log_new_learned_paths)
        self.log_success = 0
        self.log_total = 0
        self.log_learned_paths = 0
        self.log_new_learned_paths = []
