import unittest
from aminer.analysis.ValueRangeDetector import ValueRangeDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase


class TestHandler():
    """Dummy anomaly handler."""

    def __init__(self):
        self.anomaly = None

    # skipcq: PYL-W0613
    def receive_event(self, name, msg, ll, evdat, atom, obj):
        """Receive anomaly information."""
        self.anomaly = evdat


class ValueRangeDetectorTest(TestBase):
    """Unittests for the ValueRangeDetectorDetector."""

    def test1_normal_sequence_detection(self):
        """
        This test case checks the normal detection of new value ranges.
        The VRD is used to learn intervals and detect values outside of these ranges for two different identifiers.
        """
        description = "Test1ValueRangeeDetector"

        # Initialize detector
        test_handler = TestHandler()
        value_range_detector = ValueRangeDetector(self.aminer_config, [test_handler], ['/model/id'], ['/model/value'], 'Default', True,
                                                  False)
        self.analysis_context.register_component(value_range_detector, description)

        # Prepare log atoms that represent two entities (id) with floats (value). Anomalies are generated when ranges are first established.
        # Then, one identifier (a) has a valid value, while the other one (b) has a value outside of the range that generates an anomaly.
        # The following events are generated:
        #  id: a value: 2.5
        #  id: b value: 5
        #  id: a value: 4.75
        #  id: b value: 6.3
        #  id: a value: 4.25
        #  id: b value: 3.1
        m_1 = MatchElement('/model/id', b'a', b'a', None)
        m_2 = MatchElement('/model/value', b'2.5', 2.5, None)
        match_element_1 = MatchElement('/model', b'a2.5', b'a2.5', [m_1, m_2])
        parser_match_1 = ParserMatch(match_element_1)
        log_atom_1 = LogAtom(b'a2.5', parser_match_1, 1, None)

        m_3 = MatchElement('/model/id', b'b', b'b', None)
        m_4 = MatchElement('/model/value', b'5', 5, None)
        match_element_2 = MatchElement('/model', b'b5', b'b5', [m_3, m_4])
        parser_match_2 = ParserMatch(match_element_2)
        log_atom_2 = LogAtom(b'b5', parser_match_2, 2, None)

        m_5 = MatchElement('/model/id', b'a', b'a', None)
        m_6 = MatchElement('/model/value', b'4.75', 4.75, None)
        match_element_3 = MatchElement('/model', b'a4.75', b'a4.75', [m_5, m_6])
        parser_match_3 = ParserMatch(match_element_3)
        log_atom_3 = LogAtom(b'a4.75', parser_match_3, 3, None)

        m_7 = MatchElement('/model/id', b'b', b'b', None)
        m_8 = MatchElement('/model/value', b'6.3', 6.3, None)
        match_element_4 = MatchElement('/model', b'b6.3', b'b6.3', [m_7, m_8])
        parser_match_4 = ParserMatch(match_element_4)
        log_atom_4 = LogAtom(b'b6.3', parser_match_4, 4, None)

        m_9 = MatchElement('/model/id', b'a', b'a', None)
        m_10 = MatchElement('/model/value', b'4.25', 4.25, None)
        match_element_5 = MatchElement('/model', b'a4.25', b'a4.25', [m_9, m_10])
        parser_match_5 = ParserMatch(match_element_5)
        log_atom_5 = LogAtom(b'a4.25', parser_match_5, 5, None)

        m_11 = MatchElement('/model/id', b'b', b'b', None)
        m_12 = MatchElement('/model/value', b'3.1', 3.1, None)
        match_element_6 = MatchElement('/model', b'b3.1', b'b3.1', [m_11, m_12])
        parser_match_6 = ParserMatch(match_element_6)
        log_atom_6 = LogAtom(b'b3.1', parser_match_6, 6, None)

        # Forward log atoms to detector
        # First value of id (a) should not generate an anomaly
        # Input: id: a value: 2.5
        # Expected output: None
        value_range_detector.receive_atom(log_atom_1)
        self.assertIsNone(test_handler.anomaly)

        # First value of id (b) should not generate an anomaly
        # Input: id: b value: 5
        # Expected output: None
        value_range_detector.receive_atom(log_atom_2)
        self.assertIsNone(test_handler.anomaly)

        # Second value of id (a) should generate an anomaly for new range
        # Input: id: a value: 4.75
        # Expected output: Anomaly
        value_range_detector.receive_atom(log_atom_3)
        self.assertEqual(test_handler.anomaly, {'AnalysisComponent': {'AffectedLogAtomPaths': ['/model/value'],
                                                                      'AffectedLogAtomValues': [4.75],
                                                                      'IDpaths': ['/model/id'],
                                                                      'IDvalues': ['a'],
                                                                      'Range': [2.5, 2.5]}})
        test_handler.anomaly = None

        # Second value of id (b) should generate an anomaly for new range
        # Input: id: b value: 6.3
        # Expected output: Anomaly
        value_range_detector.receive_atom(log_atom_4)
        self.assertEqual(test_handler.anomaly, {'AnalysisComponent': {'AffectedLogAtomPaths': ['/model/value'],
                                                                      'AffectedLogAtomValues': [6.3],
                                                                      'IDpaths': ['/model/id'],
                                                                      'IDvalues': ['b'],
                                                                      'Range': [5, 5]}})
        test_handler.anomaly = None

        # Third value of id (a) is in expected range, thus no anomaly is generated
        # Input: id: a value: 4.25
        # Expected output: None
        value_range_detector.receive_atom(log_atom_5)
        self.assertIsNone(test_handler.anomaly)

        # Third value of id (b) is outside of expected range, thus anomaly is generated
        value_range_detector.receive_atom(log_atom_6)
        self.assertEqual(test_handler.anomaly, {'AnalysisComponent': {'AffectedLogAtomPaths': ['/model/value'],
                                                                      'AffectedLogAtomValues': [3.1],
                                                                      'IDpaths': ['/model/id'],
                                                                      'IDvalues': ['b'],
                                                                      'Range': [5, 6.3]}})
        test_handler.anomaly = None

    def test2_do_persist(self):
        """Test if learned ranges are persisted and loaded successfully."""
        description = "Test2ValueRangeeDetector"

        # Initialize detector
        test_handler = TestHandler()
        value_range_detector = ValueRangeDetector(self.aminer_config, [test_handler], ['/model/id'], ['/model/value'], 'Default', True,
                                                  False)
        self.analysis_context.register_component(value_range_detector, description)

        # Prepare log atoms that represent two entities (id) with floats (value). Anomalies are generated when ranges are first established.
        # Then, one identifier (a) has a valid value, while the other one (b) has a value outside of the range that generates an anomaly.
        # The following events are generated:
        #  id: a value: 2.5
        #  id: b value: 5
        #  id: a value: 4.75
        #  id: b value: 6.3
        #  id: a value: 4.25
        #  id: b value: 3.1
        m_1 = MatchElement('/model/id', b'a', b'a', None)
        m_2 = MatchElement('/model/value', b'2.5', 2.5, None)
        match_element_1 = MatchElement('/model', b'a2.5', b'a2.5', [m_1, m_2])
        parser_match_1 = ParserMatch(match_element_1)
        log_atom_1 = LogAtom(b'a2.5', parser_match_1, 1, None)

        m_3 = MatchElement('/model/id', b'b', b'b', None)
        m_4 = MatchElement('/model/value', b'5', 5, None)
        match_element_2 = MatchElement('/model', b'b5', b'b5', [m_3, m_4])
        parser_match_2 = ParserMatch(match_element_2)
        log_atom_2 = LogAtom(b'b5', parser_match_2, 2, None)

        m_5 = MatchElement('/model/id', b'a', b'a', None)
        m_6 = MatchElement('/model/value', b'4.75', 4.75, None)
        match_element_3 = MatchElement('/model', b'a4.75', b'a4.75', [m_5, m_6])
        parser_match_3 = ParserMatch(match_element_3)
        log_atom_3 = LogAtom(b'a4.75', parser_match_3, 3, None)

        m_7 = MatchElement('/model/id', b'b', b'b', None)
        m_8 = MatchElement('/model/value', b'6.3', 6.3, None)
        match_element_4 = MatchElement('/model', b'b6.3', b'b6.3', [m_7, m_8])
        parser_match_4 = ParserMatch(match_element_4)
        log_atom_4 = LogAtom(b'b6.3', parser_match_4, 4, None)

        m_9 = MatchElement('/model/id', b'a', b'a', None)
        m_10 = MatchElement('/model/value', b'4.25', 4.25, None)
        match_element_5 = MatchElement('/model', b'a4.25', b'a4.25', [m_9, m_10])
        parser_match_5 = ParserMatch(match_element_5)
        log_atom_5 = LogAtom(b'a4.25', parser_match_5, 5, None)

        m_11 = MatchElement('/model/id', b'b', b'b', None)
        m_12 = MatchElement('/model/value', b'3.1', 3.1, None)
        match_element_6 = MatchElement('/model', b'b3.1', b'b3.1', [m_11, m_12])
        parser_match_6 = ParserMatch(match_element_6)
        log_atom_6 = LogAtom(b'b3.1', parser_match_6, 6, None)

        value_range_detector.receive_atom(log_atom_1)
        value_range_detector.receive_atom(log_atom_2)
        value_range_detector.receive_atom(log_atom_3)
        value_range_detector.receive_atom(log_atom_4)
        value_range_detector.receive_atom(log_atom_5)
        value_range_detector.receive_atom(log_atom_6)
        value_range_detector.do_persist()
        value_range_detector1 = ValueRangeDetector(self.aminer_config, [test_handler], ['/model/id'], ['/model/value'], 'Default', True,
                                                   False)
        self.assertEqual(value_range_detector.ranges_min, value_range_detector1.ranges_min)
        self.assertEqual(value_range_detector.ranges_max, value_range_detector1.ranges_max)
        self.assertEqual(value_range_detector1.ranges_min, {('a',): 2.5, ('b',): 3.1})
        self.assertEqual(value_range_detector1.ranges_max, {('a',): 4.75, ('b',): 6.3})


if __name__ == "__main__":
    unittest.main()
