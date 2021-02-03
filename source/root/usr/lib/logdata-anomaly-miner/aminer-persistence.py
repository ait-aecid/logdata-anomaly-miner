#!/usr/bin/python3 -BbbEIsSttW all
import sys
import os
import shutil
import re
import argparse
sys.path = sys.path[1:] + ['/usr/lib/logdata-anomaly-miner', '/etc/aminer/conf-enabled']
from aminer.AminerConfig import load_config, KEY_AMINER_USER, KEY_AMINER_GROUP, KEY_PERSISTENCE_DIR  # skipcq: FLK-E402
from aminer.util.StringUtil import colflame, flame, supports_color  # skipcq: FLK-E402
from aminer.util.PersistenceUtil import clear_persistence, copytree  # skipcq: FLK-E402
from metadata import __version_string__  # skipcq: FLK-E402


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
    help_message += 'For further information read the man pages running "man aminerRemoteControl".'
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
