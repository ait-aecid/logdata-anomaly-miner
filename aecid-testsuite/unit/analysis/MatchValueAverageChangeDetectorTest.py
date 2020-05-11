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
      self.start_time = 57600
      self.match_element1 = MatchElement(self.cron_job1, "%s" % self.start_time, self.start_time, [])
      self.match_value_average_change_detector = MatchValueAverageChangeDetector(self.aminer_config,
        [self.stream_printer_event_handler], None, [self.match_element1.get_path()], 3, self.start_time, True, False, 'Default')
      self.analysis_context.register_component(self.match_value_average_change_detector, description)
      
      #create oldBin
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)

      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 1000), self.start_time + 1000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 1000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 2000), self.start_time + 2000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 2000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      #compare Data
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 10000), self.start_time + 10000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 10000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 20000), self.start_time + 20000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 20000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.assertEqual(self.output_stream.getvalue(), '')
    
    '''
    This test verifies, that no statistic evaluation is performed, until the start 
    time is reached.
    '''
    def test2receive_atom_min_bin_time_not_reached(self):
      description = "Test2MatchValueAverageChangeDetector"
      self.start_time = 57600
      self.match_element1 = MatchElement(self.cron_job1, "%s" % self.start_time, self.start_time, [])
      self.match_value_average_change_detector = MatchValueAverageChangeDetector(self.aminer_config,
        [self.stream_printer_event_handler], 'time', [self.match_element1.get_path()], 3, self.start_time + 86400, True, False, 'Default')
      self.analysis_context.register_component(self.match_value_average_change_detector, description)
      
      #create oldBin
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 1000), self.start_time + 1000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 1000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 2000), self.start_time + 2000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 2000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      #compare Data
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 10000), self.start_time + 10000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 10000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 20000), self.start_time + 20000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 20000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 30000), self.start_time + 30000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 30000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.assertEqual(self.output_stream.getvalue(), '')
    
    '''
    This test case focuses on receiving an atom and being in the statistically acceptable area.
    '''
    def test3receive_atom_statistically_ok(self):
      description = "Test3MatchValueAverageChangeDetector"
      self.start_time = 57600
      self.match_element1 = MatchElement(self.cron_job1, "%s" % self.start_time, self.start_time, [])
      self.match_value_average_change_detector = MatchValueAverageChangeDetector(self.aminer_config,
        [self.stream_printer_event_handler], 'time', [self.match_element1.get_path()], 3, self.start_time, True, False, 'Default')
      self.analysis_context.register_component(self.match_value_average_change_detector, description)
      
      #create oldBin
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 1000), self.start_time + 1000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 1000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 2000), self.start_time + 2000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 2000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      #compare Data
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 11000), self.start_time + 11000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 11000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 12000), self.start_time + 12000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 12000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 13000), self.start_time + 13000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 13000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.assertEqual(self.output_stream.getvalue(), '')
    
    '''
    This test case focuses on receiving an atom and being over the statistically acceptable area.
    '''
    def test4receiveAtomStatisticallyOutOfRange(self):
      description = "Test4MatchValueAverageChangeDetector"
      self.start_time = time.time()
      
      self.match_element1 = MatchElement(self.cron_job1, "%s" % self.start_time, self.start_time, [])
      self.match_element2 = MatchElement(self.cron_job2, "%s" % (self.start_time + 1000), self.start_time + 1000, [])
      self.match_element3 = MatchElement('cron/job3', "%s" % (self.start_time + 2000), self.start_time + 2000, [])
      self.match_value_average_change_detector = MatchValueAverageChangeDetector(self.aminer_config,
        [self.stream_printer_event_handler], None, [self.match_element1.get_path()], 3, self.start_time, True, False, 'Default')
      self.analysis_context.register_component(self.match_value_average_change_detector, description)
      
      #create oldBin
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 1000), self.start_time + 1000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 1000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 2000), self.start_time + 2000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 2000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      #compare Data
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 10000), self.start_time + 10000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 10000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 20000), self.start_time + 20000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 20000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.parserMatch = ParserMatch(self.match_element1)
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 30000), self.start_time + 30000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 30000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      self.assertEqual(self.output_stream.getvalue(), self.__expected_string %
        (datetime.fromtimestamp(self.start_time + 30000).strftime("%Y-%m-%d %H:%M:%S"), self.match_value_average_change_detector.__class__.__name__,
        description, 6, self.start_time + 20000, self.start_time + 1000))
    
    '''
    This test case proves the functionality, when using more than one path.
    '''
    def test5more_values(self):
      description = "Test5MatchValueAverageChangeDetector"
      self.start_time = time.time()
      
      self.match_element1 = MatchElement(self.cron_job1, "%s" % self.start_time, self.start_time, [])
      self.match_element2 = MatchElement(self.cron_job2, "%s" % self.start_time, self.start_time, [])
      self.match_value_average_change_detector = MatchValueAverageChangeDetector(self.aminer_config,
        [self.stream_printer_event_handler], None, [self.match_element1.get_path(), self.match_element2.get_path()], 2, self.start_time, True, False, 'Default')
      self.analysis_context.register_component(self.match_value_average_change_detector, description)
      
      #create oldBin
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 1000), self.start_time + 1000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 1000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      #create oldBin for ME2
      self.log_atom = LogAtom(self.match_element2.get_match_object(), ParserMatch(self.match_element2),
        self.start_time, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.match_element2 = MatchElement(self.cron_job2, "%s" % (self.start_time + 1000), self.start_time + 1000, [])
      self.log_atom = LogAtom(self.match_element2.get_match_object(), ParserMatch(self.match_element2),
        self.start_time + 1000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      #compare data
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 10000), self.start_time + 10000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 10000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.match_element1 = MatchElement(self.cron_job1, "%s" % (self.start_time + 20000), self.start_time + 20000, [])
      self.log_atom = LogAtom(self.match_element1.get_match_object(), ParserMatch(self.match_element1),
        self.start_time + 20000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      
      self.assertEqual(self.output_stream.getvalue(), '')
      
      #compare data with ME2
      self.match_element2 = MatchElement(self.cron_job2, "%s" % (self.start_time + 11000), self.start_time + 11000, [])
      self.log_atom = LogAtom(self.match_element2.get_match_object(), ParserMatch(self.match_element2),
        self.start_time + 11000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)

      self.match_element2 = MatchElement(self.cron_job2, "%s" % (self.start_time + 22000), self.start_time + 22000, [])
      self.log_atom = LogAtom(self.match_element2.get_match_object(), ParserMatch(self.match_element2),
        self.start_time + 22000, self.match_value_average_change_detector)
      self.match_value_average_change_detector.receive_atom(self.log_atom)
      self.assertEqual(self.output_stream.getvalue(), self.__expected_string2 %
        (datetime.fromtimestamp(self.start_time + 22000).strftime("%Y-%m-%d %H:%M:%S"),
        self.match_value_average_change_detector.__class__.__name__, description,
        4, self.start_time + 15000, self.start_time + 500, self.start_time + 16500, self.start_time + 500))


if __name__ == "__main__":
    unittest.main()
