#!/usr/bin/python3 -BbbEIsSttW all
# -*- coding: utf-8 -*-

"""
This tool allows to connect to a remote control socket, send requests and retrieve the responses.
To allow remote use of this tool, e.g. via SSH forwarding, the remote control address can be set on the command line, no configuration is
read.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import json
import os
import socket
import traceback
import sys
import argparse

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
__version__ = "2.1.0"
__version_string__ = """   (Austrian Institute of Technology)\n       (%s)\n            Version: %s""" % (__website__, __version__)

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


# Get rid of the default sys path immediately. Otherwise Python also attempts to load the following imports from e.g. directory
# where this binary resides.
sys.path = sys.path[1:] + ['/usr/lib/logdata-anomaly-miner', '/etc/aminer/conf-enabled']
# skipcq: FLK-E402
from aminer.AnalysisChild import AnalysisChildRemoteControlHandler

help_message = 'aminerremotecontrol\n'
if supports_color():
    help_message += colflame
else:
    help_message += flame
help_message += 'For further information read the man pages running "man AMinerRemoteControl".'
parser = argparse.ArgumentParser(description=help_message, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-v', '--version', action='version', version=__version_string__)
parser.add_argument('-c', '--control-socket', default='/var/run/aminer-remote.socket', type=str,
                    help='when given, use nonstandard control socket')
parser.add_argument('-d', '--data', help='provide this json serialized data within execution environment as "remote_control_data" (see man '
                                         'page).')
parser.add_argument('-e', '--exec', action='append', type=str, help='add command to the execution list, can be used more than once.')
parser.add_argument('-f', '--exec-file', type=str, help='add commands from file to the execution list in same way as if content would have '
                                                        'been used with "--Exec"')
parser.add_argument('-s', '--string-response', action='store_true',
                    help='if set, print the response just as string instead of passing it to repr')

args = parser.parse_args()

remote_control_socket_name = args.control_socket
if args.data is not None:
    args.data = json.loads(args.data)
remote_control_data = args.data
command_list = args.exec
if command_list is None:
    command_list = []
if args.exec_file is not None:
    if not os.path.exists(args.exec_file):
        print('File %s does not exist' % args.exec_file)
        sys.exit(1)
    with open(args.exec_file, 'rb') as exec_file:
        command_list += exec_file.readlines()
string_response_flag = args.string_response

if not command_list:
    print('No commands given, use --Exec [cmd]')
    sys.exit(1)

remote_control_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
try:
    remote_control_socket.connect(remote_control_socket_name)
except socket.error as connectException:
    print('Failed to connect to socket %s, AMiner might not be running or remote control is disabled in '
          'configuration: %s' % (remote_control_socket_name, str(connectException)))
    sys.exit(1)
remote_control_socket.setblocking(True)

control_handler = AnalysisChildRemoteControlHandler(remote_control_socket)

for remote_control_code, remote_control_data in command_list:
    control_handler.put_execute_request(remote_control_code, remote_control_data)
    # Send data until we are ready for receiving.
    while not control_handler.may_receive():
        control_handler.do_send()
    while not control_handler.may_get():
        control_handler.do_receive()
    request_data = control_handler.do_get()
    request_type = request_data[4:8]
    if request_type == b'RRRR':
        try:
            remote_data = json.loads(request_data[8:])
            if remote_data[0] is not None:
                print('Remote execution exception:\n%s' % remote_data[0])
            if string_response_flag:
                print('Remote execution response: %s' % str(remote_data[1]))
            else:
                print('Remote execution response: %s' % repr(remote_data[1]))
        except:  # skipcq: FLK-E722
            print('Failed to process response %s' % repr(request_data))
            traceback.print_exc()
    else:
        raise Exception('Invalid request type %s' % repr(request_type))

remote_control_socket.close()
