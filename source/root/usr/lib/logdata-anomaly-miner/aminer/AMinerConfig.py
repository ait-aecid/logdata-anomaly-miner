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
KEY_LOG_PREFIX = 'LogPrefix'
KEY_RESOURCES_MAX_MEMORY_USAGE = 'Resources.MaxMemoryUsage'
KEY_RESOURCES_MAX_PERCENT_CPU_USAGE = 'Resources.MaxCpuPercentUsage'

def loadConfig(configFileName):
  """Load the configuration file using the import module."""
  aminerConfig = None
  try:
    spec = importlib.util.spec_from_file_location('aminerConfig', configFileName)
    aminerConfig = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(aminerConfig)

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
