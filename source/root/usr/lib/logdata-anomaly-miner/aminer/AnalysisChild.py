"""This module contains classes for execution of py child
process main analysis loop."""

import base64
import errno
import fcntl
import json
import os
import select
import socket
import struct
import sys
import time
import traceback
import resource
import subprocess

from aminer import AMinerConfig
from aminer.input.LogStream import LogStream
from aminer.util import PersistencyUtil
from aminer.util import SecureOSFunctions
from aminer.util import TimeTriggeredComponentInterface
from aminer.util import JsonUtil
from aminer.input.ByteStreamLineAtomizer import ByteStreamLineAtomizer
from builtins import str
from aminer.AMinerRemoteControlExecutionMethods import AMinerRemoteControlExecutionMethods

class AnalysisContext(object):
  """This class collects information about the current analysis
  context to access it during analysis or remote management."""

  TIME_TRIGGER_CLASS_REALTIME = 1
  TIME_TRIGGER_CLASS_ANALYSISTIME = 2

  def __init__(self, aminerConfig):
    self.aminerConfig = aminerConfig
# This is the factory to create atomiziers for incoming data streams
# and link them to the analysis pipeline.
    self.atomizerFactory = None
# This is the current log processing and analysis time regarding
# the data stream being analyzed. While None, the analysis time
# e.g. used to trigger components (see analysisTimeTriggeredComponents),
# is the same as current system time. For forensic analysis this
# time has to be updated to values derived from the log data input
# to reflect the current log processing time, which will be in
# the past and may progress much faster than real system time.
    self.analysisTime = None
# Keep a registry of all analysis and filter configuration for
# later use. Remote control interface may then access them for
# runtime reconfiguration.
    self.nextRegistryId = 0
    self.registeredComponents = {}
# Keep also a list of components by name.
    self.registeredComponentsByName = {}
# Keep lists of components that should receive timer interrupts
# when real time or analysis time has elapsed.
    self.realTimeTriggeredComponents = []
    self.analysisTimeTriggeredComponents = []

  def addTimeTriggeredComponent(self, component, triggerClass=None):
    """Add a time-triggered component to the registry."""
    if not isinstance(component, TimeTriggeredComponentInterface):
      raise Exception('Attempting to register component of class ' \
          '%s not implementing aminer.util.TimeTriggeredComponentInterface' % (
              component.__class__.__name__))
    if triggerClass is None:
      triggerClass = component.getTimeTriggerClass()
    if triggerClass == AnalysisContext.TIME_TRIGGER_CLASS_REALTIME:
      self.realTimeTriggeredComponents.append(component)
    elif triggerClass == AnalysisContext.TIME_TRIGGER_CLASS_ANALYSISTIME:
      self.analysisTimeTriggeredComponents.append(component)
    else:
      raise Exception('Attempting to timer component for unknown class %s' % triggerClass)

  def registerComponent(
      self, component, componentName=None, registerTimeTriggerClassOverride=None):
    """Register a new component. A component implementing the
    TimeTriggeredComponentInterface will also be added to the
    appropriate lists unless registerTimeTriggerClassOverride
    is specified.
    @param componentName when not none, the component is also
    added to the named components. When a component with the same
    name was already registered, this will cause an error.
    @param registerTimeTriggerClassOverride if not none, ignore
    the time trigger class supplied by the component and register
    it for the classes specified in the override list. Use an
    empty list to disable registration."""
    if (componentName != None) and (componentName in self.registeredComponentsByName):
      raise Exception('Component with same name already registered')
    if (registerTimeTriggerClassOverride != None) and \
        (not isinstance(component, TimeTriggeredComponentInterface)):
      raise Exception('Requesting override on component not implementing ' \
          'TimeTriggeredComponentInterface')

    self.registeredComponents[self.nextRegistryId] = (component, componentName)
    self.nextRegistryId += 1
    if componentName != None:
      self.registeredComponentsByName[componentName] = component
    if isinstance(component, TimeTriggeredComponentInterface):
      if registerTimeTriggerClassOverride is None:
        self.addTimeTriggeredComponent(component)
      else:
        for triggerClass in registerTimeTriggerClassOverride:
          self.addTimeTriggeredComponent(component, triggerClass)

  def getRegisteredComponentIds(self):
    """Get a list of currently known component IDs."""
    return self.registeredComponents.keys()

  def getComponentById(self, idString):
    """Get a component by ID.
    @return None if not found."""
    componentInfo = self.registeredComponents.get(idString, None)
    if componentInfo is None:
      return None
    return componentInfo[0]

  def getRegisteredComponentNames(self):
    """Get a list of currently known component names."""
    return list(self.registeredComponentsByName.keys())

  def getComponentByName(self, name):
    """Get a component by name.
    @return None if not found."""
    return self.registeredComponentsByName.get(name, None)

  def getNameByComponent(self, component):
    """Get the name of a component.
    @return None if not found."""
    for componentName, componentIter in self.registeredComponentsByName.items():
      if componentIter == component:
        return componentName
    return None

  def getIdByComponent(self, component):
    """Get the name of a component.
    @return None if not found."""
    for componentName, componentIter in self.registeredComponentsByName.items():
      if componentIter == component:
        return componentName
    return None

  def buildAnalysisPipeline(self):
    """Convenience method to create the pipeline."""
    self.aminerConfig.buildAnalysisPipeline(self)

