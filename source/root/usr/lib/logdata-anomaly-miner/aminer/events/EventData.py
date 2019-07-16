from aminer.input.LogAtom import LogAtom

class EventData(object):

    def __init__(self, eventType, eventMessage, sortedLogLines, eventData, eventSource):
      self.eventType = eventType
      self.eventMessage = eventMessage
      self.sortedLogLines = sortedLogLines
      self.eventSource = eventSource
      if isinstance(eventData, LogAtom):
        self.logAtom = eventData
      elif isinstance(eventData, list) and len(eventData) == 2:
        if isinstance(eventData[0], LogAtom):
          self.logAtom = eventData[0]
        if isinstance(eventData[1], tuple):
          self.dataList = list(eventData[1])
        elif isinstance(eventData[1], list):
          self.dataList = eventData[1]
      else:
        raise(Exception("wrong eventData type!"))
    
    def receiveEventString(self):
      message = '%s (%d lines)\n' % (self.eventMessage, len(self.sortedLogLines))
      for line in self.sortedLogLines:
        message += '  '+line.decode("utf-8")+'\n'
      if self.logAtom.getTimestamp() is not None:
        message += '  [%s/%s]' % (self.logAtom.getTimestamp(), self.logAtom.source)
      if self.logAtom.parserMatch is not None:
        message += ' '+self.logAtom.parserMatch.matchElement.annotateMatch('')+'\n'
      print("%s" % message)
      return message
        