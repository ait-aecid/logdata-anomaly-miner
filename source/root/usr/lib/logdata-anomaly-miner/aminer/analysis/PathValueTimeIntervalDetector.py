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
from aminer.AminerConfig import CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX
from aminer.AnalysisChild import AnalysisContext
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface
from aminer.util import PersistenceUtil


class PathValueTimeIntervalDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """
    This class analyzes the time intervals of the appearance of log_atoms.
    The considered time intervals depend on the combination of values in the target_paths of target_path_list.
    """

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, anomaly_event_handlers, persistence_id='Default', target_path_list=None,
                 allow_missing_values_flag=True, ignore_list=None, output_log_line=True, auto_include_flag=False,
                 time_period_length=86400, max_time_diff=360, num_reduce_time_list=10):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param persistence_id name of persistency document.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that values are analyzed by their combined
        occurrences. When no paths are specified, the events given by the full path list are analyzed.
        @param allow_missing_values_flag when set to True, the detector will also use matches, where one of the pathes from target_path_list
        does not refer to an existing parsed data object.
        @param ignore_list list of paths that are not considered for correlation, i.e., events that contain one of these paths are
        omitted. The default value is [] as None is not iterable.
        @param output_log_line specifies whether the full parsed log atom should be provided in the output.
        @param auto_include_flag specifies whether new frequency measurements override ground truth frequencies.
        @param time_period_length length of the time window for which the appearances of log lines are identified with each other.
        Value of 86400 specfies a day and 604800 a week.
        @param max_time_diff maximal time difference in seconds for new times. If the difference of the new time to all previous times is
        greater than max_time_diff the new time is considered an anomaly.
        @param num_reduce_time_list number of new time entries appended to the time list, before the list is being reduced.
        """
        self.next_persist_time = time.time() + self.aminer_config.config_properties.get(KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)
        self.anomaly_event_handlers = anomaly_event_handlers
        self.auto_include_flag = auto_include_flag
        self.allow_missing_values_flag = allow_missing_values_flag
        self.aminer_config = aminer_config
        self.output_log_line = output_log_line
        self.ignore_list = ignore_list
        if self.ignore_list is None:
            self.ignore_list = []
        self.target_path_list = target_path_list
        if self.target_path_list is None:
            self.target_path_list = []
        self.time_period_length = time_period_length
        self.max_time_diff = max_time_diff
        self.num_reduce_time_list = num_reduce_time_list

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
        if log_atom.atom_time is None:
            return False

        match_dict = log_atom.parser_match.get_match_dictionary()
        # Skip paths from ignore_list.
        for ignore_path in self.ignore_list:
            if ignore_path in match_dict.keys():
                return False

        # Save the values of the target paths in match_value_list and build a tuple of them
        match_value_list = []
        for target_path in self.target_path_list:
            match_element = match_dict.get(target_path)
            if match_element is None:
                if not self.allow_missing_values_flag:
                    return False
                match_value_list.append(None)
            else:
                if isinstance(match_element, list):
                    matches = match_element
                else:
                    matches = [match_element]
                for match_element in matches:
                    match_value_list.append(match_element.match_object)
        match_value_tuple = tuple(match_value_list)

        # Print message if combination of values is new
        if match_value_tuple not in self.appeared_time_list:
            additional_information = {'AffectedLogAtomValues': [str(repr(val))[2:-1] for val in match_value_tuple],
                                      'NewTime': log_atom.atom_time % self.time_period_length}

            msg = 'First time (%s) detected for [' % (log_atom.atom_time % self.time_period_length)
            for match_value in match_value_tuple:
                msg += str(repr(match_value))[1:] + ', '
            msg = msg[:-2] + ']'
            self.print(msg, log_atom=log_atom, affected_path=self.target_path_list, additional_information=additional_information)
            self.appeared_time_list[match_value_tuple] = [log_atom.atom_time % self.time_period_length]
            self.counter_reduce_time_intervals[match_value_tuple] = 0
        else:
            # Checks if the time has already been observed
            if log_atom.atom_time % self.time_period_length not in self.appeared_time_list[match_value_tuple]:
                # Check and prints an message if the new time is out of range of the observed times
                # The second query is needed when time intevals exceed over 0/self.time_period_length
                if all((abs(log_atom.atom_time % self.time_period_length - time) > self.max_time_diff) and
                       (abs(log_atom.atom_time % self.time_period_length - time) < self.time_period_length - self.max_time_diff)
                        for time in self.appeared_time_list[match_value_tuple]):
                    additional_information = {'AffectedLogAtomValues': [str(repr(val))[2:-1] for val in match_value_tuple],
                                              'PreviousAppearedTimes': [float(val) for val in self.appeared_time_list[match_value_tuple]],
                                              'NewTime': log_atom.atom_time % self.time_period_length}

                    msg = 'New time (%s) out of range of previously observed times %s detected for [' % (
                            log_atom.atom_time % self.time_period_length, self.appeared_time_list[match_value_tuple])
                    for match_value in match_value_tuple:
                        msg += str(repr(match_value))[1:] + ', '
                    msg = msg[:-2] + ']'
                    self.print(msg, log_atom=log_atom, affected_path=self.target_path_list, additional_information=additional_information)

                    if not self.auto_include_flag:
                        return True

                # Add the new time to the time list and reduces the time list after num_reduce_time_list of times have been appended
                self.insert_and_reduce_time_intervals(match_value_tuple, log_atom.atom_time % self.time_period_length)

        return True

    def insert_and_reduce_time_intervals(self, match_value_tuple, new_time):
        """Add the new time to the time list and reduce the time list after num_reduce_time_list of times have been appended."""
        # Increase the counter of new times since last reduction
        self.counter_reduce_time_intervals[match_value_tuple] += 1

        # Get the index in which the new time is inserted
        if new_time > self.appeared_time_list[match_value_tuple][-1]:
            time_index = len(self.appeared_time_list[match_value_tuple])
        else:
            # skipcq: PTC-W0063
            time_index = next(index for index, time in enumerate(self.appeared_time_list[match_value_tuple]) if time > new_time)

        # Insert the new time
        self.appeared_time_list[match_value_tuple] = self.appeared_time_list[match_value_tuple][:time_index] + [new_time] +\
            self.appeared_time_list[match_value_tuple][time_index:]

        # Reduce the time intervals, by removing the obsolete entries
        if self.counter_reduce_time_intervals[match_value_tuple] >= self.num_reduce_time_list:
            # Reset the counter
            self.counter_reduce_time_intervals[match_value_tuple] = 0
            # Check every entry if it enlarges the time intervals, and remove it, if not.
            last_accepted_time = self.appeared_time_list[match_value_tuple][0] + self.time_period_length
            for index in range(len(self.appeared_time_list[match_value_tuple])-1, 0, -1):
                if last_accepted_time - self.appeared_time_list[match_value_tuple][index-1] < 2 * self.max_time_diff:
                    del self.appeared_time_list[match_value_tuple][index]
                else:
                    last_accepted_time = self.appeared_time_list[match_value_tuple][index]

            # Checks the last and first two time of the time list, and removes the obsolete entries
            if (len(self.appeared_time_list[match_value_tuple]) >= 4) and (
                    self.time_period_length + self.appeared_time_list[match_value_tuple][1] -
                    self.appeared_time_list[match_value_tuple][-2] < 2 * self.max_time_diff):
                self.appeared_time_list[match_value_tuple] = self.appeared_time_list[match_value_tuple][1:len(self.appeared_time_list[
                        match_value_tuple])-1]
            elif self.time_period_length + self.appeared_time_list[match_value_tuple][0] - self.appeared_time_list[match_value_tuple][-2] <\
                    2 * self.max_time_diff:
                self.appeared_time_list[match_value_tuple] = self.appeared_time_list[match_value_tuple][:len(self.appeared_time_list[
                        match_value_tuple])-1]
            elif self.time_period_length + self.appeared_time_list[match_value_tuple][1] - self.appeared_time_list[match_value_tuple][-1] <\
                    2 * self.max_time_diff:
                self.appeared_time_list[match_value_tuple] = self.appeared_time_list[match_value_tuple][1:]

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
        persist_data = [[], []]
        for match_value_tuple, time_list in self.appeared_time_list.items():
            persist_data[0].append((match_value_tuple, time_list))
        for match_value_tuple, counter in self.counter_reduce_time_intervals.items():
            persist_data[1].append((match_value_tuple, counter))
        PersistenceUtil.store_json(self.persistence_file_name, persist_data)
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug('%s persisted data.', self.__class__.__name__)

    def load_persistence_data(self):
        """Load the persistence data from storage."""
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        if persistence_data is not None:
            for match_value_tuple, time_list in persistence_data[0]:
                self.appeared_time_list[tuple(match_value_tuple)] = time_list
            for match_value_tuple, counter in persistence_data[1]:
                self.counter_reduce_time_intervals[tuple(match_value_tuple)] = counter
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug('%s loaded persistence data.', self.__class__.__name__)

    def print(self, message, log_atom, affected_path, additional_information=None):
        """Print the message."""
        if isinstance(affected_path, str):
            affected_path = [affected_path]
        if additional_information is None:
            additional_information = {}

        original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
        if self.output_log_line:
            tmp_str = ''
            for x in list(log_atom.parser_match.get_match_dictionary().keys()):
                tmp_str += '  ' + x + os.linesep
            tmp_str = tmp_str.lstrip('  ')
            sorted_log_lines = [tmp_str + original_log_line_prefix + log_atom.raw_data.decode(AminerConfig.ENCODING)]
            analysis_component = {'AffectedLogAtomPaths': list(log_atom.parser_match.get_match_dictionary().keys())}
        else:
            tmp_str = ''
            for x in affected_path:
                tmp_str += '  ' + x + os.linesep
            tmp_str = tmp_str.lstrip('  ')
            sorted_log_lines = [tmp_str + log_atom.raw_data.decode(AminerConfig.ENCODING)]
            analysis_component = {'AffectedLogAtomPaths': affected_path}

        for key, value in additional_information.items():
            analysis_component[key] = value

        event_data = {'AnalysisComponent': analysis_component}
        for listener in self.anomaly_event_handlers:
            listener.receive_event('Analysis.%s' % self.__class__.__name__, message, sorted_log_lines, event_data, log_atom, self)
