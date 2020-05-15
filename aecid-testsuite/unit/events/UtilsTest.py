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
      volatile_logarithmic_backoff_event_history = VolatileLogarithmicBackoffEventHistory(10)
      
      match_context = MatchContext(self.pid)
      fixed_dme = FixedDataModelElement('s1', self.pid)
      match_element = fixed_dme.get_match_element("match", match_context)
      
      t = time()
      log_atom = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element), t, self)
      message = self.new_val % (self.match_s1, self.match_s2,
          repr(match_element.match_object))
      
      volatile_logarithmic_backoff_event_history.receive_event(self.test % self.__class__.__name__,
        message, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self)
      self.assertEqual(volatile_logarithmic_backoff_event_history.get_history(),
        [(0, self.test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self)])
      
      volatile_logarithmic_backoff_event_history.receive_event(self.test % self.__class__.__name__,
        message, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self)
      self.assertEqual(volatile_logarithmic_backoff_event_history.get_history(),
        [(0, self.test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self),
        (1, self.test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None, log_atom, self)])
    
    '''
    In this test case no events are received by the VolatileLogarithmicBackoffEventHistory.
    '''
    def test2add_no_objects(self):
      volatile_logarithmic_backoff_event_history = VolatileLogarithmicBackoffEventHistory(10)
      self.assertEqual(volatile_logarithmic_backoff_event_history.get_history(), [])
    
    '''
    In this test case the EventHandler receives no logAtom from the test class and the output should not contain the log time.
    '''
    def test3event_data_not_log_atom(self):
      volatile_logarithmic_backoff_event_history = VolatileLogarithmicBackoffEventHistory(10)
      
      match_context = MatchContext(self.pid)
      fixed_dme = FixedDataModelElement('s1', self.pid)
      match_element = fixed_dme.get_match_element("match", match_context)

      t = time()
      log_atom = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element), t, self)
      message = self.new_val % (self.match_s1, self.match_s2,
          repr(match_element.match_object))
      
      volatile_logarithmic_backoff_event_history.receive_event(self.test % self.__class__.__name__,
        message, [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)
      self.assertEqual(volatile_logarithmic_backoff_event_history.get_history(),
        [(0, self.test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)])
    
    '''
    In this test case more events than the VolatileLogarithmicBackoffEventHistory can handle are received.
    '''
    def test4max_items_overflow(self):
      deviation = 0.05
      size = 100000
      msg = "%s=%f is not between %f and %f"
      
      match_context = MatchContext(self.pid)
      fixed_dme = FixedDataModelElement('s1', self.pid)
      match_element = fixed_dme.get_match_element("match", match_context)

      t = time()
      log_atom = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element), t, self)
      message = self.new_val % (self.match_s1, self.match_s2,
          repr(match_element.match_object))
      first = 0
      second = 0
      third = 0
      fourth = 0
      
      for _ in range(size):
        volatile_logarithmic_backoff_event_history = VolatileLogarithmicBackoffEventHistory(2)
        volatile_logarithmic_backoff_event_history.receive_event(self.test % self.__class__.__name__,
            message, [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)
        
        volatile_logarithmic_backoff_event_history.receive_event(self.test % self.__class__.__name__,
            message, [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)
        
        volatile_logarithmic_backoff_event_history.receive_event(self.test % self.__class__.__name__,
            message, [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)
        
        volatile_logarithmic_backoff_event_history.receive_event(self.test % self.__class__.__name__,
            message, [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)
        
        volatile_logarithmic_backoff_event_history.receive_event(self.test % self.__class__.__name__,
            message, [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)

        history = volatile_logarithmic_backoff_event_history.get_history()
        if history == [(0, self.test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None,
                       log_atom.get_parser_match(), self), (4, self.test % self.__class__.__name__, message,
                       [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)]:
          first += 1
        elif history == [(1, self.test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None,
                         log_atom.get_parser_match(), self), (4, self.test % self.__class__.__name__, message,
                         [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)]:
          second += 1
        elif history == [(2, self.test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None,
                         log_atom.get_parser_match(), self), (4, self.test % self.__class__.__name__, message,
                         [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)]:
          third += 1
        elif history == [(3, self.test % self.__class__.__name__, message, [log_atom.raw_data, log_atom.raw_data], None,
                         log_atom.get_parser_match(), self), (4, self.test % self.__class__.__name__, message,
                         [log_atom.raw_data, log_atom.raw_data], None, log_atom.get_parser_match(), self)]:
          fourth += 1
      val = 0.5*0.5*0.5
      minimum = size * val * (1 - deviation)
      maximum = size * val * (1 + deviation)
      self.assertTrue(minimum <= first <= maximum, msg % ("first", first, minimum, maximum))
      
      val = 0.5*0.5*0.5
      minimum = size * val * (1 - deviation)
      maximum = size * val * (1 + deviation)
      self.assertTrue(minimum <= second <= maximum, msg % ("second", second, minimum, maximum))
      
      val = 2*0.5*0.5*0.5
      minimum = size * val * (1 - deviation)
      maximum = size * val * (1 + deviation)
      self.assertTrue(minimum <= third <= maximum, msg % ("third", third, minimum, maximum))
       
      val = 0.5
      minimum = size * val * (1 - deviation)
      maximum = size * val * (1 + deviation)
      self.assertTrue(minimum <= fourth <= maximum, msg % ("fourth", fourth, minimum, maximum))


if __name__ == "__main__":
    unittest.main()
