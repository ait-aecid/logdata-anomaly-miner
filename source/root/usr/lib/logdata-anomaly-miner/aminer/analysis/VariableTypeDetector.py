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
import numpy as np
import copy
from scipy.stats import kstest, ks_2samp, norm, multinomial, distributions, chisquare
import os
import logging
import sys

from aminer.AminerConfig import build_persistence_file_name, DEBUG_LOG_NAME, KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD,\
    STAT_LOG_NAME, CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX
from aminer import AminerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.analysis.EventTypeDetector import EventTypeDetector
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface
from aminer.util import PersistenceUtil
import aminer.analysis.VTDData as VTDData


class VariableTypeDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """
    This class tests each variable of the event_types for the implemented variable types.
    This module needs to run after the event type detector is initialized
    """

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, anomaly_event_handlers, event_type_detector, persistence_id='Default', target_path_list=None,
                 used_gof_test='CM', gof_alpha=0.05, s_gof_alpha=0.05, s_gof_bt_alpha=0.05, d_alpha=0.1, d_bt_alpha=0.1, div_thres=0.3,
                 sim_thres=0.1, indicator_thres=0.4, num_init=100, num_update=50, num_update_unq=200, num_s_gof_values=50,
                 num_s_gof_bt=30, num_d_bt=30, num_pause_discrete=5, num_pause_others=2, test_gof_int=True,
                 num_stop_update=False, silence_output_without_confidence=False, silence_output_except_indicator=True,
                 num_var_type_hist_ref=10, num_update_var_type_hist_ref=10, num_var_type_considered_ind=10, num_stat_stop_update=200,
                 num_updates_until_var_reduction=20, var_reduction_thres=0.6, num_skipped_ind_for_weights=1, num_ind_for_weights=100,
                 used_multinomial_test='Chi', use_empiric_distr=True, used_range_test='MinMax', range_alpha=0.05, range_threshold=1,
                 num_reinit_range=100, range_limits_factor=1, dw_alpha=0.05, save_statistics=True, output_logline=True, ignore_list=None,
                 constraint_list=None, learn_mode=True, stop_learning_time=None, stop_learning_no_anomaly_time=None):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param event_type_detector used to track the number of occurring events.
        @param persistence_id name of persistence file.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that all values occurring in these paths are
        @param used_gof_test states the used test statistic for the continuous data type. Implemented are the 'KS' and 'CM' tests.
        @param gof_alpha significance niveau for p-value for the distribution test of the initialization. Recomended values are the
               implemented values of crit_val_ini_ks and crit_val_upd_ks or _cm.
        @param s_gof_alpha significance niveau for p-value for the sliding KS-test in the update step. Recommended values are the
               implemented values of crit_val_upd_ks.
        @param s_gof_bt_alpha significance niveau for the binomial test of the test results of the s_gof-test.
        @param d_alpha significance niveau for the binomialtest of the single discrete variables. If used_multinomial_test == 'Approx' then
               faster runtime for values in the p list of bt_min_succ_data.
        @param d_bt_alpha significance niveau for the binomialtest of the test results of the discrete tests.
        @param div_thres threshold for diversity of the values of a variable (the higher the more values have to be distinct to be
               considered to be continuous distributed).
        @param sim_thres threshold for similarity of the values of a variable (the higher the more values have to be common to be considered
               discrete).
        @param indicator_thres threshold for the variable indicators to be used in the event indicator.
        @param num_init number of lines processed before detecting the variable types. Recommended values are the implemented values of
               crit_val_ini_ks and crit_val_upd_ks or _cm.
        @param num_update number of values for which the variable type is updated. If used_multinomial_test == 'Approx' then faster runtime
               for values in the p list of bt_min_succ_data.
        @param num_update_unq number of values for which the values of type unq is unique (the last num_update + num_update_unq values are
               unique).
        @param num_s_gof_values number of values which are tested in the s_gof-test. The value has to be <= num_init, >= num_update.
               Recommended values are the implemented values of crit_val_upd_ks.
        @param num_s_gof_bt number of tested s_gof-Tests for the binomialtest of the testresults of the s_gof tests.
        @param num_d_bt number of tested discrete samples for the binomial test of the test results of the discrete tests.
        @param num_pause_discrete number of paused updates, before the discrete var type is adapted.
        @param num_pause_others number of paused update runs, before trying to find a new var_type.
        @param test_gof_int states if integer number should be tested for the continuous variable type.
        @param num_stop_update stops updating the found variable types after num_stop_update processed lines. If False the updating of lines
               will not be stopped.
        @param silence_output_without_confidence silences the all messages without a confidence-entry.
        @param silence_output_except_indicator silences the all messages which are not related with the calculated indicator.
        @param num_var_type_hist_ref states how long the reference for the var_type_hist_ref is. The reference is used in the evaluation.
        @param num_update_var_type_hist_ref number of update steps before the var_type_hist_ref is being updated.
        @param num_var_type_considered_ind this attribute states how many variable types of the history are used as the recent history in
               the calculation of the indicator. False if no output of the indicator should be generated.
        @param num_stat_stop_update number of static values of a variable, to stop tracking the variable type and read in the ETD.
               False if not wanted.
        @param num_updates_until_var_reduction number of update steps until the variables are tested if they are suitable for an indicator.
               If not suitable, they are removed from the tracking of ETD (reduce checked variables). Equals 0 if disabled.
        @param var_reduction_thres threshold for the reduction of variable types. The most likely none others var type must have a higher
               relative appearance for the variable to be further checked.
        @param num_skipped_ind_for_weights number of the skipped indicators for the calculation of the indicator weights.
        @param num_ind_for_weights number of indicators used in the calculation of the indicator weights.
        @param used_multinomial_test states the used multinomial test. Allowed values are 'MT', 'Approx' and 'Chi', where 'MT' means
               original MT, 'Approx' is the approximation with single BTs and 'Chi' is the Chi-square test.
        @param use_empiric_distr states if empiric distributions of the variables should be used if no continuous distribution is detected.
        @param used_range_test states the used method of range estimation. Allowed values are 'MeanSD', 'EmpiricQuantiles' and 'MinMax'.
               Where 'MeanSD' means the estimation through mean and standard deviation, 'EmpiricQuantiles' estimation through the empirical
               quantiles and 'MinMax' the estimation through minimum and maximum.
        @param range_alpha significance niveau for the range variable type.
        @param range_threshold maximal proportional deviation from the range before the variable type is rejected.
        @param num_reinit_range number of update steps until the range variable type is reinitialized. Set to zero if not desired.
        @param range_limits_factor factor for the limits of the range variable type.
        @param dw_alpha significance niveau of the durbin watson test to test serial correlation. If the test fails the type range is
               assigned to the variable instead of continuous.
        @param save_statistics used to track the indicators and changed variable types.
        @param output_logline specifies whether the full parsed log atom should be provided in the output.

        """
        # avoid "defined outside init" issue
        self.learn_mode, self.stop_learning_timestamp, self.next_persist_time, self.log_success, self.log_total = [None]*5
        super().__init__(
            mutable_default_args=["ignore_list", "constraint_list"], aminer_config=aminer_config,
            anomaly_event_handlers=anomaly_event_handlers, event_type_detector=event_type_detector, persistence_id=persistence_id,
            target_path_list=target_path_list, used_gof_test=used_gof_test, gof_alpha=gof_alpha, s_gof_alpha=s_gof_alpha,
            s_gof_bt_alpha=s_gof_bt_alpha, d_alpha=d_alpha, d_bt_alpha=d_bt_alpha, div_thres=div_thres, sim_thres=sim_thres,
            indicator_thres=indicator_thres, num_init=num_init, num_update=num_update, num_update_unq=num_update_unq,
            num_s_gof_values=num_s_gof_values, num_s_gof_bt=num_s_gof_bt, num_d_bt=num_d_bt, num_pause_discrete=num_pause_discrete,
            num_pause_others=num_pause_others, test_gof_int=test_gof_int, num_stop_update=num_stop_update,
            silence_output_without_confidence=silence_output_without_confidence,
            silence_output_except_indicator=silence_output_except_indicator, num_var_type_hist_ref=num_var_type_hist_ref,
            num_update_var_type_hist_ref=num_update_var_type_hist_ref, num_var_type_considered_ind=num_var_type_considered_ind,
            num_stat_stop_update=num_stat_stop_update, num_updates_until_var_reduction=num_updates_until_var_reduction,
            var_reduction_thres=var_reduction_thres, num_skipped_ind_for_weights=num_skipped_ind_for_weights,
            num_ind_for_weights=num_ind_for_weights, used_multinomial_test=used_multinomial_test, use_empiric_distr=use_empiric_distr,
            used_range_test=used_range_test, range_alpha=range_alpha, range_threshold=range_threshold, num_reinit_range=num_reinit_range,
            range_limits_factor=range_limits_factor, dw_alpha=dw_alpha, save_statistics=save_statistics, output_logline=output_logline,
            ignore_list=ignore_list, constraint_list=constraint_list, learn_mode=learn_mode, stop_learning_time=stop_learning_time,
            stop_learning_no_anomaly_time=stop_learning_no_anomaly_time
        )
        if not isinstance(self.event_type_detector, EventTypeDetector):
            msg = "event_type_detector must be an instance of EventTypeDetector."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if self.used_gof_test not in ("KS", "CM"):
            msg = "used_gof_test must be either 'KF' or 'CM'."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        if self.used_multinomial_test not in ("MT", "Approx", "Chi"):
            msg = "used_multinomial_test must be either 'MT', 'Approx' or 'Chi'."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        if self.used_range_test not in ("MeanSD", "EmpiricQuantiles", "MinMax"):
            msg = "used_range_test must be either 'MeanSD', 'EmpiricQuantiles' or 'MinMax'."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)

        # Initialization of variables, which are no input parameters
        # Saves the minimal number of successes for the BT for the s_gof-test
        self.s_gof_bt_min_success = self.bt_min_successes(self.num_s_gof_bt, 1 - self.s_gof_alpha, self.s_gof_bt_alpha)
        # Saves the minimal number of successes for the BT for discrete values
        self.d_bt_min_success = self.bt_min_successes(self.num_d_bt, 1 - self.d_alpha, self.d_bt_alpha)
        # Number of eventTypes
        self.num_events = 0
        # Add the variable_type_detector to the list of the modules, which use the event_type_detector.
        self.event_type_detector.add_following_modules(self)

        # List of the numbers of variables of the eventTypes
        self.length = []
        # Used to keep track of the indices of the variables if the target_path_list is not empty
        self.variable_path_num = []
        # List of the found vartypes
        self.var_type = []
        # Stores the alternative distribution types of continuous variables
        self.alternative_distribution_types = []
        # Stores the values the betam and special distributions. The values are needed in the s_gof test
        self.distr_val = []
        # List of the successes of the binomial test for the rejection in the s_gof or variables of discrete type
        self.bt_results = []
        # List of the history of variable types of the single variables. The lists to the variables take the form
        # [others, static, [discrete, number of appended steps], asc, desc, unique, range, ev of continuous distributions]
        self.var_type_history_list = []
        # Reference of a var_type_history_list. Used in the calculation of the indicator.
        self.var_type_history_list_reference = []
        # Order of the var_type_history_list [others, static, [discrete, number of appended steps], asc, desc, unique, range,
        # ev of continuous distributions]
        self.var_type_history_list_order = ['others', 'stat', 'd', 'asc', 'desc', 'unq', 'range', 'cont']
        # List of the distributions for which the s_gof test is implemented
        self.distr_list = ['nor', 'uni', 'spec', 'beta', 'betam', 'emp']
        # List of the numbers of log lines of this eventType, when an indicator failed
        self.failed_indicators = []
        # Stores the standardised values of all tested distributions for better performance. The list is hardcoded below
        self.quantiles = {}
        # Stores the number of minimal successes for the BT for selected sample-size and probabilities.
        self.bt_min_succ_data = {}

        self.log_success = 0
        self.log_total = 0
        self.log_new_learned = 0
        self.log_new_learned_values = []
        self.log_updated = 0

        # Initialize lists used for the tracking of the indicator
        if self.save_statistics:
            self.statistics_file_name = build_persistence_file_name(aminer_config, self.__class__.__name__, 'statistics')
            # List of the numbers of total parsed log lines, when an indicator failed. Only used for the statistics
            self.failed_indicators_total = []
            # List of the confidences of the indicators
            self.failed_indicators_values = []
            # List of the paths of the indicators
            self.failed_indicators_paths = []
            # List of the numbers of total parsed log lines, when a variable changed its type. Only used for the statistics
            self.changed_var_types = []

        # Stores the standardised values of all tested distributions for better performance.
        self.quantiles = VTDData.quantiles

        if self.used_multinomial_test == 'Approx':
            # Stores the number of minimal successes for the BT with the stated sample-sizes and probabilities
            self.bt_min_succ_data = VTDData.bt_min_succ_data

        # List of the maximal values to the significance niveau 'gof_alpha', the sample-size 'num_init' and the single
        # distributions in the initial KS-tests
        self.crit_val_ini_ks = VTDData.crit_val_ini_ks

        # List of the maximal values to the significance niveau 'gof_alpha', the samplesize 'num_init' and the single
        # distributions in the initial CM-tests
        self.crit_val_ini_cm = VTDData.crit_val_ini_cm

        # List of the maximal values to the significance niveau 'gof_alpha', the samplesize 'num_init' in the initialization and
        # the samplesize 'num_s_gof_values' in the update step and the single distributions in the s_ks-tests in the update steps
        self.crit_val_upd_ks = VTDData.crit_val_upd_ks

        # List of the maximal values to the significance niveau 'gof_alpha', the samplesize 'num_init' in the initialization and
        # the samplesize 'num_s_gof_values' in the update step and the single distributions in the s_cm-tests in the update steps
        self.crit_val_upd_cm = VTDData.crit_val_upd_cm

        # List of the critical distances to charactersitics of distributions.
        # These distances are used to prevent adapting too much on an anomalous sample in the gof tests.
        self.crit_dist_upd_cm = VTDData.crit_dist_upd_cm

        # List of the maximal values to the significance niveau 'gof_alpha', the samplesize 'num_init' in the initialization and
        # the samplesize 'num_s_gof_values' in the update steps for the CM-homogeneity test
        self.crit_val_hom_cm = VTDData.crit_val_hom_cm

        # List of the critical values of the durbin watson test
        self.crit_val_dw = VTDData.crit_val_dw

        if self.dw_alpha not in self.crit_val_dw:
            pos_vals = list(self.crit_val_dw.keys())

            nearest = self.crit_val_dw[0]
            for val in self.crit_val_dw[1:]:
                if abs(self.dw_alpha - val) < abs(self.dw_alpha - nearest):
                    nearest = val
            msg = f'Changed the parameter dw_alpha of the VTD from {self.dw_alpha} to {nearest} to use the pregenerated critical values ' \
                  f'for the dw-test'
            logging.getLogger(DEBUG_LOG_NAME).warning(msg)
            print('WARNING: ' + msg, file=sys.stderr)
            self.dw_alpha = nearest

        if num_init not in self.crit_val_dw[self.dw_alpha]:
            pos_vals = list(self.crit_val_dw[self.dw_alpha].keys())

            nearest = pos_vals[0]
            for val in pos_vals[1:]:
                if abs(num_init - val) < abs(num_init - nearest):
                    nearest = val
            msg = f'Changed the parameter num_init of the VTD from {num_init} to {nearest} to use the pregenerated critical values for ' \
                  f'the dw-test'
            logging.getLogger(DEBUG_LOG_NAME).warning(msg)
            print('WARNING: ' + msg, file=sys.stderr)
            self.num_init = nearest

        if (self.used_gof_test == 'KS' and (gof_alpha not in self.crit_val_ini_ks or gof_alpha not in self.crit_val_upd_ks)) or (
                self.used_gof_test == 'CM' and (gof_alpha not in self.crit_val_ini_cm or gof_alpha not in self.crit_val_upd_cm or
                                                gof_alpha not in self.crit_val_hom_cm)):
            if self.used_gof_test == 'KS':
                pos_vals = [val for val in self.crit_val_ini_ks if val in self.crit_val_upd_ks]
            else:
                pos_vals = [val for val in self.crit_val_ini_cm if val in self.crit_val_upd_cm and val in self.crit_val_hom_cm]

            nearest = pos_vals[0]
            for val in pos_vals[1:]:
                if abs(self.gof_alpha - val) < abs(self.gof_alpha - nearest):
                    nearest = val
            msg = f'Changed the parameter gof_alpha of the VTD from {self.gof_alpha} to {nearest} to use the pregenerated critical ' \
                  f'values for the gof-tests'
            logging.getLogger(DEBUG_LOG_NAME).warning(msg)
            print('WARNING: ' + msg, file=sys.stderr)
            self.gof_alpha = nearest

        if (self.used_gof_test == 'KS' and (num_init not in self.crit_val_ini_ks[self.gof_alpha] or num_init not in
                                            self.crit_val_upd_ks[self.gof_alpha])) or (
                self.used_gof_test == 'CM' and (num_init not in self.crit_val_ini_cm[self.gof_alpha] or
                                                num_init not in self.crit_val_upd_cm[self.gof_alpha] or
                                                num_init not in self.crit_val_hom_cm[self.gof_alpha])):
            if self.used_gof_test == 'KS':
                pos_vals = [val for val in self.crit_val_ini_ks[self.gof_alpha] if val in self.crit_val_upd_ks[self.gof_alpha]]
            else:
                pos_vals = [val for val in self.crit_val_ini_cm[self.gof_alpha] if val in self.crit_val_upd_cm[self.gof_alpha] and
                            val in self.crit_val_hom_cm[self.gof_alpha]]

            nearest = pos_vals[0]
            for val in pos_vals[1:]:
                if abs(num_init - val) < abs(num_init - nearest):
                    nearest = val
            msg = f'Changed the parameter num_init of the VTD from {num_init} to {nearest} to use the pregenerated critical values for' \
                  f' the gof-tests'
            logging.getLogger(DEBUG_LOG_NAME).warning(msg)
            print('WARNING: ' + msg, file=sys.stderr)
            self.num_init = nearest

        if (self.used_gof_test == 'KS' and (num_s_gof_values not in self.crit_val_upd_ks[self.gof_alpha][self.num_init])) or (
                self.used_gof_test == 'CM' and (num_s_gof_values not in self.crit_val_upd_cm[self.gof_alpha][self.num_init] or
                                                num_s_gof_values not in self.crit_val_hom_cm[self.gof_alpha][self.num_init])):
            if self.used_gof_test == 'KS':
                pos_vals = list(self.crit_val_upd_ks[self.gof_alpha][self.num_init].keys())
            else:
                pos_vals = [val for val in self.crit_val_upd_cm[self.gof_alpha][self.num_init] if val in
                            self.crit_val_hom_cm[self.gof_alpha][self.num_init]]

            nearest = pos_vals[0]
            for val in pos_vals[1:]:
                if abs(num_s_gof_values - val) < abs(num_s_gof_values - nearest):
                    nearest = val
            msg = f'Changed the parameter num_s_gof_values of the VTD from {num_s_gof_values} to {nearest} to use pregenerated ' \
                  f'critical values for the gof-test'
            logging.getLogger(DEBUG_LOG_NAME).warning(msg)
            print('WARNING: ' + msg, file=sys.stderr)
            self.num_s_gof_values = nearest

        # Test if the ETD saves the values
        if not self.event_type_detector.save_values:
            msg = 'Changed the parameter save_values of the VTD from False to True to properly use the PathArimaDetector'
            logging.getLogger(DEBUG_LOG_NAME).warning(msg)
            print('WARNING: ' + msg, file=sys.stderr)
            self.event_type_detector.save_values = True

        # Test if the ETD saves enough values
        if self.event_type_detector.min_num_vals < max(self.num_init, self.num_update, self.num_s_gof_values):
            msg = f'Changed the parameter min_num_vals of the ETD from {self.event_type_detector.min_num_vals} to ' \
                  f'{max(self.num_init, self.num_update, num_s_gof_values)} to use pregenerated critical values for the VTDs gof-test'
            logging.getLogger(DEBUG_LOG_NAME).warning(msg)
            print('WARNING: ' + msg, file=sys.stderr)
            self.event_type_detector.min_num_vals = max(self.num_init, self.num_update, self.num_s_gof_values)

        # Test if the ETD saves enough values
        if self.event_type_detector.max_num_vals < max(self.num_init, self.num_update, self.num_s_gof_values) + 500:
            msg = f'Changed the parameter max_num_vals of the ETD from {self.event_type_detector.max_num_vals} to ' \
                  f'{max(self.num_init, self.num_update, self.num_s_gof_values) + 500} to use pregenerated critical values for the VTDs' \
                  f' gof-test'
            logging.getLogger(DEBUG_LOG_NAME).warning(msg)
            print('WARNING: ' + msg, file=sys.stderr)
            self.event_type_detector.max_num_vals = max(self.num_init, self.num_update, self.num_s_gof_values) + 500

        # Loads the persistence
        self.persistence_file_name = build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)

        self.load_persistence_data()

        # Generate the modifiers for the estimation of the minimum and maximum for the uniform distribution
        self.min_mod_ini_uni = 1 / (self.num_init + 1)
        self.min_mod_upd_uni = 1 / (self.num_init + self.num_update + 1)
        self.max_mod_ini_uni = 1 / (self.num_init + 1)
        self.max_mod_upd_uni = 1 / (self.num_init + self.num_update + 1)

        # Generate the modifiers for the estimation of the minimum and maximum for the beta1 distribution
        self.min_mod_ini_beta1 = self.quantiles['beta1'][max(0.001, int(1 / (self.num_init + 1) * 1000 + 0.5) / 1000)]
        self.min_mod_upd_beta1 = self.quantiles['beta1'][max(0.001, int(1 / (self.num_init + self.num_update + 1) * 1000 + 0.5) / 1000)]
        self.max_mod_ini_beta1 = 1 - self.quantiles['beta1'][min(0.999, int(self.num_init / (self.num_init + 1) * 1000 + 0.5) / 1000)]
        self.max_mod_upd_beta1 = 1 - self.quantiles['beta1'][min(0.999, int((self.num_init + self.num_update) / (
                self.num_init + self.num_update + 1) * 1000 + 0.5) / 1000)]

        # Generate the modifiers for the estimation of the minimum and maximum for the beta2 distribution
        self.min_mod_ini_beta2 = self.quantiles['beta2'][max(0.001, int(1 / (self.num_init + 1) * 1000 + 0.5) / 1000)]
        self.min_mod_upd_beta2 = self.quantiles['beta2'][max(0.001, int(1 / (self.num_init + self.num_update + 1) * 1000 + 0.5) / 1000)]
        self.max_mod_ini_beta2 = 1-self.quantiles['beta2'][min(0.999, int(self.num_init / (self.num_init + 1) * 1000 + 0.5) / 1000)]
        self.max_mod_upd_beta2 = 1-self.quantiles['beta2'][min(0.999, int((self.num_init + self.num_update) / (
                self.num_init + self.num_update + 1) * 1000 + 0.5) / 1000)]

        # Generate the modifiers for the estimation of the minimum and maximum for the beta4 distribution
        self.min_mod_ini_beta4 = self.quantiles['beta4'][max(0.001, int(1 / (self.num_init + 1) * 1000 + 0.5) / 1000)]
        self.min_mod_upd_beta4 = self.quantiles['beta4'][max(0.001, int(1 / (self.num_init + self.num_update + 1) * 1000 + 0.5) / 1000)]
        self.max_mod_ini_beta4 = 1-self.quantiles['beta4'][min(0.999, int(self.num_init / (self.num_init + 1) * 1000 + 0.5) / 1000)]
        self.max_mod_upd_beta4 = 1-self.quantiles['beta4'][min(0.999, int((self.num_init + self.num_update) / (
                self.num_init + self.num_update + 1) * 1000 + 0.5) / 1000)]

    def receive_atom(self, log_atom):
        """
        Receive an parsed atom and the information about the parser match. Initializes Variables for new eventTypes.
        @param log_atom the parsed log atom
        @return True if this handler was really able to handle and process the match.
        """
        event_index = self.event_type_detector.current_index
        if event_index == -1:
            return False
        if self.learn_mode is True and self.stop_learning_timestamp is not None and \
                self.stop_learning_timestamp < log_atom.atom_time:
            logging.getLogger(DEBUG_LOG_NAME).info("Stopping learning in the %s.", self.__class__.__name__)
            self.learn_mode = False

        self.log_total += 1

        parser_match = log_atom.parser_match
        # Skip paths from ignore_list.
        for ignore_path in self.ignore_list:
            if ignore_path in parser_match.get_match_dictionary().keys():
                return False

        if self.target_path_list is None or len(self.target_path_list) == 0:
            constraint_path_flag = False
            for constraint_path in self.constraint_list:
                if parser_match.get_match_dictionary().get(constraint_path) is not None:
                    constraint_path_flag = True
                    break
            if not constraint_path_flag and self.constraint_list != []:
                return False

        # Initialize new entries in lists for a new eventType if necessary
        if len(self.length) < event_index + 1 or self.var_type[event_index] == []:
            for _ in range(event_index + 1 - len(self.length)):
                self.length.append(0)
                self.variable_path_num.append([])
                self.var_type.append([])
                self.alternative_distribution_types.append([])
                self.distr_val.append([])
                self.bt_results.append([])

            # Number of variables
            self.length[event_index] = len(self.event_type_detector.variable_key_list[event_index])
            # List of the found vartypes
            self.var_type[event_index] = [[] for i in range(self.length[event_index])]
            # Stores the alternative distributions of the variable
            self.alternative_distribution_types[event_index] = [[] for i in range(self.length[event_index])]
            # Stores the values the distribution, which are needed for the s_gof
            self.distr_val[event_index] = [[] for i in range(self.length[event_index])]
            # List of the successes of the binomial test for the rejection in the s_gof or variables of discrete type
            self.bt_results[event_index] = [[] for i in range(self.length[event_index])]

            # Adds the variable indices to the variable_path_num-list if the target_path_list is not empty
            if self.target_path_list is not None:
                for var_index in range(self.length[event_index]):
                    if self.event_type_detector.variable_key_list[event_index][var_index] in self.target_path_list:
                        self.variable_path_num[event_index].append(var_index)
            if self.num_events < event_index + 1:
                self.num_events = event_index + 1

        # Processes the current log-line by testing and updating
        self.process_ll(event_index, log_atom)
        return True

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
        tmp_list = [self.var_type, self.alternative_distribution_types, self.var_type_history_list,
                    self.var_type_history_list_reference, self.failed_indicators, [[self.distr_val[event_index][var_index] if (
                        len(self.distr_val[event_index][var_index]) > 0 and self.var_type[event_index][var_index][0] == 'emp') else [] for
                            var_index in range(len(self.distr_val[event_index]))] for event_index in range(len(self.distr_val))]]
        PersistenceUtil.store_json(self.persistence_file_name, tmp_list)

        if self.save_statistics:
            PersistenceUtil.store_json(self.statistics_file_name, [
                self.failed_indicators_total, self.failed_indicators_values, self.failed_indicators_paths, self.failed_indicators])
        logging.getLogger(DEBUG_LOG_NAME).debug('%s persisted data.', self.__class__.__name__)

    def load_persistence_data(self):
        """Extract the persistence data and appends various lists to create a consistent state."""
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        if persistence_data is not None:
            # Import the lists of the persistence
            self.var_type = persistence_data[0]
            self.alternative_distribution_types = persistence_data[1]
            self.var_type_history_list = persistence_data[2]
            self.var_type_history_list_reference = persistence_data[3]
            self.failed_indicators = persistence_data[4]
            self.distr_val = persistence_data[5]
            self.num_events = len(self.var_type)

            # Create the initial lists which derive from the persistence
            # Number of variables of the single events
            self.length = [len(self.event_type_detector.variable_key_list[event_index]) for event_index in range(self.num_events)]
            self.variable_path_num = [[] for _ in range(self.num_events)]
            # List of the successes of the binomialtest for the rejection in the s_gof or variables of discrete type
            self.bt_results = [[[] for var_index in range(self.length[event_index])] for event_index in range(self.num_events)]

            # Updates the lists for each eventType individually
            for event_index in range(self.num_events):
                # Adds the variable indices to the variable_path_num-list if the target_path_list is not empty
                if self.target_path_list is not None:
                    for var_index in range(self.length[event_index]):
                        if self.event_type_detector.variable_key_list[event_index][var_index] in self.target_path_list:
                            self.variable_path_num[event_index].append(var_index)

                # Initializes the lists for the discrete distribution, or continuous distribution
                for var_index, var_val in enumerate(self.var_type[event_index]):
                    if len(var_val) > 0:
                        if var_val[0] in self.distr_list:
                            self.bt_results[event_index][var_index] = [1] * self.num_s_gof_bt
                            if var_val[0] in ('betam', 'spec'):
                                self.s_gof_get_quantiles(event_index, var_index)
                        elif var_val[0] == 'd':
                            self.d_init_bt(event_index, var_index)
            logging.getLogger(DEBUG_LOG_NAME).debug('%s loaded persistence data.', self.__class__.__name__)

    def process_ll(self, event_index, log_atom):
        """Process the log line. Extracts and appends the values of the log line to the values-list."""
        # Return if no variable is tracked in the VTD
        if len(self.event_type_detector.variable_key_list[event_index]) == 0 or (
                self.target_path_list is not None and self.variable_path_num[event_index] == []):
            return

        # Initial detection of variable types
        if self.event_type_detector.num_event_lines[event_index] >= self.num_init and \
                self.event_type_detector.check_variables[event_index][0] and self.var_type[event_index][0] == []:
            # Test all variables

            logging.getLogger(DEBUG_LOG_NAME).debug('%s started initial detection of var types.', self.__class__.__name__)
            if self.target_path_list is None:
                for var_index in range(self.length[event_index]):
                    tmp_var_type = self.detect_var_type(event_index, var_index)

                    # VarType is empiric distribution
                    if tmp_var_type[0] == 'emp':
                        self.var_type[event_index][var_index] = tmp_var_type
                        self.bt_results[event_index][var_index] = [1] * self.num_s_gof_bt
                        self.s_gof_get_quantiles(event_index, var_index)

                    # VarType is a continuous distribution
                    elif tmp_var_type[0] in self.distr_list:
                        self.var_type[event_index][var_index] = tmp_var_type[:-1]
                        self.alternative_distribution_types[event_index][var_index] = tmp_var_type[-1]
                        self.bt_results[event_index][var_index] = [1] * self.num_s_gof_bt
                        if self.var_type[event_index][var_index][0] in ('betam', 'spec'):
                            self.s_gof_get_quantiles(event_index, var_index)

                    # Initializes the binomialtest for the discrete type
                    elif tmp_var_type[0] == 'd':
                        self.var_type[event_index][var_index] = tmp_var_type
                        self.d_init_bt(event_index, var_index)

                    # Mark the variables, which could be static parts of the parser model
                    elif tmp_var_type[0] == 'stat':
                        self.var_type[event_index][var_index] = tmp_var_type
                        self.var_type[event_index][var_index][2] = True

                    else:
                        self.var_type[event_index][var_index] = tmp_var_type

            # Test only the variables with paths in the target_path_list
            else:
                for var_index in self.variable_path_num[event_index]:
                    tmp_var_type = self.detect_var_type(event_index, var_index)

                    # VarType is empiric distribution
                    if tmp_var_type[0] == 'emp':
                        self.var_type[event_index][var_index] = tmp_var_type
                        self.bt_results[event_index][var_index] = [1] * self.num_s_gof_bt
                        self.s_gof_get_quantiles(event_index, var_index)

                    # VarType is a continuous distribution
                    elif tmp_var_type[0] in self.distr_list:
                        self.var_type[event_index][var_index] = tmp_var_type[:-1]
                        self.alternative_distribution_types[event_index][var_index] = tmp_var_type[-1]
                        self.bt_results[event_index][var_index] = [1] * self.num_s_gof_bt
                        if self.var_type[event_index][var_index][0] in ('betam', 'spec'):
                            self.s_gof_get_quantiles(event_index, var_index)

                    # VarType is range
                    elif tmp_var_type[0] == 'range':
                        self.var_type[event_index][var_index] = tmp_var_type

                    # Initializes the binomialtest for the discrete type
                    elif tmp_var_type[0] == 'd':
                        self.var_type[event_index][var_index] = tmp_var_type
                        self.d_init_bt(event_index, var_index)

                    # mMrk the variables, which could be static parts of the parser model
                    elif tmp_var_type[0] == 'stat':
                        self.var_type[event_index][var_index] = tmp_var_type
                        self.var_type[event_index][var_index][2] = True

                    else:
                        self.var_type[event_index][var_index] = tmp_var_type

            self.init_var_type_history_list(event_index)
            self.print_initial_var_type(event_index, log_atom)
            self.log_new_learned += len(self.var_type[event_index])
            self.log_new_learned_values.append(self.var_type[event_index])

        # Update variable types
        elif self.event_type_detector.num_event_lines[event_index] > self.num_init and (
                self.event_type_detector.num_event_lines[event_index] - self.num_init) % self.num_update == 0:

            logging.getLogger(DEBUG_LOG_NAME).debug('%s started update phase of var types.', self.__class__.__name__)
            # Check if the updates of the variable types should be stopped
            if self.learn_mode and (not isinstance(self.num_stop_update, bool)) and (
                    self.event_type_detector.total_records >= self.num_stop_update):
                self.learn_mode = False

            # Get the index_list for the variables which should be updated
            index_list = None
            if self.target_path_list is None:
                index_list = range(self.length[event_index])
            else:
                index_list = self.variable_path_num[event_index]
            self.log_updated += len(index_list)

            # Update the variable types and history list
            for var_index in index_list:
                # Skips the variable if check_variable is False
                if not self.event_type_detector.check_variables[event_index][var_index]:
                    continue

                # Update variable types
                self.update_var_type(event_index, var_index, log_atom)

                # This section updates the history list of the variable types
                if self.var_type[event_index][var_index][0] in self.var_type_history_list_order:
                    # Index of the variable type in the list  # [others, static, [discrete, number of appended steps],
                    # asc, desc, unique, range, ev of continuous distributions]
                    type_index = self.var_type_history_list_order.index(self.var_type[event_index][var_index][0])
                else:
                    type_index = self.var_type_history_list_order.index('cont')

                for tmp_type_index, tmp_type_val in enumerate(self.var_type_history_list[event_index][var_index]):
                    if tmp_type_index == type_index:
                        if self.var_type_history_list_order[type_index] == 'cont':
                            for _, val in enumerate(tmp_type_val):
                                val.append(0)
                            # Continuously distributed variable type.
                            if self.var_type[event_index][var_index][0] == 'uni':
                                tmp_type_val[0][-1] = (
                                    self.var_type[event_index][var_index][1] + self.var_type[event_index][var_index][2]) / 2
                                tmp_type_val[1][-1] = (
                                    self.var_type[event_index][var_index][2] - self.var_type[event_index][var_index][1]) / np.sqrt(12)
                            else:
                                tmp_type_val[0][-1] = self.var_type[event_index][var_index][1]
                                tmp_type_val[1][-1] = self.var_type[event_index][var_index][2]

                        elif self.var_type_history_list_order[type_index] == 'range':
                            tmp_type_val[0].append(self.var_type[event_index][var_index][1])
                            tmp_type_val[1].append(self.var_type[event_index][var_index][2])

                        elif len(tmp_type_val) >= 1 and isinstance(tmp_type_val[0], list):
                            tmp_type_val[0].append(1)
                            for i in range(1, len(tmp_type_val)):  # skipcq: PTC-W0060
                                tmp_type_val[i].append(0)

                        else:
                            tmp_type_val.append(1)
                    else:
                        if len(tmp_type_val) >= 1 and isinstance(tmp_type_val[0], list):
                            for _, val in enumerate(tmp_type_val):
                                val.append(0)
                        else:
                            tmp_type_val.append(0)

            # Reduce the number of variables, which are tracked
            if (self.num_updates_until_var_reduction > 0 and (
                    self.event_type_detector.num_event_lines[event_index] - self.num_init) / self.num_update ==
                    self.num_updates_until_var_reduction - 1):

                for var_index, var_val in enumerate(self.var_type_history_list[event_index]):
                    # Skips the variable if it is already not being checked
                    if not self.event_type_detector.check_variables[event_index][var_index]:
                        continue

                    tmp_max = 1
                    exceeded_thresh = False
                    for type_index in range(1, len(var_val)):  # skipcq: PTC-W0060
                        # Continuous Distribution
                        if type_index in [self.var_type_history_list_order.index('cont'), self.var_type_history_list_order.index('range')]:
                            num_app = len([1 for x in var_val[type_index][1] if x != 0])
                            if num_app / self.num_updates_until_var_reduction >= self.var_reduction_thres:
                                exceeded_thresh = True
                                break
                            if num_app > tmp_max:
                                tmp_max = num_app
                        # Distributions which are neither continuous nor range
                        else:
                            if len(var_val[type_index]) >= 1 and isinstance(var_val[type_index][0], list):
                                num_app = sum(var_val[type_index][0])
                                if num_app / self.num_updates_until_var_reduction >= self.var_reduction_thres:
                                    exceeded_thresh = True
                                    break
                                if num_app > tmp_max:
                                    tmp_max = num_app
                            else:
                                num_app = sum(var_val[type_index])
                                if num_app / self.num_updates_until_var_reduction >= self.var_reduction_thres:
                                    exceeded_thresh = True
                                    break
                                if num_app > tmp_max:
                                    tmp_max = num_app

                    # Remove the variable if it did not exceed the threshold
                    if not exceeded_thresh:
                        self.event_type_detector.check_variables[event_index][var_index] = False
                        self.event_type_detector.values[event_index][var_index] = []
                        self.var_type[event_index][var_index] = []
                        self.var_type_history_list[event_index][var_index] = []
                        self.distr_val[event_index][var_index] = []
                        if len(self.var_type_history_list_reference) > event_index and len(
                                self.var_type_history_list_reference[event_index]) > var_index:
                            self.var_type_history_list_reference[event_index][var_index] = []
                        affected_path = self.event_type_detector.variable_key_list[event_index][var_index]
                        self.print(
                            f'Stopped tracking the variable of event type {self.event_type_detector.get_event_type(event_index)} with '
                            f'Path:\n{affected_path}\nbecause of irregular variable types.', log_atom, affected_path,
                            confidence=1 / (1 + np.exp(-4 / tmp_max)) / 0.9820137900379085)
                        # 1 / (1 + np.exp(-4 / tmp_max)) / 0.9820137900379085 is the scaled sigmoidfunction.
                        # 1 / (1 + np.exp(-4)) = 0.9820137900379085

            # Saves the initial reference state of the var_type_history_list for the calculation of the indicator
            if ((self.num_updates_until_var_reduction == 0) or (
                    self.event_type_detector.num_event_lines[event_index] - self.num_init) / self.num_update >=
                self.num_updates_until_var_reduction - 1) and (not isinstance(self.num_var_type_hist_ref, bool)) and (
                    (len(self.var_type_history_list_reference) < event_index + 1) or
                    self.var_type_history_list_reference[event_index] == []) and (
                    (self.event_type_detector.num_event_lines[event_index] - self.num_init) / self.num_update >=
                    self.num_var_type_hist_ref - 1):

                if len(self.var_type_history_list_reference) < event_index + 1:
                    for i in range(event_index + 1 - len(self.var_type_history_list_reference)):
                        self.var_type_history_list_reference.append([])

                for var_index, var_val in enumerate(self.var_type_history_list[event_index]):
                    self.var_type_history_list_reference[event_index].append([])
                    for type_index, type_val in enumerate(var_val):
                        if len(type_val) >= 1 and isinstance(type_val[0], list):
                            # Continuous variable type
                            if type_index in [self.var_type_history_list_order.index('cont'),
                                              self.var_type_history_list_order.index('range')]:
                                # Calculate the mean of all entries not zero
                                self.var_type_history_list_reference[event_index][var_index].append([sum(
                                        type_val[0][-self.num_var_type_hist_ref:]) / max(len([1 for x in type_val[0][
                                            -self.num_var_type_hist_ref:] if x != 0]), 1), sum(type_val[1][-self.num_var_type_hist_ref:]) /
                                        max(len([1 for x in type_val[1][-self.num_var_type_hist_ref:] if x != 0]), 1)])
                            else:
                                self.var_type_history_list_reference[event_index][var_index].append([sum(x[
                                    -self.num_var_type_hist_ref:]) for x in type_val])
                        else:
                            self.var_type_history_list_reference[event_index][var_index].append(sum(type_val[-self.num_var_type_hist_ref:]))

            # Check the indicator for the variable types of the Event and generates an output, if it fails
            else:
                if ((self.num_updates_until_var_reduction == 0) or (
                        self.event_type_detector.num_event_lines[event_index] - self.num_init) /
                    self.num_update >= self.num_updates_until_var_reduction - 1) and (not isinstance(
                        self.num_var_type_considered_ind, bool)) and (not isinstance(self.num_var_type_hist_ref, bool)) and len(
                    self.var_type_history_list_reference) > event_index and (self.var_type_history_list_reference[event_index] != []) and (
                        ((self.event_type_detector.num_event_lines[event_index] - self.num_init) / self.num_update
                         - self.num_var_type_hist_ref) % self.num_var_type_considered_ind) == 0:

                    # Shorten the var_type_history_list
                    if len(self.var_type_history_list[event_index]) > 0 and len(self.var_type_history_list[event_index][0]) > 0 and len(
                        self.var_type_history_list[event_index][0][0]) > max(
                            self.num_var_type_considered_ind, self.num_var_type_hist_ref):
                        for var_index, var_val in enumerate(self.var_type_history_list[event_index]):
                            for type_index, type_val in enumerate(var_val):
                                # Differentiation between the entries, which are lists (e.g. discrete) and values
                                if isinstance(type_val[0], list):
                                    for i, val in enumerate(type_val):
                                        if isinstance(val, list):
                                            type_val[i] = val[-max(self.num_var_type_considered_ind, self.num_var_type_hist_ref):]
                                else:
                                    var_val[type_index] = type_val[-max(self.num_var_type_considered_ind, self.num_var_type_hist_ref):]

                    indicator_list = self.get_indicator(event_index)

                    indicator = max(0, max(indicator_list))
                    if indicator >= self.indicator_thres:

                        # Update the list of the failed indicators, which is used for the weights of the indicator
                        if len(self.failed_indicators) < event_index + 1:
                            # Extend the lists if necessary
                            tmp_len = len(self.failed_indicators)
                            for i in range(event_index + 1 - tmp_len):
                                self.failed_indicators.append([[] for _ in range(len(self.var_type[tmp_len + i]))])

                        # Indices of the variables, which would have failed the indicator
                        indices_failed_tests = []
                        for var_index in range(len(self.var_type[event_index])):  # skipcq: PTC-W0060
                            if indicator_list[var_index] >= self.indicator_thres:
                                indices_failed_tests.append(var_index)
                                self.failed_indicators[event_index][var_index].append(self.event_type_detector.num_event_lines[event_index])

                        # Multiply the single values of the indicator with their corresponding weights
                        # Number of the log line which corresponds to the first indicator, which is taken into account
                        first_line_num = self.event_type_detector.num_event_lines[event_index] - self.num_update * \
                            self.num_var_type_considered_ind * (self.num_ind_for_weights + self.num_skipped_ind_for_weights)
                        # Number of the log line which corresponds to the last indicator, which is taken into account
                        last_line_num = self.event_type_detector.num_event_lines[event_index] - self.num_update * \
                            self.num_var_type_considered_ind * self.num_skipped_ind_for_weights

                        for var_index in indices_failed_tests:
                            lower_ind = False  # Index of the lower limit of the considered values of the failed_indicator list
                            upper_ind = False  # Index of the upper limit of the considered values of the failed_indicator list

                            for i, val in enumerate(self.failed_indicators[event_index][var_index]):
                                if val >= first_line_num:
                                    lower_ind = i
                                    break

                            if isinstance(lower_ind, bool):
                                lower_ind = 0
                                upper_ind = 0
                            else:
                                for i, val in enumerate(self.failed_indicators[event_index][var_index], start=lower_ind):
                                    if val >= last_line_num:
                                        upper_ind = i
                                        break
                                if isinstance(upper_ind, bool):
                                    upper_ind = len(self.failed_indicators[event_index][var_index])

                            # Calculating the weight for the indicator
                            indicator_weight = 1 / (1 + upper_ind - lower_ind)
                            indicator_list[var_index] = indicator_list[var_index] * indicator_weight

                            # Reduce the list of the failed indicators
                            self.failed_indicators[event_index][var_index] = self.failed_indicators[event_index][var_index][lower_ind:]

                        # Calculate and print the confidence of the failed indicator
                        indicator = sum(indicator_list[var_index] for var_index in indices_failed_tests)

                        if self.save_statistics:
                            self.failed_indicators_total.append(log_atom.atom_time)
                            self.failed_indicators_values.append(np.arctan(2 * indicator) / np.pi * 2)
                            if self.event_type_detector.id_path_list != []:
                                self.failed_indicators_paths.append(self.event_type_detector.id_path_list_tuples[event_index])
                            else:
                                self.failed_indicators_paths.append(self.event_type_detector.longest_path[event_index])

                        tmp_string = ''
                        affected_paths = [self.event_type_detector.variable_key_list[event_index][var_index] for var_index in
                                          indices_failed_tests]
                        if self.var_type_history_list:
                            tmp_string += f'Event {self.event_type_detector.get_event_type(event_index)}: '
                            tmp_string += f'Indicator of a change in system behaviour: {np.arctan(2 * indicator) / np.pi * 2}. Paths to' \
                                          f' the corresponding variables: {affected_paths}'

                        self.print(tmp_string, log_atom, affected_paths, np.arctan(2 * indicator) / np.pi * 2, indicator=True)

                # Update the var_type_history_list_reference
                if self.learn_mode and (not isinstance(self.num_var_type_hist_ref, bool)) and (
                        not isinstance(self.num_update_var_type_hist_ref, bool)) and len(
                        self.var_type_history_list_reference) >= event_index + 1 and \
                        self.var_type_history_list_reference[event_index] != [] and (((
                            self.event_type_detector.num_event_lines[event_index] - self.num_init) / self.num_update -
                                self.num_var_type_hist_ref) % self.num_update_var_type_hist_ref == 0):

                    for var_index, var_val in enumerate(self.var_type_history_list[event_index]):
                        self.var_type_history_list_reference[event_index][var_index] = []
                        for type_index, type_val in enumerate(var_val):
                            if len(type_val) >= 1 and isinstance(type_val[0], list):
                                if type_index in [self.var_type_history_list_order.index('cont'),
                                                  self.var_type_history_list_order.index('range')]:
                                    # Continuous or range variable type
                                    # Calculate the mean of all entries not zero
                                    self.var_type_history_list_reference[event_index][var_index].append([sum(
                                        type_val[0][-self.num_var_type_hist_ref:]) / max(len([1 for x in type_val[0][
                                            -self.num_var_type_hist_ref:] if x != 0]), 1), sum(type_val[1][
                                                -self.num_var_type_hist_ref:]) / max(len([1 for x in type_val[1][
                                                    -self.num_var_type_hist_ref:] if x != 0]), 1)])
                                else:
                                    self.var_type_history_list_reference[event_index][var_index].append(
                                            [sum(x[-self.num_var_type_hist_ref:]) for x in type_val])
                            else:
                                self.var_type_history_list_reference[event_index][var_index].append(sum(
                                        type_val[-self.num_var_type_hist_ref:]))
                    if self.stop_learning_timestamp is not None and self.stop_learning_no_anomaly_time is not None:
                        self.stop_learning_timestamp = max(
                            self.stop_learning_timestamp, log_atom.atom_time + self.stop_learning_no_anomaly_time)

    def detect_var_type(self, event_index, var_index):
        """Give back the assumed variable type of the variable with the in self.event_type_detector stored values."""
        # Values which are being tested
        values = self.event_type_detector.values[event_index][var_index][-self.num_init:]
        # Unique values
        values_set = set(values)
        # Number of unique values
        num_diff_vals = len(values_set)

        if num_diff_vals == 1:
            return ['stat', list(values_set), False]

        # List of floats or False
        float_values = convert_to_floats(values)
        is_int = False
        if len(float_values) > 0:
            is_int = consists_of_ints(float_values)

        # Values are integer numbers
        if len(float_values) > 0:
            previous_val = float_values[0]
            asc = True
            desc = True
            # Test for ascending
            for v in float_values[1:]:
                if previous_val > v:
                    asc = False
                    break
                previous_val = v

            previous_val = float_values[0]
            # Test for descending
            for v in float_values[1:]:
                if previous_val < v:
                    desc = False
                    break
                previous_val = v
            if asc:
                if is_int:
                    return ['asc', 'int']
                return ['asc', 'float']
            if desc:
                if is_int:
                    return ['desc', 'int']
                return ['desc', 'float']

        # Checking if no integers should be tested and if the values are integers
        if not self.test_gof_int and is_int:
            float_values = []

        if len(float_values) > 0 and (num_diff_vals > self.div_thres * self.num_init):
            float_values_mean = np.mean(float_values)
            dw_result = durbin_watson([val - float_values_mean for val in float_values])
            if dw_result < self.crit_val_dw[self.dw_alpha][len(float_values)] or\
                    dw_result > 4 - self.crit_val_dw[self.dw_alpha][len(float_values)]:
                var_type = self.calculate_value_range(float_values)
            else:
                # test for a continuous distribution. If none fits, the function will return ['d']
                var_type = self.detect_continuous_shape(float_values)
        else:
            # discrete var type
            var_type = ['d']

        # Test for discrete, unique and others
        if var_type == ['d']:
            if self.num_init == num_diff_vals and (len(float_values) == 0 or is_int):
                # unique var type
                return ['unq', values]
            if num_diff_vals >= self.num_init * (1 - self.sim_thres):
                # Values do not follow a specific pattern, the second entry is the number of update runs without a new type.
                return ['others', 0]
            # Initialize the discrete type
            values_set = list(values_set)
            values_app = [0 for _ in range(num_diff_vals)]
            for value in values:
                values_app[values_set.index(value)] += 1

            values_app = [x / len(values) for x in values_app]
            # discrete var type
            return ['d', values_set, values_app, len(values)]
        return var_type

    def detect_continuous_shape(self, values):
        """
        Detect if the sample follows one of the checked continuous distribution and returns the found type in a fitting format.
        ['d'] if none fit.
        """
        # List of the p-values of the distributions
        significance = []
        # List of the tested distributions
        distribution = []

        # Converts the floats/integer to an array for faster manipulations and tests
        values = np.array(values)

        if self.used_gof_test == 'KS':
            # Test for uniform distribution
            min_val = min(values)
            max_val = max(values)
            if self.gof_alpha in self.crit_val_ini_ks and self.num_init in self.crit_val_ini_ks[self.gof_alpha]:
                significance.append(self.gof_alpha * self.crit_val_ini_ks[self.gof_alpha][self.num_init][
                    'uni'] / kstest(values, 'uniform', args=(min_val, max_val - min_val))[0])
                distribution.append(['uni', min_val, max_val])
            else:
                significance.append(kstest(values, 'uniform', args=(min_val, max_val - min_val))[1])
                distribution.append(['uni', min_val, max_val])

            # Test for normal distribution
            # Getting the expected value and sigma
            [ev, sigma] = norm.fit(values)

            # KS-test of the standardised values and the distribution
            if self.gof_alpha in self.crit_val_ini_ks and self.num_init in self.crit_val_ini_ks[self.gof_alpha]:
                significance.append(self.gof_alpha * self.crit_val_ini_ks[self.gof_alpha][self.num_init][
                    'nor'] / kstest((values - ev) / sigma, 'norm')[0])
                distribution.append(['nor', ev, sigma, min_val, max_val])
            else:
                significance.append(kstest((values - ev) / sigma, 'norm')[1])
                distribution.append(['nor', ev, sigma, min_val, max_val])

            # Test for beta distribution
            # (0.5*0.5/((0.5+0.5+1)(0.5+0.5)^2))^(1/2) = 2.82842712
            ev_tmp = (min_val + max_val) / 2
            sigma_tmp = (max_val - min_val) / 2.82842712

            if self.gof_alpha in self.crit_val_ini_ks and self.num_init in self.crit_val_ini_ks[self.gof_alpha]:
                significance.append(self.gof_alpha * self.crit_val_ini_ks[self.gof_alpha][self.num_init][
                    'beta1'] / kstest((values-min_val)/(max_val-min_val), 'beta', args=(0.5, 0.5))[0])
                distribution.append(['beta', ev_tmp, sigma_tmp, min_val, max_val, 1])
            else:
                significance.append(kstest((values-min_val)/(max_val-min_val), 'beta', args=(0.5, 0.5))[1])
                distribution.append(['beta', ev_tmp, sigma_tmp, min_val, max_val, 1])

            # KS-test of the standardised values and the distribution
            if self.gof_alpha in self.crit_val_ini_ks and self.num_init in self.crit_val_ini_ks[self.gof_alpha]:
                # Beta 2
                significance.append(self.gof_alpha * self.crit_val_ini_ks[self.gof_alpha][self.num_init][
                    'beta2'] / kstest((values-ev)/sigma*pow(5*2/(5+2+1), 1/2)/(5+2)+5/(5+2), 'beta', args=(5, 2))[0])
                distribution.append(['beta', ev, sigma, min_val, max_val, 2])

                # Beta 3
                significance.append(self.gof_alpha * self.crit_val_ini_ks[self.gof_alpha][self.num_init][
                    'beta2'] / kstest((values-ev)/sigma*pow(5*2/(5+2+1), 1/2)/(5+2)+2/(5+2), 'beta', args=(2, 5))[0])
                distribution.append(['beta', ev, sigma, min_val, max_val, 3])

                # Beta 4
                significance.append(self.gof_alpha * self.crit_val_ini_ks[self.gof_alpha][self.num_init][
                    'beta4'] / kstest((values-ev)/sigma*pow(1*5/(1+5+1), 1/2)/(1+5)+1/(1+5), 'beta', args=(1, 5))[0])
                distribution.append(['beta', ev, sigma, min_val, max_val, 4])

                # Beta 5
                significance.append(self.gof_alpha * self.crit_val_ini_ks[self.gof_alpha][self.num_init][
                    'beta4'] / kstest((values-ev)/sigma*pow(1*5/(1+5+1), 1/2)/(1+5)+5/(1+5), 'beta', args=(5, 1))[0])
                distribution.append(['beta', ev, sigma, min_val, max_val, 5])
            else:
                # Beta 2
                significance.append(kstest((values-ev)/sigma*pow(5*2/(5+2+1), 1/2)/(5+2)+5/(5+2), 'beta', args=(5, 2))[1])
                distribution.append(['beta', ev, sigma, min_val, max_val, 2])

                # Beta 3
                significance.append(kstest((values-ev)/sigma*pow(5*2/(5+2+1), 1/2)/(5+2)+2/(5+2), 'beta', args=(2, 5))[1])
                distribution.append(['beta', ev, sigma, min_val, max_val, 3])

                # Beta 4
                significance.append(kstest((values-ev)/sigma*pow(1*5/(1+5+1), 1/2)/(1+5)+1/(1+5), 'beta', args=(1, 5))[1])
                distribution.append(['beta', ev, sigma, min_val, max_val, 4])

                # Beta 5
                significance.append(kstest((values-ev)/sigma*pow(1*5/(1+5+1), 1/2)/(1+5)+5/(1+5), 'beta', args=(5, 1))[1])
                distribution.append(['beta', ev, sigma, min_val, max_val, 5])

            # Crit value for the self generated or mixed distributions
            crit_val = pow(-np.log(self.gof_alpha) * 3 / self.num_init / 4, 1 / 2)
            est_penalty = 1.4  # Estimated penalty for the adapted ev and SD

            # Test for the mixed beta distribution
            # ev/sigma of Beta 4: ev=1/(1+5)   sigma=pow(1*5/(1+5+1),1/5)/(1+5)
            # sigma in [sigmaBetam1,sigmaBetam2]
            if 1 / 6 < (ev - min_val) / (max_val - min_val) < 5 / 6:
                # Interpolate the expected distribution functions threw the sigma in the interval
                proportion = ((ev - min_val) / (max_val - min_val) - 5 / 6) / (-4 / 6)
                tmp_index = [int(round(i / proportion)) for i in range(int(round(1000 * proportion)))]

                if self.gof_alpha in self.crit_val_ini_ks and self.num_init in self.crit_val_ini_ks[self.gof_alpha]:
                    significance.append(ks_2samp([self.quantiles['betam1'][i] for i in tmp_index] + [self.quantiles['betam2'][
                        i] for i in range(1000) if i not in tmp_index], (values - min_val) / (max_val - min_val))[0] /
                        crit_val * est_penalty)
                    distribution.append(['betam', min_val, max_val - min_val, min_val, max_val, proportion])
                else:
                    significance.append(ks_2samp([self.quantiles['betam1'][i] for i in tmp_index] + [self.quantiles['betam2'][
                        i] for i in range(1000) if i not in tmp_index], (values - min_val) / (max_val - min_val))[1])
                    distribution.append(['betam', min_val, max_val - min_val, min_val, max_val, proportion])

            # Test for alternative distribution
            # KS-test of the standardised values and the distribution
            if self.gof_alpha in self.crit_val_ini_ks and self.num_init in self.crit_val_ini_ks[self.gof_alpha]:
                significance.append(ks_2samp(self.quantiles['spec'], (values - ev) / sigma)[0] / crit_val * est_penalty)
                distribution.append(['spec', ev, sigma, min_val, max_val, 0])

                significance.append(
                  ks_2samp(self.quantiles['spec'], -(values - ev) / sigma)[0] / crit_val * est_penalty)
                distribution.append(['spec', ev, sigma, min_val, max_val, 1])
            else:
                significance.append(ks_2samp(self.quantiles['spec'], (values - ev) / sigma)[1])
                distribution.append(['spec', ev, sigma, min_val, max_val, 0])

                significance.append(ks_2samp(self.quantiles['spec'], -(values - ev) / sigma)[1])
                distribution.append(['spec', ev, sigma, min_val, max_val, 1])

            # Check if one of the above tested continuous distribution fits
            if max(significance) >= self.gof_alpha:
                sort_indices = np.argsort(significance)
                sort_list = []
                for i in range(len(sort_indices) - 2, -1, -1):
                    if significance[sort_indices[i]] >= self.gof_alpha:
                        sort_list.append(distribution[sort_indices[i]])
                return distribution[sort_indices[-1]] + [sort_list]

        if self.used_gof_test == 'CM':
            min_val = min(values)
            max_val = max(values)
            [ev, sigma] = norm.fit(values)

            # Test for uniform distribution
            significance.append(cramervonmises((values-min_val) / (max_val-min_val) * (1-self.min_mod_ini_uni-self.max_mod_ini_uni) +
                                self.min_mod_ini_uni, 'uniform') / self.crit_val_ini_cm[self.gof_alpha][self.num_init]['uni'])
            distribution.append(['uni', min_val - self.min_mod_ini_uni / (1-self.min_mod_ini_uni-self.max_mod_ini_uni) * (max_val-min_val),
                                max_val + self.max_mod_ini_uni / (1-self.min_mod_ini_uni-self.max_mod_ini_uni) * (max_val-min_val)])

            # Test for normal distribution
            significance.append(cramervonmises((values-ev) / sigma, 'norm') / self.crit_val_ini_cm[self.gof_alpha][self.num_init]['nor'])
            distribution.append(['nor', ev, sigma, min_val, max_val])

            # Test for beta1 distribution
            significance.append(cramervonmises((values-min_val) / (max_val-min_val) * (1-self.min_mod_ini_beta1-self.max_mod_ini_beta1) +
                                self.min_mod_ini_beta1, 'beta', args=(0.5, 0.5)) /
                                self.crit_val_ini_cm[self.gof_alpha][self.num_init]['beta1'])
            distribution.append(['beta', ev, sigma, min_val - self.min_mod_ini_beta1 / (1-self.min_mod_ini_beta1-self.max_mod_ini_beta1) *
                                (max_val-min_val), max_val + self.max_mod_ini_beta1 / (1-self.min_mod_ini_beta1-self.max_mod_ini_beta1) *
                                (max_val-min_val), 1])

            # Test for beta2 distribution
            significance.append(cramervonmises((values-min_val) / (max_val-min_val) * (1-self.max_mod_ini_beta2-self.min_mod_ini_beta2) +
                                self.min_mod_ini_beta2, 'beta', args=(5, 2)) / self.crit_val_ini_cm[self.gof_alpha][self.num_init]['beta2'])
            distribution.append(['beta', ev, sigma, min_val - self.min_mod_ini_beta2 / (1-self.min_mod_ini_beta2-self.max_mod_ini_beta2) *
                                (max_val-min_val), max_val + self.max_mod_ini_beta2 / (1-self.min_mod_ini_beta2-self.max_mod_ini_beta2) *
                                (max_val-min_val), 2])

            # Test for beta3 distribution
            significance.append(cramervonmises((values-min_val) / (max_val-min_val) * (1-self.max_mod_ini_beta2-self.min_mod_ini_beta2) +
                                self.max_mod_ini_beta2, 'beta', args=(2, 5)) / self.crit_val_ini_cm[self.gof_alpha][self.num_init]['beta2'])
            distribution.append(['beta', ev, sigma, min_val - self.max_mod_ini_beta2 / (1-self.max_mod_ini_beta2-self.min_mod_ini_beta2) *
                                (max_val-min_val), max_val + self.min_mod_ini_beta2 / (1-self.max_mod_ini_beta2-self.min_mod_ini_beta2) *
                                (max_val-min_val), 3])

            # Test for beta4 distribution
            significance.append(cramervonmises((values-min_val) / (ev-min_val) * (1/6-self.min_mod_ini_beta4) + self.min_mod_ini_beta4,
                                'beta', args=(1, 5)) / self.crit_val_ini_cm[self.gof_alpha][self.num_init]['beta4'])
            distribution.append(['beta', ev, sigma, min_val, max_val, 4])

            # Test for beta5 distribution
            significance.append(cramervonmises((values-max_val) / (max_val-ev) * (1/6-self.min_mod_ini_beta4) + 1 - self.min_mod_ini_beta4,
                                'beta', args=(5, 1)) / self.crit_val_ini_cm[self.gof_alpha][self.num_init]['beta4'])
            distribution.append(['beta', ev, sigma, min_val, max_val, 5])

            # Check if one of the above tested continuous distribution fits
            if min(significance) <= 1:
                sort_indices = np.argsort(significance)
                sort_list = []
                for i in sort_indices[1:]:
                    if significance[i] >= self.gof_alpha:
                        sort_list.append(distribution[i])
                return distribution[sort_indices[0]] + [sort_list]

        if self.use_empiric_distr:
            return ['emp', ev, sigma, []]
        # discrete if no distribution fits
        return ['d']

    def calculate_value_range(self, values):
        """Calculate the lower and upper limit of the expected values through the mean and standard deviation of the given values."""
        if self.used_range_test == 'MeanSD':
            # Calculate the mean and standard deviation of the test sample
            [ev, sigma] = norm.fit(values)

            # Estimate distance of the mean ot the limits with the quantiles of the normal distribution.
            ev_dist = sigma * norm.ppf(self.range_alpha / 2)

            # Calculate lower and upper limit
            lower_limit = ev + ev_dist * self.range_limits_factor
            upper_limit = ev - ev_dist * self.range_limits_factor

        elif self.used_range_test == 'EmpiricQuantiles':
            # Sort values
            values.sort()

            # Calculate lower and upper limit
            lower_limit = values[0] - (values[int(len(values) * (0.5 - self.range_alpha / 2) + 0.5)] - values[0]) * self.range_limits_factor
            upper_limit = values[-1] - (
                values[-1 - int(len(values) * (0.5 - self.range_alpha / 2) + 0.5)] - values[-1]) * self.range_limits_factor

        else:
            # self.used_range_test == 'MinMax'
            # Sort values
            values.sort()

            # Calculate lower and upper limit
            lower_limit = values[0] - (values[-1] - values[0]) * (0.5 - self.range_alpha / 2) * self.range_limits_factor
            upper_limit = values[-1] + (values[-1] - values[0]) * (0.5 - self.range_alpha / 2) * self.range_limits_factor

        return ['range', lower_limit, upper_limit, 0]

    def update_var_type(self, event_index, var_index, log_atom):
        """Test if the new num_update values fit the detected var type and updates the var type if the test fails."""
        # Getting the new values and saving the old distribution for printing-purposes if the test fails
        new_values = self.event_type_detector.values[event_index][var_index][-self.num_update:]
        VT_old = copy.deepcopy(self.var_type[event_index][var_index])

        # Test and update for continuous distribution
        if self.var_type[event_index][var_index][0] in self.distr_list:
            if not consists_of_floats(new_values):
                # A value is not a float or integer, so the new assigned type is others
                # Values do not follow a specific pattern
                self.var_type[event_index][var_index] = ['others', 0]
                self.distr_val[event_index][var_index] = []
                self.bt_results[event_index][var_index] = []
                self.print_changed_var_type(event_index, VT_old, ['others'], var_index, log_atom, 1.0)
                return

            # first_distr is used to test the current distribution with the BT and to discard the alternative distributions if they
            # fail the s_gof-test once
            first_distr = True
            s_gof_result = self.s_gof_test(event_index, var_index, first_distr)
            # Calculate the confidence as the stretched sigmaoid function of the maximal value of the step fct
            # 1 / (1 + np.exp(-2)) = 1.1353352832366128
            confidence = 1 / (1 + np.exp(-2 * s_gof_result[1])) * 1.1353352832366128
            while not s_gof_result[0]:
                # If the test fails a new shape is searched for in the alternative distributions
                self.bt_results[event_index][var_index] = self.bt_results[event_index][var_index][1:] + [0]  # Update the results of the BT
                first_distr = False

                # Check if the BT is applicable and if it holds
                if first_distr and (sum(self.bt_results[event_index][var_index]) >= self.s_gof_bt_min_success):
                    return

                if not self.learn_mode:
                    # Do not update variable type
                    self.bt_results[event_index][var_index] = [1] * self.num_s_gof_bt
                    self.print_reject_var_type(event_index, self.var_type[event_index][var_index], var_index, log_atom)
                    self.var_type_history_list[event_index][var_index][0][-1] = 1
                    return

                if len(self.alternative_distribution_types[event_index][var_index]) != 0:
                    # There is at least one alternative distribution
                    # Initializes the distributionvalues and bucketnumbers
                    self.var_type[event_index][var_index] = self.alternative_distribution_types[event_index][var_index][0]
                    self.alternative_distribution_types[event_index][var_index] = self.alternative_distribution_types[event_index][
                        var_index][1:]
                    self.bt_results[event_index][var_index] = [1] * self.num_s_gof_bt
                    if self.var_type[event_index][var_index][0] in ('betam', 'spec'):
                        self.s_gof_get_quantiles(event_index, var_index)

                    s_gof_result = self.s_gof_test(event_index, var_index, first_distr)

                # There is no alternative distribution. The var type is set to others
                else:
                    # Values do not follow a specific pattern
                    self.var_type[event_index][var_index] = ['others', 0]
                    self.distr_val[event_index][var_index] = []
                    self.bt_results[event_index][var_index] = []
                    self.print_changed_var_type(event_index, VT_old, ['others'], var_index, log_atom, confidence)
                    return

            # Check if the s_gof_test was successful and remark the success
            if first_distr:
                self.bt_results[event_index][var_index] = self.bt_results[event_index][var_index][1:] + [1]

            # Print a message if the vartype has changed
            if VT_old != self.var_type[event_index][var_index]:
                self.print_changed_var_type(event_index, VT_old, self.var_type[event_index][var_index], var_index, log_atom, confidence)

        # Test and update if the values are in the specified range
        elif self.var_type[event_index][var_index][0] == 'range':
            self.var_type[event_index][var_index][3] += 1
            # Check if the sum of distances of all values outside the defined limits is greater than range_threshold times the range of
            # the limits
            if sum(max(0, val - self.var_type[event_index][var_index][2]) for val in
                    self.event_type_detector.values[event_index][var_index][-self.num_update:]) +\
                    sum(max(0, self.var_type[event_index][var_index][1] - val) for val in
                        self.event_type_detector.values[event_index][var_index][-self.num_update:]) >\
                    self.range_threshold * (self.var_type[event_index][var_index][2] - self.var_type[event_index][var_index][1]):
                # Do not update variable type
                if not self.learn_mode:
                    self.print_reject_var_type(event_index, self.var_type[event_index][var_index], var_index, log_atom)
                    self.var_type_history_list[event_index][var_index][0][-1] = 1
                    return

                # Values do not follow a specific pattern
                self.var_type[event_index][var_index] = ['others', 0]
                self.print_changed_var_type(event_index, VT_old, ['others'], var_index, log_atom)
            # Reset counter if at least one value lies outside of the limits
            elif any(max(0, val - self.var_type[event_index][var_index][2]) for val in
                     self.event_type_detector.values[event_index][var_index][-self.num_update:]) or\
                    any(max(0, self.var_type[event_index][var_index][1] - val) for val in
                        self.event_type_detector.values[event_index][var_index][-self.num_update:]):
                self.var_type[event_index][var_index][3] = 1
            # Reinitialize the range limits if no value was outside of the range in the last num_reinit_range update steps
            elif self.learn_mode and self.num_reinit_range != 0 and\
                    self.var_type[event_index][var_index][3] % self.num_reinit_range == 0:
                self.var_type[event_index][var_index] = self.calculate_value_range(
                    self.event_type_detector.values[event_index][var_index][-self.num_update:])
                if self.stop_learning_timestamp is not None and self.stop_learning_no_anomaly_time is not None:
                    self.stop_learning_timestamp = max(
                        self.stop_learning_timestamp, log_atom.atom_time + self.stop_learning_no_anomaly_time)

        # Test and update for ascending values
        elif self.var_type[event_index][var_index][0] == 'asc':
            # Search for a not ascending sequence in the values
            for j in range(-self.num_update, 0):
                if self.event_type_detector.values[event_index][var_index][j - 1] >\
                        self.event_type_detector.values[event_index][var_index][j]:
                    # Do not update variable type
                    if not self.learn_mode:
                        self.print_reject_var_type(event_index, self.var_type[event_index][var_index], var_index, log_atom)
                        self.var_type_history_list[event_index][var_index][0][-1] = 1
                        return

                    # Values do not follow a specific pattern
                    self.var_type[event_index][var_index] = ['others', 0]
                    self.print_changed_var_type(event_index, VT_old, ['others'], var_index, log_atom)
                    return

        elif self.var_type[event_index][var_index][0] == 'desc':
            # Test and update for descending values
            for j in range(-self.num_update, 0):
                # Search for a not ascending sequence in the values
                if self.event_type_detector.values[event_index][var_index][j - 1] <\
                        self.event_type_detector.values[event_index][var_index][j]:
                    if not self.learn_mode:
                        # Do not update variable type
                        self.print_reject_var_type(event_index, self.var_type[event_index][var_index], var_index, log_atom)
                        self.var_type_history_list[event_index][var_index][0][-1] = 1
                        return

                    # Values do not follow a specific pattern
                    self.var_type[event_index][var_index] = ['others', 0]
                    self.print_changed_var_type(event_index, VT_old, ['others'], var_index, log_atom)
                    return

        elif self.var_type[event_index][var_index][0] == 'd':
            # Test and update for values of the discrete type
            # Check if new values have appeared
            if len(set(new_values + self.var_type[event_index][var_index][1])) > len(self.var_type[event_index][var_index][1]):
                # New values have appeared
                # Test if vartype others
                if len(set(new_values + self.var_type[event_index][var_index][1])) >= (
                        self.num_update + self.var_type[event_index][var_index][3]) * (1 - self.sim_thres):
                    # Do not update variable type
                    if not self.learn_mode:
                        self.print_reject_var_type(event_index, self.var_type[event_index][var_index], var_index, log_atom)
                        self.var_type_history_list[event_index][var_index][0][-1] = 1
                        return

                    # Values do not follow a specific pattern
                    self.var_type[event_index][var_index] = ['others', 0]
                    self.print_changed_var_type(event_index, VT_old, ['others'], var_index, log_atom)
                    return

                # Do not update variable type
                if not self.learn_mode:
                    self.print_reject_var_type(event_index, self.var_type[event_index][var_index], var_index, log_atom)
                    self.var_type_history_list[event_index][var_index][2][1][-1] = 1
                    return

                # Create the new value-set and expands the occurrence-list for the new values
                new_values_set = list(set(self.event_type_detector.values[event_index][var_index][-self.num_update:]))
                for val in new_values_set:
                    if val not in self.var_type[event_index][var_index][1]:
                        self.var_type[event_index][var_index][1].append(val)
                        self.var_type[event_index][var_index][2].append(0)

                # update the occurrences
                # List for the appearances of the new values
                values_app = [0] * len(self.var_type[event_index][var_index][1])
                for i in range(-self.num_update, 0):
                    values_app[self.var_type[event_index][var_index][1].index(
                        self.event_type_detector.values[event_index][var_index][i])] += 1

                tmp_number = self.var_type[event_index][var_index][3] / (
                        self.num_update + self.var_type[event_index][var_index][3])
                # Updates the appearance-list in the var type of the discrete variable
                for j, val in enumerate(self.var_type[event_index][var_index][2]):
                    self.var_type[event_index][var_index][2][j] = \
                        val * tmp_number + values_app[j] / (self.num_update + self.var_type[event_index][var_index][3])

                self.var_type[event_index][var_index][3] = self.num_update + self.var_type[event_index][var_index][3]

                self.d_init_bt(event_index, var_index)
                self.print_changed_var_type(event_index, VT_old, self.var_type[event_index][var_index], var_index, log_atom)
                self.var_type_history_list[event_index][var_index][2][1][-1] = 1
                return

            # No new values have appeared, so the normal test for discrete variables is used
            self.d_test(event_index, var_index)

            # Check if the values should be considered others or if the BT failed
            if (len(set(new_values + self.var_type[event_index][var_index][1])) >= (
                    self.num_update + self.var_type[event_index][var_index][3]) * (1 - self.sim_thres)) or (sum(
                        self.bt_results[event_index][var_index][0]) < self.d_bt_min_success):

                # Do not update variable type
                if not self.learn_mode:
                    self.print_reject_var_type(event_index, self.var_type[event_index][var_index], var_index, log_atom)
                    self.bt_results[event_index][var_index][0] = [1] * self.num_d_bt
                    self.var_type_history_list[event_index][var_index][0][-1] = 1
                    return

                # Values do not follow a specific pattern
                self.var_type[event_index][var_index] = ['others', 0]
                self.print_changed_var_type(event_index, VT_old, ['others'], var_index, log_atom)
                return

            # Update the probabilities of the discrete values
            if self.learn_mode and self.bt_results[event_index][var_index][0][-1]:
                # List for the number of appearance of the values
                values_app = [0 for x in range(len(self.var_type[event_index][var_index][1]))]
                for val in new_values:
                    values_app[self.var_type[event_index][var_index][1].index(val)] += 1

                tmp_number = self.var_type[event_index][var_index][3] / (
                    self.num_update + self.var_type[event_index][var_index][3])
                # Updates the appearance-list in the var type of the discrete variable
                for j, val in enumerate(self.var_type[event_index][var_index][2]):
                    self.var_type[event_index][var_index][2][j] = \
                        val * tmp_number + values_app[j] / (self.num_update + self.var_type[event_index][var_index][3])

                self.var_type[event_index][var_index][3] = self.num_update + self.var_type[event_index][var_index][3]

                # Check if the discrete distribution has to be updated
                if ((self.var_type[event_index][var_index][3] - self.num_init) % self.num_pause_discrete) == 0:
                    self.d_init_bt(event_index, var_index)

                if self.stop_learning_timestamp is not None and self.stop_learning_no_anomaly_time is not None:
                    self.stop_learning_timestamp = max(
                        self.stop_learning_timestamp, log_atom.atom_time + self.stop_learning_no_anomaly_time)
                return

        # Test and update for static variables
        if self.var_type[event_index][var_index][0] == 'stat':
            # Check if still static
            if all(new_values[i] == self.event_type_detector.values[event_index][var_index][0] for i in range(self.num_update)):
                if self.var_type[event_index][var_index][2] and self.num_stat_stop_update is True and \
                        self.event_type_detector.num_event_lines[event_index] >= self.num_stat_stop_update:
                    self.event_type_detector.check_variables[event_index][var_index] = False
                    self.event_type_detector.values[event_index][var_index] = []
                    self.var_type[event_index][var_index] = []
                    self.var_type_history_list[event_index][var_index] = []
                    if len(self.var_type_history_list_reference) > event_index and len(self.var_type_history_list_reference[event_index]) >\
                            var_index:
                        self.var_type_history_list_reference[event_index][var_index] = []

                    affected_path = self.event_type_detector.variable_key_list[event_index][var_index]
                    self.print(f'Stopped tracking the variable of event type {self.event_type_detector.get_event_type(event_index)} with'
                               f' Path:\n{affected_path}\nbecause of its static values.', log_atom, affected_path,
                               confidence=1 - 1 / self.num_stat_stop_update)
                return

            # Do not update variable type
            if not self.learn_mode:
                self.print_reject_var_type(event_index, self.var_type[event_index][var_index], var_index, log_atom)
                self.var_type_history_list[event_index][var_index][0][-1] = 1
                return

            # Check if new values appear to be of type others
            if len(set(new_values)) >= self.num_update * (1 - self.sim_thres) and self.num_update >= 3:
                # Values do not follow a specific pattern
                self.var_type[event_index][var_index] = ['others', 0]
                self.print_changed_var_type(event_index, VT_old, ['others'], var_index, log_atom)
                return
            # Change the var type from static to discrete

            # list of the values
            values_set = list(set(self.event_type_detector.values[event_index][var_index][-self.num_init:]))
            # List to store the appearance of the values
            values_app = [0 for _ in range(len(values_set))]

            for j in range(-self.num_init, 0):
                values_app[values_set.index(self.event_type_detector.values[event_index][var_index][j])] += 1
            values_app = [x / self.num_init for x in values_app]

            # Values follow a discrete pattern
            self.var_type[event_index][var_index] = ['d', values_set, values_app, self.num_init]
            self.d_init_bt(event_index, var_index)
            self.print_changed_var_type(event_index, VT_old, self.var_type[event_index][var_index], var_index, log_atom)
            return

        # Test and update for unique values
        if self.var_type[event_index][var_index][0] == 'unq':
            # Check if the new values are not unique
            if len(set(self.event_type_detector.values[event_index][var_index][-self.num_update:])) != self.num_update:
                if not self.learn_mode:
                    # Do not update variable type
                    self.print_reject_var_type(event_index, self.var_type[event_index][var_index], var_index, log_atom)
                    self.var_type_history_list[event_index][var_index][0][-1] = 1
                    return

                self.var_type[event_index][var_index] = ['others', 0]
                self.print_changed_var_type(event_index, VT_old, ['others'], var_index, log_atom)
                return

            # Check if one of the new values has appeared in the last self.num_update_unq values
            for j in self.event_type_detector.values[event_index][var_index][-self.num_update:]:
                if j in self.event_type_detector.values[event_index][var_index][
                        -self.num_update_unq - self.num_update:-self.num_update]:
                    # Do not update variable type
                    if not self.learn_mode:
                        self.print_reject_var_type(event_index, self.var_type[event_index][var_index], var_index, log_atom)
                        self.var_type_history_list[event_index][var_index][0][-1] = 1
                        return

                    self.var_type[event_index][var_index] = ['others', 0]
                    self.print_changed_var_type(event_index, VT_old, ['others'], var_index, log_atom)
                    return
            return

        # Update for var type others
        if self.var_type[event_index][var_index][0] == 'others':
            # Do not update variable type
            if not self.learn_mode:
                return

            # Check if it has passed enough time, to check if the values have a new var_type
            if (self.var_type[event_index][var_index][1] + 1) % (self.num_pause_others + 1) == 0:
                # Added a exponential waiting time to avoid redundant tests
                if not consists_of_ints([np.log2((self.var_type[event_index][var_index][1] + 1) / (self.num_pause_others + 1))]):
                    self.var_type[event_index][var_index][1] += 1
                    return

                # Checking for a new var_type
                vt_new = self.detect_var_type(event_index, var_index)
                # Only increase the number of skipped update-cycles
                if vt_new[0] == 'others':
                    self.var_type[event_index][var_index][1] += 1
                    return

                # The variable gets assigned a new var_type
                # VarType is empiric distribution
                if vt_new[0] == 'emp':
                    self.var_type[event_index][var_index] = vt_new
                    self.bt_results[event_index][var_index] = [1] * self.num_s_gof_bt
                    self.s_gof_get_quantiles(event_index, var_index)

                # VarType is a continuous distribution
                elif vt_new[0] in self.distr_list:
                    self.var_type[event_index][var_index] = vt_new[:-1]
                    self.alternative_distribution_types[event_index][var_index] = vt_new[-1]
                    self.bt_results[event_index][var_index] = [1] * self.num_s_gof_bt
                    if self.var_type[event_index][var_index][0] in ('betam', 'spec'):
                        self.s_gof_get_quantiles(event_index, var_index)

                # VarType is discrete
                elif vt_new[0] == 'd':
                    self.var_type[event_index][var_index] = vt_new
                    self.d_init_bt(event_index, var_index)

                else:
                    self.var_type[event_index][var_index] = vt_new
                self.print_changed_var_type(event_index, ['others'], vt_new, var_index, log_atom)
            else:
                self.var_type[event_index][var_index][1] += 1

    def s_gof_get_quantiles(self, event_index, var_index):
        """Generate the needed quantiles of the distribution for the sliding gof-test."""
        if self.var_type[event_index][var_index][0] == 'emp':
            # Get a list of almost equidistant indices
            indices = [int(i) for i in [self.num_init * j / (2 * self.num_s_gof_values) for j in
                       range(2 * self.num_s_gof_values)]]

            # Get the list of values and sort them
            sorted_values = copy.copy(self.event_type_detector.values[event_index][var_index][-self.num_init:])
            sorted_values.sort()

            # Generate the list of distribution values
            distr_val = []
            for index in indices:
                distr_val.append(sorted_values[index])

            self.distr_val[event_index][var_index] = distr_val
            return

        # Calculate the quantiles of the special distribution
        if self.var_type[event_index][var_index][0] == 'spec':
            ev = self.var_type[event_index][var_index][1]
            sigma = self.var_type[event_index][var_index][2]

            indices = 0 + np.array(range(2 * self.num_s_gof_values)) / (2 * self.num_s_gof_values - 1) * (
                    1000 - 1)
            indices = indices.astype(int)

            # Generate the quantiles for the var type with the standardised quantiles
            self.distr_val[event_index][var_index] = self.quantiles['spec'][indices] * sigma + ev
            return

        # Calculate the quantiles of the mixed beta distribution
        if self.var_type[event_index][var_index][0] == 'betam':
            min_val = self.var_type[event_index][var_index][1]
            scale = self.var_type[event_index][var_index][2]
            proportion = self.var_type[event_index][var_index][5]

            indices1 = [int(round(i / proportion)) for i in range(int(round(1000 * proportion)))]
            indices2 = [i for i in range(1000) if i not in indices1]

            # Generate the quantiles for the var type with the standardised quantiles
            self.distr_val[event_index][var_index] = np.append(
                self.quantiles['betam1'][indices1] * scale + min_val, self.quantiles['betam2'][indices2] * scale + min_val)
            self.distr_val[event_index][var_index].sort()
            return

    def s_gof_test(self, event_index, var_index, first_distr):
        """
        Make a gof-test.
        @return a list with the first entry True/False and as the second entry the maximal value of the step functions
        """
        num_distr_val = 2 * self.num_s_gof_values

        if self.used_gof_test == 'KS':
            # Calculate the critical value for the KS-test
            # The parameters are in the list of the critical values
            distribution = self.var_type[event_index][var_index][0]
            if distribution == 'beta':
                distribution += str(self.var_type[event_index][var_index][-1])
            if self.s_gof_alpha in self.crit_val_upd_ks and self.num_init in self.crit_val_upd_ks[self.s_gof_alpha] \
                    and self.num_s_gof_values in self.crit_val_upd_ks[self.s_gof_alpha][self.num_init] \
                    and distribution in self.crit_val_upd_ks[self.s_gof_alpha][self.num_init][self.num_s_gof_values]:
                crit_value = \
                    self.crit_val_upd_ks[self.s_gof_alpha][self.num_init][self.num_s_gof_values][distribution]
            else:
                crit_value = ((num_distr_val + self.num_s_gof_values) * (np.log(2 / self.s_gof_alpha)) / (
                    2 * num_distr_val * self.num_s_gof_values)) ** (1 / 2)

            test_statistic = 0

            # Scipy KS-test for uniformal distribution
            if self.var_type[event_index][var_index][0] == 'uni':
                test_statistic = kstest(
                    self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:], 'uniform',
                    args=(self.var_type[event_index][var_index][1], self.var_type[event_index][var_index][2]-self.var_type[event_index][
                        var_index][1]))[0]

            # Scipy KS-test for normal distribution
            elif self.var_type[event_index][var_index][0] == 'nor':
                test_statistic = kstest(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:], 'norm', args=(
                    self.var_type[event_index][var_index][1], self.var_type[event_index][var_index][2]))[0]

            # Scipy KS-test for beta distributions
            elif self.var_type[event_index][var_index][0] == 'beta':
                if self.var_type[event_index][var_index][5] == 1:
                    test_statistic = kstest(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:], 'beta', args=(
                        0.5, 0.5, self.var_type[event_index][var_index][3], self.var_type[event_index][var_index][4] - self.var_type[
                            event_index][var_index][3]))[0]

                elif self.var_type[event_index][var_index][5] == 2:
                    # Mu and sigma of the desired distribution
                    [mu, sigma] = [5 / (5 + 2), pow(5 * 2 / (5 + 2 + 1), 1 / 2) / (5 + 2)]
                    test_statistic = kstest(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:], 'beta', args=(
                            5, 2, self.var_type[event_index][var_index][1] - mu * self.var_type[event_index][var_index][2] / sigma,
                            self.var_type[event_index][var_index][2] / sigma))[0]

                elif self.var_type[event_index][var_index][5] == 3:
                    # Mu and sigma of the desired distribution
                    [mu, sigma] = [2 / (5 + 2), pow(5 * 2 / (5 + 2 + 1), 1 / 2) / (5 + 2)]
                    test_statistic = kstest(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:], 'beta', args=(
                            2, 5, self.var_type[event_index][var_index][1] - mu * self.var_type[event_index][var_index][2] / sigma,
                            self.var_type[event_index][var_index][2] / sigma))[0]

                elif self.var_type[event_index][var_index][5] == 4:
                    # Mu and sigma of the desired distribution
                    [mu, sigma] = [1 / (5 + 1), pow(5 * 1 / (5 + 1 + 1), 1 / 2) / (5 + 1)]
                    test_statistic = kstest(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:], 'beta', args=(
                            1, 5, self.var_type[event_index][var_index][1] - mu * self.var_type[event_index][var_index][2] / sigma,
                            self.var_type[event_index][var_index][2] / sigma))[0]

                elif self.var_type[event_index][var_index][5] == 5:
                    # Mu and sigma of the desired distribution
                    [mu, sigma] = [5 / (5 + 1), pow(5 * 1 / (5 + 1 + 1), 1 / 2) / (5 + 1)]
                    test_statistic = kstest(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:], 'beta', args=(
                            5, 1, self.var_type[event_index][var_index][1] - mu * self.var_type[event_index][var_index][2] / sigma,
                            self.var_type[event_index][var_index][2] / sigma))[0]
            else:
                test_statistic = ks_2samp(self.distr_val[event_index][var_index], self.event_type_detector.values[event_index][var_index][
                        -self.num_s_gof_values:])[0]

            if first_distr:
                if test_statistic > crit_value:
                    return [False, test_statistic]
                return [True, test_statistic]
            if test_statistic > crit_value:
                return [False, 1.0]
            return [True, 0.0]

        # Else self.used_gof_test == 'CM'
        # Calculate the critical value for the CM-test
        # The parameters are in the list of the critical values
        distribution = self.var_type[event_index][var_index][0]
        if distribution == 'beta':
            distribution += str(self.var_type[event_index][var_index][-1])

        if distribution in ['uni', 'nor', 'beta1']:
            crit_value = self.crit_val_upd_cm[self.s_gof_alpha][self.num_init][self.num_s_gof_values][distribution]
        elif distribution in ['beta2', 'beta3']:
            crit_value = self.crit_val_upd_cm[self.s_gof_alpha][self.num_init][self.num_s_gof_values]['beta2']
        elif distribution in ['beta4', 'beta5']:
            crit_value = self.crit_val_upd_cm[self.s_gof_alpha][self.num_init][self.num_s_gof_values]['beta4']
        else:
            crit_value = self.crit_val_hom_cm[self.s_gof_alpha][max(self.num_init, self.num_s_gof_values)][
                    min(self.num_init, self.num_s_gof_values)]

        test_statistic = 0

        # Two sample CM-test for uniformal distribution
        if self.var_type[event_index][var_index][0] == 'uni':
            min_val = min(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:])
            max_val = max(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:])
            min_upd = min_val - self.min_mod_upd_uni / (1-self.min_mod_upd_uni-self.max_mod_upd_uni) * (max_val-min_val)
            max_upd = max_val + self.max_mod_upd_uni / (1-self.min_mod_upd_uni-self.max_mod_upd_uni) * (max_val-min_val)

            # Check if the estimated min and max differ more than the critical distance and return a negative test result
            if abs(self.var_type[event_index][var_index][1] - min_upd) / (
                    self.var_type[event_index][var_index][2] - self.var_type[event_index][var_index][1]) +\
                    abs(self.var_type[event_index][var_index][2] - max_upd) / (
                    self.var_type[event_index][var_index][2] - self.var_type[event_index][var_index][1]) >\
                    self.crit_dist_upd_cm[self.s_gof_alpha][self.num_init][self.num_s_gof_values][distribution]:
                return [False, 1]

            estimated_min = min(self.var_type[event_index][var_index][1], min_upd)
            estimated_max = max(self.var_type[event_index][var_index][2], max_upd)

            test_statistic = cramervonmises((np.array(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:]) -
                                            estimated_min) / (estimated_max - estimated_min), 'uniform')

        # Two sample CM-test for normal distribution
        elif self.var_type[event_index][var_index][0] == 'nor':
            test_statistic = cramervonmises(np.array(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:]),
                                            'norm', args=(self.var_type[event_index][var_index][1],
                                                          self.var_type[event_index][var_index][2]))

        # Two sample CM-test for beta distributions
        elif self.var_type[event_index][var_index][0] == 'beta':
            if self.var_type[event_index][var_index][5] == 1:
                min_val = min(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:])
                max_val = max(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:])
                min_upd = min_val - self.min_mod_upd_beta1 / (1-self.min_mod_upd_beta1-self.max_mod_upd_beta1) * (max_val-min_val)
                max_upd = max_val + self.max_mod_upd_beta1 / (1-self.min_mod_upd_beta1-self.max_mod_upd_beta1) * (max_val-min_val)

                # Check if the estimated min and max differ more than the critical distance and return a negative test result
                if abs(self.var_type[event_index][var_index][3] - min_upd) / (
                        self.var_type[event_index][var_index][4] - self.var_type[event_index][var_index][3]) +\
                        abs(self.var_type[event_index][var_index][4] - max_upd) / (
                        self.var_type[event_index][var_index][4] - self.var_type[event_index][var_index][3]) >\
                        self.crit_dist_upd_cm[self.s_gof_alpha][self.num_init][self.num_s_gof_values][distribution]:
                    return [False, 1]

                estimated_min = min(self.var_type[event_index][var_index][3], min_upd)
                estimated_max = max(self.var_type[event_index][var_index][4], max_upd)

                test_statistic = cramervonmises((np.array(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:])
                                                - estimated_min) / (estimated_max - estimated_min), 'beta', args=(0.5, 0.5))

            elif self.var_type[event_index][var_index][5] == 2:
                min_val = min(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:])
                max_val = max(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:])
                min_upd = min_val - self.min_mod_upd_beta2 / (1-self.max_mod_upd_beta2-self.min_mod_upd_beta2) * (max_val-min_val)
                max_upd = max_val + self.max_mod_upd_beta2 / (1-self.max_mod_upd_beta2-self.min_mod_upd_beta2) * (max_val-min_val)

                # Check if the estimated min and max differ more than the critical distance and return a negative test result
                if abs(self.var_type[event_index][var_index][3] - min_upd) / (
                        self.var_type[event_index][var_index][4] - self.var_type[event_index][var_index][3]) +\
                        abs(self.var_type[event_index][var_index][4] - max_upd) / (
                        self.var_type[event_index][var_index][4] - self.var_type[event_index][var_index][3]) >\
                        self.crit_dist_upd_cm[self.s_gof_alpha][self.num_init][self.num_s_gof_values]['beta2']:
                    return [False, 1]

                estimated_min = min(self.var_type[event_index][var_index][3], min_upd)
                estimated_max = max(self.var_type[event_index][var_index][4], max_upd)

                test_statistic = cramervonmises((np.array(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:])
                                                - estimated_min) / (estimated_max - estimated_min), 'beta', args=(5, 2))

            elif self.var_type[event_index][var_index][5] == 3:
                min_val = min(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:])
                max_val = max(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:])
                min_upd = min_val - self.max_mod_upd_beta2 / (1-self.max_mod_upd_beta2-self.min_mod_upd_beta2) * (max_val-min_val)
                max_upd = max_val + self.min_mod_upd_beta2 / (1-self.max_mod_upd_beta2-self.min_mod_upd_beta2) * (max_val-min_val)

                # Check if the estimated min and max differ more than the critical distance and return a negative test result
                if abs(self.var_type[event_index][var_index][3] - min_upd) / (
                        self.var_type[event_index][var_index][4] - self.var_type[event_index][var_index][3]) +\
                        abs(self.var_type[event_index][var_index][4] - max_upd) / (
                        self.var_type[event_index][var_index][4] - self.var_type[event_index][var_index][3]) >\
                        self.crit_dist_upd_cm[self.s_gof_alpha][self.num_init][self.num_s_gof_values]['beta2']:
                    return [False, 1]

                estimated_min = min(self.var_type[event_index][var_index][3], min_upd)
                estimated_max = max(self.var_type[event_index][var_index][4], max_upd)

                test_statistic = cramervonmises((np.array(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:])
                                                - estimated_min) / (estimated_max - estimated_min), 'beta', args=(2, 5))

            elif self.var_type[event_index][var_index][5] == 4:
                ev_upd = (self.var_type[event_index][var_index][1] * self.num_init + np.mean(
                        self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:]) *
                        self.num_s_gof_values) / (self.num_init + self.num_s_gof_values)
                estimated_min = min(min(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:]),
                                    self.var_type[event_index][var_index][3])

                # Check if the estimated min and max differ more than the critical distance and return a negative test result
                if (abs(min(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:]) -
                        self.var_type[event_index][var_index][3]) >
                        self.crit_dist_upd_cm[self.s_gof_alpha][self.num_init][self.num_s_gof_values]['beta4'][0]) or (
                        max(ev_upd / self.var_type[event_index][var_index][1], self.var_type[event_index][var_index][1] / ev_upd) >
                        self.crit_dist_upd_cm[self.s_gof_alpha][self.num_init][self.num_s_gof_values]['beta4'][1]):
                    return [False, 1]

                test_statistic = cramervonmises((np.array(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:])
                                                - estimated_min) / (ev_upd-estimated_min) * (1 / (5 + 1)-self.min_mod_upd_beta4) +
                                                self.min_mod_upd_beta4, 'beta', args=(1, 5))

            elif self.var_type[event_index][var_index][5] == 5:
                ev_upd = (self.var_type[event_index][var_index][1] * self.num_init + np.mean(
                        self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:]) *
                        self.num_s_gof_values) / (self.num_init + self.num_s_gof_values)
                estimated_max = max(max(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:]),
                                    self.var_type[event_index][var_index][4])

                # Check if the estimated min and max differ more than the critical distance and return a negative test result
                if (abs(max(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:]) -
                        self.var_type[event_index][var_index][4]) >
                        self.crit_dist_upd_cm[self.s_gof_alpha][self.num_init][self.num_s_gof_values]['beta4'][0]) or (
                        max(ev_upd / self.var_type[event_index][var_index][1], self.var_type[event_index][var_index][1] / ev_upd) >
                        self.crit_dist_upd_cm[self.s_gof_alpha][self.num_init][self.num_s_gof_values]['beta4'][1]):
                    return [False, 1]

                test_statistic = cramervonmises((np.array(self.event_type_detector.values[event_index][var_index][-self.num_s_gof_values:])
                                                - estimated_max) / (estimated_max - ev_upd) * (1 / (5 + 1)-self.min_mod_upd_beta4) + 1 -
                                                self.min_mod_upd_beta4, 'beta', args=(5, 1))

        else:
            test_statistic = cramervonmises2(self.distr_val[event_index][var_index], self.event_type_detector.values[event_index][
                    var_index][-self.num_s_gof_values:])

        if first_distr:
            if test_statistic > crit_value:
                return [False, test_statistic]
            return [True, test_statistic]
        if test_statistic > crit_value:
            return [False, 1.0]
        return [True, 0.0]

    def d_test(self, event_index, var_index):
        """Make a test if the new variables follow the discrete distribution and append the result to the BT."""
        if self.used_multinomial_test == 'MT':
            # Count the appearance of the values
            values_app = [0] * len(self.var_type[event_index][var_index][1])
            for v in self.event_type_detector.values[event_index][var_index][-self.num_update:]:
                values_app[self.var_type[event_index][var_index][1].index(v)] += 1

            # probability of the values or the test sample
            prob_of_sample = self.bt_results[event_index][var_index][1].pmf(values_app)
            # Sum of the probabilities, which are smaller than the probability of the values
            smaller_prob_sum = 0
            if len(self.var_type[event_index][var_index][1]) <= 5:
                for a in range(self.num_update + 1):
                    if len(self.var_type[event_index][var_index][1]) == 2:
                        tmp_prob = self.bt_results[event_index][var_index][1].pmf([a, self.num_update - a])
                        if tmp_prob <= prob_of_sample:
                            smaller_prob_sum += tmp_prob
                    else:
                        for b in range(self.num_update - a + 1):
                            if len(self.var_type[event_index][var_index][1]) == 3:
                                tmp_prob = self.bt_results[event_index][var_index][1].pmf([a, b, self.num_update - (a + b)])
                                if tmp_prob <= prob_of_sample:
                                    smaller_prob_sum += tmp_prob
                            else:
                                for c in range(self.num_update - (a + b) + 1):
                                    if len(self.var_type[event_index][var_index][1]) == 4:
                                        tmp_prob = self.bt_results[event_index][var_index][1].pmf(
                                            [a, b, c, self.num_update - (a + b + c)])
                                        if tmp_prob <= prob_of_sample:
                                            smaller_prob_sum += tmp_prob
                                    else:
                                        for d in range(self.num_update - (a + b + c) + 1):
                                            tmp_prob = self.bt_results[event_index][var_index][1].pmf(
                                                [a, b, c, d, self.num_update - (a + b + c + d)])
                                            if tmp_prob <= prob_of_sample:
                                                smaller_prob_sum += tmp_prob

            # Make a multinomial test
            if smaller_prob_sum < self.d_alpha:
                self.bt_results[event_index][var_index][0] = self.bt_results[event_index][var_index][0][1:] + [0]
                return
            self.bt_results[event_index][var_index][0] = self.bt_results[event_index][var_index][0][1:] + [1]
            return

        if self.used_multinomial_test == 'Chi':
            # Count the appearance of the values
            values_app = [0] * len(self.var_type[event_index][var_index][1])
            for v in self.event_type_detector.values[event_index][var_index][-self.num_update:]:
                values_app[self.var_type[event_index][var_index][1].index(v)] += 1

            # Make a chisquare test
            if chisquare(values_app, f_exp=[i * self.num_update for i in self.var_type[event_index][var_index][2]])[1] < \
                    self.d_alpha:
                self.bt_results[event_index][var_index][0] = self.bt_results[event_index][var_index][0][1:] + [0]
                return
            self.bt_results[event_index][var_index][0] = self.bt_results[event_index][var_index][0][1:] + [1]
            return

        # Make an approximated multinomial test which consists of binomial tests
        if self.used_multinomial_test == 'Approx':
            # Count the appearance of the values
            values_app = [0] * len(self.var_type[event_index][var_index][1])
            for v in self.event_type_detector.values[event_index][var_index][-self.num_update:]:
                values_app[self.var_type[event_index][var_index][1].index(v)] += 1

            # Makes for each value a twosided BT. If one fails the d-test fails
            for i, value in enumerate(values_app):
                if value < self.bt_results[event_index][var_index][1][i] or value > self.bt_results[event_index][var_index][2][i]:
                    self.bt_results[event_index][var_index][0] = self.bt_results[event_index][var_index][0][1:] + [0]
                    return

            self.bt_results[event_index][var_index][0] = self.bt_results[event_index][var_index][0][1:] + [1]
            return

    def d_init_bt(self, event_index, var_index):
        """Initialize the BT for discrete variables."""
        if self.used_multinomial_test == 'MT':
            # Initialize the list for the results and the multinomialtest
            self.bt_results[event_index][var_index] = [
                [1] * self.num_d_bt, multinomial(self.num_update, self.var_type[event_index][var_index][2])]

        elif self.used_multinomial_test == 'Approx':
            # Generates a list of the lower limits of the individual BTs of the single values
            lower_limit_list = self.num_update - self.bt_min_successes_multi_p(
                self.num_update, 1 - np.array(self.var_type[event_index][var_index][2]), self.d_alpha / 2,
                event_index, var_index)

            # Generates a list of the upper limits of the individual BTs of the single values
            upper_limit_list = self.bt_min_successes_multi_p(
                self.num_update, self.var_type[event_index][var_index][2],  self.d_alpha / 2, event_index, var_index)

            # Initialize the list for the results
            self.bt_results[event_index][var_index] = [[1] * self.num_d_bt, lower_limit_list, upper_limit_list]

        else:
            # Initialize the list for the results
            self.bt_results[event_index][var_index] = [[1] * self.num_d_bt]

    def init_var_type_history_list(self, event_index):
        """Initialize the history of the variabletypes of the eventType."""
        if len(self.var_type_history_list) < event_index + 1 or self.var_type_history_list[event_index] == []:
            for _ in range(event_index + 1 - len(self.var_type_history_list)):
                self.var_type_history_list.append([])

            # [others, static, [discrete, number of appended steps], asc, desc, unique, range, ev of continuous distributions]
            if not self.var_type_history_list[event_index]:
                self.var_type_history_list[event_index] = [[[], [], [[], []], [], [], [], [[], []], [[], []]] for _ in range(len(
                    self.var_type[event_index]))]

            # Append the first entries to the history list
            # Test only the variables with paths in the target_path_list
            if self.target_path_list is None:
                index_list = range(self.length[event_index])
            # Test all variables
            else:
                index_list = self.variable_path_num[event_index]

            for var_index in index_list:
                # This section updates the history list of the variable types
                if self.var_type[event_index][var_index][0] in self.var_type_history_list_order:
                    # Index of the variable type in the list  # [others, static, [discrete, number of appended steps],
                    # asc, desc, unique, range, ev of continuous distributions]
                    type_index = self.var_type_history_list_order.index(self.var_type[event_index][var_index][0])
                else:
                    type_index = self.var_type_history_list_order.index('cont')

                for tmp_type_index, tmp_type_val in enumerate(self.var_type_history_list[event_index][var_index]):
                    if tmp_type_index == type_index:
                        if self.var_type_history_list_order[type_index] == 'cont':
                            for _, val in enumerate(tmp_type_val):
                                val.append(0)
                            # Continuously distributed variable type.
                            if self.var_type[event_index][var_index][0] == 'uni':
                                tmp_type_val[0][-1] = (
                                    self.var_type[event_index][var_index][1] + self.var_type[event_index][var_index][2]) / 2
                                tmp_type_val[1][-1] = (
                                    self.var_type[event_index][var_index][2] - self.var_type[event_index][var_index][1]) / np.sqrt(12)
                            else:
                                tmp_type_val[0][-1] = self.var_type[event_index][var_index][1]
                                tmp_type_val[1][-1] = self.var_type[event_index][var_index][2]

                        elif len(tmp_type_val) >= 1 and isinstance(tmp_type_val[0], list):
                            tmp_type_val[0].append(1)
                            for _, val in enumerate(tmp_type_val, start=1):
                                val.append(0)
                        else:
                            tmp_type_val.append(1)
                    else:
                        if len(tmp_type_val) >= 1 and isinstance(tmp_type_val[0], list):
                            for _, val in enumerate(tmp_type_val):
                                val.append(0)
                        else:
                            tmp_type_val.append(0)

    def get_indicator(self, event_index):
        """Calculate and returns a indicator for a change in the system behaviour based on the analysis of VTD."""
        # List which stores the single indicators for the variables
        indicator_list = []

        for var_index, var_val in enumerate(self.var_type_history_list[event_index]):
            if not self.event_type_detector.check_variables[event_index][var_index]:
                indicator_list.append(0)
                continue

            # List, which stores the differences of probabilities of the types, where the current history is higher than the reference.
            diff_list = []
            # Length of the reference
            len_ref = self.num_var_type_hist_ref
            # Length of the current historylist
            len_cur = self.num_var_type_considered_ind

            # Appends the positive differnces of the probabilities to diff_list
            for type_index, type_val in enumerate(var_val):
                if self.var_type_history_list_reference[event_index][var_index][1] == len_ref and sum(var_val[1]) < len_cur:
                    diff_list.append(1)
                    break
                # Differentiation of the entries, which are lists (e.g. discrete, range, continuously distributed)
                if type_index in [2, self.var_type_history_list_order.index('range'), self.var_type_history_list_order.index('cont')]:
                    if type_index == self.var_type_history_list_order.index('cont'):
                        # Continuously distributed variable type
                        if self.var_type_history_list_reference[event_index][var_index][type_index][0] == 0:
                            diff_list.append(len([1 for x in type_val[1][-self.num_var_type_considered_ind:] if x != 0]) / len_cur)
                        else:
                            var_type_ev = sum(type_val[0][-self.num_var_type_considered_ind:]) / max(len([1 for x in type_val[0][
                                -self.num_var_type_considered_ind:] if x != 0]), 1)
                            var_type_sd = sum(type_val[1][-self.num_var_type_considered_ind:]) / max(len([1 for x in type_val[1][
                                -self.num_var_type_considered_ind:] if x != 0]), 1)

                            # Formula to include the impact of the mean, standard deviation and changes of the distribution
                            if max(self.var_type_history_list_reference[event_index][var_index][type_index][1], var_type_sd) > 0:
                                diff_list.append((min(1, abs((self.var_type_history_list_reference[event_index][var_index][
                                    type_index][0] - var_type_ev) / max(abs(self.var_type_history_list_reference[event_index][var_index][
                                        type_index][0]), abs(var_type_ev))) / 3 + abs((self.var_type_history_list_reference[event_index][
                                            var_index][type_index][1] - var_type_sd) / max(abs(self.var_type_history_list_reference[
                                                event_index][var_index][type_index][1]), abs(var_type_sd))) / 3 + 1 / 3) * len([
                                                    x for x in type_val[1][-self.num_var_type_considered_ind:] if x != 0])) / len_cur)
                            else:
                                diff_list.append(0)

                    elif type_index == self.var_type_history_list_order.index('range'):
                        # range type
                        if self.var_type_history_list_reference[event_index][var_index][type_index][0] == 0:
                            diff_list.append(len([1 for x in type_val[1][-self.num_var_type_considered_ind:] if x != 0]) / len_cur)
                        else:
                            # Calculate the lower and upper limits
                            lower_limit_cur = sum(type_val[0][-self.num_var_type_considered_ind:]) / max(len([1 for x in type_val[0][
                                -self.num_var_type_considered_ind:] if x != 0]), 1)
                            upper_limit_cur = sum(type_val[1][-self.num_var_type_considered_ind:]) / max(len([1 for x in type_val[1][
                                -self.num_var_type_considered_ind:] if x != 0]), 1)
                            lower_limit_ref = self.var_type_history_list_reference[event_index][var_index][type_index][0]
                            upper_limit_ref = self.var_type_history_list_reference[event_index][var_index][type_index][1]

                            # Check if the current history contains at least one range type
                            if lower_limit_cur != upper_limit_cur:
                                # Check if the two intervalls intercept
                                if (upper_limit_ref > lower_limit_cur) and (upper_limit_cur > lower_limit_ref):
                                    diff_list.append(
                                        (max(0, lower_limit_ref - lower_limit_cur) + max(0, upper_limit_cur - upper_limit_ref)) /
                                        (max(upper_limit_cur, upper_limit_ref) - min(lower_limit_cur, lower_limit_ref)) *
                                        len([1 for x in type_val[0][-self.num_var_type_considered_ind:] if x != 0]) / len_cur)
                                else:
                                    diff_list.append(len([1 for x in type_val[0][-self.num_var_type_considered_ind:] if x != 0]) / len_cur)
                            else:
                                diff_list.append(0)
                    else:
                        tmp_max = 0
                        for j, val in enumerate(type_val):
                            if j == 0 and self.var_type_history_list_reference[event_index][var_index][type_index][j] == 0:
                                tmp_max = max(tmp_max, (sum(val[-self.num_var_type_considered_ind:]) / len_cur -
                                                        self.var_type_history_list_reference[event_index][var_index][type_index][j] /
                                                        len_ref))
                            else:
                                tmp_max = max(tmp_max, (sum(val[-self.num_var_type_considered_ind:]) / len_cur -
                                                        self.var_type_history_list_reference[event_index][var_index][type_index][j] /
                                                        len_ref) / 2)
                        diff_list.append(tmp_max)

                else:
                    if self.var_type_history_list_reference[event_index][var_index][type_index] == 0:
                        diff_list.append(sum(type_val[-self.num_var_type_considered_ind:]) / len_cur)
                    else:
                        diff_list.append(max(0, (sum(type_val[-self.num_var_type_considered_ind:]) / len_cur -
                                                 self.var_type_history_list_reference[event_index][var_index][type_index] / len_ref)) / 2)

            if len(diff_list) == 0:
                indicator_list.append(0)
            else:
                indicator_list.append(sum(diff_list))
        return indicator_list

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
                return num_bt - i
        return 0

    def bt_min_successes_multi_p(self, num_bt, p_list, alpha, event_index, var_index):
        """
        Calculate the minimal number of successes for the BT with significance alpha.
        p_list is a list of probabilities of successes and num_bt is the number of observed tests.
        """
        if f'num_bt = {num_bt}, alpha = {alpha}' in self.bt_min_succ_data:
            # Here the min_successes are not being generated, but instead the right Indices are searched for in the bt_min_succ_data-list
            return np.searchsorted(self.bt_min_succ_data[f'num_bt = {num_bt}, alpha = {alpha}'], p_list, side='left', sorter=None)

        # Calculate the min_successes normally for each value one by one
        tmp_list = []
        for i in range(len(self.var_type[event_index][var_index][1])):  # skipcq: PTC-W0060
            tmp_list.append(self.bt_min_successes(num_bt, p_list[i], alpha))
        tmp_list = np.array(tmp_list)
        return tmp_list

    def print_initial_var_type(self, event_index, log_atom):
        """Print the initial variable types."""
        if self.silence_output_without_confidence or self.silence_output_except_indicator:
            return
        try:
            data = log_atom.raw_data.decode(AminerConfig.ENCODING)
        except UnicodeError:
            data = repr(log_atom.raw_data)
        message = f'Initial detection of variable types of event {self.event_type_detector.get_event_type(event_index)}:'
        tmp_string = ''
        type_info = {}

        for var_index in range(self.length[event_index]):
            if self.var_type[event_index][var_index]:
                tmp_string += f"  Path '{self.event_type_detector.variable_key_list[event_index][var_index]}': " \
                              f"{get_vt_string(self.var_type[event_index][var_index])}\n"
                type_info[self.event_type_detector.variable_key_list[event_index][var_index]] = self.var_type[event_index][var_index]
        tmp_string = tmp_string.lstrip('  ')

        original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
        if self.output_logline:
            sorted_log_lines = [tmp_string + original_log_line_prefix + data]
            analysis_component = {'AffectedLogAtomPaths': list(log_atom.parser_match.get_match_dictionary().keys())}
        else:
            sorted_log_lines = [tmp_string + data]
            analysis_component = {'AffectedLogAtomPaths': [self.event_type_detector.variable_key_list[event_index][var_index]]}

        if self.event_type_detector.id_path_list != []:
            event_data = {'AnalysisComponent': analysis_component, 'TotalRecords': self.event_type_detector.total_records,
                          'TypeInfo': type_info, 'IDpaths': self.event_type_detector.id_path_list,
                          'IDvalues': list(self.event_type_detector.id_path_list_tuples[event_index])}
        else:
            event_data = {'AnalysisComponent': analysis_component, 'TotalRecords': self.event_type_detector.total_records,
                          'TypeInfo': type_info}
        for listener in self.anomaly_event_handlers:
            listener.receive_event(f'Analysis.{self.__class__.__name__}', message, sorted_log_lines, event_data, log_atom, self)

    def print_changed_var_type(self, event_index, vt_old, vt_new, var_index, log_atom, confidence=None):
        """Print the changed variable types."""
        if self.save_statistics and ((self.num_updates_until_var_reduction > 0 and (
                self.event_type_detector.num_event_lines[event_index] - self.num_init) / self.num_update >=
                                      self.num_updates_until_var_reduction - 1)):
            self.changed_var_types.append(self.event_type_detector.num_event_lines[event_index])

        if (self.silence_output_without_confidence and confidence is None) or self.silence_output_except_indicator:
            return
        try:
            data = log_atom.raw_data.decode(AminerConfig.ENCODING)
        except UnicodeError:
            data = repr(log_atom.raw_data)

        original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
        if self.output_logline:
            tmp_str = ''
            for x in list(log_atom.parser_match.get_match_dictionary().keys()):
                tmp_str += '  ' + x + os.linesep
            tmp_str = tmp_str.lstrip('  ')
            sorted_log_lines = [tmp_str + original_log_line_prefix + data]
            analysis_component = {'AffectedLogAtomPaths': list(log_atom.parser_match.get_match_dictionary().keys())}
        else:
            sorted_log_lines = [
                '  ' + self.event_type_detector.variable_key_list[event_index][var_index] + os.linesep + data]
            analysis_component = {'AffectedLogAtomPaths': [self.event_type_detector.variable_key_list[event_index][var_index]]}

        if self.event_type_detector.id_path_list:
            event_data = {'AnalysisComponent': analysis_component, 'TotalRecords': self.event_type_detector.total_records,
                          'TypeInfo': {'from': vt_old[0], 'to': vt_new[0], 'lines': self.event_type_detector.num_event_lines[event_index]},
                          'IDpaths': self.event_type_detector.id_path_list,
                          'IDvalues': list(self.event_type_detector.id_path_list_tuples[event_index])}
        else:
            event_data = {'AnalysisComponent': analysis_component, 'TotalRecords': self.event_type_detector.total_records,
                          'TypeInfo': {'from': vt_old[0], 'to': vt_new[0], 'lines': self.event_type_detector.num_event_lines[event_index]}}
        vt_old_string = get_vt_string(vt_old)
        vt_new_string = get_vt_string(vt_new)
        for listener in self.anomaly_event_handlers:
            listener.receive_event(
                f'Analysis.{self.__class__.__name__}',
                f"Variable type of path '{self.event_type_detector.variable_key_list[event_index][var_index]}' of event "
                f"{self.event_type_detector.get_event_type(event_index)} changed from { vt_old_string} to {vt_new_string} after the "
                f"{self.event_type_detector.num_event_lines[event_index]}-th analysed line", sorted_log_lines, event_data, log_atom, self)

    def print_reject_var_type(self, event_index, vt, var_index, log_atom):
        """Print the changed variable types."""
        if self.silence_output_without_confidence or self.silence_output_except_indicator:
            return
        try:
            data = log_atom.raw_data.decode(AminerConfig.ENCODING)
        except UnicodeError:
            data = repr(log_atom.raw_data)

        original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
        if self.output_logline:
            tmp_str = ''
            for x in list(log_atom.parser_match.get_match_dictionary().keys()):
                tmp_str += '  ' + x + os.linesep
            tmp_str = tmp_str.lstrip('  ')
            sorted_log_lines = [tmp_str + original_log_line_prefix + data]
            analysis_component = {'AffectedLogAtomPaths': list(log_atom.parser_match.get_match_dictionary().keys())}
        else:
            sorted_log_lines = [
                '  ' + self.event_type_detector.variable_key_list[event_index][var_index] + os.linesep + data]
            analysis_component = {'AffectedLogAtomPaths': [self.event_type_detector.variable_key_list[event_index][var_index]]}

        if self.event_type_detector.id_path_list != []:
            event_data = {'AnalysisComponent': analysis_component, 'TotalRecords': self.event_type_detector.total_records,
                          'TypeInfo': {'reject': vt[0], 'lines': self.event_type_detector.num_event_lines[event_index]},
                          'IDpaths': self.event_type_detector.id_path_list,
                          'IDvalues': list(self.event_type_detector.id_path_list_tuples[event_index])}
        else:
            event_data = {'AnalysisComponent': analysis_component, 'TotalRecords': self.event_type_detector.total_records,
                          'TypeInfo': {'reject': vt[0], 'lines': self.event_type_detector.num_event_lines[event_index]}}
        for listener in self.anomaly_event_handlers:
            listener.receive_event(
                f'Analysis.{self.__class__.__name__}',
                f"Variable type of path '{self.event_type_detector.variable_key_list[event_index][var_index]}' of event "
                f"{self.event_type_detector.get_event_type(event_index)} would reject the type '{vt[0]}' after the "
                f"{self.event_type_detector.num_event_lines[event_index]}-th analysed line", sorted_log_lines, event_data, log_atom, self)

    def print(self, message, log_atom, affected_path, confidence=None, indicator=None):
        """Print the message."""
        if isinstance(affected_path, str):
            affected_path = [affected_path]
        if (self.silence_output_without_confidence and confidence is None) or (
                self.silence_output_except_indicator and indicator is None):
            return
        try:
            data = log_atom.raw_data.decode(AminerConfig.ENCODING)
        except UnicodeError:
            data = repr(log_atom.raw_data)

        original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
        if self.output_logline:
            tmp_str = ''
            for x in list(log_atom.parser_match.get_match_dictionary().keys()):
                tmp_str += '  ' + x + os.linesep
            tmp_str = tmp_str.lstrip('  ')
            sorted_log_lines = [tmp_str + original_log_line_prefix + data]
            analysis_component = {'AffectedLogAtomPaths': list(log_atom.parser_match.get_match_dictionary().keys())}
        else:
            tmp_str = ''
            for x in affected_path:
                tmp_str += '  ' + x + os.linesep
            tmp_str = tmp_str.lstrip('  ')
            sorted_log_lines = [tmp_str + data]
            analysis_component = {'AffectedLogAtomPaths': affected_path}

        if self.event_type_detector.id_path_list != []:
            event_data = {'AnalysisComponent': analysis_component, 'TotalRecords': self.event_type_detector.total_records,
                          'TypeInfo': {'Confidence': confidence, 'Indicator': indicator},
                          'IDpaths': self.event_type_detector.id_path_list,
                          'IDvalues': list(self.event_type_detector.id_path_list_tuples[self.event_type_detector.current_index])}
        else:
            event_data = {'AnalysisComponent': analysis_component, 'TotalRecords': self.event_type_detector.total_records,
                          'TypeInfo': {'Confidence': confidence, 'Indicator': indicator}}
        for listener in self.anomaly_event_handlers:
            listener.receive_event(f'Analysis.{self.__class__.__name__}', message, sorted_log_lines, event_data, log_atom, self)

    def log_statistics(self, component_name):
        """
        Log statistics of an AtomHandler. Override this method for more sophisticated statistics output of the AtomHandler.
        @param component_name the name of the component which is printed in the log line.
        """
        if AminerConfig.STAT_LEVEL == 1:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %s out of %s log atoms successfully and learned %s new variable types and updated %s variable types in the "
                "last 60 minutes.", component_name, self.log_success, self.log_total, self.log_new_learned, self.log_updated)
        elif AminerConfig.STAT_LEVEL == 2:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %s out of %s log atoms successfully and learned %s new variable types and updated %s variable types in the "
                "last 60 minutes. Following new variable types were learned: %s", component_name, self.log_success, self.log_total,
                self.log_new_learned, self.log_updated, self.log_new_learned_values)
        self.log_success = 0
        self.log_total = 0
        self.log_new_learned = 0
        self.log_new_learned_values = []
        self.log_updated = 0


def convert_to_floats(list_in):
    """Give back false if one entry of the list is no float and returns the list of floats otherwise."""
    num_list = []
    for item in list_in:
        try:
            num_list.append(float(item))
        except (ValueError, TypeError):
            return []
    return num_list


def consists_of_floats(list_in):
    """Give back false if one entry of the list is no float or integer. True otherwise."""
    return all(isinstance(x, (float, int)) for x in list_in)


def consists_of_ints(list_in):
    """Give back True if all entries are integers an False otherwise."""
    return all(item == int(item) for item in list_in)


def get_vt_string(vt):
    """Return a string which states the variable type with selected parameters."""
    if vt[0] == 'stat':
        return_string = f'{vt[0]} {vt[1]}'
    elif vt[0] == 'd':
        return_string = vt[0] + ' ['
        for i, val in enumerate(vt[2]):
            if val >= 0.1:
                return_string += f'"{str(vt[1][i])}"({str(int(val*100+0.5))}%), '
        if any(val < 0.1 for _, val in enumerate(vt[2])):
            return_string += '...]'
        else:
            return_string = return_string[:-2]
            return_string += ']'
    elif vt[0] in ('asc', 'desc'):
        return_string = f'{vt[0]} [{vt[1]}]'
    elif vt[0] == 'unq':
        return_string = vt[0]
    elif vt[0] == 'others':
        return_string = vt[0]
    elif vt[0] == 'range':
        return_string = f'{vt[0]} [min: {vt[1]}, max: {vt[2]}]'
    elif vt[0] == 'uni':
        return_string = f'{vt[0]} [min: {vt[1]}, max: {vt[2]}]'
    elif vt[0] == 'nor':
        return_string = f'{vt[0]} [EV: {vt[1]}, SD: {vt[2]}]'
    elif vt[0] == 'spec':
        return_string = f'{vt[0]}{vt[5]} [EV: {vt[1]}, SD: {vt[2]}]'
    elif vt[0] == 'beta':
        if vt[5] == 1:
            return_string = f'{vt[0]}{vt[5]} [min: {vt[3]}, max: {vt[4]}]'
        else:
            return_string = f'{vt[0]}{vt[5]} [EV: {vt[1]}, SD: {vt[2]}]'
    elif vt[0] == 'betam':
        return_string = f'{vt[0]} [min: {vt[3]}, max: {vt[4]}, proportion: {vt[5]}]'
    else:
        return_string = vt[0]
    return return_string


def cramervonmises(rvs, cdf, args=()):
    """Return the cramer von mises gof test statistic."""
    if isinstance(cdf, str):
        cdf = getattr(distributions, cdf).cdf

    vals = np.sort(np.asarray(rvs))

    if vals.size <= 1:
        raise ValueError('The sample must contain at least two observations.')
    if vals.ndim > 1:
        raise ValueError('The sample must be one-dimensional.')

    n = len(vals)
    cdfvals = cdf(vals, *args)
    sum_val = 0

    for i in range(n):
        sum_val += ((2*i+1)/(2*n)-cdfvals[i])**2

    return 1/(12*n) + sum_val


def cramervonmises2(rvs1, rvs2):
    """Return the cramer von mises two sample homogeneity test statistic."""
    vals1 = np.sort(np.asarray(rvs1))
    vals2 = np.sort(np.asarray(rvs2))

    if vals1.size <= 1 or vals2.size <= 1:
        raise ValueError('The sample must contain at least two observations.')
    if vals1.ndim > 1 or vals2.ndim > 1:
        raise ValueError('The sample must be one-dimensional.')

    n1 = len(vals1)
    n2 = len(vals2)

    sum_val = 0
    index1 = 0
    index2 = 0

    for i in range(n1+n2):
        if index1 < n1 and (index2 == n2-1 or vals1[index1] < vals2[index2]):
            sum_val += n1*(i-index1)**2
            index1 += 1
        else:
            sum_val += n2*(i-index2)**2
            index2 += 1

    return sum_val/(n1*n2*(n1+n2)) - (1*n1*n2-1)/(6*(n1+n2))


def durbin_watson(rvs):
    """Return the durbin watson test statistic."""
    return sum((rvs[i+1] - rvs[i])**2 for i in range(len(rvs) - 1)) / sum(rvs[i]**2 for i in range(len(rvs)))
