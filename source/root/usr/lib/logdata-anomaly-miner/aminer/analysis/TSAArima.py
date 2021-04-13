"""This module is a detector for testing purposes of the ETD"""

# ToDo:
# x) Remove unwanted dependency on packages (TODOs in statsmodels, but very intervined)
# x) Persistency
# x) Cleanup
# x) Add Module to the lists in the AMiner
# x) Improvement for the acf (not as dependent on min_lag or ETD.waiting_time_for_TSA)
# x) Contraint/ignore/pathlist without use

import time
import os

from aminer import AminerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events import EventSourceInterface
from aminer.input import AtomHandlerInterface
from aminer.util import TimeTriggeredComponentInterface
from aminer.util import PersistenceUtil

import numpy as np
from scipy.signal import savgol_filter
import statsmodels

class TSAArima(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface):
    """This class is used for testing purposes"""

    def __init__(self, aminer_config, anomaly_event_handlers, event_type_detector, build_sum_over_values=False, num_division_time_step=10,
                 alpha=0.05, persistence_id='Default', output_log_line=True, ignore_list=None, constraint_list=None):
        self.next_persist_time = None
        self.anomaly_event_handlers = anomaly_event_handlers
        self.aminer_config = aminer_config
        self.output_log_line = output_log_line

        # event_type_detector. Used to get the eventNumbers and values of the variables, etc.
        self.event_type_detector = event_type_detector
        # Add the varTypeDetector to the list of the modules, which use the event_type_detector.
        self.event_type_detector.add_following_modules(self)
        # States if the sum of a series of counts is build before applieing the TSA
        self.build_sum_over_values = build_sum_over_values
        # Number of division of the time window to calculate the time step
        self.num_division_time_step = num_division_time_step
        # Significance level of the estimatedd values
        self.alpha = alpha

        # List of the time steps
        self.time_step_list = []
        # History of the time windows
        self.time_window_history = []
        # List of the the single arima_models (statsmodels)
        self.arima_models_statsmodels = []

        self.plots = [[], [], []]
        self.time_history = []
        return

    def receive_atom(self, log_atom):
        return True

    def get_time_trigger_class(self):
        """Get the trigger class this component can be registered for. This detector only needs persisteny triggers in real time."""
        return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def do_timer(self, trigger_time):
        """Checks if current ruleset should be persisted"""
        return 600

    def do_persist(self):
        """Immediately write persistence data to storage."""  # No support for empirical distributions !!!
        return

    def allowlist_event(self, event_type, sorted_log_lines, event_data, allowlisting_data):
        """
        Allowlist an event generated by this source using the information emitted when generating the event.
        @return a message with information about allowlisting
        @throws Exception when allowlisting of this special event using given allowlisting_data was not possible.
        """
        if event_type != 'Analysis.%s' % self.__class__.__name__:
            raise Exception('Event not from this source')
        raise Exception('No allowlisting for algorithm malfunction or configuration errors')

    def calculate_time_steps(self, counts, log_atom):
        """Returns a list of the timestep lenghts in seconds, if no timestep should be created the value is set to -1"""
        # List of the resulting time_steps
        time_step_list = []
        # Initialize time_window_history and arima_models
        self.time_window_history = [[] for _ in range(len(counts))]
        self.arima_models_statsmodels = [None for _ in range(len(counts))]
        # Minimal size of the time step
        min_lag = max(int(0.2*self.event_type_detector.num_sections_waiting_time_for_TSA),1)
        for data in counts:
            # Apply the autocorrelation function to the data of the single event types.
            corr = list(map(abs, statsmodels.api.tsa.acf(data, nlags=len(data), fft=True)[min_lag:]))
            corr = np.array(corr)
            # Apply the Savitzky-Golay-Filter to the list corr, to smooth the curve and get better results
            corrfit = savgol_filter(corr, min(max(3,int(len(corr)/10)-int(int(len(corr)/10) % 2 == 0)), 101), 1)
            
            # Find the highest peak and set the time-step as the index + lag
            highest_peak_index = np.argmax(corrfit)
            time_step_list.append((highest_peak_index + min_lag) / self.num_division_time_step)

        message = 'Calculated the time steps for the single event types in seconds: %s'%[time_step * self.num_division_time_step *
                self.event_type_detector.waiting_time_for_TSA / self.event_type_detector.num_sections_waiting_time_for_TSA
                for time_step in time_step_list]
        affected_path = None
        self.print(message, log_atom, affected_path)

        return time_step_list

    def test_num_appearance(self, event_number, count, current_time, log_atom):
        """This function makes a one step prediction and raises an alert if the count do not match the expected appearance"""
        # Append the list of time_window_history and arima_models if it is to short
        if len(self.time_window_history) <= event_number:
            self.time_window_history += [[] for _ in range(event_number + 1 - len(self.time_window_history))]
            self.arima_models_statsmodels += [None for _ in range(event_number + 1 - len(self.arima_models_statsmodels))]

        # Initialize the arima_model if needed
        if self.arima_models_statsmodels[event_number] == None:

            # Add the new count to the history and shorten it, if neccessary
            self.time_window_history[event_number].append(count)
            if len(self.time_window_history[event_number]) > 20 * self.num_division_time_step:
                self.time_window_history[event_number] = self.time_window_history[event_number][-10*self.num_division_time_step:]

            # Check if enough values have been stored to initialize the arima_model
            if len(self.time_window_history[event_number]) >= 10*self.num_division_time_step:
                message = 'Initializing the TSA for the eventtype %s'%event_number
                affected_path = self.event_type_detector.variable_key_list[event_number]
                self.print(message, log_atom, affected_path)
                
                if not self.build_sum_over_values:
                    # Add the arima_model to the list
                    try:
                        model = statsmodels.tsa.arima.model.ARIMA(self.time_window_history[event_number][-10*self.num_division_time_step:],
                                order=(self.num_division_time_step, 0, 0), seasonal_order=(0,0,0,self.num_division_time_step))
                        self.arima_models_statsmodels[event_number] = model.fit()

                        self.time_window_history[event_number] = []
                    except:
                        self.arima_models_statsmodels[event_number] = None
                else:
                    # Add the arima_model to the list
                    try:
                        model = statsmodels.tsa.arima.model.ARIMA([sum(self.time_window_history[event_number][-10*self.num_division_time_step+i:-9*self.num_division_time_step+i]) for i in range(9*self.num_division_time_step)]+[sum(self.time_window_history[event_number][-self.num_division_time_step:])],
                                order=(self.num_division_time_step, 0, 0), seasonal_order=(0,0,0,self.num_division_time_step))
                        self.arima_models_statsmodels[event_number] = model.fit()
                    except:
                        self.arima_models_statsmodels[event_number] = None
        # Add the new value and make a one step prediction
        else:
            if not self.build_sum_over_values:
                lower_limit, upper_limit = self.one_step_prediction(event_number)
                self.plots[0].append(lower_limit)
                self.plots[1].append(count)
                self.plots[2].append(upper_limit)
                self.time_history.append(current_time)

                # Test if count is in boundaries
                message = 'EventNumber: %s, Lower: %s, Count: %s, Upper: %s'%(event_number, lower_limit, count, upper_limit)
                #print(message)
                if count < lower_limit or count > upper_limit:
                    affected_path = self.event_type_detector.variable_key_list[event_number]
                    confidence = 1 - min(count / lower_limit, upper_limit / count)
                    self.print(message, log_atom, affected_path, confidence=confidence)

                # Update the model, for the next step
                self.arima_models_statsmodels[event_number] = self.arima_models_statsmodels[event_number].append([count])
            else:
                # Add the new count to the history and shorten it, if neccessary
                self.time_window_history[event_number].append(count)
                count_sum = sum(self.time_window_history[event_number][-self.num_division_time_step:])

                lower_limit, upper_limit = self.one_step_prediction(event_number)
                self.plots[0].append(lower_limit)
                self.plots[1].append(count_sum)
                self.plots[2].append(upper_limit)
                self.time_history.append(current_time)

                # Test if count_sum is in boundaries
                message = 'EventNumber: %s, Lower: %s, Count: %s, Upper: %s'%(event_number, lower_limit, count_sum, upper_limit)
                #print(message)
                if count_sum < lower_limit or count_sum > upper_limit:
                    affected_path = self.event_type_detector.variable_key_list[event_number]
                    confidence = 1 - min(count_sum / lower_limit, upper_limit / count_sum)
                    self.print(message, log_atom, affected_path, confidence=confidence)

                # Update the model, for the next step
                self.arima_models_statsmodels[event_number] = self.arima_models_statsmodels[event_number].append([count_sum])

    def one_step_prediction(self, event_number):
        prediction = self.arima_models_statsmodels[event_number].get_forecast(1)
        prediction = prediction.conf_int(alpha=self.alpha)
        # return in the order: pred, lower_limit, upper_limit
        return prediction[0][0], prediction[0][1]

    def print(self, message, log_atom, affected_path, confidence=None):
        """Print the message."""
        if isinstance(affected_path, str):
            affected_path = [affected_path]

        original_log_line_prefix = None # self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX) # !!!
        if original_log_line_prefix is None:
            original_log_line_prefix = ''

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

        event_data = {'AnalysisComponent': analysis_component, 'TotalRecords': self.event_type_detector.total_records,
                      'TypeInfo': {'Confidence': confidence}}
        for listener in self.anomaly_event_handlers:
            listener.receive_event('Analysis.%s' % self.__class__.__name__, message, sorted_log_lines, event_data, log_atom, self)
