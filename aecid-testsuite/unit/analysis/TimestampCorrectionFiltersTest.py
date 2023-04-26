import unittest
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from aminer.analysis.TimestampCorrectionFilters import SimpleMonotonicTimestampAdjust
from time import time
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummyMatchContext
from datetime import datetime


class TimestampCorrectionFiltersTest(TestBase):
    """Unittests for the TimestampCorrectionFilters."""

    def test1receive_atom(self):
        """This test case checks if the timestamp is adjusted and log atoms are forwarded correctly."""
        description = "Test1TimestampCorrectionFilter"
        match_context = DummyMatchContext(b" pid=")
        fdme = DummyFixedDataModelElement("s1", b" pid=")
        match_element = fdme.get_match_element("match", match_context)
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False, output_logline=False)
        self.analysis_context.register_component(nmpd, description)
        smta = SimpleMonotonicTimestampAdjust([nmpd], False)

        # the atom time should be set automatically if None.
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), None, nmpd)
        self.assertEqual(smta.receive_atom(log_atom), True)
        self.assertEqual(smta.latest_timestamp_seen, 0)
        self.assertNotEqual(log_atom.atom_time, None)
        t = log_atom.atom_time + 100

        log_atom = LogAtom(fdme.data, ParserMatch(match_element), t, nmpd)
        self.assertEqual(smta.receive_atom(log_atom), True)
        self.assertEqual(smta.latest_timestamp_seen, t)
        self.assertEqual(log_atom.atom_time, t)

        log_atom = LogAtom(fdme.data, ParserMatch(match_element), t-1000, nmpd)
        self.assertEqual(smta.receive_atom(log_atom), True)
        self.assertEqual(smta.latest_timestamp_seen, t)
        self.assertEqual(log_atom.atom_time, t)

    def test2validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False)
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [""], True)
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [b""], True)
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [True], True)
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [None], True)
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [123], True)
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [123.2], True)
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [{"id": "Default"}], True)
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [["Default"]], True)
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [set()], True)
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [()], True)
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [(nmpd, False)], True)

        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [nmpd], "")
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [nmpd], None)
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [nmpd], b"Default")
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [nmpd], 123)
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [nmpd], 123.2)
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [nmpd], {"id": "Default"})
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [nmpd], ["Default"])
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [nmpd], [])
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [nmpd], ())
        self.assertRaises(TypeError, SimpleMonotonicTimestampAdjust, [nmpd], set())
        SimpleMonotonicTimestampAdjust([nmpd], False)

if __name__ == "__main__":
    unittest.main()
