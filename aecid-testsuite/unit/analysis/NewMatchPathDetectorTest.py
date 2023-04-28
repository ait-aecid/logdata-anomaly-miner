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
    match_context1 = DummyMatchContext(b" pid=")
    fdme1 = DummyFixedDataModelElement("s1", b" pid=")
    match_element1 = fdme1.get_match_element("", match_context1)

    match_context2 = DummyMatchContext(b"25537 uid=2")
    fdme2 = DummyFixedDataModelElement("d1", b"25537")
    match_element2 = fdme2.get_match_element("", match_context2)

    def test1receive_atom(self):
        """
        Test if log atoms are processed correctly and the detector is learning (learn_mode=True) and stops if learn_mode=False.
        Test if stop_learning_time and stop_learning_no_anomaly_timestamp are implemented properly.
        """
        expected_string = '%s New path(es) detected\n%s: "None" (%d lines)\n  %s\n%s\n\n'
        datetime_format_string = "%Y-%m-%d %H:%M:%S"
        # learn_mode = True
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", True, output_logline=False)
        t = round(time.time(), 3)

        log_atom1 = LogAtom(self.fdme1.data, ParserMatch(self.match_element1), t, nmpd)
        log_atom2 = LogAtom(self.match_context2.match_data, ParserMatch(self.match_element2), t, nmpd)

        self.assertTrue(nmpd.receive_atom(log_atom1))
        self.assertEqual(self.output_stream.getvalue(), expected_string % (
            datetime.fromtimestamp(t).strftime(datetime_format_string), nmpd.__class__.__name__, 1, "['/s1']", " pid="))
        self.reset_output_stream()

        # repeating should NOT produce the same result
        self.assertTrue(nmpd.receive_atom(log_atom1))
        self.assertEqual(self.output_stream.getvalue(), "")
        self.reset_output_stream()

        # learn_mode = False
        nmpd.learn_mode = False
        self.assertTrue(nmpd.receive_atom(log_atom2))
        self.assertEqual(self.output_stream.getvalue(), expected_string % (
            datetime.fromtimestamp(t).strftime(datetime_format_string), nmpd.__class__.__name__, 1, "['/d1']", " uid=2"))
        self.reset_output_stream()

        # repeating should produce the same result
        self.assertTrue(nmpd.receive_atom(log_atom2))
        self.assertEqual(self.output_stream.getvalue(), expected_string % (
            datetime.fromtimestamp(t).strftime(datetime_format_string), nmpd.__class__.__name__, 1, "['/d1']", " uid=2"))

        # stop_learning_time
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", True, output_logline=False, stop_learning_time=100)
        self.assertTrue(nmpd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 99
        self.assertTrue(nmpd.receive_atom(log_atom1))
        self.assertTrue(nmpd.learn_mode)
        log_atom1.atom_time = t + 101
        self.assertTrue(nmpd.receive_atom(log_atom1))
        self.assertFalse(nmpd.learn_mode)

        # stop_learning_no_anomaly_time
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", True, output_logline=False, stop_learning_no_anomaly_time=100)
        log_atom1.atom_time = t
        self.assertTrue(nmpd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 100
        self.assertTrue(nmpd.receive_atom(log_atom1))
        self.assertTrue(nmpd.learn_mode)
        log_atom2.atom_time = t + 100
        self.assertTrue(nmpd.receive_atom(log_atom2))
        self.assertTrue(nmpd.learn_mode)
        log_atom1.atom_time = t + 200
        self.assertTrue(nmpd.receive_atom(log_atom1))
        self.assertTrue(nmpd.learn_mode)
        log_atom1.atom_time = t + 201
        self.assertTrue(nmpd.receive_atom(log_atom1))
        self.assertFalse(nmpd.learn_mode)

    def test2do_timer(self):
        """Test if the do_timer method is implemented properly."""
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", True, output_logline=False)
        t = time.time()
        nmpd.next_persist_time = t + 400
        self.assertEqual(nmpd.do_timer(t + 200), 200)
        self.assertEqual(nmpd.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(nmpd.do_timer(t + 999), 1)
        self.assertEqual(nmpd.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

    def test3allowlist_event(self):
        """Test if the allowlist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", True, output_logline=False)
        t = round(time.time(), 3)
        analysis = "Analysis.%s"
        log_atom1 = LogAtom(self.fdme1.data, ParserMatch(self.match_element1), t, nmpd)
        nmpd.receive_atom(log_atom1)
        self.assertRaises(Exception, nmpd.allowlist_event, analysis % "NewMatchPathValueDetector", self.output_stream.getvalue(), None)

        # The NewMatchPathDetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, nmpd.allowlist_event, analysis % nmpd.__class__.__name__, self.output_stream.getvalue(), ["random", "Data"])

        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(nmpd.allowlist_event(analysis % nmpd.__class__.__name__, self.match_element1.get_path(), None),
            "Allowlisted path(es) %s in %s." % (self.match_element1.get_path(), analysis % nmpd.__class__.__name__))
        self.assertEqual(nmpd.known_path_set, {"/s1"})

        nmpd.learn_mode = False
        self.assertEqual(nmpd.allowlist_event(analysis % nmpd.__class__.__name__, self.match_element2.get_path(), None),
            "Allowlisted path(es) %s in %s." % (self.match_element2.path, analysis % nmpd.__class__.__name__))
        self.assertEqual(nmpd.known_path_set, {"/s1", "/d1"})

    def test4persistence(self):
        """Test the do_persist and load_persistence_data methods."""
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", True, output_logline=False)
        t = round(time.time(), 3)
        log_atom1 = LogAtom(self.fdme1.data, ParserMatch(self.match_element1), t, nmpd)
        log_atom2 = LogAtom(self.match_context2.match_data, ParserMatch(self.match_element2), t, nmpd)

        self.assertTrue(nmpd.receive_atom(log_atom1))
        self.assertTrue(nmpd.receive_atom(log_atom2))
        self.assertEqual(nmpd.known_path_set, {"/s1", "/d1"})
        nmpd.do_persist()
        with open(nmpd.persistence_file_name, "r") as f:
            self.assertEqual(f.readline(), '["string:/d1", "string:/s1"]')

        nmpd.known_path_set = set()
        nmpd.load_persistence_data()
        self.assertEqual(nmpd.known_path_set, {"/s1", "/d1"})

        other = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False, output_logline=False)
        self.assertEqual(nmpd.known_path_set, other.known_path_set)

    def test5validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, ["default"])
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, None)
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, "")
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, b"Default")
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, True)
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, 123)
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, 123.3)
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, {"id": "Default"})
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, ())
        self.assertRaises(TypeError, NewMatchPathDetector, self.aminer_config, set())

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
