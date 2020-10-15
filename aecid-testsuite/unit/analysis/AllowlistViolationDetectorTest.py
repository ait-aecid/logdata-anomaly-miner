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
    __expected_string = '%s No allowlisting for current atom\n%s: "%s" (%d lines)\n  %s\n\n'
    fixed_string = b'fixed String'

    def test1match_found(self):
        """This test case checks if valid inputs are recognized."""
        description = "Test1AllowlistViolationDetector"
        path_exists_match_rule = PathExistsMatchRule('match/s1', None)
        path_exists_match_rule2 = PathExistsMatchRule('match/s2', None)

        t = time.time()
        allowlist_violation_detector = AllowlistViolationDetector(self.aminer_config, [path_exists_match_rule, path_exists_match_rule2], [
            self.stream_printer_event_handler], output_log_line=False)
        self.analysis_context.register_component(allowlist_violation_detector, description)

        fixed_dme = FixedDataModelElement('s1', self.fixed_string)
        match_context = MatchContext(self.fixed_string)
        match_element = fixed_dme.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), t, allowlist_violation_detector)

        self.assertTrue(allowlist_violation_detector.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), '')

        fixed_dme = FixedDataModelElement('s2', self.fixed_string)
        match_context = MatchContext(self.fixed_string)
        match_element = fixed_dme.get_match_element('match', match_context)
        log_atom = LogAtom(match_element.match_object, ParserMatch(match_element), t, allowlist_violation_detector)

        self.assertTrue(allowlist_violation_detector.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), '')

        fixed_dme = FixedDataModelElement('s3', self.fixed_string)
        match_context = MatchContext(self.fixed_string)
        match_element = fixed_dme.get_match_element('match', match_context)
        log_atom = LogAtom(match_element.match_object, ParserMatch(match_element), t, path_exists_match_rule)

        self.assertTrue(not allowlist_violation_detector.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"), allowlist_violation_detector.__class__.__name__, description, 1,
            "b'fixed String'"))


if __name__ == "__main__":
    unittest.main()
