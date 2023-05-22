import unittest
from aminer.analysis.EventCorrelationDetector import EventCorrelationDetector, set_random_seed
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummyFirstMatchModelElement, DummyMatchContext
import time
import random
from aminer.AminerConfig import DEFAULT_PERSISTENCE_PERIOD


class EventCorrelationDetectorTest(TestBase):
    """Unittests for the EventCorrelationDetector."""
    def test1receive_atom(self):
        """
        Test if log atoms are processed correctly and the detector is learning (learn_mode=True) and stops if learn_mode=False.
        Test if stop_learning_time and stop_learning_no_anomaly_timestamp are implemented properly.
        """
        # check if perfect examples are learned with default parameters
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, learn_mode=True)
        self.run_ecd_test(ecd, self.perfect_data_diff5[:12000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, learn_mode=True)
        self.run_ecd_test(ecd, self.perfect_data_diff1[:12000])

        # the generation_probability and generation_factor are set to 0.5 in the first case and 0.1 in the second case with the perfect examples.
        # the EventCorrelationDetector should still learn the rules as expected.
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, generation_probability=0.5, generation_factor=0.5, learn_mode=True)
        self.run_ecd_test(ecd, self.perfect_data_diff5[:30000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, generation_probability=0.5, generation_factor=0.5, learn_mode=True)
        self.run_ecd_test(ecd, self.perfect_data_diff1[:30000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, generation_probability=0.3, generation_factor=0.3, learn_mode=True)
        self.run_ecd_test(ecd, self.perfect_data_diff5[:100000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, generation_probability=0.3, generation_factor=0.3, learn_mode=True)
        self.run_ecd_test(ecd, self.perfect_data_diff1[:100000])

        # examples with errors are used, but still should be learned with the default parameters.
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, learn_mode=True)
        self.run_ecd_test(ecd, self.errored_data_diff5[:12000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, learn_mode=True)
        self.run_ecd_test(ecd, self.errored_data_diff1[:12000])

        # examples with errors are used, but still should be learned. These tests are using a higher generation_probability and generation_factor, because the data contains errors.
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, generation_probability=0.7, generation_factor=0.99, learn_mode=True)
        self.run_ecd_test(ecd, self.errored_data_diff5_low_error_rate[:25000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, generation_probability=0.7, generation_factor=0.99, learn_mode=True)
        self.run_ecd_test(ecd, self.errored_data_diff1_low_error_rate[:25000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, generation_probability=0.5, generation_factor=0.95, learn_mode=True)
        self.run_ecd_test(ecd, self.errored_data_diff5_low_error_rate[:40000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, generation_probability=0.5, generation_factor=0.95, learn_mode=True)
        self.run_ecd_test(ecd, self.errored_data_diff1_low_error_rate[:40000])

        # p0 and alpha are chosen carefully to only find safe assumptions about the implications in the data. Therefor more iterations in the training phase are needed.
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=1.0, alpha=0.01, learn_mode=True)
        self.run_ecd_test(ecd, self.perfect_data_diff5[:20000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=1.0, alpha=0.01, learn_mode=True)
        self.run_ecd_test(ecd, self.errored_data_diff5_low_error_rate[:40000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=1.0, alpha=0.01, learn_mode=True)
        self.run_ecd_test(ecd, self.perfect_data_diff1[:20000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=1.0, alpha=0.01, learn_mode=True)
        self.run_ecd_test(ecd, self.errored_data_diff1_low_error_rate[:40000])

        # p0 and alpha are chosen to approximately find sequences in log data. Therefor not as many iterations are needed to learn the rules.
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=0.7, alpha=0.1, learn_mode=True)
        self.run_ecd_test(ecd, self.perfect_data_diff5[:10000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=0.7, alpha=0.1, learn_mode=True)
        self.run_ecd_test(ecd, self.errored_data_diff5[:10000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=0.7, alpha=0.1, learn_mode=True)
        self.run_ecd_test(ecd, self.perfect_data_diff1[:10000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=0.7, alpha=0.1, learn_mode=True)
        self.run_ecd_test(ecd, self.errored_data_diff1[:10000])

        # stop_learning_time
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, output_logline=False, stop_learning_time=100)
        t = time.time()
        match_context1 = DummyMatchContext(b" pid=")
        fdme1 = DummyFixedDataModelElement("s1", b" pid=")
        match_element1 = fdme1.get_match_element("", match_context1)
        match_context2 = DummyMatchContext(b"25537 uid=2")
        fdme2 = DummyFixedDataModelElement("d1", b"25537")
        match_element2 = fdme2.get_match_element("", match_context2)
        log_atom1 = LogAtom(fdme1.data, ParserMatch(match_element1), t, ecd)
        log_atom2 = LogAtom(match_context2.match_data, ParserMatch(match_element2), t, ecd)
        self.assertTrue(ecd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 99
        self.assertTrue(ecd.receive_atom(log_atom1))
        self.assertTrue(ecd.learn_mode)
        log_atom1.atom_time = t + 101
        self.assertTrue(ecd.receive_atom(log_atom1))
        self.assertFalse(ecd.learn_mode)

    def test2do_timer(self):
        """Test if the do_timer method is implemented properly."""
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler])
        t = time.time()
        ecd.next_persist_time = t + 400
        self.assertEqual(ecd.do_timer(t + 200), 200)
        self.assertEqual(ecd.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(ecd.do_timer(t + 999), 1)
        self.assertEqual(ecd.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

    def test3allowlist_event(self):
        """Test if the allowlist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler])
        t = round(time.time(), 3)
        analysis = "Analysis.%s"
        self.assertRaises(Exception, ecd.allowlist_event, analysis % "NewMatchPathValueDetector", self.output_stream.getvalue(), None)

        # The EventCorrelationDetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, ecd.allowlist_event, analysis % ecd.__class__.__name__, self.output_stream.getvalue(), ["random", "Data"])

        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(ecd.allowlist_event(analysis % ecd.__class__.__name__, "/s1", None), "Allowlisted path %s in %s." % ("/s1", analysis % ecd.__class__.__name__))
        self.assertEqual(ecd.constraint_list, ["/s1"])

        ecd.learn_mode = False
        self.assertEqual(ecd.allowlist_event(analysis % ecd.__class__.__name__, "/d1", None), "Allowlisted path %s in %s." % ("/d1", analysis % ecd.__class__.__name__))
        self.assertEqual(ecd.constraint_list, ["/s1", "/d1"])

    def test4blocklist_event(self):
        """Test if the blocklist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler])
        t = round(time.time(), 3)
        analysis = "Analysis.%s"
        self.assertRaises(Exception, ecd.blocklist_event, analysis % "NewMatchPathValueDetector", self.output_stream.getvalue(), None)

        # The EventCorrelationDetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, ecd.blocklist_event, analysis % ecd.__class__.__name__, self.output_stream.getvalue(), ["random", "Data"])

        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(ecd.blocklist_event(analysis % ecd.__class__.__name__, "/s1", None), "Blocklisted path %s in %s." % ("/s1", analysis % ecd.__class__.__name__))
        self.assertEqual(ecd.ignore_list, ["/s1"])

        ecd.learn_mode = False
        self.assertEqual(ecd.blocklist_event(analysis % ecd.__class__.__name__, "/d1", None), "Blocklisted path %s in %s." % ("/d1", analysis % ecd.__class__.__name__))
        self.assertEqual(ecd.ignore_list, ["/s1", "/d1"])

    def test5persistence(self):
        """Test the do_persist and load_persistence_data methods."""
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, learn_mode=True)
        self.run_ecd_test(ecd, self.perfect_data_diff5[:12000])
        ecd.do_persist()
        with open(ecd.persistence_file_name, "r") as f:
            self.assertEqual(f.readline(), '[["string:back", ["string:parser/first/a"], ["string:parser/first/z"], 500, 500], ["string:back", ["string:parser/first/b"], ["string:parser/first/a"], 500, 500], ["string:back", ["string:parser/first/c"], ["string:parser/first/b"], 500, 500], ["string:back", ["string:parser/first/d"], ["string:parser/first/c"], 500, 500], ["string:back", ["string:parser/first/e"], ["string:parser/first/d"], 500, 500], ["string:back", ["string:parser/first/f"], ["string:parser/first/e"], 500, 500], ["string:back", ["string:parser/first/g"], ["string:parser/first/f"], 500, 500], ["string:back", ["string:parser/first/h"], ["string:parser/first/g"], 500, 500], ["string:back", ["string:parser/first/i"], ["string:parser/first/h"], 500, 500], ["string:back", ["string:parser/first/j"], ["string:parser/first/i"], 500, 500], ["string:back", ["string:parser/first/k"], ["string:parser/first/j"], 500, 500], ["string:back", ["string:parser/first/l"], ["string:parser/first/k"], 500, 500], ["string:back", ["string:parser/first/m"], ["string:parser/first/l"], 500, 500], ["string:back", ["string:parser/first/n"], ["string:parser/first/m"], 500, 500], ["string:back", ["string:parser/first/o"], ["string:parser/first/n"], 500, 500], ["string:back", ["string:parser/first/p"], ["string:parser/first/o"], 500, 500], ["string:back", ["string:parser/first/q"], ["string:parser/first/p"], 500, 500], ["string:back", ["string:parser/first/r"], ["string:parser/first/q"], 500, 500], ["string:back", ["string:parser/first/s"], ["string:parser/first/r"], 500, 500], ["string:back", ["string:parser/first/t"], ["string:parser/first/s"], 500, 500], ["string:back", ["string:parser/first/u"], ["string:parser/first/t"], 500, 500], ["string:back", ["string:parser/first/v"], ["string:parser/first/u"], 500, 500], ["string:back", ["string:parser/first/w"], ["string:parser/first/v"], 500, 500], ["string:back", ["string:parser/first/x"], ["string:parser/first/w"], 500, 500], ["string:back", ["string:parser/first/y"], ["string:parser/first/x"], 500, 500], ["string:back", ["string:parser/first/z"], ["string:parser/first/y"], 500, 500], ["string:forward", ["string:parser/first/a"], ["string:parser/first/b"], 500, 500], ["string:forward", ["string:parser/first/b"], ["string:parser/first/c"], 500, 500], ["string:forward", ["string:parser/first/c"], ["string:parser/first/d"], 500, 500], ["string:forward", ["string:parser/first/d"], ["string:parser/first/e"], 500, 500], ["string:forward", ["string:parser/first/e"], ["string:parser/first/f"], 500, 500], ["string:forward", ["string:parser/first/f"], ["string:parser/first/g"], 500, 500], ["string:forward", ["string:parser/first/g"], ["string:parser/first/h"], 500, 500], ["string:forward", ["string:parser/first/h"], ["string:parser/first/i"], 500, 500], ["string:forward", ["string:parser/first/i"], ["string:parser/first/j"], 500, 500], ["string:forward", ["string:parser/first/j"], ["string:parser/first/k"], 500, 500], ["string:forward", ["string:parser/first/k"], ["string:parser/first/l"], 500, 500], ["string:forward", ["string:parser/first/l"], ["string:parser/first/m"], 500, 500], ["string:forward", ["string:parser/first/m"], ["string:parser/first/n"], 500, 500], ["string:forward", ["string:parser/first/n"], ["string:parser/first/o"], 500, 500], ["string:forward", ["string:parser/first/o"], ["string:parser/first/p"], 500, 500], ["string:forward", ["string:parser/first/p"], ["string:parser/first/q"], 500, 500], ["string:forward", ["string:parser/first/q"], ["string:parser/first/r"], 500, 500], ["string:forward", ["string:parser/first/r"], ["string:parser/first/s"], 500, 500], ["string:forward", ["string:parser/first/s"], ["string:parser/first/t"], 500, 500], ["string:forward", ["string:parser/first/t"], ["string:parser/first/u"], 500, 500], ["string:forward", ["string:parser/first/u"], ["string:parser/first/v"], 500, 500], ["string:forward", ["string:parser/first/v"], ["string:parser/first/w"], 500, 500], ["string:forward", ["string:parser/first/w"], ["string:parser/first/x"], 500, 500], ["string:forward", ["string:parser/first/x"], ["string:parser/first/y"], 500, 500], ["string:forward", ["string:parser/first/y"], ["string:parser/first/z"], 500, 500], ["string:forward", ["string:parser/first/z"], ["string:parser/first/a"], 500, 500]]')

        other = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, learn_mode=True)
        for key in ecd.back_rules.keys():
            for i in range(len(ecd.back_rules[key])):
                self.assertEqual(ecd.back_rules[key][i].trigger_event, other.back_rules[key][i].trigger_event)
                self.assertEqual(ecd.back_rules[key][i].implied_event, other.back_rules[key][i].implied_event)
                self.assertEqual(ecd.back_rules[key][i].max_observations, other.back_rules[key][i].max_observations)
                self.assertEqual(ecd.back_rules[key][i].min_eval_true, other.back_rules[key][i].min_eval_true)
        for key in ecd.forward_rules.keys():
            for i in range(len(ecd.forward_rules[key])):
                self.assertEqual(ecd.forward_rules[key][i].trigger_event, other.forward_rules[key][i].trigger_event)
                self.assertEqual(ecd.forward_rules[key][i].implied_event, other.forward_rules[key][i].implied_event)
                self.assertEqual(ecd.forward_rules[key][i].max_observations, other.forward_rules[key][i].max_observations)
                self.assertEqual(ecd.forward_rules[key][i].min_eval_true, other.forward_rules[key][i].min_eval_true)

    def test6validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, ["default"])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, None)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, "")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, b"Default")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, True)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, 123)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, 123.3)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, {"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, ())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, set())

        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=[""])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list="")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=b"Default")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=True)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=123)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=123.3)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list={"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=set())
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], target_path_list=[])
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], target_path_list=None)

        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_hypotheses=-1)
        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_hypotheses=0)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_hypotheses=100.22)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_hypotheses=b"Default")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_hypotheses="123")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_hypotheses={"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_hypotheses=["Default"])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_hypotheses=[])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_hypotheses=())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_hypotheses=set())
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], max_hypotheses=100)

        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], hypothesis_max_delta_time=-1)
        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], hypothesis_max_delta_time=0)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], hypothesis_max_delta_time=b"Default")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], hypothesis_max_delta_time="123")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], hypothesis_max_delta_time={"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], hypothesis_max_delta_time=["Default"])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], hypothesis_max_delta_time=[])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], hypothesis_max_delta_time=())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], hypothesis_max_delta_time=set())
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], hypothesis_max_delta_time=100)
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], hypothesis_max_delta_time=100.22)

        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], generation_probability=-1)
        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], generation_probability=1.1)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], generation_probability=b"Default")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], generation_probability="123")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], generation_probability={"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], generation_probability=["Default"])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], generation_probability=[])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], generation_probability=())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], generation_probability=set())
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], generation_probability=0)
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], generation_probability=0.5)
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], generation_probability=1)

        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], generation_factor=-1)
        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], generation_factor=1.1)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], generation_factor=b"Default")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], generation_factor="123")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], generation_factor={"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], generation_factor=["Default"])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], generation_factor=[])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], generation_factor=())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], generation_factor=set())
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], generation_factor=0)
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], generation_factor=0.5)
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], generation_factor=1)

        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_observations=-1)
        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_observations=0)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_observations=100.22)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_observations=b"Default")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_observations="123")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_observations={"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_observations=["Default"])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_observations=[])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_observations=())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], max_observations=set())
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], max_observations=100)

        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], p0=-1)
        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], p0=1.1)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], p0=b"Default")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], p0="123")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], p0={"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], p0=["Default"])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], p0=[])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], p0=())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], p0=set())
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], p0=0)
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], p0=0.5)
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], p0=1)

        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], alpha=-1)
        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], alpha=1.1)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], alpha=b"Default")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], alpha="123")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], alpha={"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], alpha=["Default"])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], alpha=[])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], alpha=())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], alpha=set())
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], alpha=0)
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], alpha=0.5)
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], alpha=1)

        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], candidates_size=-1)
        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], candidates_size=0)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], candidates_size=100.22)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], candidates_size=b"Default")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], candidates_size="123")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], candidates_size={"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], candidates_size=["Default"])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], candidates_size=[])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], candidates_size=())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], candidates_size=set())
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], candidates_size=100)

        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], hypotheses_eval_delta_time=-1)
        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], hypotheses_eval_delta_time=0)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], hypotheses_eval_delta_time=b"Default")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], hypotheses_eval_delta_time="123")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], hypotheses_eval_delta_time={"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], hypotheses_eval_delta_time=["Default"])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], hypotheses_eval_delta_time=[])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], hypotheses_eval_delta_time=())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], hypotheses_eval_delta_time=set())
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], hypotheses_eval_delta_time=100)
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], hypotheses_eval_delta_time=100.22)

        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], delta_time_to_discard_hypothesis=-1)
        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], delta_time_to_discard_hypothesis=0)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], delta_time_to_discard_hypothesis=b"Default")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], delta_time_to_discard_hypothesis="123")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], delta_time_to_discard_hypothesis={"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], delta_time_to_discard_hypothesis=["Default"])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], delta_time_to_discard_hypothesis=[])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], delta_time_to_discard_hypothesis=())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], delta_time_to_discard_hypothesis=set())
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], delta_time_to_discard_hypothesis=100)
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], delta_time_to_discard_hypothesis=100.22)

        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=b"True")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], check_rules_flag="True")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=123)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=123.22)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], check_rules_flag={"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=["Default"])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=[])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=set())
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True)

        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=b"True")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode="True")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=123)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=123.22)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode={"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=["Default"])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=[])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=set())
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True)

        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=[""])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list="")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=b"Default")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=True)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=123)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=123.3)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list={"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=set())
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], ignore_list=[])
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], ignore_list=None)

        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id="")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=None)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=b"Default")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=True)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=123)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=123.22)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id={"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=["Default"])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=[])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=set())
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], persistence_id="Default")

        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=None)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=b"True")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline="True")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=123)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=123.22)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline={"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=["Default"])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=[])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=set())
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], output_logline=True)

        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=[""])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list="")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=b"Default")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=True)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=123)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=123.3)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list={"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=set())
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], constraint_list=[])
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], constraint_list=None)

        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=-1)
        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=0)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=b"Default")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time="123")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time={"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=["Default"])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=[])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=set())
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100)
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100.22)

        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=-1)
        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=0)
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=b"Default")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time="123")
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time={"id": "Default"})
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=["Default"])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=[])
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=())
        self.assertRaises(TypeError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=set())
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=100)
        EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=100.22)

        self.assertRaises(ValueError, EventCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100, stop_learning_no_anomaly_time=100)

    @classmethod
    def setUpClass(cls):
        """Set up the data for the all tests."""
        cls.alphabet = b"abcdefghijklmnopqrstuvwxyz"
        cls.analysis = "Analysis.%s"
        children = []
        for _, val in enumerate(cls.alphabet):
            char = bytes([val])
            children.append(DummyFixedDataModelElement(char.decode(), char))
        cls.alphabet_model = DummyFirstMatchModelElement("first", children)
        error_rate = 0.000085
        cls.perfect_data_diff5 = cls.generate_perfect_data(cls, 30000, 5)
        cls.perfect_data_diff1 = cls.generate_perfect_data(cls, 30000, 1)
        cls.errored_data_diff5 = cls.generate_errored_data(cls, 100000, 5, error_rate)
        cls.errored_data_diff1 = cls.generate_errored_data(cls, 100000, 1, error_rate)
        cls.errored_data_diff5_low_error_rate = cls.generate_errored_data(cls, 100000, 5, error_rate / 2.5)
        cls.errored_data_diff1_low_error_rate = cls.generate_errored_data(cls, 100000, 1, error_rate / 2.5)
        set_random_seed(42)

    def check_rules(self, sorted_back_rules, sorted_forward_rules, diff):
        """Check if the rules are as expected."""
        for path in sorted_forward_rules:
            self.assertEqual(len(sorted_forward_rules[path]), 5 / diff)
            implications = []
            trigger = b""
            for rule in sorted_forward_rules[path]:
                trigger = rule.trigger_event[0].split("/")[-1].encode()
                implications.append(self.alphabet.index(rule.implied_event[0].split("/")[-1].encode()))
            for i in range(1, len(sorted_forward_rules[path]), 1):  # skipcq: PTC-W0060
                self.assertIn((self.alphabet.index(trigger) + i) % len(self.alphabet), implications)
        for path in sorted_back_rules:
            self.assertEqual(len(sorted_back_rules[path]), 5 / diff)
            trigger = b""
            implications = []
            for rule in sorted_back_rules[path]:
                trigger = rule.trigger_event[0].split("/")[-1].encode()
                implications.append(self.alphabet.index(rule.implied_event[0].split("/")[-1].encode()))
            for i in range(1, len(sorted_back_rules[path]), 1):  # skipcq: PTC-W0060
                self.assertIn((self.alphabet.index(trigger) - i) % len(self.alphabet), implications)

    def check_anomaly_detection(self, ecd, t, diff):
        """Check if anomalies were detected as expected."""
        for char in self.alphabet:
            self.reset_output_stream()
            char = bytes([char])
            parser_match = ParserMatch(self.alphabet_model.get_match_element("parser", DummyMatchContext(char)))
            t += 5 * 3
            ecd.receive_atom(LogAtom(char, parser_match, t, self.__class__.__name__))
            # another LogAtom must be received to check the follow anomalies.
            t += 5 * 3
            ecd.receive_atom(LogAtom(char, parser_match, t, self.__class__.__name__))

            # precede anomaly
            for i in range(1, int(5 / diff) + 1, 1):
                self.assertIn("Event %s is missing, but should precede event %s" % (
                    repr(bytes([self.alphabet[(self.alphabet.index(char) - i) % len(self.alphabet)]])), repr(char)),
                    self.output_stream.getvalue())
            for i in range(int(5 / diff) + 1, len(self.alphabet), 1):  # skipcq: PTC-W0060
                self.assertNotIn("Event %s is missing, but should precede event %s" % (
                    repr(bytes([self.alphabet[(self.alphabet.index(char) - i) % len(self.alphabet)]])), repr(char)),
                    self.output_stream.getvalue())

            # follow anomaly
            for i in range(1, int(5 / diff) + 1, 1):
                self.assertIn("Event %s is missing, but should follow event %s" % (
                    repr(bytes([self.alphabet[(self.alphabet.index(char) + i) % len(self.alphabet)]])), repr(char)),
                    self.output_stream.getvalue())
            for i in range(int(5 / diff) + 1, len(self.alphabet), 1):  # skipcq: PTC-W0060
                self.assertNotIn("Event %s is missing, but should follow event %s" % (
                    repr(bytes([self.alphabet[(self.alphabet.index(char) + i) % len(self.alphabet)]])), repr(char)),
                    self.output_stream.getvalue())

    def run_ecd_test(self, ecd, log_atoms):
        """Run the ECD test."""
        diff = log_atoms[1].atom_time - log_atoms[0].atom_time
        log_atom = None
        for log_atom in log_atoms:
            ecd.receive_atom(log_atom)
        sorted_forward_rules = dict(sorted(ecd.forward_rules.items()))
        sorted_back_rules = dict(sorted(ecd.back_rules.items()))
        self.assertEqual(len(sorted_forward_rules), len(self.alphabet_model.children))
        self.assertEqual(len(sorted_back_rules), len(self.alphabet_model.children))
        self.check_rules(sorted_back_rules, sorted_forward_rules, diff)
        ecd.learn_mode = False
        self.check_anomaly_detection(ecd, log_atom.atom_time, diff)

    def generate_perfect_data(self, iterations, diff):
        """Generate data without any error."""
        log_atoms = []
        t = time.time()
        for i in range(1, iterations+1):
            char = bytes([self.alphabet[i % len(self.alphabet)]])
            parser_match = ParserMatch(self.alphabet_model.get_match_element("parser", DummyMatchContext(char)))
            t += diff
            log_atoms.append(LogAtom(char, parser_match, t, self.__class__.__name__))
        return log_atoms

    def generate_errored_data(self, iterations, diff, error_rate):
        """Generate data with errors according to the error_rate."""
        log_atoms = []
        t = time.time()
        divisor = 1
        while error_rate * divisor < 1:
            divisor = divisor * 10
        err = divisor * error_rate
        divisor //= err
        for i in range(1, iterations+1):
            if i % divisor == 0 and i != 0:
                char = bytes([self.alphabet[int(i + random.uniform(diff+1, len(self.alphabet))) % len(self.alphabet)]])
            else:
                char = bytes([self.alphabet[i % len(self.alphabet)]])
            parser_match = ParserMatch(self.alphabet_model.get_match_element("parser", DummyMatchContext(char)))
            t += diff
            log_atoms.append(LogAtom(char, parser_match, t, self.__class__.__name__))
        return log_atoms


if __name__ == "__main__":
    unittest.main()
