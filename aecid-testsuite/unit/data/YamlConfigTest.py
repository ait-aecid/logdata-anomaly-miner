import unittest
import importlib
import yaml
import sys
import re
import aminer.AminerConfig as AminerConfig
from datetime import datetime
from aminer.AnalysisChild import AnalysisContext
from aminer.analysis.AtomFilters import SubhandlerFilter
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
from aminer.analysis.AllowlistViolationDetector import AllowlistViolationDetector
from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
from aminer.events.SyslogWriterEventHandler import SyslogWriterEventHandler
from aminer.events.DefaultMailNotificationEventHandler import DefaultMailNotificationEventHandler
from aminer.events.JsonConverterHandler import JsonConverterHandler
from aminer.input.SimpleByteStreamLineAtomizerFactory import SimpleByteStreamLineAtomizerFactory
from aminer.input.SimpleMultisourceAtomSync import SimpleMultisourceAtomSync
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.DateTimeModelElement import DateTimeModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.RepeatedElementDataModelElement import RepeatedElementDataModelElement
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement
from aminer.parsing.ElementValueBranchModelElement import ElementValueBranchModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.ParserMatch import ParserMatch
from aminer.input.LogAtom import LogAtom
from time import time
from unit.TestBase import TestBase


class YamlConfigTest(TestBase):
    """Unittests for the YamlConfig."""

    sysp = sys.path

    def setUp(self):
        """Add the aminer syspath."""
        TestBase.setUp(self)
        sys.path = sys.path[1:] + ['/usr/lib/logdata-anomaly-miner', '/etc/aminer/conf-enabled']

    def tearDown(self):
        """Reset the syspath."""
        TestBase.tearDown(self)
        sys.path = self.sysp

    def test1_load_generic_yaml_file(self):
        """Loads a yaml file into the variable aminer_config.yaml_data."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml('unit/data/configfiles/template_config.yml')
        self.assertIsNotNone(aminer_config.yaml_data)

    def test2_load_notexistent_yaml_file(self):
        """Tries to load a nonexistent yaml file. A FileNotFoundError is expected."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(FileNotFoundError):
            aminer_config.load_yaml('unit/data/configfiles/doesnotexist.yml')

    def test3_load_invalid_yaml_file(self):
        """Tries to load a file with invalid yaml syntax. Expects an YAMLError."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(yaml.YAMLError):
            aminer_config.load_yaml('unit/data/configfiles/invalid_config.yml')

    def test4_load_yaml_file_with_invalid_schema(self):
        """Tries to load a yaml-file with an invalid schema. A ValueError is expected."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(ValueError):
            aminer_config.load_yaml('unit/data/configfiles/invalid_schema.yml')

    def test5_analysis_pipeline_working_config(self):
        """This test builds a analysis_pipeline from a valid yaml-file."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml('unit/data/configfiles/multiple_components.yml')
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        self.assertTrue(isinstance(context.registered_components[0][0], SubhandlerFilter))
        self.assertTrue(isinstance(context.registered_components[1][0], NewMatchPathDetector))
        self.assertTrue(isinstance(context.registered_components[2][0], TimestampsUnsortedDetector))
        self.assertTrue(isinstance(context.registered_components[3][0], NewMatchPathValueDetector))
        self.assertTrue(isinstance(context.registered_components[4][0], NewMatchPathValueComboDetector))
        self.assertTrue(isinstance(context.registered_components[5][0], HistogramAnalysis))
        self.assertTrue(isinstance(context.registered_components[6][0], PathDependentHistogramAnalysis))
        self.assertTrue(isinstance(context.registered_components[7][0], EnhancedNewMatchPathValueComboDetector))
        self.assertTrue(isinstance(context.registered_components[8][0], MatchFilter))
        self.assertTrue(isinstance(context.registered_components[9][0], MatchValueAverageChangeDetector))
        self.assertTrue(isinstance(context.registered_components[10][0], MatchValueStreamWriter))
        self.assertTrue(isinstance(context.registered_components[11][0], NewMatchPathDetector))
        self.assertTrue(isinstance(context.registered_components[12][0], TimeCorrelationViolationDetector))
        self.assertTrue(isinstance(context.registered_components[13][0], SimpleMonotonicTimestampAdjust))
        self.assertTrue(isinstance(context.registered_components[14][0], AllowlistViolationDetector))
        self.assertTrue(isinstance(context.atomizer_factory.event_handler_list[0], StreamPrinterEventHandler))
        self.assertTrue(isinstance(context.atomizer_factory.event_handler_list[1], SyslogWriterEventHandler))
        self.assertTrue(isinstance(context.atomizer_factory.event_handler_list[2], DefaultMailNotificationEventHandler))
        self.assertEqual(context.atomizer_factory.default_timestamp_paths, ['/accesslog/time'])
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model, SequenceModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[0], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[1], FixedDataModelElement))
        self.assertEqual(context.atomizer_factory.parsing_model.children[1].element_id, 'sp0')
        self.assertEqual(context.atomizer_factory.parsing_model.children[1].fixed_data, b' ')
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[2], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[3], FixedDataModelElement))
        self.assertEqual(context.atomizer_factory.parsing_model.children[3].element_id, 'sp1')
        self.assertEqual(context.atomizer_factory.parsing_model.children[3].fixed_data, b' ')
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[4], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[5], FixedDataModelElement))
        self.assertEqual(context.atomizer_factory.parsing_model.children[5].element_id, 'sp2')
        self.assertEqual(context.atomizer_factory.parsing_model.children[5].fixed_data, b' ')
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[6], DateTimeModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[7], FixedDataModelElement))
        self.assertEqual(context.atomizer_factory.parsing_model.children[7].element_id, 'sq3')
        self.assertEqual(context.atomizer_factory.parsing_model.children[7].fixed_data, b' "')
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[8], FixedWordlistDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[9], FixedDataModelElement))
        self.assertEqual(context.atomizer_factory.parsing_model.children[9].element_id, 'sp3')
        self.assertEqual(context.atomizer_factory.parsing_model.children[9].fixed_data, b' ')
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[10], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[11], FixedDataModelElement))
        self.assertEqual(context.atomizer_factory.parsing_model.children[11].element_id, 'http1')
        self.assertEqual(context.atomizer_factory.parsing_model.children[11].fixed_data, b' HTTP/')
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[12], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[13], FixedDataModelElement))
        self.assertEqual(context.atomizer_factory.parsing_model.children[13].element_id, 'sq4')
        self.assertEqual(context.atomizer_factory.parsing_model.children[13].fixed_data, b'" ')
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[14], DecimalIntegerValueModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[15], FixedDataModelElement))
        self.assertEqual(context.atomizer_factory.parsing_model.children[15].element_id, 'sp4')
        self.assertEqual(context.atomizer_factory.parsing_model.children[15].fixed_data, b' ')
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[16], DecimalIntegerValueModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[17], FixedDataModelElement))
        self.assertEqual(context.atomizer_factory.parsing_model.children[17].element_id, 'sq5')
        self.assertEqual(context.atomizer_factory.parsing_model.children[17].fixed_data, b' "-" "')
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[18], VariableByteDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[19], FixedDataModelElement))
        self.assertEqual(context.atomizer_factory.parsing_model.element_id, 'accesslog')

    def test6_analysis_fail_without_parser_start(self):
        """This test checks if the aminer fails without a start-tag for the first parser-model."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(ValueError):
            aminer_config.load_yaml('unit/data/configfiles/missing_parserstart_config.yml')

    def test7_analysis_fail_with_double_parser_start(self):
        """This test checks if the aminer fails without a start-tag for the first parser-model."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(ValueError):
            aminer_config.load_yaml('unit/data/configfiles/double_parserstart_config.yml')

    def test8_analysis_fail_with_unknown_parser_start(self):
        """This test checks if the config-schema-validator raises an error if an unknown parser is configured."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(ValueError):
            aminer_config.load_yaml('unit/data/configfiles/unknown_parser_config.yml')

    def test9_analysis_pipeline_working_config_without_analysis_components(self):
        """This test checks if the config can be loaded without any analysis components."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml('unit/data/configfiles/multiple_components_null_analysis_components.yml')
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        self.run_empty_components_tests(context)

        del aminer_config.yaml_data['Analysis']
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        self.run_empty_components_tests(context)

    def test10_analysis_fail_with_unknown_analysis_component(self):
        """This test checks if the config-schema-validator raises an error if an unknown analysis component is configured."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(ValueError):
            aminer_config.load_yaml('unit/data/configfiles/unknown_analysis_component.yml')

    def test11_analysis_fail_with_unknown_event_handler(self):
        """This test checks if the config-schema-validator raises an error if an unknown event handler is configured."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(ValueError):
            aminer_config.load_yaml('unit/data/configfiles/unknown_event_handler.yml')

    def test12_analysis_pipeline_working_config_without_event_handler_components(self):
        """
        This test checks if the config can be loaded without any event handler components.
        This also tests if the StreamPrinterEventHandler was loaded by default.
        """
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml('unit/data/configfiles/multiple_components_null_event_handlers.yml')
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        self.run_empty_components_tests(context)

        del aminer_config.yaml_data['EventHandlers']
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        self.run_empty_components_tests(context)

    def test13_analysis_pipeline_working_with_json(self):
        """This test checks if JsonConverterHandler is working properly."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml('unit/data/configfiles/json_config.yml')
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        self.assertTrue(isinstance(context.registered_components[0][0], SubhandlerFilter))
        self.assertTrue(isinstance(context.registered_components[1][0], NewMatchPathDetector))
        self.assertTrue(isinstance(context.atomizer_factory.event_handler_list[0], JsonConverterHandler))
        self.assertTrue(isinstance(context.atomizer_factory.event_handler_list[0].json_event_handlers[0], StreamPrinterEventHandler))
        self.assertEqual(context.atomizer_factory.default_timestamp_paths, ['/accesslog/time'])
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model, SequenceModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[0], VariableByteDataModelElement))

    def test14_analysis_pipeline_working_with_learnMode(self):
        """This test checks if learnMode is working properly."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml('unit/data/configfiles/learnMode_config.yml')
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        self.assertTrue(isinstance(context.registered_components[0][0], SubhandlerFilter))
        self.assertTrue(isinstance(context.registered_components[1][0], NewMatchPathDetector))
        self.assertTrue(isinstance(context.registered_components[2][0], NewMatchPathValueDetector))
        self.assertTrue(isinstance(context.registered_components[3][0], NewMatchPathValueComboDetector))
        self.assertTrue(isinstance(context.atomizer_factory.event_handler_list[0], StreamPrinterEventHandler))
        self.assertEqual(context.atomizer_factory.default_timestamp_paths, ['/accesslog/time'])
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model, SequenceModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[0], VariableByteDataModelElement))

        # specific learn_mode arguments should be preferred.
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        self.assertTrue(context.registered_components[1][0].auto_include_flag)
        self.assertTrue(context.registered_components[2][0].auto_include_flag)
        self.assertFalse(context.registered_components[3][0].auto_include_flag)

        # unset specific learn_mode parameters and set LearnMode True.
        for component in aminer_config.yaml_data['Analysis']:
            del component['learn_mode']
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        for key in context.registered_components:
            if hasattr(context.registered_components[key][0], 'auto_include_flag'):
                self.assertTrue(context.registered_components[key][0].auto_include_flag)

        # unset specific learn_mode parameters and set LearnMode False.
        aminer_config.yaml_data['LearnMode'] = False
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        for key in context.registered_components:
            if hasattr(context.registered_components[key][0], 'auto_include_flag'):
                self.assertFalse(context.registered_components[key][0].auto_include_flag)

        # unset LearnMode config property. An Error should be raised.
        del aminer_config.yaml_data['LearnMode']
        context = AnalysisContext(aminer_config)
        self.assertRaises(ValueError, context.build_analysis_pipeline)

    def test15_analysis_pipeline_working_with_input_parameters(self):
        """This test checks if the SimpleMultisourceAtomSync and SimpleByteStreamLineAtomizerFactory are working properly."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml('unit/data/configfiles/multiSource_config.yml')
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        self.assertTrue(isinstance(context.registered_components[0][0], SubhandlerFilter))
        self.assertTrue(isinstance(context.registered_components[1][0], NewMatchPathDetector))
        self.assertTrue(isinstance(context.registered_components[2][0], NewMatchPathValueDetector))
        self.assertTrue(isinstance(context.registered_components[3][0], NewMatchPathValueComboDetector))
        self.assertTrue(isinstance(context.atomizer_factory.event_handler_list[0], StreamPrinterEventHandler))
        self.assertEqual(context.atomizer_factory.default_timestamp_paths, ['/model/accesslog/time'])
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model, SequenceModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[0], VariableByteDataModelElement))

        # test with MultiSource: True. Expects a SimpleByteStreamLineAtomizerFactory with a SimpleMultisourceAtomSync.
        self.assertTrue(isinstance(context.atomizer_factory, SimpleByteStreamLineAtomizerFactory))
        self.assertTrue(isinstance(context.atomizer_factory.atom_handler_list[0], SimpleMultisourceAtomSync))
        self.assertEqual(context.atomizer_factory.default_timestamp_paths, [aminer_config.yaml_data['Input']['timestamp_paths']])

        # test with MultiSource: False. Expects a SimpleByteStreamLineAtomizerFactory with a AtomFilters.SubhandlerFilter.
        aminer_config.yaml_data['Input']['multi_source'] = False
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        self.assertTrue(isinstance(context.atomizer_factory, SimpleByteStreamLineAtomizerFactory))
        self.assertTrue(isinstance(context.atomizer_factory.atom_handler_list[0], SubhandlerFilter))
        self.assertEqual(context.atomizer_factory.default_timestamp_paths, [aminer_config.yaml_data['Input']['timestamp_paths']])

    def test16_parsermodeltype_parameter_for_another_parsermodel_type(self):
        """This test checks if all ModelElements with child elements are working properly."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml('unit/data/configfiles/parser_child_elements_config.yml')
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        self.assertTrue(isinstance(context.registered_components[0][0], SubhandlerFilter))
        self.assertTrue(isinstance(context.registered_components[1][0], NewMatchPathDetector))
        self.assertTrue(isinstance(context.registered_components[2][0], NewMatchPathValueDetector))
        self.assertTrue(isinstance(context.registered_components[3][0], NewMatchPathValueComboDetector))
        self.assertTrue(isinstance(context.atomizer_factory.event_handler_list[0], StreamPrinterEventHandler))
        self.assertEqual(context.atomizer_factory.default_timestamp_paths, ['/model/accesslog/time'])
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model, FirstMatchModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[0], SequenceModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[0].children[0], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[0].children[1], RepeatedElementDataModelElement))
        self.assertTrue(isinstance(
            context.atomizer_factory.parsing_model.children[0].children[1].repeated_element, OptionalMatchModelElement))
        self.assertTrue(isinstance(
            context.atomizer_factory.parsing_model.children[0].children[1].repeated_element.optional_element, FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[1], FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[2], ElementValueBranchModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[2].value_model, FixedDataModelElement))
        self.assertTrue(isinstance(context.atomizer_factory.parsing_model.children[2].branch_model_dict['host'], FixedDataModelElement))

        # change OptionalModelElement to unknown_model
        aminer_config.yaml_data['Parser'][1]['args'] = b'unknown_model'
        context = AnalysisContext(aminer_config)
        self.assertRaises(ValueError, context.build_analysis_pipeline)
        aminer_config.load_yaml('unit/data/configfiles/parser_child_elements_config.yml')

        # change RepeatedElementDataModelElement to unknown_model
        aminer_config.yaml_data['Parser'][2]['args'][0] = b'unknown_model'
        context = AnalysisContext(aminer_config)
        self.assertRaises(ValueError, context.build_analysis_pipeline)
        aminer_config.load_yaml('unit/data/configfiles/parser_child_elements_config.yml')

        # change SequenceModelElement to unknown_model
        aminer_config.yaml_data['Parser'][3]['args'][1] = b'unknown_model'
        context = AnalysisContext(aminer_config)
        self.assertRaises(ValueError, context.build_analysis_pipeline)
        aminer_config.load_yaml('unit/data/configfiles/parser_child_elements_config.yml')

        # change ElementValueBranchModelElement to unknown_model
        aminer_config.yaml_data['Parser'][4]['args'][0] = b'unknown_model'
        context = AnalysisContext(aminer_config)
        self.assertRaises(ValueError, context.build_analysis_pipeline)
        aminer_config.load_yaml('unit/data/configfiles/parser_child_elements_config.yml')

        aminer_config.yaml_data['Parser'][4]['branch_model_dict'][0]['model'] = b'unknown_model'
        context = AnalysisContext(aminer_config)
        self.assertRaises(ValueError, context.build_analysis_pipeline)
        aminer_config.load_yaml('unit/data/configfiles/parser_child_elements_config.yml')

        # change FirstMatchModelElement to unknown_model
        aminer_config.yaml_data['Parser'][5]['args'][1] = b'unknown_model'
        context = AnalysisContext(aminer_config)
        self.assertRaises(ValueError, context.build_analysis_pipeline)
        aminer_config.load_yaml('unit/data/configfiles/parser_child_elements_config.yml')

    def test17_demo_yaml_config_equals_python_config(self):
        """This test checks if the yaml demo config is the same as the python version."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml('demo/aminer/demo-config.yml')
        yml_context = AnalysisContext(aminer_config)
        yml_context.build_analysis_pipeline()

        aminer_config = AminerConfig.load_config('demo/aminer/demo-config.py')
        py_context = AnalysisContext(aminer_config)
        py_context.build_analysis_pipeline()

        import copy
        yml_config_properties = copy.deepcopy(yml_context.aminer_config.config_properties)
        del yml_config_properties['Parser']
        del yml_config_properties['Input']
        del yml_config_properties['Analysis']
        del yml_config_properties['EventHandlers']
        del yml_config_properties['LearnMode']
        del yml_config_properties['SuppressNewMatchPathDetector']

        # remove SimpleUnparsedAtomHandler, VerboseUnparsedAtomHandler and NewMatchPathDetector as they are added by the YamlConfig.
        py_registered_components = copy.copy(py_context.registered_components)
        del py_registered_components[0]
        del py_registered_components[1]
        del py_registered_components[2]
        del py_registered_components[10]
        yml_registered_components = copy.copy(yml_context.registered_components)
        del yml_registered_components[0]
        del yml_registered_components[1]
        tmp = {}
        keys = list(py_registered_components.keys())
        for i in range(1, len(py_registered_components)+1):
            tmp[i] = py_registered_components[keys[i-1]]
        py_registered_components = tmp
        py_registered_components_by_name = copy.copy(py_context.registered_components_by_name)
        del py_registered_components_by_name['SimpleUnparsedHandler']
        del py_registered_components_by_name['VerboseUnparsedHandler']
        del py_registered_components_by_name['NewMatchPath']
        del py_registered_components_by_name['SimpleMonotonicTimestampAdjust']
        yml_registered_components_by_name = copy.copy(yml_context.registered_components_by_name)
        del yml_registered_components_by_name['DefaultNewMatchPathDetector']
        del yml_registered_components_by_name['AtomFilter']

        self.assertEqual(yml_config_properties, py_context.aminer_config.config_properties)
        # there actually is no easy way to compare aminer components as they do not implement the __eq__ method.
        self.assertEqual(len(yml_registered_components), len(py_registered_components))
        for i in range(2, len(yml_registered_components)):  # skipcq: PTC-W0060
            self.assertEqual(type(yml_registered_components[i]), type(py_registered_components[i]))
        self.assertEqual(yml_registered_components_by_name.keys(), py_registered_components_by_name.keys())
        for name in yml_registered_components_by_name.keys():
            self.assertEqual(type(yml_registered_components_by_name[name]), type(py_registered_components_by_name[name]))
        self.assertEqual(len(yml_context.real_time_triggered_components), len(py_context.real_time_triggered_components))
        # the atom_handler_list is not equal as the python version uses a SimpleMonotonicTimestampAdjust.
        self.assertEqual(yml_context.atomizer_factory.default_timestamp_paths, py_context.atomizer_factory.default_timestamp_paths)
        self.assertEqual(type(yml_context.atomizer_factory.event_handler_list), type(py_context.atomizer_factory.event_handler_list))

    def test18_etd_order(self):
        """Loads the template_config and checks if the position of the ETD was changed as expected."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml('unit/data/configfiles/template_config.yml')
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        self.assertEqual(context.aminer_config.yaml_data['Analysis'][0]['type'].name, 'EventTypeDetector')
        self.assertEqual(context.aminer_config.yaml_data['Analysis'][1]['type'].name, 'NewMatchPathValueDetector')
        self.assertEqual(context.aminer_config.yaml_data['Analysis'][2]['type'].name, 'NewMatchPathValueComboDetector')
        self.assertEqual(context.aminer_config.yaml_data['Analysis'][3]['type'].name, 'NewMatchPathValueComboDetector')

    def test19_stream_printer_output_file(self):
        """Check if the output_file_path property of StreamPrinterEventHandler works properly."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml('unit/data/configfiles/template_config.yml')
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        self.assertEqual(context.atomizer_factory.event_handler_list[0].stream.name, '/tmp/streamPrinter.txt')
        self.assertEqual(context.atomizer_factory.event_handler_list[0].stream.mode, 'w+')

    def test20_suppress_output(self):
        """
        Check if the suppress property and SuppressNewMatchPathDetector are working as expected.
        This test only includes the StreamPrinterEventHandler.
        """
        __expected_string1 = '%s New path(es) detected\n%s: "%s" (%d lines)\n  %s\n%s\n\n'
        t = time()
        fixed_dme = FixedDataModelElement('s1', b' pid=')
        match_context_fixed_dme = MatchContext(b' pid=')
        match_element_fixed_dme = fixed_dme.get_match_element("", match_context_fixed_dme)
        log_atom_fixed_dme = LogAtom(fixed_dme.fixed_data, ParserMatch(match_element_fixed_dme), t, 'DefaultNewMatchPathDetector')
        datetime_format_string = '%Y-%m-%d %H:%M:%S'
        match_path_s1 = "['/s1']"
        pid = " pid="
        __expected_string2 = '%s New value combination(s) detected\n%s: "%s" (%d lines)\n%s\n\n'
        fixed_dme2 = FixedDataModelElement('s1', b'25537 uid=')
        decimal_integer_value_me = DecimalIntegerValueModelElement(
            'd1', DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
        match_context_sequence_me = MatchContext(b'25537 uid=2')
        seq = SequenceModelElement('seq', [fixed_dme2, decimal_integer_value_me])
        match_element_sequence_me = seq.get_match_element('first', match_context_sequence_me)
        string2 = "  (b'25537 uid=', 2)\n25537 uid=2"

        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml('unit/data/configfiles/suppress_config.yml')
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()

        context.aminer_config.yaml_data['SuppressNewMatchPathDetector'] = False
        self.stream_printer_event_handler = context.atomizer_factory.event_handler_list[0]
        self.stream_printer_event_handler.stream = self.output_stream
        default_nmpd = context.registered_components[1][0]
        default_nmpd.output_log_line = False
        self.assertTrue(default_nmpd.receive_atom(log_atom_fixed_dme))
        self.assertEqual(self.output_stream.getvalue(), __expected_string1 % (
            datetime.fromtimestamp(t).strftime(datetime_format_string), default_nmpd.__class__.__name__, 'DefaultNewMatchPathDetector', 1,
            match_path_s1, pid))
        self.reset_output_stream()

        context.aminer_config.yaml_data['SuppressNewMatchPathDetector'] = True
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        self.stream_printer_event_handler = context.atomizer_factory.event_handler_list[0]
        self.stream_printer_event_handler.stream = self.output_stream
        default_nmpd = context.registered_components[1][0]
        default_nmpd.output_log_line = False
        self.assertTrue(default_nmpd.receive_atom(log_atom_fixed_dme))
        self.assertEqual(self.output_stream.getvalue(), "")
        self.reset_output_stream()

        value_combo_det = context.registered_components[2][0]
        log_atom_sequence_me = LogAtom(match_element_sequence_me.get_match_string(), ParserMatch(match_element_sequence_me), t,
                                       value_combo_det)
        self.stream_printer_event_handler = context.atomizer_factory.event_handler_list[0]
        self.stream_printer_event_handler.stream = self.output_stream
        self.assertTrue(value_combo_det.receive_atom(log_atom_sequence_me))
        self.assertEqual(self.output_stream.getvalue(), __expected_string2 % (
            datetime.fromtimestamp(t).strftime(datetime_format_string), value_combo_det.__class__.__name__,
            'ValueComboDetector', 1, string2))
        self.reset_output_stream()

        context.aminer_config.yaml_data['Analysis'][0]['suppress'] = True
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        value_combo_det = context.registered_components[1][0]
        self.stream_printer_event_handler = context.atomizer_factory.event_handler_list[0]
        self.stream_printer_event_handler.stream = self.output_stream
        self.assertTrue(value_combo_det.receive_atom(log_atom_sequence_me))
        self.assertEqual(self.output_stream.getvalue(), "")
        self.reset_output_stream()

    def test21_suppress_output_no_id_error(self):
        """Check if an error is raised if no id parameter is defined."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml('unit/data/configfiles/suppress_config.yml')
        aminer_config.yaml_data['Analysis'][0]['id'] = None
        aminer_config.yaml_data['Analysis'][0]['suppress'] = True
        context = AnalysisContext(aminer_config)
        self.assertRaises(ValueError, context.build_analysis_pipeline)

    def test22_set_output_handlers(self):
        """Check if setting the output_event_handlers is working as expected."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml('unit/data/configfiles/template_config.yml')
        context = AnalysisContext(aminer_config)
        context.build_analysis_pipeline()
        for index in context.registered_components:
            component = context.registered_components[index]
            if component[1] == 'EventTypeDetector':
                self.assertEqual(1, len(component[0].output_event_handlers))
                self.assertEqual(StreamPrinterEventHandler, type(component[0].output_event_handlers[0]))
            else:
                self.assertEqual(None, component[0].output_event_handlers)

    def test23_check_functionality_of_validate_bigger_than_or_equal(self):
        """Check the functionality of the _validate_bigger_than_or_equal procedure."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml('unit/data/configfiles/bigger_than_or_equal_valid.yml')
        self.assertRaises(ValueError, aminer_config.load_yaml, 'unit/data/configfiles/bigger_than_or_equal_error.yml')

    def test24_check_log_resource_list(self):
        """Check the functionality of the regex for LogResourceList.."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        self.assertRaises(ValueError, aminer_config.load_yaml, 'unit/data/configfiles/wrong_log_resource_list.yml')

    def test25_check_mail_regex(self):
        """Check the functionality of the regex for MailAlerting.TargetAddress and MailAlerting.FromAddress."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        self.assertRaises(ValueError, aminer_config.load_yaml, 'unit/data/configfiles/wrong_email.yml')

        with open('/usr/lib/logdata-anomaly-miner/aminer/schemas/BaseSchema.yml', 'r') as sma:
            # skipcq: PYL-W0123
            base_schema = eval(sma.read())
        self.assertEqual(base_schema['MailAlerting.TargetAddress']['regex'], base_schema['MailAlerting.FromAddress']['regex'])

        target_address_regex = re.compile(base_schema['MailAlerting.TargetAddress']['regex'])

        valid_emails = ['john@example.com', 'john@example.co', 'root@localhost']
        for email in valid_emails:
            self.assertEqual(target_address_regex.search(email).group(0), email, 'Failed regex check at %s.' % email)
        invalid_emails = ['john_at_example_dot_com', 'john@example.', '@example.com', ' @example.com']
        for email in invalid_emails:
            self.assertEqual(target_address_regex.search(email), None, 'Failed regex check at %s.' % email)

    def test26_filter_config_errors(self):
        """Check if errors in multiple sections like Analysis, Parser and EventHandlers are found and filtered properly."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        try:
            aminer_config.load_yaml('unit/data/configfiles/filter_config_errors.yml')
        except ValueError as e:
            msg = "Config-Error: {'AMinerGroup': ['unknown field'], 'Analysis': [{0: ['none or more than one rule validate', {'oneof " \
                  "definition 22': [{'learn_mode': ['unknown field'], 'reset_after_report_flag': ['unknown field'], 'type': {'allowed': [" \
                  "'ParserCount']}}]}]}], 'EventHandlers': [{1: ['none or more than one rule validate', {'oneof definition 3': [{" \
                  "'output_file_path': ['unknown field'], 'type': {'allowed': ['SyslogWriterEventHandler']}}]}]}], 'Parser': [{0: ['none " \
                  "or more than one rule validate', {'oneof definition 0': [{'args2': ['unknown field'], 'type': {'forbidden': [" \
                  "'ElementValueBranchModelElement', 'DecimalIntegerValueModelElement', 'DecimalFloatValueModelElement', " \
                  "'DateTimeModelElement', 'MultiLocaleDateTimeModelElement', 'DelimitedDataModelElement', 'JsonModelElement']}}]}]}]}"
            self.assertEqual(msg, str(e))
        self.assertRaises(ValueError, aminer_config.load_yaml, 'unit/data/configfiles/filter_config_errors.yml')

    def test27_same_id_analysis(self):
        """Check if a ValueError is raised when the same id is used for multiple analysis components."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        try:
            aminer_config.load_yaml('unit/data/configfiles/same_id_analysis.yml')
            context = AnalysisContext(aminer_config)
            context.build_analysis_pipeline()
        except ValueError as e:
            msg = "Config-Error: The id \"NewMatchPathValueComboDetector\" occurred multiple times in Analysis!"
            self.assertEqual(msg, str(e))
        context = AnalysisContext(aminer_config)
        self.assertRaises(ValueError, context.build_analysis_pipeline)

    def test28_same_id_event_handlers(self):
        """Check if a ValueError is raised when the same id is used for multiple event handler components."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        try:
            aminer_config.load_yaml('unit/data/configfiles/same_id_event_handlers.yml')
            context = AnalysisContext(aminer_config)
            context.build_analysis_pipeline()
        except ValueError as e:
            msg = "Config-Error: The id \"handler\" occurred multiple times in EventHandlers!"
            self.assertEqual(msg, str(e))
        context = AnalysisContext(aminer_config)
        self.assertRaises(ValueError, context.build_analysis_pipeline)

    def test29_same_id_parser(self):
        """Check if a ValueError is raised when the same id is used for multiple parser components."""
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        try:
            aminer_config.load_yaml('unit/data/configfiles/same_id_parser.yml')
            context = AnalysisContext(aminer_config)
            context.build_analysis_pipeline()
        except ValueError as e:
            msg = "Config-Error: The id \"apacheModel\" occurred multiple times in Parser!"
            self.assertEqual(msg, str(e))
        context = AnalysisContext(aminer_config)
        self.assertRaises(ValueError, context.build_analysis_pipeline)

    def run_empty_components_tests(self, context):
        """Run the empty components tests."""
        self.assertTrue(isinstance(context.registered_components[0][0], SubhandlerFilter))
        self.assertTrue(isinstance(context.registered_components[1][0], NewMatchPathDetector))
        self.assertTrue(isinstance(context.atomizer_factory.event_handler_list[0], StreamPrinterEventHandler))
        self.assertEqual(context.atomizer_factory.default_timestamp_paths, ['/accesslog/time'])
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
