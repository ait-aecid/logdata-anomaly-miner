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
# config_properties['RemoteControlSocket'] = '/var/run/aminer-remote.socket'

# Read the analyis from this file. That part of configuration
# is separated from the main configuration so that it can be loaded
# only within the analysis child. Non-absolute path names are
# interpreted relatively to the main configuration file (this
# file). When empty, this configuration has to contain the configuration
# for the child also.
# config_properties['AnalysisConfigFile'] = 'analysis.py'

# Read and store information to be used between multiple invocations
# of py in this directory. The directory must only be accessible
# to the 'AMinerUser' but not group/world readable. On violation,
# py will refuse to start. When undefined, '/var/lib/aminer'
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
# subject. Defaults to "py Alerts:"
config_properties['MailAlerting.SubjectPrefix'] = 'AMiner Alerts:'
# Define a grace time after startup before aminer will react to
# an event and send the first alert e-mail. Defaults to 0 (any
# event can immediately trigger alerting).
config_properties['MailAlerting.AlertGraceTime'] = 0
# Define how many seconds to wait after a first event triggered
# the alerting procedure before really sending out the e-mail.
# In that timespan, events are collected and will be sent all
# using a single e-mail. Defaults to 10 seconds.
config_properties['MailAlerting.EventCollectTime'] = 10
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
# config_properties['LogPrefix'] = 'Original log line: '

# Add your ruleset here:


def build_analysis_pipeline(analysis_context):
    """Define the function to create pipeline for parsing the log data. It has also to define an AtomizerFactory to instruct py
    how to process incoming data streams to create log atoms from them."""

    # Build the parsing model:
    from aminer.parsing import FirstMatchModelElement
    from aminer.parsing import SequenceModelElement
    from aminer.parsing.DateTimeModelElement import DateTimeModelElement
    from aminer.parsing import FixedDataModelElement
    from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
    from aminer.parsing import AnyByteDataModelElement

    service_children_disk_upgrade = [
        DateTimeModelElement('Date', b'%d.%m.%Y %H:%M:%S'), FixedDataModelElement('UName', b' ubuntu '),
        DelimitedDataModelElement('User', b' '), FixedDataModelElement('HD Repair', b' System rebooted for hard disk upgrade')]

    service_children_home_path = [
        FixedDataModelElement('Pwd', b'The Path of the home directory shown by pwd of the user '),
        DelimitedDataModelElement('Username', b' '), FixedDataModelElement('Is', b' is: '), AnyByteDataModelElement('Path')]

    parsing_model = FirstMatchModelElement('model', [
        SequenceModelElement('Disk Upgrade', service_children_disk_upgrade),
        SequenceModelElement('Home Path', service_children_home_path)])

    # Some generic imports.
    from aminer.analysis import AtomFilters

    # Create all global handler lists here and append the real handlers later on.
    # Use this filter to distribute all atoms to the analysis handlers.
    atom_filter = AtomFilters.SubhandlerFilter(None)

    from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
    stream_printer_event_handler = StreamPrinterEventHandler(None)
    anomaly_event_handlers = [stream_printer_event_handler]

    # Now define the AtomizerFactory using the model. A simple line based one is usually sufficient.
    from aminer.input import SimpleByteStreamLineAtomizerFactory
    analysis_context.atomizer_factory = SimpleByteStreamLineAtomizerFactory(
        parsing_model, [atom_filter], anomaly_event_handlers, default_timestamp_paths=[''])

    # Just report all unparsed atoms to the event handlers.
    from aminer.input import SimpleUnparsedAtomHandler
    atom_filter.add_handler(SimpleUnparsedAtomHandler(anomaly_event_handlers), stop_when_handled_flag=True)

    from aminer.analysis import NewMatchPathDetector
    new_match_path_detector = NewMatchPathDetector(analysis_context.aminerConfig, anomaly_event_handlers, auto_include_flag=True)
    analysis_context.register_component(new_match_path_detector, component_name=None)
    atom_filter.add_handler(new_match_path_detector)

    from aminer.analysis import NewMatchPathValueComboDetector
    new_match_path_value_combo_detector = NewMatchPathValueComboDetector(analysis_context.aminerConfig, [
        '/model/Home Path/Username', '/model/Home Path/Path'], anomaly_event_handlers, auto_include_flag=True)
    analysis_context.register_component(new_match_path_value_combo_detector, component_name=None)
    atom_filter.add_handler(new_match_path_value_combo_detector)

    # Include the e-mail notification handler only if the configuration parameter was set.
    from aminer.events import DefaultMailNotificationEventHandler
    if DefaultMailNotificationEventHandler.CONFIG_KEY_MAIL_TARGET_ADDRESS in analysis_context.aminerConfig.config_properties:
        mail_notification_handler = DefaultMailNotificationEventHandler(analysis_context.aminerConfig)
        analysis_context.register_component(mail_notification_handler, component_name=None)
        anomaly_event_handlers.append(mail_notification_handler)
