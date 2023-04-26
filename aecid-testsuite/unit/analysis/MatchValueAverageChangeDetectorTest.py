import unittest
from aminer.analysis.MatchValueAverageChangeDetector import MatchValueAverageChangeDetector
from aminer.parsing.MatchElement import MatchElement
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase
from datetime import datetime
import time
from aminer.AminerConfig import DEFAULT_PERSISTENCE_PERIOD


class MatchValueAverageChangeDetectorTest(TestBase):
    """Unittests for the MatchValueAverageChangeDetector."""

    def test1receive_atom(self):
        """Test if log atoms are processed correctly."""
        pass

    def test2do_timer(self):
        """Test if the do_timer method is implemented properly."""
        description = "Test2do_timer"
        mvacd = MatchValueAverageChangeDetector(self.aminer_config, [self.stream_printer_event_handler], None, ["cron/job1"], 3, 57600, False, "Default")
        self.analysis_context.register_component(mvacd, description)
        t = time.time()
        mvacd.next_persist_time = t + 400
        self.assertEqual(mvacd.do_timer(t + 200), 200)
        self.assertEqual(mvacd.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(mvacd.do_timer(t + 999), 1)
        self.assertEqual(mvacd.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

    def test3persistence(self):
        """Test the do_persist and load_persistence_data methods."""
        description = "test4persistence"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", True, output_logline=False)
        self.analysis_context.register_component(new_match_path_detector, description)
        t = round(time.time(), 3)
        log_atom1 = LogAtom(self.fdme1.data, ParserMatch(self.match_element1), t, new_match_path_detector)
        log_atom2 = LogAtom(self.match_context2.match_data, ParserMatch(self.match_element2), t, new_match_path_detector)

        self.assertTrue(new_match_path_detector.receive_atom(log_atom1))
        self.assertTrue(new_match_path_detector.receive_atom(log_atom2))
        self.assertEqual(new_match_path_detector.known_path_set, {"/s1", "/d1"})
        new_match_path_detector.do_persist()
        with open(new_match_path_detector.persistence_file_name, "r") as f:
            self.assertEqual(f.readline(), '["string:/d1", "string:/s1"]')

        new_match_path_detector.known_path_set = set()
        new_match_path_detector.load_persistence_data()
        self.assertEqual(new_match_path_detector.known_path_set, {"/s1", "/d1"})

        other = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False, output_logline=False)
        self.assertEqual(new_match_path_detector.known_path_set, other.known_path_set)

    def test4validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        pass















    __expected_string = '%s Statistical data report\n%s: "%s" (%d lines)\n  "cron/job1": Change: new: n = 3, avg = %s, ' \
                        'var = 100000000.0; old: n = 3, avg = %s, var = 1000000.0\n\n'
    __expected_string2 = '%s Statistical data report\n%s: "%s" (%d lines)\n  "cron/job1": Change: new: n = 2, avg = %s, ' \
                         'var = 50000000.0; old: n = 2, avg = %s, var = 500000.0\n  "cron/job2": Change: new: n = 2, avg = %s, ' \
                         'var = 60500000.0; old: n = 2, avg = %s, var = 500000.0\n\n'

    cron_job1 = "cron/job1"
    cron_job2 = "cron/job2"

    def test1receive_atom_min_bin_elements_not_reached(self):
        """This test verifies, that no statistic evaluation is performed, until the minimal amount of bin elements is reached."""
        description = "Test1MatchValueAverageChangeDetector"
        start_time = 57600
        match_element1 = MatchElement(self.cron_job1, b"%d" % start_time, start_time, None)
        match_value_average_change_detector = MatchValueAverageChangeDetector(self.aminer_config, [
            self.stream_printer_event_handler], None, [match_element1.get_path()], 3, start_time, False, "Default")
        self.analysis_context.register_component(match_value_average_change_detector, description)

        # create oldBin
        log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1), start_time, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 1000), start_time + 1000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 1000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 2000), start_time + 2000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 2000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        # compare Data
        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 10000), start_time + 10000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 10000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 20000), start_time + 20000, None)
        log_atom = LogAtom(
          match_element1.get_match_object(), ParserMatch(match_element1), start_time + 20000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        self.assertEqual(self.output_stream.getvalue(), "")

    def test2receive_atom_min_bin_time_not_reached(self):
        """This test verifies, that no statistic evaluation is performed, until the start time is reached."""
        description = "Test2MatchValueAverageChangeDetector"
        start_time = 57600
        match_element1 = MatchElement(self.cron_job1, b"%d" % start_time, start_time, None)
        match_value_average_change_detector = MatchValueAverageChangeDetector(
            self.aminer_config, [self.stream_printer_event_handler], "time", [match_element1.get_path()], 3, start_time + 86400, False,
            "Default")
        self.analysis_context.register_component(match_value_average_change_detector, description)

        # create oldBin
        log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1), start_time, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 1000), start_time + 1000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 1000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 2000), start_time + 2000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 2000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        # compare Data
        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 10000), start_time + 10000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 10000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 20000), start_time + 20000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 20000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 30000), start_time + 30000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 30000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        self.assertEqual(self.output_stream.getvalue(), "")

    def test3receive_atom_statistically_ok(self):
        """This test case focuses on receiving an atom and being in the statistically acceptable area."""
        description = "Test3MatchValueAverageChangeDetector"
        start_time = 57600
        match_element1 = MatchElement(self.cron_job1, b"%d" % start_time, start_time, None)
        match_value_average_change_detector = MatchValueAverageChangeDetector(
            self.aminer_config, [self.stream_printer_event_handler], "time", [match_element1.get_path()], 3, start_time, False, "Default")
        self.analysis_context.register_component(match_value_average_change_detector, description)

        # create oldBin
        log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1), start_time, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 1000), start_time + 1000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 1000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 2000), start_time + 2000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 2000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        # compare Data
        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 11000), start_time + 11000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 11000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 12000), start_time + 12000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 12000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 13000), start_time + 13000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 13000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        self.assertEqual(self.output_stream.getvalue(), "")

    def test4receiveAtomStatisticallyOutOfRange(self):
        """This test case focuses on receiving an atom and being over the statistically acceptable area."""
        description = "Test4MatchValueAverageChangeDetector"
        start_time = time.time()

        match_element1 = MatchElement(self.cron_job1, b"%d" % start_time, start_time, None)
        match_value_average_change_detector = MatchValueAverageChangeDetector(
            self.aminer_config, [self.stream_printer_event_handler], None, [match_element1.get_path()], 3, start_time, False, "Default")
        self.analysis_context.register_component(match_value_average_change_detector, description)

        # create oldBin
        log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1), start_time, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 1000), start_time + 1000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 1000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 2000), start_time + 2000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 2000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        # compare Data
        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 10000), start_time + 10000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 10000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 20000), start_time + 20000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 20000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 30000), start_time + 30000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 30000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(start_time + 30000).strftime("%Y-%m-%d %H:%M:%S"),
            match_value_average_change_detector.__class__.__name__, description, 6, start_time + 20000, start_time + 1000))

    def test5more_values(self):
        """This test case proves the functionality, when using more than one path."""
        description = "Test5MatchValueAverageChangeDetector"
        start_time = time.time()

        match_element1 = MatchElement(self.cron_job1, b"%d" % start_time, start_time, None)
        match_element2 = MatchElement(self.cron_job2, b"%d" % start_time, start_time, None)
        match_value_average_change_detector = MatchValueAverageChangeDetector(
            self.aminer_config, [self.stream_printer_event_handler], None, [
                match_element1.get_path(), match_element2.get_path()], 2, start_time, False, "Default")
        self.analysis_context.register_component(match_value_average_change_detector, description)

        # create oldBin
        log_atom = LogAtom(match_element1.get_match_object(), ParserMatch(match_element1), start_time, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 1000), start_time + 1000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 1000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        # create oldBin for ME2
        log_atom = LogAtom(match_element2.get_match_object(), ParserMatch(match_element2), start_time, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        match_element2 = MatchElement(self.cron_job2, b"%d" % (start_time + 1000), start_time + 1000, None)
        log_atom = LogAtom(
            match_element2.get_match_object(), ParserMatch(match_element2), start_time + 1000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        # compare data
        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 10000), start_time + 10000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 10000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        match_element1 = MatchElement(self.cron_job1, b"%d" % (start_time + 20000), start_time + 20000, None)
        log_atom = LogAtom(
            match_element1.get_match_object(), ParserMatch(match_element1), start_time + 20000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        self.assertEqual(self.output_stream.getvalue(), "")

        # compare data with ME2
        match_element2 = MatchElement(self.cron_job2, b"%d" % (start_time + 11000), start_time + 11000, None)
        log_atom = LogAtom(
            match_element2.get_match_object(), ParserMatch(match_element2), start_time + 11000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)

        match_element2 = MatchElement(self.cron_job2, b"%d" % (start_time + 22000), start_time + 22000, None)
        log_atom = LogAtom(
            match_element2.get_match_object(), ParserMatch(match_element2), start_time + 22000, match_value_average_change_detector)
        match_value_average_change_detector.receive_atom(log_atom)
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string2 % (
            datetime.fromtimestamp(start_time + 22000).strftime("%Y-%m-%d %H:%M:%S"),
            match_value_average_change_detector.__class__.__name__, description, 4, start_time + 15000, start_time + 500,
            start_time + 16500, start_time + 500))


if __name__ == "__main__":
    unittest.main()
