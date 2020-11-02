"""
This module defines functions for secure file handling.

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
import socket
import struct
import sys
import logging
from aminer import AMinerConfig

# Those should go away as soon as Python (or aminer via libc)
# provides those functions.
no_secure_open_warn_once_flag = True


def secure_open_file(file_name, flags):
    """
    Secure opening of a file with given flags. This call will refuse to open files where any path component is a symlink.
    As operating system does not provide any means to do that, open the file_name directory by directory. It also adds O_NOCTTY to the
    flags as controlling TTY logics as this is just an additional risk and does not make sense for opening of log files.
    @param file_name is the fileName as byte string
    """
    if not file_name.startswith(b'/'):
        msg = 'Secure open on relative path not supported'
        logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
        raise Exception(msg)
    if (file_name.endswith(b'/')) and ((flags & os.O_DIRECTORY) == 0):
        msg = 'Opening directory but O_DIRECTORY flag missing'
        logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
        raise Exception(msg)

    # This code would allow secure open but openat is not available
    # in python2 series. A long way to go, but keep it here for the
    # python3 port to come.
    # if trustedRoot=='/':
    #   fileName = fileName[1:]
    # else:
    #   if (not fileName.startswith(trustedRoot)) or (fileName[len(trustedRoot)] != '/'):
    #     raise Exception('File name not within trusted root')
    #   fileName = fileName[len(trustedRoot)+1:]
    #
    # dirFd = os.open(trustedRoot, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_NOCTTY)
    # lastPathPart = None
    # Open all path parts excluding the last one only as directory.
    # This will prevent us from opening something unexpected if a
    # user would move around directories while traversing.
    # for part in fileName.split['/']:
    #   if len(part)==0: continue
    #   if lastPathPart is not None:
    #     nextFd = os.openat(dirFd, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_NOCTTY)
    #     os.close(dirFd)
    #     dirFd = nextFd
    #   lastPathPart = part
    # if lastPathPart is None: lastPathPart = '.'
    # result = os.openat(dirFd, lastPathPart, flags|os.O_NOFOLLOW|os.O_NOCTTY)
    # os.close(dirFd)
    # return(result)
    # skipcq: PYL-W0603
    global no_secure_open_warn_once_flag
    if no_secure_open_warn_once_flag:
        msg = 'SECURITY: No secure open yet due to missing openat in python!'
        logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).warning(msg)
        print('WARNING: ' + msg, file=sys.stderr)
        no_secure_open_warn_once_flag = False
    return os.open(file_name, flags | os.O_NOFOLLOW | os.O_NOCTTY)


def send_annotated_file_descriptor(send_socket, send_fd, type_info, annotation_data):
    """
    Send file descriptor and associated annotation data via SCM_RIGHTS.
    @param type_info has to be a null-byte free string to inform the receiver how to handle the file descriptor and how to interpret
    the annotationData.
    @param annotation_data this optional byte array  may convey additional information about the file descriptor.
    """
    # Construct the message data first
    if isinstance(type_info, str):
        type_info = type_info.encode()
    if isinstance(annotation_data, str):
        annotation_data = annotation_data.encode()
    if type_info.find(b'\x00') >= 0:
        msg = 'Null bytes not supported in typeInfo'
        logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
        raise Exception(msg)
    message_data = b'%s\x00%s' % (type_info, annotation_data)
    send_socket.sendmsg([message_data], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, struct.pack('i', send_fd))])


def send_logstream_descriptor(send_socket, send_fd, send_file_name):
    """Send a file descriptor to be used as standard log data stream source for the analysis pipeline."""
    send_annotated_file_descriptor(send_socket, send_fd, b'logstream', send_file_name)


def receive_annoted_file_descriptor(receive_socket):
    """
    Receive a single file descriptor and attached annotation information via SCM_RIGHTS via the given socket.
    The method may raise an Exception when invoked on non-blocking sockets and no messages available.
    @return a tuple containing the received file descriptor, type information (see sendAnnotatedFileDescriptor) and the annotation
    information.
    """
    message_data, anc_data, _flags, _remote_address = receive_socket.recvmsg(1 << 16, socket.CMSG_LEN(struct.calcsize('i')))
    if len(anc_data) != 1:
        msg = 'Received %d sets of ancillary data instead of 1' % len(anc_data)
        logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
        raise Exception(msg)
    cmsg_level, cmsg_type, cmsg_data = anc_data[0]
    if (cmsg_level != socket.SOL_SOCKET) or (cmsg_type != socket.SCM_RIGHTS):
        msg = 'Received invalid message from remote side'
        logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
        raise Exception(msg)
    # Do not accept multiple or unaligned FDs.
    if len(cmsg_data) != 4:
        msg = 'Unsupported control message length %d' % len(cmsg_data)
        logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
        raise Exception(msg)
    received_fd = struct.unpack('i', cmsg_data)[0]

    split_pos = message_data.find(b'\x00')
    if split_pos < 0:
        msg = 'No null byte in received message'
        logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
        raise Exception(msg)
    type_info = message_data[:split_pos]
    annotation_data = message_data[split_pos + 1:]
    if received_fd <= 2:
        msg = 'received "reserved" fd %d' % received_fd
        logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).warning(msg)
        print('WARNING: ', file=sys.stderr)
    if isinstance(type_info, str):
        type_info = type_info.encode()
    if isinstance(annotation_data, str):
        annotation_data = annotation_data.encode()
    return received_fd, type_info, annotation_data
