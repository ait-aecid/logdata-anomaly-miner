import unittest
import time
from datetime import datetime
from aminer.analysis.EventFrequencyDetector import EventFrequencyDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase
from aminer.AminerConfig import DEFAULT_PERSISTENCE_PERIOD


class EventFrequencyDetectorTest(TestBase):
    """Unittests for the EventFrequencyDetector."""

    def test1receive_atom(self):
        """
        This test case checks the normal detection of new frequencies. The EFD is used with one path to be analyzed over four time windows.
        The frequencies do not change a lot in the first time windows, thus no anomalies are generated. Then, value frequencies change and
        anomalies are created in the last time windows. Test if log atoms are processed correctly and the detector is learning
        (learn_mode=True) and stops if learn_mode=False. Test if stop_learning_time and stop_learning_no_anomaly_timestamp are implemented properly.
        """
        # Initialize detector for analyzing values in one path in time windows of 10 seconds
        t = time.time()
        expected_string = '%s Frequency anomaly detected\n%s: "None" (%d lines)\n  %s\n\n'
        dtf = "%Y-%m-%d %H:%M:%S"
        efd = EventFrequencyDetector(aminer_config=self.aminer_config, anomaly_event_handlers=[self.stream_printer_event_handler], window_size=10,
            num_windows=1, confidence_factor=0.51, empty_window_warnings=True, learn_mode=True, output_logline=False)

        # Prepare log atoms that represent different amounts of values a, b over time
        # Four time windows are used. The first time window is used for initialization. The
        # second time window represents normal behavior, i.e., the frequencies do not change
        # too much and no anomalies should be generated. The third window contains changes
        # of value frequencies and thus anomalies should be generated. The fourth time window
        # only has the purpose of marking the end of the third time window.
        # The following log atoms are created:
        #  window 1:
        #   value a: 2 times
        #   value b: 1 time
        #  window 2:
        #   value a: 3 times
        #   value b: 1 time
        #  window 3:
        #   value a: 0 times
        #   value b: 2 times
        #  window 4:
        #   value a: 1 time
        # Start of window 1:
        log_atom1 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+1, None)
        log_atom2 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"b", b"b", None)), t+3, None)
        log_atom3 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+7, None)

        # Start of window 2:
        log_atom4 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+13, None)
        log_atom5 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"b", b"b", None)), t+17, None)
        log_atom6 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+18, None)
        log_atom7 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+19, None)

        # Start of window 3:
        log_atom8 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"b", b"b", None)), t+25, None)
        log_atom9 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"b", b"b", None)), t+25, None)

        # Start of window 4:
        log_atom10 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+35, None)

        efd.receive_atom(log_atom1)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [1]})

        efd.receive_atom(log_atom2)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [2]})

        efd.receive_atom(log_atom3)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [3]})

        efd.receive_atom(log_atom4)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [3, 1]})

        efd.receive_atom(log_atom5)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [3, 2]})

        efd.receive_atom(log_atom6)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [3, 3]})

        efd.receive_atom(log_atom7)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [3, 4]})

        efd.receive_atom(log_atom8)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [3, 4, 1]})

        efd.receive_atom(log_atom9)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [3, 4, 2]})

        efd.receive_atom(log_atom10)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [4, 2, 1]})

        # target_path_list
        efd = EventFrequencyDetector(aminer_config=self.aminer_config, anomaly_event_handlers=[self.stream_printer_event_handler], target_path_list=["/value"], window_size=10,
            num_windows=1, confidence_factor=0.51, empty_window_warnings=True, learn_mode=True, output_logline=False)
        # Forward log atoms to detector
        # Log atoms of initial window 1 should not create anomalies and add to counts
        # Input: a; initial time window is started
        # Expected output: frequency of a is 1
        efd.receive_atom(log_atom1)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("a",): [1]})

        # Input: b; initial time window is not finished
        # Expected output: frequency of b is 1 added to existing count
        efd.receive_atom(log_atom2)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("a",): [1], ("b",): [1]})

        # Input: a; initial time window is not finished
        # Expected output: frequency of a is 2 replaces a in existing count
        efd.receive_atom(log_atom3)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("a",): [2], ("b",): [1]})

        # Time window 2 should not create anomalies since a is in confidence (3 vs 2 occurrences) and b is identical (1 occurrence).
        # Input: a; initial time window is completed, second time window is started
        # Expected output: frequency of a is 1 in new time window count, old count remains unchanged
        efd.receive_atom(log_atom4)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("a",): [2, 1], ("b",): [1, 0]})

        # Input: b; second time window is not finished
        # Expected output: frequency of b is 1 in new time window count, old count remains unchanged
        efd.receive_atom(log_atom5)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("a",): [2, 1], ("b",): [1, 1]})

        # Input: a; second time window is not finished
        # Expected output: frequency of a is 3 in new time window count, old count remains unchanged
        efd.receive_atom(log_atom6)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("a",): [2, 2], ("b",): [1, 1]})

        # Input: a; second time window is not finished
        # Expected output: frequency of a is 4 in new time window count, old count remains unchanged
        efd.receive_atom(log_atom7)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("a",): [2, 3], ("b",): [1, 1]})

        # Time window 3 should create 2 anomalies since a drops from 3 to 0 and b increases from 1 to 2, which will be reported in window 4.
        # Anomalies are only reported when third time window is known to be completed, which will occur when subsequent atom is received.
        # Input: b; second time window is completed, third time window is started
        # Expected output: frequency of b is 1 in new time window count, old count remains unchanged
        efd.receive_atom(log_atom8)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("a",): [2, 3, 0], ("b",): [1, 1, 1]})

        # Input: b; third time window is not finished
        # Expected output: frequency of b is 2 in new time window count, old count remains unchanged
        efd.receive_atom(log_atom9)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("a",): [2, 3, 0], ("b",): [1, 1, 2]})

        # Time window 4 should not create anomalies since no log atom is received to evaluate it.
        # Input: a; third time window is completed, fourth time window is started
        # Expected output: Anomalies for unexpected low counts of a (0 instead of 3) and b (2 instead of 1), frequency of a is 1 in new
        # time window count, old count remains unchanged
        efd.receive_atom(log_atom10)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t+35).strftime(dtf), efd.__class__.__name__, 1, "a")
                         + expected_string % (datetime.fromtimestamp(t+25).strftime(dtf), efd.__class__.__name__, 1, "b"))
        self.assertEqual(efd.counts, {("a",): [3, 0, 1], ("b",): [1, 2, 0]})
        self.reset_output_stream()

        # unique_path_list
        efd = EventFrequencyDetector(aminer_config=self.aminer_config, anomaly_event_handlers=[self.stream_printer_event_handler], unique_path_list=["/value"], window_size=10,
            num_windows=1, confidence_factor=0.51, empty_window_warnings=True, learn_mode=True, output_logline=False)
        efd.receive_atom(log_atom1)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [1]})

        efd.receive_atom(log_atom2)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [2]})

        efd.receive_atom(log_atom3)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [3]})

        efd.receive_atom(log_atom4)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [3, 1]})

        efd.receive_atom(log_atom5)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [3, 2]})

        efd.receive_atom(log_atom6)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [3, 2]})

        efd.receive_atom(log_atom7)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [3, 2]})

        efd.receive_atom(log_atom8)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [3, 2, 1]})

        efd.receive_atom(log_atom9)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [3, 2, 1]})

        efd.receive_atom(log_atom10)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(efd.counts, {("/value",): [2, 1, 1]})

        # stop_learning_time
        efd = EventFrequencyDetector(aminer_config=self.aminer_config, anomaly_event_handlers=[self.stream_printer_event_handler], target_path_list=["/value"], window_size=10, num_windows=1,
            confidence_factor=0.51, empty_window_warnings=True, learn_mode=True, output_logline=False, stop_learning_time=100)
        self.assertTrue(efd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 99
        self.assertTrue(efd.receive_atom(log_atom1))
        self.assertTrue(efd.learn_mode)
        log_atom1.atom_time = t + 101
        self.assertTrue(efd.receive_atom(log_atom1))
        self.assertFalse(efd.learn_mode)

        # stop_learning_no_anomaly_time
        efd = EventFrequencyDetector(aminer_config=self.aminer_config, anomaly_event_handlers=[self.stream_printer_event_handler], target_path_list=["/value"], window_size=10, num_windows=1,
            confidence_factor=0.51, empty_window_warnings=True, learn_mode=True, output_logline=False, stop_learning_no_anomaly_time=100)
        log_atom1.atom_time = t
        self.assertTrue(efd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 100
        self.assertTrue(efd.receive_atom(log_atom1))
        self.assertTrue(efd.learn_mode)
        log_atom2.atom_time = t + 100
        self.assertTrue(efd.receive_atom(log_atom2))
        self.assertTrue(efd.learn_mode)
        log_atom1.atom_time = t + 200
        self.assertTrue(efd.receive_atom(log_atom3))
        self.assertTrue(efd.learn_mode)
        log_atom1.atom_time = t + 201
        self.assertTrue(efd.receive_atom(log_atom1))
        self.assertFalse(efd.learn_mode)

    def test2do_timer(self):
        """Test if the do_timer method is implemented properly."""
        efd = EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler])
        t = time.time()
        efd.next_persist_time = t + 400
        self.assertEqual(efd.do_timer(t + 200), 200)
        self.assertEqual(efd.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(efd.do_timer(t + 999), 1)
        self.assertEqual(efd.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

    def test3allowlist_event(self):
        """Test if the allowlist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        efd = EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler])
        analysis = "Analysis.%s"
        self.assertRaises(Exception, efd.allowlist_event, analysis % "NewMatchPathValueDetector", self.output_stream.getvalue(), None)

        # The EventFrequencyDetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, efd.allowlist_event, analysis % efd.__class__.__name__, self.output_stream.getvalue(), ["random", "Data"])

        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(efd.allowlist_event(analysis % efd.__class__.__name__, "/s1", None), "Allowlisted path %s in %s." % ("/s1", analysis % efd.__class__.__name__))
        self.assertEqual(efd.constraint_list, ["/s1"])

        efd.learn_mode = False
        self.assertEqual(efd.allowlist_event(analysis % efd.__class__.__name__, "/d1", None), "Allowlisted path %s in %s." % ("/d1", analysis % efd.__class__.__name__))
        self.assertEqual(efd.constraint_list, ["/s1", "/d1"])

    def test4blocklist_event(self):
        """Test if the blocklist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        efd = EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler])
        analysis = "Analysis.%s"
        self.assertRaises(Exception, efd.blocklist_event, analysis % "NewMatchPathValueDetector", self.output_stream.getvalue(), None)

        # The EventFrequencyDetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, efd.blocklist_event, analysis % efd.__class__.__name__, self.output_stream.getvalue(), ["random", "Data"])

        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(efd.blocklist_event(analysis % efd.__class__.__name__, "/s1", None), "Blocklisted path %s in %s." % ("/s1", analysis % efd.__class__.__name__))
        self.assertEqual(efd.ignore_list, ["/s1"])

        efd.learn_mode = False
        self.assertEqual(efd.blocklist_event(analysis % efd.__class__.__name__, "/d1", None), "Blocklisted path %s in %s." % ("/d1", analysis % efd.__class__.__name__))
        self.assertEqual(efd.ignore_list, ["/s1", "/d1"])

    def test5persistence(self):
        """Test the do_persist and load_persistence_data methods."""
        t = time.time()
        efd = EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], empty_window_warnings=True, learn_mode=True)
        log_atom1 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t + 1, None)
        log_atom2 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"b", b"b", None)), t + 3, None)
        log_atom3 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t + 7, None)

        # Start of window 2:
        log_atom4 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t + 13, None)
        log_atom5 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"b", b"b", None)), t + 17, None)
        log_atom6 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t + 18, None)
        log_atom7 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t + 19, None)

        # Start of window 3:
        log_atom8 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"b", b"b", None)), t + 25, None)
        log_atom9 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"b", b"b", None)), t + 25, None)

        # Start of window 4:
        log_atom10 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t + 35, None)
        efd.receive_atom(log_atom1)
        efd.receive_atom(log_atom2)
        efd.receive_atom(log_atom3)
        efd.receive_atom(log_atom4)
        efd.receive_atom(log_atom5)
        efd.receive_atom(log_atom6)
        efd.receive_atom(log_atom7)
        efd.receive_atom(log_atom8)
        efd.receive_atom(log_atom9)
        efd.receive_atom(log_atom10)
        efd.do_persist()
        with open(efd.persistence_file_name, "r") as f:
            self.assertEqual(f.read(), '[[["string:/value"], []]]')

        self.assertEqual(efd.counts, {("/value",): [10]})
        self.assertEqual(efd.scoring_value_list, {})
        efd.counts = {}
        efd.load_persistence_data()
        self.assertEqual(efd.counts, {("/value",): [0]})

        other = EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], empty_window_warnings=True, learn_mode=True)
        self.assertEqual(other.counts, efd.counts)
        self.assertEqual(other.scoring_value_list, efd.scoring_value_list)

    def test6validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, ["default"])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, None)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, "")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, b"Default")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, True)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, 123)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, 123.3)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, {"id": "Default"})
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, ())
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, set())

        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=[""])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list="")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=b"Default")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=True)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=123)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=123.3)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list={"id": "Default"})
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=())
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=set())
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], target_path_list=[])
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], target_path_list=None)

        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], scoring_path_list=[""])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], scoring_path_list="")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], scoring_path_list=b"Default")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], scoring_path_list=True)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], scoring_path_list=123)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], scoring_path_list=123.3)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], scoring_path_list={"id": "Default"})
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], scoring_path_list=())
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], scoring_path_list=set())
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], scoring_path_list=[])
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], scoring_path_list=None)

        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], unique_path_list=[""])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], unique_path_list="")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], unique_path_list=b"Default")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], unique_path_list=True)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], unique_path_list=123)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], unique_path_list=123.3)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], unique_path_list={"id": "Default"})
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], unique_path_list=())
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], unique_path_list=set())
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], unique_path_list=[])
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], unique_path_list=None)

        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], window_size=-1)
        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], window_size=0)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], window_size=b"Default")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], window_size="123")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], window_size={"id": "Default"})
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], window_size=["Default"])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], window_size=[])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], window_size=())
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], window_size=set())
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], window_size=100)
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], window_size=0.5)

        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows=-1)
        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows=0)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows=100.22)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows=b"Default")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows="123")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows={"id": "Default"})
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows=["Default"])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows=[])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows=())
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows=set())
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], num_windows=100)

        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], confidence_factor=-1)
        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], confidence_factor=1.1)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], confidence_factor=b"Default")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], confidence_factor="123")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], confidence_factor={"id": "Default"})
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], confidence_factor=["Default"])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], confidence_factor=[])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], confidence_factor=())
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], confidence_factor=set())
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], confidence_factor=0)
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], confidence_factor=0.5)
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], confidence_factor=1)

        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], empty_window_warnings=b"True")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], empty_window_warnings="True")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], empty_window_warnings=123)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], empty_window_warnings=123.22)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], empty_window_warnings={"id": "Default"})
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], empty_window_warnings=["Default"])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], empty_window_warnings=[])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], empty_window_warnings=())
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], empty_window_warnings=set())
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], empty_window_warnings=True)

        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], early_exceeding_anomaly_output=b"True")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], early_exceeding_anomaly_output="True")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], early_exceeding_anomaly_output=123)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], early_exceeding_anomaly_output=123.22)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], early_exceeding_anomaly_output={"id": "Default"})
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], early_exceeding_anomaly_output=["Default"])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], early_exceeding_anomaly_output=[])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], early_exceeding_anomaly_output=())
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], early_exceeding_anomaly_output=set())
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], early_exceeding_anomaly_output=True)

        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], set_lower_limit=-1)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], set_lower_limit=b"Default")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], set_lower_limit="123")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], set_lower_limit={"id": "Default"})
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], set_lower_limit=["Default"])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], set_lower_limit=[])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], set_lower_limit=())
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], set_lower_limit=set())
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], set_lower_limit=0)
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], set_lower_limit=10.12)

        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], set_upper_limit=-1)
        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], set_upper_limit=0)
        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], set_lower_limit=11, set_upper_limit=10)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], set_upper_limit=b"Default")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], set_upper_limit="123")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], set_upper_limit={"id": "Default"})
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], set_upper_limit=["Default"])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], set_upper_limit=[])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], set_upper_limit=())
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], set_upper_limit=set())
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], set_upper_limit=10.12)

        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id="")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=None)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=b"Default")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=True)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=123)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=123.22)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id={"id": "Default"})
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=["Default"])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=[])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=())
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=set())
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], persistence_id="Default")

        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=b"True")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode="True")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=123)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=123.22)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode={"id": "Default"})
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=["Default"])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=[])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=())
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=set())
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True)

        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=None)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=b"True")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline="True")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=123)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=123.22)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline={"id": "Default"})
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=["Default"])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=[])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=())
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=set())
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], output_logline=True)

        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=[""])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list="")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=b"Default")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=True)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=123)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=123.3)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list={"id": "Default"})
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=())
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=set())
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], ignore_list=[])
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], ignore_list=None)

        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=[""])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list="")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=b"Default")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=True)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=123)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=123.3)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list={"id": "Default"})
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=())
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=set())
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], constraint_list=[])
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], constraint_list=None)

        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=-1)
        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=0)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=b"Default")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time="123")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time={"id": "Default"})
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=["Default"])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=[])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=())
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=set())
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100)
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100.22)

        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=-1)
        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=0)
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=b"Default")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time="123")
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time={"id": "Default"})
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=["Default"])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=[])
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=())
        self.assertRaises(TypeError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=set())
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=100)
        EventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=100.22)

        self.assertRaises(ValueError, EventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100, stop_learning_no_anomaly_time=100)

    def test2_seasonal_frequency_detection(self):
        """
        Test for periodically changing frequencies
        """
        description = "Test2EventFrequencyDetector"

        # Initialize detector for analyzing values in one path in time windows of 10 seconds
        test_handler = TestHandler()
        event_frequency_detector = EventFrequencyDetector(aminer_config=self.aminer_config, anomaly_event_handlers=[test_handler],
                                                          target_path_list=['/value'], window_size=10, num_windows=100,
                                                          confidence_factor=0.51, empty_window_warnings=True, persistence_id='Default',
                                                          learn_mode=True, output_logline=True, season=20)
        self.analysis_context.register_component(event_frequency_detector, description)

        # Windows have 1 and 2 atoms alternatingly; the season is thus 2 and expected atom frequencies can be predicted exactly.
        # The anomaly is that in window 6, only 1 atom occurs although 2 should occur following the sequence.
        # The anomaly is reported by the log atom in window 7 that concludes window 6.
        # The following log atoms are created:
        #  window 1:
        #   value a: 1 times
        #  window 2:
        #   value a: 2 time
        #  window 3:
        #   value a: 1 time
        #  window 4:
        #   value a: 2 times
        #  window 5:
        #   value a: 1 time
        #  window 6:
        #   value a: 1 time
        #  window 7:
        #   value a: 1 time
        m_1 = MatchElement('/value', b'a', b'a', None)
        parser_match_1 = ParserMatch(m_1)
        log_atom_1 = LogAtom(b'a', parser_match_1, 1, None)

        m_2 = MatchElement('/value', b'a', b'a', None)
        parser_match_2 = ParserMatch(m_2)
        log_atom_2 = LogAtom(b'a', parser_match_2, 15, None)

        m_3 = MatchElement('/value', b'a', b'a', None)
        parser_match_3 = ParserMatch(m_3)
        log_atom_3 = LogAtom(b'a', parser_match_3, 16, None)

        m_4 = MatchElement('/value', b'a', b'a', None)
        parser_match_4 = ParserMatch(m_4)
        log_atom_4 = LogAtom(b'a', parser_match_4, 25, None)

        m_6 = MatchElement('/value', b'a', b'a', None)
        parser_match_6 = ParserMatch(m_6)
        log_atom_6 = LogAtom(b'a', parser_match_6, 35, None)

        m_7 = MatchElement('/value', b'a', b'a', None)
        parser_match_7 = ParserMatch(m_7)
        log_atom_7 = LogAtom(b'a', parser_match_7, 36, None)

        m_8 = MatchElement('/value', b'a', b'a', None)
        parser_match_8 = ParserMatch(m_8)
        log_atom_8 = LogAtom(b'a', parser_match_8, 45, None)

        m_9 = MatchElement('/value', b'a', b'a', None)
        parser_match_9 = ParserMatch(m_9)
        log_atom_9 = LogAtom(b'a', parser_match_9, 55, None)

        m_10 = MatchElement('/value', b'a', b'a', None)
        parser_match_10 = ParserMatch(m_10)
        log_atom_10 = LogAtom(b'a', parser_match_10, 65, None)

        event_frequency_detector.receive_atom(log_atom_1)
        self.assertFalse(test_handler.anomalies)
        event_frequency_detector.receive_atom(log_atom_2)
        self.assertFalse(test_handler.anomalies)
        event_frequency_detector.receive_atom(log_atom_3)
        self.assertFalse(test_handler.anomalies)
        event_frequency_detector.receive_atom(log_atom_4)
        # Delete anomaly that occurs since second window has 2 but first only 1 atoms. 
        self.assertTrue(test_handler.anomalies)
        test_handler.anomalies = []
        event_frequency_detector.receive_atom(log_atom_6)
        self.assertFalse(test_handler.anomalies)
        event_frequency_detector.receive_atom(log_atom_7)
        self.assertFalse(test_handler.anomalies)
        event_frequency_detector.receive_atom(log_atom_8)
        self.assertFalse(test_handler.anomalies)
        event_frequency_detector.receive_atom(log_atom_9)
        self.assertFalse(test_handler.anomalies)
        event_frequency_detector.receive_atom(log_atom_10)
        self.assertEqual(test_handler.anomalies, [
            {'AnalysisComponent':
                {'AffectedLogAtomPaths': ['/value'],
                 'AffectedLogAtomValues': ['a']}, 'FrequencyData': {
                     'ExpectedLogAtomValuesFrequency': 2.0,
                     'ExpectedLogAtomValuesFrequencyRange': [2.0, 2.0],
                     'LogAtomValuesFrequency': 1,
                     'WindowSize': 10, 'ConfidenceFactor': 0.51, 'Confidence': 0.5
                     }}])


if __name__ == "__main__":
    unittest.main()
