"""This module defines functions for secure file handling."""

import os
import socket
import struct
import sys

# Those should go away as soon as Python (or aminer via libc)
# provides those functions.
no_secure_open_warn_once_flag = True


def secure_open_file(file_name, flags):
    """Secure opening of a file with given flags. This call will refuse to open files where any path component is a symlink.
    As operating system does not provide any means to do that, open the file_name directory by directory. It also adds O_NOCTTY to the
    flags as controlling TTY logics as this is just an additional risk and does not make sense for opening of log files.
    @param file_name is the fileName as byte string"""

    if not file_name.startswith(b'/'):
        raise Exception('Secure open on relative path not supported')
    if (file_name.endswith(b'/')) and ((flags & os.O_DIRECTORY) == 0):
        raise Exception('Opening directory but O_DIRECTORY flag missing')

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

    global no_secure_open_warn_once_flag
    if no_secure_open_warn_once_flag:
        print('WARNING: SECURITY: No secure open yet due to missing openat in python!', file=sys.stderr)
        no_secure_open_warn_once_flag = False
    return os.open(file_name, flags | os.O_NOFOLLOW | os.O_NOCTTY)


def send_annotated_file_descriptor(send_socket, send_fd, type_info, annotation_data):
    """Send file descriptor and associated annotation data via SCM_RIGHTS.
    @param type_info has to be a null-byte free string to inform the receiver how to handle the file descriptor and how to interpret
    the annotationData.
    @param annotation_data this optional byte array  may convey additional information about the file descriptor."""
    # Construct the message data first
    if isinstance(type_info, str):
        type_info = type_info.encode()
    if isinstance(annotation_data, str):
        annotation_data = annotation_data.encode()
    if type_info.find(b'\x00') >= 0:
        raise Exception('Null bytes not supported in typeInfo')
    message_data = b'%s\x00%s' % (type_info, annotation_data)
    send_socket.sendmsg([message_data], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, struct.pack('i', send_fd))])


def send_logstream_descriptor(send_socket, send_fd, send_file_name):
    """Send a file descriptor to be used as standard log data stream source for the analysis pipeline."""
    send_annotated_file_descriptor(send_socket, send_fd, b'logstream', send_file_name)


def receive_annoted_file_descriptor(receive_socket):
    """Receive a single file descriptor and attached annotation information via SCM_RIGHTS via the given socket. The method
    may raise an Exception when invoked on non-blocking sockets and no messages available.
    @return a tuple containing the received file descriptor, type information (see sendAnnotatedFileDescriptor) and the annotation
    information."""
    message_data, anc_data, _flags, _remote_address = receive_socket.recvmsg(1 << 16, socket.CMSG_LEN(struct.calcsize('i')))
    if len(anc_data) != 1:
        raise Exception('Received %d sets of ancillary data instead of 1' % len(anc_data))
    cmsg_level, cmsg_type, cmsg_data = anc_data[0]
    if (cmsg_level != socket.SOL_SOCKET) or (cmsg_type != socket.SCM_RIGHTS):
        raise Exception('Received invalid message from remote side')
    # Do not accept multiple or unaligned FDs.
    if len(cmsg_data) != 4:
        raise Exception('Unsupported control message length %d' % len(cmsg_data))
    received_fd = struct.unpack('i', cmsg_data)[0]

    split_pos = message_data.find(b'\x00')
    if split_pos < 0:
        raise Exception('No null byte in received message')
    type_info = message_data[:split_pos]
    annotation_data = message_data[split_pos + 1:]
    if received_fd <= 2:
        print('WARNING: received "reserved" fd %d' % received_fd, file=sys.stderr)
    if isinstance(type_info, str):
        type_info = type_info.encode()
    if isinstance(annotation_data, str):
        annotation_data = annotation_data.encode()
    return received_fd, type_info, annotation_data
