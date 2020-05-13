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
configProperties['RemoteControlSocket'] = '/var/run/aminer-remote.socket'

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
configProperties['Resources.MaxCpuPercentUsage'] = 30
configProperties['Resources.Resources.MaxMemoryUsage'] = 64

# Add your ruleset here:

def buildAnalysisPipeline(analysisContext):
  """Define the function to create pipeline for parsing the log
  data. It has also to define an AtomizerFactory to instruct AMiner
  how to process incoming data streams to create log atoms from
  them."""

# Build the parsing model:
  # skipcq: PYL-W0611
  from aminer.parsing import FirstMatchModelElement, SequenceModelElement, DecimalFloatValueModelElement, FixedDataModelElement, DelimitedDataModelElement, AnyByteDataModelElement, FixedWordlistDataModelElement, DecimalIntegerValueModelElement, DateTimeModelElement, IpAddressDataModelElement, Base64StringModelElement, ElementValueBranchModelElement, HexStringModelElement, MultiLocaleDateTimeModelElement, OptionalMatchModelElement, RepeatedElementDataModelElement, VariableByteDataModelElement, WhiteSpaceLimitedDataModelElement

  serviceChildrenDiskReport = []

  serviceChildrenDiskReport.append(FixedDataModelElement('Space', b' Current Disk Data is: Filesystem     Type  Size  Used Avail Use%'))
  serviceChildrenDiskReport.append(DelimitedDataModelElement('Data', b'%'))
  serviceChildrenDiskReport.append(AnyByteDataModelElement('Rest'))


  serviceChildrenLoginDetails = []

  serviceChildrenLoginDetails.append(FixedDataModelElement('User', b'User '))
  serviceChildrenLoginDetails.append(DelimitedDataModelElement('Username', b' '))
  serviceChildrenLoginDetails.append(FixedWordlistDataModelElement('Status', [b' logged in', b' logged out']))
  serviceChildrenLoginDetails.append(OptionalMatchModelElement('Past Time', SequenceModelElement('Time', [FixedDataModelElement('Blank', b' '), DecimalIntegerValueModelElement('Minutes'), FixedDataModelElement('Ago', b' minutes ago.')])))


  serviceChildrenCronJob = []

  serviceChildrenCronJob.append(DateTimeModelElement('DTM', b'%Y-%m-%d %H:%M:%S'))
  serviceChildrenCronJob.append(FixedDataModelElement('UName Space1', b' '))
  serviceChildrenCronJob.append(DelimitedDataModelElement('UName', b' '))
  serviceChildrenCronJob.append(FixedDataModelElement('UName Space2', b' '))
  serviceChildrenCronJob.append(DelimitedDataModelElement('User', b' '))
  serviceChildrenCronJob.append(FixedDataModelElement('Cron', b' cron['))
  serviceChildrenCronJob.append(DecimalIntegerValueModelElement('Job Number'))
  serviceChildrenCronJob.append(FixedDataModelElement('Details', b']: Job `cron.daily` started.'))


  serviceChildrenRandomTime = []

  serviceChildrenRandomTime.append(FixedDataModelElement('Space', b'Random: '))
  serviceChildrenRandomTime.append(DecimalIntegerValueModelElement('Random'))


  serviceChildrenSensors = []

  serviceChildrenSensors.append(SequenceModelElement('CPU Temp', [FixedDataModelElement('Fixed Temp', b'CPU Temp: '), DecimalIntegerValueModelElement('Temp'), FixedDataModelElement('Degrees', b'\xc2\xb0C')]))
  serviceChildrenSensors.append(FixedDataModelElement('Space1', b', '))
  serviceChildrenSensors.append(SequenceModelElement('CPU Workload', [FixedDataModelElement('Fixed Workload', b'CPU Workload: '), DecimalIntegerValueModelElement('Workload'), FixedDataModelElement('Percent', b'%')]))
  serviceChildrenSensors.append(FixedDataModelElement('Space2', b', '))
  serviceChildrenSensors.append(DateTimeModelElement('DTM', b'%Y-%m-%d %H:%M:%S'))


  serviceChildrenUserIpAddress = []

  serviceChildrenUserIpAddress.append(FixedDataModelElement('User', b'User '))
  serviceChildrenUserIpAddress.append(DelimitedDataModelElement('Username', b' '))
  serviceChildrenUserIpAddress.append(FixedDataModelElement('Action', b' changed IP address to '))
  serviceChildrenUserIpAddress.append(IpAddressDataModelElement('IP'))


  serviceChildrenCronJobAnnouncement = []

  serviceChildrenCronJobAnnouncement.append(DateTimeModelElement('DTM', b'%Y-%m-%d %H:%M:%S'))
  serviceChildrenCronJobAnnouncement.append(FixedDataModelElement('Space', b' '))
  serviceChildrenCronJobAnnouncement.append(DelimitedDataModelElement('UName', b' '))
  serviceChildrenCronJobAnnouncement.append(FixedDataModelElement('Cron', b' cron['))
  serviceChildrenCronJobAnnouncement.append(DecimalIntegerValueModelElement('Job Number'))
  serviceChildrenCronJobAnnouncement.append(FixedDataModelElement('Run', b']: Will run job `'))
  serviceChildrenCronJobAnnouncement.append(FixedWordlistDataModelElement('Cron Type', [b'cron.daily', b'cron.hourly', b'cron.monthly', b'cron.weekly']))
  serviceChildrenCronJobAnnouncement.append(FixedDataModelElement('Start Time', b'\' in 5 min.'))


  serviceChildrenCronJobExecution = []

  serviceChildrenCronJobExecution.append(DateTimeModelElement('DTM', b'%Y-%m-%d %H:%M:%S'))
  serviceChildrenCronJobExecution.append(FixedDataModelElement('Space1', b' '))
  serviceChildrenCronJobExecution.append(DelimitedDataModelElement('UName', b' '))
  serviceChildrenCronJobExecution.append(FixedDataModelElement('Cron', b' cron['))
  serviceChildrenCronJobExecution.append(DecimalIntegerValueModelElement('Job Number'))
  serviceChildrenCronJobExecution.append(FixedDataModelElement('Job', b']: Job `'))
  serviceChildrenCronJobExecution.append(FixedWordlistDataModelElement('Cron Type', [b'cron.daily', b'cron.hourly', b'cron.monthly', b'cron.weekly']))
  serviceChildrenCronJobExecution.append(FixedDataModelElement('Started', b'\' started'))


  parsingModel = FirstMatchModelElement('model', [SequenceModelElement('Cron Announcement', serviceChildrenCronJobAnnouncement), SequenceModelElement('Cron Execution', serviceChildrenCronJobExecution), SequenceModelElement('Daily Cron', serviceChildrenCronJob), SequenceModelElement('Disk Report', serviceChildrenDiskReport), SequenceModelElement('Login Details', serviceChildrenLoginDetails), DecimalIntegerValueModelElement('Random'), SequenceModelElement('Random Time', serviceChildrenRandomTime), SequenceModelElement('Sensors', serviceChildrenSensors), SequenceModelElement('IP Addresses', serviceChildrenUserIpAddress)])

