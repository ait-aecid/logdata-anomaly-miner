import unittest
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from time import time
from aminer.parsing.ParserMatch import ParserMatch
from aminer.parsing.MatchContext import MatchContext
from aminer.input.LogAtom import LogAtom
from aminer.input.SimpleUnparsedAtomHandler import SimpleUnparsedAtomHandler
from unit.TestBase import TestBase


class SimpleUnparsedAtomHandlerTest(TestBase):
    calculation = b'256 * 2 = 512'

    def test1_atom_is_unparsed(self):
        """The atom in this test case has a ParserMatch."""
        description = "Test1SimpleUnparsedAtomHandler"
        any_byte_data_model_element = AnyByteDataModelElement('a1')
        new_match_path_detector1 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False)

        match_context = MatchContext(self.calculation)
        match_element = any_byte_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_element.match_object, ParserMatch(match_element), time(), new_match_path_detector1)

        simple_unparsed_atom_handler = SimpleUnparsedAtomHandler([self.stream_printer_event_handler])
        self.analysis_context.register_component(simple_unparsed_atom_handler, description)
        self.assertTrue(not simple_unparsed_atom_handler.receive_atom(log_atom))

    def test2_atom_is_parsed(self):
        """The atom in this test case has no ParserMatch."""
        description = "Test2SimpleUnparsedAtomHandler"
        any_byte_data_model_element = AnyByteDataModelElement('a1')
        new_match_path_detector1 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False)

        match_context = MatchContext(self.calculation)
        match_element = any_byte_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_element.match_object, None, time(), new_match_path_detector1)

        simple_unparsed_atom_handler = SimpleUnparsedAtomHandler([self.stream_printer_event_handler])
        self.analysis_context.register_component(simple_unparsed_atom_handler, description)
        self.assertTrue(simple_unparsed_atom_handler.receive_atom(log_atom))

    def test3_parser_match_is_other_element(self):
        """In this test case the ParserMatch actually is no instance of ParserMatch. The atom should still be considered to be parsed."""
        description = "Test3SimpleUnparsedAtomHandler"
        any_byte_data_model_element = AnyByteDataModelElement('a1')
        new_match_path_detector1 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False)

        match_context = MatchContext(self.calculation)
        match_element = any_byte_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_element.match_object, any_byte_data_model_element, time(), new_match_path_detector1)

        simple_unparsed_atom_handler = SimpleUnparsedAtomHandler([self.stream_printer_event_handler])
        self.analysis_context.register_component(simple_unparsed_atom_handler, description)
        self.assertTrue(not simple_unparsed_atom_handler.receive_atom(log_atom))


if __name__ == "__main__":
    unittest.main()