class AnalysisChild(TimeTriggeredComponentInterface):
  """This class defines the child performing the complete analysis
  workflow. When splitting privileges between analysis and monitor
  process, this class should only be initialized within the analysis
  process!"""
  
  def __init__(self, programName, aminerConfig):
    self.programName = programName
    self.analysisContext = AnalysisContext(aminerConfig)
    self.runAnalysisLoopFlag = True
    self.logStreamsByName = {}
    self.persistenceFileName = AMinerConfig.buildPersistenceFileName(
        self.analysisContext.aminerConfig,
        self.__class__.__name__+'/RepositioningData')
    self.nextPersistTime = time.time()+600

    self.repositioningDataDict = {}
    self.masterControlSocket = None
    self.remoteControlSocket = None

# This dictionary provides a lookup list from file descriptor
# to associated object for handling the data to and from the given
# descriptor. Currently supported handler objects are:
# * Parent process socket
# * Remote control listening socket
# * LogStreams
# * Remote control connections
    self.trackedFdsDict = {}

# Override the signal handler to allow graceful shutdown.
    def gracefulShutdownHandler(_signo, _stackFrame):
      """This is the signal handler function to react on typical
      shutdown signals."""
      print('%s: caught signal, shutting down' % programName, file=sys.stderr)
      self.runAnalysisLoopFlag = False
    import signal
    signal.signal(signal.SIGHUP, gracefulShutdownHandler)
    signal.signal(signal.SIGINT, gracefulShutdownHandler)
    signal.signal(signal.SIGTERM, gracefulShutdownHandler)

# Do this on at the end of the initialization to avoid having
# partially initialized objects inside the registry.
    self.analysisContext.addTimeTriggeredComponent(self)


  def runAnalysis(self, masterFd):
    """This method runs the analysis thread.
    @param masterFd the main communication socket to the parent
    to receive logfile updates from the parent.
    @return 0 on success, e.g. normal termination via signal or
    1 on error."""

# The masterControlSocket is the socket to communicate with the
# master process to receive commands or logstream data. Expect
# the parent/child communication socket on fd 3. This also duplicates
# the fd, so close the old one.
    self.masterControlSocket = socket.fromfd(
        masterFd, socket.AF_UNIX, socket.SOCK_DGRAM, 0)
    os.close(masterFd)
    self.trackedFdsDict[self.masterControlSocket.fileno()] = \
        self.masterControlSocket

