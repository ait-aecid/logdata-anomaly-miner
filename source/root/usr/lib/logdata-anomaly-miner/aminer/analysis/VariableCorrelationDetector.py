"""This module defines a detector for correlations between discrete variables."""
import numpy as np
import logging
import sys
from scipy.stats import chi2
import time

from aminer.AminerConfig import DEBUG_LOG_NAME, build_persistence_file_name, KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD
from aminer.AnalysisChild import AnalysisContext
from aminer.events.EventInterfaces import EventSourceInterface
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface
from aminer.util import PersistenceUtil


class VariableCorrelationDetector(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface):
    """
    This class first finds for each eventType a list of pairs of variables, which are afterwards tested if they are correlated.
    For this a couple of preselection methods can be used. (See self.used_presel_meth)
    Thereafter the correlations are checked, with the selected methods. (See self.used_cor_meth)
    This module builds upon the event_type_detector.
    """

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, anomaly_event_handlers, event_type_detector, persistence_id='Default', target_path_list=None,
                 num_init=100, num_update=100, disc_div_thres=0.3, num_steps_create_new_rules=-1, num_upd_until_validation=20,
                 num_end_learning_phase=-1, check_cor_thres=0.5, check_cor_prob_thres=1, check_cor_num_thres=10,
                 min_values_cors_thres=5, new_vals_alarm_thres=3.5, num_bt=30, alpha_bt=0.1, used_homogeneity_test='Chi',
                 alpha_chisquare_test=0.05, max_dist_rule_distr=0.1, used_presel_meth=None, intersect_presel_meth=False,
                 percentage_random_cors=0.20, match_disc_vals_sim_tresh=0.7, exclude_due_distr_lower_limit=0.4,
                 match_disc_distr_threshold=0.5, used_cor_meth=None, used_validate_cor_meth=None, validate_cor_cover_vals_thres=0.7,
                 validate_cor_distinct_thres=0.05, ignore_list=None, constraint_list=None, learn_mode=True, stop_learning_time=None,
                 stop_learning_no_anomaly_time=None):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param event_type_detector used to track the number of occurring events.
        @param persistence_id name of persistence file.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that all values occurring in these paths are
               considered for value range generation.
        @param num_init minimal number of lines of one event type to initialize the correlation rules.
        @param num_update number of lines after the initialization after which the correlations are periodically tested and updated.
        @param disc_div_thres diversity threshold for variables to be considered discrete.
        @param num_steps_create_new_rules number of update steps, for which new rules are generated periodically.
               States False if rules should not be updated.
        @param num_upd_until_validation number of update steps, for which the rules are validated periodically.
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
        @param alpha_bt significance niveau for the binomial test for the test results.
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
        @param validate_cor_cover_vals_thres threshold for the validation method coverVals. The higher the threshold the more correlations
               must be detected to be validated a correlation.
        @param validate_cor_distinct_thres threshold for the validation method distinctDistr. The threshold states which value the variance
               of the distributions have to surpass to be considered real correlations. The lower the value the less likely that the
               correlations are being rejected.
        @param ignore_list list of paths that are not considered for analysis, i.e., events that contain one of these paths are omitted.
        @param constraint_list list of paths that have to be present in the log atom to be analyzed.
        @param learn_mode specifies whether new values should be learned.
        @param stop_learning_time switch the learn_mode to False after the time.
        @param stop_learning_no_anomaly_time switch the learn_mode to False after no anomaly was detected for that time.
        """
        # avoid "defined outside init" issue
        self.learn_mode, self.stop_learning_timestamp, self.next_persist_time, self.log_success, self.log_total = [None]*5
        super().__init__(
            mutable_default_args=["target_path_list", "ignore_list", "constraint_list"], aminer_config=aminer_config,
            anomaly_event_handlers=anomaly_event_handlers, event_type_detector=event_type_detector, persistence_id=persistence_id,
            target_path_list=target_path_list, num_init=num_init, num_update=num_update, disc_div_thres=disc_div_thres,
            num_steps_create_new_rules=num_steps_create_new_rules, num_upd_until_validation=num_upd_until_validation,
            num_end_learning_phase=num_end_learning_phase, check_cor_thres=check_cor_thres, check_cor_prob_thres=check_cor_prob_thres,
            check_cor_num_thres=check_cor_num_thres, min_values_cors_thres=min_values_cors_thres, new_vals_alarm_thres=new_vals_alarm_thres,
            num_bt=num_bt, alpha_bt=alpha_bt, used_homogeneity_test=used_homogeneity_test, alpha_chisquare_test=alpha_chisquare_test,
            max_dist_rule_distr=max_dist_rule_distr, used_presel_meth=used_presel_meth, intersect_presel_meth=intersect_presel_meth,
            percentage_random_cors=percentage_random_cors, match_disc_vals_sim_tresh=match_disc_vals_sim_tresh,
            exclude_due_distr_lower_limit=exclude_due_distr_lower_limit, match_disc_distr_threshold=match_disc_distr_threshold,
            used_cor_meth=used_cor_meth, used_validate_cor_meth=used_validate_cor_meth,
            validate_cor_cover_vals_thres=validate_cor_cover_vals_thres, validate_cor_distinct_thres=validate_cor_distinct_thres,
            ignore_list=ignore_list, constraint_list=constraint_list, learn_mode=learn_mode, stop_learning_time=stop_learning_time,
            stop_learning_no_anomaly_time=stop_learning_no_anomaly_time
        )

        self.event_type_detector.add_following_modules(self)
        self.variable_type_detector = None
        if any(self.event_type_detector.following_modules[j].__class__.__name__ == 'VariableTypeDetector' for j in range(
                len(self.event_type_detector.following_modules))):
            try:
                self.variable_type_detector = self.event_type_detector.following_modules[next(j for j in range(
                    len(self.event_type_detector.following_modules)) if
                        self.event_type_detector.following_modules[j].__class__.__name__ == 'VariableTypeDetector')]
            except StopIteration:
                pass

        if self.event_type_detector.min_num_vals < max(num_init, num_update):
            msg = f'Changed the parameter min_num_vals of the ETD from {self.event_type_detector.min_num_vals} to ' \
                  f'{max(num_init, num_update)} to prevent errors in the execution of the VCD'
            logging.getLogger(DEBUG_LOG_NAME).warning(msg)
            print('WARNING: ' + msg, file=sys.stderr)
            self.event_type_detector.min_num_vals = max(num_init, num_update)
        if self.event_type_detector.max_num_vals < max(num_init, num_update) + 500:
            msg = f'Changed the parameter max_num_vals of the ETD from {self.event_type_detector.max_num_vals} to ' \
                  f'{max(num_init, num_update) + 500} to prevent errors in the execution of the VCD'
            logging.getLogger(DEBUG_LOG_NAME).warning(msg)
            print('WARNING: ' + msg, file=sys.stderr)
            self.event_type_detector.max_num_vals = max(num_init, num_update) + 500
        if self.used_homogeneity_test not in ['Chi', 'MaxDist']:
            raise ValueError(f"The homogeneity test '{used_homogeneity_test}' does not exist!")
        if self.used_presel_meth is None:
            self.used_presel_meth = []
        for presel_meth in self.used_presel_meth:
            if presel_meth not in ['matchDiscDistr', 'excludeDueDistr', 'matchDiscVals', 'random']:
                raise ValueError(f"The preselection method '{presel_meth}' does not exist!")
        if self.percentage_random_cors <= 0. or self.percentage_random_cors >= 1.:
            raise ValueError('The Random preselection method makes no sense if percentage_random_cors = %f. If the percentage_random_cors'
                             ' is >= 1.0 better use no preselection method for that case.')
        if self.used_cor_meth is None or self.used_cor_meth == []:
            self.used_cor_meth = ['Rel', 'WRel']
        for cor_meth in self.used_cor_meth:
            if cor_meth not in ['Rel', 'WRel']:
                raise ValueError(f"The correlation rule '{cor_meth}' does not exist!")
        if self.used_validate_cor_meth is None:
            self.used_validate_cor_meth = ['coverVals', 'distinctDistr']
            # The distinctDistr validation requires the 'WRel' method.
            if 'WRel' not in self.used_cor_meth:
                self.used_validate_cor_meth = ['coverVals']
        for validate_cor_meth in self.used_validate_cor_meth:
            if validate_cor_meth not in ['coverVals', 'distinctDistr']:
                raise ValueError(f"The validation correlation rule '{validate_cor_meth}' does not exist!")
        if 'WRel' not in self.used_cor_meth and 'distinctDistr' in self.used_validate_cor_meth:
            raise ValueError("The 'distinctDistr' validation correlation rule requires the 'WRel' correlation method!")

        # Calculate the minimal number of successes for the BT
        self.min_successes_bt = self.bt_min_successes(self.num_bt, 1 - self.alpha_bt, self.alpha_bt)

        self.update_rules = []  # List which states for what event types the rules are updated
        self.generate_rules = []  # List which states for what event types new rules are being generated
        self.min_successes_bt = 0  # Minimal number of successes for the binomialtest
        self.discrete_indices = []  # List of the indices to every event type which are assumed to be discrete
        self.pos_var_val = []  # List of the possible values to the single variables of the event types
        self.pos_var_cor = []  # List of all pairs of variables of the event types which are assumed to be correlated
        self.rel_list = []  # List of lists, that saves the data for the found correlations with the method Rel.
        # First index states the event_index, second index states which correlation is examined, third index states which direction of the
        # correlation is examined, fourth index states the value of the first variable and the fifth value states the value of the second
        # variable. The content is the number of appearance in the log lines.
        self.w_rel_list = []  # List of lists, that saves the data for the correlation finding with WRel.
        # First index states the event_index, second index states which correlation is examined, third index states which direction of the
        # correlation is examined, fourth index states the value of the first variable and the fifth value states the value of the second
        # variable. The content is the number of appearance in the log lines.
        self.w_rel_num_ll_to_vals = []  # List of the number of lines in which the values of the first variable have appeared
        self.w_rel_ht_results = []  # List of the results of the homogeneity tests for the binomial test
        self.w_rel_confidences = []  # List for the confidences of the homogeneity tests
        self.log_atom = None

        # Loads the persistence
        self.persistence_id = persistence_id
        self.persistence_file_name = build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)

        # Imports the persistence if self.event_type_detector.load_persistence_data is True
        if persistence_data is not None:
            self.load_persistence_data(persistence_data)

    # skipcq: PYL-W0613
    def receive_atom(self, log_atom):
        """
        Receive an parsed atom and the information about the parser match.
        @param log_atom the parsed log atom
        @return True if this handler was really able to handle and process the match.
        """
        event_index = self.event_type_detector.current_index
        if event_index == -1:
            return False
        if self.learn_mode is True and self.stop_learning_timestamp is not None and \
                self.stop_learning_timestamp < log_atom.atom_time:
            logging.getLogger(DEBUG_LOG_NAME).info(f"Stopping learning in the {self.__class__.__name__}.")
            self.learn_mode = False

        parser_match = log_atom.parser_match
        for ignore_path in self.ignore_list:
            if ignore_path in parser_match.get_match_dictionary().keys():
                return False
        constraint_path_flag = False
        for constraint_path in self.constraint_list:
            if parser_match.get_match_dictionary().get(constraint_path) is not None:
                constraint_path_flag = True
                break
        if not constraint_path_flag and self.constraint_list != []:
            return False
        self.log_atom = log_atom
        if self.event_type_detector.num_event_lines[event_index] == self.num_init:  # Initialisation Phase
            self.init_cor(event_index)  # Initialise the correlations

            if self.update_rules[event_index] and self.learn_mode:
                self.validate_cor()  # Validate the correlations and removes the cors, which fail the requirements
                if self.stop_learning_timestamp is not None and self.stop_learning_no_anomaly_time is not None:
                    self.stop_learning_timestamp = time.time() + self.stop_learning_no_anomaly_time

            # Print the found correlations
            if 'Rel' in self.used_cor_meth:
                self.print_ini_rel(event_index)
            if 'WRel' in self.used_cor_meth:
                self.print_ini_w_rel(event_index)

        # Updates or tests the correlations
        elif self.event_type_detector.num_event_lines[event_index] > self.num_init and \
                (self.event_type_detector.num_event_lines[event_index] - self.num_init) % self.num_update == 0:
            # Checks if the correlations should be updated or tested
            if self.num_end_learning_phase < 0 or self.event_type_detector.num_event_lines[event_index]-self.num_init <= \
                    (self.num_update*self.num_end_learning_phase):
                # Update Phase
                self.update_rules[event_index] = True
                if self.num_steps_create_new_rules > 0 and ((self.event_type_detector.num_event_lines[
                        event_index]-self.num_init) / self.num_update) % self.num_steps_create_new_rules == 0:  # generate new rules
                    self.generate_rules[event_index] = True
                else:
                    self.generate_rules[event_index] = False
            else:
                # Test Phase
                self.update_rules[event_index] = False
                self.generate_rules[event_index] = False

            # Updates or tests the correlations
            self.update_or_test_cor(event_index)

            if self.generate_rules[event_index] and ((self.event_type_detector.num_event_lines[
                    event_index] - self.num_init) / self.num_update / self.num_steps_create_new_rules) % self.num_upd_until_validation == 0:
                self.validate_cor()  # Validate the correlations and removes the cors, which fail the requirements
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
        persistence_data = [self.pos_var_cor, self.pos_var_val, self.discrete_indices, self.update_rules, self.generate_rules,
                            self.rel_list, self.w_rel_list, self.w_rel_num_ll_to_vals, self.w_rel_ht_results, self.w_rel_confidences]
        PersistenceUtil.store_json(self.persistence_file_name, persistence_data)

    def load_persistence_data(self, persistence_data):
        """Extract the persistence data and appends various lists to create a consistent state."""
        self.pos_var_cor = persistence_data[0]
        self.pos_var_val = persistence_data[1]
        self.discrete_indices = persistence_data[2]
        self.update_rules = persistence_data[3]
        self.generate_rules = persistence_data[4]
        self.rel_list = persistence_data[5]
        self.w_rel_list = persistence_data[6]
        self.w_rel_num_ll_to_vals = persistence_data[7]
        self.w_rel_ht_results = persistence_data[8]
        self.w_rel_confidences = persistence_data[9]

    def allowlist_event(self, event_type, event_data, allowlisting_data):  # skipcq: PYL-W0613
        """
        Allowlist an event generated by this source using the information emitted when generating the event.
        @return a message with information about allowlisting
        @throws Exception when allowlisting of this special event using given allowlisting_data was not possible.
        """
        if event_type != f'Analysis.{self.__class__.__name__}':
            raise Exception('Event not from this source')
        raise Exception('No allowlisting for algorithm malfunction or configuration errors')

    def init_cor(self, event_index):
        """Initialise the possible correlations and runs the init-functions for the methods in self.used_cor_meth."""
        # Append the supporting lists if necessary
        if len(self.pos_var_cor) < event_index+1:
            for i in range(event_index + 1 - len(self.pos_var_cor)):
                self.pos_var_cor.append([])
                self.pos_var_val.append([])
                self.discrete_indices.append([])
                self.update_rules.append(True)
                self.generate_rules.append(True)

        # Initialise the indices to the assumed discrete variables
        if len(self.discrete_indices[event_index]) == 0:
            # If the var_typeD is linked, append the discrete fields
            if self.variable_type_detector is not None:
                for i in range(len(self.event_type_detector.variable_key_list[event_index])):  # skipcq: PTC-W0060
                    if len(self.variable_type_detector.var_type[event_index][i]) > 0 and \
                            self.variable_type_detector.var_type[event_index][i][0] == 'd' and (
                            self.target_path_list == [] or
                            self.event_type_detector.variable_key_list[event_index][i] in self.target_path_list):
                        self.discrete_indices[event_index].append(i)
                        self.pos_var_val[event_index].append(self.variable_type_detector.var_type[event_index][i][1])

            # Else use the variables which are neither unique nor static # !!!
            else:
                self.discrete_indices[event_index] = [
                        var_index for var_index in range(len(self.event_type_detector.variable_key_list[event_index])) if
                        self.target_path_list == [] or
                        self.event_type_detector.variable_key_list[event_index][var_index] in self.target_path_list]
                for i in range(len(self.event_type_detector.values[event_index]) - 1, -1, -1):  # skipcq: PTC-W0060
                    tmp_list = list(set(self.event_type_detector.values[event_index][i][-self.num_init:]))
                    if len(tmp_list) == 1 or (len(tmp_list) > self.disc_div_thres * self.num_init):
                        del self.discrete_indices[event_index][i]
                    else:
                        self.pos_var_val[event_index].append(tmp_list)
                self.pos_var_val[event_index].reverse()

            # Initialise the list of the possible correlations
            # If no preselection method is used all discrete variables are matched with each other
            if not self.used_presel_meth:
                self.pos_var_cor[event_index] = [[i, j] for i in range(len(self.discrete_indices[event_index])) for j in range(
                    i+1, len(self.discrete_indices[event_index]))]

            # Else the preselection methods are used to generate the list of possible correlations
            else:
                first_run = True  # Only used if the interception of the preselected possible correlations are further analysed

                # Generate the possible correlations for the preselection methods
                for meth in self.used_presel_meth:
                    tmp_pos_var_cor = []  # List of the possible correlations for one preselection method
                    if self.variable_type_detector is None:
                        variable_values = [[] for _ in range(len(self.discrete_indices[event_index]))]  # skipcq: PTC-W0060
                        variable_distributions = [[] for _ in range(len(self.discrete_indices[event_index]))]  # skipcq: PTC-W0060
                        for i, val in enumerate(self.discrete_indices[event_index]):
                            for j in range(-1, -self.num_init-1, -1):
                                if self.event_type_detector.values[event_index][val][j] not in variable_values[i]:
                                    variable_values[i].append(self.event_type_detector.values[event_index][val][j])
                                    variable_distributions[i].append(1)
                                else:
                                    variable_distributions[i][variable_values[i].index(self.event_type_detector.values[event_index][
                                        val][j])] += 1
                            tmp_sum = sum(variable_distributions[i])
                            variable_distributions[i] = [variable_distributions[i][j]/tmp_sum for j in range(
                                len(variable_distributions[i]))]

                    if meth == 'excludeDueDistr':
                        useable_indices = []  # list of the indices, which are not excluded
                        if self.variable_type_detector is not None:
                            for i, val in enumerate(self.discrete_indices[event_index]):
                                if self.pick_cor_exclude_due_distr(self.variable_type_detector.var_type[event_index][val][2]):
                                    # Add the index to the list of useable indices if it is not excluded
                                    useable_indices.append(i)
                        else:
                            for i in range(len(self.discrete_indices[event_index])):  # skipcq: PTC-W0060
                                if self.pick_cor_exclude_due_distr(variable_distributions[i]):
                                    # Add the index to the list of useable indices if it is not excluded
                                    useable_indices.append(i)
                        tmp_pos_var_cor = [[i, j] for i in useable_indices for j in useable_indices if i < j]

                    elif meth == 'matchDiscDistr':
                        if self.variable_type_detector is not None:
                            for i, val in enumerate(self.discrete_indices[event_index]):
                                for j in range(i+1, len(val)):  # skipcq: PTC-W0060
                                    if self.pick_cor_match_disc_distr(self.variable_type_detector.var_type[event_index][
                                        val][2], self.variable_type_detector.var_type[event_index][
                                            self.discrete_indices[event_index][j]][2]):
                                        # If self.pick_cor_match_disc_distr returned True the indices are being appended
                                        tmp_pos_var_cor.append([i, j])
                        else:
                            for i in range(len(self.discrete_indices[event_index])):  # skipcq: PTC-W0060
                                for j in range(i+1, len(self.discrete_indices[event_index])):  # skipcq: PTC-W0060
                                    if self.pick_cor_match_disc_distr(variable_distributions[i], variable_distributions[j]):
                                        # If self.pick_cor_match_disc_distr returned True the indices are being appended
                                        tmp_pos_var_cor.append([i, j])

                    elif meth == 'matchDiscVals':
                        if self.variable_type_detector is not None:
                            for i, val in enumerate(self.discrete_indices[event_index]):
                                for j in range(i+1, len(self.discrete_indices[event_index])):  # skipcq: PTC-W0060
                                    if self.pick_cor_match_disc_vals(self.variable_type_detector.var_type[event_index][
                                        val][1], self.variable_type_detector.var_type[event_index][
                                            self.discrete_indices[event_index][j]][1]):
                                        # If self.pick_cor_match_disc_vals returned True the indices are being appended
                                        tmp_pos_var_cor.append([i, j])
                        else:
                            for i in range(len(self.discrete_indices[event_index])):  # skipcq: PTC-W0060
                                for j in range(i+1, len(self.discrete_indices[event_index])):  # skipcq: PTC-W0060
                                    if self.pick_cor_match_disc_vals(variable_values[i], variable_values[j]):
                                        # If self.pick_cor_match_disc_vals returned True the indices are being appended
                                        tmp_pos_var_cor.append([i, j])

                    elif meth == 'random':
                        tmp_pos_var_cor = self.pick_cor_random(event_index)

                    # Initialize, append or intercept self.pos_var_cor with tmp_pos_var_cor
                    # Initialize self.pos_var_cor
                    if first_run:
                        first_run = False
                        self.pos_var_cor[event_index] = tmp_pos_var_cor
                    # Intercept self.pos_var_cor
                    elif self.intersect_presel_meth:
                        for i in range(len(self.pos_var_cor[event_index]) - 1, -1, -1):  # skipcq: PTC-W0060
                            if self.pos_var_cor[event_index][i] not in tmp_pos_var_cor:
                                del self.pos_var_cor[event_index][i]
                    # Append self.pos_var_cor
                    else:
                        for cor in tmp_pos_var_cor:
                            if cor not in self.pos_var_cor[event_index]:
                                self.pos_var_cor[event_index].append(cor)

        # Initialise the correlation methods
        for meth in self.used_cor_meth:
            if meth == 'Rel':
                self.init_cor_rel(event_index)
            elif meth == 'WRel':
                self.init_cor_w_rel(event_index)

    def init_cor_rel(self, event_index):
        """Initialize supporting lists for the method 'Rel'."""
        # Initialise self.rel_list
        if len(self.rel_list) < event_index+1:
            for i in range(event_index + 1 - len(self.rel_list)):
                self.rel_list.append([])
        if len(self.rel_list[event_index]) == 0:
            for i in range(len(self.pos_var_cor[event_index])):  # skipcq: PTC-W0060
                self.rel_list[event_index].append([{}, {}])

        # Only calculate the correlations once, because the used method allows to efficiently calculate both directions in parallel
        for pos_var_cor_index, pos_var_cor_val in enumerate(self.pos_var_cor[event_index]):
            i = pos_var_cor_val[0]  # Index of the first variable in discrete_indices
            j = pos_var_cor_val[1]  # Index of the second variable in discrete_indices

            for k in range(-1, -self.num_init-1, -1):
                # k-th value of the i-th variable
                i_val = self.event_type_detector.values[event_index][self.discrete_indices[event_index][i]][k]
                # k-th value of the j-th variable
                j_val = self.event_type_detector.values[event_index][self.discrete_indices[event_index][j]][k]

                # Check if i_val has not appeared previously
                if i_val not in self.rel_list[event_index][pos_var_cor_index][0]:
                    # Add the relation i=i_val -> j=j_val
                    self.rel_list[event_index][pos_var_cor_index][0][i_val] = {j_val: 1}

                    # If the j_val has already appeared, then the var i had another value than i_val,
                    # therefore the relation j:j_val -> i:i_val is not possible
                    if j_val in self.rel_list[event_index][pos_var_cor_index][1]:
                        del self.rel_list[event_index][pos_var_cor_index][1][j_val]
                    # Else add the relation j=j_val -> i=i_val
                    else:
                        self.rel_list[event_index][pos_var_cor_index][1][j_val] = {i_val: 1}
                    continue

                # Check if j_val has not appeared previously
                if j_val not in self.rel_list[event_index][pos_var_cor_index][1]:
                    # Add the relation j=j_val -> i=i_val
                    self.rel_list[event_index][pos_var_cor_index][1][j_val] = {i_val: 1}
                    # i=i_val -> j=j_val is not possible
                    del self.rel_list[event_index][pos_var_cor_index][0][i_val]
                    continue

                # At least two possible values, therefore delete the relation
                if self.rel_list[event_index][pos_var_cor_index][0][i_val] != {} and j_val not in self.rel_list[event_index][
                        pos_var_cor_index][0][i_val]:
                    del self.rel_list[event_index][pos_var_cor_index][0][i_val]

                # At least two possible values, therefore delete the relation
                if self.rel_list[event_index][pos_var_cor_index][1][j_val] != {} and i_val not in self.rel_list[event_index][
                        pos_var_cor_index][1][j_val]:
                    del self.rel_list[event_index][pos_var_cor_index][1][j_val]

                # Update the appearance of the relation
                if (i_val in self.rel_list[event_index][pos_var_cor_index][0]) and (j_val in self.rel_list[event_index][
                        pos_var_cor_index][0][i_val]):
                    self.rel_list[event_index][pos_var_cor_index][0][i_val][j_val] += 1
                if (j_val in self.rel_list[event_index][pos_var_cor_index][1]) and (i_val in self.rel_list[event_index][
                        pos_var_cor_index][1][j_val]):
                    self.rel_list[event_index][pos_var_cor_index][1][j_val][i_val] += 1

    def init_cor_w_rel(self, event_index):
        """Initialize w_rel_list and runs init_single_cor_w_rel for the chosen indices."""
        # Append the w_rel_list and w_rel_num_ll_to_vals if necessary
        if len(self.w_rel_list) < event_index+1:
            for _ in range(event_index + 1 - len(self.w_rel_list)):
                self.w_rel_list.append([])
                self.w_rel_num_ll_to_vals.append([])
        if len(self.w_rel_list[event_index]) == 0:
            for _ in range(len(self.pos_var_cor[event_index])):  # skipcq: PTC-W0060
                self.w_rel_list[event_index].append([{}, {}])
                self.w_rel_num_ll_to_vals[event_index].append([{}, {}])

        # Only initialize the correlations once, because the used method allows to efficiently calculate both directions in parallel
        for pos_var_cor_index in range(len(self.pos_var_cor[event_index])):  # skipcq: PTC-W0060
            self.init_single_cor_w_rel(event_index, pos_var_cor_index)

    def init_single_cor_w_rel(self, event_index, pos_var_cor_index):
        """Initialize the first entries of w_rel_list."""
        i = self.pos_var_cor[event_index][pos_var_cor_index][0]  # Index of the first variable in discrete_indices
        j = self.pos_var_cor[event_index][pos_var_cor_index][1]  # Index of the second variable in discrete_indices
        for k in range(-1, -self.num_init-1, -1):
            # k-th value of the i-th variable
            i_val = self.event_type_detector.values[event_index][self.discrete_indices[event_index][i]][k]
            # k-th value of the j-th variable
            j_val = self.event_type_detector.values[event_index][self.discrete_indices[event_index][j]][k]

            # Updating both lists in w_rel_list[event_index][pos_var_cor_index] and w_rel_num_ll_to_vals[event_index][pos_var_cor_index]
            # Add an entry for i_val if necessary
            if i_val not in self.w_rel_list[event_index][pos_var_cor_index][0]:
                self.w_rel_list[event_index][pos_var_cor_index][0][i_val] = {}
                self.w_rel_num_ll_to_vals[event_index][pos_var_cor_index][0][i_val] = 1
            else:
                self.w_rel_num_ll_to_vals[event_index][pos_var_cor_index][0][i_val] += 1

            # Add an entry for j_val if necessary
            if j_val not in self.w_rel_list[event_index][pos_var_cor_index][1]:
                self.w_rel_list[event_index][pos_var_cor_index][1][j_val] = {}
                self.w_rel_num_ll_to_vals[event_index][pos_var_cor_index][1][j_val] = 1
            else:
                self.w_rel_num_ll_to_vals[event_index][pos_var_cor_index][1][j_val] += 1

            # Add the entries for j_val
            if j_val not in self.w_rel_list[event_index][pos_var_cor_index][0][i_val]:
                self.w_rel_list[event_index][pos_var_cor_index][0][i_val][j_val] = 1
            # Or update the appearance of the relation
            else:
                self.w_rel_list[event_index][pos_var_cor_index][0][i_val][j_val] += 1

            # Add the entries for i_val
            if i_val not in self.w_rel_list[event_index][pos_var_cor_index][1][j_val]:
                self.w_rel_list[event_index][pos_var_cor_index][1][j_val][i_val] = 1
            # Or update the appearance of the relation
            else:
                self.w_rel_list[event_index][pos_var_cor_index][1][j_val][i_val] += 1

        # Removes the entries of w_rel_list[event_index][pos_var_cor_index] which can not be considered possible correlations
        # Generate the list of entries in i, which should be deleted
        delete_i_vals = [i_val for i_val in self.w_rel_list[event_index][pos_var_cor_index][0] if not(
            self.check_cor_w_rel(self.w_rel_list[event_index][pos_var_cor_index][0][i_val].values(), len(
                self.pos_var_val[event_index][j])))]

        # Delete entries of i
        for i_val in delete_i_vals:
            del self.w_rel_list[event_index][pos_var_cor_index][0][i_val]
            del self.w_rel_num_ll_to_vals[event_index][pos_var_cor_index][0][i_val]

        # Generate the list of entries in j, which should be deleted
        delete_j_vals = [j_val for j_val in self.w_rel_list[event_index][pos_var_cor_index][1] if not(
            self.check_cor_w_rel(self.w_rel_list[event_index][pos_var_cor_index][1][j_val].values(), len(
                self.pos_var_val[event_index][i])))]

        # Delete entries of j
        for j_val in delete_j_vals:
            del self.w_rel_list[event_index][pos_var_cor_index][1][j_val]
            del self.w_rel_num_ll_to_vals[event_index][pos_var_cor_index][1][j_val]

    def update_or_test_cor(self, event_index):
        """Update or test the possible correlations and removes the false ones."""
        for meth in self.used_cor_meth:
            if meth == 'Rel':
                self.update_or_test_cor_rel(event_index)
            elif meth == 'WRel':
                self.update_or_test_cor_w_rel(event_index)

    def update_or_test_cor_rel(self, event_index):
        """Update or test the rel_list."""
        for pos_var_cor_index, pos_var_cor_val in enumerate(self.pos_var_cor[event_index]):
            i = pos_var_cor_val[0]  # Index of the first variable in discrete_indices
            j = pos_var_cor_val[1]  # Index of the second variable in discrete_indices

            if self.update_rules[event_index] and self.learn_mode:
                # Update both list in rel_list[event_index][pos_var_cor_index] and create new rules if self.generate_rules[event_index]
                # is True
                message = f'New values appeared after the {self.event_type_detector.total_records}-th line in correlation(s) of the event' \
                          f' {self.event_type_detector.get_event_type(event_index)}'
                confidence = 0
                total_correlations = len([None for _ in self.rel_list[event_index][pos_var_cor_index][0]]) + len(
                        [None for _ in self.rel_list[event_index][pos_var_cor_index][1]])
                sorted_log_lines = []
                event_data = {'EventIndex': event_index}
                affected_log_atom_paths = []
                value_changes = []
                if self.generate_rules[event_index]:
                    failed_i_vals = []
                    failed_j_vals = []
                    new_i_vals = []
                    new_j_vals = []
                for k in range(-1, -self.num_update-1, -1):
                    # k-th value of the i-th variable
                    i_val = self.event_type_detector.values[event_index][self.discrete_indices[event_index][i]][k]
                    # k-th value of the j-th variable
                    j_val = self.event_type_detector.values[event_index][self.discrete_indices[event_index][j]][k]

                    # Check if i_val has not appeared previously and appends the message to string or save the index in failed_i_vals
                    # if the correlation was violated
                    if i_val not in self.rel_list[event_index][pos_var_cor_index][0] and self.generate_rules[event_index]:
                        # Add the relation i=i_val -> j=j_val
                        self.rel_list[event_index][pos_var_cor_index][0][i_val] = {j_val: 0}
                        new_i_vals.append(i_val)
                    elif i_val in self.rel_list[event_index][pos_var_cor_index][0] and j_val not in self.rel_list[event_index][
                            pos_var_cor_index][0][i_val]:
                        if not self.generate_rules[event_index] or i_val not in new_i_vals:
                            sorted_log_lines.append(
                                # skipcq: PYL-C0209
                                'New value occurred in correlation of the paths %s = %s -> %s = old value: %s / New appeared value: %s' % (
                                    self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][
                                        pos_var_cor_val[0]]], repr(i_val),
                                    self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][
                                        pos_var_cor_val[1]]], repr(list(self.rel_list[event_index][
                                            pos_var_cor_index][0][i_val].keys())[0]), repr(j_val)))
                            affected_log_atom_paths.append(self.event_type_detector.variable_key_list[event_index][self.discrete_indices[
                                event_index][pos_var_cor_val[0]]])
                            affected_log_atom_paths.append(self.event_type_detector.variable_key_list[event_index][self.discrete_indices[
                                event_index][pos_var_cor_val[1]]])
                            change = {'OldValue': repr(list(self.rel_list[event_index][pos_var_cor_index][0][i_val].keys())[0]),
                                      'NewValue': repr(j_val)}
                            value_changes.append(change)
                            del self.rel_list[event_index][pos_var_cor_index][0][i_val]
                            confidence += 1 / total_correlations
                        if self.generate_rules[event_index] and i_val not in failed_i_vals:
                            failed_i_vals.append(i_val)

                    # Check if j_val has not appeared previously and appends the message to string or save the index in failed_j_vals if
                    # the correlation was violated
                    if j_val not in self.rel_list[event_index][pos_var_cor_index][1] and self.generate_rules[event_index]:
                        # Add the relation j=j_val -> i=i_val
                        self.rel_list[event_index][pos_var_cor_index][1][j_val] = {i_val: 0}
                        new_j_vals.append(j_val)
                    elif j_val in self.rel_list[event_index][pos_var_cor_index][1] and i_val not in self.rel_list[event_index][
                            pos_var_cor_index][1][j_val]:
                        if not self.generate_rules[event_index] or j_val not in new_j_vals:
                            sorted_log_lines.append(
                                # skipcq: PYL-C0209
                                'New value occurred in correlation of the paths %s = %s -> %s = old value: %s / New appeared value: %s' % (
                                    self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][
                                        pos_var_cor_val[1]]], repr(j_val),
                                    self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][
                                        pos_var_cor_val[0]]], repr(list(self.rel_list[event_index][
                                            pos_var_cor_index][1][j_val].keys())[0]), repr(i_val)))
                            affected_log_atom_paths.append(self.event_type_detector.variable_key_list[event_index][self.discrete_indices[
                                event_index][pos_var_cor_val[1]]])
                            affected_log_atom_paths.append(self.event_type_detector.variable_key_list[event_index][self.discrete_indices[
                                event_index][pos_var_cor_val[0]]])
                            change = {'OldValue': repr(list(self.rel_list[event_index][pos_var_cor_index][1][j_val].keys())[0]),
                                      'NewValue': repr(i_val)}
                            value_changes.append(change)
                            del self.rel_list[event_index][pos_var_cor_index][1][j_val]
                            confidence += 1 / total_correlations
                        if self.generate_rules[event_index] and j_val not in failed_j_vals:
                            failed_j_vals.append(j_val)

                    # Update the appearance of the relations
                    if (i_val in self.rel_list[event_index][pos_var_cor_index][0]) and (j_val in self.rel_list[event_index][
                            pos_var_cor_index][0][i_val]):
                        self.rel_list[event_index][pos_var_cor_index][0][i_val][j_val] += 1
                    if (j_val in self.rel_list[event_index][pos_var_cor_index][1]) and (i_val in self.rel_list[event_index][
                            pos_var_cor_index][1][j_val]):
                        self.rel_list[event_index][pos_var_cor_index][1][j_val][i_val] += 1

                # Print the message if at least one correlation was violated
                if len(sorted_log_lines) != 0:
                    event_data['AffectedLogAtomPaths'] = list(set(affected_log_atom_paths))
                    event_data['ValueChanges'] = value_changes
                    event_data['TypeInfo'] = {'Confidence': confidence}
                    for listener in self.anomaly_event_handlers:
                        sorted_log_lines += ['']*(self.event_type_detector.total_records - len(sorted_log_lines))
                        listener.receive_event(
                            f'Analysis.{self.__class__.__name__}', message, sorted_log_lines, event_data, self.log_atom, self)

                # Delete the rules which failed during the rule generation phase
                if self.generate_rules[event_index]:
                    for i_val in failed_i_vals:
                        if i_val in self.rel_list[event_index][pos_var_cor_index][0]:
                            del self.rel_list[event_index][pos_var_cor_index][0][i_val]
                    for j_val in failed_j_vals:
                        if j_val in self.rel_list[event_index][pos_var_cor_index][1]:
                            del self.rel_list[event_index][pos_var_cor_index][1][j_val]

                if self.stop_learning_timestamp is not None and self.stop_learning_no_anomaly_time is not None:
                    self.stop_learning_timestamp = time.time() + self.stop_learning_no_anomaly_time

            else:
                # Only update the possible correlations which have been initialized and print warnings
                reported_values_ij = {}
                reported_values_ji = {}

                for k in range(-1, -self.num_update-1, -1):
                    # k-th value of the i-th variable
                    i_val = self.event_type_detector.values[event_index][self.discrete_indices[event_index][i]][k]
                    # k-th value of the j-th variable
                    j_val = self.event_type_detector.values[event_index][self.discrete_indices[event_index][j]][k]

                    # A new value appeared, therefore append the new value to the list reported_values_ij
                    if i_val in self.rel_list[event_index][pos_var_cor_index][0] and self.rel_list[event_index][pos_var_cor_index][0][
                            i_val] != {} and j_val not in self.rel_list[event_index][pos_var_cor_index][0][i_val]:
                        if i_val not in reported_values_ij:
                            reported_values_ij[i_val] = {j_val: 1}
                        elif j_val in reported_values_ij[i_val]:
                            reported_values_ij[i_val][j_val] += 1
                        else:
                            reported_values_ij[i_val][j_val] = 1

                    # A new value appeared, therefore append the new value to the list reported_values_ji
                    if j_val in self.rel_list[event_index][pos_var_cor_index][1] and self.rel_list[event_index][pos_var_cor_index][1][
                            j_val] != {} and i_val not in self.rel_list[event_index][pos_var_cor_index][1][j_val]:
                        if j_val not in reported_values_ji:
                            reported_values_ji[j_val] = {i_val: 1}
                        elif i_val in reported_values_ji[j_val]:
                            reported_values_ji[j_val][i_val] += 1
                        else:
                            reported_values_ji[j_val][i_val] = 1

                # Print the message of the reported values
                for i_val in reported_values_ij:
                    # skipcq: PYL-C0209
                    message = 'Correlation of the paths %s = %s -> %s = %s would be rejected after the %s-th line' % (
                        self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][
                            pos_var_cor_val[0]]], repr(i_val),
                        self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][pos_var_cor_val[
                            1]]], list(self.rel_list[event_index][pos_var_cor_index][0][i_val].keys())[
                            0], self.event_type_detector.total_records)
                    confidence = (sum(reported_values_ij[i_val][j_val] for j_val in reported_values_ij[i_val]) / (
                            sum(reported_values_ij[i_val][j_val] for j_val in reported_values_ij[i_val]) + 1)) * (
                            len(reported_values_ij[i_val]) / (len(reported_values_ij[i_val]) + 1))
                    sorted_log_lines = []
                    event_data = {'EventIndex': event_index}
                    affected_log_atom_paths = []
                    affected_values = []
                    affected_log_atom_paths.append(self.event_type_detector.variable_key_list[event_index][self.discrete_indices[
                        event_index][pos_var_cor_val[0]]])
                    affected_log_atom_paths.append(self.event_type_detector.variable_key_list[event_index][self.discrete_indices[
                        event_index][pos_var_cor_val[1]]])
                    affected_values.append(repr(i_val))
                    affected_values.append(list(self.rel_list[event_index][pos_var_cor_index][0][i_val].keys())[0])
                    event_data['AffectedLogAtomPaths'] = list(set(affected_log_atom_paths))
                    event_data['AffectedValues'] = affected_values
                    event_data['TypeInfo'] = {'Confidence': confidence}
                    sorted_log_lines += [''] * (self.event_type_detector.total_records - len(sorted_log_lines))
                    for listener in self.anomaly_event_handlers:
                        listener.receive_event(
                            f'Analysis.{self.__class__.__name__}', message, sorted_log_lines, event_data, self.log_atom, self)

                # Print the message of the reported values
                for j_val in reported_values_ji:
                    # skipcq: PYL-C0209
                    message = 'Correlation of the paths %s = %s -> %s = %s would be rejected after the %s-th line' % (
                        self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][
                            pos_var_cor_val[1]]], repr(j_val),
                        self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][self.pos_var_cor[
                            event_index][pos_var_cor_index][0]]], list(self.rel_list[event_index][pos_var_cor_index][1][
                                j_val].keys())[0], self.event_type_detector.total_records)
                    confidence = (sum(reported_values_ji[j_val][i_val] for i_val in reported_values_ji[j_val]) / (
                            sum(reported_values_ji[j_val][i_val] for i_val in reported_values_ji[j_val]) + 1)) * (
                            len(reported_values_ji[j_val]) / (len(reported_values_ji[j_val]) + 1))
                    sorted_log_lines = []
                    event_data = {'EventIndex': event_index}
                    affected_log_atom_paths = []
                    affected_values = []
                    affected_log_atom_paths.append(self.event_type_detector.variable_key_list[event_index][self.discrete_indices[
                        event_index][pos_var_cor_val[1]]])
                    affected_log_atom_paths.append(self.event_type_detector.variable_key_list[event_index][self.discrete_indices[
                        event_index][pos_var_cor_val[0]]])
                    affected_values.append(repr(j_val))
                    affected_values.append(list(self.rel_list[event_index][pos_var_cor_index][1][j_val].keys())[0])
                    event_data['AffectedLogAtomPaths'] = list(set(affected_log_atom_paths))
                    event_data['AffectedValues'] = affected_values
                    event_data['TypeInfo'] = {'Confidence': confidence}
                    sorted_log_lines += [''] * (self.event_type_detector.total_records - len(sorted_log_lines))
                    for listener in self.anomaly_event_handlers:
                        listener.receive_event(
                            f'Analysis.{self.__class__.__name__}', message, sorted_log_lines, event_data, self.log_atom, self)

    def update_or_test_cor_w_rel(self, event_index):
        """Update or test the w_rel_list."""
        # Initialise the lists for the BT results if necessary
        if len(self.w_rel_ht_results) < event_index + 1 or self.w_rel_ht_results[event_index] == []:
            self.w_rel_ht_results += [[] for i in range(event_index + 1 - len(self.w_rel_ht_results))]
            self.w_rel_ht_results[event_index] = [
                [{i_val: [1] * self.num_bt for i_val in self.w_rel_list[event_index][pos_var_cor_index][0]}, {
                    j_val: [1]*self.num_bt for j_val in self.w_rel_list[event_index][pos_var_cor_index][1]}] for pos_var_cor_index in range(
                    len(self.pos_var_cor[event_index]))]
            self.w_rel_confidences += [[] for i in range(event_index + 1 - len(self.w_rel_confidences))]
            self.w_rel_confidences[event_index] = [
                [{i_val: [] for i_val in self.w_rel_list[event_index][pos_var_cor_index][0]}, {
                    j_val: [] for j_val in self.w_rel_list[event_index][pos_var_cor_index][1]}] for pos_var_cor_index in range(
                    len(self.pos_var_cor[event_index]))]

        # Initialises the appearance list, as a copy of the w_rel_list with 0 instead of the CountIndices
        current_appearance_list = [
            [{i_val: {j_val: 0 for j_val in self.w_rel_list[event_index][pos_var_cor_index][0][i_val]} for i_val in self.w_rel_list[
                event_index][pos_var_cor_index][0]}, {j_val: {i_val: 0 for i_val in self.w_rel_list[event_index][pos_var_cor_index][1][
                    j_val]} for j_val in self.w_rel_list[event_index][pos_var_cor_index][1]}] for pos_var_cor_index in range(
                len(self.pos_var_cor[event_index]))]

        # Counting the appearance of the cases in current_appearance_list
        for k in range(-1, -self.num_update-1, -1):
            # List of the values of discrete variables, in one log line
            vals = [self.event_type_detector.values[event_index][self.discrete_indices[event_index][i]][k] for i in range(
                len(self.discrete_indices[event_index]))]
            for pos_var_cor_index, pos_var_cor_val in enumerate(self.pos_var_cor[event_index]):
                # Count the appearances if the list is not empty or if new rules should be generated
                if current_appearance_list[pos_var_cor_index] != [{}, {}] or self.generate_rules[event_index]:

                    i = pos_var_cor_val[0]  # Index of the first variable in discrete_indices
                    j = pos_var_cor_val[1]  # Index of the second variable in discrete_indices

                    # Add the appearance of the line to the appearance list and adds new entries if self.generate_rules[event_index]
                    # is set to True.
                    if vals[i] in current_appearance_list[pos_var_cor_index][0]:
                        if vals[j] in current_appearance_list[pos_var_cor_index][0][vals[i]]:
                            current_appearance_list[pos_var_cor_index][0][vals[i]][vals[j]] += 1
                        else:
                            current_appearance_list[pos_var_cor_index][0][vals[i]][vals[j]] = 1
                    elif self.generate_rules[event_index]:
                        current_appearance_list[pos_var_cor_index][0][vals[i]] = {vals[j]: 1}

                    if vals[j] in current_appearance_list[pos_var_cor_index][1]:
                        if vals[i] in current_appearance_list[pos_var_cor_index][1][vals[j]]:
                            current_appearance_list[pos_var_cor_index][1][vals[j]][vals[i]] += 1
                        else:
                            current_appearance_list[pos_var_cor_index][1][vals[j]][vals[i]] = 1
                    elif self.generate_rules[event_index]:
                        current_appearance_list[pos_var_cor_index][1][vals[j]] = {vals[i]: 1}

        if self.generate_rules[event_index]:
            # generates new rules or appends new values to existing rules
            for pos_var_cor_index in range(len(self.pos_var_cor[event_index])):  # skipcq: PTC-W0060
                # Only consider the possible correlations which have been initialized
                if current_appearance_list[pos_var_cor_index] != [{}, {}]:
                    # Check correlations i=i_val -> j=j_val and decide if the rules should be deleted, extended or updated,
                    # or if new rules should be generated
                    for i_val in current_appearance_list[pos_var_cor_index][0]:
                        if i_val in self.w_rel_list[event_index][pos_var_cor_index][0]:
                            # Check if new values have appeared, append them and reinitialize the lists
                            tmp_bool = False
                            for j_val in current_appearance_list[pos_var_cor_index][0][i_val]:
                                if j_val not in self.w_rel_list[event_index][pos_var_cor_index][0][i_val]:
                                    tmp_bool = True
                                    break

                            # New values have appeared on the right side
                            if tmp_bool:
                                if self.check_cor_w_rel(current_appearance_list[pos_var_cor_index][0][i_val].values(), len(self.pos_var_val[
                                        event_index][j])):

                                    # Add new rules
                                    self.w_rel_list[event_index][pos_var_cor_index][0][i_val] = {}
                                    self.w_rel_num_ll_to_vals[event_index][pos_var_cor_index][0][i_val] = sum(current_appearance_list[
                                        pos_var_cor_index][0][i_val].values())

                                    # Add the entries for j_val
                                    for j_val in current_appearance_list[pos_var_cor_index][0][i_val]:
                                        self.w_rel_list[event_index][pos_var_cor_index][0][i_val][j_val] = current_appearance_list[
                                            pos_var_cor_index][0][i_val][j_val]
                                else:
                                    self.w_rel_ht_results[event_index][pos_var_cor_index][0][i_val] = self.w_rel_ht_results[event_index][
                                        pos_var_cor_index][0][i_val][1:] + [0]
                                    self.w_rel_confidences[event_index][pos_var_cor_index][0][i_val].append(
                                            0.5 + 1 / len(current_appearance_list[pos_var_cor_index][0][i_val]))
                                    self.w_rel_confidences[event_index][pos_var_cor_index][0][i_val] = self.w_rel_confidences[
                                            event_index][pos_var_cor_index][0][i_val][-(self.num_bt-self.min_successes_bt+1):]
                                    if sum(self.w_rel_ht_results[event_index][pos_var_cor_index][0][i_val]) < self.min_successes_bt:  # BT
                                        self.print_failed_wrel_update(event_index, pos_var_cor_index, 0, i_val)
                                        del self.w_rel_list[event_index][pos_var_cor_index][0][i_val]
                                        del self.w_rel_ht_results[event_index][pos_var_cor_index][0][i_val]

                            # No new values have appeared on the right side. Update the appearance of the relation
                            else:
                                # Check correlations i=i_val -> j=j_val
                                # States True after the following steps if all tests were positive, and False if at least one was negative
                                tmp_bool = True
                                if any(current_appearance_list[pos_var_cor_index][0][i_val][j_val] for j_val in current_appearance_list[
                                        pos_var_cor_index][0][i_val]):
                                    tmp_bool = self.homogeneity_test(self.w_rel_list[event_index][pos_var_cor_index][0][i_val],
                                                                     current_appearance_list[pos_var_cor_index][0][i_val], event_index,
                                                                     pos_var_cor_index, 0, i_val)

                                # Update the bt_results list
                                if tmp_bool:
                                    self.w_rel_ht_results[event_index][pos_var_cor_index][0][i_val] = self.w_rel_ht_results[event_index][
                                        pos_var_cor_index][0][i_val][1:] + [1]
                                    for j_val in self.w_rel_list[event_index][pos_var_cor_index][0][i_val]:
                                        self.w_rel_list[event_index][pos_var_cor_index][0][i_val][j_val] += current_appearance_list[
                                            pos_var_cor_index][0][i_val][j_val]
                                else:
                                    self.w_rel_ht_results[event_index][pos_var_cor_index][0][i_val] = self.w_rel_ht_results[event_index][
                                        pos_var_cor_index][0][i_val][1:] + [0]
                                    if sum(self.w_rel_ht_results[event_index][pos_var_cor_index][0][i_val]) < self.min_successes_bt:  # BT
                                        self.print_failed_wrel_update(event_index, pos_var_cor_index, 0, i_val)
                                        del self.w_rel_list[event_index][pos_var_cor_index][0][i_val]
                                        del self.w_rel_ht_results[event_index][pos_var_cor_index][0][i_val]

                        # i_val not in self.w_rel_list[event_index][pos_var_cor_index][0]. Therefore, test if the rule should be used
                        else:
                            if self.check_cor_w_rel(current_appearance_list[pos_var_cor_index][0][i_val].values(), len(self.pos_var_val[
                                    event_index][j])):
                                self.w_rel_list[event_index][pos_var_cor_index][0][i_val] = {}
                                self.w_rel_num_ll_to_vals[event_index][pos_var_cor_index][0][i_val] = sum(current_appearance_list[
                                    pos_var_cor_index][0][i_val].values())
                                self.w_rel_ht_results[event_index][pos_var_cor_index][0][i_val] = [1] * self.num_bt
                                self.w_rel_confidences[event_index][pos_var_cor_index][0][i_val] = []

                                # Add the entries for j_val
                                for j_val in current_appearance_list[pos_var_cor_index][0][i_val]:
                                    self.w_rel_list[event_index][pos_var_cor_index][0][i_val][j_val] = current_appearance_list[
                                        pos_var_cor_index][0][i_val][j_val]

                    # Check correlations j=j_val -> i=i_val and decide if the rules should be deleted, extended or updated,
                    # or if new rules should be generated.
                    for j_val in current_appearance_list[pos_var_cor_index][1]:
                        if j_val in self.w_rel_list[event_index][pos_var_cor_index][1]:
                            # Check if new values have appeared, append them and reinitialize the lists
                            tmp_bool = False
                            for i_val in current_appearance_list[pos_var_cor_index][1][j_val]:
                                if i_val not in self.w_rel_list[event_index][pos_var_cor_index][1][j_val]:
                                    tmp_bool = True
                                    break

                            # New values have appeared on the right side
                            if tmp_bool:
                                if self.check_cor_w_rel(current_appearance_list[pos_var_cor_index][1][j_val].values(), len(self.pos_var_val[
                                        event_index][i])):

                                    # Add new rules
                                    self.w_rel_list[event_index][pos_var_cor_index][1][j_val] = {}
                                    self.w_rel_num_ll_to_vals[event_index][pos_var_cor_index][1][j_val] = sum(current_appearance_list[
                                        pos_var_cor_index][1][j_val].values())

                                    # Add the entries for i_val
                                    for i_val in current_appearance_list[pos_var_cor_index][1][j_val]:
                                        self.w_rel_list[event_index][pos_var_cor_index][1][j_val][i_val] = current_appearance_list[
                                            pos_var_cor_index][1][j_val][i_val]
                                else:
                                    self.w_rel_ht_results[event_index][pos_var_cor_index][1][j_val] = self.w_rel_ht_results[event_index][
                                        pos_var_cor_index][1][j_val][1:] + [0]
                                    self.w_rel_confidences[event_index][pos_var_cor_index][1][j_val].append(
                                            0.5 + 1 / len(current_appearance_list[pos_var_cor_index][1][j_val]))
                                    self.w_rel_confidences[event_index][pos_var_cor_index][0][i_val] = self.w_rel_confidences[
                                            event_index][pos_var_cor_index][0][i_val][-(self.num_bt-self.min_successes_bt+1):]
                                    if sum(self.w_rel_ht_results[event_index][pos_var_cor_index][1][j_val]) < self.min_successes_bt:  # BT
                                        self.print_failed_wrel_update(event_index, pos_var_cor_index, 1, j_val)
                                        del self.w_rel_list[event_index][pos_var_cor_index][1][j_val]
                                        del self.w_rel_ht_results[event_index][pos_var_cor_index][1][j_val]

                            # No new values have appeared on the right side. Update the appearance of the relation
                            else:
                                # Check correlations i=i_val -> j=j_val
                                # States True after the following steps if all tests were positive, and False if at least one was negative
                                tmp_bool = True
                                if any(current_appearance_list[pos_var_cor_index][1][j_val][i_val] for i_val in current_appearance_list[
                                        pos_var_cor_index][1][j_val]):
                                    tmp_bool = self.homogeneity_test(self.w_rel_list[event_index][pos_var_cor_index][1][j_val],
                                                                     current_appearance_list[pos_var_cor_index][1][j_val], event_index,
                                                                     pos_var_cor_index, 1, j_val)

                                # Update the bt_results list
                                if tmp_bool:
                                    self.w_rel_ht_results[event_index][pos_var_cor_index][1][j_val] = self.w_rel_ht_results[event_index][
                                        pos_var_cor_index][1][j_val][1:] + [1]
                                    for i_val in self.w_rel_list[event_index][pos_var_cor_index][1][j_val]:
                                        self.w_rel_list[event_index][pos_var_cor_index][1][j_val][i_val] += current_appearance_list[
                                            pos_var_cor_index][1][j_val][i_val]
                                else:
                                    self.w_rel_ht_results[event_index][pos_var_cor_index][1][j_val] = self.w_rel_ht_results[event_index][
                                        pos_var_cor_index][1][j_val][1:] + [0]
                                    if sum(self.w_rel_ht_results[event_index][pos_var_cor_index][1][j_val]) < self.min_successes_bt:  # BT
                                        self.print_failed_wrel_update(event_index, pos_var_cor_index, 1, j_val)
                                        del self.w_rel_list[event_index][pos_var_cor_index][1][j_val]
                                        del self.w_rel_ht_results[event_index][pos_var_cor_index][1][j_val]

                        # j_val not in self.w_rel_list[event_index][pos_var_cor_index][1]. Therefore, test if the rule should be used
                        else:
                            if self.check_cor_w_rel(current_appearance_list[pos_var_cor_index][1][j_val].values(), len(self.pos_var_val[
                                    event_index][i])):
                                self.w_rel_list[event_index][pos_var_cor_index][1][j_val] = {}
                                self.w_rel_num_ll_to_vals[event_index][pos_var_cor_index][1][j_val] = sum(current_appearance_list[
                                    pos_var_cor_index][1][j_val].values())
                                self.w_rel_ht_results[event_index][pos_var_cor_index][1][j_val] = [1] * self.num_bt
                                self.w_rel_confidences[event_index][pos_var_cor_index][1][j_val] = []

                                # Add the entries for i_val
                                for i_val in current_appearance_list[pos_var_cor_index][1][j_val]:
                                    self.w_rel_list[event_index][pos_var_cor_index][1][j_val][i_val] = current_appearance_list[
                                        pos_var_cor_index][1][j_val][i_val]

        else:
            # Tests and updates the correlation rules
            for pos_var_cor_index, pos_var_cor_val in enumerate(self.pos_var_cor[event_index]):
                # Only consider the possible correlations which have been initialized
                if self.w_rel_list[event_index][pos_var_cor_index] != [{}, {}]:
                    # Initialise the lists for the indices that failed the binomial test
                    failed_i_vals = []
                    failed_j_vals = []

                    # Check correlations i=i_val -> j=j_val
                    for i_val in self.w_rel_list[event_index][pos_var_cor_index][0]:
                        # States True after the following steps if all tests were positive, and False if at least one was negative.
                        tmp_bool = True
                        if sum([current_appearance_list[pos_var_cor_index][0][i_val][j_val] for j_val in current_appearance_list[
                                pos_var_cor_index][0][i_val]]) > self.min_values_cors_thres:
                            tmp_bool = self.homogeneity_test(self.w_rel_list[event_index][pos_var_cor_index][0][i_val],
                                                             current_appearance_list[pos_var_cor_index][0][i_val], event_index,
                                                             pos_var_cor_index, 0, i_val)

                        # Update the bt_results list
                        if tmp_bool:
                            self.w_rel_ht_results[event_index][pos_var_cor_index][0][i_val] = self.w_rel_ht_results[event_index][
                                pos_var_cor_index][0][i_val][1:] + [1]
                        else:
                            self.w_rel_ht_results[event_index][pos_var_cor_index][0][i_val] = self.w_rel_ht_results[event_index][
                                pos_var_cor_index][0][i_val][1:] + [0]
                            failed_i_vals.append(i_val)

                    # Check correlations j=j_val -> i=i_val
                    for j_val in self.w_rel_list[event_index][pos_var_cor_index][1]:
                        # States True after the following steps if all tests were positive, and False if at least one was negative
                        tmp_bool = True
                        if sum([current_appearance_list[pos_var_cor_index][1][j_val][i_val] for i_val in current_appearance_list[
                                pos_var_cor_index][1][j_val]]) > self.min_values_cors_thres:
                            tmp_bool = self.homogeneity_test(self.w_rel_list[event_index][pos_var_cor_index][1][j_val],
                                                             current_appearance_list[pos_var_cor_index][1][j_val], event_index,
                                                             pos_var_cor_index, 1, j_val)

                        # Update the bt_results list
                        if tmp_bool:
                            self.w_rel_ht_results[event_index][pos_var_cor_index][1][j_val] = self.w_rel_ht_results[event_index][
                                pos_var_cor_index][1][j_val][1:] + [1]
                        else:
                            self.w_rel_ht_results[event_index][pos_var_cor_index][1][j_val] = self.w_rel_ht_results[event_index][
                                pos_var_cor_index][1][j_val][1:] + [0]
                            failed_j_vals.append(j_val)

                    if self.update_rules[event_index] and self.learn_mode:
                        # Print if new values have appeared in the correlation rules
                        message = f'New values appeared after the {self.event_type_detector.total_records}-th line in correlation(s) of ' \
                                  f'the event {self.event_type_detector.get_event_type(event_index)}'
                        confidence = 0
                        total_correlations = len([None for _ in self.w_rel_list[event_index][pos_var_cor_index][0]]) + len(
                                [None for _ in self.w_rel_list[event_index][pos_var_cor_index][1]])
                        sorted_log_lines = []
                        event_data = {'EventIndex': event_index}
                        affected_log_atom_paths = []
                        distribution_changes = []
                        for i_val in self.w_rel_list[event_index][pos_var_cor_index][0]:
                            if len(self.w_rel_list[event_index][pos_var_cor_index][0][i_val]) != len(current_appearance_list[
                                    pos_var_cor_index][0][i_val]):
                                if len(current_appearance_list[pos_var_cor_index][0][i_val]) / len(self.w_rel_list[event_index][
                                        pos_var_cor_index][0][i_val]) >= self.new_vals_alarm_thres:
                                    sorted_log_lines.append(
                                        # skipcq: PYL-C0209
                                        'Alarm: New value occurred in correlation of the paths %s = %s -> %s =' % (
                                                self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][
                                                    pos_var_cor_val[0]]], repr(i_val),
                                                self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][
                                                    pos_var_cor_val[1]]]))
                                else:
                                    # skipcq: PYL-C0209
                                    sorted_log_lines.append('New value occurred in correlation of the paths %s = %s -> %s =' % (
                                        self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][
                                            pos_var_cor_val[0]]], repr(i_val),
                                        self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][
                                            pos_var_cor_val[1]]]))
                                affected_log_atom_paths.append(self.event_type_detector.variable_key_list[event_index][
                                    self.discrete_indices[event_index][pos_var_cor_val[0]]])
                                affected_log_atom_paths.append(self.event_type_detector.variable_key_list[event_index][
                                    self.discrete_indices[event_index][pos_var_cor_val[1]]])
                                distribution = {
                                    'OldDistribution': [[j_val, self.w_rel_list[event_index][pos_var_cor_index][0][i_val][j_val] / sum(
                                        self.w_rel_list[event_index][pos_var_cor_index][0][i_val].values())] for j_val in
                                        self.w_rel_list[event_index][pos_var_cor_index][0][i_val].keys()],
                                    'NewDistribution': [[j_val, current_appearance_list[pos_var_cor_index][0][i_val][j_val] / sum(
                                        current_appearance_list[pos_var_cor_index][0][i_val].values())] for j_val in
                                        current_appearance_list[pos_var_cor_index][0][i_val].keys()]
                                }
                                distribution_changes.append(distribution)
                                sorted_log_lines.append(f"Old distribution: {distribution['OldDistribution']}")
                                sorted_log_lines.append(f"New distribution: {distribution['NewDistribution']}")
                                confidence += 1 / total_correlations

                                # Add the new values to the correlation rule
                                for j_val in current_appearance_list[pos_var_cor_index][0][i_val].keys():
                                    if j_val not in self.w_rel_list[event_index][pos_var_cor_index][0][i_val]:
                                        self.w_rel_list[event_index][pos_var_cor_index][0][i_val][j_val] = 0

                        for j_val in self.w_rel_list[event_index][pos_var_cor_index][1]:
                            if len(self.w_rel_list[event_index][pos_var_cor_index][1][j_val]) != len(current_appearance_list[
                                    pos_var_cor_index][1][j_val]):
                                if len(current_appearance_list[pos_var_cor_index][1][j_val]) / len(self.w_rel_list[event_index][
                                        pos_var_cor_index][1][j_val]) >= self.new_vals_alarm_thres:
                                    # skipcq: PYL-C0209
                                    sorted_log_lines.append('Alarm: New value occurred in correlation of the paths %s = %s -> %s =' % (
                                        self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][
                                            pos_var_cor_val[1]]],  repr(j_val),
                                        self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][
                                            pos_var_cor_val[0]]]))
                                else:
                                    # skipcq: PYL-C0209
                                    sorted_log_lines.append('New value occurred in correlation of the paths %s = %s -> %s =' % (
                                        self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][
                                            pos_var_cor_val[1]]], repr(j_val),
                                        self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][
                                            pos_var_cor_val[0]]]))
                                affected_log_atom_paths.append(self.event_type_detector.variable_key_list[event_index][
                                    self.discrete_indices[event_index][pos_var_cor_val[1]]])
                                affected_log_atom_paths.append(self.event_type_detector.variable_key_list[event_index][
                                    self.discrete_indices[event_index][pos_var_cor_val[0]]])
                                distribution = {
                                    'OldDistribution': [[i_val, self.w_rel_list[event_index][pos_var_cor_index][1][j_val][i_val] / sum(
                                        self.w_rel_list[event_index][pos_var_cor_index][1][j_val].values())] for i_val in
                                        self.w_rel_list[event_index][pos_var_cor_index][1][j_val].keys()],
                                    'NewDistribution': [[i_val, current_appearance_list[pos_var_cor_index][1][j_val][i_val] / sum(
                                        current_appearance_list[pos_var_cor_index][1][j_val].values())] for i_val in
                                        current_appearance_list[pos_var_cor_index][1][j_val].keys()]
                                }
                                distribution_changes.append(distribution)
                                sorted_log_lines.append(f"Old distribution: {distribution['OldDistribution']}")
                                sorted_log_lines.append(f"New distribution: {distribution['NewDistribution']}")
                                confidence += 1 / total_correlations

                                # Add the new values to the correlation rule
                                for i_val in current_appearance_list[pos_var_cor_index][1][j_val].keys():
                                    if i_val not in self.w_rel_list[event_index][pos_var_cor_index][1][j_val]:
                                        self.w_rel_list[event_index][pos_var_cor_index][1][j_val][i_val] = 0

                        if len(sorted_log_lines) != 0:
                            event_data['AffectedLogAtomPaths'] = list(set(affected_log_atom_paths))
                            event_data['DistributionChanges'] = distribution_changes
                            event_data['TypeInfo'] = {'Confidence': confidence}
                            sorted_log_lines += [''] * (self.event_type_detector.total_records - len(sorted_log_lines))
                            for listener in self.anomaly_event_handlers:
                                listener.receive_event(
                                    f'Analysis.{self.__class__.__name__}', message, sorted_log_lines, event_data, self.log_atom, self)

                        # Remove the failed rules if it is an update step
                        # Binomial test and delete rules of the form i=i_val -> j=j_val
                        for i_val in failed_i_vals:
                            if sum(self.w_rel_ht_results[event_index][pos_var_cor_index][0][i_val]) < self.min_successes_bt:  # BT
                                self.print_failed_wrel_update(event_index, pos_var_cor_index, 0, i_val)
                                del self.w_rel_list[event_index][pos_var_cor_index][0][i_val]
                                del self.w_rel_ht_results[event_index][pos_var_cor_index][0][i_val]

                        # Binomial test and delete rules of the form j=j_val -> i=i_val
                        for j_val in failed_j_vals:
                            if sum(self.w_rel_ht_results[event_index][pos_var_cor_index][1][j_val]) < self.min_successes_bt:  # BT
                                self.print_failed_wrel_update(event_index, pos_var_cor_index, 1, j_val)
                                del self.w_rel_list[event_index][pos_var_cor_index][1][j_val]
                                del self.w_rel_ht_results[event_index][pos_var_cor_index][1][j_val]

                        # Update the distributions of the correlation rules, which succeeded the test above
                        # Update i=i_val -> j=j_val
                        for i_val in self.w_rel_list[event_index][pos_var_cor_index][0]:
                            if self.w_rel_ht_results[event_index][pos_var_cor_index][0][i_val][-1]:
                                for j_val in self.w_rel_list[event_index][pos_var_cor_index][0][i_val]:
                                    self.w_rel_list[event_index][pos_var_cor_index][0][i_val][j_val] += current_appearance_list[
                                        pos_var_cor_index][0][i_val][j_val]

                        # Update j=j_val -> i=i_val
                        for j_val in self.w_rel_list[event_index][pos_var_cor_index][1]:
                            if self.w_rel_ht_results[event_index][pos_var_cor_index][1][j_val][-1]:
                                for i_val in self.w_rel_list[event_index][pos_var_cor_index][1][j_val]:
                                    self.w_rel_list[event_index][pos_var_cor_index][1][j_val][i_val] += current_appearance_list[
                                        pos_var_cor_index][1][j_val][i_val]

                        if self.stop_learning_timestamp is not None and self.stop_learning_no_anomaly_time is not None:
                            self.stop_learning_timestamp = time.time() + self.stop_learning_no_anomaly_time

                    else:
                        # Print the rules, which failed the binomial test
                        for i_val in failed_i_vals:
                            if sum(self.w_rel_ht_results[event_index][pos_var_cor_index][0][i_val]) < self.min_successes_bt:  # BT
                                self.print_failed_wrel_test(event_index, pos_var_cor_index, 0, i_val)
                                self.w_rel_ht_results[event_index][pos_var_cor_index][0][i_val] = [1] * self.num_bt
                                self.w_rel_confidences[event_index][pos_var_cor_index][0][i_val] = []

                        for j_val in failed_j_vals:
                            if sum(self.w_rel_ht_results[event_index][pos_var_cor_index][1][j_val]) < self.min_successes_bt:  # BT
                                self.print_failed_wrel_test(event_index, pos_var_cor_index, 1, j_val)
                                self.w_rel_ht_results[event_index][pos_var_cor_index][1][j_val] = [1] * self.num_bt
                                self.w_rel_confidences[event_index][pos_var_cor_index][1][j_val] = []

    # skipcq: PYL-R0201
    def homogeneity_test(self, occurrences1, occurrences2, event_index, pos_var_cor_index, cor_direction, value1):
        """Make a two sample test of homogeneity of the given occurrences."""
        if self.used_homogeneity_test == 'Chi':
            test_result = 0
            for val in occurrences1:
                if occurrences1[val] > 0:
                    observed1 = occurrences1[val]
                    expected1 = sum(occurrences1.values()) * (occurrences1[val]+occurrences2[val]) / \
                        (sum(occurrences1.values()) + sum(occurrences2.values()))
                    test_result += (observed1 - expected1) * (observed1 - expected1) / expected1

                    observed2 = occurrences2[val]
                    expected2 = sum(occurrences2.values()) * (occurrences1[val]+occurrences2[val]) / \
                        (sum(occurrences1.values()) + sum(occurrences2.values()))
                    test_result += (observed2 - expected2) * (observed2 - expected2) / expected2

            quantile = chi2.ppf(1-self.alpha_chisquare_test, (len(occurrences1)-1))
            if test_result >= quantile:
                self.w_rel_confidences[event_index][pos_var_cor_index][cor_direction][value1].append(test_result)
                self.w_rel_confidences[event_index][pos_var_cor_index][cor_direction][value1] = self.w_rel_confidences[
                        event_index][pos_var_cor_index][cor_direction][value1][-(self.num_bt-self.min_successes_bt+1):]
                return False
        elif self.used_homogeneity_test == 'MaxDist':
            for val in occurrences1:
                if abs(occurrences1[val] / sum(occurrences1.values()) -
                        occurrences2[val] / max(1, sum(occurrences2.values()))) > self.max_dist_rule_distr:
                    self.w_rel_confidences[event_index][pos_var_cor_index][cor_direction][value1].append(abs(
                            occurrences1[val] / sum(occurrences1.values()) - occurrences2[val] / max(
                                1, sum(occurrences2.values()))))
                    self.w_rel_confidences[event_index][pos_var_cor_index][cor_direction][value1] = self.w_rel_confidences[
                            event_index][pos_var_cor_index][cor_direction][value1][-(self.num_bt-self.min_successes_bt+1):]
                    return False
        return True

    # skipcq: PYL-R0201
    def pick_cor_match_disc_distr(self, prob_list1, prob_list2):
        """Check if the the two discrete distribution could have a possible correlation."""
        list1 = prob_list1.copy()
        list2 = prob_list2.copy()
        list1.sort(reverse=True)
        list2.sort(reverse=True)

        for i in range(min(len(list1), len(list2))):
            if abs(list1[i]-list2[i]) > self.match_disc_distr_threshold/max(len(list1), len(list2)):
                return False
        return True

    # skipcq: PYL-R0201
    def pick_cor_exclude_due_distr(self, prob_list):
        """
        Check if the the discrete distribution can be expected to have possible correlation.
        Returns True for possible correlation and False to be excluded.
        """
        # Assigning epsilon
        epsilon = self.exclude_due_distr_lower_limit + (1 - self.exclude_due_distr_lower_limit) / len(prob_list)
        # Check the single probabilities
        for _, val in enumerate(prob_list):
            if val > epsilon:
                return False
        return True

    # skipcq: PYL-R0201
    def pick_cor_match_disc_vals(self, val_list1, val_list2):
        """Check through the values of the two discrete distributions if they could have a possible correlation."""
        if len([val for val in val_list1 if val in val_list2]) > self.match_disc_vals_sim_tresh*min(
                len(val_list1), len(val_list2)):
            return True
        return False

    def pick_cor_random(self, event_index):
        """Match variables randomly to correlation."""
        # List of the generated variable pairs
        tmp_list = []

        # Calculate the number of generated variable pairs
        if self.percentage_random_cors <= 0.5:
            # Calculate the number of variable pairs.
            num_total = self.percentage_random_cors * len(self.discrete_indices[event_index]) * (len(
                self.discrete_indices[event_index]) - 1) / 2
        else:
            # Calculate the number of variable pairs which are not in the resulting correlations.
            # Used to reduce the runtime for higher values of percentage_random_cors
            num_total = (1-self.percentage_random_cors) * len(self.discrete_indices[event_index]) * (len(
                self.discrete_indices[event_index]) - 1) / 2
        if round(num_total % 1., 4) < 0.5 or (round(num_total % 1., 4) == 0.5 and self.percentage_random_cors >= 0.5):
            num_total = int(num_total)
        else:
            num_total = int(num_total+1)

        # Generate num_total variable pairs
        while len(tmp_list) < num_total:
            pos_cor = np.random.randint(0, len(self.discrete_indices[event_index]), [num_total - len(tmp_list), 2])
            for _, pos_val in enumerate(pos_cor):
                if pos_val[0] != pos_val[1] and [min(pos_val[0], pos_val[1]), max(pos_val[0], pos_val[1])] not in tmp_list:
                    tmp_list.append([min(pos_val[0], pos_val[1]), max(pos_val[0], pos_val[1])])

        if self.percentage_random_cors <= 0.5:
            # Return the generated variable pairs
            return tmp_list
        # Return all variable pairs, which are not in the generated set
        return [[i, j] for i in range(len(self.discrete_indices[event_index])) for j in range(i + 1, len(self.discrete_indices[
            event_index])) if [i, j] not in tmp_list]

    # skipcq: PYL-R0201
    def check_cor_w_rel(self, probability_list, total_pos_val):
        """Check if the probabilities can be considered a possible correlation."""
        if (self.check_cor_thres * total_pos_val < len(probability_list)) and (
                total_pos_val > self.check_cor_num_thres or max(probability_list) - min(probability_list) < (
                    self.check_cor_prob_thres * sum(probability_list) / len(probability_list))):
            return False
        return True

    def validate_cor(self):
        """Validate the found correlations and removes the ones, which fail the requirements."""
        for meth in self.used_validate_cor_meth:
            if meth == 'coverVals':
                self.validate_cor_cover_vals()
            elif meth == 'distinctDistr':
                self.validate_cor_distinct_distr()

    def validate_cor_cover_vals(self):
        """
        Rate all found relation in regards to their coverage of the values in the first variable.
        It removes the ones, which have a low rating and therefore can not considered real relations.
        """
        for meth in self.used_cor_meth:
            if meth == 'Rel':
                for event_index, event_val in enumerate(self.rel_list):
                    for pos_var_cor_index in range(len(self.pos_var_cor[event_index])):  # skipcq: PTC-W0060
                        # Check if the correlations i=i_val -> j=j_val have a high enough score
                        tmp_sum = sum([sum(event_val[pos_var_cor_index][0][i_val].values()) for i_val in event_val[pos_var_cor_index][0]])

                        if tmp_sum < self.event_type_detector.num_event_lines[event_index]*self.validate_cor_cover_vals_thres:
                            event_val[pos_var_cor_index][0] = {}

                        # Check if the correlations j=j_val -> i=i_val have a high enough score
                        tmp_sum = sum([sum(event_val[pos_var_cor_index][1][j_val].values()) for j_val in event_val[pos_var_cor_index][1]])

                        if tmp_sum < self.event_type_detector.num_event_lines[event_index]*self.validate_cor_cover_vals_thres:
                            event_val[pos_var_cor_index][1] = {}

            elif meth == 'WRel':
                for event_index, event_val in enumerate(self.w_rel_list):
                    for pos_var_cor_index in range(len(self.pos_var_cor[event_index])):  # skipcq: PTC-W0060
                        # Check if the correlations i=i_val -> j=j_val have a high enough score
                        tmp_sum = sum([sum(event_val[pos_var_cor_index][0][i_val].values()) for i_val in event_val[pos_var_cor_index][0]])

                        if tmp_sum < self.event_type_detector.num_event_lines[event_index]*self.validate_cor_cover_vals_thres:
                            event_val[pos_var_cor_index][0] = {}

                        # Check if the correlations j=j_val -> i=i_val have a high enough score
                        tmp_sum = sum([sum(event_val[pos_var_cor_index][1][j_val].values()) for j_val in event_val[pos_var_cor_index][1]])

                        if tmp_sum < self.event_type_detector.num_event_lines[event_index]*self.validate_cor_cover_vals_thres:
                            event_val[pos_var_cor_index][1] = {}

    def validate_cor_distinct_distr(self):
        """
        Compare the right hand sides of the found relations.
        It removes the correlations, which are too similar to the distribution of the variable type.
        """
        for meth in self.used_cor_meth:
            if meth == 'WRel':
                for event_index, event_val in enumerate(self.w_rel_list):
                    for pos_var_cor_index, pos_var_cor_val in enumerate(self.pos_var_cor[event_index]):
                        # Check if the correlations i=i_val -> j=j_val are distinct enough to be considered independent
                        # List in which the distributions of the single corrs are saved.
                        distribution_list = [[] for _ in range(len(self.pos_var_val[event_index][pos_var_cor_val[1]]))]  # skipcq: PTC-W0060
                        # The probabilities can be read out with: distribution_list[j_val][i_val]
                        frequency_list = []  # List which stores the appearance of the single correlations
                        for i_val in event_val[pos_var_cor_index][0]:
                            if sum(event_val[pos_var_cor_index][0][i_val].values()) > self.min_values_cors_thres:
                                # Calculates the distribution and appends it to distribution_list
                                frequency_list.append(sum(event_val[pos_var_cor_index][0][i_val].values()))
                                for k, k_val in enumerate(self.pos_var_val[event_index][pos_var_cor_val[1]]):
                                    if k_val in event_val[pos_var_cor_index][0][i_val]:
                                        distribution_list[k].append(event_val[pos_var_cor_index][0][i_val][k_val] / frequency_list[-1])
                                    else:
                                        distribution_list[k].append(0)

                        # Number of total appearances
                        total_frequency = max(1, sum(frequency_list))

                        # Mean of the distributions
                        mean_list = [sum([distribution_list[i][j]*frequency_list[j] for j in range(len(frequency_list))])/total_frequency
                                     for i in range(len(self.pos_var_val[event_index][pos_var_cor_val[1]]))]

                        # Variance of the correlations
                        variance_list = [0 for _ in range(len(self.pos_var_val[event_index][pos_var_cor_val[1]]))]
                        # Calculate the variance of the single values
                        for i in range(len(self.pos_var_val[event_index][pos_var_cor_val[1]])):  # skipcq: PTC-W0060
                            variance_list[i] = sum([(distribution_list[i][j] - mean_list[i])**2 * frequency_list[j] / total_frequency for j
                                                   in range(len(frequency_list))])

                        # Check if the variance exceeds the threshold
                        if sum(variance_list) < self.validate_cor_distinct_thres:
                            event_val[pos_var_cor_index][0] = {}

                        # Check if the correlations j=j_val -> i=i_val are distinct enough to be considered independent
                        # List in which the distributions of the single corrs are saved.
                        distribution_list = [[] for _ in range(len(self.pos_var_val[event_index][pos_var_cor_val[0]]))]  # skipcq: PTC-W0060
                        # The probabilities can be read out with: distribution_list[i_val][j_val]
                        frequency_list = []  # List which stores the appearance of the single correlations
                        for j_val in event_val[pos_var_cor_index][1]:
                            if sum(event_val[pos_var_cor_index][1][j_val].values()) > self.min_values_cors_thres:
                                # Calculates the distribution and appends it to distribution_list
                                frequency_list.append(sum(event_val[pos_var_cor_index][1][j_val].values()))
                                for k, k_val in enumerate(self.pos_var_val[event_index][pos_var_cor_val[0]]):
                                    if k_val in event_val[pos_var_cor_index][1][j_val]:
                                        distribution_list[k].append(
                                            event_val[pos_var_cor_index][1][j_val][k_val] / frequency_list[-1])
                                    else:
                                        distribution_list[k].append(0)

                        # Number of total appearances
                        total_frequency = max(1, sum(frequency_list))

                        # Mean of the distributions
                        mean_list = [sum([distribution_list[i][j]*frequency_list[j] for j in range(len(frequency_list))])/total_frequency
                                     for i in range(len(self.pos_var_val[event_index][pos_var_cor_val[0]]))]

                        # Variance of the correlations
                        variance_list = [0 for _ in range(len(self.pos_var_val[event_index][pos_var_cor_val[0]]))]

                        # Calculate the variance of the single values
                        for i in range(len(self.pos_var_val[event_index][pos_var_cor_val[0]])):  # skipcq: PTC-W0060
                            variance_list[i] = sum([(distribution_list[i][j] - mean_list[i])**2 * frequency_list[j] / total_frequency for j
                                                    in range(len(frequency_list))])

                        # Check if the variance exceeds the threshold
                        if sum(variance_list) < self.validate_cor_distinct_thres:
                            event_val[pos_var_cor_index][1] = {}

    def print_ini_rel(self, event_index):
        """Print the generated correlations for the method 'relations'."""
        message = f'Initialisation of the method relations of the event {self.event_type_detector.get_event_type(event_index)}'
        # skipcq: PYL-C0209
        message += '\n%s rules have been generated for this event type' % (
                sum([len(self.rel_list[event_index][pos_var_cor_index][0]) for pos_var_cor_index in range(len(
                    self.rel_list[event_index])) if self.rel_list[event_index][pos_var_cor_index] != [{}, {}]]) + sum([len(
                        self.rel_list[event_index][pos_var_cor_index][1]) for pos_var_cor_index in range(len(self.rel_list[event_index])) if
                        self.rel_list[event_index][pos_var_cor_index] != [{}, {}]]))
        sorted_log_lines = []
        event_data = {'EventIndex': event_index}
        affected_log_atom_paths = []
        affected_log_atom_values = []
        for pos_var_cor_index, pos_var_cor_val in enumerate(self.rel_list[event_index]):
            if pos_var_cor_val != [{}, {}]:
                i = self.pos_var_cor[event_index][pos_var_cor_index][0]
                j = self.pos_var_cor[event_index][pos_var_cor_index][1]

                for i_val in pos_var_cor_val[0]:  # Var i=i_val -> Var j=j_val
                    if len(pos_var_cor_val[0][i_val]) > 0 and sum(pos_var_cor_val[0][i_val].values()) > self.min_values_cors_thres:
                        # skipcq: PYL-C0209
                        sorted_log_lines.append('x) VarPath %s = %s' % (
                            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][i]], repr(i_val)))
                        # skipcq: PYL-C0209
                        sorted_log_lines.append(' ->VarPath %s = %s' % (
                            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][j]],
                            [[j_val, pos_var_cor_val[0][i_val][j_val]] for j_val in pos_var_cor_val[0][i_val].keys()]))
                        affected_log_atom_paths.append(
                            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][i]])
                        affected_log_atom_paths.append(
                            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][j]])
                        affected_log_atom_values.append(repr(i_val))
                        affected_log_atom_values.append([[j_val, pos_var_cor_val[0][i_val][j_val]] for j_val in pos_var_cor_val[0][
                            i_val].keys()])

                for j_val in pos_var_cor_val[1]:  # Var j=j_val -> Var i=i_val
                    if len(pos_var_cor_val[1][j_val]) > 0 and sum(pos_var_cor_val[1][j_val].values()) > self.min_values_cors_thres:
                        # skipcq: PYL-C0209
                        sorted_log_lines.append('x) VarPath %s = %s' % (
                            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][j]], repr(j_val)))
                        # skipcq: PYL-C0209
                        sorted_log_lines.append(' ->VarPath %s = %s' % (
                            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][i]],
                            [[i_val, pos_var_cor_val[1][j_val][i_val]] for i_val in pos_var_cor_val[1][j_val].keys()]))
                        affected_log_atom_paths.append(
                            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][j]])
                        affected_log_atom_paths.append(
                            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][i]])
                        affected_log_atom_values.append(repr(j_val))
                        affected_log_atom_values.append([[i_val, pos_var_cor_val[1][j_val][
                            i_val]] for i_val in pos_var_cor_val[1][j_val].keys()])
        if len(sorted_log_lines) != 0:
            event_data['AffectedLogAtomPaths'] = list(set(affected_log_atom_paths))
            event_data['AffectedLogAtomValues'] = affected_log_atom_values
            sorted_log_lines += [''] * (self.event_type_detector.total_records - len(sorted_log_lines))
            for listener in self.anomaly_event_handlers:
                listener.receive_event(f'Analysis.{self.__class__.__name__}', message, sorted_log_lines, event_data, self.log_atom, self)

    def print_ini_w_rel(self, event_index):
        """Print the generated correlations for the method 'weighted relations'."""
        message = f'Initialisation of the method weighted relations of the event {self.event_type_detector.get_event_type(event_index)}'
        # skipcq: PYL-C0209
        message += '\n%s rules have been generated for this event type' % (
                sum([len([i_val for i_val in self.w_rel_list[event_index][pos_var_cor_index][0] if len(self.w_rel_list[event_index][
                    pos_var_cor_index][0][i_val]) > 0 and sum(self.w_rel_list[event_index][pos_var_cor_index][0][i_val].values()) >
                    self.min_values_cors_thres])
                    for pos_var_cor_index, pos_var_cor_val in enumerate(self.w_rel_list[event_index]) if pos_var_cor_val != [
                        {}, {}]]) + sum([len([j_val for j_val in pos_var_cor_val[1] if len(pos_var_cor_val[1][j_val]) > 0 and sum(
                            pos_var_cor_val[1][j_val].values()) > self.min_values_cors_thres]) for pos_var_cor_index, pos_var_cor_val in
                            enumerate(self.w_rel_list[event_index]) if pos_var_cor_val != [{}, {}]]))
        sorted_log_lines = []
        event_data = {'EventIndex': event_index}
        affected_log_atom_paths = []
        affected_log_atom_values = []
        for pos_var_cor_index, pos_var_cor_val in enumerate(self.w_rel_list[event_index]):
            if pos_var_cor_val != [{}, {}]:
                i = self.pos_var_cor[event_index][pos_var_cor_index][0]
                j = self.pos_var_cor[event_index][pos_var_cor_index][1]

                for i_val in pos_var_cor_val[0]:  # Var i = i_val -> Var j = j_val
                    if len(pos_var_cor_val[0][i_val]) > 0 and sum(pos_var_cor_val[0][i_val].values()) > 50:
                        tmp_sum = sum(pos_var_cor_val[0][i_val].values())
                        # skipcq: PYL-C0209
                        sorted_log_lines.append('x) VarPath %s = %s' % (
                            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][i]], repr(i_val),))
                        # skipcq: PYL-C0209
                        sorted_log_lines.append(' ->VarPath %s = %s' % (
                            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][j]],
                            [[j_val, pos_var_cor_val[0][i_val][j_val] / tmp_sum] for j_val in pos_var_cor_val[0][i_val].keys()]))
                        affected_log_atom_paths.append(
                            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][i]])
                        affected_log_atom_paths.append(
                            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][j]])
                        affected_log_atom_values.append(repr(i_val))
                        affected_log_atom_values.append([[j_val, pos_var_cor_val[0][i_val][j_val] / tmp_sum] for j_val in pos_var_cor_val[
                            0][i_val].keys()])

                for j_val in pos_var_cor_val[1]:  # Var j = j_val -> Var i = i_val
                    if len(pos_var_cor_val[1][j_val]) > 0 and sum(pos_var_cor_val[1][j_val].values()) > 50:
                        tmp_sum = sum(pos_var_cor_val[1][j_val].values())
                        # skipcq: PYL-C0209
                        sorted_log_lines.append('x) VarPath %s = %s' % (
                            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][j]], repr(j_val)))
                        # skipcq: PYL-C0209
                        sorted_log_lines.append(' ->VarPath %s = %s' % (
                            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][i]],
                            [[i_val, pos_var_cor_val[1][j_val][i_val] / tmp_sum] for i_val in pos_var_cor_val[1][j_val].keys()]))
                        affected_log_atom_paths.append(
                            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][j]])
                        affected_log_atom_paths.append(
                            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][i]])
                        affected_log_atom_values.append(repr(j_val))
                        affected_log_atom_values.append([[i_val, pos_var_cor_val[1][j_val][i_val] / tmp_sum] for i_val in pos_var_cor_val[
                            1][j_val].keys()])

        if len(sorted_log_lines) != 0:
            event_data['AffectedLogAtomPaths'] = list(set(affected_log_atom_paths))
            event_data['AffectedLogAtomValues'] = affected_log_atom_values
            sorted_log_lines += [''] * (self.event_type_detector.total_records - len(sorted_log_lines))
            for listener in self.anomaly_event_handlers:
                listener.receive_event(f'Analysis.{self.__class__.__name__}', message, sorted_log_lines, event_data, self.log_atom, self)

    def print_failed_wrel_test(self, event_index, pos_var_cor_index, cor_direction, value1):
        """Print the correlations which failed in a test step for the method 'weighted relations'."""
        cor_direction_neg = 0
        if cor_direction == 0:
            cor_direction_neg = 1

        # skipcq: PYL-C0209
        message = 'Correlation of the paths %s = %s -> %s = %s would be rejected after the %s-th line' % (
            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][
                self.pos_var_cor[event_index][pos_var_cor_index][cor_direction]]], repr(value1),
            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][
                self.pos_var_cor[event_index][pos_var_cor_index][cor_direction_neg]]], [[value2, self.w_rel_list[event_index][
                    pos_var_cor_index][cor_direction][value1][value2] / sum(self.w_rel_list[event_index][pos_var_cor_index][
                        cor_direction][value1].values())] for value2 in self.w_rel_list[event_index][pos_var_cor_index][
                    cor_direction][value1].keys()], self.event_type_detector.total_records)
        confidence = sum(self.w_rel_confidences[event_index][pos_var_cor_index][cor_direction][value1]) / len(
                self.w_rel_confidences[event_index][pos_var_cor_index][cor_direction][value1])
        event_data = {'EventIndex': event_index}
        affected_log_atom_paths = []
        affected_values = []
        affected_log_atom_paths.append(self.event_type_detector.variable_key_list[event_index][
            self.discrete_indices[event_index][self.pos_var_cor[event_index][pos_var_cor_index][cor_direction]]])
        affected_log_atom_paths.append(self.event_type_detector.variable_key_list[event_index][
            self.discrete_indices[event_index][self.pos_var_cor[event_index][pos_var_cor_index][cor_direction_neg]]])
        affected_values.append(repr(value1))
        affected_values.append([[value2, self.w_rel_list[event_index][pos_var_cor_index][cor_direction][value1][value2] / sum(
            self.w_rel_list[event_index][pos_var_cor_index][cor_direction][value1].values())] for value2 in self.w_rel_list[
            event_index][pos_var_cor_index][cor_direction][value1].keys()])
        event_data['AffectedLogAtomPaths'] = list(set(affected_log_atom_paths))
        event_data['AffectedValues'] = affected_values
        event_data['TypeInfo'] = {'Confidence': confidence}
        sorted_log_lines = [''] * self.event_type_detector.total_records
        for listener in self.anomaly_event_handlers:
            listener.receive_event(
                f'Analysis.{self.__class__.__name__}', message, sorted_log_lines, event_data, self.log_atom, self)

    def print_failed_wrel_update(self, event_index, pos_var_cor_index, cor_direction, value1):
        """Print the correlations which failed in an update step for the method 'weighted relations'."""
        cor_direction_neg = 0
        if cor_direction == 0:
            cor_direction_neg = 1

        # skipcq: PYL-C0209
        message = 'Correlation of the target_path_list %s = %s -> %s = %s has been rejected after the %s-th line' % (
            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][
                self.pos_var_cor[event_index][pos_var_cor_index][cor_direction]]], repr(value1),
            self.event_type_detector.variable_key_list[event_index][self.discrete_indices[event_index][
                self.pos_var_cor[event_index][pos_var_cor_index][cor_direction_neg]]], [[value2, self.w_rel_list[event_index][
                    pos_var_cor_index][cor_direction][value1][value2] / sum(self.w_rel_list[event_index][pos_var_cor_index][
                        cor_direction][value1].values())] for value2 in self.w_rel_list[event_index][pos_var_cor_index][
                    cor_direction][value1].keys()], self.event_type_detector.total_records)
        confidence = sum(self.w_rel_confidences[event_index][pos_var_cor_index][cor_direction][value1]) / len(
                self.w_rel_confidences[event_index][pos_var_cor_index][cor_direction][value1])
        event_data = {'EventIndex': event_index}
        affected_log_atom_paths = []
        affected_values = []
        affected_log_atom_paths.append(self.event_type_detector.variable_key_list[event_index][
            self.discrete_indices[event_index][self.pos_var_cor[event_index][pos_var_cor_index][cor_direction]]])
        affected_log_atom_paths.append(self.event_type_detector.variable_key_list[event_index][
            self.discrete_indices[event_index][self.pos_var_cor[event_index][pos_var_cor_index][cor_direction_neg]]])
        affected_values.append(repr(value1))
        affected_values.append([[value2, self.w_rel_list[event_index][pos_var_cor_index][cor_direction][value1][value2] / sum(
            self.w_rel_list[event_index][pos_var_cor_index][cor_direction][value1].values())] for value2 in self.w_rel_list[
            event_index][pos_var_cor_index][cor_direction][value1].keys()])
        event_data['AffectedLogAtomPaths'] = list(set(affected_log_atom_paths))
        event_data['AffectedValues'] = affected_values
        event_data['TypeInfo'] = {'Confidence': confidence}
        sorted_log_lines = [''] * self.event_type_detector.total_records
        for listener in self.anomaly_event_handlers:
            listener.receive_event(
                f'Analysis.{self.__class__.__name__}', message, sorted_log_lines, event_data, self.log_atom, self)

    # skipcq: PYL-R0201
    def bt_min_successes(self, num_BT, p, alpha):
        """
        Calculate the minimal number of successes for the BT with significance alpha.
        p is the probability of success and num_BT is the number of observed tests.
        """
        tmp_sum = 0.0
        max_observations_factorial = np.math.factorial(num_BT)
        i_factorial = 1
        for i in range(num_BT + 1):
            i_factorial = i_factorial * max(i, 1)
            tmp_sum = tmp_sum + max_observations_factorial / (i_factorial * np.math.factorial(num_BT - i)) * ((1-p) ** i) * (p ** (
                    num_BT - i))
            if tmp_sum > alpha:
                return num_BT-i
        return 0
