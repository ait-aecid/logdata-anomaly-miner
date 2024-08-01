import unittest
import time
from datetime import datetime
from aminer.analysis.PCADetector import PCADetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase
from aminer.AminerConfig import DEFAULT_PERSISTENCE_PERIOD


class PCADetectorTest(TestBase):
    """Unittests for the PCADetector."""

    def test1receive_atom(self):
        """This test case checks the normal detection of value frequencies using PCA."""
        t = time.time()
        expected_string = '%s PCA anomaly detected\n%s: "None" (%d lines)\n  %s\n\n'
        dtf = "%Y-%m-%d %H:%M:%S"
        # Prepare log atoms that represent different amounts of values a, b over time
        # Five time windows are used. The first three time windows are used for initializing
        # the count matrix. The fourth window is used to verify the anomaly score computation.
        # The fifth time window is only used to mark the end of the fourth time window.
        # The following log atoms are created:
        #  window 1:
        #   value a: 2 times
        #   value b: 1 time
        #  window 2:
        #   value a: 1 times
        #   value b: 1 time
        #  window 3:
        #   value a: 1 time
        #   value b: 0 times
        #  window 4:
        #   value a: 4 time
        #   value b: 1 time
        #  window 5:
        #   value a: 1 time
        # Start of window 1:
        log_atom1 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+1, None)
        log_atom2 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"b", b"b", None)), t+3, None)
        log_atom3 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+7, None)

        # Start of window 2:
        log_atom4 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+13, None)
        log_atom5 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"b", b"b", None)), t+15, None)

        # Start of window 3:
        log_atom6 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+27, None)

        # Start of window 4:
        log_atom7 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+33, None)
        log_atom8 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+34, None)
        log_atom9 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+36, None)
        log_atom10 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+37, None)
        log_atom11 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"b", b"b", None)), t+38, None)

        # Start of window 5:
        log_atom12 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+45, None)

        # Initialize detector for analyzing values in one path in time windows of 10 seconds
        pcad = PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, output_logline=False)
        # Forward log atoms to detector
        # Log atoms of windows 1 to 3 build up the count matrix
        # Input: log atoms of windows 1 to 3
        # Expected output: No anomalies reported
        pcad.receive_atom(log_atom1)
        pcad.receive_atom(log_atom2)
        pcad.receive_atom(log_atom3)
        pcad.receive_atom(log_atom4)
        pcad.receive_atom(log_atom5)
        pcad.receive_atom(log_atom6)
        self.assertEqual(self.output_stream.getvalue(), "")

        # Log atoms of window 4 build the count vector for that window
        # Input: b; log atoms of window 4
        # Expected output: No anomalies reported
        pcad.receive_atom(log_atom7)
        pcad.receive_atom(log_atom8)
        pcad.receive_atom(log_atom9)
        pcad.receive_atom(log_atom10)
        pcad.receive_atom(log_atom11)
        self.assertEqual(self.output_stream.getvalue(), "")
        # At this point, the event count matrix contains the counts from the first three windows
        self.assertEqual(pcad.event_count_matrix, [{"/value": {"a": 2, "b": 1}}, {"/value": {"a": 1, "b": 1}}, {"/value": {"a": 1, "b": 0}}])
        # The count vector contains the counts of the fourth window
        self.assertEqual(pcad.event_count_vector, {"/value": {"a": 4, "b": 1}})

        # Log atom of window 5 triggers comparison of count vector from window 4 with PCA
        # Input: log atoms of window 5
        # Expected output: Anomaly reported on count vector of fourth window
        pcad.receive_atom(log_atom12)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t+45).strftime(dtf), pcad.__class__.__name__, 1, "a"))
        # Event count matrix is shifted by 1 so that window 0 is removed and window 4 is appended
        self.assertEqual(pcad.event_count_matrix, [{"/value": {"a": 1, "b": 1}}, {"/value": {"a": 1, "b": 0}}, {"/value": {"a": 4, "b": 1}}])

        # stop_learning_time
        pcad = PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, output_logline=False, stop_learning_time=100)
        self.assertTrue(pcad.receive_atom(log_atom1))
        log_atom2.atom_time = t + 99
        self.assertTrue(pcad.receive_atom(log_atom2))
        self.assertTrue(pcad.learn_mode)
        log_atom1.atom_time = t + 102
        self.assertTrue(pcad.receive_atom(log_atom1))
        self.assertFalse(pcad.learn_mode)

        # stop_learning_no_anomaly_time
        pcad = PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, output_logline=False, stop_learning_no_anomaly_time=100)
        log_atom1.atom_time = t
        self.assertTrue(pcad.receive_atom(log_atom1))
        log_atom1.atom_time = t + 100
        self.assertTrue(pcad.receive_atom(log_atom1))
        self.assertTrue(pcad.learn_mode)
        log_atom2.atom_time = t + 100
        self.assertTrue(pcad.receive_atom(log_atom2))
        self.assertTrue(pcad.learn_mode)
        log_atom1.atom_time = t + 200
        self.assertTrue(pcad.receive_atom(log_atom3))
        self.assertTrue(pcad.learn_mode)
        log_atom1.atom_time = t + 201
        self.assertTrue(pcad.receive_atom(log_atom1))
        self.assertFalse(pcad.learn_mode)

    def test2do_timer(self):
        """Test if the do_timer method is implemented properly."""
        pcad = PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, output_logline=False)
        t = time.time()
        pcad.next_persist_time = t + 400
        self.assertEqual(pcad.do_timer(t + 200), 200)
        self.assertEqual(pcad.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(pcad.do_timer(t + 999), 1)
        self.assertEqual(pcad.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

    def test3allowlist_event(self):
        """Test if the allowlist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        pcad = PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, output_logline=False)
        analysis = "Analysis.%s"
        self.assertRaises(Exception, pcad.allowlist_event, analysis % "NewMatchPathValueDetector", self.output_stream.getvalue(), None)

        # The PCADetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, pcad.allowlist_event, analysis % pcad.__class__.__name__, self.output_stream.getvalue(), ["random", "Data"])

        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(pcad.allowlist_event(analysis % pcad.__class__.__name__, "/s1", None), "Allowlisted path %s in %s." % ("/s1", analysis % pcad.__class__.__name__))
        self.assertEqual(pcad.constraint_list, ["/s1"])

        pcad.learn_mode = False
        self.assertEqual(pcad.allowlist_event(analysis % pcad.__class__.__name__, "/d1", None), "Allowlisted path %s in %s." % ("/d1", analysis % pcad.__class__.__name__))
        self.assertEqual(pcad.constraint_list, ["/s1", "/d1"])

    def test4blocklist_event(self):
        """Test if the blocklist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        pcad = PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, output_logline=False)
        analysis = "Analysis.%s"
        self.assertRaises(Exception, pcad.blocklist_event, analysis % "NewMatchPathValueDetector", self.output_stream.getvalue(), None)

        # The PCADetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, pcad.blocklist_event, analysis % pcad.__class__.__name__, self.output_stream.getvalue(), ["random", "Data"])

        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(pcad.blocklist_event(analysis % pcad.__class__.__name__, "/s1", None), "Blocklisted path %s in %s." % ("/s1", analysis % pcad.__class__.__name__))
        self.assertEqual(pcad.ignore_list, ["/s1"])

        pcad.learn_mode = False
        self.assertEqual(pcad.blocklist_event(analysis % pcad.__class__.__name__, "/d1", None), "Blocklisted path %s in %s." % ("/d1", analysis % pcad.__class__.__name__))
        self.assertEqual(pcad.ignore_list, ["/s1", "/d1"])

    def test5persistence(self):
        """Test the do_persist and load_persistence_data methods."""
        t = time.time()
        log_atom1 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+1, None)
        log_atom2 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"b", b"b", None)), t+3, None)
        log_atom3 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+7, None)
        log_atom4 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+13, None)
        log_atom5 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"b", b"b", None)), t+15, None)
        log_atom6 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+27, None)
        log_atom7 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+33, None)
        log_atom8 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+34, None)
        log_atom9 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+36, None)
        log_atom10 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+37, None)
        log_atom11 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"b", b"b", None)), t+38, None)
        log_atom12 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t+45, None)

        pcad = PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, output_logline=False)
        pcad.receive_atom(log_atom1)
        pcad.receive_atom(log_atom2)
        pcad.receive_atom(log_atom3)
        pcad.receive_atom(log_atom4)
        pcad.receive_atom(log_atom5)
        pcad.receive_atom(log_atom6)
        pcad.receive_atom(log_atom7)
        pcad.receive_atom(log_atom8)
        pcad.receive_atom(log_atom9)
        pcad.receive_atom(log_atom10)
        pcad.receive_atom(log_atom11)
        pcad.receive_atom(log_atom12)
        pcad.do_persist()
        with open(pcad.persistence_file_name, "r") as f:
            self.assertEqual(f.read(), '[{"string:/value": {"string:a": 1, "string:b": 1}}, {"string:/value": {"string:a": 1, "string:b": 0}}, {"string:/value": {"string:a": 4, "string:b": 1}}]')
        self.assertEqual(pcad.event_count_matrix, [{"/value": {"a": 1, "b": 1}}, {"/value": {"a": 1, "b": 0}}, {"/value": {"a": 4, "b": 1}}])
        pcad.event_count_matrix = []
        pcad.load_persistence_data()
        self.assertEqual(pcad.event_count_matrix, [{"/value": {"a": 1, "b": 1}}, {"/value": {"a": 1, "b": 0}}, {"/value": {"a": 4, "b": 1}}])

        other = PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, output_logline=False)
        self.assertEqual(other.event_count_matrix, pcad.event_count_matrix)

    def test6validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(ValueError, PCADetector, self.aminer_config, [""], [self.stream_printer_event_handler], 10, 2, 0.9, 3)
        self.assertRaises(ValueError, PCADetector, self.aminer_config, None, [self.stream_printer_event_handler], 10, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, "", [self.stream_printer_event_handler], 10, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, b"Default", [self.stream_printer_event_handler], 10, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, True, [self.stream_printer_event_handler], 10, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, 123, [self.stream_printer_event_handler], 10, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, 123.3, [self.stream_printer_event_handler], 10, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, {"id": "Default"}, [self.stream_printer_event_handler], 10, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, (), [self.stream_printer_event_handler], 10, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, set(), [self.stream_printer_event_handler], 10, 2, 0.9, 3)

        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], ["default"], 10, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], None, 10, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], "", 10, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], b"Default", 10, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], True, 10, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], 123, 10, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], 123.3, 10, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], {"id": "Default"}, 10, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], (), 10, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], set(), 10, 2, 0.9, 3)

        self.assertRaises(ValueError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 0, 2, 0.9, 3)
        self.assertRaises(ValueError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], -1, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], ["default"], 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], None, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], "", 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], b"Default", 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], True, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], {"id": "Default"}, 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], (), 2, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], set(), 2, 0.9, 3)

        self.assertRaises(ValueError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 0, 0.9, 3)
        self.assertRaises(ValueError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, -1, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, ["default"], 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, None, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, "", 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, b"Default", 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, True, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, {"id": "Default"}, 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, (), 0.9, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, set(), 0.9, 3)

        self.assertRaises(ValueError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, -1, 3)
        self.assertRaises(ValueError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 1.1, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, b"Default", 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, "123", 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, {"id": "Default"}, 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, ["Default"], 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, [], 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, (), 3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, set(), 3)
        PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0, 3)
        PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.5, 3)
        PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 1, 3)

        self.assertRaises(ValueError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, -1)
        self.assertRaises(ValueError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 0)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, b"Default")
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, "123")
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, {"id": "Default"})
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, ["Default"])
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, [])
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, ())
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, set())
        PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 100)

        self.assertRaises(ValueError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, persistence_id="")
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, persistence_id=None)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, persistence_id=b"Default")
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, persistence_id=True)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, persistence_id=123)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, persistence_id=123.22)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, persistence_id={"id": "Default"})
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, persistence_id=["Default"])
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, persistence_id=[])
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, persistence_id=())
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, persistence_id=set())
        PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, persistence_id="Default")

        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=b"True")
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode="True")
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=123)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=123.22)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode={"id": "Default"})
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=["Default"])
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=[])
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=())
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=set())
        PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True)

        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, output_logline=None)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, output_logline=b"True")
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, output_logline="True")
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, output_logline=123)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, output_logline=123.22)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, output_logline={"id": "Default"})
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, output_logline=["Default"])
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, output_logline=[])
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, output_logline=())
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, output_logline=set())
        PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, output_logline=True)

        self.assertRaises(ValueError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, ignore_list=[""])
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, ignore_list="")
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, ignore_list=b"Default")
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, ignore_list=True)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, ignore_list=123)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, ignore_list=123.3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, ignore_list={"id": "Default"})
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, ignore_list=())
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, ignore_list=set())
        PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, ignore_list=[])
        PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, ignore_list=None)

        self.assertRaises(ValueError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, constraint_list=[""])
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, constraint_list="")
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, constraint_list=b"Default")
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, constraint_list=True)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, constraint_list=123)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, constraint_list=123.3)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, constraint_list={"id": "Default"})
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, constraint_list=())
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, constraint_list=set())
        PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, constraint_list=[])
        PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, constraint_list=None)

        self.assertRaises(ValueError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_time=-1)
        self.assertRaises(ValueError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_time=0)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_time=b"Default")
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_time="123")
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_time={"id": "Default"})
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_time=["Default"])
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_time=[])
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_time=())
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_time=set())
        PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_time=100)
        PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_time=100.22)

        self.assertRaises(ValueError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_no_anomaly_time=-1)
        self.assertRaises(ValueError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_no_anomaly_time=0)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_no_anomaly_time=b"Default")
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_no_anomaly_time="123")
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_no_anomaly_time={"id": "Default"})
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_no_anomaly_time=["Default"])
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_no_anomaly_time=[])
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_no_anomaly_time=())
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_no_anomaly_time=set())
        PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_no_anomaly_time=100)
        PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_no_anomaly_time=100.22)

        self.assertRaises(ValueError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, learn_mode=True, stop_learning_time=100, stop_learning_no_anomaly_time=100)

        self.assertRaises(ValueError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, log_resource_ignore_list=["/tmp/syslog"])
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, log_resource_ignore_list="")
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, log_resource_ignore_list=b"Default")
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, log_resource_ignore_list=True)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, log_resource_ignore_list=123)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, log_resource_ignore_list=123.22)
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, log_resource_ignore_list={"id": "Default"})
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, log_resource_ignore_list=())
        self.assertRaises(TypeError, PCADetector, self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, log_resource_ignore_list=set())
        PCADetector(self.aminer_config, ["/value"], [self.stream_printer_event_handler], 10, 2, 0.9, 3, log_resource_ignore_list=["file:///tmp/syslog"])


if __name__ == "__main__":
    unittest.main()
