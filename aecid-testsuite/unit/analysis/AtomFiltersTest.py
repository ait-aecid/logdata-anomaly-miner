import unittest
from aminer.analysis.AtomFilters import SubhandlerFilter, MatchPathFilter, MatchValueFilter
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
import time
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from unit.TestBase import TestBase


class AtomFiltersTest(TestBase):
    """Unittests for the AtomFilters."""

    match_context_fixed_dme = MatchContext(b'25000')
    fixed_dme = FixedDataModelElement('s1', b'25000')
    match_element_fixed_dme = fixed_dme.get_match_element("fixed", match_context_fixed_dme)

    match_context_decimal_integer_value_me = MatchContext(b'25000')
    decimal_integer_value_me = DecimalIntegerValueModelElement('d1', DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                                                               DecimalIntegerValueModelElement.PAD_TYPE_NONE)
    match_element_decimal_integer_value_me = decimal_integer_value_me.get_match_element("integer", match_context_decimal_integer_value_me)

    def test1_no_list_or_no_atom_handler_list(self):
        """This test case verifies, that exceptions are raised when using wrong parameters."""
        self.assertRaises(Exception, SubhandlerFilter, NewMatchPathDetector(self.aminer_config, [], 'Default', True), False)
        self.assertRaises(Exception, SubhandlerFilter, FixedDataModelElement('fixed', b'gesuchter String'), False)

    def test2receive_atom_unhandled(self):
        """In this test case no handler can handle the log atom."""
        description = "Test2AtomFilters"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False)
        self.analysis_context.register_component(new_match_path_detector, description)
        t = time.time()

        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)

        subhandler_filter = SubhandlerFilter([], True)
        self.assertTrue(not subhandler_filter.receive_atom(log_atom_fixed_dme))

    def test3receive_atom_handled_by_more_handlers(self):
        """In this test case more than one handler can handle the log atom. The impact of the stop_when_handled flag is tested."""
        description = "Test3AtomFilters"
        other_description = "Test3OtherAtomFilters"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False)
        self.analysis_context.register_component(new_match_path_detector, description)
        t = time.time()

        other_new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False)
        self.analysis_context.register_component(other_new_match_path_detector, other_description)

        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)

        subhandler_filter = SubhandlerFilter([new_match_path_detector, other_new_match_path_detector], False)
        self.assertTrue(subhandler_filter.receive_atom(log_atom_fixed_dme))
        result = self.output_stream.getvalue()
        self.reset_output_stream()

        new_match_path_detector.receive_atom(log_atom_fixed_dme)
        resultFixedDME = self.output_stream.getvalue()
        self.reset_output_stream()

        other_new_match_path_detector.receive_atom(log_atom_fixed_dme)
        result_decimal_integer_value_me = self.output_stream.getvalue()

        self.assertEqual(result, resultFixedDME + result_decimal_integer_value_me)

    def test4match_path_filter_receive_atom_path_in_dictionary(self):
        """There is a path in the dictionary and the handler is not None. The default_parsed_atom_handler is None."""
        description = "Test4AtomFilters"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False)
        self.analysis_context.register_component(new_match_path_detector, description)
        t = time.time()

        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)

        match_path_filter = MatchPathFilter([(self.match_element_fixed_dme.get_path(), new_match_path_detector)], None)
        self.assertTrue(match_path_filter.receive_atom(log_atom_fixed_dme))

    def test5match_path_filter_receive_atom_path_not_in_dictionary(self):
        """The searched path is not in the dictionary. The default_parsed_atom_handler is None."""
        description = "Test5AtomFilters"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False)
        self.analysis_context.register_component(new_match_path_detector, description)
        t = time.time()

        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)

        match_path_filter = MatchPathFilter([(self.match_element_decimal_integer_value_me.get_path(), new_match_path_detector)], None)
        self.assertTrue(not match_path_filter.receive_atom(log_atom_fixed_dme))

    def test6match_path_filter_receive_atom_path_not_in_dictionary_default_set(self):
        """The searched path is not in the dictionary. The default_parsed_atom_handler is set."""
        description = "Test6AtomFilters"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False)
        self.analysis_context.register_component(new_match_path_detector, description)
        t = time.time()

        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)

        match_path_filter = MatchPathFilter([(self.match_element_decimal_integer_value_me.get_path(), new_match_path_detector)],
                                            new_match_path_detector)
        self.assertTrue(match_path_filter.receive_atom(log_atom_fixed_dme))

    def test7match_value_filter_receive_atom_target_value_and_handler_found(self):
        """A target_value and a handler, which can handle the matchObject is found."""
        description = "Test7AtomFilters"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False)
        self.analysis_context.register_component(new_match_path_detector, description)
        t = time.time()

        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)

        match_value_filter = MatchValueFilter(self.match_element_fixed_dme.get_path(), {self.fixed_dme.fixed_data: new_match_path_detector},
                                              None)
        self.assertTrue(match_value_filter.receive_atom(log_atom_fixed_dme))

    def test8match_value_filter_receive_atom_target_value_found_handler_not_found(self):
        """A target_value was found, but no handler can handle it. DefaultParsedAtomHandler = None."""
        description = "Test8AtomFilters"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False)
        self.analysis_context.register_component(new_match_path_detector, description)
        t = time.time()

        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)

        match_value_filter = MatchValueFilter(self.match_element_fixed_dme.get_path(), {self.fixed_dme.fixed_data: None}, None)
        self.assertTrue(not match_value_filter.receive_atom(log_atom_fixed_dme))

    def test9match_value_filter_receive_atom_target_value_not_found(self):
        """No target_value was found in the dictionary."""
        description = "Test9AtomFilters"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False)
        self.analysis_context.register_component(new_match_path_detector, description)
        t = time.time()

        log_atom_fixed_dme = LogAtom(b'24999', ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)
        match_value_filter = MatchValueFilter(self.match_element_fixed_dme.get_path(), {self.fixed_dme.fixed_data: None}, None)
        self.assertTrue(not match_value_filter.receive_atom(log_atom_fixed_dme))


if __name__ == "__main__":
    unittest.main()
