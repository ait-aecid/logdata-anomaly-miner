"""This component counts occurring combinations of values
and periodically sends the results as a report."""

import time
import datetime
import sys

from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.input import AtomHandlerInterface
from aminer.util import TimeTriggeredComponentInterface
from aminer.util import PersistencyUtil

class ParserCount(AtomHandlerInterface, TimeTriggeredComponentInterface):
  """This class creates a counter for path value combinations."""

  def __init__(self, aminer_config, target_path_list, report_interval,
               report_event_handlers, reset_after_report_flag=True):
    """Initialize the ParserCount component.
    @param aminer"""
    self.targetPathList = target_path_list
    self.reportInterval = report_interval
    self.reportEventHandlers = report_event_handlers
    self.resetAfterReportFlag = reset_after_report_flag
    self.initial = True
    self.countDict = {}

    for targetPath in self.targetPathList: 
      self.countDict[targetPath] = 0

  def get_time_trigger_class(self):
    """Get the trigger class this component can be registered
    for. This detector only needs persisteny triggers in real
    time."""
    return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

  def receive_atom(self, log_atom):
    match_dict = log_atom.parser_match.get_match_dictionary()
    matchValueList = []
    for targetPath in self.targetPathList:
      matchElement = match_dict.get(targetPath, None)
      if matchElement is not None:
        self.countDict[targetPath] += 1

    return True

  def do_timer(self, trigger_time):
    """Check current ruleset should be persisted"""
    if self.initial == True:
      # Skip reporting at the beginning when nothing is parsed yet.
      self.initial = False
    else:
      self.send_report()

    return self.reportInterval

  def do_persist(self):
    """Immediately write persistence data to storage."""
    return False


  def send_report(self):
    """Sends a report to the event handlers."""
    outputString = 'Parsed paths in the last ' + str(self.reportInterval) + ' seconds:\n'

    for k in self.countDict.keys():
      c = self.countDict[k]
      outputString += '\t' + str(k) + ': ' + str(c) + '\n'

    event_data = {}
    event_data['StatusInfo'] = self.countDict
    event_data['FromTime'] = datetime.datetime.utcnow().timestamp() - self.reportInterval
    event_data['ToTime'] = datetime.datetime.utcnow().timestamp()
    for listener in self.reportEventHandlers:
      listener.receive_event('Analysis.%s' % self.__class__.__name__,
                            'Count report', [outputString], event_data, None, self)
    #print(outputString, file=sys.stderr)

    if self.resetAfterReportFlag:
      for targetPath in self.targetPathList: 
        self.countDict[targetPath] = 0

