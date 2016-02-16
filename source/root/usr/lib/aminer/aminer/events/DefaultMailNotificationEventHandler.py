import email
import os
import subprocess
import sys
import time

from aminer.parsing import ParserMatch


configKeyMailAlertingTargetAddress='MailAlerting.TargetAddress'
configKeyMailAlertingFromAddress='MailAlerting.FromAddress'
configKeyMailAlertingSubjectPrefix='MailAlerting.SubjectPrefix'
configKeyMailAlertingAlertGraceTime='MailAlerting.AlertGraceTime'
configKeyMailAlertingEventCollectTime='MailAlerting.EventCollectTime'
configKeyMailAlertingMinAlertGap='MailAlerting.MinAlertGap'
configKeyMailAlertingMaxAlertGap='MailAlerting.MaxAlertGap'
configKeyMailAlertingMaxEventsPerMessage='MailAlerting.MaxEventsPerMessage'


class DefaultMailNotificationEventListener:
  """This class implements an event record listener, that will pool
received events, reduce the amount of events below the maximum
number allowed per timeframe, create text representation of received
events and send them via "sendmail" transport."""
  def __init__(self, aminerConfig):
    self.recipientAddress=aminerConfig.configProperties.get(configKeyMailAlertingTargetAddress)
    if self.recipientAddress==None:
      raise Error('Cannot create e-mail notification listener without target address')

    self.senderAddress=aminerConfig.configProperties.get(configKeyMailAlertingFromAddress)
    self.subjectPrefix=aminerConfig.configProperties.get(configKeyMailAlertingSubjectPrefix, 'AMiner Alerts:')
    self.alertGraceTimeEnd=aminerConfig.configProperties.get(configKeyMailAlertingAlertGraceTime, 0)
    self.eventCollectTime=aminerConfig.configProperties.get(configKeyMailAlertingEventCollectTime, 10)
    self.minAlertGap=aminerConfig.configProperties.get(configKeyMailAlertingMinAlertGap, 600)
    self.maxAlertGap=aminerConfig.configProperties.get(configKeyMailAlertingMaxAlertGap, 600)
    self.maxEventsPerMessage=aminerConfig.configProperties.get(configKeyMailAlertingMaxEventsPerMessage, 1000)
    if self.alertGraceTimeEnd>0:
      self.alertGraceTimeEnd+=time.time()
    self.eventsCollected=0
    self.eventCollectionStartTime=0
    self.lastAlertTime=0
    self.nextAlertTime=0
    self.currentAlertGap=self.minAlertGap
    self.currentMessage=''

# Locate the sendmail binary immediately at startup to avoid delayed
# errors due to misconfiguration.
    print >>sys.stderr, 'FIXME: no sendmail locating yet'
    self.sendmailBinaryPath='/usr/sbin/sendmail'
    self.runningSendmailProcesses=[]


  def receiveEvent(self, eventType, eventMessage, sortedLogLines, eventData):
    """Receive information about a detected event."""
    if self.alertGraceTimeEnd!=0:
      if self.alertGraceTimeEnd>=time.time(): return()
      self.alertGraceTimeEnd=0

# Avoid too many calls to the operating system time()
    currentTime=time.time()

    if (self.eventsCollected<self.maxEventsPerMessage):
      if self.eventsCollected==0:
        self.eventCollectionStartTime=currentTime
      self.eventsCollected+=1
      self.currentMessage+='%s (%d lines)\n' % (eventMessage, len(sortedLogLines))
      for line in sortedLogLines:
        self.currentMessage+='  '+line+'\n'
      if eventData!=None:
        if isinstance(eventData, ParserMatch.ParserMatch):
          self.currentMessage+='  '+eventData.getMatchElement().annotateMatch('')+'\n'
        else:
          self.currentMessage+='  '+str(eventData)+'\n'

    if self.nextAlertTime==0:
      if self.lastAlertTime!=0:
# This is the first event received after sending of a previous
# notification. If the currentAlertGap has not elapsed, increase
# the gap immediately.
        self.nextAlertTime=self.lastAlertTime+self.currentAlertGap
        if self.nextAlertTime<currentTime:
# We are already out of the required gap.
          self.currentAlertGap=self.minAlertGap
          self.lastAlertTime=0
          self.nextAlertTime=currentTime+self.eventCollectTime
        else:
# Increase the gap
         self.currentAlertGap+=1.5
         if self.currentAlertGap>self.maxAlertGap:
           self.currentAlertGap=self.maxAlertGap
      else:
# No relevant last alert time recorded, just use default.
        self.nextAlertTime=currentTime+self.eventCollectTime

    if (self.nextAlertTime!=0) and (currentTime>=self.nextAlertTime):
      self.sendNotification()
    return


  def checkTriggers(self):
    """Check if alerts should be sent."""
    if (self.nextAlertTime!=0) and (time.time()>=self.nextAlertTime):
      self.sendNotification()
    return(10)


  def sendNotification(self):
    """Really send out the message."""
    print >>sys.stderr, 'Got send notification'
    if len(self.runningSendmailProcesses)!=0:
      runningProcesses=[]
      for process in self.runningSendmailProcesses:
        if process.returncode==None:
          runningProcesses.append(process)
          continue
        if process.returncode!=0:
          print >>sys.stderr, 'Sending mail terminated with error %d' % process.returncode
      self.runningSendmailProcesses=runningProcesses

    if self.eventsCollected==0: return()

# Write whole message to file to allow sendmail send it asynchronously.
    messageTmpFile=os.tmpfile()
    message=email.mime.Text.MIMEText(self.currentMessage)
    subjectText='%s Collected Events' % self.subjectPrefix
    if self.lastAlertTime != 0:
      subjectText+=' in the last %d seconds' % (time.time()-self.lastAlertTime)
    message['Subject']=subjectText
    if self.senderAddress!=None:
      message['From']=self.senderAddress
    message['To']=self.recipientAddress
    messageTmpFile.write(message.as_string())

# Rewind before handling over the fd to sendmail.
    messageTmpFile.seek(0)

    sendmailArgs=['sendmail']
    if self.senderAddress!=None:
      sendmailArgs+=['-f', self.senderAddress]
    sendmailArgs.append(self.recipientAddress)
# Start the sendmail process. Use close_fds to avoid leaking of
# any open file descriptors to the new client.
    process=subprocess.Popen(sendmailArgs, executable=self.sendmailBinaryPath, stdin=messageTmpFile, close_fds=True)
    self.runningSendmailProcesses.append(process)
    messageTmpFile.close()

    self.lastAlertTime=time.time()
    self.eventsCollected=0
    self.currentMessage=''
    self.nextAlertTime=0
