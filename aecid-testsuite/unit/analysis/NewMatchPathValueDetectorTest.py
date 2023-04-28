import unittest
from aminer.analysis.NewMatchPathValueDetector import NewMatchPathValueDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase, DummyMatchContext, DummyFixedDataModelElement
import time
from datetime import datetime
from aminer.AminerConfig import DEFAULT_PERSISTENCE_PERIOD


class NewMatchPathValueDetectorTest(TestBase):
    """Unittests for the NewMatchPathValueDetector."""

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
        expected_string = '%s New value(s) detected\n%s: "None" (%d lines)\n  %s\n\n'
        datetime_format_string = "%Y-%m-%d %H:%M:%S"
        # learn_mode = True
        nmpvd = NewMatchPathValueDetector(self.aminer_config, [self.match_element1.path, self.match_element2.path], [self.stream_printer_event_handler], learn_mode=True, output_logline=False)
        t = round(time.time(), 3)

        log_atom1 = LogAtom(self.fdme1.data, ParserMatch(self.match_element1), t, nmpvd)
        log_atom2 = LogAtom(self.match_context2.match_data, ParserMatch(self.match_element2), t, nmpvd)

        self.assertTrue(nmpvd.receive_atom(log_atom1))
        self.assertEqual(self.output_stream.getvalue(), expected_string % (
            datetime.fromtimestamp(t).strftime(datetime_format_string), nmpvd.__class__.__name__, 1, "{'/s1': ' pid='}"))
        self.reset_output_stream()

        # repeating should NOT produce the same result
        self.assertTrue(nmpvd.receive_atom(log_atom1))
        self.assertEqual(self.output_stream.getvalue(), "")
        self.reset_output_stream()

        # learn_mode = False
        nmpvd.learn_mode = False
        self.assertTrue(nmpvd.receive_atom(log_atom2))
        self.assertEqual(self.output_stream.getvalue(), expected_string % (
            datetime.fromtimestamp(t).strftime(datetime_format_string), nmpvd.__class__.__name__, 1, "{'/d1': '25537'}"))
        self.reset_output_stream()

        # repeating should produce the same result
        self.assertTrue(nmpvd.receive_atom(log_atom2))
        self.assertEqual(self.output_stream.getvalue(), expected_string % (
            datetime.fromtimestamp(t).strftime(datetime_format_string), nmpvd.__class__.__name__, 1, "{'/d1': '25537'}"))

        # stop_learning_time
        nmpvd = NewMatchPathValueDetector(self.aminer_config, [self.match_element1.path, self.match_element2.path], [self.stream_printer_event_handler], learn_mode=True, output_logline=False, stop_learning_time=100)
        self.assertTrue(nmpvd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 99
        self.assertTrue(nmpvd.receive_atom(log_atom1))
        self.assertTrue(nmpvd.learn_mode)
        log_atom1.atom_time = t + 101
        self.assertTrue(nmpvd.receive_atom(log_atom1))
        self.assertFalse(nmpvd.learn_mode)

        # stop_learning_no_anomaly_time
        nmpvd = NewMatchPathValueDetector(self.aminer_config, [self.match_element1.path, self.match_element2.path], [self.stream_printer_event_handler], learn_mode=True, output_logline=False, stop_learning_no_anomaly_time=100)
        log_atom1.atom_time = t
        self.assertTrue(nmpvd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 100
        self.assertTrue(nmpvd.receive_atom(log_atom1))
        self.assertTrue(nmpvd.learn_mode)
        log_atom2.atom_time = t + 100
        self.assertTrue(nmpvd.receive_atom(log_atom2))
        self.assertTrue(nmpvd.learn_mode)
        log_atom1.atom_time = t + 200
        self.assertTrue(nmpvd.receive_atom(log_atom1))
        self.assertTrue(nmpvd.learn_mode)
        log_atom1.atom_time = t + 201
        self.assertTrue(nmpvd.receive_atom(log_atom1))
        self.assertFalse(nmpvd.learn_mode)

    def test2do_timer(self):
        """Test if the do_timer method is implemented properly."""
        nmpvd = NewMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, output_logline=False)
        t = time.time()
        nmpvd.next_persist_time = t + 400
        self.assertEqual(nmpvd.do_timer(t + 200), 200)
        self.assertEqual(nmpvd.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(nmpvd.do_timer(t + 999), 1)
        self.assertEqual(nmpvd.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

    def test3allowlist_event(self):
        """Test if the allowlist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        nmpvd = NewMatchPathValueDetector(self.aminer_config, [self.match_element1.path], [self.stream_printer_event_handler], learn_mode=True, output_logline=False)
        t = round(time.time(), 3)
        analysis = "Analysis.%s"
        value = b"value"
        value2 = b"value2"
        log_atom1 = LogAtom(self.fdme1.data, ParserMatch(self.match_element1), t, nmpvd)
        nmpvd.receive_atom(log_atom1)
        self.assertRaises(Exception, nmpvd.allowlist_event, analysis % "NewMatchPathDetector", self.output_stream.getvalue(), None)

        # The NewMatchPathValueDetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, nmpvd.allowlist_event, analysis % nmpvd.__class__.__name__, self.output_stream.getvalue(), ["random", "Data"])

        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(nmpvd.allowlist_event(analysis % nmpvd.__class__.__name__, value, None),
            "Allowlisted path(es) %s with %s." % (self.match_element1.path, value.decode()))
        self.assertEqual(nmpvd.known_values_set, {b" pid=", b"value"})

        nmpvd.learn_mode = False
        self.assertEqual(nmpvd.allowlist_event(analysis % nmpvd.__class__.__name__, value2, None),
            "Allowlisted path(es) %s with %s." % (self.match_element1.path, value2.decode()))
        self.assertEqual(nmpvd.known_values_set, {b" pid=", b"value", b"value2"})

    def test4persistence(self):
        """Test the do_persist and load_persistence_data methods."""
        nmpvd = NewMatchPathValueDetector(self.aminer_config, [self.match_element1.path, self.match_element2.path], [self.stream_printer_event_handler], learn_mode=True, output_logline=False)
        t = round(time.time(), 3)
        log_atom1 = LogAtom(self.fdme1.data, ParserMatch(self.match_element1), t, nmpvd)
        log_atom2 = LogAtom(self.match_context2.match_data, ParserMatch(self.match_element2), t, nmpvd)

        self.assertTrue(nmpvd.receive_atom(log_atom1))
        self.assertTrue(nmpvd.receive_atom(log_atom2))
        self.assertEqual(nmpvd.known_values_set, {b" pid=", b"25537"})
        nmpvd.do_persist()
        with open(nmpvd.persistence_file_name, "r") as f:
            self.assertEqual(f.readline(), '["bytes: pid=", "bytes:25537"]')

        nmpvd.known_values_set = set()
        nmpvd.load_persistence_data()
        self.assertEqual(nmpvd.known_values_set, {b" pid=", b"25537"})

        other = NewMatchPathValueDetector(self.aminer_config, [self.match_element1.path, self.match_element2.path], [self.stream_printer_event_handler])
        self.assertEqual(nmpvd.known_values_set, other.known_values_set)

    def test5validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(ValueError, NewMatchPathValueDetector, self.aminer_config, [""], [self.stream_printer_event_handler])
        self.assertRaises(ValueError, NewMatchPathValueDetector, self.aminer_config, [], [self.stream_printer_event_handler])
        self.assertRaises(ValueError, NewMatchPathValueDetector, self.aminer_config, None, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, "", [self.stream_printer_event_handler])
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, b"Default", [self.stream_printer_event_handler])
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, True, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, 123, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, 123.3, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, {"id": "Default"}, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, (), [self.stream_printer_event_handler])
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, set(), [self.stream_printer_event_handler])

        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], ["default"])
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], None)
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], "")
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], b"Default")
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], True)
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], 123)
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], 123.3)
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], {"id": "Default"})
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], ())
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], set())

        self.assertRaises(ValueError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id="")
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=None)
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=b"Default")
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=True)
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=123)
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=123.22)
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id={"id": "Default"})
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=["Default"])
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=[])
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=())
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=set())
        NewMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id="Default")

        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=b"True")
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode="True")
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=123)
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=123.22)
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode={"id": "Default"})
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=["Default"])
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=[])
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=())
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=set())
        NewMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True)

        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=None)
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=b"True")
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline="True")
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=123)
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=123.22)
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline={"id": "Default"})
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=["Default"])
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=[])
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=())
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=set())
        NewMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=True)

        self.assertRaises(ValueError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=-1)
        self.assertRaises(ValueError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=0)
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=b"Default")
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time="123")
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time={"id": "Default"})
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=["Default"])
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=[])
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=())
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=set())
        NewMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100)
        NewMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100.22)

        self.assertRaises(ValueError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=-1)
        self.assertRaises(ValueError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=0)
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=b"Default")
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time="123")
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time={"id": "Default"})
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=["Default"])
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=[])
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=())
        self.assertRaises(TypeError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=set())
        NewMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=100)
        NewMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=100.22)

        self.assertRaises(ValueError, NewMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100, stop_learning_no_anomaly_time=100)


if __name__ == "__main__":
    unittest.main()
