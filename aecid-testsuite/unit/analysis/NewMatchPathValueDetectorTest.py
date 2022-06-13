import unittest
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.analysis.NewMatchPathValueDetector import NewMatchPathValueDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase
from time import time
from datetime import datetime


class NewMatchPathValueDetectorTest(TestBase):
    """Unittests for the NewMatchPathValueDetector."""

    __expected_string = '%s New value(s) detected\n%s: "%s" (%d lines)\n  %s\n\n'
    analysis = 'Analysis.%s'
    datetime_format_string = '%Y-%m-%d %H:%M:%S'
    string = b'25537 uid=2'
    first_f1_s1 = 'first/f1/s1'
    string2 = "{'first/f1/s1': '25537 uid=2'}"

    fixed_dme = FixedDataModelElement('s1', string)
    decimal_integer_value_me = DecimalIntegerValueModelElement('d1', DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                                                               DecimalIntegerValueModelElement.PAD_TYPE_NONE)

    match_context_first_match_me = MatchContext(string)
    first_match_me = FirstMatchModelElement('f1', [fixed_dme, decimal_integer_value_me])
    match_element_first_match_me = first_match_me.get_match_element('first', match_context_first_match_me)

    match_context_first_match_me2 = MatchContext(string)
    first_match_me2 = FirstMatchModelElement('f2', [decimal_integer_value_me, fixed_dme])
    match_element_first_match_me2 = first_match_me2.get_match_element('second', match_context_first_match_me2)

    def test1_log_atom_not_known(self):
        """
        This test case checks the correct processing of unknown log lines, which in reality means that an anomaly has been found.
        The output is directed to an output stream and compared for accuracy. The auto_include_flag is False and the output must be
        repeatable on second run.
        """
        description = "Test1NewMatchPathValueDetector"
        new_match_path_value_detector = NewMatchPathValueDetector(self.aminer_config, [self.first_f1_s1], [
            self.stream_printer_event_handler], 'Default', False, output_log_line=False)
        self.analysis_context.register_component(new_match_path_value_detector, description)

        t = time()
        log_atom_sequence_me = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_first_match_me), t,
                                       new_match_path_value_detector)
        new_match_path_value_detector.receive_atom(log_atom_sequence_me)
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_value_detector.__class__.__name__, description,
            1, self.string2))
        self.reset_output_stream()

        # repeating should produce the same result
        new_match_path_value_detector.receive_atom(log_atom_sequence_me)
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_value_detector.__class__.__name__, description,
            1, self.string2))
        self.reset_output_stream()

        new_match_path_value_detector2 = NewMatchPathValueDetector(self.aminer_config, ['second/f2/d1'], [
            self.stream_printer_event_handler], 'Default', False, output_log_line=False)
        self.analysis_context.register_component(new_match_path_value_detector2, description + "2")
        log_atom_sequence_me2 = LogAtom(b'25537', ParserMatch(self.match_element_first_match_me2), t, new_match_path_value_detector2)

        # other MatchElement
        new_match_path_value_detector2.receive_atom(log_atom_sequence_me2)
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_value_detector.__class__.__name__,
            description + "2", 1, "{'second/f2/d1': 25537}"))

    def test2_log_atom_known(self):
        """
        This test case checks the functionality of the auto_include_flag.
        If the same MatchElement is processed a second time and the auto_include_flag was True, no event must be triggered.
        """
        description = "Test2NewMatchPathValueDetector"
        new_match_path_value_detector = NewMatchPathValueDetector(self.aminer_config, [self.first_f1_s1], [
            self.stream_printer_event_handler], 'Default', True, output_log_line=False)
        self.analysis_context.register_component(new_match_path_value_detector, description)

        t = time()
        log_atom_sequence_me = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_first_match_me), t,
                                       new_match_path_value_detector)
        new_match_path_value_detector.receive_atom(log_atom_sequence_me)
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_value_detector.__class__.__name__, description,
            1, self.string2))
        self.reset_output_stream()

        # repeating should NOT produce the same result
        new_match_path_value_detector.receive_atom(log_atom_sequence_me)
        self.assertEqual(self.output_stream.getvalue(), '')
        self.reset_output_stream()

        new_match_path_value_detector2 = NewMatchPathValueDetector(self.aminer_config, ['second/f2/d1'], [
            self.stream_printer_event_handler], 'Default', False, output_log_line=False)
        self.analysis_context.register_component(new_match_path_value_detector2, description + "2")
        log_atom_sequence_me2 = LogAtom(b'25537', ParserMatch(self.match_element_first_match_me2), t, new_match_path_value_detector2)

        # other MatchElement
        new_match_path_value_detector2.receive_atom(log_atom_sequence_me2)
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_value_detector.__class__.__name__,
            description + "2", 1, "{'second/f2/d1': 25537}"))

    def test3log_atom_known_from_persisted_data(self):
        """The persisting and reading of permitted log lines should be checked with this test."""
        description = "Test3NewMatchPathValueDetector"
        new_match_path_value_detector = NewMatchPathValueDetector(self.aminer_config, [self.first_f1_s1], [
            self.stream_printer_event_handler], 'Default', True, output_log_line=False)
        self.analysis_context.register_component(new_match_path_value_detector, description)

        t = time()
        log_atom_sequence_me = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_first_match_me), t,
                                       new_match_path_value_detector)
        new_match_path_value_detector.receive_atom(log_atom_sequence_me)
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_value_detector.__class__.__name__, description,
            1, self.string2))
        new_match_path_value_detector.do_persist()
        self.reset_output_stream()

        other_new_match_path_value_detector = NewMatchPathValueDetector(self.aminer_config, [self.first_f1_s1], [
            self.stream_printer_event_handler], 'Default', True, output_log_line=False)
        self.analysis_context.register_component(new_match_path_value_detector, description + "2")
        other_log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_first_match_me), t,
                                           other_new_match_path_value_detector)

        other_new_match_path_value_detector.receive_atom(other_log_atom_fixed_dme)
        self.assertEqual(self.output_stream.getvalue(), '')

    def test4allowlist_event(self):
        """Test the allowlist_event method."""
        description = "Test4NewMatchPathValueDetector"
        new_match_path_value_detector = NewMatchPathValueDetector(self.aminer_config, [self.first_f1_s1], [
            self.stream_printer_event_handler], 'Default', True, output_log_line=False)
        self.analysis_context.register_component(new_match_path_value_detector, description)
        self.assertEqual(set(), new_match_path_value_detector.known_values_set)

        # an unknown value should be allowlisted
        new_match_path_value_detector.allowlist_event(
            self.analysis % new_match_path_value_detector.__class__.__name__, self.fixed_dme.fixed_data.decode(), None)
        self.assertEqual({self.fixed_dme.fixed_data.decode()}, new_match_path_value_detector.known_values_set)

        # an known value should be allowlisted
        new_match_path_value_detector.allowlist_event(self.analysis % new_match_path_value_detector.__class__.__name__,
                                                      self.fixed_dme.fixed_data.decode(), None)
        self.assertEqual({self.fixed_dme.fixed_data.decode()}, new_match_path_value_detector.known_values_set)


if __name__ == "__main__":
    unittest.main()
