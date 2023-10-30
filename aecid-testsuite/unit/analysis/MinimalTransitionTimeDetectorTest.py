import unittest
import time
from datetime import datetime
from aminer.analysis.MinimalTransitionTimeDetector import MinimalTransitionTimeDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase
from aminer.AminerConfig import DEFAULT_PERSISTENCE_PERIOD


class MinimalTransitionTimeDetectorTest(TestBase):
    """Unittests for the MinimalTransitionTimeDetector."""

    def test1receive_atom(self):
        """
        Test if log atoms are processed correctly and the detector is learning (learn_mode=True) and stops if learn_mode=False.
        Test if stop_learning_time and stop_learning_no_anomaly_timestamp are implemented properly.
        """
        # Initialize detector for sequence length 2
        t = time.time()
        expected_string = '%s First Appearance: %s\n%s: "None" (%d lines)\n  %s\n\n'
        dtf = "%Y-%m-%d %H:%M:%S"

        m1 = MatchElement("/model/id", b"1", b"1", None)
        m2 = MatchElement("/model/value", b"a", b"a", None)
        log_atom1 = LogAtom(b"1a", ParserMatch(MatchElement("/model", b"1a", b"1a", [m1, m2])), t+1, None)

        m4 = MatchElement("/model/value", b"b", b"b", None)
        log_atom2 = LogAtom(b"1b", ParserMatch(MatchElement("/model", b"1b", b"1b", [m4])), t+2, None)

        m5 = MatchElement("/model/id", b"2", b"2", None)
        m6 = MatchElement("/model/value", b"a", b"a", None)
        log_atom3 = LogAtom(b"2a", ParserMatch(MatchElement("/model", b"2a", b"2a", [m5, m6])), t+3, None)

        m7 = MatchElement("/model/id", b"1", b"1", None)
        m8 = MatchElement("/model/value", b"c", b"c", None)
        log_atom4 = LogAtom(b"1c", ParserMatch(MatchElement("/model", b"1c", b"1c", [m7, m8])), t+4, None)

        m9 = MatchElement("/model/id", b"2", b"2", None)
        m10 = MatchElement("/model/value", b"b", b"b", None)
        log_atom5 = LogAtom(b"2b", ParserMatch(MatchElement("/model", b"2b", b"2b", [m9, m10])), t+5, None)

        m11 = MatchElement("/model/value", b"c", b"c", None)
        log_atom6 = LogAtom(b"1b", ParserMatch(MatchElement("/model", b"1b", b"1b", [m11])), t+6, None)

        mttd = MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], id_path_list=["/model/id"], num_log_lines_solidify_matrix=5, learn_mode=True, output_logline=False)
        mttd.receive_atom(log_atom1)
        self.assertEqual(self.output_stream.getvalue(), "")
        time_matrix = {}
        self.assertEqual(mttd.time_matrix, time_matrix)

        mttd.receive_atom(log_atom2)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(mttd.time_matrix, time_matrix)

        mttd.receive_atom(log_atom3)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(mttd.time_matrix, time_matrix)

        mttd.receive_atom(log_atom4)
        time_matrix[(m8.match_string.decode(),)] = {(m2.match_string.decode(),): log_atom4.atom_time - log_atom1.atom_time}
        self.assertEqual(self.output_stream.getvalue(),  expected_string % (datetime.fromtimestamp(t + 4).strftime(dtf),
            f"['{m2.match_string.decode()}'] - ['{m8.match_string.decode()}'] (['{m7.match_string.decode()}']), {log_atom4.atom_time - log_atom1.atom_time}", mttd.__class__.__name__, 1, "1c"))
        self.reset_output_stream()
        self.assertEqual(mttd.time_matrix, time_matrix)

        mttd.receive_atom(log_atom5)
        time_matrix[(m10.match_string.decode(),)] = {(m6.match_string.decode(),): log_atom5.atom_time - log_atom3.atom_time}
        self.assertEqual(self.output_stream.getvalue(),  expected_string % (datetime.fromtimestamp(t + 5).strftime(dtf),
            f"['{m6.match_string.decode()}'] - ['{m10.match_string.decode()}'] (['{m9.match_string.decode()}']), {log_atom5.atom_time - log_atom3.atom_time}", mttd.__class__.__name__, 1, "2b"))
        self.reset_output_stream()
        self.assertEqual(mttd.time_matrix, time_matrix)

        mttd.receive_atom(log_atom6)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(mttd.time_matrix, time_matrix)

        # allow_missing_id=True
        mttd = MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], id_path_list=["/model/id"], num_log_lines_solidify_matrix=5, learn_mode=True, output_logline=False, allow_missing_id=True)
        mttd.receive_atom(log_atom1)
        self.assertEqual(self.output_stream.getvalue(), "")
        time_matrix = {}
        self.assertEqual(mttd.time_matrix, time_matrix)

        mttd.receive_atom(log_atom2)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(mttd.time_matrix, time_matrix)

        mttd.receive_atom(log_atom3)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(mttd.time_matrix, time_matrix)

        mttd.receive_atom(log_atom4)
        time_matrix[(m8.match_string.decode(),)] = {(m2.match_string.decode(),): log_atom4.atom_time - log_atom1.atom_time}
        self.assertEqual(self.output_stream.getvalue(),  expected_string % (datetime.fromtimestamp(t + 4).strftime(dtf),
            f"['{m2.match_string.decode()}'] - ['{m8.match_string.decode()}'] (['{m7.match_string.decode()}']), {log_atom4.atom_time - log_atom1.atom_time}", mttd.__class__.__name__, 1, "1c"))
        self.reset_output_stream()
        self.assertEqual(mttd.time_matrix, time_matrix)

        mttd.receive_atom(log_atom5)
        time_matrix[(m10.match_string.decode(),)] = {(m6.match_string.decode(),): log_atom5.atom_time - log_atom3.atom_time}
        self.assertEqual(self.output_stream.getvalue(),  expected_string % (datetime.fromtimestamp(t + 5).strftime(dtf),
            f"['{m6.match_string.decode()}'] - ['{m10.match_string.decode()}'] (['{m9.match_string.decode()}']), {log_atom5.atom_time - log_atom3.atom_time}", mttd.__class__.__name__, 1, "2b"))
        self.reset_output_stream()
        self.assertEqual(mttd.time_matrix, time_matrix)

        mttd.receive_atom(log_atom6)
        time_matrix[(m11.match_string.decode(),)][(m4.match_string.decode(),)] = log_atom6.atom_time - log_atom2.atom_time
        self.assertEqual(self.output_stream.getvalue(),  expected_string % (datetime.fromtimestamp(t + 6).strftime(dtf),
            f"['{m4.match_string.decode()}'] - ['{m11.match_string.decode()}'] (['']), {log_atom6.atom_time - log_atom2.atom_time}", mttd.__class__.__name__, 1, "1b"))
        self.reset_output_stream()
        self.assertEqual(mttd.time_matrix, time_matrix)

        # stop_learning_time
        mttd = MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], id_path_list=["/model/id"], num_log_lines_solidify_matrix=5, learn_mode=True, allow_missing_id=True, stop_learning_time=100)
        self.assertTrue(mttd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 99
        self.assertTrue(mttd.receive_atom(log_atom1))
        self.assertTrue(mttd.learn_mode)
        log_atom1.atom_time = t + 101
        self.assertTrue(mttd.receive_atom(log_atom1))
        self.assertFalse(mttd.learn_mode)

        # stop_learning_no_anomaly_time
        mttd = MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], id_path_list=["/model/id"], num_log_lines_solidify_matrix=5, learn_mode=True, allow_missing_id=True, stop_learning_no_anomaly_time=100)
        log_atom1.atom_time = t
        self.assertTrue(mttd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 100
        self.assertTrue(mttd.receive_atom(log_atom1))
        self.assertTrue(mttd.learn_mode)
        log_atom2.atom_time = t + 100
        self.assertTrue(mttd.receive_atom(log_atom2))
        self.assertTrue(mttd.learn_mode)
        log_atom1.atom_time = t + 200
        self.assertTrue(mttd.receive_atom(log_atom3))
        self.assertTrue(mttd.learn_mode)
        log_atom1.atom_time = t + 201
        self.assertTrue(mttd.receive_atom(log_atom1))
        self.assertFalse(mttd.learn_mode)

    def test2do_timer(self):
        """Test if the do_timer method is implemented properly."""
        mttd = MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"])
        t = time.time()
        mttd.next_persist_time = t + 400
        self.assertEqual(mttd.do_timer(t + 200), 200)
        self.assertEqual(mttd.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(mttd.do_timer(t + 999), 1)
        self.assertEqual(mttd.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

    def test3allowlist_event(self):
        """Test if the allowlist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        mttd = MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"])
        analysis = "Analysis.%s"
        self.assertRaises(Exception, mttd.allowlist_event, analysis % "NewMatchPathValueDetector", self.output_stream.getvalue(), None)

        # The MinimalTransitionTimeDetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, mttd.allowlist_event, analysis % mttd.__class__.__name__, self.output_stream.getvalue(), ["random", "Data"])

        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(mttd.allowlist_event(analysis % mttd.__class__.__name__, "/s1", None), "Allowlisted path %s in %s." % ("/s1", analysis % mttd.__class__.__name__))
        self.assertEqual(mttd.constraint_list, ["/s1"])

        mttd.learn_mode = False
        self.assertEqual(mttd.allowlist_event(analysis % mttd.__class__.__name__, "/d1", None), "Allowlisted path %s in %s." % ("/d1", analysis % mttd.__class__.__name__))
        self.assertEqual(mttd.constraint_list, ["/s1", "/d1"])

    def test4blocklist_event(self):
        """Test if the blocklist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        esd = MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"])
        analysis = "Analysis.%s"
        self.assertRaises(Exception, esd.blocklist_event, analysis % "NewMatchPathValueDetector", self.output_stream.getvalue(), None)

        # The MinimalTransitionTimeDetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, esd.blocklist_event, analysis % esd.__class__.__name__, self.output_stream.getvalue(), ["random", "Data"])

        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(esd.blocklist_event(analysis % esd.__class__.__name__, "/s1", None), "Blocklisted path %s in %s." % ("/s1", analysis % esd.__class__.__name__))
        self.assertEqual(esd.ignore_list, ["/s1"])

        esd.learn_mode = False
        self.assertEqual(esd.blocklist_event(analysis % esd.__class__.__name__, "/d1", None), "Blocklisted path %s in %s." % ("/d1", analysis % esd.__class__.__name__))
        self.assertEqual(esd.ignore_list, ["/s1", "/d1"])

    def test5persistence(self):
        """Test the do_persist and load_persistence_data methods."""
        t = time.time()
        m1 = MatchElement("/model/id", b"1", b"1", None)
        m2 = MatchElement("/model/value", b"a", b"a", None)
        log_atom1 = LogAtom(b"1a", ParserMatch(MatchElement("/model", b"1a", b"1a", [m1, m2])), t+1, None)

        m4 = MatchElement("/model/value", b"b", b"b", None)
        log_atom2 = LogAtom(b"1b", ParserMatch(MatchElement("/model", b"1b", b"1b", [m4])), t+2, None)

        m5 = MatchElement("/model/id", b"2", b"2", None)
        m6 = MatchElement("/model/value", b"a", b"a", None)
        log_atom3 = LogAtom(b"2a", ParserMatch(MatchElement("/model", b"2a", b"2a", [m5, m6])), t+3, None)

        m7 = MatchElement("/model/id", b"1", b"1", None)
        m8 = MatchElement("/model/value", b"c", b"c", None)
        log_atom4 = LogAtom(b"1c", ParserMatch(MatchElement("/model", b"1c", b"1c", [m7, m8])), t+4, None)

        m9 = MatchElement("/model/id", b"2", b"2", None)
        m10 = MatchElement("/model/value", b"b", b"b", None)
        log_atom5 = LogAtom(b"2b", ParserMatch(MatchElement("/model", b"2b", b"2b", [m9, m10])), t+5, None)

        m11 = MatchElement("/model/value", b"c", b"c", None)
        log_atom6 = LogAtom(b"1b", ParserMatch(MatchElement("/model", b"1b", b"1b", [m11])), t+6, None)

        mttd = MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], id_path_list=["/model/id"], num_log_lines_solidify_matrix=5, learn_mode=True, output_logline=False)
        mttd.receive_atom(log_atom1)
        mttd.receive_atom(log_atom2)
        mttd.receive_atom(log_atom3)
        mttd.receive_atom(log_atom4)
        mttd.receive_atom(log_atom5)
        mttd.receive_atom(log_atom6)
        mttd.do_persist()
        with open(mttd.persistence_file_name, "r") as f:
            self.assertEqual(f.read(), '[[[3.0], [2.0]], [["string:c"], ["string:b"]], [[["string:a"]], [["string:a"]]]]')

        self.assertEqual(mttd.time_matrix, {("c",): {("a",): 3.0}, ("b",): {("a",): 2.0}})
        mttd.sequences = {}
        mttd.load_persistence_data()
        self.assertEqual(mttd.time_matrix, {('c',): {('a',): 3.0}, ('b',): {('a',): 2.0}})

        other = MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], id_path_list=["/model/id"], target_path_list=["/model/value"], num_log_lines_solidify_matrix=5, learn_mode=True)
        self.assertEqual(other.time_matrix, mttd.time_matrix)

    def test6add_to_persistence_event(self):
        mttd = MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"])
        mttd.add_to_persistence_event("Analysis.MinimalTransitionTimeDetector", [["a"], ["1"], 3.0])
        self.assertEqual(mttd.time_matrix, {("a",): {("1",): 3.0}})

    def test7remove_from_persistence_event(self):
        mttd = MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"])
        mttd.time_matrix =  {("a",): {("1",): 3.0}}
        mttd.remove_from_persistence_event("Analysis.MinimalTransitionTimeDetector", [["a"], ["1"]])
        self.assertEqual(mttd.time_matrix, {})

    def test8validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, ["default"], ["/model/value"])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, None, ["/model/value"])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, "", ["/model/value"])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, b"Default", ["/model/value"])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, True, ["/model/value"])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, 123, ["/model/value"])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, 123.3, ["/model/value"])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, {"id": "Default"}, ["/model/value"])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, (), ["/model/value"])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, set(), ["/model/value"])

        self.assertRaises(ValueError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], [""])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], [None])
        self.assertRaises(ValueError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], None)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], "")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], b"Default")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], True)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], 123)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], 123.3)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], {"id": "Default"})
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ())
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], set())
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["default"])

        self.assertRaises(ValueError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], id_path_list=[""])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], id_path_list="")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], id_path_list=b"Default")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], id_path_list=True)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], id_path_list=123)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], id_path_list=123.3)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], id_path_list={"id": "Default"})
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], id_path_list=())
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], id_path_list=set())
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], id_path_list=[])
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], id_path_list=None)

        self.assertRaises(ValueError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list=[""])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list="")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list=b"Default")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list=True)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list=123)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list=123.3)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list={"id": "Default"})
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list=())
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list=set())
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list=[])
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list=None)

        self.assertRaises(ValueError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], constraint_list=[""])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], constraint_list="")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], constraint_list=b"Default")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], constraint_list=True)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], constraint_list=123)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], constraint_list=123.3)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], constraint_list={"id": "Default"})
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], constraint_list=())
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], constraint_list=set())
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], constraint_list=[])
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], constraint_list=None)

        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_id=b"True")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_id="True")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_id=123)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_id=123.22)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_id={"id": "Default"})
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_id=["Default"])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_id=[])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_id=())
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_id=set())
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_id=True)

        self.assertRaises(ValueError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_log_lines_solidify_matrix=-1)
        self.assertRaises(ValueError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_log_lines_solidify_matrix=0)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_log_lines_solidify_matrix=100.22)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_log_lines_solidify_matrix=b"Default")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_log_lines_solidify_matrix="123")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_log_lines_solidify_matrix={"id": "Default"})
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_log_lines_solidify_matrix=["Default"])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_log_lines_solidify_matrix=[])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_log_lines_solidify_matrix=())
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_log_lines_solidify_matrix=set())
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_log_lines_solidify_matrix=100)

        self.assertRaises(ValueError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_output_threshold=-1)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_output_threshold=b"Default")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_output_threshold="123")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_output_threshold={"id": "Default"})
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_output_threshold=["Default"])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_output_threshold=[])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_output_threshold=())
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_output_threshold=set())
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_output_threshold=0)
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_output_threshold=100)
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_output_threshold=100.22)

        self.assertRaises(ValueError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], anomaly_threshold=-1)
        self.assertRaises(ValueError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], anomaly_threshold=1.1)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], anomaly_threshold=b"Default")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], anomaly_threshold="123")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], anomaly_threshold={"id": "Default"})
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], anomaly_threshold=["Default"])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], anomaly_threshold=[])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], anomaly_threshold=())
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], anomaly_threshold=set())
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], anomaly_threshold=0)
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], anomaly_threshold=1.0)
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], anomaly_threshold=0.5)

        self.assertRaises(ValueError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id="")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id=None)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id=b"Default")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id=True)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id=123)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id=123.22)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id={"id": "Default"})
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id=["Default"])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id=[])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id=())
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id=set())
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id="Default")

        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=b"True")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode="True")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=123)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=123.22)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode={"id": "Default"})
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=["Default"])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=[])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=())
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=set())
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True)

        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline=None)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline=b"True")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline="True")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline=123)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline=123.22)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline={"id": "Default"})
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline=["Default"])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline=[])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline=())
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline=set())
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline=True)

        self.assertRaises(ValueError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=-1)
        self.assertRaises(ValueError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=0)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=b"Default")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time="123")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time={"id": "Default"})
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=["Default"])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=[])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=())
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=set())
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=100)
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=100.22)

        self.assertRaises(ValueError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=-1)
        self.assertRaises(ValueError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=0)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=b"Default")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time="123")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time={"id": "Default"})
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=["Default"])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=[])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=())
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=set())
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=100)
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=100.22)

        self.assertRaises(ValueError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=100, stop_learning_no_anomaly_time=100)

        self.assertRaises(ValueError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list=["/tmp/syslog"])
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list="")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list=b"Default")
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list=True)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list=123)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list=123.22)
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list={"id": "Default"})
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list=())
        self.assertRaises(TypeError, MinimalTransitionTimeDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list=set())
        MinimalTransitionTimeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list=["file:///tmp/syslog"])


if __name__ == "__main__":
    unittest.main()
