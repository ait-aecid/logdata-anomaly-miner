import unittest
import locale
import pytz
import logging
from typic import ConstraintValueError
from io import StringIO
from pwd import getpwnam
from grp import getgrnam
from datetime import datetime, timezone
from aminer.parsing.DateTimeModelElement import MultiLocaleDateTimeModelElement
from unit.TestBase import TestBase, DummyMatchContext, initialize_loggers


class MultiLocaleDateTimeModelElementTest(TestBase):
    """
    Unittests for the MultiLocaleDateTimeModelElement.
    To calculate the expected timestamps the timezone shift was added or subtracted from the date and the epoch was calculated on
    https://www.epochconverter.com/. For example the date 24.03.2018 11:40:00 CET was converted to 24.03.2018 10:40:00 UTC and then the
    epoch in seconds was calculated (1521888000).
    """

    id_ = "dtme"
    path = "path"

    def test1get_id(self):
        """Test if get_id works properly."""
        multi_dtme = MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m.%Y %H:%M:%S", None, None)])
        self.assertEqual(multi_dtme.get_id(), self.id_)

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        multi_dtme = MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m.%Y %H:%M:%S", None, None)])
        self.assertEqual(multi_dtme.get_child_elements(), None)

    def test3get_match_element_with_different_date_formats(self):
        """Test if different date_formats can be used to match data."""
        tz_gmt10 = pytz.timezone("Etc/GMT+10")
        en_gb_utf8 = "en_GB.utf8"
        en_us_utf8 = "en_US.utf8"
        de_at_utf8 = "de_AT.utf8"
        multi_locale_dtme = MultiLocaleDateTimeModelElement(self.id_, [
            (b"%d.%m.%Y %H:%M:%S.%f", None, None), (b"%d.%m.%Y %H:%M:%S%z", None, None),  (b"%d.%m.%Y %H:%M:%S", None, None),
            (b"%d.%m.%YT%H:%M:%S", None, None), (b"%d.%m.%Y", None, None), (b"%H:%M:%S:%f", None, de_at_utf8),
            (b"%H:%M:%S", None, None), (b"%b %d", tz_gmt10, de_at_utf8), (b"%d %b %Y", None, en_gb_utf8),
            (b"%dth %b %Y", None, en_gb_utf8), (b"%d/%m/%Y", None, en_gb_utf8), (b"%m-%d-%Y", None, en_us_utf8),
            (b"%d.%m. %H:%M:%S:%f", None, de_at_utf8)])

        # test normal date
        data = b"07.02.2019 11:40:00: it still works"
        date = b"07.02.2019 11:40:00"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_+"/format1", self.path, date, 1549539600, None)

        # test leap year date
        data = b"29.02.2020 11:40:00: it still works"
        date = b"29.02.2020 11:40:00"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format1", self.path, date, 1582976400, None)

        # test normal date with T
        data = b"07.02.2019T11:40:00: it still works"
        date = b"07.02.2019T11:40:00"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format3", self.path, date, 1549539600, None)

        # test normal date with fractions
        data = b"07.02.2019 11:40:00.123456: it still works"
        date = b"07.02.2019 11:40:00.123456"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1549539600.123456, None)

        # test normal date with z
        data = b"07.02.2019 11:40:00+0000: it still works"
        date = b"07.02.2019 11:40:00+0000"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format1", self.path, date, 1549539600, None)

        # test with only date defined
        data = b"07.02.2019: it still works"
        date = b"07.02.2019"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format4", self.path, date, 1549497600, None)

        # test with only time defined. Here obviously the seconds can not be tested.
        data = b"11:40:23: it still works"
        date = b"11:40:23"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(
            data, match_element, match_context, self.id_ + "/format6", self.path, date, match_element.match_object, None)

        data = b"Feb 25 something happened"
        date = b"Feb 25"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        dtm = datetime(datetime.now().year, 2, 25, tzinfo=tz_gmt10)
        # total_seconds should be in UTC, so the timezones are parsed out.
        total_seconds = (dtm - datetime(1970, 1, 1, tzinfo=tz_gmt10)).days * 86400 - dtm.utcoffset().total_seconds()
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format7", self.path, date, total_seconds, None)

        # British date
        data = b"13 Apr 2019 something happened"
        date = b"13 Apr 2019"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format8", self.path, date, 1555113600, None)

        # British date 2
        data = b"13th Apr 2019 something happened"
        date = b"13th Apr 2019"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format9", self.path, date, 1555113600, None)

        # British date 3
        data = b"13/04/2019 something happened"
        date = b"13/04/2019"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format10", self.path, date, 1555113600, None)

        # US date
        data = b"04-13-2019 something happened"
        date = b"04-13-2019"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format11", self.path, date, 1555113600, None)

        # Austrian date no year - year should already be learnt.
        # start year has to be 2021, because all other formats have defined years.
        data = b"13.04. 15:12:54:201 something happened"
        date = b"13.04. 15:12:54:201"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format12", self.path, date, 1618326774.201, None)

        multi_locale_dtme.latest_parsed_timestamp = None
        # Austrian time no date
        data = b"15:12:54:201 something happened"
        date = b"15:12:54:201"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        dtm = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 15, 12, 54, 201, tzinfo=timezone.utc)
        # total_seconds should be in UTC, so the timezones are parsed out.
        delta = (dtm - datetime(1970, 1, 1, tzinfo=dtm.tzinfo))
        total_seconds = delta.days * 86400 + delta.seconds + delta.microseconds / 1000
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format5", self.path, date, total_seconds, None)

    def test4wrong_date(self):
        """Test if wrong input data does not return a match."""
        tz_gmt10 = pytz.timezone("Etc/GMT+10")
        en_gb_utf8 = "en_GB.utf8"
        en_us_utf8 = "en_US.utf8"
        de_at_utf8 = "de_AT.utf8"
        multi_locale_dtme = MultiLocaleDateTimeModelElement(self.id_, [
            (b"%d.%m.%Y %H:%M:%S.%f", None, None), (b"%d.%m.%Y %H:%M:%S%z", None, None),  (b"%d.%m.%Y %H:%M:%S", None, None),
            (b"%d.%m.%YT%H:%M:%S", None, None), (b"%d.%m.%Y", None, None), (b"%H:%M:%S:%f", None, de_at_utf8),
            (b"%H:%M:%S", None, None), (b"%b %d", tz_gmt10, de_at_utf8), (b"%d %b %Y", None, en_gb_utf8),
            (b"%dth %b %Y", None, en_gb_utf8), (b"%d/%m/%Y", None, en_gb_utf8), (b"%m-%d-%Y", None, en_us_utf8),
            (b"%d.%m. %H:%M:%S:%f", None, de_at_utf8)])

        # wrong day
        data = b"32.03.2019 11:40:00: it still works"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # wrong month
        data = b"01.13.2019 11:40:00: it still works"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # wrong year
        data = b"01.01.00 11:40:00: it still works"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # wrong date leap year
        data = b"29.02.2019 11:40:00: it still works"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # British date
        data = b"13 Dezember 2019"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test5get_match_element_with_unclean_format_string(self):
        """This test case checks if unclean format_strings can be used."""
        data = b"Date %d: 07.02.2018 11:40:00 UTC+0000: it still works"
        date = b"Date %d: 07.02.2018 11:40:00 UTC+0000"
        match_context = DummyMatchContext(data)
        multi_locale_dtme = MultiLocaleDateTimeModelElement(self.id_, [(b"Date %%d: %d.%m.%Y %H:%M:%S%z", None, None)])
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1518003600, None)

    def test6get_match_element_with_different_time_zones(self):
        """Test if different time_zones work with the MultiLocaleDateTimeModelElement."""
        multi_locale_dtme = MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m.%Y %H:%M:%S%z", None, None)])
        data = b"07.02.2018 11:40:00 UTC-1200: it still works"
        date = b"07.02.2018 11:40:00 UTC-1200"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1518046800, None)

        data = b"07.02.2018 11:40:00 UTC-12: it still works"
        date = b"07.02.2018 11:40:00 UTC-12"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1518046800, None)

        data = b"07.02.2018 11:40:00 UTC-5: it still works"
        date = b"07.02.2018 11:40:00 UTC-5"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1518021600, None)

        data = b"07.02.2018 11:40:00 UTC-0500: it still works"
        date = b"07.02.2018 11:40:00 UTC-0500"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1518021600, None)

        data = b"07.02.2018 11:40:00 UTC+0000: it still works"
        date = b"07.02.2018 11:40:00 UTC+0000"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1518003600, None)

        data = b"07.02.2018 11:40:00 UTC+0100: it still works"
        date = b"07.02.2018 11:40:00 UTC+0100"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1518000000, None)

        data = b"07.02.2018 11:40:00 UTC+1400: it still works"
        date = b"07.02.2018 11:40:00 UTC+1400"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1517953200, None)

    def test7get_match_element_with_different_text_locales(self):
        """Test if data with different text locales can be handled with different text_locale parameters."""
        MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m %H:%M:%S", timezone.utc, "en_US.UTF-8")])
        MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m %H:%M:%S", timezone.utc, "de_AT.UTF-8")])
        MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m %H:%M:%S", timezone.utc, "de_AT.ISO-8859-1")])

    def test8text_locale_not_installed(self):
        """Check if an exception is raised when the text_locale is not installed on the system."""
        self.assertRaises(locale.Error, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m %H:%M:%S", timezone.utc, "af-ZA.UTF-8")])

    def test9get_match_element_with_start_year(self):
        """Test if dates without year can be parsed, when the start_year is defined."""
        data = b"07.02 11:40:00: it still works"
        date = b"07.02 11:40:00"
        multi_locale_dtme = MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m %H:%M:%S", None, None)], start_year=2017)
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1486467600, None)

        multi_locale_dtme = MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m %H:%M:%S", None, None)], start_year=2019)
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1549539600, None)

    def test10get_match_element_without_start_year_defined(self):
        """Test if dates without year can still be parsed, even without defining the start_year."""
        data = b"07.02 11:40:00: it still works"
        date = b"07.02 11:40:00"
        multi_locale_dtme = MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m %H:%M:%S", None, None)])
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        dtm = datetime(datetime.now().year, 2, 7, 11, 40, tzinfo=timezone.utc)
        total_seconds = (dtm - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, total_seconds, None)

    def test11get_match_element_with_leap_start_year(self):
        """Check if leap start_years can parse the 29th February."""
        multi_locale_dtme = MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m %H:%M:%S", None, None)], start_year=2020)
        data = b"29.02 11:40:00: it still works"
        date = b"29.02 11:40:00"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1582976400, None)

    def test12get_match_element_without_leap_start_year(self):
        """Check if normal start_years can not parse the 29th February."""
        data = b"29.02 11:40:00: it still works"
        multi_locale_dtme = MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m %H:%M:%S", None, None)], start_year=2019)
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test13learn_new_start_year_with_start_year_set(self):
        """Test if a new year is learned successfully with the start year being set."""
        start_year = 2020
        multi_locale_dtme = MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m %H:%M:%S", None, None)], start_year=start_year)
        data = b"31.12 23:59:00: it still works"
        date = b"31.12 23:59:00"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1609459140, None)
        self.assertEqual(multi_locale_dtme.start_year, start_year)

        data = b"01.01 11:20:00: it still works"
        date = b"01.01 11:20:00"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1609500000, None)
        self.assertEqual(multi_locale_dtme.start_year, start_year + 1)

    def test14learn_new_start_year_without_start_year_set(self):
        """Test if a new year is learned successfully with the start year being None."""
        multi_locale_dtme = MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m %H:%M:%S", None, None)])
        data = b"31.12 23:59:00: it still works"
        date = b"31.12 23:59:00"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        dtm = datetime(datetime.now().year, 12, 31, 23, 59, tzinfo=timezone.utc)
        total_seconds = (dtm - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, total_seconds, None)

        start_year = multi_locale_dtme.start_year
        data = b"01.01 11:20:00: it still works"
        date = b"01.01 11:20:00"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        dtm = datetime(datetime.now().year+1, 1, 1, 11, 20, tzinfo=timezone.utc)
        total_seconds = (dtm - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, total_seconds, None)
        self.assertEqual(multi_locale_dtme.start_year, start_year + 1)

    def test15max_time_jump_seconds_in_time(self):
        """
        Test if the max_time_jump_seconds parameter works if the next date is in time.
        Warnings with unqualified timestamp year wraparound.
        """
        log_stream = StringIO()
        logging.basicConfig(stream=log_stream, level=logging.INFO)
        max_time_jump_seconds = 86400
        start_year = 2020
        multi_locale_dtme = MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m %H:%M:%S", None, None)], start_year=start_year,
                                                            max_time_jump_seconds=max_time_jump_seconds)
        data = b"31.12 23:59:00: it still works"
        date = b"31.12 23:59:00"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1609459140, None)
        self.assertEqual(multi_locale_dtme.start_year, 2020)

        data = b"01.01 23:59:00: it still works"
        date = b"01.01 23:59:00"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1609545540, None)
        self.assertEqual(multi_locale_dtme.start_year, 2021)
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
        multi_locale_dtme = MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m %H:%M:%S", None, None)], start_year=start_year,
                                                            max_time_jump_seconds=max_time_jump_seconds)
        data = b"31.12 23:59:00: it still works"
        date = b"31.12 23:59:00"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1609459140, None)
        self.assertEqual(multi_locale_dtme.start_year, start_year)

        data = b"01.01 23:59:01: it still works"
        date = b"01.01 23:59:01"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1577923141, None)
        self.assertEqual(multi_locale_dtme.start_year, start_year)
        self.assertIn("WARNING:DEBUG:DateTimeModelElement time inconsistencies parsing b'01.01 23:59:01', expecting value around "
                      "1609459140. Check your settings!", log_stream.getvalue())
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        initialize_loggers(self.aminer_config, getpwnam("aminer").pw_uid, getgrnam("aminer").gr_gid)

    def test17time_change_cest_cet(self):
        """Check if the time change from CET to CEST and vice versa work as expected."""
        multi_locale_dtme = MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m.%Y %H:%M:%S%z", None, None)])
        data = b"24.03.2018 11:40:00 CET: it still works"
        date = b"24.03.2018 11:40:00 CET"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1521888000, None)

        data = b"25.03.2018 11:40:00 CEST: it still works"
        date = b"25.03.2018 11:40:00 CEST"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1521970800, None)

        data = b"27.10.2018 11:40:00 CEST: it still works"
        date = b"27.10.2018 11:40:00 CEST"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1540633200, None)

        data = b"28.10.2018 11:40:00 CET: it still works"
        date = b"28.10.2018 11:40:00 CET"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1540723200, None)

        data = b"27.10.2018 11:40:00 EST: it still works"
        date = b"27.10.2018 11:40:00 EST"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1540658400, None)

        data = b"27.10.2018 11:40:00 PDT: it still works"
        date = b"27.10.2018 11:40:00 PDT"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1540665600, None)

        data = b"27.10.2018 11:40:00 GMT: it still works"
        date = b"27.10.2018 11:40:00 GMT"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1540640400, None)

    def test18same_timestamp_multiple_times(self):
        """Test if the MultiLocaleDateTimeModelElement can handle multiple same timestamps."""
        multi_locale_dtme = MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m.%Y %H:%M:%S", None, None)])
        data = b"07.02.2019 11:40:00: it still works"
        date = b"07.02.2019 11:40:00"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1549539600, None)

        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, 1549539600, None)

    def test19date_before_unix_timestamps(self):
        """Check if timestamps before the unix timestamp are processed properly."""
        multi_locale_dtme = MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m.%Y %H:%M:%S", None, None)])
        data = b"01.01.1900 11:40:00: it still works"
        date = b"01.01.1900 11:40:00"
        match_context = DummyMatchContext(data)
        match_element = multi_locale_dtme.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_ + "/format0", self.path, date, -2208946800, None)

    def test20element_id_input_validation(self):
        """Check if element_id is validated."""
        date_formats = [(b"%d.%m.%Y %H:%M:%S", None, None)]
        # empty element_id
        element_id = ""
        self.assertRaises(ValueError, MultiLocaleDateTimeModelElement, element_id, date_formats)

        # None element_id
        element_id = None
        self.assertRaises(TypeError, MultiLocaleDateTimeModelElement, element_id, date_formats)

        # bytes element_id is not allowed
        element_id = b"path"
        self.assertRaises(TypeError, MultiLocaleDateTimeModelElement, element_id, date_formats)

        # integer element_id is not allowed
        element_id = 123
        self.assertRaises(TypeError, MultiLocaleDateTimeModelElement, element_id, date_formats)

        # float element_id is not allowed
        element_id = 123.22
        self.assertRaises(TypeError, MultiLocaleDateTimeModelElement, element_id, date_formats)

        # boolean element_id is not allowed
        element_id = True
        self.assertRaises(TypeError, MultiLocaleDateTimeModelElement, element_id, date_formats)

        # dict element_id is not allowed
        element_id = {"id": "path"}
        self.assertRaises(TypeError, MultiLocaleDateTimeModelElement, element_id, date_formats)

        # list element_id is not allowed
        element_id = ["path"]
        self.assertRaises(TypeError, MultiLocaleDateTimeModelElement, element_id, date_formats)

        # empty list element_id is not allowed
        element_id = []
        self.assertRaises(TypeError, MultiLocaleDateTimeModelElement, element_id, date_formats)

        # empty tuple element_id is not allowed
        element_id = ()
        self.assertRaises(TypeError, MultiLocaleDateTimeModelElement, element_id, date_formats)

        # empty set element_id is not allowed
        element_id = set()
        self.assertRaises(TypeError, MultiLocaleDateTimeModelElement, element_id, date_formats)

    def test21date_formats_input_validation(self):
        """Check if date_format is validated and only valid values can be entered."""
        allowed_format_specifiers = b"bdfHMmSsYz%"
        # check if allowed values do not raise any exception.
        format_specifiers = b""
        for c in allowed_format_specifiers:
            format_specifiers += b"%" + str(chr(c)).encode()
            MultiLocaleDateTimeModelElement(self.id_, [(b"%" + str(chr(c)).encode(), None, None)])
        # check if all allowed values can not be used together. An exception should be raised, because of multiple month representations
        # and %s with non-second formats.
        self.assertRaises(ValueError, MultiLocaleDateTimeModelElement, self.id_, [(format_specifiers, None, None)])
        MultiLocaleDateTimeModelElement(self.id_, [(format_specifiers.replace(b"%m", b"").replace(b"%s", b""), None, None)])
        MultiLocaleDateTimeModelElement(self.id_, [(format_specifiers.replace(b"%b", b"").replace(b"%s", b""), None, None)])
        MultiLocaleDateTimeModelElement(self.id_, [(b"%s%z%f", None, None)])
        for c in allowed_format_specifiers.replace(b"s", b"").replace(b"z", b"").replace(b"f", b"").replace(b"%", b""):
            self.assertRaises(ValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%s%" + str(chr(c)).encode(), None, None)])

        # test non-existent specifiers
        for c in b"aceghijklnopqrtuvwxyABCDEFGIJKLNOPQRTUVWXZ":
            self.assertRaises(ValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%" + str(chr(c)).encode(), None, None)])

        # test multiple specifiers. % and z specifiers are allowed multiple times.
        MultiLocaleDateTimeModelElement(self.id_, [(b"%%%z%z", None, None)])
        for c in allowed_format_specifiers.replace(b"%", b"").replace(b"z", b""):
            self.assertRaises(ValueError, MultiLocaleDateTimeModelElement, self.id_, [(
                b"%" + str(chr(c)).encode() + b"%" + str(chr(c)).encode(), None, None)])

        self.assertRaises(ValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%s%z%f", None)])
        self.assertRaises(ValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"", None, None)])  # empty
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(None, None, None)])  # None
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [("", None, None)])   # string
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(123, None, None)])  # integer
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(123.22, None, None)])  # float
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(True, None, None)])  # boolean
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [({"id": "path"}, None, None)])  # dict
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(["path"], None, None)])  # list
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [([], None, None)])  # empty list
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [((), None, None)])  # empty tuple
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(set(), None, None)])  # empty set
        self.assertRaises(TypeError, MultiLocaleDateTimeModelElement, self.id_, [[b"%d.%m.%Y %H:%M:%S", None, None]])  # list inst of tuple
        self.assertRaises(ValueError, MultiLocaleDateTimeModelElement, self.id_, [()])  # empty tuple
        self.assertRaises(ValueError, MultiLocaleDateTimeModelElement, self.id_, [tuple(b"%d.%m.%Y %H:%M:%S")])  # 1 tuple
        self.assertRaises(ValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", None)])  # 2 tuple
        self.assertRaises(ValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", None, None, None)])  # 4 tuple

    def test22time_zone_input_validation(self):
        """Check if time_zone is validated and only valid values can be entered."""
        en_gb_utf8 = "en_GB.utf8"
        en_us_utf8 = "en_US.utf8"
        de_at_utf8 = "de_AT.utf8"
        multi_locale_dtme = MultiLocaleDateTimeModelElement(self.id_, [
            (b"%d.%m.%Y %H:%M:%S.%f", None, None), (b"%d.%m.%Y %H:%M:%S%z", None, None),  (b"%d.%m.%Y %H:%M:%S", None, None),
            (b"%d.%m.%YT%H:%M:%S", None, None), (b"%d.%m.%Y", None, None), (b"%H:%M:%S:%f", None, de_at_utf8),
            (b"%H:%M:%S", None, None), (b"%d %b %Y", None, en_gb_utf8), (b"%dth %b %Y", None, en_gb_utf8), (b"%d/%m/%Y", None, en_gb_utf8),
            (b"%m-%d-%Y", None, en_us_utf8), (b"%d.%m. %H:%M:%S:%f", None, de_at_utf8)])
        for dtme in multi_locale_dtme.date_time_model_elements:
            self.assertEqual(dtme.time_zone, timezone.utc)
        MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m.%Y %H:%M:%S", timezone.utc, None)])
        for tz in pytz.all_timezones:
            MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m.%Y %H:%M:%S", pytz.timezone(tz), None)])

        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", b"", None)])
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", "UTC", None)])
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", 1, None)])
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", 1.25, None)])
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", True, None)])
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", [timezone.utc], None)])
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", {"time_zone": timezone.utc}, None)])

    def test23text_locale_input_validation(self):
        """
        Check if text_locale is validated and only valid values can be entered.
        An exception has to be raised if the locale is not installed on the system.
        """
        MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m %H:%M:%S", timezone.utc, "en_US.UTF-8")])
        MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m %H:%M:%S", timezone.utc, ("en_US", "UTF-8"))])
        self.assertRaises(ValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", None, "")])
        self.assertRaises(ValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", None, tuple("en_US.UTF-8"))])
        self.assertRaises(ValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", None, ("en_US", "UTF-8", "t"))])
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", None, b"")])
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", None, 1)])
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", None, 1.2)])
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", None, True)])
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", None, ["en_US", "UTF-8"])])
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", None, {"en_US": "UTF-8"})])

    def test24start_year_input_validation(self):
        """Check if start_year is validated."""
        multi_locale_dtme = MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m %H:%M:%S", timezone.utc, None)], None)
        self.assertEqual(multi_locale_dtme.start_year, datetime.now().year)
        MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m %H:%M:%S", timezone.utc, None)], 2020)
        MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m %H:%M:%S", timezone.utc, None)], -630)
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", timezone.utc, None)], "2020")
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", timezone.utc, None)], True)
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", timezone.utc, None)], 1.25)
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", timezone.utc, None)], [2020])
        self.assertRaises(ConstraintValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", timezone.utc, None)], {"key": 2020})

    def test25max_time_jump_seconds_input_validation(self):
        """Check if max_time_jump_seconds is validated."""
        multi_locale_dtme = MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m %H:%M:%S", timezone.utc, None)], None)
        self.assertEqual(multi_locale_dtme.max_time_jump_seconds, 86400)
        MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m.%Y %H:%M:%S", timezone.utc, None)], None, 100000)
        MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m.%Y %H:%M:%S", timezone.utc, None)], None, 1)
        self.assertRaises(ValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", timezone.utc, None)], None, -1)
        self.assertRaises(ValueError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", timezone.utc, None)], None, 0)
        self.assertRaises(TypeError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", timezone.utc, None)], None, "1000")
        self.assertRaises(TypeError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", timezone.utc, None)], None, True)
        self.assertRaises(TypeError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", timezone.utc, None)], None, 1.25)
        self.assertRaises(TypeError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", timezone.utc, None)], None, {
            "key": 2020})
        self.assertRaises(TypeError, MultiLocaleDateTimeModelElement, self.id_, [(b"%d.%m.%Y %H:%M:%S", timezone.utc, None)], None, [1000])

    def test26get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = MultiLocaleDateTimeModelElement(self.id_, [(b"%d.%m.%Y %H:%M:%S", None, None)])
        data = b"07.02.2019 11:40:00: it still works"
        model_element.get_match_element(self.path, DummyMatchContext(data))
        from aminer.parsing.MatchContext import MatchContext
        model_element.get_match_element(self.path, MatchContext(data))

        from aminer.parsing.MatchElement import MatchElement
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, MatchElement(data, None, None, None))
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, data)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, data.decode())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, 123)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, 123.22)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, True)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, None)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, [])
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, {"key": MatchContext(data)})
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, set())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, ())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, model_element)


if __name__ == "__main__":
    unittest.main()
