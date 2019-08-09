from aminer.input.LogAtom import LogAtom
from datetime import datetime
from aminer.analysis import CONFIG_KEY_LOG_LINE_PREFIX

class EventData(object):

    def __init__(self, eventType, eventMessage, sortedLogLines, eventData, eventSource, analysisContext):
      self.eventType = eventType
      self.eventMessage = eventMessage
      self.sortedLogLines = sortedLogLines
      self.eventSource = eventSource
      self.analysisContext = analysisContext
      if analysisContext is not None:
        self.description = '"%s"' % analysisContext.getNameByComponent(eventSource)
      else:
        self.description = ''
      if isinstance(eventData, LogAtom):
        self.logAtom = eventData
      elif isinstance(eventData, list):
        self.eventData = eventData
      elif eventData is None:
        return
      else:
        raise(Exception("wrong eventData type!"))
    
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
        size = 0
        line = None
        for line in self.sortedLogLines:
          if isinstance(line, bytes):
            line = repr(line)
          size += line.count("\n")
        if size is 0:
          size = len(self.sortedLogLines)
        elif not line.endswith("\n"):
          size += 1
        message += '%s: %s (%d lines)\n' % (self.eventSource.__class__.__name__, self.description, size)
#### https://stackoverflow.com/questions/28802417/how-to-count-lines-in-multi-lined-strings
####        message += '%s: %s (%d lines)\n' % (self.eventSource.__class__.__name__, self.description, len([self.logAtom.rawData]))
      elif hasattr(self, "eventData"):
        for line in self.eventData:
          if isinstance(line, bytes):
            if line is not b'':
              message += '  '+line.decode("utf-8")+'\n'
            else:
              if line is not '':
                message += '  '+line+'\n'
      else:
        size = 0
        line = None
        for line in self.sortedLogLines:
          if isinstance(line, bytes):
            line = repr(line)
          size += line.count("\n")
        if size is 0:
          size = len(self.sortedLogLines)
        elif not line.endswith("\n"):
          size += 1
        message += '%s (%d lines)\n' % (self.eventMessage, size)
####          message += '%s (%d lines)\n' % (self.eventMessage, len([self.logAtom.rawData]))
      for line in self.sortedLogLines:
        if isinstance(line, bytes):
          if line is not b'':
            message += '  '+line.decode("utf-8")+'\n'
        else:
          originalLogLinePrefix = self.analysisContext.aminerConfig.configProperties.get(CONFIG_KEY_LOG_LINE_PREFIX)
          if originalLogLinePrefix is not None and line.startswith(originalLogLinePrefix):
            message+= line+'\n'
          elif line is not '':
            message += '  '+line+'\n'
            
      #uncomment the following line for debugging..
      #print("%s" % message)
      return message
        