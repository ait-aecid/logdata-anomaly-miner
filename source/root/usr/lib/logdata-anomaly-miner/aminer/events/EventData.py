from aminer.input.LogAtom import LogAtom
import json
from datetime import datetime
from aminer.analysis import CONFIG_KEY_LOG_LINE_PREFIX

class EventData(object):

    def __init__(self, eventType, eventMessage, sortedLogLines, eventData, logAtom, eventSource, analysisContext):
      self.eventType = eventType
      self.eventMessage = eventMessage
      self.sortedLogLines = sortedLogLines
      self.eventData = eventData
      self.eventSource = eventSource
      self.analysisContext = analysisContext
      if analysisContext is not None:
        self.description = '"%s"' % analysisContext.get_name_by_component(eventSource)
      else:
        self.description = ''
      if logAtom is None:
        return
      self.logAtom = logAtom
    
    def receiveEventString(self):
      message = ''
      if hasattr(self, "logAtom"):
        if self.logAtom.getTimestamp() is None:
          self.logAtom.atomTime = datetime.now()
        if not isinstance(self.logAtom.getTimestamp(), datetime):
          atomTime = datetime.fromtimestamp(self.logAtom.getTimestamp())
        else:
          atomTime = self.logAtom.getTimestamp()
        message += '%s ' % atomTime.strftime("%Y-%m-%d %H:%M:%S")
        message += '%s\n' % (self.eventMessage)
        message += '%s: %s (%d lines)\n' % (self.eventSource.__class__.__name__, self.description, len(self.sortedLogLines))
      else:
        message += '%s (%d lines)\n' % (self.eventMessage, len(self.sortedLogLines))
      for line in self.sortedLogLines:
        if isinstance(line, bytes):
          if line is not b'':
            message += '  '+line.decode("utf-8")+'\n'
        else:
          originalLogLinePrefix = self.analysisContext.aminer_config.configProperties.get(CONFIG_KEY_LOG_LINE_PREFIX)
          if originalLogLinePrefix is not None and line.startswith(originalLogLinePrefix):
            message+= line+'\n'
          elif line is not '':
            message += '  '+line+'\n'
            
      #uncomment the following line for debugging..
      #print("%s" % message)
      return message