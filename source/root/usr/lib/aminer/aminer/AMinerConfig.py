import os

KEY_LOG_FILE_LIST='LogFileList'
KEY_AMINER_USER='AMinerUser'
KEY_AMINER_GROUP='AMinerGroup'
KEY_ANALYSIS_CONFIG_FILE='AnalysisConfigFile'
KEY_PERSISTENCE_DIR='Core.PersistenceDir'
DEFAULT_PERSISTENCE_DIR='/var/lib/aminer'
KEY_REMOTE_CONTROL_SOCKET_PATH='RemoteControlSocket'

def loadConfig(configFileName):
  """Load the configuration file using the import module."""
  import imp
  aminerConfig=imp.load_module('aminerConfig', open(configFileName, 'r'), configFileName, ('', 'r', imp.PY_SOURCE))
  return(aminerConfig)

def buildPersistenceFileName(aminerConfig, *args):
  persistenceDirName=aminerConfig.configProperties.get(KEY_PERSISTENCE_DIR, DEFAULT_PERSISTENCE_DIR)
  return(os.path.join(persistenceDirName, *args))
