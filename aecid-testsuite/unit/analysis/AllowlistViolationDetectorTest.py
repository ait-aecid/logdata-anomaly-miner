import unittest
from aminer.analysis.Rules import PathExistsMatchRule
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from aminer.analysis.AllowlistViolationDetector import AllowlistViolationDetector
from unit.TestBase import TestBase
from datetime import datetime
import time


class AllowlistViolationDetectorTest(TestBase):
    """Unittests for the AllowlistViolationDetector."""

    def test1receive_atom(self):
        """This test case checks if valid inputs are recognized."""
        fixed_string = b"fixed String"
        path_exists_match_rule = PathExistsMatchRule("match/s1", None)
        path_exists_match_rule2 = PathExistsMatchRule("match/s2", None)

        t = time.time()
        allowlist_violation_detector = AllowlistViolationDetector(self.aminer_config, [path_exists_match_rule, path_exists_match_rule2], [
            self.stream_printer_event_handler], output_logline=False)

        fixed_dme = FixedDataModelElement("s1", fixed_string)
        match_context = MatchContext(fixed_string)
        match_element = fixed_dme.get_match_element("match", match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), t, allowlist_violation_detector)

        self.assertTrue(allowlist_violation_detector.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), "")

        fixed_dme = FixedDataModelElement("s2", fixed_string)
        match_context = MatchContext(fixed_string)
        match_element = fixed_dme.get_match_element("match", match_context)
        log_atom = LogAtom(match_element.match_object, ParserMatch(match_element), t, allowlist_violation_detector)

        self.assertTrue(allowlist_violation_detector.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), "")

        fixed_dme = FixedDataModelElement("s3", fixed_string)
        match_context = MatchContext(fixed_string)
        match_element = fixed_dme.get_match_element("match", match_context)
        log_atom = LogAtom(match_element.match_object, ParserMatch(match_element), t, path_exists_match_rule)

        self.assertTrue(not allowlist_violation_detector.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), '%s No allowlisting for current atom\n%s: "None" (%d lines)\n  %s\n\n' % (
            datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"), allowlist_violation_detector.__class__.__name__, 1,
            "fixed String"))

    def test2validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        pem_rule = PathExistsMatchRule("match/s1", None)
        pem_rule2 = PathExistsMatchRule("match/s2", None)
        allowlist_rules = [pem_rule, pem_rule2]

        self.assertRaises(ValueError, AllowlistViolationDetector, self.aminer_config, [], [self.stream_printer_event_handler])
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, ["default"], [self.stream_printer_event_handler])
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, None, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, "", [self.stream_printer_event_handler])
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, b"Default", [self.stream_printer_event_handler])
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, True, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, 123, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, 123.3, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, {"id": "Default"}, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, (), [self.stream_printer_event_handler])
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, set(), [self.stream_printer_event_handler])

        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, ["default"])
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, None)
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, "")
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, b"Default")
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, True)
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, 123)
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, 123.3)
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, {"id": "Default"})
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, ())
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, set())

        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, [self.stream_printer_event_handler], output_logline=None)
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, [self.stream_printer_event_handler], output_logline=b"True")
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, [self.stream_printer_event_handler], output_logline="True")
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, [self.stream_printer_event_handler], output_logline=123)
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, [self.stream_printer_event_handler], output_logline=123.22)
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, [self.stream_printer_event_handler], output_logline={"id": "Default"})
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, [self.stream_printer_event_handler], output_logline=["Default"])
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, [self.stream_printer_event_handler], output_logline=[])
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, [self.stream_printer_event_handler], output_logline=())
        self.assertRaises(TypeError, AllowlistViolationDetector, self.aminer_config, allowlist_rules, [self.stream_printer_event_handler], output_logline=set())
        AllowlistViolationDetector(self.aminer_config, allowlist_rules, [self.stream_printer_event_handler], output_logline=True)
        AllowlistViolationDetector(self.aminer_config, allowlist_rules, [], output_logline=True)


if __name__ == "__main__":
    unittest.main()
