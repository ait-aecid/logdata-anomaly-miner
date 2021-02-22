#!/usr/bin/python3 -BbbEIsSttW all
# -*- coding: utf-8 -*-

"""
This is the main program of the "aminer" logfile miner tool.
It does not import any local default site packages to decrease the attack surface due to manipulation of unused but available packages.

CAVEAT: This process will keep running with current permissions, no matter what was specified in 'AminerUser' and 'AminerGroup'
configuration properties. This is required to allow the aminer parent parent process to reopen log files, which might need the
elevated privileges.

NOTE: This tool is developed to allow secure operation even in hostile environment, e.g. when one directory, where aminer attempts
to open logfiles is already under full control of an attacker. However it is not intended to be run as SUID-binary, this would
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
from pwd import getpwnam
from grp import getgrnam

# As site packages are not included, define from where we need to execute code before loading it.
sys.path = sys.path[1:] + ['/usr/lib/logdata-anomaly-miner', '/etc/aminer/conf-enabled']
import aminer.AminerConfig as AminerConfig  # skipcq: FLK-E402
from aminer.util.StringUtil import colflame, flame, supports_color, decode_string_as_byte_string  # skipcq: FLK-E402
from aminer.util.PersistenceUtil import clear_persistence, copytree  # skipcq: FLK-E402
from aminer.util import SecureOSFunctions  # skipcq: FLK-E402
from aminer.AnalysisChild import AnalysisChild  # skipcq: FLK-E402
from aminer.input.LogStream import FileLogDataResource, UnixSocketLogDataResource  # skipcq: FLK-E402
from metadata import __version_string__, __version__  # skipcq: FLK-E402


child_termination_triggered_flag = False


def run_analysis_child(aminer_config, program_name):
    """Run the Analysis Child."""
    # Verify existance and ownership of persistence directory.
    logging.getLogger(AminerConfig.REMOTE_CONTROL_LOG_NAME).info('aminer started.')
    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).info('aminer started.')
    persistence_dir_name = aminer_config.config_properties.get(AminerConfig.KEY_PERSISTENCE_DIR, AminerConfig.DEFAULT_PERSISTENCE_DIR)
    persistence_dir_fd = SecureOSFunctions.secure_open_base_directory(persistence_dir_name, os.O_RDONLY | os.O_DIRECTORY | os.O_PATH)
    stat_result = os.fstat(persistence_dir_fd)
    if ((not stat.S_ISDIR(stat_result.st_mode)) or ((stat_result.st_mode & stat.S_IRWXU) != 0o700) or (
            stat_result.st_uid != os.getuid()) or (stat_result.st_gid != os.getgid())):
        msg = 'FATAL: persistence directory "%s" has to be owned by analysis process (uid %d!=%d, gid %d!=%d) and have access mode 0700 ' \
              'only!' % (repr(persistence_dir_name), stat_result.st_uid, os.getuid(), stat_result.st_gid, os.getgid())
        print(msg, file=sys.stderr)
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).critical(msg)
        sys.exit(1)
    import posix1e
    # O_PATH is problematic when checking ACL. However it is possible to check the ACL using the file name.
    if posix1e.has_extended(persistence_dir_name):
        msg = 'WARNING: SECURITY: Extended POSIX ACLs are set in %s, but not supported by the aminer. Backdoor access could be possible.'\
              % persistence_dir_name.decode()
        print(msg, file=sys.stderr)
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).warning(msg)

    child = AnalysisChild(program_name, aminer_config)
    # This function call will only return on error or signal induced normal termination.
    child_return_status = child.run_analysis(3)
    if child_return_status == 0:
        sys.exit(0)
    msg = '%s: run_analysis terminated with unexpected status %d' % (program_name, child_return_status)
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
                if SecureOSFunctions.base_dir_path == AminerConfig.DEFAULT_PERSISTENCE_DIR:
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
        print('%s attribute must not contain a full directory path, but only the filename.' % AminerConfig.KEY_REMOTE_CONTROL_LOG_FILE,
              file=sys.stderr)
        sys.exit(1)
    tmp_value = aminer_config.config_properties.get(AminerConfig.KEY_STAT_LOG_FILE)
    if tmp_value is not None and b'/' in tmp_value:
        print('%s attribute must not contain a full directory path, but only the filename.' % AminerConfig.KEY_STAT_LOG_FILE,
              file=sys.stderr)
        sys.exit(1)
    tmp_value = aminer_config.config_properties.get(AminerConfig.KEY_DEBUG_LOG_FILE)
    if tmp_value is not None and b'/' in tmp_value:
        print('%s attribute must not contain a full directory path, but only the filename.' % AminerConfig.KEY_DEBUG_LOG_FILE,
              file=sys.stderr)
        sys.exit(1)

    log_dir_fd = SecureOSFunctions.secure_open_log_directory(log_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_PATH)
    rc_logger = logging.getLogger(AminerConfig.REMOTE_CONTROL_LOG_NAME)
    rc_logger.setLevel(logging.DEBUG)
    remote_control_log_file = aminer_config.config_properties.get(
        AminerConfig.KEY_REMOTE_CONTROL_LOG_FILE, os.path.join(log_dir, AminerConfig.DEFAULT_REMOTE_CONTROL_LOG_FILE))
    if not remote_control_log_file.startswith(log_dir):
        remote_control_log_file = os.path.join(log_dir, remote_control_log_file)
    try:
        rc_file_handler = logging.FileHandler(remote_control_log_file)
        os.chown(remote_control_log_file, aminer_user_id, aminer_grp_id, dir_fd=log_dir_fd, follow_symlinks=False)
    except OSError as e:
        print('Could not create or open %s: %s. Stopping..' % (remote_control_log_file, e), file=sys.stderr)
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
        stat_file_handler = logging.FileHandler(stat_log_file)
        os.chown(stat_log_file, aminer_user_id, aminer_grp_id, dir_fd=log_dir_fd, follow_symlinks=False)
    except OSError as e:
        print('Could not create or open %s: %s. Stopping..' % (stat_log_file, e), file=sys.stderr)
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
        debug_file_handler = logging.FileHandler(debug_log_file)
        os.chown(debug_log_file, aminer_user_id, aminer_grp_id, dir_fd=log_dir_fd, follow_symlinks=False)
    except OSError as e:
        print('Could not create or open %s: %s. Stopping..' % (debug_log_file, e), file=sys.stderr)
        sys.exit(1)
    debug_file_handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt=datefmt))
    debug_logger.addHandler(debug_file_handler)


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
    parser.add_argument('-s', '--stat', choices=[0, 1, 2], type=int, help='set the stat level. Possible stat-levels are 0 for no statistics'
                                                                          ', 1 for normal statistic level and 2 for verbose statistics.')
    parser.add_argument('-d', '--debug', choices=[0, 1, 2], type=int, help='set the debug level. Possible debug-levels are 0 for no '
                                                                           'debugging, 1 for normal output (INFO and above), 2 for printing'
                                                                           ' all debug information.')
    parser.add_argument('--run-analysis', action='store_true', help='enable/disable analysis')
    parser.add_argument('-C', '--clear', action='store_true', help='removes all persistence directories')
    parser.add_argument('-r', '--remove', action='append', type=str, help='removes a specific persistence directory')
    parser.add_argument('-R', '--restore', type=str, help='restore a persistence backup')
    parser.add_argument('-f', '--from-begin', action='store_true', help='removes RepositioningData before starting the aminer')

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
            print("The current aminer version %s is installed." % curr_version)
        else:
            print("A new aminer version exists (%s). Currently version %s is installed." % (curr_version, __version__))
            print("Use git pull to update the aminer version.")
        sys.exit(0)

    config_file_name = args.config
    run_in_foreground_flag = args.daemon
    run_analysis_child_flag = args.run_analysis
    clear_persistence_flag = args.clear
    remove_persistence_dirs = args.remove
    from_begin_flag = args.from_begin
    if args.restore is not None and ('.' in args.restore or '/' in args.restore):
        parser.error('The restore path %s must not contain any . or /' % args.restore)
    if args.remove is not None:
        for remove in args.remove:
            if '.' in remove or '/' in remove:
                parser.error('The remove path %s must not contain any . or /' % remove)
    restore_relative_persistence_path = args.restore
    stat_level = 1
    debug_level = 1
    stat_level_console_flag = False
    debug_level_console_flag = False
    if args.stat is not None:
        stat_level = args.stat
        stat_level_console_flag = True
    if args.debug is not None:
        debug_level = args.stat
        debug_level_console_flag = True

    # Load the main configuration file.
    if not os.path.exists(config_file_name):
        print('%s: config "%s" not (yet) available!' % (program_name, config_file_name), file=sys.stderr)
        sys.exit(1)

    # Minimal import to avoid loading too much within the privileged process.
    try:
        aminer_config = AminerConfig.load_config(config_file_name)
    except ValueError as e:
        print("Config-Error: %s" % e)
        sys.exit(1)
    persistence_dir = aminer_config.config_properties.get(AminerConfig.KEY_PERSISTENCE_DIR, AminerConfig.DEFAULT_PERSISTENCE_DIR)

    child_user_name = aminer_config.config_properties.get(AminerConfig.KEY_AMINER_USER)
    child_group_name = aminer_config.config_properties.get(AminerConfig.KEY_AMINER_GROUP)
    child_user_id = -1
    child_group_id = -1
    try:
        if child_user_name is not None:
            child_user_id = getpwnam(child_user_name).pw_uid
        if child_group_name is not None:
            child_group_id = getgrnam(child_user_name).gr_gid
    except:  # skipcq: FLK-E722
        print('Failed to resolve %s or %s' % (AminerConfig.KEY_AMINER_USER, AminerConfig.KEY_AMINER_GROUP), file=sys.stderr)
        sys.exit(1)

    initialize_loggers(aminer_config, child_user_id, child_group_id)

    if restore_relative_persistence_path is not None and (clear_persistence_flag or remove_persistence_dirs):
        msg = 'The --restore parameter removes all persistence files. Do not use this parameter with --Clear or --Remove!'
        print(msg, sys.stderr)
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
        sys.exit(1)

    if not stat_level_console_flag and AminerConfig.KEY_LOG_STAT_LEVEL in aminer_config.config_properties:
        stat_level = aminer_config.config_properties[AminerConfig.KEY_LOG_STAT_LEVEL]
    if not debug_level_console_flag and AminerConfig.KEY_LOG_DEBUG_LEVEL in aminer_config.config_properties:
        debug_level = aminer_config.config_properties[AminerConfig.KEY_LOG_DEBUG_LEVEL]

    AminerConfig.STAT_LEVEL = stat_level
    AminerConfig.DEBUG_LEVEL = debug_level

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
                msg = 'Failed to delete %s. Reason: %s' % (file_path, e)
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
                msg = 'Failed to delete %s. Reason: %s' % (file_path, e)
                print(msg, file=sys.stderr)
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)

    if restore_relative_persistence_path is not None:
        absolute_persistence_path = os.path.join(persistence_dir, 'backup', restore_relative_persistence_path)
        if not os.path.exists(absolute_persistence_path):
            msg = '%s does not exist. Continuing without restoring persistence.' % absolute_persistence_path
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
        msg = '%s: %s not defined' % (program_name, AminerConfig.KEY_LOG_SOURCES_LIST)
        print(msg, file=sys.stderr)
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
        sys.exit(1)

    # Now create the management entries for each logfile.
    log_data_resource_dict = {}
    for log_resource_name in log_sources_list:
        # From here on log_resource_name is a byte array.
        log_resource_name = decode_string_as_byte_string(log_resource_name)
        log_resource = None
        if log_resource_name.startswith(b'file://'):
            log_resource = FileLogDataResource(log_resource_name, -1)
        elif log_resource_name.startswith(b'unix://'):
            log_resource = UnixSocketLogDataResource(log_resource_name, -1)
        else:
            msg = 'Unsupported schema in %s: %s' % (AminerConfig.KEY_LOG_SOURCES_LIST, repr(log_resource_name))
            print(msg, file=sys.stderr)
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            sys.exit(1)
        if not os.path.exists(log_resource_name[7:].decode()):
            msg = "WARNING: file or socket '%s' does not exist (yet)!" % log_resource_name[7:].decode()
            print(msg, file=sys.stderr)
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).warning(msg)
        try:
            log_resource.open()
        except OSError as open_os_error:
            if open_os_error.errno == errno.EACCES:
                msg = '%s: no permission to access %s' % (program_name, repr(log_resource_name))
                print(msg, file=sys.stderr)
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                sys.exit(1)
            else:
                msg = '%s: unexpected error opening %s: %d (%s)' % (
                    program_name, repr(log_resource_name), open_os_error.errno, os.strerror(open_os_error.errno))
                print(msg, file=sys.stderr)
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                sys.exit(1)
        log_data_resource_dict[log_resource_name] = log_resource

    # Create the remote control socket, if any. Do this in privileged mode to allow binding it at arbitrary locations and support restricted
    # permissions of any type for current (privileged) uid.
    remote_control_socket_name = aminer_config.config_properties.get(AminerConfig.KEY_REMOTE_CONTROL_SOCKET_PATH, None)
    remote_control_socket = None
    if remote_control_socket_name is not None:
        if os.path.exists(remote_control_socket_name):
            try:
                os.unlink(remote_control_socket_name)
            except OSError:
                msg = 'Failed to clean up old remote control socket at %s' % remote_control_socket_name
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
            os._exit(0)  # skipcq: PYL-W0212
        os.waitpid(bind_child_pid, 0)
        remote_control_socket.listen(4)

    # Now have checked all we can get from the configuration in the privileged process. Detach from the TTY when in daemon mode.
    if not run_in_foreground_flag:
        child_pid = 0
        try:
            # Fork a child to make sure, we are not the process group leader already.
            child_pid = os.fork()
        except Exception as fork_exception:  # skipcq: PYL-W0703
            msg = 'Failed to daemonize: %s' % fork_exception
            print(msg, file=sys.stderr)
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            sys.exit(1)
        if child_pid != 0:
            # This is the parent.
            os._exit(0)  # skipcq: PYL-W0212
        # This is the child. Create a new session and become process group leader. Here we get rid of the controlling tty.
        os.setsid()
        # Fork again to become an orphaned process not being session leader, hence not able to get a controlling tty again.
        try:
            child_pid = os.fork()
        except Exception as fork_exception:  # skipcq: PYL-W0703
            msg = 'Failed to daemonize: %s' % fork_exception
            print(msg, file=sys.stderr)
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            sys.exit(1)
        if child_pid != 0:
            # This is the parent.
            os._exit(0)  # skipcq: PYL-W0212
        # Move to root directory to avoid lingering in some cwd someone else might want to unmount.
        os.chdir('/')
        # Change the umask here to clean all group/other mask bits so that accidentially created files are not accessible by other.
        os.umask(0o77)

    # Install a signal handler catching common stop signals and relaying it to all children for sure.
    # skipcq: PYL-W0603
    global child_termination_triggered_flag
    child_termination_triggered_flag = False

    def graceful_shutdown_handler(_signo, _stackFrame):
        """React on typical shutdown signals."""
        msg = '%s: caught signal, shutting down' % program_name
        print(msg, file=sys.stderr)
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).info(msg)
        # Just set the flag. It is likely, that child received same signal also so avoid multiple signaling, which could interrupt the
        # shutdown procedure again.
        # skipcq: PYL-W0603
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
            initialize_loggers(aminer_config, 'aminer', 'aminer')
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
                msg = '%s: unexpected exception closing file descriptors: %s' % (program_name, open_os_error)
                print(msg, file=sys.stderr)
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                # Flush stderr before exit without any cleanup.
                sys.stderr.flush()
                os._exit(1)  # skipcq: PYL-W0212

        # Now execute the very same program again, but user might have moved or renamed it meanwhile. This would be problematic with
        # SUID-binaries (which we do not yet support). Do NOT just fork but also exec to avoid child circumventing
        # parent's ALSR due to cloned kernel VMA.
        execArgs = ['aminerChild', '--run-analysis', '--config', analysis_config_file_name, '--stat', str(stat_level), '--debug',
                    str(debug_level)]
        os.execve(sys.argv[0], execArgs, {})  # skipcq: BAN-B606
        msg = 'Failed to execute child process'
        print(msg, file=sys.stderr)
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
        sys.stderr.flush()
        os._exit(1)  # skipcq: PYL-W0212
    child_socket.close()

    # Send all log resource information currently available to child process.
    for log_resource_name, log_resource in log_data_resource_dict.items():
        if (log_resource is not None) and (log_resource.get_file_descriptor() >= 0):
            SecureOSFunctions.send_logstream_descriptor(parent_socket, log_resource.get_file_descriptor(), log_resource_name)
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
                if child_termination_triggered_flag:
                    # This was expected, just terminate.
                    break
                msg = '%s: Analysis child process %d terminated unexpectedly with signal 0x%x' % (program_name, sig_child_pid, sig_status)
                print(msg, file=sys.stderr)
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                exit_status = 1
                break
            # So the child has been cloned, the clone has terminated. This should not happen either.
            msg = '%s: untracked child %d terminated with with signal 0x%x' % (program_name, sig_child_pid, sig_status)
            print(msg, file=sys.stderr)
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            exit_status = 1

        # Child information handled, scan for rotated logfiles or other resources, where reopening might make sense.
        for log_resouce_name, log_data_resource in log_data_resource_dict.items():
            try:
                if not log_data_resource.open(reopen_flag=True):
                    continue
            except OSError as open_os_error:
                if open_os_error.errno == errno.EACCES:
                    msg = '%s: no permission to access %s' % (program_name, log_resouce_name)
                    print(msg, file=sys.stderr)
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                else:
                    msg = '%s: unexpected error reopening %s: %d (%s)' % (
                        program_name, log_resouce_name, open_os_error.errno, os.strerror(open_os_error.errno))
                    print(msg, file=sys.stderr)
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
                exit_status = 2
                continue
            SecureOSFunctions.send_logstream_descriptor(parent_socket, log_data_resource.get_file_descriptor(), log_resouce_name)
            log_data_resource.close()
        time.sleep(1)
    parent_socket.close()
    SecureOSFunctions.close_base_directory()
    SecureOSFunctions.close_log_directory()
    sys.exit(exit_status)


main()
