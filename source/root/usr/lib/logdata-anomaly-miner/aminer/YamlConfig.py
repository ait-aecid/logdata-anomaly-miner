"""
This file loads and parses a config-file in yaml format.

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
import sys
import logging
import copy
from aminer.AminerConfig import DEBUG_LOG_NAME


config_properties = {}
yaml_data = None
enhanced_new_match_path_value_combo_detector_reference = None


def load_yaml(config_file):
    """
    Load the yaml configuration from files. Basically there are two schema types: validation schemas and normalisation schemas.
    The validation schemas validate together with the BaseSchema all inputs as specifically as possible. Due to the limitations of
    oneof_schemas and the not functional normalisation in the validation schemas, the normalisation schemas are used to set default values
    and convert the date in right data types with coerce procedures.
    """
    # We might be able to remove this and us it like the config_properties
    # skipcq: PYL-W0603
    global yaml_data

    import yaml
    from aminer.ConfigValidator import ConfigValidator, NormalisationValidator
    import os
    with open(config_file) as yamlfile:
        try:
            yaml_data = yaml.safe_load(yamlfile)
            yamlfile.close()
        except yaml.YAMLError as exception:
            logging.getLogger(DEBUG_LOG_NAME).error(exception)
            raise exception

    with open(os.path.dirname(os.path.abspath(__file__)) + '/' + 'schemas/BaseSchema.yml', 'r') as sma:
        # skipcq: PYL-W0123
        base_schema = eval(sma.read())
    with open(os.path.dirname(os.path.abspath(__file__)) + '/' + 'schemas/normalisation/ParserNormalisationSchema.yml', 'r') as sma:
        # skipcq: PYL-W0123
        parser_normalisation_schema = eval(sma.read())
    with open(os.path.dirname(os.path.abspath(__file__)) + '/' + 'schemas/normalisation/AnalysisNormalisationSchema.yml', 'r') as sma:
        # skipcq: PYL-W0123
        analysis_normalisation_schema = eval(sma.read())
    with open(os.path.dirname(os.path.abspath(__file__)) + '/' + 'schemas/normalisation/EventHandlerNormalisationSchema.yml', 'r') as sma:
        # skipcq: PYL-W0123
        event_handler_normalisation_schema = eval(sma.read())

    with open(os.path.dirname(os.path.abspath(__file__)) + '/' + 'schemas/validation/ParserValidationSchema.yml', 'r') as sma:
        # skipcq: PYL-W0123
        parser_validation_schema = eval(sma.read())
    with open(os.path.dirname(os.path.abspath(__file__)) + '/' + 'schemas/validation/AnalysisValidationSchema.yml', 'r') as sma:
        # skipcq: PYL-W0123
        analysis_validation_schema = eval(sma.read())
    with open(os.path.dirname(os.path.abspath(__file__)) + '/' + 'schemas/validation/EventHandlerValidationSchema.yml', 'r') as sma:
        # skipcq: PYL-W0123
        event_handler_validation_schema = eval(sma.read())

    normalisation_schema = {
        **base_schema, **parser_normalisation_schema, **analysis_normalisation_schema, **event_handler_normalisation_schema}
    validation_schema = {**base_schema, **parser_validation_schema, **analysis_validation_schema, **event_handler_validation_schema}

    v = ConfigValidator(validation_schema)
    if not v.validate(yaml_data, validation_schema):
        filtered_errors = copy.deepcopy(v.errors)
        filter_config_errors(filtered_errors, 'Analysis', v.errors, analysis_validation_schema)
        filter_config_errors(filtered_errors, 'Parser', v.errors, parser_validation_schema)
        filter_config_errors(filtered_errors, 'EventHandlers', v.errors, event_handler_validation_schema)

        print(v.errors)
        raise ValueError("Config-Error: %s" % filtered_errors)

    v = NormalisationValidator(normalisation_schema)
    if v.validate(yaml_data, normalisation_schema):
        test = v.normalized(yaml_data)
        yaml_data = test
    else:
        logging.getLogger(DEBUG_LOG_NAME).error(v.errors)
        raise ValueError(v.errors)

    # Set default values
    for key, val in yaml_data.items():
        config_properties[str(key)] = val


def filter_config_errors(filtered_errors, key_name, errors, schema):
    """Filter oneof outputs to produce a clear overview of the error."""
    oneof = schema[key_name]['schema']['oneof']
    if key_name in errors:
        for i, err in enumerate(errors[key_name]):
            for key in err:
                if 'none or more than one rule validate' in err[key]:
                    for cause in err[key]:
                        if isinstance(cause, dict):
                            # we need to copy the dictionary as it is not possible to iterate through it and change the size.
                            for definition in copy.deepcopy(cause):
                                if 'type' in cause[definition][0] and cause[definition][0]['type'][0].startswith('unallowed value '):
                                    del cause[definition]
                                else:
                                    oneof_def_pos = int(definition.split(' ')[-1])
                                    oneof_schema_type = oneof[oneof_def_pos]['schema']['type']
                                    if 'forbidden' in oneof_schema_type:
                                        cause[definition][0]['type'] = {'forbidden': oneof_schema_type['forbidden']}
                                    elif 'allowed' in oneof_schema_type:
                                        cause[definition][0]['type'] = {'allowed': oneof_schema_type['allowed']}
            filtered_errors[key_name][i] = err


# Add your ruleset here:
def build_analysis_pipeline(analysis_context):
    """
    Define the function to create pipeline for parsing the log data.
    It has also to define an AtomizerFactory to instruct aminer how to process incoming data streams to create log atoms from them.
    """
    parsing_model = build_parsing_model()
    anomaly_event_handlers, atom_filter = build_input_pipeline(analysis_context, parsing_model)
    build_analysis_components(analysis_context, anomaly_event_handlers, atom_filter)
    event_handler_id_list = build_event_handlers(analysis_context, anomaly_event_handlers)
    # do not check UnparsedAtomHandler
    for index, analysis_component in enumerate(atom_filter.subhandler_list[1:]):
        if analysis_component[0].output_event_handlers is not None:
            event_handlers = []
            for i in analysis_component[0].output_event_handlers:
                event_handlers.append(anomaly_event_handlers[event_handler_id_list.index(i)])
            atom_filter.subhandler_list[index+1][0].output_event_handlers = event_handlers


def build_parsing_model():
    """Build the parsing model."""
    parser_model_dict = {}
    start = None
    ws_count = 0
    whitespace_str = b' '

    # We might be able to remove this and us it like the config_properties
    # skipcq: PYL-W0603
    global yaml_data
    for item in yaml_data['Parser']:
        if item['id'] in parser_model_dict:
            raise ValueError('Config-Error: The id "%s" occurred multiple times in Parser!' % item['id'])
        if 'start' in item and item['start'] is True and item['type'].name != 'JsonModelElement':
            start = item
            continue
        if item['type'].is_model:
            if 'args' in item:
                if isinstance(item['args'], list):  # skipcq: PTC-W0048
                    if item['type'].name not in ('DecimalFloatValueModelElement', 'DecimalIntegerValueModelElement'):
                        # encode string to bytearray
                        for j, val in enumerate(item['args']):
                            if isinstance(val, str):
                                item['args'][j] = val.encode()
                else:
                    if item['type'].name not in ('DecimalFloatValueModelElement', 'DecimalIntegerValueModelElement') and isinstance(
                            item['args'], str):
                        item['args'] = item['args'].encode()
            if item['type'].name == 'ElementValueBranchModelElement':
                value_model = parser_model_dict.get(item['args'][0].decode())
                if value_model is None:
                    msg = 'The parser model %s does not exist!' % item['args'][0].decode()
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
                branch_model_dict = {}
                for i in item['branch_model_dict']:
                    key = i['id']
                    model = i['model']
                    if parser_model_dict.get(model) is None:
                        msg = 'The parser model %s does not exist!' % key
                        logging.getLogger(DEBUG_LOG_NAME).error(msg)
                        raise ValueError(msg)
                    branch_model_dict[key] = parser_model_dict.get(model)
                parser_model_dict[item['id']] = item['type'].func(item['name'], value_model, item['args'][1].decode(), branch_model_dict)
            elif item['type'].name == 'DateTimeModelElement':
                parser_model_dict[item['id']] = item['type'].func(
                    item['name'], item['date_format'].encode(), None, item['text_locale'], item['start_year'],
                    item['max_time_jump_seconds'])
            elif item['type'].name == 'MultiLocaleDateTimeModelElement':
                date_formats = []
                for date_format in item['date_formats']:
                    if len(date_format['format']) != 3:
                        msg = 'The date_format must have a size of 3!'
                        logging.getLogger(DEBUG_LOG_NAME).error(msg)
                        raise ValueError(msg)
                    fmt = date_format['format']
                    fmt[0] = fmt[0].encode()
                    date_formats.append(tuple(fmt))
                parser_model_dict[item['id']] = item['type'].func(
                    item['name'], date_formats, item['start_year'], item['max_time_jump_seconds'])
            elif item['type'].name == 'RepeatedElementDataModelElement':
                model = item['args'][0].decode()
                if parser_model_dict.get(model) is None:
                    msg = 'The parser model %s does not exist!' % model
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
                item['args'][0] = parser_model_dict.get(model)
                parser_model_dict[item['id']] = item['type'].func(item['name'], item['args'][0])
                if len(item['args']) == 2:
                    parser_model_dict[item['id']] = item['type'].func(item['name'], item['args'][0], item['args'][1])
                elif len(item['args']) == 3:
                    parser_model_dict[item['id']] = item['type'].func(item['name'], item['args'][0], item['args'][1], item['args'][2])
                elif len(item['args']) > 3:
                    msg = 'The RepeatedElementDataModelElement does not have more than 3 arguments.'
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
            elif item['type'].name == 'DecimalFloatValueModelElement':
                parser_model_dict[item['id']] = item['type'].func(
                    item['name'], item['value_sign_type'], item['value_pad_type'], item['exponent_type'])
            elif item['type'].name == 'DecimalIntegerValueModelElement':
                parser_model_dict[item['id']] = item['type'].func(item['name'], item['value_sign_type'], item['value_pad_type'])
            elif item['type'].name in ('FirstMatchModelElement', 'SequenceModelElement'):
                children = []
                for child in item['args']:
                    if parser_model_dict.get(child.decode()) is None:
                        msg = 'The parser model %s does not exist!' % child.decode()
                        logging.getLogger(DEBUG_LOG_NAME).error(msg)
                        raise ValueError(msg)
                    children.append(parser_model_dict.get(child.decode()))
                parser_model_dict[item['id']] = item['type'].func(item['name'], children)
            elif item['type'].name == 'OptionalMatchModelElement':
                optional_element = parser_model_dict.get(item['args'].decode())
                if optional_element is None:
                    msg = 'The parser model %s does not exist!' % item['args'].decode()
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
                parser_model_dict[item['id']] = item['type'].func(item['name'], optional_element)
            elif item['type'].name == 'DelimitedDataModelElement':
                delimiter = item['delimiter'].encode()
                parser_model_dict[item['id']] = item['type'].func(item['name'], delimiter, item['escape'], item['consume_delimiter'])
            elif item['type'].name == 'JsonModelElement':
                key_parser_dict = parse_json_yaml(item['key_parser_dict'], parser_model_dict)
                if 'start' in item and item['start'] is True:
                    start = item['type'].func(item['name'], key_parser_dict, item['optional_key_prefix'])
                else:
                    parser_model_dict[item['id']] = item['type'].func(item['name'], key_parser_dict, item['optional_key_prefix'])
            else:
                if 'args' in item:
                    parser_model_dict[item['id']] = item['type'].func(item['name'], item['args'])
                else:
                    parser_model_dict[item['id']] = item['type'].func(item['name'])
        else:
            parser_model_dict[item['id']] = item['type'].func()

    args_list = []
    if start.__class__.__name__ == 'JsonModelElement':
        parsing_model = start
    elif 'args' in start:
        if isinstance(start['args'], list):
            for i in start['args']:
                if i == 'WHITESPACE':
                    from aminer.parsing.FixedDataModelElement import FixedDataModelElement
                    sp = 'sp%d' % ws_count
                    args_list.append(FixedDataModelElement(sp, whitespace_str))
                    ws_count += 1
                else:
                    model = parser_model_dict.get(i)
                    if model is None:
                        msg = 'The parser model %s does not exist!' % i
                        logging.getLogger(DEBUG_LOG_NAME).error(msg)
                        raise ValueError(msg)
                    args_list.append(model)
            parsing_model = start['type'].func(start['name'], args_list)
        else:
            parsing_model = start['type'].func(start['name'], [parser_model_dict[start['args']]])
    else:
        parsing_model = start['type'].func()
    return parsing_model


def build_input_pipeline(analysis_context, parsing_model):
    """Build the input pipeline."""
    # Some generic imports.
    from aminer.analysis import AtomFilters
    # Create all global handler lists here and append the real handlers later on.
    # Use this filter to distribute all atoms to the analysis handlers.
    atom_filter = AtomFilters.SubhandlerFilter(None)
    analysis_context.register_component(atom_filter, component_name="AtomFilter")
    anomaly_event_handlers = []
    # Now define the AtomizerFactory using the model. A simple line based one is usually sufficient.
    from aminer.input.SimpleByteStreamLineAtomizerFactory import SimpleByteStreamLineAtomizerFactory
    timestamp_paths = yaml_data['Input']['timestamp_paths']
    if isinstance(timestamp_paths, str):
        timestamp_paths = [timestamp_paths]
    sync_wait_time = yaml_data['Input']['sync_wait_time']
    eol_sep = yaml_data['Input']['eol_sep'].encode()
    json_format = yaml_data['Input']['json_format']
    if yaml_data['Input']['multi_source'] is True:
        from aminer.input.SimpleMultisourceAtomSync import SimpleMultisourceAtomSync
        analysis_context.atomizer_factory = SimpleByteStreamLineAtomizerFactory(parsing_model, [SimpleMultisourceAtomSync([
            atom_filter], sync_wait_time=sync_wait_time)], anomaly_event_handlers, default_timestamp_paths=timestamp_paths, eol_sep=eol_sep,
            json_format=json_format)
    else:
        analysis_context.atomizer_factory = SimpleByteStreamLineAtomizerFactory(
            parsing_model, [atom_filter], anomaly_event_handlers, default_timestamp_paths=timestamp_paths, eol_sep=eol_sep,
            json_format=json_format)
    # Just report all unparsed atoms to the event handlers.
    if yaml_data['Input']['verbose'] is True:
        from aminer.input.VerboseUnparsedAtomHandler import VerboseUnparsedAtomHandler
        atom_filter.add_handler(VerboseUnparsedAtomHandler(anomaly_event_handlers, parsing_model), stop_when_handled_flag=True)
    else:
        from aminer.input.SimpleUnparsedAtomHandler import SimpleUnparsedAtomHandler
        atom_filter.add_handler(SimpleUnparsedAtomHandler(anomaly_event_handlers), stop_when_handled_flag=True)
    if yaml_data['Input']['suppress_unparsed'] is True:
        analysis_context.suppress_detector_list.append(atom_filter.subhandler_list[-1][0])
    from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
    if 'LearnMode' in yaml_data:
        learn = yaml_data['LearnMode']
    else:
        learn = True
    nmpd = NewMatchPathDetector(analysis_context.aminer_config, anomaly_event_handlers, auto_include_flag=learn)
    nmpd.output_event_handlers = None
    analysis_context.register_component(nmpd, component_name='DefaultNewMatchPathDetector')
    atom_filter.add_handler(nmpd)
    return anomaly_event_handlers, atom_filter


def build_analysis_components(analysis_context, anomaly_event_handlers, atom_filter):
    """Build the analysis components."""
    suppress_detector_list = analysis_context.suppress_detector_list
    if yaml_data['SuppressNewMatchPathDetector']:
        suppress_detector_list.append('DefaultNewMatchPathDetector')
    if 'Analysis' in yaml_data and yaml_data['Analysis'] is not None:
        analysis_dict = {}
        match_action_dict = {}
        match_rules_dict = {}
        correlation_rules = {}
        # changed order if ETD is defined.
        for item in yaml_data['Analysis']:
            if item['type'].name == 'EventTypeDetector':
                index = yaml_data['Analysis'].index(item)
                new_analysis_list = [item]
                del yaml_data['Analysis'][index]
                new_analysis_list += yaml_data['Analysis']
                yaml_data['Analysis'] = new_analysis_list
                break

        for item in yaml_data['Analysis']:
            if item['id'] == 'None':
                comp_name = None
            else:
                comp_name = item['id']
                if analysis_context.get_component_by_name(comp_name) is not None:
                    raise ValueError('Config-Error: The id "%s" occurred multiple times in Analysis!' % comp_name)
            if 'learn_mode' in item:
                learn = item['learn_mode']
            else:
                if 'LearnMode' not in yaml_data:
                    msg = 'Config-Error: LearnMode must be defined if an analysis component does not define learn_mode.'
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
                learn = yaml_data['LearnMode']
            func = item['type'].func
            if item['suppress']:
                if comp_name is None:
                    raise ValueError(
                        'Config-Error: id must be specified for the analysis component %s to enable suppression.' % item['type'])
                suppress_detector_list.append(comp_name)
            if item['type'].name == 'NewMatchPathValueDetector':
                tmp_analyser = func(analysis_context.aminer_config, item['paths'], anomaly_event_handlers, auto_include_flag=learn,
                                    persistence_id=item['persistence_id'], output_log_line=item['output_logline'])
            elif item['type'].name == 'MatchPathFilter':
                parsed_atom_handler_lookup_list = []
                for atom_handler in item['parsed_atom_handler_lookup_list']:
                    if atom_handler[1] is not None:
                        if analysis_context.get_component_by_name(atom_handler[1]) is None:
                            msg = 'The atom handler %s does not exist!' % atom_handler[1]
                            logging.getLogger(DEBUG_LOG_NAME).error(msg)
                            raise ValueError(msg)
                        atom_handler[1] = analysis_context.get_component_by_name(atom_handler[1])
                    parsed_atom_handler_lookup_list.append(tuple(i for i in atom_handler))
                default_parsed_atom_handler = item['default_parsed_atom_handler']
                if default_parsed_atom_handler is not None:
                    if analysis_context.get_component_by_name(default_parsed_atom_handler) is None:
                        msg = 'The atom handler %s does not exist!' % default_parsed_atom_handler
                        logging.getLogger(DEBUG_LOG_NAME).error(msg)
                        raise ValueError(msg)
                    default_parsed_atom_handler = analysis_context.get_component_by_name(default_parsed_atom_handler)
                tmp_analyser = func(parsed_atom_handler_lookup_list, default_parsed_atom_handler=default_parsed_atom_handler)
            elif item['type'].name == 'MatchValueFilter':
                parsed_atom_handler_dict = {}
                for atom_handler in item['parsed_atom_handler_dict']:
                    if analysis_context.get_component_by_name(atom_handler) is None:
                        msg = 'The atom handler %s does not exist!' % atom_handler
                        logging.getLogger(DEBUG_LOG_NAME).error(msg)
                        raise ValueError(msg)
                    parsed_atom_handler_dict[atom_handler] = analysis_context.get_component_by_name(atom_handler)
                default_parsed_atom_handler = item['default_parsed_atom_handler']
                if default_parsed_atom_handler is not None:
                    if analysis_context.get_component_by_name(default_parsed_atom_handler) is None:
                        msg = 'The atom handler %s does not exist!' % default_parsed_atom_handler
                        logging.getLogger(DEBUG_LOG_NAME).error(msg)
                        raise ValueError(msg)
                    default_parsed_atom_handler = analysis_context.get_component_by_name(default_parsed_atom_handler)
                tmp_analyser = func(item['path'], parsed_atom_handler_dict, default_parsed_atom_handler=default_parsed_atom_handler)
            elif item['type'].name == 'PCADetector':
                tmp_analyser = func(analysis_context.aminer_config, item['paths'], anomaly_event_handlers,
                                    persistence_id=item['persistence_id'], window_size=item['window_size'],
                                    min_anomaly_score=item['min_anomaly_score'], min_variance=item['min_variance'],
                                    num_windows=item['num_windows'], auto_include_flag=learn, output_log_line=item['output_logline'],
                                    ignore_list=item['ignore_list'])
            elif item['type'].name == 'NewMatchPathValueComboDetector':
                tmp_analyser = func(analysis_context.aminer_config, item['paths'], anomaly_event_handlers, auto_include_flag=learn,
                                    persistence_id=item['persistence_id'], allow_missing_values_flag=item['allow_missing_values'],
                                    output_log_line=item['output_logline'])
            elif item['type'].name == 'MissingMatchPathValueDetector':
                tmp_analyser = func(analysis_context.aminer_config, item['paths'], anomaly_event_handlers, auto_include_flag=learn,
                                    persistence_id=item['persistence_id'], default_interval=item['check_interval'],
                                    realert_interval=item['realert_interval'], output_log_line=item['output_logline'])
            elif item['type'].name == 'MissingMatchPathListValueDetector':
                tmp_analyser = func(analysis_context.aminer_config, item['path'], anomaly_event_handlers, auto_include_flag=learn,
                                    persistence_id=item['persistence_id'], default_interval=item['check_interval'],
                                    realert_interval=item['realert_interval'], output_log_line=item['output_logline'])
            elif item['type'].name == 'EventSequenceDetector':
                tmp_analyser = func(analysis_context.aminer_config, anomaly_event_handlers, item['id_path_list'],
                                    target_path_list=item['paths'], persistence_id=item['persistence_id'], seq_len=item['seq_len'],
                                    auto_include_flag=learn, timeout=item['timeout'], allow_missing_id=item['allow_missing_id'],
                                    output_log_line=item['output_logline'], ignore_list=item['ignore_list'],
                                    constraint_list=item['constraint_list'])
            elif item['type'].name == 'EventFrequencyDetector':
                tmp_analyser = func(analysis_context.aminer_config, anomaly_event_handlers, target_path_list=item['paths'],
                                    persistence_id=item['persistence_id'], window_size=item['window_size'],
                                    confidence_factor=item['confidence_factor'], auto_include_flag=learn,
                                    output_log_line=item['output_logline'], ignore_list=item['ignore_list'],
                                    constraint_list=item['constraint_list'])
            elif item['type'].name == 'TimeCorrelationDetector':
                tmp_analyser = func(analysis_context.aminer_config, anomaly_event_handlers, item['parallel_check_count'],
                                    persistence_id=item['persistence_id'], record_count_before_event=item['record_count_before_event'],
                                    output_log_line=item['output_logline'], use_path_match=item['use_path_match'],
                                    use_value_match=item['use_value_match'], min_rule_attributes=item['min_rule_attributes'],
                                    max_rule_attributes=item['max_rule_attributes'])
            elif item['type'].name == 'ParserCount':
                tmp_analyser = func(
                    analysis_context.aminer_config,
                    item['paths'],
                    anomaly_event_handlers,
                    report_interval=item['report_interval'],
                    target_label_list=item['labels'],
                    split_reports_flag=item['split_reports_flag'])
            elif item['type'].name == 'EventCorrelationDetector':
                tmp_analyser = func(
                    analysis_context.aminer_config, anomaly_event_handlers, paths=item['paths'], max_hypotheses=item['max_hypotheses'],
                    hypothesis_max_delta_time=item['hypothesis_max_delta_time'], generation_probability=item['generation_probability'],
                    generation_factor=item['generation_factor'], max_observations=item['max_observations'], p0=item['p0'],
                    alpha=item['alpha'], candidates_size=item['candidates_size'],
                    hypotheses_eval_delta_time=item['hypotheses_eval_delta_time'], constraint_list=item['constraint_list'],
                    delta_time_to_discard_hypothesis=item['delta_time_to_discard_hypothesis'], check_rules_flag=item['check_rules_flag'],
                    auto_include_flag=learn, ignore_list=item['ignore_list'], persistence_id=item['persistence_id'])
            elif item['type'].name == 'NewMatchIdValueComboDetector':
                tmp_analyser = func(analysis_context.aminer_config, item['paths'], anomaly_event_handlers,
                                    id_path_list=item['id_path_list'], min_allowed_time_diff=item['min_allowed_time_diff'],
                                    auto_include_flag=learn, persistence_id=item['persistence_id'],
                                    allow_missing_values_flag=item['allow_missing_values'], output_log_line=item['output_logline'])
            elif item['type'].name == 'LinearNumericBinDefinition':
                if comp_name is None:
                    msg = 'The %s must have an id!' % item['type'].name
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
                analysis_dict[comp_name] = func(item['lower_limit'], item['bin_size'], item['bin_count'], item['outlier_bins_flag'])
                continue
            elif item['type'].name == 'ModuloTimeBinDefinition':
                if comp_name is None:
                    msg = 'The %s must have an id!' % item['type'].name
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
                analysis_dict[comp_name] = func(item['modulo_value'], item['time_unit'], item['lower_limit'], item['bin_size'],
                                                item['bin_count'], item['outlier_bins_flag'])
                continue
            elif item['type'].name == 'HistogramAnalysis':
                histogram_defs = []
                for histogram_def in item['histogram_defs']:
                    if len(histogram_def) != 2:
                        msg = 'Every item of the histogram_defs must have an size of 2!'
                        logging.getLogger(DEBUG_LOG_NAME).error(msg)
                        raise ValueError(msg)
                    if histogram_def[1] not in analysis_dict:
                        msg = '%s first must be defined before used.' % histogram_def[1]
                        logging.getLogger(DEBUG_LOG_NAME).error(msg)
                        raise ValueError(msg)
                    histogram_defs.append([histogram_def[0], analysis_dict[histogram_def[1]]])
                tmp_analyser = func(analysis_context.aminer_config, histogram_defs, item['report_interval'], anomaly_event_handlers,
                                    reset_after_report_flag=item['reset_after_report_flag'], persistence_id=item['persistence_id'],
                                    output_log_line=item['output_logline'])
            elif item['type'].name == 'PathDependentHistogramAnalysis':
                if item['bin_definition'] not in analysis_dict:
                    msg = '%s first must be defined before used.' % item['bin_definition']
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
                tmp_analyser = func(
                    analysis_context.aminer_config, item['path'], analysis_dict[item['bin_definition']], item['report_interval'],
                    anomaly_event_handlers, reset_after_report_flag=item['reset_after_report_flag'], persistence_id=item['persistence_id'],
                    output_log_line=item['output_logline'])
            elif item['type'].name == 'EnhancedNewMatchPathValueComboDetector':
                tuple_transformation_function = None
                if item['tuple_transformation_function'] == 'demo':
                    tuple_transformation_function = tuple_transformation_function_demo_print_every_10th_value
                tmp_analyser = func(analysis_context.aminer_config, item['paths'], anomaly_event_handlers,
                                    persistence_id=item['persistence_id'], allow_missing_values_flag=item['allow_missing_values'],
                                    auto_include_flag=learn, tuple_transformation_function=tuple_transformation_function,
                                    output_log_line=item['output_logline'])
                # skipcq: PYL-W0603
                global enhanced_new_match_path_value_combo_detector_reference
                enhanced_new_match_path_value_combo_detector_reference = tmp_analyser
            elif item['type'].name == 'MatchFilter':
                tmp_analyser = func(analysis_context.aminer_config, item['paths'], anomaly_event_handlers,
                                    target_value_list=item['value_list'], output_log_line=item['output_logline'])
            elif item['type'].name == 'MatchValueAverageChangeDetector':
                tmp_analyser = func(analysis_context.aminer_config, anomaly_event_handlers, item['timestamp_path'], item['paths'],
                                    item['min_bin_elements'], item['min_bin_time'], debug_mode=item['debug_mode'],
                                    persistence_id=item['persistence_id'], output_log_line=item['output_logline'])
            elif item['type'].name == 'MatchValueStreamWriter':
                stream = sys.stdout
                if item['stream'] == 'sys.stderr':
                    stream = sys.stderr
                tmp_analyser = func(stream, item['paths'], item['separator'].encode(), item['missing_value_string'].encode())
            elif item['type'].name == 'NewMatchPathDetector':
                tmp_analyser = func(analysis_context.aminer_config, anomaly_event_handlers, persistence_id=item['persistence_id'],
                                    auto_include_flag=learn, output_log_line=item['output_logline'])
            elif 'MatchAction' in item['type'].name:
                if comp_name is None:
                    msg = 'The %s must have an id!' % item['type'].name
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
                if item['type'].name == 'EventGenerationMatchAction':
                    tmp_analyser = func(item['event_type'], item['event_message'], anomaly_event_handlers)
                elif item['type'].name == 'AtomFilterMatchAction':
                    tmp_analyser = func(atom_filter, stop_when_handled_flag=item['stop_when_handled_flag'])
                match_action_dict[comp_name] = tmp_analyser
                continue
            elif 'MatchRule' in item['type'].name:
                if comp_name is None:
                    msg = 'The %s must have an id!' % item['type'].name
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
                match_action = None
                if item['match_action'] is not None:
                    if item['match_action'] not in match_action_dict:
                        msg = 'The match action %s does not exist!' % item['match_action']
                        logging.getLogger(DEBUG_LOG_NAME).error(msg)
                        raise ValueError(msg)
                    match_action = match_action_dict[item['match_action']]
                if item['type'].name in ('AndMatchRule', 'OrMatchRule', 'ParallelMatchRule'):
                    sub_rules = []
                    for sub_rule in item['sub_rules']:
                        if sub_rule not in match_rules_dict:
                            msg = 'The sub match rule %s does not exist!' % sub_rule
                            logging.getLogger(DEBUG_LOG_NAME).error(msg)
                            raise ValueError(msg)
                        sub_rules.append(match_rules_dict[sub_rule])
                    tmp_analyser = func(sub_rules, match_action=match_action)
                if item['type'].name == 'ValueDependentDelegatedMatchRule':
                    rule_lookup_dict = {}
                    for rule in item['rule_lookup_dict']:
                        if rule not in match_rules_dict:
                            msg = 'The match rule %s does not exist!' % rule
                            logging.getLogger(DEBUG_LOG_NAME).error(msg)
                            raise ValueError(msg)
                        rule_lookup_dict[rule] = match_rules_dict[rule]
                    tmp_analyser = func(item['paths'], rule_lookup_dict, default_rule=item['default_rule'], match_action=match_action)
                if item['type'].name == 'NegationMatchRule':
                    if item['sub_rule'] not in match_rules_dict:
                        msg = 'The match rule %s does not exist!' % item['sub_rule']
                        logging.getLogger(DEBUG_LOG_NAME).error(msg)
                        raise ValueError(msg)
                    sub_rule = match_rules_dict[item['sub_rule']]
                    tmp_analyser = func(sub_rule, match_action=match_action)
                if item['type'].name in ('PathExistsMatchRule', 'IPv4InRFC1918MatchRule'):
                    tmp_analyser = func(item['path'], match_action=match_action)
                if item['type'].name == 'ValueMatchRule':
                    if isinstance(item['value'], str):
                        item['value'] = item['value'].encode()
                    tmp_analyser = func(item['path'], item['value'], match_action=match_action)
                if item['type'].name == 'ValueListMatchRule':
                    value_list = []
                    for val in item['value_list']:
                        if isinstance(val, str):
                            val = val.encode()
                        value_list.append(val)
                    tmp_analyser = func(item['path'], value_list, match_action=match_action)
                if item['type'].name == 'ValueRangeMatchRule':
                    tmp_analyser = func(item['path'], item['lower_limit'], item['upper_limit'], match_action)
                if item['type'].name == 'StringRegexMatchRule':
                    tmp_analyser = func(item['path'], item['regex'], match_action=match_action)
                if item['type'].name == 'ModuloTimeMatchRule':
                    # tzinfo parameter cannot be used yet..
                    tmp_analyser = func(item['path'], item['seconds_modulo'], item['lower_limit'], item['upper_limit'],
                                        match_action=match_action)
                if item['type'].name == 'ValueDependentModuloTimeMatchRule':
                    # tzinfo parameter cannot be used yet..
                    tmp_analyser = func(item['path'], item['seconds_modulo'], item['paths'], item['limit_lookup_dict'],
                                        default_limit=item['default_limit'], match_action=match_action)
                if item['type'].name == 'DebugMatchRule':
                    tmp_analyser = func(debug_match_result=item['debug_mode'], match_action=match_action)
                if item['type'].name == 'DebugHistoryMatchRule':
                    # object_history is not supported yet..
                    tmp_analyser = func(debug_match_result=item['debug_mode'], match_action=match_action)
                match_rules_dict[comp_name] = tmp_analyser
                continue
            elif item['type'].name == 'CorrelationRule':
                artefact_match_parameters = []
                for match_parameters in item['artefact_match_parameters']:
                    artefact_match_parameters.append(tuple(i for i in match_parameters))
                tmp_analyser = func(item['rule_id'], item['min_time_delta'], item['max_time_delta'], item['max_artefacts_a_for_single_b'],
                                    artefact_match_parameters=artefact_match_parameters)
                correlation_rules[item['rule_id']] = tmp_analyser
                continue
            elif item['type'].name == 'EventClassSelector':
                if item['artefact_a_rules'] is None and item['artefact_b_rules'] is None:
                    msg = 'At least one of the EventClassSelector\'s rules must not be None!'
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
                artefact_a_rules = None
                artefact_b_rules = None
                if item['artefact_a_rules'] is not None:
                    artefact_a_rules = []
                    for rule in item['artefact_a_rules']:
                        if rule not in correlation_rules:
                            msg = 'The correlation rule %s does not exist!' % rule
                            logging.getLogger(DEBUG_LOG_NAME).error(msg)
                            raise ValueError(msg)
                        artefact_a_rules.append(correlation_rules[rule])
                if item['artefact_b_rules'] is not None:
                    artefact_b_rules = []
                    for rule in item['artefact_b_rules']:
                        if rule not in correlation_rules:
                            msg = 'The correlation rule %s does not exist!' % rule
                            logging.getLogger(DEBUG_LOG_NAME).error(msg)
                            raise ValueError(msg)
                        artefact_b_rules.append(correlation_rules[rule])
                tmp_analyser = func(item['action_id'], artefact_a_rules, artefact_b_rules)
                match_action_dict[item['action_id']] = tmp_analyser
                continue
            elif item['type'].name == 'TimeCorrelationViolationDetector':
                ruleset = []
                for rule in item['ruleset']:
                    if rule not in match_rules_dict:
                        msg = 'The match rule %s does not exist!' % rule
                        logging.getLogger(DEBUG_LOG_NAME).error(msg)
                        raise ValueError(msg)
                    ruleset.append(match_rules_dict[rule])
                tmp_analyser = func(analysis_context.aminer_config, ruleset, anomaly_event_handlers, persistence_id=item['persistence_id'],
                                    output_log_line=item['output_logline'])
            elif item['type'].name == 'SimpleMonotonicTimestampAdjust':
                tmp_analyser = func([atom_filter], stop_when_handled_flag=item['stop_when_handled_flag'])
            elif item['type'].name == 'TimestampsUnsortedDetector':
                tmp_analyser = func(analysis_context.aminer_config, anomaly_event_handlers, exit_on_error_flag=item['exit_on_error_flag'],
                                    output_log_line=item['output_logline'])
            elif item['type'].name == 'AllowlistViolationDetector':
                allowlist_rules = []
                for rule in item['allowlist_rules']:
                    if rule not in match_rules_dict:
                        msg = 'The match rule %s does not exist!' % rule
                        logging.getLogger(DEBUG_LOG_NAME).error(msg)
                        raise ValueError(msg)
                    allowlist_rules.append(match_rules_dict[rule])
                tmp_analyser = func(analysis_context.aminer_config, allowlist_rules, anomaly_event_handlers,
                                    output_log_line=item['output_logline'])
            elif item['type'].name == 'EventTypeDetector':
                tmp_analyser = func(
                    analysis_context.aminer_config, anomaly_event_handlers, persistence_id=item['persistence_id'],
                    path_list=item['paths'], min_num_vals=item['min_num_vals'], max_num_vals=item['max_num_vals'],
                    save_values=item['save_values'], track_time_for_TSA=item['track_time_for_TSA'],
                    waiting_time_for_TSA=item['waiting_time_for_TSA'],
                    num_sections_waiting_time_for_TSA=item['num_sections_waiting_time_for_TSA'])
            elif item['type'].name == 'VariableTypeDetector':
                etd = analysis_context.get_component_by_name(item['event_type_detector'])
                if etd is None:
                    msg = 'The defined EventTypeDetector %s does not exist!' % item['event_type_detector']
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
                tmp_analyser = func(
                    analysis_context.aminer_config, anomaly_event_handlers, etd, persistence_id=item['persistence_id'],
                    path_list=item['paths'], gof_alpha=item['gof_alpha'], s_gof_alpha=item['s_gof_alpha'],
                    s_gof_bt_alpha=item['s_gof_bt_alpha'], d_alpha=item['d_alpha'], d_bt_alpha=item['d_bt_alpha'],
                    div_thres=item['div_thres'], sim_thres=item['sim_thres'], indicator_thres=item['indicator_thres'],
                    num_init=item['num_init'], num_update=item['num_update'], num_update_unq=item['num_update_unq'],
                    num_s_gof_values=item['num_s_gof_values'], num_s_gof_bt=item['num_s_gof_bt'], num_d_bt=item['num_d_bt'],
                    num_pause_discrete=item['num_pause_discrete'], num_pause_others=item['num_pause_others'],
                    test_gof_int=item['test_gof_int'], update_var_type_bool=item['update_var_type_bool'],
                    num_stop_update=item['num_stop_update'], silence_output_without_confidence=item['silence_output_without_confidence'],
                    silence_output_except_indicator=item['silence_output_except_indicator'],
                    num_var_type_hist_ref=item['num_var_type_hist_ref'], num_update_var_type_hist_ref=item['num_update_var_type_hist_ref'],
                    num_var_type_considered_ind=item['num_var_type_considered_ind'], num_stat_stop_update=item['num_stat_stop_update'],
                    num_updates_until_var_reduction=item['num_updates_until_var_reduction'],
                    var_reduction_thres=item['var_reduction_thres'], num_skipped_ind_for_weights=item['num_skipped_ind_for_weights'],
                    num_ind_for_weights=item['num_ind_for_weights'], used_multinomial_test=item['used_multinomial_test'],
                    use_empiric_distr=item['use_empiric_distr'], save_statistics=item['save_statistics'],
                    output_log_line=item['output_logline'], ignore_list=item['ignore_list'], constraint_list=item['constraint_list'])
            elif item['type'].name == 'VariableCorrelationDetector':
                etd = analysis_context.get_component_by_name(item['event_type_detector'])
                if etd is None:
                    msg = 'The defined EventTypeDetector %s does not exist!' % item['event_type_detector']
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
                tmp_analyser = func(
                    analysis_context.aminer_config, anomaly_event_handlers, etd, persistence_id=item['persistence_id'],
                    num_init=item['num_init'], num_update=item['num_update'], disc_div_thres=item['disc_div_thres'],
                    num_steps_create_new_rules=item['num_steps_create_new_rules'],
                    num_upd_until_validation=item['num_upd_until_validation'], num_end_learning_phase=item['num_end_learning_phase'],
                    check_cor_thres=item['check_cor_thres'], check_cor_prob_thres=item['check_cor_prob_thres'],
                    check_cor_num_thres=item['check_cor_num_thres'], min_values_cors_thres=item['min_values_cors_thres'],
                    new_vals_alarm_thres=item['new_vals_alarm_thres'], num_bt=item['num_bt'], alpha_bt=item['alpha_bt'],
                    used_homogeneity_test=item['used_homogeneity_test'], alpha_chisquare_test=item['alpha_chisquare_test'],
                    max_dist_rule_distr=item['max_dist_rule_distr'], used_presel_meth=item['used_presel_meth'],
                    intersect_presel_meth=item['intersect_presel_meth'], percentage_random_cors=item['percentage_random_cors'],
                    match_disc_vals_sim_tresh=item['match_disc_vals_sim_tresh'],
                    exclude_due_distr_lower_limit=item['exclude_due_distr_lower_limit'],
                    match_disc_distr_threshold=item['match_disc_distr_threshold'], used_cor_meth=item['used_cor_meth'],
                    used_validate_cor_meth=item['used_validate_cor_meth'],
                    validate_cor_cover_vals_thres=item['validate_cor_cover_vals_thres'],
                    validate_cor_distinct_thres=item['validate_cor_distinct_thres'], ignore_list=item['ignore_list'],
                    constraint_list=item['constraint_list'])
            elif item['type'].name == 'PathValueTimeIntervalDetector':
                tmp_analyser = func(
                    analysis_context.aminer_config, anomaly_event_handlers, persistence_id=item['persistence_id'],
                    target_path_list=item['paths'], ignore_list=item['ignore_list'],
                    allow_missing_values_flag=item['allow_missing_values'],
                    output_log_line=item['output_logline'], time_window_length=item['time_window_length'],
                    max_time_diff=item['max_time_diff'], num_reduce_time_list=item['num_reduce_time_list'], auto_include_flag=learn)
            else:
                tmp_analyser = func(analysis_context.aminer_config, item['paths'], anomaly_event_handlers, auto_include_flag=learn)
            if item['output_event_handlers'] is not None:
                tmp_analyser.output_event_handlers = item['output_event_handlers']
            analysis_context.register_component(tmp_analyser, component_name=comp_name)
            atom_filter.add_handler(tmp_analyser)


def build_event_handlers(analysis_context, anomaly_event_handlers):
    """Build the event handlers."""
    try:
        event_handler_id_list = []
        if 'EventHandlers' in yaml_data and yaml_data['EventHandlers'] is not None:
            for item in yaml_data['EventHandlers']:
                if item['id'] in event_handler_id_list:
                    raise ValueError('Config-Error: The id "%s" occurred multiple times in EventHandlers!' % item['id'])
                event_handler_id_list.append(item['id'])
                func = item['type'].func
                ctx = None
                if item['type'].name == 'StreamPrinterEventHandler':
                    if 'output_file_path' in item:
                        try:
                            stream = open(item['output_file_path'], 'w+')
                            ctx = func(analysis_context, stream)
                        except OSError as e:
                            msg = 'Error occured when opening stream to output_file_path %s. Error: %s' % (item['output_file_path'], e)
                            logging.getLogger(DEBUG_LOG_NAME).error(msg)
                            print(msg, file=sys.stderr)
                    else:
                        ctx = func(analysis_context)
                if item['type'].name == 'DefaultMailNotificationEventHandler':
                    ctx = func(analysis_context)
                if item['type'].name == 'SyslogWriterEventHandler':
                    ctx = func(analysis_context, item['instance_name'])
                if item['type'].name == 'KafkaEventHandler':
                    import configparser
                    import os
                    config = configparser.ConfigParser()
                    if os.access(item['cfgfile'], os.R_OK):
                        config.read(item['cfgfile'])
                    else:
                        msg = "%s does not exist or is not readable" % item['cfgfile']
                        logging.getLogger(DEBUG_LOG_NAME).error(msg)
                        raise ValueError(msg)
                    options = dict(config.items("DEFAULT"))
                    for key, val in options.items():
                        try:
                            if key == "sasl_plain_username":
                                continue
                            options[key] = int(val)
                        except:  # skipcq: FLK-E722
                            pass
                    ctx = func(analysis_context, item['topic'], options)
                if ctx is None:
                    ctx = func(analysis_context)
                if item['json'] is True or item['type'].name == 'KafkaEventHandler':
                    from aminer.events.JsonConverterHandler import JsonConverterHandler
                    ctx = JsonConverterHandler([ctx], analysis_context)
                anomaly_event_handlers.append(ctx)
            return event_handler_id_list
        raise KeyError()
    except KeyError:
        # Add stdout stream printing for debugging, tuning.
        from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
        anomaly_event_handlers.append(StreamPrinterEventHandler(analysis_context, stream=sys.stderr))
    return None


def tuple_transformation_function_demo_print_every_10th_value(match_value_list):
    """Only allow output of the EnhancedNewMatchPathValueComboDetector after every 10th element."""
    extra_data = enhanced_new_match_path_value_combo_detector_reference.known_values_dict.get(tuple(match_value_list), None)
    if extra_data is not None:
        mod = 10
        if (extra_data[2] + 1) % mod == 0:
            enhanced_new_match_path_value_combo_detector_reference.auto_include_flag = False
        else:
            enhanced_new_match_path_value_combo_detector_reference.auto_include_flag = True
    return match_value_list


def parse_json_yaml(json_dict, parser_model_dict):
    """Parse an yaml configuration for json."""
    key_parser_dict = {}
    for key in json_dict.keys():
        value = json_dict[key]
        if key is None:
            key = 'null'
        if key is False:
            key = 'false'
        if key is True:
            key = 'true'
        if isinstance(value, dict):
            key_parser_dict[key] = parse_json_yaml(value, parser_model_dict)
        elif isinstance(value, list):
            if isinstance(value[0], dict):
                key_parser_dict[key] = [parse_json_yaml(value[0], parser_model_dict)]
            elif value[0] == "ALLOW_ALL":
                key_parser_dict[key] = value
            elif parser_model_dict.get(value[0]) is None:
                msg = 'The parser model %s does not exist!' % value[0]
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise ValueError(msg)
            else:
                key_parser_dict[key] = [parser_model_dict.get(value[0])]
        elif value == "ALLOW_ALL":
            key_parser_dict[key] = value
        elif parser_model_dict.get(value) is None:
            msg = 'The parser model %s does not exist!' % value
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        else:
            key_parser_dict[key] = parser_model_dict.get(value)
    return key_parser_dict
