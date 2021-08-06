"""
This module defines a detector for minimal times between the appearance of values in one path in respect to values of a second path.

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


class MinimalTimeTransitionDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """
    This class analyzes the minimal times of the appearance of log_atoms.
    The considered time intervals depend on the combination of values in the place_paths of place_path_list.
    """

    def __init__(self, aminer_config, anomaly_event_handlers, persistence_id='Default', auto_include_flag=False, output_log_line=False,
                 place_path_list=None, user_path_list=None, ignore_list=None, value_constraint_list=None,
                 num_log_lines_matrix_reduction=10000):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param persistence_id name of persistency document.
        @param place_path_list parser paths of the analyzed places. Multiple paths mean that values are analyzed by their combined
        occurrences. When no paths are specified, the events given by the full path list are analyzed.
        @param user_path_list parser paths of the analyzed users. Multiple paths mean that values are analyzed by their combined
        occurrences. When no paths are specified, the events given by the full path list are analyzed.
        @param ignore_list list of paths that are not considered for correlation, i.e., events that contain one of these paths are
        omitted. The default value is [] as None is not iterable.
        @param output_log_line specifies whether the full parsed log atom should be provided in the output.
        @param auto_include_flag specifies whether new frequency measurements override ground truth frequencies.
        @param value_constraint_list includes restrictions on the values of the stated paths.
        """

        self.next_persist_time = None
        self.anomaly_event_handlers = anomaly_event_handlers
        self.auto_include_flag = auto_include_flag
        self.aminer_config = aminer_config
        self.output_log_line = output_log_line

        self.value_constraint_list = value_constraint_list
        if self.value_constraint_list is None:
            self.value_constraint_list = []
        self.ignore_list = ignore_list
        if self.ignore_list is None:
            self.ignore_list = []
        self.place_path_list = place_path_list
        if self.place_path_list is None:
            self.place_path_list = []
        self.user_path_list = user_path_list
        if self.user_path_list is None:
            self.user_path_list = []

        self.num_log_lines_matrix_reduction = num_log_lines_matrix_reduction

        # Matrix of the minimal appeared transiton times
        self.last_logged_door = {}
        # Matrix of the minimal appeared transiton times
        self.min_time_matrix = {}

        # Loads the persistence
        self.persistence_id = persistence_id
        self.persistence_file_name = AminerConfig.build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)

        # Imports the persistence
        self.load_persistence_data()

    def receive_atom(self, log_atom):
        """
        Analyze if the time of the last transition is smaller than the previously observed minimum and periodically reduces the values
        of the matrix by using the triange inequation.
        @param log_atom the parsed log atom
        @return True if this handler was really able to handle and process the match.
        """
        match_dict = log_atom.parser_match.get_match_dictionary()
        # Skip paths from ignore_list.
        for ignore_path in self.ignore_list:
            if ignore_path in match_dict.keys():
                return False

        # Save the values of the place paths in match_place_list and build a tuple of them
        match_place_list = []
        for place_path in self.place_path_list:
            match_element = match_dict.get(place_path, None)
            if match_element is None:
                if not self.allow_missing_values_flag:
                    return False
                match_place_list.append(None)
            else:
                match_place_list.append(match_element.match_object)
        match_value_tuple = tuple(match_place_list)

        # Save the values of the user paths in match_user_list and build a tuple of them
        match_user_list = []
        for place_path in self.place_path_list:
            match_element = match_dict.get(place_path, None)
            if match_element is None:
                if not self.allow_missing_values_flag:
                    return False
                match_user_list.append(None)
            else:
                match_user_list.append(match_element.match_object)
        match_value_tuple = tuple(match_user_list)

        # Check if the log lines meet the constrictions
        for constraint in self.value_constraint_list:
            if constraint[0] not in match_dict or str(repr(match_dict[constraint[0]].match_string))[2:-1] not in constraint[1:]:
                return False

        self.print('HERE', log_atom, self.place_path_list)

        return True

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
        print('ToDo')
        persist_data = []
        PersistenceUtil.store_json(self.persistence_file_name, persist_data)
        self.next_persist_time = None
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug('%s persisted data.', self.__class__.__name__)

    def load_persistence_data(self):
        """Load the persistence data from storage."""
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        if persistence_data is not None:
            print('ToDo')
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
            sorted_log_lines = [tmp_str + original_log_line_prefix + log_atom.raw_data.decode(AminerConfig.ENCODING)]
            analysis_component = {'AffectedLogAtomPaths': list(log_atom.parser_match.get_match_dictionary().keys())}
        else:
            tmp_str = ''
            for x in affected_path:
                tmp_str += '  ' + x + os.linesep
            tmp_str = tmp_str.lstrip('  ')
            sorted_log_lines = [tmp_str + log_atom.raw_data.decode(AminerConfig.ENCODING)]
            analysis_component = {'AffectedLogAtomPaths': affected_path}

        event_data = {'AnalysisComponent': analysis_component}
        for listener in self.anomaly_event_handlers:
            listener.receive_event('Analysis.%s' % self.__class__.__name__, message, sorted_log_lines, event_data, log_atom, self)
