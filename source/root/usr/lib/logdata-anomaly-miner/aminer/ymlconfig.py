config_properties = {}
yamldata = None

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
  # TODO: Error-handling
  if v.validate(yamldata, schema):
    test = v.normalized(yamldata)
    yamldata = test
  else:
    raise ValueError(v.errors)

  # Set default values
  for key,val in yamldata.items():
    config_properties[str(key)] = val;


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
  import importlib
  import configparser   
  import sys   
#  import json
#  from pprint import pprint

  parserModelDict = {}
  start = None
  wscount = 0
  whitespace_str = b' '

  # We might be able to remove this and us it like the config_properties
  # skipqc: PYL-W0603
  global yamldata
  for item in yamldata['Parser']:
      if item['id'] == 'START':
          start = item
          continue
      if item['type'].endswith('ModelElement') and item['id'] != 'START':
          func =  getattr(__import__("aminer.parsing", fromlist=[item['type']]),item['type'])
          try:
              if isinstance(item['args'],list):
                # encode string to bytearray
                for j in range(len(item['args'])):
                    item['args'][j] = item['args'][j].encode()
                parserModelDict[item['id']] = func(item['name'],item['args'])
              else:
                parserModelDict[item['id']] = func(item['name'],item['args'].encode())
          except:
              parserModelDict[item['id']] = func(item['name'])
      else:
          # skipcq: PTC-W0034
          func =  getattr(__import__(item['type']),'get_model')
          parserModelDict[item['id']] = func()

  argslist = []
  if start['type'].endswith('ModelElement'):
    # skipcq: PTC-W0034
    func = getattr(__import__("aminer.parsing", fromlist=[start['type']]),start['type'])
  else:
    # skipcq: PTC-W0034
    func =  getattr(__import__(start['type']),'get_model')
  try:
    if isinstance(start['args'],list):
        for i in start['args']:
            if i == 'WHITESPACE':
                from aminer.parsing import FixedDataModelElement
                sp = 'sp%d' % wscount
                argslist.append(FixedDataModelElement(sp, whitespace_str))
                wscount += 1
            else:
                argslist.append(parserModelDict[i])
        parsing_model = func(start['name'],argslist)
    else:
        parsing_model = func(start['name'],[parserModelDict[start['args']]])
  except:
    parsing_model = func(start['name'])
          

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
    atomFilter.add_handler(VerboseUnparsedAtomHandler(anomaly_event_handlers, parsing_model),       stop_when_handled_flag=True)
  else:
    from aminer.input import SimpleUnparsedAtomHandler
    atomFilter.add_handler(
          SimpleUnparsedAtomHandler(anomaly_event_handlers),
          stop_when_handled_flag=True)

  from aminer.analysis import NewMatchPathDetector
  try:
      learn = yamldata['LearnMode']
  except:
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
      try: 
        learn = yamldata['LearnMode']
      except:
        learn = item['learnMode']
      func =  getattr(__import__("aminer.analysis", fromlist=[item['type']]),item['type'])
      if item['type'] == 'NewMatchPathValueDetector':
        tmpAnalyser = func(analysis_context.aminer_config,item['paths'], anomaly_event_handlers, auto_include_flag=learn,persistence_id=item['persistence_id'],output_log_line=item['output_logline'])
      elif item['type'] == 'NewMatchPathValueComboDetector':
        tmpAnalyser = func(analysis_context.aminer_config,item['paths'], anomaly_event_handlers, auto_include_flag=learn,persistence_id=item['persistence_id'],allow_missing_values_flag=item['allow_missing_values'],output_log_line=item['output_logline'])
      else:  
        tmpAnalyser = func(analysis_context.aminer_config,item['paths'], anomaly_event_handlers, auto_include_flag=learn)
      analysis_context.register_component(tmpAnalyser, component_name=compName)
      atomFilter.add_handler(tmpAnalyser)


  try:
      for item in yamldata['EventHandlers']:
          func =  getattr(__import__("aminer.events", fromlist=[item['type']]),item['type'])
          ctx = None
          if item['type'] == 'StreamPrinterEventHandler':
             if item['json'] is True:
               from aminer.events import JsonConverterHandler
               ctx = JsonConverterHandler([func(analysis_context)], analysis_context)
             else:
               ctx = func(analysis_context)
#          if item['type'] == 'KafkaEventHandler':
#            try: 
#              item['args'][0]
#            except:
#              raise ValueError("Kafka-Topic not defined")
#            try: 
#              kafkaconfig = item['args'][1]
#            except:
#              kafkaconfig = '/etc/aminer/kafka-client.conf'
#            config = configparser.ConfigParser()
#            config.read(kafkaconfig)
#            options = dict(config.items("DEFAULT"))
#            for key, val in options.items():
#              try:
#                if key == "sasl_plain_username":
#                  continue
#                options[key] = int(val)
#              except:
#                pass
#            kafkaEventHandler = func(analysis_context.aminer_config, item['args'][0], options)
#            from aminer.events import JsonConverterHandler
#            anomaly_event_handlers.append(JsonConverterHandler(analysis_context.aminer_config, messageQueueEventHandlers,
#                analysis_context, learningMode))
#          else:    
          if ctx is None:
              ctx = func(analysis_context)
          anomaly_event_handlers.append(ctx)

  except KeyError:
      # Add stdout stream printing for debugging, tuning.
      from aminer.events import StreamPrinterEventHandler
      anomaly_event_handlers.append(StreamPrinterEventHandler(analysis_context))
