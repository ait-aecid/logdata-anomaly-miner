import unittest
from aminer.analysis.ValueRangeDetector import ValueRangeDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase, DummyMatchContext, DummyFixedDataModelElement
from aminer.AminerConfig import DEFAULT_PERSISTENCE_PERIOD
import time
from datetime import datetime


class ValueRangeDetectorTest(TestBase):
    """Unittests for the ValueRangeDetectorDetector."""

    def test1receive_atom(self):
        """
        This test case checks the normal detection of new value ranges.
        The VRD is used to learn intervals and detect values outside of these ranges for two different identifiers.
        Test if log atoms are processed correctly and the detector is learning (learn_mode=True) and stops if learn_mode=False.
        Test if stop_learning_time and stop_learning_no_anomaly_timestamp are implemented properly.
        """
        expected_string = '%s Value range anomaly detected\n%s: "None" (%d lines)\n  %s\n\n'
        datetime_format_string = "%Y-%m-%d %H:%M:%S"
        t = round(time.time(), 3)

        # Prepare log atoms that represent two entities (id) with floats (value). Anomalies are generated when ranges are first established.
        # Then, one identifier (a) has a valid value, while the other one (b) has a value outside the range that generates an anomaly.
        # The following events are generated:
        #  id: a value: 2.5
        #  id: b value: 5
        #  id: a value: 4.75
        #  id: b value: 6.3
        #  id: a value: 4.25
        #  id: b value: 3.1
        m_1 = MatchElement("/model/id", b"a", b"a", None)
        m_2 = MatchElement("/model/value", b"2.5", 2.5, None)
        match_element_1 = MatchElement("/model", b"a2.5", b"a2.5", [m_1, m_2])
        parser_match_1 = ParserMatch(match_element_1)
        log_atom_1 = LogAtom(b"a2.5", parser_match_1, t, None)

        m_3 = MatchElement("/model/id", b"b", b"b", None)
        m_4 = MatchElement("/model/value", b"5", 5, None)
        match_element_2 = MatchElement("/model", b"b5", b"b5", [m_3, m_4])
        parser_match_2 = ParserMatch(match_element_2)
        log_atom_2 = LogAtom(b"b5", parser_match_2, t+1, None)

        m_5 = MatchElement("/model/id", b"a", b"a", None)
        m_6 = MatchElement("/model/value", b"4.75", 4.75, None)
        match_element_3 = MatchElement("/model", b"a4.75", b"a4.75", [m_5, m_6])
        parser_match_3 = ParserMatch(match_element_3)
        log_atom_3 = LogAtom(b"a4.75", parser_match_3, t+2, None)

        m_7 = MatchElement("/model/id", b"b", b"b", None)
        m_8 = MatchElement("/model/value", b"6.3", 6.3, None)
        match_element_4 = MatchElement("/model", b"b6.3", b"b6.3", [m_7, m_8])
        parser_match_4 = ParserMatch(match_element_4)
        log_atom_4 = LogAtom(b"b6.3", parser_match_4, t+3, None)

        m_9 = MatchElement("/model/id", b"a", b"a", None)
        m_10 = MatchElement("/model/value", b"4.25", 4.25, None)
        match_element_5 = MatchElement("/model", b"a4.25", b"a4.25", [m_9, m_10])
        parser_match_5 = ParserMatch(match_element_5)
        log_atom_5 = LogAtom(b"a4.25", parser_match_5, t+4, None)

        m_11 = MatchElement("/model/id", b"b", b"b", None)
        m_12 = MatchElement("/model/value", b"3.1", 3.1, None)
        match_element_6 = MatchElement("/model", b"b3.1", b"b3.1", [m_11, m_12])
        parser_match_6 = ParserMatch(match_element_6)
        log_atom_6 = LogAtom(b"b3.1", parser_match_6, t+5, None)

        # learn_mode = True, with id_path_list set

        # Forward log atoms to detector
        # First value of id (a) should not generate an anomaly
        # Input: id: a value: 2.5
        # Expected output: None
        value_range_detector = ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], "Default", True, False)
        value_range_detector.receive_atom(log_atom_1)
        self.assertEqual(self.output_stream.getvalue(), "")

        # First value of id (b) should not generate an anomaly
        # Input: id: b value: 5
        # Expected output: None
        value_range_detector.receive_atom(log_atom_2)
        self.assertEqual(self.output_stream.getvalue(), "")

        # Second value of id (a) should generate an anomaly for new range
        # Input: id: a value: 4.75
        # Expected output: Anomaly
        value_range_detector.receive_atom(log_atom_3)
        self.assertEqual(self.output_stream.getvalue(), expected_string % ( datetime.fromtimestamp(t+2).strftime(datetime_format_string),
            value_range_detector.__class__.__name__, 1, log_atom_3.raw_data.decode()))
        self.reset_output_stream()

        # Second value of id (b) should generate an anomaly for new range
        # Input: id: b value: 6.3
        # Expected output: Anomaly
        value_range_detector.receive_atom(log_atom_4)
        self.assertEqual(self.output_stream.getvalue(), expected_string % ( datetime.fromtimestamp(t+3).strftime(datetime_format_string),
            value_range_detector.__class__.__name__, 1, log_atom_4.raw_data.decode()))
        self.reset_output_stream()

        # Third value of id (a) is in expected range, thus no anomaly is generated
        # Input: id: a value: 4.25
        # Expected output: None
        value_range_detector.receive_atom(log_atom_5)
        self.assertEqual(self.output_stream.getvalue(), "")

        # Third value of id (b) is outside the expected range, thus anomaly is generated
        value_range_detector.receive_atom(log_atom_6)
        self.assertEqual(self.output_stream.getvalue(), expected_string % ( datetime.fromtimestamp(t+5).strftime(datetime_format_string),
            value_range_detector.__class__.__name__, 1, log_atom_6.raw_data.decode()))
        self.reset_output_stream()


        # learn_mode = True, without id_path_list set

        # Forward log atoms to detector
        # First value of id (a) should not generate an anomaly
        # Input: id: a value: 2.5
        # Expected output: None
        value_range_detector = ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], None, ["/model/value"], "Default", True, False)
        value_range_detector.receive_atom(log_atom_1)
        self.assertEqual(self.output_stream.getvalue(), "")

        # First value of id (b) should not generate an anomaly
        # Input: id: b value: 5
        # Expected output: Anomaly
        value_range_detector.receive_atom(log_atom_2)
        self.assertEqual(self.output_stream.getvalue(), expected_string % ( datetime.fromtimestamp(t+1).strftime(datetime_format_string),
            value_range_detector.__class__.__name__, 1, log_atom_2.raw_data.decode()))
        self.reset_output_stream()

        # Second value of id (a) should generate an anomaly for new range
        # Input: id: a value: 4.75
        # Expected output: None
        value_range_detector.receive_atom(log_atom_3)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.reset_output_stream()

        # Second value of id (b) should generate an anomaly for new range
        # Input: id: b value: 6.3
        # Expected output: Anomaly
        value_range_detector.receive_atom(log_atom_4)
        self.assertEqual(self.output_stream.getvalue(), expected_string % ( datetime.fromtimestamp(t+3).strftime(datetime_format_string),
            value_range_detector.__class__.__name__, 1, log_atom_4.raw_data.decode()))
        self.reset_output_stream()

        # Third value of id (a) is in expected range, thus no anomaly is generated
        # Input: id: a value: 4.25
        # Expected output: None
        value_range_detector.receive_atom(log_atom_5)
        self.assertEqual(self.output_stream.getvalue(), "")

        # All values are used in only one path, so this value should not produce an anomaly.
        value_range_detector.receive_atom(log_atom_6)
        self.assertEqual(self.output_stream.getvalue(), "")


        # learn_mode = False
        value_range_detector = ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], "Default", True, False)
        value_range_detector.ranges = {"min": {}, "max": {}}
        # setup
        value_range_detector.receive_atom(log_atom_1)
        self.assertEqual(self.output_stream.getvalue(), "")
        value_range_detector.receive_atom(log_atom_2)
        self.assertEqual(self.output_stream.getvalue(), "")
        value_range_detector.learn_mode = False

        value_range_detector.receive_atom(log_atom_4)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t + 3).strftime(datetime_format_string),
            value_range_detector.__class__.__name__, 1, log_atom_4.raw_data.decode()))
        self.reset_output_stream()

        # repeating should produce the same result
        value_range_detector.receive_atom(log_atom_4)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t + 3).strftime(datetime_format_string),
            value_range_detector.__class__.__name__, 1, log_atom_4.raw_data.decode()))
        self.reset_output_stream()

        # stop_learning_time
        value_range_detector = ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], "Default", True, False, stop_learning_time=100)
        log_atom_1.atom_time = t
        value_range_detector.receive_atom(log_atom_1)
        log_atom_2.atom_time = t + 99
        value_range_detector.receive_atom(log_atom_2)
        self.assertTrue(value_range_detector.learn_mode)
        log_atom_3.atom_time = t + 101
        value_range_detector.receive_atom(log_atom_3)
        self.assertFalse(value_range_detector.learn_mode)
        log_atom_2.atom_time = t + 1
        log_atom_3.atom_time = t + 2

        # stop_learning_no_anomaly_time
        value_range_detector = ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], "Default", True, False, stop_learning_no_anomaly_time=100)
        log_atom_1.atom_time = t
        value_range_detector.receive_atom(log_atom_1)
        log_atom_2.atom_time = t + 99
        value_range_detector.receive_atom(log_atom_2)
        self.assertTrue(value_range_detector.learn_mode)
        log_atom_3.atom_time = t + 100
        value_range_detector.receive_atom(log_atom_3)
        self.assertTrue(value_range_detector.learn_mode)
        log_atom_4.atom_time = t + 201
        value_range_detector.receive_atom(log_atom_4)
        self.assertFalse(value_range_detector.learn_mode)
        log_atom_2.atom_time = t + 1
        log_atom_3.atom_time = t + 2
        log_atom_4.atom_time = t + 2

    def test2do_timer(self):
        """Test if the do_timer method is implemented properly."""
        value_range_detector = ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], "Default", True, False)
        t = time.time()
        value_range_detector.next_persist_time = t + 400
        self.assertEqual(value_range_detector.do_timer(t + 200), 200)
        self.assertEqual(value_range_detector.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(value_range_detector.do_timer(t + 999), 1)
        self.assertEqual(value_range_detector.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

    def test3allowlist_event(self):
        """Test if the allowlist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        value_range_detector = ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["Default"], None, "Default", True, output_logline=False)
        analysis = "Analysis.%s"
        self.assertRaises(Exception, value_range_detector.allowlist_event, analysis % "NewMatchPathValueDetector", self.output_stream.getvalue(), None)

        # The ValueRangeDetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, value_range_detector.allowlist_event, analysis % value_range_detector.__class__.__name__, self.output_stream.getvalue(), ["random", "Data"])

        # Allowlist event which is in the ignore_list. If a value from the ignore_list is allowlisted, it should be deleted.
        value_range_detector.ignore_list = ["/s1"]
        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(value_range_detector.allowlist_event(analysis % value_range_detector.__class__.__name__, "/s1", None), "Allowlisted path %s." % "/s1")
        self.assertEqual(value_range_detector.constraint_list, ["/s1"])
        self.assertEqual(value_range_detector.ignore_list, [])

        value_range_detector.learn_mode = False
        self.assertEqual(value_range_detector.allowlist_event(analysis % value_range_detector.__class__.__name__, "/d1", None), "Allowlisted path %s." % "/d1")
        self.assertEqual(value_range_detector.constraint_list, ["/s1", "/d1"])

    def test4blocklist_event(self):
        """Test if the blocklist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        value_range_detector = ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["Default"], None, "Default", True, output_logline=False)
        analysis = "Analysis.%s"
        self.assertRaises(Exception, value_range_detector.blocklist_event, analysis % "NewMatchPathValueDetector", self.output_stream.getvalue(), None)

        # The ValueRangeDetector can not handle allowlisting data and therefore an exception is expected.
        self.assertRaises(Exception, value_range_detector.blocklist_event, analysis % value_range_detector.__class__.__name__, self.output_stream.getvalue(), ["random", "Data"])

        # Blocklist event which is in the constraint_list. If a value from the constraint_list is blocklisted, it should be deleted.
        value_range_detector.constraint_list = ["/s1"]
        # This test case checks in which cases an event is triggered and compares with expected results.
        self.assertEqual(value_range_detector.blocklist_event(analysis % value_range_detector.__class__.__name__, "/s1", None), "Blocklisted path /s1.")
        self.assertEqual(value_range_detector.ignore_list, ["/s1"])
        self.assertEqual(value_range_detector.constraint_list, [])

        value_range_detector.learn_mode = False
        self.assertEqual(value_range_detector.blocklist_event(analysis % value_range_detector.__class__.__name__, "/d1", None), "Blocklisted path /d1.")
        self.assertEqual(value_range_detector.ignore_list, ["/s1", "/d1"])

    def test5persistence(self):
        """Test the do_persist and load_persistence_data methods."""
        value_range_detector = ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], "Default", True, False)

        # Prepare log atoms that represent two entities (id) with floats (value). Anomalies are generated when ranges are first established.
        # Then, one identifier (a) has a valid value, while the other one (b) has a value outside the range that generates an anomaly.
        # The following events are generated:
        #  id: a value: 2.5
        #  id: b value: 5
        #  id: a value: 4.75
        #  id: b value: 6.3
        #  id: a value: 4.25
        #  id: b value: 3.1
        m_1 = MatchElement("/model/id", b"a", b"a", None)
        m_2 = MatchElement("/model/value", b"2.5", 2.5, None)
        match_element_1 = MatchElement("/model", b"a2.5", b"a2.5", [m_1, m_2])
        parser_match_1 = ParserMatch(match_element_1)
        log_atom_1 = LogAtom(b"a2.5", parser_match_1, 1, None)

        m_3 = MatchElement("/model/id", b"b", b"b", None)
        m_4 = MatchElement("/model/value", b"5", 5, None)
        match_element_2 = MatchElement("/model", b"b5", b"b5", [m_3, m_4])
        parser_match_2 = ParserMatch(match_element_2)
        log_atom_2 = LogAtom(b"b5", parser_match_2, 2, None)

        m_5 = MatchElement("/model/id", b"a", b"a", None)
        m_6 = MatchElement("/model/value", b"4.75", 4.75, None)
        match_element_3 = MatchElement("/model", b"a4.75", b"a4.75", [m_5, m_6])
        parser_match_3 = ParserMatch(match_element_3)
        log_atom_3 = LogAtom(b"a4.75", parser_match_3, 3, None)

        m_7 = MatchElement("/model/id", b"b", b"b", None)
        m_8 = MatchElement("/model/value", b"6.3", 6.3, None)
        match_element_4 = MatchElement("/model", b"b6.3", b"b6.3", [m_7, m_8])
        parser_match_4 = ParserMatch(match_element_4)
        log_atom_4 = LogAtom(b"b6.3", parser_match_4, 4, None)

        m_9 = MatchElement("/model/id", b"a", b"a", None)
        m_10 = MatchElement("/model/value", b"4.25", 4.25, None)
        match_element_5 = MatchElement("/model", b"a4.25", b"a4.25", [m_9, m_10])
        parser_match_5 = ParserMatch(match_element_5)
        log_atom_5 = LogAtom(b"a4.25", parser_match_5, 5, None)

        m_11 = MatchElement("/model/id", b"b", b"b", None)
        m_12 = MatchElement("/model/value", b"3.1", 3.1, None)
        match_element_6 = MatchElement("/model", b"b3.1", b"b3.1", [m_11, m_12])
        parser_match_6 = ParserMatch(match_element_6)
        log_atom_6 = LogAtom(b"b3.1", parser_match_6, 6, None)

        value_range_detector.receive_atom(log_atom_1)
        value_range_detector.receive_atom(log_atom_2)
        value_range_detector.receive_atom(log_atom_3)
        value_range_detector.receive_atom(log_atom_4)
        value_range_detector.receive_atom(log_atom_5)
        value_range_detector.receive_atom(log_atom_6)
        value_range_detector.do_persist()
        value_range_detector1 = ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], "Default", True, False)
        self.assertEqual(value_range_detector.ranges, value_range_detector1.ranges)
        self.assertEqual(value_range_detector1.ranges, {"min": {("a",): 2.5, ("b",): 3.1}, "max": {("a",): 4.75, ("b",): 6.3}})

        with open(value_range_detector.persistence_file_name, "r") as f:
            self.assertEqual(f.read(), """{"string:min": {"tuple:('a',)": 2.5, "tuple:('b',)": 3.1}, "string:max": {"tuple:('a',)": 4.75, "tuple:('b',)": 6.3}}""")

        value_range_detector.ranges = {"min": {}, "max": {}}
        value_range_detector.load_persistence_data()
        self.assertEqual(value_range_detector.ranges, {"min": {("a",): 2.5, ("b",): 3.1}, "max": {("a",): 4.75, ("b",): 6.3}})

        other = ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], ["/model/value"], "Default", False, False)
        self.assertEqual(value_range_detector.ranges, other.ranges)

    def test6validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, ["default"], ["Default"])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, None, ["Default"])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, "", ["Default"])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, b"Default", ["Default"])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, True, ["Default"])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, 123, ["Default"])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, 123.3, ["Default"])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, {"id": "Default"}, ["Default"])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, (), ["Default"])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, set(), ["Default"])

        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], "")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], b"Default")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], True)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], 123)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], 123.22)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], {"id": "Default"})
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ())
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], set())
        ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["Default"])
        ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], None)
        ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], [])

        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], target_path_list="")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], target_path_list=b"Default")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], target_path_list=True)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], target_path_list=123)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], target_path_list=123.22)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], target_path_list={"id": "Default"})
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], target_path_list="Default")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], target_path_list=())
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], target_path_list=set())
        ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["Default"], target_path_list=["Default"])

        self.assertRaises(ValueError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], persistence_id="")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], persistence_id=None)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], persistence_id=b"Default")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], persistence_id=True)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], persistence_id=123)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], persistence_id=123.22)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], persistence_id={"id": "Default"})
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], persistence_id=["Default"])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], persistence_id=[])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], persistence_id=())
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], persistence_id=set())
        ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["Default"], persistence_id="Default")

        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=b"True")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode="True")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=123)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=123.22)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode={"id": "Default"})
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=["Default"])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=[])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=())
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=set())
        ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True)

        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], output_logline=None)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], output_logline=b"True")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], output_logline="True")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], output_logline=123)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], output_logline=123.22)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], output_logline={"id": "Default"})
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], output_logline=["Default"])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], output_logline=[])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], output_logline=())
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], output_logline=set())
        ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["Default"], output_logline=True)

        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], ignore_list="")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], ignore_list=b"Default")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], ignore_list=True)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], ignore_list=123)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], ignore_list=123.22)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], ignore_list={"id": "Default"})
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], ignore_list="Default")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], ignore_list=())
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], ignore_list=set())
        ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["Default"], ignore_list=["Default"])

        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], constraint_list="")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], constraint_list=b"Default")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], constraint_list=True)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], constraint_list=123)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], constraint_list=123.22)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], constraint_list={"id": "Default"})
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], constraint_list="Default")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], constraint_list=())
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], constraint_list=set())
        ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["Default"], constraint_list=["Default"])

        self.assertRaises(ValueError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_time=-1)
        self.assertRaises(ValueError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_time=0)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_time=b"Default")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_time="123")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_time={"id": "Default"})
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_time=["Default"])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_time=[])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_time=())
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_time=set())
        ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_time=100)
        ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_time=100.22)

        self.assertRaises(ValueError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_no_anomaly_time=-1)
        self.assertRaises(ValueError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_no_anomaly_time=0)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_no_anomaly_time=b"Default")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_no_anomaly_time="123")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_no_anomaly_time={"id": "Default"})
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_no_anomaly_time=["Default"])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_no_anomaly_time=[])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_no_anomaly_time=())
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_no_anomaly_time=set())
        ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_no_anomaly_time=100)
        ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_no_anomaly_time=100.22)

        self.assertRaises(ValueError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], learn_mode=True, stop_learning_time=100, stop_learning_no_anomaly_time=100)

        self.assertRaises(ValueError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], log_resource_ignore_list=["/tmp/syslog"])
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], log_resource_ignore_list="")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], log_resource_ignore_list=b"Default")
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], log_resource_ignore_list=True)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], log_resource_ignore_list=123)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], log_resource_ignore_list=123.22)
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], log_resource_ignore_list={"id": "Default"})
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], log_resource_ignore_list=())
        self.assertRaises(TypeError, ValueRangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], log_resource_ignore_list=set())
        ValueRangeDetector(self.aminer_config, [self.stream_printer_event_handler], ["Default"], log_resource_ignore_list=["file:///tmp/syslog"])


if __name__ == "__main__":
    unittest.main()
