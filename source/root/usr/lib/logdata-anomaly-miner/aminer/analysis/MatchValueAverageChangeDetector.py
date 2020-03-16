"""This module defines a detector that reports diverges from
an average."""

import time
import os

from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.input import AtomHandlerInterface
from aminer.util import PersistencyUtil
from aminer.util import TimeTriggeredComponentInterface

class MatchValueAverageChangeDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
  """This detector calculates the average of a given list of values
  to monitor and reports if the average of the latest diverges
  significantly from the values observed before."""

  def __init__(self, aminer_config, anomaly_event_handlers, timestamp_path,
               analyze_path_list, min_bin_elements, min_bin_time, sync_bins_flag=True,
               debug_mode=False, persistence_id='Default'):
    """Initialize the detector. This will also trigger reading
    or creation of persistence storage location.
    @param timestamp_path if not None, use this path value for
    timestamp based bins.
    @param analyze_path_list list of match pathes to analyze in
    this detector.
    @param min_bin_elements evaluate the latest bin only after at
    least that number of elements was added to it.
    @param min_bin_time evaluate the latest bin only when the first
    element is received after minBinTime has elapsed.
    @param sync_bins_flag if true the bins of all analyzed path values
    have to be filled enough to trigger analysis.
    @param debug_mode if true, generate an analysis report even
    when average of last bin was within expected range."""
    self.anomaly_event_handlers = anomaly_event_handlers
    self.timestamp_path = timestamp_path
    self.min_bin_elements = min_bin_elements
    self.min_bin_time = min_bin_time
    self.sync_bins_flag = sync_bins_flag
    self.debug_mode = debug_mode
    self.next_persist_time = None
    self.persistence_id = persistence_id

    PersistencyUtil.addPersistableComponent(self)
    self.persistence_file_name = AMinerConfig.build_persistence_file_name(aminer_config, \
      'MatchValueAverageChangeDetector', persistence_id)
    persistence_data = PersistencyUtil.loadJson(self.persistence_file_name)
    if persistence_data is None:
      self.stat_data = []
      for path in analyze_path_list:
        self.stat_data.append((path, [],))
#   else:
#     self.knownPathSet = set(persistenceData)


  def receive_atom(self, log_atom):
    """Sends summary to all event handlers."""
    parser_match = log_atom.parserMatch
    value_dict = parser_match.getMatchDictionary()
    event_data = dict()

    timestamp_value = log_atom.getTimestamp()
    if self.timestamp_path is not None:
      match_value = value_dict.get(self.timestamp_path)
      if match_value is None:
        return
      timestamp_value = match_value.matchObject[1]
      event_data['MatchValue'] = match_value.matchObject[0]

    analysis_summary = ''
    if self.sync_bins_flag:
      ready_for_analysis_flag = True
      for (path, stat_data) in self.stat_data:
        match = value_dict.get(path, None)
        if match is None:
          ready_for_analysis_flag = (ready_for_analysis_flag and self.update(stat_data, \
            timestamp_value, None))
        else:
          ready_for_analysis_flag = (ready_for_analysis_flag and self.update(stat_data, \
            timestamp_value, match.matchObject))

      if ready_for_analysis_flag:
        anomaly_scores = []
        for (path, stat_data) in self.stat_data:
          analysis_data = self.analyze(stat_data)
          if analysis_data is not None:
            d = {}
            d['Path'] = path
            a = {}
            new = {}
            old = {}
            new['N'] = analysis_data[1]
            new['Avg'] = analysis_data[2]
            new['Var'] = analysis_data[3]
            old['N'] = analysis_data[4]
            old['Avg'] = analysis_data[5]
            old['Var'] = analysis_data[6]
            a['New'] = new
            a['Old'] = old
            d['AnalysisData'] = a
            if analysis_summary == '':
              analysis_summary += '"%s": %s' % (path, analysis_data[0])
            else:
              analysis_summary += os.linesep
              analysis_summary += '  "%s": %s' % (path, analysis_data[0])
            anomaly_scores.append(d)
        analysis_component = dict()
        analysis_component['AnomalyScores'] = anomaly_scores
        analysis_component['MinBinElements'] = self.min_bin_elements
        analysis_component['MinBinTime'] = self.min_bin_time
        analysis_component['SyncBinsFlag'] = self.sync_bins_flag
        analysis_component['DebugMode'] = self.debug_mode

        event_data['AnalysisComponent'] = analysis_component

        if self.next_persist_time is None:
          self.next_persist_time = time.time() + 600
    else:
      raise Exception('FIXME: not implemented')

    if analysis_summary:
      res = [''] * stat_data[2][0]
      res[0] = analysis_summary
      for listener in self.anomaly_event_handlers:
        listener.receiveEvent('Analysis.%s' % self.__class__.__name__, \
            'Statistical data report', res, event_data, log_atom, \
                              self)


  def get_time_trigger_class(self):
    """Get the trigger class this component should be registered
    for. This trigger is used only for persistency, so real-time
    triggering is needed."""
    return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

  def do_timer(self, triggerTime):
    """Check current ruleset should be persisted"""
    if self.next_persist_time is None:
      return 600

    delta = self.next_persist_time - triggerTime
    if delta < 0:
