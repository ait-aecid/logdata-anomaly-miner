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
yamldata = None

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
def loadYaml(config_file):
    # We might be able to remove this and us it like the config_properties
    # skipcq: PYL-W0603
    global yamldata

    import yaml
    from aminer.ConfigValidator import ConfigValidator
    import os
    with open(config_file) as yamlfile:
        try:
            yamldata = yaml.safe_load(yamlfile)
            yamlfile.close()
        except yaml.YAMLError as exception:
            raise exception

    with open(os.path.dirname(os.path.abspath(__file__)) + '/' + 'schema.py', 'r') as sma:
        # skipcq: PYL-W0123
        schema = eval(sma.read())
    sma.close()

    v = ConfigValidator(schema)
    if v.validate(yamldata, schema):
        test = v.normalized(yamldata)
        yamldata = test
    else:
        raise ValueError(v.errors)

    # Set default values
    for key, val in yamldata.items():
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

    parserModelDict = {}
    start = None
    wscount = 0
    whitespace_str = b' '

    # We might be able to remove this and us it like the config_properties
    # skipcq: PYL-W0603
    global yamldata
    for item in yamldata['Parser']:
        if 'start' in item and item['start'] is True:
            start = item
            continue
        if item['type'].ismodel:
            if 'args' in item:
                if isinstance(item['args'], list):
                    # encode string to bytearray
                    for j in range(len(item['args'])):
                        item['args'][j] = item['args'][j].encode()
                    parserModelDict[item['id']] = item['type'].func(item['name'], item['args'])
                else:
                    parserModelDict[item['id']] = item['type'].func(item['name'], item['args'].encode())
            else:
                parserModelDict[item['id']] = item['type'].func(item['name'])
        else:
            parserModelDict[item['id']] = item['type'].func()

    argslist = []
    if 'args' in start:
        if isinstance(start['args'], list):
            for i in start['args']:
                if i == 'WHITESPACE':
                    from aminer.parsing import FixedDataModelElement
                    sp = 'sp%d' % wscount
                    argslist.append(FixedDataModelElement(sp, whitespace_str))
                    wscount += 1
                else:
                    argslist.append(parserModelDict[i])
            parsing_model = start['type'].func(start['name'], argslist)
        else:
            parsing_model = start['type'].func(start['name'], [parserModelDict[start['args']]])
    else:
        parsing_model = start['type'].func()

# Some generic imports.
    from aminer.analysis import AtomFilters

# Create all global handler lists here and append the real handlers
# later on.
# Use this filter to distribute all atoms to the analysis handlers.
    atomFilter = AtomFilters.SubhandlerFilter(None)
    anomaly_event_handlers = []

# Now define the AtomizerFactory using the model. A simple line
# based one is usually sufficient.
    from aminer.input import SimpleByteStreamLineAtomizerFactory
    if yamldata['Input']['MultiSource'] is True:
        from aminer.input import SimpleMultisourceAtomSync
        analysis_context.atomizer_factory = SimpleByteStreamLineAtomizerFactory(
            parsing_model, [SimpleMultisourceAtomSync([atomFilter], sync_wait_time=5)],
            anomaly_event_handlers, default_timestamp_paths=yamldata['Input']['TimestampPath'])
    else:
        analysis_context.atomizer_factory = SimpleByteStreamLineAtomizerFactory(
            parsing_model, [atomFilter], anomaly_event_handlers,
            default_timestamp_paths=yamldata['Input']['TimestampPath'])

