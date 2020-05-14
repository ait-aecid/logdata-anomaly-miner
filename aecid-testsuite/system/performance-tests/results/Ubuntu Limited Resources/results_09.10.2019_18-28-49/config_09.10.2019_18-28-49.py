# This is a template for the "aminer" logfile miner tool. Copy
# it to "config.py" and define your ruleset.

config_properties = {}

# Define the list of log resources to read from: the resources
# named here do not need to exist when aminer is started. This
# will just result in a warning. However if they exist, they have
# to be readable by the aminer process! Supported types are:
# * file://[path]: Read data from file, reopen it after rollover
# * unix://[path]: Open the path as UNIX local socket for reading
config_properties['LogResourceList'] = ['file:///tmp/syslog']

# Define the uid/gid of the process that runs the calculation
# after opening the log files:
config_properties['AMinerUser'] = 'aminer'
config_properties['AMinerGroup'] = 'aminer'

# Define the path, where aminer will listen for incoming remote
# control connections. When missing, no remote control socket
# will be created.
config_properties['RemoteControlSocket'] = '/var/run/aminer-remote.socket'

# Read the analyis from this file. That part of configuration
# is separated from the main configuration so that it can be loaded
# only within the analysis child. Non-absolute path names are
# interpreted relatively to the main configuration file (this
# file). When empty, this configuration has to contain the configuration
# for the child also.
# config_properties['AnalysisConfigFile'] = 'analysis.py'


# Read and store information to be used between multiple invocations
# of AMiner in this directory. The directory must only be accessible
# to the 'AMinerUser' but not group/world readable. On violation,
# AMiner will refuse to start. When undefined, '/var/lib/aminer'
# is used.
config_properties['Core.PersistenceDir'] = '/tmp/lib/aminer'

# Define a target e-mail address to send alerts to. When undefined,
# no e-mail notification hooks are added.
config_properties['MailAlerting.TargetAddress'] = 'root@localhost'
# Sender address of e-mail alerts. When undefined, "sendmail"
# implementation on host will decide, which sender address should
# be used.
config_properties['MailAlerting.FromAddress'] = 'root@localhost'
# Define, which text should be prepended to the standard aminer
# subject. Defaults to "AMiner Alerts:"
config_properties['MailAlerting.SubjectPrefix'] = 'AMiner Alerts:'
# Define a grace time after startup before aminer will react to
# an event and send the first alert e-mail. Defaults to 0 (any
# event can immediately trigger alerting).
config_properties['MailAlerting.AlertGraceTime'] = 0
# Define how many seconds to wait after a first event triggered
# the alerting procedure before really sending out the e-mail.
# In that timespan, events are collected and will be sent all
# using a single e-mail. Defaults to 10 seconds.
config_properties['MailAlerting.EventCollectTime'] = 0
# Define the minimum time between two alert e-mails in seconds
# to avoid spamming. All events during this timespan are collected
# and sent out with the next report. Defaults to 600 seconds.
config_properties['MailAlerting.MinAlertGap'] = 0
# Define the maximum time between two alert e-mails in seconds.
# When undefined this defaults to "MailAlerting.MinAlertGap".
# Otherwise this will activate an exponential backoff to reduce
# messages during permanent error states by increasing the alert
# gap by 50% when more alert-worthy events were recorded while
# the previous gap time was not yet elapsed.
config_properties['MailAlerting.MaxAlertGap'] = 600
# Define how many events should be included in one alert mail
# at most. This defaults to 1000
config_properties['MailAlerting.MaxEventsPerMessage'] = 1000
config_properties['LogPrefix'] = 'Original log line: '
config_properties['Resources.MaxCpuPercentUsage'] = 30
config_properties['Resources.Resources.MaxMemoryUsage'] = 64

# Add your ruleset here:

def build_analysis_pipeline(analysis_context):
  """Define the function to create pipeline for parsing the log
  data. It has also to define an AtomizerFactory to instruct AMiner
  how to process incoming data streams to create log atoms from
  them."""

