import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from time import time
from aminer.parsing.ParserMatch import ParserMatch
from aminer.input.LogAtom import LogAtom
from unit.TestBase import TestBase
from datetime import datetime


class StreamPrinterEventHandlerTest(TestBase):
    __expectedString = '%s New value for pathes %s: %s\n%s: "%s" (%d lines)\n%s\n'
    
    pid = b' pid='
    test = 'Test.%s'
    match_s1 = 'match/s1'
    match_s2 = 'match/s2'
    new_val = 'New value for pathes %s, %s: %s'
    
    '''
    In this test case the EventHandler receives multiple lines from the test class.
    '''
    def test1log_multiple_lines_event(self):
      description = "Test1StreamPrinterEventHandler"
      self.match_context = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element = self.fixed_dme.get_match_element("match", self.match_context)
      
      self.match_context = MatchContext(self.pid)
      self.fixed_dme2 = FixedDataModelElement('s2', self.pid)
      self.match_element2 = self.fixed_dme2.get_match_element("match", self.match_context)
      self.analysis_context.register_component(self, description)
      self.t = time()
      self.log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element), self.t, self)
      
      self.stream_printer_event_handler.receive_event(self.test % self.__class__.__name__, \
          self.new_val % (self.match_s1, self.match_s2, 
          repr(self.match_element.match_object)), [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom, self)
      
      self.assertEqual(self.output_stream.getvalue(), self.__expectedString %
        (datetime.fromtimestamp(self.t).strftime("%Y-%m-%d %H:%M:%S"),
        self.match_element.get_path() + ", " + self.match_element2.get_path(), self.match_element.get_match_object(),
        self.__class__.__name__, description, 2,"  " + self.match_element.get_match_string().decode() + "\n  " + self.match_element2.get_match_string().decode() + "\n"))
    
    '''
    In this test case the EventHandler receives no lines from the test class.
    '''
    def test2log_no_line_event(self):
      description = "Test2StreamPrinterEventHandler"
      self.match_context = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element = self.fixed_dme.get_match_element("match", self.match_context)
      
      self.match_context = MatchContext(self.pid)
      self.fixed_dme2 = FixedDataModelElement('s2', self.pid)
      self.match_element2 = self.fixed_dme2.get_match_element("match", self.match_context)
      self.analysis_context.register_component(self, description)
      self.t = time()
      self.log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element), self.t, self)
      
      self.stream_printer_event_handler.receive_event(self.test % self.__class__.__name__, \
          self.new_val % (self.match_s1, self.match_s2, 
          repr(self.match_element.match_object)), [], None, self.log_atom, self)
      
      self.assertEqual(self.output_stream.getvalue(), self.__expectedString %
        (datetime.fromtimestamp(self.t).strftime("%Y-%m-%d %H:%M:%S"),
        self.match_element.get_path() + ", " + self.match_element2.get_path(), self.match_element.get_match_object(),
        self.__class__.__name__, description, 0, ""))
    
    '''
    In this test case the EventHandler receives no logAtom from the test class and the method
    should raise an exception.
    '''
    def test3event_data_not_log_atom(self):
      description = "Test3StreamPrinterEventHandler"
      self.match_context = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element = self.fixed_dme.get_match_element("match", self.match_context)
      
      self.match_context = MatchContext(self.pid)
      self.fixed_dme2 = FixedDataModelElement('s2', self.pid)
      self.match_element2 = self.fixed_dme2.get_match_element("match", self.match_context)
      self.analysis_context.register_component(self, description)
      self.t = time()
      self.log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element), self.t, self)
      
      self.assertRaises(Exception, self.stream_printer_event_handler.receive_event, self.test % self.__class__.__name__, \
        self.new_val % (self.match_s1, self.match_s2,
        repr(self.match_element.match_object)), [self.log_atom.raw_data, self.log_atom.raw_data],
        self.log_atom.get_parser_match(), self)


if __name__ == "__main__":
    unittest.main()
