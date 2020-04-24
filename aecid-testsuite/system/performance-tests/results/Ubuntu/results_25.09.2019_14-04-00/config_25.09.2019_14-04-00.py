# This is a template for the "aminer" logfile miner tool. Copy
# it to "config.py" and define your ruleset.

configProperties = {}

# Define the list of log resources to read from: the resources
# named here do not need to exist when aminer is started. This
# will just result in a warning. However if they exist, they have
# to be readable by the aminer process! Supported types are:
# * file://[path]: Read data from file, reopen it after rollover
# * unix://[path]: Open the path as UNIX local socket for reading
configProperties['LogResourceList'] = ['file:///tmp/syslog']

# Define the uid/gid of the process that runs the calculation
# after opening the log files:
configProperties['AMinerUser'] = 'aminer'
configProperties['AMinerGroup'] = 'aminer'

# Define the path, where aminer will listen for incoming remote
# control connections. When missing, no remote control socket
# will be created.
# configProperties['RemoteControlSocket'] = '/var/run/aminer-remote.socket'

# Read the analyis from this file. That part of configuration
# is separated from the main configuration so that it can be loaded
# only within the analysis child. Non-absolute path names are
# interpreted relatively to the main configuration file (this
# file). When empty, this configuration has to contain the configuration
# for the child also.
# configProperties['AnalysisConfigFile'] = 'analysis.py'


# Read and store information to be used between multiple invocations
# of AMiner in this directory. The directory must only be accessible
# to the 'AMinerUser' but not group/world readable. On violation,
# AMiner will refuse to start. When undefined, '/var/lib/aminer'
# is used.
configProperties['Core.PersistenceDir'] = '/tmp/lib/aminer'

# Define a target e-mail address to send alerts to. When undefined,
# no e-mail notification hooks are added.
configProperties['MailAlerting.TargetAddress'] = 'root@localhost'
# Sender address of e-mail alerts. When undefined, "sendmail"
# implementation on host will decide, which sender address should
# be used.
configProperties['MailAlerting.FromAddress'] = 'root@localhost'
# Define, which text should be prepended to the standard aminer
# subject. Defaults to "AMiner Alerts:"
configProperties['MailAlerting.SubjectPrefix'] = 'AMiner Alerts:'
# Define a grace time after startup before aminer will react to
# an event and send the first alert e-mail. Defaults to 0 (any
# event can immediately trigger alerting).
configProperties['MailAlerting.AlertGraceTime'] = 0
# Define how many seconds to wait after a first event triggered
# the alerting procedure before really sending out the e-mail.
# In that timespan, events are collected and will be sent all
# using a single e-mail. Defaults to 10 seconds.
configProperties['MailAlerting.EventCollectTime'] = 0
# Define the minimum time between two alert e-mails in seconds
# to avoid spamming. All events during this timespan are collected
# and sent out with the next report. Defaults to 600 seconds.
configProperties['MailAlerting.MinAlertGap'] = 0
# Define the maximum time between two alert e-mails in seconds.
# When undefined this defaults to "MailAlerting.MinAlertGap".
# Otherwise this will activate an exponential backoff to reduce
# messages during permanent error states by increasing the alert
# gap by 50% when more alert-worthy events were recorded while
# the previous gap time was not yet elapsed.
configProperties['MailAlerting.MaxAlertGap'] = 600
# Define how many events should be included in one alert mail
# at most. This defaults to 1000
configProperties['MailAlerting.MaxEventsPerMessage'] = 1000
configProperties['LogPrefix'] = 'Original log line: '

# Add your ruleset here:

def buildAnalysisPipeline(analysisContext):
  """Define the function to create pipeline for parsing the log
  data. It has also to define an AtomizerFactory to instruct AMiner
  how to process incoming data streams to create log atoms from
  them."""

# Build the parsing model:
  from aminer.parsing import AnyByteDataModelElement

  parsingModel = AnyByteDataModelElement('AnyByteDataModelElement')

# Some generic imports.
  from aminer.analysis import AtomFilters

# Create all global handler lists here and append the real handlers
# later on.
# Use this filter to distribute all atoms to the analysis handlers.
  atomFilter = AtomFilters.SubhandlerFilter(None)

  from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
  streamPrinterEventHandler = StreamPrinterEventHandler(analysisContext)
  anomalyEventHandlers = [streamPrinterEventHandler]

# Now define the AtomizerFactory using the model. A simple line
# based one is usually sufficient.
  from aminer.input import SimpleByteStreamLineAtomizerFactory
  analysisContext.atomizerFactory = SimpleByteStreamLineAtomizerFactory(
      parsingModel, [atomFilter], anomalyEventHandlers)

# Just report all unparsed atoms to the event handlers.
  from aminer.input import SimpleUnparsedAtomHandler
  simpleUnparsedAtomHandler = SimpleUnparsedAtomHandler(anomalyEventHandlers)
  atomFilter.addHandler(simpleUnparsedAtomHandler, stopWhenHandledFlag=True)
  analysisContext.registerComponent(simpleUnparsedAtomHandler, componentName="UnparsedHandler")

  from aminer.analysis import NewMatchPathDetector
  newMatchPathDetector = NewMatchPathDetector(
      analysisContext.aminerConfig, anomalyEventHandlers, autoIncludeFlag=True)
  analysisContext.registerComponent(newMatchPathDetector, componentName="NewMatchPath")
  atomFilter.addHandler(newMatchPathDetector)

  from aminer.analysis.NewMatchPathValueDetector import NewMatchPathValueDetector
  newMatchPathValueDetector = NewMatchPathValueDetector(analysisContext.aminerConfig, ['/AnyByteDataModelElement'], anomalyEventHandlers, autoIncludeFlag=True)
  analysisContext.registerComponent(newMatchPathValueDetector, componentName="NewMatchPathValue")
  atomFilter.addHandler(newMatchPathValueDetector)
