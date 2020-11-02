"""
This module can assigns every parsed log line a eventtype and can be used for profiling purposes.
It supports the modules VariableTypeDetector and VariableCorrelationDetector.
"""
import time
import copy
import logging

from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.input import AtomHandlerInterface
from aminer.util import TimeTriggeredComponentInterface
from aminer.util import PersistencyUtil


class EventTypeDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """This class keeps track of the found eventtypes and the values of each variable."""

    def __init__(self, aminer_config, anomaly_event_handlers, persistence_id='Default', path_list=None, min_num_vals=1000,
                 max_num_vals=1500, save_values=True, track_time_for_TSA=False, waiting_time_for_TSA=300,
                 num_sections_waiting_time_for_TSA=10):
        """Initialize the detector. This will also trigger reading or creation of persistence storage location."""
        self.next_persist_time = time.time() + 600.0
        self.anomaly_event_handlers = anomaly_event_handlers
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
        self.num_eventlines_TSA_ref = []
        # Index of the eventtype of the current log line
        self.current_index = 0
        # Number of the values which the list is being reduced to. Be cautious that this is higher than 'num_min_values'
        # in VarTypeD/Cor!!!
        self.min_num_vals = min_num_vals
        # Maximum number of lines in the value list before it is reduced. > min_num_vals.
        self.max_num_vals = max_num_vals
        # If False the values of the Token are not saved for further analysis. Disables self.values, and self.check_variables
        self.save_values = save_values
        # States if the time windows should be tracked for the time series analysis
        self.track_time_for_TSA = track_time_for_TSA
        # Time in seconds, until the time windows are being initialized
        self.waiting_time_for_TSA = waiting_time_for_TSA
        # Number of subdivisions of the initialization window. The length of the input-list of the function_Init-funtion is numSubd+1
        self.num_sections_waiting_time_for_TSA = num_sections_waiting_time_for_TSA

        # Loads the persistency
        PersistencyUtil.add_persistable_component(self)
        self.persistence_file_name = AMinerConfig.build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        persistence_data = PersistencyUtil.load_json(self.persistence_file_name)

        # Imports the persistency
        if persistence_data is not None:
            for key in persistence_data[0]:
                self.found_keys.append(set(key))
            self.variable_key_list = persistence_data[1]
            self.values = persistence_data[2]
            self.longest_path = persistence_data[3]
            self.check_variables = persistence_data[4]
            self.num_eventlines = persistence_data[5]
            self.etd_time_trigger = persistence_data[6]
            self.num_eventlines_TSA_ref = persistence_data[7]

            self.num_events = len(self.found_keys)
        else:
            if self.track_time_for_TSA:
                self.etd_time_trigger[0].append(-1)
                self.etd_time_trigger[1].append(-1)
                self.etd_time_trigger[2].append(-1)

    def receive_atom(self, log_atom):
        """Receives an parsed atom and keeps track of the event types and the values of the variables of them."""
        self.log_total += 1
        # Get the current time
        if self.track_time_for_TSA:
            if log_atom.atom_time is not None:
                current_time = log_atom.atom_time
            else:
                current_time = time.time()

        # Check if TSA should be initialized
        if self.track_time_for_TSA and -1 in self.etd_time_trigger[0]:
            for i in range(len(self.etd_time_trigger[0])):
                if self.etd_time_trigger[0][i] == -1:
                    for j in range(self.num_sections_waiting_time_for_TSA-1):
                        self.etd_time_trigger[0].append(current_time + self.waiting_time_for_TSA*(j+1)/(
                                self.num_sections_waiting_time_for_TSA))
                        self.etd_time_trigger[1].append(-1)
                        self.etd_time_trigger[2].append(-1)

                    self.etd_time_trigger[0][i] = current_time + self.waiting_time_for_TSA
                    break

        # Check if a trigger has been triggered
        if self.track_time_for_TSA and len(self.etd_time_trigger[0]) > 0 and current_time >= min(self.etd_time_trigger[0]):
            # Get the indices of the triggered events
            indices = [i for i in range(len(self.etd_time_trigger[0])) if current_time >= self.etd_time_trigger[0][i]]

            # Exectute the triggered functions of the TSA
            if self.track_time_for_TSA:
                for i in range(len(indices)-1, -1, -1):
                    # Checks if trigger is part of the initalisation
                    if self.etd_time_trigger[1][indices[i]] == -1 and self.etd_time_trigger[2][indices[i]] == -1:

                        # Save the number of occured eventtypes for the initialization of the TSA
                        if self.num_eventlines_TSA_ref == [] or len(
                                self.num_eventlines_TSA_ref[0]) < self.num_sections_waiting_time_for_TSA-1:

                            # Initialize the lists of self.num_eventlines_TSA_ref if not already initialized
                            if not self.num_eventlines_TSA_ref:
                                self.num_eventlines_TSA_ref = [[num] for num in self.num_eventlines]
                            else:
                                # Expand the lists of self.num_eventlines_TSA_ref
                                for j in range(len(self.num_eventlines_TSA_ref), len(self.num_eventlines)):
                                    self.num_eventlines_TSA_ref.append([0]*len(self.num_eventlines_TSA_ref[0]))
                                # Add the current number of eventlines
                                for j in range(len(self.num_eventlines)):
                                    self.num_eventlines_TSA_ref[j].append(self.num_eventlines[j]-sum(self.num_eventlines_TSA_ref[j]))

                            # Delete the initialization trigger
                            del self.etd_time_trigger[0][indices[i]]
                            del self.etd_time_trigger[1][indices[i]]
                            del self.etd_time_trigger[2][indices[i]]

                        # Initialize the trigger for the timewindows
                        else:
                            # Initialize the lists of self.num_eventlines_TSA_ref if not already initialized
                            if not self.num_eventlines_TSA_ref:
                                self.num_eventlines_TSA_ref = [[num] for num in self.num_eventlines]
                            else:
                                # Expand the lists of self.num_eventlines_TSA_ref
                                for j in range(len(self.num_eventlines_TSA_ref), len(self.num_eventlines)):
                                    self.num_eventlines_TSA_ref.append([0]*len(self.num_eventlines_TSA_ref[0]))
                                # Add the current number of eventlines
                                for j in range(len(self.num_eventlines)):
                                    self.num_eventlines_TSA_ref[j].append(self.num_eventlines[j]-sum(self.num_eventlines_TSA_ref[j]))

                            # Get the timewindow lengths
                            time_list = self.following_modules[next(j for j in range(len(
                                self.following_modules)) if self.following_modules[j].__class__.__name__ == 'TestDetector')].function_Init(
                                self.num_eventlines_TSA_ref)
                            self.num_eventlines_TSA_ref = copy.copy(self.num_eventlines)

                            # Add the new triggers
                            for j in range(len(time_list)):
                                if time_list[j] != -1:
                                    self.etd_time_trigger[0].append(self.etd_time_trigger[0][indices[i]] + time_list[j])
                                    self.etd_time_trigger[1].append(j)
                                    self.etd_time_trigger[2].append(time_list[j])

                                while current_time >= self.etd_time_trigger[0][-1]:
                                    self.following_modules[next(j for j in range(len(
                                        self.following_modules)) if self.following_modules[j].__class__.__name__ == 'TestDetector')].\
                                        function_Upd(self.etd_time_trigger[1][-1], self.num_eventlines[self.etd_time_trigger[1][
                                            -1]]-self.num_eventlines_TSA_ref[self.etd_time_trigger[1][-1]])
                                    self.etd_time_trigger[0][-1] = self.etd_time_trigger[0][-1] + self.etd_time_trigger[2][-1]
                                    self.num_eventlines_TSA_ref[self.etd_time_trigger[1][-1]] = self.num_eventlines[self.etd_time_trigger[
                                        1][-1]]

                            # Delete the initialization trigger
                            del self.etd_time_trigger[0][indices[i]]
                            del self.etd_time_trigger[1][indices[i]]
                            del self.etd_time_trigger[2][indices[i]]

                    # Trigger for an reoccuring time window
                    else:
                        while current_time >= self.etd_time_trigger[0][indices[i]]:
                            self.following_modules[next(j for j in range(len(self.following_modules)) if self.following_modules[
                                j].__class__.__name__ == 'TestDetector')].function_Upd(self.etd_time_trigger[1][indices[
                                    i]], self.num_eventlines[self.etd_time_trigger[1][indices[i]]]-self.num_eventlines_TSA_ref[
                                    self.etd_time_trigger[1][indices[i]]])
                            self.etd_time_trigger[0][indices[i]] += self.etd_time_trigger[2][indices[i]]
                            self.num_eventlines_TSA_ref[self.etd_time_trigger[1][indices[i]]] = self.num_eventlines[self.etd_time_trigger[
                                1][indices[i]]]

        valid_log_atom = False
        if self.path_list:
            for path in self.path_list:
                if path in log_atom.parser_match.get_match_dictionary().keys():
                    valid_log_atom = True
                    break
        if self.path_list and not valid_log_atom:
            return False
        self.total_records += 1

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

            # String of the longest found path
            self.longest_path.append('')
            # Number of forwardslashes in the longest path
            tmp_int = 0
            if self.path_list is None:
                for var_key in self.variable_key_list[current_index]:
                    if var_key.count('/') > tmp_int or (var_key.count('/') ==
                                                        tmp_int and len(self.longest_path[current_index]) < len(var_key)):
                        self.longest_path[current_index] = var_key
                        tmp_int = var_key.count('/')
            else:
                found_keys_list = list(self.found_keys[current_index])
                for found_key in found_keys_list:
                    if found_key.count('/') > tmp_int or\
                            (found_key.count('/') == tmp_int and len(self.longest_path[current_index]) < len(found_key)):
                        self.longest_path[current_index] = found_key
                        tmp_int = found_key.count('/')

        self.current_index = current_index

        if self.save_values:
            # Appends the values to the event type
            self.append_values(log_atom, current_index)
        self.num_eventlines[current_index] += 1
        self.log_success += 1
        return True

    def get_time_trigger_class(self):
        """Get the trigger class this component can be registered for. This detector only needs persistency triggers in real time."""
        return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def do_timer(self, trigger_time):
        """Check if current ruleset should be persisted."""
        if self.next_persist_time is None:
            return 600

        delta = self.next_persist_time - trigger_time
        if delta <= 0:
            self.do_persist()
            delta = 600
        return delta

    def do_persist(self):
        """Immediately write persistence data to storage."""
        tmp_list = [[]]
        for key in self.found_keys:
            tmp_list[0].append(list(key))
        tmp_list.append(self.variable_key_list)
        tmp_list.append(self.values)
        tmp_list.append(self.longest_path)
        tmp_list.append(self.check_variables)
        tmp_list.append(self.num_eventlines)
        tmp_list.append(self.etd_time_trigger)
        tmp_list.append(self.num_eventlines_TSA_ref)
        PersistencyUtil.store_json(self.persistence_file_name, tmp_list)

        for following_module in self.following_modules:
            following_module.do_persist()

        self.next_persist_time = time.time() + 600.0
        logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).debug('%s persisted data.', self.__class__.__name__)

    def add_following_modules(self, following_module):
        """Add the given Module to the following module list."""
        self.following_modules.append(following_module)
        logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).debug(
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
        for var_key in self.variable_key_list[current_index]:
            # Skips the variable if check_variable is False
            var_index = self.variable_key_list[current_index].index(var_key)
            if not self.check_variables[current_index][var_index]:
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
        if len(self.variable_key_list[current_index]) > 0 and len([i for i in self.check_variables[current_index] if i]) > 0:
            if len(self.values[current_index][self.check_variables[current_index].index(True)]) > self.max_num_vals:
                for var_index in range(len(self.variable_key_list[current_index])):
                    # Skips the variable if check_variable is False
                    if not self.check_variables[current_index][var_index]:
                        continue
                    self.values[current_index][var_index] = self.values[current_index][var_index][-self.min_num_vals:]
