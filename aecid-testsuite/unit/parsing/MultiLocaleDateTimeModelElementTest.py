import unittest
from aminer.parsing.MultiLocaleDateTimeModelElement import MultiLocaleDateTimeModelElement
from aminer.parsing.MatchContext import MatchContext
from unit.TestBase import TestBase, DummyMatchContext, initialize_loggers
from datetime import datetime, timezone
import pytz
####
from aminer.parsing.DateTimeModelElement import DateTimeModelElement
import locale
from io import StringIO
import logging
from pwd import getpwnam
from grp import getgrnam
####


class MultiLocaleDateTimeModelElementTest(TestBase):
    """Unittests for the MultiLocaleDateTimeModelElement."""

    def test1get_id(self):
        """Test if get_id works properly."""
        multi_dtme = MultiLocaleDateTimeModelElement("s0", [(b"%d.%m.%Y %H:%M:%S", None, None)])
        self.assertEqual(multi_dtme.get_id(), "s0")

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        multi_dtme = MultiLocaleDateTimeModelElement("s0", [(b"%d.%m.%Y %H:%M:%S", None, None)])
        self.assertEqual(multi_dtme.get_child_elements(), None)

    def test3get_match_element_with_different_date_formats(self):
        """Test if different date_formats can be used to match data."""
        tz_gmt10 = pytz.timezone("Etc/GMT+10")
        en_gb_utf8 = "en_GB.utf8"
        en_us_utf8 = "en_US.utf8"
        de_at_utf8 = "de_AT.utf8"
        multi_locale_dtme = MultiLocaleDateTimeModelElement("path", [
            (b"%d.%m.%Y %H:%M:%S", None, None), (b"%d.%m.%YT%H:%M:%S", None, None), (b"%d.%m.%Y %H:%M:%S.%f", None, None),
            (b"%d.%m.%Y %H:%M:%S%z", None, None), (b"%d.%m.%Y", None, None), (b"%H:%M:%S", None, None), (b"%b %d", tz_gmt10, de_at_utf8),
            (b"%d %B %Y", None, en_gb_utf8), (b"%dth %B %Y", None, en_gb_utf8), (b"%d/%m/%Y", None, en_gb_utf8),
            (b"%m-%d-%Y", None, en_us_utf8), (b"%d.%m. %H:%M:%S:%f", None, de_at_utf8), (b"%H:%M:%S:%f", None, de_at_utf8)])

        # test normal date
        match_context = DummyMatchContext(b"07.02.2019 11:40:00: it still works")
        match_element = multi_locale_dtme.get_match_element("match1", match_context)
        self.assertEqual(match_element.match_string, b"07.02.2019 11:40:00")
        self.assertEqual(match_element.match_object, 1549539600)
        self.assertEqual(match_context.match_string, b"07.02.2019 11:40:00")

        # test leap year date
        match_context = DummyMatchContext(b"29.02.2020 11:40:00: it still works")
        match_element = multi_locale_dtme.get_match_element("match1", match_context)
        self.assertEqual(match_element.match_string, b"29.02.2020 11:40:00")
        self.assertEqual(match_element.match_object, 1582976400)
        self.assertEqual(match_context.match_string, b"29.02.2020 11:40:00")

        # test normal date with T
        match_context = DummyMatchContext(b"07.02.2019T11:40:00: it still works")
        match_element = multi_locale_dtme.get_match_element("match1", match_context)
        self.assertEqual(match_element.match_string, b"07.02.2019T11:40:00")
        self.assertEqual(match_element.match_object, 1549539600)
        self.assertEqual(match_context.match_string, b"07.02.2019T11:40:00")

        # test normal date with fractions
        match_context = DummyMatchContext(b"07.02.2019 11:40:00.123456: it still works")
        match_element = multi_locale_dtme.get_match_element("match1", match_context)
        self.assertEqual(match_element.match_string, b"07.02.2019 11:40:00.123456")
        self.assertEqual(match_element.match_object, 1549539600.123456)
        self.assertEqual(match_context.match_string, b"07.02.2019 11:40:00.123456")

        # test normal date with z
        match_context = DummyMatchContext(b"07.02.2019 11:40:00+0000: it still works")
        match_element = multi_locale_dtme.get_match_element("match1", match_context)
        self.assertEqual(match_element.match_string, b"07.02.2019 11:40:00+0000")
        self.assertEqual(match_element.match_object, 1549539600)
        self.assertEqual(match_context.match_string, b"07.02.2019 11:40:00+0000")

        match_context = DummyMatchContext(b"07.02.2019 11:40:00: it still works")
        match_element = multi_locale_dtme.get_match_element("match1", match_context)
        self.assertEqual(match_element.match_string, b"07.02.2019 11:40:00")
        self.assertEqual(match_element.match_object, 1549539600)
        self.assertEqual(match_context.match_string, b"07.02.2019 11:40:00")

        # test with only date defined
        match_context = DummyMatchContext(b"07.02.2019: it still works")
        match_element = multi_locale_dtme.get_match_element("match1", match_context)
        self.assertEqual(match_element.match_string, b"07.02.2019")
        self.assertEqual(match_element.match_object, 1549497600)
        self.assertEqual(match_context.match_string, b"07.02.2019")

        # test with only time defined. Here obviously the seconds can not be tested.
        match_context = DummyMatchContext(b"11:40:23: it still works")
        match_element = multi_locale_dtme.get_match_element("match1", match_context)
        self.assertEqual(match_element.match_string, b"11:40:23")
        self.assertEqual(match_context.match_string, b"11:40:23")

        string = b"Feb 25"
        match_context = MatchContext(string)
        match_element = multi_locale_dtme.get_match_element("match", match_context)
        date = datetime(datetime.now().year, 2, 25, tzinfo=pytz.timezone(self.tz_gmt10))
        # total_seconds should be in UTC, so the timezones are parsed out.
        total_seconds = (date - datetime(1970, 1, 1, tzinfo=date.tzinfo)).days * 86400 + date.utcoffset().total_seconds()
        self.assertEqual(match_element.match_string, b"Feb 25")
        self.assertEqual(match_element.match_object, total_seconds)
        self.assertEqual(match_context.match_string, b"Feb 25")

        multi_locale_dtme.latest_parsed_timestamp = None
        # British date
        string = b"13 April 2019"
        match_context = MatchContext(string)
        match_element = multi_locale_dtme.get_match_element("match", match_context)
        self.assertEqual(match_element.match_string, b"13 April 2019")
        self.assertEqual(match_element.match_object, 1555113600)
        self.assertEqual(match_context.match_string, b"13 April 2019")

        # British date 2
        string = b"13th April 2019"
        match_context = MatchContext(string)
        match_element = multi_locale_dtme.get_match_element("match", match_context)
        self.assertEqual(match_element.match_string, b"13th April 2019")
        self.assertEqual(match_element.match_object, 1555113600)
        self.assertEqual(match_context.match_string, b"13th April 2019")

        # British date 3
        string = b"13/04/2019"
        match_context = MatchContext(string)
        match_element = multi_locale_dtme.get_match_element("match", match_context)
        self.assertEqual(match_element.match_string, b"13/04/2019")
        self.assertEqual(match_element.match_object, 1555113600)
        self.assertEqual(match_context.match_string, b"13/04/2019")

        # US date
        string = b"04-13-2019"
        match_context = MatchContext(string)
        match_element = multi_locale_dtme.get_match_element("match", match_context)
        self.assertEqual(match_element.match_string, b"04-13-2019")
        self.assertEqual(match_element.match_object, 1555113600)
        self.assertEqual(match_context.match_string, b"04-13-2019")

        # Austrian date no year - year should already be learnt.
        string = b"13.04. 15:12:54:201"
        match_context = MatchContext(string)
        match_element = multi_locale_dtme.get_match_element("match", match_context)
        self.assertEqual(match_element.match_string, b"13.04. 15:12:54:201")
        self.assertEqual(match_element.match_object, 1555168374.201)
        self.assertEqual(match_context.match_string, b"13.04. 15:12:54:201")

        multi_locale_dtme.latest_parsed_timestamp = None
        # Austrian time no date
        string = b"15:12:54:201"
        match_context = MatchContext(string)
        match_element = multi_locale_dtme.get_match_element("match", match_context)
        date = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 15, 12, 54, 201, tzinfo=timezone.utc)
        # total_seconds should be in UTC, so the timezones are parsed out.
        delta = (date - datetime(1970, 1, 1, tzinfo=date.tzinfo))
        total_seconds = delta.days * 86400 + delta.seconds + delta.microseconds / 1000
        self.assertEqual(match_element.match_string, b"15:12:54:201")
        self.assertEqual(match_element.match_object, total_seconds)
        self.assertEqual(match_context.match_string, b"15:12:54:201")

    def test4wrong_date(self):
        """Test if wrong input data does not return a match."""
        # wrong day
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S", timezone.utc)
        match_context = DummyMatchContext(b"32.03.2019 11:40:00: it still works")
        self.assertIsNone(date_time_model_element.get_match_element("match1", match_context))
        self.assertEqual(match_context.match_data, b"32.03.2019 11:40:00: it still works")
        self.assertEqual(match_context.match_string, b"")

        # wrong month
        match_context = DummyMatchContext(b"01.13.2019 11:40:00: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S", timezone.utc)
        self.assertIsNone(date_time_model_element.get_match_element("match1", match_context))
        self.assertEqual(match_context.match_data, b"01.13.2019 11:40:00: it still works")
        self.assertEqual(match_context.match_string, b"")

        # wrong year
        match_context = DummyMatchContext(b"01.01.00 11:40:00: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S", timezone.utc)
        self.assertIsNone(date_time_model_element.get_match_element("match1", match_context))
        self.assertEqual(match_context.match_data, b"01.01.00 11:40:00: it still works")
        self.assertEqual(match_context.match_string, b"")

        # wrong date leap year
        match_context = DummyMatchContext(b"29.02.2019 11:40:00: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S", timezone.utc)
        self.assertIsNone(date_time_model_element.get_match_element("match1", match_context))
        self.assertEqual(match_context.match_data, b"29.02.2019 11:40:00: it still works")
        self.assertEqual(match_context.match_string, b"")

        # missing T
        match_context = DummyMatchContext(b"07.02.2019 11:40:00: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%YT%H:%M:%S", timezone.utc)
        self.assertIsNone(date_time_model_element.get_match_element("match1", match_context))
        self.assertEqual(match_context.match_data, b"07.02.2019 11:40:00: it still works")
        self.assertEqual(match_context.match_string, b"")

        # missing fractions
        match_context = DummyMatchContext(b"07.02.2019 11:40:00.: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S.%f", timezone.utc)
        self.assertIsNone(date_time_model_element.get_match_element("match1", match_context))
        self.assertEqual(match_context.match_data, b"07.02.2019 11:40:00.: it still works")
        self.assertEqual(match_context.match_string, b"")

    def test5get_match_element_with_unclean_format_string(self):
        """This test case checks if unclean format_strings can be used."""
        # example "Date: 09.03.2021, Time: 10:02"
        match_context = DummyMatchContext(b"Date %d: 07.02.2018 11:40:00 UTC+0000: it still works")
        date_time_model_element = DateTimeModelElement("path", b"Date %%d: %d.%m.%Y %H:%M:%S%z", timezone.utc)
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1518003600)
        self.assertEqual(match_context.match_string, b"Date %d: 07.02.2018 11:40:00 UTC+0000")

    def test6get_match_element_with_different_time_zones(self):
        """Test if different time_zones work with the DateTimeModelElement."""
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S%z", timezone.utc)
        match_context = DummyMatchContext(b"07.02.2018 11:40:00 UTC-1200: it still works")
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1518046800)
        self.assertEqual(match_context.match_string, b"07.02.2018 11:40:00 UTC-1200")

        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S%z", timezone.utc)
        match_context = DummyMatchContext(b"07.02.2018 11:40:00 UTC-12: it still works")
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1518046800)
        self.assertEqual(match_context.match_string, b"07.02.2018 11:40:00 UTC-12")

        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S%z", timezone.utc)
        match_context = DummyMatchContext(b"07.02.2018 11:40:00 UTC-5: it still works")
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1518021600)
        self.assertEqual(match_context.match_string, b"07.02.2018 11:40:00 UTC-5")

        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S%z", timezone.utc)
        match_context = DummyMatchContext(b"07.02.2018 11:40:00 UTC-0500: it still works")
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1518021600)
        self.assertEqual(match_context.match_string, b"07.02.2018 11:40:00 UTC-0500")

        match_context = DummyMatchContext(b"07.02.2018 11:40:00 UTC+0000: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S%z", timezone.utc)
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1518003600)
        self.assertEqual(match_context.match_string, b"07.02.2018 11:40:00 UTC+0000")

        match_context = DummyMatchContext(b"07.02.2018 11:40:00 UTC+0100: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S%z", timezone.utc)
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1518000000)
        self.assertEqual(match_context.match_string, b"07.02.2018 11:40:00 UTC+0100")

        match_context = DummyMatchContext(b"07.02.2018 11:40:00 UTC+1400: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S%z", timezone.utc)
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1517953200)
        self.assertEqual(match_context.match_string, b"07.02.2018 11:40:00 UTC+1400")

    def test7get_match_element_with_different_text_locales(self):
        """Test if data with different text locales can be handled with different text_locale parameters."""
        installed = False
        try:
            self.assertEqual("de_AT.UTF-8", locale.setlocale(locale.LC_TIME, "de_AT.UTF-8"))
            installed = True
        except locale.Error:
            pass
        DateTimeModelElement("path", b"%d.%m %H:%M:%S", timezone.utc, "en_US.UTF-8")
        if installed:
            DateTimeModelElement("path", b"%d.%m %H:%M:%S", timezone.utc, "de_AT.UTF-8")

    def test8text_locale_not_installed(self):
        """Check if an exception is raised when the text_locale is not installed on the system."""
        self.assertRaises(locale.Error, DateTimeModelElement, "path", b"%d.%m %H:%M:%S", timezone.utc, "af-ZA.UTF-8")

    def test9get_match_element_with_start_year(self):
        """Test if dates without year can be parsed, when the start_year is defined."""
        match_context = DummyMatchContext(b"07.02 11:40:00: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m %H:%M:%S", timezone.utc, start_year=2017)
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1486467600)
        self.assertEqual(match_context.match_string, b"07.02 11:40:00")

        match_context = DummyMatchContext(b"07.02 11:40:00: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m %H:%M:%S", timezone.utc, start_year=2019)
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1549539600)
        self.assertEqual(match_context.match_string, b"07.02 11:40:00")

    def test10get_match_element_without_start_year_defined(self):
        """Test if dates without year can still be parsed, even without defining the start_year."""
        match_context = DummyMatchContext(b"07.02 11:40:00: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m %H:%M:%S", timezone.utc)
        self.assertIsNotNone(date_time_model_element.get_match_element("match1", match_context))
        self.assertEqual(match_context.match_string, b"07.02 11:40:00")

    def test11get_match_element_with_leap_start_year(self):
        """Check if leap start_years can parse the 29th February."""
        match_context = DummyMatchContext(b"29.02 11:40:00: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m %H:%M:%S", timezone.utc, start_year=2020)
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1582976400)
        self.assertEqual(match_context.match_string, b"29.02 11:40:00")

    def test12get_match_element_without_leap_start_year(self):
        """Check if normal start_years can not parse the 29th February."""
        match_context = DummyMatchContext(b"29.02 11:40:00: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m %H:%M:%S", timezone.utc, start_year=2019)
        self.assertIsNone(date_time_model_element.get_match_element("match1", match_context))

    def test13learn_new_start_year_with_start_year_set(self):
        """Test if a new year is learned successfully with the start year being set."""
        start_year = 2020
        match_context = DummyMatchContext(b"31.12 23:59:00: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m %H:%M:%S", timezone.utc, start_year=start_year)
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1609459140)
        self.assertEqual(match_context.match_string, b"31.12 23:59:00")
        self.assertEqual(date_time_model_element.start_year, start_year)

        match_context = DummyMatchContext(b"01.01 11:20:00: it still works")
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1609500000)
        self.assertEqual(match_context.match_string, b"01.01 11:20:00")
        self.assertEqual(date_time_model_element.start_year, start_year + 1)

    def test14learn_new_start_year_without_start_year_set(self):
        """Test if a new year is learned successfully with the start year being None."""
        match_context = DummyMatchContext(b"31.12 23:59:00: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m %H:%M:%S", timezone.utc)
        self.assertIsNotNone(date_time_model_element.get_match_element("match1", match_context))
        self.assertEqual(match_context.match_string, b"31.12 23:59:00")

        start_year = date_time_model_element.start_year
        match_context = DummyMatchContext(b"01.01 11:20:00: it still works")
        self.assertIsNotNone(date_time_model_element.get_match_element("match1", match_context))
        self.assertEqual(match_context.match_string, b"01.01 11:20:00")
        self.assertEqual(date_time_model_element.start_year, start_year + 1)

    def test15max_time_jump_seconds_in_time(self):
        """
        Test if the max_time_jump_seconds parameter works if the next date is in time.
        Warnings with unqualified timestamp year wraparound.
        """
        log_stream = StringIO()
        logging.basicConfig(stream=log_stream, level=logging.INFO)
        max_time_jump_seconds = 86400
        start_year = 2020
        match_context = DummyMatchContext(b"31.12 23:59:00: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m %H:%M:%S", timezone.utc, start_year=start_year,
            max_time_jump_seconds=max_time_jump_seconds)
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1609459140)
        self.assertEqual(match_context.match_string, b"31.12 23:59:00")
        self.assertEqual(date_time_model_element.start_year, 2020)

        match_context = DummyMatchContext(b"01.01 23:59:00: it still works")
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1609545540)
        self.assertEqual(match_context.match_string, b"01.01 23:59:00")
        self.assertEqual(date_time_model_element.start_year, 2021)
        self.assertIn("WARNING:DEBUG:DateTimeModelElement unqualified timestamp year wraparound detected from 2021-01-01T23:59:00+00:00 to "
                      "2021-01-01T23:59:00+00:00", log_stream.getvalue())
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        initialize_loggers(self.aminer_config, getpwnam("aminer").pw_uid, getgrnam("aminer").gr_gid)

    def test16max_time_jump_seconds_exceeded(self):
        """
        Test if the start_year is not updated, when the next date exceeds the max_time_jump_seconds.
        A time inconsistency warning must occur.
        """
        log_stream = StringIO()
        logging.basicConfig(stream=log_stream, level=logging.INFO)
        max_time_jump_seconds = 86400
        start_year = 2020
        match_context = DummyMatchContext(b"31.12 23:59:00: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m %H:%M:%S", timezone.utc, start_year=start_year,
            max_time_jump_seconds=max_time_jump_seconds)
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1609459140)
        self.assertEqual(match_context.match_string, b"31.12 23:59:00")
        self.assertEqual(date_time_model_element.start_year, 2020)
        match_context = DummyMatchContext(b"01.01 23:59:01: it still works")
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1577923141)
        self.assertEqual(match_context.match_string, b"01.01 23:59:01")
        self.assertEqual(date_time_model_element.start_year, 2020)
        self.assertIn("WARNING:DEBUG:DateTimeModelElement time inconsistencies parsing b'01.01 23:59:01', expecting value around "
                      "1609459140. Check your settings!", log_stream.getvalue())
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        initialize_loggers(self.aminer_config, getpwnam("aminer").pw_uid, getgrnam("aminer").gr_gid)

    def test17time_change_cest_cet(self):
        """Check if the time change from CET to CEST and vice versa work as expected."""
        match_context = DummyMatchContext(b"24.03.2018 11:40:00 CET: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S%z", timezone.utc)
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1521888000)
        self.assertEqual(match_context.match_string, b"24.03.2018 11:40:00 CET")

        match_context = DummyMatchContext(b"25.03.2018 11:40:00 CEST: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S%z", timezone.utc)
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1521970800)
        self.assertEqual(match_context.match_string, b"25.03.2018 11:40:00 CEST")

        match_context = DummyMatchContext(b"27.10.2018 11:40:00 CEST: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S%z", timezone.utc)
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1540633200)
        self.assertEqual(match_context.match_string, b"27.10.2018 11:40:00 CEST")

        match_context = DummyMatchContext(b"28.10.2018 11:40:00 CET: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S%z", timezone.utc)
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1540723200)
        self.assertEqual(match_context.match_string, b"28.10.2018 11:40:00 CET")

        match_context = DummyMatchContext(b"27.10.2018 11:40:00 EST: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S%z", timezone.utc)
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1540658400)
        self.assertEqual(match_context.match_string, b"27.10.2018 11:40:00 EST")

        match_context = DummyMatchContext(b"27.10.2018 11:40:00 PDT: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S%z", timezone.utc)
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1540665600)
        self.assertEqual(match_context.match_string, b"27.10.2018 11:40:00 PDT")

        match_context = DummyMatchContext(b"27.10.2018 11:40:00 GMT: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S%z", timezone.utc)
        self.assertEqual(date_time_model_element.get_match_element("match1", match_context).get_match_object(), 1540640400)
        self.assertEqual(match_context.match_string, b"27.10.2018 11:40:00 GMT")

    def test18same_timestamp_multiple_times(self):
        """Test if the DateTimeModelElement can handle multiple same timestamps."""
        match_context = DummyMatchContext(b"07.02.2019 11:40:00: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S", timezone.utc)
        match_element = date_time_model_element.get_match_element("match1", match_context)
        self.assertEqual(match_element.match_string, b"07.02.2019 11:40:00")
        self.assertEqual(match_element.match_object, 1549539600)
        self.assertEqual(match_context.match_string, b"07.02.2019 11:40:00")

        match_context = DummyMatchContext(b"07.02.2019 11:40:00: it still works")
        match_element = date_time_model_element.get_match_element("match1", match_context)
        self.assertEqual(match_element.match_string, b"07.02.2019 11:40:00")
        self.assertEqual(match_element.match_object, 1549539600)
        self.assertEqual(match_context.match_string, b"07.02.2019 11:40:00")

    def test19date_before_unix_timestamps(self):
        """Check if timestamps before the unix timestamp are processed properly."""
        match_context = DummyMatchContext(b"01.01.1900 11:40:00: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S", timezone.utc)
        match_element = date_time_model_element.get_match_element("match1", match_context)
        self.assertEqual(match_element.match_string, b"01.01.1900 11:40:00")
        self.assertEqual(match_element.match_object, -2208946800)

    def test20path_id_input_validation(self):
        """Check if path_id is validated."""
        date_format = b"%d.%m.%Y %H:%M:%S"
        # empty element_id
        path_id = ""
        self.assertRaises(ValueError, DateTimeModelElement, path_id, date_format)

        # bytes element_id is not allowed
        path_id = b"path"
        self.assertRaises(TypeError, DateTimeModelElement, path_id, date_format)

        # integer element_id is not allowed
        path_id = 123
        self.assertRaises(TypeError, DateTimeModelElement, path_id, date_format)

        # float element_id is not allowed
        path_id = 123.22
        self.assertRaises(TypeError, DateTimeModelElement, path_id, date_format)

        # dict element_id is not allowed
        path_id = {"id": "path"}
        self.assertRaises(TypeError, DateTimeModelElement, path_id, date_format)

        # list element_id is not allowed
        path_id = ["path"]
        self.assertRaises(TypeError, DateTimeModelElement, path_id, date_format)

    def test21date_format_input_validation(self):
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

    def test22time_zone_input_validation(self):
        """Check if time_zone is validated and only valid values can be entered."""
        dtme = DateTimeModelElement("s0", b"%d.%m.%Y %H:%M:%S")
        self.assertEqual(dtme.time_zone, timezone.utc)
        DateTimeModelElement("s0", b"%d.%m.%Y %H:%M:%S", timezone.utc)
        for tz in pytz.all_timezones:
            DateTimeModelElement("s0", b"%d.%m.%Y %H:%M:%S", pytz.timezone(tz))

        self.assertRaises(TypeError, DateTimeModelElement, "s0", b"%d.%m.%Y %H:%M:%S", "UTC")
        self.assertRaises(TypeError, DateTimeModelElement, "s0", b"%d.%m.%Y %H:%M:%S", 1)
        self.assertRaises(TypeError, DateTimeModelElement, "s0", b"%d.%m.%Y %H:%M:%S", 1.25)
        self.assertRaises(TypeError, DateTimeModelElement, "s0", b"%d.%m.%Y %H:%M:%S", True)
        self.assertRaises(TypeError, DateTimeModelElement, "s0", b"%d.%m.%Y %H:%M:%S", {"time_zone": timezone.utc})

    def test23text_locale_input_validation(self):
        """
        Check if text_locale is validated and only valid values can be entered.
        An exception has to be raised if the locale is not installed on the system.
        """
        DateTimeModelElement("path", b"%d.%m %H:%M:%S", timezone.utc, "en_US.UTF-8")
        DateTimeModelElement("path", b"%d.%m %H:%M:%S", timezone.utc, ("en_US", "UTF-8"))
        self.assertRaises(TypeError, DateTimeModelElement, "path", b"%d.%m %H:%M:%S", timezone.utc, 1)
        self.assertRaises(TypeError, DateTimeModelElement, "path", b"%d.%m %H:%M:%S", timezone.utc, 1.2)
        self.assertRaises(TypeError, DateTimeModelElement, "path", b"%d.%m %H:%M:%S", timezone.utc, ["en_US", "UTF-8"])
        self.assertRaises(TypeError, DateTimeModelElement, "path", b"%d.%m %H:%M:%S", timezone.utc, {"en_US": "UTF-8"})

    def test24start_year_input_validation(self):
        """Check if start_year is validated."""
        dtme = DateTimeModelElement("s0", b"%d.%m %H:%M:%S", timezone.utc, None, None)
        self.assertEqual(dtme.start_year, datetime.now().year)
        DateTimeModelElement("s0", b"%d.%m.%Y %H:%M:%S", timezone.utc, None, 2020)
        DateTimeModelElement("s0", b"%d.%m.%Y %H:%M:%S", timezone.utc, None, -630)
        self.assertRaises(TypeError, DateTimeModelElement, "s0", b"%d.%m.%Y %H:%M:%S", timezone.utc, None, "2020")
        self.assertRaises(TypeError, DateTimeModelElement, "s0", b"%d.%m.%Y %H:%M:%S", timezone.utc, None, True)
        self.assertRaises(TypeError, DateTimeModelElement, "s0", b"%d.%m.%Y %H:%M:%S", timezone.utc, None, 1.25)
        self.assertRaises(TypeError, DateTimeModelElement, "s0", b"%d.%m.%Y %H:%M:%S", timezone.utc, None, {"key": 2020})

    def test25max_time_jump_seconds_input_validation(self):
        """Check if max_time_jump_seconds is validated."""
        dtme = DateTimeModelElement("s0", b"%d.%m %H:%M:%S", timezone.utc, None, None)
        self.assertEqual(dtme.max_time_jump_seconds, 86400)
        DateTimeModelElement("s0", b"%d.%m.%Y %H:%M:%S", timezone.utc, None, None, 100000)
        self.assertRaises(ValueError, DateTimeModelElement, "s0", b"%d.%m.%Y %H:%M:%S", timezone.utc, None, None, -1)
        self.assertRaises(ValueError, DateTimeModelElement, "s0", b"%d.%m.%Y %H:%M:%S", timezone.utc, None, None, 0)
        self.assertRaises(TypeError, DateTimeModelElement, "s0", b"%d.%m.%Y %H:%M:%S", timezone.utc, None, None, "100000")
        self.assertRaises(TypeError, DateTimeModelElement, "s0", b"%d.%m.%Y %H:%M:%S", timezone.utc, None, None, True)
        self.assertRaises(TypeError, DateTimeModelElement, "s0", b"%d.%m.%Y %H:%M:%S", timezone.utc, None, None, 1.25)
        self.assertRaises(TypeError, DateTimeModelElement, "s0", b"%d.%m.%Y %H:%M:%S", timezone.utc, None, None, {"key": 2020})

    tz_gmt10 = "Etc/GMT+10"
    en_gb_utf8 = "en_GB.utf8"
    de_at_utf8 = "de_AT.utf8"
    multi_locale_date_time_model_element = MultiLocaleDateTimeModelElement("multiLocale",
        [(b"%b %d", de_at_utf8, "Etc/GMT+10"), (b"%d %B %Y", en_gb_utf8, None), (b"%dth %B %Y", en_gb_utf8, None),
            (b"%d/%m/%Y", en_gb_utf8, None), (b"%m-%d-%Y", "en_US.utf8", None), (b"%d.%m. %H:%M:%S:%f", de_at_utf8, None),
            (b"%H:%M:%S:%f", de_at_utf8, None)])

    def test2_multiple_normal_date_formats_matches_not_found(self):
        """In this test case multiple date formats are used and the MatchContext does not match with any of them."""
        self.multi_locale_date_time_model_element.latest_parsed_timestamp = None
        # British date
        string = b"13 Dezember 2019"
        match_context = MatchContext(string)
        match_element = self.multi_locale_date_time_model_element.get_match_element("match", match_context)
        self.assertEqual(match_element, None)

        # British date 3
        string = b"1/23/2019"
        match_context = MatchContext(string)
        self.assertEqual(None, self.multi_locale_date_time_model_element.get_match_element("match", match_context))

        # British date 3
        string = b"01/23/2019"
        match_context = MatchContext(string)
        self.assertRaises(ValueError, self.multi_locale_date_time_model_element.get_match_element, "match", match_context)

        # Austrian date no year
        string = b"13.04.2019 15:12:54:201"
        match_context = MatchContext(string)
        match_element = self.multi_locale_date_time_model_element.get_match_element("match", match_context)
        self.assertEqual(match_element, None)

    def test3_wrong_date_formats(self):
        """In this test case wrong time formats at creation of the ModelElement are used."""
        # Unsupported Date format code
        self.assertRaises(Exception, MultiLocaleDateTimeModelElement, "multi", [(b"%c", self.de_at_utf8, None)])

        # Component defined twice
        self.assertRaises(Exception, MultiLocaleDateTimeModelElement, "multi", [(b"%b %b", self.de_at_utf8, None)])

    def test4_check_timestamp_value_in_range(self):
        """In this test case the check_timestamp_value_in_range-method is tested."""
        self.multi_locale_date_time_model_element.latest_parsed_timestamp = None
        self.assertTrue(self.multi_locale_date_time_model_element.check_timestamp_value_in_range(datetime.now(tz=timezone.utc)))
        self.multi_locale_date_time_model_element.latest_parsed_timestamp = datetime.now(tz=timezone.utc)
        self.assertTrue(self.multi_locale_date_time_model_element.check_timestamp_value_in_range(datetime.now(tz=timezone.utc)))

    def test5_multiple_normal_date_formats_new_year(self):
        """In this test case the occurrence of leap years is tested with multiple date formats."""
        self.multi_locale_date_time_model_element.latest_parsed_timestamp = None
        # British date
        string = b"13 April 2019"
        match_context = MatchContext(string)
        match_element = self.multi_locale_date_time_model_element.get_match_element("match", match_context)
        date = datetime(2019, 4, 13, tzinfo=timezone.utc)
        # total_seconds should be in UTC, so the timezones are parsed out.
        total_seconds = (date - datetime(1970, 1, 1, tzinfo=date.tzinfo)).days * 86400
        self.compare_match(match_element, string, total_seconds)

        string = b"13 April 2018"
        match_context = MatchContext(string)
        match_element = self.multi_locale_date_time_model_element.get_match_element("match", match_context)
        date = datetime(2019, 4, 13, tzinfo=timezone.utc)
        # total_seconds should be in UTC, so the timezones are parsed out.
        total_seconds = (date - datetime(1970, 1, 1, tzinfo=date.tzinfo)).days * 86400
        self.compare_match(match_element, string, total_seconds)

        self.multi_locale_date_time_model_element.latest_parsed_timestamp = None
        date = datetime.now(tz=timezone.utc)
        self.assertTrue(self.multi_locale_date_time_model_element.check_timestamp_value_in_range(date))
        self.multi_locale_date_time_model_element.latest_parsed_timestamp = datetime.now(tz=timezone.utc)
        date = datetime(date.year - 1, date.month, date.day, tzinfo=timezone.utc)
        self.assertFalse(self.multi_locale_date_time_model_element.check_timestamp_value_in_range(date))

    def compare_match(self, match_element, string, total_seconds):
        """Test if the result MatchElement is as expected."""
        self.assertEqual(match_element.get_path(), "match/multiLocale")
        self.assertEqual(match_element.get_match_string(), string)
        self.assertEqual(match_element.get_match_object(), total_seconds)
        self.assertEqual(match_element.get_children(), None)


if __name__ == "__main__":
    unittest.main()
