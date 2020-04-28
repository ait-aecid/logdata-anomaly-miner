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
      self.linear_numeric_bin_definition = LinearNumericBinDefinition(0, 1, 10, True)
      self.assertEqual(self.linear_numeric_bin_definition.get_bin_names(), ['...-0]', '[0-1]', '[1-2]', '[2-3]',
        '[3-4]', '[4-5]', '[5-6]', '[6-7]', '[7-8]', '[8-9]', '[9-10]', '[10-...'])
      
      self.linear_numeric_bin_definition = LinearNumericBinDefinition(0, 2, 10, True)
      self.assertEqual(self.linear_numeric_bin_definition.get_bin_names(), ['...-0]', '[0-2]', '[2-4]', '[4-6]',
        '[6-8]', '[8-10]', '[10-12]', '[12-14]', '[14-16]', '[16-18]', '[18-20]', '[20-...'])
      
    '''
    This test case aims to test the functionality of the LinearNumericBinDefinition's get_bin method.
    '''
    def test2linear_numeric_bin_definition_get_bin(self):
      self.linear_numeric_bin_definition = LinearNumericBinDefinition(0, 1, 10, True)
      self.assertEqual(self.linear_numeric_bin_definition.get_bin(2), 3)
      
      self.linear_numeric_bin_definition = LinearNumericBinDefinition(1, 1, 10, True)
      self.assertEqual(self.linear_numeric_bin_definition.get_bin(2), 2)
      
      self.linear_numeric_bin_definition = LinearNumericBinDefinition(2, 1, 10, True)
      self.assertEqual(self.linear_numeric_bin_definition.get_bin(2), 1)
      
      self.linear_numeric_bin_definition = LinearNumericBinDefinition(0, 4, 10, True)
      self.assertEqual(self.linear_numeric_bin_definition.get_bin(2), 1)
    
    '''
    This test case aims to test the functionality of the LinearNumericBinDefinition's get_bin_p_values method.
    '''
    def test3linear_numeric_bin_definition_get_bin_p_values(self):
      self.linear_numeric_bin_definition = LinearNumericBinDefinition(0, 1, 10, True)
      self.assertNotEqual(self.linear_numeric_bin_definition.get_bin_p_value(2, 10, [2, 2]), None,
        'Probably the scipy module could not be loaded. Please check your installation.')
    
    '''
    This test case aims to test the functionality of the ModuloTimeBinDefinition's getBin method.
    '''
    def test4_modulo_time_bin_definition_get_bin(self):
      self.modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
      self.assertEqual(self.modulo_time_bin_definition.get_bin(57599), 15)
      self.assertEqual(self.modulo_time_bin_definition.get_bin(57600), 16)
      self.assertEqual(self.modulo_time_bin_definition.get_bin(61199), 16)
      self.assertEqual(self.modulo_time_bin_definition.get_bin(61200), 17)
    
    '''
    This test case aims to test the addition of Values to HistogramData class.
    '''
    def test5_histogram_data_add_value(self):
      self.modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
      self.histogram_data = HistogramData("crontab", self.modulo_time_bin_definition)
      self.histogram_data.add_value(57600)
      self.assertEqual(self.histogram_data.bin_data[16], 1)
      self.assertEqual(self.histogram_data.total_elements, 1)
      self.assertEqual(self.histogram_data.binned_elements, 0)
      
      self.histogram_data.add_value(61200)
      self.assertEqual(self.histogram_data.bin_data[16], 1)
      self.assertEqual(self.histogram_data.bin_data[17], 1)
      self.assertEqual(self.histogram_data.total_elements, 2)
      self.assertEqual(self.histogram_data.binned_elements, 0)
      
      self.histogram_data.add_value(61500)
      self.assertEqual(self.histogram_data.bin_data[16], 1)
      self.assertEqual(self.histogram_data.bin_data[17], 2)
      self.assertEqual(self.histogram_data.total_elements, 3)
      self.assertEqual(self.histogram_data.binned_elements, 0)
      
      self.histogram_data.add_value(100000)
      #100000%86400 = 13600 -> 3
      self.assertEqual(self.histogram_data.bin_data[3], 1)
      self.assertEqual(self.histogram_data.bin_data[16], 1)
      self.assertEqual(self.histogram_data.bin_data[17], 2)
      self.assertEqual(self.histogram_data.total_elements, 4)
      self.assertEqual(self.histogram_data.binned_elements, 0)
    
    '''
    This test case aims to test resetting the Values of the HistogramData class.
    '''
    def test6_histogram_data_reset(self):
      self.modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
      self.histogram_data = HistogramData("crontab", self.modulo_time_bin_definition)
      self.histogram_data.add_value(57600)
      self.histogram_data.add_value(61200)
      self.histogram_data.reset()
      self.assertEqual(self.histogram_data.total_elements, 0)
      self.assertEqual(self.histogram_data.binned_elements, 0)
      for item in self.histogram_data.bin_data:
        self.assertEqual(item, 0)
    
    '''
    This test case aims to test cloning a HistogramData object.
    '''
    def test7_histogram_data_clone(self):
      self.modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
      self.histogram_data = HistogramData("crontab", self.modulo_time_bin_definition)
      self.histogram_data.add_value(57600)
      self.histogram_data.add_value(61200)
      self.clone = self.histogram_data.clone()

      self.assertEqual(self.clone.bin_data[16], 1)
      self.assertEqual(self.clone.bin_data[17], 1)
      self.assertEqual(self.clone.total_elements, 2)
      self.assertEqual(self.clone.binned_elements, 0)
      
      self.clone.add_value(1)
      self.assertEqual(self.clone.bin_data[0], 1)
      self.assertEqual(self.histogram_data.bin_data[0], 0)
    
    '''
    This test case aims to test the functionality of the HistogramData's toString method.
    '''
    def test8_histogram_data_to_string(self):
      self.modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
      self.histogram_data = HistogramData("crontab", self.modulo_time_bin_definition)
      self.histogram_data.add_value(57600)
      
      self.histogram_data.add_value(61200)
      
      self.clone = self.histogram_data.clone()

      self.assertEqual(self.clone.bin_data[16], 1)
      self.assertEqual(self.clone.bin_data[17], 1)
      self.assertEqual(self.clone.total_elements, 2)
      self.assertEqual(self.clone.binned_elements, 0)
      
      self.clone.add_value(1)
      self.assertEqual(self.clone.bin_data[0], 1)
      self.assertEqual(self.histogram_data.bin_data[0], 0)
      self.assertEqual(self.clone.to_string(''), 'Property "crontab" (3 elements):\n* [0-1]: 1 (ratio = 3.33e-01, p = 1.20e-01)\n* [16-17]: 1 (ratio = 3.33e-01, p = 1.20e-01)\n* [17-18]: 1 (ratio = 3.33e-01, p = 1.20e-01)')
    
    '''
    This test case aims to test the functionality of the HistogramAnalysis's receiveAtom method, 
    when NO report is expected.
    '''
    def test9HistogramAnalysisReceiveAtomNoReport(self):
      description = "Test9HistogramAnalysis"
      self.start_time = 57600
      self.end_time = 662600
      self.diff = 30000
      
      self.modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
      self.histogram_data = HistogramData(self.match_crontab, self.modulo_time_bin_definition)
      self.histogram_analysis = HistogramAnalysis(self.aminer_config, [(self.histogram_data.property_path,
          self.modulo_time_bin_definition)], 604800, [self.stream_printer_event_handler], True, 'Default')
      self.analysis_context.register_component(self.histogram_analysis, description)
      self.match_element = MatchElement(self.match_crontab, self.start_time,
        self.start_time, [])
      
      t = time.time()
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element), t, self.histogram_analysis)
      self.histogram_analysis.receive_atom(self.log_atom)
      self.histogram_data.add_value(self.start_time)
      self.histogram_data.add_value(self.end_time)
      self.match_element = MatchElement(self.match_crontab, self.end_time, self.end_time, [])
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element),
        t + self.diff, self.histogram_analysis)
      self.histogram_analysis.receive_atom(self.log_atom)
      self.assertEqual(self.output_stream.getvalue(), '')
      
      #resetting the outputStream
      self.start_time = self.start_time + 3600
      self.end_time = self.end_time + 3600
      self.reset_output_stream()
      t = t+self.diff
      
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element), t, self.histogram_analysis)
      self.histogram_analysis.receive_atom(self.log_atom)
      
      self.histogram_data.add_value(self.start_time)
      self.histogram_data.add_value(self.end_time)
      self.match_element = MatchElement(self.match_crontab, self.end_time, self.end_time, [])
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element), t + self.diff, self.histogram_analysis)
      self.histogram_analysis.receive_atom(self.log_atom)
      self.assertEqual(self.output_stream.getvalue(), '')
    
    '''
    This test case aims to test the functionality of the HistogramAnalysis's receiveAtom method, 
    when A report is expected.
    '''
    def test10_histogram_analysis_receive_atom_report_expected(self):
      description = "Test10HistogramAnalysis"
      self.start_time = 57600
      self.end_time = 662600
      self.diff = 605000
      
      self.modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
      self.histogram_data = HistogramData(self.match_crontab, self.modulo_time_bin_definition)
      self.histogram_analysis = HistogramAnalysis(self.aminer_config, [(self.histogram_data.property_path, self.modulo_time_bin_definition)], 604800,
          [self.stream_printer_event_handler], True, 'Default')
      self.analysis_context.register_component(self.histogram_analysis, description)
      self.match_element = MatchElement(self.match_crontab, self.start_time, self.start_time, [])
      
      t = time.time()
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element), t, self.histogram_analysis)
      self.histogram_analysis.receive_atom(self.log_atom)
      self.histogram_data.add_value(self.start_time)
      self.histogram_data.add_value(self.end_time)
      self.match_element = MatchElement(self.match_crontab, self.end_time, self.end_time, [])
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element), t + self.diff, self.histogram_analysis)
      self.histogram_analysis.receive_atom(self.log_atom)
      
      self.assertEqual(self.output_stream.getvalue(),
        self.__expected_string_histogram_analysis % (datetime.fromtimestamp(t + self.diff).strftime(self.datetime_format_string),
        self.histogram_analysis.__class__.__name__, description, 2, datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        datetime.fromtimestamp(t+self.diff).strftime(self.datetime_format_string),
        'Property "match/crontab" (2 elements):\n  * [16-17]: 2 (ratio = 1.00e+00, p = 1.74e-03)'))
      
      #resetting the outputStream
      self.start_time = self.start_time + 3600
      self.end_time = self.end_time + 3600
      self.reset_output_stream()
      t = t+self.diff
      
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element), t, self.histogram_analysis)
      self.histogram_analysis.receive_atom(self.log_atom)
      self.histogram_data.add_value(self.start_time)
      self.histogram_data.add_value(self.end_time)
      self.match_element = MatchElement(self.match_crontab, self.end_time, self.end_time, [])
      
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element), t + self.diff, self.histogram_analysis)
      self.histogram_analysis.receive_atom(self.log_atom)
      
      self.assertEqual(self.output_stream.getvalue(),
        self.__expected_string_histogram_analysis % (datetime.fromtimestamp(t + self.diff).strftime(self.datetime_format_string),
        self.histogram_analysis.__class__.__name__, description, 2, datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        datetime.fromtimestamp(t+self.diff).strftime(self.datetime_format_string),
        'Property "match/crontab" (2 elements):\n  * [16-17]: 1 (ratio = 5.00e-01, p = 8.16e-02)\n  * [17-18]: 1 (ratio = 5.00e-01, p = 8.16e-02)'))
    
    '''
    This test case aims to test the functionality of the PathDependantHistogramAnalysis's receiveAtom method, 
    when NO report is expected.
    '''
    def test11_path_dependent_histogram_analysis_no_report(self):
      description = "Test11HistogramAnalysis"
      self.start_time = 57600
      self.end_time = 662600
      self.diff = 30000
      
      self.modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
      self.histogram_data = HistogramData(self.match_crontab, self.modulo_time_bin_definition)
      self.path_dependent_histogram_analysis = PathDependentHistogramAnalysis(self.aminer_config, self.histogram_data.property_path,
        self.modulo_time_bin_definition, 604800, [self.stream_printer_event_handler], True, 'Default')
      self.analysis_context.register_component(self.path_dependent_histogram_analysis, description)
      self.match_element = MatchElement(self.match_crontab, self.start_time, self.start_time, [])
      
      t = time.time()
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element), t, self.path_dependent_histogram_analysis)
      self.path_dependent_histogram_analysis.receive_atom(self.log_atom)
      self.histogram_data.add_value(self.start_time)
      self.histogram_data.add_value(self.end_time)
      self.match_element = MatchElement(self.match_crontab, self.end_time, self.end_time, [])
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element), t + self.diff, self.path_dependent_histogram_analysis)
      self.path_dependent_histogram_analysis.receive_atom(self.log_atom)
      self.assertEqual(self.output_stream.getvalue(), '')
          
      #resetting the outputStream
      self.start_time = self.start_time + 3600
      self.end_time = self.end_time + 3600
      self.reset_output_stream()
      t = t+self.diff
      
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element), t, self.path_dependent_histogram_analysis)
      self.path_dependent_histogram_analysis.receive_atom(self.log_atom)
      self.match_element = MatchElement(self.match_crontab, self.start_time, self.start_time, [])
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element), t, self.path_dependent_histogram_analysis)
      self.path_dependent_histogram_analysis.receive_atom(self.log_atom)
      self.histogram_data.add_value(self.start_time)
      self.histogram_data.add_value(self.end_time)
      self.histogram_data.add_value(self.start_time)
      self.histogram_data.add_value(self.end_time)
      self.match_element = MatchElement(self.match_crontab, self.end_time, self.end_time, [])
      
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element), t + self.diff, self.path_dependent_histogram_analysis)
      self.path_dependent_histogram_analysis.receive_atom(self.log_atom)
      self.match_element = MatchElement(self.match_crontab, self.end_time, self.end_time, [])
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element), t + self.diff, self.path_dependent_histogram_analysis)
      self.path_dependent_histogram_analysis.receive_atom(self.log_atom)
      self.assertEqual(self.output_stream.getvalue(), '')
    
    '''
    This test case aims to test the functionality of the PathDependantHistogramAnalysis's receiveAtom method, 
    when A report is expected.
    '''
    def test12_path_dependent_histogram_analysis_report_expected(self):
      description = "Test12HistogramAnalysis"
      self.start_time = 57600
      self.end_time = 662600
      self.diff = 605000
      
      self.modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, False)
      self.histogram_data = HistogramData(self.match_crontab, self.modulo_time_bin_definition)
      self.path_dependent_histogram_analysis = PathDependentHistogramAnalysis(self.aminer_config, self.histogram_data.property_path,
        self.modulo_time_bin_definition, 604800, [self.stream_printer_event_handler], True, 'Default')
      self.analysis_context.register_component(self.path_dependent_histogram_analysis, description)
      self.match_element = MatchElement(self.match_crontab, self.start_time, self.start_time, [])
      
      t = time.time()
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element), t, self.path_dependent_histogram_analysis)
      self.path_dependent_histogram_analysis.receive_atom(self.log_atom)
      self.histogram_data.add_value(self.start_time)
      self.histogram_data.add_value(self.end_time)
      self.match_element = MatchElement(self.match_crontab, self.end_time, self.end_time, [])
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element), t + self.diff, self.path_dependent_histogram_analysis)
      self.path_dependent_histogram_analysis.receive_atom(self.log_atom)
      self.assertEqual(self.output_stream.getvalue(),
        self.__expected_string_path_dependent_histogram_analysis % (datetime.fromtimestamp(t + self.diff).strftime(self.datetime_format_string),
        self.path_dependent_histogram_analysis.__class__.__name__, description, 2, datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        datetime.fromtimestamp(t+self.diff).strftime(self.datetime_format_string),
        'Path values "match/crontab":\nExample: 662600\n  Property "match/crontab" (2 elements):\n  * [16-17]: 2 (ratio = 1.00e+00, p = 1.74e-03)'))
      
      #resetting the outputStream
      self.start_time = self.start_time + 3600
      self.end_time = self.end_time + 3600
      self.output_stream.seek(0)
      self.output_stream.truncate(0)
      t = t+self.diff
      
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element), t, self.path_dependent_histogram_analysis)
      self.path_dependent_histogram_analysis.receive_atom(self.log_atom)
      self.match_element = MatchElement(self.match_crontab, self.start_time, self.start_time, [])
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element), t, self.path_dependent_histogram_analysis)
      self.path_dependent_histogram_analysis.receive_atom(self.log_atom)
      self.histogram_data.add_value(self.start_time)
      self.histogram_data.add_value(self.end_time)
      self.histogram_data.add_value(self.start_time)
      self.histogram_data.add_value(self.end_time)
      self.match_element = MatchElement(self.match_crontab, self.end_time, self.end_time, [])
      
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element), t + self.diff, self.path_dependent_histogram_analysis)
      self.path_dependent_histogram_analysis.receive_atom(self.log_atom)
      self.match_element = MatchElement(self.match_crontab, self.end_time, self.end_time, [])
      self.log_atom = LogAtom(self.histogram_data.bin_data, ParserMatch(self.match_element), t + self.diff, self.path_dependent_histogram_analysis)
      self.path_dependent_histogram_analysis.receive_atom(self.log_atom)
      self.assertEqual(self.output_stream.getvalue(),
        self.__expected_string_path_dependent_histogram_analysis % (datetime.fromtimestamp(t + self.diff).strftime(self.datetime_format_string),
        self.path_dependent_histogram_analysis.__class__.__name__, description, 3, datetime.fromtimestamp(t).strftime(self.datetime_format_string),
        datetime.fromtimestamp(t+self.diff).strftime(self.datetime_format_string),
        'Path values "match/crontab":\nExample: 666200\n  Property "match/crontab" (3 elements):\n  * [16-17]: 1 (ratio = 3.33e-01, p = 1.20e-01)\n  * [17-18]: 2 (ratio = 6.67e-01, p = 5.06e-03)'))


if __name__ == "__main__":
    unittest.main()
