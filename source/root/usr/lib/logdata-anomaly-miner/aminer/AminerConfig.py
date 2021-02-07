"""This module collects static configuration item keys and configuration loading and handling functions.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import importlib
# skipcq: PYL-W0611
from importlib import util
import logging

KEY_LOG_SOURCES_LIST = 'LogResourceList'
KEY_AMINER_USER = 'AminerUser'
KEY_AMINER_GROUP = 'AminerGroup'
KEY_ANALYSIS_CONFIG_FILE = 'AnalysisConfigFile'
KEY_PERSISTENCE_DIR = 'Core.PersistenceDir'
KEY_LOG_DIR = 'Core.LogDir'
DEFAULT_PERSISTENCE_DIR = '/var/lib/aminer'
DEFAULT_LOG_DIR = '/var/lib/aminer/log'
KEY_PERSISTENCE_PERIOD = 'Core.PersistencePeriod'
DEFAULT_PERSISTENCE_PERIOD = 600
KEY_REMOTE_CONTROL_SOCKET_PATH = 'RemoteControlSocket'
KEY_LOG_PREFIX = 'LogPrefix'
KEY_RESOURCES_MAX_MEMORY_USAGE = 'Resources.MaxMemoryUsage'
REMOTE_CONTROL_LOG_NAME = 'REMOTE_CONTROL'
KEY_REMOTE_CONTROL_LOG_FILE = 'Log.RemoteControlLogFile'
DEFAULT_REMOTE_CONTROL_LOG_FILE = 'aminerRemoteLog.txt'
configFN = None
STAT_LEVEL = 1
STAT_LOG_NAME = 'STAT'
KEY_STAT_LOG_FILE = 'Log.StatisticsFile'
DEFAULT_STAT_LOG_FILE = 'statistics.log'
DEBUG_LEVEL = 1
DEBUG_LOG_NAME = 'DEBUG'
KEY_DEBUG_LOG_FILE = 'Log.DebugFile'
DEFAULT_DEBUG_LOG_FILE = 'aminer.log'
KEY_LOG_STAT_PERIOD = 'Log.StatisticsPeriod'
DEFAULT_STAT_PERIOD = 3600
KEY_LOG_STAT_LEVEL = 'Log.StatisticsLevel'
KEY_LOG_DEBUG_LEVEL = 'Log.DebugLevel'
CONFIG_KEY_LOG_LINE_PREFIX = 'LogPrefix'


def load_config(config_file_name):
    """Load the configuration file using the import module."""
    aminer_config = None
    # skipcq: PYL-W0603
    global configFN
    configFN = config_file_name
    ymlext = ['.YAML', '.YML', '.yaml', '.yml']
    extension = os.path.splitext(config_file_name)[1]
    yaml_config = None

    if extension in ymlext:
        yaml_config = config_file_name
        config_file_name = os.path.dirname(os.path.abspath(__file__)) + '/' + 'YamlConfig.py'
    try:
        spec = importlib.util.spec_from_file_location('aminer_config', config_file_name)
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        if extension in ymlext:
            # skipcq: FLK-E722
            aminer_config.load_yaml(yaml_config)
    except ValueError as e:
        logging.getLogger(DEBUG_LOG_NAME).error(e)
        raise e
    except Exception:
        msg = 'Failed to load configuration from %s' % config_file_name
        print(msg, file=sys.stderr)
        logging.getLogger(DEBUG_LOG_NAME).error(msg)
        exception_info = sys.exc_info()
        logging.getLogger(DEBUG_LOG_NAME).error(exception_info)
        raise Exception(exception_info[0], exception_info[1], exception_info[2])
    return aminer_config


def build_persistence_file_name(aminer_config, *args):
    """Build the full persistence file name from persistence directory configuration and path parts."""
    persistence_dir_name = aminer_config.config_properties.get(KEY_PERSISTENCE_DIR, DEFAULT_PERSISTENCE_DIR)
    return os.path.join(persistence_dir_name, *args)


def save_config(analysis_context, new_file):
    """Save the current configuration to a file by using the aminerRemoteControl."""
    register_component = 'register_component('
    VAR_ID = 0
    msg = ""
    with open(configFN, "r") as file:
        old = file.read()

    for config_property in analysis_context.aminer_config.config_properties:
        find_str = "config_properties['%s'] = " % config_property
        pos = old.find(find_str)
        if pos == -1:
            msg += "WARNING: %snot found in the old config file.\n" % find_str
            rc_logger = logging.getLogger(REMOTE_CONTROL_LOG_NAME)
            rc_logger.warning(msg.strip('\n'))
        else:
            string = old[pos + len(find_str):]
            old_len = string.find('\n')
            string = string[:old_len]
            prop = analysis_context.aminer_config.config_properties[config_property]
            if (string[0] == "'" and string[-1] == "'") or (string[0] == '"' and string[-1] == '"'):
                prop = "'" + prop + "'"
            if "%s" % string != "%s" % prop:
                old = old[:pos + len(find_str)] + "%s" % prop + old[pos + len(find_str) + old_len:]

    for component_id in analysis_context.get_registered_component_ids():
        component = analysis_context.get_component_by_id(component_id)
        name = analysis_context.get_name_by_component(component)
        start = 0
        old_start = 0
        for i in range(0, component_id + 1):
            start = start + 1
            start = old.find('.register_component(', start)
        if old_start > start:
            break
        old_start = start

        if old.find('component_name', start) < old.find(')', start):
            old_component_name_start = old.find('"', old.find('component_name', start))
            old_component_name_end = old.find('"', old_component_name_start + 1)
            if old_component_name_start > old.find(')', start) or old_component_name_start == -1:
                old_component_name_start = old.find("'", old.find('component_name', start))
                old_component_name_end = old.find("'", old_component_name_start + 1)
            old_len = old_component_name_end - old_component_name_start + 1
            old_component_name = old[old_component_name_start:]
            old_component_name = old_component_name[:old_len]
            if old_component_name != '"%s"' % name:
                old = old[:old_component_name_start] + '"%s"' % name + old[old_component_name_end + 1:]

    log_dir = analysis_context.aminer_config.config_properties.get(KEY_LOG_DIR, DEFAULT_LOG_DIR)
    remote_control_log_file = analysis_context.aminer_config.config_properties.get(
        KEY_REMOTE_CONTROL_LOG_FILE, os.path.join(log_dir, DEFAULT_REMOTE_CONTROL_LOG_FILE))
    try:
        with open(remote_control_log_file, "r") as logFile:
            logs = logFile.readlines()
    except OSError as e:
        msg = 'Could not read %s: %s\n' % (remote_control_log_file, e)
        logging.getLogger(DEBUG_LOG_NAME).error(msg.strip('\n'))
        print(msg, file=sys.stderr)

    i = len(logs) - 1
    while i > 0:
        if "INFO aminer started." in logs[i]:
            logs = logs[i:]
            break
        i = i - 1

    for i in range(len(logs)):
        if "REMOTECONTROL change_attribute_of_registered_analysis_component" in logs[i]:
            logs[i] = logs[i][:logs[i].find('#')]
            arr = logs[i].split(',', 3)
            if arr[1].find("'") != -1:
                component_name = arr[1].split("'")[1]
            else:
                component_name = arr[1].split('"')[1]
            if arr[2].find("'") != -1:
                attr = arr[2].split("'")[1]
            else:
                attr = arr[2].split('"')[1]
            value = arr[3].strip().split(")")[0]

            pos = old.find('component_name="%s"' % component_name)
            if pos == -1:
                pos = old.find("component_name='%s'" % component_name)
            while old[pos] != '\n':
                pos = pos - 1
            pos = old.find(register_component, pos) + len(register_component)
            var = old[pos:old.find(',', pos)]
            pos = old.find("%s =" % var)
            if pos == -1:
                pos = old.find("%s=" % var)
            pos = old.find(attr, pos)
            p1 = old.find(")", pos)
            p2 = old.find(",", pos)
            if -1 not in (p1, p2):
                end = min(old.find(")", pos), old.find(",", pos))
            elif p1 == -1 and p2 == -1:
                msg += "WARNING: '%s.%s' could not be found in the current config!\n" % (component_name, attr)
                rc_logger = logging.getLogger(REMOTE_CONTROL_LOG_NAME)
                rc_logger.warning(msg.strip('\n'))
                continue
            elif p1 == -1:
                end = p2
            elif p2 == -1:
                end = p1
            old = old[:old.find("=", pos) + 1] + "%s" % value + old[end:]

        if "REMOTECONTROL add_handler_to_atom_filter_and_register_analysis_component" in logs[i]:
            parameters = logs[i].split(",", 2)

            # find the name of the filter_config variable in the old config.
            pos = old.find(parameters[1].strip())
            new_pos = pos
            while old[new_pos] != '\n':
                new_pos = new_pos - 1
            filter_config = old[new_pos:pos]
            pos = filter_config.find(register_component) + len(register_component)
            filter_config = filter_config[pos:filter_config.find(',', pos)].strip()

            new_parameters = parameters[2].split(")")
            component_name = new_parameters[1].strip(', ')

            var = "analysis_component%d" % VAR_ID
            VAR_ID = VAR_ID + 1
            old = old + "\n  %s = %s)" % (var, new_parameters[0].strip())
            old = old + "\n  %s.register_component(%s, component_name=%s)" % (filter_config, var, component_name)
            old = old + "\n  %s.add_handler(%s)\n" % (filter_config, var)

    # remove double lines
    old = old.replace('\n\n\n', '\n\n')

    try:
        with open(new_file, "w") as file:
            file.write(old)
        msg += "Successfully saved the current config to %s." % new_file
        logging.getLogger(DEBUG_LOG_NAME).info(msg)
        return msg
    except FileNotFoundError:
        msg += "FAILURE: file '%s' could not be found or opened!" % new_file
        logging.getLogger(DEBUG_LOG_NAME).error(msg)
        return msg
