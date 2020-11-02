import unittest
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from aminer.input.SimpleMultisourceAtomSync import SimpleMultisourceAtomSync
from aminer.parsing.MatchContext import MatchContext
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from time import time, sleep
from unit.TestBase import TestBase
from datetime import datetime


class SimpleMultisourceAtomSyncTest(TestBase):
    """Unittests for the SimpleMultisourceAtomSync."""

    __expected_string = '%s New path(es) detected\n%s: "%s" (%d lines)\n  %s\n%s\n\n'

    calculation = b'256 * 2 = 512'
    datetime_format_string = '%Y-%m-%d %H:%M:%S'
    match_path = "['match/a1']"

    def test1sorted_log_atoms(self):
        """In this test case multiple, SORTED LogAtoms of different sources are received by the class."""
        description = "Test1SimpleMultisourceAtomSync"
        sync_wait_time = 3

        any_byte_data_model_element = AnyByteDataModelElement('a1')
        new_match_path_detector1 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False,
                                                        output_log_line=False)
        self.analysis_context.register_component(new_match_path_detector1, description)
        new_match_path_detector2 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False,
                                                        output_log_line=False)
        self.analysis_context.register_component(new_match_path_detector2, description + "2")

        simple_multisource_atom_sync = SimpleMultisourceAtomSync([new_match_path_detector1, new_match_path_detector2], sync_wait_time)

        t = time()
        match_context = MatchContext(self.calculation)
        match_element = any_byte_data_model_element.get_match_element('match', match_context)
        log_atom1 = LogAtom(match_element.match_object, ParserMatch(match_element), t, new_match_path_detector1)
        log_atom2 = LogAtom(match_element.match_object, ParserMatch(match_element), t + 1, new_match_path_detector1)

        self.assertTrue(not simple_multisource_atom_sync.receive_atom(log_atom1))
        sleep(sync_wait_time + 1)

        # not of the same source, thus must not be accepted.
        self.assertTrue(not simple_multisource_atom_sync.receive_atom(log_atom2))
        self.assertTrue(simple_multisource_atom_sync.receive_atom(log_atom1))
        # logAtom1 is handled now, so logAtom2 is accepted.
        self.reset_output_stream()
        self.assertTrue(simple_multisource_atom_sync.receive_atom(log_atom2))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
          datetime.fromtimestamp(t + 1).strftime(self.datetime_format_string), new_match_path_detector1.__class__.__name__, description, 1,
          self.match_path, self.calculation) + self.__expected_string % (
          datetime.fromtimestamp(t + 1).strftime(self.datetime_format_string), new_match_path_detector1.__class__.__name__,
          description + "2", 1, self.match_path, self.calculation))

    def test2no_timestamp_log_atom(self):
        """In this test case a LogAtom with no timestamp is received by the class."""
        description = "Test2SimpleMultisourceAtomSync"
        sync_wait_time = 3

        any_byte_data_model_element = AnyByteDataModelElement('a1')
        new_match_path_detector1 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False,
                                                        output_log_line=False)
        self.analysis_context.register_component(new_match_path_detector1, description)
        simple_multisource_atom_sync = SimpleMultisourceAtomSync([new_match_path_detector1], sync_wait_time)
        t = time()

        match_context = MatchContext(self.calculation)
        match_element = any_byte_data_model_element.get_match_element('match', match_context)
        log_atom1 = LogAtom(match_element.match_object, ParserMatch(match_element), None, new_match_path_detector1)

        self.assertTrue(simple_multisource_atom_sync.receive_atom(log_atom1))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
          datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_detector1.__class__.__name__, description, 1,
          self.match_path, self.calculation))

    def test3unsorted_log_atom(self):
        """In this test case multiple, UNSORTED LogAtoms of different sources are received by the class."""
        description = "Test3SimpleMultisourceAtomSync"
        sync_wait_time = 3

        any_byte_data_model_element = AnyByteDataModelElement('a1')
        new_match_path_detector1 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False,
                                                        output_log_line=False)
        self.analysis_context.register_component(new_match_path_detector1, description)
        new_match_path_detector2 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False,
                                                        output_log_line=False)
        self.analysis_context.register_component(new_match_path_detector2, description + "2")

        simple_multisource_atom_sync = SimpleMultisourceAtomSync([new_match_path_detector1, new_match_path_detector2], sync_wait_time)
        t = time()
        match_context = MatchContext(self.calculation)
        match_element = any_byte_data_model_element.get_match_element('match', match_context)
        log_atom1 = LogAtom(match_element.match_object, ParserMatch(match_element), t, new_match_path_detector1)
        log_atom2 = LogAtom(match_element.match_object, ParserMatch(match_element), t - 1, new_match_path_detector1)

        self.assertTrue(not simple_multisource_atom_sync.receive_atom(log_atom1))
        sleep(sync_wait_time)

        # unsorted, should be accepted
        self.reset_output_stream()
        self.assertTrue(simple_multisource_atom_sync.receive_atom(log_atom2))
        self.assertTrue(simple_multisource_atom_sync.receive_atom(log_atom1))
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
          datetime.fromtimestamp(t - 1).strftime(self.datetime_format_string), new_match_path_detector1.__class__.__name__, description, 1,
          self.match_path, self.calculation) + self.__expected_string % (
          datetime.fromtimestamp(t - 1).strftime(self.datetime_format_string), new_match_path_detector1.__class__.__name__,
          description + "2", 1, self.match_path, self.calculation) + self.__expected_string % (
          datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_detector1.__class__.__name__, description, 1,
          self.match_path, self.calculation) + self.__expected_string % (
          datetime.fromtimestamp(t).strftime(self.datetime_format_string), new_match_path_detector1.__class__.__name__, description + "2",
          1, self.match_path, self.calculation))

    def test4has_idle_source(self):
        """In this test case a source becomes idle and expires."""
        description = "Test4SimpleMultisourceAtomSync"
        sync_wait_time = 3

        any_byte_data_model_element = AnyByteDataModelElement('a1')
        new_match_path_detector1 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False,
                                                        output_log_line=False)
        self.analysis_context.register_component(new_match_path_detector1, description)
        new_match_path_detector2 = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False,
                                                        output_log_line=False)
        self.analysis_context.register_component(new_match_path_detector2, description + "2")

        simple_multisource_atom_sync = SimpleMultisourceAtomSync([new_match_path_detector1], sync_wait_time)
        t = time()
        match_context = MatchContext(self.calculation)
        match_element = any_byte_data_model_element.get_match_element('match', match_context)
        log_atom1 = LogAtom(match_element.match_object, ParserMatch(match_element), t, new_match_path_detector1)
        log_atom2 = LogAtom(match_element.match_object, ParserMatch(match_element), t, new_match_path_detector2)

        self.assertTrue(not simple_multisource_atom_sync.receive_atom(log_atom1))
        self.assertTrue(not simple_multisource_atom_sync.receive_atom(log_atom2))
        sleep(sync_wait_time + 1)

        self.assertTrue(simple_multisource_atom_sync.receive_atom(log_atom1))
        # log_atom1 is handled now, so new_match_path_detector1 should be deleted after waiting the sync_wait_time.
        self.assertTrue(not simple_multisource_atom_sync.receive_atom(log_atom2))
        sleep(sync_wait_time + 1)
        self.assertTrue(not simple_multisource_atom_sync.receive_atom(log_atom2))
        self.assertEqual(simple_multisource_atom_sync.sources_dict, {
            new_match_path_detector1: [log_atom1.get_timestamp(), None], new_match_path_detector2: [log_atom2.get_timestamp(), log_atom2]})

        self.assertTrue(simple_multisource_atom_sync.receive_atom(log_atom1))
        self.assertTrue(simple_multisource_atom_sync.receive_atom(log_atom1))
        sleep(sync_wait_time + 1)
        self.assertTrue(simple_multisource_atom_sync.receive_atom(log_atom1))
        self.assertEqual(simple_multisource_atom_sync.sources_dict, {
            new_match_path_detector1: [log_atom1.get_timestamp(), None], new_match_path_detector2: [log_atom2.get_timestamp(), log_atom2]})
        log_atom1 = LogAtom(match_element.match_object, ParserMatch(match_element), t + 1, new_match_path_detector1)
        self.assertTrue(not simple_multisource_atom_sync.receive_atom(log_atom1))
        self.assertEqual(simple_multisource_atom_sync.sources_dict, {
            new_match_path_detector1: [log_atom1.get_timestamp() - 1, log_atom1],
            new_match_path_detector2: [log_atom2.get_timestamp(), log_atom2]})

        log_atom1 = LogAtom(match_element.match_object, ParserMatch(match_element), t - 1, new_match_path_detector1)
        self.assertTrue(simple_multisource_atom_sync.receive_atom(log_atom1))


if __name__ == "__main__":
    unittest.main()