# Some generic imports.
  from aminer.analysis import AtomFilters

# Create all global handler lists here and append the real handlers
# later on.
# Use this filter to distribute all atoms to the analysis handlers.
  atomFilter = AtomFilters.SubhandlerFilter(None)

  from aminer.analysis.TimestampCorrectionFilters import SimpleMonotonicTimestampAdjust
  simpleMonotonicTimestampAdjust = SimpleMonotonicTimestampAdjust([atomFilter])
  analysisContext.registerComponent(simpleMonotonicTimestampAdjust, componentName="SimpleMonotonicTimestampAdjust")

  from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
  streamPrinterEventHandler = StreamPrinterEventHandler(analysisContext)
  anomalyEventHandlers = [streamPrinterEventHandler]

# Now define the AtomizerFactory using the model. A simple line
# based one is usually sufficient.
  from aminer.input import SimpleByteStreamLineAtomizerFactory
  analysisContext.atomizerFactory = SimpleByteStreamLineAtomizerFactory(
      parsingModel, [simpleMonotonicTimestampAdjust], anomalyEventHandlers)

# Just report all unparsed atoms to the event handlers.
  from aminer.input import SimpleUnparsedAtomHandler
  simpleUnparsedAtomHandler = SimpleUnparsedAtomHandler(anomalyEventHandlers)
  atomFilter.addHandler(simpleUnparsedAtomHandler, stopWhenHandledFlag=True)
  analysisContext.registerComponent(simpleUnparsedAtomHandler, componentName="UnparsedHandler")

  from aminer.analysis.TimestampsUnsortedDetector import TimestampsUnsortedDetector
  timestampsUnsortedDetector = TimestampsUnsortedDetector(analysisContext.aminerConfig, anomalyEventHandlers)
  atomFilter.addHandler(timestampsUnsortedDetector)
  analysisContext.registerComponent(timestampsUnsortedDetector, componentName="TimestampsUnsortedDetector")

  from aminer.analysis import Rules
  from aminer.analysis import WhitelistViolationDetector
  _violationAction=Rules.EventGenerationMatchAction('Analysis.GenericViolation',
      'Violation detected', anomalyEventHandlers)
  whitelistRules=[]
  
