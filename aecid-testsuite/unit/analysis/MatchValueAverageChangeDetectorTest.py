import unittest
from aminer.analysis.MatchValueAverageChangeDetector import MatchValueAverageChangeDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase, DummySequenceModelElement, DummyNumberModelElement, DummyFixedDataModelElement, DummyMatchContext
import time
import math
from aminer.AminerConfig import DEFAULT_PERSISTENCE_PERIOD


class MatchValueAverageChangeDetectorTest(TestBase):
    """Unittests for the MatchValueAverageChangeDetector."""

    def test1receive_atom(self):
        """Test if log atoms are processed correctly."""
        start_time = 30
        cron_job1 = "match/cron/job1"
        cron_job2 = "match/cron/job2"
        parsing_model = DummySequenceModelElement("cron", [DummyNumberModelElement("job1"), DummyFixedDataModelElement("sp", b" "), DummyNumberModelElement("job2")])

        # verify that no statistic evaluation is performed, until the minimal amount of bin elements is reached.
        # first is initial generation of the bins.
        mvacd = MatchValueAverageChangeDetector(self.aminer_config, [self.stream_printer_event_handler], None, [cron_job1], 10, start_time, False, "Default")
        for i in range(1, 41):
            t = start_time + math.pow(i, 7)
            match_context = DummyMatchContext(b"%d %d" % (t, start_time + i))
            match_element = parsing_model.get_match_element("match", match_context)
            log_atom = LogAtom(match_element.get_match_object(), ParserMatch(match_element), start_time + i, mvacd)
            mvacd.receive_atom(log_atom)
            if i < mvacd.min_bin_elements * 2 or i % mvacd.min_bin_elements != 0:
                self.assertEqual(self.output_stream.getvalue(), "")
            else:
                self.assertNotEqual(self.output_stream.getvalue(), "")
                self.reset_output_stream()

        # verify that no statistic evaluation is performed, until the start time is reached.
        mvacd = MatchValueAverageChangeDetector(self.aminer_config, [self.stream_printer_event_handler], cron_job2, [cron_job1], 10, start_time, False, "Default")
        for i in range(41):
            t = start_time + math.pow(i, 7)
            match_context = DummyMatchContext(b"%d %d" % (t, i))
            match_element = parsing_model.get_match_element("match", match_context)
            log_atom = LogAtom(match_element.get_match_object(), ParserMatch(match_element), i, mvacd)
            mvacd.receive_atom(log_atom)
            if i <= 30 or i < mvacd.min_bin_elements * 2 or i % mvacd.min_bin_elements != 0:
                self.assertEqual(self.output_stream.getvalue(), "")
            else:
                self.assertNotEqual(self.output_stream.getvalue(), "")
                self.reset_output_stream()

        mvacd = MatchValueAverageChangeDetector(self.aminer_config, [self.stream_printer_event_handler], None, [cron_job1, cron_job2], 10, start_time, False, "Default")
        for i in range(1, 41):
            t = start_time + math.pow(i, 7)
            t1 = start_time + math.pow(i, 4)
            match_context = DummyMatchContext(b"%d %d" % (t, t1))
            match_element = parsing_model.get_match_element("match", match_context)
            log_atom = LogAtom(match_element.get_match_object(), ParserMatch(match_element), t1, mvacd)
            mvacd.receive_atom(log_atom)
            if i < mvacd.min_bin_elements * 2 or i % mvacd.min_bin_elements != 0:
                self.assertEqual(self.output_stream.getvalue(), "")
            else:
                self.assertNotEqual(self.output_stream.getvalue(), "")
                self.reset_output_stream()

    def test2do_timer(self):
        """Test if the do_timer method is implemented properly."""
        mvacd = MatchValueAverageChangeDetector(self.aminer_config, [self.stream_printer_event_handler], None, ["cron/job1"], 3, 57600, False, "Default")
        t = time.time()
        mvacd.next_persist_time = t + 400
        self.assertEqual(mvacd.do_timer(t + 200), 200)
        self.assertEqual(mvacd.do_timer(t + 400), DEFAULT_PERSISTENCE_PERIOD)
        self.assertEqual(mvacd.do_timer(t + 999), 1)
        self.assertEqual(mvacd.do_timer(t + 1000), DEFAULT_PERSISTENCE_PERIOD)

    def test3persistence(self):
        """Test the do_persist and load_persistence_data methods."""
        mvacd = MatchValueAverageChangeDetector(self.aminer_config, [self.stream_printer_event_handler], None, ["cron/job1"], 3, 57600, False, "Default")
        mvacd.stat_data = [("cron/job1", [57600, 57600, (3, 3000.0, 5000000.0, 1000.0, 1000000.0), (2, 30000.0, 500000000.0)])]
        mvacd.do_persist()
        with open(mvacd.persistence_file_name, "r") as f:
            self.assertEqual(f.read(), '[["string:cron/job1", [57600, 57600, [3, 3000.0, 5000000.0, 1000.0, 1000000.0], [2, 30000.0, 500000000.0]]]]')

        mvacd.stat_data = []
        mvacd.load_persistence_data()
        self.assertEqual(mvacd.stat_data, [("cron/job1", [57600, 57600, (3, 3000.0, 5000000.0, 1000.0, 1000000.0), (2, 30000.0, 500000000.0)])])

        other = MatchValueAverageChangeDetector(self.aminer_config, [self.stream_printer_event_handler], None, ["cron/job1"], 3, 57600, False, "Default")
        self.assertEqual(mvacd.stat_data, other.stat_data)

    def test4validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, ["default"], None, ["/path"], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, None, None, ["/path"], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, "", None, ["/path"], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, b"Default", None, ["/path"], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, True, None, ["/path"], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, 123, None, ["/path"], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, 123.3, None, ["/path"], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, {"id": "Default"}, None, ["/path"], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, (), None, ["/path"], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, set(), None, ["/path"], 3, 1)

        self.assertRaises(ValueError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], "", ["/path"], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], 123, ["/path"], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], 123.2, ["/path"], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], b"", ["/path"], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], b"default", ["/path"], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], {"id": "Default"}, ["/path"], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], ["Default"], ["/path"], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], [], ["/path"], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], (), ["/path"], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], set(), ["/path"], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], True, ["/path"], 3, 1)

        self.assertRaises(ValueError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, [], 3, 1)
        self.assertRaises(ValueError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, [""], 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, "", 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, 123, 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, 123.2, 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, b"default", 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, {"id": "Default"}, 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, (), 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, set(), 3, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, True, 3, 1)

        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], None, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], "3", 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], b"3", 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], {"id": 3}, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], [3], 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], [], 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], (), 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], set(), 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], True, 1)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 123.3, 1)
        self.assertRaises(ValueError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], -1, 1)
        self.assertRaises(ValueError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 0, 1)

        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, None)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, "1")
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, b"1")
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, {"id": 1})
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, [1])
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, ())
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, set())
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, True)
        self.assertRaises(ValueError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, -1)
        self.assertRaises(ValueError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 0)
        MatchValueAverageChangeDetector(self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1)
        MatchValueAverageChangeDetector(self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1.2)

        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, debug_mode=None)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, debug_mode=b"True")
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, debug_mode="True")
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, debug_mode=123)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, debug_mode=123.22)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, debug_mode={"id": "Default"})
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, debug_mode=["Default"])
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, debug_mode=[])
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, debug_mode=())
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, debug_mode=set())
        MatchValueAverageChangeDetector(self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, debug_mode=True)

        self.assertRaises(ValueError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, persistence_id="")
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, persistence_id=None)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, persistence_id=b"Default")
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, persistence_id=True)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, persistence_id=123)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, persistence_id=123.22)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, persistence_id={"id": "Default"})
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, persistence_id=["Default"])
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, persistence_id=[])
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, persistence_id=())
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, persistence_id=set())
        MatchValueAverageChangeDetector(self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, persistence_id="Default")

        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, output_logline=None)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, output_logline=b"True")
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, output_logline="True")
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, output_logline=123)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, output_logline=123.22)
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, output_logline={"id": "Default"})
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, output_logline=["Default"])
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, output_logline=[])
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, output_logline=())
        self.assertRaises(TypeError, MatchValueAverageChangeDetector, self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, output_logline=set())
        MatchValueAverageChangeDetector(self.aminer_config, [self.stream_printer_event_handler], None, ["/path"], 3, 1, output_logline=True)


if __name__ == "__main__":
    unittest.main()
