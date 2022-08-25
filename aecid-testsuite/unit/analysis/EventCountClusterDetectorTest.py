import unittest
from aminer.analysis.EventCountClusterDetector import EventCountClusterDetector
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


class EventCountClusterDetectorTest(TestBase):
    """Unittests for the EventFrequencyDetector."""

    def test1_normal_count_detection(self):
        """
        This test checks the normal operation of the ECCD
        """
        description = "Test1EventFrequencyDetector"

        # Initialize detector for analyzing values in one path in time windows of 10 seconds
        test_handler = TestHandler()
        eccd = EventCountClusterDetector(aminer_config=self.aminer_config, anomaly_event_handlers=[test_handler],
                                                          target_path_list=['/p/value'], id_path_list=['/p/id'],
                                                          window_size=10, num_windows=50,
                                                          confidence_factor=0.5, idf=True, norm=False, add_normal=False,
                                                          check_empty_windows=False, persistence_id='Default',
                                                          learn_mode=True, output_logline=False)
        self.analysis_context.register_component(eccd, description)

        # The following log atoms are created:
        #  window 1:
        #   value a: 1 time by x, 1 time by y
        #   value b: 1 time by x
        #  window 2:
        #   value a: 2 times by x, 1 time by y
        #   value b: 1 time by x
        #  window 3:
        #   value b: 1 time by x
        #   value c: 1 time by x
        #  window 4:
        #   value a: 1 time by x
        # Start of window 1:
        m1_1 = MatchElement('/p/value', b'a', b'a', None)
        m1_2 = MatchElement('/p/id', b'x', b'x', None)
        p1 = ParserMatch(MatchElement('/p', b'ax', b'ax', [m1_1, m1_2]))
        log_atom_1 = LogAtom(b'ax', p1, 1, None)

        m2_1 = MatchElement('/p/value', b'a', b'a', None)
        m2_2 = MatchElement('/p/id', b'y', b'y', None)
        p2 = ParserMatch(MatchElement('/p', b'ay', b'ay', [m2_1, m2_2]))
        log_atom_2 = LogAtom(b'ay', p2, 2, None)

        m3_1 = MatchElement('/p/value', b'b', b'b', None)
        m3_2 = MatchElement('/p/id', b'x', b'x', None)
        p3 = ParserMatch(MatchElement('/p', b'bx', b'bx', [m3_1, m3_2]))
        log_atom_3 = LogAtom(b'bx', p3, 3, None)

        # Start of window 2:
        m4_1 = MatchElement('/p/value', b'a', b'a', None)
        m4_2 = MatchElement('/p/id', b'x', b'x', None)
        p4 = ParserMatch(MatchElement('/p', b'ax', b'ax', [m4_1, m4_2]))
        log_atom_4 = LogAtom(b'ax', p4, 13, None)

        m5_1 = MatchElement('/p/value', b'a', b'a', None)
        m5_2 = MatchElement('/p/id', b'y', b'y', None)
        p5 = ParserMatch(MatchElement('/p', b'ay', b'ay', [m5_1, m5_2]))
        log_atom_5 = LogAtom(b'ay', p5, 14, None)

        m6_1 = MatchElement('/p/value', b'b', b'b', None)
        m6_2 = MatchElement('/p/id', b'x', b'x', None)
        p6 = ParserMatch(MatchElement('/p', b'bx', b'bx', [m6_1, m6_2]))
        log_atom_6 = LogAtom(b'bx', p6, 15, None)

        m7_1 = MatchElement('/p/value', b'a', b'a', None)
        m7_2 = MatchElement('/p/id', b'x', b'x', None)
        p7 = ParserMatch(MatchElement('/p', b'ax', b'ax', [m7_1, m7_2]))
        log_atom_7 = LogAtom(b'ax', p4, 16, None)

        # Start of window 3:
        m8_1 = MatchElement('/p/value', b'c', b'c', None)
        m8_2 = MatchElement('/p/id', b'x', b'x', None)
        p8 = ParserMatch(MatchElement('/p', b'cx', b'cx', [m8_1, m8_2]))
        log_atom_8 = LogAtom(b'cx', p8, 23, None)

        m9_1 = MatchElement('/p/value', b'b', b'b', None)
        m9_2 = MatchElement('/p/id', b'x', b'x', None)
        p9 = ParserMatch(MatchElement('/p', b'bx', b'bx', [m9_1, m9_2]))
        log_atom_9 = LogAtom(b'bx', p9, 24, None)

        # Start of window 4:
        m10_1 = MatchElement('/p/value', b'a', b'a', None)
        m10_2 = MatchElement('/p/id', b'x', b'x', None)
        p10 = ParserMatch(MatchElement('/p', b'ax', b'ax', [m10_1, m10_2]))
        log_atom_10 = LogAtom(b'ax', p10, 43, None)

        # Forward log atoms to detector
        eccd.receive_atom(log_atom_1)
        self.assertFalse(test_handler.anomalies)
        eccd.receive_atom(log_atom_2)
        self.assertFalse(test_handler.anomalies)
        eccd.receive_atom(log_atom_3)
        self.assertFalse(test_handler.anomalies)
        eccd.receive_atom(log_atom_4)
        # End of first time window; first count vector triggers anomaly for x
        self.assertTrue(test_handler.anomalies)
        # Remove anomaly
        test_handler.anomalies = []
        eccd.receive_atom(log_atom_5)
        # End of first time window; first count vector triggers anomaly for y
        self.assertTrue(test_handler.anomalies)
        # Remove anomaly
        test_handler.anomalies = []
        eccd.receive_atom(log_atom_6)
        self.assertFalse(test_handler.anomalies)
        eccd.receive_atom(log_atom_7)
        self.assertFalse(test_handler.anomalies)
        eccd.receive_atom(log_atom_8)
        # No anomaly reported for x since 2 times a and 1 time b (window 1) is similar enough to 1 time a and 1 time b (window 2)
        self.assertFalse(test_handler.anomalies)
        eccd.receive_atom(log_atom_9)
        self.assertFalse(test_handler.anomalies)
        eccd.receive_atom(log_atom_10)
        # Check learned count vectors at end of third time window
        # For x, count vector from first and third windows are included in model; for y only first window
        self.assertEquals(eccd.known_counts, {('x',): [{('a',): 1, ('b',): 1}, {('c',): 1, ('b',): 1}], ('y',): [{('a',): 1}]})
        # Since a occurs in both x and y, its idf factor is only 0.176 (=log10(3/2)),
        # compared to b and c which have an idf factor of 0.477 (=log10(3/1)).
        # Comparing the count vectors for x in the first and third window, we see that
        #  a occurs only in first window, which increases diff to 0.176/0.176
        #  b occurs once in first and third windows, which updates diff to 0.176/0.653
        #  c occurs only in third window, which increaes diff to 0.653/1.13
        # The final score is thus 0.653/1.13=0.578, which exceeds the threshold of 0.5.
        self.assertEqual(test_handler.anomalies, [
            {'AnalysisComponent':
                {'AffectedLogAtomPaths': ['/p/value'],
                 'AffectedLogAtomFrequencies': [1, 1],
                 'AffectedIdValues': ['x'],
                 'AffectedLogAtomValues': [('c',), ('b',)]}, 'CountData': {
                     'ConfidenceFactor': 0.5, 'Confidence': 0.577893478883737
                     }}])

if __name__ == "__main__":
    unittest.main()
