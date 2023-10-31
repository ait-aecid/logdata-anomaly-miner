import unittest
import time
from datetime import datetime
from aminer.analysis.PathValueTimeIntervalDetector import PathValueTimeIntervalDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase
from aminer.AminerConfig import DEFAULT_PERSISTENCE_PERIOD


class PathValueTimeIntervalDetectorTest(TestBase):
    """Unittests for the PathValueTimeIntervalDetector."""

    def test1receive_atom(self):
        """
        Test if log atoms are processed correctly and the detector is learning (learn_mode=True) and stops if learn_mode=False.
        Test if stop_learning_time and stop_learning_no_anomaly_timestamp are implemented properly.
        """
        t = time.time()
        expected_string_first = '%s First time (%d) detected for [%s]\n%s: "None" (%d lines)\n  %s\n\n'
        expected_string_new = '%s New time (%d) out of range of previously observed times %s detected for [%s]\n%s: "None" (%d lines)\n  %s\n\n'
        dtf = "%Y-%m-%d %H:%M:%S"

        log_atom1 = LogAtom(b"1", ParserMatch(MatchElement("/model/id", b"1", b"1", None)), t, None)
        log_atom2 = LogAtom(b"1", ParserMatch(MatchElement("/model/value", b"1", b"1", None)), t, None)
        log_atom3 = LogAtom(b"3", ParserMatch(MatchElement("/model/id", b"3", b"3", None)), t, None)
        pvtid = PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], learn_mode=True, output_logline=False)

        pvtid.receive_atom(log_atom1)
        self.assertEqual(self.output_stream.getvalue(), expected_string_first % (datetime.fromtimestamp(t).strftime(dtf), int(t % pvtid.time_period_length), "1", pvtid.__class__.__name__, 1, "/model/id\n1"))
        self.reset_output_stream()
        appeared_time_list = {(log_atom1.raw_data.decode(),): [t % pvtid.time_period_length]}
        for i in range(10):
            log_atom1.atom_time += 1
            pvtid.receive_atom(log_atom1)
            appeared_time_list[(log_atom1.raw_data.decode(),)] += [log_atom1.atom_time % pvtid.time_period_length]
            if (i + 1) % pvtid.num_reduce_time_list == 0:
                appeared_time_list[(log_atom1.raw_data.decode(),)] = [appeared_time_list[(log_atom1.raw_data.decode(),)][0], appeared_time_list[(log_atom1.raw_data.decode(),)][-1]]
            self.assertEqual(pvtid.counter_reduce_time_intervals[(log_atom1.raw_data.decode(),)], (i+1) % pvtid.num_reduce_time_list)
            self.assertEqual(pvtid.appeared_time_list, appeared_time_list)
        log_atom1.atom_time = t + 100000
        pvtid.receive_atom(log_atom1)
        self.assertEqual(self.output_stream.getvalue(), expected_string_new % (datetime.fromtimestamp(t+100000).strftime(dtf), int((t+100000) % pvtid.time_period_length),
            [int(t % pvtid.time_period_length), int((t+10) % pvtid.time_period_length)], "1", pvtid.__class__.__name__, 1, "/model/id\n1"))
        self.reset_output_stream()
        log_atom1.atom_time = t

        # allow_missing_values_flag=False
        pvtid = PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], learn_mode=True, output_logline=False, allow_missing_values_flag=False)
        pvtid.receive_atom(log_atom1)
        self.assertEqual(self.output_stream.getvalue(), expected_string_first % (datetime.fromtimestamp(t).strftime(dtf), int(t % pvtid.time_period_length), "1", pvtid.__class__.__name__, 1, "/model/id\n1"))
        self.reset_output_stream()
        appeared_time_list = {(log_atom1.raw_data.decode(),): [t % pvtid.time_period_length]}
        for i in range(10):
            log_atom1.atom_time += 1
            pvtid.receive_atom(log_atom1)
            appeared_time_list[(log_atom1.raw_data.decode(),)] += [log_atom1.atom_time % pvtid.time_period_length]
            if (i + 1) % pvtid.num_reduce_time_list == 0:
                appeared_time_list[(log_atom1.raw_data.decode(),)] = [appeared_time_list[(log_atom1.raw_data.decode(),)][0], appeared_time_list[(log_atom1.raw_data.decode(),)][-1]]
            self.assertEqual(pvtid.counter_reduce_time_intervals[(log_atom1.raw_data.decode(),)], (i+1) % pvtid.num_reduce_time_list)
            self.assertEqual(pvtid.appeared_time_list, appeared_time_list)
        log_atom1.atom_time = t + 100000
        pvtid.receive_atom(log_atom1)
        self.assertEqual(self.output_stream.getvalue(), expected_string_new % (datetime.fromtimestamp(t+100000).strftime(dtf), int((t+100000) % pvtid.time_period_length),
            [int(t % pvtid.time_period_length), int((t+10) % pvtid.time_period_length)], "1", pvtid.__class__.__name__, 1, "/model/id\n1"))
        self.reset_output_stream()
        log_atom1.atom_time = t

        self.assertFalse(pvtid.receive_atom(log_atom2))

        # stop_learning_time
        pvtid = PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=100)
        self.assertTrue(pvtid.receive_atom(log_atom1))
        log_atom1.atom_time = t + 99
        self.assertTrue(pvtid.receive_atom(log_atom1))
        self.assertTrue(pvtid.learn_mode)
        log_atom1.atom_time = t + 101
        self.assertTrue(pvtid.receive_atom(log_atom1))
        self.assertFalse(pvtid.learn_mode)

        # stop_learning_no_anomaly_time
        pvtid = PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=100)
        log_atom1.atom_time = t
        self.assertTrue(pvtid.receive_atom(log_atom1))
        log_atom3.atom_time = t + 100
        self.assertTrue(pvtid.receive_atom(log_atom3))
        self.assertTrue(pvtid.learn_mode)
        log_atom2.atom_time = t + 100
        self.assertTrue(pvtid.receive_atom(log_atom2))
        self.assertTrue(pvtid.learn_mode)
        log_atom1.atom_time = t + 200
        self.assertTrue(pvtid.receive_atom(log_atom1))
        self.assertTrue(pvtid.learn_mode)
        log_atom1.atom_time = t + 201
        self.assertTrue(pvtid.receive_atom(log_atom1))
        self.assertFalse(pvtid.learn_mode)

    def test2do_timer(self):
        """Test if the do_timer method is implemented properly."""
        pvtid = PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"])
        t = time.time()
        pvtid.next_persist_time = t + 400
        self.assertEqual(pvtid.do_timer(t + 200), 200)
        self.assertEqual(pvtid.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(pvtid.do_timer(t + 999), 1)
        self.assertEqual(pvtid.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

    def test3persistence(self):
        """Test the do_persist and load_persistence_data methods."""
        t = time.time()
        log_atom1 = LogAtom(b"1", ParserMatch(MatchElement("/model/id", b"1", b"1", None)), t, None)
        pvtid = PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/id"], learn_mode=True, output_logline=False)

        pvtid.receive_atom(log_atom1)
        appeared_time_list = {(log_atom1.raw_data.decode(),): [t % pvtid.time_period_length]}
        for i in range(10):
            log_atom1.atom_time += 1
            pvtid.receive_atom(log_atom1)
            appeared_time_list[(log_atom1.raw_data.decode(),)] += [log_atom1.atom_time % pvtid.time_period_length]
            if (i + 1) % pvtid.num_reduce_time_list == 0:
                appeared_time_list[(log_atom1.raw_data.decode(),)] = [appeared_time_list[(log_atom1.raw_data.decode(),)][0], appeared_time_list[(log_atom1.raw_data.decode(),)][-1]]
        log_atom1.atom_time = t + 100000
        appeared_time_list[(log_atom1.raw_data.decode(),)] += [log_atom1.atom_time % pvtid.time_period_length]
        pvtid.receive_atom(log_atom1)
        pvtid.do_persist()
        with open(pvtid.persistence_file_name, "r") as f:
            self.assertEqual(f.read(), f'[[[["string:1"], {appeared_time_list[(log_atom1.raw_data.decode(),)]}]], [[["string:1"], 1]]]')
        self.assertEqual(pvtid.counter_reduce_time_intervals[(log_atom1.raw_data.decode(),)], 1)
        self.assertEqual(pvtid.appeared_time_list, appeared_time_list)
        pvtid.appeared_time_list = {}
        pvtid.counter_reduce_time_intervals = {}
        pvtid.load_persistence_data()
        self.assertEqual(pvtid.counter_reduce_time_intervals[(log_atom1.raw_data.decode(),)], 1)
        self.assertEqual(pvtid.appeared_time_list, appeared_time_list)

        other = PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], target_path_list=["/model/value"], learn_mode=True)
        self.assertEqual(other.counter_reduce_time_intervals, pvtid.counter_reduce_time_intervals)
        self.assertEqual(other.appeared_time_list, pvtid.appeared_time_list)

    def test4add_to_persistence_event(self):
        pvtid = PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"])
        pvtid.add_to_persistence_event("Analysis.PathValueTimeIntervalDetector", [["a"], 3.0])
        self.assertEqual(pvtid.counter_reduce_time_intervals, {('a',): 0})
        self.assertEqual(pvtid.appeared_time_list, {('a',): [3.0]})

    def test5remove_from_persistence_event(self):
        pvtid = PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"])
        pvtid.counter_reduce_time_intervals =  {('a',): 0}
        pvtid.appeared_time_list =  {('a',): [3.0]}
        pvtid.remove_from_persistence_event("Analysis.PathValueTimeIntervalDetector", [["a"], 3.0])
        self.assertEqual(pvtid.counter_reduce_time_intervals, {('a',): 0})
        self.assertEqual(pvtid.appeared_time_list, {('a',): []})

    def test6validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, ["default"], ["/model/value"])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, None, ["/model/value"])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, "", ["/model/value"])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, b"Default", ["/model/value"])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, True, ["/model/value"])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, 123, ["/model/value"])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, 123.3, ["/model/value"])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, {"id": "Default"}, ["/model/value"])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, (), ["/model/value"])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, set(), ["/model/value"])

        self.assertRaises(ValueError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], [""])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], [None])
        self.assertRaises(ValueError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], None)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], "")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], b"Default")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], True)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], 123)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], 123.3)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], {"id": "Default"})
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ())
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], set())

        self.assertRaises(ValueError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id="")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id=None)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id=b"Default")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id=True)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id=123)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id=123.22)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id={"id": "Default"})
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id=["Default"])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id=[])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id=())
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id=set())
        PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], persistence_id="Default")

        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_values_flag=b"True")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_values_flag="True")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_values_flag=123)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_values_flag=123.22)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_values_flag={"id": "Default"})
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_values_flag=["Default"])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_values_flag=[])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_values_flag=())
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_values_flag=set())
        PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], allow_missing_values_flag=True)

        self.assertRaises(ValueError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list=[""])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list="")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list=b"Default")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list=True)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list=123)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list=123.3)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list={"id": "Default"})
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list=())
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list=set())
        PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list=[])
        PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], ignore_list=None)

        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline=None)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline=b"True")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline="True")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline=123)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline=123.22)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline={"id": "Default"})
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline=["Default"])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline=[])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline=())
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline=set())
        PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], output_logline=True)

        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=b"True")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode="True")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=123)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=123.22)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode={"id": "Default"})
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=["Default"])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=[])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=())
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=set())
        PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True)

        self.assertRaises(ValueError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_period_length=-1)
        self.assertRaises(ValueError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_period_length=0)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_period_length=100.22)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_period_length=b"Default")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_period_length="123")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_period_length={"id": "Default"})
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_period_length=["Default"])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_period_length=[])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_period_length=())
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_period_length=set())
        PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], time_period_length=100)

        self.assertRaises(ValueError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], max_time_diff=-1)
        self.assertRaises(ValueError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], max_time_diff=0)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], max_time_diff=100.22)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], max_time_diff=b"Default")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], max_time_diff="123")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], max_time_diff={"id": "Default"})
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], max_time_diff=["Default"])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], max_time_diff=[])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], max_time_diff=())
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], max_time_diff=set())
        PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], max_time_diff=100)

        self.assertRaises(ValueError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_reduce_time_list=-1)
        self.assertRaises(ValueError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_reduce_time_list=0)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_reduce_time_list=100.22)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_reduce_time_list=b"Default")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_reduce_time_list="123")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_reduce_time_list={"id": "Default"})
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_reduce_time_list=["Default"])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_reduce_time_list=[])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_reduce_time_list=())
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_reduce_time_list=set())
        PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], num_reduce_time_list=100)

        self.assertRaises(ValueError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=-1)
        self.assertRaises(ValueError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=0)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=b"Default")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time="123")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time={"id": "Default"})
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=["Default"])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=[])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=())
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=set())
        PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=100)
        PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=100.22)

        self.assertRaises(ValueError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=-1)
        self.assertRaises(ValueError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=0)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=b"Default")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time="123")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time={"id": "Default"})
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=["Default"])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=[])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=())
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=set())
        PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=100)
        PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=100.22)

        self.assertRaises(ValueError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], learn_mode=True, stop_learning_time=100, stop_learning_no_anomaly_time=100)

        self.assertRaises(ValueError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list=["/tmp/syslog"])
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list="")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list=b"Default")
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list=True)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list=123)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list=123.22)
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list={"id": "Default"})
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list=())
        self.assertRaises(TypeError, PathValueTimeIntervalDetector, self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list=set())
        PathValueTimeIntervalDetector(self.aminer_config, [self.stream_printer_event_handler], ["/model/value"], log_resource_ignore_list=["file:///tmp/syslog"])


if __name__ == "__main__":
    unittest.main()
