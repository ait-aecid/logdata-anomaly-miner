import base64
import fcntl
import json
import os
import select
import socket
import struct
import sys
import time
import traceback

from aminer import AMinerUtils
from aminer.input import LogStream
from aminer.input import ByteLineReader


class AnalysisChild:
  """This class defines the child performing the complete analysis
  workflow. When splitting privileges between analysis and monitor
  process, this class should only be initialized within the analysis
  process!"""

  def __init__(self, programName, aminerConfig):
    self.programName=programName
    self.analysisContext=AMinerUtils.AnalysisContext(aminerConfig)

# Override the signal handler to allow graceful shutdown.
    def gracefulShutdownHandler(_signo, _stackFrame):
      print >>sys.stderr, '%s: caught signal, shutting down' % programName
      from aminer.util import PersistencyUtil
      PersistencyUtil.persistAll()
      sys.exit(0)
    import signal
    signal.signal(signal.SIGHUP, gracefulShutdownHandler)
    signal.signal(signal.SIGINT, gracefulShutdownHandler)
    signal.signal(signal.SIGTERM, gracefulShutdownHandler)


  def runAnalysis(self, masterFd):
    """This method runs the analysis thread.
    @param masterFd the main communication socket to the parent
    to receive logfile updates from the parent."""

# The masterControlSocket is the socket to communicate with the
# master process to receive commands or logstream data. Expect
# the parent/child communication socket on fd 3. This also duplicates
# the fd, so close the old one.
    masterControlSocket=socket.fromfd(masterFd, socket.AF_UNIX, socket.SOCK_DGRAM, 0)
    os.close(masterFd)

# Locate the real analysis configuration.
    self.analysisContext.buildAnalysisPipeline()
    rawAtomHandlers=self.analysisContext.rawAtomHandlers
    timeTriggeredHandlers=self.analysisContext.timeTriggeredHandlers

    logStreams=[]
    logStreamsByName={}
    remoteControlSocket=None
    childSocketSelectList=[masterControlSocket.fileno(),]

    nextListenerTriggerTime=time.time()

# The number of lines read during the last pass over all log data
# streams. Start with -1 to make first round of select return
# immediately.
    lastReadLines=-1

    while True:
      if lastReadLines==0:
        (readList, writeList, exceptList)=select.select(childSocketSelectList, [], [], 1)
      else:
        (readList, writeList, exceptList)=select.select(childSocketSelectList, [], [], 0)
      for readFd in readList:
        if readFd==masterControlSocket.fileno():
# We cannot fail with None here as the socket was in the readList.
          (receivedFd, receivedTypeInfo, annotationData)=AMinerUtils.receiveAnnotedFileDescriptor(masterControlSocket)
          if 'logstream'==receivedTypeInfo:
            resource=AMinerUtils.LogDataResource(annotationData, receivedFd)
# Make fd nonblocking
            fdFlags=fcntl.fcntl(resource.logFileFd, fcntl.F_GETFL)
            fcntl.fcntl(resource.logFileFd, fcntl.F_SETFL, fdFlags|os.O_NONBLOCK)
            logStream=logStreamsByName.get(resource.logFileName)
            if logStream==None:
              logStream=LogStream(resource)
              logStreams.append(logStream)
              logStreamsByName[resource.logFileName]=logStream
            else:
              logStream.rollOver(resource)
          elif 'remotecontrol'==receivedTypeInfo:
            if remoteControlSocket!=None:
              raise Exception('Received another remote control socket: multiple remote control not (yet?) supported.')
            remoteControlSocket=socket.fromfd(receivedFd, socket.AF_UNIX,
                socket.SOCK_STREAM, 0)
            os.close(receivedFd)
            childSocketSelectList.append(remoteControlSocket.fileno())
          else:
            raise Exception('Unhandled type info on received fd: %s' %
                repr(receivedTypeInfo))
          continue
        elif readFd==remoteControlSocket.fileno():
# Remote we received an connection, accept it.
          (controlClientSocket, remoteAddress)=remoteControlSocket.accept()
# Keep track of information received via this remote control socket.
          remoteControlHandler=AnalysisChildRemoteControlHandler(controlClientSocket.fileno())

# FIXME: Here we should enter asynchronous read mode as described
# in the header of AnalysisChildRemoteControlHandler. At the moment
# everything is done within the thread. Make sure to continue
# in blocking mode.
          controlClientSocket.setblocking(1)
          while True:
            while remoteControlHandler.maySend():
              remoteControlHandler.doSend()
            if remoteControlHandler.mayProcess():
              remoteControlHandler.doProcess(self.analysisContext)
              continue
            if not(remoteControlHandler.doReceive()): break
          try:
            remoteControlHandler.terminate()
          except Exception as terminateException:
            print >>sys.stderr, 'Unclear termination of remote control: %s' % str(terminateException)
# This is quite useless, the file descriptor was closed already.
# by terminate. But call just anything to keep garbage collection
# from closing and freeing the socket too early.
          controlClientSocket.close()
          continue
        raise Exception('Illegal state reached')

      if time.time()>=nextListenerTriggerTime:
        nextTriggerOffset=3600
        for handler in timeTriggeredHandlers:
          nextTriggerRequest=handler.checkTriggers()
          nextTriggerOffset=min(nextTriggerOffset, nextTriggerRequest)
        nextListenerTriggerTime=time.time()+nextTriggerOffset

      lastReadLines=0

      for logStream in logStreams:
