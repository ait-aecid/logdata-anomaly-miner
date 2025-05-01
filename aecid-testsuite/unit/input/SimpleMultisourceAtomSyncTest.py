import unittest
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from aminer.input.SimpleMultisourceAtomSync import SimpleMultisourceAtomSync
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from time import time, sleep
from unit.TestBase import TestBase, DummyMatchContext
from datetime import datetime


class SimpleMultisourceAtomSyncTest(TestBase):
    """Unittests for the SimpleMultisourceAtomSync."""

    def test1receive_atom(self):
        """Test if the SimpleMultisourceAtomSync works in different scenarios and orders the data correctly."""

        __expected_string = '%s New path(s) detected\n%s: "None" (%d lines)\n  %s\n\n'
        __expected_string_no_date = 'New path(s) detected\n%s: "None" (%d lines)\n  %s\n\n'

        calculation = b'256 * 2 = 512'
        datetime_format_string = '%Y-%m-%d %H:%M:%S'
        match_path = "['match/a1']"

        # already sorted log atoms
        sync_wait_time = 3
        abdme = AnyByteDataModelElement("a1")
        nmpd1 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False, output_logline=False)
        nmpd2 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False, output_logline=False)
        smas = SimpleMultisourceAtomSync([nmpd1, nmpd2], sync_wait_time)

        t = time()
        match_element = abdme.get_match_element("match", DummyMatchContext(calculation))
        log_atom1 = LogAtom(match_element.match_object, ParserMatch(match_element), t, nmpd1)
        log_atom2 = LogAtom(match_element.match_object, ParserMatch(match_element), t + 1, nmpd1)

        self.assertFalse(smas.receive_atom(log_atom1))
        sleep(sync_wait_time + 1)

        # not of the same source, thus must not be accepted.
        self.assertFalse(smas.receive_atom(log_atom2))
        self.assertTrue(smas.receive_atom(log_atom1))
        # logAtom1 is handled now, so logAtom2 is accepted.
        self.reset_output_stream()
        self.assertTrue(smas.receive_atom(log_atom2))
        self.assertEqual(self.output_stream.getvalue(), __expected_string % (
          datetime.fromtimestamp(t + 1).strftime(datetime_format_string), nmpd1.__class__.__name__, 1,
          match_path) + __expected_string % (
          datetime.fromtimestamp(t + 1).strftime(datetime_format_string), nmpd1.__class__.__name__, 1, match_path))

        # In this test case a LogAtom with no timestamp is received by the class.
        self.reset_output_stream()
        smas = SimpleMultisourceAtomSync([nmpd1], sync_wait_time)
        log_atom1 = LogAtom(match_element.match_object, ParserMatch(match_element), None, nmpd1)

        self.assertTrue(smas.receive_atom(log_atom1))
        self.assertEqual(self.output_stream.getvalue(), __expected_string_no_date % (nmpd1.__class__.__name__, 1, match_path))

        # In this test case multiple, UNSORTED LogAtoms of different sources are received by the class.
        smas = SimpleMultisourceAtomSync([nmpd1, nmpd2], sync_wait_time)
        t = time()
        log_atom1 = LogAtom(match_element.match_object, ParserMatch(match_element), t, nmpd1)
        log_atom2 = LogAtom(match_element.match_object, ParserMatch(match_element), t - 1, nmpd1)

        self.assertFalse(smas.receive_atom(log_atom1))
        sleep(sync_wait_time)

        # unsorted, should be accepted
        self.reset_output_stream()
        self.assertTrue(smas.receive_atom(log_atom2))
        self.assertTrue(smas.receive_atom(log_atom1))
        self.assertEqual(self.output_stream.getvalue(), __expected_string % (
            datetime.fromtimestamp(t - 1).strftime(datetime_format_string), nmpd1.__class__.__name__, 1, match_path) + __expected_string % (
            datetime.fromtimestamp(t - 1).strftime(datetime_format_string), nmpd1.__class__.__name__, 1, match_path) + __expected_string % (
            datetime.fromtimestamp(t).strftime(datetime_format_string), nmpd1.__class__.__name__, 1, match_path) + __expected_string % (
            datetime.fromtimestamp(t).strftime(datetime_format_string), nmpd1.__class__.__name__, 1, match_path))

        # In this test case a source becomes idle and expires.
        smas = SimpleMultisourceAtomSync([nmpd1], sync_wait_time)
        t = time()
        log_atom1 = LogAtom(match_element.match_object, ParserMatch(match_element), t, nmpd1)
        log_atom2 = LogAtom(match_element.match_object, ParserMatch(match_element), t, nmpd2)

        self.assertFalse(smas.receive_atom(log_atom1))
        self.assertFalse(smas.receive_atom(log_atom2))
        sleep(sync_wait_time + 1)

        self.assertTrue(smas.receive_atom(log_atom1))
        # log_atom1 is handled now, so new_match_path_detector1 should be deleted after waiting the sync_wait_time.
        self.assertFalse(smas.receive_atom(log_atom2))
        sleep(sync_wait_time + 1)
        self.assertFalse(smas.receive_atom(log_atom2))
        self.assertEqual(smas.sources_dict, {nmpd1: [log_atom1.get_timestamp(), None], nmpd2: [log_atom2.get_timestamp(), log_atom2]})

        self.assertTrue(smas.receive_atom(log_atom1))
        self.assertTrue(smas.receive_atom(log_atom1))
        sleep(sync_wait_time + 1)
        self.assertTrue(smas.receive_atom(log_atom1))
        self.assertEqual(smas.sources_dict, {nmpd1: [log_atom1.get_timestamp(), None], nmpd2: [log_atom2.get_timestamp(), log_atom2]})
        log_atom1 = LogAtom(match_element.match_object, ParserMatch(match_element), t + 1, nmpd1)
        self.assertFalse(smas.receive_atom(log_atom1))
        self.assertEqual(smas.sources_dict, {nmpd1: [log_atom1.get_timestamp() - 1, log_atom1], nmpd2: [log_atom2.get_timestamp(), log_atom2]})

        log_atom1 = LogAtom(match_element.match_object, ParserMatch(match_element), t - 1, nmpd1)
        self.assertTrue(smas.receive_atom(log_atom1))

    def test2validate_parameters(self):
        """Test all initialization parameters for the atomizer. Input parameters must be validated in the class."""
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False, output_logline=False)
        self.assertRaises(TypeError, SimpleMultisourceAtomSync, "default", 3)
        self.assertRaises(TypeError, SimpleMultisourceAtomSync, b"Default", 3)
        self.assertRaises(TypeError, SimpleMultisourceAtomSync, None, 3)
        self.assertRaises(TypeError, SimpleMultisourceAtomSync, True, 3)
        self.assertRaises(TypeError, SimpleMultisourceAtomSync, 123, 3)
        self.assertRaises(TypeError, SimpleMultisourceAtomSync, 123.3, 3)
        self.assertRaises(TypeError, SimpleMultisourceAtomSync, ["default"], 3)
        self.assertRaises(TypeError, SimpleMultisourceAtomSync, {"id": "Default"}, 3)
        self.assertRaises(TypeError, SimpleMultisourceAtomSync, [], 3)
        self.assertRaises(TypeError, SimpleMultisourceAtomSync, (), 3)
        self.assertRaises(TypeError, SimpleMultisourceAtomSync, set(), 3)

        self.assertRaises(TypeError, SimpleMultisourceAtomSync, [nmpd], "default")
        self.assertRaises(TypeError, SimpleMultisourceAtomSync, [nmpd], b"Default",)
        self.assertRaises(TypeError, SimpleMultisourceAtomSync, [nmpd], None)
        self.assertRaises(TypeError, SimpleMultisourceAtomSync, [nmpd], True)
        self.assertRaises(TypeError, SimpleMultisourceAtomSync, [nmpd], ["default"])
        self.assertRaises(TypeError, SimpleMultisourceAtomSync, [nmpd], {"id": "Default"})
        self.assertRaises(TypeError, SimpleMultisourceAtomSync, [nmpd], [])
        self.assertRaises(TypeError, SimpleMultisourceAtomSync, [nmpd], ())
        self.assertRaises(TypeError, SimpleMultisourceAtomSync, [nmpd], set())
        SimpleMultisourceAtomSync([nmpd], 123)
        SimpleMultisourceAtomSync([nmpd], 123.3)


if __name__ == "__main__":
    unittest.main()
