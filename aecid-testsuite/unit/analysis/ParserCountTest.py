from aminer.analysis.ParserCount import ParserCount, current_processed_lines_str, total_processed_lines_str
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummyMatchContext, DummyFirstMatchModelElement, DummySequenceModelElement
import time


class ParserCountTest(TestBase):
    """Unittests for the ParserCount."""

    match_context_m1 = DummyMatchContext(b"First string")
    match_context_m2 = DummyMatchContext(b" to match.")
    match_context_m3 = DummyMatchContext(b"some completely other string to match.")
    match_context_seq = DummyMatchContext(b"First string to match.")
    fixed_dme_m1 = DummyFixedDataModelElement("m1", b"First string")
    fixed_dme_m2 = DummyFixedDataModelElement("m2", b" to match.")
    seq = DummySequenceModelElement("seq", [fixed_dme_m1, fixed_dme_m2])
    fixed_dme_m3 = DummyFixedDataModelElement("m3", b"some completely other string to match.")
    match_element_m1 = fixed_dme_m1.get_match_element("fixed", match_context_m1)
    match_element_m2 = fixed_dme_m2.get_match_element("fixed", match_context_m2)
    match_element_m3 = fixed_dme_m3.get_match_element("fixed", match_context_m3)
    match_element_seq = seq.get_match_element("fixed", match_context_seq)

    def test1receive_atom(self):
        """Test if the receive_atom method counts all paths properly."""
        # no path in the match_dictionary matches
        parser_count = ParserCount(self.aminer_config, ["fixed/seq", "fixed/seq/m1", "fixed/seq/m2"], [self.stream_printer_event_handler])
        t = time.time()
        log_atom = LogAtom(self.fixed_dme_m3.data, ParserMatch(self.match_element_m3), t, parser_count)
        old_count_dict = dict(parser_count.count_dict)
        parser_count.receive_atom(log_atom)
        self.assertEqual(parser_count.count_dict, old_count_dict)

        # single path matching
        parser_count = ParserCount(self.aminer_config, ["fixed/seq", "fixed/seq/m1", "fixed/seq/m2", "fixed/m3"], [self.stream_printer_event_handler])
        old_count_dict = dict(parser_count.count_dict)
        old_count_dict["fixed/m3"][current_processed_lines_str] = 1
        old_count_dict["fixed/m3"][total_processed_lines_str] = 1
        parser_count.receive_atom(log_atom)
        self.assertEqual(parser_count.count_dict, old_count_dict)

        # multiple paths matching
        parser_count = ParserCount(self.aminer_config, ["fixed/seq", "fixed/seq/m1", "fixed/seq/m2", "fixed/m3"], [self.stream_printer_event_handler])
        log_atom = LogAtom(self.match_context_seq.match_data, ParserMatch(self.match_element_seq), t, parser_count)
        old_count_dict = dict(parser_count.count_dict)
        old_count_dict["fixed/seq"][current_processed_lines_str] = 1
        old_count_dict["fixed/seq"][total_processed_lines_str] = 1
        old_count_dict["fixed/seq/m1"][current_processed_lines_str] = 1
        old_count_dict["fixed/seq/m1"][total_processed_lines_str] = 1
        old_count_dict["fixed/seq/m2"][current_processed_lines_str] = 1
        old_count_dict["fixed/seq/m2"][total_processed_lines_str] = 1
        parser_count.receive_atom(log_atom)
        self.assertEqual(parser_count.count_dict, old_count_dict)

        # multiple paths matching without having target_paths specified
        parser_count = ParserCount(self.aminer_config, None, [self.stream_printer_event_handler])
        t = time.time()
        log_atom = LogAtom(self.match_context_seq.match_data, ParserMatch(self.match_element_seq), t, parser_count)
        old_count_dict = dict(parser_count.count_dict)
        old_count_dict["fixed/seq"] = {current_processed_lines_str: 1, total_processed_lines_str: 1}
        parser_count.receive_atom(log_atom)
        self.assertEqual(parser_count.count_dict, old_count_dict)

    def test2do_timer(self):
        """Test if the do_timer method is implemented properly."""
        parser_count = ParserCount(self.aminer_config, ["fixed/seq", "fixed/seq/m1", "fixed/seq/m2"], [self.stream_printer_event_handler])
        t = time.time()
        parser_count.next_report_time = t + 40
        self.assertEqual(parser_count.do_timer(t + 20), 20)
        self.assertEqual(parser_count.do_timer(t + 40), parser_count.report_interval)
        self.assertEqual(parser_count.do_timer(t + 99), 1)
        self.assertEqual(parser_count.do_timer(t + 100), parser_count.report_interval)

    def test3send_report_resetting(self):
        """This unittest tests the functionality of resetting the counts."""
        parser_count = ParserCount(self.aminer_config, ["fixed/seq", "fixed/seq/m1", "fixed/seq/m2", "fixed/m3"], [self.stream_printer_event_handler], 600)
        parser_count.count_dict["fixed/seq"][current_processed_lines_str] = 5
        parser_count.count_dict["fixed/seq"][total_processed_lines_str] = 5
        parser_count.count_dict["fixed/seq/m1"][current_processed_lines_str] = 5
        parser_count.count_dict["fixed/seq/m1"][total_processed_lines_str] = 5
        parser_count.count_dict["fixed/seq/m2"][current_processed_lines_str] = 5
        parser_count.count_dict["fixed/seq/m2"][total_processed_lines_str] = 5
        parser_count.count_dict["fixed/m3"][current_processed_lines_str] = 17
        parser_count.count_dict["fixed/m3"][total_processed_lines_str] = 17
        old_count_dict = dict(parser_count.count_dict)
        parser_count.send_report()
        self.assertEqual(parser_count.count_dict, old_count_dict)
        parser_count.send_report()
        old_count_dict["fixed/seq"][current_processed_lines_str] = 0
        old_count_dict["fixed/seq/m1"][current_processed_lines_str] = 0
        old_count_dict["fixed/seq/m2"][current_processed_lines_str] = 0
        old_count_dict["fixed/m3"][current_processed_lines_str] = 0
        self.assertEqual(parser_count.count_dict, old_count_dict)

    def test4validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(ValueError, ParserCount, self.aminer_config, ["fixed/seq"], [])
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], ["default"])
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], None)
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], "")
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], b"Default")
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], True)
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], 123)
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], 123.3)
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], {"id": "Default"})
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], ())
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], set())

        self.assertRaises(ValueError, ParserCount, self.aminer_config, [""], [self.stream_printer_event_handler])
        self.assertRaises(TypeError, ParserCount, self.aminer_config, "", [self.stream_printer_event_handler])
        self.assertRaises(TypeError, ParserCount, self.aminer_config, b"Default", [self.stream_printer_event_handler])
        self.assertRaises(TypeError, ParserCount, self.aminer_config, True, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, ParserCount, self.aminer_config, 123, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, ParserCount, self.aminer_config, 123.22, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, ParserCount, self.aminer_config, {"id": "Default"}, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, ParserCount, self.aminer_config, (), [self.stream_printer_event_handler])
        self.assertRaises(TypeError, ParserCount, self.aminer_config, set(), [self.stream_printer_event_handler])

        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], report_interval="")
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], report_interval=None)
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], report_interval=b"Default")
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], report_interval=True)
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], report_interval={"id": "Default"})
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], report_interval=["Default"])
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], report_interval=[])
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], report_interval=())
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], report_interval=set())
        ParserCount(self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], report_interval=123)
        ParserCount(self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], report_interval=123.22)

        self.assertRaises(ValueError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], target_label_list=[])
        self.assertRaises(ValueError, ParserCount, self.aminer_config, None, [self.stream_printer_event_handler], target_label_list=["p"])
        self.assertRaises(ValueError, ParserCount, self.aminer_config, ["path1", "path2"], [self.stream_printer_event_handler], target_label_list=["p"])
        self.assertRaises(ValueError, ParserCount, self.aminer_config, ["path1"], [self.stream_printer_event_handler], target_label_list=["p1", "p2"])
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], target_label_list="")
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], target_label_list=b"Default")
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], target_label_list=True)
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], target_label_list={"id": "Default"})
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], target_label_list=123)
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], target_label_list=123.22)
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], target_label_list=())
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], target_label_list=set())
        ParserCount(self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], target_label_list=["p"])

        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], split_reports_flag="")
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], split_reports_flag=None)
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], split_reports_flag=b"Default")
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], split_reports_flag=123)
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], split_reports_flag=123.22)
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], split_reports_flag={"id": "Default"})
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], split_reports_flag=["Default"])
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], split_reports_flag=[])
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], split_reports_flag=())
        self.assertRaises(TypeError, ParserCount, self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], split_reports_flag=set())
        ParserCount(self.aminer_config, ["fixed/seq"], [self.stream_printer_event_handler], split_reports_flag=True)
