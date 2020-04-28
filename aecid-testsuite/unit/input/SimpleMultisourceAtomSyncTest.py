import unittest
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from aminer.input.SimpleMultisourceAtomSync import SimpleMultisourceAtomSync
from aminer.parsing.MatchContext import MatchContext
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from time import time, sleep
from unit.TestBase import TestBase
from datetime import datetime

class SimpleMultisourceAtomSyncTest(TestBase):
    __expected_string = '%s New path(es) detected\n%s: "%s" (%d lines)\n  %s\n%s\n\n'
    
    calculation = b'256 * 2 = 512'
    datetime_format_string = '%Y-%m-%d %H:%M:%S'
    match_path = "['match/a1']"
    
    '''
    In this test case multiple, SORTED LogAtoms of different sources are received by the class.
    '''
    def test1sorted_log_atoms(self):
      description = "Test1SimpleMultisourceAtomSync"
      self.sync_wait_time = 3
      
      self.any_byte_data_model_element = AnyByteDataModelElement('a1')
      self.new_match_path_detector1 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler],
        'Default', False, output_log_line=False)
      self.analysis_context.register_component(self.new_match_path_detector1, description)
      self.new_match_path_detector2 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler],
        'Default', False, output_log_line=False)
      self.analysis_context.register_component(self.new_match_path_detector2, description + "2")
      
      self.simple_multisource_atom_sync = SimpleMultisourceAtomSync([self.new_match_path_detector1,
        self.new_match_path_detector2], self.sync_wait_time)
      
      t = time()
      self.match_context = MatchContext(self.calculation)
      self.match_element = self.any_byte_data_model_element.get_match_element('match', self.match_context)
      self.log_atom1 = LogAtom(self.match_element.match_object, ParserMatch(self.match_element),
        t, self.new_match_path_detector1)
      self.log_atom2 = LogAtom(self.match_element.match_object, ParserMatch(self.match_element),
        t+1, self.new_match_path_detector1)
      
      self.assertTrue(not self.simple_multisource_atom_sync.receive_atom(self.log_atom1))
      sleep(self.sync_wait_time + 1)
      
      #not of the same source, thus must not be accepted.
      self.assertTrue(not self.simple_multisource_atom_sync.receive_atom(self.log_atom2))
      self.assertTrue(self.simple_multisource_atom_sync.receive_atom(self.log_atom1))
      #logAtom1 is handled now, so logAtom2 is accepted.
      self.reset_output_stream()
      self.assertTrue(self.simple_multisource_atom_sync.receive_atom(self.log_atom2))
      self.assertEqual(self.output_stream.getvalue(), self.__expected_string %
        (datetime.fromtimestamp(t+1).strftime(self.datetime_format_string), self.new_match_path_detector1.__class__.__name__, description, 1,
        self.match_path, self.calculation) + self.__expected_string % (datetime.fromtimestamp(t+1).strftime(self.datetime_format_string),
        self.new_match_path_detector1.__class__.__name__, description + "2", 1, self.match_path, self.calculation))
    
    '''
    In this test case a LogAtom with no timestamp is received by the class.
    '''
    def test2no_timestamp_log_atom(self):
      description = "Test2SimpleMultisourceAtomSync"
      self.sync_wait_time = 3
      
      self.any_byte_data_model_element = AnyByteDataModelElement('a1')
      self.new_match_path_detector1 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler],
        'Default', False, output_log_line=False)
      self.analysis_context.register_component(self.new_match_path_detector1, description)
      self.simple_multisource_atom_sync = SimpleMultisourceAtomSync([self.new_match_path_detector1], self.sync_wait_time)
      t = time()
      
      self.match_context = MatchContext(self.calculation)
      self.match_element = self.any_byte_data_model_element.get_match_element('match', self.match_context)
      self.log_atom1 = LogAtom(self.match_element.match_object, ParserMatch(self.match_element), None, self.new_match_path_detector1)
      
      self.assertTrue(self.simple_multisource_atom_sync.receive_atom(self.log_atom1))
      self.assertEqual(self.output_stream.getvalue(), self.__expected_string %
        (datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        self.new_match_path_detector1.__class__.__name__, description, 1,
        self.match_path, self.calculation))
    
    '''
    In this test case multiple, UNSORTED LogAtoms of different sources are received by the class.
    '''
    def test3unsorted_log_atom(self):
      description = "Test3SimpleMultisourceAtomSync"
      self.sync_wait_time = 3
      
      self.any_byte_data_model_element = AnyByteDataModelElement('a1')
      self.new_match_path_detector1 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler],
        'Default', False, output_log_line=False)
      self.analysis_context.register_component(self.new_match_path_detector1, description)
      self.new_match_path_detector2 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler],
        'Default', False, output_log_line=False)
      self.analysis_context.register_component(self.new_match_path_detector2, description + "2")
      
      self.simple_multisource_atom_sync = SimpleMultisourceAtomSync([self.new_match_path_detector1, self.new_match_path_detector2], self.sync_wait_time)
      t = time()
      self.match_context = MatchContext(self.calculation)
      self.match_element = self.any_byte_data_model_element.get_match_element('match', self.match_context)
      self.log_atom1 = LogAtom(self.match_element.match_object, ParserMatch(self.match_element), t, self.new_match_path_detector1)
      self.log_atom2 = LogAtom(self.match_element.match_object, ParserMatch(self.match_element), t - 1, self.new_match_path_detector1)
      
      self.assertTrue(not self.simple_multisource_atom_sync.receive_atom(self.log_atom1))
      sleep(self.sync_wait_time)
      
      #unsorted, should be accepted
      self.reset_output_stream()
      self.assertTrue(self.simple_multisource_atom_sync.receive_atom(self.log_atom2))
      self.assertTrue(self.simple_multisource_atom_sync.receive_atom(self.log_atom1))
      self.assertEqual(self.output_stream.getvalue(), self.__expected_string %
        (datetime.fromtimestamp(t-1).strftime(self.datetime_format_string), self.new_match_path_detector1.__class__.__name__, description, 1,
        self.match_path, self.calculation) + self.__expected_string % (datetime.fromtimestamp(t-1).strftime(self.datetime_format_string),
        self.new_match_path_detector1.__class__.__name__, description + "2", 1, self.match_path, self.calculation) +
        self.__expected_string % (datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        self.new_match_path_detector1.__class__.__name__, description, 1, self.match_path, self.calculation) +
        self.__expected_string % (datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        self.new_match_path_detector1.__class__.__name__, description + "2", 1, self.match_path, self.calculation))
    
    '''
    In this test case a source becomes idle and expires.
    '''
    def test4has_idle_source(self):
      description = "Test4SimpleMultisourceAtomSync"
      self.sync_wait_time = 3
      
      self.any_byte_data_model_element = AnyByteDataModelElement('a1')
      self.new_match_path_detector1 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler],
        'Default', False, output_log_line=False)
      self.analysis_context.register_component(self.new_match_path_detector1, description)
      self.new_match_path_detector2 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler],
        'Default', False, output_log_line=False)
      self.analysis_context.register_component(self.new_match_path_detector2, description + "2")
      
      self.simple_multisource_atom_sync = SimpleMultisourceAtomSync([self.new_match_path_detector1], self.sync_wait_time)
      t = time()
      self.match_context = MatchContext(self.calculation)
      self.match_element = self.any_byte_data_model_element.get_match_element('match', self.match_context)
      self.log_atom1 = LogAtom(self.match_element.match_object, ParserMatch(self.match_element), t, self.new_match_path_detector1)
      self.log_atom2 = LogAtom(self.match_element.match_object, ParserMatch(self.match_element), t, self.new_match_path_detector2)
      
      self.assertTrue(not self.simple_multisource_atom_sync.receive_atom(self.log_atom1))
      self.assertTrue(not self.simple_multisource_atom_sync.receive_atom(self.log_atom2))
      sleep(self.sync_wait_time + 1)
      
      self.assertTrue(self.simple_multisource_atom_sync.receive_atom(self.log_atom1))
      #logAtom1 is handled now, so newMatchPathDetector1 should be deleted after waiting the syncWaitTime.
      self.assertTrue(not self.simple_multisource_atom_sync.receive_atom(self.log_atom2))
      sleep(self.sync_wait_time + 1)
      self.assertTrue(not self.simple_multisource_atom_sync.receive_atom(self.log_atom2))
      self.assertEqual(self.simple_multisource_atom_sync.sources_dict,
        {self.new_match_path_detector1:[self.log_atom1.get_timestamp(), None],
        self.new_match_path_detector2:[self.log_atom2.get_timestamp(), self.log_atom2]})
      
      self.assertTrue(self.simple_multisource_atom_sync.receive_atom(self.log_atom1))
      self.assertTrue(self.simple_multisource_atom_sync.receive_atom(self.log_atom1))
      sleep(self.sync_wait_time + 1)
      self.assertTrue(self.simple_multisource_atom_sync.receive_atom(self.log_atom1))
      self.assertEqual(self.simple_multisource_atom_sync.sources_dict,
        {self.new_match_path_detector1:[self.log_atom1.get_timestamp(), None],
        self.new_match_path_detector2:[self.log_atom2.get_timestamp(), self.log_atom2]})
      self.log_atom1 = LogAtom(self.match_element.match_object, ParserMatch(self.match_element), t + 1, self.new_match_path_detector1)
      self.assertTrue(not self.simple_multisource_atom_sync.receive_atom(self.log_atom1))
      self.assertEqual(self.simple_multisource_atom_sync.sources_dict,
        {self.new_match_path_detector1:[self.log_atom1.get_timestamp() - 1, self.log_atom1],
        self.new_match_path_detector2:[self.log_atom2.get_timestamp(), self.log_atom2]})
      
      self.log_atom1 = LogAtom(self.match_element.match_object, ParserMatch(self.match_element), t - 1, self.new_match_path_detector1)
      self.assertTrue(self.simple_multisource_atom_sync.receive_atom(self.log_atom1))


if __name__ == "__main__":
    unittest.main()
