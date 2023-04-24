import unittest
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
import time
from aminer.parsing.ParserMatch import ParserMatch
from aminer.input.LogAtom import LogAtom
from aminer.analysis.UnparsedAtomHandlers import SimpleUnparsedAtomHandler, VerboseUnparsedAtomHandler
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummyMatchContext
from datetime import datetime


class SimpleUnparsedAtomHandlerTest(TestBase):
    """Unittests for the SimpleUnparsedAtomHandler."""

    datetime_format_string = "%Y-%m-%d %H:%M:%S"
    calculation = b"256 * 2 = 512"

    def test1SimpleUnparsedAtomHandler_receive_atom(self):
        """Test if the SimpleUnparsedAtomHandler can handle matching log atoms and not matching log atoms."""
        description = "Test1SimpleUnparsedAtomHandler"
        t = time.time()
        fdme = DummyFixedDataModelElement("s1", self.calculation)
        new_match_path_detector1 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False)

        # match exists
        match_context = DummyMatchContext(self.calculation)
        match_element = fdme.get_match_element("match", match_context)
        log_atom = LogAtom(match_element.match_object, ParserMatch(match_element), t, new_match_path_detector1)

        simple_unparsed_atom_handler = SimpleUnparsedAtomHandler([self.stream_printer_event_handler])
        self.analysis_context.register_component(simple_unparsed_atom_handler, description)
        self.assertFalse(simple_unparsed_atom_handler.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), "")

        # match does not exist
        log_atom = LogAtom(match_element.match_object, None, t, new_match_path_detector1)
        self.assertTrue(simple_unparsed_atom_handler.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(),
                         f'{datetime.fromtimestamp(t).strftime(self.datetime_format_string)} Unparsed atom received\n'
                         f'{simple_unparsed_atom_handler.__class__.__name__}: "{description}" (1 lines)\n  {self.calculation.decode()}\n\n')
        self.reset_output_stream()

        # the ParserMatch actually is no instance of ParserMatch, but the atom should still be considered to be parsed.
        log_atom = LogAtom(match_element.match_object, fdme, t, new_match_path_detector1)
        self.assertFalse(simple_unparsed_atom_handler.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), "")

    def test2VerboseUnparsedAtomHandler_receive_atom(self):
        """Test if the VerboseUnparsedAtomHandler can handle matching log atoms and not matching log atoms."""
        description = "Test2VerboseUnparsedAtomHandler"
        t = time.time()
        fdme = DummyFixedDataModelElement("s1", self.calculation)
        new_match_path_detector1 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False)

        # match exists
        match_context = DummyMatchContext(self.calculation)
        match_element = fdme.get_match_element("match", match_context)
        log_atom = LogAtom(match_element.match_object, ParserMatch(match_element), t, new_match_path_detector1)

        verbose_unparsed_atom_handler = VerboseUnparsedAtomHandler([self.stream_printer_event_handler], fdme)
        self.analysis_context.register_component(verbose_unparsed_atom_handler, description)
        self.assertFalse(verbose_unparsed_atom_handler.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), "")

        # match does not exist
        log_atom = LogAtom(match_element.match_object, None, t, new_match_path_detector1)
        self.assertTrue(verbose_unparsed_atom_handler.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(),
                         f'{datetime.fromtimestamp(t).strftime(self.datetime_format_string)} Unparsed atom received\n'
                         f'{verbose_unparsed_atom_handler.__class__.__name__}: "{description}" (1 lines)\n  Starting match update on "'
                         f'{self.calculation.decode()}"\n  Removed: "{self.calculation.decode()}", remaining 0 bytes\n  Shortest unmatched '
                         f'data: ""\n{self.calculation.decode()}\n\n')
        self.reset_output_stream()

        # the ParserMatch actually is no instance of ParserMatch, but the atom should still be considered to be parsed.
        log_atom = LogAtom(match_element.match_object, fdme, t, new_match_path_detector1)
        self.assertFalse(verbose_unparsed_atom_handler.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
