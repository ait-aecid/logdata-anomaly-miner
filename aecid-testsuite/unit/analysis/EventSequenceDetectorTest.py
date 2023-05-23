import unittest
import time
from datetime import datetime
from aminer.analysis.EventSequenceDetector import EventSequenceDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase
from aminer.AminerConfig import DEFAULT_PERSISTENCE_PERIOD


class EventSequenceDetectorTest(TestBase):
    """Unittests for the EventSequenceDetectorDetector."""

    def test1receive_atom(self):
        """
        This test case checks the normal detection of new sequences. The ESD is used to detect value sequences of length 2 and uses one id
        path to cope with interleaving sequences, i.e., the sequences only make sense when logs that contain the same id are considered.
        Test if log atoms are processed correctly and the detector is learning (learn_mode=True) and stops if learn_mode=False.
        Test if stop_learning_time and stop_learning_no_anomaly_timestamp are implemented properly.
        """
        # Initialize detector for sequence length 2
        t = time.time()
        expected_string = '%s New sequence detected\n%s: "None" (%d lines)\n  %s\n\n'
        dtf = "%Y-%m-%d %H:%M:%S"

        # Prepare log atoms that represent two users (id) that produce interleaved sequence a, b, c
        # This means, user with id 1 creates sequence a, b, c, and user with id 2 creates sequence
        # a, b, however, these sequences are interleaved. The ESD resolves this issue using the id
        # as an id path (/model/id). The path of the values is /model/value.
        # The following events are generated:
        #  id: 1 value: a
        #  id: 1 value: b
        #  id: 2 value: a
        #  id: 1 value: c
        #  id: 2 value: b
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

        esd = EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], id_path_list=["/model/id"], seq_len=2, learn_mode=True, output_logline=False)

        esd.receive_atom(log_atom1)
        self.assertEqual(self.output_stream.getvalue(), "")
        sequences_set = set()
        self.assertEqual(esd.sequences, sequences_set)

        esd.receive_atom(log_atom2)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(esd.sequences, sequences_set)

        esd.receive_atom(log_atom3)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(esd.sequences, sequences_set)

        esd.receive_atom(log_atom4)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t + 4).strftime(dtf), esd.__class__.__name__, 1, "1c"))
        self.reset_output_stream()
        sequences_set.add((('/model', '/model/id', '/model/value'), ('/model', '/model/id', '/model/value')))
        self.assertEqual(esd.sequences, sequences_set)

        esd.receive_atom(log_atom5)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(esd.sequences, sequences_set)

        # target_path_list
        esd = EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], id_path_list=["/model/id"], target_path_list=["/model/value"], seq_len=2, learn_mode=True, output_logline=False)
        # Forward log atoms to detector
        # Since sequence length is 2, first atom should not have any effect
        # Input: id: 1 value: a
        # Expected output: None
        esd.receive_atom(log_atom1)
        self.assertEqual(self.output_stream.getvalue(), "")
        sequences_set = set()
        self.assertEqual(esd.sequences, sequences_set)

        # Second log atom should create first sequence
        # Input: id: 1 value: b
        # Expected output: New sequence (a, b) detected, added to known sequences
        esd.receive_atom(log_atom2)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(esd.sequences, sequences_set)

        # Next log atom is of different user, should not have any effect
        # Input: id: 2 value: a
        # Expected output: None
        esd.receive_atom(log_atom3)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(esd.sequences, sequences_set)

        # Next log atom is of user with id 1, but new value c, thus new sequence should be generated
        # Input: id: 1 value: c
        # Expected output: New sequence (b, c) detected, added to known sequences
        esd.receive_atom(log_atom4)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t + 4).strftime(dtf), esd.__class__.__name__, 1, "1c"))
        self.reset_output_stream()
        sequences_set.add((("a",), ("c",)))
        self.assertEqual(esd.sequences, sequences_set)

        # Next log atom is of user with id 2, but sequence a, b is already known from user with id 1, thus no effect
        # Input: id: 2 value: b
        # Expected output: None
        esd.receive_atom(log_atom5)
        self.assertEqual(self.output_stream.getvalue(),  expected_string % (datetime.fromtimestamp(t + 5).strftime(dtf), esd.__class__.__name__, 1, "2b"))
        self.reset_output_stream()
        sequences_set.add((("a",), ("b",)))
        self.assertEqual(esd.sequences, sequences_set)

        # allow_missing_id=True
        esd = EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], id_path_list=["/model/id"], target_path_list=["/model/value"], seq_len=2, learn_mode=True, output_logline=False, allow_missing_id=True)
        esd.receive_atom(log_atom1)
        self.assertEqual(self.output_stream.getvalue(), "")
        sequences_set = set()
        self.assertEqual(esd.sequences, sequences_set)

        esd.receive_atom(log_atom2)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(esd.sequences, sequences_set)

        esd.receive_atom(log_atom3)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(esd.sequences, sequences_set)

        esd.receive_atom(log_atom4)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t + 4).strftime(dtf), esd.__class__.__name__, 1, "1c"))
        self.reset_output_stream()
        sequences_set.add((("a",), ("c",)))
        self.assertEqual(esd.sequences, sequences_set)

        esd.receive_atom(log_atom5)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t + 5).strftime(dtf), esd.__class__.__name__, 1, "2b"))
        self.reset_output_stream()
        sequences_set.add((("a",), ("b",)))
        self.assertEqual(esd.sequences, sequences_set)

        # stop_learning_time
        esd = EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], id_path_list=["/model/id"], target_path_list=["/model/value"], seq_len=2, learn_mode=True, allow_missing_id=True, stop_learning_time=100)
        self.assertTrue(esd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 99
        self.assertTrue(esd.receive_atom(log_atom1))
        self.assertTrue(esd.learn_mode)
        log_atom1.atom_time = t + 101
        self.assertTrue(esd.receive_atom(log_atom1))
        self.assertFalse(esd.learn_mode)

        # stop_learning_no_anomaly_time
        esd = EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], id_path_list=["/model/id"], target_path_list=["/model/value"], seq_len=2, learn_mode=True, allow_missing_id=True, stop_learning_no_anomaly_time=100)
        log_atom1.atom_time = t
        self.assertTrue(esd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 100
        self.assertTrue(esd.receive_atom(log_atom1))
        self.assertTrue(esd.learn_mode)
        log_atom2.atom_time = t + 100
        self.assertTrue(esd.receive_atom(log_atom2))
        self.assertTrue(esd.learn_mode)
        log_atom1.atom_time = t + 200
        self.assertTrue(esd.receive_atom(log_atom3))
        self.assertTrue(esd.learn_mode)
        log_atom1.atom_time = t + 201
        self.assertTrue(esd.receive_atom(log_atom1))
        self.assertFalse(esd.learn_mode)

    def test2do_timer(self):
        """Test if the do_timer method is implemented properly."""
        esd = EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler])
        t = time.time()
        esd.next_persist_time = t + 400
        self.assertEqual(esd.do_timer(t + 200), 200)
        self.assertEqual(esd.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(esd.do_timer(t + 999), 1)
        self.assertEqual(esd.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

    def test3allowlist_event(self):
        """Test if the allowlist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        esd = EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler])
        t = round(time.time(), 3)
        analysis = "Analysis.%s"
        self.assertRaises(Exception, esd.allowlist_event, analysis % "NewMatchPathValueDetector", self.output_stream.getvalue(), None)

        # The EventSequenceDetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, esd.allowlist_event, analysis % esd.__class__.__name__, self.output_stream.getvalue(), ["random", "Data"])

        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(esd.allowlist_event(analysis % esd.__class__.__name__, "/s1", None), "Allowlisted path %s in %s." % ("/s1", analysis % esd.__class__.__name__))
        self.assertEqual(esd.constraint_list, ["/s1"])

        esd.learn_mode = False
        self.assertEqual(esd.allowlist_event(analysis % esd.__class__.__name__, "/d1", None), "Allowlisted path %s in %s." % ("/d1", analysis % esd.__class__.__name__))
        self.assertEqual(esd.constraint_list, ["/s1", "/d1"])

    def test4blocklist_event(self):
        """Test if the blocklist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        esd = EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler])
        t = round(time.time(), 3)
        analysis = "Analysis.%s"
        self.assertRaises(Exception, esd.blocklist_event, analysis % "NewMatchPathValueDetector", self.output_stream.getvalue(), None)

        # The EventSequenceDetector can not handle allowlisting data and therefore an exception is expected.
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
        esd = EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], id_path_list=["/model/id"], target_path_list=["/model/value"], seq_len=2, learn_mode=True)
        m1 = MatchElement("/model/id", b"1", b"1", None)
        m2 = MatchElement("/model/value", b"a", b"a", None)
        log_atom1 = LogAtom(b"1a", ParserMatch(MatchElement("/model", b"1a", b"1a", [m1, m2])), t + 1, None)

        m4 = MatchElement("/model/value", b"b", b"b", None)
        log_atom2 = LogAtom(b"1b", ParserMatch(MatchElement("/model", b"1b", b"1b", [m4])), t + 2, None)

        m5 = MatchElement("/model/id", b"2", b"2", None)
        m6 = MatchElement("/model/value", b"a", b"a", None)
        log_atom3 = LogAtom(b"2a", ParserMatch(MatchElement("/model", b"2a", b"2a", [m5, m6])), t + 3, None)

        m7 = MatchElement("/model/id", b"1", b"1", None)
        m8 = MatchElement("/model/value", b"c", b"c", None)
        log_atom4 = LogAtom(b"1c", ParserMatch(MatchElement("/model", b"1c", b"1c", [m7, m8])), t + 4, None)

        m9 = MatchElement("/model/id", b"2", b"2", None)
        m10 = MatchElement("/model/value", b"b", b"b", None)
        log_atom5 = LogAtom(b"2b", ParserMatch(MatchElement("/model", b"2b", b"2b", [m9, m10])), t + 5, None)

        esd.receive_atom(log_atom1)
        esd.receive_atom(log_atom2)
        esd.receive_atom(log_atom3)
        esd.receive_atom(log_atom4)
        esd.receive_atom(log_atom5)
        esd.do_persist()
        with open(esd.persistence_file_name, "r") as f:
            self.assertEqual(f.read(), '[[["string:a"], ["string:b"]], [["string:a"], ["string:c"]]]')

        self.assertEqual(esd.sequences, {(("a",), ("b",)), (("a",), ("c",))})
        esd.sequences = set()
        esd.load_persistence_data()
        self.assertEqual(esd.sequences, {(("a",), ("b",)), (("a",), ("c",))})

        other = EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], id_path_list=["/model/id"], target_path_list=["/model/value"], seq_len=2, learn_mode=True)
        self.assertEqual(other.sequences, {(("a",), ("b",)), (("a",), ("c",))})

    def test6validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, ["default"])
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, None)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, "")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, b"Default")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, True)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, 123)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, 123.3)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, {"id": "Default"})
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, ())
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, set())

        self.assertRaises(ValueError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=[""])
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list="")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=b"Default")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=True)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=123)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=123.3)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list={"id": "Default"})
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=())
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], id_path_list=set())
        EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], id_path_list=[])
        EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], id_path_list=None)

        self.assertRaises(ValueError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=[""])
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list="")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=b"Default")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=True)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=123)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=123.3)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list={"id": "Default"})
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=())
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], target_path_list=set())
        EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], target_path_list=[])
        EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], target_path_list=None)

        self.assertRaises(ValueError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], seq_len=-1)
        self.assertRaises(ValueError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], seq_len=0)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], seq_len=100.22)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], seq_len=b"Default")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], seq_len="123")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], seq_len={"id": "Default"})
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], seq_len=["Default"])
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], seq_len=[])
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], seq_len=())
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], seq_len=set())
        EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], seq_len=100)

        self.assertRaises(ValueError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], timeout=-1)
        self.assertRaises(ValueError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], timeout=0)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], timeout=b"Default")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], timeout="123")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], timeout={"id": "Default"})
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], timeout=["Default"])
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], timeout=[])
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], timeout=())
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], timeout=set())
        EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], timeout=100)
        EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], timeout=100.22)

        self.assertRaises(ValueError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id="")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=None)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=b"Default")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=True)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=123)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=123.22)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id={"id": "Default"})
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=["Default"])
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=[])
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=())
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], persistence_id=set())
        EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], persistence_id="Default")

        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=b"True")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode="True")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=123)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=123.22)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode={"id": "Default"})
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=["Default"])
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=[])
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=())
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=set())
        EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True)

        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=None)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=b"True")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline="True")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=123)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=123.22)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline={"id": "Default"})
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=["Default"])
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=[])
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=())
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], output_logline=set())
        EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], output_logline=True)

        self.assertRaises(ValueError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=[""])
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list="")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=b"Default")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=True)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=123)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=123.3)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list={"id": "Default"})
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=())
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], ignore_list=set())
        EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], ignore_list=[])
        EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], ignore_list=None)

        self.assertRaises(ValueError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=[""])
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list="")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=b"Default")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=True)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=123)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=123.3)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list={"id": "Default"})
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=())
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], constraint_list=set())
        EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], constraint_list=[])
        EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], constraint_list=None)

        self.assertRaises(ValueError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=-1)
        self.assertRaises(ValueError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=0)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=b"Default")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time="123")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time={"id": "Default"})
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=["Default"])
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=[])
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=())
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=set())
        EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100)
        EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100.22)

        self.assertRaises(ValueError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=-1)
        self.assertRaises(ValueError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=0)
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=b"Default")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time="123")
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time={"id": "Default"})
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=["Default"])
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=[])
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=())
        self.assertRaises(TypeError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=set())
        EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=100)
        EventSequenceDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=100.22)

        self.assertRaises(ValueError, EventSequenceDetector, self.aminer_config, [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100, stop_learning_no_anomaly_time=100)


if __name__ == "__main__":
    unittest.main()
