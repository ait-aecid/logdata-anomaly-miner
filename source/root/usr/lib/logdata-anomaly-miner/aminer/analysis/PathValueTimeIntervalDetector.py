"""This module defines a detector for variable type.

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
from time import strftime, gmtime

from aminer import AminerConfig
from aminer.AminerConfig import CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX
from aminer.AnalysisChild import AnalysisContext
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface
from aminer.util import PersistenceUtil


class PathValueTimeIntervalDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """
    This class tests each variable of the event_types for the implemented variable types.
    This module needs to run after the EventTypeDetector is initialized
    """

    def __init__(self, aminer_config, anomaly_event_handlers, persistence_id='Default', path_list=None, allow_missing_values_flag=True,
                 ignore_list=None, constraint_list=None, target_path_list=None, output_log_line=True, auto_include_flag=False,
                 max_time_diff=360, num_reduce_time_list=10):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param target_path_list the list of values to extract from each match to create the value combination to be checked.
        @param allow_missing_values_flag when set to True, the detector will also use matches, where one of the pathes from target_path_list
        does not refer to an existing parsed data object.
        @param auto_include_flag when set to True, this detector will report a new time only the first time before including it
        in the known values set automatically.
        """
        self.next_persist_time = None
        self.anomaly_event_handlers = anomaly_event_handlers
        self.auto_include_flag = auto_include_flag
        self.allow_missing_values_flag = allow_missing_values_flag
        self.aminer_config = aminer_config
        self.output_log_line = output_log_line
        self.path_list = path_list
        self.ignore_list = ignore_list
        if self.ignore_list is None:
            self.ignore_list = []
        self.constraint_list = constraint_list
        if self.constraint_list is None:
            self.constraint_list = []
        self.target_path_list = target_path_list
        if self.target_path_list is None:
            self.target_path_list = []

        # Maximal time difference in seconds for new times.
        # If the distance of the new time to all previous times is greater than max_time_diff the new time is considdered an anomaly.
        self.max_time_diff = max_time_diff
        # Number of new time entries appended to the time list, before the list is being reduced.
        self.num_reduce_time_list = num_reduce_time_list

        # Keys: Tuple of values of the paths of target_path_list, Entries: List of all appeared times to the tuple.
        self.appeared_time_list = {}
        # Keys: Tuple of values of the paths of target_path_list, Entries: Counter of appended times to the time list since last rediction.
        self.counter_reduce_time_intervals = {}

        # Loads the persistence
        self.persistence_id = persistence_id
        self.persistence_file_name = AminerConfig.build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)

        # Imports the persistence
        self.load_persistence_data()

    def receive_atom(self, log_atom):
        """
        Receive an parsed atom and the information about the parser match. Initializes Variables for new eventTypes.
        @param log_atom the parsed log atom
        @return True if this handler was really able to handle and process the match.
        """
        match_dict = log_atom.parser_match.get_match_dictionary()
        # Skip paths from ignore_list.
        for ignore_path in self.ignore_list:
            if ignore_path in match_dict.keys():
                return False

        if self.path_list is None or len(self.path_list) == 0:
            # Event is defined by the full path of log atom.
            constraint_path_flag = False
            for constraint_path in self.constraint_list:
                if match_dict.get(constraint_path) is not None:
                    constraint_path_flag = True
                    break
            if not constraint_path_flag and self.constraint_list != []:
                return False

        # Save the values of the target paths in match_value_list and build a tuple of them
        match_value_list = []
        for target_path in self.target_path_list:
            match_element = match_dict.get(target_path, None)
            if match_element is None:
                if not self.allow_missing_values_flag:
                    return False
                match_value_list.append(None)
            else:
                match_value_list.append(match_element.match_object)
        match_value_tuple = tuple(match_value_list)

        # Check if the combination of values and prints an message if it is new.
        if match_value_tuple not in self.appeared_time_list:
            msg = 'New observed combination: ['
            for match_value in match_value_tuple:
                msg += str(repr(match_value)) + ', '
            msg = msg[:-2] + ']'
            self.print(msg, log_atom=log_atom, affected_path=self.target_path_list)
            self.appeared_time_list[match_value_tuple] = [log_atom.atom_time % 86400]
            self.counter_reduce_time_intervals[match_value_tuple] = 0
        else:
            # Checks if the time has already been observed
            if log_atom.atom_time % 86400 not in self.appeared_time_list[match_value_tuple]:
                # Check and prints an message if the new time is out of range of the observed times
                if all((abs(log_atom.atom_time % 86400 - time) > self.max_time_diff) and
                       (abs(log_atom.atom_time % 86400 - time) < 86400 - self.max_time_diff)
                        for time in self.appeared_time_list[match_value_tuple]):
                    msg = 'New time (%s) out of range of previously observed times (%s) detected in the combination: [' % (strftime(
                            '%H:%M:%S', gmtime(log_atom.atom_time)), [
                            strftime('%H:%M:%S', gmtime(time)) for time in self.appeared_time_list[match_value_tuple]])
                    for match_value in match_value_tuple:
                        msg += str(repr(match_value)) + ', '
                    msg = msg[:-2] + ']'
                    self.print(msg, log_atom=log_atom, affected_path=self.target_path_list)

                    if not self.auto_include_flag:
                        return True

                # Add the new time to the time list and reduces the time list after num_reduce_time_list of times have been appended
                self.insert_and_reduce_time_intervals(match_value_tuple, log_atom.atom_time % 86400)

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
        if self.counter_reduce_time_intervals[match_value_tuple] == self.num_reduce_time_list:
            # Reset the counter
            self.counter_reduce_time_intervals[match_value_tuple] = 0
            # Check every entry if it enlarges the time intervals, and remove it, if not.
            last_accepted_time = self.appeared_time_list[match_value_tuple][0] + 86400
            for index in range(len(self.appeared_time_list[match_value_tuple])-1, 0, -1):
                if last_accepted_time - self.appeared_time_list[match_value_tuple][index-1] < 2 * self.max_time_diff:
                    del self.appeared_time_list[match_value_tuple][index]
                else:
                    last_accepted_time = self.appeared_time_list[match_value_tuple][index]

            # Checks the last and first two time of the time list, and removes the obsolete entries
            if (len(self.appeared_time_list[match_value_tuple]) >= 4) and (
                    86400 + self.appeared_time_list[match_value_tuple][1] - self.appeared_time_list[match_value_tuple][-2] <
                    2 * self.max_time_diff):
                self.appeared_time_list[match_value_tuple] = self.appeared_time_list[match_value_tuple][1:len(self.appeared_time_list[
                        match_value_tuple])-1]
            elif 86400 + self.appeared_time_list[match_value_tuple][0] - self.appeared_time_list[match_value_tuple][-2] <\
                    2 * self.max_time_diff:
                self.appeared_time_list[match_value_tuple] = self.appeared_time_list[match_value_tuple][:len(self.appeared_time_list[
                        match_value_tuple])-1]
            elif 86400 + self.appeared_time_list[match_value_tuple][1] - self.appeared_time_list[match_value_tuple][-1] <\
                    2 * self.max_time_diff:
                self.appeared_time_list[match_value_tuple] = self.appeared_time_list[match_value_tuple][1:]

    def get_time_trigger_class(self):  # skipcq: PYL-R0201
        """Get the trigger class this component can be registered for. This detector only needs persisteny triggers in real time."""
        return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def do_timer(self, trigger_time):
        """Check if current ruleset should be persisted."""
        if self.next_persist_time is None:
            return self.aminer_config.config_properties.get(AminerConfig.KEY_PERSISTENCE_PERIOD, AminerConfig.DEFAULT_PERSISTENCE_PERIOD)

        delta = self.next_persist_time - trigger_time
        if delta < 0:
            self.do_persist()
            delta = self.aminer_config.config_properties.get(AminerConfig.KEY_PERSISTENCE_PERIOD, AminerConfig.DEFAULT_PERSISTENCE_PERIOD)
        return delta

    def do_persist(self):
        """Immediately write persistence data to storage."""
        persist_data = [[], []]
        for match_value_tuple, time_list in self.appeared_time_list.items():
            persist_data[0].append((match_value_tuple, time_list))
        for match_value_tuple, counter in self.counter_reduce_time_intervals.items():
            persist_data[1].append((match_value_tuple, counter))
        PersistenceUtil.store_json(self.persistence_file_name, persist_data)
        self.next_persist_time = None
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

    def print(self, message, log_atom, affected_path):
        """Print the message."""
        if isinstance(affected_path, str):
            affected_path = [affected_path]

        original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
        if self.output_log_line:
            tmp_str = ''
            for x in list(log_atom.parser_match.get_match_dictionary().keys()):
                tmp_str += '  ' + x + os.linesep
            tmp_str = tmp_str.lstrip('  ')
            sorted_log_lines = [tmp_str + original_log_line_prefix + log_atom.raw_data.decode()]
            analysis_component = {'AffectedLogAtomPaths': list(log_atom.parser_match.get_match_dictionary().keys())}
        else:
            tmp_str = ''
            for x in affected_path:
                tmp_str += '  ' + x + os.linesep
            tmp_str = tmp_str.lstrip('  ')
            sorted_log_lines = [tmp_str + log_atom.raw_data.decode()]
            analysis_component = {'AffectedLogAtomPaths': affected_path}

        event_data = {'AnalysisComponent': analysis_component}
        for listener in self.anomaly_event_handlers:
            listener.receive_event('Analysis.%s' % self.__class__.__name__, message, sorted_log_lines, event_data, log_atom, self)
