"""
This file contains interface definition useful implemented by classes in this directory and for use from code outside this directory.
All classes are defined in separate files, only the namespace references are added here to simplify the code.

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
import abc
import time
import logging
from aminer.AminerConfig import STAT_LOG_NAME, DEBUG_LOG_NAME, KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD
from aminer import AminerConfig


class AtomizerFactory(metaclass=abc.ABCMeta):
    """
    This is the common interface of all factories to create atomizers for new data sources.
    These atomizers are integrated into the downstream processing pipeline.
    """

    @abc.abstractmethod
    def get_atomizer_for_resource(self, resource_name):
        """
        Get an atomizer for a given resource.
        @return a StreamAtomizer object
        """


class StreamAtomizer(metaclass=abc.ABCMeta):
    """
    This is the common interface of all binary stream atomizers.
    Atomizers in general should be good detecting and reporting malformed atoms but continue to function by attempting error correction or
    resynchronization with the stream after the bad atom. This type of atomizer also signals a stream source when the stream data cannot be
    handled at the moment to throttle reading  of the underlying stream.
    """

    @abc.abstractmethod
    def consume_data(self, stream_data, end_of_stream_flag=False):
        """
        Consume data from the underlying stream for atomizing. Data should only be consumed after splitting of an atom.
        The caller has to keep unconsumed data till the next invocation.
        @param stream_data the data offered to be consumed or zero length data when endOfStreamFlag is True (see below).
        @param end_of_stream_flag this flag is used to indicate, that the streamData offered is the last from the input stream.
        If the streamData does not form a complete atom, no rollover is expected or rollover would have honoured the atom boundaries,
        then the StreamAtomizer should treat that as an error. With rollover, consuming of the stream end data will signal the
        invoker to continue with data from next stream. When end of stream was reached but invoker has no streamData to send,
        it will invoke this method with zero-length data, which has to be consumed with a zero-length reply.
        @return the number of consumed bytes, 0 if the atomizer would need more data for a complete atom or -1 when no data was
        consumed at the moment but data might be consumed later on. The only situation where 0 is not an allowed return value
        is when end_of_stream_flag is set and stream_data not empty.
        """


class AtomHandlerInterface(metaclass=abc.ABCMeta):
    """This is the common interface of all handlers suitable for receiving log atoms."""
    output_event_handlers = None

    def __init__(self, mutable_default_args=None, learn_mode=None, stop_learning_time=None, stop_learning_no_anomaly_time=None,
                 stop_when_handled_flag=None, **kwargs):
        """
        Initialize the parameters of analysis components.
        @param mutable_default_args a list of arguments which contain mutable values and should be set to their default value indicated by
               the argument name (i.e. ending with list or dict).
        @param aminer_config configuration from analysis_context.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param id_path_list specifies group identifiers for which data should be learned/analyzed.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that all values occurring in these paths are
               considered for value range generation.
        @param persistence_id name of persistence file.
        @param learn_mode specifies whether new values should be learned.
        @param output_logline specifies whether the full parsed log atom should be provided in the output.
        @param ignore_list list of paths that are not considered for analysis, i.e., events that contain one of these paths are omitted.
        @param constraint_list list of paths that have to be present in the log atom to be analyzed.
        @param stop_learning_time switch the learn_mode to False after the time.
        @param stop_learning_no_anomaly_time switch the learn_mode to False after no anomaly was detected for that time.
        @param allowlist_rules list of rules executed until the first rule matches.
        @param subhandler_list a list of objects implementing the AtomHandlerInterface which are run until the end, if
               stop_when_handled_flag is False or until an atom handler can handle the log atom.
        @param stop_when_handled_flag True, if the atom handler processing should stop after successfully receiving the log atom.
        @param parsed_atom_handler_lookup_list contains tuples with search path string and handler. When the handler is None,
               the filter will just drop a received atom without forwarding.
        @param default_parsed_atom_handler invoke this handler when no handler was found for given match path or do not invoke any
               handler when None.
        @param target_path the path to be analyzed in the parser match of the log atom.
        @param parsed_atom_handler_dict a dictionary of match value to atom handler.
        @param default_parsed_atom_handler invoke this default handler when no value handler was found or do not invoke any handler
               when None.
        @param allow_missing_values_flag when set to True, the detector will also use matches, where one of the paths from paths does not
               refer to an existing parsed data object.
        @param tuple_transformation_function when not None, this function will be invoked on each extracted value combination list to
               transform it. It may modify the list directly or create a new one to return it.
        @param prob_thresh limit for the average probability of character pairs for which anomalies are reported.
        @param skip_repetitions boolean that determines whether only distinct values are used for character pair counting. This
               counteracts the problem of imbalanced word frequencies that distort the frequency table generated in a single aminer run.
        @param max_hypotheses maximum amount of hypotheses and rules hold in memory.
        @param hypothesis_max_delta_time time span of events considered for hypothesis generation.
        @param generation_probability probability in [0, 1] that currently processed log line is considered for hypothesis with each of the
               candidates.
        @param generation_factor likelihood in [0, 1] that currently processed log line is added to the set of candidates for hypothesis
               generation.
        @param max_observations maximum amount of evaluations before hypothesis is transformed into a rule or discarded or rule is
               evaluated.
        @param p0 expected value for hypothesis evaluation distribution.
        @param alpha significance level of the estimated values.
        @param candidates_size maximum number of stored candidates used for hypothesis generation.
        @param hypotheses_eval_delta_time duration between hypothesis evaluation phases that remove old hypotheses that are likely to remain
               unused.
        @param delta_time_to_discard_hypothesis time span required for old hypotheses to be discarded.
        @param check_rules_flag specifies whether existing rules are evaluated.
        @param window_size the length of the time window for counting in seconds.
        @param num_windows the number of previous time windows considered for expected frequency estimation.
        @param confidence_factor defines range of tolerable deviation of measured frequency from expected frequency according to
               occurrences_mean +- occurrences_std / self.confidence_factor. Default value is 0.33 = 3*sigma deviation. confidence_factor
               must be in range [0, 1].
        @param empty_window_warnings whether anomalies should be generated for too small window sizes.
        @param early_exceeding_anomaly_output states if an anomaly should be raised the first time the appearance count exceeds the range.
        @param set_lower_limit sets the lower limit of the frequency test to the specified value.
        @param set_upper_limit sets the upper limit of the frequency test to the specified value.
        @param seq_len the length of the sequences to be learned (larger lengths increase precision, but may overfit the data).
        @param allow_missing_id specifies whether log atoms without id path should be omitted (only if id path is set).
        @param timeout maximum allowed seconds between two entries of sequence; sequence is split in subsequences if exceeded.
        @param allowed_id_tuples specifies a list of tuples of allowed id's. Log atoms are omitted if not matching.
        @param min_num_vals number of the values which the list of stored logline values is being reduced to.
        @param max_num_vals the maximum list size of the stored logline values before being reduced to the last min_num_values.
        @param save_values if false the values of the log atom are not saved for further analysis. This disables values and check_variables.
        @param track_time_for_tsa if true time windows are tracked for time series analysis (necessary for the TSAArimaDetector).
        @param waiting_time_for_tsa time in seconds before the time windows tracking is initialized.
        @param num_sections_waiting_time_for_tsa the number used to initialize the TSAArimaDetector with calculate_time_steps.
        @param histogram_definitions a list of tuples containing the target property path to analyze and the BinDefinition to apply.
        @param report_interval delay in seconds before re-reporting. The parameter is applied to the parsed record data time, not the system
               time. Hence, reports can be delayed when no data is received.
        @param reset_after_report_flag reset the histogram data after reporting.
        @param bin_definition the bin definition (LinearNumericBinDefinition, ModuloTimeBinDefinition) to be used.
        @param target_value_list if not None, only match log atom if the match value is contained in the list.
        @param timestamp_path if not None, use this path value for timestamp based bins.
        @param min_bin_elements evaluate the latest bin only after at least that number of elements was added to it.
        @param min_bin_time evaluate the latest bin only when the first element is received after min_bin_time has elapsed.
        @param debug_mode if true, generate an analysis report even when average of last bin was within expected range.
        @param stream the stream on which the match results are written.
        @param separator a string to be added between match values in the output stream.
        @param missing_value_string a string which is added if no match was found.
        @param time_output_threshold threshold for the tested minimal transition time which has to be exceeded to be tested.
        @param anomaly_threshold threshold for the confidence which must be exceeded to raise an anomaly.
        @param default_interval time in seconds before a value is reported missing. The parameter is applied to the parsed record data time,
               not the system time. Hence, reports can be delayed when no data is received.
        @param realert_interval time in seconds before a value is reported missing for a second time. The parameter is applied to the
               parsed record data time, not the system time. Hence, reports can be delayed when no data is received.
        @param combine_values if true the combined values are used as identifiers. When false, individual values are checked.
        @param min_allowed_time_diff the minimum amount of time in seconds after the first appearance of a log atom with a specific id
               that is waited for other log atoms with the same id to occur. The maximum possible time to keep an incomplete combo
               is 2*min_allowed_time_diff
        @param target_label_list a list of labels for the target_path_list. This list must have the same size as target_path_list.
        @param split_reports_flag if true every path produces an own report, otherwise one report for all paths is produced.
        @param event_type_detector used to track the number of occurring events.
        @param num_init number of lines processed before the period length is calculated.
        @param force_period_length states if the period length is calculated through the ACF, or if the period length is forced to
               be set to set_period_length.
        @param set_period_length states how long the period length is if force_period_length is set to True.
        @param alpha_bt significance level for the bt test.
        @param num_results_bt number of results which are used in the binomial test.
        @param num_min_time_history number of lines processed before the period length is calculated.
        @param num_max_time_history maximum number of values of the time_history.
        @param num_periods_tsa_ini number of periods used to initialize the Arima-model.
        @param time_period_length length of the time window for which the appearances of log lines are identified with each other.
               Value of 86400 specifies a day and 604800 a week.
        @param max_time_diff maximal time difference in seconds for new times. If the difference of the new time to all previous times is
               greater than max_time_diff the new time is considered an anomaly.
        @param num_reduce_time_list number of new time entries appended to the time list, before the list is being reduced.
        @param min_anomaly_score the minimum computed outlier score for reporting anomalies. Scores are scaled by training data, i.e.,
               reasonable minimum scores are >1 to detect outliers with respect to currently trained PCA matrix.
        @param min_variance the minimum variance covered by the principal components in range [0, 1].
        @param parallel_check_count number of rule detection checks to run in parallel.
        @param record_count_before_event number of events used to calculate statistics (i.e., window size)
        @param use_path_match if true rules are build based on path existence
        @param use_value_match if true rules are built based on actual values
        @param min_rule_attributes minimum number of attributes forming a rule
        @param max_rule_attributes maximum number of attributes forming a rule
        @param ruleset a list of MatchRule rules with appropriate CorrelationRules attached as actions.
        @param exit_on_error_flag exit the aminer forcefully if a log atom with a wrong timestamp is found.
        @param acf_pause_interval_percentage states which area of the results of the ACF are not used to find the highest peak.
        @param acf_auto_pause_interval states if the pause area is automatically set.
               If enabled, the variable acf_pause_interval_percentage loses its functionality.
        @param acf_auto_pause_interval_num_min states the number of values in which a local minima must be the minimum, to be considered a
               local minimum of the function and not an outlier.
        @param build_sum_over_values states if the sum of a series of counts is build before applying the TSA.
        @param num_division_time_step number of division of the time window to calculate the time step.
        @param acf_threshold threshold, which has to be exceeded by the highest peak of the cdf function of the time series, to be analyzed.
        @param round_time_interval_threshold threshold for the rounding of the time_steps to the times in self.assumed_time_steps.
               The higher the threshold the easier the time is rounded to the next time in the list.
        @param min_log_lines_per_time_step states the minimal average number of log lines per time step to make a TSA.
        @param num_update number of lines after the initialization after which the correlations are periodically tested and updated.
        @param disc_div_thres diversity threshold for variables to be considered discrete.
        @param num_steps_create_new_rules number of update steps, for which new rules are generated periodically.
               States False if rules should not be updated.
        @param num_end_learning_phase number of update steps until the update phase ends and the test phase begins;
               False if no End should be defined.
        @param check_cor_thres threshold for the number of allowed different values of the distribution to be considered a correlation.
        @param check_cor_prob_thres threshold for the difference of the probability of the values to be considered a correlation.
        @param check_cor_num_thres number of allowed different values for the calculation if the distribution can be considered a
               correlation.
        @param min_values_cors_thres minimal number of appearances of values on the left side to consider the distribution as a possible
               correlation.
        @param new_vals_alarm_thres threshold which has to be exceeded by number of new values divided by number of old values to generate
               an alarm.
        @param num_bt number of considered test-samples for the binomial test.
        @param used_homogeneity_test states the used homogeneity test which is used for the updates and tests of the correlations.
               The implemented methods are ['Chi', 'MaxDist'].
        @param alpha_chisquare_test significance level alpha for the chi-square test.
        @param max_dist_rule_distr maximum distance between the distribution of the rule and the distribution of the read in values before
               the rule fails.
        @param used_presel_meth used preselection methods.
               The implemented methods are ['matchDiscDistr', 'excludeDueDistr', 'matchDiscVals', 'random']
        @param intersect_presel_meth states if the intersection or the union of the possible correlations found by the used_presel_meth is
               used for the resulting correlations.
        @param percentage_random_cors percentage of the randomly picked correlations of all possible ones in the preselection method random.
        @param match_disc_vals_sim_tresh similarity threshold for the preselection method pick_cor_match_disc_vals.
        @param exclude_due_distr_lower_limit lower limit for the maximal appearance to one value of the distributions.
               If the maximal appearance is exceeded the variable is excluded.
        @param match_disc_distr_threshold threshold for the preselection method pick_cor_match_disc_distr.
        @param used_cor_meth used correlation detection methods. The implemented methods are ['Rel', 'WRel'].
        @param used_validate_cor_meth used validation methods. The implemented methods are ['coverVals', 'distinctDistr'].
        @param validate_cor_cover_vals_thres threshold for the validation method cover_vals. The higher the threshold the more correlations
               must be detected to be validated a correlation.
        @param validate_cor_distinct_thres threshold for the validation method distinct_distr. The threshold states which value the variance
               of the distributions have to surpass to be considered real correlations. The lower the value the less likely that the
               correlations are being rejected.
        @param used_gof_test states the used test statistic for the continuous data type. Implemented are the 'KS' and 'CM' tests.
        @param gof_alpha significance niveau for p-value for the distribution test of the initialization. Recommended values are the
               implemented values of crit_val_ini_ks and crit_val_upd_ks or _cm.
        @param s_gof_alpha significance niveau for p-value for the sliding KS-test in the update step. Recommended values are the
               implemented values of crit_val_upd_ks.
        @param s_gof_bt_alpha significance niveau for the binomial test of the test results of the s_gof-test.
        @param d_alpha significance niveau for the binomial test of the single discrete variables. If used_multinomial_test == 'Approx' then
               faster runtime for values in the p list of bt_min_succ_data.
        @param d_bt_alpha significance niveau for the binomial test of the test results of the discrete tests.
        @param div_thres threshold for diversity of the values of a variable (the higher the more values have to be distinct to be
               considered to be continuous distributed).
        @param sim_thres threshold for similarity of the values of a variable (the higher the more values have to be common to be considered
               discrete).
        @param indicator_thres threshold for the variable indicators to be used in the event indicator.
        @param num_update_unq number of values for which the values of type unq is unique (the last num_update + num_update_unq values are
               unique).
        @param num_s_gof_values number of values which are tested in the s_gof-test. The value has to be <= num_init, >= num_update.
               Recommended values are the implemented values of crit_val_upd_ks.
        @param num_s_gof_bt number of tested s_gof-Tests for the binomial test of the test results of the s_gof tests.
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
        """
        allowed_kwargs = [
            "mutable_default_args", "aminer_config", "anomaly_event_handlers", "learn_mode", "persistence_id", "id_path_list",
            "stop_learning_time", "stop_learning_no_anomaly_time", "output_logline", "target_path_list", "constraint_list", "ignore_list",
            "allowlist_rules", "subhandler_list", "stop_when_handled_flag", "parsed_atom_handler_lookup_list",
            "default_parsed_atom_handler", "target_path", "parsed_atom_handler_dict", "allow_missing_values_flag",
            "tuple_transformation_function", "prob_thresh", "skip_repetitions", "max_hypotheses", "hypothesis_max_delta_time",
            "generation_probability", "generation_factor", "max_observations", "p0", "alpha", "candidates_size",
            "hypotheses_eval_delta_time", "delta_time_to_discard_hypothesis", "check_rules_flag", "window_size", "num_windows",
            "confidence_factor", "empty_window_warnings", "early_exceeding_anomaly_output", "set_lower_limit", "set_upper_limit", "seq_len",
            "allow_missing_id", "timeout", "allowed_id_tuples", "min_num_vals", "max_num_vals", "save_values", "track_time_for_tsa",
            "waiting_time", "num_sections_waiting_time", "histogram_definitions", "report_interval", "reset_after_report_flag",
            "bin_definition", "target_value_list", "timestamp_path", "min_bin_elements", "min_bin_time", "debug_mode", "stream",
            "separator", "missing_value_string", "num_log_lines_solidify_matrix", "time_output_threshold", "anomaly_threshold",
            "default_interval", "realert_interval", "combine_values", "min_allowed_time_diff", "target_label_list", "split_reports_flag",
            "event_type_detector", "num_init", "force_period_length", "set_period_length", "alpha_bt", "num_results_bt",
            "num_min_time_history", "num_max_time_history", "num_periods_tsa_ini", "time_period_length", "max_time_diff",
            "num_reduce_time_list", "min_anomaly_score", "min_variance", "parallel_check_count", "record_count_before_event",
            "use_path_match", "use_value_match", "min_rule_attributes", "max_rule_attributes", "ruleset", "exit_on_error_flag",
            "acf_pause_interval_percentage", "acf_auto_pause_interval", "acf_auto_pause_interval_num_min", "build_sum_over_values",
            "num_division_time_step", "acf_threshold", "round_time_interval_threshold", "min_log_lines_per_time_step", "num_update",
            "disc_div_thres", "num_steps_create_new_rules", "num_upd_until_validation", "num_end_learning_phase", "check_cor_thres",
            "check_cor_prob_thres", "check_cor_num_thres", "min_values_cors_thres", "new_vals_alarm_thres", "num_bt",
            "used_homogeneity_test", "alpha_chisquare_test", "max_dist_rule_distr", "used_presel_meth", "intersect_presel_meth",
            "percentage_random_cors", "match_disc_vals_sim_tresh", "exclude_due_distr_lower_limit", "match_disc_distr_threshold",
            "used_cor_meth", "used_validate_cor_meth", "validate_cor_cover_vals_thres", "validate_cor_distinct_thres", "used_gof_test",
            "gof_alpha", "s_gof_alpha", "s_gof_bt_alpha", "d_alpha", "d_bt_alpha", "div_thres", "sim_thres", "indicator_thres",
            "num_update_unq", "num_s_gof_values", "num_s_gof_bt", "num_d_bt", "num_pause_discrete", "num_pause_others", "test_gof_int",
            "num_stop_update", "silence_output_without_confidence", "silence_output_except_indicator", "num_var_type_hist_ref",
            "num_update_var_type_hist_ref", "num_var_type_considered_ind", "num_stat_stop_update", "num_updates_until_var_reduction",
            "var_reduction_thres", "num_skipped_ind_for_weights", "num_ind_for_weights", "used_multinomial_test", "use_empiric_distr",
            "used_range_test", "range_alpha", "range_threshold", "num_reinit_range", "range_limits_factor", "dw_alpha", "save_statistics"
        ]
        self.log_success = 0
        self.log_total = 0
        self.persistence_id = None  # persistence_id is always needed.
        for argument, value in list(locals().items())[1:-1]:  # skip self parameter and kwargs
            if value is not None:
                setattr(self, argument, value)
        for argument, value in kwargs.items():  # skip self parameter and kwargs
            if argument not in allowed_kwargs:
                msg = f"Argument {argument} is unknown. Consider changing it or adding it to the allowed_kwargs list."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)
            setattr(self, argument, value)

        if learn_mode is False and (stop_learning_time is not None or stop_learning_no_anomaly_time is not None):
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

        if hasattr(self, "aminer_config"):
            self.next_persist_time = time.time() + self.aminer_config.config_properties.get(
                KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)

        if mutable_default_args is not None:
            for argument in mutable_default_args:
                if hasattr(self, argument) and getattr(self, argument) is not None:
                    continue
                if argument.endswith("list"):
                    setattr(self, argument, [])
                elif argument.endswith("dict"):
                    setattr(self, argument, {})
                elif argument.endswith("set"):
                    setattr(self, argument, set())
                elif argument.endswith("tuple"):
                    setattr(self, argument, tuple())

        if hasattr(self, "subhandler_list"):
            if (not isinstance(self.subhandler_list, list)) or \
                    (not all(isinstance(handler, AtomHandlerInterface) for handler in self.subhandler_list)):
                msg = "Only subclasses of AtomHandlerInterface allowed in subhandler_list."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)
            for handler_pos, handler_element in enumerate(self.subhandler_list):
                self.subhandler_list[handler_pos] = (handler_element, stop_when_handled_flag)
        if hasattr(self, "allowed_id_tuples"):
            if self.allowed_id_tuples is None:
                self.allowed_id_tuples = []
            else:
                self.allowed_id_tuples = [tuple(tuple_list) for tuple_list in self.allowed_id_tuples]

        if hasattr(self, "confidence_factor") and not 0 <= self.confidence_factor <= 1:
            logging.getLogger(DEBUG_LOG_NAME).warning('confidence_factor must be in the range [0,1]!')
            self.confidence_factor = 1

    @abc.abstractmethod
    def receive_atom(self, log_atom):
        """
        Receive a log atom from a source.
        @param log_atom binary raw atom data
        @return True if this handler was really able to handle and process the atom. Depending on this information, the caller
        may decide if it makes sense passing the atom also to other handlers or to retry later. This behaviour has to be documented
        at each source implementation sending LogAtoms.
        """

    def log_statistics(self, component_name):
        """
        Log statistics of an AtomHandler. Override this method for more sophisticated statistics output of the AtomHandler.
        @param component_name the name of the component which is printed in the log line.
        """
        if AminerConfig.STAT_LEVEL > 0:
            logging.getLogger(STAT_LOG_NAME).info("'%s' processed %d out of %d log atoms successfully in the last 60"
                                                  " minutes.", component_name, self.log_success, self.log_total)
        self.log_success = 0
        self.log_total = 0


class LogDataResource(metaclass=abc.ABCMeta):
    """
    This is the superinterface of each logdata resource monitored by aminer.
    The interface is designed in a way, that instances of same subclass can be used both on aminer parent process side for keeping track of
    the resources and forwarding the file descriptors to the child, but also on child side for the same purpose. The only difference is,
    that on child side, the stream reading and read continuation features are used also. After creation on child side, this is the sole
    place for reading and closing the streams. An external process may use the file descriptor only to wait for input via select.
    """

    @abc.abstractmethod
    def __init__(self, log_resource_name, log_stream_fd, default_buffer_size=1 << 16, repositioning_data=None):
        """
        Create a new LogDataResource. Object creation must not touch the logStreamFd or read any data, unless repositioning_data  was given.
        In the later case, the stream has to support seek operation to reread data.
        @param log_resource_name the unique encoded name of this source as byte array.
        @param log_stream_fd the stream for reading the resource or -1 if not yet opened.
        @param repositioning_data if not None, attemt to position the the stream using the given data.
        """

    @abc.abstractmethod
    def open(self, reopen_flag=False):
        """
        Open the given resource.
        @param reopen_flag when True, attempt to reopen the same resource and check if it differs from the previously opened one.
        @raise Exception if valid logStreamFd was already provided, is still open and reopenFlag is False.
        @raise OSError when opening failed with unexpected error.
        @return True if the resource was really opened or False if opening was not yet possible but should be attempted again.
        """

    @abc.abstractmethod
    def get_resource_name(self):
        """Get the name of this log resource."""

    @abc.abstractmethod
    def get_file_descriptor(self):
        """Get the file descriptor of this open resource."""

    @abc.abstractmethod
    def fill_buffer(self):
        """
        Fill the buffer data of this resource. The repositioning information is not updated, update_position() has to be used.
        @return the number of bytes read or -1 on error or end.
        """

    @abc.abstractmethod
    def update_position(self, length):
        """Update the positioning information and discard the buffer data afterwards."""

    @abc.abstractmethod
    def get_repositioning_data(self):
        """Get the data for repositioning the stream. The returned structure has to be JSON serializable."""

    @abc.abstractmethod
    def close(self):
        """Close this logdata resource. Data access methods will not work any more afterwards."""
