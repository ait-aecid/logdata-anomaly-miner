import unittest
from aminer.analysis.AtomFilters import SubhandlerFilter, MatchPathFilter, MatchValueFilter
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
import time
from datetime import datetime
from unit.TestBase import TestBase, DummyMatchContext, DummyFixedDataModelElement


class AtomFiltersTest(TestBase):
    """Unittests for the AtomFilters."""

    __expected_string = '%s New path(es) detected\n%s: "%s" (%d lines)\n  %s: %s\n%s\n%s\n\n'
    match_path = "fixed/s1"
    datetime_format_string = "%Y-%m-%d %H:%M:%S"

    def test1receive_atom_SubhandlerFilter(self):
        """Test if log atoms are processed correctly with the SubhandlerFilter and the stop_when_handled flag is working properly."""
        description = "Test1SubhandlerFilter"
        data = b"25000"
        match_context = DummyMatchContext(data)
        fdme = DummyFixedDataModelElement("s1", data)
        match_element = fdme.get_match_element("fixed", match_context)
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False)
        self.analysis_context.register_component(nmpd, description)
        other_nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False)
        self.analysis_context.register_component(other_nmpd, description + "2")
        t = time.time()
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), t, nmpd)

        # more than one subhandler can handle the log_atom (stop_when_handled flag is false).
        subhandler_filter = SubhandlerFilter([nmpd, other_nmpd], False)
        self.assertTrue(subhandler_filter.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), nmpd.__class__.__name__, description, 1,
            self.match_path, data.decode(), f"['{self.match_path}']", data.decode()) + self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), nmpd.__class__.__name__, description + "2", 1,
            self.match_path, data.decode(), f"['{self.match_path}']", data.decode()))
        self.reset_output_stream()

        # SubhandlerFilter stops processing after first subhandler handles the log_atom (stop_when_handled flag is true).
        subhandler_filter = SubhandlerFilter([nmpd, other_nmpd], True)
        self.assertTrue(subhandler_filter.receive_atom(log_atom))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
            datetime.fromtimestamp(t).strftime(self.datetime_format_string), nmpd.__class__.__name__, description, 1,
            self.match_path, data.decode(), f"['{self.match_path}']", data.decode()))
        self.reset_output_stream()

        # atom not handled.
        subhandler_filter = SubhandlerFilter([], True)
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), t, nmpd)
        self.assertFalse(subhandler_filter.receive_atom(log_atom))

    def test2add_handler_SubhandlerFilter(self):
        """Test if new detectors can be added to the SubhandlerFilter."""
        description = "Test2SubhandlerFilter"
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler],"Default", False)
        self.analysis_context.register_component(nmpd, description)
        other_nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler],"Default", False)
        self.analysis_context.register_component(other_nmpd, description + "2")
        subhandler_filter = SubhandlerFilter([nmpd, other_nmpd], False)
        self.assertEqual(subhandler_filter.subhandler_list, [(nmpd, False), (other_nmpd, False)])
        subhandler_filter.add_handler(nmpd, True)
        subhandler_filter.add_handler(other_nmpd, False)
        self.assertEqual(subhandler_filter.subhandler_list, [(nmpd, False), (other_nmpd, False), (nmpd, True), (other_nmpd, False)])
        subhandler_filter = SubhandlerFilter([nmpd, other_nmpd], True)
        self.assertEqual(subhandler_filter.subhandler_list, [(nmpd, True), (other_nmpd, True)])

    def test3receive_atom_MatchPathFilter(self):
        """Test if log atoms are processed correctly with the MatchPathFilter and the stop_when_handled flag is working properly."""
        description = "Test3MatchPathFilter"
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False)
        self.analysis_context.register_component(nmpd, description)
        data = b"data"
        match_context = DummyMatchContext(data)
        fdme = DummyFixedDataModelElement("s1", data)
        match_element = fdme.get_match_element("fixed", match_context)
        t = time.time()
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), t, nmpd)

        # There is a path in the dictionary and the handler are not None. The default_parsed_atom_handler is None.
        match_path_filter = MatchPathFilter([(match_element.get_path(), nmpd)], None)
        self.assertTrue(match_path_filter.receive_atom(log_atom))

        # The searched path is not in the dictionary. The default_parsed_atom_handler is None.
        match_path_filter = MatchPathFilter([("d1", nmpd)], None)
        self.assertFalse(match_path_filter.receive_atom(log_atom))

        # The searched path is not in the dictionary. The default_parsed_atom_handler is set.
        match_path_filter = MatchPathFilter([("d1", nmpd)], nmpd)
        self.assertTrue(match_path_filter.receive_atom(log_atom))

    def test4receive_atom_MatchValueFilter(self):
        """Test if log atoms are processed correctly with the MatchValueFilter and the stop_when_handled flag is working properly."""
        description = "Test4MatchValueFilter"
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False)
        self.analysis_context.register_component(nmpd, description)
        other_nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False)
        self.analysis_context.register_component(nmpd, description + "1")
        data = b"data"
        other_data = b"other data"
        match_context = DummyMatchContext(data)
        fdme = DummyFixedDataModelElement("s1", data)
        match_element = fdme.get_match_element("fixed", match_context)
        t = time.time()
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), t, nmpd)

        # A target_value and a handler, which can handle the match_object is found.
        match_value_filter = MatchValueFilter(match_element.get_path(), {fdme.data: nmpd}, other_nmpd)
        self.assertTrue(match_value_filter.receive_atom(log_atom))

        # No default handler is used.
        other_match_context = DummyMatchContext(other_data)
        other_fdme = DummyFixedDataModelElement("d1", other_data)
        other_match_element = other_fdme.get_match_element("fixed", other_match_context)
        log_atom = LogAtom(other_fdme.data, ParserMatch(other_match_element), t, other_nmpd)
        self.assertTrue(match_value_filter.receive_atom(log_atom))

        # No target_value was found in the dictionary.
        log_atom = LogAtom(other_data, None, t, nmpd)
        self.assertFalse(match_value_filter.receive_atom(log_atom))

    def test5validate_parameters_SubhandlerFilter(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler],"Default", False)
        self.assertRaises(TypeError, SubhandlerFilter, [""], True)
        self.assertRaises(TypeError, SubhandlerFilter, [b""], True)
        self.assertRaises(TypeError, SubhandlerFilter, [True], True)
        self.assertRaises(TypeError, SubhandlerFilter, [None], True)
        self.assertRaises(TypeError, SubhandlerFilter, [123], True)
        self.assertRaises(TypeError, SubhandlerFilter, [123.2], True)
        self.assertRaises(TypeError, SubhandlerFilter, [{"id": "Default"}], True)
        self.assertRaises(TypeError, SubhandlerFilter, [["Default"]], True)
        self.assertRaises(TypeError, SubhandlerFilter, [set()], True)
        self.assertRaises(TypeError, SubhandlerFilter, [()], True)
        self.assertRaises(TypeError, SubhandlerFilter, [(nmpd, False)], True)

        self.assertRaises(TypeError, SubhandlerFilter, [nmpd], "")
        self.assertRaises(TypeError, SubhandlerFilter, [nmpd], None)
        self.assertRaises(TypeError, SubhandlerFilter, [nmpd], b"Default")
        self.assertRaises(TypeError, SubhandlerFilter, [nmpd], 123)
        self.assertRaises(TypeError, SubhandlerFilter, [nmpd], 123.2)
        self.assertRaises(TypeError, SubhandlerFilter, [nmpd], {"id": "Default"})
        self.assertRaises(TypeError, SubhandlerFilter, [nmpd], ["Default"])
        self.assertRaises(TypeError, SubhandlerFilter, [nmpd], [])
        self.assertRaises(TypeError, SubhandlerFilter, [nmpd], ())
        self.assertRaises(TypeError, SubhandlerFilter, [nmpd], set())
        SubhandlerFilter([nmpd], False)

    def test6validate_parameters_MatchPathFilter(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False)
        self.assertRaises(TypeError, MatchPathFilter, [""])
        self.assertRaises(TypeError, MatchPathFilter, [b""])
        self.assertRaises(TypeError, MatchPathFilter, [True])
        self.assertRaises(TypeError, MatchPathFilter, [None])
        self.assertRaises(TypeError, MatchPathFilter, [123])
        self.assertRaises(TypeError, MatchPathFilter, [123.2])
        self.assertRaises(TypeError, MatchPathFilter, [{"id": "Default"}])
        self.assertRaises(TypeError, MatchPathFilter, [["Default"]])
        self.assertRaises(TypeError, MatchPathFilter, [set()])
        self.assertRaises(TypeError, MatchPathFilter, [()])
        self.assertRaises(TypeError, MatchPathFilter, [("path", None)])

        self.assertRaises(TypeError, MatchPathFilter, [("path", nmpd)], "")
        self.assertRaises(TypeError, MatchPathFilter, [("path", nmpd)], True)
        self.assertRaises(TypeError, MatchPathFilter, [("path", nmpd)], b"Default")
        self.assertRaises(TypeError, MatchPathFilter, [("path", nmpd)], 123)
        self.assertRaises(TypeError, MatchPathFilter, [("path", nmpd)], 123.2)
        self.assertRaises(TypeError, MatchPathFilter, [("path", nmpd)], {"id": "Default"})
        self.assertRaises(TypeError, MatchPathFilter, [("path", nmpd)], ["Default"])
        self.assertRaises(TypeError, MatchPathFilter, [("path", nmpd)], [])
        self.assertRaises(TypeError, MatchPathFilter, [("path", nmpd)], ())
        self.assertRaises(TypeError, MatchPathFilter, [("path", nmpd)], set())
        MatchPathFilter([("path", nmpd)], None)
        MatchPathFilter([("path", nmpd)], nmpd)

    def test7validate_parameters_MatchValueFilter(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False)
        dictionary = {b"val": nmpd}
        path = "path"
        self.assertRaises(TypeError, MatchValueFilter, "", dictionary)
        self.assertRaises(TypeError, MatchValueFilter, b"", dictionary)
        self.assertRaises(TypeError, MatchValueFilter, True, dictionary)
        self.assertRaises(TypeError, MatchValueFilter, None, dictionary)
        self.assertRaises(TypeError, MatchValueFilter, 123, dictionary)
        self.assertRaises(TypeError, MatchValueFilter, 123.2, dictionary)
        self.assertRaises(TypeError, MatchValueFilter, {"id": "Default"}, dictionary)
        self.assertRaises(TypeError, MatchValueFilter, ["Default"], dictionary)
        self.assertRaises(TypeError, MatchValueFilter, set(), dictionary)
        self.assertRaises(TypeError, MatchValueFilter, (), dictionary)
        self.assertRaises(TypeError, MatchValueFilter, ("path", None), dictionary)

        self.assertRaises(TypeError, MatchValueFilter, path, "")
        self.assertRaises(TypeError, MatchValueFilter, path, True)
        self.assertRaises(TypeError, MatchValueFilter, path, b"Default")
        self.assertRaises(TypeError, MatchValueFilter, path, 123)
        self.assertRaises(TypeError, MatchValueFilter, path, 123.2)
        self.assertRaises(TypeError, MatchValueFilter, path, {"id": "Default"})
        self.assertRaises(TypeError, MatchValueFilter, path, ["Default"])
        self.assertRaises(TypeError, MatchValueFilter, path, [])
        self.assertRaises(TypeError, MatchValueFilter, path, ())
        self.assertRaises(TypeError, MatchValueFilter, path, set())
        self.assertRaises(TypeError, MatchValueFilter, path, {"id": None})

        self.assertRaises(TypeError, MatchValueFilter, path, dictionary, "")
        self.assertRaises(TypeError, MatchValueFilter, path, dictionary, b"")
        self.assertRaises(TypeError, MatchValueFilter, path, dictionary, True)
        self.assertRaises(TypeError, MatchValueFilter, path, dictionary, 123)
        self.assertRaises(TypeError, MatchValueFilter, path, dictionary, 123.22)
        self.assertRaises(TypeError, MatchValueFilter, path, dictionary, {"id": "Default"})
        self.assertRaises(TypeError, MatchValueFilter, path, dictionary, ["Default"])
        self.assertRaises(TypeError, MatchValueFilter, path, dictionary, [nmpd])
        self.assertRaises(TypeError, MatchValueFilter, path, dictionary, set())
        self.assertRaises(TypeError, MatchValueFilter, path, dictionary, ())

        MatchValueFilter("path", dictionary, None)
        MatchValueFilter("path", dictionary, nmpd)


if __name__ == "__main__":
    unittest.main()
