import time

from aminer.analysis.NewMatchIdValueComboDetector import NewMatchIdValueComboDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase, DummyMatchContext, DummyFixedDataModelElement, DummySequenceModelElement
from aminer.AminerConfig import DEFAULT_PERSISTENCE_PERIOD
from datetime import datetime


class NewMatchIdValueComboDetectorTest(TestBase):
    """Unittests for the NewMatchIdValueComboDetector."""

    match_context = DummyMatchContext(b" pid=25537 uid=2")
    fdme1 = DummyFixedDataModelElement("s1", b" pid=")
    fdme2 = DummyFixedDataModelElement("d1", b"25537")
    seq1 = DummySequenceModelElement("seq", [fdme1, fdme2])
    match_element1 = seq1.get_match_element("", match_context)

    match_context = DummyMatchContext(b"ddd 25538ddd 25539")
    fdme3 = DummyFixedDataModelElement("s1", b"ddd ")
    fdme4 = DummyFixedDataModelElement("d1", b"25538")
    fdme5 = DummyFixedDataModelElement("d1", b"25539")
    seq2 = DummySequenceModelElement("seq", [fdme3, fdme4])
    match_element2 = seq2.get_match_element("", match_context)
    seq3 = DummySequenceModelElement("seq", [fdme3, fdme5])
    match_element3 = seq3.get_match_element("", match_context)

    def test1receive_atom(self):
        """
        Test if log atoms are processed correctly and the detector is learning (learn_mode=True) and stops if learn_mode=False.
        Test if stop_learning_time and stop_learning_no_anomaly_timestamp are implemented properly.
        """
        expected_string = '%s New value combination(s) detected\n%s: "None" (%d lines)\n  %s\n\n'
        datetime_format_string = "%Y-%m-%d %H:%M:%S"
        # learn_mode = True
        nmivcd = NewMatchIdValueComboDetector(self.aminer_config, ["/seq/s1", "/seq/d1"], [self.stream_printer_event_handler], ["/seq/d1"], 120, learn_mode=True, output_logline=False)
        t = round(time.time(), 3)

        log_atom1 = LogAtom(self.match_element1.match_string, ParserMatch(self.match_element1), t, nmivcd)
        log_atom2 = LogAtom(self.match_element2.match_string, ParserMatch(self.match_element2), t, nmivcd)
        log_atom3 = LogAtom(self.match_element3.match_string, ParserMatch(self.match_element3), t, nmivcd)

        self.assertTrue(nmivcd.receive_atom(log_atom1))
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t).strftime(datetime_format_string), nmivcd.__class__.__name__, 1, "{'/seq/s1': ' pid=', '/seq/d1': '25537'}"))
        self.reset_output_stream()

        # repeating should NOT produce the same result
        self.assertTrue(nmivcd.receive_atom(log_atom1))
        self.assertEqual(self.output_stream.getvalue(), "")
        self.reset_output_stream()

        # learn_mode = False
        nmivcd.learn_mode = False
        self.assertTrue(nmivcd.receive_atom(log_atom2))
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t).strftime(datetime_format_string), nmivcd.__class__.__name__, 1, "{'/seq/s1': 'ddd ', '/seq/d1': '25538'}"))
        self.reset_output_stream()

        # repeating should produce the same result
        self.assertTrue(nmivcd.receive_atom(log_atom2))
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t).strftime(datetime_format_string), nmivcd.__class__.__name__, 1, "{'/seq/s1': 'ddd ', '/seq/d1': '25538'}"))
        self.reset_output_stream()

        # allow_missing_values_flag=True
        nmivcd.allow_missing_values_flag = True
        self.assertTrue(nmivcd.receive_atom(log_atom3))
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t).strftime(datetime_format_string), nmivcd.__class__.__name__, 1, "{'/seq/s1': 'ddd ', '/seq/d1': '25539'}"))

        # stop_learning_time
        nmivcd = NewMatchIdValueComboDetector(self.aminer_config, ["/seq/s1", "/seq/d1"], [self.stream_printer_event_handler], ["/seq/d1"], 120, learn_mode=True, output_logline=False, stop_learning_time=100)
        self.assertTrue(nmivcd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 99
        self.assertTrue(nmivcd.receive_atom(log_atom1))
        self.assertTrue(nmivcd.learn_mode)
        log_atom1.atom_time = t + 101
        self.assertTrue(nmivcd.receive_atom(log_atom1))
        self.assertFalse(nmivcd.learn_mode)

        # stop_learning_no_anomaly_time
        nmivcd = NewMatchIdValueComboDetector(self.aminer_config, ["/seq/s1", "/seq/d1"], [self.stream_printer_event_handler], ["/seq/d1"], 120, learn_mode=True, output_logline=False, stop_learning_no_anomaly_time=100)
        log_atom1.atom_time = t
        self.assertTrue(nmivcd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 100
        self.assertTrue(nmivcd.receive_atom(log_atom1))
        self.assertTrue(nmivcd.learn_mode)
        log_atom2.atom_time = t + 100
        self.assertTrue(nmivcd.receive_atom(log_atom2))
        self.assertTrue(nmivcd.learn_mode)
        log_atom1.atom_time = t + 200
        self.assertTrue(nmivcd.receive_atom(log_atom1))
        self.assertTrue(nmivcd.learn_mode)
        log_atom1.atom_time = t + 201
        self.assertTrue(nmivcd.receive_atom(log_atom1))
        self.assertFalse(nmivcd.learn_mode)

    def test2do_timer(self):
        """Test if the do_timer method is implemented properly."""
        nmivcd = NewMatchIdValueComboDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], ["path/id"], 120, learn_mode=True, output_logline=False)
        t = time.time()
        nmivcd.next_persist_time = t + 400
        self.assertEqual(nmivcd.do_timer(t + 200), 200)
        self.assertEqual(nmivcd.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(nmivcd.do_timer(t + 999), 1)
        self.assertEqual(nmivcd.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

    def test3allowlist_event(self):
        """Test if the allowlist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        nmivcd = NewMatchIdValueComboDetector(self.aminer_config, ["/seq/s1", "/seq/d1"], [self.stream_printer_event_handler], ["/seq/d1"], 100, learn_mode=True, output_logline=False)
        t = round(time.time(), 3)
        analysis = "Analysis.%s"
        value = "value"
        value2 = "2"
        log_atom1 = LogAtom(self.match_element1.match_string, ParserMatch(self.match_element1), t, nmivcd)
        nmivcd.receive_atom(log_atom1)
        self.assertRaises(Exception, nmivcd.allowlist_event, analysis % "NewMatchPathDetector", self.output_stream.getvalue(), None)

        # The NewMatchPathValueComboDetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, nmivcd.allowlist_event, analysis % nmivcd.__class__.__name__, self.output_stream.getvalue(), ["random", "Data"])

        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(nmivcd.allowlist_event(analysis % nmivcd.__class__.__name__, {"/seq/s1": value, "/seq/d1": value2}, None), "Allowlisted path(es) %s with %s." % ("/seq/s1, /seq/d1", {"/seq/s1": value, "/seq/d1": value2}))
        self.assertEqual(nmivcd.known_values, [{"/seq/s1": " pid=", "/seq/d1": "25537"},  {"/seq/s1": value, "/seq/d1": value2}])

        self.assertRaises(TypeError, nmivcd.allowlist_event, analysis % nmivcd.__class__.__name__, {"/seq/s1": None, "/seq/d1": value2}, None)
        self.assertRaises(TypeError, nmivcd.allowlist_event, analysis % nmivcd.__class__.__name__, {"/seq/d1": value2}, None)
        self.assertRaises(TypeError, nmivcd.allowlist_event, analysis % nmivcd.__class__.__name__, {"/seq/s2": value, "/seq/d1": value2}, None)

        # allow_missing_values_flag = True
        nmivcd.allow_missing_values_flag = True
        self.assertEqual(nmivcd.allowlist_event(analysis % nmivcd.__class__.__name__,  {"/seq/s1": None, "/seq/d1": value2}, None), "Allowlisted path(es) %s with %s." % ("/seq/s1, /seq/d1", {"/seq/s1": None, "/seq/d1": value2}))
        self.assertEqual(nmivcd.known_values, [{"/seq/s1": " pid=", "/seq/d1": "25537"},  {"/seq/s1": value, "/seq/d1": value2}, {"/seq/s1": None, "/seq/d1": value2}])

    def test4persistence(self):
        """Test the do_persist and load_persistence_data methods."""
        nmivcd = NewMatchIdValueComboDetector(self.aminer_config, ["/seq/s1", "/seq/d1"], [self.stream_printer_event_handler], ["/seq/d1"], 100, learn_mode=True, output_logline=False)
        t = round(time.time(), 3)
        log_atom1 = LogAtom(self.match_element1.match_string, ParserMatch(self.match_element1), t, nmivcd)
        log_atom2 = LogAtom(self.match_element2.match_string, ParserMatch(self.match_element2), t, nmivcd)

        self.assertTrue(nmivcd.receive_atom(log_atom1))
        self.assertTrue(nmivcd.receive_atom(log_atom2))
        self.assertEqual(nmivcd.known_values, [{"/seq/d1": "25537", "/seq/s1": " pid="}, {"/seq/d1": "25538", "/seq/s1": "ddd "}])
        nmivcd.do_persist()
        with open(nmivcd.persistence_file_name, "r") as f:
            self.assertEqual(f.read(), '[{"string:/seq/s1": "string: pid=", "string:/seq/d1": "string:25537"}, {"string:/seq/s1": "string:ddd ", "string:/seq/d1": "string:25538"}]')

        nmivcd.known_values = []
        nmivcd.load_persistence_data()
        self.assertEqual(nmivcd.known_values, [{"/seq/d1": "25537", "/seq/s1": " pid="}, {"/seq/d1": "25538", "/seq/s1": "ddd "}])

        other = NewMatchIdValueComboDetector(self.aminer_config, [self.match_element1.path, self.match_element2.path], [self.stream_printer_event_handler], ["/seq/s1/id", "/seq/d1/id"], 100)
        self.assertEqual(nmivcd.known_values, other.known_values)

    def test5validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        ids = ["path/id"]
        self.assertRaises(ValueError, NewMatchIdValueComboDetector, self.aminer_config, [""], [self.stream_printer_event_handler], ids, 1)
        self.assertRaises(ValueError, NewMatchIdValueComboDetector, self.aminer_config, [], [self.stream_printer_event_handler], ids, 1)
        self.assertRaises(ValueError, NewMatchIdValueComboDetector, self.aminer_config, None, [self.stream_printer_event_handler], ids, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, "", [self.stream_printer_event_handler], ids, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, b"Default", [self.stream_printer_event_handler], ids, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, True, [self.stream_printer_event_handler], ids, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, 123, [self.stream_printer_event_handler], ids, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, 123.3, [self.stream_printer_event_handler], ids, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, {"id": "Default"}, [self.stream_printer_event_handler], ids, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, (), [self.stream_printer_event_handler], ids, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, set(), [self.stream_printer_event_handler], ids, 1)

        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], ["default"], ids, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], None, ids, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], "", ids, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], b"Default", ids, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], True, ids, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], 123, ids, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], 123.3, ids, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], {"id": "Default"}, ids, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], (), ids, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], set(), ids, 1)

        self.assertRaises(ValueError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], [""], 1)
        self.assertRaises(ValueError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], [], 1)
        self.assertRaises(ValueError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], None, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], "", 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], b"Default", 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], True, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], 123, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], 123.3, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], {"id": "Default"}, 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], (), 1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], set(), 1)

        self.assertRaises(ValueError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 0)
        self.assertRaises(ValueError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, -1)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, ["default"])
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, None)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, "")
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, b"default")
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, True)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, {"id": "Default"})
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, ())
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, set())
        NewMatchIdValueComboDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 0.1)

        self.assertRaises(ValueError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, persistence_id="")
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, persistence_id=None)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, persistence_id=b"Default")
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, persistence_id=True)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, persistence_id=123)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, persistence_id=123.22)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, persistence_id={"id": "Default"})
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, persistence_id=["Default"])
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, persistence_id=[])
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, persistence_id=())
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, persistence_id=set())
        NewMatchIdValueComboDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, persistence_id="Default")

        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, allow_missing_values_flag=b"True")
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, allow_missing_values_flag="True")
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, allow_missing_values_flag=123)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, allow_missing_values_flag=123.22)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, allow_missing_values_flag={"id": "Default"})
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, allow_missing_values_flag=["Default"])
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, allow_missing_values_flag=[])
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, allow_missing_values_flag=())
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, allow_missing_values_flag=set())
        NewMatchIdValueComboDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, allow_missing_values_flag=True)

        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=b"True")
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode="True")
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=123)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=123.22)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode={"id": "Default"})
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=["Default"])
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=[])
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=())
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=set())
        NewMatchIdValueComboDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True)

        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, output_logline=None)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, output_logline=b"True")
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, output_logline="True")
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, output_logline=123)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, output_logline=123.22)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, output_logline={"id": "Default"})
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, output_logline=["Default"])
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, output_logline=[])
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, output_logline=())
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, output_logline=set())
        NewMatchIdValueComboDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, output_logline=True)

        self.assertRaises(ValueError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_time=-1)
        self.assertRaises(ValueError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_time=0)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_time=b"Default")
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_time="123")
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_time={"id": "Default"})
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_time=["Default"])
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_time=[])
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_time=())
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_time=set())
        NewMatchIdValueComboDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_time=100)
        NewMatchIdValueComboDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_time=100.22)

        self.assertRaises(ValueError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_no_anomaly_time=-1)
        self.assertRaises(ValueError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_no_anomaly_time=0)
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_no_anomaly_time=b"Default")
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_no_anomaly_time="123")
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_no_anomaly_time={"id": "Default"})
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_no_anomaly_time=["Default"])
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_no_anomaly_time=[])
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_no_anomaly_time=())
        self.assertRaises(TypeError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_no_anomaly_time=set())
        NewMatchIdValueComboDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_no_anomaly_time=100)
        NewMatchIdValueComboDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_no_anomaly_time=100.22)

        self.assertRaises(ValueError, NewMatchIdValueComboDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], ids, 1, learn_mode=True, stop_learning_time=100, stop_learning_no_anomaly_time=100)
