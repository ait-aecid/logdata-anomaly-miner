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
import logging
import tempfile
import shutil
import sys

from aminer import AMinerConfig
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
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(openOsError)
            raise openOsError
    create_missing_directories(file_name)


def replace_persistence_file(file_name, new_file_handle):
    """Replace the named file with the file referred by the handle."""
    try:
        os.unlink(file_name, dir_fd=SecureOSFunctions.secure_open_base_directory())
    except OSError as openOsError:
        if openOsError.errno != errno.ENOENT:
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(openOsError)
            raise openOsError

    tmp_file_name = os.readlink('/proc/self/fd/%d' % new_file_handle)
    if SecureOSFunctions.base_dir_path.decode() in file_name:
        file_name = file_name.replace(SecureOSFunctions.base_dir_path.decode(), '').lstrip('/')
    os.link(
        tmp_file_name, file_name, src_dir_fd=SecureOSFunctions.tmp_base_dir_fd, dst_dir_fd=SecureOSFunctions.secure_open_base_directory())
    os.unlink(tmp_file_name, dir_fd=SecureOSFunctions.tmp_base_dir_fd)


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
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(openOsError)
            raise openOsError
        return None

    result = None
    try:
        result = JsonUtil.load_json(persistence_data)
    except ValueError as valueError:
        msg = 'Corrupted data in %s' % file_name, valueError
        logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
        raise Exception(msg)
    return result


def store_json(file_name, object_data):
    """Store persistence data to file."""
    persistence_data = JsonUtil.dump_as_json(object_data)
    # Create a temporary file within persistence directory to write new persistence data to it.
    # Thus the old data is not modified, any error creating or writing the file will not harm the old state.
    fd, _ = tempfile.mkstemp(dir=SecureOSFunctions.tmp_base_dir_path)
    os.write(fd, bytes(persistence_data, 'utf-8'))
    create_missing_directories(file_name)
    replace_persistence_file(file_name, fd)
    os.close(fd)


def create_missing_directories(file_name):
    """Create missing persistence directories."""
    # Find out, which directory is missing by stating our way up.
    dir_name_length = file_name.rfind('/')
    if dir_name_length > 0:
        if not os.path.exists(file_name[:dir_name_length]):
            os.makedirs(file_name[:dir_name_length])


def clear_persistence(persistence_dir_name):
    """Delete all persistence data from the persistence_dir."""
    for filename in os.listdir(persistence_dir_name):
        if filename == 'backup':
            continue
        file_path = os.path.join(persistence_dir_name, filename)
        try:
            if not os.path.isdir(file_path):
                msg = 'The AMiner persistence directory should not contain any files.'
                print(msg, file=sys.stderr)
                logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).warning(msg)
                continue
            shutil.rmtree(file_path)
        except OSError as e:
            msg = 'Failed to delete %s. Reason: %s' % (file_path, e)
            print(msg, file=sys.stderr)
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)


def copytree(src, dst, symlinks=False, ignore=None):
    """Copy a directory recursively. This method has no issue with the destination directory existing (shutil.copytree has)."""
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
