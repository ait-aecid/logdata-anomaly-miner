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

# This method loads the yaml-configfile and overrides defaults if
# neccessary
def loadYaml(config_file):
    # We might be able to remove this and us it like the config_properties
    # skipcq: PYL-W0603
    global yamldata

    import yaml
    from cerberus import Validator
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

    v = Validator(schema)
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
    import configparser
    # skipcq: PYL-W0611
    import sys
#  import json
#  from pprint import pprint

    parserModelDict = {}
    start = None
    wscount = 0
    whitespace_str = b' '

    # We might be able to remove this and us it like the config_properties
    # skipcq: PYL-W0603
    global yamldata
    for item in yamldata['Parser']:
        if item['id'] == 'START':
            start = item
            continue
        if item['type'].endswith('ModelElement') and item['id'] != 'START':
            func = getattr(__import__("aminer.parsing", fromlist=[item['type']]), item['type'])
            if 'args' in item:
                if isinstance(item['args'], list):
                    # encode string to bytearray
                    for j in range(len(item['args'])):
                        item['args'][j] = item['args'][j].encode()
                    parserModelDict[item['id']] = func(item['name'], item['args'])
                else:
                    parserModelDict[item['id']] = func(item['name'], item['args'].encode())
            else:
                parserModelDict[item['id']] = func(item['name'])
        else:
            # skipcq: PTC-W0034
            func = getattr(__import__(item['type']), 'get_model')
            parserModelDict[item['id']] = func()

    argslist = []
    if start['type'].endswith('ModelElement'):
        # skipcq: PTC-W0034
        func = getattr(__import__("aminer.parsing", fromlist=[start['type']]), start['type'])
    else:
        # skipcq: PTC-W0034
        func = getattr(__import__(start['type']), 'get_model')
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
            parsing_model = func(start['name'], argslist)
        else:
            parsing_model = func(start['name'], [parserModelDict[start['args']]])
    else:
        parsing_model = func()

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
                analysis_context.aminer_config, item['paths'],
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
                whitelisted_paths=item['whitelisted_paths'],
                persistence_id=item['persistence_id'])
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
                #whitelisted_paths=item['whitelisted_paths'],
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
