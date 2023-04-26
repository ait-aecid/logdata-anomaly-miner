import unittest
from aminer.analysis.CharsetDetector import CharsetDetector
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


class CharsetDetectorTest(TestBase):
    """Unittests for the ValueRangeDetectorDetector."""

    def test1_normal_sequence_detection(self):
        """
        This test case checks the normal detection of new character sets.
        The charset detector is used to learn an alphabet and detect new characters for different identifiers.
        """
        return 1
        description = "Test1CharsetDetector"

        # Initialize detector
        test_handler = TestHandler()
        event_charset_detector = CharsetDetector(self.aminer_config, [test_handler], ['/model/id'], ['/model/value'], 'Default', True,
                                                 False)
        self.analysis_context.register_component(event_charset_detector, description)

        # Prepare log atoms that represent two entities (id) with strings (value). Anomalies are generated when new characters are observed.
        # The following events are generated:
        #  id: a value: abc
        #  id: b value: xyz
        #  id: a value: asdf
        #  id: a value: xxx
        #  id: a value: bass
        #  id: a value: max
        m_1 = MatchElement('/model/id', b'a', b'a', None)
        m_2 = MatchElement('/model/value', b'abc', b'abc', None)
        match_element_1 = MatchElement('/model', b'aabc', b'aabc', [m_1, m_2])
        parser_match_1 = ParserMatch(match_element_1)
        log_atom_1 = LogAtom(b'aabc', parser_match_1, 1, None)

        m_3 = MatchElement('/model/id', b'b', b'b', None)
        m_4 = MatchElement('/model/value', b'xyz', b'xyz', None)
        match_element_2 = MatchElement('/model', b'bxyz', b'bxyz', [m_3, m_4])
        parser_match_2 = ParserMatch(match_element_2)
        log_atom_2 = LogAtom(b'bxyz', parser_match_2, 2, None)

        m_5 = MatchElement('/model/id', b'a', b'a', None)
        m_6 = MatchElement('/model/value', b'asdf', b'asdf', None)
        match_element_3 = MatchElement('/model', b'aasdf', b'aasdf', [m_5, m_6])
        parser_match_3 = ParserMatch(match_element_3)
        log_atom_3 = LogAtom(b'aasdf', parser_match_3, 3, None)

        m_7 = MatchElement('/model/id', b'a', b'a', None)
        m_8 = MatchElement('/model/value', b'xxx', b'xxx', None)
        match_element_4 = MatchElement('/model', b'bxxx', b'bxxx', [m_7, m_8])
        parser_match_4 = ParserMatch(match_element_4)
        log_atom_4 = LogAtom(b'bxxx', parser_match_4, 4, None)

        m_9 = MatchElement('/model/id', b'a', b'a', None)
        m_10 = MatchElement('/model/value', b'bass', b'bass', None)
        match_element_5 = MatchElement('/model', b'abass', b'abass', [m_9, m_10])
        parser_match_5 = ParserMatch(match_element_5)
        log_atom_5 = LogAtom(b'abass', parser_match_5, 5, None)

        m_11 = MatchElement('/model/id', b'a', b'a', None)
        m_12 = MatchElement('/model/value', b'max', b'max', None)
        match_element_6 = MatchElement('/model', b'bmax', b'bmax', [m_11, m_12])
        parser_match_6 = ParserMatch(match_element_6)
        log_atom_6 = LogAtom(b'bmax', parser_match_6, 6, None)

        # Forward log atoms to detector
        # First value of id (a) should not generate an anomaly
        # Input: id: a value: abc
        # Expected output: None
        event_charset_detector.receive_atom(log_atom_1)
        self.assertIsNone(test_handler.anomaly)

        # First value of id (b) should not generate an anomaly
        # Input: id: b value: xyz
        # Expected output: None
        event_charset_detector.receive_atom(log_atom_2)
        self.assertIsNone(test_handler.anomaly)

        # Second value of id (a) should generate an anomaly for new characters ('sdf' of 'asdf' not in 'abc')
        # Input: id: a value: asdf
        # Expected output: Anomaly
        event_charset_detector.receive_atom(log_atom_3)
        self.assertEqual(test_handler.anomaly, {'AnalysisComponent': {'AffectedLogAtomPaths': ['/model/value'],
                                                                      'AffectedLogAtomValues': ['asdf'],
                                                                      'MissingCharacters': ['s', 'd', 'f']}})
        test_handler.anomaly = None

        # Third value of id (a) should generate an anomaly for new characters ('x' not in 'abcsdf', only in 'xyz' from other id (b))
        # Input: id: a value: xxx
        # Expected output: Anomaly
        event_charset_detector.receive_atom(log_atom_4)
        self.assertEqual(test_handler.anomaly, {'AnalysisComponent': {'AffectedLogAtomPaths': ['/model/value'],
                                                                      'AffectedLogAtomValues': ['xxx'],
                                                                      'MissingCharacters': ['x']}})
        test_handler.anomaly = None

        # Fourth value of id (a) should not generate an anomaly (all characters of 'bass' in 'abcsdfx')
        # Input: id: a value: bass
        # Expected output: None
        event_charset_detector.receive_atom(log_atom_5)
        self.assertIsNone(test_handler.anomaly)

        # Fifth value of id (a) should generate an anomaly for new characters ('m' of 'max' not in 'abcsdfx')
        event_charset_detector.receive_atom(log_atom_6)
        self.assertEqual(test_handler.anomaly, {'AnalysisComponent': {'AffectedLogAtomPaths': ['/model/value'],
                                                                      'AffectedLogAtomValues': ['max'],
                                                                      'MissingCharacters': ['m']}})
        test_handler.anomaly = None


if __name__ == "__main__":
    unittest.main()
