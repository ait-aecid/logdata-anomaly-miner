import unittest
from aminer.analysis.HistogramAnalysis import LinearNumericBinDefinition, ModuloTimeBinDefinition, HistogramData, HistogramAnalysis, \
    PathDependentHistogramAnalysis
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
import time
from datetime import datetime
from aminer.parsing.MatchElement import MatchElement
from unit.TestBase import TestBase


class HistogramAnalysisTest(TestBase):
    """Unittests for the HistogramAnalysis."""

    def test1LinearNumericBinDefinition(self):
        """This test case aims to validate the functionality of the LinearNumericBinDefinition."""
        # test get_bin_names method
        self.assertEqual(LinearNumericBinDefinition(0, 1, 10, True).get_bin_names(), [
            "...-0]", "[0-1]", "[1-2]", "[2-3]", "[3-4]", "[4-5]", "[5-6]", "[6-7]", "[7-8]", "[8-9]", "[9-10]", "[10-..."])
        self.assertEqual(LinearNumericBinDefinition(0, 2, 10, True).get_bin_names(), [
            "...-0]", "[0-2]", "[2-4]", "[4-6]", "[6-8]", "[8-10]", "[10-12]", "[12-14]", "[14-16]", "[16-18]", "[18-20]", "[20-..."])

        # test get_bin method
        self.assertEqual(LinearNumericBinDefinition(0, 1, 10, True).get_bin(2), 3)
        self.assertEqual(LinearNumericBinDefinition(1, 1, 10, True).get_bin(2), 2)
        self.assertEqual(LinearNumericBinDefinition(2, 1, 10, True).get_bin(2), 1)
        self.assertEqual(LinearNumericBinDefinition(0, 4, 10, True).get_bin(2), 1)
        # test get_bin_p_values method
        lnbd = LinearNumericBinDefinition(0, 1, 10, True)
        self.assertNotEqual(lnbd.get_bin_p_value(2, 10, 2), None, "Probably the scipy module could not be loaded. Please check your installation.")

    def test2ModuloTimeBinDefinition(self):
        """This test case aims to validate the functionality of the ModuloTimeBinDefinition."""
        mtbd = ModuloTimeBinDefinition(86400, 3600, 0, 1, 10, False)
        self.assertEqual(mtbd.get_bin_names(), ["[0-1]", "[1-2]", "[2-3]", "[3-4]", "[4-5]", "[5-6]", "[6-7]", "[7-8]", "[8-9]", "[9-10]"])

        mtbd = ModuloTimeBinDefinition(86400, 3600, 0, 2, 10, False)
        self.assertEqual(mtbd.get_bin_names(), ["[0-2]", "[2-4]", "[4-6]", "[6-8]", "[8-10]", "[10-12]", "[12-14]", "[14-16]", "[16-18]", "[18-20]"])

        # test get_bin method
        modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
        self.assertEqual(modulo_time_bin_definition.get_bin(57599), 15)
        self.assertEqual(modulo_time_bin_definition.get_bin(57600), 16)
        self.assertEqual(modulo_time_bin_definition.get_bin(61199), 16)
        self.assertEqual(modulo_time_bin_definition.get_bin(61200), 17)

        # test get_bin_p_values method
        mtbd = ModuloTimeBinDefinition(86400, 3600, 0, 1, 10, False)
        self.assertNotEqual(mtbd.get_bin_p_value(2, 10, 2), None, "Probably the scipy module could not be loaded. Please check your installation.")

    def test3HistogramData(self):
        """This test case aims to validate the functionality of the HistogramData."""
        # test add_value method
        modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
        histogram_data = HistogramData("crontab", modulo_time_bin_definition)
        histogram_data.add_value(57600)
        self.assertEqual(histogram_data.bin_data[16], 1)
        self.assertEqual(histogram_data.total_elements, 1)
        self.assertEqual(histogram_data.binned_elements, 0)

        histogram_data.add_value(61200)
        self.assertEqual(histogram_data.bin_data[16], 1)
        self.assertEqual(histogram_data.bin_data[17], 1)
        self.assertEqual(histogram_data.total_elements, 2)
        self.assertEqual(histogram_data.binned_elements, 0)

        histogram_data.add_value(61500)
        self.assertEqual(histogram_data.bin_data[16], 1)
        self.assertEqual(histogram_data.bin_data[17], 2)
        self.assertEqual(histogram_data.total_elements, 3)
        self.assertEqual(histogram_data.binned_elements, 0)

        histogram_data.add_value(100000)
        # 100000%86400 = 13600 -> 3
        self.assertEqual(histogram_data.bin_data[3], 1)
        self.assertEqual(histogram_data.bin_data[16], 1)
        self.assertEqual(histogram_data.bin_data[17], 2)
        self.assertEqual(histogram_data.total_elements, 4)
        self.assertEqual(histogram_data.binned_elements, 0)

        # test clone method
        clone = histogram_data.clone()
        self.assertEqual(clone.bin_data[3], 1)
        self.assertEqual(clone.bin_data[16], 1)
        self.assertEqual(clone.bin_data[17], 2)
        self.assertEqual(clone.total_elements, 4)
        self.assertEqual(clone.binned_elements, 0)

        clone.add_value(1)
        self.assertEqual(clone.bin_data[0], 1)
        self.assertEqual(histogram_data.bin_data[0], 0)

        # test reset method
        histogram_data.reset()
        self.assertEqual(histogram_data.total_elements, 0)
        self.assertEqual(histogram_data.binned_elements, 0)
        for item in histogram_data.bin_data:
            self.assertEqual(item, 0)

        self.assertEqual(clone.bin_data[0], 1)
        self.assertEqual(clone.bin_data[3], 1)
        self.assertEqual(clone.bin_data[16], 1)
        self.assertEqual(clone.bin_data[17], 2)
        self.assertEqual(clone.total_elements, 5)
        self.assertEqual(clone.binned_elements, 0)

        # test to_string method
        self.assertEqual(clone.to_string(""), 'Property "crontab" (5 elements):\n* [0-1]: 1 (ratio = 2.00e-01, p = 1.92e-01)\n'
            '* [3-4]: 1 (ratio = 2.00e-01, p = 1.92e-01)\n* [16-17]: 1 (ratio = 2.00e-01, p = 1.92e-01)\n* [17-18]: 2 (ratio = 4.00e-01, p = 1.60e-02)')

    def test4receive_atom_HistogramAnalysis(self):
        """Test if reports on anomalies are generated correctly."""
        expected_string = '%s Histogram report\n%s: "None" (%d lines)\n  Histogram report from %s till %s\n  %s\n\n'
        datetime_format_string = "%Y-%m-%d %H:%M:%S"
        t = time.time()

        # test the functionality of the HistogramAnalysis, when NO report is expected
        start_time = 57600
        end_time = 662600
        diff = 30000
        mtbd = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
        histogram_data = HistogramData("match", mtbd)
        histogram_analysis = HistogramAnalysis(self.aminer_config, [(histogram_data.property_path, mtbd)], 604800, [self.stream_printer_event_handler])
        match_element_start = MatchElement("match", str(start_time).encode(), start_time, None)
        log_atom_start = LogAtom(histogram_data.bin_data, ParserMatch(match_element_start), t, histogram_analysis)
        match_element_end = MatchElement("match", str(end_time).encode(), end_time, None)
        log_atom_end = LogAtom(histogram_data.bin_data, ParserMatch(match_element_end), t + diff, histogram_analysis)

        histogram_analysis.receive_atom(log_atom_start)
        histogram_analysis.receive_atom(log_atom_end)
        self.assertEqual(self.output_stream.getvalue(), "")

        log_atom_start.atom_time += diff
        log_atom_end.atom_time += diff
        histogram_analysis.receive_atom(log_atom_start)
        histogram_analysis.receive_atom(log_atom_end)
        self.assertEqual(self.output_stream.getvalue(), "")

        # test the functionality of the HistogramAnalysis, when a report is expected.
        start_time = 57600
        end_time = 662600
        diff = 605000
        histogram_data.reset()
        histogram_analysis = HistogramAnalysis(self.aminer_config, [(histogram_data.property_path, mtbd)], 604800, [self.stream_printer_event_handler])
        match_element_start = MatchElement("match", str(start_time).encode(), start_time, None)
        log_atom_start = LogAtom(histogram_data.bin_data, ParserMatch(match_element_start), t, histogram_analysis)
        match_element_end = MatchElement("match", str(end_time).encode(), end_time, None)
        log_atom_end = LogAtom(histogram_data.bin_data, ParserMatch(match_element_end), t + diff, histogram_analysis)
        histogram_analysis.receive_atom(log_atom_start)
        histogram_analysis.receive_atom(log_atom_end)

        dtm = datetime.fromtimestamp(t).strftime(datetime_format_string)
        dtm2 = datetime.fromtimestamp(t + diff).strftime(datetime_format_string)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (dtm2, histogram_analysis.__class__.__name__, 2, dtm, dtm2,
            'Property "match" (2 elements):\n  * [16-17]: 2 (ratio = 1.00e+00, p = 1.74e-03)'))

        self.reset_output_stream()
        t1 = t + diff
        start_time += 3600
        end_time += 3600
        log_atom_start = LogAtom(histogram_data.bin_data, ParserMatch(match_element_start), t1, histogram_analysis)
        match_element_end = MatchElement("match", str(end_time).encode(), end_time, None)
        log_atom_end = LogAtom(histogram_data.bin_data, ParserMatch(match_element_end), t1 + diff, histogram_analysis)
        histogram_analysis.receive_atom(log_atom_start)
        histogram_analysis.receive_atom(log_atom_end)

        dtm = datetime.fromtimestamp(t1).strftime(datetime_format_string)
        dtm2 = datetime.fromtimestamp(t1 + diff).strftime(datetime_format_string)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (dtm2, histogram_analysis.__class__.__name__, 2, dtm, dtm2,
            'Property "match" (2 elements):\n  * [16-17]: 1 (ratio = 5.00e-01, p = 8.16e-02)\n  * [17-18]: 1 (ratio = 5.00e-01, p = 8.16e-02)'))

        # reset_after_report_flag = False
        start_time = 57600
        end_time = 662600
        diff = 605000
        histogram_data.reset()
        histogram_analysis = HistogramAnalysis(self.aminer_config, [(histogram_data.property_path, mtbd)], 604800, [self.stream_printer_event_handler], reset_after_report_flag=False)
        match_element_start = MatchElement("match", str(start_time).encode(), start_time, None)
        log_atom_start = LogAtom(histogram_data.bin_data, ParserMatch(match_element_start), t1, histogram_analysis)
        match_element_end = MatchElement("match", str(end_time).encode(), end_time, None)
        log_atom_end = LogAtom(histogram_data.bin_data, ParserMatch(match_element_end), t1 + diff, histogram_analysis)
        histogram_analysis.receive_atom(log_atom_start)
        histogram_analysis.receive_atom(log_atom_end)

        dtm = datetime.fromtimestamp(t1).strftime(datetime_format_string)
        dtm2 = datetime.fromtimestamp(t1 + diff).strftime(datetime_format_string)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (dtm2, histogram_analysis.__class__.__name__, 2, dtm, dtm2,
            'Property "match" (2 elements):\n  * [16-17]: 1 (ratio = 5.00e-01, p = 8.16e-02)\n  * [17-18]: 1 (ratio = 5.00e-01, p = 8.16e-02)') +
            expected_string % (dtm2, histogram_analysis.__class__.__name__, 2, dtm, dtm2, 'Property "match" (2 elements):\n  * [16-17]: 2 (ratio = 1.00e+00, p = 1.74e-03)'))

        self.reset_output_stream()
        t2 = t1 + diff
        start_time += 3600
        end_time += 3600
        log_atom_start = LogAtom(histogram_data.bin_data, ParserMatch(match_element_start), t2, histogram_analysis)
        match_element_end = MatchElement("match", str(end_time).encode(), end_time, None)
        log_atom_end = LogAtom(histogram_data.bin_data, ParserMatch(match_element_end), t2 + diff, histogram_analysis)
        histogram_analysis.receive_atom(log_atom_start)
        histogram_analysis.receive_atom(log_atom_end)

        dtm = datetime.fromtimestamp(t2).strftime(datetime_format_string)
        dtm2 = datetime.fromtimestamp(t2 + diff).strftime(datetime_format_string)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (dtm2, histogram_analysis.__class__.__name__, 4, dtm, dtm2,
             'Property "match" (4 elements):\n  * [16-17]: 3 (ratio = 7.50e-01, p = 2.80e-04)\n  * [17-18]: 1 (ratio = 2.50e-01, p = 1.57e-01)'))

    def test5receive_atom_PathDependentHistogramAnalysis(self):
        """Test if reports on anomalies are generated correctly."""
        expected_string = '%s Histogram report\n%s: "None" (%d lines)\n  Path histogram report from %s till %s\n%s\n\n'
        datetime_format_string = "%Y-%m-%d %H:%M:%S"
        t = time.time()

        # test the functionality of the HistogramAnalysis, when NO report is expected
        start_time = 57600
        end_time = 662600
        diff = 30000
        mtbd = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
        histogram_data = HistogramData("match", mtbd)
        pdha = PathDependentHistogramAnalysis(self.aminer_config, histogram_data.property_path, mtbd, 604800, [self.stream_printer_event_handler], True)
        match_element_start = MatchElement("match", str(start_time).encode(), start_time, None)
        log_atom_start = LogAtom(histogram_data.bin_data, ParserMatch(match_element_start), t, pdha)
        match_element_end = MatchElement("match", str(end_time).encode(), end_time, None)
        log_atom_end = LogAtom(histogram_data.bin_data, ParserMatch(match_element_end), t + diff, pdha)

        pdha.receive_atom(log_atom_start)
        pdha.receive_atom(log_atom_end)
        self.assertEqual(self.output_stream.getvalue(), "")

        log_atom_start.atom_time += diff
        log_atom_end.atom_time += diff
        pdha.receive_atom(log_atom_start)
        pdha.receive_atom(log_atom_end)
        self.assertEqual(self.output_stream.getvalue(), "")

        # test the functionality of the HistogramAnalysis, when a report is expected.
        start_time = 57600
        end_time = 662600
        diff = 605000
        histogram_data.reset()
        pdha = PathDependentHistogramAnalysis(self.aminer_config, histogram_data.property_path, mtbd, 604800, [self.stream_printer_event_handler], True)
        match_element_start = MatchElement("match", str(start_time).encode(), start_time, None)
        log_atom_start = LogAtom(histogram_data.bin_data, ParserMatch(match_element_start), t, pdha)
        match_element_end = MatchElement("match", str(end_time).encode(), end_time, None)
        log_atom_end = LogAtom(histogram_data.bin_data, ParserMatch(match_element_end), t + diff, pdha)
        pdha.receive_atom(log_atom_start)
        pdha.receive_atom(log_atom_end)

        dtm = datetime.fromtimestamp(t).strftime(datetime_format_string)
        dtm2 = datetime.fromtimestamp(t + diff).strftime(datetime_format_string)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (dtm2, pdha.__class__.__name__, 2, dtm, dtm2,
            'Path values "match":\nExample: 662600\n  Property "match" (2 elements):\n  * [16-17]: 2 (ratio = 1.00e+00, p = 1.74e-03)'))

        self.reset_output_stream()
        t1 = t + diff
        start_time += 3600
        end_time += 3600
        log_atom_start = LogAtom(histogram_data.bin_data, ParserMatch(match_element_start), t1, pdha)
        match_element_end = MatchElement("match", str(end_time).encode(), end_time, None)
        log_atom_end = LogAtom(histogram_data.bin_data, ParserMatch(match_element_end), t1 + diff, pdha)
        pdha.receive_atom(log_atom_start)
        pdha.receive_atom(log_atom_end)

        dtm = datetime.fromtimestamp(t1).strftime(datetime_format_string)
        dtm2 = datetime.fromtimestamp(t1 + diff).strftime(datetime_format_string)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (dtm2, pdha.__class__.__name__, 2, dtm, dtm2,
            'Path values "match":\nExample: 666200\n  Property "match" (2 elements):\n  * [16-17]: 1 (ratio = 5.00e-01, p = 8.16e-02)\n  * [17-18]: 1 (ratio = 5.00e-01, p = 8.16e-02)'))

        # reset_after_report_flag = False
        start_time = 57600
        end_time = 662600
        diff = 605000
        histogram_data.reset()
        pdha = PathDependentHistogramAnalysis(self.aminer_config, histogram_data.property_path, mtbd, 604800, [self.stream_printer_event_handler], reset_after_report_flag=False)
        match_element_start = MatchElement("match", str(start_time).encode(), start_time, None)
        log_atom_start = LogAtom(histogram_data.bin_data, ParserMatch(match_element_start), t1, pdha)
        match_element_end = MatchElement("match", str(end_time).encode(), end_time, None)
        log_atom_end = LogAtom(histogram_data.bin_data, ParserMatch(match_element_end), t1 + diff, pdha)
        pdha.receive_atom(log_atom_start)
        pdha.receive_atom(log_atom_end)

        dtm = datetime.fromtimestamp(t1).strftime(datetime_format_string)
        dtm2 = datetime.fromtimestamp(t1 + diff).strftime(datetime_format_string)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (dtm2, pdha.__class__.__name__, 2, dtm, dtm2,
            'Path values "match":\nExample: 666200\n  Property "match" (2 elements):\n  * [16-17]: 1 (ratio = 5.00e-01, p = 8.16e-02)\n  * [17-18]: 1 (ratio = 5.00e-01, p = 8.16e-02)') +
            expected_string % (dtm2, pdha.__class__.__name__, 2, dtm, dtm2,
            'Path values "match":\nExample: 662600\n  Property "match" (2 elements):\n  * [16-17]: 2 (ratio = 1.00e+00, p = 1.74e-03)'))

        self.reset_output_stream()
        t2 = t1 + diff
        start_time += 3600
        end_time += 3600
        log_atom_start = LogAtom(histogram_data.bin_data, ParserMatch(match_element_start), t2, pdha)
        match_element_end = MatchElement("match", str(end_time).encode(), end_time, None)
        log_atom_end = LogAtom(histogram_data.bin_data, ParserMatch(match_element_end), t2 + diff, pdha)
        pdha.receive_atom(log_atom_start)
        pdha.receive_atom(log_atom_end)

        dtm = datetime.fromtimestamp(t2).strftime(datetime_format_string)
        dtm2 = datetime.fromtimestamp(t2 + diff).strftime(datetime_format_string)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (dtm2, pdha.__class__.__name__, 4, dtm, dtm2,
            'Path values "match":\nExample: 666200\n  Property "match" (4 elements):\n  * [16-17]: 3 (ratio = 7.50e-01, p = 2.80e-04)\n  * [17-18]: 1 (ratio = 2.50e-01, p = 1.57e-01)'))

    def test6validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(TypeError, LinearNumericBinDefinition, "0", 1, 1, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, b"0", 1, 1, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, [0], 1, 1, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, {0: 0}, 1, 1, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, set(), 1, 1, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, True, 1, 1, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, (0,), 1, 1, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, None, 1, 1, True)

        self.assertRaises(ValueError, LinearNumericBinDefinition, 1, -1, 1, True)
        self.assertRaises(ValueError, LinearNumericBinDefinition, 1, 0, 1, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, 1.1, 1, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, True, 1, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, "1", 1, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, b"1", 1, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, [1], 1, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, {1: 1}, 1, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, set(), 1, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, (1,), 1, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, None, 1, True)

        self.assertRaises(ValueError, LinearNumericBinDefinition, 1, 1, -1, True)
        self.assertRaises(ValueError, LinearNumericBinDefinition, 1, 1, 0, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, 1, 1.1, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, 1, True, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, 1, "1", True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, 1, b"1", True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, 1, [1], True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, 1, {1: 1}, True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, 1, set(), True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, 1, (1,), True)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, 1, None, True)

        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, 1, 1, 1)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, 1, 1, 1.1)
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, 1, 1, "1")
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, 1, 1, b"1")
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, 1, 1, [1])
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, 1, 1, {1: 1})
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, 1, 1, set())
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, 1, 1, (1,))
        self.assertRaises(TypeError, LinearNumericBinDefinition, 1, 1, 1, None)

        LinearNumericBinDefinition(-100, 1, 1, True)
        lnbd = LinearNumericBinDefinition(0, 1, 1, False)
        LinearNumericBinDefinition(100, 1, 1, False)
        LinearNumericBinDefinition(100.3, 1, 1, False)

        self.assertRaises(ValueError, ModuloTimeBinDefinition, 0, 3600, 1, 1, 1, True)
        self.assertRaises(ValueError, ModuloTimeBinDefinition, -1, 3600, 1, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, True, 3600, 1, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, "1", 3600, 1, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, b"1", 3600, 1, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, [1], 3600, 1, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, {1: 1}, 3600, 1, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, set(), 3600, 1, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, (1,), 3600, 1, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, None, 3600, 1, 1, 1, True)

        self.assertRaises(ValueError, ModuloTimeBinDefinition, 86400, 0, 1, 1, 1, True)
        self.assertRaises(ValueError, ModuloTimeBinDefinition, 86400, -1, 1, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 1.1, 1, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, True, 1, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, "1", 1, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, b"1", 1, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, [1], 1, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, {1: 1}, 1, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, set(), 1, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, (1,), 1, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, None, 1, 1, 1, True)

        self.assertRaises(ValueError, ModuloTimeBinDefinition, 86400, 3600, -1, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, "0", 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, b"0", 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, [0], 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, {0: 0}, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, set(), 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, True, 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, (0,), 1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, None, 1, 1, True)

        self.assertRaises(ValueError, ModuloTimeBinDefinition, 86400, 3600, 1, -1, 1, True)
        self.assertRaises(ValueError, ModuloTimeBinDefinition, 86400, 3600, 1, 0, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, 1.1, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, True, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, "1", 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, b"1", 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, [1], 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, {1: 1}, 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, set(), 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, (1,), 1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, None, 1, True)

        self.assertRaises(ValueError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, -1, True)
        self.assertRaises(ValueError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, 0, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, 1.1, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, True, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, "1", True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, b"1", True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, [1], True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, {1: 1}, True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, set(), True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, (1,), True)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, None, True)

        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, 1, 1)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, 1, 1.1)
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, 1, "1")
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, 1, b"1")
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, 1, [1])
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, 1, {1: 1})
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, 1, set())
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, 1, (1,))
        self.assertRaises(TypeError, ModuloTimeBinDefinition, 86400, 3600, 1, 1, 1, None)

        ModuloTimeBinDefinition(0.1, 1, 0, 1, 1, True)
        mtbd = ModuloTimeBinDefinition(86400, 3600, 100, 1, 1, False)
        ModuloTimeBinDefinition(86400, 3600, 100.3, 1, 1, False)

        self.assertRaises(ValueError, HistogramData, "", mtbd)
        self.assertRaises(TypeError, HistogramData, None, mtbd)
        self.assertRaises(TypeError, HistogramData, 1, mtbd)
        self.assertRaises(TypeError, HistogramData, 1.1, mtbd)
        self.assertRaises(TypeError, HistogramData, True, mtbd)
        self.assertRaises(TypeError, HistogramData, b"match", mtbd)
        self.assertRaises(TypeError, HistogramData, [1], mtbd)
        self.assertRaises(TypeError, HistogramData, {1: 1}, mtbd)
        self.assertRaises(TypeError, HistogramData, set(), mtbd)
        self.assertRaises(TypeError, HistogramData, (1,), mtbd)

        self.assertRaises(TypeError, HistogramData, "match", None)
        self.assertRaises(TypeError, HistogramData, "match", 1)
        self.assertRaises(TypeError, HistogramData, "match", 1.1)
        self.assertRaises(TypeError, HistogramData, "match", True)
        self.assertRaises(TypeError, HistogramData, "match", b"match")
        self.assertRaises(TypeError, HistogramData, "match", [1])
        self.assertRaises(TypeError, HistogramData, "match", {1: 1})
        self.assertRaises(TypeError, HistogramData, "match", set())
        self.assertRaises(TypeError, HistogramData, "match", (1,))

        HistogramData("match", mtbd)
        HistogramData("match", lnbd)

        defs = [("path", mtbd)]
        self.assertRaises(ValueError, HistogramAnalysis, self.aminer_config, [], 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, [("path", "path")], 100, [self.stream_printer_event_handler])
        self.assertRaises(ValueError, HistogramAnalysis, self.aminer_config, [("", mtbd)], 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, ["default"], 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, b"Default", 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, True, 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, 123, 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, 123.3, 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, {"id": "Default"}, 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, (), 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, set(), 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, None, 100, [self.stream_printer_event_handler])

        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, ["default"], [self.stream_printer_event_handler])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, None, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, "", [self.stream_printer_event_handler])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, b"Default", [self.stream_printer_event_handler])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, True, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100.1, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, {"id": "Default"}, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, (), [self.stream_printer_event_handler])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, set(), [self.stream_printer_event_handler])

        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, ["default"])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, None)
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, "")
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, b"Default")
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, True)
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, 123)
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, 123.3)
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, {"id": "Default"})
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, ())
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, set())

        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], reset_after_report_flag=["default"])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], reset_after_report_flag=None)
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], reset_after_report_flag="")
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], reset_after_report_flag=b"Default")
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], reset_after_report_flag=123)
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], reset_after_report_flag=123.3)
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], reset_after_report_flag={"id": "Default"})
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], reset_after_report_flag=())
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], reset_after_report_flag=set())

        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], output_logline=["default"])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], output_logline=None)
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], output_logline="")
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], output_logline=b"Default")
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], output_logline=123)
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], output_logline=123.3)
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], output_logline={"id": "Default"})
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], output_logline=())
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], output_logline=set())

        self.assertRaises(ValueError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], log_resource_ignore_list=["/tmp/syslog"])
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], log_resource_ignore_list="")
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], log_resource_ignore_list=b"Default")
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], log_resource_ignore_list=True)
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], log_resource_ignore_list=123)
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], log_resource_ignore_list=123.22)
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], log_resource_ignore_list={"id": "Default"})
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], log_resource_ignore_list=())
        self.assertRaises(TypeError, HistogramAnalysis, self.aminer_config, defs, 100, [self.stream_printer_event_handler], log_resource_ignore_list=set())
        HistogramAnalysis(self.aminer_config, defs, 100, [self.stream_printer_event_handler], log_resource_ignore_list=["file:///tmp/syslog"])

        self.assertRaises(ValueError, PathDependentHistogramAnalysis, self.aminer_config, "", mtbd, 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, b"path", mtbd, 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, ["default"], mtbd, 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, b"Default", mtbd, 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, True, mtbd, 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, 123, mtbd, 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, 123.3, mtbd, 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, {"id": "Default"}, mtbd, 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, (), mtbd, 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, set(), mtbd, 100, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, None, mtbd, 100, [self.stream_printer_event_handler])

        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", [mtbd], ["default"], [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", b"path", ["default"], [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", "", ["default"], [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", True, ["default"], [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", 123.3, ["default"], [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", {"id": "Default"}, ["default"], [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", (), ["default"], [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", set(), ["default"], [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", None, ["default"], [self.stream_printer_event_handler])

        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, ["default"], [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, None, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, "", [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, b"Default", [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, True, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100.1, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, {"id": "Default"}, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, (), [self.stream_printer_event_handler])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, set(), [self.stream_printer_event_handler])

        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, ["default"])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, None)
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, "")
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, b"Default")
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, True)
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, 123)
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, 123.3)
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, {"id": "Default"})
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, ())
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, set())

        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], reset_after_report_flag=["default"])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], reset_after_report_flag=None)
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], reset_after_report_flag="")
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], reset_after_report_flag=b"Default")
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], reset_after_report_flag=123)
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], reset_after_report_flag=123.3)
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], reset_after_report_flag={"id": "Default"})
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], reset_after_report_flag=())
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], reset_after_report_flag=set())

        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], output_logline=["default"])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], output_logline=None)
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], output_logline="")
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], output_logline=b"Default")
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], output_logline=123)
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], output_logline=123.3)
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], output_logline={"id": "Default"})
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], output_logline=())
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], output_logline=set())

        self.assertRaises(ValueError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], log_resource_ignore_list=["/tmp/syslog"])
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], log_resource_ignore_list="")
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], log_resource_ignore_list=b"Default")
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], log_resource_ignore_list=True)
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], log_resource_ignore_list=123)
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], log_resource_ignore_list=123.22)
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], log_resource_ignore_list={"id": "Default"})
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], log_resource_ignore_list=())
        self.assertRaises(TypeError, PathDependentHistogramAnalysis, self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], log_resource_ignore_list=set())
        PathDependentHistogramAnalysis(self.aminer_config, "path", mtbd, 100, [self.stream_printer_event_handler], log_resource_ignore_list=["file:///tmp/syslog"])


if __name__ == "__main__":
    unittest.main()
