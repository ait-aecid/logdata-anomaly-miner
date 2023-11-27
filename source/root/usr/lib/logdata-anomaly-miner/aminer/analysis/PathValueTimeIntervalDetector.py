"""
This module defines a detector for time intervals of the appearance of log lines.

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

from aminer import AminerConfig
from aminer.AminerConfig import DEBUG_LOG_NAME, KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD, CONFIG_KEY_LOG_LINE_PREFIX,\
    DEFAULT_LOG_LINE_PREFIX
from aminer.AnalysisChild import AnalysisContext
from aminer.input.InputInterfaces import AtomHandlerInterface, PersistableComponentInterface
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface
from aminer.util import PersistenceUtil


class PathValueTimeIntervalDetector(AtomHandlerInterface, TimeTriggeredComponentInterface, PersistableComponentInterface):
    """
    This class analyzes the time intervals of the appearance of log_atoms.
    The considered time intervals depend on the combination of values in the target_paths of target_path_list.
    """

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, anomaly_event_handlers, target_path_list, persistence_id="Default",
                 allow_missing_values_flag=True, ignore_list=None, output_logline=True, learn_mode=False, time_period_length=86400,
                 max_time_diff=360, num_reduce_time_list=10, stop_learning_time=None, stop_learning_no_anomaly_time=None,
                 log_resource_ignore_list=None):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param persistence_id name of persistence file.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that values are analyzed by their combined
        occurrences. When no paths are specified, the events given by the full path list are analyzed.
        @param allow_missing_values_flag when set to True, the detector will also use matches, where one of the pathes from paths
               does not refer to an existing parsed data object.
        @param ignore_list list of paths that are not considered for correlation, i.e., events that contain one of these paths are
               omitted. The default value is [] as None is not iterable.
        @param output_logline specifies whether the full parsed log atom should be provided in the output.
        @param learn_mode specifies whether new frequency measurements override ground truth frequencies.
        @param time_period_length length of the time window for which the appearances of log lines are identified with each other.
               Value of 86400 specifies a day and 604800 a week.
        @param max_time_diff maximal time difference in seconds for new times. If the difference of the new time to all previous times is
               greater than max_time_diff the new time is considered an anomaly.
        @param num_reduce_time_list number of new time entries appended to the time list, before the list is being reduced.
        @param stop_learning_time switch the learn_mode to False after the time.
        @param stop_learning_no_anomaly_time switch the learn_mode to False after no anomaly was detected for that time.
        """
        # avoid "defined outside init" issue
        self.learn_mode, self.stop_learning_timestamp, self.next_persist_time, self.log_success, self.log_total = [None]*5
        super().__init__(
            mutable_default_args=["ignore_list", "log_resource_ignore_list"], aminer_config=aminer_config,
            anomaly_event_handlers=anomaly_event_handlers, persistence_id=persistence_id, target_path_list=target_path_list,
            allow_missing_values_flag=allow_missing_values_flag, ignore_list=ignore_list, output_logline=output_logline,
            learn_mode=learn_mode, time_period_length=time_period_length, max_time_diff=max_time_diff,
            num_reduce_time_list=num_reduce_time_list, stop_learning_time=stop_learning_time,
            stop_learning_no_anomaly_time=stop_learning_no_anomaly_time, log_resource_ignore_list=log_resource_ignore_list
        )
        if not self.target_path_list:
            msg = "target_path_list must not be empty or None."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)

        # Keys: Tuple of values of the paths of target_path_list, Entries: List of all appeared times to the tuple.
        self.appeared_time_list = {}
        # Keys: Tuple of values of the paths of target_path_list, Entries: Counter of appended times to the time list since last reduction.
        self.counter_reduce_time_intervals = {}

        # Loads the persistence
        self.persistence_id = persistence_id
        self.persistence_file_name = AminerConfig.build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)

        # Imports the persistence
        self.load_persistence_data()

    def receive_atom(self, log_atom):
        """
        Analyze if the time of the log_atom appeared in the time interval of a previously appeared times.
        The considered time intervals originate of events with the same combination of values in the target_paths of target_path_list.
        @param log_atom the parsed log atom
        @return True if this handler was really able to handle and process the match.
        """
        for source in self.log_resource_ignore_list:
            if log_atom.source.resource_name.decode() == source:
                return False
        if log_atom.atom_time is None:
            return False
        if self.learn_mode is True and self.stop_learning_timestamp is not None and \
                self.stop_learning_timestamp < log_atom.atom_time:
            logging.getLogger(DEBUG_LOG_NAME).info("Stopping learning in the %s.", self.__class__.__name__)
            self.learn_mode = False

        match_dict = log_atom.parser_match.get_match_dictionary()
        # Skip paths from ignore_list.
        for ignore_path in self.ignore_list:
            if ignore_path in match_dict.keys():
                return False

        # Get current index from combination of values of paths of target_path_list
        id_tuple = ()
        for id_path in self.target_path_list:
            id_match = log_atom.parser_match.get_match_dictionary().get(id_path)
            if id_match is None:
                if self.allow_missing_values_flag is True:
                    # Insert placeholder for id_path that is not available
                    id_tuple += ("",)
                else:
                    # Omit log atom if one of the id paths is not found.
                    return False
            else:
                if isinstance(id_match.match_object, bytes):
                    id_tuple += (id_match.match_object.decode(AminerConfig.ENCODING),)
                else:
                    id_tuple += (id_match.match_object,)

        # Print message if combination of values is new
        if id_tuple not in self.appeared_time_list:
            additional_information = {"AffectedLogAtomValues": [str(repr(val))[2:-1] for val in id_tuple],
                                      "NewTime": log_atom.atom_time % self.time_period_length}

            msg = f"First time ({int(log_atom.atom_time % self.time_period_length)}) detected for ["
            for match_value in id_tuple:
                msg += str(match_value) + ", "
            msg = msg[:-2] + "]"
            self.print(msg, log_atom=log_atom, affected_path=self.target_path_list, additional_information=additional_information)
            self.appeared_time_list[id_tuple] = [log_atom.atom_time % self.time_period_length]
            self.counter_reduce_time_intervals[id_tuple] = 0
            if self.stop_learning_timestamp is not None and self.stop_learning_no_anomaly_time is not None:
                self.stop_learning_timestamp = max(
                    self.stop_learning_timestamp, log_atom.atom_time + self.stop_learning_no_anomaly_time)
        else:
            # Checks if the time has already been observed
            if log_atom.atom_time % self.time_period_length not in self.appeared_time_list[id_tuple]:
                # Check and print a message if the new time is out of range of the observed times
                # The second query is needed when time intervals exceed over 0/self.time_period_length
                if all((abs(log_atom.atom_time % self.time_period_length - time) > self.max_time_diff) and
                       (abs(log_atom.atom_time % self.time_period_length - time) < self.time_period_length - self.max_time_diff)
                        for time in self.appeared_time_list[id_tuple]):
                    additional_information = {"AffectedLogAtomValues": [str(repr(val))[2:-1] for val in id_tuple],
                                              "PreviousAppearedTimes": [float(val) for val in self.appeared_time_list[id_tuple]],
                                              "NewTime": log_atom.atom_time % self.time_period_length}

                    msg = f"New time ({int(log_atom.atom_time % self.time_period_length)}) out of range of previously observed times " \
                          f"{[int(x) for x in self.appeared_time_list[id_tuple]]} detected for ["
                    for match_value in id_tuple:
                        msg += str(match_value) + ", "
                    msg = msg[:-2] + "]"
                    self.print(msg, log_atom=log_atom, affected_path=self.target_path_list, additional_information=additional_information)
                    if not self.learn_mode:
                        return True
                    if self.stop_learning_timestamp is not None and self.stop_learning_no_anomaly_time is not None:
                        self.stop_learning_timestamp = max(
                            self.stop_learning_timestamp, log_atom.atom_time + self.stop_learning_no_anomaly_time)
                # Add the new time to the time list and reduces the time list after num_reduce_time_list of times have been appended
                self.insert_and_reduce_time_intervals(id_tuple, log_atom.atom_time % self.time_period_length)
        return True

    def insert_and_reduce_time_intervals(self, id_tuple, new_time):
        """Add the new time to the time list and reduce the time list after num_reduce_time_list of times have been appended."""
        # Increase the counter of new times since last reduction
        self.counter_reduce_time_intervals[id_tuple] += 1

        # Get the index in which the new time is inserted
        if new_time > self.appeared_time_list[id_tuple][-1]:
            time_index = len(self.appeared_time_list[id_tuple])
        else:
            # skipcq: PTC-W0063
            time_index = next(index for index, time in enumerate(self.appeared_time_list[id_tuple]) if time > new_time)

        # Insert the new time
        self.appeared_time_list[id_tuple] = self.appeared_time_list[id_tuple][:time_index] + [new_time] +\
            self.appeared_time_list[id_tuple][time_index:]

        # Reduce the time intervals, by removing the obsolete entries
        if self.counter_reduce_time_intervals[id_tuple] >= self.num_reduce_time_list:
            # Reset the counter
            self.counter_reduce_time_intervals[id_tuple] = 0
            # Check every entry if it enlarges the time intervals, and remove it, if not.
            last_accepted_time = self.appeared_time_list[id_tuple][0] + self.time_period_length
            for index in range(len(self.appeared_time_list[id_tuple])-1, 0, -1):
                if last_accepted_time - self.appeared_time_list[id_tuple][index-1] < 2 * self.max_time_diff:
                    del self.appeared_time_list[id_tuple][index]
                else:
                    last_accepted_time = self.appeared_time_list[id_tuple][index]

            # Checks the last and first two time of the time list, and removes the obsolete entries
            if (len(self.appeared_time_list[id_tuple]) >= 4) and (
                    self.time_period_length + self.appeared_time_list[id_tuple][1] -
                    self.appeared_time_list[id_tuple][-2] < 2 * self.max_time_diff):
                self.appeared_time_list[id_tuple] = self.appeared_time_list[id_tuple][1:len(self.appeared_time_list[
                        id_tuple])-1]
            elif self.time_period_length + self.appeared_time_list[id_tuple][0] - self.appeared_time_list[id_tuple][-2] <\
                    2 * self.max_time_diff:
                self.appeared_time_list[id_tuple] = self.appeared_time_list[id_tuple][:len(self.appeared_time_list[
                        id_tuple])-1]
            elif self.time_period_length + self.appeared_time_list[id_tuple][1] - self.appeared_time_list[id_tuple][-1] <\
                    2 * self.max_time_diff:
                self.appeared_time_list[id_tuple] = self.appeared_time_list[id_tuple][1:]

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
        persist_data = [[], []]
        for id_tuple, time_list in self.appeared_time_list.items():
            persist_data[0].append((id_tuple, time_list))
        for id_tuple, counter in self.counter_reduce_time_intervals.items():
            persist_data[1].append((id_tuple, counter))
        PersistenceUtil.store_json(self.persistence_file_name, persist_data)
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug("%s persisted data.", self.__class__.__name__)

    def load_persistence_data(self):
        """Load the persistence data from storage."""
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        if persistence_data is not None:
            for id_tuple, time_list in persistence_data[0]:
                self.appeared_time_list[tuple(id_tuple)] = time_list
            for id_tuple, counter in persistence_data[1]:
                self.counter_reduce_time_intervals[tuple(id_tuple)] = counter
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug("%s loaded persistence data.", self.__class__.__name__)

    def print_persistence_event(self, event_type, event_data):
        """
        Print the persistence of component_name. Event_data specifies what information is output.
        @return a message with information about the persistence.
        @throws Exception when the output for the event_data was not possible.
        """
        if event_type != f"Analysis.{self.__class__.__name__}":
            msg = "Event not from this source"
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)

        # Query if event_data has one of the stated formats
        if not (isinstance(event_data, list) and len(event_data) <= 1 and ((len(event_data) == 1 and (
                    isinstance(event_data[0], list) and len(event_data[0]) in [0, len(self.target_path_list)]) and
                    all(isinstance(value, str) for value in event_data[0])) or len(event_data) == 0)):
            msg = "Event_data has the wrong format. " \
                "The supported formats are [] and [path_value_list], where the path value list is a list of strings with the same " \
                "length as the defined paths in the config."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)

        # Convert path value lists to tuples
        for i in range(len(event_data)):
            event_data[i] = tuple(event_data[i])

        if len(event_data) == 0:
            # Print the set of all appeared path values if no event_data is given
            values_set = set(self.appeared_time_list.keys())
            values_list = list(values_set)
            values_list.sort()

            string = f"Time intervals are tracked for the following path values: {values_list}"
        elif len(event_data) == 1:
            id_tuple = event_data[0]
            # Check if the path value is tracked
            if id_tuple not in self.appeared_time_list:
                return f"Persistence includes no information for {id_tuple}."

            # Calculate the current time intervals
            time_intervals = [[max(0, t - self.max_time_diff), min(self.time_period_length, t + self.max_time_diff)] for t in
                              self.appeared_time_list[id_tuple]]
            # Add time intervals, when the time intervals exceed the time period length or undercuts zero.
            if self.appeared_time_list[id_tuple][-1] + self.max_time_diff > self.time_period_length:
                time_intervals = [[0, self.appeared_time_list[id_tuple][-1] + self.max_time_diff - self.time_period_length]] +\
                    time_intervals
            if self.appeared_time_list[id_tuple][0] - self.max_time_diff < 0:
                time_intervals = time_intervals +\
                    [[self.appeared_time_list[id_tuple][0] - self.max_time_diff + self.time_period_length, self.time_period_length]]

            # Get the indices of the time windows whoch intercept and therefore are merged
            indices = [i for i in range(len(time_intervals) - 1) if time_intervals[i][1] > time_intervals[i + 1][0]]

            # Merge the time intervals
            for index in reversed(indices):
                time_intervals[index + 1][0] = time_intervals[index][0]
                time_intervals = time_intervals[:index] + time_intervals[index + 1:]

            # Set output string
            string = f"The list of appeared times is {self.appeared_time_list[id_tuple]} and the resulting time intervals are " \
                     f"{time_intervals} for path value {id_tuple}"
        return string

    def add_to_persistence_event(self, event_type, event_data):
        """
        Add or overwrite the information of event_data to the persistence of component_name.
        @return a message with information about the addition to the persistence.
        @throws Exception when the addition of this special event using given event_data was not possible.
        """
        if event_type != f"Analysis.{self.__class__.__name__}":
            msg = "Event not from this source"
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)

        if not isinstance(event_data, list) or len(event_data) != 2 or not isinstance(event_data[0], list) or\
                len(event_data[0]) != len(self.target_path_list) or not all(isinstance(value, str) for value in event_data[0]) or\
                not isinstance(event_data[1], (int, float)):
            msg = "Event_data has the wrong format. " \
                "The supported format is [path_value_list, new_appeared_time], " \
                "where path_value_list is a list of strings with the same length as paths defined in the config."
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)

        id_tuple = tuple(event_data[0])
        new_time = event_data[1]

        msg = ""
        if id_tuple not in self.appeared_time_list:
            # Print message if combination of values is new
            msg = f"First time ({new_time % self.time_period_length}) added for {id_tuple}"
            self.appeared_time_list[id_tuple] = [new_time % self.time_period_length]
            self.counter_reduce_time_intervals[id_tuple] = 0
        else:
            # Print a message if the new time is added to the list of observed times
            msg = f"New time ({new_time % self.time_period_length}) added to the range of previously observed times " \
                  f"{self.appeared_time_list[id_tuple]} for {id_tuple}"
            # Add the new time to the time list and reduces the time list after num_reduce_time_list of times have been appended
            self.insert_and_reduce_time_intervals(id_tuple, new_time % self.time_period_length)
        return msg

    def remove_from_persistence_event(self, event_type, event_data):
        """
        Add or overwrite the information of event_data to the persistence of component_name.
        @return a message with information about the addition to the persistence.
        @throws Exception when the addition of this special event using given event_data was not possible.
        """
        if event_type != f"Analysis.{self.__class__.__name__}":
            msg = "Event not from this source"
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)

        if not isinstance(event_data, list) or len(event_data) != 2 or not isinstance(event_data[0], list) or\
                len(event_data[0]) != len(self.target_path_list) or not all(isinstance(value, str) for value in event_data[0]) or\
                not isinstance(event_data[1], (int, float)):
            msg = "Event_data has the wrong format. " \
                "The supported format is [path_value_list, old_appeared_time], " \
                "where path_value_list is a list of strings with the same length as paths defined in the config."
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)

        id_tuple = tuple(event_data[0])
        new_time = event_data[1]

        if id_tuple not in self.appeared_time_list:
            # Print message if combination of values is new
            msg = f"{id_tuple} has previously not appeared"
        elif not any(abs(new_time - val) < 0.5 for val in self.appeared_time_list[id_tuple]):
            # Print a message if the new time does not appear the list of observed times
            msg = f"Time ({new_time % self.time_period_length}) does not appear in the previously observed times " \
                  f"{self.appeared_time_list[id_tuple]} for {id_tuple}"
        else:
            # Remove the old time from the time list.
            for index in reversed(range(len(self.appeared_time_list[id_tuple]))):
                if abs(new_time - self.appeared_time_list[id_tuple][index]) < 0.5:
                    self.appeared_time_list[id_tuple] = self.appeared_time_list[id_tuple][:index] +\
                            self.appeared_time_list[id_tuple][index + 1:]

            # Print a message if the new time is added to the list of observed times
            msg = f"Time ({new_time % self.time_period_length}) was removed from the range of previously observed times " \
                  f"{self.appeared_time_list[id_tuple]} for {id_tuple}"
        return msg

    def print(self, message, log_atom, affected_path, additional_information=None):
        """Print the message."""
        if isinstance(affected_path, str):
            affected_path = [affected_path]
        if additional_information is None:
            additional_information = {}

        original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
        if self.output_logline:
            tmp_str = ""
            for x in list(log_atom.parser_match.get_match_dictionary().keys()):
                tmp_str += "  " + x + os.linesep
            tmp_str = tmp_str.lstrip("  ")
            sorted_log_lines = [tmp_str + original_log_line_prefix + log_atom.raw_data.decode(AminerConfig.ENCODING)]
            analysis_component = {"AffectedLogAtomPaths": list(log_atom.parser_match.get_match_dictionary().keys())}
        else:
            tmp_str = ""
            for x in affected_path:
                tmp_str += "  " + x + os.linesep
            tmp_str = tmp_str.lstrip("  ")
            sorted_log_lines = [tmp_str + log_atom.raw_data.decode(AminerConfig.ENCODING)]
            analysis_component = {"AffectedLogAtomPaths": affected_path}

        for key, value in additional_information.items():
            analysis_component[key] = value

        event_data = {"AnalysisComponent": analysis_component}
        for listener in self.anomaly_event_handlers:
            listener.receive_event(f"Analysis.{self.__class__.__name__}", message, sorted_log_lines, event_data, log_atom, self)
