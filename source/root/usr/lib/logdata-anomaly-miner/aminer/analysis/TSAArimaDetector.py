"""
This module is a detector which uses a tsa-arima model to track appearance frequencies of events.

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

from aminer import AminerConfig
from aminer.AminerConfig import KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD, DEBUG_LOG_NAME, CONFIG_KEY_LOG_LINE_PREFIX,\
    DEFAULT_LOG_LINE_PREFIX
from aminer.AnalysisChild import AnalysisContext
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface
from aminer.util import PersistenceUtil

import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import acf
from scipy.signal import savgol_filter


class TSAArimaDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """This class is used for an arima time series analysis of the appearances of log lines to events."""

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, anomaly_event_handlers, event_type_detector, acf_pause_interval_percentage=0.2,
                 acf_auto_pause_interval=True, acf_auto_pause_interval_num_min=10, build_sum_over_values=False, num_periods_tsa_ini=15,
                 num_division_time_step=10, alpha=0.05, num_min_time_history=20, num_max_time_history=30, num_results_bt=15, alpha_bt=0.05,
                 acf_threshold=0.2, round_time_inteval_threshold=0.02, force_period_length=False, set_period_length=604800,
                 min_log_lines_per_time_step=10, persistence_id='Default', path_list=None, ignore_list=None, output_log_line=True,
                 auto_include_flag=True, stop_learning_time=None, stop_learning_no_anomaly_time=None):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param event_type_detector used to track the number of events in the time windows.
        @param acf_pause_interval_percentage states which area of the resutls of the ACF are not used to find the highest peak.
        @param acf_auto_pause_interval states if the pause area is automatically set.
        If enabled, the variable acf_pause_interval_percentage loses its functionality.
        @param acf_auto_pause_interval_num_min states the number of values in which a local minima must be the minimum, to be considered a
        local minimum of the function and not an outlier.
        @param build_sum_over_values states if the sum of a series of counts is build before applying the TSA.
        @param num_periods_tsa_ini number of periods used to initialize the Arima-model.
        @param num_division_time_step number of division of the time window to calculate the time step.
        @param alpha significance level of the estimated values.
        @param num_min_time_history number of lines processed before the period length is calculated.
        @param num_max_time_history maximum number of values of the time_history.
        @param num_results_bt number of results which are used in the binomial test.
        @param alpha_bt significance level for the bt test.
        @param round_time_inteval_threshold threshold for the rounding of the time_steps to the times in self.assumed_time_steps.
        The higher the threshold the easier the time is rounded to the next time in the list.
        @param acf_threshold threshold, which has to be exceeded by the highest peak of the cdf function of the time series, to be analysed.
        @param force_period_length states if the period length is calculated through the ACF, or if the period length is forced to
        be set to set_period_length.
        @param set_period_length states how long the period length is if force_period_length is set to True.
        @param min_log_lines_per_time_step states the minimal average number of log lines per time step to make a TSA.
        @param persistence_id name of persistency document.
        @param path_list At least one of the parser paths in this list needs to appear in the event to be analysed.
        @param ignore_list list of paths that are not considered for correlation, i.e., events that contain one of these paths are
        omitted. The default value is [] as None is not iterable.
        @param output_log_line specifies whether the full parsed log atom should be provided in the output.
        @param auto_include_flag specifies whether new frequency measurements override ground truth frequencies.
        @param stop_learning_time switch the learn_mode to False after the time.
        @param stop_learning_no_anomaly_time switch the learn_mode to False after no anomaly was detected for that time.
        """
        self.aminer_config = aminer_config
        self.next_persist_time = time.time() + self.aminer_config.config_properties.get(KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)
        self.anomaly_event_handlers = anomaly_event_handlers
        self.output_log_line = output_log_line
        self.auto_include_flag = auto_include_flag
        self.path_list = path_list
        if self.path_list is None:
            self.path_list = []
        self.ignore_list = ignore_list
        if self.ignore_list is None:
            self.ignore_list = []

        self.event_type_detector = event_type_detector
        self.acf_pause_interval_percentage = acf_pause_interval_percentage
        self.acf_auto_pause_interval = acf_auto_pause_interval
        self.acf_auto_pause_interval_num_min = acf_auto_pause_interval_num_min
        self.build_sum_over_values = build_sum_over_values
        self.num_periods_tsa_ini = num_periods_tsa_ini
        self.num_division_time_step = num_division_time_step
        self.alpha = alpha
        self.num_min_time_history = num_min_time_history
        self.num_max_time_history = num_max_time_history
        self.num_results_bt = num_results_bt
        self.alpha_bt = alpha_bt
        self.round_time_inteval_threshold = round_time_inteval_threshold
        self.acf_threshold = acf_threshold
        self.force_period_length = force_period_length
        self.set_period_length = set_period_length
        self.min_log_lines_per_time_step = min_log_lines_per_time_step

        # Add the TSAArimaDetector-module to the list of the modules, which use the event_type_detector.
        self.event_type_detector.add_following_modules(self)

        # History of the time windows
        self.time_window_history = []
        # List of the the single arima_models (statsmodels)
        self.arima_models = []
        # List of the observed values and the predictions of the TSAArima
        self.prediction_history = []
        # List of the times of the observations
        self.time_history = []
        # List of the the results if th value was in the limits of the one step predictions
        self.result_list = []
        # Minimal number of successes for the binomial test
        self.bt_min_suc = self.bt_min_successes(self.num_results_bt, self.alpha, self.alpha_bt)
        # Assumed occuring time steps in seconds. 1 minute: 60, 1 hour: 3600, 12 hours: 43200, 1 day: 86400, 1 week: 604800.
        self.assumed_time_steps = [60, 3600, 43200, 86400, 604800]

        # Load the persistence
        self.persistence_id = persistence_id
        self.persistence_file_name = AminerConfig.build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)

        if auto_include_flag is False and (stop_learning_time is not None or stop_learning_no_anomaly_time is not None):
            msg = "It is not possible to use the stop_learning_time or stop_learning_no_anomaly_time when the learn_mode is False."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        if stop_learning_time is not None and stop_learning_no_anomaly_time is not None:
            msg = "stop_learning_time is mutually exclusive to stop_learning_no_anomaly_time. Only one of these attributes may be used."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        if not isinstance(stop_learning_time, (type(None), int)):
            msg = "stop_learning_time has to be of the type int or None."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if not isinstance(stop_learning_no_anomaly_time, (type(None), int)):
            msg = "stop_learning_no_anomaly_time has to be of the type int or None."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)

        self.stop_learning_timestamp = None
        if stop_learning_time is not None:
            self.stop_learning_timestamp = time.time() + stop_learning_time
        self.stop_learning_no_anomaly_time = stop_learning_no_anomaly_time
        if stop_learning_no_anomaly_time is not None:
            self.stop_learning_timestamp = time.time() + stop_learning_no_anomaly_time

        # Import the persistence
        if persistence_data is not None:
            self.time_window_history = persistence_data[0]

            self.arima_models = [None for _ in self.time_window_history]
            # skipcq: PTC-W0060
            for event_index in range(len(self.arima_models)):
                if len(self.time_window_history[event_index]) >= self.num_periods_tsa_ini*self.num_division_time_step:
                    try:
                        if not self.build_sum_over_values:
                            model = ARIMA(
                                    self.time_window_history[event_index][-self.num_periods_tsa_ini*self.num_division_time_step:],
                                    order=(self.num_division_time_step, 0, 0), seasonal_order=(0, 0, 0, self.num_division_time_step))
                            self.arima_models[event_index] = model.fit()
                        else:
                            model = ARIMA([sum(self.time_window_history[event_index][
                                    -self.num_periods_tsa_ini*self.num_division_time_step+i:
                                    -(self.num_periods_tsa_ini-1)*self.num_division_time_step+i]) for i in
                                    range((self.num_periods_tsa_ini-1)*self.num_division_time_step)]+[
                                    sum(self.time_window_history[event_index][-self.num_division_time_step:])],
                                    order=(self.num_division_time_step, 0, 0), seasonal_order=(0, 0, 0, self.num_division_time_step))
                            self.arima_models[event_index] = model.fit()
                    except:  # skipcq FLK-E722
                        self.arima_models[event_index] = None
                        self.time_window_history[event_index] = []
                else:
                    self.arima_models[event_index] = None
                    self.time_window_history[event_index] = []

            self.prediction_history = persistence_data[1]
            self.time_history = persistence_data[2]
            self.result_list = persistence_data[3]

            # List of the pauses of the tests to the event numbers. If an arima model was initialized with the persistency, the model must
            # be trained before it can be used for forecasts. An integer states how many tests should be skipped before the next
            # output to this event number. None if no model was initialized for this event number.
            self.test_pause = [self.num_division_time_step if arima_models_statsmodel is not None else None for
                               arima_models_statsmodel in self.arima_models]
            # If all entries are None set the variable to None
            if all(entry is None for entry in self.test_pause):
                self.test_pause = None
        else:
            self.test_pause = None

    def receive_atom(self, log_atom):  # skipcq: PYL-W0613, PYL-R0201
        """
        Receive the atom and return True.
        The log_atom doesn't need to be analysed, because the counting and calls of the predictions is performed by the ETD.
        """
        return True

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
        persistence_data = [self.time_window_history, self.prediction_history, self.time_history, self.result_list]
        PersistenceUtil.store_json(self.persistence_file_name, persistence_data)

        logging.getLogger(DEBUG_LOG_NAME).debug('%s persisted data.', self.__class__.__name__)

    def allowlist_event(self, event_type, sorted_log_lines, event_data, allowlisting_data):  # skipcq: PYL-W0613
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
        # Initialize time_window_history
        self.time_window_history = [[] for _ in range(len(counts))]
        # Initialize arima_models
        self.arima_models = [None for _ in range(len(counts))]
        # Initialize prediction_history
        self.prediction_history = [[[], [], []] for _ in range(len(counts))]
        # Initialize time_history
        self.time_history = [[] for _ in range(len(counts))]
        # Initialize the lists of the results
        self.result_list = [[1]*self.num_results_bt for _ in range(len(counts))]

        if self.force_period_length:
            # Force the period length
            time_step_list = [self.set_period_length / self.num_division_time_step for count in counts]
        else:
            # Minimal size of the time step
            min_lag = max(int(self.acf_pause_interval_percentage*self.event_type_detector.num_sections_waiting_time_for_tsa), 1)

            for event_index, data in enumerate(counts):
                if (self.path_list != [] and all(path not in self.event_type_detector.found_keys[event_index] for path in self.path_list))\
                        or (self.ignore_list != [] and any(ignore_path in self.event_type_detector.found_keys[event_index] for ignore_path
                                                           in self.ignore_list)):
                    time_step_list.append(-1)
                else:
                    # Apply the autocorrelation function to the data of the single event types.
                    corr = list(map(abs, acf(data, nlags=len(data), fft=True)))
                    corr = np.array(corr)
                    # Apply the Savitzky-Golay-Filter to the list corr, to smooth the curve and get better results
                    corrfit = savgol_filter(corr, min(max(3, int(len(corr)/100)-int(int(len(corr)/100) % 2 == 0)), 101), 1)

                    # Set the pause area automatically
                    if self.acf_auto_pause_interval:
                        # Find the first local minima, which is the minimum in the last and next self.acf_auto_pause_interval_num_min values
                        for i in range(self.acf_auto_pause_interval_num_min, len(corrfit)-self.acf_auto_pause_interval_num_min):
                            if corrfit[i] == min(corrfit[i-self.acf_auto_pause_interval_num_min: i+self.acf_auto_pause_interval_num_min+1]):
                                min_lag = i
                                break

                    # Find the highest peak and set the time-step as the index + lag
                    highest_peak_index = np.argmax(corrfit[min_lag:])
                    if corrfit[min_lag + highest_peak_index] > self.acf_threshold:
                        time_step_list.append((highest_peak_index + min_lag) / self.num_division_time_step *
                                              self.event_type_detector.waiting_time_for_tsa /
                                              self.event_type_detector.num_sections_waiting_time_for_tsa)
                    else:
                        time_step_list.append(-1)

            # Round the time_steps if they are similar to the times in self.assumed_time_steps
            for index, time_step in enumerate(time_step_list):
                if time_step != -1:
                    for assumed_time_step in self.assumed_time_steps:
                        if abs(assumed_time_step - time_step * self.num_division_time_step) / assumed_time_step <\
                                self.round_time_inteval_threshold:
                            time_step_list[index] = assumed_time_step / self.num_division_time_step
                            break

        for index, time_step in enumerate(time_step_list):
            if time_step_list[index] != -1 and sum(counts[index]) / len(counts[index]) * time_step_list[index] /\
                    self.event_type_detector.waiting_time_for_tsa * self.event_type_detector.num_sections_waiting_time_for_tsa <\
                    self.min_log_lines_per_time_step:
                time_step_list[index] = -1

        # Print a message of the length of the time steps
        message = 'Calculated the periods for the single event types in seconds: %s' % [
                time_step * self.num_division_time_step if time_step != -1 else 'None' for time_step in time_step_list]
        affected_path = []
        self.print(message, log_atom, affected_path)

        return time_step_list

    def test_num_appearance(self, event_index, count, current_time, log_atom):
        """This function makes a one step prediction and raises an alert if the count do not match the expected appearance"""
        if self.auto_include_flag is True and self.stop_learning_timestamp is not None and \
                self.stop_learning_timestamp < log_atom.atom_time:
            logging.getLogger(DEBUG_LOG_NAME).info(f"Stopping learning in the {self.__class__.__name__}.")
            self.auto_include_flag = False

        # Append the list of time_window_history and arima_models if it is to short
        if len(self.time_window_history) <= event_index:
            self.time_window_history += [[] for _ in range(event_index + 1 - len(self.time_window_history))]
            self.arima_models += [None for _ in range(event_index + 1 - len(self.arima_models))]
            self.prediction_history += [[[], [], []] for _ in range(event_index + 1 - len(self.prediction_history))]
            self.time_history += [[] for _ in range(event_index + 1 - len(self.time_history))]
            self.result_list += [[1]*self.num_results_bt for _ in range(event_index + 1 - len(self.result_list))]

        # Initialize the arima_model if needed
        if self.auto_include_flag and self.arima_models[event_index] is None:

            # Add the new count to the history and shorten it, if necessary
            self.time_window_history[event_index].append(count)
            if len(self.time_window_history[event_index]) > 2 * self.num_periods_tsa_ini * self.num_division_time_step:
                self.time_window_history[event_index] = self.time_window_history[event_index][
                        -self.num_periods_tsa_ini*self.num_division_time_step:]

            # Check if enough values have been stored to initialize the arima_model
            if len(self.time_window_history[event_index]) >= self.num_periods_tsa_ini*self.num_division_time_step:
                message = 'Initializing the TSA for the event %s' % self.event_type_detector.get_event_type(event_index)
                affected_path = self.event_type_detector.variable_key_list[event_index]
                self.print(message, log_atom, affected_path)

                if not self.build_sum_over_values:
                    # Add the arima_model to the list
                    try:
                        model = ARIMA(
                                self.time_window_history[event_index][-self.num_periods_tsa_ini*self.num_division_time_step:],
                                order=(self.num_division_time_step, 0, 0), seasonal_order=(0, 0, 0, self.num_division_time_step))
                        self.arima_models[event_index] = model.fit()
                    except:  # skipcq FLK-E722
                        self.arima_models[event_index] = None
                else:
                    # Add the arima_model to the list
                    try:
                        model = ARIMA([sum(self.time_window_history[event_index][
                                -self.num_periods_tsa_ini*self.num_division_time_step+i:
                                -(self.num_periods_tsa_ini-1)*self.num_division_time_step+i]) for i in
                                range((self.num_periods_tsa_ini-1)*self.num_division_time_step)]+[
                                sum(self.time_window_history[event_index][-self.num_division_time_step:])],
                                order=(self.num_division_time_step, 0, 0), seasonal_order=(0, 0, 0, self.num_division_time_step))
                        self.arima_models[event_index] = model.fit()
                    except:  # skipcq FLK-E722
                        self.arima_models[event_index] = None
                        self.time_window_history[event_index] = []
            if self.stop_learning_timestamp is not None and self.stop_learning_no_anomaly_time is not None:
                self.stop_learning_timestamp = time.time() + self.stop_learning_no_anomaly_time
        # Add the new value and make a one step prediction
        elif self.arima_models[event_index] is not None:
            if not self.build_sum_over_values:
                # Add the predction and time to the lists
                lower_limit, upper_limit = self.one_step_prediction(event_index)
                if self.test_pause is not None and len(self.test_pause) > event_index and self.test_pause[event_index] is not None:
                    self.prediction_history[event_index][0].append(0)
                    self.prediction_history[event_index][1].append(count)
                    self.prediction_history[event_index][2].append(0)
                    self.time_history[event_index].append(current_time)
                else:
                    self.prediction_history[event_index][0].append(lower_limit)
                    self.prediction_history[event_index][1].append(count)
                    self.prediction_history[event_index][2].append(upper_limit)
                    self.time_history[event_index].append(current_time)
                # Shorten the lists if neccessary
                if len(self.time_history[event_index]) > self.num_max_time_history:
                    self.prediction_history[event_index][0] = self.prediction_history[event_index][0][-self.num_min_time_history:]
                    self.prediction_history[event_index][1] = self.prediction_history[event_index][1][-self.num_min_time_history:]
                    self.prediction_history[event_index][2] = self.prediction_history[event_index][2][-self.num_min_time_history:]
                    self.time_history[event_index] = self.time_history[event_index][-self.num_min_time_history:]

                if self.test_pause is not None and len(self.test_pause) > event_index and self.test_pause[event_index] is not None:
                    if self.test_pause[event_index] == 1:
                        self.test_pause[event_index] = None
                        # If all entries are None set the variable to None
                        if all(entry is None for entry in self.test_pause):
                            self.test_pause = None
                    else:
                        self.test_pause[event_index] -= 1
                else:
                    # Test if count is in boundaries
                    if count < lower_limit or count > upper_limit:
                        message = 'Event: %s, Lower: %s, Count: %s, Upper: %s' % (
                                self.event_type_detector.get_event_type(event_index), lower_limit, count, upper_limit)
                        affected_path = self.event_type_detector.variable_key_list[event_index]
                        if count < lower_limit:
                            confidence = (lower_limit - count) / (upper_limit - count)
                        else:
                            confidence = (count - upper_limit) / (count - lower_limit)
                        self.print(message, log_atom, affected_path, confidence=confidence)
                        self.result_list[event_index].append(0)
                    else:
                        self.result_list[event_index].append(1)

                    if len(self.result_list[event_index]) >= 2 * self.num_results_bt:
                        self.result_list[event_index] = self.result_list[event_index][-self.num_results_bt:]

                # Discard or update the model, for the next step
                if self.auto_include_flag and sum(self.result_list[event_index][-self.num_results_bt:]) < self.bt_min_suc:
                    message = 'Discard the TSA model for the event %s' % self.event_type_detector.get_event_type(event_index)
                    affected_path = self.event_type_detector.variable_key_list[event_index]
                    self.print(message, log_atom, affected_path)

                    # Discard the trained model and reset the result_list
                    self.arima_models[event_index] = None
                    self.result_list[event_index] = [1]*self.num_results_bt

                    if self.stop_learning_timestamp is not None and self.stop_learning_no_anomaly_time is not None:
                        self.stop_learning_timestamp = time.time() + self.stop_learning_no_anomaly_time
                else:
                    # Update the model
                    self.arima_models[event_index] = self.arima_models[event_index].append([count])

            else:
                # Add the new count to the history and shorten it, if neccessary
                self.time_window_history[event_index].append(count)
                count_sum = sum(self.time_window_history[event_index][-self.num_division_time_step:])

                # Add the predction and time to the lists
                lower_limit, upper_limit = self.one_step_prediction(event_index)
                self.prediction_history[event_index][0].append(lower_limit)
                self.prediction_history[event_index][1].append(count_sum)
                self.prediction_history[event_index][2].append(upper_limit)
                self.time_history[event_index].append(current_time)
                # Shorten the lists if neccessary
                if len(self.time_history[event_index]) > self.num_max_time_history:
                    self.prediction_history[event_index][0] = self.prediction_history[event_index][0][-self.num_min_time_history:]
                    self.prediction_history[event_index][1] = self.prediction_history[event_index][1][-self.num_min_time_history:]
                    self.prediction_history[event_index][2] = self.prediction_history[event_index][2][-self.num_min_time_history:]
                    self.time_history[event_index] = self.time_history[event_index][-self.num_min_time_history:]

                # Test if count_sum is in boundaries
                if count_sum < lower_limit or count_sum > upper_limit:
                    message = 'Event: %s, Lower: %s, Count: %s, Upper: %s' % (
                            self.event_type_detector.get_event_type(event_index), lower_limit, count_sum, upper_limit)
                    affected_path = self.event_type_detector.variable_key_list[event_index]
                    confidence = 1 - min(count_sum / lower_limit, upper_limit / count_sum)
                    self.print(message, log_atom, affected_path, confidence=confidence)

                # Update the model, for the next step
                self.arima_models[event_index] = self.arima_models[event_index].append([count_sum])

    def one_step_prediction(self, event_index):
        """Make a one step prediction with the Arima model"""
        prediction = self.arima_models[event_index].get_forecast(1)
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

        if confidence is not None:
            event_data = {'AnalysisComponent': analysis_component, 'TotalRecords': self.event_type_detector.total_records,
                          'TypeInfo': {'Confidence': confidence}}
        else:
            event_data = {'AnalysisComponent': analysis_component, 'TotalRecords': self.event_type_detector.total_records,
                          'TypeInfo': {}}
        for listener in self.anomaly_event_handlers:
            listener.receive_event('Analysis.%s' % self.__class__.__name__, message, sorted_log_lines, event_data, log_atom, self)
