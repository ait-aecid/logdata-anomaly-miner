import errno
import json
import os

from aminer import AMinerUtils

# Have a registry of all persistable components. Those might be
# happy to be invoked before python process is terminating.
persistableComponents=[]
def addPersistableComponent(component):
  persistableComponents.append(component)

def persistAll():
  for component in persistableComponents:
    component.doPersist()

def loadJson(fileName):
  """Load persistency data from file.
  @return None if file did not yet exist."""

  persistenceData=None
  try:
    persistenceFileHandle=AMinerUtils.openPersistenceFile(fileName, os.O_RDONLY|os.O_NOFOLLOW)
    persistenceData=os.read(persistenceFileHandle, os.fstat(persistenceFileHandle).st_size)
    os.close(persistenceFileHandle)
  except OSError as openOsError:
    if openOsError.errno!=errno.ENOENT:
      raise openOsError
    return(None)

  result=None
  try:
    result=json.loads(persistenceData)
  except ValueError as valueError:
    raise Exception('Corrupted data in %s' % fileName, valueError)

  return(result)


def storeJson(fileName, objectData):
  """Store persistency data to file."""
  persistenceData=json.dumps(objectData)
  fd=AMinerUtils.createTemporaryPersistenceFile(fileName)
  os.write(fd, persistenceData)
  AMinerUtils.replacePersistenceFile(fileName, fd)
  os.close(fd)