# Build the parsing model:
  # skipcq: PYL-W0611
  from aminer.parsing import FirstMatchModelElement, SequenceModelElement, DecimalFloatValueModelElement, FixedDataModelElement, DelimitedDataModelElement, AnyByteDataModelElement, FixedWordlistDataModelElement, DecimalIntegerValueModelElement, DateTimeModelElement, IpAddressDataModelElement, Base64StringModelElement, ElementValueBranchModelElement, HexStringModelElement, MultiLocaleDateTimeModelElement, OptionalMatchModelElement, RepeatedElementDataModelElement, VariableByteDataModelElement, WhiteSpaceLimitedDataModelElement

  service_children_disk_report = []

  service_children_disk_report.append(FixedDataModelElement('Space', b' Current Disk Data is: Filesystem     Type  Size  Used Avail Use%'))
  service_children_disk_report.append(DelimitedDataModelElement('Data', b'%'))
  service_children_disk_report.append(AnyByteDataModelElement('Rest'))


  service_children_login_details = []

  service_children_login_details.append(FixedDataModelElement('User', b'User '))
  service_children_login_details.append(DelimitedDataModelElement('Username', b' '))
  service_children_login_details.append(FixedWordlistDataModelElement('Status', [b' logged in', b' logged out']))
  service_children_login_details.append(OptionalMatchModelElement('Past Time', SequenceModelElement('Time', [FixedDataModelElement('Blank', b' '), DecimalIntegerValueModelElement('Minutes'), FixedDataModelElement('Ago', b' minutes ago.')])))


  service_children_cron_job = []

  service_children_cron_job.append(DateTimeModelElement('DTM', b'%Y-%m-%d %H:%M:%S'))
  service_children_cron_job.append(FixedDataModelElement('UName Space1', b' '))
  service_children_cron_job.append(DelimitedDataModelElement('UName', b' '))
  service_children_cron_job.append(FixedDataModelElement('UName Space2', b' '))
  service_children_cron_job.append(DelimitedDataModelElement('User', b' '))
  service_children_cron_job.append(FixedDataModelElement('Cron', b' cron['))
  service_children_cron_job.append(DecimalIntegerValueModelElement('Job Number'))
  service_children_cron_job.append(FixedDataModelElement('Details', b']: Job `cron.daily` started.'))


  service_children_random_time = []

  service_children_random_time.append(FixedDataModelElement('Space', b'Random: '))
  service_children_random_time.append(DecimalIntegerValueModelElement('Random'))


  service_children_sensors = []

  service_children_sensors.append(SequenceModelElement('CPU Temp', [FixedDataModelElement('Fixed Temp', b'CPU Temp: '), DecimalIntegerValueModelElement('Temp'), FixedDataModelElement('Degrees', b'\xc2\xb0C')]))
  service_children_sensors.append(FixedDataModelElement('Space1', b', '))
  service_children_sensors.append(SequenceModelElement('CPU Workload', [FixedDataModelElement('Fixed Workload', b'CPU Workload: '), DecimalIntegerValueModelElement('Workload'), FixedDataModelElement('Percent', b'%')]))
  service_children_sensors.append(FixedDataModelElement('Space2', b', '))
  service_children_sensors.append(DateTimeModelElement('DTM', b'%Y-%m-%d %H:%M:%S'))


  service_children_user_ip_address = []

  service_children_user_ip_address.append(FixedDataModelElement('User', b'User '))
  service_children_user_ip_address.append(DelimitedDataModelElement('Username', b' '))
  service_children_user_ip_address.append(FixedDataModelElement('Action', b' changed IP address to '))
  service_children_user_ip_address.append(IpAddressDataModelElement('IP'))


  service_children_cron_job_announcement = []

  service_children_cron_job_announcement.append(DateTimeModelElement('DTM', b'%Y-%m-%d %H:%M:%S'))
  service_children_cron_job_announcement.append(FixedDataModelElement('Space', b' '))
  service_children_cron_job_announcement.append(DelimitedDataModelElement('UName', b' '))
  service_children_cron_job_announcement.append(FixedDataModelElement('Cron', b' cron['))
  service_children_cron_job_announcement.append(DecimalIntegerValueModelElement('Job Number'))
  service_children_cron_job_announcement.append(FixedDataModelElement('Run', b']: Will run job `'))
  service_children_cron_job_announcement.append(FixedWordlistDataModelElement('Cron Type', [b'cron.daily', b'cron.hourly', b'cron.monthly', b'cron.weekly']))
  service_children_cron_job_announcement.append(FixedDataModelElement('Start Time', b'\' in 5 min.'))


  service_children_cron_job_execution = []

  service_children_cron_job_execution.append(DateTimeModelElement('DTM', b'%Y-%m-%d %H:%M:%S'))
  service_children_cron_job_execution.append(FixedDataModelElement('Space1', b' '))
  service_children_cron_job_execution.append(DelimitedDataModelElement('UName', b' '))
  service_children_cron_job_execution.append(FixedDataModelElement('Cron', b' cron['))
  service_children_cron_job_execution.append(DecimalIntegerValueModelElement('Job Number'))
  service_children_cron_job_execution.append(FixedDataModelElement('Job', b']: Job `'))
  service_children_cron_job_execution.append(FixedWordlistDataModelElement('Cron Type', [b'cron.daily', b'cron.hourly', b'cron.monthly', b'cron.weekly']))
  service_children_cron_job_execution.append(FixedDataModelElement('Started', b'\' started'))


  parsing_model = FirstMatchModelElement('model', [SequenceModelElement('Cron Announcement', service_children_cron_job_announcement), SequenceModelElement('Cron Execution', service_children_cron_job_execution), SequenceModelElement('Daily Cron', service_children_cron_job), SequenceModelElement('Disk Report', service_children_disk_report), SequenceModelElement('Login Details', service_children_login_details), DecimalIntegerValueModelElement('Random'), SequenceModelElement('Random Time', service_children_random_time), SequenceModelElement('Sensors', service_children_sensors), SequenceModelElement('IP Addresses', service_children_user_ip_address)])

