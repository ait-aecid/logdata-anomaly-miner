"""This module collects static configuration item keys and configuration
loading and handling functions."""

import os
import sys
from importlib import util
import logging

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
VAR_ID = 0


def load_config(config_file_name):
  """Load the configuration file using the import module."""
  aminer_config = None
  global configFN
  configFN = config_file_name
  try:
    spec = util.spec_from_file_location('aminer_config', config_file_name)
    aminer_config = util.module_from_spec(spec)
    spec.loader.exec_module(aminer_config)

  # skipcq: FLK-E722
  except:
    print('Failed to load configuration from %s' % config_file_name, file=sys.stderr)
    exception_info = sys.exc_info()
    raise Exception(exception_info[0], exception_info[1], exception_info[2])
  return aminer_config


def build_persistence_file_name(aminer_config, *args):
  """Build the full persistency file name from persistency directory
  configuration and path parts."""
  persistence_dir_name = aminer_config.config_properties.get(
      KEY_PERSISTENCE_DIR, DEFAULT_PERSISTENCE_DIR)
  return os.path.join(persistence_dir_name, *args)


def save_config(analysis_context, new_file):
  register_component = 'registerComponent('
  global VAR_ID
  VAR_ID = 0
  msg = ""
  with open(configFN, "r") as file:
    old = file.read()
  
  for config_property in analysis_context.aminer_config.config_properties:
    find_str = "config_properties['%s'] = "%config_property
    pos = old.find(find_str)
    if pos == -1:
      msg += "WARNING: %s not found in the old config file."%find_str
      logging.basicConfig(filename=LOG_FILE,level=logging.DEBUG, 
          format='%(asctime)s %(levelname)s %(message)s', datefmt='%d.%m.%Y %H:%M:%S')
      logging.warning("WARNING: %s not found in the old config file."%find_str)
    else:
      string = old[pos + len(find_str):]
      old_len = string.find('\n')
      string = string[:old_len]
      prop = analysis_context.aminer_config.config_properties[config_property]
      if (string[0] == "'" and string[len(string)-1] == "'") or \
          (string[0] == '"' and string[len(string)-1] == '"'):
        prop = "'" + prop + "'"
      if "%s"%string != "%s"%prop:
        old = old[:pos+len(find_str)] + "%s"%prop + old[pos+len(find_str)+old_len:]
      
  for component_id in analysis_context.get_registered_component_ids():
    component = analysis_context.get_component_by_id(component_id)
    name = analysis_context.get_name_by_component(component)
    start = 0
    old_start = 0
    for i in range(0, component_id+1):
      start = start + 1
      start = old.find('.registerComponent(', start)
    if old_start > start:
      break
    old_start = start

    if old.find('componentName', start) < old.find(')', start):
      old_component_name_start = old.find('"', old.find('componentName', start))
      old_component_name_end = old.find('"', old_component_name_start+1)
      if old_component_name_start > old.find(')', start) or old_component_name_start == -1:
        old_component_name_start = old.find("'", old.find('componentName', start))
        old_component_name_end = old.find("'", old_component_name_start+1)
      old_len = old_component_name_end - old_component_name_start + 1
      old_component_name = old[old_component_name_start:]
      old_component_name = old_component_name[:old_len]
      if old_component_name != '"%s"'%name:
        old = old[:old_component_name_start] + '"%s"'%name + old[old_component_name_end+1:]
        
  with open(LOG_FILE, "r") as logFile:
    logs = logFile.readlines()
  
  i = len(logs) - 1
  while i > 0:
    if("INFO AMiner started." in logs[i]):
      logs = logs[i:]
      break
    i = i - 1

  for i in enumerate(logs):
    if "REMOTECONTROL changeAttributeOfRegisteredAnalysisComponent" in logs[i]:
      logs[i] = logs[i][:logs[i].find('#')]
      arr = logs[i].split(',',3)
      if arr[1].find("'") != -1:
        component_name = arr[1].split("'")[1]
      else:
        component_name = arr[1].split('"')[1]
      if arr[2].find("'") != -1:
        attr = arr[2].split("'")[1]
      else:
        attr = arr[2].split('"')[1]
      value = arr[3].strip().split(")")[0]

      pos = old.find('componentName="%s"'%component_name)
      if pos == -1:
        pos = old.find("componentName='%s'"%component_name)
      while old[pos] != '\n':
        pos = pos - 1
      pos = old.find(register_component, pos) + len(register_component)
      var = old[pos:old.find(',', pos)]
      pos = old.find("%s ="%var)
      if pos == -1:
        pos = old.find("%s="%var)
      pos = old.find(attr, pos)
      p1 = old.find(")", pos)
      p2 = old.find(",", pos)
      if p1 != -1 and p2 != -1:
        end = min(old.find(")", pos), old.find(",", pos))
      elif p1 == -1 and p2 == -1:
        msg += "WARNING: '%s.%s' could not be found in the current config!\n"%(component_name, attr)
        continue
      elif p1 == -1:
        end = p2
      elif p2 == -1:
        end = p1
      old = old[:old.find("=", pos)+1] + "%s"%value + old[end:]

    if "REMOTECONTROL addHandlerToAtomFilterAndRegisterAnalysisComponent" in logs[i]:
      parameters = logs[i].split(",",2)

      #find the name of the filter_config variable in the old config.
      pos = old.find(parameters[1].strip())
      new_pos = pos
      while old[new_pos] != '\n':
        new_pos = new_pos - 1
      filter_config = old[new_pos:pos]
      pos = filter_config.find(register_component) + len(register_component)
      filter_config = filter_config[pos:filter_config.find(',', pos)].strip()

      new_parameters = parameters[2].split(")")
      component_name = new_parameters[1].strip(', ')

      var = "analysisComponent%d"%VAR_ID
      VAR_ID = VAR_ID + 1
      old = old + "\n  %s = %s)"%(var, new_parameters[0].strip())
      old = old + "\n  %s.registerComponent(%s, componentName=%s)"%(filter_config, var, component_name)
      old = old + "\n  %s.addHandler(%s)\n"%(filter_config, var)

  #remove double lines
  old = old.replace('\n\n\n', '\n\n')

  try:
    with open(new_file, "w") as file:
      file.write(old)
    msg += "Successfully saved the current config to %s." % new_file
    return msg
  except FileNotFoundError:
    msg += "FAILURE: file '%s' could not be found or opened!" % new_file
    return msg
