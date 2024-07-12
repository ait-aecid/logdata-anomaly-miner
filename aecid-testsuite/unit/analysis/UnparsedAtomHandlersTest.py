import unittest
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
import time
from aminer.parsing.ParserMatch import ParserMatch
from aminer.input.LogAtom import LogAtom
from aminer.analysis.UnparsedAtomHandlers import SimpleUnparsedAtomHandler, VerboseUnparsedAtomHandler
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummyMatchContext, DummySequenceModelElement
from datetime import datetime


class SimpleUnparsedAtomHandlerTest(TestBase):
    """Unittests for the SimpleUnparsedAtomHandler."""

    datetime_format_string = "%Y-%m-%d %H:%M:%S"
    calculation = b"256 * 2 = 512"

    def test1receive_atom_SimpleUnparsedAtomHandler(self):
        """Test if the SimpleUnparsedAtomHandler can handle matching log atoms and not matching log atoms."""
        t = time.time()
        fdme = DummyFixedDataModelElement("s1", self.calculation)
        new_match_path_detector1 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False)

        # match exists
        match_context = DummyMatchContext(self.calculation)
        match_element = fdme.get_match_element("match", match_context)
        log_atom = LogAtom(match_element.match_object, ParserMatch(match_element), t, new_match_path_detector1)

        simple_unparsed_atom_handler = SimpleUnparsedAtomHandler([self.stream_printer_event_handler])
        self.assertFalse(simple_unparsed_atom_handler.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), "")

        # match does not exist
        log_atom = LogAtom(match_element.match_object, None, t, new_match_path_detector1)
        self.assertTrue(simple_unparsed_atom_handler.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(),
                         f'{datetime.fromtimestamp(t).strftime(self.datetime_format_string)} Unparsed atom received\n'
                         f'{simple_unparsed_atom_handler.__class__.__name__}: "None" (1 lines)\n  {self.calculation.decode()}\n\n')
        self.reset_output_stream()

        # the ParserMatch actually is no instance of ParserMatch, but the atom should still be considered to be parsed.
        log_atom = LogAtom(match_element.match_object, fdme, t, new_match_path_detector1)
        self.assertFalse(simple_unparsed_atom_handler.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), "")

    def test2_receive_atom_VerboseUnparsedAtomHandler(self):
        """Test if the VerboseUnparsedAtomHandler can handle matching log atoms and not matching log atoms."""
        t = time.time()
        fdme = DummyFixedDataModelElement("s1", self.calculation)
        new_match_path_detector1 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False)

        # match exists
        match_context = DummyMatchContext(self.calculation)
        match_element = fdme.get_match_element("match", match_context)
        log_atom = LogAtom(match_element.match_object, ParserMatch(match_element), t, new_match_path_detector1)

        verbose_unparsed_atom_handler = VerboseUnparsedAtomHandler([self.stream_printer_event_handler], fdme)
        self.assertFalse(verbose_unparsed_atom_handler.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), "")

        # match does not exist
        log_atom = LogAtom(match_element.match_object, None, t, new_match_path_detector1)
        self.assertTrue(verbose_unparsed_atom_handler.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(),
                         f'{datetime.fromtimestamp(t).strftime(self.datetime_format_string)} Unparsed atom received\n'
                         f'{verbose_unparsed_atom_handler.__class__.__name__}: "None" (1 lines)\n  Starting match update on "'
                         f'{self.calculation.decode()}"\n  Removed: "{self.calculation.decode()}", remaining 0 bytes\n  Shortest unmatched '
                         f'data: ""\n{self.calculation.decode()}\n\n')
        self.reset_output_stream()

        # the ParserMatch actually is no instance of ParserMatch, but the atom should still be considered to be parsed.
        log_atom = LogAtom(match_element.match_object, fdme, t, new_match_path_detector1)
        self.assertFalse(verbose_unparsed_atom_handler.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), "")

    def test3validate_parameters_SimpleUnparsedAtomHandler(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(TypeError, SimpleUnparsedAtomHandler, ["default"])
        self.assertRaises(TypeError, SimpleUnparsedAtomHandler, None)
        self.assertRaises(TypeError, SimpleUnparsedAtomHandler, "")
        self.assertRaises(TypeError, SimpleUnparsedAtomHandler, b"Default")
        self.assertRaises(TypeError, SimpleUnparsedAtomHandler, True)
        self.assertRaises(TypeError, SimpleUnparsedAtomHandler, 123)
        self.assertRaises(TypeError, SimpleUnparsedAtomHandler, 123.3)
        self.assertRaises(TypeError, SimpleUnparsedAtomHandler, {"id": "Default"})
        self.assertRaises(TypeError, SimpleUnparsedAtomHandler, ())
        self.assertRaises(TypeError, SimpleUnparsedAtomHandler, set())
        SimpleUnparsedAtomHandler([self.stream_printer_event_handler])

    def test4validate_parameters_VerboseUnparsedAtomHandler(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        parsing_model = DummySequenceModelElement("seq", [DummyFixedDataModelElement("s1", b"string"), DummyFixedDataModelElement("sp", b" ")])
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, ["default"], parsing_model)
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, None, parsing_model)
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, "", parsing_model)
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, b"Default", parsing_model)
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, True, parsing_model)
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, 123, parsing_model)
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, 123.3, parsing_model)
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, {"id": "Default"}, parsing_model)
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, (), parsing_model)
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, set(), parsing_model)

        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, [self.stream_printer_event_handler], ["default"])
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, [self.stream_printer_event_handler], None)
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, [self.stream_printer_event_handler], "")
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, [self.stream_printer_event_handler], b"Default")
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, [self.stream_printer_event_handler], True)
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, [self.stream_printer_event_handler], 123)
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, [self.stream_printer_event_handler], 123.3)
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, [self.stream_printer_event_handler], {"id": "Default"})
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, [self.stream_printer_event_handler], ())
        self.assertRaises(TypeError, VerboseUnparsedAtomHandler, [self.stream_printer_event_handler], set())
        VerboseUnparsedAtomHandler([self.stream_printer_event_handler], parsing_model)


if __name__ == "__main__":
    unittest.main()
