import unittest
from aminer.parsing.DateTimeModelElement import DateTimeModelElement
from aminer.parsing.MatchContext import MatchContext
import datetime


class DateTimeModelElementTest(unittest.TestCase):
    __expected_match_context = b': it still works'

    def test1date_formats_exceptions(self):
        """This test case verifies, if all date_format qualifiers are valid and exceptions are raised, if they are invalid."""
        match_context = MatchContext(b'07.02.2019 11:40:00: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m.%Y %H:%M:%S')
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_string(), b'07.02.2019 11:40:00')

        self.assertRaises(Exception, DateTimeModelElement, 'path', b'%h %b')
        self.assertRaises(Exception, DateTimeModelElement, 'path', b'%H%H')
        self.assertRaises(Exception, DateTimeModelElement, 'path', b'%H%s')

    def test2start_year_value(self):
        """This test checks if they class is parsing dates without year values correctly."""
        match_context = MatchContext(b'07.02 11:40:00: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m %H:%M:%S', None, None, 2017)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486467600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)

        match_context = MatchContext(b'07.02 11:40:00 UTC+0000: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m %H:%M:%S %z', None, None, 2017)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486467600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)
        match_context = MatchContext(b'07.02 11:40:00 UTC+0001: it still works')
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486471200)
        self.assertEqual(match_context.match_data, self.__expected_match_context)

        match_context = MatchContext(b'07.02 11:40:00 UTC+0000: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m %H:%M:%S %z', None, None, 2017)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486467600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)
        match_context = MatchContext(b'07.02 11:40:00 UTC-0001: it still works')
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486464000)
        self.assertEqual(match_context.match_data, self.__expected_match_context)

        match_context = MatchContext(b'07.02 11:40:00 CET+1: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m %H:%M:%S %z', None, None, 2017)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486467600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)
        match_context = MatchContext(b'07.02 11:40:00 CET+2: it still works')
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486471200)
        self.assertEqual(match_context.match_data, self.__expected_match_context)

        match_context = MatchContext(b'07/Feb:11:40:00 +0000] "GET /login.php HTTP/1.1" 200 2532 "-" "Mozilla/5.0 (X11; Ubuntu; '
                                     b'Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0')
        date_time_model_element = DateTimeModelElement('path', b'%d/%b:%H:%M:%S %z', None, None, 2017)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486467600)
        self.assertEqual(match_context.match_data, b'] "GET /login.php HTTP/1.1" 200 2532 "-" "Mozilla/5.0 (X11; Ubuntu; '
                                                   b'Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0')

        match_context = MatchContext(b'07.02 11:40:00 UTC: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m %H:%M:%S %z', None, None, 2017)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486467600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)

    def test3_new_year_with_start_year_value(self):
        startYear = 2017
        match_context = MatchContext(b'07.02.2018 11:40:00: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m.%Y %H:%M:%S', None, None, startYear)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1518003600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)
        match_context = MatchContext(b'07.02.2018 11:40:00 UTC+0000: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m.%Y %H:%M:%S %z', None, None, startYear)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1518003600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)
        match_context = MatchContext(b'07.02.2018 11:40:00 UTC+0001: it still works')
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1518007200)
        self.assertEqual(match_context.match_data, self.__expected_match_context)

        match_context = MatchContext(b'07.02.2018 11:40:00 UTC+0000: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m.%Y %H:%M:%S %z', None, None, startYear)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1518003600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)
        match_context = MatchContext(b'07.02.2018 11:40:00 UTC-0001: it still works')
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1518000000)
        self.assertEqual(match_context.match_data, self.__expected_match_context)

        match_context = MatchContext(b'07.02.2018 11:40:00 CET+1: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m.%Y %H:%M:%S %z', None, None, startYear)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1518003600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)
        match_context = MatchContext(b'07.02.2018 11:40:00 UTC+2: it still works')
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1518007200)
        self.assertEqual(match_context.match_data, self.__expected_match_context)

        match_context = MatchContext(b'07/Feb/2017:11:40:00 +0000] "GET /login.php HTTP/1.1" 200 2532 "-" "Mozilla/5.0 (X11; Ubuntu; '
                                     b'Linux x86_64; rv:730.0) Gecko/20100101 Firefox/73.0')
        date_time_model_element = DateTimeModelElement('path', b'%d/%b/%Y:%H:%M:%S %z', None, None, 2017)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486467600)
        self.assertEqual(match_context.match_data, b'] "GET /login.php HTTP/1.1" 200 2532 "-" "Mozilla/5.0 (X11; Ubuntu; '
                                                   b'Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0')

        match_context = MatchContext(b'07.02.2018 11:40:00 UTC: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m.%Y %H:%M:%S %z', None, None, startYear)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1518003600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)

    def test4_default_timezone(self):
        """This test case checks if the default Timezone is utc."""
        match_context = MatchContext(b'07.02.2018 11:40:00')
        date_time_model_element = DateTimeModelElement(
            'path', b'%d.%m.%Y %H:%M:%S', datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo)
        date1 = date_time_model_element.get_match_element('match1', match_context).get_match_object()
        self.assertEqual(match_context.match_data, b'')

        match_context = MatchContext(b'07.02.2018 11:40:00')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m.%Y %H:%M:%S')
        date2 = date_time_model_element.get_match_element('match1', match_context).get_match_object()
        self.assertEqual(match_context.match_data, b'')
        self.assertEqual(date1 - date2, 0)


if __name__ == "__main__":
    unittest.main()
