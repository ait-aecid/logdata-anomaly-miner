import unittest
from aminer.analysis.EventSequenceDetector import EventSequenceDetector
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


class EventSequenceDetectorTest(TestBase):
    """Unittests for the EventSequenceDetectorDetector."""

    def test1_normal_sequence_detection(self):
        """This test case checks the normal detection of new sequences.
        The ESD is used to detect value sequences of length 2 and uses one id path to cope with
        interleaving sequences, i.e., the sequences only make sense when logs that contain the
        same id are considered."""
        description = "Test1EventSequenceDetector"

        # Initialize detector for sequence length 2
        test_handler = TestHandler()
        event_sequence_detector = EventSequenceDetector(self.aminer_config, ['/model/value'], [
            test_handler], ['/model/id'], 2, 'Default', True, output_log_line=False)
        self.analysis_context.register_component(event_sequence_detector, description)

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
        m_1 = MatchElement('/model/id', '1', '1', None)
        m_2 = MatchElement('/model/value', 'a', 'a', None)
        match_element_1 = MatchElement('/model', '1a', '1a', [m_1, m_2])
        parser_match_1 = ParserMatch(match_element_1)
        log_atom_1 = LogAtom('1a', parser_match_1, 1, None)

        m_3 = MatchElement('/model/id', '1', '1', None)
        m_4 = MatchElement('/model/value', 'b', 'b', None)
        match_element_2 = MatchElement('/model', '1b', '1b', [m_3, m_4])
        parser_match_2 = ParserMatch(match_element_2)
        log_atom_2 = LogAtom('1b', parser_match_2, 2, None)

        m_5 = MatchElement('/model/id', '2', '2', None)
        m_6 = MatchElement('/model/value', 'a', 'a', None)
        match_element_3 = MatchElement('/model', '2a', '2a', [m_5, m_6])
        parser_match_3 = ParserMatch(match_element_3)
        log_atom_3 = LogAtom('2a', parser_match_3, 3, None)

        m_7 = MatchElement('/model/id', '1', '1', None)
        m_8 = MatchElement('/model/value', 'c', 'c', None)
        match_element_4 = MatchElement('/model', '1c', '1c', [m_7, m_8])
        parser_match_4 = ParserMatch(match_element_4)
        log_atom_4 = LogAtom('1c', parser_match_4, 4, None)

        m_9 = MatchElement('/model/id', '2', '2', None)
        m_10 = MatchElement('/model/value', 'b', 'b', None)
        match_element_5 = MatchElement('/model', '2b', '2b', [m_9, m_10])
        parser_match_5 = ParserMatch(match_element_5)
        log_atom_5 = LogAtom('2b', parser_match_5, 5, None)

        # Forward log atoms to detector
        # Since sequence length is 2, first atom should not have any effect
        # Input: id: 1 value: a
        # Expected output: None
        event_sequence_detector.receive_atom(log_atom_1)
        self.assertIsNone(test_handler.anomaly)
        sequences_set = set()
        self.assertEqual(event_sequence_detector.sequences, sequences_set)

        # Second log atom should create first sequence
        # Input: id: 1 value: b
        # Expected output: New sequence (a, b) detected, added to known sequences
        event_sequence_detector.receive_atom(log_atom_2)
        self.assertEqual(test_handler.anomaly, {'AnalysisComponent': {'AffectedLogAtomPaths': [['/model/value']],
                                                                      'AffectedLogAtomValues': [('a',), ('b',)]}})
        sequences_set.add((('a',), ('b',)))
        self.assertEqual(event_sequence_detector.sequences, sequences_set)
        test_handler.anomaly = None

        # Next log atom is of different user, should not have any effect
        # Input: id: 2 value: a
        # Expected output: None
        event_sequence_detector.receive_atom(log_atom_3)
        self.assertIsNone(test_handler.anomaly)
        self.assertEqual(event_sequence_detector.sequences, sequences_set)

        # Next log atom is of user with id 1, but new value c, thus new sequence should be generated
        # Input: id: 1 value: c
        # Expected output: New sequence (b, c) detected, added to known sequences
        event_sequence_detector.receive_atom(log_atom_4)
        self.assertEqual(test_handler.anomaly, {'AnalysisComponent': {'AffectedLogAtomPaths': [['/model/value']],
                                                                      'AffectedLogAtomValues': [('b',), ('c',)]}})
        sequences_set.add((('b',), ('c',)))
        self.assertEqual(event_sequence_detector.sequences, sequences_set)
        test_handler.anomaly = None

        # Next log atom is of user with id 2, but sequence a, b is already known from user with id 1, thus no effect
        # Input: id: 2 value: b
        # Expected output: None
        event_sequence_detector.receive_atom(log_atom_5)
        self.assertIsNone(test_handler.anomaly)
        self.assertEqual(event_sequence_detector.sequences, sequences_set)


if __name__ == "__main__":
    unittest.main()