# Locate the real analysis configuration.
    self.analysisContext.buildAnalysisPipeline()
    if self.analysisContext.atomizerFactory is None:
      print('FATAL: buildAnalysisPipeline() did ' \
          'not initialize atomizerFactory, terminating', file=sys.stderr)
      return 1

    realTimeTriggeredComponents = self.analysisContext.realTimeTriggeredComponents
    analysisTimeTriggeredComponents = self.analysisContext.analysisTimeTriggeredComponents
    
    maxMemoryMB = self.analysisContext.aminerConfig.configProperties.get(AMinerConfig.KEY_RESOURCES_MAX_MEMORY_USAGE, None)
    if maxMemoryMB is not None:
      try:
        maxMemoryMB = int(maxMemoryMB)
        resource.setrlimit(resource.RLIMIT_AS, (maxMemoryMB*1024*1024, resource.RLIM_INFINITY))
      except ValueError:
        print('FATAL: %s must be an integer, terminating'
          % AMinerConfig.KEY_RESOURCES_MAX_MEMORY_USAGE, file=sys.stderr)
        return 1
      
    maxCpuPercentUsage = self.analysisContext.aminerConfig.configProperties.get(AMinerConfig.KEY_RESOURCES_MAX_PERCENT_CPU_USAGE)
    if maxCpuPercentUsage is not None:
      try:
        maxCpuPercentUsage = int(maxCpuPercentUsage)
        # limit
        pid = os.getpid()
        packageInstalledCmd = ['dpkg', '-l', 'cpulimit']
        cpulimitCmd = ['cpulimit', '-p', str(pid), '-l', str(maxCpuPercentUsage)]
        
        out = subprocess.Popen(packageInstalledCmd, 
           stdout=subprocess.PIPE, 
           stderr=subprocess.STDOUT)
        stdout,stderr = out.communicate()
        
        if 'dpkg-query: no packages found matching cpulimit' in stdout.decode():
          print('FATAL: cpulimit package must be installed, when using the property %s'
            % AMinerConfig.KEY_RESOURCES_MAX_PERCENT_CPU_USAGE, file=sys.stderr)
          return 1
        else:
          out = subprocess.Popen(cpulimitCmd, 
           stdout=subprocess.PIPE, 
           stderr=subprocess.STDOUT)
      except ValueError:
        print('FATAL: %s must be an integer, terminating' 
          % AMinerConfig.KEY_RESOURCES_MAX_PERCENT_CPU_USAGE, file=sys.stderr)
        return 1

# Load continuation data for last known log streams. The loaded
# data has to be a dictionary with repositioning information for
# each stream. The data is used only when creating the first stream
# with that name.
    self.repositioningDataDict = PersistencyUtil.loadJson(
        self.persistenceFileName)
    if self.repositioningDataDict is None:
      self.repositioningDataDict = {}

# A list of LogStreams where handleStream() blocked due to downstream
# not being able to consume the data yet.
    blockedLogStreams = []

# Always start when number is None.
    nextRealTimeTriggerTime = None
    nextAnalysisTimeTriggerTime = None

    delayedReturnStatus = 0
    while self.runAnalysisLoopFlag:
# Build the list of inputs to select for anew each time: the LogStream
# file descriptors may change due to rollover.
      inputSelectFdList = []
      outputSelectFdList = []
      for fdHandlerObject in self.trackedFdsDict.values():
        if isinstance(fdHandlerObject, LogStream):
          streamFd = fdHandlerObject.getCurrentFd()
          if streamFd < 0:
            continue
          inputSelectFdList.append(streamFd)
        elif isinstance(fdHandlerObject, AnalysisChildRemoteControlHandler):
          fdHandlerObject.addSelectFds(
              inputSelectFdList, outputSelectFdList)
        else:
# This has to be a socket, just add the file descriptor.
          inputSelectFdList.append(fdHandlerObject.fileno())

# Loop over the list in reverse order to avoid skipping elements
# in remove.
      for logStream in reversed(blockedLogStreams):
        currentStreamFd = logStream.handleStream()
        if currentStreamFd >= 0:
          self.trackedFdsDict[currentStreamFd] = logStream
          inputSelectFdList.append(currentStreamFd)
          blockedLogStreams.remove(logStream)

      readList = None
      writeList = None
      exceptList = None
      try:
        (readList, writeList, exceptList) = select.select(
            inputSelectFdList, outputSelectFdList, [], 1)
      except select.error as selectError:
