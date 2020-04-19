import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.ParserMatch import ParserMatch
from aminer.input.LogAtom import LogAtom
from aminer.analysis.MissingMatchPathValueDetector import MissingMatchPathValueDetector,\
  MissingMatchPathListValueDetector
import time
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from unit.TestBase import TestBase
from datetime import datetime

class MissingMatchPathValueDetectorTest(TestBase):
    __expected_string = '%s Interval too large between values\n%s: "%s" (%d lines)\n    %s\n\n'
    __default_interval = 3600
    __realert_interval = 86400

    pid = b' pid='
    datetime_format_string = '%Y-%m-%d %H:%M:%S'
    match1_s1_overdue = "match1/s1: b' pid=' overdue 400.0s (interval -400)"
    string = b'25537 uid=2'

    '''
    This test case checks whether a missing value is created without using the autoIncludeFlag. (should not be the case)
    '''
    def test1_receive_atom(self):
      description = "Test1MissingMatchPathValueDetector"
      self.match_context_fixed_dme = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element_fixed_dme = self.fixed_dme.get_match_element("match1", self.match_context_fixed_dme)
      self.missing_match_path_value_detector = MissingMatchPathValueDetector(self.aminer_config,
        self.match_element_fixed_dme.get_path(), [self.stream_printer_event_handler], 'Default', False, self.__default_interval, self.__realert_interval)
      self.analysis_context.register_component(self.missing_match_path_value_detector, description)
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), 1,
        self.missing_match_path_value_detector)
      self.assertTrue(self.missing_match_path_value_detector.receive_atom(self.log_atom_fixed_dme))
      
    '''
    This test case checks if the ReceiveAtom controls the MatchElement and responds correctly, 
    when it is missing.
    '''
    def test2_receive_atom_without_match_element(self):
      description = "Test2MissingMatchPathValueDetector"
      self.match_context_fixed_dme = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element_fixed_dme = self.fixed_dme.get_match_element("match1", self.match_context_fixed_dme)
      self.match_context_fixed_dme = MatchContext(self.pid)
      self.matchElementFixedDME2 = self.fixed_dme.get_match_element("match2", self.match_context_fixed_dme)
      self.missing_match_path_value_detector = MissingMatchPathValueDetector(self.aminer_config,
        self.match_element_fixed_dme.get_path(), [self.stream_printer_event_handler], 'Default', False, self.__default_interval, self.__realert_interval)
      self.analysis_context.register_component(self.missing_match_path_value_detector, description)
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.matchElementFixedDME2), 1,
        self.missing_match_path_value_detector)
      self.assertFalse(self.missing_match_path_value_detector.receive_atom(self.log_atom_fixed_dme))
      
    '''
    This test case checks whether the class returns wrong positives, when the time limit is not passed.
    '''
    def test3_receive_atom_no_missing_value(self):
      description = "Test3MissingMatchPathValueDetector"
      self.match_context_fixed_dme = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element_fixed_dme = self.fixed_dme.get_match_element("match1", self.match_context_fixed_dme)
      self.missing_match_path_value_detector = MissingMatchPathValueDetector(self.aminer_config,
        self.match_element_fixed_dme.get_path(), [self.stream_printer_event_handler], 'Default', True, self.__default_interval, self.__realert_interval)
      self.analysis_context.register_component(self.missing_match_path_value_detector, description)
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme),
        time.time(), self.missing_match_path_value_detector)
      self.assertTrue(self.missing_match_path_value_detector.receive_atom(self.log_atom_fixed_dme))
      
      self.past_time = 3200
      self.missing_match_path_value_detector = MissingMatchPathValueDetector(self.aminer_config,
        self.match_element_fixed_dme.get_path(), [self.stream_printer_event_handler], 'Default', True,
        self.missing_match_path_value_detector.default_interval - self.past_time, self.__realert_interval)
      
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme),
        time.time() + self.past_time, self.missing_match_path_value_detector)
      self.assertTrue(self.missing_match_path_value_detector.receive_atom(self.log_atom_fixed_dme))
      self.assertEqual(self.output_stream.getvalue(), '')
    
    '''
    This test case checks if missing values are reported correctly.
    '''
    def test4_receive_atom_missing_value(self):
      description = "Test4MissingMatchPathValueDetector"
      self.match_context_fixed_dme = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element_fixed_dme = self.fixed_dme.get_match_element("match1", self.match_context_fixed_dme)
      self.missing_match_path_value_detector = MissingMatchPathValueDetector(self.aminer_config, self.match_element_fixed_dme.get_path(),
        [self.stream_printer_event_handler], 'Default', True, self.__default_interval, self.__realert_interval)
      self.analysis_context.register_component(self.missing_match_path_value_detector, description)
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), time.time(), self.missing_match_path_value_detector)
      self.assertTrue(self.missing_match_path_value_detector.receive_atom(self.log_atom_fixed_dme))
      
      self.past_time = 4000
      t = time.time()
      self.missing_match_path_value_detector = MissingMatchPathValueDetector(self.aminer_config, self.match_element_fixed_dme.get_path(),
        [self.stream_printer_event_handler], 'Default', True, self.missing_match_path_value_detector.default_interval - self.past_time, self.__realert_interval, output_log_line=False)
      self.analysis_context.register_component(self.missing_match_path_value_detector, description + "2")
      
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), time.time() + self.past_time, self.missing_match_path_value_detector)
      self.assertTrue(self.missing_match_path_value_detector.receive_atom(self.log_atom_fixed_dme), )
      self.assertTrue(self.output_stream.getvalue() == self.__expected_string % (
        datetime.fromtimestamp(t + self.past_time).strftime(self.datetime_format_string),
        self.missing_match_path_value_detector.__class__.__name__, description + "2",
        1, self.match1_s1_overdue + "\nb' pid='"))
      
    '''
    Persisting elements is tested in this test case.
    '''
    def test5_missing_value_on_persisted(self):
      description = "Test5MissingMatchPathValueDetector"
      self.match_context_fixed_dme = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element_fixed_dme = self.fixed_dme.get_match_element("match1", self.match_context_fixed_dme)
      self.missing_match_path_value_detector = MissingMatchPathValueDetector(self.aminer_config,
                                                                             self.match_element_fixed_dme.get_path(), [self.stream_printer_event_handler], 'Default', True, self.__default_interval, self.__realert_interval)
      self.analysis_context.register_component(self.missing_match_path_value_detector, description)
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme),
        round(time.time()), self.missing_match_path_value_detector)
      self.assertTrue(self.missing_match_path_value_detector.receive_atom(self.log_atom_fixed_dme))
      self.missing_match_path_value_detector.do_persist()
      
      self.past_time = 4000
      t = time.time()
      self.other_missing_match_path_value_detector = MissingMatchPathValueDetector(self.aminer_config,
        self.match_element_fixed_dme.get_path(), [self.stream_printer_event_handler], 'Default', True, self.__default_interval, self.__realert_interval)
      self.analysis_context.register_component(self.other_missing_match_path_value_detector, description + "2")
      self.other_missing_match_path_value_detector.set_check_value(self.other_missing_match_path_value_detector.
        get_channel_key(self.log_atom_fixed_dme), self.__default_interval - self.past_time)
      
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme),
        round(time.time()) + self.past_time, self.other_missing_match_path_value_detector)
      self.assertTrue(self.other_missing_match_path_value_detector.receive_atom(self.log_atom_fixed_dme))
      self.assertTrue((self.output_stream.getvalue() == self.__expected_string % (
        datetime.fromtimestamp(t + self.past_time).strftime(self.datetime_format_string),
        self.other_missing_match_path_value_detector.__class__.__name__, description + "2",
        1, self.match1_s1_overdue)) or (self.output_stream.getvalue(), self.__expected_string % (
        datetime.fromtimestamp(t + self.past_time + 1).strftime(self.datetime_format_string),
        self.other_missing_match_path_value_detector.__class__.__name__, description + "2",
        1, self.match1_s1_overdue)))
      
    '''
    This test case checks, whether a missing value is created by a list without using the autoIncludeFlag. (should not be the case)
    '''
    def test6_receive_atom_list(self):
      description = "Test6MissingMatchPathValueDetector"
      self.match_context_fixed_dme = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element_fixed_dme = self.fixed_dme.get_match_element("match1", self.match_context_fixed_dme)
      self.match_context_decimal_integer_value_me = MatchContext(self.string)
      self.decimal_integer_value_me = DecimalIntegerValueModelElement('d1',
        DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      self.match_element_decimal_integer_value_me = self.decimal_integer_value_me.get_match_element("match2",
        self.match_context_decimal_integer_value_me)
      
      self.missing_match_path_list_value_detector = MissingMatchPathListValueDetector(self.aminer_config,
        [self.match_element_fixed_dme.get_path(), self.match_element_decimal_integer_value_me.get_path()],
        [self.stream_printer_event_handler], 'Default', False, self.__default_interval, self.__realert_interval)
      self.analysis_context.register_component(self.missing_match_path_list_value_detector, description)
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme),
        1, self.missing_match_path_list_value_detector)
      self.assertTrue(self.missing_match_path_list_value_detector.receive_atom(self.log_atom_fixed_dme))
    
    '''
    This test case checks if the ReceiveAtom controls the list of MatchElements and responds correctly, 
    when a value is missing.
    '''
    def test7_receive_atom_list_without_match_element(self):
      description = "Test7MissingMatchPathValueDetector"
      self.match_context_fixed_dme = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element_fixed_dme = self.fixed_dme.get_match_element("match1", self.match_context_fixed_dme)
      self.match_context_decimal_integer_value_me = MatchContext(self.string)
      self.decimal_integer_value_me = DecimalIntegerValueModelElement('d1',
        DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      self.match_element_decimal_integer_value_me = self.decimal_integer_value_me.get_match_element("match2",
        self.match_context_decimal_integer_value_me)
      
      self.match_context_fixed_dme = MatchContext(self.pid)
      self.matchElementFixedDME2 = self.fixed_dme.get_match_element("match3", self.match_context_fixed_dme)
      self.missing_match_path_list_value_detector = MissingMatchPathListValueDetector(self.aminer_config,
        [self.match_element_fixed_dme.get_path(), self.match_element_decimal_integer_value_me.get_path()],
        [self.stream_printer_event_handler], 'Default', False, self.__default_interval, self.__realert_interval)
      self.analysis_context.register_component(self.missing_match_path_list_value_detector, description)
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.matchElementFixedDME2), 1,
        self.missing_match_path_list_value_detector)
      self.assertFalse(self.missing_match_path_list_value_detector.receive_atom(self.log_atom_fixed_dme))

    '''
    This test case checks whether the class returns wrong positives on lists, when the time limit should not be passed.
    '''
    def test8_receive_atom_list_no_missing_value(self):
      description = "Test8MissingMatchPathValueDetector"
      self.match_context_fixed_dme = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element_fixed_dme = self.fixed_dme.get_match_element("match1", self.match_context_fixed_dme)
      
      self.match_context_decimal_integer_value_me = MatchContext(self.string)
      self.decimal_integer_value_me = DecimalIntegerValueModelElement('d1',
        DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      self.match_element_decimal_integer_value_me = self.decimal_integer_value_me.get_match_element("match2",
        self.match_context_decimal_integer_value_me)
      
      self.missing_match_path_list_value_detector = MissingMatchPathListValueDetector(self.aminer_config,
        [self.match_element_fixed_dme.get_path(), self.match_element_decimal_integer_value_me.get_path()],
        [self.stream_printer_event_handler], 'Default', True, self.__default_interval, self.__realert_interval)
      self.analysis_context.register_component(self.missing_match_path_list_value_detector, description)
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme),
        round(time.time()), self.missing_match_path_list_value_detector)
      self.assertTrue(self.missing_match_path_list_value_detector.receive_atom(self.log_atom_fixed_dme))
      
      self.past_time = 3200
      self.missing_match_path_list_value_detector = MissingMatchPathListValueDetector(self.aminer_config,
        [self.match_element_fixed_dme.get_path(), self.match_element_decimal_integer_value_me.get_path()],
        [self.stream_printer_event_handler], 'Default', True, self.missing_match_path_list_value_detector.
                                                                default_interval - self.past_time, self.__realert_interval)
      self.analysis_context.register_component(self.missing_match_path_list_value_detector, description + "2")
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme),
        round(time.time()) + self.past_time, self.missing_match_path_list_value_detector)
      self.assertTrue(self.missing_match_path_list_value_detector.receive_atom(self.log_atom_fixed_dme))
      self.assertEqual(self.output_stream.getvalue(), '')
      
    '''
    This test case checks if missing values are reported correctly.
    '''
    def test9_receive_atom_list_missing_value(self):
      description = "Test90MissingMatchPathValueDetector"
      self.match_context_fixed_dme = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element_fixed_dme = self.fixed_dme.get_match_element("match1", self.match_context_fixed_dme)
      self.match_context_decimal_integer_value_me = MatchContext(self.string)
      self.decimal_integer_value_me = DecimalIntegerValueModelElement('d1',
        DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      self.match_element_decimal_integer_value_me = self.decimal_integer_value_me.get_match_element("match2",
        self.match_context_decimal_integer_value_me)
      
      self.missing_match_path_list_value_detector = MissingMatchPathListValueDetector(self.aminer_config,
        [self.match_element_fixed_dme.get_path(), self.match_element_decimal_integer_value_me.get_path()],
        [self.stream_printer_event_handler], 'Default', True, self.__default_interval, self.__realert_interval)
      self.analysis_context.register_component(self.missing_match_path_list_value_detector, description)
      
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme),
        round(time.time()), self.missing_match_path_list_value_detector)
      self.assertTrue(self.missing_match_path_list_value_detector.receive_atom(self.log_atom_fixed_dme))
      
      self.past_time = 4000
      self.missing_match_path_list_value_detector = MissingMatchPathListValueDetector(self.aminer_config,
        [self.match_element_fixed_dme.get_path(), self.match_element_decimal_integer_value_me.get_path()],
        [self.stream_printer_event_handler], 'Default', True, self.missing_match_path_list_value_detector.
                                                                default_interval - self.past_time, self.__realert_interval)
      self.analysis_context.register_component(self.missing_match_path_list_value_detector, description + "2")
      
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme),
        round(time.time()) + self.past_time, self.missing_match_path_list_value_detector)
      self.assertTrue(self.missing_match_path_list_value_detector.receive_atom(self.log_atom_fixed_dme))
      self.assertTrue((self.output_stream.getvalue() == self.__expected_string % (
        datetime.fromtimestamp(time.time() + self.past_time).strftime(self.datetime_format_string),
        self.missing_match_path_list_value_detector.__class__.__name__, description + "2",
        1,"match1/s1, match2/d1: b' pid=' overdue 400s (interval -400)")) or (self.output_stream.getvalue(), self.__expected_string % (
        datetime.fromtimestamp(time.time() + self.past_time + 1).strftime(self.datetime_format_string),
        self.missing_match_path_list_value_detector.__class__.__name__, description + "2",
        1,"match1/s1, match2/d1: b' pid=' overdue 400s (interval -400)")))
      
    '''
    Persisting lists is tested in this test case.
    '''
    def test10_missing_value_on_persisted(self):
      description = "Test91MissingMatchPathValueDetector"
      self.match_context_fixed_dme = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s2', self.pid)
      self.match_element_fixed_dme = self.fixed_dme.get_match_element("match3", self.match_context_fixed_dme)
      
      self.match_context_decimal_integer_value_me = MatchContext(self.string)
      self.decimal_integer_value_me = DecimalIntegerValueModelElement('d2',
        DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      self.match_element_decimal_integer_value_me = self.decimal_integer_value_me.get_match_element("match4",
        self.match_context_decimal_integer_value_me)
      self.missing_match_path_list_value_detector = MissingMatchPathListValueDetector(self.aminer_config,
        [self.match_element_fixed_dme.get_path(), self.match_element_decimal_integer_value_me.get_path()],
        [self.stream_printer_event_handler], 'Default', True, self.__default_interval, self.__realert_interval)
      self.analysis_context.register_component(self.missing_match_path_list_value_detector, description)
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme),
        round(time.time()), self.missing_match_path_list_value_detector)
      self.assertTrue(self.missing_match_path_list_value_detector.receive_atom(self.log_atom_fixed_dme))
      self.missing_match_path_list_value_detector.do_persist()
      
      self.past_time = 4000
      t = time.time()
      self.other_missing_match_path_list_value_detector = MissingMatchPathListValueDetector(self.aminer_config,
        [self.match_element_fixed_dme.get_path(), self.match_element_decimal_integer_value_me.get_path()],
        [self.stream_printer_event_handler], 'Default', True, self.__default_interval, self.__realert_interval)
      self.analysis_context.register_component(self.other_missing_match_path_list_value_detector, description + "2")
      self.other_missing_match_path_list_value_detector.set_check_value(self.other_missing_match_path_list_value_detector.
        get_channel_key(self.log_atom_fixed_dme), self.__default_interval - self.past_time)
      
      self.log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme),
        round(time.time()) + self.past_time, self.other_missing_match_path_list_value_detector)
      self.assertTrue(self.other_missing_match_path_list_value_detector.receive_atom(self.log_atom_fixed_dme))
      self.assertTrue((self.output_stream.getvalue() == self.__expected_string % (
        datetime.fromtimestamp(t + self.past_time).strftime(self.datetime_format_string),
        self.other_missing_match_path_list_value_detector.__class__.__name__, description + "2",
        1,"match3/s2, match4/d2: b' pid=' overdue 400s (interval -400)")) or (self.output_stream.getvalue(), self.__expected_string % (
        datetime.fromtimestamp(t + self.past_time + 1).strftime(self.datetime_format_string),
        self.other_missing_match_path_list_value_detector.__class__.__name__, description + "2",
        1, "match3/s2, match4/d2: b' pid=' overdue 400s (interval -400)")))


if __name__ == "__main__":
    unittest.main()
