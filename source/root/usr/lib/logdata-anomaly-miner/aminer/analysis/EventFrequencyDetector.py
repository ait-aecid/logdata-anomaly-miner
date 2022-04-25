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
import numpy as np

from aminer.AminerConfig import DEBUG_LOG_NAME, build_persistence_file_name, KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD,\
    STAT_LOG_NAME, CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX
from aminer import AminerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events.EventInterfaces import EventSourceInterface
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util import PersistenceUtil
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface


class EventFrequencyDetector(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface):
    """This class creates events when event or value frequencies change."""

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, anomaly_event_handlers, target_path_list=None, window_size=600, num_windows=50,
                 confidence_factor=0.33, empty_window_warnings=True, early_exceeding_anomaly_output=False, set_lower_limit=None,
                 set_upper_limit=None, persistence_id='Default', auto_include_flag=False, output_log_line=True, ignore_list=None,
                 constraint_list=None):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that values are analyzed by their combined
        occurrences. When no paths are specified, the events given by the full path list are analyzed.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param window_size the length of the time window for counting in seconds.
        @param num_windows the number of previous time windows considered for expected frequency estimation.
        @param confidence_factor defines range of tolerable deviation of measured frequency from expected frequency according to
        occurrences_mean +- occurrences_std / self.confidence_factor. Default value is 0.33 = 3*sigma deviation. confidence_factor
        must be in range [0, 1].
        @param empty_window_warnings whether anomalies should be generated for too small window sizes.
        @param early_exceeding_anomaly_output states if a anomaly should be raised the first time the appearance count exceedes the range.
        @param set_lower_limit sets the lower limit of the frequency test to the specified value.
        @param set_upper_limit sets the upper limit of the frequency test to the specified value.
        @param persistence_id name of persistency document.
        @param auto_include_flag specifies whether new frequency measurements override ground truth frequencies.
        @param output_log_line specifies whether the full parsed log atom should be provided in the output.
        @param ignore_list list of paths that are not considered for analysis, i.e., events that contain one of these paths are
        omitted. The default value is [] as None is not iterable.
        @param constrain_list list of paths that have to be present in the log atom to be analyzed.
        """
        self.target_path_list = target_path_list
        self.anomaly_event_handlers = anomaly_event_handlers
        self.auto_include_flag = auto_include_flag
        self.output_log_line = output_log_line
        self.aminer_config = aminer_config
        self.next_persist_time = time.time() + self.aminer_config.config_properties.get(KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)
        self.persistence_id = persistence_id
        self.constraint_list = constraint_list
        if self.constraint_list is None:
            self.constraint_list = []
        self.ignore_list = ignore_list
        if self.ignore_list is None:
            self.ignore_list = []
        self.window_size = window_size
        self.num_windows = num_windows
        if not 0 <= confidence_factor <= 1:
            logging.getLogger(DEBUG_LOG_NAME).warning('confidence_factor must be in the range [0,1]!')
            confidence_factor = 1
        self.confidence_factor = confidence_factor
        self.empty_window_warnings = empty_window_warnings
        self.early_exceeding_anomaly_output = early_exceeding_anomaly_output
        self.set_lower_limit = set_lower_limit
        self.set_upper_limit = set_upper_limit
        self.next_check_time = None
        self.counts = {}
        self.ranges = {}
        self.exceeded_range_frequency = {}
        self.log_total = 0
        self.log_success = 0
        self.log_windows = 0

        self.persistence_file_name = build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)

        # Persisted data contains lists of event-frequency pairs, i.e., [[<ev>, [<freq1, freq2>]], [<ev>, [<freq1, freq2>]], ...]
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        if persistence_data is not None:
            for entry in persistence_data:
                log_event = entry[0]
                freqs = entry[1]
                # In case that num_windows differ, only take as many as possible
                self.counts[tuple(log_event)] = freqs[max(0, len(freqs) - num_windows - 1):] + [0]
            logging.getLogger(DEBUG_LOG_NAME).debug('%s loaded persistence data.', self.__class__.__name__)

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

            # Update next_check_time if a time window was skipped
            skipped_windows = 0
            if log_atom.atom_time >= self.next_check_time:
                skipped_windows = 1 + int((log_atom.atom_time - self.next_check_time) / self.window_size)
                self.next_check_time = self.next_check_time + skipped_windows * self.window_size
                # Output anomaly in case that no log event occurs within a time window
                if self.empty_window_warnings is True:
                    analysis_component = {'AffectedLogAtomPaths': self.target_path_list}
                    event_data = {'AnalysisComponent': analysis_component}
                    for listener in self.anomaly_event_handlers:
                        listener.receive_event('Analysis.%s' % self.__class__.__name__, 'No log events received in time window',
                                               [''], event_data, log_atom, self)
            for log_ev in self.counts:
                # Check if ranges should be initialised
                if log_ev not in self.ranges:
                    self.ranges[log_ev] = None
                    self.exceeded_range_frequency[log_ev] = False
                # Calculate the ranges if it was not already calculated
                if self.ranges[log_ev] is None:
                    self.ranges[log_ev] = self.calculate_range(log_ev)
                if log_ev not in self.counts or (len(self.counts[log_ev]) < 2 and (
                        self.set_lower_limit is None or self.set_upper_limit is None)):
                    # At least counts from 1 window necessary for prediction
                    self.reset_counter(log_ev)
                    continue
                # Compare log event frequency of previous time windows and current time window
                if self.counts[log_ev][-1] < self.ranges[log_ev][0] or self.counts[log_ev][-1] > self.ranges[log_ev][1]:
                    occurrences_mean = (self.ranges[log_ev][0] + self.ranges[log_ev][1]) / 2
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
                    analysis_component = {'AffectedLogAtomPaths': self.target_path_list, 'AffectedLogAtomValues': list(log_ev)}
                    frequency_info = {'ExpectedLogAtomValuesFrequency': occurrences_mean,
                                      'ExpectedLogAtomValuesFrequencyRange': [
                                          np.ceil(max(0, self.ranges[log_ev][0])),
                                          np.floor(self.ranges[log_ev][1])],
                                      'LogAtomValuesFrequency': self.counts[log_ev][-1],
                                      'ConfidenceFactor': self.confidence_factor,
                                      'Confidence': 1 - min(occurrences_mean, self.counts[log_ev][-1]) /
                                      max(occurrences_mean, self.counts[log_ev][-1])}
                    event_data = {'AnalysisComponent': analysis_component, 'FrequencyData': frequency_info}
                    for listener in self.anomaly_event_handlers:
                        listener.receive_event('Analysis.%s' % self.__class__.__name__, 'Frequency anomaly detected', sorted_log_lines,
                                               event_data, log_atom, self)
                    # Reset exceeded_range_frequency to output a warning when the count exceedes the ranges next time
                    self.exceeded_range_frequency[log_ev] = False

                # Reset counter and range estimation
                for _ in range(skipped_windows + 1):
                    self.reset_counter(log_ev)
                self.ranges[log_ev] = None
        elif self.early_exceeding_anomaly_output and log_event in self.counts and (len(self.counts[log_event]) >= 2 or (
                self.set_lower_limit is not None and self.set_upper_limit is not None)):
            # Check if the count exceeds the range and output a warning the first time the range exceeds it
            if log_event not in self.ranges:
                self.ranges[log_event] = None
                self.exceeded_range_frequency[log_event] = False
            # Calculate the ranges if it was not already calculated
            if self.ranges[log_event] is None:
                self.ranges[log_event] = self.calculate_range(log_event)
            # Compare log event frequency of previous time windows and current time window
            if self.counts[log_event][-1] + 1 > self.ranges[log_event][1] and not self.exceeded_range_frequency[log_event]:
                occurrences_mean = (self.ranges[log_event][0] + self.ranges[log_event][1]) / 2
                self.exceeded_range_frequency[log_event] = True
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
                analysis_component = {'AffectedLogAtomPaths': self.target_path_list, 'AffectedLogAtomValues': list(log_event)}
                frequency_info = {'ExpectedLogAtomValuesFrequency': occurrences_mean,
                                  'ExpectedLogAtomValuesFrequencyRange': [
                                      np.ceil(max(0, self.ranges[log_event][0])),
                                      np.floor(self.ranges[log_event][1])],
                                  'LogAtomValuesFrequency': self.counts[log_event][-1] + 1,
                                  'ConfidenceFactor': self.confidence_factor}
                event_data = {'AnalysisComponent': analysis_component, 'FrequencyData': frequency_info}
                for listener in self.anomaly_event_handlers:
                    listener.receive_event('Analysis.%s' % self.__class__.__name__, 'Frequency exceeds range for the first time',
                                           sorted_log_lines, event_data, log_atom, self)
        # Increase count for observed events
        if log_event in self.counts:
            self.counts[log_event][-1] += 1
        else:
            self.counts[log_event] = [1]
        self.log_success += 1

    def reset_counter(self, event_type):
        # Create count index for new time window
        if self.auto_include_flag is True:
            if len(self.counts[event_type]) <= self.num_windows + 1:
                self.counts[event_type].append(0)
            else:
                self.counts[event_type] = self.counts[event_type][1:] + [0]
        else:
            self.counts[event_type][-1] = 0

    def calculate_range(self, log_event):
        """Calculate the corresponding range to log_event."""
        if self.set_lower_limit is None or self.set_upper_limit is None:
            if log_event not in self.counts or len(self.counts[log_event]) < 2:
                return None
            occurrences_mean = -1
            occurrences_std = -1
            occurrences_mean = np.mean(self.counts[log_event][-self.num_windows-1:-1])
            if len(self.counts[log_event][-self.num_windows-1:-1]) > 1:
                # Only compute standard deviation for at least 2 observed counts
                occurrences_std = np.std(self.counts[log_event][-self.num_windows-1:-1])
            else:
                # Otherwise use default value so that only (1 - confidence_factor) relevant (other factor cancels out)
                occurrences_std = occurrences_mean * (1 - self.confidence_factor)
        # Calculate limits
        if self.set_lower_limit is not None:
            lower_limit = self.set_lower_limit
        else:
            lower_limit = occurrences_mean - occurrences_std / self.confidence_factor
        if self.set_upper_limit is not None:
            upper_limit = self.set_upper_limit
        else:
            upper_limit = occurrences_mean + occurrences_std / self.confidence_factor
        return [lower_limit, upper_limit]

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
        persist_data = []
        for log_ev, freqs in self.counts.items():
            # Skip last count as the time window may not be complete yet and count thus too low
            persist_data.append((log_ev, freqs[:-1]))
        PersistenceUtil.store_json(self.persistence_file_name, persist_data)
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
                "'%s' processed %d out of %d log atoms successfully in %d time windows in the last 60"
                " minutes.", component_name, self.log_success, self.log_total, self.log_windows)
        elif AminerConfig.STAT_LEVEL == 2:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully in %d time windows in the last 60"
                " minutes.", component_name, self.log_success, self.log_total, self.log_windows)
        self.log_success = 0
        self.log_total = 0
        self.log_windows = 0
