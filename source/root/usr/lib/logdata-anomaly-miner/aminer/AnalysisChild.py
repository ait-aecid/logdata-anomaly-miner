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

from aminer import AMinerConfig
from aminer import AMinerUtils
from aminer.input import LogDataResource
from aminer.input import LogStream
from aminer.util import PersistencyUtil


class AnalysisChild:
  """This class defines the child performing the complete analysis
  workflow. When splitting privileges between analysis and monitor
  process, this class should only be initialized within the analysis
  process!"""

  def __init__(self, programName, aminerConfig):
    self.programName=programName
    self.analysisContext=AMinerUtils.AnalysisContext(aminerConfig)
    self.runAnalysisLoopFlag=True

# Override the signal handler to allow graceful shutdown.
    def gracefulShutdownHandler(_signo, _stackFrame):
      print >>sys.stderr, '%s: caught signal, shutting down' % programName
      self.runAnalysisLoopFlag=False
    import signal
    signal.signal(signal.SIGHUP, gracefulShutdownHandler)
    signal.signal(signal.SIGINT, gracefulShutdownHandler)
    signal.signal(signal.SIGTERM, gracefulShutdownHandler)


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
    masterControlSocket=socket.fromfd(masterFd, socket.AF_UNIX, socket.SOCK_DGRAM, 0)
    os.close(masterFd)

# Locate the real analysis configuration.
    self.analysisContext.buildAnalysisPipeline()
    if self.analysisContext.atomizerFactory==None:
      print >>sys.stderr, 'FATAL: buildAnalysisPipeline() did not initialize atomizerFactory, terminating'
      return(1)

    realTimeTriggeredComponents=self.analysisContext.realTimeTriggeredComponents
    analysisTimeTriggeredComponents=self.analysisContext.analysisTimeTriggeredComponents

    logStreamsByName={}
# Load continuation data for last known log streams. The loaded
# data has to be a dictionary with repositioning information for
# each stream. The data is used only when creating the first stream
# with that name.
    persistenceFileName=AMinerConfig.buildPersistenceFileName(
        self.analysisContext.aminerConfig,
        self.__class__.__name__+'/RepositioningData')
    repositioningDataDict=PersistencyUtil.loadJson(persistenceFileName)
    if repositioningDataDict==None: repositioningDataDict={}

    remoteControlSocket=None
    childSocketSelectList=[masterControlSocket.fileno()]
# This list has the same number of elements as childSocketSelectList.
# For each select file descriptor from a logStream it keeps the
# logStream object at same position for quick reference.
    childSocketSelectStreams=[None]
# A list of LogStreams where handleStream() blocked due to downstream
# not being able to consume the data yet.
    blockedLogStreams=[]

# Every number is larger than None so using this starting value
# will cause the trigger to be invoked on the first event.
    nextRealTimeTriggerTime=None
    nextAnalysisTimeTriggerTime=None

    delayedReturnStatus=0
    while self.runAnalysisLoopFlag:
      readList=None
      writeList=None
      exceptList=None
      try:
        (readList, writeList, exceptList)=select.select(childSocketSelectList, [], [], 1)
      except select.error as selectError:
# Interrupting signals, e.g. for shutdown are OK.
        if selectError[0]==errno.EINTR: continue
        print >>sys.stderr, 'Unexpected select result %s' % str(selectError)
        delayedReturnStatus=1
        break
      if len(readList)==0:
# All reads failed. Unblock all blocked streams to retry those
# too.
        for logStream in blockedLogStreams:
          currentFd=logStream.getCurrentFd()
          if currentFd<0: continue
          childSocketSelectList.append(currentFd)
          childSocketSelectStreams.append(logStream)
          blockedLogStreams.remove(logStream)
          continue
      for readFd in readList:
        if readFd==masterControlSocket.fileno():
# We cannot fail with None here as the socket was in the readList.
          (receivedFd, receivedTypeInfo, annotationData)=AMinerUtils.receiveAnnotedFileDescriptor(masterControlSocket)
          if 'logstream'==receivedTypeInfo:
            repositioningData=repositioningDataDict.get(annotationData, None)
            if repositioningData!=None:
              del repositioningDataDict[annotationData]
            resource=LogDataResource(annotationData,
                receivedFd, repositioningData=repositioningData)
# Make fd nonblocking
            fdFlags=fcntl.fcntl(resource.logFileFd, fcntl.F_GETFL)
            fcntl.fcntl(resource.logFileFd, fcntl.F_SETFL, fdFlags|os.O_NONBLOCK)
            logStream=logStreamsByName.get(resource.logFileName)
            if logStream==None:
              streamAtomizer=self.analysisContext.atomizerFactory.getAtomizerForResource(resource.logFileName)
              logStream=LogStream(resource, streamAtomizer)
              logStreamsByName[resource.logFileName]=logStream
# Add the stream to the select list.
              childSocketSelectList.append(resource.logFileFd)
              childSocketSelectStreams.append(logStream)
            else:
              logStream.addNextResource(resource)
          elif 'remotecontrol'==receivedTypeInfo:
            if remoteControlSocket!=None:
              raise Exception('Received another remote control socket: multiple remote control not (yet?) supported.')
            remoteControlSocket=socket.fromfd(receivedFd, socket.AF_UNIX,
                socket.SOCK_STREAM, 0)
            os.close(receivedFd)
            childSocketSelectList.append(remoteControlSocket.fileno())
            childSocketSelectStreams.append(None)
          else:
            raise Exception('Unhandled type info on received fd: %s' %
                repr(receivedTypeInfo))
          continue

        if readFd==remoteControlSocket.fileno():
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

# This has to be a logStream, handle it. Only when downstream
# blocks, add the stream to the blocked stream list.
        streamPos=childSocketSelectList.index(readFd)
        logStream=childSocketSelectStreams[streamPos]
        handleResult=logStream.handleStream()
        if handleResult<0:
          del childSocketSelectList[streamPos]
          del childSocketSelectStreams[streamPos]
          blockedLogStreams.append(logStream)


# Handle the real time events.
      realTime=time.time()
      if realTime>=nextRealTimeTriggerTime:
        nextTriggerOffset=3600
        for component in realTimeTriggeredComponents:
          nextTriggerRequest=component.doTimer(realTime)
          nextTriggerOffset=min(nextTriggerOffset, nextTriggerRequest)
        nextRealTimeTriggerTime=realTime+nextTriggerOffset

# Handle the analysis time events. The analysis time will be different
# when an analysis time component is registered.
      analysisTime=self.analysisContext.analysisTime
      if analysisTime==None: analysisTime=realTime
      if analysisTime>=nextAnalysisTimeTriggerTime:
        nextTriggerOffset=3600
        for component in analysisTimeTriggeredComponents:
          nextTriggerRequest=component.doTimer(realTime)
          nextTriggerOffset=min(nextTriggerOffset, nextTriggerRequest)
        nextAnalysisTimeTriggerTime=analysisTime+nextTriggerOffset

# Analysis loop is only left on shutdown. Try to persist everything
# and leave.
    PersistencyUtil.persistAll()
    repositioningDataDict={}
    for logStreamName, logStream in logStreamsByName.iteritems():
      repositioningData=logStream.getRepositioningData()
      if repositioningData!=None:
        repositioningDataDict[logStreamName]=repositioningData
    PersistencyUtil.storeJson(persistenceFileName, repositioningDataDict)
    return(delayedReturnStatus)


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
