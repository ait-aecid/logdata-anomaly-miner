import unittest
from unit.TestBase import TestBase, DummyMatchContext, DummyFixedDataModelElement, DummyNumberModelElement, DummyFirstMatchModelElement
from aminer.analysis.TimeCorrelationDetector import TimeCorrelationDetector
import time
import random
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from datetime import datetime


class TimeCorrelationDetectorTest(TestBase):
    """Unittests for the TimeCorrlelationDetectorTest."""
    match_context1 = DummyMatchContext(b" pid=")
    fdme1 = DummyFixedDataModelElement("s1", b" pid=")
    match_element1 = fdme1.get_match_element("", match_context1)

    match_context2 = DummyMatchContext(b"25537 uid=2")
    fdme2 = DummyFixedDataModelElement("d1", b"25537")
    match_element2 = fdme2.get_match_element("", match_context2)

    def test1receive_atom(self):
        """Test if log atoms are processed correctly and new rules are created."""
        expected_string = '%s Correlation report\nTimeCorrelationDetector: "None" (%d lines)\n  '
        dtf = "%Y-%m-%d %H:%M:%S"
        t = time.time()
        string = b"ddd 25537 uid=2"
        fdme = DummyFixedDataModelElement("s1", string)
        nme = DummyNumberModelElement("d1")
        fmme = DummyFirstMatchModelElement("f1", [fdme, nme])

        # test different parallel_check_count values
        record_count = 70
        record_count_path = 100
        record_count_value = 50
        for i in [1, 2, 10]:
            tcd = TimeCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], i, record_count_before_event=record_count, max_rule_attributes=1)
            tcd_path = TimeCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], i, record_count_before_event=record_count_path, use_path_match=True, use_value_match=False, max_rule_attributes=5)
            tcd_value = TimeCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], i, record_count_before_event=record_count_value, use_path_match=False, use_value_match=True, max_rule_attributes=15)
            for j in range(1, 201):
                pos = random.randint(0, 1)
                data = [string, b"%d" % j][pos]
                match_context = DummyMatchContext(data)
                match_element = fmme.get_match_element("first", match_context)
                log_atom = LogAtom(data, ParserMatch(match_element), t, tcd)
                self.assertTrue(tcd.receive_atom(log_atom))
                if j != 0 and j % record_count == 0:
                    self.assertTrue(self.output_stream.getvalue().startswith(expected_string % (datetime.fromtimestamp(t).strftime(dtf), j)))
                    self.assertEqual(self.output_stream.getvalue().count("\n"), i*(i+1)+4)
                    self.reset_output_stream()
                self.assertTrue(tcd_path.receive_atom(log_atom))
                if j != 0 and j % record_count_path == 0:
                    self.assertFalse("value" in self.output_stream.getvalue())
                    self.reset_output_stream()
                self.assertTrue(tcd_value.receive_atom(log_atom))
                if j != 0 and j % record_count_value == 0:
                    self.assertFalse("hasPath" in self.output_stream.getvalue())
                    self.reset_output_stream()
                else:
                    self.assertEqual(self.output_stream.getvalue(), "")

    def test2validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, ["default"], 2)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, None, 2)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, "", 2)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, b"Default", 2)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, True, 2)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, 123, 2)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, 123.3, 2)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, {"id": "Default"}, 2)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, (), 2)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, set(), 2)

        self.assertRaises(ValueError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 0)
        self.assertRaises(ValueError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], -1)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], ["default"])
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], None)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], "")
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], b"Default")
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], True)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 123.3)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], {"id": "Default"})
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], ())
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], set())

        self.assertRaises(ValueError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, persistence_id="")
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, persistence_id=None)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, persistence_id=b"Default")
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, persistence_id=True)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, persistence_id=123)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, persistence_id=123.22)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, persistence_id={"id": "Default"})
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, persistence_id=["Default"])
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, persistence_id=[])
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, persistence_id=())
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, persistence_id=set())
        TimeCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], 2, persistence_id="Default")

        self.assertRaises(ValueError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, record_count_before_event=0)
        self.assertRaises(ValueError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, record_count_before_event=-1)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, record_count_before_event=["default"])
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, record_count_before_event=None)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, record_count_before_event="")
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, record_count_before_event=b"Default")
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, record_count_before_event=True)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, record_count_before_event=123.3)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, record_count_before_event={"id": "Default"})
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, record_count_before_event=())
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, record_count_before_event=set())
        TimeCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], 2, record_count_before_event=2)

        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, output_logline=None)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, output_logline=b"True")
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, output_logline="True")
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, output_logline=123)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, output_logline=123.22)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, output_logline={"id": "Default"})
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, output_logline=["Default"])
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, output_logline=[])
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, output_logline=())
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, output_logline=set())
        TimeCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], 2, output_logline=True)

        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, use_path_match=b"True")
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, use_path_match="True")
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, use_path_match=123)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, use_path_match=123.22)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, use_path_match={"id": "Default"})
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, use_path_match=["Default"])
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, use_path_match=[])
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, use_path_match=())
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, use_path_match=set())
        TimeCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], 2, use_path_match=True)

        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, use_value_match=b"True")
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, use_value_match="True")
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, use_value_match=123)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, use_value_match=123.22)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, use_value_match={"id": "Default"})
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, use_value_match=["Default"])
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, use_value_match=[])
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, use_value_match=())
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, use_value_match=set())
        TimeCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], 2, use_value_match=True)

        self.assertRaises(ValueError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, min_rule_attributes=0)
        self.assertRaises(ValueError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, min_rule_attributes=-1)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, min_rule_attributes=["default"])
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, min_rule_attributes=None)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, min_rule_attributes="")
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, min_rule_attributes=b"Default")
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, min_rule_attributes=True)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, min_rule_attributes=123.3)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, min_rule_attributes={"id": "Default"})
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, min_rule_attributes=())
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, min_rule_attributes=set())
        TimeCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], 2, min_rule_attributes=2)

        self.assertRaises(ValueError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, max_rule_attributes=0)
        self.assertRaises(ValueError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, max_rule_attributes=-1)
        self.assertRaises(ValueError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, min_rule_attributes=2, max_rule_attributes=1)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, max_rule_attributes=["default"])
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, max_rule_attributes=None)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, max_rule_attributes="")
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, max_rule_attributes=b"Default")
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, max_rule_attributes=True)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, max_rule_attributes=123.3)
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, max_rule_attributes={"id": "Default"})
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, max_rule_attributes=())
        self.assertRaises(TypeError, TimeCorrelationDetector, self.aminer_config, [self.stream_printer_event_handler], 2, max_rule_attributes=set())
        TimeCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], 2, max_rule_attributes=2)
        TimeCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], 2, min_rule_attributes=1, max_rule_attributes=1)


if __name__ == "__main__":
    unittest.main()
