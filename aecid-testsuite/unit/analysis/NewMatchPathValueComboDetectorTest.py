import unittest
from aminer.parsing import MatchContext, FixedDataModelElement, DecimalIntegerValueModelElement, ParserMatch, SequenceModelElement
from aminer.analysis.NewMatchPathValueComboDetector import NewMatchPathValueComboDetector
from aminer.input.LogAtom import LogAtom
import time
from unit.TestBase import TestBase
from datetime import datetime


class NewMatchPathValueComboDetectorTest(TestBase):
    __expected_string = '%s New value combination(s) detected\n%s: "%s" (%d lines)\n%s\n\n'
    fixed_dme = FixedDataModelElement('s1', b'25537 uid=')
    fixed_dme2 = FixedDataModelElement('s2', b' uid=2')
    datetime_format_string = '%Y-%m-%d %H:%M:%S'
    first_seq_s1 = 'first/seq/s1'
    first_seq_d1 = 'first/seq/d1'
    string = "  first/seq: b'25537 uid=2'\n  " + first_seq_s1 + ": b'25537 uid='\n  " + first_seq_d1 + ": 2\n(b'25537 uid=', 2)"
    string2 = "  (b'25537 uid=', 2)\nb'25537 uid=2'"

    decimal_integer_value_me = DecimalIntegerValueModelElement('d1', DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                                                               DecimalIntegerValueModelElement.PAD_TYPE_NONE)

    match_context_sequence_me = MatchContext(b'25537 uid=2')
    seq = SequenceModelElement('seq', [fixed_dme, decimal_integer_value_me])
    match_element_sequence_me = seq.get_match_element('first', match_context_sequence_me)

    match_context_sequence_me2 = MatchContext(b'25537 uid=2')
    seq2 = SequenceModelElement('seq2', [decimal_integer_value_me, fixed_dme2])
    match_element_sequence_me2 = seq2.get_match_element('second', match_context_sequence_me2)

    def test1_log_atom_not_known(self):
        """This test case checks the correct processing of unknown log lines, which in reality means that an anomaly has been found. The
        output is directed to an output stream and compared for accuracy. The auto_include_flag is False and the output must be
        repeatable on second run."""
        description = "Test1NewMatchPathValueComboDetector"
        new_match_path_value_combo_detector = NewMatchPathValueComboDetector(self.aminer_config, [self.first_seq_s1, self.first_seq_d1], [
            self.stream_printer_event_handler], 'Default', False, False, output_log_line=False)
        self.analysis_context.register_component(new_match_path_value_combo_detector, description)

        t = time.time()
        log_atom_sequence_me = LogAtom(self.match_element_sequence_me.get_match_string(), ParserMatch(self.match_element_sequence_me), t,
                                       new_match_path_value_combo_detector)

        self.assertTrue(new_match_path_value_combo_detector.receive_atom(log_atom_sequence_me))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_value_combo_detector.__class__.__name__,
            description, 1, self.string2))
        self.reset_output_stream()

        # repeating should produce the same result
        self.assertTrue(new_match_path_value_combo_detector.receive_atom(log_atom_sequence_me))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_value_combo_detector.__class__.__name__,
            description, 1, self.string2))
        self.reset_output_stream()

        new_match_path_value_combo_detector2 = NewMatchPathValueComboDetector(self.aminer_config, ['second/seq2/d1', 'second/seq2/s2'], [
            self.stream_printer_event_handler], 'Default', False, False, output_log_line=False)
        self.analysis_context.register_component(new_match_path_value_combo_detector2, description + "2")

        log_atom_sequence_me2 = LogAtom(self.match_element_sequence_me2.get_match_string(), ParserMatch(self.match_element_sequence_me2), t,
                                        new_match_path_value_combo_detector2)

        # other MatchElement
        self.assertTrue(new_match_path_value_combo_detector2.receive_atom(log_atom_sequence_me2))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_value_combo_detector.__class__.__name__,
            description + "2", 1, "  (25537, b' uid=2')\nb'25537 uid=2'"))

    def test2_log_atom_known(self):
        """This test case checks the functionality of the auto_include_flag. If the same MatchElement is processed a second time and the
        auto_include_flag was True, no event must be triggered."""
        description = "Test2NewMatchPathValueComboDetector"
        new_match_path_value_combo_detector = NewMatchPathValueComboDetector(self.aminer_config, [self.first_seq_s1, self.first_seq_d1], [
            self.stream_printer_event_handler], 'Default', False, True, output_log_line=False)
        self.analysis_context.register_component(new_match_path_value_combo_detector, description)

        t = time.time()
        log_atom_sequence_me = LogAtom(self.match_element_sequence_me.get_match_string(), ParserMatch(self.match_element_sequence_me), t,
                                       new_match_path_value_combo_detector)

        self.assertTrue(new_match_path_value_combo_detector.receive_atom(log_atom_sequence_me))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_value_combo_detector.__class__.__name__,
            description, 1, self.string2))
        self.reset_output_stream()

        # repeating should NOT produce the same result
        self.assertTrue(new_match_path_value_combo_detector.receive_atom(log_atom_sequence_me))
        self.assertEqual(self.output_stream.getvalue(), '')
        self.reset_output_stream()

        new_match_path_value_combo_detector2 = NewMatchPathValueComboDetector(self.aminer_config, ['second/seq2/d1', 'second/seq2/s2'], [
            self.stream_printer_event_handler], 'Default', False, False, output_log_line=False)
        self.analysis_context.register_component(new_match_path_value_combo_detector2, description + "2")

        log_atom_sequence_me2 = LogAtom(self.match_element_sequence_me2.get_match_string(), ParserMatch(self.match_element_sequence_me2), t,
                                        new_match_path_value_combo_detector2)

        # other MatchElement
        self.assertTrue(new_match_path_value_combo_detector2.receive_atom(log_atom_sequence_me2))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_value_combo_detector.__class__.__name__,
            description + "2", 1, "  (25537, b' uid=2')\nb'25537 uid=2'"))

    def test3_log_atom_known_from_persisted_data(self):
        """The persisting and reading of permitted log lines should be checked with this test."""
        description = "Test3NewMatchPathValueComboDetector"
        new_match_path_value_combo_detector = NewMatchPathValueComboDetector(self.aminer_config, [self.first_seq_s1, self.first_seq_d1], [
            self.stream_printer_event_handler], 'Default', False, True, output_log_line=False)
        self.analysis_context.register_component(new_match_path_value_combo_detector, description)

        t = time.time()
        log_atom_sequence_me = LogAtom(self.match_element_sequence_me.get_match_string(), ParserMatch(self.match_element_sequence_me), t,
                                       new_match_path_value_combo_detector)

        self.assertTrue(new_match_path_value_combo_detector.receive_atom(log_atom_sequence_me))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_value_combo_detector.__class__.__name__,
            description, 1, self.string2))
        new_match_path_value_combo_detector.do_persist()
        self.reset_output_stream()

        other_new_match_path_value_combo_detector = NewMatchPathValueComboDetector(self.aminer_config, [
            self.first_seq_s1, self.first_seq_d1], [self.stream_printer_event_handler], 'Default', False, True, output_log_line=False)
        self.analysis_context.register_component(other_new_match_path_value_combo_detector, description + "2")
        other_log_atom_fixed_dme = LogAtom(self.match_element_sequence_me.get_match_string(), ParserMatch(self.match_element_sequence_me),
                                           t, other_new_match_path_value_combo_detector)

        self.assertTrue(other_new_match_path_value_combo_detector.receive_atom(other_log_atom_fixed_dme))
        self.assertEqual(self.output_stream.getvalue(), '')

    def test4_allowlist_event_with_known_and_unknown_paths(self):
        """This test case checks in which cases an event is triggered and compares with expected results."""
        description = "Test4NewMatchPathValueComboDetector"
        new_match_path_value_combo_detector = NewMatchPathValueComboDetector(self.aminer_config, [self.first_seq_s1, self.first_seq_d1], [
            self.stream_printer_event_handler], 'Default', False, True, output_log_line=False)
        self.analysis_context.register_component(new_match_path_value_combo_detector, description)

        t = time.time()
        log_atom_sequence_me = LogAtom(self.match_element_sequence_me.get_match_string(), ParserMatch(self.match_element_sequence_me), t,
                                       new_match_path_value_combo_detector)
        new_match_path_value_combo_detector.receive_atom(log_atom_sequence_me)
        self.assertEqual(
            new_match_path_value_combo_detector.allowlist_event('Analysis.%s' % new_match_path_value_combo_detector.__class__.__name__, [
                log_atom_sequence_me, [self.match_element_sequence_me.get_path()]],
                [log_atom_sequence_me, self.match_element_sequence_me.get_path()], None), 'Allowlisted path(es) %s with %s in %s' % (
                ", ".join(new_match_path_value_combo_detector.target_path_list), self.match_element_sequence_me.get_path(),
                log_atom_sequence_me))

        log_atom_sequence_me2 = LogAtom(self.match_element_sequence_me2.get_match_string(), ParserMatch(self.match_element_sequence_me2), t,
                                        new_match_path_value_combo_detector)
        new_match_path_value_combo_detector.auto_include_flag = False
        self.assertEqual(
            new_match_path_value_combo_detector.allowlist_event('Analysis.%s' % new_match_path_value_combo_detector.__class__.__name__, [
                log_atom_sequence_me2, [self.match_element_sequence_me2.get_path()]], [
                log_atom_sequence_me2, self.match_element_sequence_me2.get_path()], None), 'Allowlisted path(es) %s with %s in %s' % (
                ", ".join(new_match_path_value_combo_detector.target_path_list), self.match_element_sequence_me2.path,
                log_atom_sequence_me2))


if __name__ == "__main__":
    unittest.main()
