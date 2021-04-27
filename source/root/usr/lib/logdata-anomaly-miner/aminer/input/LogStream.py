"""
This module contains interfaces and classes for logdata resource handling and combining them to resumable virtual LogStream objects.

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

import base64
import errno
import hashlib
import os
import socket
import stat
import sys
import logging

from aminer.AminerConfig import DEBUG_LOG_NAME
from aminer.util import SecureOSFunctions
from aminer.util.StringUtil import encode_byte_string_as_string
from aminer.input.InputInterfaces import LogDataResource


class FileLogDataResource(LogDataResource):
    """
    This class defines a single log data resource using an underlying file accessible via the file descriptor.
    The characteristics of this type of resource is, that reopening and repositioning of the stream has to be possible.
    """

    def __init__(self, log_resource_name, log_stream_fd, default_buffer_size=1 << 16, repositioning_data=None):
        """
        Create a new file type resource.
        @param log_resource_name the unique name of this source as bytes array, has to start with "file://" before the file path.
        @param log_stream_fd the stream for reading the resource or -1 if not yet opened.
        @param repositioning_data if not None, attempt to position the stream using the given data.
        """
        if not log_resource_name.startswith(b'file://'):
            msg = 'Attempting to create different type resource as file'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        self.log_resource_name = log_resource_name
        self.log_file_fd = log_stream_fd
        self.stat_data = None
        if self.log_file_fd >= 0:
            self.stat_data = os.fstat(log_stream_fd)
        self.buffer = b''
        self.default_buffer_size = default_buffer_size
        self.total_consumed_length = 0
        # Create a hash for repositioning. There is no need to be cryptographically secure here: if upstream can manipulate the content,
        # to provoke hash collisions, correct positioning would not matter anyway.
        # skipcq: PTC-W1003
        self.repositioning_digest = hashlib.md5()

        if (log_stream_fd != -1) and (repositioning_data is not None):
            if repositioning_data[0] != self.stat_data.st_ino:
                msg = 'Not attempting to reposition on %s, inode number mismatch' % encode_byte_string_as_string(self.log_resource_name)
                logging.getLogger(DEBUG_LOG_NAME).warning(msg)
                print(msg, file=sys.stderr)
            elif repositioning_data[1] > self.stat_data.st_size:
                msg = 'Not attempting to reposition on %s, file size too small' % encode_byte_string_as_string(self.log_resource_name)
                logging.getLogger(DEBUG_LOG_NAME).warning(msg)
                print(msg, file=sys.stderr)
            else:
                # skipcq: PTC-W1003
                hash_algo = hashlib.md5()
                length = repositioning_data[1]
                while length != 0:
                    block = None
                    if length < default_buffer_size:
                        block = os.read(self.log_file_fd, length)
                    else:
                        block = os.read(self.log_file_fd, default_buffer_size)
                    if not block:
                        msg = 'Not attempting to reposition on %s, file shrunk while reading' % encode_byte_string_as_string(
                            self.log_resource_name)
                        logging.getLogger(DEBUG_LOG_NAME).warning(msg)
                        print(msg, file=sys.stderr)
                        break
                    hash_algo.update(block)
                    length -= len(block)
                digest = hash_algo.digest()
                if length == 0:
                    if digest == base64.b64decode(repositioning_data[2]):
                        # Repositioning is OK, keep current digest and length data.
                        self.total_consumed_length = repositioning_data[1]
                        self.repositioning_digest = hash_algo
                    else:
                        msg = 'Not attempting to reposition on %s, digest changed' % encode_byte_string_as_string(self.log_resource_name)
                        logging.getLogger(DEBUG_LOG_NAME).warning(msg)
                        print(msg, file=sys.stderr)
                        length = -1
                if length != 0:
                    # Repositioning failed, go back to the beginning of the stream.
                    os.lseek(self.log_file_fd, 0, os.SEEK_SET)

    def open(self, reopen_flag=False):
        """
        Open the given resource.
        @param reopen_flag when True, attempt to reopen the same resource and check if it differs from the previously opened one.
        @raise Exception if valid log_stream_fd was already provided, is still open and reopen_flag is False.
        @raise OSError when opening failed with unexpected error.
        @return True if the resource was really opened or False if opening was not yet possible but should be attempted again.
        """
        if not reopen_flag and (self.log_file_fd != -1):
            msg = 'Cannot reopen stream still open when not instructed to do so'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        log_file_fd = -1
        stat_data = None
        try:
            log_file_fd = SecureOSFunctions.secure_open_file(self.log_resource_name[7:], os.O_RDONLY)
            stat_data = os.fstat(log_file_fd)
        except OSError as openOsError:
            msg = 'OSError occurred in FileLogDataResource.open(). Error message: %s' % openOsError
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            if log_file_fd != -1:
                os.close(log_file_fd)
            if openOsError.errno == errno.ENOENT:
                return False
            raise
        if not stat.S_ISREG(stat_data.st_mode):
            os.close(log_file_fd)
            msg = 'Attempting to open non-regular file %s as file' % encode_byte_string_as_string(self.log_resource_name)
            print(msg, file=sys.stderr)
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)

        if reopen_flag and (self.stat_data is not None) and (stat_data.st_ino == self.stat_data.st_ino) and (
                stat_data.st_dev == self.stat_data.st_dev):
            # Reopening was requested, but we would reopen the file already opened, which is of no use.
            os.close(log_file_fd)
            return False
        # This is a new file or a successful reopen attempt.
        self.log_file_fd = log_file_fd
        self.stat_data = stat_data
        return True

    def get_resource_name(self):
        """Get the name of this log resource."""
        return self.log_resource_name

    def get_file_descriptor(self):
        """Get the file descriptor of this open resource."""
        return self.log_file_fd

    def fill_buffer(self):
        """
        Fill the buffer data of this resource. The repositioning information is not updated, update_position() has to be used.
        @return the number of bytes read or -1 on error or end.
        """
        data = os.read(self.log_file_fd, self.default_buffer_size)
        self.buffer += data
        return len(data)

    def update_position(self, length):
        """Update the positioning information and discard the buffer data afterwards."""
        self.repositioning_digest.update(self.buffer[:length])
        self.total_consumed_length += length
        self.buffer = self.buffer[length:]

    def get_repositioning_data(self):
        """Get the data for repositioning the stream. The returned structure has to be JSON serializable."""
        return [self.stat_data.st_ino, self.total_consumed_length, base64.b64encode(self.repositioning_digest.digest())]

    def close(self):
        """Close the log file."""
        os.close(self.log_file_fd)
        self.log_file_fd = -1


class UnixSocketLogDataResource(LogDataResource):
    """
    This class defines a single log data resource connecting to a local UNIX socket.
    The characteristics of this type of resource is, that reopening works only after end of stream of was reached.
    """

    # skipcq: PYL-W0231
    def __init__(self, log_resource_name, log_stream_fd, default_buffer_size=1 << 16, repositioning_data=None):
        """
        Create a new unix socket type resource.
        @param log_resource_name the unique name of this source as byte array, has to start with "unix://" before the file path.
        @param log_stream_fd the stream for reading the resource or -1 if not yet opened.
        @param repositioning_data has to be None for this type of resource.
        """
        if not log_resource_name.startswith(b'unix://'):
            msg = 'Attempting to create different type resource as unix'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        self.log_resource_name = log_resource_name
        self.log_stream_fd = log_stream_fd
        self.buffer = b''
        self.default_buffer_size = default_buffer_size
        self.total_consumed_length = 0

    def open(self, reopen_flag=False):
        """
        Open the given resource.
        @param reopen_flag when True, attempt to reopen the same resource and check if it differs from the previously opened one.
        @raise Exception if valid log_stream_fd was already provided, is still open and reopenFlag is False.
        @raise OSError when opening failed with unexpected error.
        @return True if the resource was really opened or False if opening was not yet possible but should be attempted again.
        """
        if reopen_flag:  # skipcq: PTC-W0048
            if self.log_stream_fd != -1:
                return False
        elif self.log_stream_fd != -1:
            msg = 'Cannot reopen stream still open when not instructed to do so'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        log_socket = None
        try:
            log_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            log_socket.connect(self.log_resource_name[7:])
        except socket.error as socketError:
            logging.getLogger(DEBUG_LOG_NAME).error('OSError occurred in UnixSocketLogDataResource.open(). Error message: %s',
                                                    socketError.msg)
            if log_socket is not None:
                log_socket.close()
            if socketError.errno in (errno.ENOENT, errno.ECONNREFUSED):
                return False
            # Transform exception to OSError as caller does not expect something else.
            raise OSError(socketError[0], socketError[1])
        self.log_stream_fd = os.dup(log_socket.fileno())
        log_socket.close()
        return True

    def get_resource_name(self):
        """Get the name of this log resoruce."""
        return self.log_resource_name

    def get_file_descriptor(self):
        """Get the file descriptor of this open resource."""
        return self.log_stream_fd

    def fill_buffer(self):
        """
        Fill the buffer data of this resource. The repositioning information is not updated, update_position() has to be used.
        @return the number of bytes read or -1 on error or end.
        """
        data = os.read(self.log_stream_fd, self.default_buffer_size)
        self.buffer += data
        return len(data)

    def update_position(self, length):
        """Update the positioning information and discard the buffer data afterwards."""
        self.total_consumed_length += length
        self.buffer = self.buffer[length:]

    def get_repositioning_data(self):
        """Get the data for repositioning the stream. The returned structure has to be JSON serializable."""
        return None

    def close(self):
        """Close the log stream."""
        os.close(self.log_stream_fd)
        self.log_stream_fd = -1


class LogStream:
    """
    This class defines a continuous stream of logging data from a given source.
    This class also handles rollover from one file descriptor to a new one.
    """

    def __init__(self, log_data_resource, stream_atomizer):
        """
        Create a new logstream with an initial logDataResource.
        @param stream_atomizer the atomizer to forward data to.
        """
        # The resource currently processed. Might also be None when previous
        # resource was read till end and no rollover to new one had occurred.
        self.log_data_resource = log_data_resource
        self.stream_atomizer = stream_atomizer
        # Last reading state, those are the same as returned by StreamAtomizer
        # consumeData() method. Start with state 0 (more data required).
        self.last_consume_state = 0
        self.next_resources = []

    def add_next_resource(self, next_log_data_resource):
        """
        Roll over from one fd to another one pointing to the newer version of the same file.
        This will also change reading behaviour of current resource to await EOF or stop as soon as first blocking read does not return
        any data.
        """
        # Just append the resource to the list of next resources. The next read operation without any input from the primary resource
        # will pick it up automatically.
        if self.log_data_resource is None:
            self.log_data_resource = next_log_data_resource
        else:
            self.next_resources.append(next_log_data_resource)

    def handle_stream(self):
        """
        Handle data from this stream by forwarding it to the atomizer.
        @return the file descriptor to monitoring for new input or -1 if there is no new data or atomizer was not yet ready to
        consume data. Handling should be tried again later on.
        """
        if self.log_data_resource is None:
            return -1
        if self.last_consume_state == 0:
            # We need more data, read it.
            read_length = self.log_data_resource.fill_buffer()
            if read_length == -1:
                self.last_consume_state = self.roll_over()
                return self.last_consume_state

            if read_length == 0:
                if not self.next_resources:
                    # There is just no input, but we still need more since last round as indicated by lastConsumeState. We would not have
                    # been called if this is a blocking stream, so this must be the preliminary end of the file. Tell caller to wait and
                    # retry read later on. Keep lastConsumeState value, consume still wants more data.
                    return -1

                # This seems to EOF for rollover.
                self.last_consume_state = self.roll_over()
                return self.last_consume_state

        # So there was something read, process it the same way as if data was already available in previous round.
        self.last_consume_state = self.stream_atomizer.consume_data(self.log_data_resource.buffer, False)
        if self.last_consume_state < 0:
            return -1
        if self.last_consume_state != 0:
            self.log_data_resource.update_position(self.last_consume_state)
        return self.log_data_resource.get_file_descriptor()

    def roll_over(self):
        """
        End reading of the current resource and switch to the next.
        This method does not handle last_consume_state, that has to be done outside.
        @return state in same manner as handle_stream()
        """
        consumed_length = self.stream_atomizer.consume_data(self.log_data_resource.buffer, True)
        if consumed_length < 0:
            # Consumer is not ready to consume yet. Retry later on.
            return -1
        if consumed_length != len(self.log_data_resource.buffer):
            if consumed_length != 0:
                # Some data consumed, unclear why not all when already at end of stream. Retry again immediately to find out why.
                self.log_data_resource.update_position(consumed_length)
                return self.log_data_resource.get_file_descriptor()

            # This is a clear protocol violation (see StreamAtomizer documentation): When at EOF, 0 is no valid return value.
            msg = 'Procotol violation by %s detected, flushing data' % self.stream_atomizer.__class__.__name__
            logging.getLogger(DEBUG_LOG_NAME).critical(msg)
            print('FATAL: ' + msg, file=sys.stderr)
            consumed_length = len(self.log_data_resource.buffer)

        # Everything consumed, so now ready for rollover.
        self.log_data_resource.update_position(consumed_length)
        self.log_data_resource.close()
        if not self.next_resources:
            self.log_data_resource = None
            return -1
        self.log_data_resource = self.next_resources[0]
        del self.next_resources[0]
        return self.log_data_resource.get_file_descriptor()

    def get_current_fd(self):
        """Get the file descriptor for reading the currently active log_data resource."""
        if self.log_data_resource is None:
            return -1
        return self.log_data_resource.get_file_descriptor()

    def get_repositioning_data(self):
        """Get the repositioning information from the currently active underlying log_data resource."""
        if self.log_data_resource is None:
            return None
        return self.log_data_resource.get_repositioning_data()

    def close(self):
        """Close the log stream."""
        if self.log_data_resource is not None:
            self.log_data_resource.close()
