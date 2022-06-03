import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.ParserMatch import ParserMatch
from aminer.input.LogAtom import LogAtom
from aminer.analysis.MissingMatchPathValueDetector import MissingMatchPathValueDetector, MissingMatchPathListValueDetector
import time
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from unit.TestBase import TestBase
from datetime import datetime, timezone


class MissingMatchPathValueDetectorTest(TestBase):
    """Unittests for the MissingMatchPathValueDetector."""

    __expected_string = '%s Interval too large between values\n%s: "%s" (%d lines)\n    %s\n\n'
    __default_interval = 3600
    __realert_interval = 86400

    pid = b' pid='
    datetime_format_string = '%Y-%m-%d %H:%M:%S'
    match1_s1_overdue = "['match1/s1']: \"[' pid=']\" overdue 400s (interval -400)"
    string = b'25537 uid=2'

    def test1_receive_atom(self):
        """This test case checks whether a missing value is created without using the learn_mode (should not be the case)."""
        description = "Test1MissingMatchPathValueDetector"
        match_context_fixed_dme = MatchContext(self.pid)
        fixed_dme = FixedDataModelElement('s1', self.pid)
        match_element_fixed_dme = fixed_dme.get_match_element("match1", match_context_fixed_dme)
        missing_match_path_value_detector = MissingMatchPathValueDetector(self.aminer_config, [match_element_fixed_dme.get_path()], [
            self.stream_printer_event_handler], 'Default', False, self.__default_interval, self.__realert_interval)
        self.analysis_context.register_component(missing_match_path_value_detector, description)
        log_atom_fixed_dme = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element_fixed_dme), 1, missing_match_path_value_detector)
        self.assertTrue(missing_match_path_value_detector.receive_atom(log_atom_fixed_dme))

    def test2_receive_atom_without_match_element(self):
        """This test case checks if the ReceiveAtom controls the MatchElement and responds correctly, when it is missing."""
        description = "Test2MissingMatchPathValueDetector"
        match_context_fixed_dme = MatchContext(self.pid)
        fixed_dme = FixedDataModelElement('s1', self.pid)
        match_element_fixed_dme = fixed_dme.get_match_element("match1", match_context_fixed_dme)
        match_context_fixed_dme = MatchContext(self.pid)
        matchElementFixedDME2 = fixed_dme.get_match_element("match2", match_context_fixed_dme)
        missing_match_path_value_detector = MissingMatchPathValueDetector(self.aminer_config, [match_element_fixed_dme.get_path()], [
            self.stream_printer_event_handler], 'Default', False, self.__default_interval, self.__realert_interval)
        self.analysis_context.register_component(missing_match_path_value_detector, description)
        log_atom_fixed_dme = LogAtom(fixed_dme.fixed_data, ParserMatch(matchElementFixedDME2), 1, missing_match_path_value_detector)
        self.assertFalse(missing_match_path_value_detector.receive_atom(log_atom_fixed_dme))

    def test3_receive_atom_no_missing_value(self):
        """This test case checks whether the class returns wrong positives, when the time limit is not passed."""
        description = "Test3MissingMatchPathValueDetector"
        t = time.time()
        match_context_fixed_dme = MatchContext(self.pid)
        fixed_dme = FixedDataModelElement('s1', self.pid)
        match_element_fixed_dme = fixed_dme.get_match_element("match1", match_context_fixed_dme)
        missing_match_path_value_detector = MissingMatchPathValueDetector(self.aminer_config, [match_element_fixed_dme.get_path()], [
            self.stream_printer_event_handler], 'Default', True, self.__default_interval, self.__realert_interval)
        self.analysis_context.register_component(missing_match_path_value_detector, description)
        log_atom_fixed_dme = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element_fixed_dme), t, missing_match_path_value_detector)
        self.assertTrue(missing_match_path_value_detector.receive_atom(log_atom_fixed_dme))

        past_time = 3200
        missing_match_path_value_detector = MissingMatchPathValueDetector(self.aminer_config, [match_element_fixed_dme.get_path()], [
            self.stream_printer_event_handler], 'Default', True, missing_match_path_value_detector.default_interval - past_time,
            self.__realert_interval)

        log_atom_fixed_dme = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element_fixed_dme), t + past_time,
                                     missing_match_path_value_detector)
        self.assertTrue(missing_match_path_value_detector.receive_atom(log_atom_fixed_dme))
        self.assertEqual(self.output_stream.getvalue(), '')

    def test4_receive_atom_missing_value(self):
        """This test case checks if missing values are reported correctly."""
        description = "Test4MissingMatchPathValueDetector"
        t = time.time()
        match_context_fixed_dme = MatchContext(self.pid)
        fixed_dme = FixedDataModelElement('s1', self.pid)
        match_element_fixed_dme = fixed_dme.get_match_element("match1", match_context_fixed_dme)
        missing_match_path_value_detector = MissingMatchPathValueDetector(self.aminer_config, [match_element_fixed_dme.get_path()], [
            self.stream_printer_event_handler], 'Default', True, self.__default_interval, self.__realert_interval)
        self.analysis_context.register_component(missing_match_path_value_detector, description)
        log_atom_fixed_dme = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element_fixed_dme), t, missing_match_path_value_detector)
        self.assertTrue(missing_match_path_value_detector.receive_atom(log_atom_fixed_dme))

        past_time = 4000
        missing_match_path_value_detector = MissingMatchPathValueDetector(self.aminer_config, [match_element_fixed_dme.get_path()], [
            self.stream_printer_event_handler], 'Default', True, missing_match_path_value_detector.default_interval - past_time,
            self.__realert_interval, output_log_line=False)
        self.analysis_context.register_component(missing_match_path_value_detector, description + "2")

        log_atom_fixed_dme = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element_fixed_dme), t + past_time,
                                     missing_match_path_value_detector)
        self.assertTrue(missing_match_path_value_detector.receive_atom(log_atom_fixed_dme))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t + past_time).strftime(self.datetime_format_string),
            missing_match_path_value_detector.__class__.__name__, description + "2", 1, self.match1_s1_overdue))

    def test5_missing_value_on_persisted(self):
        """Persisting elements is tested in this test case."""
        description = "Test5MissingMatchPathValueDetector"
        t = time.time()
        match_context_fixed_dme = MatchContext(self.pid)
        fixed_dme = FixedDataModelElement('s1', self.pid)
        match_element_fixed_dme = fixed_dme.get_match_element("match1", match_context_fixed_dme)
        missing_match_path_value_detector = MissingMatchPathValueDetector(self.aminer_config, [match_element_fixed_dme.get_path()], [
            self.stream_printer_event_handler], 'Default', True, self.__default_interval, self.__realert_interval)
        self.analysis_context.register_component(missing_match_path_value_detector, description)
        log_atom_fixed_dme = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element_fixed_dme), round(t),
                                     missing_match_path_value_detector)
        self.assertTrue(missing_match_path_value_detector.receive_atom(log_atom_fixed_dme))
        missing_match_path_value_detector.do_persist()

        past_time = 4000
        other_missing_match_path_value_detector = MissingMatchPathValueDetector(self.aminer_config, [match_element_fixed_dme.get_path()], [
            self.stream_printer_event_handler], 'Default', True, self.__default_interval, self.__realert_interval)
        self.analysis_context.register_component(other_missing_match_path_value_detector, description + "2")
        other_missing_match_path_value_detector.set_check_value(other_missing_match_path_value_detector.get_channel_key(
            log_atom_fixed_dme)[1], self.__default_interval - past_time, match_element_fixed_dme.get_path())

        log_atom_fixed_dme = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element_fixed_dme), round(t) + past_time,
                                     other_missing_match_path_value_detector)
        self.assertTrue(other_missing_match_path_value_detector.receive_atom(log_atom_fixed_dme))
        # skipcq: PYL-R1714
        self.assertTrue((self.output_stream.getvalue() == self.__expected_string % (
            datetime.fromtimestamp(t + past_time).strftime(self.datetime_format_string),
            other_missing_match_path_value_detector.__class__.__name__, description + "2", 1, self.match1_s1_overdue)) or (
                        self.output_stream.getvalue() == self.__expected_string % (
                            datetime.fromtimestamp(t + past_time + 1).strftime(self.datetime_format_string),
                            other_missing_match_path_value_detector.__class__.__name__, description + "2", 1, self.match1_s1_overdue)))

    def test6_receive_atom_list(self):
        """This test case checks, whether a missing value is created by a list without using the learn_mode."""
        description = "Test6MissingMatchPathValueDetector"
        match_context_fixed_dme = MatchContext(self.pid)
        fixed_dme = FixedDataModelElement('s1', self.pid)
        match_element_fixed_dme = fixed_dme.get_match_element("match1", match_context_fixed_dme)
        match_context_decimal_integer_value_me = MatchContext(self.string)
        decimal_integer_value_me = DecimalIntegerValueModelElement('d1', DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                                                                   DecimalIntegerValueModelElement.PAD_TYPE_NONE)
        match_element_decimal_integer_value_me = decimal_integer_value_me.get_match_element(
            "match2", match_context_decimal_integer_value_me)

        missing_match_path_list_value_detector = MissingMatchPathListValueDetector(self.aminer_config, [
            match_element_fixed_dme.get_path(), match_element_decimal_integer_value_me.get_path()], [self.stream_printer_event_handler],
            'Default', False, self.__default_interval, self.__realert_interval)
        self.analysis_context.register_component(missing_match_path_list_value_detector, description)
        log_atom_fixed_dme = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element_fixed_dme), 1, missing_match_path_list_value_detector)
        self.assertTrue(missing_match_path_list_value_detector.receive_atom(log_atom_fixed_dme))

    def test7_receive_atom_list_without_match_element(self):
        """This test case checks if the ReceiveAtom controls the list of MatchElements and responds correctly, when a value is missing."""
        description = "Test7MissingMatchPathValueDetector"
        match_context_fixed_dme = MatchContext(self.pid)
        fixed_dme = FixedDataModelElement('s1', self.pid)
        match_element_fixed_dme = fixed_dme.get_match_element("match1", match_context_fixed_dme)
        match_context_decimal_integer_value_me = MatchContext(self.string)
        decimal_integer_value_me = DecimalIntegerValueModelElement('d1', DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                                                                   DecimalIntegerValueModelElement.PAD_TYPE_NONE)
        match_element_decimal_integer_value_me = decimal_integer_value_me.get_match_element(
            "match2", match_context_decimal_integer_value_me)

        match_context_fixed_dme = MatchContext(self.pid)
        matchElementFixedDME2 = fixed_dme.get_match_element("match3", match_context_fixed_dme)
        missing_match_path_list_value_detector = MissingMatchPathListValueDetector(self.aminer_config, [
            match_element_fixed_dme.get_path(), match_element_decimal_integer_value_me.get_path()], [self.stream_printer_event_handler],
            'Default', False, self.__default_interval, self.__realert_interval)
        self.analysis_context.register_component(missing_match_path_list_value_detector, description)
        log_atom_fixed_dme = LogAtom(fixed_dme.fixed_data, ParserMatch(matchElementFixedDME2), 1, missing_match_path_list_value_detector)
        self.assertFalse(missing_match_path_list_value_detector.receive_atom(log_atom_fixed_dme))

    def test8_receive_atom_list_no_missing_value(self):
        """This test case checks whether the class returns wrong positives on lists, when the time limit should not be passed."""
        description = "Test8MissingMatchPathValueDetector"
        t = time.time()
        match_context_fixed_dme = MatchContext(self.pid)
        fixed_dme = FixedDataModelElement('s1', self.pid)
        match_element_fixed_dme = fixed_dme.get_match_element("match1", match_context_fixed_dme)

        match_context_decimal_integer_value_me = MatchContext(self.string)
        decimal_integer_value_me = DecimalIntegerValueModelElement('d1', DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                                                                   DecimalIntegerValueModelElement.PAD_TYPE_NONE)
        match_element_decimal_integer_value_me = decimal_integer_value_me.get_match_element(
            "match2", match_context_decimal_integer_value_me)

        missing_match_path_list_value_detector = MissingMatchPathListValueDetector(self.aminer_config, [
            match_element_fixed_dme.get_path(), match_element_decimal_integer_value_me.get_path()], [self.stream_printer_event_handler],
            'Default', True, self.__default_interval, self.__realert_interval)
        self.analysis_context.register_component(missing_match_path_list_value_detector, description)
        log_atom_fixed_dme = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element_fixed_dme), round(t),
                                     missing_match_path_list_value_detector)
        self.assertTrue(missing_match_path_list_value_detector.receive_atom(log_atom_fixed_dme))

        past_time = 3200
        missing_match_path_list_value_detector = MissingMatchPathListValueDetector(self.aminer_config, [
            match_element_fixed_dme.get_path(), match_element_decimal_integer_value_me.get_path()], [self.stream_printer_event_handler],
            'Default', True, missing_match_path_list_value_detector.default_interval - past_time, self.__realert_interval)
        self.analysis_context.register_component(missing_match_path_list_value_detector, description + "2")
        log_atom_fixed_dme = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element_fixed_dme), round(t) + past_time,
                                     missing_match_path_list_value_detector)
        self.assertTrue(missing_match_path_list_value_detector.receive_atom(log_atom_fixed_dme))
        self.assertEqual(self.output_stream.getvalue(), '')

    def test9_receive_atom_list_missing_value(self):
        """This test case checks if missing values are reported correctly."""
        description = "Test90MissingMatchPathValueDetector"
        t = time.time()
        match_context_fixed_dme = MatchContext(self.pid)
        fixed_dme = FixedDataModelElement('s1', self.pid)
        match_element_fixed_dme = fixed_dme.get_match_element("match1", match_context_fixed_dme)
        match_context_decimal_integer_value_me = MatchContext(self.string)
        decimal_integer_value_me = DecimalIntegerValueModelElement('d1', DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                                                                   DecimalIntegerValueModelElement.PAD_TYPE_NONE)
        match_element_decimal_integer_value_me = decimal_integer_value_me.get_match_element(
            "match2", match_context_decimal_integer_value_me)

        missing_match_path_list_value_detector = MissingMatchPathListValueDetector(self.aminer_config, [
            match_element_fixed_dme.get_path(), match_element_decimal_integer_value_me.get_path()], [self.stream_printer_event_handler],
            'Default', True, self.__default_interval, self.__realert_interval)
        self.analysis_context.register_component(missing_match_path_list_value_detector, description)

        log_atom_fixed_dme = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element_fixed_dme), round(t),
                                     missing_match_path_list_value_detector)
        self.assertTrue(missing_match_path_list_value_detector.receive_atom(log_atom_fixed_dme))

        past_time = 4000
        missing_match_path_list_value_detector = MissingMatchPathListValueDetector(self.aminer_config, [
            match_element_fixed_dme.get_path(), match_element_decimal_integer_value_me.get_path()], [self.stream_printer_event_handler],
            'Default', True, missing_match_path_list_value_detector.default_interval - past_time, self.__realert_interval)
        self.analysis_context.register_component(missing_match_path_list_value_detector, description + "2")

        log_atom_fixed_dme = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element_fixed_dme), round(t) + past_time,
                                     missing_match_path_list_value_detector)
        self.assertTrue(missing_match_path_list_value_detector.receive_atom(log_atom_fixed_dme))
        # skipcq: PYL-R1714
        self.assertTrue((self.output_stream.getvalue() == self.__expected_string % (
            datetime.fromtimestamp(t + past_time).strftime(self.datetime_format_string),
            missing_match_path_list_value_detector.__class__.__name__, description + "2", 1,
            "match1/s1, match2/d1: ' pid=' overdue 400s (interval -400)")) or (self.output_stream.getvalue() == self.__expected_string % (
              datetime.fromtimestamp(t + past_time + 1).strftime(self.datetime_format_string),
              missing_match_path_list_value_detector.__class__.__name__, description + "2", 1,
              "match1/s1, match2/d1: ' pid=' overdue 400s (interval -400)")))

    def test10_missing_value_on_persisted(self):
        """Persisting lists is tested in this test case."""
        description = "Test91MissingMatchPathValueDetector"
        t = time.time()
        match_context_fixed_dme = MatchContext(self.pid)
        fixed_dme = FixedDataModelElement('s2', self.pid)
        match_element_fixed_dme = fixed_dme.get_match_element("match3", match_context_fixed_dme)

        match_context_decimal_integer_value_me = MatchContext(self.string)
        decimal_integer_value_me = DecimalIntegerValueModelElement('d2', DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                                                                   DecimalIntegerValueModelElement.PAD_TYPE_NONE)
        match_element_decimal_integer_value_me = decimal_integer_value_me.get_match_element(
            "match4", match_context_decimal_integer_value_me)
        missing_match_path_list_value_detector = MissingMatchPathListValueDetector(self.aminer_config, [
            match_element_fixed_dme.get_path(), match_element_decimal_integer_value_me.get_path()], [self.stream_printer_event_handler],
            'Default', True, self.__default_interval, self.__realert_interval)
        self.analysis_context.register_component(missing_match_path_list_value_detector, description)
        log_atom_fixed_dme = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element_fixed_dme), round(t),
                                     missing_match_path_list_value_detector)
        self.assertTrue(missing_match_path_list_value_detector.receive_atom(log_atom_fixed_dme))
        missing_match_path_list_value_detector.do_persist()

        past_time = 4000
        other_missing_match_path_list_value_detector = MissingMatchPathListValueDetector(self.aminer_config, [
            match_element_fixed_dme.get_path(), match_element_decimal_integer_value_me.get_path()], [self.stream_printer_event_handler],
            'Default', True, self.__default_interval, self.__realert_interval)
        self.analysis_context.register_component(other_missing_match_path_list_value_detector, description + "2")
        other_missing_match_path_list_value_detector.set_check_value(other_missing_match_path_list_value_detector.get_channel_key(
            log_atom_fixed_dme)[1], self.__default_interval - past_time, match_element_fixed_dme.get_path())

        log_atom_fixed_dme = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element_fixed_dme), round(t) + past_time,
                                     other_missing_match_path_list_value_detector)
        self.assertTrue(other_missing_match_path_list_value_detector.receive_atom(log_atom_fixed_dme))
        # skipcq: PYL-R1714
        self.assertTrue((self.output_stream.getvalue() == self.__expected_string % (
            datetime.fromtimestamp(t + past_time).strftime(self.datetime_format_string),
            other_missing_match_path_list_value_detector.__class__.__name__, description + "2", 1,
            "match3/s2, match4/d2: ' pid=' overdue 400s (interval -400)")) or (self.output_stream.getvalue() == self.__expected_string % (
              datetime.fromtimestamp(t + past_time + 1).strftime(self.datetime_format_string),
              other_missing_match_path_list_value_detector.__class__.__name__, description + "2", 1,
              "match3/s2, match4/d2: ' pid=' overdue 400s (interval -400)")))

    def test11multiple_paths(self):
        """Test the functionality of the MissingMatchPathValueDetector with multiple target_path_list."""
        description = "Test11MissingMatchPathValueDetector"
        match_context = MatchContext(self.pid + b"22")
        fixed_dme = FixedDataModelElement('s1', self.pid)
        decimal_integer_value_me = DecimalIntegerValueModelElement('d1', DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                                                                   DecimalIntegerValueModelElement.PAD_TYPE_NONE)
        seq = SequenceModelElement('model', [fixed_dme, decimal_integer_value_me])
        match_element = seq.get_match_element("match", match_context)
        missing_match_path_value_detector = MissingMatchPathValueDetector(self.aminer_config, [
            "match/model", "match/model/s1", "match/model/d1"], [self.stream_printer_event_handler], 'Default', False,
            self.__default_interval, self.__realert_interval)
        self.analysis_context.register_component(missing_match_path_value_detector, description)
        log_atom = LogAtom(fixed_dme.fixed_data + b"22", ParserMatch(match_element), 1, missing_match_path_value_detector)
        self.assertTrue(missing_match_path_value_detector.receive_atom(log_atom))

    def test12multiple_paths_data_from_file(self):
        """Test the functionality of the MissingMatchPathValueDetector with multiple target_path_list with more data."""
        description = "Test12MissingMatchPathValueDetector"
        with open('unit/data/multiple_pathes_mmpvd.txt', 'rb') as f:
            data = f.readlines()

        host1 = FixedDataModelElement("host1", b"host1 ")
        host2 = FixedDataModelElement("host2", b"host2 ")
        service1 = FixedDataModelElement("service1", b"service1")
        service2 = FixedDataModelElement("service2", b"service2")
        seq11 = SequenceModelElement("seq11", [host1, service1])
        seq12 = SequenceModelElement("seq12", [host1, service2])
        seq21 = SequenceModelElement("seq21", [host2, service1])
        seq22 = SequenceModelElement("seq22", [host2, service2])
        first = FirstMatchModelElement("first", [seq11, seq12, seq21, seq22])
        missing_match_path_value_detector11 = MissingMatchPathValueDetector(self.aminer_config, [
            "match/first/seq11", "match/first/seq11/host1", "match/first/seq11/service1"], [self.stream_printer_event_handler],
            'Default11', True, 480, 480)
        self.analysis_context.register_component(missing_match_path_value_detector11, description+"11")
        missing_match_path_value_detector12 = MissingMatchPathValueDetector(self.aminer_config, [
            "match/first/seq12", "match/first/seq12/host1", "match/first/seq12/service2"], [self.stream_printer_event_handler],
            'Default23', True, 480, 480)
        self.analysis_context.register_component(missing_match_path_value_detector12, description+"12")
        missing_match_path_value_detector21 = MissingMatchPathValueDetector(self.aminer_config, [
            "match/first/seq21", "match/first/seq21/host2", "match/first/seq21/service1"], [self.stream_printer_event_handler],
            'Default21', True, 480, 480)
        self.analysis_context.register_component(missing_match_path_value_detector21, description+"21")
        missing_match_path_value_detector22 = MissingMatchPathValueDetector(self.aminer_config, [
            "match/first/seq22", "match/first/seq22/host2", "match/first/seq22/service2"], [self.stream_printer_event_handler],
            'Default22', True, 480, 480)
        self.analysis_context.register_component(missing_match_path_value_detector22, description+"22")
        t = 0
        for line in data:
            split_line = line.rsplit(b" ", 2)
            date = datetime.strptime(split_line[0].decode(), "%Y-%m-%d %H:%M:%S")
            date = date.astimezone(timezone.utc)
            t = (date - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
            # initialize the detectors and remove the first output.
            if missing_match_path_value_detector11.learn_mode is True:
                line = b"host1 service1host1 service2host2 service1host2 service2"
                match_context = MatchContext(line)
                match_element = first.get_match_element("match", match_context)
                log_atom = LogAtom(line, ParserMatch(match_element), t, missing_match_path_value_detector11)
                missing_match_path_value_detector11.receive_atom(log_atom)
                missing_match_path_value_detector11.learn_mode = False
                match_element = first.get_match_element("match", match_context)
                log_atom = LogAtom(line, ParserMatch(match_element), t, missing_match_path_value_detector12)
                missing_match_path_value_detector12.receive_atom(log_atom)
                missing_match_path_value_detector12.learn_mode = False
                match_element = first.get_match_element("match", match_context)
                log_atom = LogAtom(line, ParserMatch(match_element), t, missing_match_path_value_detector21)
                missing_match_path_value_detector21.receive_atom(log_atom)
                missing_match_path_value_detector21.learn_mode = False
                match_element = first.get_match_element("match", match_context)
                log_atom = LogAtom(line, ParserMatch(match_element), t, missing_match_path_value_detector22)
                missing_match_path_value_detector22.receive_atom(log_atom)
                missing_match_path_value_detector22.learn_mode = False
                self.reset_output_stream()
            line = split_line[1] + b" " + split_line[2]
            match_context = MatchContext(line)
            match_element = first.get_match_element("match", match_context)
            log_atom = LogAtom(line, ParserMatch(match_element), t, missing_match_path_value_detector11)
            res = missing_match_path_value_detector11.receive_atom(log_atom)
            if match_element.get_path() == "match/first/seq11":
                self.assertTrue(res)
            res = missing_match_path_value_detector12.receive_atom(log_atom)
            if match_element.get_path() == "match/first/seq12":
                self.assertTrue(res)
            res = missing_match_path_value_detector21.receive_atom(log_atom)
            if match_element.get_path() == "match/first/seq21":
                self.assertTrue(res)
            res = missing_match_path_value_detector22.receive_atom(log_atom)
            if match_element.get_path() == "match/first/seq22":
                self.assertTrue(res)
        # need to produce a valid match to trigger missing match target_path_list.
        line = b"host1 service1host1 service2host2 service1host2 service2"
        match_context = MatchContext(line)
        match_element = first.get_match_element("match", match_context)
        log_atom = LogAtom(line, ParserMatch(match_element), t, missing_match_path_value_detector11)
        missing_match_path_value_detector11.receive_atom(log_atom)
        match_element = first.get_match_element("match", match_context)
        log_atom = LogAtom(line, ParserMatch(match_element), t, missing_match_path_value_detector12)
        missing_match_path_value_detector12.receive_atom(log_atom)
        match_element = first.get_match_element("match", match_context)
        log_atom = LogAtom(line, ParserMatch(match_element), t, missing_match_path_value_detector21)
        missing_match_path_value_detector21.receive_atom(log_atom)
        match_element = first.get_match_element("match", match_context)
        log_atom = LogAtom(line, ParserMatch(match_element), t, missing_match_path_value_detector22)
        missing_match_path_value_detector22.receive_atom(log_atom)

        # exactly one overdue should be found
        msg = "2021-03-12 21:30:51 Interval too large between values\nMissingMatchPathValueDetector: \"Test12MissingMatchPathValue" \
              "Detector11\" (1 lines)\n    ['match/first/seq11', 'match/first/seq11/host1', 'match/first/seq11/service1']: \"['host1 " \
              "service1', 'host1 ', 'service1']\" overdue 12.0s (interval 480)\n\n"
        self.assertEqual(msg, self.output_stream.getvalue())


if __name__ == "__main__":
    unittest.main()
