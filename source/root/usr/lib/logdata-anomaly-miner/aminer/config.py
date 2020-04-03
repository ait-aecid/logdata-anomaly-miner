# This is a template for the "aminer" logdata-anomaly-miner tool. Copy
# it to "config.py" and define your ruleset.

configProperties = {}
yamldata = None

# Define the list of log resources to read from: the resources
# named here do not need to exist when aminer is started. This
# will just result in a warning. However if they exist, they have
# to be readable by the aminer process! Supported types are:
# * file://[path]: Read data from file, reopen it after rollover
# * unix://[path]: Open the path as UNIX local socket for reading
configProperties['LogResourceList'] = ['file:///var/log/apache2/access.log']

# Define the uid/gid of the process that runs the calculation
# after opening the log files:
configProperties['AMinerUser'] = 'aminer'
configProperties['AMinerGroup'] = 'aminer'

# This method loads the yaml-configfile and overrides defaults if
# neccessary
def loadYaml(configFile):
  global yamldata

  import yaml
  from cerberus import Validator
  import os
  with open(configFile) as yamlfile:
    try:
        yamldata = yaml.safe_load(yamlfile)
    except yaml.YAMLError as exception:
        raise exception
    
  schema = eval(open(os.path.dirname(os.path.abspath(__file__)) + '/' + 'schema.py', 'r').read())
  v = Validator(schema)
  # TODO: Error-handling
  if v.validate(yamldata, schema):
    test = v.normalized(yamldata)
    yamldata = test
  else:
    raise ValueError(v.errors)

  # Set default values
  for key,val in yamldata.items():
    configProperties[str(key)] = val;


# Read and store information to be used between multiple invocations
# of AMiner in this directory. The directory must only be accessible
# to the 'AMinerUser' but not group/world readable. On violation,
# AMiner will refuse to start. When undefined, '/var/lib/aminer'
# is used.
# configProperties['Core.PersistenceDir'] = '/var/lib/aminer'

# Add your ruleset here:
def buildAnalysisPipeline(analysisContext):
  """Define the function to create pipeline for parsing the log
  data. It has also to define an AtomizerFactory to instruct AMiner
  how to process incoming data streams to create log atoms from
  them."""
  import importlib
  import configparser   
  import sys   
  import json
#  from pprint import pprint

  parserModelDict = dict()
  start = None

  global yamldata
  for item in yamldata['Parser']:
      if item['id'] == 'START':
          start = item
          continue
      if item['type'].endswith('ModelElement') and item['id'] != 'START':
          func =  getattr(__import__("aminer.parsing", fromlist=[item['type']]),item['type'])
          if isinstance(item['args'],list):
            parserModelDict[item['id']] = func(item['name'],item['args'])
          else:
            parserModelDict[item['id']] = func(item['name'],item['args'].encode())
      else:
          func =  getattr(__import__(item['type']),'getModel')
          parserModelDict[item['id']] = func()

  argslist = list()

  func = getattr(__import__("aminer.parsing", fromlist=[start['type']]),start['type'])
  if isinstance(start['args'],list):
      for i in parserModelDict:
          argslist.append(parserModelDict[i])
      parsingModel = func(start['name'],argslist)
  else:
      parsingModel = func(start['name'],[parserModelDict[start['args']]])
          

# Some generic imports.
  from aminer.analysis import AtomFilters

# Create all global handler lists here and append the real handlers
# later on.
# Use this filter to distribute all atoms to the analysis handlers.
  atomFilter = AtomFilters.SubhandlerFilter(None)
  anomalyEventHandlers = []

# Now define the AtomizerFactory using the model. A simple line
# based one is usually sufficient.
  from aminer.input import SimpleByteStreamLineAtomizerFactory
  if yamldata['Input']['MultiSource'] == True:
        from aminer.input import SimpleMultisourceAtomSync
        analysis_context.atomizer_factory = SimpleByteStreamLineAtomizerFactory(
            parsing_model, [SimpleMultisourceAtomSync([atomFilter], sync_wait_time=5)], 
            anomaly_event_handlers, default_timestamp_path=yamldata['Input']['TimestampPath'])
  else:
        analysisContext.atomizerFactory = SimpleByteStreamLineAtomizerFactory(
            parsingModel, [atomFilter], anomalyEventHandlers,
            defaultTimestampPath=yamldata['Input']['TimestampPath'])

# Just report all unparsed atoms to the event handlers.
  if yamldata['Input']['Verbose'] == True:
    from aminer.input import VerboseUnparsedAtomHandler
    atomFilter.addHandler(VerboseUnparsedAtomHandler(anomalyEventHandlers, parsingModel),       stopWhenHandledFlag=True)
  else:
    from aminer.input import SimpleUnparsedAtomHandler
    atomFilter.addHandler(
          SimpleUnparsedAtomHandler(anomalyEventHandlers),
          stopWhenHandledFlag=True)

  from aminer.analysis import NewMatchPathDetector
  try:
      learn = yamldata['LearnMode']
  except:
      learn = True
  newMatchPathDetector = NewMatchPathDetector(
      analysisContext.aminerConfig, anomalyEventHandlers, autoIncludeFlag=learn)
  analysisContext.registerComponent(newMatchPathDetector, componentName=None)
  atomFilter.addHandler(newMatchPathDetector)

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
        tmpAnalyser = func(analysisContext.aminerConfig,item['paths'], anomalyEventHandlers, autoIncludeFlag=learn,persistenceId=item['persistence_id'],outputLogLine=item['output_logline'])
      elif item['type'] == 'NewMatchPathValueComboDetector':
        tmpAnalyser = func(analysisContext.aminerConfig,item['paths'], anomalyEventHandlers, autoIncludeFlag=learn,persistenceId=item['persistence_id'],allowMissingValuesFlag=item['allow_missing_values'],outputLogLine=item['output_logline'])
      else:  
        tmpAnalyser = func(analysisContext.aminerConfig,item['paths'], anomalyEventHandlers, autoIncludeFlag=learn)
      analysisContext.registerComponent(tmpAnalyser, componentName=compName)
      atomFilter.addHandler(tmpAnalyser)


  try:
      for item in yamldata['EventHandlers']:
          func =  getattr(__import__("aminer.events", fromlist=[item['type']]),item['type'])
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
#            kafkaEventHandler = func(analysisContext.aminerConfig, item['args'][0], options)
#            from aminer.events import JsonConverterHandler
#            anomalyEventHandlers.append(JsonConverterHandler(analysisContext.aminerConfig, messageQueueEventHandlers,
#                analysisContext, learningMode))
#          else:    
          ctx = func(analysisContext)
          anomalyEventHandlers.append(ctx)

  except KeyError:
      # Add stdout stream printing for debugging, tuning.
      from aminer.events import StreamPrinterEventHandler
      anomalyEventHandlers.append(StreamPrinterEventHandler(analysisContext))
