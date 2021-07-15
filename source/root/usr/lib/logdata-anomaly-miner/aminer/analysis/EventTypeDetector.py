"""
This module can assigns every parsed log line a eventtype and can be used for profiling purposes.
It supports the modules VariableTypeDetector and VariableCorrelationDetector.

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
import copy
import logging

from aminer import AminerConfig
from aminer.AminerConfig import build_persistence_file_name, KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD, DEBUG_LOG_NAME
from aminer.AnalysisChild import AnalysisContext
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface
from aminer.util import PersistenceUtil


class EventTypeDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """This class keeps track of the found eventtypes and the values of each variable."""

    def __init__(self, aminer_config, anomaly_event_handlers, persistence_id='Default', path_list=None, id_path_list=None,
                 allow_missing_id=False, allowed_id_tuples=None, min_num_vals=1000, max_num_vals=1500, save_values=True,
                 track_time_for_tsa=False, waiting_time_for_tsa=1000, num_sections_waiting_time_for_tsa=100):
        """Initialize the detector. This will also trigger reading or creation of persistence storage location."""
        self.next_persist_time = time.time() + 600.0
        self.anomaly_event_handlers = anomaly_event_handlers
        # One or more paths that specify the trace of the EventTypeDetector. If the list is not empty the events corresponds to the values
        # in these paths not the event types.
        self.id_path_list = id_path_list
        if self.id_path_list is None:
            self.id_path_list = []
        # Specifies whether log atoms without id path should be omitted (only if id path is set).
        self.allow_missing_id = allow_missing_id
        # List of the allowed id tuples. Log atoms with id tuples not in this list are not analyzed, when this list is not empty.
        if allowed_id_tuples is None:
            self.allowed_id_tuples = []
        else:
            self.allowed_id_tuples = [tuple(tuple_list) for tuple_list in allowed_id_tuples]
        # Number of the values which the list is being reduced to.
        self.min_num_vals = min_num_vals
        # Maximum number of lines in the value list before it is reduced. > min_num_vals.
        self.max_num_vals = max_num_vals
        # If False the values of the Token are not saved for further analysis. Disables self.values, and self.check_variables
        self.save_values = save_values
        # States if the time windows should be tracked for the time series analysis
        self.track_time_for_tsa = track_time_for_tsa
        # Time in seconds, until the time windows are being initialized
        self.waiting_time_for_tsa = waiting_time_for_tsa
        # Number of sections of the initialization window. The length of the input-list of the calculate_time_steps is this number
        self.num_sections_waiting_time_for_tsa = num_sections_waiting_time_for_tsa
        self.aminer_config = aminer_config

        self.num_events = 0
        # List of the longest path of the events
        self.longest_path = []
        # List of the keys corresponding to the events
        self.found_keys = []
        # List of the keys, which take values in the log-line
        self.variable_key_list = []
        # List of the values of the log-lines. If the lenght reaches max_num_vals the list gets reduced to min_num_vals values per variable
        self.values = []
        # Saves the number of lines of the event types
        self.num_eventlines = []
        # Saves the number of total log-lines
        self.total_records = 0
        # List of the modules which follow the event_type_detector. The implemented modules are form the list
        # [variableTypeDetector, variableCorrelationDetector]
        self.following_modules = []
        # List of paths, which variables are being tracked. All other paths will not get tracked. If None all paths are being tracked.
        self.path_list = path_list
        # List of bools, which state if the variables of variable_key_list are updated.
        self.check_variables = []
        # List ot the time trigger. The first list states the times when something should be triggered, the second list states the indices
        # of the eventtyps, or a list of the evnettype, a path and a value which should be counted (-1 for an initialization)
        # the third list states, the length of the time window (-1 for a one time trigger)
        self.etd_time_trigger = [[], [], []]
        # Reference containing the number of lines of the events for the TSA
        self.num_eventlines_tsa_ref = []
        # Index of the eventtype of the current log line
        self.current_index = 0
        # List of the id tuples
        self.id_path_list_tuples = []

        # Loads the persistence
        self.persistence_file_name = build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)
        self.load_persistence_data()

    def receive_atom(self, log_atom):
        """Receives an parsed atom and keeps track of the event types and the values of the variables of them."""
        self.log_total += 1
        # Get the current time
        if self.track_time_for_tsa:
            if log_atom.atom_time is not None:
                current_time = log_atom.atom_time
            else:
                current_time = time.time()

        # Check if TSA should be initialized
        if self.track_time_for_tsa and -1 in self.etd_time_trigger[0] and 'TSAArimaDetector' in [module.__class__.__name__ for module in
                                                                                                 self.following_modules]:
            for i, val in enumerate(self.etd_time_trigger[0]):
                if val == -1:
                    for j in range(self.num_sections_waiting_time_for_tsa-1):
                        self.etd_time_trigger[0].append(current_time + self.waiting_time_for_tsa * (j + 1) / (
                                self.num_sections_waiting_time_for_tsa))
                        self.etd_time_trigger[1].append(-1)
                        self.etd_time_trigger[2].append(-1)

                    self.etd_time_trigger[0][i] = current_time + self.waiting_time_for_tsa
                    break

        # Check if a trigger has been triggered
        if self.track_time_for_tsa and len(self.etd_time_trigger[0]) > 0 and any(current_time >= x for x in self.etd_time_trigger[0]):
            # Get the indices of the triggered events
            indices = [i for i, time_trigger in enumerate(self.etd_time_trigger[0]) if current_time >= time_trigger]

            # Execute the triggered functions of the TSA
            for i in range(len(indices)-1, -1, -1):
                # Checks if trigger is part of the initalisation
                if self.etd_time_trigger[1][indices[i]] == -1 and self.etd_time_trigger[2][indices[i]] == -1:

                    # Save the number of occured eventtypes for the initialization of the TSA
                    if self.num_eventlines_tsa_ref == [] or len(
                            self.num_eventlines_tsa_ref[0]) < self.num_sections_waiting_time_for_tsa-1:

                        # Initialize the lists of self.num_eventlines_tsa_ref if not already initialized
                        if not self.num_eventlines_tsa_ref:
                            self.num_eventlines_tsa_ref = [[num] for num in self.num_eventlines]
                        else:
                            # Expand the lists of self.num_eventlines_tsa_ref
                            for j in range(len(self.num_eventlines_tsa_ref), len(self.num_eventlines)):  # skipcq: PTC-W0060
                                self.num_eventlines_tsa_ref.append([0]*len(self.num_eventlines_tsa_ref[0]))
                            # Add the current number of eventlines
                            for j, val in enumerate(self.num_eventlines):
                                self.num_eventlines_tsa_ref[j].append(val-sum(self.num_eventlines_tsa_ref[j]))

                        # Delete the initialization trigger
                        del self.etd_time_trigger[0][indices[i]]
                        del self.etd_time_trigger[1][indices[i]]
                        del self.etd_time_trigger[2][indices[i]]

                    # Initialize the trigger for the timewindows
                    else:
                        # Initialize the lists of self.num_eventlines_tsa_ref if not already initialized
                        if not self.num_eventlines_tsa_ref:
                            self.num_eventlines_tsa_ref = [[num] for num in self.num_eventlines]
                        else:
                            # Expand the lists of self.num_eventlines_tsa_ref
                            for j in range(len(self.num_eventlines_tsa_ref), len(self.num_eventlines)):  # skipcq: PTC-W0060
                                self.num_eventlines_tsa_ref.append([0]*len(self.num_eventlines_tsa_ref[0]))
                            # Add the current number of eventlines
                            for j, val in enumerate(self.num_eventlines):
                                self.num_eventlines_tsa_ref[j].append(val-sum(self.num_eventlines_tsa_ref[j]))

                        # skipcq: PTC-W0063
                        # Get the timewindow lengths
                        time_list = self.following_modules[next(
                            j for j in range(len(self.following_modules)) if self.following_modules[j].__class__.__name__ ==
                            'TSAArimaDetector')].calculate_time_steps(self.num_eventlines_tsa_ref, log_atom)
                        self.num_eventlines_tsa_ref = copy.copy(self.num_eventlines)

                        num_added_trigger = 0

                        # Add the new triggers
                        for j, val in enumerate(time_list):
                            if val != -1:
                                num_added_trigger += 1
                                self.etd_time_trigger[0].append(self.etd_time_trigger[0][indices[i]] + val * self.waiting_time_for_tsa /
                                                                self.num_sections_waiting_time_for_tsa)
                                self.etd_time_trigger[1].append(j)
                                self.etd_time_trigger[2].append(val * self.waiting_time_for_tsa / self.num_sections_waiting_time_for_tsa)

                        # Delete the initialization trigger
                        del self.etd_time_trigger[0][indices[i]]
                        del self.etd_time_trigger[1][indices[i]]
                        del self.etd_time_trigger[2][indices[i]]

                        # Run the update function for all trigger, which would already have been triggered
                        for k in range(1, num_added_trigger+1):
                            while current_time >= self.etd_time_trigger[0][-k]:
                                # skipcq: PTC-W0063
                                self.following_modules[next(
                                    j for j in range(len(self.following_modules)) if self.following_modules[j].__class__.__name__ ==
                                    'TSAArimaDetector')].test_num_appearance(self.etd_time_trigger[1][-k], self.num_eventlines[
                                                                     self.etd_time_trigger[1][-k]] - self.num_eventlines_tsa_ref[
                                                                     self.etd_time_trigger[1][-k]], current_time, log_atom)
                                self.etd_time_trigger[0][-k] += self.etd_time_trigger[2][-k]
                                self.num_eventlines_tsa_ref[self.etd_time_trigger[1][-k]] = self.num_eventlines[self.etd_time_trigger[
                                    1][-k]]

                # Trigger for an reoccuring time window
                else:
                    while current_time >= self.etd_time_trigger[0][indices[i]]:
                        # skipcq: PTC-W0063
                        self.following_modules[next(
                            j for j in range(len(self.following_modules)) if self.following_modules[j].__class__.__name__ ==
                            'TSAArimaDetector')].test_num_appearance(self.etd_time_trigger[1][indices[i]], self.num_eventlines[
                                                             self.etd_time_trigger[1][indices[i]]]-self.num_eventlines_tsa_ref[
                                                             self.etd_time_trigger[1][indices[i]]], current_time, log_atom)
                        self.etd_time_trigger[0][indices[i]] += self.etd_time_trigger[2][indices[i]]
                        self.num_eventlines_tsa_ref[self.etd_time_trigger[1][indices[i]]] = self.num_eventlines[self.etd_time_trigger[
                            1][indices[i]]]

        valid_log_atom = False
        if self.path_list:
            for path in self.path_list:
                if path in log_atom.parser_match.get_match_dictionary().keys():
                    valid_log_atom = True
                    break
        if self.path_list and not valid_log_atom:
            self.current_index = -1
            return False
        self.total_records += 1

        # Get the current index, eighter from the combination of values of the paths of id_path_list, or the event type
        if self.id_path_list != []:
            # In case that id_path_list is set, use it to differentiate sequences by their id.
            # Otherwise, the empty tuple () is used as the only key of the current_sequences dict.
            id_tuple = ()
            for id_path in self.id_path_list:
                id_match = log_atom.parser_match.get_match_dictionary().get(id_path)
                if id_match is None:
                    if self.allow_missing_id is True:
                        # Insert placeholder for id_path that is not available
                        id_tuple += ('',)
                    else:
                        # Omit log atom if one of the id paths is not found.
                        return False
                else:
                    if isinstance(id_match.match_object, bytes):
                        id_tuple += (id_match.match_object.decode(AminerConfig.ENCODING),)
                    else:
                        id_tuple += (id_match.match_object,)

            # Check if only certain tuples are allowed and if the tuplle is included.
            if self.allowed_id_tuples != [] and id_tuple not in self.allowed_id_tuples:
                self.current_index = -1
                return False

            # Searches if the id_tuple has previously appeared
            current_index = -1
            for event_index, var_key in enumerate(self.id_path_list_tuples):
                if id_tuple == var_key:
                    current_index = event_index
        else:
            # Searches if the event type has previously appeared
            current_index = -1
            for event_index in range(self.num_events):
                if self.longest_path[event_index] in log_atom.parser_match.get_match_dictionary() and set(
                        log_atom.parser_match.get_match_dictionary()) == self.found_keys[event_index]:
                    current_index = event_index

        # Initialize a new event type if the event type of the new line has not appeared
        if current_index == -1:
            current_index = self.num_events
            self.num_events += 1
            self.found_keys.append(set(log_atom.parser_match.get_match_dictionary().keys()))

            # Initialize the list of the keys to the variables
            self.variable_key_list.append(list(self.found_keys[current_index]))
            # Delete the entries with value None or timestamps as values
            for var_index in range(len(self.variable_key_list[current_index]) - 1, -1, -1):
                if log_atom.parser_match.get_match_dictionary()[self.variable_key_list[current_index][var_index]].match_object is None:
                    del self.variable_key_list[current_index][var_index]
                elif (self.path_list is not None) and self.variable_key_list[current_index][var_index] not in self.path_list:
                    del self.variable_key_list[current_index][var_index]

            # Initialize the empty lists for the values and initialize the check_variables list for the variables
            if self.save_values:
                self.init_values(current_index)
                self.check_variables.append([True for _ in range(len(self.variable_key_list[current_index]))])
            self.num_eventlines.append(0)

            if self.id_path_list == []:
                # String of the longest found path
                self.longest_path.append('')
                # Number of forwardslashes in the longest path
                tmp_int = 0
                if self.path_list is None:
                    for var_key in self.variable_key_list[current_index]:
                        if var_key is not None:
                            count = var_key.count('/')
                            if (count > tmp_int or (count == tmp_int and len(self.longest_path[current_index]) < len(var_key))):
                                self.longest_path[current_index] = var_key
                                tmp_int = count
                else:
                    found_keys_list = list(self.found_keys[current_index])
                    for found_key in found_keys_list:
                        count = found_key.count('/')
                        if count > tmp_int or (count == tmp_int and len(self.longest_path[current_index]) < len(found_key)):
                            self.longest_path[current_index] = found_key
                            tmp_int = count
            else:
                self.id_path_list_tuples.append(id_tuple)

        self.current_index = current_index

        if self.save_values:
            # Appends the values to the event type
            self.append_values(log_atom, current_index)
        self.num_eventlines[current_index] += 1
        self.log_success += 1
        return True

    def get_time_trigger_class(self):  # skipcq: PYL-R0201
        """Get the trigger class this component can be registered for. This detector only needs persistence triggers in real time."""
        return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def do_timer(self, trigger_time):
        """Check if current ruleset should be persisted."""
        if self.next_persist_time is None:
            return self.aminer_config.config_properties.get(KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)

        delta = self.next_persist_time - trigger_time
        if delta <= 0:
            self.do_persist()
            delta = self.aminer_config.config_properties.get(KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)
        return delta

    def load_persistence_data(self):
        """Load the persistence data from storage."""
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        if persistence_data is not None:
            for key in persistence_data["found_keys"]:
                self.found_keys.append(set(key))
            self.variable_key_list = persistence_data["variable_key_list"]
            self.values = persistence_data["values"]
            self.longest_path = persistence_data["longest_path"]
            self.check_variables = persistence_data["check_variables"]
            self.num_eventlines = persistence_data["num_eventlines"]
            self.etd_time_trigger = persistence_data["etd_time_trigger"]
            self.num_eventlines_TSA_ref = persistence_data["num_eventlines_TSA_ref"]
            self.num_events = len(self.found_keys)
        else:
            if self.track_time_for_TSA:
                self.etd_time_trigger[0].append(-1)
                self.etd_time_trigger[1].append(-1)
                self.etd_time_trigger[2].append(-1)

    def do_persist(self):
        """Immediately write persistence data to storage."""
        persist_dict = {"found_keys": self.found_keys, "variable_key_list": self.variable_key_list, "values": self.values,
                        "longest_path": self.longest_path, "check_variables": self.check_variables, "num_eventlines": self.num_eventlines,
                        "etd_time_trigger": self.etd_time_trigger, "num_eventlines_TSA_ref": self.num_eventlines_TSA_ref}
        PersistenceUtil.store_json(self.persistence_file_name, persist_dict)

        for following_module in self.following_modules:
            following_module.do_persist()

        self.next_persist_time = time.time() + self.aminer_config.config_properties.get(
            KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)
        logging.getLogger(DEBUG_LOG_NAME).debug('%s persisted data.', self.__class__.__name__)

    def add_following_modules(self, following_module):
        """Add the given Module to the following module list."""
        self.following_modules.append(following_module)
        logging.getLogger(DEBUG_LOG_NAME).debug(
            '%s added following module %s.', self.__class__.__name__, following_module.__class__.__name__)

    def init_values(self, current_index):
        """Initialize the variable_key_list and the list for the values."""
        # Initializes the value_list
        if not self.values:
            self.values = [[[] for _ in range(len(self.variable_key_list[current_index]))]]
        else:
            self.values.append([[] for _ in range(len(self.variable_key_list[current_index]))])

    def append_values(self, log_atom, current_index):
        """Add the values of the variables of the current line to self.values."""
        for var_index, var_key in enumerate(self.variable_key_list[current_index]):
            # Skips the variable if check_variable is False, or if the var_key is not included in the match_dict
            if not self.check_variables[current_index][var_index]:
                continue
            if var_key not in log_atom.parser_match.get_match_dictionary():
                self.values[current_index][var_index] = []
                self.check_variables[current_index][var_index] = False
                continue

            raw_match_object = ''
            if isinstance(log_atom.parser_match.get_match_dictionary()[var_key].match_object, bytearray):
                raw_match_object = repr(
                    bytes(log_atom.parser_match.get_match_dictionary()[var_key].match_object))[2:-1]
            elif isinstance(log_atom.parser_match.get_match_dictionary()[var_key].match_object, bytes):
                raw_match_object = repr(log_atom.parser_match.get_match_dictionary()[var_key].match_object)[2:-1]

            # Try to convert the values to floats and add them as values
            try:
                if raw_match_object != '':
                    self.values[current_index][var_index].append(float(raw_match_object))
                else:
                    self.values[current_index][var_index].append(
                        float(log_atom.parser_match.get_match_dictionary()[var_key].match_object))
            # Add the strings as values
            except:  # skipcq: FLK-E722
                if isinstance(log_atom.parser_match.get_match_dictionary()[var_key].match_string, bytes):
                    self.values[current_index][var_index].append(
                        repr(log_atom.parser_match.get_match_dictionary()[var_key].match_string)[2:-1])
                else:
                    self.values[current_index][var_index].append(log_atom.parser_match.get_match_dictionary()[var_key].match_string)

        # Reduce the numbers of entries in the value_list
        if len(self.variable_key_list[current_index]) > 0 and len([i for i in self.check_variables[current_index] if i]) > 0 and \
                len(self.values[current_index][self.check_variables[current_index].index(True)]) > self.max_num_vals:
            for var_index in range(len(self.variable_key_list[current_index])):  # skipcq: PTC-W0060
                # Skips the variable if check_variable is False
                if not self.check_variables[current_index][var_index]:
                    continue
                self.values[current_index][var_index] = self.values[current_index][var_index][-self.min_num_vals:]
