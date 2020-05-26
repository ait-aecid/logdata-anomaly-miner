# This is a template for the "aminer" logdata-anomaly-miner tool. Copy
# it to "config.py" and define your ruleset.

config_properties = {}

# Define the list of log resources to read from: the resources
# named here do not need to exist when aminer is started. This
# will just result in a warning. However if they exist, they have
# to be readable by the aminer process! Supported types are:
# * file://[path]: Read data from file, reopen it after rollover
# * unix://[path]: Open the path as UNIX local socket for reading
config_properties['LogResourceList'] = ['file:///var/log/apache2/access.log']

# Define the uid/gid of the process that runs the calculation
# after opening the log files:
config_properties['AMinerUser'] = 'aminer'
config_properties['AMinerGroup'] = 'aminer'

learn_mode = True

# Read and store information to be used between multiple invocations
# of AMiner in this directory. The directory must only be accessible
# to the 'AMinerUser' but not group/world readable. On violation,
# AMiner will refuse to start. When undefined, '/var/lib/aminer'
# is used.
# config_properties['Core.PersistenceDir'] = '/var/lib/aminer'

# Add your ruleset here:


def build_analysis_pipeline(analysis_context):
    """Define the function to create pipeline for parsing the log
    data. It has also to define an AtomizerFactory to instruct AMiner
    how to process incoming data streams to create log atoms from
    them."""

    # Build the parsing model:
    from aminer.parsing import SequenceModelElement

    import ApacheAccessModel
    apache_access_model = ApacheAccessModel.get_model()

    parsing_model = SequenceModelElement('model', [apache_access_model])

    # Some generic imports.
    from aminer.analysis import AtomFilters

    # Create all global handler lists here and append the real handlers
    # later on.
    # Use this filter to distribute all atoms to the analysis handlers.
    atom_filter = AtomFilters.SubhandlerFilter(None)
    anomaly_event_handlers = []

    # Now define the AtomizerFactory using the model. A simple line
    # based one is usually sufficient.
    from aminer.input import SimpleByteStreamLineAtomizerFactory
    analysis_context.atomizer_factory = SimpleByteStreamLineAtomizerFactory(
        parsing_model, [atom_filter], anomaly_event_handlers, default_timestamp_paths='/model/accesslog/time')

    # Just report all unparsed atoms to the event handlers.
    from aminer.input import SimpleUnparsedAtomHandler
    atom_filter.add_handler(SimpleUnparsedAtomHandler(anomaly_event_handlers), stop_when_handled_flag=True)

    from aminer.analysis import NewMatchPathDetector
    new_match_path_detector = NewMatchPathDetector(analysis_context.aminer_config, anomaly_event_handlers, auto_include_flag=learn_mode)
    analysis_context.register_component(new_match_path_detector, component_name=None)
    atom_filter.add_handler(new_match_path_detector)

    # Check if status-code changed
    from aminer.analysis import NewMatchPathValueDetector
    new_match_path_value_detector = NewMatchPathValueDetector(
        analysis_context.aminer_config, ["/model/accesslog/status"], anomaly_event_handlers, auto_include_flag=learn_mode)
    analysis_context.register_component(new_match_path_value_detector, component_name=None)
    atom_filter.add_handler(new_match_path_value_detector)

    # Check if HTTP-Method for a HTTP-Request has changed
    from aminer.analysis import NewMatchPathValueComboDetector
    new_match_path_value_combo_detector = NewMatchPathValueComboDetector(analysis_context.aminer_config, [
        "/model/accesslog/request", "/model/accesslog/method"], anomaly_event_handlers, auto_include_flag=learn_mode)
    analysis_context.register_component(new_match_path_value_combo_detector, component_name=None)
    atom_filter.add_handler(new_match_path_value_combo_detector)

    # Check if HTTP-Statuscode for a HTTP-Request has changed
    new_match_path_value_combo_detector2 = NewMatchPathValueComboDetector(analysis_context.aminer_config, [
        "/model/accesslog/request", "/model/accesslog/status"], anomaly_event_handlers, auto_include_flag=learn_mode)
    analysis_context.register_component(new_match_path_value_combo_detector2, component_name=None)
    atom_filter.add_handler(new_match_path_value_combo_detector2)

    # Add stdout stream printing for debugging, tuning.
    from aminer.events import StreamPrinterEventHandler
    anomaly_event_handlers.append(StreamPrinterEventHandler(analysis_context))
