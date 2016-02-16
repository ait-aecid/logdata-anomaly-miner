# This is a template for the "aminer" logfile miner tool. Copy
# it to "config.py" and define your ruleset.

configProperties={}

# List of log files to read from:
configProperties['LogFileList']=['/home/rfiedler/cais-cluster/AECID/ProductionComponent/input.txt']

# Define the uid/gid of the process that runs the calculation
# after opening the log files:
# configProperties['AMinerUser']='aminer'
# configProperties['AMinerGroup']='aminer'

# Read the analyis from this file. That part of configuration
# is separated from the main configuration so that it can be loaded
# only within the analysis child. Non-absolute path names are
# interpreted relatively to the main configuration file (this
# file). Defaults to "analysis.py".
# configProperties['AnalysisConfigFile']='analysis.py'

# Define a target e-mail address to send alerts to. When undefined,
# no e-mail notification hooks are added.
configProperties['MailAlerting.TargetAddress']='root@localhost'
configProperties['MailAlerting.FromAddress']='root@localhost'
# Define, which text should be prepended to the standard aminer
# subject. Defaults to "AMiner Alerts:"
configProperties['MailAlerting.SubjectPrefix']='AMiner Alerts:'
# Define a grace time after startup before aminer will react to
# an event and send the first alert e-mail. Defaults to 0 (any
# event can immediately trigger alerting).
# configProperties['MailAlerting.AlertGraceTime']=0
# Define how many seconds to wait after a first event triggered
# the alerting procedure before really sending out the e-mail.
# In that timespan, events are collected and will be sent all
# using a single e-mail. Defaults to 10 seconds.
# configProperties['MailAlerting.EventCollectTime']=10
# Define the minimum time between two alert e-mails in seconds
# to avoid spamming. All events during this timespan are collected
# and sent out with the next report. Defaults to 600 seconds.
# configProperties['MailAlerting.MinAlertGap']=600
# Define the maximum time between two alert e-mails in seconds.
# When undefined this defaults to "MailAlerting.MinAlertGap".
# Otherwise this will activate an exponential backoff to reduce
# messages during permanent error states by increasing the alert
# gap by 50% when more alert-worthy events were recorded while
# the previous gap time was not yet elapsed.
# configProperties['MailAlerting.MaxAlertGap']=600
# Define how many events should be included in one alert mail
# at most. This defaults to 1000
# configProperties['MailAlerting.MaxEventsPerMessage']=1000


# Add your ruleset here:

# FIXME: Workaround for non-root installs
import sys
sys.path=sys.path+['/home/rfiedler/cais-cluster/AECID/ProductionComponent/source/root/usr/lib/aminer', '/home/rfiedler/cais-cluster/AECID/ProductionComponent/source/testing/config']

# Define a model for parsing the log data:
def parsingModel():
  import FirstMatchModelElement
  import SequenceModelElement

  serviceChildren=[]

  import AhitApacheParsingModel
  serviceChildren+=[AhitApacheParsingModel.getModel()]

  import ConfigSyslogPreambleModel
  syslogPreambleModel=ConfigSyslogPreambleModel.getModel()
  return(SequenceModelElement.SequenceModelElement('model', [syslogPreambleModel, FirstMatchModelElement.FirstMatchModelElement('services', serviceChildren)]))


# Get the list of listeners to listen:
def analysisEventListenersList(aminerConfig):
  analysisEventListeners=[]
# if aminerConfig.configProperties.has_key(DefaultMailNotificationEventListener.configKeyMailAlertingTargetAddress):
#   analysisEventListeners.append(DefaultMailNotificationEventListener.DefaultMailNotificationEventListener(aminerConfig))

  import StreamPrinterEventListener
  analysisEventListeners.append(StreamPrinterEventListener.StreamPrinterEventListener(aminerConfig))

  return(analysisEventListeners)
