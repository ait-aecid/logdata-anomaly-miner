import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from time import time
from aminer.analysis.TimestampsUnsortedDetector import TimestampsUnsortedDetector
from unit.TestBase import TestBase
from datetime import datetime


class TimestampsUnsortedDetectorTest(TestBase):
    __expected_string = '%s Timestamp %s below %s\n%s: "%s" (%d lines)\n  %s\n\n'
    
    pid = b' pid='
    datetime_format_string = '%Y-%m-%d %H:%M:%S'
    
    '''
    This test case checks if an event is created, when the timestamp is lower than the last one.
    '''
    def test1timestamp_lower_than_last_timestamp(self):
      description = "Test1TimestampsUnsortedDetector"
      self.match_context_fixed_dme = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element_fixed_dme = self.fixed_dme.get_match_element("match", self.match_context_fixed_dme)
      self.new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler],
        'Default', False)
      self.analysis_context.register_component(self.new_match_path_detector, description)
      
      self.t = time()
      self.log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), self.t, self.new_match_path_detector)
      self.timestamp_unsorted_detector = TimestampsUnsortedDetector(self.aminer_config, [self.stream_printer_event_handler], False, output_log_line=False)
      self.analysis_context.register_component(self.timestamp_unsorted_detector, description + "2")
      self.assertTrue(self.timestamp_unsorted_detector.receive_atom(self.log_atom))
      self.assertEqual(self.output_stream.getvalue(), '')
      
      self.log_atom.set_timestamp(self.t - 10000)
      self.assertTrue(self.timestamp_unsorted_detector.receive_atom(self.log_atom))
      self.assertEqual(self.output_stream.getvalue(), self.__expected_string %
        (datetime.fromtimestamp(self.t-10000).strftime(self.datetime_format_string),
        datetime.fromtimestamp(self.t-10000).strftime(self.datetime_format_string),
        datetime.fromtimestamp(self.t).strftime(self.datetime_format_string),
        self.timestamp_unsorted_detector.__class__.__name__, description + "2", 1, "b' pid='"))
    
    '''
    This test case checks if the program exits, when the timestamp is lower than the last one
    and the exitOnError flag is set.
    '''
    def test2timestamp_lower_than_last_timestamp_exit_on_error(self):
      description = "Test2TimestampsUnsortedDetector"
      self.match_context_fixed_dme = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element_fixed_dme = self.fixed_dme.get_match_element("match", self.match_context_fixed_dme)
      self.new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler],
        'Default', False)
      self.analysis_context.register_component(self.new_match_path_detector, description)
      
      self.t = time()
      self.log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), self.t, self.new_match_path_detector)
      self.timestamp_unsorted_detector = TimestampsUnsortedDetector(self.aminer_config, [self.stream_printer_event_handler], True, output_log_line=False)
      self.analysis_context.register_component(self.timestamp_unsorted_detector, description + "2")
      self.assertTrue(self.timestamp_unsorted_detector.receive_atom(self.log_atom))
      self.assertEqual(self.output_stream.getvalue(), '')
      
      self.log_atom.set_timestamp(self.t - 10000)
      with self.assertRaises(SystemExit) as cm:self.timestamp_unsorted_detector.receive_atom(self.log_atom)
      self.assertEqual(cm.exception.code, 1)
      self.assertEqual(self.output_stream.getvalue(), self.__expected_string %
        (datetime.fromtimestamp(self.t-10000).strftime(self.datetime_format_string),
        datetime.fromtimestamp(self.t-10000).strftime(self.datetime_format_string),
        datetime.fromtimestamp(self.t).strftime(self.datetime_format_string),
        self.timestamp_unsorted_detector.__class__.__name__, description + "2", 1, "b' pid='"))
    
    '''
    This test case checks if nothing happens, when the timestamp is, as expected, higher than the last one.
    '''
    def test3timestamp_higher_than_last_timestamp(self):
      description = "Test3TimestampsUnsortedDetector"
      self.match_context_fixed_dme = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element_fixed_dme = self.fixed_dme.get_match_element("match", self.match_context_fixed_dme)
      self.new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler],
        'Default', False)
      self.analysis_context.register_component(self.new_match_path_detector, description)
      
      self.t = time()
      self.log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), self.t, self.new_match_path_detector)
      self.timestamp_unsorted_detector = TimestampsUnsortedDetector(self.aminer_config, [self.stream_printer_event_handler], False, output_log_line=False)
      self.analysis_context.register_component(self.timestamp_unsorted_detector, description + "2")
      self.assertTrue(self.timestamp_unsorted_detector.receive_atom(self.log_atom))
      self.assertEqual(self.output_stream.getvalue(), '')
      
      self.log_atom.set_timestamp(self.t)
      self.assertTrue(self.timestamp_unsorted_detector.receive_atom(self.log_atom))
      self.assertEqual(self.output_stream.getvalue(), '')
      
      self.log_atom.set_timestamp(self.t + 10000)
      self.assertTrue(self.timestamp_unsorted_detector.receive_atom(self.log_atom))
      self.assertEqual(self.output_stream.getvalue(), '')


if __name__ == "__main__":
    unittest.main()
