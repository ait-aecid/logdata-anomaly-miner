import unittest
import time
from datetime import datetime
from aminer.analysis.CharsetDetector import CharsetDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase
from aminer.AminerConfig import DEFAULT_PERSISTENCE_PERIOD


class CharsetDetectorTest(TestBase):
    """Unittests for the ValueRangeDetectorDetector."""

    def test1receive_atom(self):
        """
        This test case checks the normal detection of new character sets. The charset detector is used to learn an alphabet and detect new
        characters for different identifiers. Test if log atoms are processed correctly and the detector is learning (learn_mode=True) and
        stops if learn_mode=False. Test if stop_learning_time and stop_learning_no_anomaly_timestamp are implemented properly.
        """
        t = time.time()
        expected_string = '%s New and/or expired character(s) detected\n%s: "None" (%d lines)\n  %s\n\n'
        dtf = "%Y-%m-%d %H:%M:%S"

        # Prepare log atoms that represent two entities (id) with strings (value). Anomalies are generated when new characters are observed.
        # The following events are generated:
        #  id: a value: abc
        #  id: b value: xyz
        #  id: a value: asdf
        #  id: a value: xxx
        #  id: a value: bass
        #  id: a value: max
        m1 = MatchElement("/model/id", b"a", b"a", None)
        m2 = MatchElement("/model/value", b"abc", b"abc", None)
        log_atom1 = LogAtom(b"aabc", ParserMatch(MatchElement("/model", b"aabc", b"aabc", [m1, m2])), t+1, None)

        m3 = MatchElement("/model/id", b"b", b"b", None)
        m4 = MatchElement("/model/value", b"xyz", b"xyz", None)
        log_atom2 = LogAtom(b"bxyz", ParserMatch(MatchElement("/model", b"bxyz", b"bxyz", [m3, m4])), t+2, None)

        m5 = MatchElement("/model/id", b"a", b"a", None)
        m6 = MatchElement("/model/value", b"asdf", b"asdf", None)
        log_atom3 = LogAtom(b"aasdf", ParserMatch(MatchElement("/model", b"aasdf", b"aasdf", [m5, m6])), t+3, None)

        m7 = MatchElement("/model/id", b"a", b"a", None)
        m8 = MatchElement("/model/value", b"xxx", b"xxx", None)
        log_atom4 = LogAtom(b"bxxx", ParserMatch(MatchElement("/model", b"bxxx", b"bxxx", [m7, m8])), t+4, None)

        m9 = MatchElement("/model/id", b"a", b"a", None)
        m10 = MatchElement("/model/value", b"bass", b"bass", None)
        log_atom5 = LogAtom(b"abass", ParserMatch(MatchElement("/model", b"abass", b"abass", [m9, m10])), t+5, None)

        m11 = MatchElement("/model/id", b"a", b"a", None)
        m12 = MatchElement("/model/value", b"max", b"max", None)
        log_atom6 = LogAtom(b"bmax", ParserMatch(MatchElement("/model", b"bmax", b"bmax", [m11, m12])), t+6, None)

        cd = CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, output_logline=False)
        # Forward log atoms to detector
        # First value of id (a) should not generate an anomaly
        # Input: id: a value: abc
        # Expected output: None
        cd.receive_atom(log_atom1)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(cd.charsets, {("a",): set([ord(x) for x in "abc"])})

        # First value of id (b) should not generate an anomaly
        # Input: id: b value: xyz
        # Expected output: None
        cd.receive_atom(log_atom2)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(cd.charsets, {("a",): set([ord(x) for x in "abc"]), ("b",): set([ord(x) for x in "xyz"])})

        # Second value of id (a) should generate an anomaly for new characters ("sdf" of "asdf" not in "abc")
        # Input: id: a value: asdf
        # Expected output: Anomaly
        cd.receive_atom(log_atom3)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t + 3).strftime(dtf), cd.__class__.__name__, 1, "aasdf"))
        self.reset_output_stream()
        self.assertEqual(cd.charsets, {("a",): set([ord(x) for x in "abcdfs"]), ("b",): set([ord(x) for x in "xyz"])})

        # Third value of id (a) should generate an anomaly for new characters ("x" not in "abcsdf", only in "xyz" from other id (b))
        # Input: id: a value: xxx
        # Expected output: Anomaly
        cd.receive_atom(log_atom4)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t + 4).strftime(dtf), cd.__class__.__name__, 1, "bxxx"))
        self.reset_output_stream()
        self.assertEqual(cd.charsets, {("a",): set([ord(x) for x in "abcdfsx"]), ("b",): set([ord(x) for x in "xyz"])})

        # Fourth value of id (a) should not generate an anomaly (all characters of "bass" in "abcsdfx")
        # Input: id: a value: bass
        # Expected output: None
        cd.receive_atom(log_atom5)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(cd.charsets, {("a",): set([ord(x) for x in "abcdfsx"]), ("b",): set([ord(x) for x in "xyz"])})

        # Fifth value of id (a) should generate an anomaly for new characters ("m" of "max" not in "abcsdfx")
        cd.receive_atom(log_atom6)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t + 6).strftime(dtf), cd.__class__.__name__, 1, "bmax"))
        self.reset_output_stream()
        self.assertEqual(cd.charsets, {("a",): set([ord(x) for x in "abcdfmsx"]), ("b",): set([ord(x) for x in "xyz"])})

        # stop_learning_time
        cd = CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, output_logline=False, stop_learning_time=100)
        self.assertTrue(cd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 99
        self.assertTrue(cd.receive_atom(log_atom1))
        self.assertTrue(cd.learn_mode)
        log_atom1.atom_time = t + 102
        self.assertTrue(cd.receive_atom(log_atom1))
        self.assertFalse(cd.learn_mode)

        # stop_learning_no_anomaly_time
        cd = CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, output_logline=False, stop_learning_no_anomaly_time=100)
        log_atom1.atom_time = t
        self.assertTrue(cd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 100
        self.assertTrue(cd.receive_atom(log_atom1))
        self.assertTrue(cd.learn_mode)
        log_atom2.atom_time = t + 100
        self.assertTrue(cd.receive_atom(log_atom2))
        self.assertTrue(cd.learn_mode)
        log_atom1.atom_time = t + 200
        self.assertTrue(cd.receive_atom(log_atom3))
        self.assertTrue(cd.learn_mode)
        log_atom1.atom_time = t + 201
        self.assertTrue(cd.receive_atom(log_atom1))
        self.assertFalse(cd.learn_mode)

    def test2do_timer(self):
        """Test if the do_timer method is implemented properly."""
        cd = CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"])
        t = time.time()
        cd.next_persist_time = t + 400
        self.assertEqual(cd.do_timer(t + 200), 200)
        self.assertEqual(cd.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(cd.do_timer(t + 999), 1)
        self.assertEqual(cd.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

    def test3allowlist_event(self):
        """Test if the allowlist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        cd = CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"])
        analysis = "Analysis.%s"
        self.assertRaises(Exception, cd.allowlist_event, analysis % "NewMatchPathValueDetector", self.output_stream.getvalue(), None)

        # The CharsetDetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, cd.allowlist_event, analysis % cd.__class__.__name__, self.output_stream.getvalue(), ["random", "Data"])

        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(cd.allowlist_event(analysis % cd.__class__.__name__, "/s1", None), "Allowlisted path %s in %s." % ("/s1", analysis % cd.__class__.__name__))
        self.assertEqual(cd.constraint_list, ["/s1"])

        cd.learn_mode = False
        self.assertEqual(cd.allowlist_event(analysis % cd.__class__.__name__, "/d1", None), "Allowlisted path %s in %s." % ("/d1", analysis % cd.__class__.__name__))
        self.assertEqual(cd.constraint_list, ["/s1", "/d1"])

    def test4blocklist_event(self):
        """Test if the blocklist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        cd = CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"])
        analysis = "Analysis.%s"
        self.assertRaises(Exception, cd.blocklist_event, analysis % "NewMatchPathValueDetector", self.output_stream.getvalue(), None)

        # The CharsetDetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, cd.blocklist_event, analysis % cd.__class__.__name__, self.output_stream.getvalue(), ["random", "Data"])

        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(cd.blocklist_event(analysis % cd.__class__.__name__, "/s1", None), "Blocklisted path %s in %s." % ("/s1", analysis % cd.__class__.__name__))
        self.assertEqual(cd.ignore_list, ["/s1"])

        cd.learn_mode = False
        self.assertEqual(cd.blocklist_event(analysis % cd.__class__.__name__, "/d1", None), "Blocklisted path %s in %s." % ("/d1", analysis % cd.__class__.__name__))
        self.assertEqual(cd.ignore_list, ["/s1", "/d1"])

    def test5persistence(self):
        """Test the do_persist and load_persistence_data methods."""
        t = time.time()
        cd = CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, output_logline=False, expire_persistence_time=86400)
        m1 = MatchElement("/model/id", b"a", b"a", None)
        m2 = MatchElement("/model/value", b"abc", b"abc", None)
        log_atom1 = LogAtom(b"aabc", ParserMatch(MatchElement("/model", b"aabc", b"aabc", [m1, m2])), t + 1, None)

        m3 = MatchElement("/model/id", b"b", b"b", None)
        m4 = MatchElement("/model/value", b"xyz", b"xyz", None)
        log_atom2 = LogAtom(b"bxyz", ParserMatch(MatchElement("/model", b"bxyz", b"bxyz", [m3, m4])), t + 2, None)

        m5 = MatchElement("/model/id", b"a", b"a", None)
        m6 = MatchElement("/model/value", b"asdf", b"asdf", None)
        log_atom3 = LogAtom(b"aasdf", ParserMatch(MatchElement("/model", b"aasdf", b"aasdf", [m5, m6])), t + 3, None)

        m7 = MatchElement("/model/id", b"a", b"a", None)
        m8 = MatchElement("/model/value", b"xxx", b"xxx", None)
        log_atom4 = LogAtom(b"axxx", ParserMatch(MatchElement("/model", b"axxx", b"axxx", [m7, m8])), t + 4, None)

        m9 = MatchElement("/model/id", b"a", b"a", None)
        m10 = MatchElement("/model/value", b"bass", b"bass", None)
        log_atom5 = LogAtom(b"abass", ParserMatch(MatchElement("/model", b"abass", b"abass", [m9, m10])), t + 5, None)

        m11 = MatchElement("/model/id", b"b", b"b", None)
        m12 = MatchElement("/model/value", b"max", b"max", None)
        log_atom6 = LogAtom(b"bmax", ParserMatch(MatchElement("/model", b"bmax", b"bmax", [m11, m12])), t + 6, None)

        cd.receive_atom(log_atom1)
        cd.receive_atom(log_atom2)
        cd.receive_atom(log_atom3)
        cd.receive_atom(log_atom4)
        cd.receive_atom(log_atom5)
        cd.receive_atom(log_atom6)
        cd.do_persist()
        p = t + cd.expire_persistence_time
        with open(cd.persistence_file_name, "r") as f:
            self.assertEqual(f.read(), f'[[["string:a"], [97, 98, 99, 115, 100, 102, 120], [{p+5}, {p+5}, {p+1}, {p+5}, {p+3}, {p+3}, {p+4}]], [["string:b"], [97, 120, 121, 122, 109], [{p+6}, {p+6}, {p+2}, {p+2}, {p+6}]]]')

        cd.learn_mode = False
        t = p - 3
        log_atom1 = LogAtom(b"aabc", ParserMatch(MatchElement("/model", b"aabc", b"aabc", [m1, m2])), t + 1, None)
        log_atom3 = LogAtom(b"aasdf", ParserMatch(MatchElement("/model", b"aasdf", b"aasdf", [m5, m6])), t + 3, None)
        log_atom5 = LogAtom(b"abass", ParserMatch(MatchElement("/model", b"abass", b"abass", [m9, m10])), t + 5, None)
        log_atom6 = LogAtom(b"bmax", ParserMatch(MatchElement("/model", b"bmax", b"bmax", [m11, m12])), t + 6, None)
        log_atom2 = LogAtom(b"bxyz", ParserMatch(MatchElement("/model", b"bxyz", b"bxyz", [m3, m4])), t + cd.expire_persistence_time + 2, None)  # x will be missing in 'b'
        log_atom4 = LogAtom(b"axxx", ParserMatch(MatchElement("/model", b"axxx", b"axxx", [m7, m8])), t + cd.expire_persistence_time + 4, None)  # x will be missing in 'a'
        cd.receive_atom(log_atom1)
        cd.receive_atom(log_atom2)
        cd.receive_atom(log_atom3)
        cd.receive_atom(log_atom4)
        cd.receive_atom(log_atom5)
        cd.receive_atom(log_atom6)
        t2 = t+cd.expire_persistence_time
        cd.do_persist(t2+3)
        with open(cd.persistence_file_name, "r") as f:
            self.assertEqual(f.read(), f'[[["string:a"], [97, 98, 100, 102, 115], [{t2 + 5}, {t2 + 5}, {t2 + 3}, {t2 + 3}, {t2 + 5}]], [["string:b"], [97, 109], [{t2 + 6}, {t2 + 6}]]]')

        self.assertEqual(cd.charsets, {("a",): set([ord(x) for x in "abdfs"]), ("b",): set([ord(x) for x in "am"])})
        cd.charsets = {}
        cd.load_persistence_data()
        self.assertEqual(cd.charsets, {("a",): set([ord(x) for x in "abdfs"]), ("b",): set([ord(x) for x in "am"])})

        other = CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, output_logline=False)
        self.assertEqual(other.charsets, cd.charsets)

        cd.expire_persistence_time = None
        cd.do_persist()
        with open(cd.persistence_file_name, "r") as f:
            self.assertEqual(f.read(), f'[[["string:a"], [97, 98, 100, 102, 115]], [["string:b"], [97, 109]]]')

        other = CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, output_logline=False)
        self.assertEqual(other.charsets, cd.charsets)
        self.assertEqual(other.charsets_timestamps, {})

        other.expire_persistence_time = 86400
        other.receive_atom(log_atom1)
        other.receive_atom(log_atom2)
        other.receive_atom(log_atom3)
        other.receive_atom(log_atom4)
        other.receive_atom(log_atom5)
        other.receive_atom(log_atom6)
        t2 = t + other.expire_persistence_time
        other.do_persist(t2 + 3)
        self.assertEqual(other.charsets, {("a",): set([ord(x) for x in "abdfsx"]), ("b",): set([ord(x) for x in "amxyz"])})
        self.assertNotEqual(other.charsets_timestamps, {})

