#!/usr/bin/python3 -BbbEIsSttW all
# -*- coding: utf-8 -*-

"""This is the main program of the "aminer" logfile miner tool. It does not import any local default site packages to decrease the attack
surface due to manipulation of unused but available packages.

CAVEAT: This process will keep running with current permissions, no matter what was specified in 'AMinerUser' and 'AMinerGroup'
configuration properties. This is required to allow the AMiner parent parent process to reopen log files, which might need the
elevated privileges.

NOTE: This tool is developed to allow secure operation even in hostile environment, e.g. when one directory, where AMiner attempts
to open logfiles is already under full control of an attacker. However it is not intended to be run as SUID-binary, this would
require code changes to protect also against standard SUID attacks.

Parameters:
* --Config [file]: Location of configuration file, defaults to '/etc/aminer/config.py' when not set.
* --RunAnalysis: This parameters is NOT intended to be used on command line when starting aminer, it will trigger execution
  of the unprivileged aminer background child performing the real analysis.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy
of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>."""

import errno
import os
import re
import socket
import time

__authors__ = ["Markus Wurzenberger", "Max Landauer", "Wolfgang Hotwagner", "Ernst Leierzopf", "Roman Fiedler", "Georg Hoeld",
               "Florian Skopik"]
__contact__ = "aecid@ait.ac.at"
__copyright__ = "Copyright 2020, AIT Austrian Institute of Technology GmbH"
__date__ = "2020/06/19"
__deprecated__ = False
__email__ = "aecid@ait.ac.at"
__website__ = "https://aecid.ait.ac.at"
__license__ = "GPLv3"
__maintainer__ = "Markus Wurzenberger"
__status__ = "Production"
__version__ = "2.0.1"

import sys

# As site packages are not included, define from where we need to execute code before loading it.
sys.path = sys.path[1:] + ['/usr/lib/logdata-anomaly-miner', '/etc/aminer/conf-enabled']

colflame = ("\033[31m"
            "            *     (        )       (     \n"
            "   (      (  `    )\\ )  ( /(       )\\ )  \n"
            "   )\\     )\\))(  (()/(  )\\()) (   (()/(  \n"
            "\033[33m"
            "((((_)(  ((_)()\\  /(_))((_)\\  )\\   /(_)) \n"
            " )\\ _ )\\ (_()((_)(_))   _((_)((_) (_))   \n"
            " (_)\033[39m_\\\033[33m(_)\033[39m|  \\/  ||_ _| | \\| || __|| _ \\  \n"
            "  / _ \\  | |\\/| | | |  | .` || _| |   /  \n"
            " /_/ \\_\\ |_|  |_||___| |_|\\_||___||_|_\\  "
            "\033[39m")

flame = ("            *     (        )       (     \n"
         "   (      (  `    )\\ )  ( /(       )\\ )  \n"
         "   )\\     )\\))(  (()/(  )\\()) (   (()/(  \n"
         "((((_)(  ((_)()\\  /(_))((_)\\  )\\   /(_)) \n"
         " )\\ _ )\\ (_()((_)(_))   _((_)((_) (_))   \n"
         " (_)_\\(_)|  \\/  ||_ _| | \\| || __|| _ \\  \n"
         "  / _ \\  | |\\/| | | |  | .` || _| |   /  \n"
         " /_/ \\_\\ |_|  |_||___| |_|\\_||___||_|_\\  ")


def supports_color():
    """Returns True if the running system's terminal supports color, and False otherwise.
    The function was borrowed from the django-project (https://github.com/django/django/blob/master/django/core/management/color.py)"""
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    return supported_platform and is_a_tty


def print_help(program_name, version=False):
    """AMiner print_help function"""
    global colflame  # skipcq: PYL-W0603
    global flame  # skipcq: PYL-W0603
    if supports_color():
        print(colflame)
    else:
        print(flame)
    print("   (Austrian Institute of Technology)")
    print("       (%s)" % __website__)
    print("            Version: %s" % __version__)
    if version:
        return
    print("\nusage: %s [options]" % program_name)
    print("options:")
    print("  --Config <config-file>\tpath to the config-file")
    print("  --Foreground          \tdo not fork")
    print("  --RunAnalysis         \tenable/disable analysis")
    print("  --Help                \tprint this print_help screen")
    print("  --Version             \tprint version-string")


