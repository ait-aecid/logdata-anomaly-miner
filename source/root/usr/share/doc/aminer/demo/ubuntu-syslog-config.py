# This demo creates an analysis pipeline to parse typical Ubuntu
# server logs.
#
# DO NOT USE THIS TO RUN PRODUCTION ANALYSIS PIPELINE AS IT CONTAINS
# SETTINGS FOR TESTING, THAT MAY IMPEDE SECURITY AND PERFORMANCE!
# THOSE CHANGES ARE MARKED WITH "DEMO" TO AVOID ACCIDENTAL USE!

configProperties={}

# Define the list of log files to read from: the files named here
# do not need to exist when aminer is started. This will just
# result in a warning. However if they exist, they have to be
# readable by the aminer process!
# DEMO: FORBIDDEN RELATIVE PATH!
configProperties['LogFileList']=['test.log']

# Define the uid/gid of the process that runs the calculation
# after opening the log files:
# DEMO: PRIVILEGE SEPARATION DISABLED!
# configProperties['AMinerUser']='aminer'
# configProperties['AMinerGroup']='aminer'

# Define the path, where aminer will listen for incoming remote
# control connections. When missing, no remote control socket
# will be created.
# configProperties['RemoteControlSocket']='/var/run/aminer-remote.socket'

# Read the analyis from this file. That part of configuration
# is separated from the main configuration so that it can be loaded
# only within the analysis child. Non-absolute path names are
# interpreted relatively to the main configuration file (this
# file). Defaults to "analysis.py".
# configProperties['AnalysisConfigFile']='analysis.py'

# Read and store information to be used between multiple invocations
# of AMiner in this directory. The directory must only be accessible
# to the 'AMinerUser' but not group/world readable. On violation,
# AMiner will refuse to start. When undefined, '/var/lib/aminer'
# is used.
# DEMO: FORBIDDEN RELATIVE PATH!
configProperties['Core.PersistenceDir']='aminer'

# Define a target e-mail address to send alerts to. When undefined,
# no e-mail notification hooks are added.
# configProperties['MailAlerting.TargetAddress']='root@localhost'
# Sender address of e-mail alerts. When undefined, "sendmail"
# implementation on host will decide, which sender address should
# be used.
# configProperties['MailAlerting.FromAddress']='root@localhost'
# Define, which text should be prepended to the standard aminer
# subject. Defaults to "AMiner Alerts:"
# configProperties['MailAlerting.SubjectPrefix']='AMiner Alerts:'
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

# DEMO: INCLUSION OF ALL AMINER ELEMENTS AND ALL PYTHON SITE PACKAGES
# NOT RECOMMENDED!
import sys
sys.path=sys.path+['/etc/aminer/conf-available/generic', '/usr/lib/python2.7/dist-packages']

# DEMO: DISABLE SECURE OPEN TO ALLOW RELATIVE PATH, SYMLINKS!
import os
def insecureDemoOpen(fileName, flags):
  return(os.open(fileName, flags|os.O_NOCTTY))
from aminer import AMinerUtils
AMinerUtils.secureOpenFile=insecureDemoOpen


# Add your ruleset here:

# Define the function to create pipeline for parsing the log data.
# It has also to define an AtomizerFactory to instruct AMiner
# how to process incoming data streams to create log atoms from
# them.
def buildAnalysisPipeline(analysisContext):
# Build the parsing model first
  from aminer.parsing import FirstMatchModelElement
  from aminer.parsing import SequenceModelElement

  serviceChildren=[]

  import CronParsingModel
  serviceChildren.append(CronParsingModel.getModel())

  import EximParsingModel
  serviceChildren.append(EximParsingModel.getModel())

  import RsyslogParsingModel
  serviceChildren.append(RsyslogParsingModel.getModel())

  import SyslogPreambleModel
  syslogPreambleModel=SyslogPreambleModel.getModel()

  parsingModel=SequenceModelElement('model', [
      syslogPreambleModel,
      FirstMatchModelElement('services', serviceChildren)])


# Create all global handler lists here and append the real handlers
# later on.
# Use this filter to distribute all atoms to the analysis handlers.
  atomFilter=AtomFilters.SubhandlerFilter(None)
  anomalyEventHandlers=[]

# Now define the AtomizerFactory using the model. A simple line
# based one is usually sufficient.
  from aminer.input import SimpleByteStreamLineAtomizerFactory
  analysisContext.atomizerFactory=SimpleByteStreamLineAtomizerFactory(
      parsingModel, [atomFilter], anomalyEventHandlers,
      defaultTimestampPath='/model/syslog/time')

# Always report the unparsed lines: a part of the parsing model
# seems to be missing or wrong.
  from aminer.input import SimpleUnparsedAtomHandler
  atomFilter.addHandler(SimpleUnparsedAtomHandler(anomalyEventHandlers),
      stopWhenHandledFlag=True)

# Report new parsing model path values. Those occurr when a line
# with new structural properties was parsed.
  from aminer.analysis import NewMatchPathDetector
  newMatchPathDetector=NewMatchPathDetector(
      analysisContext.aminerConfig, anomalyEventHandlers, autoIncludeFlag=True)
  analysisContext.registerComponent(newMatchPathDetector, componentName=None)
  atomFilter.addHandler(newMatchPathDetector)

# Run a whitelisting over the parsed lines.
  from aminer.analysis import Rules
  from aminer.analysis import WhitelistViolationDetector
  violationAction=Rules.EventGenerationMatchAction('Analysis.GenericViolation',
      'Violation detected', anomalyEventHandlers)
  whitelistRules=[]
# Filter out things so bad, that we do not want to accept the
# risk, that a too broad whitelisting rule will accept the data
# later on.
  whitelistRules.append(Rules.ValueMatchRule('/model/services/cron/msgtype/exec/user', 'hacker', violationAction))
# Ignore Exim queue run start/stop messages
  whitelistRules.append(Rules.PathExistsMatchRule('/model/services/exim/msg/queue/pid'))
# Ignore all ntpd messages for now.
  whitelistRules.append(Rules.PathExistsMatchRule('/model/services/ntpd'))
# Add a debugging rule in the middle to see everything not whitelisted
# up to this point.
  whitelistRules.append(Rules.DebugMatchRule(False))
# Ignore hourly cronjobs, but only when started at expected time
# and duration is not too long.
  whitelistRules.append(Rules.AndMatchRule([
      Rules.ValueMatchRule('/model/services/cron/msgtype/exec/command', '(   cd / && run-parts --report /etc/cron.hourly)'),
      Rules.ModuloTimeMatchRule('/model/syslog/time', 3600, 17*60, 17*60+5)]))

  atomFilter.addHandler(WhitelistViolationDetector(whitelistRules, anomalyEventHandlers))

# Include the e-mail notification handler only if the configuration
# parameter was set.
  from aminer.events import DefaultMailNotificationEventHandler
  if analysisContext.aminerConfig.configProperties.has_key(
      DefaultMailNotificationEventHandler.CONFIG_KEY_MAIL_TARGET_ADDRESS):
    mailNotificationHandler=DefaultMailNotificationEventHandler(analysisContext.aminerConfig)
    analysisContext.registerComponent(mailNotificationHandler,
        componentName=None)
    anomalyEventHandlers.append(mailNotificationHandler)

# Add stdout stream printing for debugging, tuning.
  from aminer.events import StreamPrinterEventHandler
  anomalyEventHandlers.append(StreamPrinterEventHandler(analysisContext.aminerConfig))
