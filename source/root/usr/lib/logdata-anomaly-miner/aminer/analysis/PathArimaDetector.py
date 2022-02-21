"""
This module is a detector which uses a tsa-arima model to analyze the values of the paths in target_path_list.

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
import sys
import statsmodels
import statsmodels.api as sm
from scipy.stats import binom_test

from aminer import AminerConfig
from aminer.AminerConfig import KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD, DEBUG_LOG_NAME, CONFIG_KEY_LOG_LINE_PREFIX,\
    DEFAULT_LOG_LINE_PREFIX
from aminer.AnalysisChild import AnalysisContext
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface
from aminer.util import PersistenceUtil


class PathArimaDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """This class is used for an arima time series analysis of the values of the paths in target_path_list."""

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, anomaly_event_handlers, event_type_detector, persistence_id='Default', target_path_list=None,
                 output_log_line=True, auto_include_flag=False, num_init=50, force_period_length=False, set_period_length=10, alpha=0.05,
                 alpha_bt=0.05, num_results_bt=15, num_min_time_history=20, num_max_time_history=30, num_periods_tsa_ini=20):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param event_type_detector used to track the number of events in the time windows.
        @param persistence_id name of persistency document.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that values are analyzed by their combined
        occurrences. When no paths are specified, the events given by the full path list are analyzed.
        @param output_log_line specifies whether the full parsed log atom should be provided in the output.
        @param auto_include_flag specifies whether new frequency measurements override ground truth frequencies.
        @param num_init number of lines processed before the period length is calculated.
        @param force_period_length states if the period length is calculated through the ACF, or if the period length is forced to
        be set to set_period_length.
        @param set_period_length states how long the period length is if force_period_length is set to True.
        @param alpha significance level of the estimated values.
        @param alpha_bt significance level for the bt test.
        @param num_results_bt number of results which are used in the binomial test.
        @param num_min_time_history number of lines processed before the period length is calculated.
        @param num_max_time_history maximum number of values of the time_history.
        @param num_periods_tsa_ini number of periods used to initialize the Arima-model.
        """
        self.aminer_config = aminer_config
        self.anomaly_event_handlers = anomaly_event_handlers
        self.event_type_detector = event_type_detector
        # Add the PathArimaDetector to the list of the modules, which use the event_type_detector.
        self.event_type_detector.add_following_modules(self)
        self.persistence_id = persistence_id
        self.target_path_list = target_path_list
        if self.target_path_list is None:
            self.target_path_list = []
        self.output_log_line = output_log_line
        self.auto_include_flag = auto_include_flag
        self.num_init = num_init
        self.force_period_length = force_period_length
        self.set_period_length = set_period_length
        self.alpha = alpha
        self.alpha_bt = alpha_bt
        self.num_results_bt = num_results_bt
        self.num_min_time_history = num_min_time_history
        self.num_max_time_history = num_max_time_history
        self.num_periods_tsa_ini = num_periods_tsa_ini

        # Test if the ETD saves the values
        if not self.event_type_detector.save_values:
            msg = 'Changed the parameter save_values of the VTD from False to True to properly use the PathArimaDetector'
            logging.getLogger(DEBUG_LOG_NAME).warning(msg)
            print('WARNING: ' + msg, file=sys.stderr)
            self.event_type_detector.save_values = True

        # Test if the ETD saves enough values
        if self.event_type_detector.min_num_vals < self.num_periods_tsa_ini * int(self.num_init/2):
            msg = 'Changed the parameter min_num_vals of the ETD from %s to %s to properly use the PathArimaDetector' % (
                    self.event_type_detector.min_num_vals, self.num_periods_tsa_ini * int(self.num_init/2))
            logging.getLogger(DEBUG_LOG_NAME).warning(msg)
            print('WARNING: ' + msg, file=sys.stderr)
            self.event_type_detector.min_num_vals = self.num_periods_tsa_ini * int(self.num_init/2)

        # Test if the ETD saves enough values
        if self.event_type_detector.max_num_vals < self.num_periods_tsa_ini * int(self.num_init/2) + 500:
            msg = 'Changed the parameter max_num_vals of the ETD from %s to %s to use pregenerated critical values for the gof-test' % (
                    self.event_type_detector.max_num_vals, self.num_periods_tsa_ini * int(self.num_init/2) + 500)
            logging.getLogger(DEBUG_LOG_NAME).warning(msg)
            print('WARNING: ' + msg, file=sys.stderr)
            self.event_type_detector.max_num_vals = self.num_periods_tsa_ini * int(self.num_init/2) + 500

        self.next_persist_time = time.time() + self.aminer_config.config_properties.get(KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)
        # List of the indices of the target_paths in the ETD
        self.target_path_index_list = []
        # List of the period_lengths
        self.period_length_list = []
        # List of the the single arima_models (statsmodels)
        self.arima_models = []
        # List of the observed values and the predictions of the TSAArima
        self.prediction_history = []
        # List of the the results if th value was in the limits of the one step predictions
        self.result_list = []
        # Minimal number of successes for the binomial test in the last num_results_bt results
        self.bt_min_suc = self.bt_min_successes(self.num_results_bt, self.alpha, self.alpha_bt)

        # Loads the persistence
        self.persistence_file_name = AminerConfig.build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)
        self.load_persistence_data()

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
        persistence_data = []
        persistence_data.append(self.target_path_index_list)
        persistence_data.append(self.period_length_list)
        persistence_data.append(self.prediction_history)
        PersistenceUtil.store_json(self.persistence_file_name, persistence_data)

        logging.getLogger(DEBUG_LOG_NAME).debug('%s persisted data.', self.__class__.__name__)

    def load_persistence_data(self):
        """Load the persistence data from storage."""
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)

        if persistence_data is not None:
            self.target_path_index_list = persistence_data[0]
            self.period_length_list = persistence_data[1]
            self.prediction_history = persistence_data[2]

    def receive_atom(self, log_atom):
        """
        Receive an parsed atom and the information about the parser match. Tests if the event type includes paths of target_path_list and
        analyzes their values with an TSA Arima model.
        @param log_atom the parsed log atom
        @return True if this handler was really able to handle and process the match.
        """
        event_index = self.event_type_detector.current_index

        # Check if enough log lines have appeared to calculate the period length, initilize the arima model, or make a prediction
        if (len(self.period_length_list) <= event_index or self.period_length_list[event_index] is None) and\
                len(self.event_type_detector.values[self.event_type_detector.current_index][0]) >= self.num_init:
            # Extend the list of the period_lengths and target_path_index if necessary
            if len(self.period_length_list) <= event_index:
                self.period_length_list += [None for _ in range(len(self.period_length_list), event_index + 2)]
                self.target_path_index_list += [None for _ in range(len(self.target_path_index_list), event_index + 2)]

            # Add all paths to the target_path_list if they are included in the ET and solely consist of floats
            self.target_path_index_list[event_index] = []
            for target_path in self.target_path_list:
                if target_path in self.event_type_detector.variable_key_list[event_index]:
                    var_index = self.event_type_detector.variable_key_list[event_index].index(target_path)
                    if all(type(val) is float for val in self.event_type_detector.values[event_index][var_index]):
                        self.target_path_index_list[event_index].append(var_index)

            # Calculate the period_length of the current event types values
            counts = [self.event_type_detector.values[event_index][var_index] for var_index in self.target_path_index_list[event_index]]
            self.calculate_period_length(event_index, counts, log_atom)

            # Try to initilize the arima model
            self.test_num_appearance(event_index, log_atom)
        elif len(self.period_length_list) > event_index and self.period_length_list[event_index] is not None:
            # Try to initilize or make a prediction with the arima model
            self.test_num_appearance(event_index, log_atom)

        return True

    def calculate_period_length(self, event_index, counts, log_atom):
        """Returns a list of the period length, if no period was found the value is set to -1"""
        if self.force_period_length:
            # Check if the period length should be forced
            self.period_length_list[event_index] = [self.set_period_length for _ in counts]
        else:
            # Calculate the period lengths with the auto correlation function
            self.period_length_list[event_index] = [None for _ in counts]

            for target_path_index, data in enumerate(counts):
                if data is not None:
                    # Apply the autocorrelation function to the data of the single target_paths.
                    corr = list(map(abs, sm.tsa.acf(data, nlags=len(data), fft=True)))
                    corr = np.array(corr)
                    min_lag = -1

                    # Find the first local minimum
                    for i in range(1, len(corr)-1):
                        if corr[i] == min(corr[i-1: i+2]):
                            min_lag = i
                            break

                    # Find the highest peak and set the time-step as the index + lag
                    if min_lag != -1:
                        highest_peak_index = np.argmax(corr[min_lag:])
                        self.period_length_list[event_index][target_path_index] = int(highest_peak_index + min_lag)

        # Print a message of the length of the time steps
        message = 'Calculated the periods for the event %s: %s' % (
                self.event_type_detector.get_event_type(event_index), self.period_length_list[event_index])
        affected_path = self.event_type_detector.variable_key_list[event_index]
        self.print(message, log_atom, affected_path)

    def test_num_appearance(self, event_index, log_atom):
        """This function makes a one step prediction and raises an alert if the count do not match the expected appearance"""
        # Return, if not TSA should be calculated for this ET
        if all(period is None for period in self.period_length_list[event_index]):
            return

        # Append the lists for the arima models if it is to short
        if len(self.arima_models) <= event_index:
            self.arima_models += [None for _ in range(event_index + 1 - len(self.arima_models))]
            self.result_list += [None for _ in range(event_index + 1 - len(self.result_list))]
        if len(self.prediction_history) <= event_index:
            self.prediction_history += [None for _ in range(event_index + 1 - len(self.prediction_history))]

        # Initialize the lists for the arima models for this ET
        if self.arima_models[event_index] is None:
            self.arima_models[event_index] = [None for _ in range(len(self.target_path_index_list[event_index]))]
            self.result_list[event_index] = [[] for _ in range(len(self.target_path_index_list[event_index]))]
        if self.prediction_history[event_index] is None:
            self.prediction_history[event_index] = [[[], [], []] for _ in range(len(self.target_path_index_list[event_index]))]

        # Check if the new values are floats
        if any(not self.event_type_detector.check_variables[event_index][var_index] or
                not isinstance(self.event_type_detector.values[event_index][var_index][-1], float) for var_index in
                self.target_path_index_list[event_index]):
            delete_indices = [count_index for count_index, var_index in enumerate(self.target_path_index_list[event_index])
                              if not self.event_type_detector.check_variables[event_index][var_index] or
                              not isinstance(self.event_type_detector.values[event_index][var_index][-1], float)]
            delete_indices.sort(reverse=True)

            for count_index in delete_indices:
                # Remove the entries of the lists
                if len(self.target_path_index_list) > event_index and len(self.target_path_index_list[event_index]) > count_index:
                    self.target_path_index_list[event_index] = self.target_path_index_list[event_index][:count_index] +\
                            self.target_path_index_list[event_index][count_index + 1:]
                if len(self.period_length_list) > event_index and len(self.period_length_list[event_index]) > count_index:
                    self.period_length_list[event_index] = self.period_length_list[event_index][:count_index] +\
                            self.period_length_list[event_index][count_index + 1:]
                if len(self.arima_models) > event_index and len(self.arima_models[event_index]) > count_index:
                    self.arima_models[event_index] = self.arima_models[event_index][:count_index] +\
                            self.arima_models[event_index][count_index + 1:]
                if len(self.prediction_history) > event_index and len(self.prediction_history[event_index]) > count_index:
                    self.prediction_history[event_index] = self.prediction_history[event_index][:count_index] +\
                            self.prediction_history[event_index][count_index + 1:]
                if len(self.result_list) > event_index and len(self.result_list[event_index]) > count_index:
                    self.result_list[event_index] = self.result_list[event_index][:count_index] +\
                            self.result_list[event_index][count_index + 1:]

            message = 'Disabled the TSA for the targetpaths %s of event %s' % (
                    [self.event_type_detector.variable_key_list[event_index][count_index] for count_index in delete_indices],
                    self.event_type_detector.get_event_type(event_index))
            affected_path = [self.event_type_detector.variable_key_list[event_index][count_index] for count_index in delete_indices]
            self.print(message, log_atom, affected_path)

        # Initialize and update the arima_model if possible
        for count_index, var_index in enumerate(self.target_path_index_list[event_index]):
            # Initialize the arima_model if possible if possible
            if self.auto_include_flag and self.arima_models[event_index][count_index] is None:
                if self.period_length_list[event_index][count_index] is not None:

                    # Add the current value to the lists
                    self.prediction_history[event_index][count_index][0].append(0)
                    self.prediction_history[event_index][count_index][1].append(self.event_type_detector.values[event_index][var_index][-1])
                    self.prediction_history[event_index][count_index][2].append(0)

                    # Check if enough values have been stored to initialize the arima_model
                    if len(self.event_type_detector.values[event_index][var_index]) >= self.num_periods_tsa_ini *\
                            self.period_length_list[event_index][count_index]:
                        message = 'Initializing the TSA for the event %s and targetpath %s' % (
                                self.event_type_detector.get_event_type(event_index),
                                self.event_type_detector.variable_key_list[event_index][count_index])
                        affected_path = self.event_type_detector.variable_key_list[event_index][count_index]
                        self.print(message, log_atom, affected_path)

                        # Add the arima_model to the list
                        try:
                            model = statsmodels.tsa.arima.model.ARIMA(
                                    self.event_type_detector.values[event_index][var_index][
                                        -self.num_periods_tsa_ini * self.period_length_list[event_index][count_index]:],
                                    order=(self.period_length_list[event_index][count_index], 0, 0),
                                    seasonal_order=(0, 0, 0, self.period_length_list[event_index][count_index]))
                            self.arima_models[event_index][count_index] = model.fit()
                        except:  # skipcq FLK-E722
                            self.arima_models[event_index][count_index] = None

            # Make a one step prediction with the new values
            elif self.arima_models[event_index][count_index] is not None:
                count = self.event_type_detector.values[event_index][var_index][-1]

                # Add the predction to the lists
                lower_limit, upper_limit = self.one_step_prediction(event_index, count_index)
                self.prediction_history[event_index][count_index][0].append(lower_limit)
                self.prediction_history[event_index][count_index][1].append(count)
                self.prediction_history[event_index][count_index][2].append(upper_limit)

                # Shorten the lists if neccessary
                if len(self.prediction_history[event_index][count_index][0]) > self.num_max_time_history:
                    self.prediction_history[event_index][count_index][0] = self.prediction_history[event_index][count_index][0][
                        -self.num_min_time_history:]
                    self.prediction_history[event_index][count_index][1] = self.prediction_history[event_index][count_index][1][
                        -self.num_min_time_history:]
                    self.prediction_history[event_index][count_index][2] = self.prediction_history[event_index][count_index][2][
                        -self.num_min_time_history:]

                else:
                    # Test if count is in boundaries
                    if count < lower_limit or count > upper_limit:
                        message = 'Event: %s, Path: %s, Lower: %s, Count: %s, Upper: %s' % (
                                self.event_type_detector.get_event_type(event_index),
                                self.event_type_detector.variable_key_list[event_index][var_index], lower_limit, count, upper_limit)
                        affected_path = self.event_type_detector.variable_key_list[event_index][var_index]
                        if count < lower_limit:
                            confidence = (lower_limit - count) / (upper_limit - count)
                        else:
                            confidence = (count - upper_limit) / (count - lower_limit)
                        self.print(message, log_atom, affected_path, confidence=confidence)
                        self.result_list[event_index][count_index].append(0)
                    else:
                        self.result_list[event_index][count_index].append(1)

                    # Reduce the number of entries in the time history if it gets too large
                    if len(self.result_list[event_index][count_index]) >= 2 * max(
                            self.num_results_bt, self.num_periods_tsa_ini * self.period_length_list[event_index][count_index]):
                        self.result_list[event_index][count_index] = self.result_list[event_index][count_index][-max(
                            self.num_results_bt, self.num_periods_tsa_ini * self.period_length_list[event_index][count_index]):]

                # Check if the too few or many successes are in the last section of the test history and discard the model
                # Else update the model for the next step
                if self.auto_include_flag and (
                        sum(self.result_list[event_index][count_index][-self.num_results_bt:]) +
                        max(0, self.num_results_bt - len(self.result_list[event_index][count_index])) < self.bt_min_suc or
                        binom_test(x=sum(self.result_list[event_index][count_index][
                        -self.num_periods_tsa_ini * self.period_length_list[event_index][count_index]:]),
                        n=self.num_periods_tsa_ini * self.period_length_list[event_index][count_index],
                        p=(1-self.alpha), alternative='greater') < self.alpha_bt):

                    message = 'Discard the TSA model for the event %s and path %s' % (
                            self.event_type_detector.get_event_type(event_index),
                            self.event_type_detector.variable_key_list[event_index][var_index])
                    affected_path = self.event_type_detector.variable_key_list[event_index][var_index]
                    self.print(message, log_atom, affected_path)

                    # Discard the trained model and reset the result_list
                    self.arima_models[event_index][count_index] = None
                    self.result_list[event_index][count_index] = []
                else:
                    # Update the model
                    self.arima_models[event_index][count_index] = self.arima_models[event_index][count_index].append([count])

    def one_step_prediction(self, event_index, count_index):
        """Make a one step prediction with the Arima model"""
        prediction = self.arima_models[event_index][count_index].get_forecast(1)
        prediction = prediction.conf_int(alpha=self.alpha)

        # return in the order: lower_limit, upper_limit
        return prediction[0][0], prediction[0][1]

    def bt_min_successes(self, num_bt, p, alpha):  # skipcq: PYL-R0201
        """
        Calculate the minimal number of successes for the BT with significance alpha.
        p is the probability of success and num_bt is the number of observed tests.
        """
        tmp_sum = 0.0
        max_observations_factorial = np.math.factorial(num_bt)
        i_factorial = 1
        for i in range(num_bt + 1):
            i_factorial = i_factorial * max(i, 1)
            tmp_sum = tmp_sum + max_observations_factorial / (i_factorial * np.math.factorial(num_bt - i)) * ((1 - p) ** i) * (
                p ** (num_bt - i))
            if tmp_sum > alpha:
                return i
        return num_bt

    def print(self, message, log_atom, affected_path, confidence=None):
        """Print the message."""
        if isinstance(affected_path, str):
            affected_path = [affected_path]

        original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
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

        event_data = {'AnalysisComponent': analysis_component, 'TotalRecords': self.event_type_detector.total_records, 'TypeInfo': {}}
        if self.event_type_detector.id_path_list != []:
            event_data['IDpaths'] = self.event_type_detector.id_path_list
            event_data['IDvalues'] = list(self.event_type_detector.id_path_list_tuples[self.event_type_detector.current_index])
        if confidence is not None:
            event_data['TypeInfo']['Confidence'] = confidence
        for listener in self.anomaly_event_handlers:
            listener.receive_event('Analysis.%s' % self.__class__.__name__, message, sorted_log_lines, event_data, log_atom, self)
