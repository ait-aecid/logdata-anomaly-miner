import unittest
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.analysis.NewMatchPathValueDetector import NewMatchPathValueDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase
import time
from datetime import datetime


class NewMatchPathValueDetectorTest(TestBase):
    __expected_string = '%s New value(s) detected\n%s: "%s" (%d lines)\n  %s\n\n'
    
    datetime_format_string = '%Y-%m-%d %H:%M:%S'
    string = b'25537 uid=2'
    first_f1_s1 = 'first/f1/s1'
    string2 = "{'first/f1/s1': '25537 uid=2'}\nb'25537 uid=2'"
    
    fixed_dme = FixedDataModelElement('s1', string)
    decimalIntegerValueME = DecimalIntegerValueModelElement('d1', 
      DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
    
    match_context_first_match_me = MatchContext(string)
    first_match_me = FirstMatchModelElement('f1', [fixed_dme, decimalIntegerValueME])
    match_element_first_match_me = first_match_me.get_match_element('first', match_context_first_match_me)
    
    match_context_first_match_me2 = MatchContext(string)
    first_match_me2 = FirstMatchModelElement('f2', [decimalIntegerValueME, fixed_dme])
    match_element_first_match_me2 = first_match_me2.get_match_element('second', match_context_first_match_me2)
    
    '''
    This test case checks the correct processing of unknown log lines, which in reality means that an anomaly has been found. 
    The output is directed to an output stream and compared for accuracy. The autoIncludeFlag is False and the output must be repeatable on second run. 
    '''
    def test1_log_atom_not_known(self):
      description = "Test1NewMatchPathValueDetector"
      new_match_path_value_detector = NewMatchPathValueDetector(self.aminer_config, [self.first_f1_s1],
        [self.stream_printer_event_handler], 'Default', False, output_log_line=False)
      self.analysis_context.register_component(new_match_path_value_detector, description)

      t = time.time()
      log_atom_sequence_me = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_first_match_me),
        t, new_match_path_value_detector)
      new_match_path_value_detector.receive_atom(log_atom_sequence_me)
      self.assertEqual(self.output_stream.getvalue(), self.__expected_string %
        (datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        new_match_path_value_detector.__class__.__name__, description, 1, self.string2))
      self.reset_output_stream()
      
      #repeating should produce the same result
      new_match_path_value_detector.receive_atom(log_atom_sequence_me)
      self.assertEqual(self.output_stream.getvalue(), self.__expected_string %
        (datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        new_match_path_value_detector.__class__.__name__, description, 1, self.string2))
      self.reset_output_stream()
      
      new_match_path_value_detector2 = NewMatchPathValueDetector(self.aminer_config, ['second/f2/d1'],
        [self.stream_printer_event_handler], 'Default', False, output_log_line=False)
      self.analysis_context.register_component(new_match_path_value_detector2, description + "2")
      log_atom_sequence_me2 = LogAtom(b'25537', ParserMatch(self.match_element_first_match_me2), t, new_match_path_value_detector2)
      
      #other MatchElement
      new_match_path_value_detector2.receive_atom(log_atom_sequence_me2)
      self.assertEqual(self.output_stream.getvalue(), self.__expected_string %
        (datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        new_match_path_value_detector.__class__.__name__, description + "2", 1, "{'second/f2/d1': 25537}\nb'25537'"))

    '''
    This test case checks the functionality of the autoIncludeFlag. 
    If the same MatchElement is processed a second time and the autoIncludeFlag was True, no event must be triggered.
    '''
    def test2_log_atom_known(self):
      description = "Test2NewMatchPathValueDetector"
      new_match_path_value_detector = NewMatchPathValueDetector(self.aminer_config, [self.first_f1_s1],
        [self.stream_printer_event_handler], 'Default', True, output_log_line=False)
      self.analysis_context.register_component(new_match_path_value_detector, description)
      
      t = time.time()
      log_atom_sequence_me = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_first_match_me),
        t, new_match_path_value_detector)
      new_match_path_value_detector.receive_atom(log_atom_sequence_me)
      self.assertEqual(self.output_stream.getvalue(), self.__expected_string %
        (datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        new_match_path_value_detector.__class__.__name__, description, 1, self.string2))
      self.reset_output_stream()
      
      #repeating should NOT produce the same result
      new_match_path_value_detector.receive_atom(log_atom_sequence_me)
      self.assertEqual(self.output_stream.getvalue(), '')
      self.reset_output_stream()
      
      new_match_path_value_detector2 = NewMatchPathValueDetector(self.aminer_config, ['second/f2/d1'],
        [self.stream_printer_event_handler], 'Default', False, output_log_line=False)
      self.analysis_context.register_component(new_match_path_value_detector2, description + "2")
      log_atom_sequence_me2 = LogAtom(b'25537', ParserMatch(self.match_element_first_match_me2), t, new_match_path_value_detector2)
      
      #other MatchElement
      new_match_path_value_detector2.receive_atom(log_atom_sequence_me2)
      self.assertEqual(self.output_stream.getvalue(), self.__expected_string %
        (datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        new_match_path_value_detector.__class__.__name__, description + "2", 1, "{'second/f2/d1': 25537}\nb'25537'"))
    
    '''
    The persisting and reading of permitted log lines should be checked with this test.
    '''
    def test3_log_atom_known_from_persisted_data(self):
      description = "Test3NewMatchPathValueDetector"
      new_match_path_value_detector = NewMatchPathValueDetector(self.aminer_config, [self.first_f1_s1],
        [self.stream_printer_event_handler], 'Default', True, output_log_line=False)
      self.analysis_context.register_component(new_match_path_value_detector, description)
      
      t = time.time()
      log_atom_sequence_me = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_first_match_me), t, new_match_path_value_detector)
      new_match_path_value_detector.receive_atom(log_atom_sequence_me)
      self.assertEqual(self.output_stream.getvalue(), self.__expected_string %
        (datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        new_match_path_value_detector.__class__.__name__, description, 1, self.string2))
      new_match_path_value_detector.do_persist()
      self.reset_output_stream()
      
      other_new_match_path_value_detector = NewMatchPathValueDetector(self.aminer_config, [self.first_f1_s1],
        [self.stream_printer_event_handler], 'Default', True, output_log_line=False)
      self.analysis_context.register_component(new_match_path_value_detector, description + "2")
      other_log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_first_match_me), t, other_new_match_path_value_detector)
      
      other_new_match_path_value_detector.receive_atom(other_log_atom_fixed_dme)
      self.assertEqual(self.output_stream.getvalue(), '')

    
if __name__ == "__main__":
    unittest.main()
