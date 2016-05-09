import io
import os
import syslog

from aminer.events import StreamPrinterEventHandler

class SyslogWriterEventHandler:
  """This class implements an event record listener to forward
  events to the local syslog instance.
  CAVEAT: USE THIS AT YOUR OWN RISK: by creating aminer/syslog
  log data processing loops, you will flood your syslog and probably
  fill up your disks."""
  def __init__(self, aminerConfig, instanceName='aminer'):
    self.instanceName=instanceName
    syslog.openlog('%s[%d]' % (self.instanceName, os.getpid()),
        syslog.LOG_INFO, syslog.LOG_DAEMON)
    syslog.syslog(syslog.LOG_INFO, 'SDS logger initialized')
    self.bufferStream=io.BytesIO()
    self.eventWriter=StreamPrinterEventHandler.StreamPrinterEventHandler(
        None, self.bufferStream)
    self.eventId=0

  def receiveEvent(self, eventType, eventMessage, sortedLogLines, eventData):
    """Receive information about a detected even and forward it
    to syslog."""
    self.bufferStream.seek(0)
    self.bufferStream.truncate(0)
    self.eventWriter.receiveEvent(eventType, eventMessage, sortedLogLines,
        eventData)
    eventData=self.bufferStream.getvalue()
    currentEventId=self.eventId
    self.eventId+=1
    serial=0
    for dataLine in eventData.strip().split('\n'):
# Python syslog is very ugly if lines are too long, so break them
# down.
      while len(dataLine)!=0:
        message=None
        if serial==0:
          message='[%d] %s' % (currentEventId, dataLine[:800])
        else:
          message='[%d-%d] %s' % (currentEventId, serial, dataLine[:800])
        dataLine=dataLine[800:]
        syslog.syslog(syslog.LOG_INFO, message)
        serial+=1
