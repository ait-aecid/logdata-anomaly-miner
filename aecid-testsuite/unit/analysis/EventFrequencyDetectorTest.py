import unittest
from aminer.analysis.EventFrequencyDetector import EventFrequencyDetector
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


class EventFrequencyDetectorTest(TestBase):
    """Unittests for the EventFrequencyDetector."""

    def test1_normal_frequency_detection(self):
        """This test case checks the normal detection of new frequencies."""
        description = "Test1EventFrequencyDetector"

        # Initialize detector
        test_handler = TestHandler()
        event_frequency_detector = EventFrequencyDetector(self.aminer_config, ['/value'], [
            test_handler], 10, 2, 'Default', True, output_log_line=False)
        self.analysis_context.register_component(event_frequency_detector, description)

        # Prepare log atoms that represent different amounts of values a, b over time
        #  window 1:
        #   value a: 2 times
        #   value b: 1 time
        #  window 2:
        #   value a: 3 times
        #   value b: 1 time
        #  window 3:
        #   value a: 1 time
        #   value b: 0 times
        #  window 4:
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

        m_5 = MatchElement('/value', 'a', 'a', None)
        parser_match_5 = ParserMatch(m_5)
        log_atom_5 = LogAtom('a', parser_match_5, 15, None)

        m_6 = MatchElement('/value', 'b', 'b', None)
        parser_match_6 = ParserMatch(m_6)
        log_atom_6 = LogAtom('b', parser_match_6, 17, None)

        m_7 = MatchElement('/value', 'a', 'a', None)
        parser_match_7 = ParserMatch(m_7)
        log_atom_7 = LogAtom('a', parser_match_7, 19, None)

        # Start of window 3:
        m_8 = MatchElement('/value', 'a', 'a', None)
        parser_match_8 = ParserMatch(m_8)
        log_atom_8 = LogAtom('a', parser_match_8, 25, None)

        # Start of window 4:
        m_9 = MatchElement('/value', 'a', 'a', None)
        parser_match_9 = ParserMatch(m_9)
        log_atom_9 = LogAtom('a', parser_match_9, 35, None)

        # Forward log atoms to detector
        # Log atoms of initial window 1 should not create anomalies and add to counts
        # Add a
        event_frequency_detector.receive_atom(log_atom_1)
        self.assertFalse(test_handler.anomalies)
        self.assertEqual(event_frequency_detector.counts, {('a',): 1})
        self.assertEqual(event_frequency_detector.counts_prev, {})

        # Add b
        event_frequency_detector.receive_atom(log_atom_2)
        self.assertFalse(test_handler.anomalies)
        self.assertEqual(event_frequency_detector.counts, {('a',): 1, ('b',): 1})
        self.assertEqual(event_frequency_detector.counts_prev, {})

        # Add a
        event_frequency_detector.receive_atom(log_atom_3)
        self.assertFalse(test_handler.anomalies)
        self.assertEqual(event_frequency_detector.counts, {('a',): 2, ('b',): 1})
        self.assertEqual(event_frequency_detector.counts_prev, {})

        # Time window 2 should not create anomalies since a is within confidence (3 instead of 2 occurrences) and b is identical (1 occurrence).
        # Also, counts is moved to counts_prev.
        # Add a
        event_frequency_detector.receive_atom(log_atom_4)
        self.assertFalse(test_handler.anomalies)
        self.assertEqual(event_frequency_detector.counts, {('a',): 1})
        self.assertEqual(event_frequency_detector.counts_prev, {('a',): 2, ('b',): 1})

        # Add a
        event_frequency_detector.receive_atom(log_atom_5)
        self.assertFalse(test_handler.anomalies)
        self.assertEqual(event_frequency_detector.counts, {('a',): 2})
        self.assertEqual(event_frequency_detector.counts_prev, {('a',): 2, ('b',): 1})

        # Add b
        event_frequency_detector.receive_atom(log_atom_6)
        self.assertFalse(test_handler.anomalies)
        self.assertEqual(event_frequency_detector.counts, {('a',): 2, ('b',): 1})
        self.assertEqual(event_frequency_detector.counts_prev, {('a',): 2, ('b',): 1})

        # Add a
        event_frequency_detector.receive_atom(log_atom_7)
        self.assertFalse(test_handler.anomalies)
        self.assertEqual(event_frequency_detector.counts, {('a',): 3, ('b',): 1})
        self.assertEqual(event_frequency_detector.counts_prev, {('a',): 2, ('b',): 1})

        # Time window 3 should create 2 anomalies since a drops from 3 to 1 and b drops from 1 to 0, which will be reported in window 4.
        # Add a
        event_frequency_detector.receive_atom(log_atom_8)
        self.assertFalse(test_handler.anomalies)
        self.assertEqual(event_frequency_detector.counts, {('a',): 1})
        self.assertEqual(event_frequency_detector.counts_prev, {('a',): 3, ('b',): 1})

        # Time window 4 should not create anomalies since no log atom is received to evaluate it.
        # Add a
        # This should cause one anomaly for a and b respectively.
        event_frequency_detector.receive_atom(log_atom_9)
        self.assertEqual(test_handler.anomalies, [{'AnalysisComponent': {'AffectedLogAtomPaths': ['/value'], 'AffectedLogAtomValues': ['a']}, 'FrequencyData': {'ExpectedLogAtomValuesFrequency': 3, 'LogAtomValuesFrequency': 1, 'ConfidenceFactor': 2, 'Confidence': 0.6666666666666667}}, {'AnalysisComponent': {'AffectedLogAtomPaths': ['/value'], 'AffectedLogAtomValues': ['b']}, 'FrequencyData': {'ExpectedLogAtomValuesFrequency': 1, 'LogAtomValuesFrequency': 0, 'ConfidenceFactor': 2, 'Confidence': 1.0}}])
        self.assertEqual(event_frequency_detector.counts, {('a',): 1})
        self.assertEqual(event_frequency_detector.counts_prev, {('a',): 1})


if __name__ == "__main__":
    unittest.main()