def run_analysis_child(aminer_config, program_name):
    """Runs the Analysis Child"""
    from aminer import AMinerConfig
    # Verify existance and ownership of persistence directory.
    persistence_dir_name = aminer_config.config_properties.get(AMinerConfig.KEY_PERSISTENCE_DIR, AMinerConfig.DEFAULT_PERSISTENCE_DIR)
    from aminer.util import SecureOSFunctions
    print('WARNING: SECURITY: Open should use O_PATH, but not yet available in python', file=sys.stderr)
    if isinstance(persistence_dir_name, str):
        persistence_dir_name = persistence_dir_name.encode()
    persistence_dir_fd = SecureOSFunctions.secure_open_file(persistence_dir_name, os.O_RDONLY | os.O_DIRECTORY)
    stat_result = os.fstat(persistence_dir_fd)
    import stat
    if ((not stat.S_ISDIR(stat_result.st_mode)) or ((stat_result.st_mode & stat.S_IRWXU) != 0o700) or (
            stat_result.st_uid != os.getuid()) or (stat_result.st_gid != os.getgid())):
        print('FATAL: persistence directory "%s" has to be owned by analysis process (uid %d!=%d, gid %d!=%d) '
              'and have access mode 0700 only!' % (
                  repr(persistence_dir_name), stat_result.st_uid, os.getuid(), stat_result.st_gid, os.getgid()), file=sys.stderr)
        sys.exit(1)
    print('WARNING: SECURITY: No checking for backdoor access via POSIX ACLs, use "getfacl" from "acl" package '
          'to check manually.', file=sys.stderr)
    os.close(persistence_dir_fd)

    from aminer.AnalysisChild import AnalysisChild
    child = AnalysisChild(program_name, aminer_config)
    # This function call will only return on error or signal induced normal termination.
    child_return_status = child.run_analysis(3)
    if child_return_status == 0:
        sys.exit(0)
    print('%s: run_analysis terminated with unexpected status %d' % (program_name, child_return_status), file=sys.stderr)
    sys.exit(1)


