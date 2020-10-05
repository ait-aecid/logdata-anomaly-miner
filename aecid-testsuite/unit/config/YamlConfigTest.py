import unittest
import importlib
import yaml
import sys
# import json
# import shlex
# import configparser
# import uu
# import resource


class YamlConfigTest(unittest.TestCase):
    sysp = sys.path

    def setUp(self):
        sys.path = sys.path[1:] + ['/usr/lib/logdata-anomaly-miner', '/etc/aminer/conf-enabled']

    def tearDown(self):
        sys.path = self.sysp

    """ Loads a yaml file into the variable aminer_config.yaml_data """
    def test1_load_generic_yaml_file(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml('unit/data/configfiles/template_config.yml')
        self.assertIsNotNone(aminer_config.yaml_data)

    """ Tries to load a nonexistent yaml file. a FileNotFoundError is expected """
    def test2_load_notexistent_yaml_file(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(FileNotFoundError):
            aminer_config.load_yaml('unit/data/configfiles/doesnotexist.yml')

    """ Tries to load a file with invalid yaml syntax. Expects an YAMLError """
    def test3_load_invalid_yaml_file(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(yaml.YAMLError):
            aminer_config.load_yaml('unit/data/configfiles/invalid_config.yml')

    """ Tries to load a yaml-file with an invalid schema. A ValueError is expected """
    def test4_load_yaml_file_with_invalid_schema(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(ValueError):
            aminer_config.load_yaml('unit/data/configfiles/invalid_schema.yml')

    """ This test builds a analysis_pipeline from a valid yaml-file """
    def test5_analysis_pipeline_working_config(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml('unit/data/configfiles/apache_inline_config.yml')
        from aminer.AnalysisChild import AnalysisContext
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        """ the following lines help to debug the context for defining the testcases
        from pprint import pprint
        pprint(vars(context))
        pprint(vars(context.atomizer_factory))
        pprint(vars(context.atomizer_factory.parsing_model))
        pprint(vars(context.atomizer_factory.atom_handler_list[0])) """
        from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
        from aminer.analysis.NewMatchPathValueDetector import NewMatchPathValueDetector
        from aminer.analysis.NewMatchPathValueComboDetector import NewMatchPathValueComboDetector
        from aminer.analysis.HistogramAnalysis import HistogramAnalysis, PathDependentHistogramAnalysis
        from aminer.analysis.EnhancedNewMatchPathValueComboDetector import EnhancedNewMatchPathValueComboDetector
        from aminer.analysis.MatchFilter import MatchFilter
        from aminer.analysis.MatchValueAverageChangeDetector import MatchValueAverageChangeDetector
        from aminer.analysis.MatchValueStreamWriter import MatchValueStreamWriter
        from aminer.analysis.TimeCorrelationViolationDetector import TimeCorrelationViolationDetector
        from aminer.analysis.TimestampCorrectionFilters import SimpleMonotonicTimestampAdjust
        from aminer.analysis.TimestampsUnsortedDetector import TimestampsUnsortedDetector
        from aminer.analysis.WhitelistViolationDetector import WhitelistViolationDetector
        from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
        from aminer.events.SyslogWriterEventHandler import SyslogWriterEventHandler
        from aminer.events.DefaultMailNotificationEventHandler import DefaultMailNotificationEventHandler
        from aminer.parsing.SequenceModelElement import SequenceModelElement
        from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement
        from aminer.parsing.FixedDataModelElement import FixedDataModelElement
        from aminer.parsing.DateTimeModelElement import DateTimeModelElement
        from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
        from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
        self.assertTrue(isinstance(context.registered_components[0][0], NewMatchPathDetector))
        self.assertTrue(isinstance(context.registered_components[1][0], TimestampsUnsortedDetector))
        self.assertTrue(isinstance(context.registered_components[2][0], NewMatchPathValueDetector))
        self.assertTrue(isinstance(context.registered_components[3][0], NewMatchPathValueComboDetector))
        self.assertTrue(isinstance(context.registered_components[4][0], HistogramAnalysis))
        self.assertTrue(isinstance(context.registered_components[5][0], PathDependentHistogramAnalysis))
        self.assertTrue(isinstance(context.registered_components[6][0], EnhancedNewMatchPathValueComboDetector))
        self.assertTrue(isinstance(context.registered_components[7][0], MatchFilter))
        self.assertTrue(isinstance(context.registered_components[8][0], MatchValueAverageChangeDetector))
        self.assertTrue(isinstance(context.registered_components[9][0], MatchValueStreamWriter))
        self.assertTrue(isinstance(context.registered_components[10][0], NewMatchPathDetector))
        self.assertTrue(isinstance(context.registered_components[11][0], TimeCorrelationViolationDetector))
        self.assertTrue(isinstance(context.registered_components[12][0], SimpleMonotonicTimestampAdjust))
        self.assertTrue(isinstance(context.registered_components[13][0], WhitelistViolationDetector))
        self.assertTrue(isinstance(context.atomizer_factory.event_handler_list[0], StreamPrinterEventHandler))
        self.assertTrue(isinstance(context.atomizer_factory.event_handler_list[1], SyslogWriterEventHandler))
        self.assertTrue(isinstance(context.atomizer_factory.event_handler_list[2], DefaultMailNotificationEventHandler))
        self.assertEqual(context.atomizer_factory.default_timestamp_paths, '/accesslog/time')
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model, SequenceModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[0], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[1], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[2], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[3], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[4], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[5], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[6], DateTimeModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[7], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[8], FixedWordlistDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[9], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[10], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[11], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[12], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[13], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[14], DecimalIntegerValueModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[15], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[16], DecimalIntegerValueModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[17], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[18], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[19], FixedDataModelElement))
        self.assertEqual(context.atomizer_factory.parsing_model.element_id, 'accesslog')

    """ This test checks if the aminer fails without a start-tag for the first parser-model """
    def test6_analysis_fail_without_parser_start(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(ValueError):
            aminer_config.load_yaml('unit/data/configfiles/missing_parserstart_config.yml')

    """ This test checks if the aminer fails without a start-tag for the first parser-model """
    def test7_analysis_fail_with_double_parser_start(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(ValueError):
            aminer_config.load_yaml('unit/data/configfiles/double_parserstart_config.yml')

    """ This test checks if the config-schema-validator raises an error if an unknown parser is configured  """
    def test8_analysis_fail_with_unknown_parser_start(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(ValueError):
            aminer_config.load_yaml('unit/data/configfiles/unknown_parser_config.yml')

    """This test checks if the config can be loaded without any analysis components."""
    def test9_analysis_pipeline_working_config_with_analysis_components(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml('unit/data/configfiles/apache_inline_config_null_analysis_components.yml')
        from aminer.AnalysisChild import AnalysisContext
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        self.run_empty_analysis_components_tests(context)

        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml('unit/data/configfiles/apache_inline_config_undefined_analysis_components.yml')
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        self.run_empty_analysis_components_tests(context)

    def run_empty_analysis_components_tests(self, context):
        """ the following lines help to debug the context for defining the testcases
        from pprint import pprint
        pprint(vars(context))
        pprint(vars(context.atomizer_factory))
        pprint(vars(context.atomizer_factory.parsing_model))
        pprint(vars(context.atomizer_factory.atom_handler_list[0])) """
        from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
        from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
        from aminer.parsing.SequenceModelElement import SequenceModelElement
        from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement
        from aminer.parsing.FixedDataModelElement import FixedDataModelElement
        from aminer.parsing.DateTimeModelElement import DateTimeModelElement
        from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
        from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
        self.assertTrue(isinstance(context.registered_components[0][0], NewMatchPathDetector))
        self.assertTrue(isinstance(context.atomizer_factory.event_handler_list[0], StreamPrinterEventHandler))
        self.assertEqual(context.atomizer_factory.default_timestamp_paths, '/accesslog/time')
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model, SequenceModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[0], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[1], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[2], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[3], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[4], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[5], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[6], DateTimeModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[7], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[8], FixedWordlistDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[9], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[10], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[11], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[12], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[13], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[14], DecimalIntegerValueModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[15], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[16], DecimalIntegerValueModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[17], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[18], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[19], FixedDataModelElement))
        self.assertEqual(context.atomizer_factory.parsing_model.element_id, 'accesslog')


if __name__ == "__main__":
    unittest.main()
