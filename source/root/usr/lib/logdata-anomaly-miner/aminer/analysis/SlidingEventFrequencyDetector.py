"""This module defines a detector for event and value frequency exceedances
with a sliding window approach.

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
from collections import deque

from aminer.AminerConfig import STAT_LOG_NAME, CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX, DEBUG_LOG_NAME
from aminer import AminerConfig
from aminer.input.InputInterfaces import AtomHandlerInterface


class SlidingEventFrequencyDetector(AtomHandlerInterface):
    """This class creates events when event or value frequencies exceed the set
    limit."""

    def __init__(self, aminer_config, anomaly_event_handlers, set_upper_limit, target_path_list=None, scoring_path_list=None,
                 window_size=600, local_maximum_threshold=0.2, persistence_id="Default", learn_mode=False, output_logline=True,
                 ignore_list=None, constraint_list=None, stop_learning_time=None, stop_learning_no_anomaly_time=None,
                 log_resource_ignore_list=None):
        """Initialize the detector.

        @param aminer_config configuration from analysis_context.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that values are analyzed by their combined
               occurrences. When no paths are specified, the events given by the full path list are analyzed.
        @param scoring_path_list parser paths of values to be analyzed by following event handlers like the ScoringEventHandler.
               Multiple paths mean that values are analyzed by their combined occurrences.
        @param window_size the length of the time window for counting in seconds.
        @param set_upper_limit sets the upper limit of the frequency test to the specified value.
        @param local_maximum_threshold sets the threshold for the detection of local maxima in the frequency analysis.
               A local maximum occurs if the last maximum of the anomaly is higher than local_maximum_threshold times the upper limit.
        @param persistence_id name of persistence document.
        @param learn_mode specifies whether new frequency measurements override ground truth frequencies.
        @param output_logline specifies whether the full parsed log atom should be provided in the output.
        @param ignore_list list of paths that are not considered for analysis, i.e., events that contain one of these paths are omitted.
               The default value is [] as None is not iterable.
        @param constraint_list list of paths that have to be present in the log atom to be analyzed.
        """
        # Avoid "defined outside init" issue
        self.learn_mode, self.stop_learning_timestamp, self.next_persist_time, self.log_success, self.log_total = [None]*5
        self.stop_learning_timestamp_initialized = None
        super().__init__(
            mutable_default_args=["target_path_list", "scoring_path_list", "ignore_list", "constraint_list", "log_resource_ignore_list"],
            aminer_config=aminer_config, window_size=window_size, anomaly_event_handlers=anomaly_event_handlers,
            target_path_list=target_path_list, scoring_path_list=scoring_path_list, set_upper_limit=set_upper_limit,
            local_maximum_threshold=local_maximum_threshold, persistence_id=persistence_id, learn_mode=learn_mode,
            output_logline=output_logline, ignore_list=ignore_list, constraint_list=constraint_list, stop_learning_time=stop_learning_time,
            stop_learning_no_anomaly_time=stop_learning_no_anomaly_time, log_resource_ignore_list=log_resource_ignore_list
        )
        if not self.set_upper_limit:
            msg = "set_upper_limit must not be None."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        self.counts = {}
        self.scoring_value_list = {}
        self.max_frequency = {}
        self.max_frequency_time = {}
        self.max_frequency_log_atom = {}
        self.ranges = {}
        self.exceeded_frequency_range = {}
        self.exceeded_frequency_range_time = {}

    def receive_atom(self, log_atom):
        """Receive a log atom from a source."""
        for source in self.log_resource_ignore_list:
            if log_atom.source.resource_name == source:
                return False
        if not self.stop_learning_timestamp_initialized:
            self.stop_learning_timestamp_initialized = True
            if self.stop_learning_timestamp is not None:
                self.stop_learning_timestamp = log_atom.atom_time + self.stop_learning_timestamp
            elif self.stop_learning_no_anomaly_time is not None:
                self.stop_learning_timestamp = log_atom.atom_time + self.stop_learning_no_anomaly_time

        if self.learn_mode is True and self.stop_learning_timestamp is not None and self.stop_learning_timestamp < log_atom.atom_time:
            logging.getLogger(DEBUG_LOG_NAME).info("Stopping learning in the " + str(self.__class__.__name__) + ".")
            self.learn_mode = False

        parser_match = log_atom.parser_match
        self.log_total += 1

        # Skip paths from ignore list.
        for ignore_path in self.ignore_list:
            if ignore_path in parser_match.get_match_dictionary().keys():
                return False

        # Get the log event and save it in log_event
        if self.target_path_list is None or len(self.target_path_list) == 0:
            # Event is defined by the full path of log atom.
            constraint_path_flag = False
            for constraint_path in self.constraint_list:
                if parser_match.get_match_dictionary().get(constraint_path) is not None:
                    constraint_path_flag = True
                    break
            if not constraint_path_flag and self.constraint_list != []:
                return False
            log_event = tuple(parser_match.get_match_dictionary().keys())
        else:
            # Event is defined by value combos in target_path_list
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
                return False
            log_event = tuple(values)

        # Initialize the needed variables at first event occurrence
        if log_event not in self.counts:
            # Initialize counts, max_frequency, max_frequency_time exceeded_frequency_range and self.exceeded_frequency_range_time
            self.counts[log_event] = deque()
            self.max_frequency[log_event] = 0
            self.max_frequency_time[log_event] = 0
            self.max_frequency_log_atom[log_event] = None
            self.exceeded_frequency_range[log_event] = False
            self.exceeded_frequency_range_time[log_event] = 0
            # Initialize the list for the scoring output if scoring_path_list is set
            if len(self.scoring_path_list) > 0:
                self.scoring_value_list[log_event] = deque()

        # Append current time to the counts list
        self.counts[log_event].append(log_atom.atom_time)

        # Get the id list if the scoring_path_list is set and save it for the anomaly message
        if len(self.scoring_path_list) > 0:
            for scoring_path in self.scoring_path_list:
                scoring_match = log_atom.parser_match.get_match_dictionary().get(scoring_path)
                if scoring_match is not None:
                    # Get the value of the current path
                    if isinstance(scoring_match.match_object, bytes):
                        scoring_value = scoring_match.match_object.decode(AminerConfig.ENCODING)
                    else:
                        scoring_value = scoring_match.match_object
                    # Save the value in the list
                    if log_event in self.counts:
                        self.scoring_value_list[log_event].append(scoring_value)
                    else:
                        self.scoring_value_list[log_event] = [scoring_value]

        # Get current frequency
        current_frequency = self.get_current_frequency(log_atom, log_event)

        # Save the current frequency and time if it exceeded the max_frequency
        if current_frequency >= self.set_upper_limit and current_frequency >= self.max_frequency[log_event]:
            self.max_frequency[log_event] = current_frequency
            self.max_frequency_time[log_event] = log_atom.atom_time
            self.max_frequency_log_atom[log_event] = log_atom
            # Reset counter
            self.reset_counter(log_atom, log_event)

        # Check if the frequency exceeded the upper limit for the first time
        if not self.exceeded_frequency_range[log_event] and current_frequency > self.set_upper_limit:
            # Print anomaly message if the last exceeding anomaly lies more than one time window in the past.
            if self.exceeded_frequency_range_time[log_event] + self.window_size < log_atom.atom_time:
                self.print(log_event, current_frequency, first_exceeded_threshold=True)
                self.exceeded_frequency_range_time[log_event] = log_atom.atom_time
            # Reset exceeded_frequency_range
            self.exceeded_frequency_range[log_event] = True
        # Check if the previous max_frequency is a local maximum
        # A local maximum is assumed if it lies one time window in the past, the frequency returned into the interval, or
        # if the maximum of the anomaly is higher than local_maximum_threshold times the upper limit
        elif self.exceeded_frequency_range[log_event] and (
                self.max_frequency_time[log_event] + self.window_size < log_atom.atom_time or
                current_frequency <= self.set_upper_limit or
                current_frequency < self.max_frequency[log_event] - self.local_maximum_threshold * self.set_upper_limit):
            # Print anomaly message
            self.print(log_event, self.max_frequency[log_event], first_exceeded_threshold=False)

            # Reset max frequency and counter
            self.max_frequency[log_event] = 0
            self.max_frequency_time[log_event] = 0
            self.max_frequency_log_atom[log_event] = None
            self.reset_counter(log_atom, log_event)

            # Reset variable exceeded_frequency_range if the current frequency is lower or equal to the upper limit
            if current_frequency <= self.set_upper_limit:
                self.exceeded_frequency_range[log_event] = False
        return True

    def print(self, log_event, frequency, first_exceeded_threshold=False):
        """Sends an event to the listeners.

        The event can be the first exceeding of the limits or a local
        maximum
        """
        try:
            data = self.max_frequency_log_atom[log_event].raw_data.decode(AminerConfig.ENCODING)
        except UnicodeError:
            data = repr(self.max_frequency_log_atom[log_event].raw_data)
        if self.output_logline:
            original_log_line_prefix = self.aminer_config.config_properties.get(
                CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
            sorted_log_lines = [self.max_frequency_log_atom[log_event].parser_match.match_element.annotate_match("") + os.linesep +
                                original_log_line_prefix + data]
        else:
            sorted_log_lines = [data]
        analysis_component = {"AffectedLogAtomPaths": self.target_path_list, "AffectedLogAtomValues": list(log_event)}
        frequency_info = {"ExpectedLogAtomValuesFrequencyRange": [0, self.set_upper_limit],
                          "LogAtomValuesFrequency": frequency,
                          "WindowSize": self.window_size
                          }
        if not first_exceeded_threshold:
            # Calculate the confidence value
            frequency_info["Confidence"] = 1 - self.set_upper_limit / frequency
            # Local maximum timestamp
            frequency_info["Local_maximum_timestamp"] = self.max_frequency_time[log_event]
            # In case that scoring_path_list is set, give their values to the event handlers for further analysis.
            if len(self.scoring_path_list) > 0:
                frequency_info["IdValues"] = list(self.scoring_value_list[log_event])[:self.max_frequency[log_event]]

        event_data = {"AnalysisComponent": analysis_component, "FrequencyData": frequency_info}
        if first_exceeded_threshold:
            message = "Frequency exceeds range for the first time"
        else:
            message = "Frequency anomaly detected"

        for listener in self.anomaly_event_handlers:
            listener.receive_event(f"Analysis.{self.__class__.__name__}", message, sorted_log_lines, event_data,
                                   self.max_frequency_log_atom[log_event], self)

    def log_statistics(self, component_name):
        """Log statistics of an AtomHandler.

        Override this method for more sophisticated statistics output of the AtomHandler.
        @param component_name the name of the component which is printed in the log line.
        """
        if AminerConfig.STAT_LEVEL == 1:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %s out of %s log atoms successfully in the last 60 minutes.", component_name, self.log_success,
                self.log_total)
        elif AminerConfig.STAT_LEVEL == 2:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %s out of %s log atoms successfully in the last 60 minutes.", component_name, self.log_success,
                self.log_total)
        self.log_success = 0
        self.log_total = 0

    def reset_counter(self, log_atom, log_event):
        """Remove any times from counts and scoring_value_list that fell out of
        the time window."""
        while len(self.counts[log_event]) > 0 and self.counts[log_event][0] < log_atom.atom_time - self.window_size:
            self.counts[log_event].popleft()
            if len(self.scoring_path_list) > 0:
                self.scoring_value_list[log_event].popleft()

    def get_current_frequency(self, log_atom, log_event):
        """Return current frequency of the current log event."""
        return len([None for timestamp in self.counts[log_event] if timestamp >= log_atom.atom_time - self.window_size])

    def get_weight_analysis_field_path(self):
        """Return the path to the list in the output of the detector which is
        weighted by the ScoringEventHandler."""
        if self.scoring_path_list:
            return ["FrequencyData", "IdValues"]
        return []

    def get_weight_output_field_path(self):
        """Return the path where the ScoringEventHandler adds the scorings in
        the output of the detector."""
        if self.scoring_path_list:
            return ["FrequencyData", "Scoring"]
        return []
