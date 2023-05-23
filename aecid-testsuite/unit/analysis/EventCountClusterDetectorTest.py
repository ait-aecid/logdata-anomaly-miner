import unittest
import time
from datetime import datetime
from aminer.analysis.EventCountClusterDetector import EventCountClusterDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase
from aminer.AminerConfig import DEFAULT_PERSISTENCE_PERIOD


class EventCountClusterDetectorTest(TestBase):
    """Unittests for the EventFrequencyDetector."""

    def test1receive_atom(self):
        """
        This test checks the normal operation of EventCountClusterDetector. Test if log atoms are processed correctly and the detector is
        learning (learn_mode=True) and stops if learn_mode=False. Test if stop_learning_time and stop_learning_no_anomaly_timestamp are implemented properly.
        """
        t = time.time()
        expected_string = '%s Frequency anomaly detected\n%s: "None" (%d lines)\n  %s\n\n'
        dtf = "%Y-%m-%d %H:%M:%S"

        # The following log atoms are created:
        #  window 1:
        #   value a: 1 time by x, 1 time by y
        #   value b: 1 time by x
        #  window 2:
        #   value a: 2 times by x, 1 time by y
        #   value b: 1 time by x
        #  window 3:
        #   value b: 1 time by x
        #   value c: 1 time by x
        #  window 4:
        #   value a: 1 time by x
        # Start of window 1:
        m1 = MatchElement("/p/value", b"a", b"a", None)
        m2 = MatchElement("/p/id", b"x", b"x", None)
        log_atom1 = LogAtom(b"ax", ParserMatch(MatchElement("/p", b"ax", b"ax", [m1, m2])), t+1, None)

        m3 = MatchElement("/p/value", b"a", b"a", None)
        m4 = MatchElement("/p/id", b"y", b"y", None)
        log_atom2 = LogAtom(b"ay", ParserMatch(MatchElement("/p", b"ay", b"ay", [m3, m4])), t+2, None)

        m5 = MatchElement("/p/value", b"b", b"b", None)
        m6 = MatchElement("/p/id", b"x", b"x", None)
        log_atom3 = LogAtom(b"bx", ParserMatch(MatchElement("/p", b"bx", b"bx", [m5, m6])), t+3, None)

        # Start of window 2:
        m7 = MatchElement("/p/value", b"a", b"a", None)
        m8 = MatchElement("/p/id", b"x", b"x", None)
        log_atom4 = LogAtom(b"ax", ParserMatch(MatchElement("/p", b"ax", b"ax", [m7, m8])), t+13, None)

        m9 = MatchElement("/p/value", b"a", b"a", None)
        m10 = MatchElement("/p/id", b"y", b"y", None)
        log_atom5 = LogAtom(b"ay", ParserMatch(MatchElement("/p", b"ay", b"ay", [m9, m10])), t+14, None)

        m11 = MatchElement("/p/value", b"b", b"b", None)
        m12 = MatchElement("/p/id", b"x", b"x", None)
        log_atom6 = LogAtom(b"bx",  ParserMatch(MatchElement("/p", b"bx", b"bx", [m11, m12])), t+15, None)

        m13 = MatchElement("/p/value", b"a", b"a", None)
        m14 = MatchElement("/p/id", b"x", b"x", None)
        log_atom7 = LogAtom(b"ax", ParserMatch(MatchElement("/p", b"ax", b"ax", [m13, m14])), t+16, None)

        # Start of window 3:
        m15 = MatchElement("/p/value", b"c", b"c", None)
        m16 = MatchElement("/p/id", b"x", b"x", None)
        log_atom8 = LogAtom(b"cx", ParserMatch(MatchElement("/p", b"cx", b"cx", [m15, m16])), t+23, None)

        m17 = MatchElement("/p/value", b"b", b"b", None)
        m18 = MatchElement("/p/id", b"x", b"x", None)
        log_atom9 = LogAtom(b"bx", ParserMatch(MatchElement("/p", b"bx", b"bx", [m17, m18])), t+24, None)

        # Start of window 4:
        m19 = MatchElement("/p/value", b"a", b"a", None)
        m20 = MatchElement("/p/id", b"x", b"x", None)
        log_atom10 = LogAtom(b"ax", ParserMatch(MatchElement("/p", b"ax", b"ax", [m19, m20])), t+43, None)

        eccd = EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], target_path_list=["/p/value"], id_path_list=["/p/id"],
            window_size=10, num_windows=50, confidence_factor=0.5, idf=True, norm=False, add_normal=False, check_empty_windows=False, learn_mode=True, output_logline=False)

        # Forward log atoms to detector
        eccd.receive_atom(log_atom1)
        self.assertEqual(self.output_stream.getvalue(), "")
        eccd.receive_atom(log_atom2)
        self.assertEqual(self.output_stream.getvalue(), "")
        eccd.receive_atom(log_atom3)
        self.assertEqual(self.output_stream.getvalue(), "")
        eccd.receive_atom(log_atom4)
        # End of first time window; first count vector triggers anomaly for x
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t + 13).strftime(dtf), eccd.__class__.__name__, 1, "ax"))
        self.reset_output_stream()
        eccd.receive_atom(log_atom5)
        # End of first time window; first count vector triggers anomaly for y
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t + 14).strftime(dtf), eccd.__class__.__name__, 1, "ay"))
        self.reset_output_stream()
        eccd.receive_atom(log_atom6)
        self.assertEqual(self.output_stream.getvalue(), "")
        eccd.receive_atom(log_atom7)
        self.assertEqual(self.output_stream.getvalue(), "")
        eccd.receive_atom(log_atom8)
        # No anomaly reported for x since 2 times a and 1 time b (window 1) is similar enough to 1 time a and 1 time b (window 2)
        self.assertEqual(self.output_stream.getvalue(), "")
        eccd.receive_atom(log_atom9)
        self.assertEqual(self.output_stream.getvalue(), "")
        eccd.receive_atom(log_atom10)
        # Check learned count vectors at end of third time window
        # For x, count vector from first and third windows are included in model; for y only first window
        self.assertEqual(eccd.known_counts, {("x",): [{("a",): 1, ("b",): 1}, {("c",): 1, ("b",): 1}], ("y",): [{("a",): 1}]})
        # Since a occurs in both x and y, its idf factor is only 0.176 (=log10(3/2)),
        # compared to b and c which have an idf factor of 0.477 (=log10(3/1)).
        # Comparing the count vectors for x in the first and third window, we see that
        #  a occurs only in first window, which increases diff to 0.176/0.176
        #  b occurs once in first and third windows, which updates diff to 0.176/0.653
        #  c occurs only in third window, which increases diff to 0.653/1.13
        # The final score is thus 0.653/1.13=0.578, which exceeds the threshold of 0.5.
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t + 43).strftime(dtf), eccd.__class__.__name__, 1, "ax"))

        # stop_learning_time
        eccd = EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], target_path_list=["/p/value"], id_path_list=["/p/id"],
            window_size=10, num_windows=50, confidence_factor=0.5, idf=True, norm=False, add_normal=False, check_empty_windows=False, learn_mode=True, output_logline=False, stop_learning_time=100)
        self.assertTrue(eccd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 99
        self.assertTrue(eccd.receive_atom(log_atom1))
        self.assertTrue(eccd.learn_mode)
        log_atom1.atom_time = t + 101
        self.assertTrue(eccd.receive_atom(log_atom1))
        self.assertFalse(eccd.learn_mode)

        # stop_learning_no_anomaly_time
        eccd = EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], target_path_list=["/p/value"], id_path_list=["/p/id"],
            window_size=10, num_windows=50, confidence_factor=0.5, idf=True, norm=False, add_normal=False, check_empty_windows=False, learn_mode=True, output_logline=False, stop_learning_no_anomaly_time=100)
        log_atom1.atom_time = t
        self.assertTrue(eccd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 100
        self.assertTrue(eccd.receive_atom(log_atom1))
        self.assertTrue(eccd.learn_mode)
        log_atom2.atom_time = t + 100
        self.assertTrue(eccd.receive_atom(log_atom2))
        self.assertTrue(eccd.learn_mode)
        log_atom1.atom_time = t + 200
        self.assertTrue(eccd.receive_atom(log_atom3))
        self.assertTrue(eccd.learn_mode)
        log_atom1.atom_time = t + 201
        self.assertTrue(eccd.receive_atom(log_atom1))
        self.assertFalse(eccd.learn_mode)

    def test2do_timer(self):
        """Test if the do_timer method is implemented properly."""
        eccd = EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler])
        t = time.time()
        eccd.next_persist_time = t + 400
        self.assertEqual(eccd.do_timer(t + 200), 200)
        self.assertEqual(eccd.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(eccd.do_timer(t + 999), 1)
        self.assertEqual(eccd.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

    def test3allowlist_event(self):
        """Test if the allowlist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        eccd = EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler])
        t = round(time.time(), 3)
        analysis = "Analysis.%s"
        self.assertRaises(Exception, eccd.allowlist_event, analysis % "NewMatchPathValueDetector", self.output_stream.getvalue(), None)

        # The EventCountClusterDetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, eccd.allowlist_event, analysis % eccd.__class__.__name__, self.output_stream.getvalue(), ["random", "Data"])

        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(eccd.allowlist_event(analysis % eccd.__class__.__name__, "/s1", None), "Allowlisted path %s in %s." % ("/s1", analysis % eccd.__class__.__name__))
        self.assertEqual(eccd.constraint_list, ["/s1"])

        eccd.learn_mode = False
        self.assertEqual(eccd.allowlist_event(analysis % eccd.__class__.__name__, "/d1", None), "Allowlisted path %s in %s." % ("/d1", analysis % eccd.__class__.__name__))
        self.assertEqual(eccd.constraint_list, ["/s1", "/d1"])

    def test4blocklist_event(self):
        """Test if the blocklist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        eccd = EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler])
        t = round(time.time(), 3)
        analysis = "Analysis.%s"
        self.assertRaises(Exception, eccd.blocklist_event, analysis % "NewMatchPathValueDetector", self.output_stream.getvalue(), None)

        # The EventCountClusterDetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, eccd.blocklist_event, analysis % eccd.__class__.__name__, self.output_stream.getvalue(), ["random", "Data"])

        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(eccd.blocklist_event(analysis % eccd.__class__.__name__, "/s1", None), "Blocklisted path %s in %s." % ("/s1", analysis % eccd.__class__.__name__))
        self.assertEqual(eccd.ignore_list, ["/s1"])

        eccd.learn_mode = False
        self.assertEqual(eccd.blocklist_event(analysis % eccd.__class__.__name__, "/d1", None), "Blocklisted path %s in %s." % ("/d1", analysis % eccd.__class__.__name__))
        self.assertEqual(eccd.ignore_list, ["/s1", "/d1"])

    def test5persistence(self):
        """Test the do_persist and load_persistence_data methods."""
        t = time.time()
        eccd = EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], target_path_list=["/p/value"], id_path_list=["/p/id"],
            window_size=10, num_windows=50, confidence_factor=0.5, idf=True, norm=False, add_normal=False, check_empty_windows=False, learn_mode=True, output_logline=False)
        m1 = MatchElement("/p/value", b"a", b"a", None)
        m2 = MatchElement("/p/id", b"x", b"x", None)
        log_atom1 = LogAtom(b"ax", ParserMatch(MatchElement("/p", b"ax", b"ax", [m1, m2])), t + 1, None)

        m3 = MatchElement("/p/value", b"a", b"a", None)
        m4 = MatchElement("/p/id", b"y", b"y", None)
        log_atom2 = LogAtom(b"ay", ParserMatch(MatchElement("/p", b"ay", b"ay", [m3, m4])), t + 2, None)

        m5 = MatchElement("/p/value", b"b", b"b", None)
        m6 = MatchElement("/p/id", b"x", b"x", None)
        log_atom3 = LogAtom(b"bx", ParserMatch(MatchElement("/p", b"bx", b"bx", [m5, m6])), t + 3, None)

        # Start of window 2:
        m7 = MatchElement("/p/value", b"a", b"a", None)
        m8 = MatchElement("/p/id", b"x", b"x", None)
        log_atom4 = LogAtom(b"ax", ParserMatch(MatchElement("/p", b"ax", b"ax", [m7, m8])), t + 13, None)

        m9 = MatchElement("/p/value", b"a", b"a", None)
        m10 = MatchElement("/p/id", b"y", b"y", None)
        log_atom5 = LogAtom(b"ay", ParserMatch(MatchElement("/p", b"ay", b"ay", [m9, m10])), t + 14, None)

        m11 = MatchElement("/p/value", b"b", b"b", None)
        m12 = MatchElement("/p/id", b"x", b"x", None)
        log_atom6 = LogAtom(b"bx", ParserMatch(MatchElement("/p", b"bx", b"bx", [m11, m12])), t + 15, None)

        m13 = MatchElement("/p/value", b"a", b"a", None)
        m14 = MatchElement("/p/id", b"x", b"x", None)
        log_atom7 = LogAtom(b"ax", ParserMatch(MatchElement("/p", b"ax", b"ax", [m13, m14])), t + 16, None)

        # Start of window 3:
        m15 = MatchElement("/p/value", b"c", b"c", None)
        m16 = MatchElement("/p/id", b"x", b"x", None)
        log_atom8 = LogAtom(b"cx", ParserMatch(MatchElement("/p", b"cx", b"cx", [m15, m16])), t + 23, None)

        m17 = MatchElement("/p/value", b"b", b"b", None)
        m18 = MatchElement("/p/id", b"x", b"x", None)
        log_atom9 = LogAtom(b"bx", ParserMatch(MatchElement("/p", b"bx", b"bx", [m17, m18])), t + 24, None)

        # Start of window 4:
        m19 = MatchElement("/p/value", b"a", b"a", None)
        m20 = MatchElement("/p/id", b"x", b"x", None)
        log_atom10 = LogAtom(b"ax", ParserMatch(MatchElement("/p", b"ax", b"ax", [m19, m20])), t + 43, None)

        eccd.receive_atom(log_atom1)
        eccd.receive_atom(log_atom2)
        eccd.receive_atom(log_atom3)
        eccd.receive_atom(log_atom4)
        eccd.receive_atom(log_atom5)
        eccd.receive_atom(log_atom6)
        eccd.receive_atom(log_atom7)
        eccd.receive_atom(log_atom8)
        eccd.receive_atom(log_atom9)
        eccd.receive_atom(log_atom10)
        eccd.do_persist()
        self.maxDiff = None
        with open(eccd.persistence_file_name, "r") as f:
            self.assertEqual(f.read(), '[[[["string:x"], [[[["string:a"], 1], [["string:b"], 1]], [[["string:b"], 1], [["string:c"], 1]]]], [["string:y"], [[[["string:a"], 1]]]]], [["string:x"], ["string:y"]], [[["string:a"], [["string:x"], ["string:y"]]], [["string:b"], [["string:x"]]], [["string:c"], [["string:x"]]]]]')

        self.assertEqual(eccd.known_counts, {('x',): [{('a',): 1, ('b',): 1}, {('c',): 1, ('b',): 1}], ('y',): [{('a',): 1}]})
        self.assertEqual(eccd.idf_total, {('x',), ('y',)})
        self.assertEqual(eccd.idf_counts, {('a',): {('x',), ('y',)}, ('b',): {('x',)}, ('c',): {('x',)}})
        eccd.load_persistence_data()
        self.assertEqual(eccd.known_counts, {('x',): [{('a',): 1, ('b',): 1}, {('c',): 1, ('b',): 1}], ('y',): [{('a',): 1}]})
        self.assertEqual(eccd.idf_total, {('x',), ('y',)})
        self.assertEqual(eccd.idf_counts, {('a',): {('x',), ('y',)}, ('b',): {('x',)}, ('c',): {('x',)}})

        other = EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], target_path_list=["/p/value"], id_path_list=["/p/id"],
            window_size=10, num_windows=50, confidence_factor=0.5, idf=True, norm=False, add_normal=False, check_empty_windows=False, learn_mode=True, output_logline=False)
        self.assertEqual(other.known_counts, eccd.known_counts)
        self.assertEqual(other.idf_total, eccd.idf_total)
        self.assertEqual(other.idf_counts, eccd.idf_counts)

    def test6validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, ["default"])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, None)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, "")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, b"Default")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, True)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, 123)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, 123.3)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, {"id": "Default"})
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, ())
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, set())

        self.assertRaises(ValueError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=[""])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list="")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=b"Default")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=True)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=123)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=123.3)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list={"id": "Default"})
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=())
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=set())
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], target_path_list=[])
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], target_path_list=None)

        self.assertRaises(ValueError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], window_size=-1)
        self.assertRaises(ValueError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], window_size=0)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], window_size=b"Default")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], window_size="123")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], window_size={"id": "Default"})
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], window_size=["Default"])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], window_size=[])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], window_size=())
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], window_size=set())
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], window_size=100)
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], window_size=100.22)

        self.assertRaises(ValueError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=[""])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list="")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=b"Default")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=True)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=123)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=123.3)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list={"id": "Default"})
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=())
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=set())
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], id_path_list=[])
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], id_path_list=None)

        self.assertRaises(ValueError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows=-1)
        self.assertRaises(ValueError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows=0)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows=100.22)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows=b"Default")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows="123")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows={"id": "Default"})
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows=["Default"])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows=[])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows=())
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], num_windows=set())
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], num_windows=100)

        self.assertRaises(ValueError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], confidence_factor=-1)
        self.assertRaises(ValueError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], confidence_factor=1.1)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], confidence_factor=b"Default")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], confidence_factor="123")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], confidence_factor={"id": "Default"})
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], confidence_factor=["Default"])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], confidence_factor=[])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], confidence_factor=())
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], confidence_factor=set())
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], confidence_factor=0)
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], confidence_factor=0.5)
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], confidence_factor=1)

        self.assertRaises(ValueError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], idf=True)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=["/model/id"], idf=b"True")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=["/model/id"], idf="True")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=["/model/id"], idf=123)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=["/model/id"], idf=123.22)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=["/model/id"], idf={"id": "Default"})
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=["/model/id"], idf=["Default"])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=["/model/id"], idf=[])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=["/model/id"], idf=())
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=["/model/id"], idf=set())
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], id_path_list=["/model/id"], idf=True)

        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], norm=b"True")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], norm="True")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], norm=123)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], norm=123.22)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], norm={"id": "Default"})
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], norm=["Default"])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], norm=[])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], norm=())
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], norm=set())
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], norm=True)

        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], add_normal=b"True")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], add_normal="True")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], add_normal=123)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], add_normal=123.22)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], add_normal={"id": "Default"})
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], add_normal=["Default"])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], add_normal=[])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], add_normal=())
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], add_normal=set())
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], add_normal=True)

        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], check_empty_windows=b"True")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], check_empty_windows="True")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], check_empty_windows=123)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], check_empty_windows=123.22)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], check_empty_windows={"id": "Default"})
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], check_empty_windows=["Default"])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], check_empty_windows=[])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], check_empty_windows=())
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], check_empty_windows=set())
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], check_empty_windows=True)

        self.assertRaises(ValueError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id="")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=None)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=b"Default")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=True)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=123)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=123.22)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id={"id": "Default"})
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=["Default"])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=[])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=())
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=set())
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], persistence_id="Default")

        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=b"True")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode="True")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=123)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=123.22)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode={"id": "Default"})
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=["Default"])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=[])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=())
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=set())
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True)

        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=None)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=b"True")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline="True")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=123)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=123.22)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline={"id": "Default"})
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=["Default"])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=[])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=())
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=set())
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], output_logline=True)

        self.assertRaises(ValueError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=[""])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list="")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=b"Default")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=True)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=123)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=123.3)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list={"id": "Default"})
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=())
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=set())
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], ignore_list=[])
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], ignore_list=None)

        self.assertRaises(ValueError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=[""])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list="")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=b"Default")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=True)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=123)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=123.3)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list={"id": "Default"})
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=())
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=set())
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], constraint_list=[])
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], constraint_list=None)

        self.assertRaises(ValueError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=-1)
        self.assertRaises(ValueError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=0)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=b"Default")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time="123")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time={"id": "Default"})
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=["Default"])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=[])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=())
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=set())
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100)
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100.22)

        self.assertRaises(ValueError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=-1)
        self.assertRaises(ValueError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=0)
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=b"Default")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time="123")
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time={"id": "Default"})
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=["Default"])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=[])
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=())
        self.assertRaises(TypeError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=set())
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=100)
        EventCountClusterDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=100.22)

        self.assertRaises(ValueError, EventCountClusterDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100, stop_learning_no_anomaly_time=100)


if __name__ == "__main__":
    unittest.main()
