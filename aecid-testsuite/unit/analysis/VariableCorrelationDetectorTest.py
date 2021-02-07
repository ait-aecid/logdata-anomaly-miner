from aminer.analysis.EventTypeDetector import EventTypeDetector
from aminer.analysis.VariableTypeDetector import VariableTypeDetector
from aminer.analysis.VariableCorrelationDetector import VariableCorrelationDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing import ParserMatch, MatchElement
from unit.TestBase import TestBase

from time import time
import random
from copy import deepcopy


class VariableCorrelationDetectorTest(TestBase):
    """This class containts unittests for the VariableCorrelationDetector."""

    # Number of execution of the tested function
    iterations = 20
    # Size of the initial datasample
    dataset_size = 100
    # Significance level
    significance_niveau = 0.05

    def test1filter_variables_with_vtd(self):
        """This test case checks if the variables are filtered accurately using the VariableTypeDetector."""
        self.filter_variables(True)

    def test2filter_variables_without_vtd(self):
        """This test case checks if the variables are filtered accurately without using the VariableTypeDetector."""
        self.filter_variables(False)

    def filter_variables(self, use_vtd):
        """Run the filter variables code with or without the VariableTypeDetector."""
        t = time()
        stat_data = b'5.3.0-55-generic'
        log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        if use_vtd:
            vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=self.dataset_size,
                                       div_thres=0.1, test_ks_int=True, sim_thres=0.3, ks_alpha=self.significance_niveau)
        vcd = VariableCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.1)
        for _ in range(self.dataset_size):
            etd.receive_atom(log_atom)
            if use_vtd:
                vtd.receive_atom(log_atom)
        vcd.init_cor(0)
        # the vcd should not learn any correlations in static data.
        self.assertEqual(vcd.pos_var_val, [[]])

        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        if use_vtd:
            vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=self.dataset_size,
                                       div_thres=0.1, test_ks_int=False, sim_thres=0.5, ks_alpha=self.significance_niveau)
        vcd = VariableCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.1)
        for i in range(self.dataset_size):
            stat_data = bytes(str((i % 60) * 0.1), 'utf-8')
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            etd.receive_atom(log_atom)
            if use_vtd:
                vtd.receive_atom(log_atom)
        vcd.init_cor(0)
        # the vcd should not learn any correlations in others data.
        self.assertEqual(vcd.pos_var_val, [[]])

        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        if use_vtd:
            vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=self.dataset_size,
                                       div_thres=0.1, test_ks_int=True, sim_thres=0.3, ks_alpha=self.significance_niveau)
        vcd = VariableCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.1)
        values = []
        for i in range(self.dataset_size):
            stat_data = bytes(str((i % 10) * 0.1), 'utf-8')
            values.append(float(stat_data))
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            etd.receive_atom(log_atom)
            if use_vtd:
                vtd.receive_atom(log_atom)
        vcd.init_cor(0)
        values_set = list(set(values))
        # the vcd should learn any correlations in discrete data.
        self.assertEqual(vcd.pos_var_val, [[values_set]])

        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        if use_vtd:
            vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=self.dataset_size,
                                       div_thres=0.1, test_ks_int=True, sim_thres=0.3, ks_alpha=self.significance_niveau)
        vcd = VariableCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.1)
        values = []
        for i in range(self.dataset_size):
            stat_data = bytes(str((i % 11) * 0.1), 'utf-8')
            values.append(float(stat_data))
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            etd.receive_atom(log_atom)
            if use_vtd:
                vtd.receive_atom(log_atom)
        vcd.init_cor(0)
        # the vcd should not learn any correlations if the discrete data is not in the threshold.
        self.assertEqual(vcd.pos_var_val, [[]])

    def test3initialize_variables_with_matchDiscDistr_preselection_method(self):
        """This test case checks the functionality of the matchDiscDistr preselection method."""
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vcd = VariableCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.1)
        values_list1 = [1.0/10]*10
        values_list2 = [1.0/14]*14
        # an correlation should be detected even if the second list contains more values than the first.
        self.assertTrue(vcd.pick_cor_match_disc_distr(values_list1, values_list2))

        values_list2 = [1.0/7]*7
        # an correlation should be detected even if the second list contains less values than the first.
        self.assertTrue(vcd.pick_cor_match_disc_distr(values_list1, values_list2))

        values_list2 = [1.0/30]*30
        # an correlation should not be detected if the probability of occurrence difference is too high.
        self.assertFalse(vcd.pick_cor_match_disc_distr(values_list1, values_list2))

        values_list2 = [0.2] + [0.8/9]*9
        # an correlation should not be detected if the probability of occurrence difference is too high.
        self.assertFalse(vcd.pick_cor_match_disc_distr(values_list1, values_list2))

        # find correlations even when the lists are randomly shuffled.
        values_list1 = [0.3]*2 + [0.4/3]*3
        values_list2 = [1.0/5] * 5
        random.shuffle(values_list1)
        self.assertTrue(vcd.pick_cor_match_disc_distr(values_list1, values_list2))

    def test4initialize_variables_with_excludeDueDistr_preselection_method(self):
        """This test case checks the functionality of the excludeDueDistr preselection method."""
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vcd = VariableCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.1)

        # equal distribution - no exclusion expected
        values = [0.1]*10
        self.assertTrue(vcd.pick_cor_exclude_due_distr(values))

        # almost equal distribution - no exclusion expected
        values = [0.3] + [0.078]*9
        self.assertTrue(vcd.pick_cor_exclude_due_distr(values))

        # one value with high probability - exclusion expected
        values = [0.5] + [0.056]*9
        self.assertFalse(vcd.pick_cor_exclude_due_distr(values))

        # multiple values with high probability - no exclusion expected
        values = [0.3]*3 + [0.014]*7
        self.assertTrue(vcd.pick_cor_exclude_due_distr(values))

        # check boundaries
        values = [0.5]*2
        self.assertTrue(vcd.pick_cor_exclude_due_distr(values))

        values = [0.8, 0.2]
        self.assertFalse(vcd.pick_cor_exclude_due_distr(values))

        values = [0.33]*3
        self.assertTrue(vcd.pick_cor_exclude_due_distr(values))

        values = [0.7] + [0.15]*2
        self.assertFalse(vcd.pick_cor_exclude_due_distr(values))

        values = [0.25]*4
        self.assertTrue(vcd.pick_cor_exclude_due_distr(values))

        values = [0.58] + [0.14]*3
        self.assertFalse(vcd.pick_cor_exclude_due_distr(values))

    def test5initialize_variables_with_matchDiscVals_preselection_method(self):
        """
        This test case checks the functionality of the matchDiscVals preselection method.
        This test actually uses values instead of probabilities, but they are similar to the values used in test3.
        """
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vcd = VariableCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.1)
        values_set1 = [i*0.1 for i in range(10)]
        values_set2 = [i*0.2 for i in range(7)]
        # an correlation should be detected even if the second list contains less values than the first.
        self.assertTrue(vcd.pick_cor_match_disc_vals(values_set1, values_set2))

        values_set2 = [i*0.3 for i in range(7)]
        # an correlation should not be detected if too many values are different.
        self.assertFalse(vcd.pick_cor_match_disc_vals(values_set1, values_set2))

        values = []
        for i in range(58):
            stat_data = bytes(str(i * 0.1), 'utf-8')
            values.append(float(stat_data))
        values_set1 = values

        values = []
        for i in range(41):
            stat_data = bytes(str(i * 0.2), 'utf-8')
            values.append(float(stat_data))
        values_set2 = values
        # an correlation should be detected if not too many values are different.
        self.assertTrue(vcd.pick_cor_match_disc_vals(values_set1, values_set2))

        values = []
        for i in range(42):
            stat_data = bytes(str(i * 0.2), 'utf-8')
            values.append(float(stat_data))
        values_set2 = values
        # an correlation should not be detected if too many values are different.
        self.assertFalse(vcd.pick_cor_match_disc_vals(values_set1, values_set2))

    def test6initialize_variables_with_random_preselection_method(self):
        """
        This test case checks the functionality of the random preselection method. It tests all percentage_random_cors in [0.01..1.0[.
        For all paths the possible amount of combinations is 10. The expected number of correlations is rounded. For example with
        0.05 <= percentage_random_cors < 0.15 exactly one combination is expected. The combinations also must not be repeated reversed and
        combinations with itself are not allowed. The used discrete data is for every path the same.
        """
        t = time()
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vcd = VariableCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.1,
                                          used_presel_meth=['random'])
        values = []
        for i in range(self.dataset_size):
            stat_data = bytes(str((i % 10) * 0.1), 'utf-8')
            values.append(float(stat_data))
            children = [MatchElement(str(j), stat_data.decode(), stat_data, None) for j in range(5)]
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('/', bytes(str(i), 'utf-8').decode(), bytes(str(i), 'utf-8'), children)),
                               t, self.__class__.__name__)
            etd.receive_atom(log_atom)
        vcd.init_cor(0)
        # test random correlation picking by using vcd.percentage_random_cors [0.01..1.0[
        for i in range(1, 100):
            vcd.percentage_random_cors = i / 100
            # out of 10 possible combinations exactly x should occur.
            x = i // 10 + (i % 10 >= 5)
            correlations = vcd.pick_cor_random(0)
            self.assertEqual(len(correlations), x, "Error at i = %d" % i)
            for corr in correlations:
                # one path must not correlate with itself.
                self.assertNotEqual(corr[0], corr[1])
                # the same, reversed combination must not be in values.
                self.assertFalse([corr[1], corr[0]] in correlations)

        # test if a ValueError is raised when percentage_random_cors is out of range.
        self.assertRaises(ValueError, VariableCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], etd,
                          disc_div_thres=0.1, used_presel_meth=['random'], percentage_random_cors=1.2)
        self.assertRaises(ValueError, VariableCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], etd,
                          disc_div_thres=0.1, used_presel_meth=['random'], percentage_random_cors=1.0)
        self.assertRaises(ValueError, VariableCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], etd,
                          disc_div_thres=0.1, used_presel_meth=['random'], percentage_random_cors=0.0)
        self.assertRaises(ValueError, VariableCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], etd,
                          disc_div_thres=0.1, used_presel_meth=['random'], percentage_random_cors=-1.2)

    def test7initialize_variables_with_intersect_presel_meth(self):
        """
        This test case checks the functionality of the intersect_presel_meth flag with multiple preselection methods.
        These are 'excludeDueDistr' and 'matchDiscVals'. In the first case intersect_presel_meth=False and correlations can be detected
        successfully. In the second case intersect_presel_meth=True and no correlations are found because they are excluded in
        'excludeDueDistr'.
        """
        t = time()
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vcd_union = VariableCorrelationDetector(
            self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.1, used_presel_meth=[
                'excludeDueDistr', 'matchDiscVals'], intersect_presel_meth=False)
        vcd_intersection = VariableCorrelationDetector(
            self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.5, used_presel_meth=[
                'excludeDueDistr', 'matchDiscVals'], intersect_presel_meth=True)
        vcd_exclude = VariableCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.1,
                                                  used_presel_meth=['excludeDueDistr'])
        vcd_match = VariableCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.1,
                                                used_presel_meth=['matchDiscVals'])
        var1 = ['a']*50 + ['b']*50
        var2 = ['a']*90 + ['b']*10
        var3 = ['c']*20 + ['d']*50 + ['e']*30
        var4 = ['c']*50 + ['d']*50

        for i in range(len(var1)):
            children = [MatchElement('2', var2[i], var2[i].encode(), None), MatchElement('3', var3[i], var3[i].encode(), None),
                        MatchElement('4', var4[i], var4[i].encode(), None)]
            log_atom = LogAtom(var1[i].encode(), ParserMatch(MatchElement('/', var1[i], var1[i].encode(), children)), t,
                               self.__class__.__name__)
            etd.receive_atom(log_atom)
        vcd_union.init_cor(0)
        vcd_intersection.init_cor(0)
        vcd_exclude.init_cor(0)
        vcd_match.init_cor(0)
        values_set = [[list(set(var1))] + [list(set(var2))] + [list(set(var3))] + [list(set(var4))]]
        self.assertTrue(sorted(vcd_union.pos_var_val), sorted(values_set))
        # intersect_presel_meth=False -> correlations should be found.
        # the correlation has to be in at least one presel method. (OR-Statement)
        unique_list = deepcopy(vcd_exclude.pos_var_cor[0])
        for cor in vcd_match.pos_var_cor[0]:
            if cor not in unique_list:
                unique_list.append(cor)
        self.assertEqual(len(unique_list), len(vcd_union.pos_var_cor[0]))

        values_set = [[list(set(var1))] + [list(set(var2))] + [list(set(var3))] + [list(set(var4))]]
        self.assertTrue(sorted(vcd_intersection.pos_var_val), sorted(values_set))
        # intersect_presel_meth=True -> correlations should still be found.
        # the correlation has to be in both presel methods. (AND-Statement)
        unique_list = []
        for cor in vcd_exclude.pos_var_cor[0]:
            if cor in vcd_match.pos_var_cor[0] and cor not in unique_list:
                unique_list.append(cor)
        for cor in vcd_match.pos_var_cor[0]:
            if cor in vcd_exclude.pos_var_cor[0] and cor not in unique_list:
                unique_list.append(cor)
        self.assertEqual(len(unique_list), len(vcd_intersection.pos_var_cor[0]))

    def test8initialize_variables_with_no_preselection_method(self):
        """
        This test case checks the selection with no preselection method used.
        Also this test case checks the functionality of the Rel and WRel methods. For the data generation the main path '/' always contains
        (i % 10)*1 and child elements contain (i % 10)*1 for half of the time and (i % 10)*2 for the other half. The first half of
        the data contains 10 different values. These values are not combined with other values like in the second half of the data, which
        introduces 5 new values. Therefore 15 combinations exist (5+4+3+2+1=15). 10 correlations exist when '/' = i*1 -> child = i*1. In the
        second half 5 new correlations are added when '/' = i*1 -> child = i*2.
        """
        t = time()
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vcd = VariableCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.5,
                                          num_init=self.dataset_size)
        values1 = []
        # generate the first half of the data with child elements being (i % 10) * 0.1.
        for i in range(self.dataset_size // 2):
            stat_data = bytes(str((i % 10) * 1), 'utf-8')
            values1.append(float(stat_data))
            children = [MatchElement(str(0), stat_data.decode(), stat_data, None)]
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('/', bytes(str((i % 10) * 1), 'utf-8').decode(),
                               bytes(str((i % 10) * 1), 'utf-8'), children)), t, self.__class__.__name__)
            etd.receive_atom(log_atom)
        values2 = []
        # generate the second half of the data with child elements being (i % 10) * 2.
        for i in range(self.dataset_size // 2):
            stat_data = bytes(str((i % 10) * 2), 'utf-8')
            values2.append(float(stat_data))
            children = [MatchElement(str(0), stat_data.decode(), stat_data, None)]
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('/', bytes(str((i % 10) * 1), 'utf-8').decode(),
                               bytes(str((i % 10) * 1), 'utf-8'), children)), t, self.__class__.__name__)
            etd.receive_atom(log_atom)
        vcd.init_cor(0)
        values_set = list(set(values1 + values2))
        pos_var_val = deepcopy(vcd.pos_var_val)
        # all child elements should contain data from values1 and values2.
        index = pos_var_val[0].index(values_set)
        del pos_var_val[0][index]
        # no other element should contain the united set of values1 and values2.
        self.assertRaises(ValueError, pos_var_val[0].index, values_set)
        # only values1 should be found, because the main path contains only data generated with (i % 10) * 1.
        self.assertEqual(pos_var_val, [[list(set(values1))]])

        # test the functionality of the Rel and WRel methods
        # copy both lists to not modify the actual lists of the vcd.
        rel_list = deepcopy(vcd.rel_list)
        w_rel_list = deepcopy(vcd.w_rel_list)
        for rel in rel_list[0]:
            for r in rel:
                step = 2
                for i in range(len(r)):
                    key = (i % 20 >= 10)*10 + ((i % 10) * step)
                    # search for the key k in the relation r or convert key to float if applicable.
                    for k in r:
                        if key == 0.0:
                            break
                        if k != 0.0 and k % key == 0:
                            key = k
                            break
                    value = r[key]
                    # there is no difference between the first half and the second half of the data, when value = 0.
                    if key == 0.0:
                        self.assertEqual({key: 10}, value)
                    # as the Rel method can learn only one relation, the values should be 2, 4, 6 and 8 when the key is divisible
                    # by 2 and smaller than 10.
                    elif key % 2 == 0 and key < 10.0:
                        self.assertEqual({key: 4}, value)
                    # as the Rel method can learn only one relation, the values should be 2, 4, 6 and 8 when the key is divisible
                    # by 2 and greater or equal 10.
                    elif key % 2 == 0:
                        self.assertEqual({(key/2): 5}, value)
                    else:
                        raise ValueError('The %f: %f combination must not occur in Rel.' % (key, value))

        # relations should be found in both directions and the count should be equal.
        cnt_half = 0  # for example key = 18.0 -> inner key = 9.0
        cnt_double = 0  # for example key = 9.0 -> inner key = 18.0
        for w_rel in w_rel_list[0]:
            for r in w_rel:
                step = 1.0
                # search for the step size
                for k in r:
                    if k >= 10.0:
                        step = 2.0
                if step == 1.0:
                    cnt_half += 1
                else:
                    cnt_double += 1
                for i in range(len(r)):
                    key = (i % 20 >= 10)*10 + ((i % 10) * step)
                    value = r[key]
                    # there is no difference between the first half and the second half of the data, when value = 0.
                    if key == 0.0:
                        self.assertEqual({key: 10}, value)
                    # this if is only reached when step = 2.0.
                    elif key >= 10.0:
                        self.assertEqual({key/2: 5}, value)
                    elif step == 1.0:
                        self.assertEqual({key*2: 5, key: 5}, value)
                    elif step == 2.0:
                        self.assertEqual({key/2: 5, key: 5}, value)
                    else:
                        raise ValueError('The %f: %f combination must not occur in WRel.' % (key, value))
        self.assertEqual(cnt_half, 1)
        self.assertEqual(cnt_double, 1)

    def test9nonexistent_preselection_methods(self):
        """This test case checks if an error occurs, when using an nonexistent preselection method."""
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        self.assertRaises(ValueError, VariableCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], etd,
                          disc_div_thres=0.1, used_presel_meth=['nonexistentPreselMeth'])

    def test10nonexistent_correlation_methods(self):
        """This test case checks if an error occurs, when using an nonexistent correlation method or empty list."""
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        self.assertRaises(ValueError, VariableCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], etd,
                          disc_div_thres=0.1, used_cor_meth=['nonexistentCorDMeth'])

    def test11validate_correlation_rules_coverVals(self):
        """
        This test case checks the functionality of the coverVals validation method.
        The validate_cor_cover_vals_thres is tested in the interval [0.1..1.0]. The data consists mostly of (i % 10) * 1 and every 7th
        value the child elements use (i % 10) * 2 as the condition (i % 7 == 0 and i != 0) is met. Comparing the count of values with
        h*10, as h is used to get the steps with 10%. If the count is smaller than h*10, no value must be found.
        """
        t = time()
        # run test for every 10% of validate_cor_cover_vals_thres
        for h in range(1, 11, 1):
            etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
            vcd = VariableCorrelationDetector(
                self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.5, used_validate_cor_meth=['coverVals'],
                validate_cor_cover_vals_thres=0.7, num_init=self.dataset_size)
            # set new validate_cor_cover_vals_thres
            vcd.validate_cor_cover_vals_thres = h*0.1
            # init and validate. This is needed as the ETD also needs to be initialized.
            for i in range(self.dataset_size):
                stat_data = bytes(str((i % 10)), 'utf-8')
                children = [MatchElement(str(0), stat_data.decode(), stat_data, None)]
                log_atom = LogAtom(stat_data, ParserMatch(MatchElement('/', stat_data.decode(), stat_data, children)), t,
                                   self.__class__.__name__)
                etd.receive_atom(log_atom)
            vcd.init_cor(0)
            vcd.rel_list = [[[{9.0: {9.0: 26}, 16.0: {16.0: 13}}, {9.0: {9.0: 26}, 16.0: {16.0: 13}}]]]
            vcd.w_rel_list = [[[{9.0: {9.0: 26}, 16.0: {16.0: 13, 8.0: 5}}, {9.0: {9.0: 26}, 16.0: {16.0: 13, 8.0: 5}}]]]
            vcd.pos_var_cor = [[[0, 1]]]
            old_rel_list = deepcopy(vcd.rel_list[0])
            old_w_rel_list = deepcopy(vcd.w_rel_list[0])
            vcd.validate_cor()
            self.assertEqual(len(old_rel_list), len(vcd.rel_list[0]))
            self.assertEqual(len(old_w_rel_list), len(vcd.w_rel_list[0]))
            for i in range(len(vcd.rel_list[0])):
                for r in old_rel_list[i]:
                    cnt = 0
                    for key in r:
                        for val in r[key]:
                            cnt += r[key][val]
                    # when the count is smaller than validate_cor_cover_vals_thres in percent, then there should not be any correlations.
                    # h must be multiplied by 10 as it represents 10% steps.
                    if cnt < h * 10:
                        for val in vcd.rel_list[0][i]:
                            self.assertEqual({}, val)
                    else:
                        self.assertEqual(vcd.rel_list[0], old_rel_list)

            for i in range(len(vcd.w_rel_list[0])):
                for r in old_w_rel_list[i]:
                    cnt = 0
                    for key in r:
                        for val in r[key]:
                            cnt += r[key][val]
                    # when the count is smaller than validate_cor_cover_vals_thres in percent, then there should not be any correlations.
                    # h must be multiplied by 10 as it represents 10% steps.
                    if cnt < h * 10:
                        for val in vcd.w_rel_list[0][i]:
                            self.assertEqual({}, val)
                    else:
                        self.assertEqual(vcd.w_rel_list[0], old_w_rel_list)

    def test12validate_correlation_rules_distinctDistr(self):
        """
        This test case checks the functionality of the distinctDistr validation method.
        The first collection of datasets is similar and therefore produces more correlations. The second collection of datasets is not so
        similar and the number of correlations is smaller. The expected correlations can not be compared directly, because the order of the
        correlations is not guaranteed with the distinctDistr validation method. To achieve the equality test, both correlation variables
        are compared to [[], [], []] after all existing correlations are removed.
        """
        t = time()
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vcd = VariableCorrelationDetector(
            self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.1, used_validate_cor_meth=['distinctDistr'],
            validate_cor_distinct_thres=0.05, num_init=self.dataset_size)
        # init and validate
        similar_data1 = ['a']*50 + ['b']*20 + ['c']*25 + ['d']*5
        similar_data2 = ['a']*45 + ['b']*25 + ['c']*15 + ['d']*10 + ['e']*5
        similar_data3 = ['a']*55 + ['b']*15 + ['c']*20 + ['d']*10
        unsimilar_data1 = ['a']*50 + ['b']*20 + ['c']*25 + ['d']*5
        unsimilar_data2 = ['a']*10 + ['b']*15 + ['c']*15 + ['d']*10 + ['e']*50
        unsimilar_data3 = ['a']*25 + ['b']*15 + ['c']*50 + ['d']*10

        for i in range(self.dataset_size):
            children = [MatchElement(str(1), similar_data2[i], bytes(similar_data2[i], 'utf-8'), None),
                        MatchElement(str(2), similar_data3[i], bytes(similar_data3[i], 'utf-8'), None)]
            log_atom = LogAtom(similar_data1, ParserMatch(MatchElement('/', similar_data1[i],
                               bytes(similar_data1[i], 'utf-8'), children)), t, self.__class__.__name__)
            etd.receive_atom(log_atom)
        vcd.init_cor(0)
        old_w_rel_list = deepcopy(vcd.w_rel_list[0])
        vcd.validate_cor()
        self.assertEqual(len(old_w_rel_list), len(vcd.w_rel_list[0]))
        expected_similar_correlations = [[{
            'd': {'e': 5}, 'c': {'d': 10, 'c': 15}, 'b': {'b': 20}, 'a': {'b': 5, 'a': 45}}, {
            'e': {'d': 5}, 'd': {'c': 10}, 'c': {'c': 15}, 'b': {'b': 20, 'a': 5}, 'a': {'a': 45}}], [{
                'd': {'d': 5}, 'c': {'d': 5, 'c': 20}, 'b': {'b': 15, 'a': 5}, 'a': {'a': 50}}, {
                'd': {'d': 5, 'c': 5}, 'c': {'c': 20}, 'b': {'b': 15}, 'a': {'b': 5, 'a': 50}}], [{
                    'e': {'d': 5}, 'd': {'d': 5, 'c': 5}, 'c': {'c': 15}, 'b': {'b': 15, 'a': 10}, 'a': {'a': 45}},
            {'d': {'e': 5, 'd': 5}, 'c': {'d': 5, 'c': 15}, 'b': {'b': 15}, 'a': {'b': 10, 'a': 45}}]]
        for w_rel in vcd.w_rel_list[0]:
            for cor in w_rel:
                deleted = False
                for i in range(len(expected_similar_correlations)):
                    if cor in expected_similar_correlations[i]:
                        index = expected_similar_correlations[i].index(cor)
                        del expected_similar_correlations[i][index]
                        deleted = True
                        break
                # if the correlation was not deleted an error is raised and the test fails.
                if not deleted:
                    raise ValueError('Correlation %s could not be found in the WRel List.' % cor)
        self.assertEqual([[], [], []], expected_similar_correlations)

        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=self.dataset_size, div_thres=0.1,
                                   test_ks_int=True, sim_thres=0.1, ks_alpha=self.significance_niveau)
        vcd = VariableCorrelationDetector(
            self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.1, used_validate_cor_meth=['distinctDistr'],
            validate_cor_distinct_thres=0.05, num_init=self.dataset_size)
        for i in range(self.dataset_size):
            children = [MatchElement(str(1), unsimilar_data2[i], bytes(unsimilar_data2[i], 'utf-8'), None),
                        MatchElement(str(2), unsimilar_data3[i], bytes(unsimilar_data3[i], 'utf-8'), None)]
            log_atom = LogAtom(unsimilar_data1[i], ParserMatch(MatchElement('/', unsimilar_data1[i],
                               bytes(unsimilar_data1[i], 'utf-8'), children)), t, self.__class__.__name__)
            etd.receive_atom(log_atom)
            vtd.receive_atom(log_atom)
        vcd.init_cor(0)
        old_w_rel_list = deepcopy(vcd.w_rel_list[0])
        vcd.validate_cor()
        self.assertEqual(len(old_w_rel_list), len(vcd.w_rel_list[0]))
        expected_unsimilar_correlations = [[
            {}, {'a': {'a': 10}, 'b': {'a': 15}, 'c': {'a': 15}, 'd': {'a': 10}, 'e': {'b': 20, 'c': 25, 'd': 5}}], [
            {}, {'a': {'a': 25}, 'b': {'a': 15}, 'd': {'c': 5, 'd': 5}}], [
            {'a': {'a': 10}, 'b': {'a': 15}, 'c': {'b': 15}, 'd': {'c': 10}, 'e': {'c': 40, 'd': 10}}, {
                'a': {'a': 10, 'b': 15}, 'b': {'c': 15}, 'c': {'d': 10, 'e': 40}, 'd': {'e': 10}}]]
        for w_rel in vcd.w_rel_list[0]:
            for cor in w_rel:
                deleted = False
                for i in range(len(expected_unsimilar_correlations)):
                    if cor in expected_unsimilar_correlations[i]:
                        index = expected_unsimilar_correlations[i].index(cor)
                        del expected_unsimilar_correlations[i][index]
                        deleted = True
                        break
                # if the correlation was not deleted an error is raised and the test fails.
                if not deleted:
                    raise ValueError('Correlation %s could not be found in the WRel List.%s' % (cor, vcd.w_rel_list[0]))
        self.assertEqual([[], [], []], expected_unsimilar_correlations)

    def test13validate_correlation_rules_distinctDistr_without_WRel(self):
        """This test case checks if an error occurs, when using the distinctDistr validation method without the WRel correlation method."""
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        self.assertRaises(ValueError, VariableCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], etd,
                          disc_div_thres=0.1, used_cor_meth=['Rel'], used_validate_cor_meth=['distinctDistr'])

    def test14nonexistent_validation_method(self):
        """This test case checks if an error occurs, when using an nonexistent validation method or empty list."""
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        self.assertRaises(ValueError, VariableCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], etd,
                          disc_div_thres=0.1, used_validate_cor_meth=['nonexistentValidateCorDMeth'])

    def test15update_and_test_correlation_rules_with_rel_correlation_method(self):
        """
        This test case checks the functionality of the Rel correlation method in the update, correlation generation and test phases.
        The correlations are initialized with 10 values for each correlation and keys calculated with (i % 10) * 0.1. In the update phase
        keys are calculated with (i % 10) * 0.2. Due to that the existing value's count must stay the same in cases where new values are not
        created and new values must be created from 1.0 to 1.8. Values are increased by or created with a count of 10.
        """
        description = 'test15VCD1'
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vcd = VariableCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.5,
                                          used_cor_meth=['Rel'], num_init=self.dataset_size)
        self.analysis_context.register_component(vcd, description)
        self.update_or_test_with_rel_correlation_method(etd, vcd, update_rules=True, generate_rules=True)
        for rel in vcd.rel_list[0]:
            for r in rel:
                for i in r:
                    key = i
                    value = r[key]
                    # existing values which are divisible by 2 and smaller than 10.0 should be updated.
                    if key % 2 == 0 and key < 10.0:
                        self.assertEqual({key: 20}, value)
                    # new values which are divisible by 2 and greater than 10.0 should be created.
                    # other values should stay the same as before.
                    else:
                        self.assertEqual({key: 10}, value)

        description = 'test15VCD2'
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vcd = VariableCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.5,
                                          used_cor_meth=['Rel'], num_init=self.dataset_size)
        self.analysis_context.register_component(vcd, description)
        self.update_or_test_with_rel_correlation_method(etd, vcd, update_rules=True, generate_rules=False)
        for rel in vcd.rel_list[0]:
            for r in rel:
                for i in r:
                    key = i
                    value = r[key]
                    # no new values should be created.
                    self.assertFalse(key % 2 == 0 and key >= 10.0)
                    # existing values which are divisible by 2 and smaller than 10.0 should be updated.
                    if key % 2 == 0 and key < 10.0:
                        self.assertEqual({key: 20}, value)
                    # other values should stay the same as before.
                    else:
                        self.assertEqual({key: 10}, value)

        description = 'test15VCD3'
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vcd = VariableCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.5,
                                          used_cor_meth=['Rel'], num_init=self.dataset_size)
        self.analysis_context.register_component(vcd, description)
        old_rel_list = self.update_or_test_with_rel_correlation_method(etd, vcd, update_rules=False, generate_rules=False)
        # no values in the rel_list should be changed.
        self.assertEqual(vcd.rel_list[0], old_rel_list)

        description = 'test15VCD4'
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vcd = VariableCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.5,
                                          used_cor_meth=['Rel'], num_init=self.dataset_size)
        self.analysis_context.register_component(vcd, description)
        offset = 200
        self.update_or_test_with_rel_correlation_method(etd, vcd, update_rules=True, generate_rules=False, offset=offset)
        # old correlations from child elements with the value being divisible by 2 should be deleted. The first ten correlations from the
        # initialization phase were not touched and should remain the same. The other correlation however should delete every value which
        # is divisible by 2.
        rel_list = deepcopy(vcd.rel_list[0])
        # delete correlations from the init phase.
        for rel in vcd.rel_list[0]:
            if rel[0] == rel[1]:
                index = rel_list.index(rel)
                del rel_list[index]
        self.assertEqual(1, len(rel_list))
        for rel in rel_list:
            # the order of the correlations is not guaranteed.
            if len(rel[0]) > len(rel[1]):
                rel0 = rel[0]
                rel1 = rel[1]
            else:
                rel0 = rel[1]
                rel1 = rel[0]
            for i in rel0:
                key = i
                value = rel0[key]
                self.assertEqual({key: 10}, value)
            for i in rel1:
                key = i
                value = rel1[key]
                # no values divisible by 2 should exist.
                self.assertFalse(key % 2 == 0)
                self.assertEqual({key: 10}, value)

    def update_or_test_with_rel_correlation_method(self, etd, vcd, update_rules, generate_rules, offset=0):
        """Run the update or test of rel correlations."""
        t = time()
        values = []
        # generate the initialization data with child elements being (i % 10) * 1.
        for i in range(self.dataset_size):
            stat_data = bytes(str((i % 10) * 1), 'utf-8')
            values.append(float(stat_data))
            children = [MatchElement(str(0), stat_data.decode(), stat_data, None)]
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('/', stat_data.decode(), stat_data, children)), t,
                               self.__class__.__name__)
            etd.receive_atom(log_atom)
        vcd.init_cor(0)
        # test if the initialization contains only correlations with 10 values.
        for rel in vcd.rel_list[0]:
            for r in rel:
                for i in r:
                    key = i
                    value = r[key]
                    self.assertEqual({key: 10}, value)
        old_rel_list = deepcopy(vcd.rel_list[0])
        values = []
        # generate the update data with child elements being (i % 10) * 2.
        for i in range(self.dataset_size):
            stat_data = bytes(str((i % 10) * 2 + offset), 'utf-8')
            values.append(float(stat_data))
            children = [MatchElement(str(0), stat_data.decode(), stat_data, None)]
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement(
                '/', bytes(str((i % 10) * 2), 'utf-8').decode(), bytes(str((i % 10) * 2), 'utf-8'), children)), t,
                self.__class__.__name__)
            etd.receive_atom(log_atom)
        vcd.log_atom = log_atom
        vcd.update_rules[0] = update_rules
        vcd.generate_rules[0] = generate_rules
        vcd.update_or_test_cor(0)
        return old_rel_list

    def test16update_and_test_correlation_rules_with_w_rel_correlation_method(self):
        """
        This test case checks the functionality of the WRel correlation method in the update, correlation generation and test phases.
        The correlations are initialized with 70% of the values having (i % 10) * 0.1 and 30% of the values having (i % 10) * 0.2. In the
        update phase the ratio is changed from 70:30 to 80:20. Thus the expected ratio is 75:25, when update_rules=True wihout offset.
        """
        # This part tests if rules are updated when update_rules=True and generate_rules=True, however no new rules are generated as the
        # same data is passed on in the update process.
        description = 'test16VCD1'
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vcd = VariableCorrelationDetector(
            self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.5, used_cor_meth=['WRel'],
            num_init=self.dataset_size, num_update=self.dataset_size, max_dist_rule_distr=0.5)
        self.analysis_context.register_component(vcd, description)
        self.update_or_test_with_w_rel_correlation_method(etd, vcd, update_rules=True, generate_rules=True)
        self.assertEqual(1, len(vcd.w_rel_list[0]))
        for rel in vcd.w_rel_list[0]:
            for r in rel:
                for i in r:
                    key = i
                    value = r[key]
                    if key == 0:
                        self.assertEqual({key: 20}, value)
                    elif key >= 10.0:
                        self.assertEqual({key/2: 5}, value)
                    elif key % 2 == 0:
                        self.assertTrue(value in ({key/2: 5, key: 15}, {key*2: 5, key: 15}))
                    else:
                        self.assertTrue(value in ({key: 15}, {key*2: 5, key: 15}))

        # This part tests if rules are updated when update_rules=True and generate_rules=False. Therefore the assumptions of correlations is
        # the same as above, because there were no new correlations generated due to the same data being used.
        description = 'test16VCD2'
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vcd = VariableCorrelationDetector(
            self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.5, used_cor_meth=['WRel'],
            num_init=self.dataset_size, num_update=self.dataset_size, max_dist_rule_distr=0.5)
        self.analysis_context.register_component(vcd, description)
        self.update_or_test_with_w_rel_correlation_method(etd, vcd, update_rules=True, generate_rules=False)
        self.assertEqual(1, len(vcd.w_rel_list[0]))
        for rel in vcd.w_rel_list[0]:
            for r in rel:
                for i in r:
                    key = i
                    value = r[key]
                    if key == 0:
                        self.assertEqual({key: 20}, value)
                    elif key >= 10.0:
                        self.assertEqual({key/2: 5}, value)
                    elif key % 2 == 0:
                        self.assertTrue(value in ({key/2: 5, key: 15}, {key*2: 5, key: 15}))
                    else:
                        self.assertTrue(value in ({key: 15}, {key*2: 5, key: 15}))

        # This part tests if rules are updated when update_rules=False and generate_rules=False. No correlation should be changed.
        description = 'test16VCD3'
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vcd = VariableCorrelationDetector(
            self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.5, used_cor_meth=['WRel'],
            num_init=self.dataset_size, num_update=self.dataset_size, max_dist_rule_distr=0.5)
        self.analysis_context.register_component(vcd, description)
        old_w_rel_list = self.update_or_test_with_w_rel_correlation_method(etd, vcd, update_rules=False, generate_rules=False)
        # no values in the rel_list should be changed.
        self.assertEqual(vcd.w_rel_list[0], old_w_rel_list)

        # This part tests if rules are updated when update_rules=True and generate_rules=False but with an offset of 200. Therefore the
        # assumptions of correlations for the first part should stay the same and no new correlations should be learned, because an offset
        # is added to all data.
        description = 'test16VCD4'
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vcd = VariableCorrelationDetector(
            self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.5, used_cor_meth=['WRel'],
            num_init=self.dataset_size, num_update=self.dataset_size, max_dist_rule_distr=0.5)
        self.analysis_context.register_component(vcd, description)
        offset = 200
        self.update_or_test_with_w_rel_correlation_method(etd, vcd, update_rules=True, generate_rules=False, offset=offset)
        self.assertEqual(1, len(vcd.w_rel_list[0]))
        for rel in vcd.w_rel_list[0]:
            for r in rel:
                for i in r:
                    key = i
                    value = r[key]
                    if key == 0:
                        self.assertTrue(value in ({key: 10}, {key: 10, float(offset): 2}))
                    elif key >= 10.0:
                        self.assertEqual({key / 2: 3}, value)
                    elif key % 2 == 0:
                        self.assertTrue(value in ({key/2: 3, key: 7}, {key*2: 3, key: 7, key*2+offset: 2}))
                    else:
                        self.assertTrue(value in ({key: 7}, {key*2: 3, key: 7, key*2+offset: 2}))

        # This part tests if rules are updated when update_rules=True and generate_rules=True but with an offset of 200. Therefore the
        # assumptions of correlations for the first part should stay the same and new correlations should be learned, because an offset
        # is added to all data.
        description = 'test16VCD5'
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vcd = VariableCorrelationDetector(
            self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.5,
            used_cor_meth=['WRel'], num_init=self.dataset_size, num_update=self.dataset_size, max_dist_rule_distr=0.5)
        self.analysis_context.register_component(vcd, description)
        offset = 200
        self.update_or_test_with_w_rel_correlation_method(etd, vcd, update_rules=True, generate_rules=True, offset=offset)
        self.assertEqual(1, len(vcd.w_rel_list[0]))
        for rel in vcd.w_rel_list[0]:
            for r in rel:
                for i in r:
                    key = i
                    value = r[key]
                    if key == 0:
                        self.assertTrue(value in ({key: 10}, {key: 0, float(offset): 2}))
                    elif key >= 10.0:
                        self.assertTrue(value in ({(key-offset)/2: 2}, {key/2: 3}, {(key-offset)/2: 2, key: 8}, {key: 8}))
                    elif key % 2 == 0:
                        self.assertTrue(value in ({key/2: 3, key: 7}, {key*2: 0, key: 0, key*2+offset: 2}))
                    else:
                        self.assertTrue(value in ({key: 7}, {key*2: 0, key: 0, key*2+offset: 2}))

    def update_or_test_with_w_rel_correlation_method(self, etd, vcd, update_rules, generate_rules, offset=0):
        """
        Run the update or test of w_rel correlations. This method initializes the vcd with a distribution of 70% 0.1 and 30% 0.2.
        In the update phase the distribution is 80% 1 and 20% 2.
        """
        t = time()
        values = []
        # generate the initialization data with child elements being (i % 10) * 1.
        for i in range(70):
            stat_data = bytes(str((i % 10) * 1), 'utf-8')
            values.append(float(stat_data))
            children = [MatchElement(str(0), stat_data.decode(), stat_data, None)]
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('/', stat_data.decode(), stat_data, children)), t,
                               self.__class__.__name__)
            etd.receive_atom(log_atom)
        for i in range(30):
            stat_data = bytes(str((i % 10) * 2), 'utf-8')
            values.append(float(stat_data))
            children = [MatchElement(str(0), stat_data.decode(), stat_data, None)]
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('/', bytes(
                str((i % 10) * 1), 'utf-8').decode(), bytes(str((i % 10) * 1), 'utf-8'), children)), t, self.__class__.__name__)
            etd.receive_atom(log_atom)
        vcd.init_cor(0)
        old_w_rel_list = deepcopy(vcd.w_rel_list[0])
        self.assertEqual(1, len(vcd.w_rel_list[0]))
        for rel in vcd.w_rel_list[0]:
            for r in rel:
                for i in r:
                    key = i
                    value = r[key]
                    if key == 0:
                        self.assertEqual({key: 10}, value)
                    elif key >= 10.0:
                        self.assertEqual({key/2: 3}, value)
                    elif key % 2 == 0:
                        self.assertTrue(value in ({key/2: 3, key: 7}, {key*2: 3, key: 7}))
                    else:
                        self.assertTrue(value in ({key: 7}, {key*2: 3, key: 7}))

        values = []
        for i in range(80):
            stat_data = bytes(str((i % 10) * 1 + offset), 'utf-8')
            values.append(float(stat_data))
            children = [MatchElement(str(0), stat_data.decode(), stat_data, None)]
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('/', stat_data.decode(), stat_data, children)), t,
                               self.__class__.__name__)
            etd.receive_atom(log_atom)
        for i in range(20):
            stat_data = bytes(str((i % 10) * 2 + offset), 'utf-8')
            values.append(float(stat_data))
            children = [MatchElement(str(0), stat_data.decode(), stat_data, None)]
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('/', bytes(
                str((i % 10) * 1), 'utf-8').decode(), bytes(str((i % 10) * 1), 'utf-8'), children)), t, self.__class__.__name__)
            etd.receive_atom(log_atom)
        vcd.log_atom = log_atom
        vcd.update_rules[0] = update_rules
        vcd.generate_rules[0] = generate_rules
        vcd.update_or_test_cor(0)
        return old_w_rel_list

    def test17init_and_update_timings(self):
        """This test checks if the init and update intervals are calculated correctly."""
        description = 'test17VCD1'
        t = time()
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vcd = VariableCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], etd, disc_div_thres=0.5,
                                          num_init=self.dataset_size, num_update=self.dataset_size)
        self.analysis_context.register_component(vcd, description)
        values = []
        for i in range(self.dataset_size):
            stat_data = bytes(str((i % 10) * 0.1), 'utf-8')
            values.append(float(stat_data))
            children = [MatchElement(str(0), stat_data.decode(), stat_data, None)]
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('/', bytes(str((i % 10) * 0.1), 'utf-8').decode(), bytes(
                str((i % 10) * 0.1), 'utf-8'), children)), t, self.__class__.__name__)
            etd.receive_atom(log_atom)
            vcd.receive_atom(log_atom)
            if i < self.dataset_size - 1:
                self.assertEqual(vcd.pos_var_cor, [])
                self.assertEqual(vcd.pos_var_val, [])
                self.assertEqual(vcd.w_rel_list, [])
                self.assertEqual(vcd.rel_list, [])
        # just check if some values were learned and save them to compare.
        self.assertNotEqual(vcd.pos_var_cor, [])
        self.assertNotEqual(vcd.pos_var_val, [])
        self.assertNotEqual(vcd.w_rel_list, [])
        self.assertNotEqual(vcd.rel_list, [])
        old_pos_var_cor = deepcopy(vcd.pos_var_cor)
        old_pos_var_val = deepcopy(vcd.pos_var_val)
        old_w_rel_list = deepcopy(vcd.w_rel_list)
        old_rel_list = deepcopy(vcd.rel_list)

        values = []
        for i in range(self.dataset_size):
            stat_data = bytes(str((i % 10) * 1), 'utf-8')
            values.append(float(stat_data))
            children = [MatchElement(str(0), stat_data.decode(), stat_data, None)]
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('/', bytes(str((i % 10) * 1), 'utf-8').decode(), bytes(
                str((i % 10) * 1), 'utf-8'), children)), t, self.__class__.__name__)
            etd.receive_atom(log_atom)
            vcd.receive_atom(log_atom)
            if i < self.dataset_size - 1:
                self.assertEqual(vcd.pos_var_cor, old_pos_var_cor)
                self.assertEqual(vcd.pos_var_val, old_pos_var_val)
                self.assertEqual(vcd.w_rel_list, old_w_rel_list)
                self.assertEqual(vcd.rel_list, old_rel_list)
        # no new values are expected as num_steps_create_new_rules is False by default.
        self.assertEqual(vcd.pos_var_cor, old_pos_var_cor)
        self.assertEqual(vcd.pos_var_val, old_pos_var_val)
        self.assertNotEqual(vcd.w_rel_list, old_w_rel_list)
        self.assertNotEqual(vcd.rel_list, old_rel_list)
