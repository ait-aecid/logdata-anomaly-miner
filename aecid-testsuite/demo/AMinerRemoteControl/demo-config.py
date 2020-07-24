from aminer.parsing import FirstMatchModelElement, SequenceModelElement, FixedDataModelElement, DelimitedDataModelElement, \
    AnyByteDataModelElement, FixedWordlistDataModelElement, DecimalIntegerValueModelElement, DateTimeModelElement, \
    IpAddressDataModelElement, OptionalMatchModelElement

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
config_properties['Resources.MaxMemoryUsage'] = 64

# Add your ruleset here:


def build_analysis_pipeline(analysis_context):
    """Define the function to create pipeline for parsing the log
    data. It has also to define an AtomizerFactory to instruct AMiner
    how to process incoming data streams to create log atoms from
    them."""

    # Build the parsing model:

    service_children_disk_report = [
        FixedDataModelElement('Space', b' Current Disk Data is: Filesystem     Type  Size  Used Avail Use%'),
        DelimitedDataModelElement('Data', b'%'), AnyByteDataModelElement('Rest')]

    service_children_login_details = [
        FixedDataModelElement('User', b'User '), DelimitedDataModelElement('Username', b' '),
        FixedWordlistDataModelElement('Status', [b' logged in', b' logged out']),
        OptionalMatchModelElement('PastTime', SequenceModelElement('Time', [
            FixedDataModelElement('Blank', b' '), DecimalIntegerValueModelElement('Minutes'),
            FixedDataModelElement('Ago', b' minutes ago.')]))]

    service_children_cron_job = [
        DateTimeModelElement('DTM', b'%Y-%m-%d %H:%M:%S'), FixedDataModelElement('UNameSpace1', b' '),
        DelimitedDataModelElement('UName', b' '), FixedDataModelElement('UNameSpace2', b' '), DelimitedDataModelElement('User', b' '),
        FixedDataModelElement('Cron', b' cron['), DecimalIntegerValueModelElement('JobNumber'),
        FixedDataModelElement('Details', b']: Job `cron.daily` started.')]

    service_children_random_time = [FixedDataModelElement('Space', b'Random: '), DecimalIntegerValueModelElement('Random')]

    service_children_sensors = [SequenceModelElement('CPUTemp', [
        FixedDataModelElement('FixedTemp', b'CPU Temp: '), DecimalIntegerValueModelElement('Temp'),
        FixedDataModelElement('Degrees', b'\xc2\xb0C')]), FixedDataModelElement('Space1', b', '), SequenceModelElement('CPUWorkload', [
            FixedDataModelElement('FixedWorkload', b'CPUWorkload: '), DecimalIntegerValueModelElement('Workload'),
            FixedDataModelElement('Percent', b'%')]), FixedDataModelElement('Space2', b', '),
        DateTimeModelElement('DTM', b'%Y-%m-%d %H:%M:%S')]

    service_children_user_ip_address = [
        FixedDataModelElement('User', b'User '), DelimitedDataModelElement('Username', b' '),
        FixedDataModelElement('Action', b' changed IP address to '), IpAddressDataModelElement('IP')]

    service_children_cron_job_announcement = [
        DateTimeModelElement('DTM', b'%Y-%m-%d %H:%M:%S'), FixedDataModelElement('Space', b' '),
        DelimitedDataModelElement('UName', b' '), FixedDataModelElement('Cron', b' cron['), DecimalIntegerValueModelElement('JobNumber'),
        FixedDataModelElement('Run', b']: Will run job `'),
        FixedWordlistDataModelElement('CronType', [b'cron.daily', b'cron.hourly', b'cron.monthly', b'cron.weekly']),
        FixedDataModelElement('StartTime', b'\' in 5 min.')]

    service_children_cron_job_execution = [
        DateTimeModelElement('DTM', b'%Y-%m-%d %H:%M:%S'), FixedDataModelElement('Space1', b' '),
        DelimitedDataModelElement('UName', b' '), FixedDataModelElement('Cron', b' cron['), DecimalIntegerValueModelElement('JobNumber'),
        FixedDataModelElement('Job', b']: Job `'),
        FixedWordlistDataModelElement('CronType', [b'cron.daily', b'cron.hourly', b'cron.monthly', b'cron.weekly']),
        FixedDataModelElement('Started', b'\' started')]

    parsing_model = FirstMatchModelElement('model', [
        SequenceModelElement('CronAnnouncement', service_children_cron_job_announcement),
        SequenceModelElement('CronExecution', service_children_cron_job_execution),
        SequenceModelElement('DailyCron', service_children_cron_job), SequenceModelElement('DiskReport', service_children_disk_report),
        SequenceModelElement('LoginDetails', service_children_login_details), DecimalIntegerValueModelElement('Random'),
        SequenceModelElement('RandomTime', service_children_random_time), SequenceModelElement('Sensors', service_children_sensors),
        SequenceModelElement('IPAddresses', service_children_user_ip_address)])

    # Some generic imports.
    from aminer.analysis import AtomFilters

    # Create all global handler lists here and append the real handlers later on.
    # Use this filter to distribute all atoms to the analysis handlers.
    atom_filters = AtomFilters.SubhandlerFilter(None)
    analysis_context.register_component(atom_filters, component_name="AtomFilter")

    from aminer.analysis.TimestampCorrectionFilters import SimpleMonotonicTimestampAdjust
    simple_monotonic_timestamp_adjust = SimpleMonotonicTimestampAdjust([atom_filters])
    analysis_context.register_component(simple_monotonic_timestamp_adjust, component_name="SimpleMonotonicTimestampAdjust")

    from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
    stream_printer_event_handler = StreamPrinterEventHandler(analysis_context)
    from aminer.events.Utils import VolatileLogarithmicBackoffEventHistory
    volatile_logarithmic_backoff_event_history = VolatileLogarithmicBackoffEventHistory(100)
    anomaly_event_handlers = [stream_printer_event_handler, volatile_logarithmic_backoff_event_history]
    analysis_context.register_component(volatile_logarithmic_backoff_event_history, component_name="VolatileLogarithmicBackoffEventHistory")

    # Now define the AtomizerFactory using the model. A simple line based one is usually sufficient.
    from aminer.input import SimpleByteStreamLineAtomizerFactory
    analysis_context.atomizer_factory = SimpleByteStreamLineAtomizerFactory(parsing_model, [simple_monotonic_timestamp_adjust],
                                                                            anomaly_event_handlers)

    # Just report all unparsed atoms to the event handlers.
    from aminer.input import SimpleUnparsedAtomHandler
    simple_unparsed_atom_handler = SimpleUnparsedAtomHandler(anomaly_event_handlers)
    atom_filters.add_handler(simple_unparsed_atom_handler, stop_when_handled_flag=True)
    analysis_context.register_component(simple_unparsed_atom_handler, component_name="UnparsedHandler")

    from aminer.analysis.TimestampsUnsortedDetector import TimestampsUnsortedDetector
    timestamps_unsorted_detector = TimestampsUnsortedDetector(analysis_context.aminer_config, anomaly_event_handlers)
    atom_filters.add_handler(timestamps_unsorted_detector)
    analysis_context.register_component(timestamps_unsorted_detector, component_name="TimestampsUnsortedDetector")

    from aminer.analysis import Rules
    from aminer.analysis import WhitelistViolationDetector
    whitelist_rules = [
        Rules.OrMatchRule([
            Rules.AndMatchRule([
                Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes'),
                Rules.NegationMatchRule(Rules.ValueMatchRule('/model/LoginDetails/Username', b'root'))]),
            Rules.AndMatchRule([
                Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes')),
                Rules.PathExistsMatchRule('/model/LoginDetails')]),
            Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/LoginDetails'))])]

    # This rule list should trigger, when the line does not look like: User root (logged in, logged out)
    # or User 'username' (logged in, logged out) x minutes ago.
    whitelist_violation_detector = WhitelistViolationDetector(analysis_context.aminer_config, whitelist_rules, anomaly_event_handlers)
    analysis_context.register_component(whitelist_violation_detector, component_name="Whitelist")
    atom_filters.add_handler(whitelist_violation_detector)

    from aminer.analysis import ParserCount
    parser_count = ParserCount(analysis_context.aminer_config, None, anomaly_event_handlers, 10, False)
    analysis_context.register_component(parser_count, component_name="ParserCount")
    atom_filters.add_handler(parser_count)

    from aminer.analysis import NewMatchPathDetector
    new_match_path_detector = NewMatchPathDetector(analysis_context.aminer_config, anomaly_event_handlers, auto_include_flag=False)
    analysis_context.register_component(new_match_path_detector, component_name="NewMatchPath")
    atom_filters.add_handler(new_match_path_detector)

    def tuple_transformation_function(match_value_list):
        extra_data = enhanced_new_match_path_value_combo_detector.known_values_dict.get(tuple(match_value_list), None)
        if extra_data is not None:
            mod = 10000
            if (extra_data[2] + 1) % mod == 0:
                enhanced_new_match_path_value_combo_detector.auto_include_flag = False
            else:
                enhanced_new_match_path_value_combo_detector.auto_include_flag = True
        return match_value_list

    from aminer.analysis.EnhancedNewMatchPathValueComboDetector import EnhancedNewMatchPathValueComboDetector
    enhanced_new_match_path_value_combo_detector = EnhancedNewMatchPathValueComboDetector(
        analysis_context.aminer_config, ['/model/DailyCron/UName', '/model/DailyCron/JobNumber'], anomaly_event_handlers,
        auto_include_flag=False, tuple_transformation_function=tuple_transformation_function)
    analysis_context.register_component(enhanced_new_match_path_value_combo_detector, component_name="EnhancedNewValueCombo")
    atom_filters.add_handler(enhanced_new_match_path_value_combo_detector)

    from aminer.analysis.HistogramAnalysis import HistogramAnalysis, LinearNumericBinDefinition, ModuloTimeBinDefinition, \
        PathDependentHistogramAnalysis
    modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 3600, 0, 1, 24, True)
    linear_numeric_bin_definition = LinearNumericBinDefinition(50, 5, 20, True)
    histogram_analysis = HistogramAnalysis(analysis_context.aminer_config, [
        ('/model/RandomTime/Random', modulo_time_bin_definition), ('/model/Random', linear_numeric_bin_definition)], 10,
        anomaly_event_handlers)
    analysis_context.register_component(histogram_analysis, component_name="HistogramAnalysis")
    atom_filters.add_handler(histogram_analysis)

    path_dependent_histogram_analysis = PathDependentHistogramAnalysis(analysis_context.aminer_config, '/model/RandomTime',
                                                                       modulo_time_bin_definition, 10, anomaly_event_handlers)
    analysis_context.register_component(path_dependent_histogram_analysis, component_name="PathDependentHistogramAnalysis")
    atom_filters.add_handler(path_dependent_histogram_analysis)

    from aminer.analysis.MatchValueAverageChangeDetector import MatchValueAverageChangeDetector
    match_value_average_change_detector = MatchValueAverageChangeDetector(analysis_context.aminer_config, anomaly_event_handlers, None,
                                                                          ['/model/Random'], 100, 10)
    analysis_context.register_component(match_value_average_change_detector, component_name="MatchValueAverageChange")
    atom_filters.add_handler(match_value_average_change_detector)

    import sys
    from aminer.analysis.MatchValueStreamWriter import MatchValueStreamWriter
    match_value_stream_writer = MatchValueStreamWriter(
        sys.stdout, ['/model/Sensors/CPUTemp', '/model/Sensors/CPUWorkload', '/model/Sensors/DTM'], b';', b'')
    analysis_context.register_component(match_value_stream_writer, component_name="MatchValueStreamWriter")
    atom_filters.add_handler(match_value_stream_writer)

    from aminer.analysis.NewMatchPathValueComboDetector import NewMatchPathValueComboDetector
    new_match_path_value_combo_detector = NewMatchPathValueComboDetector(analysis_context.aminer_config, [
        '/model/IPAddresses/Username', '/model/IPAddresses/IP'], anomaly_event_handlers, auto_include_flag=False)
    analysis_context.register_component(new_match_path_value_combo_detector, component_name="NewMatchPathValueCombo")
    atom_filters.add_handler(new_match_path_value_combo_detector)

    from aminer.analysis.NewMatchPathValueDetector import NewMatchPathValueDetector
    new_match_path_value_detector = NewMatchPathValueDetector(analysis_context.aminer_config, [
        '/model/DailyCron/Job Number', '/model/IPAddresses/Username'], anomaly_event_handlers, auto_include_flag=False)
    analysis_context.register_component(new_match_path_value_detector, component_name="NewMatchPathValue")
    atom_filters.add_handler(new_match_path_value_detector)

    from aminer.analysis.MissingMatchPathValueDetector import MissingMatchPathValueDetector
    missing_match_path_value_detector = MissingMatchPathValueDetector(
        analysis_context.aminer_config, '/model/DiskReport/Space', anomaly_event_handlers, auto_include_flag=False, default_interval=2,
        realert_interval=5)
    analysis_context.register_component(missing_match_path_value_detector, component_name="MissingMatch")
    atom_filters.add_handler(missing_match_path_value_detector)

    from aminer.analysis.TimeCorrelationDetector import TimeCorrelationDetector
    time_correlation_detector = TimeCorrelationDetector(
        analysis_context.aminer_config, anomaly_event_handlers, 2, min_rule_attributes=1, max_rule_attributes=5,
        record_count_before_event=70000, output_log_line=True)
    analysis_context.register_component(time_correlation_detector, component_name="TimeCorrelationDetector")
    atom_filters.add_handler(time_correlation_detector)

    from aminer.analysis.TimeCorrelationViolationDetector import TimeCorrelationViolationDetector, CorrelationRule, EventClassSelector
    cron_job_announcement = CorrelationRule('CronJobAnnouncement', 5, 6, max_artefacts_a_for_single_b=1, artefact_match_parameters=[
        ('/model/CronAnnouncement/JobNumber', '/model/CronExecution/JobNumber')])
    a_class_selector = EventClassSelector('Announcement', [cron_job_announcement], None)
    b_class_selector = EventClassSelector('Execution', None, [cron_job_announcement])
    rules = [Rules.PathExistsMatchRule('/model/CronAnnouncement/Run', a_class_selector),
             Rules.PathExistsMatchRule('/model/CronExecution/Job', b_class_selector)]

    time_correlation_violation_detector = TimeCorrelationViolationDetector(analysis_context.aminer_config, rules, anomaly_event_handlers)
    analysis_context.register_component(time_correlation_violation_detector, component_name="TimeCorrelationViolationDetector")
    atom_filters.add_handler(time_correlation_violation_detector)

    from aminer.events import DefaultMailNotificationEventHandler
    if DefaultMailNotificationEventHandler.CONFIG_KEY_MAIL_TARGET_ADDRESS in analysis_context.aminer_config.config_properties:
        mail_notification_handler = DefaultMailNotificationEventHandler(analysis_context)
        analysis_context.register_component(mail_notification_handler, component_name="MailHandler")
        anomaly_event_handlers.append(mail_notification_handler)
