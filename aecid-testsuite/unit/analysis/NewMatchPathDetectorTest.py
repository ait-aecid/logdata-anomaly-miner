import unittest
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from aminer.analysis.NewMatchPathValueComboDetector import NewMatchPathValueComboDetector
from aminer.input.LogAtom import LogAtom
import time
from datetime import datetime
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase


class NewMatchPathDetectorTest(TestBase):
    """Unittests for the NewMatchPathDetector."""

    __expected_string = '%s New path(es) detected\n%s: "%s" (%d lines)\n  %s\n%s\n\n'
    match_path_s1 = "['/s1']"
    match_path_d1 = "['/d1']"

    datetime_format_string = '%Y-%m-%d %H:%M:%S'
    analysis = 'Analysis.%s'
    pid = " pid="
    uid = " uid=2"

    match_context_fixed_dme = MatchContext(b' pid=')
    fixed_dme = FixedDataModelElement('s1', b' pid=')
    match_element_fixed_dme = fixed_dme.get_match_element("", match_context_fixed_dme)

    match_context_decimal_integer_value_me = MatchContext(b'25537 uid=2')
    decimal_integer_value_me = DecimalIntegerValueModelElement('d1', DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                                                               DecimalIntegerValueModelElement.PAD_TYPE_NONE)
    match_element_decimal_integer_value_me = decimal_integer_value_me.get_match_element("", match_context_decimal_integer_value_me)

    def test1_log_atom_not_known(self):
        """
        This test case checks the correct processing of unknown log lines, which in reality means that an anomaly has been found.
        The output is directed to an output stream and compared for accuracy. The auto_include_flag is False and the output must be
        repeatable on second run.
        """
        description = "Test1NewMatchPathDetector"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False,
                                                       output_log_line=False)
        self.analysis_context.register_component(new_match_path_detector, description)
        t = round(time.time(), 3)
        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)
        log_atom_decimal_integer_value_me = LogAtom(self.match_context_decimal_integer_value_me.match_data,
                                                    ParserMatch(self.match_element_decimal_integer_value_me), t, new_match_path_detector)

        self.assertTrue(new_match_path_detector.receive_atom(log_atom_fixed_dme))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_detector.__class__.__name__, description, 1,
            self.match_path_s1, self.pid))
        self.reset_output_stream()

        # repeating should produce the same result
        self.assertTrue(new_match_path_detector.receive_atom(log_atom_fixed_dme))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_detector.__class__.__name__, description, 1,
            self.match_path_s1, self.pid))
        self.reset_output_stream()

        # other MatchElement
        self.assertTrue(new_match_path_detector.receive_atom(log_atom_decimal_integer_value_me))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_detector.__class__.__name__, description, 1,
            self.match_path_d1, self.uid))

    def test2_log_atom_known(self):
        """
        This test case checks the functionality of the auto_include_flag.
        If the same MatchElement is processed a second time and the auto_include_flag was True, no event must be triggered.
        """
        description = "Test2NewMatchPathDetector"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', True,
                                                       output_log_line=False)
        self.analysis_context.register_component(new_match_path_detector, description)
        t = round(time.time(), 3)

        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)
        log_atom_decimal_integer_value_me = LogAtom(self.match_context_decimal_integer_value_me.match_data,
                                                    ParserMatch(self.match_element_decimal_integer_value_me), t, new_match_path_detector)

        self.assertTrue(new_match_path_detector.receive_atom(log_atom_fixed_dme))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_detector.__class__.__name__, description, 1,
            self.match_path_s1, self.pid))
        self.reset_output_stream()

        # repeating should NOT produce the same result
        self.assertTrue(new_match_path_detector.receive_atom(log_atom_fixed_dme))
        self.assertEqual(self.output_stream.getvalue(), '')
        self.reset_output_stream()

        # other MatchElement
        self.assertTrue(new_match_path_detector.receive_atom(log_atom_decimal_integer_value_me))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_detector.__class__.__name__, description, 1,
            self.match_path_d1, self.uid))

    def test3_log_atom_known_from_persisted_data(self):
        """The persisting and reading of permitted log lines should be checked with this test."""
        description = "Test3NewMatchPathDetector"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', True,
                                                       output_log_line=False)
        self.analysis_context.register_component(new_match_path_detector, description)
        t = round(time.time(), 3)
        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)

        self.assertTrue(new_match_path_detector.receive_atom(log_atom_fixed_dme))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_detector.__class__.__name__, description, 1,
            self.match_path_s1, self.pid))
        new_match_path_detector.do_persist()
        self.reset_output_stream()

        otherNewMatchPathDetector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False,
                                                         output_log_line=False)
        otherLogAtomFixedDME = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, otherNewMatchPathDetector)

        self.assertTrue(otherNewMatchPathDetector.receive_atom(otherLogAtomFixedDME))
        self.assertEqual(self.output_stream.getvalue(), '')

    def test4_get_time_trigger_class(self):
        """
        The known paths are to be periodically stored after a certain time. This requires a synchronization class.
        The return of the correct class is to be checked in this test case.
        """
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', True,
                                                       output_log_line=False)
        self.assertEqual(new_match_path_detector.get_time_trigger_class(), 1)

    # skipcq: PYL-W0105
    """The following test cases should check if the doTimer() method is working properly.This includes the updating of nextPersistTime.
    As it is not updated directly in the method this test cases are not correct. Due to that they are commented."""

    def test8_allowlist_event_type_exception(self):
        """This test case checks whether an exception is thrown when entering an event of another class."""
        description = "Test8NewMatchPathDetector"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', True,
                                                       output_log_line=False)
        self.analysis_context.register_component(new_match_path_detector, description)
        t = round(time.time(), 3)
        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)
        new_match_path_detector.receive_atom(log_atom_fixed_dme)
        new_match_path_value_combo_detector = NewMatchPathValueComboDetector(self.aminer_config, [], [self.stream_printer_event_handler],
                                                                             'Default', True, True)
        self.assertRaises(
            Exception, new_match_path_detector.allowlist_event, self.analysis % new_match_path_value_combo_detector.__class__.__name__,
            self.output_stream.getvalue(), None)

    def test9_allowlist_event_allowlisting_data_exception(self):
        """The NewMatchPathDetector can not handle allowlisting data and therefore an exception is expected."""
        description = "Test9NewMatchPathDetector"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', True,
                                                       output_log_line=False)
        self.analysis_context.register_component(new_match_path_detector, description)
        t = round(time.time(), 3)
        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)
        new_match_path_detector.receive_atom(log_atom_fixed_dme)
        self.assertRaises(Exception, new_match_path_detector.allowlist_event, self.analysis % new_match_path_detector.__class__.__name__,
                          self.output_stream.getvalue(), ['random', 'Data'])

    def test10_allowlist_event_with_known_and_unknown_paths(self):
        """This test case checks in which cases an event is triggered and compares with expected results."""
        description = "Test10NewMatchPathDetector"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', True,
                                                       output_log_line=False)
        self.analysis_context.register_component(new_match_path_detector, description)
        t = round(time.time(), 3)
        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)
        new_match_path_detector.receive_atom(log_atom_fixed_dme)
        self.assertEqual(new_match_path_detector.allowlist_event(
            self.analysis % new_match_path_detector.__class__.__name__, self.match_element_fixed_dme.get_path(), None),
            'Allowlisted path(es) %s in %s.' % (
                self.match_element_fixed_dme.get_path(), self.analysis % new_match_path_detector.__class__.__name__))

        new_match_path_detector.auto_include_flag = False
        self.assertEqual(new_match_path_detector.allowlist_event(
            self.analysis % new_match_path_detector.__class__.__name__, self.match_element_decimal_integer_value_me.get_path(), None),
            'Allowlisted path(es) %s in %s.' % (
                self.match_element_decimal_integer_value_me.path, self.analysis % new_match_path_detector.__class__.__name__))

if __name__ == "__main__":
    unittest.main()
