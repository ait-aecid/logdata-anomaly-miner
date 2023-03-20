import unittest
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from aminer.input.LogAtom import LogAtom
import time
from datetime import datetime
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummyMatchContext
from aminer.AminerConfig import DEFAULT_PERSISTENCE_PERIOD


class NewMatchPathDetectorTest(TestBase):
    """Unittests for the NewMatchPathDetector."""

    __expected_string = '%s New path(es) detected\n%s: "%s" (%d lines)\n  %s\n%s\n\n'
    match_path_s1 = "['/s1']"
    match_path_d1 = "['/d1']"

    datetime_format_string = "%Y-%m-%d %H:%M:%S"
    analysis = "Analysis.%s"
    pid = " pid="
    uid = " uid=2"

    match_context_fixed_dme = DummyMatchContext(b" pid=")
    fixed_dme = DummyFixedDataModelElement("s1", b" pid=")
    match_element_fixed_dme = fixed_dme.get_match_element("", match_context_fixed_dme)

    match_context_decimal_integer_value_me = DummyMatchContext(b"25537 uid=2")
    decimal_integer_value_me = DummyFixedDataModelElement("d1", b"25537")
    match_element_decimal_integer_value_me = decimal_integer_value_me.get_match_element("", match_context_decimal_integer_value_me)

    def test1receive_atom(self):
        """
        Test if log atoms are processed correctly and the detector is learning (learn_mode=True) and stops if learn_mode=False.
        Test if stop_learning_time and stop_learning_no_anomaly_timestamp are implemented properly.
        """
        # learn_mode = True
        description = "test1receive_atom"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", True, output_logline=False)
        self.analysis_context.register_component(new_match_path_detector, description)
        t = round(time.time(), 3)

        log_atom_fixed_dme = LogAtom(self.fixed_dme.data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)
        log_atom_decimal_integer_value_me = LogAtom(self.match_context_decimal_integer_value_me.match_data,
                                                    ParserMatch(self.match_element_decimal_integer_value_me), t, new_match_path_detector)

        self.assertTrue(new_match_path_detector.receive_atom(log_atom_fixed_dme))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_detector.__class__.__name__, description, 1,
            self.match_path_s1, self.pid))
        self.reset_output_stream()

        # repeating should NOT produce the same result
        self.assertTrue(new_match_path_detector.receive_atom(log_atom_fixed_dme))
        self.assertEqual(self.output_stream.getvalue(), '')
        self.reset_output_stream()

        # learn_mode = False
        new_match_path_detector.learn_mode = False
        self.assertTrue(new_match_path_detector.receive_atom(log_atom_decimal_integer_value_me))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_detector.__class__.__name__, description, 1,
            self.match_path_d1, self.uid))
        self.reset_output_stream()

        # repeating should produce the same result
        self.assertTrue(new_match_path_detector.receive_atom(log_atom_decimal_integer_value_me))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_detector.__class__.__name__, description, 1,
            self.match_path_d1, self.uid))

        # stop_learning_time
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", True, output_logline=False, stop_learning_time=100)
        self.assertTrue(new_match_path_detector.receive_atom(log_atom_fixed_dme))
        log_atom_fixed_dme.atom_time = t + 99
        self.assertTrue(new_match_path_detector.receive_atom(log_atom_fixed_dme))
        self.assertTrue(new_match_path_detector.learn_mode)
        log_atom_fixed_dme.atom_time = t + 101
        self.assertTrue(new_match_path_detector.receive_atom(log_atom_fixed_dme))
        self.assertFalse(new_match_path_detector.learn_mode)

        # stop_learning_no_anomaly_time
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", True, output_logline=False, stop_learning_no_anomaly_time=100)
        log_atom_fixed_dme.atom_time = t
        self.assertTrue(new_match_path_detector.receive_atom(log_atom_fixed_dme))
        log_atom_fixed_dme.atom_time = t + 100
        self.assertTrue(new_match_path_detector.receive_atom(log_atom_fixed_dme))
        self.assertTrue(new_match_path_detector.learn_mode)
        log_atom_decimal_integer_value_me.atom_time = t + 100
        self.assertTrue(new_match_path_detector.receive_atom(log_atom_decimal_integer_value_me))
        self.assertTrue(new_match_path_detector.learn_mode)
        log_atom_fixed_dme.atom_time = t + 200
        self.assertTrue(new_match_path_detector.receive_atom(log_atom_fixed_dme))
        self.assertTrue(new_match_path_detector.learn_mode)
        log_atom_fixed_dme.atom_time = t + 201
        self.assertTrue(new_match_path_detector.receive_atom(log_atom_fixed_dme))
        self.assertFalse(new_match_path_detector.learn_mode)

    def test2do_timer(self):
        """Test if the do_timer method is implemented properly."""
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", True, output_logline=False)
        t = time.time()
        new_match_path_detector.next_persist_time = t + 400
        self.assertEqual(new_match_path_detector.do_timer(t + 200), 200)
        self.assertEqual(new_match_path_detector.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(new_match_path_detector.do_timer(t + 999), 1)
        self.assertEqual(new_match_path_detector.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

    def test3allowlist_event(self):
        """Test if the allowlist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        description = "Test8NewMatchPathDetector"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", True, output_logline=False)
        self.analysis_context.register_component(new_match_path_detector, description)
        t = round(time.time(), 3)
        log_atom_fixed_dme = LogAtom(self.fixed_dme.data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)
        new_match_path_detector.receive_atom(log_atom_fixed_dme)
        self.assertRaises(Exception, new_match_path_detector.allowlist_event, self.analysis % "NewMatchPathValueDetector", self.output_stream.getvalue(), None)

        # The NewMatchPathDetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, new_match_path_detector.allowlist_event, self.analysis % new_match_path_detector.__class__.__name__,
                          self.output_stream.getvalue(), ["random", "Data"])

        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(new_match_path_detector.allowlist_event(
            self.analysis % new_match_path_detector.__class__.__name__, self.match_element_fixed_dme.get_path(), None),
            "Allowlisted path(es) %s in %s." % (
                self.match_element_fixed_dme.get_path(), self.analysis % new_match_path_detector.__class__.__name__))
        self.assertEqual(new_match_path_detector.known_path_set, {"/s1"})

        new_match_path_detector.learn_mode = False
        self.assertEqual(new_match_path_detector.allowlist_event(
            self.analysis % new_match_path_detector.__class__.__name__, self.match_element_decimal_integer_value_me.get_path(), None),
            "Allowlisted path(es) %s in %s." % (
                self.match_element_decimal_integer_value_me.path, self.analysis % new_match_path_detector.__class__.__name__))
        self.assertEqual(new_match_path_detector.known_path_set, {"/s1", "/d1"})

    def test4persistence(self):
        """Test the do_persist and load_persistence_data methods."""
        description = "test4persistence"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", True, output_logline=False)
        self.analysis_context.register_component(new_match_path_detector, description)
        t = round(time.time(), 3)
        log_atom_fixed_dme = LogAtom(self.fixed_dme.data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)
        log_atom_decimal_integer_value_me = LogAtom(self.match_context_decimal_integer_value_me.match_data,
                                                    ParserMatch(self.match_element_decimal_integer_value_me), t, new_match_path_detector)

        self.assertTrue(new_match_path_detector.receive_atom(log_atom_fixed_dme))
        self.assertTrue(new_match_path_detector.receive_atom(log_atom_decimal_integer_value_me))
        self.assertEqual(new_match_path_detector.known_path_set, {"/s1", "/d1"})
        new_match_path_detector.do_persist()
        with open(new_match_path_detector.persistence_file_name, "r") as f:
            self.assertEqual(f.readline(), '["string:/d1", "string:/s1"]')

        new_match_path_detector.known_path_set = set()
        new_match_path_detector.load_persistence_data()
        self.assertEqual(new_match_path_detector.known_path_set, {"/s1", "/d1"})

        other = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False, output_logline=False)
        self.assertEqual(new_match_path_detector.known_path_set, other.known_path_set)

    def test5validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(ValueError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id="")
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=None)
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=b"Default")
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=True)
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=123)
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=123.22)
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id={"id": "Default"})
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=["Default"])
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=[])
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=())
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=set())
        NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], persistence_id="Default")

        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=b"True")
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode="True")
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=123)
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=123.22)
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode={"id": "Default"})
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=["Default"])
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=[])
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=())
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=set())
        NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True)

        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=None)
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=b"True")
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline="True")
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=123)
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=123.22)
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline={"id": "Default"})
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=["Default"])
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=[])
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=())
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=set())
        NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], output_logline=True)

        self.assertRaises(ValueError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=-1)
        self.assertRaises(ValueError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=0)
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=b"Default")
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time="123")
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time={"id": "Default"})
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=["Default"])
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=[])
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=())
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=set())
        NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100)
        NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100.22)

        self.assertRaises(ValueError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=-1)
        self.assertRaises(ValueError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=0)
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=b"Default")
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time="123")
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time={"id": "Default"})
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=["Default"])
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=[])
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=())
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=set())
        NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=100)
        NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=100.22)

        self.assertRaises(ValueError, NewMatchPathDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100, stop_learning_no_anomaly_time=100)


if __name__ == "__main__":
    unittest.main()