# Interrupting signals, e.g. for shutdown are OK.
        if selectError[0] == errno.EINTR:
          continue
        print('Unexpected select result %s' % str(selectError), file=sys.stderr)
        delayedReturnStatus = 1
        break
      for readFd in readList:
        fdHandlerObject = self.trackedFdsDict[readFd]
        if isinstance(fdHandlerObject, LogStream):
# Handle this LogStream. Only when downstream processing blocks,
# add the stream to the blocked stream list.
          handleResult = fdHandlerObject.handleStream()
          if handleResult < 0:
# No need to care if current internal file descriptor in LogStream
# has changed in handleStream(), this will be handled when unblocking.
            del self.trackedFdsDict[readFd]
            blockedLogStreams.append(fdHandlerObject)
          elif handleResult != readFd:
# The current fd has changed, update the tracking list.
            del self.trackedFdsDict[readFd]
            self.trackedFdsDict[handleResult] = fdHandlerObject
          continue

        if isinstance(fdHandlerObject, AnalysisChildRemoteControlHandler):
          try:
            fdHandlerObject.doReceive()
          except Exception as receiveException:
            print('Unclean termination of remote ' \
                'control: %s' % str(receiveException), file=sys.stderr)
          if fdHandlerObject.isDead():
            del self.trackedFdsDict[readFd]
# Reading is only attempted when output buffer was already flushed.
# Try processing the next request to fill the output buffer for
# next round.
          else:
            fdHandlerObject.doProcess(self.analysisContext)
          continue

        if fdHandlerObject == self.masterControlSocket:
          self.handleMasterControlSocketReceive()
          continue

        if fdHandlerObject == self.remoteControlSocket:
# We received a remote connection, accept it unconditionally.
# Users should make sure, that they do not exhaust resources by
# hogging open connections.
          (controlClientSocket, remoteAddress) = \
              self.remoteControlSocket.accept()
# Keep track of information received via this remote control socket.
          remoteControlHandler = AnalysisChildRemoteControlHandler(
              controlClientSocket)
          self.trackedFdsDict[controlClientSocket.fileno()] = remoteControlHandler
          continue
        raise Exception('Unhandled object type %s' % type(fdHandlerObject))

      for writeFd in writeList:
        fdHandlerObject = self.trackedFdsDict[writeFd]
        if isinstance(fdHandlerObject, AnalysisChildRemoteControlHandler):
          bufferFlushedFlag = False
          try:
            bufferFlushedFlag = fdHandlerObject.doSend()
          except OSError as sendError:
            print('Error sending data via remote ' \
                'control: %s' % str(sendError), file=sys.stderr)
            try:
              fdHandlerObject.terminate()
            except Exception as terminateException:
              print('Unclean termination of remote ' \
                  'control: %s' % str(terminateException), file=sys.stderr)
          if bufferFlushedFlag:
            fdHandlerObject.doProcess(self.analysisContext)
          if fdHandlerObject.isDead():
            del self.trackedFdsDict[writeFd]
          continue
        raise Exception('Unhandled object type %s' % type(fdHandlerObject))


# Handle the real time events.
      realTime = time.time()
      if nextRealTimeTriggerTime is None or realTime >= nextRealTimeTriggerTime:
        nextTriggerOffset = 3600
        for component in realTimeTriggeredComponents:
          nextTriggerRequest = component.doTimer(realTime)
          nextTriggerOffset = min(nextTriggerOffset, nextTriggerRequest)
        nextRealTimeTriggerTime = realTime+nextTriggerOffset

# Handle the analysis time events. The analysis time will be different
# when an analysis time component is registered.
      analysisTime = self.analysisContext.analysisTime
      if analysisTime is None:
        analysisTime = realTime
      if nextAnalysisTimeTriggerTime is None or analysisTime >= nextAnalysisTimeTriggerTime:
        nextTriggerOffset = 3600
        for component in analysisTimeTriggeredComponents:
          nextTriggerRequest = component.doTimer(realTime)
          nextTriggerOffset = min(nextTriggerOffset, nextTriggerRequest)
        nextAnalysisTimeTriggerTime = analysisTime+nextTriggerOffset

