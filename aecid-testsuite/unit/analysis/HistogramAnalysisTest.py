import unittest
from aminer.analysis.HistogramAnalysis import LinearNumericBinDefinition,\
  ModuloTimeBinDefinition, HistogramData, HistogramAnalysis,\
  PathDependentHistogramAnalysis
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
import time
from datetime import datetime
from aminer.parsing.MatchElement import MatchElement
from unit.TestBase import TestBase


class HistogramAnalysisTest(TestBase):
    __expected_string_histogram_analysis = '%s Histogram report\n%s: "%s" (%d lines)\n  Histogram report from %s till %s\n  %s\n\n'
    __expected_string_path_dependent_histogram_analysis = '%s Histogram report\n%s: "%s" (%d lines)\n  Path histogram report from %s till %s\n%s\n\n'

    match_crontab = 'match/crontab'
    datetime_format_string = '%Y-%m-%d %H:%M:%S'
    
    '''
    This test case aims to test the functionality of the LinearNumericBinDefinition's get_bin_names method.
    '''
    def test1linear_numeric_bin_definition_get_bin_names(self):
      linear_numeric_bin_definition = LinearNumericBinDefinition(0, 1, 10, True)
      self.assertEqual(linear_numeric_bin_definition.get_bin_names(), ['...-0]', '[0-1]', '[1-2]', '[2-3]',
        '[3-4]', '[4-5]', '[5-6]', '[6-7]', '[7-8]', '[8-9]', '[9-10]', '[10-...'])
      
      linear_numeric_bin_definition = LinearNumericBinDefinition(0, 2, 10, True)
      self.assertEqual(linear_numeric_bin_definition.get_bin_names(), ['...-0]', '[0-2]', '[2-4]', '[4-6]',
        '[6-8]', '[8-10]', '[10-12]', '[12-14]', '[14-16]', '[16-18]', '[18-20]', '[20-...'])
      
    '''
    This test case aims to test the functionality of the LinearNumericBinDefinition's get_bin method.
    '''
    def test2linear_numeric_bin_definition_get_bin(self):
      linear_numeric_bin_definition = LinearNumericBinDefinition(0, 1, 10, True)
      self.assertEqual(linear_numeric_bin_definition.get_bin(2), 3)
      
      linear_numeric_bin_definition = LinearNumericBinDefinition(1, 1, 10, True)
      self.assertEqual(linear_numeric_bin_definition.get_bin(2), 2)
      
      linear_numeric_bin_definition = LinearNumericBinDefinition(2, 1, 10, True)
      self.assertEqual(linear_numeric_bin_definition.get_bin(2), 1)
      
      linear_numeric_bin_definition = LinearNumericBinDefinition(0, 4, 10, True)
      self.assertEqual(linear_numeric_bin_definition.get_bin(2), 1)
    
    '''
    This test case aims to test the functionality of the LinearNumericBinDefinition's get_bin_p_values method.
    '''
    def test3linear_numeric_bin_definition_get_bin_p_values(self):
      linear_numeric_bin_definition = LinearNumericBinDefinition(0, 1, 10, True)
      self.assertNotEqual(linear_numeric_bin_definition.get_bin_p_value(2, 10, [2, 2]), None,
        'Probably the scipy module could not be loaded. Please check your installation.')
    
    '''
    This test case aims to test the functionality of the ModuloTimeBinDefinition's getBin method.
    '''
    def test4_modulo_time_bin_definition_get_bin(self):
      modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
      self.assertEqual(modulo_time_bin_definition.get_bin(57599), 15)
      self.assertEqual(modulo_time_bin_definition.get_bin(57600), 16)
      self.assertEqual(modulo_time_bin_definition.get_bin(61199), 16)
      self.assertEqual(modulo_time_bin_definition.get_bin(61200), 17)
    
    '''
    This test case aims to test the addition of Values to HistogramData class.
    '''
    def test5_histogram_data_add_value(self):
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
    
    '''
    This test case aims to test resetting the Values of the HistogramData class.
    '''
    def test6_histogram_data_reset(self):
      modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
      histogram_data = HistogramData("crontab", modulo_time_bin_definition)
      histogram_data.add_value(57600)
      histogram_data.add_value(61200)
      histogram_data.reset()
      self.assertEqual(histogram_data.total_elements, 0)
      self.assertEqual(histogram_data.binned_elements, 0)
      for item in histogram_data.bin_data:
        self.assertEqual(item, 0)
    
    '''
    This test case aims to test cloning a HistogramData object.
    '''
    def test7_histogram_data_clone(self):
      modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
      histogram_data = HistogramData("crontab", modulo_time_bin_definition)
      histogram_data.add_value(57600)
      histogram_data.add_value(61200)
      clone = histogram_data.clone()

      self.assertEqual(clone.bin_data[16], 1)
      self.assertEqual(clone.bin_data[17], 1)
      self.assertEqual(clone.total_elements, 2)
      self.assertEqual(clone.binned_elements, 0)
      
      clone.add_value(1)
      self.assertEqual(clone.bin_data[0], 1)
      self.assertEqual(histogram_data.bin_data[0], 0)
    
    '''
    This test case aims to test the functionality of the HistogramData's toString method.
    '''
    def test8_histogram_data_to_string(self):
      modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
      histogram_data = HistogramData("crontab", modulo_time_bin_definition)
      histogram_data.add_value(57600)
      
      histogram_data.add_value(61200)
      
      clone = histogram_data.clone()

      self.assertEqual(clone.bin_data[16], 1)
      self.assertEqual(clone.bin_data[17], 1)
      self.assertEqual(clone.total_elements, 2)
      self.assertEqual(clone.binned_elements, 0)
      
      clone.add_value(1)
      self.assertEqual(clone.bin_data[0], 1)
      self.assertEqual(histogram_data.bin_data[0], 0)
      self.assertEqual(clone.to_string(''), 'Property "crontab" (3 elements):\n* [0-1]: 1 (ratio = 3.33e-01, p = 1.20e-01)\n* [16-17]: 1 (ratio = 3.33e-01, p = 1.20e-01)\n* [17-18]: 1 (ratio = 3.33e-01, p = 1.20e-01)')
    
    '''
    This test case aims to test the functionality of the HistogramAnalysis's receiveAtom method, 
    when NO report is expected.
    '''
    def test9HistogramAnalysisReceiveAtomNoReport(self):
      description = "Test9HistogramAnalysis"
      start_time = 57600
      end_time = 662600
      diff = 30000
      
      modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
      histogram_data = HistogramData(self.match_crontab, modulo_time_bin_definition)
      histogram_analysis = HistogramAnalysis(self.aminer_config, [(histogram_data.property_path,
          modulo_time_bin_definition)], 604800, [self.stream_printer_event_handler], True, 'Default')
      self.analysis_context.register_component(histogram_analysis, description)
      match_element = MatchElement(self.match_crontab, start_time,
        start_time, [])
      
      t = time.time()
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t, histogram_analysis)
      histogram_analysis.receive_atom(log_atom)
      histogram_data.add_value(start_time)
      histogram_data.add_value(end_time)
      match_element = MatchElement(self.match_crontab, end_time, end_time, [])
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element),
        t + diff, histogram_analysis)
      histogram_analysis.receive_atom(log_atom)
      self.assertEqual(self.output_stream.getvalue(), '')
      
      # resetting the outputStream
      start_time = start_time + 3600
      end_time = end_time + 3600
      self.reset_output_stream()
      t = t + diff
      
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t, histogram_analysis)
      histogram_analysis.receive_atom(log_atom)
      
      histogram_data.add_value(start_time)
      histogram_data.add_value(end_time)
      match_element = MatchElement(self.match_crontab, end_time, end_time, [])
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t + diff, histogram_analysis)
      histogram_analysis.receive_atom(log_atom)
      self.assertEqual(self.output_stream.getvalue(), '')
    
    '''
    This test case aims to test the functionality of the HistogramAnalysis's receiveAtom method, 
    when A report is expected.
    '''
    def test10_histogram_analysis_receive_atom_report_expected(self):
      description = "Test10HistogramAnalysis"
      start_time = 57600
      end_time = 662600
      diff = 605000
      
      modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
      histogram_data = HistogramData(self.match_crontab, modulo_time_bin_definition)
      histogram_analysis = HistogramAnalysis(self.aminer_config, [(histogram_data.property_path, modulo_time_bin_definition)], 604800,
          [self.stream_printer_event_handler], True, 'Default')
      self.analysis_context.register_component(histogram_analysis, description)
      match_element = MatchElement(self.match_crontab, start_time, start_time, [])
      
      t = time.time()
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t, histogram_analysis)
      histogram_analysis.receive_atom(log_atom)
      histogram_data.add_value(start_time)
      histogram_data.add_value(end_time)
      match_element = MatchElement(self.match_crontab, end_time, end_time, [])
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t + diff, histogram_analysis)
      histogram_analysis.receive_atom(log_atom)
      
      self.assertEqual(self.output_stream.getvalue(),
        self.__expected_string_histogram_analysis % (datetime.fromtimestamp(t + diff).strftime(self.datetime_format_string),
        histogram_analysis.__class__.__name__, description, 2, datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        datetime.fromtimestamp(t + diff).strftime(self.datetime_format_string),
        'Property "match/crontab" (2 elements):\n  * [16-17]: 2 (ratio = 1.00e+00, p = 1.74e-03)'))
      
      # resetting the outputStream
      start_time = start_time + 3600
      end_time = end_time + 3600
      self.reset_output_stream()
      t = t + diff
      
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t, histogram_analysis)
      histogram_analysis.receive_atom(log_atom)
      histogram_data.add_value(start_time)
      histogram_data.add_value(end_time)
      match_element = MatchElement(self.match_crontab, end_time, end_time, [])
      
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t + diff, histogram_analysis)
      histogram_analysis.receive_atom(log_atom)
      
      self.assertEqual(self.output_stream.getvalue(),
        self.__expected_string_histogram_analysis % (datetime.fromtimestamp(t + diff).strftime(self.datetime_format_string),
        histogram_analysis.__class__.__name__, description, 2, datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        datetime.fromtimestamp(t + diff).strftime(self.datetime_format_string),
        'Property "match/crontab" (2 elements):\n  * [16-17]: 1 (ratio = 5.00e-01, p = 8.16e-02)\n  * [17-18]: 1 (ratio = 5.00e-01, p = 8.16e-02)'))
    
    '''
    This test case aims to test the functionality of the PathDependantHistogramAnalysis's receiveAtom method, 
    when NO report is expected.
    '''
    def test11_path_dependent_histogram_analysis_no_report(self):
      description = "Test11HistogramAnalysis"
      start_time = 57600
      end_time = 662600
      diff = 30000
      
      modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
      histogram_data = HistogramData(self.match_crontab, modulo_time_bin_definition)
      path_dependent_histogram_analysis = PathDependentHistogramAnalysis(self.aminer_config, histogram_data.property_path,
        modulo_time_bin_definition, 604800, [self.stream_printer_event_handler], True, 'Default')
      self.analysis_context.register_component(path_dependent_histogram_analysis, description)
      match_element = MatchElement(self.match_crontab, start_time, start_time, [])
      
      t = time.time()
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t, path_dependent_histogram_analysis)
      path_dependent_histogram_analysis.receive_atom(log_atom)
      histogram_data.add_value(start_time)
      histogram_data.add_value(end_time)
      match_element = MatchElement(self.match_crontab, end_time, end_time, [])
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t + diff, path_dependent_histogram_analysis)
      path_dependent_histogram_analysis.receive_atom(log_atom)
      self.assertEqual(self.output_stream.getvalue(), '')
          
      # resetting the outputStream
      start_time = start_time + 3600
      end_time = end_time + 3600
      self.reset_output_stream()
      t = t + diff
      
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t, path_dependent_histogram_analysis)
      path_dependent_histogram_analysis.receive_atom(log_atom)
      match_element = MatchElement(self.match_crontab, start_time, start_time, [])
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t, path_dependent_histogram_analysis)
      path_dependent_histogram_analysis.receive_atom(log_atom)
      histogram_data.add_value(start_time)
      histogram_data.add_value(end_time)
      histogram_data.add_value(start_time)
      histogram_data.add_value(end_time)
      match_element = MatchElement(self.match_crontab, end_time, end_time, [])
      
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t + diff, path_dependent_histogram_analysis)
      path_dependent_histogram_analysis.receive_atom(log_atom)
      match_element = MatchElement(self.match_crontab, end_time, end_time, [])
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t + diff, path_dependent_histogram_analysis)
      path_dependent_histogram_analysis.receive_atom(log_atom)
      self.assertEqual(self.output_stream.getvalue(), '')
    
    '''
    This test case aims to test the functionality of the PathDependantHistogramAnalysis's receiveAtom method, 
    when A report is expected.
    '''
    def test12_path_dependent_histogram_analysis_report_expected(self):
      description = "Test12HistogramAnalysis"
      start_time = 57600
      end_time = 662600
      diff = 605000
      
      modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
      histogram_data = HistogramData(self.match_crontab, modulo_time_bin_definition)
      path_dependent_histogram_analysis = PathDependentHistogramAnalysis(self.aminer_config, histogram_data.property_path,
        modulo_time_bin_definition, 604800, [self.stream_printer_event_handler], True, 'Default')
      self.analysis_context.register_component(path_dependent_histogram_analysis, description)
      match_element = MatchElement(self.match_crontab, start_time, start_time, [])
      
      t = time.time()
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t, path_dependent_histogram_analysis)
      path_dependent_histogram_analysis.receive_atom(log_atom)
      histogram_data.add_value(start_time)
      histogram_data.add_value(end_time)
      match_element = MatchElement(self.match_crontab, end_time, end_time, [])
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t + diff, path_dependent_histogram_analysis)
      path_dependent_histogram_analysis.receive_atom(log_atom)
      self.assertEqual(self.output_stream.getvalue(),
        self.__expected_string_path_dependent_histogram_analysis % (datetime.fromtimestamp(t + diff).strftime(self.datetime_format_string),
        path_dependent_histogram_analysis.__class__.__name__, description, 2, datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        datetime.fromtimestamp(t + diff).strftime(self.datetime_format_string),
        'Path values "match/crontab":\nExample: 662600\n  Property "match/crontab" (2 elements):\n  * [16-17]: 2 (ratio = 1.00e+00, p = 1.74e-03)'))
      
      # resetting the outputStream
      start_time = start_time + 3600
      end_time = end_time + 3600
      self.output_stream.seek(0)
      self.output_stream.truncate(0)
      t = t + diff
      
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t, path_dependent_histogram_analysis)
      path_dependent_histogram_analysis.receive_atom(log_atom)
      match_element = MatchElement(self.match_crontab, start_time, start_time, [])
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t, path_dependent_histogram_analysis)
      path_dependent_histogram_analysis.receive_atom(log_atom)
      histogram_data.add_value(start_time)
      histogram_data.add_value(end_time)
      histogram_data.add_value(start_time)
      histogram_data.add_value(end_time)
      match_element = MatchElement(self.match_crontab, end_time, end_time, [])
      
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t + diff, path_dependent_histogram_analysis)
      path_dependent_histogram_analysis.receive_atom(log_atom)
      match_element = MatchElement(self.match_crontab, end_time, end_time, [])
      log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t + diff, path_dependent_histogram_analysis)
      path_dependent_histogram_analysis.receive_atom(log_atom)
      self.assertEqual(self.output_stream.getvalue(),
        self.__expected_string_path_dependent_histogram_analysis % (datetime.fromtimestamp(t + diff).strftime(self.datetime_format_string),
        path_dependent_histogram_analysis.__class__.__name__, description, 3, datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        datetime.fromtimestamp(t + diff).strftime(self.datetime_format_string),
        'Path values "match/crontab":\nExample: 666200\n  Property "match/crontab" (3 elements):\n  * [16-17]: 1 (ratio = 3.33e-01, p = 1.20e-01)\n  * [17-18]: 2 (ratio = 6.67e-01, p = 5.06e-03)'))


if __name__ == "__main__":
    unittest.main()
