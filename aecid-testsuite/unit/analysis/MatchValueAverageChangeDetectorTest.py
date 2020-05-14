import unittest
from aminer.analysis.MatchValueAverageChangeDetector import MatchValueAverageChangeDetector
from aminer.parsing.MatchElement import MatchElement
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase
from datetime import datetime
import time


class MatchValueAverageChangeDetectorTest(TestBase):
    __expected_string = '%s Statistical data report\n%s: "%s" (%d lines)\n  "cron/job1": Change: new: n = 3, avg = %s, var = 100000000.0; old: n = 3, avg = %s, var = 1000000.0\n\n'
    __expected_string2 = '%s Statistical data report\n%s: "%s" (%d lines)\n  "cron/job1": Change: new: n = 2, avg = %s, var = 50000000.0; old: n = 2, avg = %s, var = 500000.0\n  "cron/job2": Change: new: n = 2, avg = %s, var = 60500000.0; old: n = 2, avg = %s, var = 500000.0\n\n'
    
    cron_job1 = 'cron/job1'
    cron_job2 = 'cron/job2'
    
    '''
    This test verifies, that no statistic evaluation is performed, until the minimal 
    amount of bin elements is reached.
    '''
    def test1receive_atom_min_bin_elements_not_reached(self):
      description = "Test1MatchValueAverageChangeDetector"
      start_time = 57600
      match_element1 = MatchElement(self.cron_job1, "%s" % start_time, start_time, [])
      match_value_average_change_detector = MatchValueAverageChangeDetector(self.aminer_config,
        [self.stream_printer_event_handler], None, [match_element1.get_path()], 3, start_time, True, False, 'Default')
      self.analysis_context.register_component(match_value_average_change_detector, description)
      
      # create oldBin
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)

      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 1000), start_time + 1000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 1000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 2000), start_time + 2000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 2000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      # compare Data
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 10000), start_time + 10000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 10000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 20000), start_time + 20000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 20000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      self.assertEqual(self.output_stream.getvalue(), '')
    
    '''
    This test verifies, that no statistic evaluation is performed, until the start 
    time is reached.
    '''
    def test2receive_atom_min_bin_time_not_reached(self):
      description = "Test2MatchValueAverageChangeDetector"
      start_time = 57600
      match_element1 = MatchElement(self.cron_job1, "%s" % start_time, start_time, [])
      match_value_average_change_detector = MatchValueAverageChangeDetector(self.aminer_config,
        [self.stream_printer_event_handler], 'time', [match_element1.get_path()], 3, start_time + 86400, True, False, 'Default')
      self.analysis_context.register_component(match_value_average_change_detector, description)
      
      # create oldBin
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 1000), start_time + 1000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 1000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 2000), start_time + 2000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 2000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      # compare Data
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 10000), start_time + 10000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 10000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 20000), start_time + 20000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 20000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 30000), start_time + 30000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 30000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      self.assertEqual(self.output_stream.getvalue(), '')
    
    '''
    This test case focuses on receiving an atom and being in the statistically acceptable area.
    '''
    def test3receive_atom_statistically_ok(self):
      description = "Test3MatchValueAverageChangeDetector"
      start_time = 57600
      match_element1 = MatchElement(self.cron_job1, "%s" % start_time, start_time, [])
      match_value_average_change_detector = MatchValueAverageChangeDetector(self.aminer_config,
        [self.stream_printer_event_handler], 'time', [match_element1.get_path()], 3, start_time, True, False, 'Default')
      self.analysis_context.register_component(match_value_average_change_detector, description)
      
      # create oldBin
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 1000), start_time + 1000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 1000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 2000), start_time + 2000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 2000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      # compare Data
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 11000), start_time + 11000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 11000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 12000), start_time + 12000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 12000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 13000), start_time + 13000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 13000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      self.assertEqual(self.output_stream.getvalue(), '')
    
    '''
    This test case focuses on receiving an atom and being over the statistically acceptable area.
    '''
    def test4receiveAtomStatisticallyOutOfRange(self):
      description = "Test4MatchValueAverageChangeDetector"
      start_time = time.time()
      
      match_element1 = MatchElement(self.cron_job1, "%s" % start_time, start_time, [])
      match_value_average_change_detector = MatchValueAverageChangeDetector(self.aminer_config,
        [self.stream_printer_event_handler], None, [match_element1.get_path()], 3, start_time, True, False, 'Default')
      self.analysis_context.register_component(match_value_average_change_detector, description)
      
      # create oldBin
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 1000), start_time + 1000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 1000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 2000), start_time + 2000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 2000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      # compare Data
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 10000), start_time + 10000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 10000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 20000), start_time + 20000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 20000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)

      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 30000), start_time + 30000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 30000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      self.assertEqual(self.output_stream.getvalue(), self.__expected_string %
        (datetime.fromtimestamp(start_time + 30000).strftime("%Y-%m-%d %H:%M:%S"), match_value_average_change_detector.__class__.__name__,
        description, 6, start_time + 20000, start_time + 1000))
    
    '''
    This test case proves the functionality, when using more than one path.
    '''
    def test5more_values(self):
      description = "Test5MatchValueAverageChangeDetector"
      start_time = time.time()
      
      match_element1 = MatchElement(self.cron_job1, "%s" % start_time, start_time, [])
      match_element2 = MatchElement(self.cron_job2, "%s" % start_time, start_time, [])
      match_value_average_change_detector = MatchValueAverageChangeDetector(self.aminer_config,
        [self.stream_printer_event_handler], None, [match_element1.get_path(), match_element2.get_path()], 2, start_time, True, False, 'Default')
      self.analysis_context.register_component(match_value_average_change_detector, description)
      
      # create oldBin
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 1000), start_time + 1000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 1000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      # create oldBin for ME2
      log_atom = LogAtom(match_element2.get_match_object(), ParserMatch(match_element2),
        start_time, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      match_element2 = MatchElement(self.cron_job2, "%s" % (start_time + 1000), start_time + 1000, [])
      log_atom = LogAtom(match_element2.get_match_object(), ParserMatch(match_element2),
        start_time + 1000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      # compare data
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 10000), start_time + 10000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 10000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      match_element1 = MatchElement(self.cron_job1, "%s" % (start_time + 20000), start_time + 20000, [])
      log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1),
        start_time + 20000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      
      self.assertEqual(self.output_stream.getvalue(), '')
      
      # compare data with ME2
      match_element2 = MatchElement(self.cron_job2, "%s" % (start_time + 11000), start_time + 11000, [])
      log_atom = LogAtom(match_element2.get_match_object(), ParserMatch(match_element2),
        start_time + 11000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)

      match_element2 = MatchElement(self.cron_job2, "%s" % (start_time + 22000), start_time + 22000, [])
      log_atom = LogAtom(match_element2.get_match_object(), ParserMatch(match_element2),
        start_time + 22000, match_value_average_change_detector)
      match_value_average_change_detector.receive_atom(log_atom)
      self.assertEqual(self.output_stream.getvalue(), self.__expected_string2 %
        (datetime.fromtimestamp(start_time + 22000).strftime("%Y-%m-%d %H:%M:%S"),
        match_value_average_change_detector.__class__.__name__, description,
        4, start_time + 15000, start_time + 500, start_time + 16500, start_time + 500))


if __name__ == "__main__":
    unittest.main()
