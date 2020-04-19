import unittest
from aminer.parsing.DateTimeModelElement import DateTimeModelElement
from aminer.parsing.MatchContext import MatchContext
import datetime


class DateTimeModelElementTest(unittest.TestCase):

    '''
    This test case verifies, if all dateFormat qualifiers are valid 
    and exceptions are raised, if they are invalid.
    '''
    def test1date_formats_exceptions(self):
      self.match_context = MatchContext(b'07.02.2019 11:40:00: it still works')
      self.date_time_model_element = DateTimeModelElement('path', b'%d.%m.%Y %H:%M:%S')
      self.assertEqual(self.date_time_model_element.get_match_element('match1',
        self.match_context).get_match_string(), b'07.02.2019 11:40:00')
      
      self.assertRaises(Exception, DateTimeModelElement, 'path', b'%h %b')
      self.assertRaises(Exception, DateTimeModelElement, 'path', b'%H%H')
      self.assertRaises(Exception, DateTimeModelElement, 'path', b'%H%s')
    
    '''
    This test checks if they class is parsing dates without year values correctly.
    '''
    def test2start_year_value(self):
      self.match_context = MatchContext(b'07.02 11:40:00: it still works')
      self.date_time_model_element = DateTimeModelElement('path', b'%d.%m %H:%M:%S', None, None, 2017)
      self.assertEqual(self.date_time_model_element.get_match_element('match1',
        self.match_context).get_match_object(), 1486460400)
    
    def test3_new_year_with_start_year_value(self):
      self.startYear = 2017
      self.match_context = MatchContext(b'07.02.2018 11:40:00: it still works')
      self.date_time_model_element = DateTimeModelElement('path', b'%d.%m.%Y %H:%M:%S', None, None, self.startYear)
      self.assertEqual(self.date_time_model_element.get_match_element('match1',
        self.match_context).get_match_object(), 1517996400)
      
      self.match_context = MatchContext(b'07.02 11:40:00: it still works')
      self.date_time_model_element = DateTimeModelElement('path', b'%d.%m %H:%M:%S', None, None, self.startYear)
      self.assertEqual(self.date_time_model_element.get_match_element('match1',
        self.match_context).get_match_object(), 1486460400)

    '''
    This test case checks if the default Timezone is utc.
    '''
    def test4_default_timezone(self):
      self.match_context = MatchContext(b'07.02.2018 11:40:00')
      self.date_time_model_element = DateTimeModelElement('path', b'%d.%m.%Y %H:%M:%S', datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo)
      self.date1 = self.date_time_model_element.get_match_element('match1',
        self.match_context).get_match_object()
      
      self.match_context = MatchContext(b'07.02.2018 11:40:00')
      self.date_time_model_element = DateTimeModelElement('path', b'%d.%m.%Y %H:%M:%S')
      self.date2 = self.date_time_model_element.get_match_element('match1',
        self.match_context).get_match_object()
      self.assertEqual(self.date1 - self.date2, 0)


if __name__ == "__main__":
    unittest.main()