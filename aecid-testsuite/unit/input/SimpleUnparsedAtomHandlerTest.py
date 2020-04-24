import unittest
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from time import time
from aminer.parsing.ParserMatch import ParserMatch
from aminer.parsing.MatchContext import MatchContext
from aminer.input.LogAtom import LogAtom
from aminer.input.SimpleUnparsedAtomHandler import SimpleUnparsedAtomHandler
from unit.TestBase import TestBase


class SimpleUnparsedAtomHandlerTest(TestBase):
    
    calculation = b'256 * 2 = 512'
    
    '''
    The atom in this test case has a parserMatch.
    '''
    def test1_atom_is_unparsed(self):
      description = "Test1SimpleUnparsedAtomHandler"
      self.any_byte_data_model_element = AnyByteDataModelElement('a1')
      self.new_match_path_detector1 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler],
        'Default', False)
      
      self.match_context = MatchContext(self.calculation)
      self.match_element = self.any_byte_data_model_element.get_match_element('match', self.match_context)
      self.log_atom = LogAtom(self.match_element.match_object, ParserMatch(self.match_element), time(), self.new_match_path_detector1)
      
      self.simple_unparsed_atom_handler = SimpleUnparsedAtomHandler([self.stream_printer_event_handler])
      self.analysis_context.register_component(self.simple_unparsed_atom_handler, description)
      self.assertTrue(not self.simple_unparsed_atom_handler.receive_atom(self.log_atom))
    
    '''
    The atom in this test case has no parserMatch.
    '''
    def test2_atom_is_parsed(self):
      description = "Test2SimpleUnparsedAtomHandler"
      self.any_byte_data_model_element = AnyByteDataModelElement('a1')
      self.new_match_path_detector1 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler],
        'Default', False)
      
      self.match_context = MatchContext(self.calculation)
      self.match_element = self.any_byte_data_model_element.get_match_element('match', self.match_context)
      self.log_atom = LogAtom(self.match_element.match_object, None, time(), self.new_match_path_detector1)
      
      self.simple_unparsed_atom_handler = SimpleUnparsedAtomHandler([self.stream_printer_event_handler])
      self.analysis_context.register_component(self.simple_unparsed_atom_handler, description)
      self.assertTrue(self.simple_unparsed_atom_handler.receive_atom(self.log_atom))
    
    '''
    In this test case the ParserMatch actually is no instance of ParserMatch. The atom should still be considered to be parsed.
    '''
    def test3_parser_match_is_other_element(self):
      description = "Test3SimpleUnparsedAtomHandler"
      self.any_byte_data_model_element = AnyByteDataModelElement('a1')
      self.new_match_path_detector1 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler],
        'Default', False)
      
      self.match_context = MatchContext(self.calculation)
      self.match_element = self.any_byte_data_model_element.get_match_element('match', self.match_context)
      self.log_atom = LogAtom(self.match_element.match_object, self.any_byte_data_model_element, time(), self.new_match_path_detector1)
      
      self.simple_unparsed_atom_handler = SimpleUnparsedAtomHandler([self.stream_printer_event_handler])
      self.analysis_context.register_component(self.simple_unparsed_atom_handler, description)
      self.assertTrue(not self.simple_unparsed_atom_handler.receive_atom(self.log_atom))


if __name__ == "__main__":
    unittest.main()