# Analysis loop is only left on shutdown. Try to persist everything
# and leave.
    PersistencyUtil.persistAll()
    return delayedReturnStatus

  def handleMasterControlSocketReceive(self):
    """Receive information from the parent process via the master
    control socket. This method may only be invoked when receiving
    is guaranteed to be nonblocking and to return data."""

# We cannot fail with None here as the socket was in the readList.
    (receivedFd, receivedTypeInfo, annotationData) = \
        SecureOSFunctions.receiveAnnotedFileDescriptor(self.masterControlSocket)
    if receivedTypeInfo == b'logstream':
      repositioningData = self.repositioningDataDict.get(annotationData, None)
      if repositioningData != None:
        del self.repositioningDataDict[annotationData]
      resource = None
      if annotationData.startswith(b'file://'):
        from aminer.input.LogStream import FileLogDataResource
        resource = FileLogDataResource(annotationData, receivedFd, \
            repositioningData=repositioningData)
      elif annotationData.startswith(b'unix://'):
        from aminer.input.LogStream import UnixSocketLogDataResource
        resource = UnixSocketLogDataResource(annotationData, receivedFd)
      else:
        raise Exception('Filedescriptor of unknown type received')
# Make fd nonblocking.
      fdFlags = fcntl.fcntl(resource.getFileDescriptor(), fcntl.F_GETFL)
      fcntl.fcntl(resource.getFileDescriptor(), fcntl.F_SETFL, fdFlags|os.O_NONBLOCK)
      logStream = self.logStreamsByName.get(resource.getResourceName())
      if logStream is None:
        streamAtomizer = self.analysisContext.atomizerFactory.getAtomizerForResource(
            resource.getResourceName())
        logStream = LogStream(resource, streamAtomizer)
        self.trackedFdsDict[resource.getFileDescriptor()] = logStream
        self.logStreamsByName[resource.getResourceName()] = logStream
      else:
        logStream.addNextResource(resource)
    elif receivedTypeInfo == b'remotecontrol':
      if self.remoteControlSocket != None:
        raise Exception('Received another remote control ' \
            'socket: multiple remote control not (yet?) supported.')
      self.remoteControlSocket = socket.fromfd(
          receivedFd, socket.AF_UNIX, socket.SOCK_STREAM, 0)
      os.close(receivedFd)
      self.trackedFdsDict[self.remoteControlSocket.fileno()] = \
          self.remoteControlSocket
    else:
      raise Exception('Unhandled type info on received fd: %s' % (
          repr(receivedTypeInfo)))


  def getTimeTriggerClass(self):
    """Get the trigger class this component can be registered
    for. See AnalysisContext class for different trigger classes
    available."""
    return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

  def doTimer(self, triggerTime):
    """This method is called to perform trigger actions and to
    determine the time for next invocation. The caller may decide
    to invoke this method earlier than requested during the previous
    call. Classes implementing this method have to handle such
    cases. Each class should try to limit the time spent in this
    method as it might delay trigger signals to other components.
    For extensive compuational work or IO, a separate thread should
    be used.
    @param triggerTime the time this trigger is invoked. This
    might be the current real time when invoked from real time
    timers or the forensic log timescale time value.
    @return the number of seconds when next invocation of this
    trigger is required."""
    delta = self.nextPersistTime-triggerTime
    if delta <= 0:
      self.repositioningDataDict = {}
      for logStreamName, logStream in self.logStreamsByName.items():
        repositioningData = logStream.getRepositioningData()
        if repositioningData != None:
          self.repositioningDataDict[logStreamName] = repositioningData
      PersistencyUtil.storeJson(
          self.persistenceFileName, self.repositioningDataDict)
      delta = 600
      self.nextPersistTime = triggerTime+delta
    return delta


