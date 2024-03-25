#!/usr/bin/python3 -BbbEIsSttW all
# -*- coding: utf-8 -*-

"""
This is the main program of the "aminer" logfile miner tool.
It does not import any local default site packages to decrease the attack surface due to manipulation of unused but available packages.

CAVEAT: This process will keep running with current permissions, no matter what was specified in 'AminerUser' and 'AminerGroup'
configuration properties. This is required to allow the aminer parent process to reopen log files, which might need the
elevated privileges.

NOTE: This tool is developed to allow secure operation even in hostile environment, e.g. when one directory, where aminer attempts
to open logfiles is already under full control of an attacker. However, it is not intended to be run as SUID-binary, this would
require code changes to protect also against standard SUID attacks.

Parameters:
* --config [file]: Location of configuration file, defaults to '/etc/aminer/config.py' when not set.
* --run-analysis: This parameters is NOT intended to be used on command line when starting aminer, it will trigger execution
  of the unprivileged aminer background child performing the real analysis.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy
of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import errno
import os
import re
import socket
import time
import sys
import logging
import shutil
import warnings
import argparse
import stat
import tempfile
import ast
from pwd import getpwnam
from grp import getgrnam
from logging.handlers import RotatingFileHandler

# As site packages are not included, define from where we need to execute code before loading it.
sys.path = sys.path[1:] + ['/usr/lib/logdata-anomaly-miner', '/etc/aminer/conf-enabled']
import aminer.AminerConfig as AminerConfig
from aminer.util.StringUtil import colflame, flame, supports_color, decode_string_as_byte_string
from aminer.util.PersistenceUtil import clear_persistence, copytree
from aminer.util import SecureOSFunctions
from aminer.AnalysisChild import AnalysisChild
from aminer.input.LogStream import FileLogDataResource, UnixSocketLogDataResource
from metadata import __version_string__, __version__


child_termination_triggered_flag = False
offline_mode = False


def run_analysis_child(aminer_config, program_name):
    """Run the Analysis Child."""
    # Verify existence and ownership of persistence directory.
    logging.getLogger(AminerConfig.REMOTE_CONTROL_LOG_NAME).info('aminer started.')
    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).info('aminer started.')
    persistence_dir_name = aminer_config.config_properties.get(AminerConfig.KEY_PERSISTENCE_DIR, AminerConfig.DEFAULT_PERSISTENCE_DIR)
    persistence_dir_fd = SecureOSFunctions.secure_open_base_directory(persistence_dir_name, os.O_RDONLY | os.O_DIRECTORY | os.O_PATH)
    stat_result = os.fstat(persistence_dir_fd)
    if ((not stat.S_ISDIR(stat_result.st_mode)) or ((stat_result.st_mode & stat.S_IRWXU) != 0o700) or (
            stat_result.st_uid != os.getuid()) or (stat_result.st_gid != os.getgid())):
        msg = f"FATAL: persistence directory \"{repr(persistence_dir_name)}\" has to be owned by analysis process (uid " \
              f"{stat_result.st_uid}!={os.getuid()}, gid {stat_result.st_gid}!={os.getgid()}) and have access mode 0700 only!"
        print(msg, file=sys.stderr)
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).critical(msg)
        sys.exit(1)
    import posix1e
    # O_PATH is problematic when checking ACL. However, it is possible to check the ACL using the file name.
    try:
        if posix1e.has_extended(persistence_dir_name):
            msg = f"WARNING: SECURITY: Extended POSIX ACLs are set in {persistence_dir_name.decode()}, but not supported by the aminer. " \
                  f"Backdoor access could be possible."
            print(msg, file=sys.stderr)
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).warning(msg)
    except OSError:  # system does not support POSIX ACLs.
        pass

    child = AnalysisChild(program_name, aminer_config)
    child.offline_mode = offline_mode
    # This function call will only return on error or signal induced normal termination.
    child_return_status = child.run_analysis(3)
    if child_return_status == 0:
        sys.exit(0)
    msg = f"{program_name}: run_analysis terminated with unexpected status {child_return_status}"
    print(msg, file=sys.stderr)
    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
    sys.exit(1)


def initialize_loggers(aminer_config, aminer_user_id, aminer_grp_id):
    """Initialize all loggers."""
    datefmt = '%d/%b/%Y:%H:%M:%S %z'

    log_dir = aminer_config.config_properties.get(AminerConfig.KEY_LOG_DIR, AminerConfig.DEFAULT_LOG_DIR)
    if log_dir == AminerConfig.DEFAULT_LOG_DIR:
        try:
            if not os.path.isdir(log_dir):
                persistence_dir_path = aminer_config.config_properties.get(
                    AminerConfig.KEY_PERSISTENCE_DIR, AminerConfig.DEFAULT_PERSISTENCE_DIR)
                persistence_dir_fd = SecureOSFunctions.secure_open_base_directory(
                    persistence_dir_path, os.O_RDONLY | os.O_DIRECTORY | os.O_PATH)
                if SecureOSFunctions.base_dir_path.decode() == AminerConfig.DEFAULT_PERSISTENCE_DIR:
                    relative_path_log_dir = os.path.split(AminerConfig.DEFAULT_LOG_DIR)[1]
                    os.mkdir(relative_path_log_dir, dir_fd=persistence_dir_fd)
                    os.chown(relative_path_log_dir, aminer_user_id, aminer_grp_id, dir_fd=persistence_dir_fd, follow_symlinks=False)
        except OSError as e:
            if e.errno != errno.EEXIST:
                msg = 'Unable to create log-directory: %s' % log_dir
            else:
                msg = e
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg.strip('\n'))
            print(msg, file=sys.stderr)

    tmp_value = aminer_config.config_properties.get(AminerConfig.KEY_REMOTE_CONTROL_LOG_FILE)
    if tmp_value is not None and b'/' in tmp_value:
        print(f"{AminerConfig.KEY_REMOTE_CONTROL_LOG_FILE} attribute must not contain a full directory path, but only the filename.",
              file=sys.stderr)
        sys.exit(1)
    tmp_value = aminer_config.config_properties.get(AminerConfig.KEY_STAT_LOG_FILE)
    if tmp_value is not None and b'/' in tmp_value:
        print(f"{AminerConfig.KEY_STAT_LOG_FILE} attribute must not contain a full directory path, but only the filename.", file=sys.stderr)
        sys.exit(1)
    tmp_value = aminer_config.config_properties.get(AminerConfig.KEY_DEBUG_LOG_FILE)
    if tmp_value is not None and b'/' in tmp_value:
        print(f"{AminerConfig.KEY_DEBUG_LOG_FILE} attribute must not contain a full directory path, but only the filename.",
              file=sys.stderr)
        sys.exit(1)

    max_bytes = aminer_config.config_properties.get(AminerConfig.KEY_LOG_ROTATION_MAX_BYTES, AminerConfig.DEFAULT_LOG_ROTATION_MAX_BYTES)
    backup_count = aminer_config.config_properties.get(
        AminerConfig.KEY_LOG_ROTATION_BACKUP_COUNT, AminerConfig.DEFAULT_LOG_ROTATION_BACKUP_COUNT)
    log_dir_fd = SecureOSFunctions.secure_open_log_directory(log_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_PATH)
    rc_logger = logging.getLogger(AminerConfig.REMOTE_CONTROL_LOG_NAME)
    rc_logger.setLevel(logging.DEBUG)
    remote_control_log_file = aminer_config.config_properties.get(
        AminerConfig.KEY_REMOTE_CONTROL_LOG_FILE, os.path.join(log_dir, AminerConfig.DEFAULT_REMOTE_CONTROL_LOG_FILE))
    if not remote_control_log_file.startswith(log_dir):
        remote_control_log_file = os.path.join(log_dir, remote_control_log_file)
    try:
        rc_file_handler = RotatingFileHandler(remote_control_log_file, maxBytes=max_bytes, backupCount=backup_count)
        os.chown(remote_control_log_file, aminer_user_id, aminer_grp_id, dir_fd=log_dir_fd, follow_symlinks=False)
    except OSError as e:
        print(f"Could not create or open {remote_control_log_file}: {e}. Stopping..", file=sys.stderr)
        sys.exit(1)
    rc_file_handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt=datefmt))
    rc_logger.addHandler(rc_file_handler)
    logging.addLevelName(15, "REMOTECONTROL")

    stat_logger = logging.getLogger(AminerConfig.STAT_LOG_NAME)
    stat_logger.setLevel(logging.INFO)
    stat_log_file = aminer_config.config_properties.get(
        AminerConfig.KEY_STAT_LOG_FILE, os.path.join(log_dir, AminerConfig.DEFAULT_STAT_LOG_FILE))
    if not stat_log_file.startswith(log_dir):
        stat_log_file = os.path.join(log_dir, stat_log_file)
    try:
        stat_file_handler = RotatingFileHandler(stat_log_file, maxBytes=max_bytes, backupCount=backup_count)
        os.chown(stat_log_file, aminer_user_id, aminer_grp_id, dir_fd=log_dir_fd, follow_symlinks=False)
    except OSError as e:
        print(f"Could not create or open {stat_log_file}: {e}. Stopping..", file=sys.stderr)
        sys.exit(1)
    stat_file_handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(message)s', datefmt=datefmt))
    stat_logger.addHandler(stat_file_handler)

    debug_logger = logging.getLogger(AminerConfig.DEBUG_LOG_NAME)
    if AminerConfig.DEBUG_LEVEL == 0:
        debug_logger.setLevel(logging.ERROR)
    elif AminerConfig.DEBUG_LEVEL == 1:
        debug_logger.setLevel(logging.INFO)
    else:
        debug_logger.setLevel(logging.DEBUG)
    debug_log_file = aminer_config.config_properties.get(
        AminerConfig.KEY_DEBUG_LOG_FILE, os.path.join(log_dir, AminerConfig.DEFAULT_DEBUG_LOG_FILE))
    if not debug_log_file.startswith(log_dir):
        debug_log_file = os.path.join(log_dir, debug_log_file)
    try:
        debug_file_handler = RotatingFileHandler(debug_log_file, maxBytes=max_bytes, backupCount=backup_count)
        os.chown(debug_log_file, aminer_user_id, aminer_grp_id, dir_fd=log_dir_fd, follow_symlinks=False)
    except OSError as e:
        print(f"Could not create or open {debug_log_file}: {e}. Stopping..", file=sys.stderr)
        sys.exit(1)
    debug_file_handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt=datefmt))
    debug_logger.addHandler(debug_file_handler)


def parse_var(s):
    """
    Parse a key, value pair, separated by "=".
    That's the reverse of ShellArgs.

    On the command line (argparse) a declaration will typically look like:
        foo=hello
    or
        foo="hello world"
    """
    items = s.split("=")
    key = items[0].strip()  # we remove blanks around keys, as is logical
    if len(items) > 1:
        # rejoin the rest:
        value = "=".join(items[1:])
    return key, value


def parse_vars(items):
    """Parse a series of key-value pairs and return a dictionary."""
    d = {}

    if items:
        for item in items:
            key, value = parse_var(item)
            d[key] = value
    return d


def main():
    """Run the aminer main program."""
    # Extract program name, but only when sure to contain no problematic characters.
    warnings.filterwarnings('ignore', category=ImportWarning)
    program_name = sys.argv[0].split('/')[-1]
    if (program_name == '.') or (program_name == '..') or (re.match('^[a-zA-Z0-9._-]+$', program_name) is None):
        print('Invalid program name, check your execution args', file=sys.stderr)
        sys.exit(1)

    # We will not read stdin from here on, so get rid of it immediately, thus aberrant child cannot manipulate caller's stdin using it.
    stdin_fd = os.open('/dev/null', os.O_RDONLY)
    os.dup2(stdin_fd, 0)
    os.close(stdin_fd)

    help_message = 'aminer - logdata-anomaly-miner\n'
    if supports_color():
        help_message += colflame
    else:
        help_message += flame
    parser = argparse.ArgumentParser(description=help_message, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v', '--version', action='version', version=__version_string__)
    parser.add_argument('-u', '--check-updates', action='store_true', help='check if updates for the aminer are available.')
    parser.add_argument('-c', '--config', default='/etc/aminer/config.yml', type=str, help='path to the config-file')
    parser.add_argument('-D', '--daemon', action='store_false', help='run as a daemon process')
    parser.add_argument('-s', '--stat', choices=["0", "1", "2"], type=str,
                        help='set the stat level. Possible stat-levels are 0 for no statistics, 1 for normal statistic level and 2 for '
                             'verbose statistics.')
    parser.add_argument('-d', '--debug', choices=["0", "1", "2"], type=str,
                        help='set the debug level. Possible debug-levels are 0 for no debugging, 1 for normal output (INFO and above), 2 '
                             'for printing all debug information.')
    parser.add_argument('--run-analysis', action='store_true', help='enable/disable analysis')
    parser.add_argument('-C', '--clear', action='store_true', help='removes all persistence directories')
    parser.add_argument('-r', '--remove', action='append', type=str, help='removes a specific persistence directory')
    parser.add_argument('-R', '--restore', type=str, help='restore a persistence backup')
    parser.add_argument('-f', '--from-begin', action='store_true', help='removes RepositioningData before starting the aminer')
    parser.add_argument('-o', '--offline-mode', action='store_true', help='stop the aminer after all logs have been processed.')
    parser.add_argument("--config-properties", metavar="KEY=VALUE", nargs='+',
                        help="Set a number of config_properties by using key-value pairs (do not put spaces before or after the = sign). "
                             "If a value contains spaces, you should define it with double quotes: 'foo=\"this is a sentence\". Note that "
                             "values are always treated as strings. If values are already defined in the config_properties, the input "
                             "types are converted to the ones already existing.")

    args = parser.parse_args()

    if args.check_updates:
        import urllib3
        url = 'https://raw.githubusercontent.com/ait-aecid/logdata-anomaly-miner/main/source/root/usr/lib/logdata-anomaly-miner/metadata.py'
        http = urllib3.PoolManager()
        r = http.request('GET', url, preload_content=True)
        metadata = r.data.decode()
        http.clear()
        lines = metadata.split('\n')
        curr_version = None
        for line in lines:
            if '__version__ = ' in line:
                curr_version = line.split('__version__ = ')[1].strip('"')
                break
        if __version__ == curr_version:
            print(f"The current aminer version {curr_version} is installed.")
        else:
            print(f"A new aminer version exists ({curr_version}). Currently version {__version__} is installed.")
            print("Use git pull to update the aminer version.")
        sys.exit(0)

    config_file_name = args.config
    run_in_foreground_flag = args.daemon
    run_analysis_child_flag = args.run_analysis
    clear_persistence_flag = args.clear
    remove_persistence_dirs = args.remove
    from_begin_flag = args.from_begin
    global offline_mode
    offline_mode = args.offline_mode
    if args.restore is not None and ('.' in args.restore or '/' in args.restore):
        parser.error(f"The restore path {args.restore} must not contain any . or /")
    if args.remove is not None:
        for remove in args.remove:
            if '.' in remove or '/' in remove:
                parser.error(f"The remove path {remove} must not contain any . or /")
    restore_relative_persistence_path = args.restore
    stat_level = 1
    debug_level = 1
    stat_level_console_flag = False
    debug_level_console_flag = False
    if args.stat is not None:
        stat_level = int(args.stat)
        stat_level_console_flag = True
    if args.debug is not None:
        debug_level = int(args.debug)
        debug_level_console_flag = True

    # Load the main configuration file.
    if not os.path.exists(config_file_name):
        print(f"{program_name}: config \"{config_file_name}\" not (yet) available!", file=sys.stderr)
        sys.exit(1)

    # using the solution here to override config_properties:
    # https://stackoverflow.com/questions/27146262/create-variable-key-value-pairs-with-argparse-python
    use_temp_config = False
    config_properties = parse_vars(args.config_properties)
    if args.config_properties and "LearnMode" in config_properties:
        ymlext = [".YAML", ".YML", ".yaml", ".yml"]
        extension = os.path.splitext(config_file_name)[1]
        if extension in ymlext:
            use_temp_config = True
            fd, temp_config = tempfile.mkstemp(suffix=".yml")
            with open(config_file_name) as f:
                for line in f:
                    if "LearnMode" in line:
                        line = "LearnMode: %s" % config_properties["LearnMode"]
                    os.write(fd, line.encode())
            config_file_name = temp_config
            os.close(fd)
        else:
            msg = "The LearnMode parameter does not exist in .py configs!"
            print(msg, sys.stderr)
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            sys.exit(1)

    # Minimal import to avoid loading too much within the privileged process.
    try:
        aminer_config = AminerConfig.load_config(config_file_name)
        if use_temp_config:
            os.remove(config_file_name)
            config_file_name = args.config
    except ValueError:
        sys.exit(1)

    for config_property in config_properties:
        if config_property == "LearnMode":
            continue
        old_value = aminer_config.config_properties.get(config_property)
        value = config_properties[config_property]
        if old_value is not None:
            try:
                if isinstance(old_value, bool):
                    if value == "True":
                        value = True
                    elif value == "False":
                        value = False
                    else:
                        msg = f"The {config_property} parameter must be of type {type(old_value)}!"
                        print(msg, sys.stderr)
                        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                        sys.exit(1)
                elif isinstance(old_value, int):
                    value = int(value)
                elif isinstance(old_value, float):
                    value = float(value)
                elif isinstance(old_value, list):
                    value = ast.literal_eval(value)
            except ValueError:
                msg = f"The {config_property} parameter must be of type {type(old_value)}!"
                print(msg, sys.stderr)
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                sys.exit(1)
        else:
            msg = f"The {config_property} parameter is not set in the config. It will be treated as a string!"
            print("WARNING: " + msg, sys.stderr)
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).warning(msg)
        aminer_config.config_properties[config_property] = value

    persistence_dir = aminer_config.config_properties.get(AminerConfig.KEY_PERSISTENCE_DIR, AminerConfig.DEFAULT_PERSISTENCE_DIR)
    child_user_name = aminer_config.config_properties.get(AminerConfig.KEY_AMINER_USER)
    child_group_name = aminer_config.config_properties.get(AminerConfig.KEY_AMINER_GROUP)
    child_user_id = -1
    child_group_id = -1
    try:
        if child_user_name is not None:
            child_user_id = getpwnam(child_user_name).pw_uid
        if child_group_name is not None:
            child_group_id = getgrnam(child_group_name).gr_gid
    except:
        print(f"Failed to resolve {AminerConfig.KEY_AMINER_USER} or {AminerConfig.KEY_AMINER_GROUP}", file=sys.stderr)
        sys.exit(1)

    if not stat_level_console_flag and AminerConfig.KEY_LOG_STAT_LEVEL in aminer_config.config_properties:
        stat_level = aminer_config.config_properties[AminerConfig.KEY_LOG_STAT_LEVEL]
    if not debug_level_console_flag and AminerConfig.KEY_LOG_DEBUG_LEVEL in aminer_config.config_properties:
        debug_level = aminer_config.config_properties[AminerConfig.KEY_LOG_DEBUG_LEVEL]
    if AminerConfig.CONFIG_KEY_ENCODING in aminer_config.config_properties:
        AminerConfig.ENCODING = aminer_config.config_properties[AminerConfig.CONFIG_KEY_ENCODING]

    AminerConfig.STAT_LEVEL = stat_level
    AminerConfig.DEBUG_LEVEL = debug_level

    initialize_loggers(aminer_config, child_user_id, child_group_id)

    if restore_relative_persistence_path is not None and (clear_persistence_flag or remove_persistence_dirs):
        msg = 'The --restore parameter removes all persistence files. Do not use this parameter with --Clear or --Remove!'
        print(msg, sys.stderr)
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
        sys.exit(1)

    if clear_persistence_flag:
        if remove_persistence_dirs:
            msg = 'The --clear and --remove arguments must not be used together!'
            print(msg, file=sys.stderr)
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            sys.exit(1)
        clear_persistence(persistence_dir)

    if remove_persistence_dirs:
        persistence_dir_name = aminer_config.config_properties.get(AminerConfig.KEY_PERSISTENCE_DIR, AminerConfig.DEFAULT_PERSISTENCE_DIR)
        for filename in os.listdir(persistence_dir_name):
            file_path = os.path.join(persistence_dir_name, filename)
            try:
                if not os.path.isdir(file_path):
                    msg = 'The aminer persistence directory should not contain any files.'
                    print(msg, file=sys.stderr)
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).warning(msg)
                    continue
                shutil.rmtree(file_path)
            except OSError as e:
                msg = f"Failed to delete {file_path}. Reason: {e}"
                print(msg, file=sys.stderr)
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)

        for filename in remove_persistence_dirs:
            file_path = os.path.join(persistence_dir, filename)
            try:
                if not os.path.exists(file_path):
                    continue
                if not os.path.isdir(file_path):
                    msg = 'The aminer persistence directory should not contain any files.'
                    print(msg, file=sys.stderr)
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).warning(msg)
                    continue
                shutil.rmtree(file_path)
            except OSError as e:
                msg = f"Failed to delete {file_path}. Reason: {e}"
                print(msg, file=sys.stderr)
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)

    if restore_relative_persistence_path is not None:
        absolute_persistence_path = os.path.join(persistence_dir, 'backup', restore_relative_persistence_path)
        if not os.path.exists(absolute_persistence_path):
            msg = f"{absolute_persistence_path} does not exist. Continuing without restoring persistence."
            print(msg, file=sys.stderr)
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).warning(msg)
        else:
            clear_persistence(persistence_dir)
            copytree(absolute_persistence_path, persistence_dir)
            persistence_dir_fd = SecureOSFunctions.secure_open_base_directory(persistence_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_PATH)
            for dirpath, _dirnames, filenames in os.walk(persistence_dir):
                os.chown(dirpath, child_user_id, child_group_id, dir_fd=persistence_dir_fd, follow_symlinks=False)
                for filename in filenames:
                    os.chown(os.path.join(dirpath, filename), child_user_id, child_user_id, dir_fd=persistence_dir_fd,
                             follow_symlinks=False)

    if from_begin_flag:
        repositioning_data_path = os.path.join(aminer_config.config_properties.get(
            AminerConfig.KEY_PERSISTENCE_DIR, AminerConfig.DEFAULT_PERSISTENCE_DIR), 'AnalysisChild', 'RepositioningData')
        if os.path.exists(repositioning_data_path):
            os.remove(repositioning_data_path)

    if run_analysis_child_flag:
        # Call analysis process, this function will never return.
        run_analysis_child(aminer_config, program_name)

    # Start importing of aminer specific components after reading of "config.py" to allow replacement of components via sys.path
    # from within configuration.
    log_sources_list = aminer_config.config_properties.get(AminerConfig.KEY_LOG_SOURCES_LIST)
    if (log_sources_list is None) or not log_sources_list:
        msg = f"{program_name}: {AminerConfig.KEY_LOG_SOURCES_LIST} not defined"
        print(msg, file=sys.stderr)
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
        sys.exit(1)

    # Now create the management entries for each logfile.
    log_data_resource_dict = {}
    for resource in log_sources_list:
        obj = {}
        if isinstance(resource, str):
            obj["url"] = decode_string_as_byte_string(resource)
        elif isinstance(resource, dict):
            for key, val in resource.items():
                if key not in ("url", "json", "xml", "parser_id"):
                    msg = f"Unknown argument in LogResourceList: {key}"
                    print(msg, file=sys.stderr)
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                    sys.exit(1)
                if key == "json" and not isinstance(val, bool):
                    msg = "Argument json must be of type boolean!"
                    print(msg, file=sys.stderr)
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                    sys.exit(1)
                if key == "xml" and not isinstance(val, bool):
                    msg = "Argument xml must be of type boolean!"
                    print(msg, file=sys.stderr)
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                    sys.exit(1)
                obj[key] = val
        else:
            msg = "LogResourceList must be of type dict or string"
            print(msg, file=sys.stderr)
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            sys.exit(1)
        if "json" in obj and "xml" in obj:
            msg = "Log resources can not be in the json and xml format at the same time."
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        if "json" not in obj:
            obj["json"] = None
        if "xml" not in obj:
            obj["xml"] = None
        if "parser_id" not in obj:
            obj["parser_id"] = None
        if isinstance(obj["url"], str):
            obj["url"] = decode_string_as_byte_string(obj["url"])
        url = obj["url"]
        if url.startswith(b'file://'):
            obj["log_resource"] = FileLogDataResource(url, -1)
        elif url.startswith(b'unix://'):
            obj["log_resource"] = UnixSocketLogDataResource(url, -1)
        else:
            msg = f"Unsupported schema in {AminerConfig.KEY_LOG_SOURCES_LIST}: {repr(obj)}"
            print(msg, file=sys.stderr)
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            sys.exit(1)
        if obj["xml"]:
            obj["log_resource"].default_buffer_size = 1 << 32
        if not os.path.exists(url[7:].decode()):
            msg = f"WARNING: file or socket '{url[7:].decode()}' does not exist (yet)!"
            print(msg, file=sys.stderr)
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).warning(msg)
        try:
            obj["log_resource"].open()
        except OSError as open_os_error:
            if open_os_error.errno == errno.EACCES:
                msg = f"{program_name}: no permission to access{repr(obj)}"
                print(msg, file=sys.stderr)
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                sys.exit(1)
            else:
                msg = f"{program_name}: unexpected error opening {repr(obj)}: {open_os_error.errno} " \
                      f"({os.strerror(open_os_error.errno)})"
                print(msg, file=sys.stderr)
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                sys.exit(1)
        log_data_resource_dict[url] = obj

    # Create the remote control socket, if any. Do this in privileged mode to allow binding it at arbitrary locations and support restricted
    # permissions of any type for current (privileged) uid.
    remote_control_socket_name = aminer_config.config_properties.get(AminerConfig.KEY_REMOTE_CONTROL_SOCKET_PATH, None)
    remote_control_socket = None
    if remote_control_socket_name is not None:
        if os.path.exists(remote_control_socket_name):
            try:
                os.unlink(remote_control_socket_name)
            except OSError:
                msg = f"Failed to clean up old remote control socket at {remote_control_socket_name}"
                print(msg, file=sys.stderr)
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                sys.exit(1)
        # Create the local socket: there is no easy way to create it with correct permissions, hence a fork is needed, setting umask,
        # bind the socket. It is also recommended to create the socket in a directory having the correct permissions already.
        remote_control_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        remote_control_socket.setblocking(False)
        bind_child_pid = os.fork()
        if bind_child_pid == 0:
            os.umask(0o177)
            remote_control_socket.bind(remote_control_socket_name)
            # Do not perform any cleanup, flushing of streams. Use _exit(0) to avoid interference with fork.
            os._exit(0)
        os.waitpid(bind_child_pid, 0)
        remote_control_socket.listen(4)

    # Now have checked all we can get from the configuration in the privileged process. Detach from the TTY when in daemon mode.
    if not run_in_foreground_flag:
        child_pid = 0
        try:
            # Fork a child to make sure, we are not the process group leader already.
            child_pid = os.fork()
        except Exception as fork_exception:
            msg = 'Failed to daemonize: %s' % fork_exception
            print(msg, file=sys.stderr)
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            sys.exit(1)
        if child_pid != 0:
            # This is the parent.
            os._exit(0)
        # This is the child. Create a new session and become process group leader. Here we get rid of the controlling tty.
        os.setsid()
        # Fork again to become an orphaned process not being session leader, hence not able to get a controlling tty again.
        try:
            child_pid = os.fork()
        except Exception as fork_exception:
            msg = f"Failed to daemonize: {fork_exception}"
            print(msg, file=sys.stderr)
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            sys.exit(1)
        if child_pid != 0:
            # This is the parent.
            os._exit(0)
        # Move to root directory to avoid lingering in some cwd someone else might want to unmount.
        os.chdir('/')
        # Change the umask here to clean all group/other mask bits so that accidentially created files are not accessible by others.
        os.umask(0o77)

    # Install a signal handler catching common stop signals and relaying it to all children for sure.
    global child_termination_triggered_flag
    child_termination_triggered_flag = False

    def graceful_shutdown_handler(_signo, _stackFrame):
        """React on typical shutdown signals."""
        msg = '%s: caught signal, shutting down' % program_name
        print(msg, file=sys.stderr)
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).info(msg)
        # Just set the flag. It is likely, that child received same signal also so avoid multiple signaling, which could interrupt the
        # shutdown procedure again.
        global child_termination_triggered_flag
        child_termination_triggered_flag = True

    import signal
    signal.signal(signal.SIGHUP, graceful_shutdown_handler)
    signal.signal(signal.SIGINT, graceful_shutdown_handler)
    signal.signal(signal.SIGTERM, graceful_shutdown_handler)

    # Now create the socket to connect the analysis child.
    (parent_socket, child_socket) = socket.socketpair(socket.AF_UNIX, socket.SOCK_DGRAM, 0)
    # Have it nonblocking from here on.
    parent_socket.setblocking(False)
    child_socket.setblocking(False)

    # Use normal fork, we should have been detached from TTY already. Flush stderr to avoid duplication of output if both child and
    # parent want to write something.
    sys.stderr.flush()
    child_pid = os.fork()
    if child_pid == 0:
        # Relocate the child socket fd to 3 if needed
        if child_socket.fileno() != 3:
            os.dup2(child_socket.fileno(), 3)
            child_socket.close()

        # Clear the supplementary groups before dropping privileges. This makes only sense when changing the uid or gid.
        if os.getuid() == 0:
            if ((child_user_id != -1) and (child_user_id != os.getuid())) or ((child_group_id != -1) and (child_group_id != os.getgid())):
                os.setgroups([])

            # Drop privileges before executing child. setuid/gid will raise an exception when call has failed.
            if child_group_id != -1:
                os.setgid(child_group_id)
            if child_user_id != -1:
                os.setuid(child_user_id)
        else:
            msg = 'INFO: No privilege separation when started as unprivileged user'
            print(msg, file=sys.stderr)
            tmp_username = aminer_config.config_properties.get(AminerConfig.KEY_AMINER_USER)
            tmp_group = aminer_config.config_properties.get(AminerConfig.KEY_AMINER_GROUP)
            aminer_user_id = -1
            aminer_group_id = -1
            try:
                if tmp_username is not None:
                    aminer_user_id = getpwnam(tmp_username).pw_uid
                if tmp_group is not None:
                    aminer_group_id = getgrnam(tmp_group).gr_gid
            except:
                print(f"Failed to resolve {AminerConfig.KEY_AMINER_USER} or {AminerConfig.KEY_AMINER_GROUP}", file=sys.stderr)
                sys.exit(1)

            initialize_loggers(aminer_config, aminer_user_id, aminer_group_id)
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).info(msg)

        # Now resolve the specific analysis configuration file (if any).
        analysis_config_file_name = aminer_config.config_properties.get(AminerConfig.KEY_ANALYSIS_CONFIG_FILE, None)
        if analysis_config_file_name is None:
            analysis_config_file_name = config_file_name
        elif not os.path.isabs(analysis_config_file_name):
            analysis_config_file_name = os.path.join(os.path.dirname(config_file_name), analysis_config_file_name)

        # This is the child. Close all parent file descriptors, we do not need. Perhaps this could be done more elegantly.
        for close_fd in range(4, 1 << 16):
            try:
                os.close(close_fd)
            except OSError as open_os_error:
                if open_os_error.errno == errno.EBADF:
                    continue
                msg = f"{program_name}: unexpected exception closing file descriptors:{open_os_error}"
                print(msg, file=sys.stderr)
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                # Flush stderr before exit without any cleanup.
                sys.stderr.flush()
                os._exit(1)

        # Now execute the very same program again, but user might have moved or renamed it meanwhile. This would be problematic with
        # SUID-binaries (which we do not yet support). Do NOT just fork but also exec to avoid child circumventing
        # parent's ALSR due to cloned kernel VMA.
        exec_args = ['aminerChild', '--run-analysis', '--config', analysis_config_file_name, '--stat', str(stat_level), '--debug',
                     str(debug_level)]
        if offline_mode:
            exec_args.append("--offline-mode")
        if args.config_properties:
            exec_args.append("--config-properties")
            for config_property in args.config_properties:
                exec_args.append(config_property)
        os.execv(sys.argv[0], exec_args)
        msg = 'Failed to execute child process'
        print(msg, file=sys.stderr)
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
        sys.stderr.flush()
        os._exit(1)
    child_socket.close()

    # Send all log resource information currently available to child process.
    for url, obj in log_data_resource_dict.items():
        log_resource = obj["log_resource"]
        if (log_resource is not None) and (log_resource.get_file_descriptor() >= 0):
            SecureOSFunctions.send_logstream_descriptor(parent_socket, log_resource.get_file_descriptor(), url)
            log_resource.close()

    # Send the remote control server socket, if any and close it afterwards. It is not needed any more on parent side.
    if remote_control_socket is not None:
        SecureOSFunctions.send_annotated_file_descriptor(parent_socket, remote_control_socket.fileno(), 'remotecontrol', '')
        remote_control_socket.close()

    exit_status = 0
    child_termination_triggered_count = 0
    while True:
        if child_termination_triggered_flag:
            if child_termination_triggered_count == 0:
                time.sleep(1)
            elif child_termination_triggered_count < 5:
                os.kill(child_pid, signal.SIGTERM)
            else:
                os.kill(0, signal.SIGKILL)
            child_termination_triggered_count += 1
        (sig_child_pid, sig_status) = os.waitpid(-1, os.WNOHANG)
        if sig_child_pid != 0:
            if sig_child_pid == child_pid:
                if child_termination_triggered_flag or offline_mode:
                    # This was expected, just terminate.
                    break
                msg = f"{program_name}: Analysis child process {sig_child_pid} terminated unexpectedly with signal 0x{sig_status}"
                print(msg, file=sys.stderr)
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                exit_status = 1
                break
            # So the child has been cloned, the clone has terminated. This should not happen either.
            msg = f"{program_name}: untracked child {sig_child_pid} terminated with with signal 0x{sig_status}"
            print(msg, file=sys.stderr)
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            exit_status = 1

        # Child information handled, scan for rotated logfiles or other resources, where reopening might make sense.
        for log_resouce_name, obj in log_data_resource_dict.items():
            log_resource = obj["log_resource"]
            try:
                if not log_resource.open(reopen_flag=True):
                    continue
            except OSError as open_os_error:
                if open_os_error.errno == errno.EACCES:
                    msg = f"{program_name}: no permission to access {log_resouce_name}"
                    print(msg, file=sys.stderr)
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                else:
                    msg = f"{program_name}: unexpected error reopening {log_resouce_name}: {open_os_error.errno} " \
                          f"({os.strerror(open_os_error.errno)})"
                    print(msg, file=sys.stderr)
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                exit_status = 2
                continue
            SecureOSFunctions.send_logstream_descriptor(parent_socket, log_resource.get_file_descriptor(), log_resouce_name)
            log_resource.close()
        time.sleep(1)
    parent_socket.close()
    SecureOSFunctions.close_base_directory()
    SecureOSFunctions.close_log_directory()
    sys.exit(exit_status)


main()
