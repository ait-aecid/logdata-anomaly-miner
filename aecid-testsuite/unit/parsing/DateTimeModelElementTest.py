import unittest
import logging
import pytz
import locale
from io import StringIO
from aminer.parsing.DateTimeModelElement import DateTimeModelElement
from aminer.parsing.MatchContext import MatchContext
from unit.TestBase import TestBase, DummyMatchContext, initialize_loggers
from datetime import datetime, timezone, timedelta
from pwd import getpwnam
from grp import getgrnam


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
        match_context = DummyMatchContext(b"07.02.2019 11:40:00: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S", timezone.utc)
        match_element = date_time_model_element.get_match_element("match1", match_context)
        self.assertEqual(match_element.match_string, b"07.02.2019 11:40:00")
        self.assertEqual(match_element.match_object, 1549539600)
        self.assertEqual(match_context.match_string, b"07.02.2019 11:40:00")

        # test leap year date
        match_context = DummyMatchContext(b"29.02.2020 11:40:00: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S", timezone.utc)
        match_element = date_time_model_element.get_match_element("match1", match_context)
        self.assertEqual(match_element.match_string, b"29.02.2020 11:40:00")
        self.assertEqual(match_element.match_object, 1582976400)
        self.assertEqual(match_context.match_string, b"29.02.2020 11:40:00")

        # test normal date with T
        match_context = DummyMatchContext(b"07.02.2019T11:40:00: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%YT%H:%M:%S", timezone.utc)
        match_element = date_time_model_element.get_match_element("match1", match_context)
        self.assertEqual(match_element.match_string, b"07.02.2019T11:40:00")
        self.assertEqual(match_element.match_object, 1549539600)
        self.assertEqual(match_context.match_string, b"07.02.2019T11:40:00")

        # test normal date with fractions
        match_context = DummyMatchContext(b"07.02.2019 11:40:00.123456: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S.%f", timezone.utc)
        match_element = date_time_model_element.get_match_element("match1", match_context)
        self.assertEqual(match_element.match_string, b"07.02.2019 11:40:00.123456")
        self.assertEqual(match_element.match_object, 1549539600.123456)
        self.assertEqual(match_context.match_string, b"07.02.2019 11:40:00.123456")

        # test normal date with z
        match_context = DummyMatchContext(b"07.02.2019 11:40:00+0000: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S%z", timezone.utc)
        match_element = date_time_model_element.get_match_element("match1", match_context)
        self.assertEqual(match_element.match_string, b"07.02.2019 11:40:00+0000")
        self.assertEqual(match_element.match_object, 1549539600)
        self.assertEqual(match_context.match_string, b"07.02.2019 11:40:00+0000")

        match_context = DummyMatchContext(b"07.02.2019 11:40:00: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y %H:%M:%S%z", timezone.utc)
        match_element = date_time_model_element.get_match_element("match1", match_context)
        self.assertEqual(match_element.match_string, b"07.02.2019 11:40:00")
        self.assertEqual(match_element.match_object, 1549539600)
        self.assertEqual(match_context.match_string, b"07.02.2019 11:40:00")

        # test with only date defined
        match_context = DummyMatchContext(b"07.02.2019: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%d.%m.%Y", timezone.utc)
        match_element = date_time_model_element.get_match_element("match1", match_context)
        self.assertEqual(match_element.match_string, b"07.02.2019")
        self.assertEqual(match_element.match_object, 1549497600)
        self.assertEqual(match_context.match_string, b"07.02.2019")

        # test with only time defined. Here obviously the seconds can not be tested.
        #################
        #This test does not work yet. By default the current day/month/year need to be used.
        #################
        match_context = DummyMatchContext(b"11:40:23: it still works")
        date_time_model_element = DateTimeModelElement("path", b"%H:%M:%S", timezone.utc)
        match_element = date_time_model_element.get_match_element("match1", match_context)
        self.assertEqual(match_element.match_string, b"11:40:23")
        self.assertEqual(match_context.match_string, b"11:40:23")

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
        # timedelta returns the difference between two datetimes. Therefore it has to have the opposite sign.
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
        date_time_model_element = DateTimeModelElement(
            "path", b"%d.%m %H:%M:%S", timezone.utc, start_year=start_year, max_time_jump_seconds=max_time_jump_seconds)
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
        date_time_model_element = DateTimeModelElement(
            "path", b"%d.%m %H:%M:%S", timezone.utc, start_year=start_year, max_time_jump_seconds=max_time_jump_seconds)
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

    def test26performance(self):
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
