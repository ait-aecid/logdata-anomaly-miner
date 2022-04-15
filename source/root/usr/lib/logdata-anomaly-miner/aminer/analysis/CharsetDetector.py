"""
This module defines an detector for value character sets.
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
import time

from aminer.AminerConfig import DEBUG_LOG_NAME, STAT_LOG_NAME, CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX, KEY_PERSISTENCE_PERIOD,\
    DEFAULT_PERSISTENCE_PERIOD
from aminer import AminerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events.EventInterfaces import EventSourceInterface
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util import PersistenceUtil
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface


class CharsetDetector(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface):
    """This class creates events when numeric values are outside learned intervals."""

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, anomaly_event_handlers, id_path_list, target_path_list=None, persistence_id='Default',
                 auto_include_flag=False, output_log_line=True, ignore_list=None, constraint_list=None, stop_learning_time=None,
                 stop_learning_no_anomaly_time=None):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param id_path_list to specify group identifiers for which numeric ranges should be learned.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that all values occurring in these paths
        are considered for value range generation.
        @param persistence_id name of persistency document.
        @param auto_include_flag specifies whether value ranges should be extended when values outside of ranges are observed.
        @param output_log_line specifies whether the full parsed log atom should be provided in the output.
        @param ignore_list list of paths that are not considered for analysis, i.e., events that contain one of these paths are
        omitted.
        @param constraint_list list of paths that have to be present in the log atom to be analyzed.
        @param stop_learning_time switch the auto_include_flag to False after the time.
        @param stop_learning_no_anomaly_time switch the auto_include_flag to False after no anomaly was detected for that time.
        """
        self.target_path_list = target_path_list
        self.anomaly_event_handlers = anomaly_event_handlers
        self.auto_include_flag = auto_include_flag
        self.output_log_line = output_log_line
        self.aminer_config = aminer_config
        self.next_persist_time = time.time() + self.aminer_config.config_properties.get(KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)
        self.persistence_id = persistence_id
        self.id_path_list = id_path_list
        if constraint_list is None:
            self.constraint_list = []
        else:
            self.constraint_list = set(constraint_list)
        if ignore_list is None:
            self.ignore_list = []
        else:
            self.ignore_list = set(ignore_list)
        self.log_total = 0
        self.log_success = 0

        self.charsets = {}

        if auto_include_flag is False and (stop_learning_time is not None or stop_learning_no_anomaly_time is not None):
            msg = "It is not possible to use the stop_learning_time or stop_learning_no_anomaly_time when the auto_include_flag is False."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        if stop_learning_time is not None and stop_learning_no_anomaly_time is not None:
            msg = "stop_learning_time is mutually exclusive to stop_learning_no_anomaly_time. Only one of these attributes may be used."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        if not isinstance(stop_learning_time, (type(None), int)):
            msg = "stop_learning_time has to be of the type int or None."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if not isinstance(stop_learning_no_anomaly_time, (type(None), int)):
            msg = "stop_learning_no_anomaly_time has to be of the type int or None."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)

        self.stop_learning_timestamp = None
        if stop_learning_time is not None:
            self.stop_learning_timestamp = time.time() + stop_learning_time
        self.stop_learning_no_anomaly_time = stop_learning_no_anomaly_time
        if stop_learning_no_anomaly_time is not None:
            self.stop_learning_timestamp = time.time() + stop_learning_no_anomaly_time

        # Persisted data stores characters as bytes for each id, i.e., [[[<id1, id2, ...>], [<byte1, byte2, ...>]], ...]]
        self.persistence_file_name = AminerConfig.build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        if persistence_data is not None:
            for lst in persistence_data:
                self.charsets[tuple(lst[0])] = set(lst[1])

    def receive_atom(self, log_atom):
        """Receive a log atom from a source."""
        self.log_total += 1
        parser_match = log_atom.parser_match
        if self.auto_include_flag is True and self.stop_learning_timestamp is not None and \
                self.stop_learning_timestamp < log_atom.atom_time:
            logging.getLogger(DEBUG_LOG_NAME).info(f"Stopping learning in the {self.__class__.__name__}.")
            self.auto_include_flag = False

        # Skip atom when ignore paths in atom or constraint paths not in atom.
        all_paths_set = set(parser_match.get_match_dictionary().keys())
        if len(all_paths_set.intersection(self.ignore_list)) > 0 or \
                len(all_paths_set.intersection(self.constraint_list)) != len(self.constraint_list):
            return

        # Store all values from target paths in a list.
        values = []
        all_values_none = True
        for path in self.target_path_list:
            match = parser_match.get_match_dictionary().get(path)
            if match is None:
                continue
            matches = []
            if isinstance(match, list):
                matches = match
            else:
                matches.append(match)
            for match in matches:
                value = match.match_object
                if value is not None:
                    all_values_none = False
                values.append(value)
        if all_values_none is True:
            return

        # Store all values from id paths in a list. Use empty list as default path if not applicable.
        id_vals = []
        for path in self.id_path_list:
            match = parser_match.get_match_dictionary().get(path)
            if match is None:
                continue
            matches = []
            if isinstance(match, list):
                matches = match
            else:
                matches.append(match)
            for match in matches:
                if isinstance(match.match_object, bytes):
                    value = match.match_object.decode(AminerConfig.ENCODING)
                else:
                    value = str(match.match_object)
                id_vals.append(value)
        id_event = tuple(id_vals)

        # Check if one of the values has new characters for a specific id path.
        if id_event in self.charsets:
            missing_chars = set()
            for c in b''.join(values):
                if c not in self.charsets[id_event]:
                    missing_chars.add(c)
            if len(missing_chars) > 0:
                try:
                    data = log_atom.raw_data.decode(AminerConfig.ENCODING)
                except UnicodeError:
                    data = repr(log_atom.raw_data)
                if self.output_log_line:
                    original_log_line_prefix = self.aminer_config.config_properties.get(
                        CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
                    sorted_log_lines = [log_atom.parser_match.match_element.annotate_match('') + os.linesep + original_log_line_prefix +
                                        data]
                else:
                    sorted_log_lines = [data]
                missing_chars_decoded = []
                for character in missing_chars:
                    missing_chars_decoded.append(character.to_bytes(1, 'big').decode(AminerConfig.ENCODING))
                affected_values = []
                for value in values:
                    affected_values.append(value.decode(AminerConfig.ENCODING))
                analysis_component = {'AffectedLogAtomPaths': self.target_path_list, 'AffectedLogAtomValues': affected_values,
                                      'MissingCharacters': missing_chars_decoded}
                event_data = {'AnalysisComponent': analysis_component}
                for listener in self.anomaly_event_handlers:
                    listener.receive_event('Analysis.%s' % self.__class__.__name__, 'New character(s) detected', sorted_log_lines,
                                           event_data, log_atom, self)
            # Extend charsets if learn mode is active.
            if self.auto_include_flag is True:
                self.charsets[id_event].update(missing_chars)
                if self.stop_learning_timestamp is not None and self.stop_learning_no_anomaly_time is not None:
                    self.stop_learning_timestamp = time.time() + self.stop_learning_no_anomaly_time
        else:
            self.charsets[id_event] = set(b''.join(values))
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
        lst = []
        for id_ev, charset in self.charsets.items():
            lst.append([id_ev, list(charset)])
        PersistenceUtil.store_json(self.persistence_file_name, lst)
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug('%s persisted data.', self.__class__.__name__)

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
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if blocklisting_data is not None:
            msg = 'Blocklisting data not understood by this detector'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if event_data not in self.ignore_list:
            self.ignore_list.append(event_data)
        return 'Blocklisted path %s.' % event_data

    def log_statistics(self, component_name):
        """
        Log statistics of an AtomHandler. Override this method for more sophisticated statistics output of the AtomHandler.
        @param component_name the name of the component which is printed in the log line.
        """
        if AminerConfig.STAT_LEVEL == 1:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully in the last 60"
                " minutes.", component_name, self.log_success, self.log_total)
        elif AminerConfig.STAT_LEVEL == 2:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully in the last 60"
                " minutes.", component_name, self.log_success, self.log_total)
        self.log_success = 0
        self.log_total = 0