# Some generic imports.
  from aminer.analysis import AtomFilters

# Create all global handler lists here and append the real handlers
# later on.
# Use this filter to distribute all atoms to the analysis handlers.
  atom_filter = AtomFilters.SubhandlerFilter(None)

  from aminer.analysis.TimestampCorrectionFilters import SimpleMonotonicTimestampAdjust
  simple_monotonic_timestamp_adjust = SimpleMonotonicTimestampAdjust([atom_filter])
  analysis_context.register_component(simple_monotonic_timestamp_adjust, component_name="SimpleMonotonicTimestampAdjust")

  from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
  stream_printer_event_handler = StreamPrinterEventHandler(analysis_context)
  anomaly_event_handlers = [stream_printer_event_handler]

# Now define the AtomizerFactory using the model. A simple line
# based one is usually sufficient.
  from aminer.input import SimpleByteStreamLineAtomizerFactory
  analysis_context.atomizer_factory = SimpleByteStreamLineAtomizerFactory(
      parsing_model, [simple_monotonic_timestamp_adjust], anomaly_event_handlers)

# Just report all unparsed atoms to the event handlers.
  from aminer.input import SimpleUnparsedAtomHandler
  simple_unparsed_atom_handler = SimpleUnparsedAtomHandler(anomaly_event_handlers)
  atom_filter.add_handler(simple_unparsed_atom_handler, stop_when_handled_flag=True)
  analysis_context.register_component(simple_unparsed_atom_handler, component_name="UnparsedHandler")

  from aminer.analysis.TimestampsUnsortedDetector import TimestampsUnsortedDetector
  timestamps_unsorted_detector = TimestampsUnsortedDetector(analysis_context.aminer_config, anomaly_event_handlers)
  atom_filter.add_handler(timestamps_unsorted_detector)
  analysis_context.register_component(timestamps_unsorted_detector, component_name="TimestampsUnsortedDetector")

  from aminer.analysis import Rules
  from aminer.analysis import WhitelistViolationDetector
  _violation_action = Rules.EventGenerationMatchAction('Analysis.GenericViolation',
      'Violation detected', anomaly_event_handlers)
  whitelist_rules = []
  
