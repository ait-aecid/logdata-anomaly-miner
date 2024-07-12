from aminer.analysis.EventTypeDetector import EventTypeDetector
from aminer.analysis.VariableTypeDetector import VariableTypeDetector, convert_to_floats, consists_of_ints, consists_of_floats
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from aminer.parsing.MatchElement import MatchElement
from unit.TestBase import TestBase
from aminer.AminerConfig import DEFAULT_PERSISTENCE_PERIOD

import time
import pickle  # skipcq: BAN-B403
import random


class VariableTypeDetectorTest(TestBase):
    """Unittests for the VariableTypeDetector."""

    path = "path"

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
        string_float_list = ["11.123", "12.0", "13.55", b"12.11"]
        result = convert_to_floats(string_float_list)
        self.assertEqual(float_list, result, result)

        # use a list of strings with values being no floats
        string_no_float_list = ["11.123", "10:24 AM", "13.55", b"12.11"]
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
        string_int_list = ["11", "12", "27", "33", b"190"]
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
        with open("unit/data/vtd_data/uni_data_test3", "rb") as f:
            [uni_data_list, uni_result_shapes_ks, uni_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open("unit/data/vtd_data/nor_data_test3", "rb") as f:
            [nor_data_list, nor_result_shapes_ks, nor_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open("unit/data/vtd_data/beta1_data_test3", "rb") as f:
            [beta1_data_list, beta1_result_shapes_ks, beta1_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open("unit/data/vtd_data/beta2_data_test3", "rb") as f:
            [beta2_data_list, beta2_result_shapes_ks, beta2_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open("unit/data/vtd_data/beta3_data_test3", "rb") as f:
            [beta3_data_list, beta3_result_shapes_ks, beta3_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open("unit/data/vtd_data/beta4_data_test3", "rb") as f:
            [beta4_data_list, beta4_result_shapes_ks, beta4_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open("unit/data/vtd_data/beta5_data_test3", "rb") as f:
            [beta5_data_list, beta5_result_shapes_ks, beta5_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301

        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd_ks = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=dataset_size,
                                      div_thres=0.5, test_gof_int=True, sim_thres=0.3, gof_alpha=significance_niveau,
                                      used_gof_test="KS")
        vtd_cm = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=dataset_size,
                                      div_thres=0.5, test_gof_int=True, sim_thres=0.3, gof_alpha=significance_niveau,
                                      used_gof_test="CM")

        result_list_ks = []  # List of the results of the single tests
        result_list_cm = []  # List of the results of the single tests
        for i in range(iterations):
            distribution_list = vtd_ks.detect_continuous_shape(uni_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if distribution_list[0] == "uni" or "uni" in [distr[0] for distr in distribution_list[-1]]:
                result_list_ks.append(1)
            else:
                result_list_ks.append(0)

            distribution_list = vtd_cm.detect_continuous_shape(uni_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if distribution_list[0] == "uni" or "uni" in [distr[0] for distr in distribution_list[-1]]:
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
            if distribution_list[0] == "nor" or "nor" in [distr[0] for distr in distribution_list[-1]]:
                result_list_ks.append(1)
            else:
                result_list_ks.append(0)

            distribution_list = vtd_cm.detect_continuous_shape(nor_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if distribution_list[0] == "nor" or "nor" in [distr[0] for distr in distribution_list[-1]]:
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
            if (distribution_list[0] == "beta" and distribution_list[-2] == 1) or "beta1" in [
                    distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                result_list_ks.append(1)
            else:
                result_list_ks.append(0)

            distribution_list = vtd_cm.detect_continuous_shape(beta1_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if (distribution_list[0] == "beta" and distribution_list[-2] == 1) or "beta1" in [
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
            if (distribution_list[0] == "beta" and distribution_list[-2] == 2) or "beta2" in [
                    distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                result_list_ks.append(1)
            else:
                result_list_ks.append(0)

            distribution_list = vtd_cm.detect_continuous_shape(beta2_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if (distribution_list[0] == "beta" and distribution_list[-2] == 2) or "beta2" in [
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
            if (distribution_list[0] == "beta" and distribution_list[-2] == 3) or "beta3" in [
                    distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                result_list_ks.append(1)
            else:
                result_list_ks.append(0)

            distribution_list = vtd_cm.detect_continuous_shape(beta3_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if (distribution_list[0] == "beta" and distribution_list[-2] == 3) or "beta3" in [
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
            if (distribution_list[0] == "beta" and distribution_list[-2] == 4) or "beta4" in [
                    distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                result_list_ks.append(1)
            else:
                result_list_ks.append(0)

            distribution_list = vtd_cm.detect_continuous_shape(beta4_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if (distribution_list[0] == "beta" and distribution_list[-2] == 4) or "beta4" in [
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
            if (distribution_list[0] == "beta" and distribution_list[-2] == 5) or "beta5" in [
                    distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                result_list_ks.append(1)
            else:
                result_list_ks.append(0)

            distribution_list = vtd_cm.detect_continuous_shape(beta5_data_list[i * dataset_size:(i + 1) * dataset_size])

            # Add if the searched distribution is present in the found distributions
            if (distribution_list[0] == "beta" and distribution_list[-2] == 5) or "beta5" in [
                    distr[0]+str(distr[-1]) for distr in distribution_list[-1]]:
                result_list_cm.append(1)
            else:
                result_list_cm.append(0)

        # Test if the result list is correct
        self.assertTrue(result_list_ks == beta5_result_shapes_ks)
        self.assertTrue(result_list_cm == beta5_result_shapes_cm)

    def test4detect_var_type(self):
        """This unittest tests possible scenarios of the detect_var_type method."""
        # Load list of an uniformal distributed sample which consists of integers
        with open("unit/data/vtd_data/uni_data_test4", "rb") as f:
            uni_data_list_int = pickle.load(f)  # skipcq: BAN-B301

        num_init = 100
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init,
                                   used_gof_test="KS")
        t = time.time()
        # test the "static" path of detect_var_type
        stat_data = b"5.3.0-55-generic"
        log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
        # check what happens if less than numMinAppearance values are available
        for i in range(num_init):
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(["stat", [stat_data.decode()], False], result)

        # reset etd and vtd for clear results.
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init,
                                   used_gof_test="KS")

        # test ascending with float values
        for i in range(num_init):
            stat_data = bytes(str(i * 0.1), "utf-8")
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(["asc", "float"], result)

        # reset etd and vtd for clear results.
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init,
                                   used_gof_test="KS")

        # test ascending with integer values
        for i in range(num_init):
            stat_data = bytes(str(i), "utf-8")
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(["asc", "int"], result)

        # reset etd and vtd for clear results.
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init,
                                   used_gof_test="KS")

        # test descending with float values
        for i in range(num_init, 0, -1):
            stat_data = bytes(str(i * 0.1), "utf-8")
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(["desc", "float"], result)

        # reset etd and vtd for clear results.
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init,
                                   used_gof_test="KS")

        # test descending with integer values
        for i in range(num_init, 0, -1):
            stat_data = bytes(str(i), "utf-8")
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(["desc", "int"], result)

        # reset etd and vtd for clear results.
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init, div_thres=0.3,
                                   test_gof_int=True, used_gof_test="KS")

        # test "num_init" and "div_thres"
        values = []
        for i in range(num_init):
            stat_data = bytes(str(uni_data_list_int[i]), "utf-8")
            values.append(float(stat_data))
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        # this means that the uniformal distribution must be detected.

        self.assertTrue(result[0] == "uni" or (isinstance(result[-1], list) and "uni" in [distr[0] for distr in result[-1]]), result)

        # test "divThres" option for the continuous distribution
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init, div_thres=1.0,
                                   test_gof_int=True, used_gof_test="KS")
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(["unq", values], result)

        # test "testInt" option for the continuous distribution
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init, div_thres=0.3,
                                   test_gof_int=False, used_gof_test="KS")
        result = vtd.detect_var_type(0, 0)
        self.assertEqual(["unq", values], result)

        # test "simThres" option to result in "others"
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init, div_thres=0.5,
                                   test_gof_int=False, sim_thres=0.5, used_gof_test="KS")
        values = []
        for i in range(100):
            stat_data = bytes(str((i % 50) * 0.1), "utf-8")
            values.append(float(stat_data))
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        # at least (1 - "simThresh") * "numMinAppearance" and maximal "numMinAppearance" * "divThres" - 1 unique values must exist.
        self.assertEqual(["others", 0], result)

        # test discrete result
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=num_init, div_thres=0.5,
                                   test_gof_int=False, sim_thres=0.3, used_gof_test="KS")
        values = []
        for i in range(num_init):
            stat_data = bytes(str((i % 50) * 0.1), "utf-8")
            values.append(float(stat_data))
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
        result = vtd.detect_var_type(0, 0)
        values_set = list(set(values))
        values_app = [0 for _ in range(len(values_set))]
        for value in values:
            values_app[values_set.index(value)] += 1
        values_app = [x / len(values) for x in values_app]
        self.assertEqual(["d", values_set, values_app, len(values)], result)

    def test5consists_of_floats(self):
        """This unittest tests the consists_of_floats method."""
        # test an empty list
        data_list = []
        self.assertTrue(consists_of_floats(data_list))

        # test a list of integers and floats
        data_list = [10, 11.12, 13, 177, 0.5, 0.]
        self.assertTrue(consists_of_floats(data_list))

        # test a list containing a string
        data_list = [10, 11.12, 13, 177, 0.5, 0., "dd"]
        self.assertFalse(consists_of_floats(data_list))

        # test a list containing bytes
        data_list = [10, 11.12, 13, 177, 0.5, 0., b"x"]
        self.assertFalse(consists_of_floats(data_list))

    def test6receive_atom(self):
        """
        This unittest tests if atoms are sorted to the right distribution and if the update steps also work properly.
        Therefore, the assumption that after 200 values the VTD with the default parameters can change to the right distribution.
        """
        # load data
        with open("unit/data/vtd_data/nor_data_test6", "rb") as f:
            nor_data_list = pickle.load(f)  # skipcq: BAN-B301
        with open("unit/data/vtd_data/beta1_data_test6", "rb") as f:
            beta1_data_list = pickle.load(f)  # skipcq: BAN-B301
        with open("unit/data/vtd_data/uni_data_test6", "rb") as f:
            uni_data_list = pickle.load(f)  # skipcq: BAN-B301

        nor_data_list = nor_data_list*10
        beta1_data_list = beta1_data_list*10
        vtd_arguments = [(50, 30), (75, 50), (100, 50), (100, 75), (100, 100)]

        for init, update in vtd_arguments:
            etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
            vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=init, num_update=update,
                                       num_s_gof_values=update, div_thres=0.45, sim_thres=0.75, num_pause_others=0)
            t = time.time()
            stat_data = b"True"
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
            # initialize data
            for i in range(init):
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(["stat", [stat_data.decode()], True], result, (init, update, result))

            # static -> static
            for i in range(update):
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(["stat", [stat_data.decode()], True], result, (init, update, result))

            # static -> uni
            for uni_data in uni_data_list[2*update:4*update]:
                log_atom = LogAtom(uni_data, ParserMatch(MatchElement(self.path, str(uni_data).encode(), str(uni_data), None)), t,
                                   self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            pos_distr = vtd.alternative_distribution_types[0][0]
            self.assertTrue(result[0] == "uni" or "uni" in [distr[0] for distr in pos_distr], (init, update, result))

            # uni -> others
            for i in range(update):
                stat_data = bytes(str((i % int(update / 5))), "utf-8")
                log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(["others", 0], result, (init, update, result))

            # others -> d
            for i in range(update):
                stat_data = bytes(str((i % int(update / 5))), "utf-8")
                log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual("d", result[0], (init, update, result))

            # reset all
            etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
            vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=init, num_update=update,
                                       num_s_gof_values=update, div_thres=0.45, sim_thres=0.75, num_pause_others=0, num_d_bt=30)

            # initialize with d
            for i in range(init):
                stat_data = bytes(str((i % int(update / 5))), "utf-8")
                log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual("d", result[0], (init, update, result))

            # discrete to others with new values
            for uni_data in [i / update for i in range(update)]:
                log_atom = LogAtom(uni_data, ParserMatch(MatchElement(self.path, str(uni_data).encode(), str(uni_data), None)), t,
                                   self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(["others", 0], result, (init, update, result))

            # reset all
            etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
            vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=init, num_update=update,
                                       num_s_gof_values=update, div_thres=0.45, sim_thres=0.75, num_pause_others=0, num_d_bt=20)

            # initialize with d
            for i in range(init):
                stat_data = bytes(str((i % int(update / 5))), "utf-8")
                log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual("d", result[0], (init, update, result))

            # discrete to others without new values, low num_d_bt
            for i in range(update):
                stat_data = bytes(str((i % int(update / 20))), "utf-8")
                log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(["others", 0], result, (init, update, result))

            # reset all
            etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
            vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=init, num_update=update,
                                       num_s_gof_values=update, div_thres=0.45, sim_thres=0.75, num_pause_others=0, num_d_bt=100)

            # initialize with d
            for i in range(init):
                stat_data = bytes(str((i % int(update / 5))), "utf-8")
                log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual("d", result[0], (init, update, result))

            # discrete to others without new values, high num_d_bt
            for i in range(update):
                stat_data = bytes(str((i % int(update / 20))), "utf-8")
                log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertNotEqual(["others", 0], result, (init, update, result))

            # reset all
            etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
            vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=init, num_update=update,
                                       num_s_gof_values=update, div_thres=0.45, sim_thres=0.75, num_pause_others=0)
            t = time.time()
            stat_data = b"True"
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
            # initialize data
            for i in range(init):
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(["stat", [stat_data.decode()], True], result, (init, update, result))

            # static -> asc
            for i in range(2*update):
                stat_data = bytes(str(i * 0.1), "utf-8")
                log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(["asc", "float"], result, (init, update, result))

            # asc -> desc
            for i in range(2*update, 0, -1):
                stat_data = bytes(str(i * 0.1), "utf-8")
                log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(["desc", "float"], result, (init, update, result))

            # reset all
            etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
            vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=init, num_update=update,
                                       num_s_gof_values=update, div_thres=0.45, sim_thres=0.75, num_pause_others=0)
            t = time.time()
            stat_data = b"True"
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
            # initialize data
            for i in range(init):
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(["stat", [stat_data.decode()], True], result, (init, update, result))

            # static -> nor
            for nor_data in nor_data_list[update:3*update]:
                log_atom = LogAtom(nor_data, ParserMatch(MatchElement(self.path, str(nor_data).encode(), str(nor_data), None)), t,
                                   self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            pos_distr = vtd.alternative_distribution_types[0][0]
            self.assertTrue(result[0] == "nor" or "nor" in [distr[0] for distr in pos_distr], (init, update, result))

            # nor -> beta1
            for beta1_data in beta1_data_list[:2*update]:
                log_atom = LogAtom(beta1_data, ParserMatch(MatchElement(self.path, str(beta1_data).encode(), str(beta1_data), None)), t,
                                   self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            pos_distr = vtd.alternative_distribution_types[0][0]
            self.assertTrue((result[0] == "beta" and result[-1] == 1) or "beta1" in [distr[0]+str(distr[-1]) for distr in pos_distr],
                            (init, update, result))

            # reset all
            etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
            vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=init, num_update=update,
                                       num_s_gof_values=update, div_thres=0.45, sim_thres=0.75, num_pause_others=0)
            t = time.time()
            stat_data = b"True"
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t,
                               self.__class__.__name__)
            # initialize data
            for i in range(init):
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual(["stat", [stat_data.decode()], True], result, (init, update, result))

            # static -> unq
            vtd.test_gof_int = False
            unq_data_list = [bytes(str(i), "utf-8") for i in range(2*update)]
            random.shuffle(unq_data_list)
            for unq_data in unq_data_list:
                log_atom = LogAtom(unq_data, ParserMatch(MatchElement(self.path, unq_data, unq_data, None)), t, self.__class__.__name__)
                self.assertTrue(etd.receive_atom(log_atom))
                vtd.receive_atom(log_atom)
            result = vtd.var_type[0][0]
            self.assertEqual("unq", result[0], (init, update, result))

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
        with open("unit/data/vtd_data/uni_data_test7", "rb") as f:
            [uni_data_list_ini, uni_data_list_upd, uni_result_shapes_ks, uni_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open("unit/data/vtd_data/nor_data_test7", "rb") as f:
            [nor_data_list_ini, nor_data_list_upd, nor_result_shapes_ks, nor_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open("unit/data/vtd_data/beta1_data_test7", "rb") as f:
            [beta1_data_list_ini, beta1_data_list_upd, beta1_result_shapes_ks, beta1_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open("unit/data/vtd_data/beta2_data_test7", "rb") as f:
            [beta2_data_list_ini, beta2_data_list_upd, beta2_result_shapes_ks, beta2_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open("unit/data/vtd_data/beta3_data_test7", "rb") as f:
            [beta3_data_list_ini, beta3_data_list_upd, beta3_result_shapes_ks, beta3_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open("unit/data/vtd_data/beta4_data_test7", "rb") as f:
            [beta4_data_list_ini, beta4_data_list_upd, beta4_result_shapes_ks, beta4_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301
        with open("unit/data/vtd_data/beta5_data_test7", "rb") as f:
            [beta5_data_list_ini, beta5_data_list_upd, beta5_result_shapes_ks, beta5_result_shapes_cm] = pickle.load(f)  # skipcq: BAN-B301

        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd_ks = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=dataset_size_ini,
                                      num_update=dataset_size_upd, gof_alpha=significance_niveau, used_gof_test="KS")
        vtd_cm = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=dataset_size_ini,
                                      num_update=dataset_size_upd, gof_alpha=significance_niveau, used_gof_test="CM")

        result_list_ks = []  # List of the results of the single tests
        result_list_cm = []  # List of the results of the single tests
        for i in range(iterations):
            # Create the initial distribution, which has to pass the initial test
            variable_type_ini = vtd_ks.detect_continuous_shape(uni_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == "uni":
                variable_type_ini = variable_type_ini[:-1]
            elif "uni" in [distr[0] for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == "uni":
                        variable_type_ini = distr
            else:
                variable_type_ini = ["others", 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[uni_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_ks.var_type = [[variable_type_ini]]
            result_list_ks.append(vtd_ks.s_gof_test(0, 0, True)[0])

            variable_type_ini = vtd_cm.detect_continuous_shape(uni_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == "uni":
                variable_type_ini = variable_type_ini[:-1]
            elif "uni" in [distr[0] for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == "uni":
                        variable_type_ini = distr
            else:
                variable_type_ini = ["others", 0]

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
            if variable_type_ini[0] == "nor":
                variable_type_ini = variable_type_ini[:-1]
            elif "nor" in [distr[0] for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == "nor":
                        variable_type_ini = distr
            else:
                variable_type_ini = ["others", 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[nor_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_ks.var_type = [[variable_type_ini]]
            result_list_ks.append(vtd_ks.s_gof_test(0, 0, True)[0])

            variable_type_ini = vtd_cm.detect_continuous_shape(nor_data_list_ini[i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == "nor":
                variable_type_ini = variable_type_ini[:-1]
            elif "nor" in [distr[0] for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == "nor":
                        variable_type_ini = distr
            else:
                variable_type_ini = ["others", 0]

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
            if variable_type_ini[0] == "beta" and variable_type_ini[-2] == 1:
                variable_type_ini = variable_type_ini[:-1]
            elif "beta1" in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == "beta" and distr[-1] == 1:
                        variable_type_ini = distr
            else:
                variable_type_ini = ["others", 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[beta1_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_ks.var_type = [[variable_type_ini]]
            result_list_ks.append(vtd_ks.s_gof_test(0, 0, True)[0])

            variable_type_ini = vtd_cm.detect_continuous_shape(beta1_data_list_ini[
                i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == "beta" and variable_type_ini[-2] == 1:
                variable_type_ini = variable_type_ini[:-1]
            elif "beta1" in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == "beta" and distr[-1] == 1:
                        variable_type_ini = distr
            else:
                variable_type_ini = ["others", 0]

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
            if variable_type_ini[0] == "beta" and variable_type_ini[-2] == 2:
                variable_type_ini = variable_type_ini[:-1]
            elif "beta2" in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == "beta" and distr[-1] == 2:
                        variable_type_ini = distr
            else:
                variable_type_ini = ["others", 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[beta2_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_ks.var_type = [[variable_type_ini]]
            result_list_ks.append(vtd_ks.s_gof_test(0, 0, True)[0])

            variable_type_ini = vtd_cm.detect_continuous_shape(beta2_data_list_ini[
                i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == "beta" and variable_type_ini[-2] == 2:
                variable_type_ini = variable_type_ini[:-1]
            elif "beta2" in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == "beta" and distr[-1] == 2:
                        variable_type_ini = distr
            else:
                variable_type_ini = ["others", 0]

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
            if variable_type_ini[0] == "beta" and variable_type_ini[-2] == 3:
                variable_type_ini = variable_type_ini[:-1]
            elif "beta3" in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == "beta" and distr[-1] == 3:
                        variable_type_ini = distr
            else:
                variable_type_ini = ["others", 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[beta3_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_ks.var_type = [[variable_type_ini]]
            result_list_ks.append(vtd_ks.s_gof_test(0, 0, True)[0])

            variable_type_ini = vtd_cm.detect_continuous_shape(beta3_data_list_ini[
                i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == "beta" and variable_type_ini[-2] == 3:
                variable_type_ini = variable_type_ini[:-1]
            elif "beta3" in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == "beta" and distr[-1] == 3:
                        variable_type_ini = distr
            else:
                variable_type_ini = ["others", 0]

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
            if variable_type_ini[0] == "beta" and variable_type_ini[-2] == 4:
                variable_type_ini = variable_type_ini[:-1]
            elif "beta4" in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == "beta" and distr[-1] == 4:
                        variable_type_ini = distr
            else:
                variable_type_ini = ["others", 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[beta4_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_ks.var_type = [[variable_type_ini]]
            result_list_ks.append(vtd_ks.s_gof_test(0, 0, True)[0])

            variable_type_ini = vtd_cm.detect_continuous_shape(beta4_data_list_ini[
                i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == "beta" and variable_type_ini[-2] == 4:
                variable_type_ini = variable_type_ini[:-1]
            elif "beta4" in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == "beta" and distr[-1] == 4:
                        variable_type_ini = distr
            else:
                variable_type_ini = ["others", 0]

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
            if variable_type_ini[0] == "beta" and variable_type_ini[-2] == 5:
                variable_type_ini = variable_type_ini[:-1]
            elif "beta5" in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == "beta" and distr[-1] == 5:
                        variable_type_ini = distr
            else:
                variable_type_ini = ["others", 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[beta5_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_ks.var_type = [[variable_type_ini]]
            result_list_ks.append(vtd_ks.s_gof_test(0, 0, True)[0])

            variable_type_ini = vtd_cm.detect_continuous_shape(beta5_data_list_ini[
                i * dataset_size_ini:(i + 1) * dataset_size_ini])
            if variable_type_ini[0] == "beta" and variable_type_ini[-2] == 5:
                variable_type_ini = variable_type_ini[:-1]
            elif "beta5" in [distr[0]+str(distr[-1]) for distr in variable_type_ini[-1]]:
                for distr in variable_type_ini[-1]:
                    if distr[0] == "beta" and distr[-1] == 5:
                        variable_type_ini = distr
            else:
                variable_type_ini = ["others", 0]

            # Test and save the result of the s_gof-Test
            etd.values = [[beta5_data_list_upd[i * dataset_size_upd:(i + 1) * dataset_size_upd]]]
            vtd_cm.var_type = [[variable_type_ini]]
            result_list_cm.append(vtd_cm.s_gof_test(0, 0, True)[0])

        # Test if the result list is correct
        self.assertTrue(result_list_ks == beta5_result_shapes_ks)
        self.assertTrue(result_list_cm == beta5_result_shapes_cm)

    def test8do_timer(self):
        """Test if the do_timer method is implemented properly."""
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd)
        t = time.time()
        vtd.next_persist_time = t + 400
        self.assertEqual(vtd.do_timer(t + 200), 200)
        self.assertEqual(vtd.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(vtd.do_timer(t + 999), 1)
        self.assertEqual(vtd.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

    def test9persistence(self):
        """Test the do_persist and load_persistence_data methods."""
        # load data
        with open("unit/data/vtd_data/uni_data_test6", "rb") as f:
            uni_data_list = pickle.load(f)  # skipcq: BAN-B301
        init = 100
        update = 100
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        vtd = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=init, num_update=update,
                                   num_s_gof_values=update, div_thres=0.45, sim_thres=0.75, num_pause_others=0)
        t = time.time()
        stat_data = b"True"
        log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
        # initialize data
        for i in range(init):
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
        result = vtd.var_type[0][0]
        self.assertEqual(["stat", [stat_data.decode()], True], result, (init, update, result))

        # static -> static
        for i in range(update):
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
        result = vtd.var_type[0][0]
        self.assertEqual(["stat", [stat_data.decode()], True], result, (init, update, result))

        # static -> uni
        for uni_data in uni_data_list[2 * update:4 * update]:
            log_atom = LogAtom(uni_data, ParserMatch(MatchElement(self.path, str(uni_data).encode(), str(uni_data), None)), t,
                               self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
        result = vtd.var_type[0][0]
        pos_distr = vtd.alternative_distribution_types[0][0]
        self.assertTrue(result[0] == "uni" or "uni" in [distr[0] for distr in pos_distr], (init, update, result))

        # uni -> others
        for i in range(update):
            stat_data = bytes(str((i % int(update / 5))), "utf-8")
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
        result = vtd.var_type[0][0]
        self.assertEqual(["others", 0], result, (init, update, result))

        # others -> d
        for i in range(update):
            stat_data = bytes(str((i % int(update / 5))), "utf-8")
            log_atom = LogAtom(stat_data, ParserMatch(MatchElement(self.path, stat_data, stat_data, None)), t, self.__class__.__name__)
            self.assertTrue(etd.receive_atom(log_atom))
            vtd.receive_atom(log_atom)
        result = vtd.var_type[0][0]
        self.assertEqual("d", result[0], (init, update, result))

        self.assertEqual(vtd.var_type, [[['d', [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0],[0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05], 100]]])
        self.assertEqual(vtd.alternative_distribution_types, [[[]]])
        self.assertEqual(vtd.var_type_history_list, [[[[0, 0, 1, 0, 1, 0], [1, 1, 0, 0, 0, 0], [[0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0]], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]], [[0, 0, 0, -0.15555384791577725, 0, 0],  [0, 0, 0, 0.5762564151199925, 0, 0]]]]])
        self.assertEqual(vtd.var_type_history_list_reference, [])
        self.assertEqual(vtd.failed_indicators, [])
        self.assertEqual(vtd.distr_val, [[[]]])

        vtd.do_persist()
        with open(vtd.persistence_file_name, "r") as f:
            self.assertEqual(f.read(), '[[[["string:d", [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0], [0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05], 100]]], [[[]]], [[[[0, 0, 1, 0, 1, 0], [1, 1, 0, 0, 0, 0], [[0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0]], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]], [[0, 0, 0, -0.15555384791577725, 0, 0], [0, 0, 0, 0.5762564151199925, 0, 0]]]]], [], [], [[[]]]]')

        vtd.load_persistence_data()
        self.assertEqual(vtd.var_type, [[['d', [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0],[0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05], 100]]])
        self.assertEqual(vtd.alternative_distribution_types, [[[]]])
        self.assertEqual(vtd.var_type_history_list, [[[[0, 0, 1, 0, 1, 0], [1, 1, 0, 0, 0, 0], [[0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0]], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]], [[0, 0, 0, -0.15555384791577725, 0, 0],  [0, 0, 0, 0.5762564151199925, 0, 0]]]]])
        self.assertEqual(vtd.var_type_history_list_reference, [])
        self.assertEqual(vtd.failed_indicators, [])
        self.assertEqual(vtd.distr_val, [[[]]])

        other = VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=init, num_update=update,
                                     num_s_gof_values=update, div_thres=0.45, sim_thres=0.75, num_pause_others=0)
        self.assertEqual(vtd.var_type, other.var_type)
        self.assertEqual(vtd.alternative_distribution_types, other.alternative_distribution_types)
        self.assertEqual(vtd.var_type_history_list, other.var_type_history_list)
        self.assertEqual(vtd.var_type_history_list_reference, other.var_type_history_list_reference)
        self.assertEqual(vtd.failed_indicators, other.failed_indicators)
        self.assertEqual(vtd.distr_val, other.distr_val)

    def test10validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, ["default"], etd)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, None, etd)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, "", etd)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, b"Default", etd)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, True, etd)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, 123, etd)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, 123.3, etd)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, {"id": "Default"}, etd)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, (), etd)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, set(), etd)

        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], "")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], None)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], True)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], 123)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], 123.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], {"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], ())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id="")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id=None)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id=True)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id=123)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id=123.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id="Default")

        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=b"True")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode="True")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=123)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=123.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True)

        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list="")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=True)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=123)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=123.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=["/model/path"])
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=[])
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=None)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_gof_test="SomethingElse")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_gof_test=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_gof_test=123)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_gof_test=123.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_gof_test=None)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_gof_test=True)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_gof_test={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_gof_test=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_gof_test=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_gof_test=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_gof_test=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, used_gof_test="KS")
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, used_gof_test="CM")

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, gof_alpha=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, gof_alpha=1.1)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, gof_alpha=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, gof_alpha="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, gof_alpha={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, gof_alpha=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, gof_alpha=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, gof_alpha=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, gof_alpha=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, gof_alpha=0)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, gof_alpha=0.5)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, gof_alpha=1)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_alpha=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_alpha=1.1)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_alpha=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_alpha="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_alpha={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_alpha=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_alpha=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_alpha=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_alpha=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_alpha=0)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_alpha=0.5)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_alpha=1)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_bt_alpha=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_bt_alpha=1.1)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_bt_alpha=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_bt_alpha="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_bt_alpha={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_bt_alpha=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_bt_alpha=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_bt_alpha=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_bt_alpha=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_bt_alpha=0)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_bt_alpha=0.5)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, s_gof_bt_alpha=1)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, d_alpha=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, d_alpha=1.1)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, d_alpha=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, d_alpha="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, d_alpha={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, d_alpha=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, d_alpha=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, d_alpha=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, d_alpha=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, d_alpha=0)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, d_alpha=0.5)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, d_alpha=1)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, d_bt_alpha=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, d_bt_alpha=1.1)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, d_bt_alpha=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, d_bt_alpha="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, d_bt_alpha={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, d_bt_alpha=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, d_bt_alpha=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, d_bt_alpha=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, d_bt_alpha=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, d_bt_alpha=0)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, d_bt_alpha=0.5)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, d_bt_alpha=1)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, div_thres=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, div_thres=1.1)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, div_thres=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, div_thres="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, div_thres={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, div_thres=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, div_thres=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, div_thres=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, div_thres=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, div_thres=0)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, div_thres=0.5)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, div_thres=1)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, sim_thres=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, sim_thres=1.1)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, sim_thres=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, sim_thres="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, sim_thres={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, sim_thres=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, sim_thres=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, sim_thres=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, sim_thres=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, sim_thres=0)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, sim_thres=0.5)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, sim_thres=1)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, indicator_thres=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, indicator_thres=1.1)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, indicator_thres=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, indicator_thres="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, indicator_thres={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, indicator_thres=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, indicator_thres=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, indicator_thres=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, indicator_thres=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, indicator_thres=0)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, indicator_thres=0.5)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, indicator_thres=1)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init=0)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init=100.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=100)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update=0)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update=100.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_update=50)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_unq=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_unq=0)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_unq=100.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_unq=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_unq="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_unq={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_unq=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_unq=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_unq=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_unq=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_update_unq=100)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_values=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_values=0)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_values=101, num_init=100, num_update=50)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_values=49, num_init=100, num_update=50)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_values=100.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_values=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_values="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_values={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_values=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_values=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_values=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_values=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_values=100, num_init=100, num_update=50)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_values=50, num_init=100, num_update=50)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_bt=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_bt=0)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_bt=100.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_bt=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_bt="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_bt={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_bt=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_bt=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_bt=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_bt=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_s_gof_bt=100)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_d_bt=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_d_bt=0)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_d_bt=100.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_d_bt=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_d_bt="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_d_bt={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_d_bt=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_d_bt=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_d_bt=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_d_bt=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_d_bt=100)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_discrete=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_discrete=0)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_discrete=100.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_discrete=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_discrete="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_discrete={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_discrete=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_discrete=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_discrete=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_discrete=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_discrete=100)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_others=-1)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_others=100.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_others=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_others="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_others={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_others=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_others=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_others=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_others=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_others=100)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_pause_others=0)

        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, test_gof_int=None)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, test_gof_int=b"True")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, test_gof_int="True")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, test_gof_int=123)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, test_gof_int=123.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, test_gof_int={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, test_gof_int=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, test_gof_int=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, test_gof_int=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, test_gof_int=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, test_gof_int=True)

        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stop_update=None)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stop_update=b"True")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stop_update="True")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stop_update=123)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stop_update=123.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stop_update={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stop_update=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stop_update=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stop_update=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stop_update=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_stop_update=True)

        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_without_confidence=None)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_without_confidence=b"True")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_without_confidence="True")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_without_confidence=123)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_without_confidence=123.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_without_confidence={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_without_confidence=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_without_confidence=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_without_confidence=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_without_confidence=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_without_confidence=True)

        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_except_indicator=None)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_except_indicator=b"True")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_except_indicator="True")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_except_indicator=123)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_except_indicator=123.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_except_indicator={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_except_indicator=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_except_indicator=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_except_indicator=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_except_indicator=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, silence_output_except_indicator=True)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_hist_ref=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_hist_ref=0)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_hist_ref=100.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_hist_ref=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_hist_ref="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_hist_ref={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_hist_ref=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_hist_ref=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_hist_ref=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_hist_ref=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_hist_ref=100)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_var_type_hist_ref=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_var_type_hist_ref=0)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_var_type_hist_ref=100.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_var_type_hist_ref=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_var_type_hist_ref="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_var_type_hist_ref={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_var_type_hist_ref=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_var_type_hist_ref=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_var_type_hist_ref=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_update_var_type_hist_ref=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_update_var_type_hist_ref=100)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_considered_ind=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_considered_ind=0)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_considered_ind=100.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_considered_ind=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_considered_ind="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_considered_ind={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_considered_ind=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_considered_ind=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_considered_ind=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_considered_ind=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_var_type_considered_ind=100)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stat_stop_update=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stat_stop_update=0)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stat_stop_update=100.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stat_stop_update=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stat_stop_update="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stat_stop_update={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stat_stop_update=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stat_stop_update=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stat_stop_update=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_stat_stop_update=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_stat_stop_update=100)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_updates_until_var_reduction=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_updates_until_var_reduction=0)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_updates_until_var_reduction=100.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_updates_until_var_reduction=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_updates_until_var_reduction="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_updates_until_var_reduction={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_updates_until_var_reduction=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_updates_until_var_reduction=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_updates_until_var_reduction=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_updates_until_var_reduction=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_updates_until_var_reduction=100)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, var_reduction_thres=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, var_reduction_thres=1.1)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, var_reduction_thres=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, var_reduction_thres="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, var_reduction_thres={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, var_reduction_thres=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, var_reduction_thres=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, var_reduction_thres=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, var_reduction_thres=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, var_reduction_thres=0)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, var_reduction_thres=0.5)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, var_reduction_thres=1)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_skipped_ind_for_weights=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_skipped_ind_for_weights=0)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_skipped_ind_for_weights=100.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_skipped_ind_for_weights=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_skipped_ind_for_weights="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_skipped_ind_for_weights={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_skipped_ind_for_weights=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_skipped_ind_for_weights=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_skipped_ind_for_weights=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_skipped_ind_for_weights=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_skipped_ind_for_weights=100)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_ind_for_weights=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_ind_for_weights=0)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_ind_for_weights=100.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_ind_for_weights=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_ind_for_weights="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_ind_for_weights={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_ind_for_weights=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_ind_for_weights=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_ind_for_weights=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_ind_for_weights=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_ind_for_weights=100)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_multinomial_test="SomethingElse")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_multinomial_test=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_multinomial_test=None)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_multinomial_test=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_multinomial_test=123)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_multinomial_test=123.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_multinomial_test=True)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_multinomial_test={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_multinomial_test=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_multinomial_test=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, used_multinomial_test="MT")
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, used_multinomial_test="Approx")
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, used_multinomial_test="Chi")

        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, use_empiric_distr=None)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, use_empiric_distr=b"True")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, use_empiric_distr="True")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, use_empiric_distr=123)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, use_empiric_distr=123.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, use_empiric_distr={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, use_empiric_distr=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, use_empiric_distr=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, use_empiric_distr=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, use_empiric_distr=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, use_empiric_distr=True)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_range_test="SomethingElse")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_range_test=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_range_test=None)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_range_test=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_range_test=123)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_range_test=123.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_range_test=True)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_range_test={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_range_test=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, used_range_test=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, used_range_test="MeanSD")
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, used_range_test="EmpiricQuantiles")
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, used_range_test="MinMax")

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_alpha=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_alpha=1.1)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_alpha=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_alpha="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_alpha={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_alpha=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_alpha=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_alpha=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_alpha=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, range_alpha=0)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, range_alpha=0.5)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, range_alpha=1)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_threshold=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_threshold=1.1)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_threshold=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_threshold="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_threshold={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_threshold=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_threshold=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_threshold=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_threshold=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, range_threshold=0)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, range_threshold=0.5)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, range_threshold=1)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_reinit_range=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_reinit_range=0)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_reinit_range=100.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_reinit_range=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_reinit_range="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_reinit_range={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_reinit_range=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_reinit_range=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_reinit_range=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_reinit_range=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_reinit_range=100)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_limits_factor=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_limits_factor=0)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_limits_factor=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_limits_factor="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_limits_factor={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_limits_factor=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_limits_factor=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_limits_factor=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, range_limits_factor=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, range_limits_factor=100)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, range_limits_factor=100.22)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, dw_alpha=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, dw_alpha=1.1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, dw_alpha=0)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, dw_alpha=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, dw_alpha="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, dw_alpha={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, dw_alpha=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, dw_alpha=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, dw_alpha=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, dw_alpha=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, dw_alpha=0.05)

        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, save_statistics=None)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, save_statistics=b"True")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, save_statistics="True")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, save_statistics=123)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, save_statistics=123.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, save_statistics={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, save_statistics=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, save_statistics=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, save_statistics=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, save_statistics=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, save_statistics=True)

        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline=None)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline=b"True")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline="True")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline=123)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline=123.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, output_logline=True)

        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, ignore_list="")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, ignore_list=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, ignore_list=True)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, ignore_list=123)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, ignore_list=123.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, ignore_list={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, ignore_list=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, ignore_list=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, ignore_list=["/model/path"])
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, ignore_list=[])
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, ignore_list=None)

        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, constraint_list="")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, constraint_list=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, constraint_list=True)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, constraint_list=123)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, constraint_list=123.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, constraint_list={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, constraint_list=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, constraint_list=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, constraint_list=["/model/path"])
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, constraint_list=[])
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, constraint_list=None)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=0)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=100)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=100.22)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time=-1)
        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time=0)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time="123")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time=["Default"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time=[])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time=100)
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time=100.22)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=100, stop_learning_no_anomaly_time=100)

        self.assertRaises(ValueError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, log_resource_ignore_list=["/tmp/syslog"])
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, log_resource_ignore_list="")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, log_resource_ignore_list=b"Default")
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, log_resource_ignore_list=True)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, log_resource_ignore_list=123)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, log_resource_ignore_list=123.22)
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, log_resource_ignore_list={"id": "Default"})
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, log_resource_ignore_list=())
        self.assertRaises(TypeError, VariableTypeDetector, self.aminer_config, [self.stream_printer_event_handler], etd, log_resource_ignore_list=set())
        VariableTypeDetector(self.aminer_config, [self.stream_printer_event_handler], etd, log_resource_ignore_list=["file:///tmp/syslog"])
