"""This module collects static configuration item keys and configuration
loading and handling functions."""

import os
import sys
import importlib
from importlib import util
import logging
import random

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
LOG_FILE = '/tmp/AMinerRemoteLog.txt'
configFN = None

def loadConfig(configFileName):
  """Load the configuration file using the import module."""
  aminerConfig = None
  global configFN
  configFN = configFileName
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

def saveConfig(analysisContext, newFile):
  msg = ""
  with open(configFN, "r") as file:
    oldConfig = file.read()
  
  for configProperty in analysisContext.aminerConfig.configProperties:
    findStr = "configProperties['%s'] = "%configProperty
    old = oldConfig
    pos = old.find(findStr)
    if pos == -1:
      msg += "WARNING: %s not found in the old config file."%findStr
      logging.basicConfig(filename=LOG_FILE,level=logging.DEBUG, 
          format='%(asctime)s %(levelname)s %(message)s', datefmt='%d.%m.%Y %H:%M:%S')
      logging.warning("WARNING: %s not found in the old config file.")
    else:
      string = old[pos + len(findStr):]
      oldLen = string.find('\n')
      string = string[:oldLen]
      prop = analysisContext.aminerConfig.configProperties[configProperty]
      if (string[0] == "'" and string[len(string)-1] == "'") or \
          (string[0] == '"' and string[len(string)-1] == '"'):
        prop = "'" + prop + "'"
      if "%s"%string != "%s"%prop:
        old = old[:pos+len(findStr)] + "%s"%prop + old[pos+len(findStr)+oldLen:]
      
  for componentId in analysisContext.getRegisteredComponentIds():
    component = analysisContext.getComponentById(componentId)
    name = analysisContext.getNameByComponent(component)
    start = 0
    old = oldConfig
    for i in range(0, componentId+1):
      start = start + 1
      start = old.find('.registerComponent(', start)
      
    if old.find('componentName', start) < old.find(')', start):
      oldComponentNameStart = old.find('"', old.find('componentName', start))
      oldComponentNameEnd = old.find('"', oldComponentNameStart+1)
      if oldComponentNameStart > old.find(')', start) or oldComponentNameStart == -1:
        oldComponentNameStart = old.find("'", old.find('componentName', start))
        oldComponentNameEnd = old.find("'", oldComponentNameStart+1)
      oldLen = oldComponentNameEnd - oldComponentNameStart + 1
      oldComponentName = old[oldComponentNameStart:]
      oldComponentName = oldComponentName[:oldLen]
      if oldComponentName != '"%s"'%name:
        old = old[:oldComponentNameStart] + '"%s"'%name + old[oldComponentNameEnd+1:]
        
  with open(LOG_FILE, "r") as logFile:
    logs = logFile.readlines()
  
  i = len(logs) - 1
  while i > 0:
    if("INFO AMiner started." in logs[i]):
      logs = logs[i:]
      break
    i = i - 1

  for i in range(0, len(logs)):
    if "REMOTECONTROL changeAttributeOfRegisteredAnalysisComponent" in logs[i]:
      arr = logs[i].split(',')
      if arr[1].find("'"):
        componentName = arr[1].split("'")[1]
      else:
        componentName = arr[1].split('"')[1]
      if arr[2].find("'"):
        attr = arr[2].split("'")[1]
      else:
        attr = arr[2].split('"')[1]
      value = arr[3].strip().split(")")[0]

      old = oldConfig
      pos = old.find('componentName="%s"'%componentName)
      if pos == -1:
        pos = old.find("componentName='%s'"%componentName)
      while old[pos] != '\n':
        pos = pos - 1
      pos = old.find('registerComponent(', pos) + len('registerComponent(')
      var = old[pos:old.find(',', pos)]
      pos = old.find("%s ="%var)
      if pos == -1:
        pos = old.find("%s="%var)
      pos = old.find(attr, pos)
      end = min(old.find(")", pos), old.find(",", pos))
      old = old[:old.find("=", pos)+1] + "%s"%value + old[end:]


    if "REMOTECONTROL addHandlerToAtomFilterAndRegisterAnalysisComponent" in logs[i]:
      old = oldConfig
      parameters = logs[i].split(",",2)

      #find the name of the filter variable in the old config.
      pos1 = 0
      pos0 = -1
      filter = ''
      while pos0 == -1:
        pos1 = old.find(parameters[1].strip(' \'"'), pos1)
        pos = pos1
        filter = old[pos-70:pos]
        pos = filter.find('registerComponent(') + len('registerComponent(')
        pos0 = filter.find(',',pos)
        if pos0 == -1:
          pos1 = pos1+1
        filter = filter[pos:filter.find(',',pos)].strip()

      newParameters = parameters[2].split(")")
      componentName = newParameters[1].strip(', ')

      var = "var%d"%random.randint(0,10000)
      old = old + "\n  %s = %s)"%(var, newParameters[0].strip())
      old = old + "\n  %s.registerComponent(%s, componentName=%s)"%(filter, var, componentName)
      old = old + "\n  %s.addHandler(%s)"%(filter, var)
  
  with open(newFile, "w") as file:
    file.write(old)
  return msg
  

