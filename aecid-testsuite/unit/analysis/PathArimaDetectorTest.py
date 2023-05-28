import unittest
import time
from datetime import datetime
from aminer.analysis.PathArimaDetector import PathArimaDetector
from aminer.analysis.EventTypeDetector import EventTypeDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummyFirstMatchModelElement, DummyMatchContext
from aminer.AminerConfig import DEFAULT_PERSISTENCE_PERIOD
from aminer.analysis.EventCorrelationDetector import EventCorrelationDetector, set_random_seed
import random


class PathArimaDetectorTest(TestBase):
    """Unittests for the PathArimaDetector."""

    def test1receive_atom(self):
        """
        This test case checks the normal detection of new sequences. The ESD is used to detect value sequences of length 2 and uses one id
        path to cope with interleaving sequences, i.e., the sequences only make sense when logs that contain the same id are considered.
        Test if log atoms are processed correctly and the detector is learning (learn_mode=True) and stops if learn_mode=False.
        Test if stop_learning_time and stop_learning_no_anomaly_timestamp are implemented properly.
        """
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        pad = PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, output_logline=False)
        self.run_pad_test(pad, etd, self.data)

        # target_path_list
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler], target_path_list=["/model/value"])
        pad = PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=["/model/value"], learn_mode=True, output_logline=False)
        self.run_pad_test(pad, etd, self.data)

        # stop_learning_time
        t = time.time()
        log_atom1 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t, None)
        log_atom2 = LogAtom(b"b", ParserMatch(MatchElement("/value", b"b", b"b", None)), t, None)
        log_atom3 = LogAtom(b"a", ParserMatch(MatchElement("/value", b"a", b"a", None)), t, None)
        pad = PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=["/model/value"], learn_mode=True, stop_learning_time=100)
        self.assertTrue(pad.receive_atom(log_atom1))
        log_atom1.atom_time = t + 99
        self.assertTrue(pad.receive_atom(log_atom1))
        self.assertTrue(pad.learn_mode)
        log_atom1.atom_time = t + 101
        self.assertTrue(pad.receive_atom(log_atom1))
        self.assertFalse(pad.learn_mode)

        # stop_learning_no_anomaly_time
        pad = PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=["/model/value"], learn_mode=True, stop_learning_no_anomaly_time=100)
        log_atom1.atom_time = t
        self.assertTrue(pad.receive_atom(log_atom1))
        log_atom1.atom_time = t + 100
        self.assertTrue(pad.receive_atom(log_atom1))
        self.assertTrue(pad.learn_mode)
        log_atom2.atom_time = t + 100
        self.assertTrue(pad.receive_atom(log_atom2))
        self.assertTrue(pad.learn_mode)
        log_atom1.atom_time = t + 200
        self.assertTrue(pad.receive_atom(log_atom3))
        self.assertTrue(pad.learn_mode)
        log_atom1.atom_time = t + 201
        self.assertTrue(pad.receive_atom(log_atom1))
        self.assertFalse(pad.learn_mode)

    def test2do_timer(self):
        """Test if the do_timer method is implemented properly."""
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        pad = PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd)
        t = time.time()
        pad.next_persist_time = t + 400
        self.assertEqual(pad.do_timer(t + 200), 200)
        self.assertEqual(pad.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(pad.do_timer(t + 999), 1)
        self.assertEqual(pad.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

    def test3persistence(self):
        """Test the do_persist and load_persistence_data methods."""
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        pad = PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, output_logline=False)
        self.run_pad_test(pad, etd, self.data)
        pad.do_persist()
        with open(pad.persistence_file_name, "r") as f:
            self.assertEqual(f.read(), '[[[], null], [[], null], [[]]]')

        self.assertEqual(pad.target_path_index_list, [[], None])
        self.assertEqual(pad.period_length_list, [[], None])
        self.assertEqual(pad.prediction_history, [[]])
        pad.target_path_index_list = []
        pad.period_length_list = []
        pad.prediction_history = []
        pad.load_persistence_data()
        self.assertEqual(pad.target_path_index_list, [[], None])
        self.assertEqual(pad.period_length_list, [[], None])
        self.assertEqual(pad.prediction_history, [[]])

        other = PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True)
        self.assertEqual(other.target_path_index_list, pad.target_path_index_list)
        self.assertEqual(other.period_length_list, pad.period_length_list)
        self.assertEqual(other.prediction_history, pad.prediction_history)

    def test4validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        etd = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler], save_values=False)
        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd)
        etd.save_values = True
        old_val = etd.min_num_vals
        etd.min_num_vals = 10
        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd)
        etd.min_num_vals = old_val
        old_val = etd.max_num_vals
        etd.max_num_vals = 10
        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd)
        etd.max_num_vals = old_val

        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, ["default"], etd)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, None, etd)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, "", etd)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, b"Default", etd)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, True, etd)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, 123, etd)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, 123.3, etd)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, {"id": "Default"}, etd)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, (), etd)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, set(), etd)

        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id="")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id=None)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id=b"Default")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id=True)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id=123)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id=123.22)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id={"id": "Default"})
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id=["Default"])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id=[])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id=())
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id=set())
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, persistence_id="Default")

        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=[""])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list="")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=b"Default")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=True)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=123)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=123.3)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list={"id": "Default"})
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=())
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=set())
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=[])
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, target_path_list=None)

        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline=None)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline=b"True")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline="True")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline=123)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline=123.22)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline={"id": "Default"})
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline=["Default"])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline=[])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline=())
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, output_logline=set())
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, output_logline=True)

        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=b"True")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode="True")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=123)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=123.22)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode={"id": "Default"})
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=["Default"])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=[])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=())
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=set())
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True)

        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init=-1)
        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init=0)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init=100.22)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init=b"Default")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init="123")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init={"id": "Default"})
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init=["Default"])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init=[])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init=())
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_init=set())
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_init=100)

        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, force_period_length=b"True")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, force_period_length="True")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, force_period_length=123)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, force_period_length=123.22)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, force_period_length={"id": "Default"})
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, force_period_length=["Default"])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, force_period_length=[])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, force_period_length=())
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, force_period_length=set())
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, force_period_length=True)

        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, set_period_length=-1)
        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, set_period_length=0)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, set_period_length=100.22)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, set_period_length=b"Default")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, set_period_length="123")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, set_period_length={"id": "Default"})
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, set_period_length=["Default"])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, set_period_length=[])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, set_period_length=())
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, set_period_length=set())
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, set_period_length=100)

        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, alpha=-1)
        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, alpha=1.1)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, alpha=b"Default")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, alpha="123")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, alpha={"id": "Default"})
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, alpha=["Default"])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, alpha=[])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, alpha=())
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, alpha=set())
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, alpha=0)
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, alpha=0.5)
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, alpha=1)

        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, alpha_bt=-1)
        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, alpha_bt=1.1)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, alpha_bt=b"Default")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, alpha_bt="123")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, alpha_bt={"id": "Default"})
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, alpha_bt=["Default"])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, alpha_bt=[])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, alpha_bt=())
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, alpha_bt=set())
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, alpha_bt=0)
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, alpha_bt=0.5)
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, alpha_bt=1)

        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_results_bt=-1)
        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_results_bt=0)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_results_bt=100.22)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_results_bt=b"Default")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_results_bt="123")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_results_bt={"id": "Default"})
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_results_bt=["Default"])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_results_bt=[])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_results_bt=())
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_results_bt=set())
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_results_bt=100)

        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_min_time_history=-1)
        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_min_time_history=0)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_min_time_history=b"Default")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_min_time_history="123")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_min_time_history={"id": "Default"})
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_min_time_history=["Default"])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_min_time_history=[])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_min_time_history=())
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_min_time_history=set())

        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_max_time_history=-1)
        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_max_time_history=0)
        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_min_time_history=30, num_max_time_history=20)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_max_time_history=b"Default")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_max_time_history="123")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_max_time_history={"id": "Default"})
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_max_time_history=["Default"])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_max_time_history=[])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_max_time_history=())
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_max_time_history=set())
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_min_time_history=20, num_max_time_history=100)
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_min_time_history=20.1, num_max_time_history=100.1)

        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_periods_tsa_ini=-1)
        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_periods_tsa_ini=0)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_periods_tsa_ini=100.22)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_periods_tsa_ini=b"Default")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_periods_tsa_ini="123")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_periods_tsa_ini={"id": "Default"})
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_periods_tsa_ini=["Default"])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_periods_tsa_ini=[])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_periods_tsa_ini=())
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, num_periods_tsa_ini=set())
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, num_periods_tsa_ini=20)

        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=-1)
        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=0)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=b"Default")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time="123")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time={"id": "Default"})
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=["Default"])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=[])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=())
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=set())
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=100)
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=100.22)

        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time=-1)
        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time=0)
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time=b"Default")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time="123")
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time={"id": "Default"})
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time=["Default"])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time=[])
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time=())
        self.assertRaises(TypeError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time=set())
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time=100)
        PathArimaDetector(self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_no_anomaly_time=100.22)

        self.assertRaises(ValueError, PathArimaDetector, self.aminer_config, [self.stream_printer_event_handler], etd, learn_mode=True, stop_learning_time=100, stop_learning_no_anomaly_time=100)

    @classmethod
    def setUpClass(cls):
        """Set up the data for the all tests."""
        cls.alphabet = b"abcdefghijklmnopqrstuvwxyz"
        cls.analysis = "Analysis.%s"
        children = []
        for _, val in enumerate(cls.alphabet):
            char = bytes([val])
            children.append(DummyFixedDataModelElement("value", char))
        cls.alphabet_model = DummyFirstMatchModelElement("first", children)
        cls.data = cls.generate_data(cls, 120, 1)
        set_random_seed(42)

    def run_pad_test(self, pad, etd, log_atoms):
        """Run the ECD test."""
        for log_atom in log_atoms:
            etd.receive_atom(log_atom)
            pad.receive_atom(log_atom)
        self.assertTrue(pad.arima_models)

    def generate_data(self, iterations, diff):
        """Generate data without any error."""
        log_atoms = []
        t = time.time()
        for i in range(1, iterations+1):
            char = bytes([self.alphabet[i % len(self.alphabet)]])
            t += diff
            num = str(random.uniform(0, 1000)).encode()
            m1 = MatchElement("/model/id", num, num, None)
            m2 = MatchElement("/model/value", char, char, None)
            log_atoms.append(LogAtom(num + char, ParserMatch(MatchElement("/model", num + char, num + char, [m1, m2])), t + 1, None))
        return log_atoms


if __name__ == "__main__":
    unittest.main()
