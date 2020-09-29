""" This file loads and parses a config-file in yaml format.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""
config_properties = {}
yaml_data = None

# Define the list of log resources to read from: the resources
# named here do not need to exist when aminer is started. This
# will just result in a warning. However if they exist, they have
# to be readable by the aminer process! Supported types are:
# * file://[path]: Read data from file, reopen it after rollover
# * unix://[path]: Open the path as UNIX local socket for reading
config_properties['LogResourceList'] = []

# Define the uid/gid of the process that runs the calculation
# after opening the log files:
config_properties['AMinerUser'] = 'aminer'
config_properties['AMinerGroup'] = 'aminer'


# This method loads the yaml-configfile and overrides defaults if neccessary
def load_yaml(config_file):
    # We might be able to remove this and us it like the config_properties
    # skipcq: PYL-W0603
    global yaml_data

    import yaml
    from aminer.ConfigValidator import ConfigValidator
    import os
    with open(config_file) as yamlfile:
        try:
            yaml_data = yaml.safe_load(yamlfile)
            yamlfile.close()
        except yaml.YAMLError as exception:
            raise exception

    with open(os.path.dirname(os.path.abspath(__file__)) + '/' + 'schema.py', 'r') as sma:
        # skipcq: PYL-W0123
        schema = eval(sma.read())
    sma.close()

    v = ConfigValidator(schema)
    if v.validate(yaml_data, schema):
        test = v.normalized(yaml_data)
        yaml_data = test
    else:
        raise ValueError(v.errors)

    # Set default values
    for key, val in yaml_data.items():
        config_properties[str(key)] = val


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
    # skipcq: PYL-W0611
    import importlib
    # skipcq: PYL-W0611
    # import configparser
    # skipcq: PYL-W0611
    import sys

    parser_model_dict = {}
    start = None
    ws_count = 0
    whitespace_str = b' '

    # We might be able to remove this and us it like the config_properties
    # skipcq: PYL-W0603
    global yaml_data
    for item in yaml_data['Parser']:
        if 'start' in item and item['start'] is True:
            start = item
            continue
        if item['type'].is_model:
            if 'args' in item:
                if isinstance(item['args'], list):
                    # encode string to bytearray
                    for j in range(len(item['args'])):
                        item['args'][j] = item['args'][j].encode()
                    parser_model_dict[item['id']] = item['type'].func(item['name'], item['args'])
                else:
                    parser_model_dict[item['id']] = item['type'].func(item['name'], item['args'].encode())
            else:
                parser_model_dict[item['id']] = item['type'].func(item['name'])
        else:
            parser_model_dict[item['id']] = item['type'].func()

    args_list = []
    if 'args' in start:
        if isinstance(start['args'], list):
            for i in start['args']:
                if i == 'WHITESPACE':
                    from aminer.parsing import FixedDataModelElement
                    sp = 'sp%d' % ws_count
                    args_list.append(FixedDataModelElement(sp, whitespace_str))
                    ws_count += 1
                else:
                    args_list.append(parser_model_dict[i])
            parsing_model = start['type'].func(start['name'], args_list)
        else:
            parsing_model = start['type'].func(start['name'], [parser_model_dict[start['args']]])
    else:
        parsing_model = start['type'].func()

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
    if yaml_data['Input']['multi_source'] is True:
        from aminer.input import SimpleMultisourceAtomSync
        analysis_context.atomizer_factory = SimpleByteStreamLineAtomizerFactory(
            parsing_model, [SimpleMultisourceAtomSync([atom_filter], sync_wait_time=5)],
            anomaly_event_handlers, default_timestamp_paths=yaml_data['Input']['timestamp_path'])
    else:
        analysis_context.atomizer_factory = SimpleByteStreamLineAtomizerFactory(
            parsing_model, [atom_filter], anomaly_event_handlers,
            default_timestamp_paths=yaml_data['Input']['timestamp_path'])

# Just report all unparsed atoms to the event handlers.
    if yaml_data['Input']['verbose'] is True:
        from aminer.input import VerboseUnparsedAtomHandler
        atom_filter.add_handler(
            VerboseUnparsedAtomHandler(anomaly_event_handlers, parsing_model),
            stop_when_handled_flag=True)
    else:
        from aminer.input import SimpleUnparsedAtomHandler
        atom_filter.add_handler(
            SimpleUnparsedAtomHandler(anomaly_event_handlers),
            stop_when_handled_flag=True)

    from aminer.analysis import NewMatchPathDetector
    if 'learn_mode' in yaml_data:
        learn = yaml_data['learn_mode']
    else:
        learn = True
    nmpd = NewMatchPathDetector(
        analysis_context.aminer_config, anomaly_event_handlers, auto_include_flag=learn)
    analysis_context.register_component(nmpd, component_name=None)
    atom_filter.add_handler(nmpd)

    if 'Analysis' in yaml_data and yaml_data['Analysis'] is not None:
        analysis_dict = {}
        match_action_dict = {}
        match_rules_dict = {}
        correlation_rules = {}
        for item in yaml_data['Analysis']:
            if item['id'] == 'None':
                comp_name = None
            else:
                comp_name = item['id']
            if 'learn_mode' in yaml_data:
                learn = yaml_data['learn_mode']
            else:
                learn = item['output_log_line']
            func = getattr(__import__("aminer.analysis", fromlist=[item['type']]), item['type'])
            if item['type'] == 'NewMatchPathValueDetector':
                tmp_analyser = func(
                    analysis_context.aminer_config,
                    item['paths'], anomaly_event_handlers, auto_include_flag=learn,
                    persistence_id=item['persistence_id'],
                    output_log_line=learn)
            elif item['type'] == 'MatchPathFilter':
                parsed_atom_handler_lookup_list = []
                for atom_handler in item['parsed_atom_handler_lookup_list']:
                    if atom_handler[1] is not None:
                        if analysis_context.get_component_by_id(atom_handler[1]) is None:
                            raise ValueError('The atom handler %s does not exist!' % atom_handler[1])
                        atom_handler[1] = analysis_context.get_component_by_id(atom_handler[1])
                    parsed_atom_handler_lookup_list.append(tuple(i for i in atom_handler))
                default_parsed_atom_handler = item['default_parsed_atom_handler']
                if default_parsed_atom_handler is not None:
                    if analysis_context.get_component_by_id(default_parsed_atom_handler) is None:
                        raise ValueError('The atom handler %s does not exist!' % default_parsed_atom_handler)
                    default_parsed_atom_handler = analysis_context.get_component_by_id(default_parsed_atom_handler)
                tmp_analyser = func(
                    parsed_atom_handler_lookup_list,
                    default_parsed_atom_handler=default_parsed_atom_handler)
            elif item['type'] == 'MatchValueFilter':
                parsed_atom_handler_dict = {}
                for atom_handler in item['parsed_atom_handler_dict']:
                    if analysis_context.get_component_by_id(atom_handler) is None:
                        raise ValueError('The atom handler %s does not exist!' % atom_handler)
                    parsed_atom_handler_dict[atom_handler] = analysis_context.get_component_by_id(atom_handler)
                default_parsed_atom_handler = item['default_parsed_atom_handler']
                if default_parsed_atom_handler is not None:
                    if analysis_context.get_component_by_id(default_parsed_atom_handler) is None:
                        raise ValueError('The atom handler %s does not exist!' % default_parsed_atom_handler)
                    default_parsed_atom_handler = analysis_context.get_component_by_id(default_parsed_atom_handler)
                tmp_analyser = func(
                    item['path'],
                    parsed_atom_handler_dict,
                    default_parsed_atom_handler=default_parsed_atom_handler)
            elif item['type'] == 'NewMatchPathValueComboDetector':
                tmp_analyser = func(
                    analysis_context.aminer_config, item['paths'],
                    anomaly_event_handlers, auto_include_flag=learn,
                    persistence_id=item['persistence_id'],
                    allow_missing_values_flag=item['allow_missing_values'],
                    output_log_line=learn)
            elif item['type'] == 'MissingMatchPathValueDetector':
                tmp_analyser = func(
                    analysis_context.aminer_config, item['path'],
                    anomaly_event_handlers, auto_include_flag=learn,
                    persistence_id=item['persistence_id'],
                    default_interval=item['check_interval'],
                    realert_interval=item['realert_interval'],
                    output_log_line=learn)
            elif item['type'] == 'MissingMatchPathListValueDetector':
                tmp_analyser = func(
                    analysis_context.aminer_config, item['path'],
                    anomaly_event_handlers, auto_include_flag=learn,
                    persistence_id=item['persistence_id'],
                    default_interval=item['check_interval'],
                    realert_interval=item['realert_interval'],
                    output_log_line=learn)
            elif item['type'] == 'TimeCorrelationDetector':
                tmp_analyser = func(
                    analysis_context.aminer_config, anomaly_event_handlers,
                    parallel_check_count=item['parallel_check_count'],
                    persistence_id=item['persistence_id'],
                    record_count_before_event=item['record_count_before_event'],
                    output_log_line=learn,
                    use_path_match=item['use_path_match'],
                    use_value_match=item['use_value_match'],
                    min_rule_attributes=item['min_rule_attributes'],
                    max_rule_attributes=item['max_rule_attributes'])
            elif item['type'] == 'ParserCount':
                tmp_analyser = func(
                    analysis_context.aminer_config,
                    item['paths'],
                    report_interval=item['report_interval'],
                    report_event_handlers=anomaly_event_handlers,
                    reset_after_report_flag=item['reset_after_report_flag'])
            elif item['type'] == 'EventCorrelationDetector':
                tmp_analyser = func(
                    analysis_context.aminer_config, anomaly_event_handlers,
                    paths=item['paths'],
                    max_hypotheses=item['max_hypotheses'],
                    hypothesis_max_delta_time=item['hypothesis_max_delta_time'],
                    generation_probability=item['generation_probability'],
                    generation_factor=item['generation_factor'],
                    max_observations=item['max_observations'],
                    p0=item['p0'],
                    alpha=item['alpha'],
                    candidates_size=item['candidates_size'],
                    hypotheses_eval_delta_time=item['hypotheses_eval_delta_time'],
                    delta_time_to_discard_hypothesis=item['delta_time_to_discard_hypothesis'],
                    check_rules_flag=item['check_rules_flag'],
                    auto_include_flag=item['auto_include_flag'],
                    # whitelisted_paths=item['whitelisted_paths'],
                    persistence_id=item['persistence_id'])
            elif item['type'] == 'NewMatchIdValueComboDetector':
                tmp_analyser = func(
                    analysis_context.aminer_config,
                    item['paths'],
                    anomaly_event_handlers,
                    id_path_list=item['id_path_list'],
                    min_allowed_time_diff=item['min_allowed_time_diff'],
                    auto_include_flag=learn,
                    persistence_id=item['persistence_id'],
                    allow_missing_values_flag=item['allow_missing_values'],
                    output_log_line=learn)
            elif item['type'] == 'LinearNumericBinDefinition':
                if comp_name is None:
                    raise ValueError('The %s must have an id!' % item['type'])
                analysis_dict[comp_name] = func(
                    item['lower_limit'],
                    item['bin_size'],
                    item['bin_count'],
                    item['outlier_bins_flag'])
                continue
            elif item['type'] == 'ModuloTimeBinDefinition':
                if comp_name is None:
                    raise ValueError('The %s must have an id!' % item['type'])
                analysis_dict[comp_name] = func(
                    item['modulo_value'],
                    item['time_unit'],
                    item['lower_limit'],
                    item['bin_size'],
                    item['bin_count'],
                    item['outlier_bins_flag'])
                continue
            elif item['type'] == 'HistogramAnalysis':
                histogram_defs = []
                for histogram_def in item['histogram_defs']:
                    if len(histogram_def) != 2:
                        raise ValueError('Every item of the histogram_defs must have an size of 2!')
                    if histogram_def[1] not in analysis_dict:
                        raise ValueError('%s first must be defined before used.' % histogram_def[1])
                    histogram_defs.append([histogram_def[0], analysis_dict[histogram_def[1]]])
                tmp_analyser = func(
                    analysis_context.aminer_config,
                    histogram_defs,
                    item['report_interval'],
                    anomaly_event_handlers,
                    reset_after_report_flag=item['reset_after_report_flag'],
                    persistence_id=item['persistence_id'],
                    output_log_line=learn)
            elif item['type'] == 'PathDependentHistogramAnalysis':
                if item['bin_definition'] not in analysis_dict:
                    raise ValueError('%s first must be defined before used.' % item['bin_definition'])
                tmp_analyser = func(
                    analysis_context.aminer_config,
                    item['path'],
                    analysis_dict[item['bin_definition']],
                    item['report_interval'],
                    anomaly_event_handlers,
                    reset_after_report_flag=item['reset_after_report_flag'],
                    persistence_id=item['persistence_id'],
                    output_log_line=learn)
            elif item['type'] == 'EnhancedNewMatchPathValueComboDetector':
                tuple_transformation_function = None
                if item['tuple_transformation_function'] == 'demo':
                    tuple_transformation_function = tuple_transformation_function_demo_print_every_10th_value
                tmp_analyser = func(
                    analysis_context.aminer_config,
                    item['paths'],
                    anomaly_event_handlers,
                    persistence_id=item['persistence_id'],
                    allow_missing_values_flag=item['allow_missing_values'],
                    auto_include_flag=learn,
                    tuple_transformation_function=tuple_transformation_function,
                    output_log_line=learn)
            elif item['type'] == 'MatchFilter':
                tmp_analyser = func(
                    analysis_context.aminer_config,
                    item['paths'],
                    anomaly_event_handlers,
                    target_value_list=item['value_list'],
                    output_log_line=learn)
            elif item['type'] == 'MatchValueAverageChangeDetector':
                tmp_analyser = func(
                    analysis_context.aminer_config,
                    anomaly_event_handlers,
                    item['timestamp_path'],
                    item['paths'],
                    item['min_bin_elements'],
                    item['min_bin_time'],
                    sync_bins_flag=item['sync_bins_flag'],
                    debug_mode=item['debug_mode'],
                    persistence_id=item['persistence_id'],
                    output_log_line=learn)
            elif item['type'] == 'MatchValueStreamWriter':
                stream = sys.stdout
                if item['stream'] == 'sys.stderr':
                    stream = sys.stderr
                tmp_analyser = func(
                    stream,
                    item['paths'],
                    item['separator'].encode(),
                    item['missing_value_string'].encode())
            elif item['type'] == 'NewMatchPathDetector':
                tmp_analyser = func(
                    analysis_context.aminer_config,
                    anomaly_event_handlers,
                    persistence_id=item['persistence_id'],
                    auto_include_flag=learn,
                    output_log_line=learn)
            elif 'MatchAction' in item['type']:
                if comp_name is None:
                    raise ValueError('The %s must have an id!' % item['type'])
                if item['type'] == 'EventGenerationMatchAction':
                    tmp_analyser = func(
                        item['event_type'],
                        item['event_message'],
                        anomaly_event_handlers)
                elif item['type'] == 'AtomFilterMatchAction':
                    tmp_analyser = func(
                        atom_filter,
                        stop_when_handled_flag=item['stop_when_handled_flag'])
                match_action_dict[comp_name] = tmp_analyser
                continue
            elif 'MatchRule' in item['type']:
                if comp_name is None:
                    raise ValueError('The %s must have an id!' % item['type'])
                match_action = None
                if item['match_action'] is not None:
                    if item['match_action'] not in match_action_dict:
                        raise ValueError('The match action %s does not exist!' % item['match_action'])
                    match_action = match_action_dict[item['match_action']]
                if item['type'] in ('AndMatchRule', 'OrMatchRule', 'ParallelMatchRule'):
                    sub_rules = []
                    for sub_rule in item['sub_rules']:
                        if sub_rule not in match_rules_dict:
                            raise ValueError('The sub match rule %s does not exist!' % sub_rule)
                        sub_rules.append(match_rules_dict[sub_rule])
                    tmp_analyser = func(
                        sub_rules,
                        match_action=match_action)
                if item['type'] == 'ValueDependentDelegatedMatchRule':
                    rule_lookup_dict = {}
                    for rule in item['rule_lookup_dict']:
                        if rule not in match_rules_dict:
                            raise ValueError('The match rule %s does not exist!' % rule)
                        rule_lookup_dict[rule] = match_rules_dict[rule]
                    tmp_analyser = func(
                        item['paths'],
                        rule_lookup_dict,
                        default_rule=item['default_rule'],
                        match_action=match_action)
                if item['type'] == 'NegationMatchRule':
                    if item['sub_rule'] not in match_rules_dict:
                        raise ValueError('The match rule %s does not exist!' % item['sub_rule'])
                    sub_rule = match_rules_dict[item['sub_rule']]
                    tmp_analyser = func(
                        sub_rule,
                        match_action=match_action)
                if item['type'] in ('PathExistsMatchRule', 'IPv4InRFC1918MatchRule'):
                    tmp_analyser = func(
                        item['path'],
                        match_action=match_action)
                if item['type'] == 'ValueMatchRule':
                    if isinstance(item['value'], str):
                        item['value'] = item['value'].encode()
                    tmp_analyser = func(
                        item['path'],
                        item['value'],
                        match_action=match_action)
                if item['type'] == 'ValueListMatchRule':
                    value_list = []
                    for val in item['value_list']:
                        if isinstance(val, str):
                            val = val.encode()
                        value_list.append(val)
                    tmp_analyser = func(
                        item['path'],
                        value_list,
                        match_action=match_action)
                if item['type'] == 'ValueRangeMatchRule':
                    tmp_analyser = func(
                        item['path'],
                        item['lower_limit'],
                        item['upper_limit'],
                        match_action)
                if item['type'] == 'StringRegexMatchRule':
                    tmp_analyser = func(
                        item['path'],
                        item['regex'],
                        match_action=match_action)
                if item['type'] == 'ModuloTimeMatchRule':
                    # tzinfo parameter cannot be used yet..
                    tmp_analyser = func(
                        item['path'],
                        item['seconds_modulo'],
                        item['lower_limit'],
                        item['upper_limit'],
                        match_action=match_action)
                if item['type'] == 'ValueDependentModuloTimeMatchRule':
                    # tzinfo parameter cannot be used yet..
                    tmp_analyser = func(
                        item['path'],
                        item['seconds_modulo'],
                        item['paths'],
                        item['limit_lookup_dict'],
                        default_limit=item['default_limit'],
                        match_action=match_action)
                if item['type'] == 'DebugMatchRule':
                    tmp_analyser = func(
                        debug_match_result=item['debug_mode'],
                        match_action=match_action)
                if item['type'] == 'DebugHistoryMatchRule':
                    # object_history is not supported yet..
                    tmp_analyser = func(
                        debug_match_result=item['debug_mode'],
                        match_action=match_action)
                match_rules_dict[comp_name] = tmp_analyser
                continue
            elif item['type'] == 'CorrelationRule':
                artefact_match_parameters = []
                for match_parameters in item['artefact_match_parameters']:
                    artefact_match_parameters.append(tuple(i for i in match_parameters))
                tmp_analyser = func(
                    item['rule_id'],
                    item['min_time_delta'],
                    item['max_time_delta'],
                    item['max_artefacts_a_for_single_b'],
                    artefact_match_parameters=artefact_match_parameters)
                correlation_rules[item['rule_id']] = tmp_analyser
                continue
            elif item['type'] == 'EventClassSelector':
                if item['artefact_a_rules'] is None and item['artefact_b_rules'] is None:
                    raise ValueError('At least one of the EventClassSelector\'s rules must not be None!')
                tmp_analyser = func(
                    item['action_id'],
                    item['artefact_a_rules'],
                    item['artefact_b_rules'])
                match_action_dict[item['action_id']] = tmp_analyser
                continue
            elif item['type'] == 'TimeCorrelationViolationDetector':
                ruleset = []
                for rule in item['ruleset']:
                    if rule not in match_rules_dict:
                        raise ValueError('The match rule %s does not exist!' % rule)
                    ruleset.append(match_rules_dict[rule])
                tmp_analyser = func(
                    analysis_context.aminer_config,
                    ruleset,
                    anomaly_event_handlers,
                    persistence_id=item['persistence_id'],
                    output_log_line=learn)
            elif item['type'] == 'SimpleMonotonicTimestampAdjust':
                tmp_analyser = func(
                    [atom_filter],
                    stop_when_handled_flag=item['stop_when_handled_flag'])
            elif item['type'] == 'TimestampsUnsortedDetector':
                tmp_analyser = func(
                    analysis_context.aminer_config,
                    anomaly_event_handlers,
                    exit_on_error_flag=item['exit_on_error_flag'],
                    output_log_line=learn)
            elif item['type'] == 'WhitelistViolationDetector':
                whitelist_rules = []
                for rule in item['whitelist_rules']:
                    if rule not in match_rules_dict:
                        raise ValueError('The match rule %s does not exist!' % rule)
                    whitelist_rules.append(match_rules_dict[rule])
                tmp_analyser = func(
                    analysis_context.aminer_config,
                    whitelist_rules,
                    anomaly_event_handlers,
                    output_log_line=learn)
            else:
                tmp_analyser = func(
                    analysis_context.aminer_config,
                    item['paths'],
                    anomaly_event_handlers,
                    auto_include_flag=learn)
            analysis_context.register_component(tmp_analyser, component_name=comp_name)
            atom_filter.add_handler(tmp_analyser)

    try:
        for item in yaml_data['EventHandlers']:
            func = getattr(__import__("aminer.events", fromlist=[item['type']]), item['type'])
            ctx = None
            if item['type'] in ('StreamPrinterEventHandler', 'DefaultMailNotificationEventHandler'):
                ctx = func(analysis_context)
            if item['type'] == 'SyslogWriterEventHandler':
                ctx = func(analysis_context, item['instance_name'])
            if item['type'] == 'KafkaEventHandler':
                ctx = func(analysis_context, item['topic'], item['options'])
            if item['json'] is True:
                from aminer.events import JsonConverterHandler
                ctx = JsonConverterHandler([ctx], analysis_context)
            if ctx is None:
                ctx = func(analysis_context)
            anomaly_event_handlers.append(ctx)

    except KeyError:
        # Add stdout stream printing for debugging, tuning.
        from aminer.events import StreamPrinterEventHandler
        anomaly_event_handlers.append(StreamPrinterEventHandler(analysis_context))


def tuple_transformation_function_demo_print_every_10th_value(self, match_value_list):
    extra_data = self.known_values_dict.get(tuple(match_value_list), None)
    if extra_data is not None:
        mod = 10
        if (extra_data[2] + 1) % mod == 0:
            self.auto_include_flag = False
        else:
            self.auto_include_flag = True
    return match_value_list
