import unittest
from aminer.parsing.ParserMatch import ParserMatch
from aminer.analysis.NewMatchPathValueComboDetector import NewMatchPathValueComboDetector
from aminer.input.LogAtom import LogAtom
import time
from unit.TestBase import TestBase, DummyMatchContext, DummyFixedDataModelElement, DummySequenceModelElement
from datetime import datetime
from aminer.AminerConfig import DEFAULT_PERSISTENCE_PERIOD


class NewMatchPathValueComboDetectorTest(TestBase):
    """Unittests for the NewMatchPathValueComboDetector."""

    match_context = DummyMatchContext(b" pid=25537 uid=2")
    fdme1 = DummyFixedDataModelElement("s1", b" pid=")
    fdme2 = DummyFixedDataModelElement("d1", b"25537")
    seq1 = DummySequenceModelElement("seq", [fdme1, fdme2])
    match_element1 = seq1.get_match_element("", match_context)

    match_context = DummyMatchContext(b"ddd 25538ddd ")
    fdme3 = DummyFixedDataModelElement("s1", b"ddd ")
    fdme4 = DummyFixedDataModelElement("d1", b"25538")
    seq2 = DummySequenceModelElement("seq", [fdme3, fdme4])
    match_element2 = seq2.get_match_element("", match_context)
    match_element3 = fdme3.get_match_element("/seq", match_context)

    def test1receive_atom(self):
        """
        Test if log atoms are processed correctly and the detector is learning (learn_mode=True) and stops if learn_mode=False.
        Test if stop_learning_time and stop_learning_no_anomaly_timestamp are implemented properly.
        """
        expected_string = '%s New value combination(s) detected\n%s: "None" (%d lines)\n  %s\n\n'
        datetime_format_string = "%Y-%m-%d %H:%M:%S"
        # learn_mode = True
        nmpvcd = NewMatchPathValueComboDetector(self.aminer_config, ["/seq/s1", "/seq/d1"], [self.stream_printer_event_handler], learn_mode=True, output_logline=False)
        t = round(time.time(), 3)

        log_atom1 = LogAtom(self.match_element1.match_string, ParserMatch(self.match_element1), t, nmpvcd)
        log_atom2 = LogAtom(self.match_element2.match_string, ParserMatch(self.match_element2), t, nmpvcd)
        log_atom3 = LogAtom(self.match_element3.match_string, ParserMatch(self.match_element3), t, nmpvcd)

        self.assertTrue(nmpvcd.receive_atom(log_atom1))
        self.assertEqual(self.output_stream.getvalue(), expected_string % (
            datetime.fromtimestamp(t).strftime(datetime_format_string), nmpvcd.__class__.__name__, 1, "(b' pid=', b'25537')"))
        self.reset_output_stream()

        # repeating should NOT produce the same result
        self.assertTrue(nmpvcd.receive_atom(log_atom1))
        self.assertEqual(self.output_stream.getvalue(), "")
        self.reset_output_stream()

        # learn_mode = False
        nmpvcd.learn_mode = False
        self.assertTrue(nmpvcd.receive_atom(log_atom2))
        self.assertEqual(self.output_stream.getvalue(), expected_string % (
            datetime.fromtimestamp(t).strftime(datetime_format_string), nmpvcd.__class__.__name__, 1, "(b'ddd ', b'25538')"))
        self.reset_output_stream()

        # repeating should produce the same result
        self.assertTrue(nmpvcd.receive_atom(log_atom2))
        self.assertEqual(self.output_stream.getvalue(), expected_string % (
            datetime.fromtimestamp(t).strftime(datetime_format_string), nmpvcd.__class__.__name__, 1, "(b'ddd ', b'25538')"))
        self.reset_output_stream()

        # allow_missing_values_flag=True
        nmpvcd.allow_missing_values_flag = True
        self.assertTrue(nmpvcd.receive_atom(log_atom3))
        self.assertEqual(self.output_stream.getvalue(), expected_string % (
            datetime.fromtimestamp(t).strftime(datetime_format_string), nmpvcd.__class__.__name__, 1, "(b'ddd ', None)"))

        # stop_learning_time
        nmpvcd = NewMatchPathValueComboDetector(self.aminer_config, ["/seq/s1", "/seq/d1"], [self.stream_printer_event_handler], learn_mode=True, output_logline=False, stop_learning_time=100)
        self.assertTrue(nmpvcd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 99
        self.assertTrue(nmpvcd.receive_atom(log_atom1))
        self.assertTrue(nmpvcd.learn_mode)
        log_atom1.atom_time = t + 101
        self.assertTrue(nmpvcd.receive_atom(log_atom1))
        self.assertFalse(nmpvcd.learn_mode)

        # stop_learning_no_anomaly_time
        nmpvcd = NewMatchPathValueComboDetector(self.aminer_config, ["/seq/s1", "/seq/d1"], [self.stream_printer_event_handler], learn_mode=True, output_logline=False, stop_learning_no_anomaly_time=100)
        log_atom1.atom_time = t
        self.assertTrue(nmpvcd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 100
        self.assertTrue(nmpvcd.receive_atom(log_atom1))
        self.assertTrue(nmpvcd.learn_mode)
        log_atom2.atom_time = t + 100
        self.assertTrue(nmpvcd.receive_atom(log_atom2))
        self.assertTrue(nmpvcd.learn_mode)
        log_atom1.atom_time = t + 200
        self.assertTrue(nmpvcd.receive_atom(log_atom1))
        self.assertTrue(nmpvcd.learn_mode)
        log_atom1.atom_time = t + 201
        self.assertTrue(nmpvcd.receive_atom(log_atom1))
        self.assertFalse(nmpvcd.learn_mode)

    def test2do_timer(self):
        """Test if the do_timer method is implemented properly."""
        nmpvcd = NewMatchPathValueComboDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, output_logline=False)
        t = time.time()
        nmpvcd.next_persist_time = t + 400
        self.assertEqual(nmpvcd.do_timer(t + 200), 200)
        self.assertEqual(nmpvcd.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(nmpvcd.do_timer(t + 999), 1)
        self.assertEqual(nmpvcd.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

    def test3allowlist_event(self):
        """Test if the allowlist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        nmpvcd = NewMatchPathValueComboDetector(self.aminer_config, ["/seq/s1", "/seq/d1"], [self.stream_printer_event_handler], learn_mode=True, output_logline=False)
        t = round(time.time(), 3)
        analysis = "Analysis.%s"
        value = b"value"
        value2 = b"value2"
        log_atom1 = LogAtom(self.match_element1.match_string, ParserMatch(self.match_element1), t, nmpvcd)
        nmpvcd.receive_atom(log_atom1)
        self.assertRaises(Exception, nmpvcd.allowlist_event, analysis % "NewMatchPathDetector", self.output_stream.getvalue(), None)

        # The NewMatchPathValueComboDetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, nmpvcd.allowlist_event, analysis % nmpvcd.__class__.__name__, self.output_stream.getvalue(), ["random", "Data"])

        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(nmpvcd.allowlist_event(analysis % nmpvcd.__class__.__name__, (value, value2), None),
            "Allowlisted path(es) %s with %s." % ("/seq/s1, /seq/d1", (value, value2)))
        self.assertEqual(nmpvcd.known_values_set, {(b" pid=", b"25537"), (value, value2)})

        self.assertRaises(TypeError, nmpvcd.allowlist_event, analysis % nmpvcd.__class__.__name__, (value, None), None)

        # allow_missing_values_flag = True
        nmpvcd.allow_missing_values_flag = True
        self.assertEqual(nmpvcd.allowlist_event(analysis % nmpvcd.__class__.__name__, (value, None), None),
            "Allowlisted path(es) %s with %s." % ("/seq/s1, /seq/d1", (value, None)))
        self.assertEqual(nmpvcd.known_values_set, {(b" pid=", b"25537"), (value, value2), (value, None)})

    def test4persistence(self):
        """Test the do_persist and load_persistence_data methods."""
        nmpvcd = NewMatchPathValueComboDetector(self.aminer_config, ["/seq/s1", "/seq/d1"], [self.stream_printer_event_handler], learn_mode=True, output_logline=False)
        t = round(time.time(), 3)
        log_atom1 = LogAtom(self.match_element1.match_string, ParserMatch(self.match_element1), t, nmpvcd)
        log_atom2 = LogAtom(self.match_element2.match_string, ParserMatch(self.match_element2), t, nmpvcd)

        self.assertTrue(nmpvcd.receive_atom(log_atom1))
        self.assertTrue(nmpvcd.receive_atom(log_atom2))
        self.assertEqual(nmpvcd.known_values_set, {(b"ddd ", b"25538"), (b" pid=", b"25537")})
        nmpvcd.do_persist()
        with open(nmpvcd.persistence_file_name, "r") as f:
            self.assertEqual(f.read(), '[["bytes: pid=", "bytes:25537"], ["bytes:ddd ", "bytes:25538"]]')

        nmpvcd.known_values_set = set()
        nmpvcd.load_persistence_data()
        self.assertEqual(nmpvcd.known_values_set, {(b"ddd ", b"25538"), (b" pid=", b"25537")})

        other = NewMatchPathValueComboDetector(self.aminer_config, [self.match_element1.path, self.match_element2.path], [self.stream_printer_event_handler])
        self.assertEqual(nmpvcd.known_values_set, other.known_values_set)

    def test5validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(ValueError, NewMatchPathValueComboDetector, self.aminer_config, [""], [self.stream_printer_event_handler])
        self.assertRaises(ValueError, NewMatchPathValueComboDetector, self.aminer_config, [], [self.stream_printer_event_handler])
        self.assertRaises(ValueError, NewMatchPathValueComboDetector, self.aminer_config, None, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, "", [self.stream_printer_event_handler])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, b"Default", [self.stream_printer_event_handler])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, True, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, 123, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, 123.3, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, {"id": "Default"}, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, (), [self.stream_printer_event_handler])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, set(), [self.stream_printer_event_handler])

        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], ["default"])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], None)
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], "")
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], b"Default")
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], True)
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], 123)
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], 123.3)
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], {"id": "Default"})
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], ())
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], set())

        self.assertRaises(ValueError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id="")
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=None)
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=b"Default")
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=True)
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=123)
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=123.22)
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id={"id": "Default"})
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=["Default"])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=[])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=())
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=set())
        NewMatchPathValueComboDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id="Default")

        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], allow_missing_values_flag=b"True")
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], allow_missing_values_flag="True")
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], allow_missing_values_flag=123)
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], allow_missing_values_flag=123.22)
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], allow_missing_values_flag={"id": "Default"})
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], allow_missing_values_flag=["Default"])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], allow_missing_values_flag=[])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], allow_missing_values_flag=())
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], allow_missing_values_flag=set())
        NewMatchPathValueComboDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], allow_missing_values_flag=True)

        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=b"True")
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode="True")
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=123)
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=123.22)
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode={"id": "Default"})
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=["Default"])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=[])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=())
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=set())
        NewMatchPathValueComboDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True)

        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=None)
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=b"True")
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline="True")
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=123)
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=123.22)
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline={"id": "Default"})
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=["Default"])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=[])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=())
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=set())
        NewMatchPathValueComboDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=True)

        self.assertRaises(ValueError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=-1)
        self.assertRaises(ValueError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=0)
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=b"Default")
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time="123")
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time={"id": "Default"})
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=["Default"])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=[])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=())
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=set())
        NewMatchPathValueComboDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100)
        NewMatchPathValueComboDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100.22)

        self.assertRaises(ValueError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=-1)
        self.assertRaises(ValueError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=0)
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=b"Default")
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time="123")
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time={"id": "Default"})
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=["Default"])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=[])
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=())
        self.assertRaises(TypeError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=set())
        NewMatchPathValueComboDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=100)
        NewMatchPathValueComboDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=100.22)

        self.assertRaises(ValueError, NewMatchPathValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100, stop_learning_no_anomaly_time=100)


if __name__ == "__main__":
    unittest.main()
