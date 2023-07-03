import unittest
import time
from datetime import datetime
from aminer.analysis.SlidingEventFrequencyDetector import SlidingEventFrequencyDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase


class SlidingEventFrequencyDetectorTest(TestBase):
    """Unittests for the SlidingEventFrequencyDetector."""

    def test1receive_atom(self):
        """
        This test case checks the normal detection of new frequencies. The sEFD is used with one path to be analyzed over four time windows.
        The frequencies do not change a lot in the first time windows, thus no anomalies are generated. Then, value frequencies change and
        anomalies are created in the last time windows. Test if log atoms are processed correctly and the detector is learning
        (learn_mode=True) and stops if learn_mode=False. Test if stop_learning_time and stop_learning_no_anomaly_timestamp are implemented properly.
        """
        # Initialize detector for analyzing values in one path in time windows of 10 seconds
        t = time.time()
        expected_string_first = '%s Frequency exceeds range for the first time\n%s: "None" (%d lines)\n  %s\n\n'
        expected_string = '%s Frequency anomaly detected\n%s: "None" (%d lines)\n  %s\n\n'
        dtf = "%Y-%m-%d %H:%M:%S"
        sefd = SlidingEventFrequencyDetector(aminer_config=self.aminer_config, anomaly_event_handlers=[self.stream_printer_event_handler], window_size=10, set_upper_limit=2, learn_mode=True, output_logline=False)

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

        sefd.receive_atom(log_atom1)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("/value",)]), [t+1])

        sefd.receive_atom(log_atom2)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("/value",)]), [t+1, t+3])

        sefd.receive_atom(log_atom3)
        self.assertEqual(self.output_stream.getvalue(), expected_string_first % (datetime.fromtimestamp(t+7).strftime(dtf), sefd.__class__.__name__, 1, "a"))
        self.reset_output_stream()
        self.assertEqual(list(sefd.counts[("/value",)]), [t+1, t+3, t+7])

        sefd.receive_atom(log_atom4)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("/value",)]), [t+3, t+7, t+13])

        sefd.receive_atom(log_atom5)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("/value",)]), [t+7, t+13, t+17])

        sefd.receive_atom(log_atom6)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("/value",)]), [t+13, t+17, t+18])

        sefd.receive_atom(log_atom7)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("/value",)]), [t+13, t+17, t+18, t+19])

        sefd.receive_atom(log_atom8)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("/value",)]), [t+17, t+18, t+19, t+25])

        sefd.receive_atom(log_atom9)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("/value",)]), [t+17, t+18, t+19, t+25, t+25])

        sefd.receive_atom(log_atom10)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t+25).strftime(dtf), sefd.__class__.__name__, 1, "b"))
        self.reset_output_stream()
        self.assertEqual(list(sefd.counts[("/value",)]), [t+25, t+25, t+35])

        # target_path_list
        sefd = SlidingEventFrequencyDetector(aminer_config=self.aminer_config, anomaly_event_handlers=[self.stream_printer_event_handler], target_path_list=["/value"], window_size=10, set_upper_limit=2, learn_mode=True, output_logline=False)
        # Forward log atoms to detector
        # Log atoms of initial window 1 should not create anomalies and add to counts
        # Input: a; initial time window is started
        # Expected output: frequency of a is 1
        sefd.receive_atom(log_atom1)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("a",)]), [t + 1])

        # Input: b; initial time window is not finished
        # Expected output: frequency of b is 1 added to existing count
        sefd.receive_atom(log_atom2)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("a",)]), [t + 1])
        self.assertEqual(list(sefd.counts[("b",)]), [t + 3])

        # Input: a; initial time window is not finished
        # Expected output: frequency of a is 2 replaces a in existing count
        sefd.receive_atom(log_atom3)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.reset_output_stream()
        self.assertEqual(list(sefd.counts[("a",)]), [t + 1, t + 7])
        self.assertEqual(list(sefd.counts[("b",)]), [t + 3])

        # Time window 2 should not create anomalies since a is in confidence (3 vs 2 occurrences) and b is identical (1 occurrence).
        # Input: a; initial time window is completed, second time window is started
        # Expected output: frequency of a is 1 in new time window count, old count remains unchanged
        sefd.receive_atom(log_atom4)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("a",)]), [t + 7, t + 13])
        self.assertEqual(list(sefd.counts[("b",)]), [t + 3])

        # Input: b; second time window is not finished
        # Expected output: frequency of b is 1 in new time window count, old count remains unchanged
        sefd.receive_atom(log_atom5)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("a",)]), [t + 7, t + 13])
        self.assertEqual(list(sefd.counts[("b",)]), [t + 3, t + 17])

        # Input: a; second time window is not finished
        # Expected output: frequency of a is 3 in new time window count, old count remains unchanged
        sefd.receive_atom(log_atom6)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("a",)]), [t + 13, t + 18])
        self.assertEqual(list(sefd.counts[("b",)]), [t + 3, t + 17])

        # Input: a; second time window is not finished
        # Expected output: frequency of a is 4 in new time window count, old count remains unchanged
        sefd.receive_atom(log_atom7)
        self.assertEqual(self.output_stream.getvalue(), expected_string_first % (datetime.fromtimestamp(t+19).strftime(dtf), sefd.__class__.__name__, 1, "a"))
        self.reset_output_stream()
        self.assertEqual(list(sefd.counts[("a",)]), [t + 13, t + 18, t + 19])
        self.assertEqual(list(sefd.counts[("b",)]), [t + 3, t + 17])

        # Time window 3 should create 2 anomalies since a drops from 3 to 0 and b increases from 1 to 2, which will be reported in window 4.
        # Anomalies are only reported when third time window is known to be completed, which will occur when subsequent atom is received.
        # Input: b; second time window is completed, third time window is started
        # Expected output: frequency of b is 1 in new time window count, old count remains unchanged
        sefd.receive_atom(log_atom8)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(list(sefd.counts[("a",)]), [t + 13, t + 18, t + 19])
        self.assertEqual(list(sefd.counts[("b",)]), [t + 17, t + 25])

        # Input: b; third time window is not finished
        # Expected output: frequency of b is 2 in new time window count, old count remains unchanged
        sefd.receive_atom(log_atom9)
        self.assertEqual(self.output_stream.getvalue(), expected_string_first % (datetime.fromtimestamp(t+25).strftime(dtf), sefd.__class__.__name__, 1, "b"))
        self.reset_output_stream()
        self.assertEqual(list(sefd.counts[("a",)]), [t + 13, t + 18, t + 19])
        self.assertEqual(list(sefd.counts[("b",)]), [t + 17, t + 25, t + 25])

        # Time window 4 should not create anomalies since no log atom is received to evaluate it.
        # Input: a; third time window is completed, fourth time window is started
        # Expected output: Anomalies for unexpected low counts of a (0 instead of 3) and b (2 instead of 1), frequency of a is 1 in new
        # time window count, old count remains unchanged
        sefd.receive_atom(log_atom10)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t+19).strftime(dtf), sefd.__class__.__name__, 1, "a"))
        self.reset_output_stream()
        self.assertEqual(list(sefd.counts[("a",)]), [t + 35])
        self.assertEqual(list(sefd.counts[("b",)]), [t + 17, t + 25, t + 25])

        # stop_learning_time
        sefd = SlidingEventFrequencyDetector(aminer_config=self.aminer_config, anomaly_event_handlers=[self.stream_printer_event_handler], target_path_list=["/value"], window_size=10, set_upper_limit=2, learn_mode=True, output_logline=False, stop_learning_time=100)
        self.assertTrue(sefd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 99
        self.assertTrue(sefd.receive_atom(log_atom1))
        self.assertTrue(sefd.learn_mode)
        log_atom1.atom_time = t + 101
        self.assertTrue(sefd.receive_atom(log_atom1))
        self.assertFalse(sefd.learn_mode)

        # stop_learning_no_anomaly_time
        sefd = SlidingEventFrequencyDetector(aminer_config=self.aminer_config, anomaly_event_handlers=[self.stream_printer_event_handler], target_path_list=["/value"], window_size=10, set_upper_limit=2, learn_mode=True, output_logline=False, stop_learning_no_anomaly_time=100)
        log_atom1.atom_time = t
        self.assertTrue(sefd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 100
        self.assertTrue(sefd.receive_atom(log_atom1))
        self.assertTrue(sefd.learn_mode)
        log_atom2.atom_time = t + 100
        self.assertTrue(sefd.receive_atom(log_atom2))
        self.assertTrue(sefd.learn_mode)
        log_atom1.atom_time = t + 200
        self.assertTrue(sefd.receive_atom(log_atom3))
        self.assertTrue(sefd.learn_mode)
        log_atom1.atom_time = t + 201
        self.assertTrue(sefd.receive_atom(log_atom1))
        self.assertFalse(sefd.learn_mode)

    def test2validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, ["default"], 300)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, None, 300)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, "", 300)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, b"Default", 300)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, True, 300)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, 123, 300)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, 123.3, 300)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, {"id": "Default"}, 300)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, (), 300)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, set(), 300)

        self.assertRaises(ValueError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], -1)
        self.assertRaises(ValueError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 0)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], None)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], b"Default")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], "123")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], {"id": "Default"})
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], ())
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], set())
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 100)
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 100.22)

        self.assertRaises(ValueError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, target_path_list=[""])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, target_path_list="")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, target_path_list=b"Default")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, target_path_list=True)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, target_path_list=123)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, target_path_list=123.3)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, target_path_list={"id": "Default"})
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, target_path_list=())
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, target_path_list=set())
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, target_path_list=[])
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, target_path_list=None)

        self.assertRaises(ValueError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, scoring_path_list=[""])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, scoring_path_list="")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, scoring_path_list=b"Default")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, scoring_path_list=True)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, scoring_path_list=123)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, scoring_path_list=123.3)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, scoring_path_list={"id": "Default"})
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, scoring_path_list=())
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, scoring_path_list=set())
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, scoring_path_list=[])
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, scoring_path_list=None)

        self.assertRaises(ValueError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, window_size=-1)
        self.assertRaises(ValueError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, window_size=0)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, window_size=b"Default")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, window_size="123")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, window_size={"id": "Default"})
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, window_size=["Default"])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, window_size=[])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, window_size=())
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, window_size=set())
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, window_size=100)
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, window_size=0.5)

        self.assertRaises(ValueError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, local_maximum_threshold=-1)
        self.assertRaises(ValueError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, local_maximum_threshold=1.1)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, local_maximum_threshold=b"Default")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, local_maximum_threshold="123")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, local_maximum_threshold={"id": "Default"})
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, local_maximum_threshold=["Default"])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, local_maximum_threshold=[])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, local_maximum_threshold=())
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, local_maximum_threshold=set())
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, local_maximum_threshold=0)
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, local_maximum_threshold=0.5)
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, local_maximum_threshold=1)

        self.assertRaises(ValueError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, persistence_id="")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, persistence_id=None)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, persistence_id=b"Default")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, persistence_id=True)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, persistence_id=123)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, persistence_id=123.22)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, persistence_id={"id": "Default"})
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, persistence_id=["Default"])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, persistence_id=[])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, persistence_id=())
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, persistence_id=set())
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, persistence_id="Default")

        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=b"True")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode="True")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=123)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=123.22)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode={"id": "Default"})
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=["Default"])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=[])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=())
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=set())
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True)

        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, output_logline=None)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, output_logline=b"True")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, output_logline="True")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, output_logline=123)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, output_logline=123.22)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, output_logline={"id": "Default"})
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, output_logline=["Default"])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, output_logline=[])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, output_logline=())
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, output_logline=set())
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, output_logline=True)

        self.assertRaises(ValueError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, ignore_list=[""])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, ignore_list="")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, ignore_list=b"Default")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, ignore_list=True)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, ignore_list=123)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, ignore_list=123.3)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, ignore_list={"id": "Default"})
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, ignore_list=())
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, ignore_list=set())
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, ignore_list=[])
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, ignore_list=None)

        self.assertRaises(ValueError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, constraint_list=[""])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, constraint_list="")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, constraint_list=b"Default")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, constraint_list=True)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, constraint_list=123)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, constraint_list=123.3)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, constraint_list={"id": "Default"})
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, constraint_list=())
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, constraint_list=set())
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, constraint_list=[])
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, constraint_list=None)

        self.assertRaises(ValueError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_time=-1)
        self.assertRaises(ValueError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_time=0)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_time=b"Default")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_time="123")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_time={"id": "Default"})
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_time=["Default"])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_time=[])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_time=())
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_time=set())
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_time=100)
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_time=100.22)

        self.assertRaises(ValueError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_no_anomaly_time=-1)
        self.assertRaises(ValueError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_no_anomaly_time=0)
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_no_anomaly_time=b"Default")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_no_anomaly_time="123")
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_no_anomaly_time={"id": "Default"})
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_no_anomaly_time=["Default"])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_no_anomaly_time=[])
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_no_anomaly_time=())
        self.assertRaises(TypeError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_no_anomaly_time=set())
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_no_anomaly_time=100)
        SlidingEventFrequencyDetector(self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_no_anomaly_time=100.22)

        self.assertRaises(ValueError, SlidingEventFrequencyDetector, self.aminer_config, [self.stream_printer_event_handler], 300, learn_mode=True, stop_learning_time=100, stop_learning_no_anomaly_time=100)


if __name__ == "__main__":
    unittest.main()
