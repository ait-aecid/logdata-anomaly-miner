import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from aminer.analysis.TimestampCorrectionFilters import SimpleMonotonicTimestampAdjust
from time import time
from unit.TestBase import TestBase
from datetime import datetime


class TimestampCorrectionFiltersTest(TestBase):
    __expected_string = '%s New path(es) detected\n%s: "%s" (%d lines)\n  %s\nb\' pid=\'\n\n'
    match_path = "['match/s1']"
     
    '''
    this test case checks if the timestamp is adjusted and logAtoms are forwarded correctly.
    '''
    def test1simple_monotonic_timestamp_adjust_test(self):
      description = "Test1TimestampCorrectionFilter"
      self.match_context_fixed_dme = MatchContext(b' pid=')
      self.fixed_dme = FixedDataModelElement('s1', b' pid=')
      self.match_element_fixed_dme = self.fixed_dme.get_match_element("match", self.match_context_fixed_dme)
      t = time()
   
      self.new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler],
        'Default', False, output_log_line=False)
      self.analysis_context.register_component(self.new_match_path_detector, description)
      self.simple_monotonic_timstamp_adjust = SimpleMonotonicTimestampAdjust([self.new_match_path_detector], False)
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, self.new_match_path_detector)
      self.assertEqual(self.simple_monotonic_timstamp_adjust.receive_atom(self.log_atom_fixed_dme), True)
      self.assertEqual(self.output_stream.getvalue(), self.__expected_string %
        (datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"),
        self.new_match_path_detector.__class__.__name__, description, 1, self.match_path))
    

if __name__ == "__main__":
    unittest.main()
