"""This module collects static configuration item keys and configuration
loading and handling functions."""

import os
import sys

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
  try:
    import imp
    aminerConfig = imp.load_module(
        'aminerConfig', open(configFileName, 'r'), configFileName,
        ('', 'r', imp.PY_SOURCE))
  except:
    print >>sys.stderr, 'Failed to load configuration from %s' % configFileName
    exceptionInfo = sys.exc_info()
    raise exceptionInfo[0], exceptionInfo[1], exceptionInfo[2]
  return aminerConfig

def buildPersistenceFileName(aminerConfig, *args):
  """Build the full persistency file name from persistency directory
  configuration and path parts."""
  persistenceDirName = aminerConfig.configProperties.get(
      KEY_PERSISTENCE_DIR, DEFAULT_PERSISTENCE_DIR)
  return os.path.join(persistenceDirName, *args)