# Just report all unparsed atoms to the event handlers.
    if yamldata['Input']['Verbose'] is True:
        from aminer.input import VerboseUnparsedAtomHandler
        atomFilter.add_handler(
            VerboseUnparsedAtomHandler(anomaly_event_handlers, parsing_model),
            stop_when_handled_flag=True)
    else:
        from aminer.input import SimpleUnparsedAtomHandler
        atomFilter.add_handler(
            SimpleUnparsedAtomHandler(anomaly_event_handlers),
            stop_when_handled_flag=True)

    from aminer.analysis import NewMatchPathDetector
    if 'LearnMode' in yamldata:
        learn = yamldata['LearnMode']
    else:
        learn = True
    nmpd = NewMatchPathDetector(
        analysis_context.aminer_config, anomaly_event_handlers, auto_include_flag=learn)
    analysis_context.register_component(nmpd, component_name=None)
    atomFilter.add_handler(nmpd)

    if 'Analysis' in yamldata and yamldata['Analysis'] is not None:
        analysis_dict = {}
        match_action_dict = {}
        match_rules_dict = {}
        correlation_rules = {}
        for item in yamldata['Analysis']:
            if item['id'] == 'None':
                compName = None
            else:
                compName = item['id']
            if 'LearnMode' in yamldata:
                learn = yamldata['LearnMode']
            else:
                learn = item['learnMode']
            func = getattr(__import__("aminer.analysis", fromlist=[item['type']]), item['type'])
            if item['type'] == 'NewMatchPathValueDetector':
                tmpAnalyser = func(
                    analysis_context.aminer_config,
                    item['paths'], anomaly_event_handlers, auto_include_flag=learn,
                    persistence_id=item['persistence_id'],
                    output_log_line=item['output_logline'])
            elif item['type'] == 'NewMatchPathValueComboDetector':
                tmpAnalyser = func(
                    analysis_context.aminer_config, item['paths'],
                    anomaly_event_handlers, auto_include_flag=learn,
                    persistence_id=item['persistence_id'],
                    allow_missing_values_flag=item['allow_missing_values'],
                    output_log_line=item['output_logline'])
            elif item['type'] == 'MissingMatchPathValueDetector':
                tmpAnalyser = func(
                    analysis_context.aminer_config, item['path'],
                    anomaly_event_handlers, auto_include_flag=learn,
                    persistence_id=item['persistence_id'],
                    default_interval=item['check_interval'],
                    realert_interval=item['realert_interval'],
                    output_log_line=item['output_logline'])
            elif item['type'] == 'MissingMatchPathListValueDetector':
                tmpAnalyser = func(
                    analysis_context.aminer_config, item['path'],
                    anomaly_event_handlers, auto_include_flag=learn,
                    persistence_id=item['persistence_id'],
                    default_interval=item['check_interval'],
                    realert_interval=item['realert_interval'],
                    output_log_line=item['output_logline'])
            elif item['type'] == 'TimeCorrelationDetector':
                tmpAnalyser = func(
                    analysis_context.aminer_config, anomaly_event_handlers,
                    parallel_check_count=item['parallel_check_count'],
                    persistence_id=item['persistence_id'],
                    record_count_before_event=item['record_count_before_event'],
                    output_log_line=item['output_logline'],
                    use_path_match=item['use_path_match'],
                    use_value_match=item['use_value_match'],
                    min_rule_attributes=item['min_rule_attributes'],
                    max_rule_attributes=item['max_rule_attributes'])
            elif item['type'] == 'ParserCount':
                tmpAnalyser = func(
                    analysis_context.aminer_config,
                    item['paths'],
                    report_interval=item['report_interval'],
                    report_event_handlers=anomaly_event_handlers,
                    reset_after_report_flag=item['reset_after_report_flag'])
            elif item['type'] == 'EventCorrelationDetector':
                tmpAnalyser = func(
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
                tmpAnalyser = func(
                    analysis_context.aminer_config,
                    item['paths'],
                    anomaly_event_handlers,
                    id_path_list=item['id_path_list'],
                    min_allowed_time_diff=item['min_allowed_time_diff'],
                    auto_include_flag=learn,
                    persistence_id=item['persistence_id'],
                    allow_missing_values_flag=item['allow_missing_values'],
                    output_log_line=item['output_logline'])
            elif item['type'] == 'LinearNumericBinDefinition':
                if compName is None:
                    raise ValueError('The %s must have an id!' % item['type'])
                analysis_dict[compName] = func(
                    item['lower_limit'],
                    item['bin_size'],
                    item['bin_count'],
                    item['outlier_bins_flag'])
                continue
            elif item['type'] == 'ModuloTimeBinDefinition':
                if compName is None:
                    raise ValueError('The %s must have an id!' % item['type'])
                analysis_dict[compName] = func(
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
                tmpAnalyser = func(
                    analysis_context.aminer_config,
                    histogram_defs,
                    item['report_interval'],
                    anomaly_event_handlers,
                    reset_after_report_flag=item['reset_after_report_flag'],
                    persistence_id=item['persistence_id'],
                    output_log_line=item['output_logline'])
            elif item['type'] == 'PathDependentHistogramAnalysis':
                if item['bin_definition'] not in analysis_dict:
                    raise ValueError('%s first must be defined before used.' % item['bin_definition'])
                tmpAnalyser = func(
                    analysis_context.aminer_config,
                    item['path'],
                    analysis_dict[item['bin_definition']],
                    item['report_interval'],
                    anomaly_event_handlers,
                    reset_after_report_flag=item['reset_after_report_flag'],
                    persistence_id=item['persistence_id'],
                    output_log_line=item['output_logline'])
            elif item['type'] == 'EnhancedNewMatchPathValueComboDetector':
                tuple_transformation_function = None
                if item['tuple_transformation_function'] == 'demo':
                    tuple_transformation_function = tuple_transformation_function_demo_print_every_10th_value
                tmpAnalyser = func(
                    analysis_context.aminer_config,
                    item['paths'],
                    anomaly_event_handlers,
                    persistence_id=item['persistence_id'],
                    allow_missing_values_flag=item['allow_missing_values'],
                    auto_include_flag=learn,
                    tuple_transformation_function=tuple_transformation_function,
                    output_log_line=item['output_logline'])
            elif item['type'] == 'MatchFilter':
                tmpAnalyser = func(
                    analysis_context.aminer_config,
                    item['paths'],
                    anomaly_event_handlers,
                    target_value_list=item['value_list'],
                    output_log_line=item['output_logline'])
            elif item['type'] == 'MatchValueAverageChangeDetector':
                tmpAnalyser = func(
                    analysis_context.aminer_config,
                    anomaly_event_handlers,
                    item['timestamp_path'],
                    item['paths'],
                    item['min_bin_elements'],
                    item['min_bin_time'],
                    sync_bins_flag=item['sync_bins_flag'],
                    debug_mode=item['debug_mode'],
                    persistence_id=item['persistence_id'],
                    output_log_line=item['output_logline'])
            elif item['type'] == 'MatchValueStreamWriter':
                stream = sys.stdout
                if item['stream'] == 'sys.stderr':
                    stream = sys.stderr
                tmpAnalyser = func(
                    stream,
                    item['paths'],
                    item['separator'].encode(),
                    item['missing_value_string'].encode())
            elif item['type'] == 'NewMatchPathDetector':
                tmpAnalyser = func(
                    analysis_context.aminer_config,
                    anomaly_event_handlers,
                    persistence_id=item['persistence_id'],
                    auto_include_flag=learn,
                    output_log_line=item['output_logline'])
            elif 'MatchAction' in item['type']:
                if compName is None:
                    raise ValueError('The %s must have an id!' % item['type'])
                if item['type'] == 'EventGenerationMatchAction':
                    tmpAnalyser = func(
                        item['event_type'],
                        item['event_message'],
                        anomaly_event_handlers)
                elif item['type'] == 'AtomFilterMatchAction':
                    tmpAnalyser = func(
                        atomFilter,
                        stop_when_handled_flag=item['stop_when_handled_flag'])
                match_action_dict[compName] = tmpAnalyser
                continue
            elif 'MatchRule' in item['type']:
                if compName is None:
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
                    tmpAnalyser = func(
                        sub_rules,
                        match_action=match_action)
                if item['type'] == 'ValueDependentDelegatedMatchRule':
                    rule_lookup_dict = {}
                    for rule in item['rule_lookup_dict']:
                        if rule not in match_rules_dict:
                            raise ValueError('The match rule %s does not exist!' % rule)
                        rule_lookup_dict[rule] = match_rules_dict[rule]
                    tmpAnalyser = func(
                        item['paths'],
                        rule_lookup_dict,
                        default_rule=item['default_rule'],
                        match_action=match_action)
                if item['type'] == 'NegationMatchRule':
                    if item['sub_rule'] not in match_rules_dict:
                        raise ValueError('The match rule %s does not exist!' % item['sub_rule'])
                    sub_rule = match_rules_dict[item['sub_rule']]
                    tmpAnalyser = func(
                        sub_rule,
                        match_action=match_action)
                if item['type'] in ('PathExistsMatchRule', 'IPv4InRFC1918MatchRule'):
                    tmpAnalyser = func(
                        item['path'],
                        match_action=match_action)
                if item['type'] == 'ValueMatchRule':
                    if isinstance(item['value'], str):
                        item['value'] = item['value'].encode()
                    tmpAnalyser = func(
                        item['path'],
                        item['value'],
                        match_action=match_action)
                if item['type'] == 'ValueListMatchRule':
                    value_list = []
                    for val in item['value_list']:
                        if isinstance(val, str):
                            val = val.encode()
                        value_list.append(val)
                    tmpAnalyser = func(
                        item['path'],
                        value_list,
                        match_action=match_action)
                if item['type'] == 'ValueRangeMatchRule':
                    tmpAnalyser = func(
                        item['path'],
                        item['lower_limit'],
                        item['upper_limit'],
                        match_action)
                if item['type'] == 'StringRegexMatchRule':
                    tmpAnalyser = func(
                        item['path'],
                        item['regex'],
                        match_action=match_action)
                if item['type'] == 'ModuloTimeMatchRule':
                    # tzinfo parameter cannot be used yet..
                    tmpAnalyser = func(
                        item['path'],
                        item['seconds_modulo'],
                        item['lower_limit'],
                        item['upper_limit'],
                        match_action=match_action)
                if item['type'] == 'ValueDependentModuloTimeMatchRule':
                    # tzinfo parameter cannot be used yet..
                    tmpAnalyser = func(
                        item['path'],
                        item['seconds_modulo'],
                        item['paths'],
                        item['limit_lookup_dict'],
                        default_limit=item['default_limit'],
                        match_action=match_action)
                if item['type'] == 'DebugMatchRule':
                    tmpAnalyser = func(
                        debug_match_result=item['debug_mode'],
                        match_action=match_action)
                if item['type'] == 'DebugHistoryMatchRule':
                    # object_history is not supported yet..
                    tmpAnalyser = func(
                        debug_match_result=item['debug_mode'],
                        match_action=match_action)
                match_rules_dict[compName] = tmpAnalyser
                continue
            elif item['type'] == 'CorrelationRule':
                artefact_match_parameters = []
                for match_parameters in item['artefact_match_parameters']:
                    artefact_match_parameters.append(tuple(i for i in match_parameters))
                tmpAnalyser = func(
                    item['rule_id'],
                    item['min_time_delta'],
                    item['max_time_delta'],
                    item['max_artefacts_a_for_single_b'],
                    artefact_match_parameters=artefact_match_parameters)
                correlation_rules[item['rule_id']] = tmpAnalyser
                continue
            elif item['type'] == 'EventClassSelector':
                if item['artefact_a_rules'] is None and item['artefact_b_rules'] is None:
                    raise ValueError('At least one of the EventClassSelector\'s rules must not be None!')
                tmpAnalyser = func(
                    item['action_id'],
                    item['artefact_a_rules'],
                    item['artefact_b_rules'])
                match_action_dict[item['action_id']] = tmpAnalyser
                continue
            elif item['type'] == 'TimeCorrelationViolationDetector':
                ruleset = []
                for rule in item['ruleset']:
                    if rule not in match_rules_dict:
                        raise ValueError('The match rule %s does not exist!' % rule)
                    ruleset.append(match_rules_dict[rule])
                tmpAnalyser = func(
                    analysis_context.aminer_config,
                    ruleset,
                    anomaly_event_handlers,
                    persistence_id=item['persistence_id'],
                    output_log_line=item['output_logline'])
            else:
                tmpAnalyser = func(
                    analysis_context.aminer_config,
                    item['paths'], anomaly_event_handlers, auto_include_flag=learn)
            analysis_context.register_component(tmpAnalyser, component_name=compName)
            atomFilter.add_handler(tmpAnalyser)

    try:
        for item in yamldata['EventHandlers']:
            func = getattr(__import__("aminer.events", fromlist=[item['type']]), item['type'])
            ctx = None
            if item['type'] == 'StreamPrinterEventHandler':
                if item['json'] is True:
                    from aminer.events import JsonConverterHandler
                    ctx = JsonConverterHandler([func(analysis_context)], analysis_context)
                else:
                    ctx = func(analysis_context)
#           if item['type'] == 'KafkaEventHandler':
#             try:
#               item['args'][0]
#             except:
#               raise ValueError("Kafka-Topic not defined")
#             try:
#               kafkaconfig = item['args'][1]
#             except:
#               kafkaconfig = '/etc/aminer/kafka-client.conf'
#             config = configparser.ConfigParser()
#             config.read(kafkaconfig)
#             options = dict(config.items("DEFAULT"))
#             for key, val in options.items():
#               try:
#                 if key == "sasl_plain_username":
#                   continue
#                 options[key] = int(val)
#               except:
#                 pass
#             kafkaEventHandler = func(analysis_context.aminer_config, item['args'][0], options)
#             from aminer.events import JsonConverterHandler
#             anomaly_event_handlers.append(
#                 JsonConverterHandler(analysis_context.aminer_config, messageQueueEventHandlers,
#                 analysis_context, learningMode))
#           else:
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
