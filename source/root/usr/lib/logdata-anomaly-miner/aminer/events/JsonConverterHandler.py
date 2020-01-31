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
  def __init__(self, jsonEventHandlers, analysisContext, trainingMode):
    self.jsonEventHandlers = jsonEventHandlers
    self.analysisContext = analysisContext
    self.trainingMode = trainingMode

  def receiveEvent(self, eventType, eventMessage, sortedLogLines, eventData, logAtom,
                   eventSource):
    """Receive information about a detected event."""
    self.eventData = EventData(eventType, eventMessage, sortedLogLines, eventData, logAtom, eventSource, self.analysisContext)

    detector = dict()
    detector['ID'] = self.analysisContext.getIdByComponent(eventSource)
    if eventSource.__class__.__name__ == 'ExtractedData_class':
      detector['Type'] = 'DistributionDetector'
    else:
      detector['Type'] = str(eventSource.__class__.__name__)
    detector['Description'] = self.analysisContext.getNameByComponent(eventSource)

    if eventSource.__class__.__name__ == 'VariableTypeDetector' and len(eventData) >= 4 and isinstance(eventData[3], float):
      detector['Confidence'] = float(eventData[3])
      eventData['Confidence'] = float(eventData[3])
    else:
      detector['Confidence'] = 1.0
      eventData['Confidence'] = 1.0

    eventData['Detectors'] = [detector]
    eventData['Description'] = eventMessage
    eventData['Timestamp'] = str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
    eventData['rawData'] = bytes.decode(logAtom.rawData)
    eventData['annotatedMatchElement'] = logAtom.parserMatch.matchElement.annotateMatch('')
    eventData['eventSource'] = eventSource.__class__.__name__
    eventData['logLinesCount'] = len(sortedLogLines)
    eventData['trainingMode'] = self.trainingMode

    if hasattr(eventSource, 'targetPathList'):
      path = eventSource.targetPathList[0]
      path_parts = path.split('/')
      short_path = ''
      for i in range(1, len(path_parts) - 1):
        short_path += path_parts[i] + '/'
      eventData['Path'] = short_path

    jsonData = json.dumps(eventData, indent=2)
    #print(jsonData)

    for listener in self.jsonEventHandlers:
      listener.receiveEvent(eventType, eventMessage, [str(jsonData)], {}, logAtom, eventSource)

    return
