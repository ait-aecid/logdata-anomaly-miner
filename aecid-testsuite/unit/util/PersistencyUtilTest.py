import unittest
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
import time
from aminer.util import PersistencyUtil
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.analysis.NewMatchPathValueComboDetector import NewMatchPathValueComboDetector
from unit.TestBase import TestBase


class PersistencyUtilTest(TestBase):
    __expected_string = 'New path(es) %s  (1 lines)\n  %s\n  [%s, [\'%s\']]\n\n'

    string = b'25537 uid=2'

    match_context_fixed_dme = MatchContext(b' pid=')
    fixed_dme = FixedDataModelElement('s1', b' pid=')
    match_element_fixed_dme = fixed_dme.get_match_element("", match_context_fixed_dme)

    match_context_decimal_integer_value_me = MatchContext(string)
    decimal_integer_value_me = DecimalIntegerValueModelElement('d1', DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                                                               DecimalIntegerValueModelElement.PAD_TYPE_NONE)
    match_element_decimal_integer_value_me = decimal_integer_value_me.get_match_element("", match_context_decimal_integer_value_me)

    fixed_dme = FixedDataModelElement('s1', string)

    decimal_integer_value_me = DecimalIntegerValueModelElement('d1', DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                                                               DecimalIntegerValueModelElement.PAD_TYPE_NONE)

    match_context_first_match_me = MatchContext(string)
    first_match_me = FirstMatchModelElement('f1', [fixed_dme, decimal_integer_value_me])
    match_element_first_match_me = first_match_me.get_match_element('first', match_context_first_match_me)

    match_context_first_match_me2 = MatchContext(string)
    first_match_me2 = FirstMatchModelElement('f2', [decimal_integer_value_me, fixed_dme])
    match_element_first_match_me2 = first_match_me2.get_match_element('second', match_context_first_match_me2)

    def test1persist_multiple_objects_of_single_class(self):
        """In this test case multiple instances of one class are to be persisted and loaded."""
        description = "Test1PersistencyUtil"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', True)
        self.analysis_context.register_component(new_match_path_detector, description)

        t = time.time()
        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)
        log_atom_decimal_integer_value_me = LogAtom(self.match_context_decimal_integer_value_me.match_data,
                                                    ParserMatch(self.match_element_decimal_integer_value_me), t, new_match_path_detector)
        new_match_path_detector.receive_atom(log_atom_fixed_dme)
        new_match_path_detector.receive_atom(log_atom_decimal_integer_value_me)

        other_new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'otherDetector', True)
        self.analysis_context.register_component(other_new_match_path_detector, description + "2")
        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, other_new_match_path_detector)
        other_new_match_path_detector.receive_atom(log_atom_fixed_dme)

        PersistencyUtil.persist_all()
        self.assertTrue(
            PersistencyUtil.load_json(new_match_path_detector.persistence_file_name) == [
                self.match_element_fixed_dme.get_path(), self.match_element_decimal_integer_value_me.get_path()] or
            PersistencyUtil.load_json(
                new_match_path_detector.persistence_file_name) == [
                self.match_element_decimal_integer_value_me.get_path(), self.match_element_fixed_dme.get_path()])
        self.assertEqual(PersistencyUtil.load_json(other_new_match_path_detector.persistence_file_name), [
            self.match_element_fixed_dme.get_path()])

    def test2persist_multiple_objects_of_multiple_class(self):
        """In this test case multiple instances of multiple classes are to be persisted and loaded."""
        description = "Test2PersistencyUtil"
        new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default2', True)
        self.analysis_context.register_component(new_match_path_detector, description)

        t = time.time()
        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, new_match_path_detector)
        log_atom_decimal_integer_value_me = LogAtom(self.match_context_decimal_integer_value_me.match_data,
                                                    ParserMatch(self.match_element_decimal_integer_value_me), t, new_match_path_detector)
        new_match_path_detector.receive_atom(log_atom_fixed_dme)
        new_match_path_detector.receive_atom(log_atom_decimal_integer_value_me)

        other_new_match_path_detector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'otherDetector2',
                                                             True)
        self.analysis_context.register_component(other_new_match_path_detector, description + "2")
        log_atom_fixed_dme = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), t, other_new_match_path_detector)
        other_new_match_path_detector.receive_atom(log_atom_fixed_dme)

        new_match_path_value_combo_detector = NewMatchPathValueComboDetector(self.aminer_config, ['first/f1/s1'],
                                                                             [self.stream_printer_event_handler], 'Default', False, True)
        self.analysis_context.register_component(new_match_path_value_combo_detector, description + "3")
        log_atom_sequence_me = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_first_match_me), t,
                                       new_match_path_value_combo_detector)
        new_match_path_value_combo_detector.receive_atom(log_atom_sequence_me)

        PersistencyUtil.persist_all()
        self.assertTrue(
            PersistencyUtil.load_json(new_match_path_detector.persistence_file_name) == [
                self.match_element_fixed_dme.get_path(), self.match_element_decimal_integer_value_me.get_path()] or
            PersistencyUtil.load_json(
                new_match_path_detector.persistence_file_name) == [
                self.match_element_decimal_integer_value_me.get_path(), self.match_element_fixed_dme.get_path()])
        self.assertEqual(PersistencyUtil.load_json(other_new_match_path_detector.persistence_file_name),
                         [self.match_element_fixed_dme.get_path()])
        self.assertEqual(PersistencyUtil.load_json(new_match_path_value_combo_detector.persistence_file_name),
                         ([[log_atom_sequence_me.raw_data]]))


if __name__ == "__main__":
    unittest.main()