def main():
    """AMiner main function"""
    # Extract program name, but only when sure to contain no problematic characters.
    program_name = sys.argv[0].split('/')[-1]
    if (program_name == '.') or (program_name == '..') or (re.match('^[a-zA-Z0-9._-]+$', program_name) is None):
        print('Invalid program name, check your execution args', file=sys.stderr)
        sys.exit(1)

    # We will not read stdin from here on, so get rid of it immediately, thus aberrant child cannot manipulate caller's stdin using it.
    stdin_fd = os.open('/dev/null', os.O_RDONLY)
    os.dup2(stdin_fd, 0)
    os.close(stdin_fd)

    config_file_name = '/etc/aminer/config.py'
    run_in_foreground_flag = False
    run_analysis_child_flag = False
    clear_persistence_flag = False
    remove_persistence_dirs = []
    from_begin_flag = False

    arg_pos = 1
    while arg_pos < len(sys.argv):
        arg_name = sys.argv[arg_pos]
        arg_pos += 1

        if arg_name == '--Config':
            config_file_name = sys.argv[arg_pos]
            arg_pos += 1
            continue
        if arg_name == '--Foreground':
            run_in_foreground_flag = True
            continue
        if arg_name == '--RunAnalysis':
            run_analysis_child_flag = True
            continue
        if arg_name == '--Clear':
            clear_persistence_flag = True
            continue
        if arg_name == '--Remove':
            if '.' in sys.argv[arg_pos] or '/' in sys.argv[arg_pos]:
                print('The remove path %s must not contain any . or /' % sys.argv[arg_pos], file=sys.stderr)
                sys.exit(1)
            remove_persistence_dirs.append(sys.argv[arg_pos])
            arg_pos += 1
            continue
        if arg_name == '--FromBegin':
            from_begin_flag = True
            continue
        if arg_name in ('--print_help', '--Help', '-h'):
            print_help(program_name)
            sys.exit(1)
        if arg_name in ('--version', '--Version'):
            print_help(program_name, True)
            sys.exit(1)

        print('Unknown parameter "%s"' % arg_name, file=sys.stderr)
        sys.exit(1)

    # Load the main configuration file.
    if not os.path.exists(config_file_name):
        print('%s: config "%s" not (yet) available!' % (program_name, config_file_name), file=sys.stderr)
        sys.exit(1)

    # Minimal import to avoid loading too much within the privileged process.
    from aminer import AMinerConfig
    try:
        aminer_config = AMinerConfig.load_config(config_file_name)
    except ValueError as e:
        print("Config-Error: %s" % e)
        sys.exit(1)

    if clear_persistence_flag:
        if remove_persistence_dirs:
            print('The --Clear and --Remove arguments must not be used together!', file=sys.stderr)
            sys.exit(1)
        import shutil
        persistence_dir_name = aminer_config.config_properties.get(AMinerConfig.KEY_PERSISTENCE_DIR, AMinerConfig.DEFAULT_PERSISTENCE_DIR)
        for filename in os.listdir(persistence_dir_name):
            file_path = os.path.join(persistence_dir_name, filename)
            try:
                if not os.path.isdir(file_path):
                    print('The AMiner persistence directory should not contain any files.', file=sys.stderr)
                    continue
                shutil.rmtree(file_path)
            except OSError as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e), file=sys.stderr)

    if remove_persistence_dirs:
        import shutil
        persistence_dir_name = aminer_config.config_properties.get(AMinerConfig.KEY_PERSISTENCE_DIR, AMinerConfig.DEFAULT_PERSISTENCE_DIR)
        for filename in remove_persistence_dirs:
            file_path = os.path.join(persistence_dir_name, filename)
            try:
                if not os.path.exists(file_path):
                    continue
                if not os.path.isdir(file_path):
                    print('The AMiner persistence directory should not contain any files.', file=sys.stderr)
                    continue
                shutil.rmtree(file_path)
            except OSError as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e), file=sys.stderr)

    if from_begin_flag:
        repositioning_data_path = os.path.join(aminer_config.config_properties.get(
            AMinerConfig.KEY_PERSISTENCE_DIR, AMinerConfig.DEFAULT_PERSISTENCE_DIR), 'AnalysisChild', 'RepositioningData')
        if os.path.exists(repositioning_data_path):
            os.remove(repositioning_data_path)

    if run_analysis_child_flag:
        # Call analysis process, this function will never return.
        run_analysis_child(aminer_config, program_name)

    # Start importing of aminer specific components after reading of "config.py" to allow replacement of components via sys.path
    # from within configuration.
    from aminer.util import SecureOSFunctions
    from aminer.util import decode_string_as_byte_string
    log_sources_list = aminer_config.config_properties.get(AMinerConfig.KEY_LOG_SOURCES_LIST)
    if (log_sources_list is None) or not log_sources_list:
        print('%s: %s not defined' % (program_name, AMinerConfig.KEY_LOG_SOURCES_LIST), file=sys.stderr)
        sys.exit(1)

    # Now create the management entries for each logfile.
    log_data_resource_dict = {}
    for log_resource_name in log_sources_list:
        # From here on log_resource_name is a byte array.
        log_resource_name = decode_string_as_byte_string(log_resource_name)
        log_resource = None
        if log_resource_name.startswith(b'file://'):
            from aminer.input.LogStream import FileLogDataResource
            log_resource = FileLogDataResource(log_resource_name, -1)
        elif log_resource_name.startswith(b'unix://'):
            from aminer.input.LogStream import UnixSocketLogDataResource
            log_resource = UnixSocketLogDataResource(log_resource_name, -1)
        else:
            print('Unsupported schema in %s: %s' % (AMinerConfig.KEY_LOG_SOURCES_LIST, repr(log_resource_name)), file=sys.stderr)
            sys.exit(1)

        try:
            log_resource.open()
        except OSError as open_os_error:
            if open_os_error.errno == errno.EACCES:
                print('%s: no permission to access %s' % (program_name, repr(log_resource_name)), file=sys.stderr)
                sys.exit(1)
            else:
                print('%s: unexpected error opening %s: %d (%s)' % (
                    program_name, repr(log_resource_name), open_os_error.errno, os.strerror(open_os_error.errno)), file=sys.stderr)
                sys.exit(1)
        log_data_resource_dict[log_resource_name] = log_resource

    child_user_name = aminer_config.config_properties.get(AMinerConfig.KEY_AMINER_USER, None)
    child_group_name = aminer_config.config_properties.get(AMinerConfig.KEY_AMINER_GROUP, None)
    child_user_id = -1
    child_group_id = -1
    try:
        if child_user_name is not None:
            from pwd import getpwnam
            child_user_id = getpwnam(child_user_name).pw_uid
        if child_group_name is not None:
            from grp import getgrnam
            child_group_id = getgrnam(child_user_name).gr_gid
    except:  # skipcq: FLK-E722
        print('Failed to resolve %s or %s' % (AMinerConfig.KEY_AMINER_USER, AMinerConfig.KEY_AMINER_GROUP), file=sys.stderr)
        sys.exit(1)

    # Create the remote control socket, if any. Do this in privileged mode to allow binding it at arbitrary locations and support restricted
    # permissions of any type for current (privileged) uid.
    remote_control_socket_name = aminer_config.config_properties.get(AMinerConfig.KEY_REMOTE_CONTROL_SOCKET_PATH, None)
    remote_control_socket = None
    if remote_control_socket_name is not None:
        if os.path.exists(remote_control_socket_name):
            try:
                os.unlink(remote_control_socket_name)
            except OSError:
                print('Failed to clean up old remote control socket at %s' % remote_control_socket_name, file=sys.stderr)
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
            print('Failed to daemonize: %s' % fork_exception, file=sys.stderr)
            sys.exit(1)
        if child_pid != 0:
            # This is the parent. Exit without any python cleanup.
            os._exit(0)  # skipcq: PYL-W0212
        # This is the child. Create a new session and become process group leader. Here we get rid of the controlling tty.
        os.setsid()
        # Fork again to become an orphaned process not being session leader, hence not able to get a controlling tty again.
        try:
            child_pid = os.fork()
        except Exception as fork_exception:  # skipcq: PYL-W0703
            print('Failed to daemonize: %s' % fork_exception, file=sys.stderr)
            sys.exit(1)
        if child_pid != 0:
            # This is the parent. Exit without any python cleanup.
            os._exit(0)  # skipcq: PYL-W0212
        # Move to root directory to avoid lingering in some cwd someone else might want to unmount.
        os.chdir('/')
        # Change the umask here to clean all group/other mask bits so that accidentially created files are not accessible by other.
        os.umask(0o77)

    # Install a signal handler catching common stop signals and relaying it to all children for sure.
    global child_termination_triggered_flag
    child_termination_triggered_flag = False

    def graceful_shutdown_handler(_signo, _stackFrame):
        """This is the signal handler function to react on typical shutdown signals."""
        print('%s: caught signal, shutting down' % program_name, file=sys.stderr)
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

        # This is the child. Close all parent file descriptors, we do not need. Perhaps this could be done more elegantly.
        for close_fd in range(4, 1 << 16):
            try:
                os.close(close_fd)
            except OSError as open_os_error:
                if open_os_error.errno == errno.EBADF:
                    continue
                print('%s: unexpected exception closing file descriptors: %s' % (program_name, open_os_error), file=sys.stderr)
                # Flush stderr before exit without any cleanup.
                sys.stderr.flush()
                os._exit(1)  # skipcq: PYL-W0212

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
            print('INFO: No privilege separation when started as unprivileged user', file=sys.stderr)

        # Now resolve the specific analysis configuration file (if any).
        analysis_config_file_name = aminer_config.config_properties.get(AMinerConfig.KEY_ANALYSIS_CONFIG_FILE, None)
        if analysis_config_file_name is None:
            analysis_config_file_name = config_file_name
        elif not os.path.isabs(analysis_config_file_name):
            analysis_config_file_name = os.path.join(os.path.dirname(config_file_name), analysis_config_file_name)

        # Now execute the very same program again, but user might have moved or renamed it meanwhile. This would be problematic with
        # SUID-binaries (which we do not yet support). Do NOT just fork but also exec to avoid child circumventing
        # parent's ALSR due to cloned kernel VMA.
        execArgs = ['AMinerChild', '--RunAnalysis', '--Config', analysis_config_file_name]
        os.execve(sys.argv[0], execArgs, {})  # skipcq: BAN-B606
        print('%s: Failed to execute child process', file=sys.stderr)
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
                print('%s: Analysis child process %d terminated unexpectedly with signal 0x%x' % (
                    program_name, sig_child_pid, sig_status), file=sys.stderr)
                exit_status = 1
                break
            # So the child has been cloned, the clone has terminated. This should not happen either.
            print('%s: untracked child %d terminated with with signal 0x%x' % (program_name, sig_child_pid, sig_status), file=sys.stderr)
            exit_status = 1

        # Child information handled, scan for rotated logfiles or other resources, where reopening might make sense.
        for log_resouce_name, log_data_resource in log_data_resource_dict.items():
            try:
                if not log_data_resource.open(reopen_flag=True):
                    continue
            except OSError as open_os_error:
                if open_os_error.errno == errno.EACCES:
                    print('%s: no permission to access %s' % (program_name, log_resouce_name), file=sys.stderr)
                else:
                    print('%s: unexpected error reopening %s: %d (%s)' % (
                        program_name, log_resouce_name, open_os_error.errno, os.strerror(open_os_error.errno)), file=sys.stderr)
                exit_status = 2
                continue

            SecureOSFunctions.send_logstream_descriptor(parent_socket, log_data_resource.get_file_descriptor(), log_resouce_name)
            log_data_resource.close()

        time.sleep(1)
    sys.exit(exit_status)


main()
