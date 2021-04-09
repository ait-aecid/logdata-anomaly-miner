import unittest
from aminer.analysis.PCADetector import PCADetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase


class TestHandler():
    """Dummy anomaly handler."""

    def __init__(self):
        self.anomalies = []

    # skipcq: PYL-W0613
    def receive_event(self, name, msg, ll, evdat, atom, obj):
        """Receive anomaly information."""
        self.anomalies.append(evdat)


class PCADetectorTest(TestBase):
    """Unittests for the PCADetector."""

    def test1_normal_pca_detection(self):
        """
        This test case checks the normal detection of value frequencies using PCA.
        """
        description = "Test1PCADetector"

        # Initialize detector for analyzing values in one path in time windows of 10 seconds
        test_handler = TestHandler()
        pca_detector = PCADetector(self.aminer_config, ['/value'], [test_handler], 10, 2, 0.9, 3, 'Default', True, output_log_line=False)
        self.analysis_context.register_component(pca_detector, description)

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
        m_1 = MatchElement('/value', 'a', 'a', None)
        parser_match_1 = ParserMatch(m_1)
        log_atom_1 = LogAtom('a', parser_match_1, 1, None)

        m_2 = MatchElement('/value', 'b', 'b', None)
        parser_match_2 = ParserMatch(m_2)
        log_atom_2 = LogAtom('b', parser_match_2, 3, None)

        m_3 = MatchElement('/value', 'a', 'a', None)
        parser_match_3 = ParserMatch(m_3)
        log_atom_3 = LogAtom('a', parser_match_3, 7, None)

        # Start of window 2:
        m_4 = MatchElement('/value', 'a', 'a', None)
        parser_match_4 = ParserMatch(m_4)
        log_atom_4 = LogAtom('a', parser_match_4, 13, None)

        m_5 = MatchElement('/value', 'b', 'b', None)
        parser_match_5 = ParserMatch(m_5)
        log_atom_5 = LogAtom('b', parser_match_5, 15, None)

        # Start of window 3:
        m_6 = MatchElement('/value', 'a', 'a', None)
        parser_match_6 = ParserMatch(m_6)
        log_atom_6 = LogAtom('b', parser_match_6, 27, None)

        # Start of window 4:
        m_7 = MatchElement('/value', 'a', 'a', None)
        parser_match_7 = ParserMatch(m_7)
        log_atom_7 = LogAtom('a', parser_match_7, 33, None)

        m_8 = MatchElement('/value', 'a', 'a', None)
        parser_match_8 = ParserMatch(m_8)
        log_atom_8 = LogAtom('a', parser_match_8, 34, None)

        m_9 = MatchElement('/value', 'a', 'a', None)
        parser_match_9 = ParserMatch(m_9)
        log_atom_9 = LogAtom('a', parser_match_9, 36, None)

        m_10 = MatchElement('/value', 'a', 'a', None)
        parser_match_10 = ParserMatch(m_10)
        log_atom_10 = LogAtom('a', parser_match_10, 37, None)

        m_11 = MatchElement('/value', 'b', 'b', None)
        parser_match_11 = ParserMatch(m_11)
        log_atom_11 = LogAtom('b', parser_match_11, 38, None)

        # Start of window 5:
        m_12 = MatchElement('/value', 'a', 'a', None)
        parser_match_12 = ParserMatch(m_12)
        log_atom_12 = LogAtom('a', parser_match_12, 45, None)

        # Forward log atoms to detector
        # Log atoms of windows 1 to 3 build up the count matrix
        # Input: log atoms of windows 1 to 3
        # Expected output: No anomalies reported
        pca_detector.receive_atom(log_atom_1)
        pca_detector.receive_atom(log_atom_2)
        pca_detector.receive_atom(log_atom_3)
        pca_detector.receive_atom(log_atom_4)
        pca_detector.receive_atom(log_atom_5)
        pca_detector.receive_atom(log_atom_6)
        self.assertFalse(test_handler.anomalies)

        # Log atoms of window 4 build the count vector for that window
        # Input: b; log atoms of window 4
        # Expected output: No anomalies reported
        pca_detector.receive_atom(log_atom_7)
        pca_detector.receive_atom(log_atom_8)
        pca_detector.receive_atom(log_atom_9)
        pca_detector.receive_atom(log_atom_10)
        pca_detector.receive_atom(log_atom_11)
        self.assertFalse(test_handler.anomalies)
        # At this point, the event count matrix contains the counts from the first three windows
        self.assertEqual(pca_detector.event_count_matrix, 
            [{'/value': {'a': 2, 'b': 1}}, {'/value': {'a': 1, 'b': 1}}, {'/value': {'a': 1, 'b': 0}}])
        # The count vector contains the counts of the fourth window
        self.assertEqual(pca_detector.event_count_vector, {'/value': {'a': 4, 'b': 1}})

        # Log atom of window 5 triggers comparison of count vector from window 4 with PCA
        # Input: log atoms of window 5
        # Expected output: Anomaly reported on count vector of fourth window
        pca_detector.receive_atom(log_atom_12)
        self.assertEqual(test_handler.anomalies, [{'AnalysisComponent': {'AffectedLogAtomPaths': ['/value'], 
            'AffectedLogAtomValues': [['a', 'b']], 'AffectedValueCounts': [[4, 1]], 'AnomalyScore': 9.0}}])
        # Event count matrix is shifted by 1 so that window 0 is removed and window 4 is appended
        self.assertEqual(pca_detector.event_count_matrix, 
            [{'/value': {'a': 1, 'b': 1}}, {'/value': {'a': 1, 'b': 0}}, {'/value': {'a': 4, 'b': 1}}])

if __name__ == "__main__":
    unittest.main()
