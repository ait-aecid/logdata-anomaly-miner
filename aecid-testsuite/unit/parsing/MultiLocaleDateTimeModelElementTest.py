import unittest
from aminer.parsing.MultiLocaleDateTimeModelElement import MultiLocaleDateTimeModelElement
from aminer.parsing.MatchContext import MatchContext
from datetime import datetime
import pytz


class MultiLocaleDateTimeModelElementTest(unittest.TestCase):
  tz_gmt10 = "Etc/GMT+10"
  en_gb_utf8 = "en_GB.utf8"
  de_at_utf8 = "de_AT.utf8"
  multi_locale_date_time_model_element = MultiLocaleDateTimeModelElement("multiLocale",
    [(b'%b %d', de_at_utf8, "Etc/GMT+10"), (b'%d %B %Y', en_gb_utf8, None),
     (b'%dth %B %Y', en_gb_utf8, None), (b'%d/%m/%Y', en_gb_utf8, None),
     (b'%m-%d-%Y', "en_US.utf8", None), (b'%d.%m. %H:%M:%S:%f', de_at_utf8, None),
     (b'%H:%M:%S:%f', de_at_utf8, None)])
  
  '''
  In this test case multiple date formats are used and different time formats create
  a MatchElement.
  '''
  def test1_multiple_normal_date_formats_matches_found(self):
    self.multi_locale_date_time_model_element.latest_parsed_timestamp = None
    #date without year and time
    string = b'Feb 25'
    match_context = MatchContext(string)
    match_element = self.multi_locale_date_time_model_element.get_match_element('match', match_context)
    date = datetime(datetime.now().year, 2, 25, tzinfo=pytz.timezone(self.tz_gmt10))
    #total_seconds should be in UTC, so the timezones are parsed out.
    total_seconds = (date-datetime(1970, 1, 1, tzinfo=date.tzinfo)).days*86400+date.utcoffset().total_seconds()
    self.compare_match(match_element, string, total_seconds)
    
    self.multi_locale_date_time_model_element.latest_parsed_timestamp = None
    #British date
    string = b'13 April 2019'
    match_context = MatchContext(string)
    match_element = self.multi_locale_date_time_model_element.get_match_element('match', match_context)
    date = datetime(2019, 4, 13, tzinfo=pytz.timezone('UTC'))
    #total_seconds should be in UTC, so the timezones are parsed out.
    total_seconds = (date-datetime(1970, 1, 1, tzinfo=date.tzinfo)).days*86400
    self.compare_match(match_element, string, total_seconds)
    
    #British date 2
    string = b'13th April 2019'
    match_context = MatchContext(string)
    match_element = self.multi_locale_date_time_model_element.get_match_element('match', match_context)
    self.compare_match(match_element, string, total_seconds)
    
    #British date 3
    string = b'13/04/2019'
    match_context = MatchContext(string)
    match_element = self.multi_locale_date_time_model_element.get_match_element('match', match_context)
    self.compare_match(match_element, string, total_seconds)
    
    #US date
    string = b'04-13-2019'
    match_context = MatchContext(string)
    match_element = self.multi_locale_date_time_model_element.get_match_element('match', match_context)
    self.compare_match(match_element, string, total_seconds)
    
    #Austrian date no year
    string = b'13.04. 15:12:54:201'
    match_context = MatchContext(string)
    match_element = self.multi_locale_date_time_model_element.get_match_element('match', match_context)
    date = datetime(2019, 4, 13, 15, 12, 54, 201, tzinfo=pytz.timezone('UTC'))
    #total_seconds should be in UTC, so the timezones are parsed out.
    delta = (date-datetime(1970, 1, 1, tzinfo=date.tzinfo))
    total_seconds = delta.days*86400+delta.seconds+delta.microseconds/1000
    self.compare_match(match_element, string, total_seconds)
    
    self.multi_locale_date_time_model_element.latest_parsed_timestamp = None
    #Austrian time no date
    string = b'15:12:54:201'
    match_context = MatchContext(string)
    match_element = self.multi_locale_date_time_model_element.get_match_element('match', match_context)
    date = datetime(datetime.now().year, 1, 1, 15, 12, 54, 201, tzinfo=pytz.timezone('UTC'))
    #total_seconds should be in UTC, so the timezones are parsed out.
    delta = (date-datetime(1970, 1, 1, tzinfo=date.tzinfo))
    total_seconds = delta.days*86400+delta.seconds+delta.microseconds/1000
    self.compare_match(match_element, string, total_seconds)
  
  '''
  In this test case multiple date formats are used and the MatchContext does not match
  with any of them.
  '''
  def test2_multiple_normal_date_formats_matches_not_found(self):
    self.multi_locale_date_time_model_element.latest_parsed_timestamp = None
    #British date
    string = b'13 Dezember 2019'
    match_context = MatchContext(string)
    match_element = self.multi_locale_date_time_model_element.get_match_element('match', match_context)
    self.assertEqual(match_element, None)
    
    #British date 3
    string = b'1/23/2019'
    match_context = MatchContext(string)
    self.assertEqual(None, self.multi_locale_date_time_model_element.get_match_element('match', match_context))
    
    #British date 3
    string = b'01/23/2019'
    match_context = MatchContext(string)
    self.assertRaises(ValueError, self.multi_locale_date_time_model_element.get_match_element, 'match', match_context)
    
    #Austrian date no year
    string = b'13.04.2019 15:12:54:201'
    match_context = MatchContext(string)
    match_element = self.multi_locale_date_time_model_element.get_match_element('match', match_context)
    self.assertEqual(match_element, None)

  '''
  In this test case wrong time formats at creation of the ModelElement are used.
  '''
  def test3_wrong_date_formats(self):
    #Unsupported Date format code
    self.assertRaises(Exception, MultiLocaleDateTimeModelElement, "multi", [(b'%c', self.de_at_utf8, None)])
    
    #Component defined twice
    self.assertRaises(Exception, MultiLocaleDateTimeModelElement, "multi", [(b'%b %b', self.de_at_utf8, None)])
  
  '''
  In this test case the checkTimestampValueInRange-method is tested.
  '''
  def test4_check_timestamp_value_in_range(self):
    self.multi_locale_date_time_model_element.latest_parsed_timestamp = None
    self.assertTrue(self.multi_locale_date_time_model_element.checkTimestampValueInRange(datetime.now(tz=pytz.timezone('UTC'))))
    self.multi_locale_date_time_model_element.latest_parsed_timestamp = datetime.now(tz=pytz.timezone('UTC'))
    self.assertTrue(self.multi_locale_date_time_model_element.checkTimestampValueInRange(datetime.now(tz=pytz.timezone('UTC'))))
  
  '''
  In this test case the occurrence of leap years is tested with multiple date formats.
  '''
  def test5_multiple_normal_date_formats_new_year(self):
    self.multi_locale_date_time_model_element.latest_parsed_timestamp = None
    #British date
    string = b'13 April 2019'
    match_context = MatchContext(string)
    match_element = self.multi_locale_date_time_model_element.get_match_element('match', match_context)
    date = datetime(2019, 4, 13, tzinfo=pytz.timezone('UTC'))
    #total_seconds should be in UTC, so the timezones are parsed out.
    total_seconds = (date-datetime(1970, 1, 1, tzinfo=date.tzinfo)).days*86400
    self.compare_match(match_element, string, total_seconds)
    
    string = b'13 April 2018'
    match_context = MatchContext(string)
    match_element = self.multi_locale_date_time_model_element.get_match_element('match', match_context)
    date = datetime(2019, 4, 13, tzinfo=pytz.timezone('UTC'))
    #total_seconds should be in UTC, so the timezones are parsed out.
    total_seconds = (date-datetime(1970, 1, 1, tzinfo=date.tzinfo)).days*86400
    self.compare_match(match_element, string, total_seconds)

    self.multi_locale_date_time_model_element.latest_parsed_timestamp = None
    date = datetime.now(tz=pytz.timezone('UTC'))
    self.assertTrue(self.multi_locale_date_time_model_element.checkTimestampValueInRange(date))
    self.multi_locale_date_time_model_element.latest_parsed_timestamp = datetime.now(tz=pytz.timezone('UTC'))
    date = datetime(date.year-1, date.month, date.day, tzinfo=pytz.timezone('UTC'))
    self.assertFalse(self.multi_locale_date_time_model_element.checkTimestampValueInRange(date))

  def compare_match(self, match_element, string, total_seconds):
    self.assertEqual(match_element.get_path(), 'match/multiLocale')
    self.assertEqual(match_element.get_match_string(), string)
    self.assertEqual(match_element.get_match_object(), total_seconds)
    self.assertEqual(match_element.get_children(), None)


if __name__ == "__main__":
    unittest.main()
