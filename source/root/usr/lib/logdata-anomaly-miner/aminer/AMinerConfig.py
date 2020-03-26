"""This module collects static configuration item keys and configuration
loading and handling functions."""

import os
import sys
import importlib
from importlib import util

KEY_LOG_SOURCES_LIST = 'LogResourceList'
KEY_AMINER_USER = 'AMinerUser'
KEY_AMINER_GROUP = 'AMinerGroup'
KEY_ANALYSIS_CONFIG_FILE = 'AnalysisConfigFile'
KEY_PERSISTENCE_DIR = 'Core.PersistenceDir'
DEFAULT_PERSISTENCE_DIR = '/var/lib/aminer'
KEY_REMOTE_CONTROL_SOCKET_PATH = 'RemoteControlSocket'

def loadConfig(configFileName):
  """Load the configuration file using the import module."""
  aminerConfig = None
  ymlext = ['.YAML','.YML','.yaml','.yml']
  extension = os.path.splitext(configFileName)[1]
  yamlconfig = None
  if extension in ymlext:
    yamlconfig = configFileName
    configFileName = os.path.dirname(os.path.abspath(__file__)) + '/' + 'config.py'
  try:
    spec = importlib.util.spec_from_file_location('aminerConfig', configFileName)
    aminerConfig = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(aminerConfig)
    if extension in ymlext:
      aminerConfig.loadYaml(yamlconfig)
  except ValueError as e:
      raise e
  except:
    print('Failed to load configuration from %s' % configFileName, file=sys.stderr)
    exceptionInfo = sys.exc_info()
    raise Exception(exceptionInfo[0], exceptionInfo[1], exceptionInfo[2])
  return aminerConfig

def buildPersistenceFileName(aminerConfig, *args):
  """Build the full persistency file name from persistency directory
  configuration and path parts."""
  persistenceDirName = aminerConfig.configProperties.get(
      KEY_PERSISTENCE_DIR, DEFAULT_PERSISTENCE_DIR)
  return os.path.join(persistenceDirName, *args)
