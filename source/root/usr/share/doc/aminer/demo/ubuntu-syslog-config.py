# This demo creates an analysis pipeline to parse typical Ubuntu
# server logs.
#
# DO NOT USE THIS TO RUN PRODUCTION ANALYSIS PIPELINE AS IT CONTAINS
# SETTINGS FOR TESTING, THAT MAY IMPEDE SECURITY AND PERFORMANCE!
# THOSE CHANGES ARE MARKED WITH "DEMO" TO AVOID ACCIDENTAL USE!

configProperties = {}

# Define the list of log resources to read from: the resources
# named here do not need to exist when aminer is started. This
# will just result in a warning. However if they exist, they have
# to be readable by the aminer process! Supported types are:
# * file://[path]: Read data from file, reopen it after rollover
# * unix://[path]: Open the path as UNIX local socket for reading
# DEMO: FORBIDDEN RELATIVE PATH!
configProperties['LogResourceList'] = ['file://test.log']

# Define the uid/gid of the process that runs the calculation
# after opening the log files:
# DEMO: PRIVILEGE SEPARATION DISABLED!
# configProperties['AMinerUser'] = 'aminer'
# configProperties['AMinerGroup'] = 'aminer'

# Define the path, where aminer will listen for incoming remote
# control connections. When missing, no remote control socket
# will be created.
# configProperties['RemoteControlSocket'] = '/var/run/aminer-remote.socket'

# Read the analyis from this file. That part of configuration
# is separated from the main configuration so that it can be loaded
# only within the analysis child. Non-absolute path names are
# interpreted relatively to the main configuration file (this
# file). Defaults to "analysis.py".
# configProperties['AnalysisConfigFile'] = 'analysis.py'

# Read and store information to be used between multiple invocations
# of AMiner in this directory. The directory must only be accessible
# to the 'AMinerUser' but not group/world readable. On violation,
# AMiner will refuse to start. When undefined, '/var/lib/aminer'
# is used.
# DEMO: FORBIDDEN RELATIVE PATH!
configProperties['Core.PersistenceDir'] = 'aminer'

# Define a target e-mail address to send alerts to. When undefined,
# no e-mail notification hooks are added.
# configProperties['MailAlerting.TargetAddress'] = 'root@localhost'
# Sender address of e-mail alerts. When undefined, "sendmail"
# implementation on host will decide, which sender address should
# be used.
# configProperties['MailAlerting.FromAddress'] = 'root@localhost'
# Define, which text should be prepended to the standard aminer
# subject. Defaults to "AMiner Alerts:"
# configProperties['MailAlerting.SubjectPrefix'] = 'AMiner Alerts:'
# Define a grace time after startup before aminer will react to
# an event and send the first alert e-mail. Defaults to 0 (any
# event can immediately trigger alerting).
# configProperties['MailAlerting.AlertGraceTime'] = 0
# Define how many seconds to wait after a first event triggered
# the alerting procedure before really sending out the e-mail.
# In that timespan, events are collected and will be sent all
# using a single e-mail. Defaults to 10 seconds.
# configProperties['MailAlerting.EventCollectTime'] = 10
# Define the minimum time between two alert e-mails in seconds
# to avoid spamming. All events during this timespan are collected
# and sent out with the next report. Defaults to 600 seconds.
# configProperties['MailAlerting.MinAlertGap'] = 600
# Define the maximum time between two alert e-mails in seconds.
# When undefined this defaults to "MailAlerting.MinAlertGap".
# Otherwise this will activate an exponential backoff to reduce
# messages during permanent error states by increasing the alert
# gap by 50% when more alert-worthy events were recorded while
# the previous gap time was not yet elapsed.
# configProperties['MailAlerting.MaxAlertGap'] = 600
# Define how many events should be included in one alert mail
# at most. This defaults to 1000
# configProperties['MailAlerting.MaxEventsPerMessage'] = 1000

# DEMO: INCLUSION OF ALL AMINER ELEMENTS AND ALL PYTHON SITE PACKAGES
# NOT RECOMMENDED!
import sys
sys.path = sys.path+['/etc/aminer/conf-available/generic', '/usr/lib/python2.7/dist-packages']

# DEMO: DISABLE SECURE OPEN TO ALLOW RELATIVE PATH, SYMLINKS!
import os
def insecure_demo_open(file_name, flags):
  """Perform a normal open supporting also relative path to override
  more strict secureOpenFile function in test environment."""
  return os.open(file_name, flags|os.O_NOCTTY)
from aminer.util import SecureOSFunctions
SecureOSFunctions.secureOpenFile = insecure_demo_open


