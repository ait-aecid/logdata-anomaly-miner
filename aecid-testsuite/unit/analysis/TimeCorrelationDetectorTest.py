import unittest
from unit.TestBase import TestBase
from aminer.parsing import FixedDataModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import MatchContext
from aminer.analysis.TimeCorrelationDetector import TimeCorrelationDetector
import time
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from datetime import datetime

class TimeCorrelationDetectorTest(TestBase):
  __expected_string = '%s Correlation report\nTimeCorrelationDetector: "%s" (%d lines)\n  '
  
  string = b'25537 uid=2'
  datetime_format_string = '%Y-%m-%d %H:%M:%S'
  
  fixed_dme = FixedDataModelElement('s1', string)
  decimal_integer_value_me = DecimalIntegerValueModelElement('d1',
    DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
  
  match_context_first_match_me = MatchContext(string)
  first_match_me = FirstMatchModelElement('f1', [fixed_dme, decimal_integer_value_me])
  match_element_first_match_me = first_match_me.get_match_element('first', match_context_first_match_me)
    
  match_context_first_match_me2 = MatchContext(string)
  first_match_me2 = FirstMatchModelElement('f2', [decimal_integer_value_me, fixed_dme])
  match_element_first_match_me2 = first_match_me2.get_match_element('second', match_context_first_match_me2)

  '''
  This test case unit the creation of a report. As the rules are chosen randomly this test can
  not be very specific in checking the actual values of the report.
  '''
  def test1_normal_report(self):
    description = "Test1TimeCorrelationDetector"
    time_correlation_detector = TimeCorrelationDetector(self.aminer_config, 2, 1, 0,
      [self.stream_printer_event_handler], record_count_before_event=10)
    self.analysis_context.register_component(time_correlation_detector, component_name=description)

    t = time.time()
    for i in range(0, 10):
      self.logAtomSequenceME = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_first_match_me), t, time_correlation_detector)
      time_correlation_detector.receive_atom(self.logAtomSequenceME)
    self.assertTrue(self.output_stream.getvalue().startswith(self.__expected_string % (datetime.fromtimestamp(t).strftime(self.datetime_format_string),
      description, 10)))
    self.reset_output_stream()
     
    for i in range(0, 10):
      self.logAtomSequenceME = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_first_match_me), t + i, time_correlation_detector)
      time_correlation_detector.receive_atom(self.logAtomSequenceME)
    self.assertTrue(self.output_stream.getvalue().startswith(self.__expected_string % (datetime.fromtimestamp(t + 9).strftime(self.datetime_format_string),
      description, 20)))
    self.reset_output_stream()
    
    for i in range(10, 15):
      self.logAtomSequenceME = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_first_match_me), t + i, time_correlation_detector)
      time_correlation_detector.receive_atom(self.logAtomSequenceME)
      self.logAtomSequenceME2 = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_first_match_me2), t + i, time_correlation_detector)
      time_correlation_detector.receive_atom(self.logAtomSequenceME2)
    self.assertTrue(self.output_stream.getvalue().startswith(self.__expected_string % (datetime.fromtimestamp(t + 14).strftime(self.datetime_format_string),
      description, 30)))


if __name__ == "__main__":
    unittest.main()