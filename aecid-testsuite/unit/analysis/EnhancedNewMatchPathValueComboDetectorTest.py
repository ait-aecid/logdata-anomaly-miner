import unittest
from aminer.parsing import FixedDataModelElement, DecimalIntegerValueModelElement, MatchContext, ParserMatch, SequenceModelElement
from aminer.input.LogAtom import LogAtom
from aminer.analysis.EnhancedNewMatchPathValueComboDetector import EnhancedNewMatchPathValueComboDetector
from unit.TestBase import TestBase
import time
from datetime import datetime


class EnhancedNewMatchPathValueComboDetectorTest(TestBase):
    __expected_string = '%s New value combination(s) detected\n%s: "%s" (%d lines)\n%s\n\n'
    __expected_allowlisting_string = 'Allowlisted path(es) %s with %s in %s'
    fixed_dme = FixedDataModelElement('s1', b'25537 uid=')
    fixed_dme2 = FixedDataModelElement('s2', b' uid=2')

    decimal_integer_value_me = DecimalIntegerValueModelElement('d1', DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                                                               DecimalIntegerValueModelElement.PAD_TYPE_NONE)

    match_context_sequence_me = MatchContext(b'25537 uid=2')
    seq = SequenceModelElement('seq', [fixed_dme, decimal_integer_value_me])
    match_element_sequence_me = seq.get_match_element('first', match_context_sequence_me)

    match_context_sequence_me2 = MatchContext(b'25537 uid=2')
    seq2 = SequenceModelElement('seq2', [decimal_integer_value_me, fixed_dme2])
    match_element_sequence_me2 = seq2.get_match_element('second', match_context_sequence_me2)

    first_seq_s1 = 'first/seq/s1'
    first_seq_d1 = 'first/seq/d1'
    datetime_format_string = '%Y-%m-%d %H:%M:%S'
    exp_str = "  first/seq: b'25537 uid=2'\n  " + first_seq_s1 + ": b'25537 uid='\n  " + first_seq_d1 + \
              ": 2\n{(b'25537 uid=', 2): [%s, %s, 1]}"
    exp_str2 = "  {(b'25537 uid=', 2): [%s, %s, 1]}\nb'25537 uid=2'"

    def test1_log_atom_not_known(self):
        """This test case checks the correct processing of unknown log lines, which in reality means that an anomaly has been found. The
        output is directed to an output stream and compared for accuracy. The auto_include_flag is False and the output must be repeatable
        on second run."""
        description = "Test1EnhancedNewMatchPathValueComboDetector"
        enhanced_new_match_path_value_combo_detector = EnhancedNewMatchPathValueComboDetector(self.aminer_config, [
            self.first_seq_s1, self.first_seq_d1], [self.stream_printer_event_handler], 'Default', False, False, output_log_line=False)
        self.analysis_context.register_component(enhanced_new_match_path_value_combo_detector, description)

        t = round(time.time(), 3)
        log_atom_sequence_me = LogAtom(self.match_element_sequence_me.get_match_string(), ParserMatch(self.match_element_sequence_me), t,
                                       enhanced_new_match_path_value_combo_detector)

        self.assertTrue(enhanced_new_match_path_value_combo_detector.receive_atom(log_atom_sequence_me))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string),
            enhanced_new_match_path_value_combo_detector.__class__.__name__, description, 1, self.exp_str2 % (t, t)))
        self.reset_output_stream()

        log_atom_sequence_me = LogAtom(self.match_element_sequence_me.get_match_string(), ParserMatch(self.match_element_sequence_me),
                                       t + 2, enhanced_new_match_path_value_combo_detector)

        # repeating should produce the same result with new extraData.
        self.assertTrue(enhanced_new_match_path_value_combo_detector.receive_atom(log_atom_sequence_me))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t + 2).strftime(self.datetime_format_string),
            enhanced_new_match_path_value_combo_detector.__class__.__name__, description, 1,
            "  {(b'25537 uid=', 2): [%s, %s, 2]}\nb'25537 uid=2'" % (t, t + 2)))
        self.reset_output_stream()

        enhanced_new_match_path_value_combo_detector2 = EnhancedNewMatchPathValueComboDetector(self.aminer_config, [
            'second/seq2/d1', 'second/seq2/s2'], [self.stream_printer_event_handler], 'Default', False, False, output_log_line=False)

        self.analysis_context.register_component(enhanced_new_match_path_value_combo_detector2, description + "2")
        log_atom_sequence_me2 = LogAtom(self.match_element_sequence_me2.get_match_string(), ParserMatch(self.match_element_sequence_me2), t,
                                        enhanced_new_match_path_value_combo_detector2)

        # other MatchElement
        self.assertTrue(enhanced_new_match_path_value_combo_detector2.receive_atom(log_atom_sequence_me2))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string),
            enhanced_new_match_path_value_combo_detector.__class__.__name__, description + "2", 1,
            "  {(25537, b' uid=2'): [%s, %s, 1]}\nb'25537 uid=2'" % (t, t)))

    def test2_log_atom_known(self):
        """This test case checks the functionality of the auto_include_flag. If the same MatchElement is processed a second time and the
        auto_include_flag was True, no event must be triggered."""
        description = "Test2EnhancedNewMatchPathValueComboDetector"
        enhanced_new_match_path_value_combo_detector = EnhancedNewMatchPathValueComboDetector(self.aminer_config, [
            self.first_seq_s1, self.first_seq_d1], [self.stream_printer_event_handler], 'Default', False, True, output_log_line=False)
        self.analysis_context.register_component(enhanced_new_match_path_value_combo_detector, description)

        t = round(time.time(), 3)
        log_atom_sequence_me = LogAtom(self.match_element_sequence_me.get_match_string(), ParserMatch(self.match_element_sequence_me), t,
                                       enhanced_new_match_path_value_combo_detector)

        self.assertTrue(enhanced_new_match_path_value_combo_detector.receive_atom(log_atom_sequence_me))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string),
            enhanced_new_match_path_value_combo_detector.__class__.__name__, description, 1, self.exp_str2 % (t, t)))
        self.reset_output_stream()

        t = round(time.time(), 3)
        log_atom_sequence_me = LogAtom(self.match_element_sequence_me.get_match_string(), ParserMatch(self.match_element_sequence_me), t,
                                       enhanced_new_match_path_value_combo_detector)

        # repeating should NOT produce the same result, only persist the new extraData.
        self.assertTrue(enhanced_new_match_path_value_combo_detector.receive_atom(log_atom_sequence_me))
        self.assertEqual(self.output_stream.getvalue(), '')
        self.reset_output_stream()

        enhanced_new_match_path_value_combo_detector2 = EnhancedNewMatchPathValueComboDetector(self.aminer_config, [
            'second/seq2/d1', 'second/seq2/s2'], [self.stream_printer_event_handler], 'Default', False, False, output_log_line=False)

        self.analysis_context.register_component(enhanced_new_match_path_value_combo_detector2, description + "2")
        log_atom_sequence_me2 = LogAtom(self.match_element_sequence_me2.get_match_string(), ParserMatch(self.match_element_sequence_me2), t,
                                        enhanced_new_match_path_value_combo_detector2)

        # other MatchElement
        self.assertTrue(enhanced_new_match_path_value_combo_detector2.receive_atom(log_atom_sequence_me2))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string),
            enhanced_new_match_path_value_combo_detector.__class__.__name__, description + "2", 1,
            "  {(25537, b' uid=2'): [%s, %s, 1]}\nb'25537 uid=2'" % (t, t)))

    def test3_log_atom_known_from_persisted_data(self):
        """The persisting and reading of permitted log lines should be checked with this test."""
        description = "Test3EnhancedNewMatchPathValueComboDetector"
        enhanced_new_match_path_value_combo_detector = EnhancedNewMatchPathValueComboDetector(self.aminer_config, [
            self.first_seq_s1, self.first_seq_d1], [self.stream_printer_event_handler], 'Default', False, True, output_log_line=False)
        self.analysis_context.register_component(enhanced_new_match_path_value_combo_detector, description)

        t = round(time.time(), 3)
        log_atom_sequence_me = LogAtom(self.match_element_sequence_me.get_match_string(), ParserMatch(self.match_element_sequence_me), t,
                                       enhanced_new_match_path_value_combo_detector)

        self.assertTrue(enhanced_new_match_path_value_combo_detector.receive_atom(log_atom_sequence_me))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string),
            enhanced_new_match_path_value_combo_detector.__class__.__name__, description, 1, self.exp_str2 % (t, t)))
        enhanced_new_match_path_value_combo_detector.do_persist()
        self.reset_output_stream()

        other_enhanced_new_match_path_value_combo_detector = EnhancedNewMatchPathValueComboDetector(self.aminer_config, [
            self.first_seq_s1, self.first_seq_d1], [self.stream_printer_event_handler], 'Default', False, False, output_log_line=False)
        self.analysis_context.register_component(other_enhanced_new_match_path_value_combo_detector, description + "2")
        other_log_atom_sequence_me = LogAtom(self.match_element_sequence_me.get_match_string(), ParserMatch(self.match_element_sequence_me),
                                             t + 2, other_enhanced_new_match_path_value_combo_detector)

        self.assertTrue(other_enhanced_new_match_path_value_combo_detector.receive_atom(other_log_atom_sequence_me))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t + 2).strftime(self.datetime_format_string),
            enhanced_new_match_path_value_combo_detector.__class__.__name__, description + "2", 1,
            "  {(b'25537 uid=', 2): [%s, %s, 2]}\nb'25537 uid=2'" % (t, t + 2)))
        self.reset_output_stream()

        other_log_atom_sequence_me = LogAtom(self.match_element_sequence_me.get_match_string(), ParserMatch(self.match_element_sequence_me),
                                             t + 5, other_enhanced_new_match_path_value_combo_detector)

        self.assertTrue(other_enhanced_new_match_path_value_combo_detector.receive_atom(other_log_atom_sequence_me))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t + 5).strftime(self.datetime_format_string),
            enhanced_new_match_path_value_combo_detector.__class__.__name__, description + "2", 1,
            "  {(b'25537 uid=', 2): [%s, %s, 3]}\nb'25537 uid=2'" % (t, t + 5)))

    def test4_allowlist_event_with_known_and_unknown_paths(self):
        """This test case checks in which cases an event is triggered and compares with expected results."""
        description = "Test4EnhancedNewMatchPathValueComboDetector"
        enhanced_new_match_path_value_combo_detector = EnhancedNewMatchPathValueComboDetector(self.aminer_config, [
            self.first_seq_s1, self.first_seq_d1], [self.stream_printer_event_handler], 'Default', False, True, output_log_line=False)
        self.analysis_context.register_component(enhanced_new_match_path_value_combo_detector, description)

        t = time.time()
        log_atom_sequence_me = LogAtom(self.match_element_sequence_me.get_match_string(), ParserMatch(self.match_element_sequence_me), t,
                                       enhanced_new_match_path_value_combo_detector)
        self.assertEqual(enhanced_new_match_path_value_combo_detector.allowlist_event(
            'Analysis.%s' % enhanced_new_match_path_value_combo_detector.__class__.__name__,
            [log_atom_sequence_me, [self.match_element_sequence_me.get_path()]],
            [log_atom_sequence_me, self.match_element_sequence_me.get_path()], None), self.__expected_allowlisting_string % (
            ', '.join(enhanced_new_match_path_value_combo_detector.target_path_list), self.match_element_sequence_me.get_path(),
            log_atom_sequence_me))

        log_atom_sequence_me2 = LogAtom(self.match_element_sequence_me2.get_match_string(), ParserMatch(self.match_element_sequence_me2), t,
                                        enhanced_new_match_path_value_combo_detector)

        enhanced_new_match_path_value_combo_detector.auto_include_flag = False
        self.assertEqual(enhanced_new_match_path_value_combo_detector.allowlist_event(
            'Analysis.%s' % enhanced_new_match_path_value_combo_detector.__class__.__name__,
            [log_atom_sequence_me2, [self.match_element_sequence_me2.get_path()]],
            [log_atom_sequence_me2, self.match_element_sequence_me2.get_path()], None), self.__expected_allowlisting_string % (
            ', '.join(enhanced_new_match_path_value_combo_detector.target_path_list), self.match_element_sequence_me2.path,
            log_atom_sequence_me2))

    def test5save_metadata(self):
        """This test case checks the correctness of the metadata informations"""
        enhanced_new_match_path_value_combo_detector = EnhancedNewMatchPathValueComboDetector(self.aminer_config, ['first/f1/s1'], [
            self.stream_printer_event_handler], 'Default', False, True, None, output_log_line=False)
        t = 1
        log_atom_sequence_me = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_sequence_me), t,
                                       enhanced_new_match_path_value_combo_detector)

        enhanced_new_match_path_value_combo_detector.receive_atom(log_atom_sequence_me)
        self.assertEqual(enhanced_new_match_path_value_combo_detector.known_values_dict.get((self.fixed_dme.fixed_data, (t, t, 1))), None)


if __name__ == "__main__":
    unittest.main()