# This rule list should trigger, when the line does not look like: User root (logged in, logged out) 
# or User 'username' (logged in, logged out) x minutes ago.
  whitelistRules.append(Rules.OrMatchRule([
	Rules.AndMatchRule([Rules.PathExistsMatchRule('/model/Login Details/Past Time/Time/Minutes'), 
		Rules.NegationMatchRule(Rules.ValueMatchRule('/model/Login Details/Username', b'root'))]), 
	Rules.AndMatchRule([Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/Login Details/Past Time/Time/Minutes')),
		Rules.PathExistsMatchRule('/model/Login Details')]),
	Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/Login Details'))]))
  whitelistViolationDetector = WhitelistViolationDetector(analysisContext.aminerConfig, whitelistRules, anomalyEventHandlers)
  analysisContext.registerComponent(whitelistViolationDetector, componentName="Whitelist")
  atomFilter.addHandler(whitelistViolationDetector)


  from aminer.analysis import NewMatchPathDetector
  newMatchPathDetector = NewMatchPathDetector(
      analysisContext.aminerConfig, anomalyEventHandlers, auto_include_flag=True)
  analysisContext.registerComponent(newMatchPathDetector, componentName="NewMatchPath")
  atomFilter.addHandler(newMatchPathDetector)

  def tuple_transformation_function(matchValueList):
    extraData = enhancedNewMatchPathValueComboDetector.knownValuesDict.get(tuple(matchValueList),None)
    if extraData is None:
        return matchValueList
    mod = 10000
    if (extraData[2]+1) % mod == 0:
	    enhancedNewMatchPathValueComboDetector.auto_include_flag=False
    else:
        enhancedNewMatchPathValueComboDetector.auto_include_flag=True
    return matchValueList

  from aminer.analysis.EnhancedNewMatchPathValueComboDetector import EnhancedNewMatchPathValueComboDetector
  enhancedNewMatchPathValueComboDetector = EnhancedNewMatchPathValueComboDetector(analysisContext.aminerConfig, 
		['/model/Daily Cron/UName', '/model/Daily Cron/Job Number'], anomalyEventHandlers, auto_include_flag=True, tuple_transformation_function=tuple_transformation_function)
  analysisContext.registerComponent(enhancedNewMatchPathValueComboDetector, componentName = "EnhancedNewValueCombo")
  atomFilter.addHandler(enhancedNewMatchPathValueComboDetector)

  from aminer.analysis.HistogramAnalysis import HistogramAnalysis, LinearNumericBinDefinition, ModuloTimeBinDefinition, PathDependentHistogramAnalysis
  moduloTimeBinDefinition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, True)
  linearNumericBinDefinition = LinearNumericBinDefinition(50, 5, 20, True)
  histogramAnalysis = HistogramAnalysis(analysisContext.aminerConfig, [('/model/Random Time/Random', moduloTimeBinDefinition), ('/model/Random', linearNumericBinDefinition)],
		10, anomalyEventHandlers)
  analysisContext.registerComponent(histogramAnalysis, componentName="HistogramAnalysis")
  atomFilter.addHandler(histogramAnalysis)

  pathDependentHistogramAnalysis = PathDependentHistogramAnalysis(analysisContext.aminerConfig, '/model/Random Time', moduloTimeBinDefinition, 10, anomalyEventHandlers)
  analysisContext.registerComponent(pathDependentHistogramAnalysis, componentName="PathDependentHistogramAnalysis")
  atomFilter.addHandler(pathDependentHistogramAnalysis)

  from aminer.analysis.MatchValueAverageChangeDetector import MatchValueAverageChangeDetector
  matchValueAverageChangeDetector = MatchValueAverageChangeDetector(analysisContext.aminerConfig, anomalyEventHandlers, None, ['/model/Random'], 100, 10)
  analysisContext.registerComponent(matchValueAverageChangeDetector, componentName="MatchValueAverageChange")
  atomFilter.addHandler(matchValueAverageChangeDetector)

  import sys
  from aminer.analysis.MatchValueStreamWriter import MatchValueStreamWriter
  matchValueStreamWriter = MatchValueStreamWriter(sys.stdout, ['/model/Sensors/CPU Temp', '/model/Sensors/CPU Workload', '/model/Sensors/DTM'], b';', b'')
  analysisContext.registerComponent(matchValueStreamWriter, componentName="MatchValueStreamWriter")
  atomFilter.addHandler(matchValueStreamWriter)

  from aminer.analysis.NewMatchPathValueComboDetector import NewMatchPathValueComboDetector
  newMatchPathValueComboDetector = NewMatchPathValueComboDetector(analysisContext.aminerConfig, ['/model/IP Addresses/Username', '/model/IP Addresses/IP'], anomalyEventHandlers, auto_include_flag=True)
  analysisContext.registerComponent(newMatchPathValueComboDetector, componentName="NewMatchPathValueCombo")
  atomFilter.addHandler(newMatchPathValueComboDetector)

  from aminer.analysis.NewMatchPathValueDetector import NewMatchPathValueDetector
  newMatchPathValueDetector = NewMatchPathValueDetector(analysisContext.aminerConfig, ['/model/Daily Cron/Job Number', '/model/IP Addresses/Username'], anomalyEventHandlers, auto_include_flag=True)
  analysisContext.registerComponent(newMatchPathValueDetector, componentName="NewMatchPathValue")
  atomFilter.addHandler(newMatchPathValueDetector)

  from aminer.analysis.MissingMatchPathValueDetector import MissingMatchPathValueDetector
  missingMatchPathValueDetector = MissingMatchPathValueDetector(
	  analysisContext.aminerConfig, '/model/Disk Report/Space', anomalyEventHandlers, auto_include_flag=True, default_interval=2, realert_interval=5)
  analysisContext.registerComponent(missingMatchPathValueDetector, componentName="MissingMatch")
  atomFilter.addHandler(missingMatchPathValueDetector)

  from aminer.analysis.TimeCorrelationDetector import TimeCorrelationDetector
  timeCorrelationDetector = TimeCorrelationDetector(analysisContext.aminerConfig, 2, 1, 0, anomalyEventHandlers, record_count_before_event=70000)
  analysisContext.registerComponent(timeCorrelationDetector, componentName="TimeCorrelationDetector")
  atomFilter.addHandler(timeCorrelationDetector)

  from aminer.analysis.TimeCorrelationViolationDetector import TimeCorrelationViolationDetector, CorrelationRule, EventClassSelector
  cronJobAnnouncement = CorrelationRule('Cron Job Announcement', 5, 6, max_artefacts_a_for_single_b=1, artefact_match_parameters=[('/model/Cron Announcement/Job Number','/model/Cron Execution/Job Number')])
  aClassSelector=EventClassSelector('Announcement', [cronJobAnnouncement], None)
  bClassSelector=EventClassSelector('Execution', None, [cronJobAnnouncement])
  rules = []
  rules.append(Rules.PathExistsMatchRule('/model/Cron Announcement/Run', aClassSelector))
  rules.append(Rules.PathExistsMatchRule('/model/Cron Execution/Job', bClassSelector))

  timeCorrelationViolationDetector = TimeCorrelationViolationDetector(analysisContext.aminerConfig, rules, anomalyEventHandlers)
  analysisContext.registerComponent(timeCorrelationViolationDetector, componentName="TimeCorrelationViolationDetector")
  atomFilter.addHandler(timeCorrelationViolationDetector)
