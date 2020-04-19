import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.events.SyslogWriterEventHandler import SyslogWriterEventHandler
from time import time, sleep
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
import os
from unit.TestBase import TestBase
from datetime import datetime


class SyslogWriterEventHandlerTest(TestBase):
    '''
    Some of the test cases may fail if the same numbers as the PID are found in the syslog.
    Rerun the unit, when this happens.
    '''
    __expected_string = '[0] %s New value for pathes %s, %s: %s\n[0-1] %s: "%s" (%d lines)\n[0-2]   %s\n[0-3]   %s\n'
    __expected_string2 = '[0] %s New value for pathes %s, %s: %s\n[0-1] %s: "%s" (%d lines)\n'
  
    pid = b' pid='
    test = 'Test.%s'
    match_s1 = 'match/s1'
    match_s2 = 'match/s2'
    new_val = 'New value for pathes %s, %s: %s'
  
    '''
    In this test case the EventHandler receives multiple lines from the test class.
    '''
    def test1log_multiple_lines_event(self):
      description = "Test1SyslogWriterEventHandler"
      self.match_context = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element = self.fixed_dme.get_match_element("match", self.match_context)
      
      self.match_context = MatchContext(self.pid)
      self.fixed_dme2 = FixedDataModelElement('s2', self.pid)
      self.match_element2 = self.fixed_dme2.get_match_element("match", self.match_context)
      
      self.syslog_writer_event_handler = SyslogWriterEventHandler(self.analysis_context, 'aminer')
      self.analysis_context.register_component(self, description)
      
      self.t = time()
      self.log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element), self.t, self)
      
      self.syslog_writer_event_handler.receive_event(self.test % self.__class__.__name__, \
          self.new_val % (self.match_s1, self.match_s2, 
          repr(self.match_element.match_object)), [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom, self)
      self.string = ''
      
      sleep(0.2)
      with open("/var/log/syslog") as search:
          for line in search:
              line = line.rstrip()  # remove '\n' at end of line
              if 'aminer['+str(os.getpid())+']' in line:
                line = line.split("]: ")
                self.string += (line[1]) + '\n'
      self.found = False
      self.string = self.string.split('Syslog logger initialized\n')
      self.expected = self.__expected_string % (datetime.fromtimestamp(self.t).strftime("%Y-%m-%d %H:%M:%S"),
        self.match_element.get_path(), self.match_element2.get_path(), self.match_element.get_match_object(),
        self.__class__.__name__, description, 2, self.match_element.get_match_string().decode(),
        self.match_element2.get_match_string().decode())
      
      for log in self.string:
        if self.expected in log:
            self.found = True
      self.assertTrue(self.found)
    
    '''
    In this test case the EventHandler receives no lines from the test class.
    '''
    def test2log_no_line_event(self):
      description = "Test2SyslogWriterEventHandler"
      self.match_context = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element = self.fixed_dme.get_match_element("match", self.match_context)
      
      self.match_context = MatchContext(self.pid)
      self.fixed_dme2 = FixedDataModelElement('s2', self.pid)
      self.match_element2 = self.fixed_dme2.get_match_element("match", self.match_context)
      
      self.syslog_writer_event_handler = SyslogWriterEventHandler(self.analysis_context, 'aminer')
      self.analysis_context.register_component(self, description)
      
      self.t = time()
      self.log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element), self.t, self)
      
      self.syslog_writer_event_handler.receive_event(self.test % self.__class__.__name__, \
          self.new_val % (self.match_s1, self.match_s2, 
          repr(self.match_element.match_object)), [], None, self.log_atom, self)
      self.string = ''
      
      sleep(0.2)
      with open("/var/log/syslog") as search:
          for line in search:
              line = line.rstrip()  # remove '\n' at end of line
              if 'aminer['+str(os.getpid())+']' in line:
                line = line.split("]: ")
                self.string += (line[1]) + '\n'
      self.found = False
      self.string = self.string.split('Syslog logger initialized\n')
      self.expected = self.__expected_string2 % (datetime.fromtimestamp(self.t).strftime("%Y-%m-%d %H:%M:%S"),
        self.match_element.get_path(), self.match_element2.get_path(), self.match_element.get_match_object(),
        self.__class__.__name__, description, 0)

      for log in self.string:
        if self.expected in log:
            self.found = True
      self.assertTrue(self.found)
    
    '''
    In this test case the EventHandler receives no logAtom from the test class and the class
    should raise an exception.
    '''
    def test3event_data_not_log_atom(self):
      description = "Test3SyslogWriterEventHandler"
      self.match_context = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element = self.fixed_dme.get_match_element("match", self.match_context)
      
      self.match_context = MatchContext(self.pid)
      self.fixed_dme2 = FixedDataModelElement('s2', self.pid)
      self.match_element2 = self.fixed_dme2.get_match_element("match", self.match_context)
      self.analysis_context.register_component(self, description)
      
      self.syslog_writer_event_handler = SyslogWriterEventHandler(self.analysis_context, 'aminer')
      self.t = time()
      self.log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element), self.t, self)
      self.assertRaises(Exception, self.syslog_writer_event_handler.receive_event, self.test %
        self.__class__.__name__, self.new_val % (self.match_s1, self.match_s2,
        repr(self.match_element.match_object)), [self.log_atom.raw_data, self.log_atom.raw_data],
        self.log_atom.get_parser_match(), self)


if __name__ == "__main__":
    unittest.main()
