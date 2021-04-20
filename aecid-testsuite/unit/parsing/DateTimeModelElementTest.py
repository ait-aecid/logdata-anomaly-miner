import unittest
import logging
import pytz
import locale
from io import StringIO
from aminer.parsing.DateTimeModelElement import DateTimeModelElement
from unit.TestBase import TestBase, DummyMatchContext, initialize_loggers
from datetime import datetime, timezone
from pwd import getpwnam
from grp import getgrnam


class DateTimeModelElementTest(TestBase):
    """
    Unittests for the DateTimeModelElement.
    To calculate the expected timestamps the timezone shift was added or subtracted from the date and the epoch was calculated on
    https://www.epochconverter.com/. For example the date 24.03.2018 11:40:00 CET was converted to 24.03.2018 10:40:00 UTC and then the
    epoch in seconds was calculated (1521888000).
    """

    id_ = "dtme"
    path = "path"

    def test1get_id(self):
        """Test if get_id works properly."""
        dtme = DateTimeModelElement(self.id_, b"%d.%m.%Y %H:%M:%S")
        self.assertEqual(dtme.get_id(), self.id_)

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        dtme = DateTimeModelElement(self.id_, b"%d.%m.%Y %H:%M:%S")
        self.assertEqual(dtme.get_child_elements(), None)

    def test3get_match_element_with_different_date_formats(self):
        """Test if different date_formats can be used to match data."""
        # test normal date
        data = b"07.02.2019 11:40:00: it still works"
        date = b"07.02.2019 11:40:00"
        match_context = DummyMatchContext(data)
        date_time_model_element = DateTimeModelElement(self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1549539600, None)

        # test leap year date
        data = b"29.02.2020 11:40:00: it still works"
        date = b"29.02.2020 11:40:00"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1582976400, None)

        # test normal date with T
        data = b"07.02.2019T11:40:00: it still works"
        date = b"07.02.2019T11:40:00"
        match_context = DummyMatchContext(data)
        date_time_model_element = DateTimeModelElement(self.id_, b"%d.%m.%YT%H:%M:%S", timezone.utc)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1549539600, None)

        # test normal date with fractions
        data = b"07.02.2019 11:40:00.123456: it still works"
        date = b"07.02.2019 11:40:00.123456"
        match_context = DummyMatchContext(data)
        date_time_model_element = DateTimeModelElement(self.id_, b"%d.%m.%Y %H:%M:%S.%f", timezone.utc)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1549539600.123456, None)

        # test normal date with z
        data = b"07.02.2019 11:40:00+0000: it still works"
        date = b"07.02.2019 11:40:00+0000"
        match_context = DummyMatchContext(data)
        date_time_model_element = DateTimeModelElement(self.id_, b"%d.%m.%Y %H:%M:%S%z", timezone.utc)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1549539600, None)

        data = b"07.02.2019 11:40:00: it still works"
        date = b"07.02.2019 11:40:00"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1549539600, None)

        # test with only date defined
        data = b"07.02.2019: it still works"
        date = b"07.02.2019"
        match_context = DummyMatchContext(data)
        date_time_model_element = DateTimeModelElement(self.id_, b"%d.%m.%Y", timezone.utc)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1549497600, None)

        # test with only time defined. Here obviously the seconds can not be tested.
        data = b"11:40:23: it still works"
        date = b"11:40:23"
        match_context = DummyMatchContext(data)
        date_time_model_element = DateTimeModelElement(self.id_, b"%H:%M:%S", timezone.utc)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, match_element.match_object, None)
        self.assertEqual(match_element.match_string, b"11:40:23")
        self.assertEqual(match_context.match_string, b"11:40:23")

    def test4wrong_date(self):
        """Test if wrong input data does not return a match."""
        # wrong day
        data = b"32.03.2019 11:40:00: it still works"
        date_time_model_element = DateTimeModelElement(self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc)
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # wrong month
        data = b"01.13.2019 11:40:00: it still works"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # wrong year
        data = b"01.01.00 11:40:00: it still works"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # wrong date leap year
        data = b"29.02.2019 11:40:00: it still works"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # missing T
        data = b"07.02.2019 11:40:00: it still works"
        match_context = DummyMatchContext(data)
        date_time_model_element = DateTimeModelElement(self.id_, b"%d.%m.%YT%H:%M:%S", timezone.utc)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

        # missing fractions
        data = b"07.02.2019 11:40:00.: it still works"
        match_context = DummyMatchContext(data)
        date_time_model_element = DateTimeModelElement(self.id_, b"%d.%m.%Y %H:%M:%S.%f", timezone.utc)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test5get_match_element_with_unclean_format_string(self):
        """This test case checks if unclean format_strings can be used."""
        data = b"Date %d: 07.02.2018 11:40:00 UTC+0000: it still works"
        date = b"Date %d: 07.02.2018 11:40:00 UTC+0000"
        match_context = DummyMatchContext(data)
        date_time_model_element = DateTimeModelElement(self.id_, b"Date %%d: %d.%m.%Y %H:%M:%S%z", timezone.utc)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1518003600, None)

    def test6get_match_element_with_different_time_zones(self):
        """Test if different time_zones work with the DateTimeModelElement."""
        date_time_model_element = DateTimeModelElement(self.id_, b"%d.%m.%Y %H:%M:%S%z", timezone.utc)
        data = b"07.02.2018 11:40:00 UTC-1200: it still works"
        date = b"07.02.2018 11:40:00 UTC-1200"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1518046800, None)

        data = b"07.02.2018 11:40:00 UTC-12: it still works"
        date = b"07.02.2018 11:40:00 UTC-12"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1518046800, None)

        data = b"07.02.2018 11:40:00 UTC-5: it still works"
        date = b"07.02.2018 11:40:00 UTC-5"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1518021600, None)

        data = b"07.02.2018 11:40:00 UTC-0500: it still works"
        date = b"07.02.2018 11:40:00 UTC-0500"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1518021600, None)

        data = b"07.02.2018 11:40:00 UTC+0000: it still works"
        date = b"07.02.2018 11:40:00 UTC+0000"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1518003600, None)

        data = b"07.02.2018 11:40:00 UTC+0100: it still works"
        date = b"07.02.2018 11:40:00 UTC+0100"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1518000000, None)

        data = b"07.02.2018 11:40:00 UTC+1400: it still works"
        date = b"07.02.2018 11:40:00 UTC+1400"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1517953200, None)

    def test7get_match_element_with_different_text_locales(self):
        """Test if data with different text locales can be handled with different text_locale parameters."""
        DateTimeModelElement(self.id_, b"%d.%m %H:%M:%S", timezone.utc, "en_US.UTF-8")
        DateTimeModelElement(self.id_, b"%d.%m %H:%M:%S", timezone.utc, "de_AT.UTF-8")
        DateTimeModelElement(self.id_, b"%d.%m %H:%M:%S", timezone.utc, "de_AT.ISO-8859-1")

    def test8text_locale_not_installed(self):
        """Check if an exception is raised when the text_locale is not installed on the system."""
        self.assertRaises(locale.Error, DateTimeModelElement, self.id_, b"%d.%m %H:%M:%S", timezone.utc, "af-ZA.UTF-8")

    def test9get_match_element_with_start_year(self):
        """Test if dates without year can be parsed, when the start_year is defined."""
        data = b"07.02 11:40:00: it still works"
        date = b"07.02 11:40:00"
        date_time_model_element = DateTimeModelElement(self.id_, b"%d.%m %H:%M:%S", timezone.utc, start_year=2017)
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1486467600, None)

        match_context = DummyMatchContext(data)
        date_time_model_element = DateTimeModelElement(self.id_, b"%d.%m %H:%M:%S", timezone.utc, start_year=2019)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1549539600, None)

    def test10get_match_element_without_start_year_defined(self):
        """Test if dates without year can still be parsed, even without defining the start_year."""
        data = b"07.02 11:40:00: it still works"
        date = b"07.02 11:40:00"
        date_time_model_element = DateTimeModelElement(self.id_, b"%d.%m %H:%M:%S", timezone.utc)
        match_context = DummyMatchContext(data)
        dtm = datetime(datetime.now().year, 2, 7, 11, 40, tzinfo=timezone.utc)
        total_seconds = (dtm - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, total_seconds, None)

    def test11get_match_element_with_leap_start_year(self):
        """Check if leap start_years can parse the 29th February."""
        data = b"29.02 11:40:00: it still works"
        date = b"29.02 11:40:00"
        date_time_model_element = DateTimeModelElement(self.id_, b"%d.%m %H:%M:%S", timezone.utc, start_year=2020)
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1582976400, None)

    def test12get_match_element_without_leap_start_year(self):
        """Check if normal start_years can not parse the 29th February."""
        data = b"29.02 11:40:00: it still works"
        date_time_model_element = DateTimeModelElement(self.id_, b"%d.%m %H:%M:%S", timezone.utc, start_year=2019)
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_no_match_results(data, match_element, match_context)

    def test13learn_new_start_year_with_start_year_set(self):
        """Test if a new year is learned successfully with the start year being set."""
        data = b"31.12 23:59:00: it still works"
        date = b"31.12 23:59:00"
        start_year = 2020
        date_time_model_element = DateTimeModelElement(self.id_, b"%d.%m %H:%M:%S", timezone.utc, start_year=start_year)
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1609459140, None)
        self.assertEqual(date_time_model_element.start_year, start_year)

        data = b"01.01 11:20:00: it still works"
        date = b"01.01 11:20:00"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1609500000, None)
        self.assertEqual(date_time_model_element.start_year, start_year + 1)

    def test14learn_new_start_year_without_start_year_set(self):
        """Test if a new year is learned successfully with the start year being None."""
        data = b"31.12 23:59:00: it still works"
        date = b"31.12 23:59:00"
        date_time_model_element = DateTimeModelElement(self.id_, b"%d.%m %H:%M:%S", timezone.utc)
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        dtm = datetime(datetime.now().year, 12, 31, 23, 59, tzinfo=timezone.utc)
        total_seconds = (dtm - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, total_seconds, None)

        data = b"01.01 11:20:00: it still works"
        date = b"01.01 11:20:00"
        start_year = date_time_model_element.start_year
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        dtm = datetime(datetime.now().year+1, 1, 1, 11, 20, tzinfo=timezone.utc)
        total_seconds = (dtm - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, total_seconds, None)
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
        date_time_model_element = DateTimeModelElement(
            self.id_, b"%d.%m %H:%M:%S", timezone.utc, start_year=start_year, max_time_jump_seconds=max_time_jump_seconds)
        data = b"31.12 23:59:00: it still works"
        date = b"31.12 23:59:00"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1609459140, None)
        self.assertEqual(date_time_model_element.start_year, start_year)

        data = b"01.01 23:59:00: it still works"
        date = b"01.01 23:59:00"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1609545540, None)
        self.assertEqual(date_time_model_element.start_year, start_year + 1)
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
        date_time_model_element = DateTimeModelElement(
            self.id_, b"%d.%m %H:%M:%S", timezone.utc, start_year=start_year, max_time_jump_seconds=max_time_jump_seconds)
        data = b"31.12 23:59:00: it still works"
        date = b"31.12 23:59:00"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1609459140, None)
        self.assertEqual(date_time_model_element.start_year, start_year)

        data = b"01.01 23:59:01: it still works"
        date = b"01.01 23:59:01"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1577923141, None)
        self.assertEqual(date_time_model_element.start_year, start_year)
        self.assertIn("WARNING:DEBUG:DateTimeModelElement time inconsistencies parsing b'01.01 23:59:01', expecting value around "
                      "1609459140. Check your settings!", log_stream.getvalue())
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        initialize_loggers(self.aminer_config, getpwnam("aminer").pw_uid, getgrnam("aminer").gr_gid)

    def test17time_change_cest_cet(self):
        """Check if the time change from CET to CEST and vice versa work as expected."""
        data = b"24.03.2018 11:40:00 CET: it still works"
        date = b"24.03.2018 11:40:00 CET"
        date_time_model_element = DateTimeModelElement(self.id_, b"%d.%m.%Y %H:%M:%S%z", timezone.utc)
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1521888000, None)

        # make sure format changes with longer format specifiers also work
        data = b"25.03.2018 11:40:00 CEST: it still works"
        date = b"25.03.2018 11:40:00 CEST"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1521970800, None)

        data = b"27.10.2018 11:40:00 CEST: it still works"
        date = b"27.10.2018 11:40:00 CEST"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1540633200, None)

        data = b"28.10.2018 11:40:00 CET: it still works"
        date = b"28.10.2018 11:40:00 CET"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1540723200, None)

        data = b"27.10.2018 11:40:00 EST: it still works"
        date = b"27.10.2018 11:40:00 EST"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1540658400, None)

        data = b"27.10.2018 11:40:00 PDT: it still works"
        date = b"27.10.2018 11:40:00 PDT"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1540665600, None)

        data = b"27.10.2018 11:40:00 GMT: it still works"
        date = b"27.10.2018 11:40:00 GMT"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1540640400, None)

    def test18same_timestamp_multiple_times(self):
        """Test if the DateTimeModelElement can handle multiple same timestamps."""
        data = b"07.02.2019 11:40:00: it still works"
        date = b"07.02.2019 11:40:00"
        date_time_model_element = DateTimeModelElement(self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc)
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1549539600, None)

        data = b"07.02.2019 11:40:00: it still works"
        date = b"07.02.2019 11:40:00"
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, 1549539600, None)

    def test19date_before_unix_timestamps(self):
        """Check if timestamps before the unix timestamp are processed properly."""
        data = b"01.01.1900 11:40:00: it still works"
        date = b"01.01.1900 11:40:00"
        date_time_model_element = DateTimeModelElement(self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc)
        match_context = DummyMatchContext(data)
        match_element = date_time_model_element.get_match_element(self.path, match_context)
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, date, -2208946800, None)

    def test20element_id_input_validation(self):
        """Check if element_id is validated."""
        date_format = b"%d.%m.%Y %H:%M:%S"
        # empty element_id
        element_id = ""
        self.assertRaises(ValueError, DateTimeModelElement, element_id, date_format)

        # None element_id
        element_id = None
        self.assertRaises(TypeError, DateTimeModelElement, element_id, date_format)

        # bytes element_id is not allowed
        element_id = b"path"
        self.assertRaises(TypeError, DateTimeModelElement, element_id, date_format)

        # bytes element_id is not allowed
        element_id = True
        self.assertRaises(TypeError, DateTimeModelElement, element_id, date_format)

        # integer element_id is not allowed
        element_id = 123
        self.assertRaises(TypeError, DateTimeModelElement, element_id, date_format)

        # float element_id is not allowed
        element_id = 123.22
        self.assertRaises(TypeError, DateTimeModelElement, element_id, date_format)

        # boolean element_id is not allowed
        element_id = True
        self.assertRaises(TypeError, DateTimeModelElement, element_id, date_format)

        # dict element_id is not allowed
        element_id = {"id": "path"}
        self.assertRaises(TypeError, DateTimeModelElement, element_id, date_format)

        # list element_id is not allowed
        element_id = ["path"]
        self.assertRaises(TypeError, DateTimeModelElement, element_id, date_format)

        # empty list element_id is not allowed
        element_id = []
        self.assertRaises(TypeError, DateTimeModelElement, element_id, date_format)

        # empty tuple element_id is not allowed
        element_id = ()
        self.assertRaises(TypeError, DateTimeModelElement, element_id, date_format)

        # empty set element_id is not allowed
        element_id = set()
        self.assertRaises(TypeError, DateTimeModelElement, element_id, date_format)

    def test21date_format_input_validation(self):
        """Check if date_format is validated and only valid values can be entered."""
        allowed_format_specifiers = b"bdfHMmSsYz%"
        # check if allowed values do not raise any exception.
        format_specifiers = b""
        for c in allowed_format_specifiers:
            format_specifiers += b"%" + str(chr(c)).encode()
            DateTimeModelElement(self.id_, b"%" + str(chr(c)).encode())
        # check if all allowed values can not be used together. An exception should be raised, because of multiple month representations
        # and %s with non-second formats.
        self.assertRaises(ValueError, DateTimeModelElement, self.id_, format_specifiers)
        DateTimeModelElement(self.id_, format_specifiers.replace(b"%m", b"").replace(b"%s", b""))
        DateTimeModelElement(self.id_, format_specifiers.replace(b"%b", b"").replace(b"%s", b""))
        DateTimeModelElement(self.id_, b"%s%z%f")
        for c in allowed_format_specifiers.replace(b"s", b"").replace(b"z", b"").replace(b"f", b"").replace(b"%", b""):
            self.assertRaises(ValueError, DateTimeModelElement, self.id_, b"%s%" + str(chr(c)).encode())

        # test non-existent specifiers
        for c in b"aceghijklnopqrtuvwxyABCDEFGIJKLNOPQRTUVWXZ":
            self.assertRaises(ValueError, DateTimeModelElement, self.id_, b"%" + str(chr(c)).encode())

        # test multiple specifiers. % and z specifiers are allowed multiple times.
        DateTimeModelElement(self.id_, b"%%%z%z")
        for c in allowed_format_specifiers.replace(b"%", b"").replace(b"z", b""):
            self.assertRaises(ValueError, DateTimeModelElement, self.id_, b"%" + str(chr(c)).encode() + b"%" + str(chr(c)).encode())

        self.assertRaises(ValueError, DateTimeModelElement, self.id_, b"")  # empty date_format
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, None)  # None date_format
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, "")  # string date_format is not allowed
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, 123)  # integer date_format is not allowed
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, 123.22)  # float date_format is not allowed
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, True)  # boolean date_format is not allowed
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, {"id": "path"})  # dict date_format is not allowed
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, ["path"])  # list date_format is not allowed
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, [])  # empty list date_format is not allowed
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, ())  # empty tuple date_format is not allowed
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, set())  # empty set date_format is not allowed

    def test22time_zone_input_validation(self):
        """Check if time_zone is validated and only valid values can be entered."""
        dtme = DateTimeModelElement(self.id_, b"%d.%m.%Y %H:%M:%S")
        self.assertEqual(dtme.time_zone, timezone.utc)
        DateTimeModelElement(self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc)
        for tz in pytz.all_timezones:
            DateTimeModelElement(self.id_, b"%d.%m.%Y %H:%M:%S", pytz.timezone(tz))

        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", b"UTC")
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", "UTC")
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", 1)
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", 1.25)
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", True)
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", {"time_zone": timezone.utc})
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", [timezone.utc])
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", [])
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", set())
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", ())

    def test23text_locale_input_validation(self):
        """
        Check if text_locale is validated and only valid values can be entered.
        An exception has to be raised if the locale is not installed on the system.
        """
        DateTimeModelElement(self.id_, b"%d.%m %H:%M:%S", timezone.utc, "en_US.UTF-8")
        DateTimeModelElement(self.id_, b"%d.%m %H:%M:%S", timezone.utc, ("en_US", "UTF-8"))
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m %H:%M:%S", timezone.utc, 1)
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m %H:%M:%S", timezone.utc, 1.2)
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m %H:%M:%S", timezone.utc, True)
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m %H:%M:%S", timezone.utc, ["en_US", "UTF-8"])
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m %H:%M:%S", timezone.utc, {"en_US": "UTF-8"})
        self.assertRaises(ValueError, DateTimeModelElement, self.id_, b"%d.%m %H:%M:%S", timezone.utc, tuple("en_US.UTF-8"))
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m %H:%M:%S", timezone.utc, set())
        self.assertRaises(ValueError, DateTimeModelElement, self.id_, b"%d.%m %H:%M:%S", timezone.utc, ())
        self.assertRaises(ValueError, DateTimeModelElement, self.id_, b"%d.%m %H:%M:%S", timezone.utc, ("en_US", "UTF-8", "de_AT", "UTF-8"))

    def test24start_year_input_validation(self):
        """Check if start_year is validated."""
        dtme = DateTimeModelElement(self.id_, b"%d.%m %H:%M:%S", timezone.utc, None, None)
        self.assertEqual(dtme.start_year, datetime.now().year)
        DateTimeModelElement(self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, 2020)
        DateTimeModelElement(self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, -630)
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, "2020")
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, True)
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, 1.25)
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, [2020])
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, [])
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, {"key": 2020})
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, set())
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, ())

    def test25max_time_jump_seconds_input_validation(self):
        """Check if max_time_jump_seconds is validated."""
        dtme = DateTimeModelElement(self.id_, b"%d.%m %H:%M:%S", timezone.utc, None, None)
        self.assertEqual(dtme.max_time_jump_seconds, 86400)
        DateTimeModelElement(self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, None, 100000)
        self.assertRaises(ValueError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, None, -1)
        self.assertRaises(ValueError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, None, 0)
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, None, "100000")
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, None, True)
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, None, 1.25)
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, None, [2020])
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, None, [])
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, None, {"key": 2020})
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, None, ())
        self.assertRaises(TypeError, DateTimeModelElement, self.id_, b"%d.%m.%Y %H:%M:%S", timezone.utc, None, None, set())

    def test26get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = DateTimeModelElement(self.id_, b"%d.%m.%Y %H:%M:%S")
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

    def test27performance(self):  # skipcq: PYL-R0201
        """Test the performance of the implementation."""
        import_setup = """
import copy
from unit.TestBase import DummyMatchContext
from aminer.parsing.DateTimeModelElement import DateTimeModelElement
times = 300000
"""
        string_no_z_setup = """
date = b"18.03.2021 16:12:55"
dtme = DateTimeModelElement("s0", b"%d.%m.%Y %H:%M:%S")
"""
        string_z_setup = """
date = b"18.03.2021 16:12:55 UTC+0100"
dtme = DateTimeModelElement("s0", b"%d.%m.%Y %H:%M:%S %z")
"""
        end_setup = """
dummy_match_context = DummyMatchContext(date)
dummy_match_context_list = [copy.deepcopy(dummy_match_context) for _ in range(times)]

def run():
    match_context = dummy_match_context_list.pop(0)
    dtme.get_match_element("match", match_context)
"""
        _no_z_setup = import_setup + string_no_z_setup + end_setup
        _z_setup = import_setup + string_z_setup + end_setup
        # import timeit
        # times = 300000
        # print()
        # print("Every date is run 300.000 times.")
        # t = timeit.timeit(setup=_no_z_setup, stmt="run()", number=times)
        # print("No %z parameter: ", t)
        # t = timeit.timeit(setup=_z_setup, stmt="run()", number=times)
        # print("Date with %z parameter: ", t)


if __name__ == "__main__":
    unittest.main()
