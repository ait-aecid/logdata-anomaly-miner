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
      match_context_fixed_dme = MatchContext(b' pid=')
      fixed_dme = FixedDataModelElement('s1', b' pid=')
      match_element_fixed_dme = self.fixed_dme.get_match_element("match", match_context_fixed_dme)
      t = time()
   
      new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler],
        'Default', False, output_log_line=False)
      self.analysis_context.register_component(new_match_path_detector, description)
      simple_monotonic_timstamp_adjust = SimpleMonotonicTimestampAdjust([new_match_path_detector], False)
      log_atom_fixed_dme = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element_fixed_dme), t, new_match_path_detector)
      self.assertEqual(simple_monotonic_timstamp_adjust.receive_atom(log_atom_fixed_dme), True)
      self.assertEqual(self.output_stream.getvalue(), self.__expected_string %
        (datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"),
        new_match_path_detector.__class__.__name__, description, 1, self.match_path))
    

if __name__ == "__main__":
    unittest.main()
