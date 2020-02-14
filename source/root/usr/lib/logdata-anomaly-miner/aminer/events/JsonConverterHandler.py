"""This module defines an event handler that converts an event to JSON."""

import json
import datetime
import time
import types
import base64

from aminer.events import EventHandlerInterface
from aminer.events.EventData import EventData
from aminer.input.LogAtom import LogAtom

class JsonConverterHandler(EventHandlerInterface):
  """This class implements an event record listener, that will
  convert event data to JSON format."""
  def __init__(self, jsonEventHandlers, analysisContext):
    self.jsonEventHandlers = jsonEventHandlers
    self.analysisContext = analysisContext

  def receiveEvent(self, eventType, eventMessage, sortedLogLines, eventData, logAtom,
                   eventSource):
    """Receive information about a detected event."""
    self.eventData = EventData(eventType, eventMessage, sortedLogLines, eventData, logAtom, eventSource, self.analysisContext)
    jsonError = ''

    logData = dict()
    if isinstance(logAtom.rawData, bytes):
      logData['RawLogData'] = bytes.decode(logAtom.rawData)
    else:
      logData['RawLogData'] = logAtom.rawData
    if logAtom.atomTime is not None:
      if isinstance(logAtom.atomTime, datetime.datetime):
        logData['Timestamp'] = str(logAtom.atomTime.strftime('%Y-%m-%dT%H:%M:%SZ'))
      else:
        logData['Timestamp'] = logAtom.atomTime
    else:
      logData['Timestamp'] = str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
    logData['LogLinesCount'] = len(sortedLogLines)
    if logAtom.parserMatch is not None:
      logData['AnnotatedMatchElement'] = logAtom.parserMatch.matchElement.annotateMatch('')

    analysisComponent = dict()
    analysisComponent['AnalysisComponentIdentifier'] = self.analysisContext.getIdByComponent(eventSource)
    if eventSource.__class__.__name__ == 'ExtractedData_class':
      analysisComponent['AnalysisComponentType'] = 'DistributionDetector'
    else:
      analysisComponent['AnalysisComponentType'] = str(eventSource.__class__.__name__)
    analysisComponent['AnalysisComponentName'] = self.analysisContext.getNameByComponent(eventSource)
    analysisComponent['Message'] = eventMessage
    analysisComponent['PersistenceFileName'] = eventSource.persistenceId
    if hasattr(eventSource, 'autoIncludeFlag'):
      analysisComponent['TrainingMode'] = eventSource.autoIncludeFlag

    oldAnalysisComponent = eventData.get('AnalysisComponent', None)
    if oldAnalysisComponent is not None:
      for key in oldAnalysisComponent:
        if key in analysisComponent.keys():
          jsonError += "AnalysisComponent attribute '%s' is already in use and can not be overwritten!\n" % key
          continue
        analysisComponent[key] = oldAnalysisComponent.get(key, None)

    eventData['LogData'] = logData
    eventData['AnalysisComponent'] = analysisComponent
    if jsonError != '':
      eventData['JsonError'] = jsonError

    # if eventSource.__class__.__name__ == 'VariableTypeDetector' and len(eventData) >= 4 and isinstance(eventData[3], float):
    #   detector['Confidence'] = float(eventData[3])
    #   eventData['Confidence'] = float(eventData[3])
    # else:
    #   detector['Confidence'] = 1.0
    #   eventData['Confidence'] = 1.0

    # if hasattr(eventSource, 'targetPathList'):
    #   path = eventSource.targetPathList[0]
    #   path_parts = path.split('/')
    #   short_path = ''
    #   for i in range(1, len(path_parts) - 1):
    #     short_path += path_parts[i] + '/'
    #   eventData['Path'] = short_path

    jsonData = json.dumps(eventData, indent=2)
    res = [''] * len(sortedLogLines)
    res[0] = str(jsonData)
    #print(jsonData)

    for listener in self.jsonEventHandlers:
      listener.receiveEvent(eventType, eventMessage, res, {}, logAtom, eventSource)

    return
