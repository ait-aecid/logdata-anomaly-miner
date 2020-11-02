"""
This module defines functions for reading and writing files in a secure way.

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

import errno
import os
import sys
import time

from aminer.util import SecureOSFunctions
from aminer.util import JsonUtil

# Have a registry of all persistable components. Those might be happy to be invoked before python process is terminating.
persistable_components = []


def add_persistable_component(component):
    """Add a component to the registry of all persistable components."""
    persistable_components.append(component)


def open_persistence_file(file_name, flags):
    """
    Open the given persistence file.
    When O_CREAT was specified, the function will attempt to create the directories too.
    """
    if isinstance(file_name, str):
        file_name = file_name.encode()
    try:
        fd = SecureOSFunctions.secure_open_file(file_name, flags)
        return fd
    except OSError as openOsError:
        if ((flags & os.O_CREAT) == 0) or (openOsError.errno != errno.ENOENT):
            raise openOsError

    # Find out, which directory is missing by stating our way up.
    dir_name_length = file_name.rfind(b'/')
    if dir_name_length > 0:
        os.makedirs(file_name[:dir_name_length])
    return SecureOSFunctions.secure_open_file(file_name, flags)


def create_temporary_persistence_file(file_name):
    """
    Create a temporary file within persistence directory to write new persistence data to it.
    Thus the old data is not modified, any error creating or writing the file will not harm the old state.
    """
    fd = None
    # skipcq: PYL-W0511
    # FIXME: This should use O_TMPFILE, but not yet available. That would obsolete the loop also.
    # while True:
    #  fd = openPersistenceFile('%s.tmp-%f' % (fileName, time.time()), os.O_WRONLY|os.O_CREAT|os.O_EXCL)
    #  break
    fd = open_persistence_file('%s.tmp-%f' % (file_name, time.time()), os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    return fd


no_secure_link_unlink_at_warn_once_flag = True


def replace_persistence_file(file_name, new_file_handle):
    """Replace the named file with the file refered by the handle."""
    # skipcq: PYL-W0603
    global no_secure_link_unlink_at_warn_once_flag
    if no_secure_link_unlink_at_warn_once_flag:
        print('WARNING: SECURITY: unsafe unlink (unavailable unlinkat/linkat should be used, but \
      not available in python)', file=sys.stderr)
        no_secure_link_unlink_at_warn_once_flag = False
    try:
        os.unlink(file_name)
    except OSError as openOsError:
        if openOsError.errno != errno.ENOENT:
            raise openOsError

    tmp_file_name = os.readlink('/proc/self/fd/%d' % new_file_handle)
    os.link(tmp_file_name, file_name)
    os.unlink(tmp_file_name)


def persist_all():
    """Persist all persistable components in the registry."""
    for component in persistable_components:
        component.do_persist()


def load_json(file_name):
    """
    Load persistence data from file.
    @return None if file did not yet exist.
    """
    persistence_data = None
    try:
        persistence_file_handle = open_persistence_file(file_name, os.O_RDONLY | os.O_NOFOLLOW)
        persistence_data = os.read(persistence_file_handle, os.fstat(persistence_file_handle).st_size)
        persistence_data = str(persistence_data, 'utf-8')
        os.close(persistence_file_handle)
    except OSError as openOsError:
        if openOsError.errno != errno.ENOENT:
            raise openOsError
        return None

    result = None
    try:
        result = JsonUtil.load_json(persistence_data)
    except ValueError as valueError:
        raise Exception('Corrupted data in %s' % file_name, valueError)

    return result


def store_json(file_name, object_data):
    """Store persistence data to file."""
    persistence_data = JsonUtil.dump_as_json(object_data)
    fd = create_temporary_persistence_file(file_name)
    os.write(fd, bytes(persistence_data, 'utf-8'))
    replace_persistence_file(file_name, fd)
    os.close(fd)