#     PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
      self.next_persist_time = None
      delta = 600
    return delta


  def do_persist(self):
    """Immediately write persistence data to storage."""
#   PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
    self.next_persist_time = None


  def update(self, stat_data, timestamp_value, value):
    """Update the collected statistics data.
    @param value if value not None, check only conditions if current
    bin is full enough.
    @return true if the bin is full enough to perform an analysis."""

    if value is not None:
      if not stat_data:
# Append timestamp, k-value, old-bin (n, sum, sum2, avg, variance),
# current-bin (n, sum, sum2)
        stat_data.append(timestamp_value)
        stat_data.append(value)
        stat_data.append(None)
        stat_data.append((1, 0.0, 0.0,))
      else:
        delta = value - stat_data[1]
        bin_values = stat_data[3]
        stat_data[3] = (bin_values[0] + 1, bin_values[1] + delta, bin_values[2] + delta * delta)

    if not stat_data:
      return False
    if stat_data[3][0] < self.min_bin_elements:
      return False
    if self.timestamp_path is not None:
      return timestamp_value - stat_data[0] >= self.min_bin_time
    return True


  def analyze(self, stat_data):
    """Perform the analysis and progress from the last bin to
    the next one.
    @return None when statistical data was as expected and debugging
    is disabled."""

    current_bin = stat_data[3]
    current_average = current_bin[1]/current_bin[0]
    current_variance = (current_bin[2]-(current_bin[1]*current_bin[1])/current_bin[0])/(current_bin[0]-1)
# Append timestamp, k-value, old-bin (n, sum, sum2, avg, variance),
# current-bin (n, sum, sum2)

    old_bin = stat_data[2]
    if old_bin is None:
      stat_data[2] = (current_bin[0], current_bin[1], current_bin[2], current_average, current_variance,)
      stat_data[3] = (0, 0.0, 0.0)
      if self.debug_mode:
        return 'Initial: n = %d, avg = %s, var = %s' % (current_bin[0], \
                                                        current_average + stat_data[1], current_variance)
    else:
      total_n = old_bin[0]+current_bin[0]
      total_sum = old_bin[1]+current_bin[1]
      total_sum2 = old_bin[2]+current_bin[2]

      stat_data[2] = (total_n, total_sum, total_sum2, total_sum / total_n, \
                      (total_sum2-(total_sum*total_sum)/total_n) / (total_n-1))
      stat_data[3] = (0, 0.0, 0.0)

      if (current_variance > 2*old_bin[4]) or (abs(current_average-old_bin[3]) > old_bin[4]) \
         or self.debug_mode:
        res = ['Change: new: n = %d, avg = %s, var = %s; old: n = %d, avg = %s, var = %s' % \
               (current_bin[0], current_average + stat_data[1], current_variance, old_bin[0], \
                old_bin[3] + stat_data[1], old_bin[4]), current_bin[0], current_average + stat_data[1], current_variance, old_bin[0], \
               old_bin[3] + stat_data[1], old_bin[4]]
        return res
    return None
