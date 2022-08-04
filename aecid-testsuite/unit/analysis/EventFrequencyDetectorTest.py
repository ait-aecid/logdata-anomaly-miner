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
        """
        This test case checks the normal detection of new frequencies.
        The EFD is used with one path to be analyzed over four time windows. The frequencies
        do not change a lot in the first time windows, thus no anomalies are generated. Then,
        value frequencies change and anomalies are created in the last time windows.
        """
        description = "Test1EventFrequencyDetector"

        # Initialize detector for analyzing values in one path in time windows of 10 seconds
        test_handler = TestHandler()
        event_frequency_detector = EventFrequencyDetector(aminer_config=self.aminer_config, anomaly_event_handlers=[test_handler],
                                                          target_path_list=['/value'], window_size=10, num_windows=1,
                                                          confidence_factor=0.51, empty_window_warnings=True, persistence_id='Default',
                                                          auto_include_flag=True, output_log_line=False)
        self.analysis_context.register_component(event_frequency_detector, description)

        # Prepare log atoms that represent different amounts of values a, b over time
        # Four time windows are used. The first time window is used for initialization. The
        # second time window represents normal behavior, i.e., the frequencies do not change
        # too much and no anomalies should be generated. The third window contains changes
        # of value frequencies and thus anomalies should be generated. The fourth time window
        # only has the purpose of marking the end of the third time window.
        # The following log atoms are created:
        #  window 1:
        #   value a: 2 times
        #   value b: 1 time
        #  window 2:
        #   value a: 3 times
        #   value b: 1 time
        #  window 3:
        #   value a: 0 times
        #   value b: 2 times
        #  window 4:
        #   value a: 1 time
        # Start of window 1:
        m_1 = MatchElement('/value', b'a', b'a', None)
        parser_match_1 = ParserMatch(m_1)
        log_atom_1 = LogAtom(b'a', parser_match_1, 1, None)

        m_2 = MatchElement('/value', b'b', b'b', None)
        parser_match_2 = ParserMatch(m_2)
        log_atom_2 = LogAtom(b'b', parser_match_2, 3, None)

        m_3 = MatchElement('/value', b'a', b'a', None)
        parser_match_3 = ParserMatch(m_3)
        log_atom_3 = LogAtom(b'a', parser_match_3, 7, None)

        # Start of window 2:
        m_4 = MatchElement('/value', b'a', b'a', None)
        parser_match_4 = ParserMatch(m_4)
        log_atom_4 = LogAtom(b'a', parser_match_4, 13, None)

        m_6 = MatchElement('/value', b'b', b'b', None)
        parser_match_6 = ParserMatch(m_6)
        log_atom_6 = LogAtom(b'b', parser_match_6, 17, None)

        m_7 = MatchElement('/value', b'a', b'a', None)
        parser_match_7 = ParserMatch(m_7)
        log_atom_7 = LogAtom(b'a', parser_match_7, 18, None)

        m_8 = MatchElement('/value', b'a', b'a', None)
        parser_match_8 = ParserMatch(m_8)
        log_atom_8 = LogAtom(b'a', parser_match_8, 19, None)

        # Start of window 3:
        m_9 = MatchElement('/value', b'b', b'b', None)
        parser_match_9 = ParserMatch(m_9)
        log_atom_9 = LogAtom(b'b', parser_match_9, 25, None)

        m_10 = MatchElement('/value', b'b', b'b', None)
        parser_match_10 = ParserMatch(m_10)
        log_atom_10 = LogAtom(b'b', parser_match_10, 25, None)

        # Start of window 4:
        m_11 = MatchElement('/value', b'a', b'a', None)
        parser_match_11 = ParserMatch(m_11)
        log_atom_11 = LogAtom(b'a', parser_match_11, 35, None)

        # Forward log atoms to detector
        # Log atoms of initial window 1 should not create anomalies and add to counts
        # Input: a; initial time window is started
        # Expected output: frequency of a is 1
        event_frequency_detector.receive_atom(log_atom_1)
        self.assertFalse(test_handler.anomalies)
        self.assertEqual(event_frequency_detector.counts, {('a',): [1]})

        # Input: b; initial time window is not finished
        # Expected output: frequency of b is 1 added to existing count
        event_frequency_detector.receive_atom(log_atom_2)
        self.assertFalse(test_handler.anomalies)
        self.assertEqual(event_frequency_detector.counts, {('a',): [1], ('b',): [1]})

        # Input: a; initial time window is not finished
        # Expected output: frequency of a is 2 replaces a in existing count
        event_frequency_detector.receive_atom(log_atom_3)
        self.assertFalse(test_handler.anomalies)
        self.assertEqual(event_frequency_detector.counts, {('a',): [2], ('b',): [1]})

        # Time window 2 should not create anomalies since a is in confidence (3 vs 2 occurrences) and b is identical (1 occurrence).
        # Input: a; initial time window is completed, second time window is started
        # Expected output: frequency of a is 1 in new time window count, old count remains unchanged
        event_frequency_detector.receive_atom(log_atom_4)
        self.assertFalse(test_handler.anomalies)
        self.assertEqual(event_frequency_detector.counts, {('a',): [2, 1], ('b',): [1, 0]})

        # Input: b; second time window is not finished
        # Expected output: frequency of b is 1 in new time window count, old count remains unchanged
        event_frequency_detector.receive_atom(log_atom_6)
        self.assertFalse(test_handler.anomalies)
        self.assertEqual(event_frequency_detector.counts, {('a',): [2, 1], ('b',): [1, 1]})

        # Input: a; second time window is not finished
        # Expected output: frequency of a is 3 in new time window count, old count remains unchanged
        event_frequency_detector.receive_atom(log_atom_7)
        self.assertFalse(test_handler.anomalies)
        self.assertEqual(event_frequency_detector.counts, {('a',): [2, 2], ('b',): [1, 1]})

        # Input: a; second time window is not finished
        # Expected output: frequency of a is 4 in new time window count, old count remains unchanged
        event_frequency_detector.receive_atom(log_atom_8)
        self.assertFalse(test_handler.anomalies)
        self.assertEqual(event_frequency_detector.counts, {('a',): [2, 3], ('b',): [1, 1]})

        # Time window 3 should create 2 anomalies since a drops from 3 to 0 and b increases from 1 to 2, which will be reported in window 4.
        # Anomalies are only reported when third time window is known to be completed, which will occur when subsequent atom is received.
        # Input: b; second time window is completed, third time window is started
        # Expected output: frequency of b is 1 in new time window count, old count remains unchanged
        event_frequency_detector.receive_atom(log_atom_9)
        self.assertFalse(test_handler.anomalies)
        self.assertEqual(event_frequency_detector.counts, {('a',): [2, 3, 0], ('b',): [1, 1, 1]})

        # Input: b; third ime window is not finished
        # Expected output: frequency of b is 2 in new time window count, old count remains unchanged
        event_frequency_detector.receive_atom(log_atom_10)
        self.assertFalse(test_handler.anomalies)
        self.assertEqual(event_frequency_detector.counts, {('a',): [2, 3, 0], ('b',): [1, 1, 2]})

        # Time window 4 should not create anomalies since no log atom is received to evaluate it.
        # Input: a; third time window is completed, fourth time window is started
        # Expected output: Anomalies for unexpected low counts of a (0 instead of 3) and b (2 instead of 1), frequency of a is 1 in new
        # time window count, old count remains unchanged
        event_frequency_detector.receive_atom(log_atom_11)
        self.assertEqual(test_handler.anomalies, [
            {'AnalysisComponent':
                {'AffectedLogAtomPaths': ['/value'],
                 'AffectedLogAtomValues': ['a']}, 'FrequencyData': {
                     'ExpectedLogAtomValuesFrequency': 3.0,
                     'ExpectedLogAtomValuesFrequencyRange': [1.0, 5.0],
                     'LogAtomValuesFrequency': 0,
                     'ConfidenceFactor': 0.51, 'Confidence': 1.0
                     }}, {'AnalysisComponent': {'AffectedLogAtomPaths': ['/value'],
                          'AffectedLogAtomValues': ['b']}, 'FrequencyData':
                              {'ExpectedLogAtomValuesFrequency': 1.0,
                               'ExpectedLogAtomValuesFrequencyRange': [1.0, 1.0],
                               'LogAtomValuesFrequency': 2,
                               'ConfidenceFactor': 0.51,
                               'Confidence': 0.5}}])
        self.assertEqual(event_frequency_detector.counts, {('a',): [3, 0, 1], ('b',): [1, 2, 0]})


if __name__ == "__main__":
    unittest.main()
