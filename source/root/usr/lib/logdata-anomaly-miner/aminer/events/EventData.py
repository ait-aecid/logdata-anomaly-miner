from aminer.input.LogAtom import LogAtom
import json
from datetime import datetime
from aminer.analysis import CONFIG_KEY_LOG_LINE_PREFIX

class EventData(object):

    def __init__(self, event_type, event_message, sorted_log_lines, event_data, log_atom, event_source, analysis_context):
      self.event_type = event_type
      self.event_message = event_message
      self.sorted_log_lines = sorted_log_lines
      self.event_data = event_data
      self.event_source = event_source
      self.analysis_context = analysis_context
      if analysis_context is not None:
        self.description = '"%s"' % analysis_context.get_name_by_component(event_source)
      else:
        self.description = ''
      if log_atom is None:
        return
      self.log_atom = log_atom
    
    def receive_event_string(self):
      message = ''
      if hasattr(self, "log_atom"):
        if self.log_atom.get_timestamp() is None:
          self.log_atom.atomTime = datetime.now()
        if isinstance(self.log_atom.get_timestamp(), type(None)):
          import time
          self.log_atom.atom_time = time.time()
        if not isinstance(self.log_atom.get_timestamp(), datetime):
          atom_time = datetime.fromtimestamp(self.log_atom.get_timestamp())
        else:
          atom_time = self.log_atom.get_timestamp()
        message += '%s ' % atom_time.strftime("%Y-%m-%d %H:%M:%S")
        message += '%s\n' % (self.event_message)
        message += '%s: %s (%d lines)\n' % (self.event_source.__class__.__name__, self.description, len(self.sorted_log_lines))
      else:
        message += '%s (%d lines)\n' % (self.event_message, len(self.sorted_log_lines))
      for line in self.sorted_log_lines:
        if isinstance(line, bytes):
          if line is not b'':
            message += '  '+line.decode("utf-8")+'\n'
        else:
          original_log_line_prefix = self.analysis_context.aminer_config.configProperties.get(CONFIG_KEY_LOG_LINE_PREFIX)
          if original_log_line_prefix is not None and line.startswith(original_log_line_prefix):
            message+= line+'\n'
          elif line is not '':
            message += '  '+line+'\n'
            
      #uncomment the following line for debugging..
      #print("%s" % message)
      return message