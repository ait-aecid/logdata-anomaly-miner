import unittest
from aminer.parsing.DateTimeModelElement import DateTimeModelElement
from aminer.parsing.MatchContext import MatchContext
from unit.TestBase import TestBase, DummyMatchContext
import datetime


class DateTimeModelElementTest(TestBase):
    """Unittests for the DateTimeModelElement."""

    __expected_match_context = b": it still works"

    def test1get_id(self):
        """Test if get_id works properly."""
        dtme = DateTimeModelElement("s0", b"%d.%m.%Y %H:%M:%S")
        self.assertEqual(dtme.get_id(), "s0")

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        dtme = DateTimeModelElement("s0", b"%d.%m.%Y %H:%M:%S")
        self.assertEqual(dtme.get_child_elements(), None)

    def test3get_match_element_with_different_date_formats(self):
        """Test if different date_formats can be used to match data."""
        # test normal date
        match_context = DummyMatchContext(b'07.02.2019 11:40:00: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m.%Y %H:%M:%S')
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_string(), b'07.02.2019 11:40:00')
        self.assertEqual(match_context.match_data, b'07.02.2019 11:40:00')

        # test with only date defined
        match_context = DummyMatchContext(b'07.02.2019: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m.%Y')
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_string(), b'07.02.2019')
        self.assertEqual(match_context.match_data, b'07.02.2019')
        # TODO: add test where only time is defined without date.

    def test4wrong_date(self):
        """Test if wrong input data does not return a match."""

    def test5get_match_element_with_unclean_format_string(self):
        """This test case checks if unclean format_strings can be used."""
        # example "Date: 09.03.2021, Time: 10:02"

    def test6get_match_element_with_different_time_zones(self):
        """Test if different time_zones work with the DateTimeModelElement."""

    def test7get_match_element_with_different_text_locales(self):
        """Test if data with different text locales can be handled with different text_locale parameters."""

    def test8text_locale_not_installed(self):
        """Check if an exception is raised when the text_locale is not installed on the system."""

    def test9get_match_element_with_start_year(self):
        """Test if dates without year can be parsed, when the start_year is defined."""

    def test10get_match_element_without_start_year_defined(self):
        """Test if dates without year can still be parsed, even without defining the start_year."""

    def test11get_match_element_with_leap_start_year(self):
        """Check if leap start_years can parse the 29th February."""

    def test12get_match_element_without_leap_start_year(self):
        """Check if normal start_years can not parse the 29th February."""

    def test13learn_new_start_year_with_start_year_set(self):
        """Test if a new year is learned successfully with the start year being set."""

    def test14learn_new_start_year_without_start_year_set(self):
        """Test if a new year is learned successfully with the start year being None."""

    def test15max_time_jump_seconds_in_time(self):
        """Test if the max_time_jump_seconds parameter works if the next date is in time."""

    def test16max_time_jump_seconds_in_time_new_year(self):
        """Test if the max_time_jump_seconds parameter works if the next date is in time on new year."""

    def test17max_time_jump_seconds_exceeded(self):
        """Test if an exception is raised, when the next date exceeds the max_time_jump_seconds."""

    def test18time_change_cest_cet(self):
        """Check if the time change from CEST to CET and vice versa work as expected."""

    def test19unqualified_timestamp_year_wraparound(self):
        """Check if a warning is returned when an unqualified timestamp year wraparound occurs."""

    def test20time_inconsistencies(self):
        """Check if a warning is returned when a time inconsistency occurs."""

    def test21same_timestamp_multiple_times(self):
        """Test if the DateTimeModelElement can handle multiple same timestamps."""

    def test22date_before_unix_timestamps(self):
        """I don't know what happens if a date before the unix timestamp start is passed...????"""

    def test23path_id_input_validation(self):
        """Check if path_id is validated."""
        date_format = b"%d.%m.%Y %H:%M:%S"
        # empty element_id
        path_id = ""
        self.assertRaises(ValueError, DateTimeModelElement, path_id, date_format)

        # bytes element_id is not allowed
        path_id = b"path"
        self.assertRaises(ValueError, DateTimeModelElement, path_id, date_format)

        # integer element_id is not allowed
        path_id = 123
        self.assertRaises(ValueError, DateTimeModelElement, path_id, date_format)

        # float element_id is not allowed
        path_id = 123.22
        self.assertRaises(ValueError, DateTimeModelElement, path_id, date_format)

        # dict element_id is not allowed
        path_id = {"id": "path"}
        self.assertRaises(ValueError, DateTimeModelElement, path_id, date_format)

        # list element_id is not allowed
        path_id = ["path"]
        self.assertRaises(ValueError, DateTimeModelElement, path_id, date_format)

    def test24date_format_input_validation(self):
        """Check if date_format is validated and only valid values can be entered."""
        allowed_format_specifiers = b"bdfHMmSsYz%"
        # check if allowed values do not raise any exception.
        format_specifiers = b""
        for c in allowed_format_specifiers:
            format_specifiers += b"%" + str(chr(c)).encode()
            DateTimeModelElement("s0", b"%" + str(chr(c)).encode())
        # check if all allowed values can not be used together. An exception should be raised, because of multiple month representations
        # and %s with non-second formats.
        self.assertRaises(ValueError, DateTimeModelElement, "s0", format_specifiers)
        DateTimeModelElement("s0", format_specifiers.replace(b"%m", b"").replace(b"%s", b""))
        DateTimeModelElement("s0", format_specifiers.replace(b"%b", b"").replace(b"%s", b""))
        DateTimeModelElement("s0", b"%s%z%f")
        for c in allowed_format_specifiers.replace(b"s", b"").replace(b"z", b"").replace(b"f", b"").replace(b"%", b""):
            self.assertRaises(ValueError, DateTimeModelElement, "s0", b"%s%" + str(chr(c)).encode())

        # test non-existent specifiers
        for c in b"aceghijklnopqrtuvwxyABCDEFGIJKLNOPQRTUVWXZ":
            self.assertRaises(ValueError, DateTimeModelElement, "s0", b"%" + str(chr(c)).encode())

        # test multiple specifiers. % and z specifiers are allowed multiple times.
        DateTimeModelElement("s0", b"%%%z%z")
        for c in allowed_format_specifiers.replace(b"%", b"").replace(b"z", b""):
            self.assertRaises(ValueError, DateTimeModelElement, "s0", b"%" + str(chr(c)).encode() + b"%" + str(chr(c)).encode())



    def test25time_zone_input_validation(self):
        """Check if time_zone is validated and only valid values can be entered."""

    def test26text_locale_input_validation(self):
        """
        Check if text_locale is validated and only valid values can be entered.
        An exception has to be raised if the locale is not installed on the system.
        """

    def test27start_year_input_validation(self):
        """Check if start_year is validated."""

    def test28max_time_jump_seconds_input_validation(self):
        """Check if max_time_jump_seconds is validated."""






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
        date_time_model_element = DateTimeModelElement('path', b'%d.%m %H:%M:%S', datetime.timezone.utc, None, 2017)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486467600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)

        match_context = MatchContext(b'07.02 11:40:00 UTC+0000: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m %H:%M:%S %z', datetime.timezone.utc, None, 2017)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486467600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)
        match_context = MatchContext(b'07.02 11:40:00 UTC+0001: it still works')
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486471200)
        self.assertEqual(match_context.match_data, self.__expected_match_context)

        match_context = MatchContext(b'07.02 11:40:00 UTC+0000: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m %H:%M:%S %z', datetime.timezone.utc, None, 2017)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486467600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)
        match_context = MatchContext(b'07.02 11:40:00 UTC-0001: it still works')
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486464000)
        self.assertEqual(match_context.match_data, self.__expected_match_context)

        match_context = MatchContext(b'07.02 11:40:00 CET+1: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m %H:%M:%S %z', datetime.timezone.utc, None, 2017)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486467600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)
        match_context = MatchContext(b'07.02 11:40:00 CET+2: it still works')
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486471200)
        self.assertEqual(match_context.match_data, self.__expected_match_context)

        match_context = MatchContext(b'07/Feb:11:40:00 +0000] "GET /login.php HTTP/1.1" 200 2532 "-" "Mozilla/5.0 (X11; Ubuntu; '
                                     b'Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0')
        date_time_model_element = DateTimeModelElement('path', b'%d/%b:%H:%M:%S %z', datetime.timezone.utc, None, 2017)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486467600)
        self.assertEqual(match_context.match_data, b'] "GET /login.php HTTP/1.1" 200 2532 "-" "Mozilla/5.0 (X11; Ubuntu; '
                                                   b'Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0')

        match_context = MatchContext(b'07.02 11:40:00 UTC: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m %H:%M:%S %z', datetime.timezone.utc, None, 2017)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486467600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)

    def test3_new_year_with_start_year_value(self):
        """This test case checks if a new year is learned successfully with the start year being set."""
        start_year = 2017
        match_context = MatchContext(b'07.02.2018 11:40:00: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m.%Y %H:%M:%S', datetime.timezone.utc, None, start_year)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1518003600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)
        match_context = MatchContext(b'07.02.2018 11:40:00 UTC+0000: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m.%Y %H:%M:%S %z', datetime.timezone.utc, None, start_year)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1518003600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)
        match_context = MatchContext(b'07.02.2018 11:40:00 UTC+0001: it still works')
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1518007200)
        self.assertEqual(match_context.match_data, self.__expected_match_context)

        match_context = MatchContext(b'07.02.2018 11:40:00 UTC+0000: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m.%Y %H:%M:%S %z', datetime.timezone.utc, None, start_year)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1518003600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)
        match_context = MatchContext(b'07.02.2018 11:40:00 UTC-0001: it still works')
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1518000000)
        self.assertEqual(match_context.match_data, self.__expected_match_context)

        match_context = MatchContext(b'07.02.2018 11:40:00 CET+1: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m.%Y %H:%M:%S %z', datetime.timezone.utc, None, start_year)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1518003600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)
        match_context = MatchContext(b'07.02.2018 11:40:00 UTC+2: it still works')
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1518007200)
        self.assertEqual(match_context.match_data, self.__expected_match_context)

        match_context = MatchContext(b'07/Feb/2017:11:40:00 +0000] "GET /login.php HTTP/1.1" 200 2532 "-" "Mozilla/5.0 (X11; Ubuntu; '
                                     b'Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0')
        date_time_model_element = DateTimeModelElement('path', b'%d/%b/%Y:%H:%M:%S %z', datetime.timezone.utc, None, 2017)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1486467600)
        self.assertEqual(match_context.match_data, b'] "GET /login.php HTTP/1.1" 200 2532 "-" "Mozilla/5.0 (X11; Ubuntu; '
                                                   b'Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0')

        match_context = MatchContext(b'07.02.2018 11:40:00 UTC: it still works')
        date_time_model_element = DateTimeModelElement('path', b'%d.%m.%Y %H:%M:%S %z', datetime.timezone.utc, None, start_year)
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

    def test5_unclean_format_string(self):
        """This test case checks if unclean format_strings can be used."""
        match_context = MatchContext(b'Test 07.02.2018 11:40:00 UTC+0000: it still works')
        date_time_model_element = DateTimeModelElement('path', b'Test %d.%m.%Y %H:%M:%S %z', datetime.timezone.utc, None, 2017)
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1518003600)
        self.assertEqual(match_context.match_data, self.__expected_match_context)
        match_context = MatchContext(b'Test 07.02.2018 11:40:00 UTC-0001: it still works')
        self.assertEqual(date_time_model_element.get_match_element('match1', match_context).get_match_object(), 1518000000)
        self.assertEqual(match_context.match_data, self.__expected_match_context)


if __name__ == "__main__":
    unittest.main()
