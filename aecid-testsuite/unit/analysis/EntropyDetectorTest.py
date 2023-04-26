import unittest
from aminer.analysis.EntropyDetector import EntropyDetector
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


class EntropyDetectorTest(TestBase):
    """Unittests for the EntropyDetector."""

    def test1_normal_sequence_detection(self):
        """
        This test case checks the normal detection of new character sets.
        The charset detector is used to learn an alphabet and detect new characters for different identifiers.
        """
        return 1
        description = "Test1EntropyDetector"

        # Initialize detector
        test_handler = TestHandler()
        event_entropy_detector = EntropyDetector(self.aminer_config, [test_handler], ['/value'], 0.05, False, False, 'Default', True,
                                                 False)
        self.analysis_context.register_component(event_entropy_detector, description)

        # Prepare log atoms that represent string values. Anomalies are detected when character pair distributions deviate.
        # The following events are generated:
        #  value: aminer
        #  value: logdata-anomaly-miner
        #  value: ait-aecid
        #  value: austrian
        #  value: institute
        #  value: lfmvasacz
        m_1 = MatchElement('/value', b'aminer', b'aminer', None)
        parser_match_1 = ParserMatch(m_1)
        log_atom_1 = LogAtom(b'aminer', parser_match_1, 1, None)

        m_2 = MatchElement('/value', b'logdata-anomaly-miner', b'logdata-anomaly-miner', None)
        parser_match_2 = ParserMatch(m_2)
        log_atom_2 = LogAtom(b'logdata-anomaly-miner', parser_match_2, 2, None)

        m_3 = MatchElement('/value', b'ait-aecid', b'ait-aecid', None)
        parser_match_3 = ParserMatch(m_3)
        log_atom_3 = LogAtom(b'ait-aecid', parser_match_3, 3, None)

        m_4 = MatchElement('/value', b'austrian', b'austrian', None)
        parser_match_4 = ParserMatch(m_4)
        log_atom_4 = LogAtom(b'austrian', parser_match_4, 4, None)

        m_5 = MatchElement('/value', b'institute', b'institute', None)
        parser_match_5 = ParserMatch(m_5)
        log_atom_5 = LogAtom(b'institute', parser_match_5, 5, None)

        m_6 = MatchElement('/value', b'lfmvasacz', b'lfmvasacz', None)
        parser_match_6 = ParserMatch(m_6)
        log_atom_6 = LogAtom(b'lfmvasacz', parser_match_6, 6, None)

        # Forward log atoms to detector
        # First value should generate an anomaly, because no frequencies are known yet
        # Input: aminer
        # Expected output: Anomaly
        event_entropy_detector.receive_atom(log_atom_1)
        self.assertEqual(test_handler.anomaly, {'AnalysisComponent': {'AffectedLogAtomPaths': ['/value'],
                                                                      'AffectedLogAtomValues': ['aminer'],
                                                                      'CriticalValue': 0.0,
                                                                      'ProbabilityThreshold': 0.05}})
        test_handler.anomaly = None

        # Second value should not generate an anomaly, because it contains substring 'miner' which shares charpairs with 'aminer'
        # Input: logdata-anomaly-miner
        # Expected output: None
        event_entropy_detector.receive_atom(log_atom_2)
        self.assertIsNone(test_handler.anomaly)

        # Third value should not generate an anomaly, since it is a normal string
        # Input: ait-aecid
        # Expected output: None
        event_entropy_detector.receive_atom(log_atom_3)
        self.assertIsNone(test_handler.anomaly)

        # Fourth value should not generate an anomaly, since it is a normal string
        # Input: austrian
        # Expected output: None
        event_entropy_detector.receive_atom(log_atom_4)
        self.assertIsNone(test_handler.anomaly)

        # Fifth value should not generate an anomaly, since it is a normal string
        # Input: institute
        # Expected output: None
        event_entropy_detector.receive_atom(log_atom_5)
        self.assertIsNone(test_handler.anomaly)

        # Sixth value should generate an anomaly, since it is a randomly generated string
        # Input: lfmvasacz
        # Expected output: Anomaly
        event_entropy_detector.receive_atom(log_atom_6)
        self.assertEqual(test_handler.anomaly, {'AnalysisComponent': {'AffectedLogAtomPaths': ['/value'],
                                                                      'AffectedLogAtomValues': ['lfmvasacz'],
                                                                      'CriticalValue': 0.02,
                                                                      'ProbabilityThreshold': 0.05}})
        test_handler.anomaly = None


if __name__ == "__main__":
    unittest.main()