class AnalysisChildRemoteControlHandler(object):
  """This class stores information about one open remote control
  connection. The handler can be in 3 different states:
  * receive request: the control request was not completely received.
    The main process may use select() to wait for input data without
    blocking or polling.
  * execute: the request is complete and is currently under execution.
    In that mode all other aminer analysis activity is blocked.
  * respond: send back results from execution.

  All sent and received control packets have following common
  structure:
  * Total length in bytes (4 bytes): The maximal length is currently
    limited to 64k
  * Type code (4 bytes)
  * Data

  The handler processes following types:
  * Execute request ('EEEE'): Data is loaded as json artefact
    containing a list with two elements. The first one is the
    Python code to be executed. The second one is available within
    the execution namespace as 'remoteControlData'.

  The handler produces following requests:
  * Execution response ('RRRR'): The response contains a json
    artefact with a two element list. The first element is the
    content of 'remoteControlResponse' from the Python execution
    namespace. The second one is the exception message and traceback
    as string if an error has occured.

  Method naming:
  * do...(): Those methods perform an action consuming input or
    output buffer data.
  * may...(): Those methods return true if it would make sense
    to call a do...() method with the same name.
  * put...(): Those methods put a request on the buffers."""

  maxControlPacketSize = 1 << 16

  def __init__(self, controlClientSocket):
    self.controlClientSocket = controlClientSocket
    self.remoteControlFd = controlClientSocket.fileno()
    self.inputBuffer = b''
    self.outputBuffer = b''

  def mayReceive(self):
    """Check if this handler may receive more requests."""
    return len(self.outputBuffer) == 0

  def doProcess(self, analysisContext):
    """Process the next request, if any."""
    requestData = self.doGet()
    if requestData is None:
      return
    requestType = requestData[4:8]
    if requestType == b'EEEE':
      jsonRemoteControlResponse = None
      exceptionData = None
      try:
        jsonRequestData = (json.loads(requestData[8:].decode()))
        jsonRequestData = JsonUtil.decodeObject(jsonRequestData)
        if (jsonRequestData is None) or \
            (not isinstance(jsonRequestData, list)) or \
            (len(jsonRequestData) != 2):
          raise Exception('Invalid request data')
        methods = AMinerRemoteControlExecutionMethods()
        execLocals = {'analysisContext':analysisContext, 'remoteControlData':jsonRequestData[1], 
                      'print':print, 'printResponse':methods.printResponse, 'dir':dir, 'methods':methods,
                      'changeConfigProperty':methods.changeConfigProperty}
        exec(jsonRequestData[0], {'__builtins__' : None}, execLocals)
        exec("print(dir())", {'__builtins__' : None}, execLocals)
        jsonRemoteControlResponse = json.dumps(
            execLocals.get('remoteControlResponse', None))
        if (methods.REMOTE_CONTROL_RESPONSE == ''):
          methods.REMOTE_CONTROL_RESPONSE = None
        if execLocals.get('remoteControlResponse', None) is None:
          jsonRemoteControlResponse = json.dumps(methods.REMOTE_CONTROL_RESPONSE)
        else:
          jsonRemoteControlResponse = json.dumps(execLocals.get('remoteControlResponse', None) + methods.REMOTE_CONTROL_RESPONSE)
      except:
        exceptionData = traceback.format_exc()
# This is little dirty but avoids having to pass over remoteControlResponse
# dumping again.
      if jsonRemoteControlResponse is None:
        jsonRemoteControlResponse = 'null'
      jsonResponse = '[%s, %s]' % (json.dumps(exceptionData), jsonRemoteControlResponse)
      if len(jsonResponse)+8 > self.maxControlPacketSize:
# Damn: the response would be larger than packet size. Fake a
# secondary exception and return part of the json string included.
# Binary search of size could be more efficient, knowing the maximal
# size increase a string could have in json.
        maxIncludeSize = len(jsonResponse)
        minIncludeSize = 0
        minIncludeResponseData = None
        while True:
          testSize = (maxIncludeSize+minIncludeSize) >> 1
          if testSize == minIncludeSize:
            break
          emergencyResponseData = json.dumps(['Exception: Response ' \
              'too large\nPartial response data: %s...' % jsonResponse[:testSize], None])
          if len(emergencyResponseData)+8 > self.maxControlPacketSize:
            maxIncludeSize = testSize-1
          else:
            minIncludeSize = testSize
            minIncludeResponseData = emergencyResponseData
        jsonResponse = minIncludeResponseData
