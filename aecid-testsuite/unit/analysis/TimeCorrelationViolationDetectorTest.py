import unittest
import time
from aminer.analysis.TimeCorrelationViolationDetector import CorrelationRule, EventClassSelector, TimeCorrelationViolationDetector
from aminer.analysis import Rules
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase, DummyMatchContext, DummySequenceModelElement, DummyFixedDataModelElement, DummyNumberModelElement
from datetime import datetime


class TimeCorrelationViolationDetectorTest(TestBase):
    """Unittests for the TimeCorrelationViolationDetector."""

    def test1receive_atom(self):
        """Test if log atoms are processed correctly and violations are detected."""
        expected_string = '%s Correlation rule "%s" violated\nTimeCorrelationViolationDetector: "None" (%d lines)\n  '
        expected_string_too_early = expected_string + 'FAIL: B-Event for "%s" (%s) was found too early!\n\n\n'
        expected_string_too_late = expected_string + 'FAIL: B-Event for "%s" (%s) was not found in time!\n\n\n'
        expected_string_different_attributes = expected_string + 'FAIL: "%s" (%s) %d is not equal %d\n\n\n'

        model = "/model"
        dtf = "%Y-%m-%d %H:%M:%S"

        service_children1 = [
            DummyFixedDataModelElement("Value1Key", b"Value1: "), DummyFixedDataModelElement("Value1Value", b"fixed Value1"),
            DummyFixedDataModelElement("Value2Key", b", Value2: "), DummyNumberModelElement("Value2Value"),
            DummyFixedDataModelElement("Value3Key", b", Value3: "), DummyFixedDataModelElement("Value3Value", b"fixed Value3"),
            DummyFixedDataModelElement("Value4Key", b", Value4: "), DummyFixedDataModelElement("Value4Value", b"fixed Value4")]

        service_children2 = [
            DummyFixedDataModelElement("Value1Key", b"Value1: "), DummyFixedDataModelElement("Value1Value", b"fixed Value1"),
            DummyFixedDataModelElement("Value2Key", b", Value2: "), DummyFixedDataModelElement("Value2Value", b"fixed Value2"),
            DummyFixedDataModelElement("Value3Key", b", Value3: "), DummyNumberModelElement("Value3Value"),
            DummyFixedDataModelElement("Value4Key", b", Value4: "), DummyFixedDataModelElement("Value4Value", b"fixed Value4")]

        service_children3 = [
            DummyFixedDataModelElement("Value1Key", b"Value1: "), DummyFixedDataModelElement("Value1Value", b"other Value1"),
            DummyFixedDataModelElement("Value2Key", b", Value2: "), DummyFixedDataModelElement("Value2Value", b"fixed Value2"),
            DummyFixedDataModelElement("Value3Key", b", Value3: "), DummyNumberModelElement("Value3Value"),
            DummyFixedDataModelElement("Value4Key", b", Value4: "), DummyFixedDataModelElement("Value4Value", b"fixed Value4")]

        match_context1 = DummyMatchContext(b"Value1: fixed Value1, Value2: 22500, Value3: fixed Value3, Value4: fixed Value4")
        match_context2 = DummyMatchContext(b"Value1: fixed Value1, Value2: fixed Value2, Value3: 22500, Value4: fixed Value4")
        match_context3 = DummyMatchContext(b"Value1: fixed Value1, Value2: fixed Value2, Value3: 22501, Value4: fixed Value4")
        match_context4 = DummyMatchContext(b"Value1: other Value1, Value2: fixed Value2, Value3: 22500, Value4: fixed Value4")

        seq1 = DummySequenceModelElement("sequence1", service_children1)
        seq2 = DummySequenceModelElement("sequence2", service_children2)
        seq3 = DummySequenceModelElement("sequence2", service_children3)

        match_element1 = seq1.get_match_element(model, match_context1)
        match_element2 = seq2.get_match_element(model, match_context2)
        match_element3 = seq2.get_match_element(model, match_context3)
        match_element4 = seq3.get_match_element(model, match_context4)
        t = time.time()

        def setup():
            cr = CorrelationRule("Correlation", 2, 10)
            ecsa = EventClassSelector("Selector1", [cr], None)
            ecsb = EventClassSelector("Selector2", None, [cr])
            rules = [Rules.PathExistsMatchRule("/model/sequence1/Value2Key", ecsa), Rules.PathExistsMatchRule("/model/sequence2/Value3Key", ecsb)]
            return cr, ecsa, ecsb, rules

        # in time
        cr, ecsa, ecsb, rules = setup()
        tcvd = TimeCorrelationViolationDetector(self.analysis_context.aminer_config, rules, [self.stream_printer_event_handler])
        iterations = 30
        for i in range(iterations):
            log_atom = LogAtom(match_context1.match_data, ParserMatch(match_element1), t, self)
            tcvd.receive_atom(log_atom)
        for i in range(iterations):
            log_atom = LogAtom(match_context2.match_data, ParserMatch(match_element2), t + 2 + i * 0.1, self)
            tcvd.receive_atom(log_atom)
        self.assertEqual(self.output_stream.getvalue(), "")

        # too early
        cr, ecsa, ecsb, rules = setup()
        tcvd = TimeCorrelationViolationDetector(self.analysis_context.aminer_config, rules, [self.stream_printer_event_handler])
        log_atom1 = LogAtom(match_context1.match_data, ParserMatch(match_element1), t, self)
        tcvd.receive_atom(log_atom1)
        log_atom2 = LogAtom(match_context2.match_data, ParserMatch(match_element2), t + 1, self)
        tcvd.receive_atom(log_atom2)
        tcvd.do_timer(t)
        self.assertEqual(self.output_stream.getvalue(), expected_string_too_early % (datetime.fromtimestamp(t).strftime(dtf), cr.rule_id, 1,
            match_element1.match_string.decode(), ecsa.action_id))
        self.reset_output_stream()

        # too late
        cr, ecsa, ecsb, rules = setup()
        tcvd = TimeCorrelationViolationDetector(self.analysis_context.aminer_config, rules, [self.stream_printer_event_handler])
        log_atom1 = LogAtom(match_context1.match_data, ParserMatch(match_element1), t, self)
        tcvd.receive_atom(log_atom1)
        log_atom2 = LogAtom(match_context2.match_data, ParserMatch(match_element2), t + 10.1, self)
        tcvd.receive_atom(log_atom2)
        tcvd.do_timer(t)
        self.assertEqual(self.output_stream.getvalue(), expected_string_too_late % (datetime.fromtimestamp(t).strftime(dtf), cr.rule_id, 1,
            match_element1.match_string.decode(), ecsa.action_id))
        self.reset_output_stream()

        # test max_violations
        cr, ecsa, ecsb, rules = setup()
        tcvd = TimeCorrelationViolationDetector(self.analysis_context.aminer_config, rules, [self.stream_printer_event_handler])
        iterations = 30
        for i in range(iterations):
            log_atom = LogAtom(match_context1.match_data, ParserMatch(match_element1), t, self)
            tcvd.receive_atom(log_atom)
        for i in range(iterations):
            log_atom = LogAtom(match_context2.match_data, ParserMatch(match_element2), t + 11 + i * 0.1, self)
            tcvd.receive_atom(log_atom)
        tcvd.do_timer(t)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (datetime.fromtimestamp(t).strftime(dtf), cr.rule_id, 1) +
                         'FAIL: B-Event for "%s" (%s) was not found in time!\n' % (match_element1.match_string.decode(), ecsa.action_id) * 20 + "... (10 more)\n\n\n")
        self.reset_output_stream()

        # change value 3 - error expected
        cr = CorrelationRule("Correlation", 2, 10, artefact_match_parameters=[("/model/sequence1/Value2Value", "/model/sequence2/Value3Value")])
        ecsa = EventClassSelector("Selector1", [cr], None)
        ecsb = EventClassSelector("Selector2", None, [cr])
        rules = [Rules.PathExistsMatchRule("/model/sequence1/Value2Key", ecsa), Rules.PathExistsMatchRule("/model/sequence2/Value3Key", ecsb)]
        tcvd = TimeCorrelationViolationDetector(self.analysis_context.aminer_config, rules, [self.stream_printer_event_handler])
        log_atom1 = LogAtom(match_context1.match_data, ParserMatch(match_element1), t, self)
        tcvd.receive_atom(log_atom1)
        log_atom2 = LogAtom(match_context3.match_data, ParserMatch(match_element3), t + 2, self)
        tcvd.receive_atom(log_atom2)
        tcvd.do_timer(t)
        self.assertEqual(self.output_stream.getvalue(), expected_string_different_attributes % (
            datetime.fromtimestamp(t).strftime(dtf), cr.rule_id, 1, match_element1.match_string.decode(), ecsa.action_id, 22500, 22501))
        self.reset_output_stream()

        # - change value 1 - no error expected as path is not checked.
        cr = CorrelationRule("Correlation", 2, 10, artefact_match_parameters=[("/model/sequence1/Value2Value", "/model/sequence2/Value3Value")])
        ecsa = EventClassSelector("Selector1", [cr], None)
        ecsb = EventClassSelector("Selector2", None, [cr])
        rules = [Rules.PathExistsMatchRule("/model/sequence1/Value2Key", ecsa), Rules.PathExistsMatchRule("/model/sequence2/Value3Key", ecsb)]
        tcvd = TimeCorrelationViolationDetector(self.analysis_context.aminer_config, rules, [self.stream_printer_event_handler])
        log_atom1 = LogAtom(match_context1.match_data, ParserMatch(match_element1), t, self)
        tcvd.receive_atom(log_atom1)
        log_atom2 = LogAtom(match_context4.match_data, ParserMatch(match_element4), t + 2, self)
        tcvd.receive_atom(log_atom2)
        tcvd.do_timer(t)
        self.assertEqual(self.output_stream.getvalue(), "")

    def test2do_timer(self):
        """Test if the do_timer method is implemented properly."""
        cr = CorrelationRule("Correlation", 2, 10)
        ecsa = EventClassSelector("Selector1", [cr], None)
        ecsb = EventClassSelector("Selector2", None, [cr])
        rules = [Rules.PathExistsMatchRule("/model/sequence1/Value2Key", ecsa), Rules.PathExistsMatchRule("/model/sequence2/Value3Key", ecsb)]
        tcvd = TimeCorrelationViolationDetector(self.analysis_context.aminer_config, rules, [self.stream_printer_event_handler])
        t = time.time()
        self.assertEqual(tcvd.do_timer(t + 200), 10)
        self.assertEqual(tcvd.do_timer(t + 400), 10)
        self.assertEqual(tcvd.do_timer(t + 999), 10)
        self.assertEqual(tcvd.do_timer(t + 1000), 10)

    def test3validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        cr = CorrelationRule("Correlation", 2, 10)
        ecsa = EventClassSelector("Selector1", [cr], None)
        ecsb = EventClassSelector("Selector2", None, [cr])
        rules = [Rules.PathExistsMatchRule("/model/sequence1/Value2Key", ecsa), Rules.PathExistsMatchRule("/model/sequence2/Value3Key", ecsb)]

        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, ["default"], [self.stream_printer_event_handler])
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, None, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, "", [self.stream_printer_event_handler])
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, b"Default", [self.stream_printer_event_handler])
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, True, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, 123, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, 123.3, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, {"id": "Default"}, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, (), [self.stream_printer_event_handler])
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, set(), [self.stream_printer_event_handler])

        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, rules, ["default"])
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, rules, None)
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, rules, "")
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, rules, b"Default")
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, rules, True)
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, rules, 123)
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, rules, 123.3)
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, rules, {"id": "Default"})
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, rules, ())
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, rules, set())

        self.assertRaises(ValueError, TimeCorrelationViolationDetector, self.aminer_config, rules, [self.stream_printer_event_handler], log_resource_ignore_list=["/tmp/syslog"])
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, rules, [self.stream_printer_event_handler], log_resource_ignore_list="")
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, rules, [self.stream_printer_event_handler], log_resource_ignore_list=b"Default")
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, rules, [self.stream_printer_event_handler], log_resource_ignore_list=True)
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, rules, [self.stream_printer_event_handler], log_resource_ignore_list=123)
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, rules, [self.stream_printer_event_handler], log_resource_ignore_list=123.22)
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, rules, [self.stream_printer_event_handler], log_resource_ignore_list={"id": "Default"})
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, rules, [self.stream_printer_event_handler], log_resource_ignore_list=())
        self.assertRaises(TypeError, TimeCorrelationViolationDetector, self.aminer_config, rules, [self.stream_printer_event_handler], log_resource_ignore_list=set())
        TimeCorrelationViolationDetector(self.aminer_config, rules, [self.stream_printer_event_handler], log_resource_ignore_list=["file:///tmp/syslog"])

        self.assertRaises(ValueError, EventClassSelector, "", [cr], [cr])
        self.assertRaises(TypeError, EventClassSelector, ["default"], [cr], [cr])
        self.assertRaises(TypeError, EventClassSelector, None, [cr], [cr])
        self.assertRaises(TypeError, EventClassSelector, b"Default", [cr], [cr])
        self.assertRaises(TypeError, EventClassSelector, True, [cr], [cr])
        self.assertRaises(TypeError, EventClassSelector, 123, [cr], [cr])
        self.assertRaises(TypeError, EventClassSelector, 123.3, [cr], [cr])
        self.assertRaises(TypeError, EventClassSelector, {"id": "Default"}, [cr], [cr])
        self.assertRaises(TypeError, EventClassSelector, (), [cr], [cr])
        self.assertRaises(TypeError, EventClassSelector, set(), [cr], [cr])

        self.assertRaises(TypeError, EventClassSelector, "default", "", [cr])
        self.assertRaises(TypeError, EventClassSelector, "default", ["default"], [cr])
        self.assertRaises(TypeError, EventClassSelector, "default", [None], [cr])
        self.assertRaises(TypeError, EventClassSelector, "default", b"Default", [cr])
        self.assertRaises(TypeError, EventClassSelector, "default", True, [cr])
        self.assertRaises(TypeError, EventClassSelector, "default", 123, [cr])
        self.assertRaises(TypeError, EventClassSelector, "default", 123.3, [cr])
        self.assertRaises(TypeError, EventClassSelector, "default", {"id": "Default"}, [cr])
        self.assertRaises(TypeError, EventClassSelector, "default", (), [cr])
        self.assertRaises(TypeError, EventClassSelector, "default", set(), [cr])

        self.assertRaises(TypeError, EventClassSelector, "default", [cr], "")
        self.assertRaises(TypeError, EventClassSelector, "default", [cr], ["default"])
        self.assertRaises(TypeError, EventClassSelector, "default", [cr], [None])
        self.assertRaises(TypeError, EventClassSelector, "default", [cr], b"Default")
        self.assertRaises(TypeError, EventClassSelector, "default", [cr], True)
        self.assertRaises(TypeError, EventClassSelector, "default", [cr], 123)
        self.assertRaises(TypeError, EventClassSelector, "default", [cr], 123.3)
        self.assertRaises(TypeError, EventClassSelector, "default", [cr], {"id": "Default"})
        self.assertRaises(TypeError, EventClassSelector, "default", [cr], ())
        self.assertRaises(TypeError, EventClassSelector, "default", [cr], set())

        self.assertRaises(ValueError, EventClassSelector, "default", None, None)
        self.assertRaises(ValueError, EventClassSelector, "default", [], [])
        EventClassSelector("default", [cr, cr], [cr])
        EventClassSelector("default", None, [cr])
        EventClassSelector("default", [cr], None)
        EventClassSelector("default", [], [cr])
        EventClassSelector("default", [cr], [])

        self.assertRaises(ValueError, CorrelationRule, "", 1, 10)
        self.assertRaises(TypeError, CorrelationRule, ["default"], 1, 10)
        self.assertRaises(TypeError, CorrelationRule, None, 1, 10)
        self.assertRaises(TypeError, CorrelationRule, b"Default", 1, 10)
        self.assertRaises(TypeError, CorrelationRule, True, 1, 10)
        self.assertRaises(TypeError, CorrelationRule, 123, 1, 10)
        self.assertRaises(TypeError, CorrelationRule, 123.3, 1, 10)
        self.assertRaises(TypeError, CorrelationRule, {"id": "Default"}, 1, 10)
        self.assertRaises(TypeError, CorrelationRule, (), 1, 10)
        self.assertRaises(TypeError, CorrelationRule, set(), 1, 10)

        self.assertRaises(TypeError, CorrelationRule, "default", "", 10)
        self.assertRaises(TypeError, CorrelationRule, "default", ["default"], 10)
        self.assertRaises(TypeError, CorrelationRule, "default", None, 10)
        self.assertRaises(TypeError, CorrelationRule, "default", b"Default", 10)
        self.assertRaises(TypeError, CorrelationRule, "default", True, 10)
        self.assertRaises(TypeError, CorrelationRule, "default", "123", 10)
        self.assertRaises(TypeError, CorrelationRule, "default", {"id": "Default"}, 10)
        self.assertRaises(TypeError, CorrelationRule, "default", (), 10)
        self.assertRaises(TypeError, CorrelationRule, "default", set(), 10)

        self.assertRaises(TypeError, CorrelationRule, "default", 1, "")
        self.assertRaises(TypeError, CorrelationRule, "default", 1, ["default"])
        self.assertRaises(TypeError, CorrelationRule, "default", 1, None)
        self.assertRaises(TypeError, CorrelationRule, "default", 1, b"Default")
        self.assertRaises(TypeError, CorrelationRule, "default", 1, True)
        self.assertRaises(TypeError, CorrelationRule, "default", 1, "123")
        self.assertRaises(TypeError, CorrelationRule, "default", 1, {"id": "Default"})
        self.assertRaises(TypeError, CorrelationRule, "default", 1, ())
        self.assertRaises(TypeError, CorrelationRule, "default", 1, set())

        self.assertRaises(ValueError, CorrelationRule, "default", -1, 10)
        self.assertRaises(ValueError, CorrelationRule, "default", 10, 1)
        self.assertRaises(ValueError, CorrelationRule, "default", 10, 10)

        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, artefact_match_parameters="")
        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, artefact_match_parameters=["default"])
        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, artefact_match_parameters=b"Default")
        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, artefact_match_parameters=True)
        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, artefact_match_parameters="123")
        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, artefact_match_parameters=123)
        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, artefact_match_parameters=123.3)
        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, artefact_match_parameters={"id": "Default"})
        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, artefact_match_parameters=())
        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, artefact_match_parameters=set())

        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, max_violations="")
        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, max_violations=["default"])
        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, max_violations=None)
        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, max_violations=b"Default")
        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, max_violations=True)
        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, max_violations="123")
        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, max_violations=123.3)
        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, max_violations={"id": "Default"})
        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, max_violations=())
        self.assertRaises(TypeError, CorrelationRule, "default", 1, 10, max_violations=set())
        CorrelationRule("default", 0, 10, artefact_match_parameters=[("/model/sequence1/Value2Key", "/model/sequence2/Value3Key")])


if __name__ == "__main__":
    unittest.main()
