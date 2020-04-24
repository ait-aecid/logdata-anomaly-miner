import unittest
from aminer.events.Utils import VolatileLogarithmicBackoffEventHistory
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from time import time
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase


class UtilsTest(TestBase):

    pid = b' pid='
    test = 'Test.%s'
    match_s1 = 'match/s1'
    match_s2 = 'match/s2'
    new_val = 'New value for pathes %s, %s: %s '

    '''
    In this test case multiple events are received by the VolatileLogarithmicBackoffEventHistory.
    '''
    def test1add_multiple_objects(self):
      self.volatile_logarithmic_backoff_event_history = VolatileLogarithmicBackoffEventHistory(10)
      
      self.match_context = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element = self.fixed_dme.get_match_element("match", self.match_context)
      
      self.match_context = MatchContext(self.pid)
      self.fixed_dme2 = FixedDataModelElement('s2', self.pid)
      self.match_element2 = self.fixed_dme2.get_match_element("match", self.match_context)
      
      self.t = time()
      self.log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element), self.t, self)
      self.message = self.new_val % (self.match_s1, self.match_s2, 
          repr(self.match_element.match_object))
      
      self.volatile_logarithmic_backoff_event_history.receive_event(self.test % self.__class__.__name__,
        self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom, self)
      self.assertEqual(self.volatile_logarithmic_backoff_event_history.get_history(),
        [(0, self.test % self.__class__.__name__, self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom, self)])
      
      self.volatile_logarithmic_backoff_event_history.receive_event(self.test % self.__class__.__name__,
        self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom, self)
      self.assertEqual(self.volatile_logarithmic_backoff_event_history.get_history(),
        [(0, self.test % self.__class__.__name__, self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom, self),
        (1, self.test % self.__class__.__name__, self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom, self)])
    
    '''
    In this test case no events are received by the VolatileLogarithmicBackoffEventHistory.
    '''
    def test2add_no_objects(self):
      self.volatile_logarithmic_backoff_event_history = VolatileLogarithmicBackoffEventHistory(10)
      self.assertEqual(self.volatile_logarithmic_backoff_event_history.get_history(), [])
    
    '''
    In this test case the EventHandler receives no logAtom from the test class and the output should not contain the log time.
    '''
    def test3event_data_not_log_atom(self):
      self.volatile_logarithmic_backoff_event_history = VolatileLogarithmicBackoffEventHistory(10)
      
      self.match_context = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element = self.fixed_dme.get_match_element("match", self.match_context)
      
      self.match_context = MatchContext(self.pid)
      self.fixed_dme2 = FixedDataModelElement('s2', self.pid)
      self.match_element2 = self.fixed_dme2.get_match_element("match", self.match_context)

      self.t = time()
      self.log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element), self.t, self)
      self.message = self.new_val % (self.match_s1, self.match_s2, 
          repr(self.match_element.match_object))
      
      self.volatile_logarithmic_backoff_event_history.receive_event(self.test % self.__class__.__name__,
        self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom.get_parser_match(), self)
      self.assertEqual(self.volatile_logarithmic_backoff_event_history.get_history(),
        [(0, self.test % self.__class__.__name__, self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom.get_parser_match(), self)])
    
    '''
    In this test case more events than the VolatileLogarithmicBackoffEventHistory can handle are received.
    '''
    def test4max_items_overflow(self):
      self.deviation = 0.05
      self.number_of_events = 5
      self.size = 100000
      msg = "%s=%f is not between %f and %f"
      
      self.match_context = MatchContext(self.pid)
      self.fixed_dme = FixedDataModelElement('s1', self.pid)
      self.match_element = self.fixed_dme.get_match_element("match", self.match_context)
      
      self.match_context = MatchContext(self.pid)
      self.fixed_dme2 = FixedDataModelElement('s2', self.pid)
      self.match_element2 = self.fixed_dme2.get_match_element("match", self.match_context)

      self.t = time()
      self.log_atom = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element), self.t, self)
      self.message = self.new_val % (self.match_s1, self.match_s2, 
          repr(self.match_element.match_object))
      first = 0
      second = 0
      third = 0
      fourth = 0
      
      for _ in range(self.size):
        self.volatile_logarithmic_backoff_event_history = VolatileLogarithmicBackoffEventHistory(2)
        self.volatile_logarithmic_backoff_event_history.receive_event(self.test % self.__class__.__name__,
            self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom.get_parser_match(), self)
        
        self.volatile_logarithmic_backoff_event_history.receive_event(self.test % self.__class__.__name__,
            self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom.get_parser_match(), self)
        
        self.volatile_logarithmic_backoff_event_history.receive_event(self.test % self.__class__.__name__,
            self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom.get_parser_match(), self)
        
        self.volatile_logarithmic_backoff_event_history.receive_event(self.test % self.__class__.__name__,
            self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom.get_parser_match(), self)
        
        self.volatile_logarithmic_backoff_event_history.receive_event(self.test % self.__class__.__name__,
            self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom.get_parser_match(), self)

        history = self.volatile_logarithmic_backoff_event_history.get_history()
        if history == [(0, self.test %
            self.__class__.__name__, self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom.get_parser_match(), self),
            (4, self.test % self.__class__.__name__, self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom.get_parser_match(), self)]:
          first += 1
        elif history == [(1, self.test %
            self.__class__.__name__, self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom.get_parser_match(), self),
            (4, self.test % self.__class__.__name__, self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom.get_parser_match(), self)]:
          second += 1
        elif history == [(2, self.test %
            self.__class__.__name__, self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom.get_parser_match(), self),
            (4, self.test % self.__class__.__name__, self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom.get_parser_match(), self)]:
          third += 1
        elif history == [(3, self.test %
            self.__class__.__name__, self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom.get_parser_match(), self),
            (4, self.test % self.__class__.__name__, self.message, [self.log_atom.raw_data, self.log_atom.raw_data], None, self.log_atom.get_parser_match(), self)]:
          fourth += 1
      val = 0.5*0.5*0.5
      self.min = self.size * val * (1 - self.deviation)
      self.max = self.size * val * (1 + self.deviation)
      self.assertTrue(first <= self.max and first >= self.min, msg % ("first", first, self.min, self.max))
      
      val = 0.5*0.5*0.5
      self.min = self.size * val * (1 - self.deviation)
      self.max = self.size * val * (1 + self.deviation)
      self.assertTrue(second <= self.max and second >= self.min, msg % ("second", second, self.min, self.max))
      
      val = 2*0.5*0.5*0.5
      self.min = self.size * val * (1 - self.deviation)
      self.max = self.size * val * (1 + self.deviation)
      self.assertTrue(third <= self.max and third >= self.min, msg % ("third", third, self.min, self.max))
       
      val = 0.5
      self.min = self.size * val * (1 - self.deviation)
      self.max = self.size * val * (1 + self.deviation)
      self.assertTrue(fourth <= self.max and fourth >= self.min, msg % ("fourth", fourth, self.min, self.max))


if __name__ == "__main__":
    unittest.main()