# Now size is OK, send the data
      jsonResponse = jsonResponse.encode()
      self.outputBuffer += struct.pack("!I", len(jsonResponse)+8)+b'RRRR'+jsonResponse
    else:
      raise Exception('Invalid request type %s' % repr(requestType))

  def mayGet(self):
    """Check if a call to doGet would make sense.
    @return True if the input buffer already contains a complete
    wellformed packet or definitely malformed one."""
    if len(self.inputBuffer) < 4:
      return False
    requestLength = struct.unpack("!I", self.inputBuffer[:4])[0]
    return (requestLength <= len(self.inputBuffer)) or \
        (requestLength >= self.maxControlPacketSize)

  def doGet(self):
    """Get the next packet from the input buffer and remove it.
    @return the packet data including the length preamble or None
    when request not yet complete."""
    if len(self.inputBuffer) < 4:
      return None
    requestLength = struct.unpack("!I", self.inputBuffer[:4])[0]
    if (requestLength < 0) or (requestLength >= self.maxControlPacketSize):
      raise Exception('Invalid length value 0x%x in malformed ' \
          'request starting with b64:%s' % (requestLength, base64.b64encode(self.inputBuffer[:60])))
    if requestLength > len(self.inputBuffer):
      return None
    requestData = self.inputBuffer[:requestLength]
    self.inputBuffer = self.inputBuffer[requestLength:]
    return requestData

  def doReceive(self):
    """Receive data from the remote side and add it to the input
    buffer. This method call expects to read at least one byte
    of data. A zero byte read indicates EOF and will cause normal
    handler termination when all input and output buffers are
    empty. Any other state or error causes handler termination
    before reporting the error.
    @return True if read was successful, false if EOF is reached
    without reading any data and all buffers are empty.
    @throws Exception when unexpected errors occured while receiving
    or shuting down the connection."""
    data = os.read(self.remoteControlFd, 1 << 16)
    self.inputBuffer += data
    if not data:
      self.terminate()

  def doSend(self):
    """Send data from the output buffer to the remote side.
    @return True if output buffer was emptied."""
    sendLength = os.write(self.remoteControlFd, self.outputBuffer)
    if sendLength == len(self.outputBuffer):
      self.outputBuffer = b''
      return True
    self.outputBuffer = self.outputBuffer[sendLength:]
    return False

  def putRequest(self, requestType, requestData):
    """Add a request of given type to the send queue.
    @param requestType is a byte string denoting the type of the
    request. Currently only 'EEEE' is supported.
    @param requestData is a byte string denoting the content of
    the request."""
    if not isinstance(requestType, bytes):
      raise Exception('Request type is not a byte string')
    if len(requestType) != 4:
      raise Exception('Request type has to be 4 bytes long')
    if not isinstance(requestData, bytes):
      raise Exception('Request data is not a byte string')
    if len(requestData)+8 > self.maxControlPacketSize:
      raise Exception('Data too large to fit into single packet')
    self.outputBuffer += struct.pack("!I", len(requestData)+8)+requestType+requestData

  def putExecuteRequest(self, remoteControlCode, remoteControlData):
    """Add a request to send exception data to the send queue."""
    remoteControlData = json.dumps([JsonUtil.encodeObject(remoteControlCode), \
            JsonUtil.encodeObject(remoteControlData)])
    self.putRequest(b'EEEE', remoteControlData.encode())

  def addSelectFds(self, inputSelectFdList, outputSelectFdList):
    """Update the file descriptor lists for selecting on read
    and write file descriptors."""
    if self.outputBuffer:
      outputSelectFdList.append(self.remoteControlFd)
    else:
      inputSelectFdList.append(self.remoteControlFd)

  def terminate(self):
    """End this remote control session."""
    self.controlClientSocket.close()
# Avoid accidential reuse.
    self.controlClientSocket = None
    self.remoteControlFd = -1
    if self.inputBuffer or self.outputBuffer:
      raise Exception('Unhandled input data')

  def isDead(self):
    """Check if this remote control connection is already dead."""
    return self.remoteControlFd == -1
