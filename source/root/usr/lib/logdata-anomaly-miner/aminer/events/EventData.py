from aminer.input.LogAtom import LogAtom
from datetime import datetime

class EventData(object):

    def __init__(self, eventType, eventMessage, sortedLogLines, eventData, eventSource, analysisContext):
      self.eventType = eventType
      self.eventMessage = eventMessage
      self.sortedLogLines = sortedLogLines
      self.eventSource = eventSource
      if analysisContext is not None:
        self.description = '"%s"' % analysisContext.getNameByComponent(eventSource)
      else:
        self.description = ''
      if isinstance(eventData, LogAtom):
        self.logAtom = eventData
#         self.dataList = None
#       elif isinstance(eventData, list) and len(eventData) == 2:
#         if isinstance(eventData[0], LogAtom):
#           self.logAtom = eventData[0]
#         if isinstance(eventData[1], tuple):
#           self.dataList = list(eventData[1])
#         elif isinstance(eventData[1], list):
#           self.dataList = eventData[1]
      else:
        raise(Exception("wrong eventData type!"))
    
    def receiveEventString(self):
      if not isinstance(self.logAtom.getTimestamp(), datetime):
        atomTime = datetime.fromtimestamp(self.logAtom.getTimestamp())
      else:
        atomTime = self.logAtom.getTimestamp()
      message = '%s ' % atomTime.strftime("%Y-%m-%d %H:%M:%S")
      message += '%s\n' % (self.eventMessage)
      if self.logAtom.getTimestamp() is not None:
        message += '%s: %s (%d lines)\n' % (self.logAtom.source.__class__.__name__, self.description, len(self.sortedLogLines))
      #if self.logAtom.parserMatch is not None:
      #  message += '  '+self.logAtom.parserMatch.matchElement.annotateMatch('')+'\n'
      for line in self.sortedLogLines:
        if isinstance(line, bytes):
          if line is not b'':
            message += '  '+line.decode("utf-8")+'\n'
        else:
          if line is not '':
            message += '  '+line+'\n'
      #if self.dataList is not None:
      #  for line in self.dataList:
      #    message += '  '+line+'\n'
      print("%s" % message)
      return message
        