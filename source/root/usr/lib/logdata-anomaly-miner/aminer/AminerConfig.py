"""This module collects static configuration item keys and configuration
loading and handling functions.

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
import importlib.util
import logging

KEY_LOG_SOURCES_LIST = "LogResourceList"
KEY_AMINER_USER = "AminerUser"
KEY_AMINER_GROUP = "AminerGroup"
KEY_ANALYSIS_CONFIG_FILE = "AnalysisConfigFile"
KEY_PERSISTENCE_DIR = "Core.PersistenceDir"
KEY_LOG_DIR = "Core.LogDir"
DEFAULT_PERSISTENCE_DIR = "/var/lib/aminer"
DEFAULT_LOG_DIR = "/var/lib/aminer/log"
KEY_PERSISTENCE_PERIOD = "Core.PersistencePeriod"
DEFAULT_PERSISTENCE_PERIOD = 600
KEY_REMOTE_CONTROL_SOCKET_PATH = "RemoteControlSocket"
KEY_LOG_PREFIX = "LogPrefix"
KEY_RESOURCES_MAX_MEMORY_USAGE = "Resources.MaxMemoryUsage"
REMOTE_CONTROL_LOG_NAME = "REMOTE_CONTROL"
KEY_REMOTE_CONTROL_LOG_FILE = "Log.RemoteControlLogFile"
DEFAULT_REMOTE_CONTROL_LOG_FILE = "aminerRemoteLog.log"
STAT_LEVEL = 1
STAT_LOG_NAME = "STAT"
KEY_STAT_LOG_FILE = "Log.StatisticsFile"
DEFAULT_STAT_LOG_FILE = "statistics.log"
DEBUG_LEVEL = 1
DEBUG_LOG_NAME = "DEBUG"
KEY_DEBUG_LOG_FILE = "Log.DebugFile"
DEFAULT_DEBUG_LOG_FILE = "aminer.log"
KEY_LOG_STAT_PERIOD = "Log.StatisticsPeriod"
DEFAULT_STAT_PERIOD = 3600
KEY_LOG_STAT_LEVEL = "Log.StatisticsLevel"
KEY_LOG_DEBUG_LEVEL = "Log.DebugLevel"
KEY_LOG_ROTATION_MAX_BYTES = "Log.Rotation.MaxBytes"
DEFAULT_LOG_ROTATION_MAX_BYTES = 2 << 19  # 1 Megabyte
KEY_LOG_ROTATION_BACKUP_COUNT = "Log.Rotation.BackupCount"
DEFAULT_LOG_ROTATION_BACKUP_COUNT = 5
CONFIG_KEY_LOG_LINE_PREFIX = "LogPrefix"
DEFAULT_LOG_LINE_PREFIX = ""
CONFIG_KEY_ENCODING = "Log.Encoding"
ENCODING = "utf-8"
KEY_AMINER_ID = "AminerId"
KEY_LOG_LINE_IDENTIFIER = "LogLineIdentifier"


def load_config(config_file_name):
    """Load the configuration file using the import module."""
    ymlext = [".YAML", ".YML", ".yaml", ".yml"]
    extension = os.path.splitext(config_file_name)[1]
    yaml_config = None

    if extension in ymlext:
        yaml_config = config_file_name
        config_file_name = os.path.dirname(os.path.abspath(__file__)) + "/" + "YamlConfig.py"
    try:
        spec = importlib.util.spec_from_file_location("aminer_config", config_file_name)
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        if extension in ymlext:
            aminer_config.load_yaml(yaml_config)
    except ValueError as e:
        logging.getLogger(DEBUG_LOG_NAME).error(e)
        raise e
    except Exception:
        msg = f"Failed to load configuration from {config_file_name}"
        print(msg, file=sys.stderr)
        logging.getLogger(DEBUG_LOG_NAME).error(msg)
        exception_info = sys.exc_info()
        logging.getLogger(DEBUG_LOG_NAME).error(exception_info)
        raise Exception(exception_info[0], exception_info[1], exception_info[2])
    return aminer_config


def build_persistence_file_name(aminer_config, *args):
    """Build the full persistence file name from persistence directory
    configuration and path parts."""
    persistence_dir_name = aminer_config.config_properties.get(KEY_PERSISTENCE_DIR, DEFAULT_PERSISTENCE_DIR)
    return os.path.join(persistence_dir_name, *args)
