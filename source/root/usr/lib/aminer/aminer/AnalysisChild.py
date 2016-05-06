import fcntl
import os
import select
import socket
import sys
import time

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
    self.aminerConfig=aminerConfig

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

# Expect the parent/child communication socket on fd 3. This also
# duplicates the fd, so close the old one.
    childSocket=socket.fromfd(masterFd, socket.AF_UNIX, socket.SOCK_DGRAM, 0)
    os.close(masterFd)

# Locate the real analysis configuration.
    (rawAtomHandlers, timeTriggeredHandlers)=self.aminerConfig.buildAnalysisPipeline(self.aminerConfig)

    logStreams=[]
    logStreamsByName={}
    childSocketSelectList=[childSocket.fileno(),]

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
        if readFd==childSocket.fileno():
# We cannot fail with None here as the childSocket was in the readList.
          (receivedFd, receivedTypeInfo, annotationData)=AMinerUtils.receiveAnnotedFileDescriptor(childSocket)
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
          else:
            raise Exception('Unhandled type info on received fd: %s' %
                repr(receivedTypeInfo))
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
