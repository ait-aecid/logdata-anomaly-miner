import unittest
import importlib
import yaml

class YamlConfigTest(unittest.TestCase):

    """ Loads a yaml file into the variable aminer_config.yamldata """
    def test_load_generic_yaml_file(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.loadYaml('unit/data/configfiles/template_config.yml')
        self.assertIsNotNone(aminer_config.yamldata)

    def test_load_notexistent_yaml_file(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(FileNotFoundError):
          aminer_config.loadYaml('unit/data/configfiles/doesnotexist.yml')

    def test_load_invalid_yaml_file(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(yaml.YAMLError):
          aminer_config.loadYaml('unit/data/configfiles/invalid_config.yml')

    def test_load_yaml_file_with_invalid_schema(self):
        spec = importlib.util.spec_from_file_location('aminer_config', '/usr/lib/logdata-anomaly-miner/aminer/ymlconfig.py')
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        with self.assertRaises(ValueError):
          aminer_config.loadYaml('unit/data/configfiles/invalid_schema.yml')


if __name__ == "__main__":
    unittest.main()

