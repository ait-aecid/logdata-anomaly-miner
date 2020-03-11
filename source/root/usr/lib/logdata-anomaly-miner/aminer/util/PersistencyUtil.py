"""This module defines functions for reading and writing files
in a secure way."""

import errno
import os
import sys
import time

from aminer.util import SecureOSFunctions
from aminer.util import JsonUtil

# Have a registry of all persistable components. Those might be
# happy to be invoked before python process is terminating.
persistableComponents = []

def addPersistableComponent(component):
  """Add a component to the registry of all persistable components."""
  persistableComponents.append(component)

def openPersistenceFile(fileName, flags):
  """This function opens the given persistence file. When O_CREAT
  was specified, the function will attempt to create the directories
  too."""
  if isinstance(fileName, str):
    fileName = fileName.encode()
  try:
    fd = SecureOSFunctions.secureOpenFile(fileName, flags)
    return fd
  except OSError as openOsError:
    if ((flags&os.O_CREAT) == 0) or (openOsError.errno != errno.ENOENT):
      raise openOsError

# Find out, which directory is missing by stating our way up.
  dirNameLength = fileName.rfind(b'/')
  if dirNameLength > 0:
    os.makedirs(fileName[:dirNameLength])
  return SecureOSFunctions.secureOpenFile(fileName, flags)

def createTemporaryPersistenceFile(fileName):
  """Create a temporary file within persistence directory to write
  new persistence data to it. Thus the old data is not modified,
  any error creating or writing the file will not harm the old
  state."""
  fd = None
  # FIXME: This should use O_TMPFILE, but not yet available. That would
  # obsolete the loop also.
  # while True:
  #  fd = openPersistenceFile('%s.tmp-%f' % (fileName, time.time()), \
  #    os.O_WRONLY|os.O_CREAT|os.O_EXCL)
  #  break
  fd = openPersistenceFile('%s.tmp-%f' % (fileName, time.time()), \
     os.O_WRONLY|os.O_CREAT|os.O_EXCL)
  return fd
noSecureLinkUnlinkAtWarnOnceFlag = True
def replacePersistenceFile(fileName, newFileHandle):
  """Replace the named file with the file refered by the handle."""
  global noSecureLinkUnlinkAtWarnOnceFlag
  if noSecureLinkUnlinkAtWarnOnceFlag:
    print('WARNING: SECURITY: unsafe unlink (unavailable unlinkat/linkat should be used, but \
      not available in python)', file=sys.stderr)
    noSecureLinkUnlinkAtWarnOnceFlag = False
  try:
    os.unlink(fileName)
  except OSError as openOsError:
    if openOsError.errno != errno.ENOENT:
      raise openOsError

  tmpFileName = os.readlink('/proc/self/fd/%d' % newFileHandle)
  os.link(tmpFileName, fileName)
  os.unlink(tmpFileName)

def persistAll():
  """Persist all persistable components in the registry."""
  for component in persistableComponents:
    component.doPersist()

def loadJson(fileName):
  """Load persistency data from file.
  @return None if file did not yet exist."""
  persistenceData = None
  try:
    persistenceFileHandle = openPersistenceFile(fileName, os.O_RDONLY|os.O_NOFOLLOW)
    persistenceData = os.read(persistenceFileHandle, os.fstat(persistenceFileHandle).st_size)
    persistenceData = str(persistenceData, 'utf-8')
    os.close(persistenceFileHandle)
  except OSError as openOsError:
    if openOsError.errno != errno.ENOENT:
      raise openOsError
    return None

  result = None
  try:
    result = JsonUtil.loadJson(persistenceData)
  except ValueError as valueError:
    raise Exception('Corrupted data in %s' % fileName, valueError)

  return result


def storeJson(fileName, objectData):
  """Store persistency data to file."""
  persistenceData = JsonUtil.dumpAsJson(objectData)
  fd = createTemporaryPersistenceFile(fileName)
  os.write(fd, bytes(persistenceData, 'utf-8'))
  replacePersistenceFile(fileName, fd)
  os.close(fd)
