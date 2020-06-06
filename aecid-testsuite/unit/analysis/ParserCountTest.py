from aminer.analysis import ParserCount
from aminer.input import LogAtom
from aminer.parsing import FixedDataModelElement, MatchContext, SequenceModelElement, ParserMatch
from unit.TestBase import TestBase

import time


class ParserCountTest(TestBase):
    match_context_m1 = MatchContext(b'First string')
    match_context_m2 = MatchContext(b' to match.')
    match_context_m3 = MatchContext(b'some completely other string to match.')
    match_context_seq = MatchContext(b'First string to match.')
    fixed_dme_m1 = FixedDataModelElement('m1', b'First string')
    fixed_dme_m2 = FixedDataModelElement('m2', b' to match.')
    seq = SequenceModelElement('seq', [fixed_dme_m1, fixed_dme_m2])
    fixed_dme_m3 = FixedDataModelElement('m3', b'some completely other string to match.')
    match_element_m1 = fixed_dme_m1.get_match_element('fixed', match_context_m1)
    match_element_m2 = fixed_dme_m2.get_match_element('fixed', match_context_m2)
    match_element_m3 = fixed_dme_m3.get_match_element('fixed', match_context_m3)
    match_element_seq = seq.get_match_element('fixed', match_context_seq)

    def test1log_atom_not_in_path_list(self):
        """This unittest checks if no action happens, when no path in the match_dictionary matches a target_path."""
        parser_count = ParserCount(self.aminer_config, ['fixed/seq', 'fixed/seq/m1', 'fixed/seq/m2'], [self.stream_printer_event_handler])
        t = time.time()
        log_atom = LogAtom(self.fixed_dme_m3.fixed_data, ParserMatch(self.match_element_m3), t, parser_count)
        old_count_dict = dict(parser_count.count_dict)
        parser_count.receive_atom(log_atom)
        self.assertEqual(parser_count.count_dict, old_count_dict)

    def test2log_atom_matches_single_path(self):
        """This unittest tests the receive_atom method with a single path matching."""
        parser_count = ParserCount(self.aminer_config, ['fixed/seq', 'fixed/seq/m1', 'fixed/seq/m2', 'fixed/m3'],
                                   [self.stream_printer_event_handler])
        t = time.time()
        log_atom = LogAtom(self.fixed_dme_m3.fixed_data, ParserMatch(self.match_element_m3), t, parser_count)
        old_count_dict = dict(parser_count.count_dict)
        old_count_dict['fixed/m3'] = 1
        parser_count.receive_atom(log_atom)
        self.assertEqual(parser_count.count_dict, old_count_dict)

    def test3log_atom_matches_multiple_paths(self):
        """This unittest tests the receive_atom method with multiple paths matching."""
        parser_count = ParserCount(self.aminer_config, ['fixed/seq', 'fixed/seq/m1', 'fixed/seq/m2', 'fixed/m3'],
                                   [self.stream_printer_event_handler])
        t = time.time()
        log_atom = LogAtom(self.match_context_seq.match_data, ParserMatch(self.match_element_seq), t, parser_count)
        old_count_dict = dict(parser_count.count_dict)
        old_count_dict['fixed/seq'] = 1
        old_count_dict['fixed/seq/m1'] = 1
        old_count_dict['fixed/seq/m2'] = 1
        parser_count.receive_atom(log_atom)
        self.assertEqual(parser_count.count_dict, old_count_dict)

    def test4do_timer(self):
        """This unittest checks if the do_timer method works properly."""
        parser_count = ParserCount(self.aminer_config, ['fixed/m3'], [self.stream_printer_event_handler], 600)
        t = time.time()
        self.assertEqual(int(parser_count.do_timer(t + 100)), 600)
        self.assertEqual(self.output_stream.getvalue(), "")
        log_atom = LogAtom(self.match_context_seq.match_data, ParserMatch(self.match_element_seq), t, parser_count)
        parser_count.receive_atom(log_atom)
        self.assertEqual(int(parser_count.do_timer(t + 100)), 500)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(parser_count.do_timer(t + 601), 600)
        self.assertNotEqual(self.output_stream.getvalue(), "")
        self.reset_output_stream()

    def test5reset_after_report_flag(self):
        """This unittest tests the functionality of the reset_after_report flag."""
        parser_count = ParserCount(self.aminer_config, ['fixed/seq', 'fixed/seq/m1', 'fixed/seq/m2', 'fixed/m3'],
                                   [self.stream_printer_event_handler], 600, False)
        parser_count.count_dict['fixed/seq'] = 5
        parser_count.count_dict['fixed/seq/m1'] = 5
        parser_count.count_dict['fixed/seq/m2'] = 5
        parser_count.count_dict['fixed/m3'] = 17
        old_count_dict = dict(parser_count.count_dict)
        parser_count.send_report()
        self.assertEqual(parser_count.count_dict, old_count_dict)
        parser_count.reset_after_report_flag = True
        parser_count.send_report()
        # no changes happened, so no report and no resetting happening
        self.assertEqual(parser_count.count_dict, old_count_dict)
        parser_count.count_dict['fixed/m3'] = 18
        parser_count.send_report()
        old_count_dict['fixed/seq'] = 0
        old_count_dict['fixed/seq/m1'] = 0
        old_count_dict['fixed/seq/m2'] = 0
        old_count_dict['fixed/m3'] = 0
        self.assertEqual(parser_count.count_dict, old_count_dict)

    def test6receive_atom_without_target_paths(self):
        """This unittest tests the receive_atom method with multiple paths matching without having target_paths specified."""
        parser_count = ParserCount(self.aminer_config, None, [self.stream_printer_event_handler])
        t = time.time()
        log_atom = LogAtom(self.match_context_seq.match_data, ParserMatch(self.match_element_seq), t, parser_count)
        old_count_dict = dict(parser_count.count_dict)
        old_count_dict['fixed/seq'] = 1
        parser_count.receive_atom(log_atom)
        self.assertEqual(parser_count.count_dict, old_count_dict)
