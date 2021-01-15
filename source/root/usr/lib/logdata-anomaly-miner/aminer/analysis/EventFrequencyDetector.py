"""
This module defines an detector for event and value frequency deviations.
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
from aminer.util import PersistenceUtil
from aminer.util import TimeTriggeredComponentInterface
from aminer.analysis import CONFIG_KEY_LOG_LINE_PREFIX


class EventFrequencyDetector(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface):
    """This class creates events when event or value frequencies change."""

    def __init__(self, aminer_config, target_path_list, anomaly_event_handlers, window_size=600, confidence_factor=2,
                 persistence_id='Default', auto_include_flag=False, output_log_line=True, ignore_list=None, constraint_list=None):
        """Initialize the detector."""
        self.target_path_list = target_path_list
        self.anomaly_event_handlers = anomaly_event_handlers
        self.auto_include_flag = auto_include_flag
        self.next_persist_time = None
        self.output_log_line = output_log_line
        self.aminer_config = aminer_config
        self.persistence_id = persistence_id
        self.constraint_list = constraint_list
        if self.constraint_list is None:
            self.constraint_list = []
        self.ignore_list = ignore_list
        if self.ignore_list is None:
            self.ignore_list = []
        self.window_size = window_size
        if confidence_factor < 1:
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).warning('confidence_factor must be >= 1!')
            confidence_factor = 1
        self.confidence_factor = confidence_factor
        self.next_check_time = None
        self.counts = {}
        self.counts_prev = {}
        self.log_total = 0
        self.log_success = 0
        self.log_windows = 0

        PersistenceUtil.add_persistable_component(self)
        self.persistence_file_name = AMinerConfig.build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)

        # Persisted data contains lists of event-frequency pairs, i.e., [[<ev1, ev2>, <freq>], [<ev1, ev2>, <freq>], ...]
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        if persistence_data is not None:
            for entry in persistence_data:
                log_event = entry[0]
                frequency = entry[1]
                self.counts_prev[tuple(log_event)] = frequency
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).debug('%s loaded persistence data.', self.__class__.__name__)

    def receive_atom(self, log_atom):
        """Receive a log atom from a source."""
        parser_match = log_atom.parser_match
        self.log_total += 1

        # Skip paths from ignore list.
        for ignore_path in self.ignore_list:
            if ignore_path in parser_match.get_match_dictionary().keys():
                return

        if self.target_path_list is None or len(self.target_path_list) == 0:
            # Event is defined by the full path of log atom.
            constraint_path_flag = False
            for constraint_path in self.constraint_list:
                if parser_match.get_match_dictionary().get(constraint_path) is not None:
                    constraint_path_flag = True
                    break
            if not constraint_path_flag and self.constraint_list != []:
                return
            log_event = tuple(parser_match.get_match_dictionary().keys())
        else:
            # Event is defined by value combos in paths
            values = []
            all_values_none = True
            for path in self.target_path_list:
                match = parser_match.get_match_dictionary().get(path)
                if match is None:
                    continue
                if isinstance(match.match_object, bytes):
                    value = match.match_object.decode()
                else:
                    value = str(match.match_object)
                if value is not None:
                    all_values_none = False
                values.append(value)
            if all_values_none is True:
                return
            log_event = tuple(values)

        if self.next_check_time is None:
            # First processed log atom, initialize next check time.
            self.next_check_time = log_atom.atom_time + self.window_size
            self.log_windows += 1
        elif log_atom.atom_time >= self.next_check_time:
            # Log atom exceeded next check time; time window is complete.
            self.next_check_time = self.next_check_time + self.window_size
            self.log_windows += 1
            if self.next_persist_time is None:
                self.next_persist_time = time.time() + self.aminer_config.config_properties.get(
                    AMinerConfig.KEY_PERSISTENCE_PERIOD, AMinerConfig.DEFAULT_PERSISTENCE_PERIOD)

            if log_atom.atom_time >= self.next_check_time:
                self.next_check_time = log_atom.atom_time + self.window_size
                analysis_component = {'AffectedLogAtomPaths': [self.target_path_list]}
                event_data = {'AnalysisComponent': analysis_component}
                for listener in self.anomaly_event_handlers:
                    listener.receive_event('Analysis.%s' % self.__class__.__name__, 'No log events received in time window',
                                           [''], event_data, log_atom, self)
            for log_ev in self.counts_prev:
                # Get log event frequency in previous time window
                occurrences = 0
                if log_ev in self.counts:
                    occurrences = self.counts[log_ev]
                # Compare log event frequency of previous and current time window
                if occurrences < self.counts_prev[log_ev] / self.confidence_factor or occurrences > self.counts_prev[log_ev] * \
                                                                                      self.confidence_factor:
                    if self.output_log_line:
                        sorted_log_lines = [log_atom.parser_match.match_element.annotate_match('') + os.linesep + original_log_line_prefix +
                                            repr(log_atom.raw_data)]
                    else:
                        sorted_log_lines = [repr(log_atom.raw_data)]
                    confidence = 1 - min(occurrences, self.counts_prev[log_ev]) / max(occurrences, self.counts_prev[log_ev])
                    analysis_component = {'AffectedLogAtomPaths': self.target_path_list, 'AffectedLogAtomValues': list(log_ev)}
                    frequency_info = {'ExpectedLogAtomValuesFrequency': self.counts_prev[log_ev], 'LogAtomValuesFrequency': occurrences,
                                      'ConfidenceFactor': self.confidence_factor,
                                      'Confidence': confidence}
                    event_data = {'AnalysisComponent': analysis_component, 'FrequencyData': frequency_info}
                    for listener in self.anomaly_event_handlers:
                        listener.receive_event('Analysis.%s' % self.__class__.__name__, 'Frequency anomaly detected', sorted_log_lines,
                                               event_data, log_atom, self)
            if self.auto_include_flag is True:
                self.counts_prev = self.counts
            self.counts = {}

        if log_event in self.counts:
            self.counts[log_event] += 1
        else:
            self.counts[log_event] = 1
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
        persist_data = []
        for log_ev, freq in self.counts_prev.items():
            persist_data.append((log_ev, freq))
        PersistenceUtil.store_json(self.persistence_file_name, persist_data)
        self.next_persist_time = None
        logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).debug('%s persisted data.', self.__class__.__name__)

    def allowlist_event(self, event_type, event_data, allowlisting_data):
        """
        Allowlist an event generated by this source using the information emitted when generating the event.
        @return a message with information about allowlisting
        @throws Exception when allowlisting of this special event using given allowlisting_data was not possible.
        """
        if event_type != 'Analysis.%s' % self.__class__.__name__:
            msg = 'Event not from this source'
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if allowlisting_data is not None:
            msg = 'Allowlisting data not understood by this detector'
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if event_data not in self.constraint_list:
            self.constraint_list.append(event_data)
        return 'Allowlisted path %s.' % event_data

    def blocklist_event(self, event_type, event_data, blocklisting_data):
        """
        Blocklist an event generated by this source using the information emitted when generating the event.
        @return a message with information about blocklisting
        @throws Exception when blocklisting of this special event using given blocklisting_data was not possible.
        """
        if event_type != 'Analysis.%s' % self.__class__.__name__:
            msg = 'Event not from this source'
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if blocklisting_data is not None:
            msg = 'Blocklisting data not understood by this detector'
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if event_data not in self.ignore_list:
            self.ignore_list.append(event_data)
        return 'Blocklisted path %s.' % event_data

    def log_statistics(self, component_name):
        """
        Log statistics of an AtomHandler. Override this method for more sophisticated statistics output of the AtomHandler.
        @param component_name the name of the component which is printed in the log line.
        """
        if STAT_LEVEL == 1:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully in %d time windows in the last 60"
                " minutes.", component_name, self.log_success, self.log_total, self.log_windows)
        elif STAT_LEVEL == 2:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully in %d time windows in the last 60"
                " minutes. Following new sequences were learned: %s", component_name, self.log_success, self.log_total,
                self.log_windows)
        self.log_success = 0
        self.log_total = 0
        self.log_windows = 0
