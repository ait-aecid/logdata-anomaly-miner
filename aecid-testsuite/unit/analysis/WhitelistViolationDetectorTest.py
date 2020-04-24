import unittest
from aminer.analysis.Rules import PathExistsMatchRule
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from aminer.analysis.WhitelistViolationDetector import WhitelistViolationDetector
from unit.TestBase import TestBase
from datetime import datetime
import time

class WhitelistViolationDetectorTest(TestBase):
    __expected_string = '%s No whitelisting for current atom\n%s: "%s" (%d lines)\n  %s\n\n'
    
    fixed_string = b'fixed String'

    '''
    This test case checks if valid inputs are recognized.
    '''
    def test1match_found(self):
      description = "Test1WhitelistViolationDetector"
      self.path_exists_match_rule = PathExistsMatchRule('match/s1', None)
      self.path_exists_match_rule2 = PathExistsMatchRule('match/s2', None)
      
      t = time.time()
      self.whitelist_violation_detector = WhitelistViolationDetector(self.aminer_config,
        [self.path_exists_match_rule, self.path_exists_match_rule2], [self.stream_printer_event_handler], output_log_line=False)
      self.analysis_context.register_component(self.whitelist_violation_detector, description)
      
      self.fixed_dme = FixedDataModelElement('s1', self.fixed_string)
      self.match_context = MatchContext(self.fixed_string)
      self.match_element = self.fixed_dme.get_match_element('match', self.match_context)
      self.log_atom = self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element),
        t, self.whitelist_violation_detector)
      
      self.assertTrue(self.whitelist_violation_detector.receive_atom(self.log_atom))
      self.assertEqual(self.output_stream.getvalue(), '')
      
      self.fixed_dme = FixedDataModelElement('s2', self.fixed_string)
      self.match_context = MatchContext(self.fixed_string)
      self.match_element = self.fixed_dme.get_match_element('match', self.match_context)
      self.log_atom = self.log_atom = LogAtom(self.match_element.match_object, ParserMatch(self.match_element),
        t, self.whitelist_violation_detector)
      
      self.assertTrue(self.whitelist_violation_detector.receive_atom(self.log_atom))
      self.assertEqual(self.output_stream.getvalue(), '')
      
      self.fixed_dme = FixedDataModelElement('s3', self.fixed_string)
      self.match_context = MatchContext(self.fixed_string)
      self.match_element = self.fixed_dme.get_match_element('match', self.match_context)
      self.log_atom = self.log_atom = LogAtom(self.match_element.match_object, ParserMatch(self.match_element),
        t, self.path_exists_match_rule)
      
      self.assertTrue(not self.whitelist_violation_detector.receive_atom(self.log_atom))
      self.assertEqual(self.output_stream.getvalue(), self.__expected_string %
        (datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"),
        self.whitelist_violation_detector.__class__.__name__, description, 1, "b'fixed String'"))


if __name__ == "__main__":
    unittest.main()
