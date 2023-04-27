import unittest
from aminer.parsing.ParserMatch import ParserMatch
from aminer.input.LogAtom import LogAtom
from aminer.analysis.MissingMatchPathValueDetector import MissingMatchPathValueDetector, MissingMatchPathListValueDetector
import time
from unit.TestBase import TestBase, DummyMatchContext, DummyFixedDataModelElement, DummySequenceModelElement, DummyFirstMatchModelElement
from datetime import datetime, timezone
from aminer.AminerConfig import DEFAULT_PERSISTENCE_PERIOD


class MissingMatchPathValueDetectorTest(TestBase):
    """Unittests for the MissingMatchPathValueDetector."""

    expected_string = '%s Interval too large between values\n%s: "None" (%d lines)\n  %s\n\n'
    datetime_format_string = "%Y-%m-%d %H:%M:%S"

    def test1receive_atom_MissingMatchPathValueDetector(self):
        """
        Test if log atoms are processed correctly and the detector is learning (learn_mode=True) and stops if learn_mode=False.
        Test if stop_learning_time and stop_learning_no_anomaly_timestamp are implemented properly.
        """
        data = b" pid="
        match_context = DummyMatchContext(data)
        fdme = DummyFixedDataModelElement("s1", data)
        fdme2 = DummyFixedDataModelElement("s2", data)
        match_element1 = fdme.get_match_element("match", match_context)
        match_context = DummyMatchContext(data)
        match_element2 = fdme2.get_match_element("match", match_context)
        mmpvd = MissingMatchPathValueDetector(self.aminer_config, ["match/s1"], [self.stream_printer_event_handler], learn_mode=True)
        t = time.time()
        log_atom1 = LogAtom(fdme.data, ParserMatch(match_element1), t, mmpvd)
        log_atom2 = LogAtom(fdme.data, ParserMatch(match_element2), t, mmpvd)

        # learn_mode = True
        # check if the log atom is not processed if the path does not match.
        self.assertFalse(mmpvd.receive_atom(log_atom2))

        # check if no anomaly is produced if the log atom is received in time.
        self.assertTrue(mmpvd.receive_atom(log_atom1))
        passed_time = t + 3200
        log_atom = LogAtom(fdme.data, ParserMatch(match_element1), passed_time, mmpvd)
        self.assertTrue(mmpvd.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), "")

        # check if anomalies are detected properly.
        passed_time += 4000
        log_atom = LogAtom(fdme.data, ParserMatch(match_element1), passed_time, mmpvd)
        self.assertTrue(mmpvd.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), self.expected_string % (datetime.fromtimestamp(passed_time).strftime(self.datetime_format_string),
            mmpvd.__class__.__name__, 1, "['match/s1']: \"[' pid=']\" overdue 400s (interval 3600)"))
        self.reset_output_stream()

        # multiple paths
        match_context = DummyMatchContext(data + data)
        seq = DummySequenceModelElement("model", [fdme, fdme2])
        match_element = seq.get_match_element("match", match_context)
        mmpvd = MissingMatchPathValueDetector(self.aminer_config, ["match/model", "match/model/s1", "match/model/s2"], [self.stream_printer_event_handler], learn_mode=True)
        log_atom = LogAtom(fdme.data + fdme.data, ParserMatch(match_element), 1, mmpvd)
        self.assertTrue(mmpvd.receive_atom(log_atom))

        # learn_mode = False
        # check if a missing value is created without using the learn_mode (should not be the case).
        mmpvd = MissingMatchPathValueDetector(self.aminer_config, ["match/s1"], [self.stream_printer_event_handler], learn_mode=False)
        self.assertFalse(mmpvd.receive_atom(log_atom2))
        self.assertTrue(mmpvd.receive_atom(log_atom1))
        passed_time = t + 3200
        log_atom = LogAtom(fdme.data, ParserMatch(match_element1), passed_time, mmpvd)
        self.assertTrue(mmpvd.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), "")

        # check if anomalies are detected properly.
        passed_time += 4000
        log_atom = LogAtom(fdme.data, ParserMatch(match_element1), passed_time, mmpvd)
        self.assertTrue(mmpvd.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), "")

        # combine_values = False

        # stop_learning_time
        mmpvd = MissingMatchPathValueDetector(self.aminer_config, ["match/s1"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100)
        self.assertTrue(mmpvd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 99
        self.assertTrue(mmpvd.receive_atom(log_atom1))
        self.assertTrue(mmpvd.learn_mode)
        log_atom1.atom_time = t + 101
        self.assertTrue(mmpvd.receive_atom(log_atom1))
        self.assertFalse(mmpvd.learn_mode)

        # stop_learning_no_anomaly_time
        mmpvd = MissingMatchPathValueDetector(self.aminer_config, ["match/s1"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=10000)
        log_atom1.atom_time = t
        self.assertTrue(mmpvd.receive_atom(log_atom1))
        log_atom1.atom_time = t + 100
        self.assertTrue(mmpvd.receive_atom(log_atom1))
        self.assertTrue(mmpvd.learn_mode)
        log_atom2.atom_time = t + 100
        self.assertFalse(mmpvd.receive_atom(log_atom2))
        self.assertTrue(mmpvd.learn_mode)
        log_atom1.atom_time = t + 3800
        self.assertTrue(mmpvd.receive_atom(log_atom1))
        self.assertTrue(mmpvd.learn_mode)
        log_atom1.atom_time = t + 13800
        self.assertTrue(mmpvd.receive_atom(log_atom1))
        self.assertTrue(mmpvd.learn_mode)
        log_atom1.atom_time = t + 13801
        self.assertTrue(mmpvd.receive_atom(log_atom1))
        self.assertFalse(mmpvd.learn_mode)

    def test2receive_atom_MissingMatchPathListValueDetector(self):
        """
        Test if log atoms are processed correctly and the detector is learning (learn_mode=True) and stops if learn_mode=False.
        Test if stop_learning_time and stop_learning_no_anomaly_timestamp are implemented properly.
        """
        # check if a missing value is created by a list without using the learn_mode.
        data = b" pid="
        match_context = DummyMatchContext(data + data)
        fdme = DummyFixedDataModelElement("s1", data)
        match_element = fdme.get_match_element("match", match_context)
        t = time.time()

        mmplvd = MissingMatchPathListValueDetector(self.aminer_config, ["match/s1", "match/s2"], [self.stream_printer_event_handler], learn_mode=True)
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), t, mmplvd)
        self.assertTrue(mmplvd.receive_atom(log_atom))
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), t + 4000, mmplvd)
        self.assertTrue(mmplvd.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), self.expected_string % (datetime.fromtimestamp(log_atom.atom_time).strftime(self.datetime_format_string),
            mmplvd.__class__.__name__, 1, "match/s1, match/s2: ' pid=' overdue 400s (interval 3600)"))
        self.reset_output_stream()

        # check if the class returns wrong positives on lists, when the time limit should not be passed.
        mmplvd = MissingMatchPathListValueDetector(self.aminer_config, ["match/s1", "match/s2"], [self.stream_printer_event_handler], learn_mode=True)
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), round(t), mmplvd)
        self.assertTrue(mmplvd.receive_atom(log_atom))

        past_time = 3200
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), round(t) + past_time, mmplvd)
        self.assertTrue(mmplvd.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), "")

        # check if missing values are reported correctly.
        mmplvd = MissingMatchPathListValueDetector(self.aminer_config, ["match/s1", "match/s2"], [self.stream_printer_event_handler], learn_mode=True)
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), round(t), mmplvd)
        self.assertTrue(mmplvd.receive_atom(log_atom))
        past_time = 4000
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), round(t) + past_time, mmplvd)
        self.assertTrue(mmplvd.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), self.expected_string % (datetime.fromtimestamp(log_atom.atom_time).strftime(self.datetime_format_string),
            mmplvd.__class__.__name__, 1, "match/s1, match/s2: ' pid=' overdue 400s (interval 3600)"))

        # check if no anomaly is produced if the log atom is received in time.
        match_element = fdme.get_match_element("match3", match_context)
        mmplvd = MissingMatchPathListValueDetector(self.aminer_config, ["match/s1", "match/s2"], [self.stream_printer_event_handler])
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), 1, mmplvd)
        self.assertFalse(mmplvd.receive_atom(log_atom))

    def test3multiple_paths_data_from_file(self):
        """Test the functionality of the MissingMatchPathValueDetector with multiple paths with more data."""
        description = "Test3MissingMatchPathValueDetector"
        with open("unit/data/multiple_pathes_mmpvd.txt", "rb") as f:
            data = f.readlines()

        host1 = DummyFixedDataModelElement("host1", b"host1 ")
        host2 = DummyFixedDataModelElement("host2", b"host2 ")
        service1 = DummyFixedDataModelElement("service1", b"service1")
        service2 = DummyFixedDataModelElement("service2", b"service2")
        seq11 = DummySequenceModelElement("seq11", [host1, service1])
        seq12 = DummySequenceModelElement("seq12", [host1, service2])
        seq21 = DummySequenceModelElement("seq21", [host2, service1])
        seq22 = DummySequenceModelElement("seq22", [host2, service2])
        first = DummyFirstMatchModelElement("first", [seq11, seq12, seq21, seq22])
        mmpvd11 = MissingMatchPathValueDetector(self.aminer_config, [
            "match/first/seq11", "match/first/seq11/host1", "match/first/seq11/service1"], [self.stream_printer_event_handler],
            "Default11", True, 480, 480)
        self.analysis_context.register_component(mmpvd11, description+"11")
        missing_match_path_value_detector12 = MissingMatchPathValueDetector(self.aminer_config, [
            "match/first/seq12", "match/first/seq12/host1", "match/first/seq12/service2"], [self.stream_printer_event_handler],
            "Default23", True, 480, 480)
        self.analysis_context.register_component(missing_match_path_value_detector12, description+"12")
        missing_match_path_value_detector21 = MissingMatchPathValueDetector(self.aminer_config, [
            "match/first/seq21", "match/first/seq21/host2", "match/first/seq21/service1"], [self.stream_printer_event_handler],
            "Default21", True, 480, 480)
        self.analysis_context.register_component(missing_match_path_value_detector21, description+"21")
        missing_match_path_value_detector22 = MissingMatchPathValueDetector(self.aminer_config, [
            "match/first/seq22", "match/first/seq22/host2", "match/first/seq22/service2"], [self.stream_printer_event_handler],
            "Default22", True, 480, 480)
        self.analysis_context.register_component(missing_match_path_value_detector22, description+"22")
        t = 0
        for line in data:
            split_line = line.rsplit(b" ", 2)
            date = datetime.strptime(split_line[0].decode(), "%Y-%m-%d %H:%M:%S")
            date = date.astimezone(timezone.utc)
            t = (date - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
            # initialize the detectors and remove the first output.
            if mmpvd11.learn_mode is True:
                line = b"host1 service1host1 service2host2 service1host2 service2"
                match_context = DummyMatchContext(line)
                match_element = first.get_match_element("match", match_context)
                log_atom = LogAtom(line, ParserMatch(match_element), t, mmpvd11)
                mmpvd11.receive_atom(log_atom)
                mmpvd11.learn_mode = False
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
            match_context = DummyMatchContext(line)
            match_element = first.get_match_element("match", match_context)
            log_atom = LogAtom(line, ParserMatch(match_element), t, mmpvd11)
            res = mmpvd11.receive_atom(log_atom)
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
        # need to produce a valid match to trigger missing match paths.
        line = b"host1 service1host1 service2host2 service1host2 service2"
        match_context = DummyMatchContext(line)
        match_element = first.get_match_element("match", match_context)
        log_atom = LogAtom(line, ParserMatch(match_element), t, mmpvd11)
        mmpvd11.receive_atom(log_atom)
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
        msg = "2021-03-12 21:30:51 Interval too large between values\nMissingMatchPathValueDetector: \"Test3MissingMatchPathValue" \
              "Detector11\" (1 lines)\n  ['match/first/seq11', 'match/first/seq11/host1', 'match/first/seq11/service1']: \"['host1 " \
              "service1', 'host1 ', 'service1']\" overdue 12s (interval 480)\n\n"
        self.assertEqual(msg, self.output_stream.getvalue())

    def test4do_timer(self):
        """Test if the do_timer method is implemented properly."""
        mmpvd = MissingMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler])
        t = time.time()
        mmpvd.next_persist_time = t + 400
        self.assertEqual(mmpvd.do_timer(t + 200), 200)
        self.assertEqual(mmpvd.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(mmpvd.do_timer(t + 999), 1)
        self.assertEqual(mmpvd.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

        mmplvd = MissingMatchPathListValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler])
        t = time.time()
        mmplvd.next_persist_time = t + 400
        self.assertEqual(mmplvd.do_timer(t + 200), 200)
        self.assertEqual(mmplvd.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(mmplvd.do_timer(t + 999), 1)
        self.assertEqual(mmplvd.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

    def test5allowlist_event(self):
        """Test if the allowlist_event method is implemented properly."""
        # This test case checks whether an exception is thrown when entering an event of another class.
        mmpvd = MissingMatchPathValueDetector(self.aminer_config, ["match/s1"], [self.stream_printer_event_handler], learn_mode=True)
        data = b" pid="
        t = time.time()
        match_context = DummyMatchContext(data)
        analysis = "Analysis.%s"
        fdme = DummyFixedDataModelElement("s1", data)
        match_element = fdme.get_match_element("match", match_context)
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), t, mmpvd)
        mmpvd.receive_atom(log_atom)
        self.assertRaises(Exception, mmpvd.allowlist_event, analysis % "NewMatchPathValueDetector", self.output_stream.getvalue(), None)

        # check in which cases an event is triggered and compares with expected results.
        self.assertEqual(mmpvd.allowlist_event(analysis % mmpvd.__class__.__name__, ("data", "match/s1"), 10), f"Updated 'data' in 'match/s1' to new interval 10.")
        self.assertEqual(mmpvd.expected_values_dict, {"[' pid=']": [t, 3600, 0, "['match/s1']"], "data": [t, 10, 0, "match/s1"]})

        self.assertEqual(mmpvd.allowlist_event(analysis % mmpvd.__class__.__name__, ("data1", "match/s1"), -1), f"Updated 'data1' in 'match/s1' to new interval 3600.")
        self.assertEqual(mmpvd.expected_values_dict, {"[' pid=']": [t, 3600, 0, "['match/s1']"], "data": [t, 10, 0, "match/s1"], "data1": [t, 3600, 0, "match/s1"]})

        mmpvd.learn_mode = False
        self.assertEqual(mmpvd.allowlist_event(analysis % mmpvd.__class__.__name__, ("data3", "match/s2"), 10), "Updated 'data3' in 'match/s2' to new interval 10.")
        self.assertEqual(mmpvd.expected_values_dict, {"[' pid=']": [t, 3600, 0, "['match/s1']"], "data": [t, 10, 0, "match/s1"], "data1": [t, 3600, 0, "match/s1"], "data3": [t, 10, 0, "match/s2"]})

    def test6persistence(self):
        """
        Test the do_persist and load_persistence_data methods.
        In this case the persistence of MissingMatchPathValueDetector and MissingMatchPathListValueDetector are the same, as the same
        methods are used.
        """
        data = b" pid="
        t = time.time()
        match_context = DummyMatchContext(data + b"22")
        fdme = DummyFixedDataModelElement("s1", data)
        fdme2 = DummyFixedDataModelElement("s2", b"22")
        match_element = fdme.get_match_element("match", match_context)
        match_element2 = fdme2.get_match_element("match", match_context)
        mmpvd = MissingMatchPathValueDetector(self.aminer_config, ["match/s1"], [self.stream_printer_event_handler], learn_mode=True)
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), round(t), mmpvd)
        self.assertTrue(mmpvd.receive_atom(log_atom))
        mmpvd.do_persist()
        with open(mmpvd.persistence_file_name, "r") as f:
            self.assertEqual(f.readline(), f"""{{"string:[' pid=']": [{int(round(t, 0))}, {mmpvd.default_interval}, 0, "string:['match/s1']"]}}""")

        mmpvd.expected_values_dict = {}
        mmpvd.load_persistence_data()
        self.assertEqual(mmpvd.expected_values_dict, {"[' pid=']": [int(round(t, 0)), mmpvd.default_interval, 0, "['match/s1']"]})

        passed_time = 4000
        other_mmpvd = MissingMatchPathValueDetector(self.aminer_config, ["match/s1"], [self.stream_printer_event_handler], learn_mode=True)
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), round(t) + passed_time, other_mmpvd)
        self.assertTrue(other_mmpvd.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), self.expected_string % (datetime.fromtimestamp(log_atom.atom_time).strftime(self.datetime_format_string),
            mmpvd.__class__.__name__, 1, "['match/s1']: \"[' pid=']\" overdue 400s (interval 3600)"))
        self.reset_output_stream()

        # combine_values = False
        mmpvd = MissingMatchPathValueDetector(self.aminer_config, ["match/s1"], [self.stream_printer_event_handler], learn_mode=True, combine_values=False)
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), round(t), mmpvd)
        self.assertTrue(mmpvd.receive_atom(log_atom))
        mmpvd.do_persist()
        with open(mmpvd.persistence_file_name, "r") as f:
            self.assertEqual(f.readline(), f"""{{"string: pid=": [{int(round(t, 0))}, {mmpvd.default_interval}, 0, "string:match/s1"]}}""")

        mmpvd.expected_values_dict = {}
        mmpvd.load_persistence_data()
        self.assertEqual(mmpvd.expected_values_dict, {" pid=": [int(round(t, 0)), mmpvd.default_interval, 0, "match/s1"]})

        other_mmpvd = MissingMatchPathValueDetector(self.aminer_config, ["match/s1"], [self.stream_printer_event_handler], learn_mode=True)
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), round(t), other_mmpvd)
        self.assertTrue(other_mmpvd.receive_atom(log_atom))
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), round(t) + passed_time, other_mmpvd)
        self.assertTrue(other_mmpvd.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), self.expected_string % (datetime.fromtimestamp(log_atom.atom_time).strftime(self.datetime_format_string),
            mmpvd.__class__.__name__, 1, "['match/s1']: \"[' pid=']\" overdue 400s (interval 3600)"))
        self.reset_output_stream()

        # MissingMatchPathListValueDetector
        mmplvd = MissingMatchPathListValueDetector(self.aminer_config, ["match/s1", "match/s2"], [self.stream_printer_event_handler], learn_mode=True)
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), round(t), mmpvd)
        log_atom2 = LogAtom(fdme2.data, ParserMatch(match_element2), round(t), mmpvd)
        self.assertTrue(mmplvd.receive_atom(log_atom2))
        self.assertTrue(mmplvd.receive_atom(log_atom))
        mmplvd.do_persist()
        with open(mmplvd.persistence_file_name, "r") as f:
            self.assertEqual(f.readline(),f"""{{"string:22": [{int(round(t, 0))}, {mmplvd.default_interval}, 0, "string:match/s2"], "string: pid=": [{int(round(t, 0))}, {mmplvd.default_interval}, 0, "string:match/s1"]}}""")

        mmplvd.expected_values_dict = {}
        mmplvd.load_persistence_data()
        self.assertEqual(mmplvd.expected_values_dict, {" pid=": [int(round(t, 0)), mmplvd.default_interval, 0, "match/s1"], "22": [int(round(t, 0)), mmplvd.default_interval, 0, "match/s2"]})

        other_mmplvd = MissingMatchPathListValueDetector(self.aminer_config, ["match/s1", "match/s2"], [self.stream_printer_event_handler], learn_mode=True)
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), round(t), other_mmplvd)
        self.assertTrue(other_mmplvd.receive_atom(log_atom))
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), round(t) + passed_time, other_mmplvd)
        self.assertTrue(other_mmplvd.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), self.expected_string % (datetime.fromtimestamp(log_atom.atom_time).strftime(self.datetime_format_string),
            mmplvd.__class__.__name__, 1, "match/s1, match/s2: '22' overdue 400s (interval 3600)\n  match/s1, match/s2: ' pid=' overdue 400s (interval 3600)"))

    def test7validate_parameters(self):
        """
        Test all initialization parameters for the detector. Input parameters must be validated in the class.
        In this case the checks for MissingMatchPathValueDetector and MissingMatchPathListValueDetector are the same, as the same
        constructor is used.
        """
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, "default", [self.stream_printer_event_handler])
        self.assertRaises(ValueError, MissingMatchPathValueDetector, self.aminer_config, None, [self.stream_printer_event_handler])
        self.assertRaises(ValueError, MissingMatchPathValueDetector, self.aminer_config, [""], [self.stream_printer_event_handler])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, b"Default", [self.stream_printer_event_handler])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, True, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, 123, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, 123.3, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, {"id": "Default"}, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, (), [self.stream_printer_event_handler])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, set(), [self.stream_printer_event_handler])

        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], ["default"])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], None)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], "")
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], b"Default")
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], True)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], 123)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], 123.3)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], {"id": "Default"})
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], ())
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], set())

        self.assertRaises(ValueError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id="")
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=None)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=b"Default")
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=True)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=123)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=123.22)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id={"id": "Default"})
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=["Default"])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=[])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=())
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id=set())
        MissingMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], persistence_id="Default")

        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=b"True")
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode="True")
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=123)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=123.22)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode={"id": "Default"})
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=["Default"])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=[])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=())
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=set())
        MissingMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True)

        self.assertRaises(ValueError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, default_interval=-1)
        self.assertRaises(ValueError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, default_interval=0)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, default_interval=b"Default")
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, default_interval="123")
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, default_interval={"id": "Default"})
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, default_interval=["Default"])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, default_interval=[])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, default_interval=())
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, default_interval=set())
        MissingMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, default_interval=100)
        MissingMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, default_interval=100.22)

        self.assertRaises(ValueError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, realert_interval=-1)
        self.assertRaises(ValueError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, realert_interval=0)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, realert_interval=b"Default")
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, realert_interval="123")
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, realert_interval={"id": "Default"})
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, realert_interval=["Default"])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, realert_interval=[])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, realert_interval=())
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, realert_interval=set())
        MissingMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, realert_interval=100)
        MissingMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, realert_interval=100.22)

        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], combine_values=None)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], combine_values=b"True")
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], combine_values="True")
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], combine_values=123)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], combine_values=123.22)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], combine_values={"id": "Default"})
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], combine_values=["Default"])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], combine_values=[])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], combine_values=())
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], combine_values=set())
        MissingMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], combine_values=True)

        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=None)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=b"True")
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline="True")
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=123)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=123.22)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline={"id": "Default"})
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=["Default"])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=[])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=())
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=set())
        MissingMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], output_logline=True)

        self.assertRaises(ValueError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=-1)
        self.assertRaises(ValueError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=0)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=b"Default")
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time="123")
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time={"id": "Default"})
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=["Default"])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=[])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=())
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=set())
        MissingMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100)
        MissingMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100.22)

        self.assertRaises(ValueError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=-1)
        self.assertRaises(ValueError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=0)
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=b"Default")
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time="123")
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time={"id": "Default"})
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=["Default"])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=[])
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=())
        self.assertRaises(TypeError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=set())
        MissingMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=100)
        MissingMatchPathValueDetector(self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_no_anomaly_time=100.22)

        self.assertRaises(ValueError, MissingMatchPathValueDetector, self.aminer_config, ["path"], [self.stream_printer_event_handler], learn_mode=True, stop_learning_time=100, stop_learning_no_anomaly_time=100)


if __name__ == "__main__":
    unittest.main()