# This rule list should trigger, when the line does not look like: User root (logged in, logged out) 
# or User 'username' (logged in, logged out) x minutes ago.
  whitelist_rules.append(Rules.OrMatchRule([
    Rules.AndMatchRule([Rules.PathExistsMatchRule('/model/Login Details/Past Time/Time/Minutes'), 
        Rules.NegationMatchRule(Rules.ValueMatchRule('/model/Login Details/Username', b'root'))]), 
    Rules.AndMatchRule([Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/Login Details/Past Time/Time/Minutes')),
        Rules.PathExistsMatchRule('/model/Login Details')]),
    Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/Login Details'))]))
  whitelist_violation_detector = WhitelistViolationDetector(analysis_context.aminer_config, whitelist_rules, anomaly_event_handlers)
  analysis_context.register_component(whitelist_violation_detector, component_name="Whitelist")
  atom_filter.add_handler(whitelist_violation_detector)


  from aminer.analysis import NewMatchPathDetector
  new_match_path_detector = NewMatchPathDetector(
      analysis_context.aminer_config, anomaly_event_handlers, auto_include_flag=True)
  analysis_context.register_component(new_match_path_detector, component_name="NewMatchPath")
  atom_filter.add_handler(new_match_path_detector)

  def tuple_transformation_function(match_value_list):
    extra_data = enhanced_new_match_path_value_combo_detector.known_values_dict.get(tuple(match_value_list),None)
    if extra_data is None:
        return match_value_list
    mod = 10000
    if (extra_data[2]+1) % mod == 0:
        enhanced_new_match_path_value_combo_detector.auto_include_flag = False
    else:
        enhanced_new_match_path_value_combo_detector.auto_include_flag = True
    return match_value_list

  from aminer.analysis.EnhancedNewMatchPathValueComboDetector import EnhancedNewMatchPathValueComboDetector
  enhanced_new_match_path_value_combo_detector = EnhancedNewMatchPathValueComboDetector(analysis_context.aminer_config, 
        ['/model/Daily Cron/UName', '/model/Daily Cron/Job Number'], anomaly_event_handlers, auto_include_flag=True, tuple_transformation_function=tuple_transformation_function)
  analysis_context.register_component(enhanced_new_match_path_value_combo_detector, component_name="EnhancedNewValueCombo")
  atom_filter.add_handler(enhanced_new_match_path_value_combo_detector)

  from aminer.analysis.HistogramAnalysis import HistogramAnalysis, LinearNumericBinDefinition, ModuloTimeBinDefinition, PathDependentHistogramAnalysis
  modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, True)
  linear_numeric_bin_definition = LinearNumericBinDefinition(50, 5, 20, True)
  histogram_analysis = HistogramAnalysis(analysis_context.aminer_config, [('/model/Random Time/Random', modulo_time_bin_definition), ('/model/Random', linear_numeric_bin_definition)],
        10, anomaly_event_handlers)
  analysis_context.register_component(histogram_analysis, component_name="HistogramAnalysis")
  atom_filter.add_handler(histogram_analysis)

  path_dependent_histogram_analysis = PathDependentHistogramAnalysis(analysis_context.aminer_config, '/model/Random Time', modulo_time_bin_definition, 10, anomaly_event_handlers)
  analysis_context.register_component(path_dependent_histogram_analysis, component_name="PathDependentHistogramAnalysis")
  atom_filter.add_handler(path_dependent_histogram_analysis)

  from aminer.analysis.MatchValueAverageChangeDetector import MatchValueAverageChangeDetector
  matchValueAverageChangeDetector = MatchValueAverageChangeDetector(analysis_context.aminer_config, anomaly_event_handlers, None, ['/model/Random'], 100, 10)
  analysis_context.register_component(matchValueAverageChangeDetector, component_name="MatchValueAverageChange")
  atom_filter.add_handler(matchValueAverageChangeDetector)

  import sys
  from aminer.analysis.MatchValueStreamWriter import MatchValueStreamWriter
  match_value_stream_writer = MatchValueStreamWriter(sys.stdout, ['/model/Sensors/CPU Temp', '/model/Sensors/CPU Workload', '/model/Sensors/DTM'], b';', b'')
  analysis_context.register_component(match_value_stream_writer, component_name="MatchValueStreamWriter")
  atom_filter.add_handler(match_value_stream_writer)

  from aminer.analysis.NewMatchPathValueComboDetector import NewMatchPathValueComboDetector
  new_match_path_value_combo_detector = NewMatchPathValueComboDetector(analysis_context.aminer_config, ['/model/IP Addresses/Username', '/model/IP Addresses/IP'], anomaly_event_handlers, auto_include_flag=True)
  analysis_context.register_component(new_match_path_value_combo_detector, component_name="NewMatchPathValueCombo")
  atom_filter.add_handler(new_match_path_value_combo_detector)

  from aminer.analysis.NewMatchPathValueDetector import NewMatchPathValueDetector
  new_match_path_value_detector = NewMatchPathValueDetector(analysis_context.aminer_config, ['/model/Daily Cron/Job Number', '/model/IP Addresses/Username'], anomaly_event_handlers, auto_include_flag=True)
  analysis_context.register_component(new_match_path_value_detector, component_name="NewMatchPathValue")
  atom_filter.add_handler(new_match_path_value_detector)

  from aminer.analysis.MissingMatchPathValueDetector import MissingMatchPathValueDetector
  missing_match_path_value_detector = MissingMatchPathValueDetector(
      analysis_context.aminer_config, '/model/Disk Report/Space', anomaly_event_handlers, auto_include_flag=True, default_interval=2, realert_interval=5)
  analysis_context.register_component(missing_match_path_value_detector, component_name="MissingMatch")
  atom_filter.add_handler(missing_match_path_value_detector)

  from aminer.analysis.TimeCorrelationDetector import TimeCorrelationDetector
  time_correlation_detector = TimeCorrelationDetector(analysis_context.aminer_config, 2, 1, 0, anomaly_event_handlers, record_count_before_event=70000)
  analysis_context.register_component(time_correlation_detector, component_name="TimeCorrelationDetector")
  atom_filter.add_handler(time_correlation_detector)

  from aminer.analysis.TimeCorrelationViolationDetector import TimeCorrelationViolationDetector, CorrelationRule, EventClassSelector
  cron_job_announcement = CorrelationRule('Cron Job Announcement', 5, 6, max_artefacts_a_for_single_b=1, artefact_match_parameters=[('/model/Cron Announcement/Job Number','/model/Cron Execution/Job Number')])
  a_class_selector = EventClassSelector('Announcement', [cron_job_announcement], None)
  b_class_selector = EventClassSelector('Execution', None, [cron_job_announcement])
  rules = []
  rules.append(Rules.PathExistsMatchRule('/model/Cron Announcement/Run', a_class_selector))
  rules.append(Rules.PathExistsMatchRule('/model/Cron Execution/Job', b_class_selector))

  time_correlation_violation_detector = TimeCorrelationViolationDetector(analysis_context.aminer_config, rules, anomaly_event_handlers)
  analysis_context.register_component(time_correlation_violation_detector, component_name="TimeCorrelationViolationDetector")
  atom_filter.add_handler(time_correlation_violation_detector)