# FIXME: no message read synchronization beween multiple fds,
# see Readme.txt (Multiple file synchronization)
        for logLine in range(0, 1000):
          lineData=logStream.readLine()
          if lineData==None:
            if logStream.byteLineReader.isEndOfStream():
              logStreams.remove(logStream)
              logStreamsByName.remove(logStream.logDataResource.logFileName)
            break

          lastReadLines+=1
          for handler in rawAtomHandlers:
            handler.receiveAtom(lineData)


class AnalysisChildRemoteControlHandler:
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

  maxControlPacketSize=1<<16

  def __init__(self, remoteControlFd):
    self.remoteControlFd=remoteControlFd
    self.inputBuffer=''
    self.outputBuffer=''

  def mayReceive(self):
    """Check if this handler may receive more requests."""
    return(len(self.outputBuffer)==0)

  def maySend(self):
    return(len(self.outputBuffer)!=0)

  def mayProcess(self):
    """Check if this handler has sufficient data to process the
    action described in the input buffer."""
    if len(self.inputBuffer)<8: return(False)
    requestLength=struct.unpack("!I", self.inputBuffer[:4])[0]
# If length value is malformed, still return true. Handle all
# the malformed packet stuff in the execute functions.
    if (requestLength<0) or (requestLength>=self.maxControlPacketSize):
      return(True)
    return(requestLength<=len(self.inputBuffer))

  def doProcess(self, analysisContext):
    requestData=self.doGet()
    requestType=requestData[4:8]
    if requestType=='EEEE':
      execLocals={'analysisContext': analysisContext}
      jsonRemoteControlResponse=None
      exceptionData=None
      try:
        jsonRequestData=json.loads(requestData[8:])
        if (jsonRequestData==None) or (not isinstance(jsonRequestData, list)) or (len(jsonRequestData)!=2):
          raise Exception('Invalid request data')
        execLocals['remoteControlData']=jsonRequestData[1]
        exec(jsonRequestData[0], {}, execLocals)
        jsonRemoteControlResponse=json.dumps(execLocals.get('remoteControlResponse', None))
      except:
        exceptionData=traceback.format_exc()
# This is little dirty but avoids having to pass over remoteControlResponse
# dumping again.
      if jsonRemoteControlResponse==None: jsonRemoteControlResponse='null'
      jsonResponse='[%s, %s]' % (json.dumps(exceptionData), jsonRemoteControlResponse)
      if len(jsonResponse)+8>self.maxControlPacketSize:
# Damn: the response would be larger than packet size. Fake a
# secondary exception and return part of the json string included.
# Binary search of size could be more efficient, knowing the maximal
# size increase a string could have in json.
        maxIncludeSize=len(jsonResponse)
        minIncludeSize=0
        minIncludeResponseData=None
        while True:
          testSize=(maxIncludeSize+minIncludeSize)>>1
          if testSize==minIncludeSize: break
          emergencyResponseData=json.dumps(['Exception: Response too large\nPartial response data: %s...' % jsonResponse[:testSize], None])
          if len(emergencyResponseData)+8>self.maxControlPacketSize:
            maxIncludeSize=testSize-1
          else:
            minIncludeSize=testSize
            minIncludeResponseData=emergencyResponseData
        jsonResponse=minIncludeResponseData
# Now size is OK, send the data
      self.outputBuffer+=struct.pack("!I", len(jsonResponse)+8)+'RRRR'+jsonResponse
    else:
      raise Exception('Invalid request type %s' % repr(requestType))

  def doGet(self):
    """Get the next packet from the input and remove it.
    @return the packet data."""
    requestLength=struct.unpack("!I", self.inputBuffer[:4])[0]
    if (requestLength<0) or (requestLength>=self.maxControlPacketSize):
      raise Exception('Invalid length value 0x%x in malformed request starting with b64:%s' % (requestLength, base64.b64encode(self.inputBuffer[:60])))
    requestData=self.inputBuffer[:requestLength]
    self.inputBuffer=self.inputBuffer[requestLength:]
    return(requestData)

  def doReceive(self):
    """Receive data from the remote side and add it to the input
    buffer. This method call expects to read at least one byte
    of data. A zero byte read indicates EOF.
    @return true if read was successful, false if EOF is reached
    without reading any data."""
    data=os.read(self.remoteControlFd, 1<<16)
    self.inputBuffer+=data
    return(len(data)!=0)

  def doSend(self):
    os.write(self.remoteControlFd, self.outputBuffer)
    self.outputBuffer=''


  def putRequest(self, requestType, requestData):
    if len(requestType)!=4: raise Exception('Request type has to be 4 bytes long')
    if len(requestData)+8>self.maxControlPacketSize:
      raise Exception('Data too large to fit into single packet')
    self.outputBuffer+=struct.pack("!I", len(requestData)+8)+requestType+requestData
    
  def putExecuteRequest(self, remoteControlCode, remoteControlData):
    remoteControlData=json.dumps([remoteControlCode, remoteControlData])
    self.putRequest('EEEE', remoteControlData)

  def terminate(self):
    os.close(self.remoteControlFd)
# Avoid accidential reuse.
    self.remoteControlFd=-1
    if (len(self.inputBuffer)!=0) or (len(self.outputBuffer)!=0):
      raise Exception('Unhandled input data')
