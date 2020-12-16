import sys
import os
import shutil
import re
import argparse
from aminer.AMinerConfig import load_config, KEY_AMINER_USER, KEY_AMINER_GROUP, KEY_PERSISTENCE_DIR
from metadata import *


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
    """
    Return True if the running system's terminal supports color, and False otherwise.
    The function was borrowed from the django-project (https://github.com/django/django/blob/master/django/core/management/color.py)
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    return supported_platform and is_a_tty


def clear_persistence(persistence_dir_name):
    """Delete all persistence data from the persistence_dir."""
    for filename in os.listdir(persistence_dir_name):
        if filename == 'backup':
            continue
        file_path = os.path.join(persistence_dir_name, filename)
        try:
            if not os.path.isdir(file_path):
                print('The AMiner persistence directory should not contain any files.', file=sys.stderr)
                continue
            shutil.rmtree(file_path)
        except OSError as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e), file=sys.stderr)


def copytree(src, dst, symlinks=False, ignore=None):
    """Copy a directory recursively. This method has no issue with the destination directory existing (shutil.copytree has)."""
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def main():
    """Run the aminer-persistence program."""
    # Extract program name, but only when sure to contain no problematic characters.
    program_name = sys.argv[0].split('/')[-1]
    if (program_name == '.') or (program_name == '..') or (re.match('^[a-zA-Z0-9._-]+$', program_name) is None):
        print('Invalid program name, check your execution args', file=sys.stderr)
        sys.exit(1)

    help_message = 'aminer-persistence\n'
    if supports_color():
        help_message += colflame
    else:
        help_message += flame
    help_message += 'For further information read the man pages running "man AMinerRemoteControl".'
    parser = argparse.ArgumentParser(description=help_message, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v', '--version', action='version', version=__version_string__)
    parser.add_argument('-c', '--config', type=str, help='path to the config-file')
    parser.add_argument('-l', '--list', action='store_true', help='list all existing backups')
    parser.add_argument('-b', '--backup', action='store_true', help='create a backup with the current datetime')
    parser.add_argument('-r', '--restore', type=str, help='restore a persistence backup')
    parser.add_argument('-u', '--user', type=str, help='set the aminer user. Only used with --restore')
    parser.add_argument('-g', '--group', type=str, help='set the aminer group. Only used with --restore')
    parser.add_argument('-p', '--persistence-dir', type=str, help='set the persistence directory. Only used with --restore')

    args = parser.parse_args()

    absolute_persistence_path = None
    config_file_name = args.config
    rc_response_string = 'Remote execution response: '
    if args.list:
        # skipcq: BAN-B605, BAN-B607
        process = os.popen('sudo aminerremotecontrol --exec "list_backups(analysis_context)"')
        print(process.read().strip('\n').strip(rc_response_string))
    if args.backup:
        # skipcq: BAN-B605, BAN-B607
        process = os.popen('sudo aminerremotecontrol --exec "create_backup(analysis_context)"')
        print(process.read().strip('\n').strip(rc_response_string))
    if args.restore is not None:
        if not args.restore.startswith('/'):
            print('The restore path must be absolute.', file=sys.stderr)
            sys.exit(1)
        absolute_persistence_path = args.restore
    if '.' in args.user or '/' in args.user:
        print('The aminer user %s must not contain any . or /' % args.user, file=sys.stderr)
        sys.exit(1)
    aminer_user = args.user
    if '.' in args.group or '/' in args.group:
        print('The aminer group %s must not contain any . or /' % args.group, file=sys.stderr)
        sys.exit(1)
    aminer_grp = args.group
    if not args.persistence_dir.startswith('/'):
        print('The persistence_dir path must be absolute.', file=sys.stderr)
        sys.exit(1)
    persistence_dir = args.persistence_dir

    if absolute_persistence_path is not None:
        if config_file_name is not None:
            aminer_config = load_config(config_file_name)
            if args.user is None:
                aminer_user = aminer_config.config_properties[KEY_AMINER_USER]
            if args.group is None:
                aminer_grp = aminer_config.config_properties[KEY_AMINER_GROUP]
            if args.persistence_dir is None:
                persistence_dir = aminer_config.config_properties[KEY_PERSISTENCE_DIR]
        else:
            aminer_user = 'aminer'
            aminer_grp = 'aminer'
            persistence_dir = '/var/lib/aminer'

        if not os.path.exists(absolute_persistence_path):
            print('%s does not exist.' % absolute_persistence_path, file=sys.stderr)
        else:
            clear_persistence(persistence_dir)
            copytree(absolute_persistence_path, persistence_dir)
            for dirpath, _dirnames, filenames in os.walk(persistence_dir):
                shutil.chown(dirpath, aminer_user, aminer_grp)
                for filename in filenames:
                    shutil.chown(os.path.join(dirpath, filename), aminer_user, aminer_grp)
            print('Restored persistence from %s successfully.' % absolute_persistence_path)


main()