# Add your ruleset here:

def build_analysis_pipeline(analysis_context):
  """Define the function to create pipeline for parsing the log
  data. It has also to define an AtomizerFactory to instruct AMiner
  how to process incoming data streams to create log atoms from
  them."""
# Build the parsing model first:
  from aminer.parsing import FirstMatchModelElement
  from aminer.parsing import SequenceModelElement

  service_children = []

  import CronParsingModel
  service_children.append(CronParsingModel.getModel())

  import EximParsingModel
  service_children.append(EximParsingModel.getModel())

  import RsyslogParsingModel
  service_children.append(RsyslogParsingModel.getModel())

  import syslog_preamble_model
  syslog_preamble_model = syslog_preamble_model.getModel()

  parsing_model = SequenceModelElement('model', [
      syslog_preamble_model,
      FirstMatchModelElement('services', service_children)])


# Some generic imports.
  from aminer.analysis import AtomFilters
  from aminer.analysis import Rules

# Create all global handler lists here and append the real handlers
# later on.
# Use this filter to distribute all atoms to the analysis handlers.
  atom_filter = AtomFilters.SubhandlerFilter(None)
  anomaly_event_handlers = []

# Now define the AtomizerFactory using the model. A simple line
# based one is usually sufficient.
  from aminer.input import SimpleByteStreamLineAtomizerFactory
  analysis_context.atomizerFactory = SimpleByteStreamLineAtomizerFactory(
      parsing_model, [atom_filter], anomaly_event_handlers,
      defaultTimestampPath='/model/syslog/time')

# Always report the unparsed lines: a part of the parsing model
# seems to be missing or wrong.
  from aminer.input import SimpleUnparsedAtomHandler
  atom_filter.addHandler(
      SimpleUnparsedAtomHandler(anomaly_event_handlers),
      stopWhenHandledFlag=True)

# Report new parsing model path values. Those occurr when a line
# with new structural properties was parsed.
  from aminer.analysis import NewMatchPathDetector
  new_match_path_detector = NewMatchPathDetector(
      analysis_context.aminerConfig, anomaly_event_handlers, autoIncludeFlag=True)
  analysis_context.registerComponent(
      new_match_path_detector, componentName='DefaultMatchPathDetector')
  atom_filter.addHandler(new_match_path_detector)

# Run a whitelisting over the parsed lines.
  from aminer.analysis import WhitelistViolationDetector
  violation_action = Rules.EventGenerationMatchAction(
      'Analysis.GenericViolation', 'Violation detected', anomaly_event_handlers)
  whitelist_rules = []
# Filter out things so bad, that we do not want to accept the
# risk, that a too broad whitelisting rule will accept the data
# later on.
  whitelist_rules.append(Rules.ValueMatchRule(
      '/model/services/cron/msgtype/exec/user', 'hacker', violation_action))
# Ignore Exim queue run start/stop messages
  whitelist_rules.append(Rules.PathExistsMatchRule(
      '/model/services/exim/msg/queue/pid'))
# Ignore all ntpd messages for now.
  whitelist_rules.append(Rules.PathExistsMatchRule('/model/services/ntpd'))
# Add a debugging rule in the middle to see everything not whitelisted
# up to this point.
  whitelist_rules.append(Rules.DebugMatchRule(False))
# Ignore hourly cronjobs, but only when started at expected time
# and duration is not too long.
  whitelist_rules.append(Rules.AndMatchRule([
      Rules.ValueMatchRule(
          '/model/services/cron/msgtype/exec/command',
          '(   cd / && run-parts --report /etc/cron.hourly)'),
      Rules.ModuloTimeMatchRule('/model/syslog/time', 3600, 17*60, 17*60+5)]))

  whitelistViolationDetector = WhitelistViolationDetector(whitelist_rules, anomaly_event_handlers)
  atom_filter.addHandler(whitelistViolationDetector)

# Include the e-mail notification handler only if the configuration
# parameter was set.
  from aminer.events import DefaultMailNotificationEventHandler
  if DefaultMailNotificationEventHandler.CONFIG_KEY_MAIL_TARGET_ADDRESS in analysis_context.aminerConfig.configProperties:
    mail_notification_handler = DefaultMailNotificationEventHandler(analysis_context.aminerConfig)
    analysis_context.registerComponent(
        mail_notification_handler, componentName=None)
    anomaly_event_handlers.append(mail_notification_handler)

# Add stdout stream printing for debugging, tuning.
  from aminer.events import StreamPrinterEventHandler
  anomaly_event_handlers.append(StreamPrinterEventHandler(analysis_context.aminerConfig))