def test6validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, ["default"], ["/model/id"], ["/model/value"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, None, ["/model/id"], ["/model/value"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, "", ["/model/id"], ["/model/value"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, b"Default", ["/model/id"], ["/model/value"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, True, ["/model/id"], ["/model/value"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, 123, ["/model/id"], ["/model/value"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, 123.3, ["/model/id"], ["/model/value"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, {"id": "Default"}, ["/model/id"], ["/model/value"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, (), ["/model/id"], ["/model/value"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, set(), ["/model/id"], ["/model/value"])

        self.assertRaises(ValueError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], [""], ["/model/value"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], "", ["/model/value"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], b"Default", ["/model/value"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], True, ["/model/value"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], 123, ["/model/value"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], 123.3, ["/model/value"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], {"id": "Default"}, ["/model/value"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], (), ["/model/value"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], set(), ["/model/value"])

        self.assertRaises(ValueError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], [""])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], "")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], b"Default")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], True)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], 123)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], 123.3)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], {"id": "Default"})
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ())
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], set())

        self.assertRaises(ValueError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], persistence_id="")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], persistence_id=None)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], persistence_id=b"Default")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], persistence_id=True)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], persistence_id=123)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], persistence_id=123.22)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], persistence_id={"id": "Default"})
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], persistence_id=["Default"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], persistence_id=[])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], persistence_id=())
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], persistence_id=set())
        CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], persistence_id="Default")

        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=b"True")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode="True")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=123)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=123.22)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode={"id": "Default"})
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=["Default"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=[])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=())
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=set())
        CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True)

        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], output_logline=None)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], output_logline=b"True")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], output_logline="True")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], output_logline=123)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], output_logline=123.22)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], output_logline={"id": "Default"})
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], output_logline=["Default"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], output_logline=[])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], output_logline=())
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], output_logline=set())
        CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], output_logline=True)

        self.assertRaises(ValueError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], ignore_list=[""])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], ignore_list="")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], ignore_list=b"Default")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], ignore_list=True)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], ignore_list=123)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], ignore_list=123.3)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], ignore_list={"id": "Default"})
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], ignore_list=())
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], ignore_list=set())
        CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], ignore_list=[])
        CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], ignore_list=None)

        self.assertRaises(ValueError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], constraint_list=[""])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], constraint_list="")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], constraint_list=b"Default")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], constraint_list=True)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], constraint_list=123)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], constraint_list=123.3)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], constraint_list={"id": "Default"})
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], constraint_list=())
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], constraint_list=set())
        CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], constraint_list=[])
        CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], constraint_list=None)

        self.assertRaises(ValueError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_time=-1)
        self.assertRaises(ValueError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_time=0)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_time=b"Default")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_time="123")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_time={"id": "Default"})
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_time=["Default"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_time=[])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_time=())
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_time=set())
        CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_time=100)
        CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_time=100.22)

        self.assertRaises(ValueError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=-1)
        self.assertRaises(ValueError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=0)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=b"Default")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time="123")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time={"id": "Default"})
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=["Default"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=[])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=())
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=set())
        CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=100)
        CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=100.22)

        self.assertRaises(ValueError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], learn_mode=True, stop_learning_time=100, stop_learning_no_anomaly_time=100)

        self.assertRaises(ValueError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], log_resource_ignore_list=["/tmp/syslog"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], log_resource_ignore_list="")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], log_resource_ignore_list=b"Default")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], log_resource_ignore_list=True)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], log_resource_ignore_list=123)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], log_resource_ignore_list=123.22)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], log_resource_ignore_list={"id": "Default"})
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], log_resource_ignore_list=())
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], log_resource_ignore_list=set())
        CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], log_resource_ignore_list=["file:///tmp/syslog"])

        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], severity="Test")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], severity=b"Default")
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], severity=True)
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], severity={"id": "Default"})
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], severity=["Default"])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], severity=[])
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], severity=())
        self.assertRaises(TypeError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], severity=set())
        self.assertRaises(ValueError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], severity=123)
        self.assertRaises(ValueError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], severity=123.22)
        self.assertRaises(ValueError, CharsetDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], severity=-0.22)
        CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], severity=None)
        CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], severity=0)
        CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], severity=1)
        CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], severity=0.1)
        CharsetDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], severity=0.99)


if __name__ == "__main__":
    unittest.main()
