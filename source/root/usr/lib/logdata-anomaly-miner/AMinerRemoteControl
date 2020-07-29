#!/usr/bin/python3 -BbbEIsSttW all
# -*- coding: utf-8 -*-

"""This tool allows to connect to a remote control socket, send requests and retrieve the responses. To allow remote use of this
tool, e.g. via SSH forwarding, the remote control address can be set on the command line, no configuration is read.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>."""

import json
import os
import socket
import traceback
import sys

from aminer.AnalysisChild import AnalysisChildRemoteControlHandler

__authors__ = ["Markus Wurzenberger", "Max Landauer", "Wolfgang Hotwagner", "Ernst Leierzopf", "Roman Fiedler", "Georg Hoeld",
               "Florian Skopik"]
__contact__ = "aecid@ait.ac.at"
__copyright__ = "Copyright 2020, AIT Austrian Institute of Technology GmbH"
__date__ = "2020/06/19"
__deprecated__ = False
__email__ = "aecid@ait.ac.at"
__license__ = "GPLv3"
__maintainer__ = "Markus Wurzenberger"
__status__ = "Production"
__version__ = "2.0.1"

# Get rid of the default sys path immediately. Otherwise Python also attempts to load the following imports from e.g. directory
# where this binary resides.
sys.path = sys.path[1:] + ['/usr/lib/logdata-anomaly-miner']

remote_control_socket_name = None
remote_control_data = None
arg_pos = 1
command_list = []
string_response_flag = False
while arg_pos < len(sys.argv):
    param_name = sys.argv[arg_pos]
    arg_pos += 1

    if param_name == '--ControlSocket':
        if remote_control_socket_name is not None:
            print('%s: %s parameter given twice' % (sys.argv[0], param_name))
            sys.exit(1)
        remote_control_socket_name = sys.argv[arg_pos]
        arg_pos += 1
        continue
    if param_name == '--Data':
        remote_control_data = json.loads(sys.argv[arg_pos])
        arg_pos += 1
        continue
    if param_name == '--Exec':
        command_list.append((sys.argv[arg_pos].encode(), remote_control_data))
        arg_pos += 1
        continue
    if param_name == '--ExecFile':
        if not os.path.exists(sys.argv[arg_pos]):
            print('File %s does not exit' % sys.argv[arg_pos])
            sys.exit(1)
        exec_data = None
        with open(sys.argv[arg_pos], 'rb') as exec_file:
            exec_data = exec_file.read()
        command_list.append((exec_data, remote_control_data))
        arg_pos += 1
        continue
    if param_name == '--Help':
        if len(sys.argv) != 2:
            print('Ignoring all other arguments with --Help')
        print("""Usage: %s [arguments]
  --ControlSocket [socketpath]: when given, use nonstandard control socket.
  --Data [data]: provide this json serialized data within execution
    environment as 'remote_control_data' (see man page).
  --Exec [command]: add command to the execution list, can be
    used more than once.
  --ExecFile [file]: add commands from file to the execution list
    in same way as if content would have been used with "--Exec".
  --Help: this output
  --StringResponse: if set, print the response just as string
    instead of passing it to repr.

  For further information read the man pages running 'man AMinerRemoteControl'.""" % sys.argv[0])
        sys.exit(0)
    if param_name == '--StringResponse':
        string_response_flag = True
        continue

    print('Unknown parameter "%s", use --Help for overview' % param_name)
    sys.exit(1)

if remote_control_socket_name is None:
    remote_control_socket_name = '/var/run/aminer-remote.socket'

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
