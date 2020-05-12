import unittest
from aminer.analysis.AtomFilters import SubhandlerFilter, MatchPathFilter,\
  MatchValueFilter
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
import time
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from unit.TestBase import TestBase


class AtomFiltersTest(TestBase):    
    match_context_fixed_dme = MatchContext(b'25000')
    fixed_dme = FixedDataModelElement('s1', b'25000')
    match_element_fixed_dme = fixed_dme.get_match_element("fixed", match_context_fixed_dme)
    
    match_context_decimal_integer_value_me = MatchContext(b'25000')
    decimal_integer_value_me = DecimalIntegerValueModelElement('d1',
        DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
    match_element_decimal_integer_value_me = decimal_integer_value_me.get_match_element("integer",
        match_context_decimal_integer_value_me)
    
    '''
    This test case verifies, that exceptions are raised when using wrong parameters.
    '''
    def test1_no_list_or_no_atom_handler_list(self):
      self.assertRaises(Exception, SubhandlerFilter, NewMatchPathDetector(self.aminer_config, [], 'Default', True), False)
      self.assertRaises(Exception, SubhandlerFilter, FixedDataModelElement('fixed', b'gesuchter String'), False)
      
    '''
    In this test case no handler can handle the log atom.
    '''
    def test2receive_atom_unhandled(self):
      description = "Test2AtomFilters"
      self.new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False)
      self.analysis_context.register_component(self.new_match_path_detector, description)
      t = time.time()
      
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data,
        ParserMatch(self.match_element_fixed_dme), t, self.new_match_path_detector)
      
      self.subhandler_filter = SubhandlerFilter([], True)
      self.assertTrue(not self.subhandler_filter.receive_atom(self.log_atom_fixed_dme))
    
    '''
    In this test case more than one handler can handle the log atom.
    The impact of the stop_when_handled flag is tested.
    '''
    def test3receive_atom_handled_by_more_handlers(self):
      description = "Test3AtomFilters"
      other_description = "Test3OtherAtomFilters"
      self.new_match_path_detector = NewMatchPathDetector(self.aminer_config,
        [self.stream_printer_event_handler], 'Default', False)
      self.analysis_context.register_component(self.new_match_path_detector, description)
      t = time.time()
      
      self.other_new_match_path_detector = NewMatchPathDetector(self.aminer_config,
        [self.stream_printer_event_handler], 'Default', False)
      self.analysis_context.register_component(self.other_new_match_path_detector, other_description)
      
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data,
         ParserMatch(self.match_element_fixed_dme), t, self.new_match_path_detector)
      self.log_atom_decimal_integer_value_me = LogAtom(self.match_context_decimal_integer_value_me.match_data,
         ParserMatch(self.match_element_decimal_integer_value_me), t, self.other_new_match_path_detector)
      
      self.subhandler_filter = SubhandlerFilter([self.new_match_path_detector, self.other_new_match_path_detector], False)
      self.assertTrue(self.subhandler_filter.receive_atom(self.log_atom_fixed_dme))
      self.result = self.output_stream.getvalue()
      self.reset_output_stream()
      
      self.new_match_path_detector.receive_atom(self.log_atom_fixed_dme)
      self.resultFixedDME = self.output_stream.getvalue()
      self.reset_output_stream()
      
      self.other_new_match_path_detector.receive_atom(self.log_atom_fixed_dme)
      self.result_decimal_integer_value_me = self.output_stream.getvalue()
      
      self.assertEqual(self.result, self.resultFixedDME + self.result_decimal_integer_value_me)
    
    '''
    There is a path in the dictionary and the handler is not None.
    The default_parsed_atom_handler is None.
    '''
    def test4match_path_filter_receive_atom_path_in_dictionary(self):
      description = "Test4AtomFilters"
      self.new_match_path_detector = NewMatchPathDetector(self.aminer_config,
        [self.stream_printer_event_handler], 'Default', False)
      self.analysis_context.register_component(self.new_match_path_detector, description)
      t = time.time()
      
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data,
         ParserMatch(self.match_element_fixed_dme), t, self.new_match_path_detector)
      
      self.match_path_filter = MatchPathFilter([(self.match_element_fixed_dme.get_path(),
         self.new_match_path_detector)], None)
      self.assertTrue(self.match_path_filter.receive_atom(self.log_atom_fixed_dme))
    
    '''
    The searched path is not in the dictionary.
    The default_parsed_atom_handler is None.
    '''
    def test5match_path_filter_receive_atom_path_not_in_dictionary(self):
      description = "Test5AtomFilters"
      self.new_match_path_detector = NewMatchPathDetector(self.aminer_config,
        [self.stream_printer_event_handler], 'Default', False)
      self.analysis_context.register_component(self.new_match_path_detector, description)
      t = time.time()
      
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data,
        ParserMatch(self.match_element_fixed_dme), t, self.new_match_path_detector)
      
      self.match_path_filter = MatchPathFilter([(self.match_element_decimal_integer_value_me.get_path(),
        self.new_match_path_detector)], None)
      self.assertTrue(not self.match_path_filter.receive_atom(self.log_atom_fixed_dme))
    
    '''
    The searched path is not in the dictionary.
    The default_parsed_atom_handler is set.
    '''
    def test6match_path_filter_receive_atom_path_not_in_dictionary_default_set(self):
      description = "Test6AtomFilters"
      self.new_match_path_detector = NewMatchPathDetector(self.aminer_config,
        [self.stream_printer_event_handler], 'Default', False)
      self.analysis_context.register_component(self.new_match_path_detector, description)
      t = time.time()
      
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data,
        ParserMatch(self.match_element_fixed_dme), t, self.new_match_path_detector)
      
      self.match_path_filter = MatchPathFilter([(self.match_element_decimal_integer_value_me.get_path(),
        self.new_match_path_detector)], self.new_match_path_detector)
      self.assertTrue(self.match_path_filter.receive_atom(self.log_atom_fixed_dme))

    '''
    A target_value and a handler, which can handle the matchObject is found.
    '''
    def test7match_value_filter_receive_atom_target_value_and_handler_found(self):
      description = "Test7AtomFilters"
      self.new_match_path_detector = NewMatchPathDetector(self.aminer_config,
        [self.stream_printer_event_handler], 'Default', False)
      self.analysis_context.register_component(self.new_match_path_detector, description)
      t = time.time()
      
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data,
        ParserMatch(self.match_element_fixed_dme), t, self.new_match_path_detector)

      self.match_value_filter = MatchValueFilter(self.match_element_fixed_dme.get_path(),
        {self.fixed_dme.fixed_data:self.new_match_path_detector}, None)
      self.assertTrue(self.match_value_filter.receive_atom(self.log_atom_fixed_dme))
    
    '''
    A target_value was found, but no handler can handle it. DefaultParsedAtomHandler = None
    '''
    def test8match_value_filter_receive_atom_target_value_found_handler_not_found(self):
      description = "Test8AtomFilters"
      self.new_match_path_detector = NewMatchPathDetector(self.aminer_config,
        [self.stream_printer_event_handler], 'Default', False)
      self.analysis_context.register_component(self.new_match_path_detector, description)
      t = time.time()
      
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data,
        ParserMatch(self.match_element_fixed_dme), t, self.new_match_path_detector)

      self.match_value_filter = MatchValueFilter(self.match_element_fixed_dme.get_path(),
        {self.fixed_dme.fixed_data:None}, None)
      self.assertTrue(not self.match_value_filter.receive_atom(self.log_atom_fixed_dme))
    
    '''
    No target_value was found in the dictionary.
    '''
    def test9match_value_filter_receive_atom_target_value_not_found(self):
      description = "Test9AtomFilters"
      self.new_match_path_detector = NewMatchPathDetector(self.aminer_config,
        [self.stream_printer_event_handler], 'Default', False)
      self.analysis_context.register_component(self.new_match_path_detector, description)
      t = time.time()
      
      self.log_atom_fixed_dme = LogAtom(b'24999', ParserMatch(self.match_element_fixed_dme), t, self.new_match_path_detector)
      self.match_value_filter = MatchValueFilter(self.match_element_fixed_dme.get_path(),
        {self.fixed_dme.fixed_data:None}, None)
      self.assertTrue(not self.match_value_filter.receive_atom(self.log_atom_fixed_dme))


if __name__ == "__main__":
    unittest.main()
