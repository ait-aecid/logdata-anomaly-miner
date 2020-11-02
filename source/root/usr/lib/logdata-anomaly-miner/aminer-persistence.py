import sys
import os
import shutil
import re


__website__ = "https://aecid.ait.ac.at"


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


def print_help(program_name, version=False):
    """Print the aminer-persistence help."""
    global colflame  # skipcq: PYL-W0603
    global flame  # skipcq: PYL-W0603
    if supports_color():
        print(colflame)
    else:
        print(flame)
    print("   (Austrian Institute of Technology)")
    print("       (%s)" % __website__)
    if version:
        return
    print("\nusage: %s [options]" % program_name)
    print("options:")
    print("  -l, --List                      \tlist all existing backups")
    print("  -b, --Backup                    \tcreate a backup with the current datetime")
    print("  -r, --Restore <persistence-path>\tenable/disable analysis")
    print("  -u, --User <aminer-user>        \tset the aminer user. Only used with --Restore")
    print("  -g, --Group <aminer-group>      \tset the aminer group. Only used with --Restore")
    print("  -h, --Help                      \tprint this print_help screen")


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

    absolute_persistence_path = None
    aminer_user = 'aminer'
    aminer_grp = 'aminer'
    persistence_dir = '/var/lib/aminer'
    rc_response_string = 'Remote execution response: '
    arg_pos = 1
    while arg_pos < len(sys.argv):
        arg_name = sys.argv[arg_pos]
        arg_pos += 1

        if arg_name in ('--List', '--list', '-l'):
            # skipcq: BAN-B605, BAN-B607
            process = os.popen('sudo aminerRemoteControl --Exec "list_backups(analysis_context)"')
            print(process.read().strip('\n').strip(rc_response_string))
            break
        if arg_name in ('--Backup', '--backup', '-b'):
            # skipcq: BAN-B605, BAN-B607
            process = os.popen('sudo aminerRemoteControl --Exec "create_backup(analysis_context)"')
            print(process.read().strip('\n').strip(rc_response_string))
            break
        if arg_name in ('--Restore', '--restore', '-r'):
            if not sys.argv[arg_pos].startswith('/'):
                print('The backup path must be absolute.', file=sys.stderr)
                sys.exit(1)
            absolute_persistence_path = sys.argv[arg_pos]
            arg_pos += 1
            continue
        if arg_name in ('--User', '--user', '-u'):
            if '.' in sys.argv[arg_pos] or '/' in sys.argv[arg_pos]:
                print('The aminer user %s must not contain any . or /' % sys.argv[arg_pos], file=sys.stderr)
                sys.exit(1)
            aminer_user = sys.argv[arg_pos]
            arg_pos += 1
            continue
        if arg_name in ('--Group', '--group', '-g'):
            if '.' in sys.argv[arg_pos] or '/' in sys.argv[arg_pos]:
                print('The aminer group %s must not contain any . or /' % sys.argv[arg_pos], file=sys.stderr)
                sys.exit(1)
            aminer_grp = sys.argv[arg_pos]
            arg_pos += 1
            continue
        if arg_name in ('--print_help', '--Help', '--help', '-h'):
            print_help(program_name)
            sys.exit(1)

        print('Unknown parameter "%s"' % arg_name, file=sys.stderr)
        sys.exit(1)

    if absolute_persistence_path is not None:
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
