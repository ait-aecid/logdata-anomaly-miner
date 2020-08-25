"""This module can assignes every parsed log line a eventtype and can be used for profiling purposes. It supports the modules
VariableTypeDetector and VariableCorrelationDetector."""
import cProfile
import sys
import os
import time
import copy

from datetime import datetime
from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events import EventSourceInterface
from aminer.input import AtomHandlerInterface
from aminer.util import TimeTriggeredComponentInterface
from aminer.util import PersistencyUtil

# ToDo:
# x) Adapt the Persitency
# x) Restructure the TSA part
# x) Implement the time trigger for the ECD -> Max



class EventTypeDetector(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface):
    """This class keeps track of the found eventtypes and the values of each variable"""

    def __init__(self, aminer_config, anomaly_event_handlers, persistence_id='Default', auto_include_flag=False, options=None,
                 path_list=None, output_log_line=True):
        """Initialize the detector. This will also trigger reading or creation of persistence storage location."""
        self.next_persist_time = None
        self.num_events = 0
        # List of the longest path of the events
        self.longest_path = []
        # List of the keys corresponding to the events
        self.found_keys = []
        # List of the keys, which take values in the log-line
        self.variable_key_list = []
        # List of the values of the log-lines. If the lenght reaches maxNumVals the list gets reduced to minNumVals values per variable
        self.values = []
        # Saves the number of lines of the event-types
        self.num_eventlines = []
        # Saves the number of total log-lines
        self.total_records = 0
        # List of the modules which follow the event_type_detector. The implemented modules are form the list
        # [variableTypeDetector, variableCorrelationDetector]
        self.following_modules = []
        # List of paths, which variables are being tracked. All other paths will not get tracked. If None all paths are being tracked.
        self.path_list = path_list
        self.check_variables = []
        self.log_atom = None # !!!
        # List ot the time trigger. The first list states the times when something should be triggered,
        # the second list states the indices of the eventtyps, or a list of the evnettype, a path and a value which should be counted (-1 for an initialisation)
        # the third list states, the length of the time window (-1 for a one time trigger)
        self.time_trigger = [[], [], []]
        # Reference containing the number of lines of the events for the TSA
        self.num_eventlines_TSA_ref = []
        # Index of the eventtype of the current log line
        self.current_index = 0

        self.options = {
            'minNumVals': 1000,
            # Number of the values which the list is being reduced to. Be cautious that this is higher than 'num_min_values'
            # in VarTypeD/Cor!!!
            # > minNumVals. Maximum number of lines in the value list before it is reduced
            'maxNumVals': 1500,
            # If True, generates simple output, which states how many lines the EvTypeD has already processed
            'generateSimpleOutput': False,
            # The number of lines to be processed before printing an output.
            'outputAfterNumberOfLines': 10000,
            # States if the persistency should be overwritten in do_persist
            'writePersistenceData': auto_include_flag,
            # If True the persistency will be loaded, if False it will initialise without the persistency
            'loadPersistenceData': False,
            # States if the profiler will be run
            'runProfiler': False,
            # If False the following modules will print output. If True the print functions will stay silent
            'silence': False,
            # If False the values of the Token are not saved for further analysis. Disables self.values, and self.check_variables
            'saveValues': True,
            # States if the time windows should be tracked for the time series analysis
            'trackTimeForTSA': False,
            # Time in seconds, untill the time windows are being initialised
            'waitingTimeForTSA': 1
        }

        if options is not None:
            # Overwrites the options with the specified input options
            for key in options.keys():
                if key in self.options:
                    self.options[key] = options[key]
                else:
                    print('Unknown option %s in EventTypeDetector', key, file=sys.stderr)

        # Used to profile the algorithm
        if self.options['runProfiler']:
            self.profiler = cProfile.Profile()
            self.profiler.enable()

        self.anomaly_event_handlers = anomaly_event_handlers
        self.output_log_line = output_log_line

        # Loads the persistency
        PersistencyUtil.add_persistable_component(self)
        self.persistence_file_name = AMinerConfig.build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        persistence_data = PersistencyUtil.load_json(self.persistence_file_name)

        # Imports the persistency if self.options['loadPersistenceData'] is True
        if persistence_data is not None and self.options['loadPersistenceData']:
            for key in persistence_data[0]:
                self.found_keys.append(set(key))
            self.variable_key_list = persistence_data[1]
            self.values = persistence_data[2]
            self.longest_path = persistence_data[3]
            self.check_variables = persistence_data[4]
            self.num_eventlines = persistence_data[5]

            self.num_events = len(self.found_keys)
        else:
            if self.options['trackTimeForTSA']:
                self.time_trigger[0].append(time.time() + self.options['waitingTimeForTSA'])
                self.time_trigger[1].append(-1)
                self.time_trigger[2].append(-1)

    def receive_atom(self, log_atom):
        """Receives an parsed atom and keeps track of the event-types and the values of the variables of them"""
        debug_mode = False

        # time.sleep(0.05) # !!!
        # Check if a trigger has been triggered
        if self.options['trackTimeForTSA'] and time.time() >= min(self.time_trigger[0]):
            # Get the indices of the triggered events
            time_tmp = time.time()
            indices = [i for i in range(len(self.time_trigger[0])) if time_tmp >= self.time_trigger[0][i]]
            if debug_mode:
                print(time_tmp)
                print(self.time_trigger[0])
                print(indices)

            # Exectute the functions for the TSA
            if self.options['trackTimeForTSA']:
                for i in range(len(indices) - 1, -1, -1):
                    if type(self.time_trigger[1][indices[i]]) == int:
                        # Trigger for an initalisation
                        if self.time_trigger[1][indices[i]] == -1:
                            if debug_mode:
                                print('Init')
                                print('Totalnumber of read in Lines: %s, List to the numbers per Event: %s'%(self.total_records, self.num_eventlines))

                            # Get the timewindow lengths
                            time_list = self.following_modules[0].function_Init(self.num_eventlines)
                            self.num_eventlines_TSA_ref = copy.copy(self.num_eventlines)

                            # Add the new triggers
                            for j in range(len(time_list)):
                                if time_list[j] != -1:
                                    self.time_trigger[0].append(time_tmp + time_list[j])
                                    self.time_trigger[1].append(j)
                                    self.time_trigger[2].append(time_list[j])

                            del self.time_trigger[0][indices[i]]
                            del self.time_trigger[1][indices[i]]
                            del self.time_trigger[2][indices[i]]
                            if debug_mode:
                                print(self.time_trigger)
                        
                        # Trigger for an reoccuring time window
                        else:
                            if debug_mode:
                                print('Upd')
                                print('Totalnumber of read in Lines: %s, List to the numbers per Event: %s'%(self.total_records, self.num_eventlines))
                            self.following_modules[0].function_Upd(self.time_trigger[1][indices[i]], self.num_eventlines[self.time_trigger[1][indices[i]]]-self.num_eventlines_TSA_ref[self.time_trigger[1][indices[i]]])
                            self.time_trigger[0][indices[i]] = time.time() + self.time_trigger[2][indices[i]]
                            self.num_eventlines_TSA_ref[self.time_trigger[1][indices[i]]] = self.num_eventlines[self.time_trigger[1][indices[i]]]
            if debug_mode:
                print(self.time_trigger[0])

        self.log_atom = log_atom # !!!
        valid_log_atom = False
        if self.path_list:
            for path in self.path_list:
                if path in log_atom.parser_match.get_match_dictionary().keys():
                    valid_log_atom = True
                    break
        if self.path_list and not valid_log_atom:
            return False
        self.total_records += 1

        # Could be None, but shouldn't, because only parsed lines are called with the reveive_atom function
        # FIXME: This check should not be necessary.
        if log_atom.parser_match is None:
            return False

        # Seaches if the path_list has already apeared
        current_index = -1
        for event_index in range(self.num_events):
            if self.longest_path[event_index] in log_atom.parser_match.get_match_dictionary() and set(
                    log_atom.parser_match.get_match_dictionary()) == self.found_keys[event_index]:
                current_index = event_index

        # Initialiseds a new event-type if the event-type of the new line has not appeared
        if current_index == -1:
            current_index = self.num_events
            self.num_events += 1
            self.found_keys.append(set(log_atom.parser_match.get_match_dictionary().keys()))

            # Initialise the list of the keys to the variables
            self.variable_key_list.append(list(self.found_keys[current_index]))
            # Delete the entries with value None or timestamps as values
            for var_index in range(len(self.variable_key_list[current_index]) - 1, -1, -1):
                if log_atom.parser_match.get_match_dictionary()[self.variable_key_list[current_index][var_index]].match_object is None:
                    del self.variable_key_list[current_index][var_index]
                elif (self.path_list is not None) and self.variable_key_list[current_index][var_index] not in self.path_list:
                    del self.variable_key_list[current_index][var_index]

            # Initial the lists for the values
            if self.options['saveValues']:
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

        if self.options['saveValues']:
            # Appends the values to the event-type
            self.append_values(log_atom, current_index)
        self.num_eventlines[current_index] += 1

        # Generates a output, which states, how many log-lines have been processed by the EvTypeD
        if self.options['generateSimpleOutput'] and self.total_records % self.options['outputAfterNumberOfLines'] == 0:
            self.print('Number of processed log lines of EventTypeDetector: %s' % self.total_records, log_atom, current_index)

        # Output for the 'End'-line # !!!
        if '/firstmatch0/End' in log_atom.parser_match.get_match_dictionary():
            self.do_persist()
            self.failfunction()

        return True

    def get_time_trigger_class(self):
        """Get the trigger class this component can be registered for. This detector only needs persistency triggers in real time."""
        return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def do_timer(self, trigger_time):
        """Checks if current ruleset should be persisted"""
        if self.next_persist_time is None:
            return 600

        delta = self.next_persist_time - trigger_time
        if delta <= 0:
            self.do_persist()
            delta = 600
        return delta

    def do_persist(self):
        """Immediately write persistence data to storage."""
        if self.options['runProfiler']:
            self.profiler.disable()
            self.profiler.print_stats()

        if not self.options['writePersistenceData']:
            return

        tmp_list = [[]]
        for key in self.found_keys:
            tmp_list[0].append(list(key))
        tmp_list.append(self.variable_key_list)
        tmp_list.append(self.values)
        tmp_list.append(self.longest_path)
        tmp_list.append(self.check_variables)
        tmp_list.append(self.num_eventlines)
        PersistencyUtil.store_json(self.persistence_file_name, tmp_list)

        for following_module in self.following_modules:
            following_module.do_persist()

        self.next_persist_time = None

    def add_following_modules(self, following_module):
        """Adds the given Module to the following module list"""
        self.following_modules.append(following_module)

    def init_values(self, current_index):
        """Initializes the variable_key_list and the list for the values"""
        # Initialises the value_list
        if not self.values:
            self.values = [[[] for _ in range(len(self.variable_key_list[current_index]))]]
        else:
            self.values.append([[] for _ in range(len(self.variable_key_list[current_index]))])

    def append_values(self, log_atom, current_index):
        """Adds the values of the variables of the current line to self.values"""
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
            except:
                if isinstance(log_atom.parser_match.get_match_dictionary()[var_key].match_string, bytearray):
                    self.values[current_index][var_index].append(
                        repr(bytes(log_atom.parser_match.get_match_dictionary()[var_key].match_string))[2:-1])
                elif isinstance(log_atom.parser_match.get_match_dictionary()[var_key].match_string, bytes):
                    self.values[current_index][var_index].append(
                        repr(log_atom.parser_match.get_match_dictionary()[var_key].match_string)[2:-1])
                else:
                    self.values[current_index][var_index].append(log_atom.parser_match.get_match_dictionary()[var_key].match_string)

        # Reduce the numbers of entries in the value_list
        if len(self.variable_key_list[current_index]) > 0 and len([i for i in self.check_variables[current_index] if i]) > 0:
            if len(self.values[current_index][self.check_variables[current_index].index(True)]) > self.options['maxNumVals']:
                for var_index in range(len(self.variable_key_list[current_index])):
                    # Skips the variable if check_variable is False
                    if not self.check_variables[current_index][var_index]:
                        continue
                    self.values[current_index][var_index] = self.values[current_index][var_index][-self.options['minNumVals']:]

    def print(self, message, log_atom, current_index):
        """Prints the message"""
        if self.options['silence']:
            return
        analysis_component = {'AffectedLogAtomPaths': [log_atom.parser_match.get_match_dictionary().keys()]}
        if self.output_log_line:
            match_paths_values = {}
            for match_path, match_element in log_atom.parser_match.get_match_dictionary().items():
                match_value = match_element.match_object
                if isinstance(match_value, tuple):
                    tmp_list = []
                    for val in match_value:
                        if isinstance(val, datetime):
                            tmp_list.append(datetime.timestamp(val))
                        else:
                            tmp_list.append(val)
                    match_value = tmp_list
                if isinstance(match_value, bytes):
                    match_value = match_value.decode()
                match_paths_values[match_path] = match_value
            analysis_component['ParsedLogAtom'] = match_paths_values
            sorted_log_lines = [log_atom.parser_match.match_element.annotate_match('') + os.linesep + log_atom.raw_data.decode()]
        else:
            sorted_log_lines = [self.longest_path[current_index] + os.linesep + log_atom.raw_data.decode()]
        event_data = {'AnalysisComponent': analysis_component, 'TotalRecords': self.total_records}
        for listener in self.anomaly_event_handlers:
            listener.receive_event('Analysis.%s' % self.__class__.__name__, message, sorted_log_lines, event_data, log_atom, self)
