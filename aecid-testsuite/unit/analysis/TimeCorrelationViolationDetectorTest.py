from unit.TestBase import TestBase
from aminer.parsing import FixedDataModelElement, DecimalIntegerValueModelElement
import unittest
import time
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.analysis.TimeCorrelationViolationDetector import CorrelationRule, \
  EventClassSelector, TimeCorrelationViolationDetector
from aminer.analysis import Rules
from aminer.parsing.MatchContext import MatchContext
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from datetime import datetime


class TimeCorrelationViolationDetectorTest(TestBase):
  __expected_string = '%s Correlation rule "%s" violated\nTimeCorrelationViolationDetector: "%s" (%d lines)\n  FAIL: '
  __expected_string_not_found = __expected_string + 'B-Event for "%s" (%s) not found!\n\n'
  __expected_string_too_early = __expected_string + 'B-Event for "%s" (%s) was found too early!\n\n\n'
  __expected_string_too_late = __expected_string + 'B-Event for "%s" (%s) was not found in time!\n\n\n'
  __expected_string_different_attributes = __expected_string + '"%s" (%s) %d is not equal %d\n\n\n'
  
  model = '/model'
  datetime_format_string = '%Y-%m-%d %H:%M:%S'

  service_children1 = []

  service_children1.append(FixedDataModelElement('Value1Key', b'Value1: '))
  service_children1.append(FixedDataModelElement('Value1Value', b'fixed Value1'))
  service_children1.append(FixedDataModelElement('Value2Key', b', Value2: '))
  service_children1.append(DecimalIntegerValueModelElement('Value2Value'))
  service_children1.append(FixedDataModelElement('Value3Key', b', Value3: '))
  service_children1.append(FixedDataModelElement('Value3Value', b'fixed Value3'))
  service_children1.append(FixedDataModelElement('Value4Key', b', Value4: '))
  service_children1.append(FixedDataModelElement('Value4Value', b'fixed Value4'))

  service_children2 = []

  service_children2.append(FixedDataModelElement('Value1Key', b'Value1: '))
  service_children2.append(FixedDataModelElement('Value1Value', b'fixed Value1'))
  service_children2.append(FixedDataModelElement('Value2Key', b', Value2: '))
  service_children2.append(FixedDataModelElement('Value2Value', b'fixed Value2'))
  service_children2.append(FixedDataModelElement('Value3Key', b', Value3: '))
  service_children2.append(DecimalIntegerValueModelElement('Value3Value'))
  service_children2.append(FixedDataModelElement('Value4Key', b', Value4: '))
  service_children2.append(FixedDataModelElement('Value4Value', b'fixed Value4'))
  
  match_context1 = MatchContext(b'Value1: fixed Value1, Value2: 22500, Value3: fixed Value3, Value4: fixed Value4')
  match_context2 = MatchContext(b'Value1: fixed Value1, Value2: fixed Value2, Value3: 22500, Value4: fixed Value4')
  match_context2_different = MatchContext(b'Value1: fixed Value1, Value2: fixed Value2, Value3: 22501, Value4: fixed Value4')
  
  seq1 = SequenceModelElement('sequence1', service_children1)
  seq2 = SequenceModelElement('sequence2', service_children2)
  
  match_element1 = seq1.get_match_element(model, match_context1)
  match_element2 = seq2.get_match_element(model, match_context2)
  match_element2_different = seq2.get_match_element(model, match_context2_different)
  
  def setUp(self):
    TestBase.setUp(self)
    self.correlation_rule = CorrelationRule('Correlation', 1, 1.2, max_artefacts_a_for_single_b=1,
                                           artefact_match_parameters=[('/model/sequence1/Value2Value', '/model/sequence2/Value3Value')])
    self.a_class_selector = EventClassSelector('Selector1', [self.correlation_rule], None)
    self.b_class_selector = EventClassSelector('Selector2', None, [self.correlation_rule])
    self.rules = []
    self.rules.append(Rules.PathExistsMatchRule('/model/sequence1/Value2Key', self.a_class_selector))
    self.rules.append(Rules.PathExistsMatchRule('/model/sequence2/Value3Key', self.b_class_selector))
  
  '''
  In this test case the status is OK after receiving the expected data and no error message
  is returned. The output of the doTimer-method is also tested in this test case.
  '''
  def test1_check_status_ok(self):
    description = "Test1TimeCorrelationViolationDetector"
    time_correlation_violation_detector = TimeCorrelationViolationDetector(
      self.analysis_context.aminer_config, self.rules, [self.stream_printer_event_handler])
    self.analysis_context.register_component(time_correlation_violation_detector, component_name=description)
    
    log_atom1 = LogAtom(self.match_context1.match_data, ParserMatch(self.match_element1), time.time(), self)
    time_correlation_violation_detector.receive_atom(log_atom1)
    log_atom2 = LogAtom(self.match_context2.match_data, ParserMatch(self.match_element2), time.time() + 1, self)
    time_correlation_violation_detector.receive_atom(log_atom2)
    
    time_correlation_violation_detector.do_timer(time.time())
    self.assertEqual(self.output_stream.getvalue(), "")

  '''
  In this test case the second log line is not found and an appropriate error message is expected 
  from the checkStatus-method. The output of the doTimer-method is also tested in this test case.
  '''
  def test2_check_status_not_found_error(self):
    description = "Test2TimeCorrelationViolationDetector"
    time_correlation_violation_detector = TimeCorrelationViolationDetector(
      self.analysis_context.aminer_config, self.rules, [self.stream_printer_event_handler])
    self.analysis_context.register_component(time_correlation_violation_detector, component_name=description)
    t = time.time()
    log_atom1 = LogAtom(self.match_context1.match_data, ParserMatch(self.match_element1), t, self)
    time_correlation_violation_detector.receive_atom(log_atom1)
    r = self.correlation_rule.check_status(t + 2)
    self.assertEqual(r[0], 'FAIL: B-Event for "%s" (%s) was not found in time!\n' % (
      self.match_element1.get_match_string().decode("utf-8"), self.a_class_selector.action_id))

  '''
  In this test case the second log line is found too early and an appropriate error messageis expected 
  from the checkStatus-method. The output of the doTimer-method is also tested in this test case.
  '''
  def test3_check_status_before_expected_timespan(self):
    description = "Test3TimeCorrelationViolationDetector"
    time_correlation_violation_detector = TimeCorrelationViolationDetector(
      self.analysis_context.aminer_config, self.rules, [self.stream_printer_event_handler])
    self.analysis_context.register_component(time_correlation_violation_detector, component_name=description)
    
    t = time.time()
    log_atom1 = LogAtom(self.match_context1.match_data, ParserMatch(self.match_element1), t, self)
    time_correlation_violation_detector.receive_atom(log_atom1)
    log_atom2 = LogAtom(self.match_context2.match_data, ParserMatch(self.match_element2), time.time(), self)
    time_correlation_violation_detector.receive_atom(log_atom2)
    time_correlation_violation_detector.do_timer(time.time())
    self.assertEqual(self.output_stream.getvalue(), self.__expected_string_too_early % (datetime.fromtimestamp(t).strftime(self.datetime_format_string),
      self.correlation_rule.rule_id, description, 1, self.match_element1.get_match_string().decode("utf-8"), self.a_class_selector.action_id))

  '''
  In this test case the second log line is found too late and an appropriate error message is expected 
  from the checkStatus-method.  The output of the doTimer-method is also tested in this test case.
  '''
  def test4_check_status_after_expected_timespan(self):
    description = "Test4TimeCorrelationViolationDetector"
    time_correlation_violation_detector = TimeCorrelationViolationDetector(
      self.analysis_context.aminer_config, self.rules, [self.stream_printer_event_handler])
    self.analysis_context.register_component(time_correlation_violation_detector, component_name=description)
    
    t = time.time()
    log_atom1 = LogAtom(self.match_context1.match_data, ParserMatch(self.match_element1), t, self)
    time_correlation_violation_detector.receive_atom(log_atom1)
    log_atom2 = LogAtom(self.match_context2.match_data, ParserMatch(self.match_element2), t + 5, self)
    time_correlation_violation_detector.receive_atom(log_atom2)
    time_correlation_violation_detector.do_timer(time.time())
    self.assertEqual(self.output_stream.getvalue(), self.__expected_string_too_late % (datetime.fromtimestamp(t).strftime(self.datetime_format_string),
      self.correlation_rule.rule_id, description, 1, self.match_element1.get_match_string().decode("utf-8"), self.a_class_selector.action_id))
  
  '''
  In this test case the second log line has different attributes than expected and an appropriate error message 
  is expected from the checkStatus-method.  The output of the doTimer-method is also tested in this test case.
  '''
  def test5_check_status_attributes_not_matching(self):
    description = "Test5TimeCorrelationViolationDetector"
    time_correlation_violation_detector = TimeCorrelationViolationDetector(
      self.analysis_context.aminer_config, self.rules, [self.stream_printer_event_handler])
    self.analysis_context.register_component(time_correlation_violation_detector, component_name=description)
    
    t = time.time()
    log_atom1 = LogAtom(self.match_context1.match_data, ParserMatch(self.match_element1), t, self)
    time_correlation_violation_detector.receive_atom(log_atom1)
    log_atom2 = LogAtom(self.match_context2.match_data, ParserMatch(self.match_element2_different), t + 1, self)
    time_correlation_violation_detector.receive_atom(log_atom2)
    time_correlation_violation_detector.do_timer(time.time())
    self.assertEqual(self.output_stream.getvalue(), self.__expected_string_different_attributes % (datetime.fromtimestamp(t).strftime(self.datetime_format_string),
      self.correlation_rule.rule_id, description, 1, self.match_element1.get_match_string().decode("utf-8"), self.a_class_selector.action_id, 22500, 22501))

  '''
  In this test case the prepareHistoryEntry-method is tested with multiple 
  artefactMatchParameters. Also the case of not finding a parameter is tested.
  '''
  def test6_prepare_history_entry(self):
    t = time.time()
    p1 = ParserMatch(self.match_element1)
    p2 = ParserMatch(self.match_element2)
    log_atom1 = LogAtom(self.match_context1.match_data, p1, t, self)
    log_atom2 = LogAtom(self.match_context2.match_data, p2, t + 5, self)
    
    result = self.correlation_rule.prepare_history_entry(self.a_class_selector, log_atom1)
    self.assertEqual(result, [t, 0, self.a_class_selector, p1, 22500])
    result = self.correlation_rule.prepare_history_entry(self.b_class_selector, log_atom2)
    self.assertEqual(result, [t+5, 0, self.b_class_selector, p2, 22500])

if __name__ == "__main__":
    unittest.main()
