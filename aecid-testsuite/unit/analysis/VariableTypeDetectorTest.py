from aminer.analysis.EventTypeDetector import EventTypeDetector
from aminer.analysis.VariableTypeDetector import VariableTypeDetector, convert_to_floats, consists_of_ints, consists_of_floats
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from aminer.parsing.MatchElement import MatchElement
from unit.TestBase import TestBase

import sys
import io
import time
import pickle  # skipcq: BAN-B403
import random


class VariableTypeDetectorTest(TestBase):
    """Unittests for the VariableTypeDetector."""

    def test1convert_to_floats(self):
        """This unittest tests possible inputs of the convert_to_floats function."""
        # use a list full of floats
        float_list = [11.123, 12.0, 13.55, 12.11]
        result = convert_to_floats(float_list)
        self.assertEqual(float_list, result, result)

        # use a list containing some floats and integers
        float_int_list = [11.123, 12, 13.55, 12.11, 120]
        result = convert_to_floats(float_int_list)
        self.assertEqual([11.123, 12.0, 13.55, 12.11, 120.0], result, result)

        # use a list of strings with float values
        string_float_list = ['11.123', '12.0', '13.55', b'12.11']
        result = convert_to_floats(string_float_list)
        self.assertEqual(float_list, result, result)

        # use a list of strings with values being no floats
        string_no_float_list = ['11.123', '10:24 AM', '13.55', b'12.11']
        result = convert_to_floats(string_no_float_list)
        self.assertFalse(result)

    def test2consists_of_ints(self):
        """This unittest tests possible inputs of the consists_of_ints function."""
        # use a list full of integers
        int_list = [11, 12, 27, 33, 190]
        self.assertTrue(consists_of_ints(int_list))

        # use a list containing integers and floats
        int_float_list = [11, 12, 27, 33.0, 190]
        self.assertTrue(consists_of_ints(int_float_list))

        # use a list containing integers and floats
        int_float_list = [11, 12, 27, 33.0, 190.2]
        self.assertFalse(consists_of_ints(int_float_list))

        # use a list with integers as strings
        string_int_list = ['11', '12', '27', '33', b'190']
        self.assertFalse(consists_of_ints(string_int_list))

    def test3detect_continuous_shape_fixed_data(self):
        """
        This unittest tests possible continuously distributed variables raising from the detect_continous_shape method.
        It uses fix data sets. Every distribution has generated 20*100 Datasets and var_ev = 0, var_var = 1.
        """
        # Number of execution of the tested function
        iterations = 20
        # Size of the initial datasample
        dataset_size = 100
        # Significance level
        significance_niveau = 0.05

        # load data
        with open('unit/data/vtd_data/uni_data_test3', 'rb') as f:
            [uni_data_list, uni_result_shapes_ks, uni_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open('unit/data/vtd_data/nor_data_test3', 'rb') as f:
            [nor_data_list, nor_result_shapes_ks, nor_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open('unit/data/vtd_data/beta1_data_test3', 'rb') as f:
            [beta1_data_list, beta1_result_shapes_ks, beta1_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open('unit/data/vtd_data/beta2_data_test3', 'rb') as f:
            [beta2_data_list, beta2_result_shapes_ks, beta2_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open('unit/data/vtd_data/beta3_data_test3', 'rb') as f:
            [beta3_data_list, beta3_result_shapes_ks, beta3_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open('unit/data/vtd_data/beta4_data_test3', 'rb') as f:
            [beta4_data_list, beta4_result_shapes_ks, beta4_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open('unit/data/vtd_data/beta5_data_test3', 'rb') as f:
            [beta5_data_list, beta5_result_shapes_ks, beta5_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301

        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd_ks = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=dataset_size,
                                   div_thres=0.5, test_gof_int=True, sim_thres=0.3, gof_alpha=significance_niveau,
                                   used_gof_test='KS')
        vtd_cm = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=dataset_size,
                                   div_thres=0.5, test_gof_int=True, sim_thres=0.3, gof_alpha=significance_niveau,
                                   used_gof_test='CM')

        result_list_ks = []  # List of the results of the single tests
        result_list_cm = []  # List of the results of the single tests
        for i in range(iterations):
            distribution_list = vtd_ks.detect_continuous_shape(uni_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if distribution_list[0] == 'uni' or 'uni' in [distr[0] for distr in distribution_list[-1]]:
                result_list_ks.append(1)
            else:
                result_list_ks.append(0)

            distribution_list = vtd_cm.detect_continuous_shape(uni_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if distribution_list[0] == 'uni' or 'uni' in [distr[0] for distr in distribution_list[-1]]:
                result_list_cm.append(1)
            else:
                result_list_cm.append(0)

        # Test if the result list is correct
        self.assertTrue(result_list_ks == uni_result_shapes_ks)
        self.assertTrue(result_list_cm == uni_result_shapes_cm)

        result_list_ks = []  # List of the results of the single tests
        result_list_cm = []  # List of the results of the single tests
        for i in range(iterations):
            distribution_list = vtd_ks.detect_continuous_shape(nor_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if distribution_list[0] == 'nor' or 'nor' in [distr[0] for distr in distribution_list[-1]]:
                result_list_ks.append(1)
            else:
                result_list_ks.append(0)

            distribution_list = vtd_cm.detect_continuous_shape(nor_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if distribution_list[0] == 'nor' or 'nor' in [distr[0] for distr in distribution_list[-1]]:
                result_list_cm.append(1)
            else:
                result_list_cm.append(0)

        # Test if the result list is correct
        self.assertTrue(result_list_ks == nor_result_shapes_ks)
        self.assertTrue(result_list_cm == nor_result_shapes_cm)

        result_list_ks = []  # List of the results of the single tests
        result_list_cm = []  # List of the results of the single tests
        for i in range(iterations):
            distribution_list = vtd_ks.detect_continuous_shape(beta1_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if (distribution_list[0] == 'beta' and distribution_list[-2] == 1) or 'beta1' in [
                    distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                result_list_ks.append(1)
            else:
                result_list_ks.append(0)

            distribution_list = vtd_cm.detect_continuous_shape(beta1_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if (distribution_list[0] == 'beta' and distribution_list[-2] == 1) or 'beta1' in [
                    distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                result_list_cm.append(1)
            else:
                result_list_cm.append(0)

        # Test if the result list is correct
        self.assertTrue(result_list_ks == beta1_result_shapes_ks)
        self.assertTrue(result_list_cm == beta1_result_shapes_cm)

        result_list_ks = []  # List of the results of the single tests
        result_list_cm = []  # List of the results of the single tests
        for i in range(iterations):
            distribution_list = vtd_ks.detect_continuous_shape(beta2_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if (distribution_list[0] == 'beta' and distribution_list[-2] == 2) or 'beta2' in [
                    distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                result_list_ks.append(1)
            else:
                result_list_ks.append(0)

            distribution_list = vtd_cm.detect_continuous_shape(beta2_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if (distribution_list[0] == 'beta' and distribution_list[-2] == 2) or 'beta2' in [
                    distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                result_list_cm.append(1)
            else:
                result_list_cm.append(0)

        # Test if the result list is correct
        self.assertTrue(result_list_ks == beta2_result_shapes_ks)
        self.assertTrue(result_list_cm == beta2_result_shapes_cm)

        result_list_ks = []  # List of the results of the single tests
        result_list_cm = []  # List of the results of the single tests
        for i in range(iterations):
            distribution_list = vtd_ks.detect_continuous_shape(beta3_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if (distribution_list[0] == 'beta' and distribution_list[-2] == 3) or 'beta3' in [
                    distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                result_list_ks.append(1)
            else:
                result_list_ks.append(0)

            distribution_list = vtd_cm.detect_continuous_shape(beta3_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if (distribution_list[0] == 'beta' and distribution_list[-2] == 3) or 'beta3' in [
                    distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                result_list_cm.append(1)
            else:
                result_list_cm.append(0)

        # Test if the result list is correct
        self.assertTrue(result_list_ks == beta3_result_shapes_ks)
        self.assertTrue(result_list_cm == beta3_result_shapes_cm)

        result_list_ks = []  # List of the results of the single tests
        result_list_cm = []  # List of the results of the single tests
        for i in range(iterations):
            distribution_list = vtd_ks.detect_continuous_shape(beta4_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if (distribution_list[0] == 'beta' and distribution_list[-2] == 4) or 'beta4' in [
                    distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                result_list_ks.append(1)
            else:
                result_list_ks.append(0)

            distribution_list = vtd_cm.detect_continuous_shape(beta4_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if (distribution_list[0] == 'beta' and distribution_list[-2] == 4) or 'beta4' in [
                    distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                result_list_cm.append(1)
            else:
                result_list_cm.append(0)

        # Test if the result list is correct
        self.assertTrue(result_list_ks == beta4_result_shapes_ks)
        self.assertTrue(result_list_cm == beta4_result_shapes_cm)

        result_list_ks = []  # List of the results of the single tests
        result_list_cm = []  # List of the results of the single tests
        for i in range(iterations):
            distribution_list = vtd_ks.detect_continuous_shape(beta5_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if (distribution_list[0] == 'beta' and distribution_list[-2] == 5) or 'beta5' in [
                    distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                result_list_ks.append(1)
            else:
                result_list_ks.append(0)

            distribution_list = vtd_cm.detect_continuous_shape(beta5_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if (distribution_list[0] == 'beta' and distribution_list[-2] == 5) or 'beta5' in [
                    distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                result_list_cm.append(1)
            else:
                result_list_cm.append(0)

        # Test if the result list is correct
        self.assertTrue(result_list_ks == beta5_result_shapes_ks)
        self.assertTrue(result_list_cm == beta5_result_shapes_cm)

    def test4detect_var_type(self):
        """This unittest tests possible scenarios of the detect_var_type method."""
        num_init = 100
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init,
                                   used_gof_test='KS')
        t = time.time()
        # test the 'static' path of detect_var_type
        stat_data = b'5.3.0-55-generic'
        log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
        # check what happens if less than numMinAppearance values are available
        for i in range(num_init):
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(['stat', [stat_data.decode()], False], result)

        # reset etd and vtd for clear results.
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init,
                                   used_gof_test='KS')

        # test ascending with float values
        for i in range(num_init):
            stat_data = bytes(str(i * 0.1), 'utf-8')
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(['asc', 'float'], result)

        # reset etd and vtd for clear results.
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init,
                                   used_gof_test='KS')

        # test ascending with integer values
        for i in range(num_init):
            stat_data = bytes(str(i), 'utf-8')
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(['asc', 'int'], result)

        # reset etd and vtd for clear results.
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init,
                                   used_gof_test='KS')

        # test descending with float values
        for i in range(num_init, 0, -1):
            stat_data = bytes(str(i * 0.1), 'utf-8')
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(['desc', 'float'], result)

        # reset etd and vtd for clear results.
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init,
                                   used_gof_test='KS')

        # test descending with integer values
        for i in range(num_init, 0, -1):
            stat_data = bytes(str(i), 'utf-8')
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(['desc', 'int'], result)

        # reset etd and vtd for clear results.
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init, div_thres=0.3,
                                   test_gof_int=True, used_gof_test='KS')

        # test 'num_init' and 'div_thres'
        # prevent results from becoming asc or desc
        stat_data = bytes(str(99), 'utf-8')
        log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
        etd.receive_atom(log_atom)
        values = [float(stat_data)]
        for i in range(99):
            stat_data = bytes(str(i), 'utf-8')
            values.append(float(stat_data))
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        # this means that the uniformal distribution must be detected.
        self.assertNotEqual(result[0] == 'uni' or 'uni' in [distr[0] for distr in result[-1]], result)

        # test 'divThres' option for the continuous distribution
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init, div_thres=1.0,
                                   test_gof_int=True, used_gof_test='KS')
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(['unq', values], result)

        # test 'testInt' option for the continuous distribution
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init, div_thres=0.3,
                                   test_gof_int=False, used_gof_test='KS')
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(['unq', values], result)

        # test 'simThres' option to result in 'others'
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init, div_thres=0.5,
                                   test_gof_int=False, sim_thres=0.5, used_gof_test='KS')
        values = []
        for i in range(100):
            stat_data = bytes(str((i % 50) * 0.1), 'utf-8')
            values.append(float(stat_data))
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        # at least (1 - 'simThresh') * 'numMinAppearance' and maximal 'numMinAppearance' * 'divThres' - 1 unique values must exist.
        self.assertEqual(['others', 0], result)

        # test discrete result
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init, div_thres=0.5,
                                   test_gof_int=False, sim_thres=0.3, used_gof_test='KS')
        values = []
        for i in range(num_init):
            stat_data = bytes(str((i % 50) * 0.1), 'utf-8')
            values.append(float(stat_data))
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        values_set = list(set(values))
        values_app = [0 for _ in range(len(values_set))]
        for value in values:
            values_app[values_set.index(value)] += 1
        values_app = [x / len(values) for x in values_app]
        self.assertEqual(['d', values_set, values_app, len(values)], result)

    def test5consists_of_floats(self):
        """This unittest tests the consists_of_floats method."""
        # test an empty list
        data_list = []
        self.assertTrue(consists_of_floats(data_list))

        # test a list of integers and floats
        data_list = [10, 11.12, 13, 177, 0.5, 0.]
        self.assertTrue(consists_of_floats(data_list))

        # test a list containing a string
        data_list = [10, 11.12, 13, 177, 0.5, 0., 'dd']
        self.assertFalse(consists_of_floats(data_list))

        # test a list containing bytes
        data_list = [10, 11.12, 13, 177, 0.5, 0., b'x']
        self.assertFalse(consists_of_floats(data_list))

    def test6receive_atom(self):
        """
        This unittest tests if atoms are sorted to the right distribution and if the update steps also work properly.
        Therefore the assumption that after 200 values the VTD with the default parameters can change to the right distribution.
        """
        # load data
        with open('unit/data/vtd_data/nor_data_test6', 'rb') as f:
            nor_data_list = pickle.load(f)  # skipcq: BAN-B301
        with open('unit/data/vtd_data/beta1_data_test6', 'rb') as f:
            beta1_data_list = pickle.load(f)  # skipcq: BAN-B301

        nor_data_list = nor_data_list*10
        beta1_data_list = beta1_data_list*10
        vtd_arguments = [(50, 30), (75, 50), (100, 50), (100, 75), (100, 100)]

        for init, update in vtd_arguments:
            etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
            vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=init, num_update=update,
                                       num_s_gof_values=update, div_thres=0.45, sim_thres=0.75, num_pause_others=0)
            t = time.time()
            stat_data = b'True'
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            # initialize data
            for i in range(init):
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(['stat', [stat_data.decode()], True], result, (init, update, result))

            # static -> static
            for i in range(update):
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(['stat', [stat_data.decode()], True], result, (init, update, result))

            # static -> uni
            for uni_data in [((i+1) % update) / update for i in range(2*update)]:
                log_atom = LogAtom(uni_data, ParserMatch(MatchElement('', uni_data, str(uni_data), None)), t, self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            pos_distr = vtd.alternative_distribution_types[0][0]
            self.assertTrue(result[0] == 'uni' or 'uni' in [distr[0] for distr in pos_distr], (init, update, result))

            # uni -> others
            for i in range(update):
                stat_data = bytes(str((i % int(update / 5))), 'utf-8')
                log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t,
                                   self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(['others', 0], result, (init, update, result))

            # others -> d
            for i in range(update):
                stat_data = bytes(str((i % int(update / 5))), 'utf-8')
                log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t,
                                   self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual('d', result[0], (init, update, result))

            # reset all
            etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
            vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=init, num_update=update,
                                       num_s_gof_values=update, div_thres=0.45, sim_thres=0.75, num_pause_others=0, num_d_bt=30)

            # initialize with d
            for i in range(init):
                stat_data = bytes(str((i % int(update / 5))), 'utf-8')
                log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t,
                                   self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual('d', result[0], (init, update, result))

            # discrete to others with new values
            for uni_data in [i / update for i in range(update)]:
                log_atom = LogAtom(uni_data, ParserMatch(MatchElement('', uni_data, str(uni_data), None)), t, self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(['others', 0], result, (init, update, result))

            # reset all
            etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
            vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=init, num_update=update,
                                       num_s_gof_values=update, div_thres=0.45, sim_thres=0.75, num_pause_others=0, num_d_bt=20)

            # initialize with d
            for i in range(init):
                stat_data = bytes(str((i % int(update / 5))), 'utf-8')
                log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t,
                                   self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual('d', result[0], (init, update, result))

            # discrete to others without new values, low num_d_bt
            for i in range(update):
                stat_data = bytes(str((i % int(update / 20))), 'utf-8')
                log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t,
                                   self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(['others', 0], result, (init, update, result))

            # reset all
            etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
            vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=init, num_update=update,
                                       num_s_gof_values=update, div_thres=0.45, sim_thres=0.75, num_pause_others=0, num_d_bt=100)

            # initialize with d
            for i in range(init):
                stat_data = bytes(str((i % int(update / 5))), 'utf-8')
                log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t,
                                   self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual('d', result[0], (init, update, result))

            # discrete to others without new values, high num_d_bt
            for i in range(update):
                stat_data = bytes(str((i % int(update / 20))), 'utf-8')
                log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t,
                                   self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertNotEqual(['others', 0], result, (init, update, result))

            # reset all
            etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
            vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=init, num_update=update,
                                       num_s_gof_values=update, div_thres=0.45, sim_thres=0.75, num_pause_others=0)
            t = time.time()
            stat_data = b'True'
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            # initialize data
            for i in range(init):
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(['stat', [stat_data.decode()], True], result, (init, update, result))

            # static -> asc
            for i in range(2*update):
                stat_data = bytes(str(i * 0.1), 'utf-8')
                log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t,
                                   self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(['asc', 'float'], result, (init, update, result))

            # asc -> desc
            for i in range(2*update, 0, -1):
                stat_data = bytes(str(i * 0.1), 'utf-8')
                log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t,
                                   self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(['desc', 'float'], result, (init, update, result))

            # reset all
            etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
            vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=init, num_update=update,
                                       num_s_gof_values=update, div_thres=0.45, sim_thres=0.75, num_pause_others=0)
            t = time.time()
            stat_data = b'True'
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            # initialize data
            for i in range(init):
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(['stat', [stat_data.decode()], True], result, (init, update, result))

            # static -> nor
            for nor_data in nor_data_list[:2*update]:
                log_atom = LogAtom(nor_data, ParserMatch(MatchElement('', nor_data, str(nor_data), None)), t, self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            pos_distr = vtd.alternative_distribution_types[0][0]
            self.assertTrue(result[0] == 'nor' or 'nor' in [distr[0] for distr in pos_distr], (init, update, result))

            # nor -> beta1
            for beta1_data in beta1_data_list[:2*update]:
                log_atom = LogAtom(beta1_data, ParserMatch(MatchElement('', beta1_data, str(beta1_data), None)), t, self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            pos_distr = vtd.alternative_distribution_types[0][0]
            self.assertTrue((result[0] == 'beta' and result[-1] == 1) or 'beta1' in [distr[0]+str(distr[-1]) for distr in pos_distr],
                            (init, update, result))

            # reset all
            etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
            vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=init, num_update=update,
                                       num_s_gof_values=update, div_thres=0.45, sim_thres=0.75, num_pause_others=0)
            t = time.time()
            stat_data = b'True'
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement('', stat_data.decode(), stat_data, None)), t, self.__class__.__name__)
            # initialize data
            for i in range(init):
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(['stat', [stat_data.decode()], True], result, (init, update, result))

            # static -> unq
            vtd.test_gof_int = False
            unq_data_list = [bytes(str(i), 'utf-8') for i in range(2*update)]
            random.shuffle(unq_data_list)
            for unq_data in unq_data_list:
                log_atom = LogAtom(unq_data, ParserMatch(MatchElement('', unq_data, unq_data, None)), t, self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual('unq', result[0], (init, update, result))

    def test7update_continuous_VT(self):
        """
        This unittest tests the s_gof_test method. It uses randomised datasets, which can be printed in the terminal.
        Every distribution has generated 30*300 Datasets and var_ev = 0, var_var = 1.
        """
        # Number of execution of the tested function
        iterations = 20
        # Size of the initial datasample
        dataset_size_ini = 100
        # Size of the update datasample
        dataset_size_upd = 50
        # Significance level
        significance_niveau = 0.05

        # load data
        with open('unit/data/vtd_data/uni_data_test7', 'rb') as f:
            [uni_data_list_ini, uni_data_list_upd, uni_result_shapes_ks, uni_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open('unit/data/vtd_data/nor_data_test7', 'rb') as f:
            [nor_data_list_ini, nor_data_list_upd, nor_result_shapes_ks, nor_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open('unit/data/vtd_data/beta1_data_test7', 'rb') as f:
            [beta1_data_list_ini, beta1_data_list_upd, beta1_result_shapes_ks, beta1_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open('unit/data/vtd_data/beta2_data_test7', 'rb') as f:
            [beta2_data_list_ini, beta2_data_list_upd, beta2_result_shapes_ks, beta2_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open('unit/data/vtd_data/beta3_data_test7', 'rb') as f:
            [beta3_data_list_ini, beta3_data_list_upd, beta3_result_shapes_ks, beta3_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open('unit/data/vtd_data/beta4_data_test7', 'rb') as f:
            [beta4_data_list_ini, beta4_data_list_upd, beta4_result_shapes_ks, beta4_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open('unit/data/vtd_data/beta5_data_test7', 'rb') as f:
            [beta5_data_list_ini, beta5_data_list_upd, beta5_result_shapes_ks, beta5_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301

        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd_ks = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=dataset_size_ini,
                                   num_update=dataset_size_upd, gof_alpha=significance_niveau, used_gof_test='KS')
        vtd_cm = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=dataset_size_ini,
                                   num_update=dataset_size_upd, gof_alpha=significance_niveau, used_gof_test='CM')

        result_list_ks = []  # List of the results of the single tests
        result_list_cm = []  # List of the results of the single tests
        for i in range(iterations):
            # Create the initial distribution, which has to pass the initial test
            variable_type_ini = vtd_ks.detect_continuous_shape(uni_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == 'uni':
                variable_type_ini = variable_type_ini[:-1]
            elif 'uni' in [distr[0] for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == 'uni':
                        variable_type_ini = distr
            else:
                variable_type_ini = ['others', 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[uni_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_ks.var_type = [[variable_type_ini]]
            result_list_ks.append(vtd_ks.s_gof_test(0, 0, True)[0])

            variable_type_ini = vtd_cm.detect_continuous_shape(uni_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == 'uni':
                variable_type_ini = variable_type_ini[:-1]
            elif 'uni' in [distr[0] for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == 'uni':
                        variable_type_ini = distr
            else:
                variable_type_ini = ['others', 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[uni_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_cm.var_type = [[variable_type_ini]]
            result_list_cm.append(vtd_cm.s_gof_test(0, 0, True)[0])

        # Test if the result list is correct
        self.assertTrue(result_list_ks == uni_result_shapes_ks)
        self.assertTrue(result_list_cm == uni_result_shapes_cm)

        result_list_ks = []  # List of the results of the single tests
        result_list_cm = []  # List of the results of the single tests
        for i in range(iterations):
            # Create the initial distribution, which has to pass the initial test
            variable_type_ini = vtd_ks.detect_continuous_shape(nor_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == 'nor':
                variable_type_ini = variable_type_ini[:-1]
            elif 'nor' in [distr[0] for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == 'nor':
                        variable_type_ini = distr
            else:
                variable_type_ini = ['others', 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[nor_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_ks.var_type = [[variable_type_ini]]
            result_list_ks.append(vtd_ks.s_gof_test(0, 0, True)[0])

            variable_type_ini = vtd_cm.detect_continuous_shape(nor_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == 'nor':
                variable_type_ini = variable_type_ini[:-1]
            elif 'nor' in [distr[0] for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == 'nor':
                        variable_type_ini = distr
            else:
                variable_type_ini = ['others', 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[nor_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_cm.var_type = [[variable_type_ini]]
            result_list_cm.append(vtd_cm.s_gof_test(0, 0, True)[0])

        # Test if the result list is correct
        self.assertTrue(result_list_ks == nor_result_shapes_ks)
        self.assertTrue(result_list_cm == nor_result_shapes_cm)

        result_list_ks = []  # List of the results of the single tests
        result_list_cm = []  # List of the results of the single tests
        for i in range(iterations):
            # Create the initial distribution, which has to pass the initial test
            variable_type_ini = vtd_ks.detect_continuous_shape(beta1_data_list_ini[
                i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == 'beta' and variable_type_ini[-2] == 1:
                variable_type_ini = variable_type_ini[:-1]
            elif 'beta1' in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == 'beta' and distr[-1] == 1:
                        variable_type_ini = distr
            else:
                variable_type_ini = ['others', 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[beta1_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_ks.var_type = [[variable_type_ini]]
            result_list_ks.append(vtd_ks.s_gof_test(0, 0, True)[0])

            variable_type_ini = vtd_cm.detect_continuous_shape(beta1_data_list_ini[
                i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == 'beta' and variable_type_ini[-2] == 1:
                variable_type_ini = variable_type_ini[:-1]
            elif 'beta1' in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == 'beta' and distr[-1] == 1:
                        variable_type_ini = distr
            else:
                variable_type_ini = ['others', 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[beta1_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_cm.var_type = [[variable_type_ini]]
            result_list_cm.append(vtd_cm.s_gof_test(0, 0, True)[0])

        # Test if the result list is correct
        self.assertTrue(result_list_ks == beta1_result_shapes_ks)
        self.assertTrue(result_list_cm == beta1_result_shapes_cm)

        result_list_ks = []  # List of the results of the single tests
        result_list_cm = []  # List of the results of the single tests
        for i in range(iterations):
            # Create the initial distribution, which has to pass the initial test
            variable_type_ini = vtd_ks.detect_continuous_shape(beta2_data_list_ini[
                i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == 'beta' and variable_type_ini[-2] == 2:
                variable_type_ini = variable_type_ini[:-1]
            elif 'beta2' in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == 'beta' and distr[-1] == 2:
                        variable_type_ini = distr
            else:
                variable_type_ini = ['others', 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[beta2_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_ks.var_type = [[variable_type_ini]]
            result_list_ks.append(vtd_ks.s_gof_test(0, 0, True)[0])

            variable_type_ini = vtd_cm.detect_continuous_shape(beta2_data_list_ini[
                i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == 'beta' and variable_type_ini[-2] == 2:
                variable_type_ini = variable_type_ini[:-1]
            elif 'beta2' in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == 'beta' and distr[-1] == 2:
                        variable_type_ini = distr
            else:
                variable_type_ini = ['others', 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[beta2_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_cm.var_type = [[variable_type_ini]]
            result_list_cm.append(vtd_cm.s_gof_test(0, 0, True)[0])

        # Test if the result list is correct
        self.assertTrue(result_list_ks == beta2_result_shapes_ks)
        self.assertTrue(result_list_cm == beta2_result_shapes_cm)

        result_list_ks = []  # List of the results of the single tests
        result_list_cm = []  # List of the results of the single tests
        for i in range(iterations):
            # Create the initial distribution, which has to pass the initial test
            variable_type_ini = vtd_ks.detect_continuous_shape(beta3_data_list_ini[
                i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == 'beta' and variable_type_ini[-2] == 3:
                variable_type_ini = variable_type_ini[:-1]
            elif 'beta3' in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == 'beta' and distr[-1] == 3:
                        variable_type_ini = distr
            else:
                variable_type_ini = ['others', 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[beta3_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_ks.var_type = [[variable_type_ini]]
            result_list_ks.append(vtd_ks.s_gof_test(0, 0, True)[0])

            variable_type_ini = vtd_cm.detect_continuous_shape(beta3_data_list_ini[
                i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == 'beta' and variable_type_ini[-2] == 3:
                variable_type_ini = variable_type_ini[:-1]
            elif 'beta3' in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == 'beta' and distr[-1] == 3:
                        variable_type_ini = distr
            else:
                variable_type_ini = ['others', 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[beta3_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_cm.var_type = [[variable_type_ini]]
            result_list_cm.append(vtd_cm.s_gof_test(0, 0, True)[0])

        # Test if the result list is correct
        self.assertTrue(result_list_ks == beta3_result_shapes_ks)
        self.assertTrue(result_list_cm == beta3_result_shapes_cm)

        result_list_ks = []  # List of the results of the single tests
        result_list_cm = []  # List of the results of the single tests
        for i in range(iterations):
            # Create the initial distribution, which has to pass the initial test
            variable_type_ini = vtd_ks.detect_continuous_shape(beta4_data_list_ini[
                i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == 'beta' and variable_type_ini[-2] == 4:
                variable_type_ini = variable_type_ini[:-1]
            elif 'beta4' in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == 'beta' and distr[-1] == 4:
                        variable_type_ini = distr
            else:
                variable_type_ini = ['others', 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[beta4_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_ks.var_type = [[variable_type_ini]]
            result_list_ks.append(vtd_ks.s_gof_test(0, 0, True)[0])

            variable_type_ini = vtd_cm.detect_continuous_shape(beta4_data_list_ini[
                i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == 'beta' and variable_type_ini[-2] == 4:
                variable_type_ini = variable_type_ini[:-1]
            elif 'beta4' in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == 'beta' and distr[-1] == 4:
                        variable_type_ini = distr
            else:
                variable_type_ini = ['others', 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[beta4_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_cm.var_type = [[variable_type_ini]]
            result_list_cm.append(vtd_cm.s_gof_test(0, 0, True)[0])

        # Test if the result list is correct
        self.assertTrue(result_list_ks == beta4_result_shapes_ks)
        self.assertTrue(result_list_cm == beta4_result_shapes_cm)

        result_list_ks = []  # List of the results of the single tests
        result_list_cm = []  # List of the results of the single tests
        for i in range(iterations):
            # Create the initial distribution, which has to pass the initial test
            variable_type_ini = vtd_ks.detect_continuous_shape(beta5_data_list_ini[
                i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == 'beta' and variable_type_ini[-2] == 5:
                variable_type_ini = variable_type_ini[:-1]
            elif 'beta5' in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == 'beta' and distr[-1] == 5:
                        variable_type_ini = distr
            else:
                variable_type_ini = ['others', 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[beta5_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_ks.var_type = [[variable_type_ini]]
            result_list_ks.append(vtd_ks.s_gof_test(0, 0, True)[0])

            variable_type_ini = vtd_cm.detect_continuous_shape(beta5_data_list_ini[
                i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == 'beta' and variable_type_ini[-2] == 5:
                variable_type_ini = variable_type_ini[:-1]
            elif 'beta5' in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == 'beta' and distr[-1] == 5:
                        variable_type_ini = distr
            else:
                variable_type_ini = ['others', 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[beta5_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_cm.var_type = [[variable_type_ini]]
            result_list_cm.append(vtd_cm.s_gof_test(0, 0, True)[0])

        # Test if the result list is correct
        self.assertTrue(result_list_ks == beta5_result_shapes_ks)
        self.assertTrue(result_list_cm == beta5_result_shapes_cm)
