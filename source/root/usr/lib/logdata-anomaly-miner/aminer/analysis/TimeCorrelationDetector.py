"""This module defines a detector for time correlation between atoms."""

from datetime import datetime
import random
import time

from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.analysis import Rules
from aminer.input import AtomHandlerInterface
from aminer.util import get_log_int
from aminer.util import PersistencyUtil
from aminer.util import TimeTriggeredComponentInterface


class TimeCorrelationDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
  """This class tries to find time correlation patterns between
  different log atoms. When a possible correlation rule is detected,
  it creates an event including the rules. This is useful to implement
  checks as depicted in http://dx.doi.org/10.1016/j.cose.2014.09.006."""

  def __init__(self, aminer_config, parallel_check_count, correlation_test_count, max_fail_count,
          anomaly_event_handlers, persistence_id='Default', record_count_before_event=0x10000, output_log_line=True):
    """Initialize the detector. This will also trigger reading
    or creation of persistence storage location.
    @param parallel_check_count number of rule detection checks
    to run in parallel.
    @param correlation_test_count number of unit to perform on a rule under
    test.
    @param max_fail_count maximal number of test failures so that
    rule is still eligible for reporting."""
    self.last_timestamp = 0.0
    self.parallel_check_count = parallel_check_count
    self.correlation_test_count = correlation_test_count
    self.max_fail_count = max_fail_count
    self.anomaly_event_handlers = anomaly_event_handlers
    self.max_rule_attributes = 5
    self.last_unhandled_match = None
    self.next_persist_time = None
    self.total_records = 0
    self.record_count_before_event = record_count_before_event
    self.persistence_id = persistence_id
    self.output_log_line = output_log_line

    PersistencyUtil.add_persistable_component(self)
    self.persistence_file_name = AMinerConfig.build_persistence_file_name(
        aminer_config, 'TimeCorrelationDetector', persistence_id)
    persistence_data = PersistencyUtil.load_json(self.persistence_file_name)
    if persistence_data is None:
      self.feature_list = []
      self.event_count_table = [0] * parallel_check_count * parallel_check_count * 2
      self.event_delta_table = [0] * parallel_check_count * parallel_check_count * 2
#   else:
#     self.knownPathSet = set(persistenceData)

  def receive_atom(self, log_atom):
    event_data = {}
    timestamp = log_atom.get_timestamp()
    if timestamp is None:
      timestamp = time.time()
    if timestamp < self.last_timestamp:
      for listener in self.anomaly_event_handlers:
        listener.receive_event('Analysis.%s' % self.__class__.__name__,
            'Logdata not sorted: last %s, current %s' % (self.last_timestamp, timestamp),
                               [log_atom.parser_match.match_element.annotate_match('')], event_data, log_atom, self)
      return
    self.last_timestamp = timestamp

    self.total_records += 1
    features_found_list = []

    for feature in self.feature_list:
      if feature.rule.match(log_atom):
        feature.trigger_count += 1
        self.update_tables_for_feature(feature, timestamp)
        features_found_list.append(feature)

    if len(self.feature_list) < self.parallel_check_count:
      if (random.randint(0, 1) != 0) and (self.last_unhandled_match is not None):
        log_atom = self.last_unhandled_match
      new_rule = self.create_random_rule(log_atom)
      if new_rule is not None:
        new_feature = CorrelationFeature(new_rule, len(self.feature_list), timestamp)
        self.feature_list.append(new_feature)
        new_feature.trigger_count = 1
        self.update_tables_for_feature(new_feature, timestamp)
        features_found_list.append(new_feature)

    for feature in features_found_list:
      feature.last_trigger_time = timestamp

    if not features_found_list:
      self.last_unhandled_match = log_atom
    elif self.next_persist_time is None:
      self.next_persist_time = time.time() + 600

    if (self.total_records % self.record_count_before_event) == 0:
      result = self.total_records * ['']
      result[0] = self.analysis_status_to_string()

      analysis_component = {'AffectedLogAtomPathes': list(log_atom.parser_match.get_match_dictionary()),
        'AffectedLogAtomValues': [log_atom.raw_data.decode()]}
      if self.output_log_line:
        match_paths_values = {}
        for match_path, match_element in log_atom.parser_match.get_match_dictionary().items():
          match_value = match_element.match_object
          if isinstance(match_value, tuple):
            l = []
            for val in match_value:
              if isinstance(val, datetime):
                l.append(datetime.timestamp(val))
              else:
                l.append(val)
            match_value = l
          if isinstance(match_value, bytes):
            match_value = match_value.decode()
          match_paths_values[match_path] = match_value
        analysis_component['ParsedLogAtom'] = match_paths_values
        feature_list = []
        for feature in self.feature_list:
          l = {}
          r = self.rule_to_dict(feature.rule)
          l['Rule'] = r
          l['Index'] = feature.index
          l['CreationTime'] = feature.creation_time
          l['LastTriggerTime'] = feature.last_trigger_time
          l['TriggerCount'] = feature.trigger_count
          feature_list.append(l)
        analysis_component['FeatureList'] = feature_list
      analysis_component['AnalysisStatus'] = result[0]
      analysis_component['TotalRecords'] = self.total_records

      event_data['AnalysisComponent'] = analysis_component
      for listener in self.anomaly_event_handlers:
        listener.receive_event('Analysis.%s' % self.__class__.__name__,
            'Correlation report', result,
                               event_data, log_atom, self)
      self.reset_statistics()

  def rule_to_dict(self, rule):
    r = {}
    r['Type'] = str(rule.__class__.__name__)
    for var in vars(rule):
      attr = getattr(rule, var, None)
      if attr is None:
        r[var] = None
      elif isinstance(attr, list):
        l = []
        for v in attr:
          d = self.rule_to_dict(v)
          d['Type'] = str(v.__class__.__name__)
          l.append(d)
        r['subRules'] = l
      else:
        r[var] = attr
    return r

  def get_time_trigger_class(self):
    """Get the trigger class this component should be registered
    for. This trigger is used only for persistency, so real-time
    triggering is needed."""
    return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

  def do_timer(self, trigger_time):
    """Check current ruleset should be persisted"""
    if self.next_persist_time is None:
      return 600

    delta = self.next_persist_time - trigger_time
    if delta < 0:
#     PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
      self.next_persist_time = None
      delta = 600
    return delta


  def do_persist(self):
    """Immediately write persistence data to storage."""
#   PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
    self.next_persist_time = None


  def create_random_rule(self, log_atom):
    """Create a random existing path rule or value match rule."""
    parser_match = log_atom.parser_match
    sub_rules = []
    all_keys = list(parser_match.get_match_dictionary().keys())
    attribute_count = get_log_int(self.max_rule_attributes) + 1
    while attribute_count > 0:
      key_pos = random.randint(0, len(all_keys)-1)
      key_name = all_keys[key_pos]
      all_keys = all_keys[:key_pos]+all_keys[key_pos+1:]
      key_value = parser_match.get_match_dictionary().get(key_name).match_object
# Not much sense handling parsed date values in this implementation,
# so just ignore this attribute.
      if (isinstance(key_value, tuple)) and (isinstance(key_value[0], datetime)):
        if not all_keys:
          break
        continue

      attribute_count -= 1
      rule_type = random.randint(0, 1)
      if rule_type == 0:
        sub_rules.append(Rules.PathExistsMatchRule(key_name))
      elif rule_type == 1:
        sub_rules.append(Rules.ValueMatchRule(key_name, key_value))
      else:
        raise Exception('Invalid rule type')
      if not all_keys:
        break

    if len(sub_rules) > 1:
      return Rules.AndMatchRule(sub_rules)
    if len(sub_rules) > 0:
      return sub_rules[0]
    return None
    


  def update_tables_for_feature(self, target_feature, timestamp):
    """Assume that this event was the effect of a previous cause-related
    event. Loop over all cause-related features (rows) to search
    for matches."""
    feature_table_pos = (target_feature.index << 1)
    for feature in self.feature_list:
      delta = timestamp-feature.last_trigger_time
      if delta <= 10.0:
        self.event_count_table[feature_table_pos] += 1
        self.event_delta_table[feature_table_pos] += int(delta * 1000)
      feature_table_pos += (self.parallel_check_count << 1)

    feature_table_pos = ((target_feature.index * self.parallel_check_count) << 1) + 1
    for feature in self.feature_list:
      delta = timestamp-feature.last_trigger_time
      if delta <= 10.0:
        self.event_count_table[feature_table_pos] += 1
        self.event_delta_table[feature_table_pos] -= int(delta * 1000)
      feature_table_pos += 2


  def analysis_status_to_string(self):
    """Get a string representation of all features."""
    result = ''
    for feature in self.feature_list:
      trigger_count = feature.trigger_count
      result += '%s (%d) e = %d:' % (feature.rule, feature.index, trigger_count)
      stat_pos = (self.parallel_check_count * feature.index) << 1
      for feature_pos in range(0, len(self.feature_list)):
        event_count = self.event_count_table[stat_pos]
        ratio = '-'
        if trigger_count != 0:
          ratio = '%.2e' % (float(event_count)/trigger_count)
        delta = '-'
        if event_count != 0:
          delta = '%.2e' % (float(self.event_delta_table[stat_pos]) * 0.001 / event_count)
        result += '\n  %d: {c = %#6d r = %s dt = %s' % (feature_pos, event_count, ratio, delta)
        stat_pos += 1
        event_count = self.event_count_table[stat_pos]
        ratio = '-'
        if trigger_count != 0:
          ratio = '%.2e' % (float(event_count)/trigger_count)
        delta = '-'
        if event_count != 0:
          delta = '%.2e' % (float(self.event_delta_table[stat_pos]) * 0.001 / event_count)
        result += ' c = %#6d r = %s dt = %s}' % (event_count, ratio, delta)
        stat_pos += 1
      result += '\n'
    return result

  def reset_statistics(self):
    """Reset all features."""
    for feature in self.feature_list:
      feature.creation_time = 0
      feature.last_trigger_time = 0
      feature.trigger_count = 0
    self.event_count_table = [0] * self.parallel_check_count * self.parallel_check_count * 2
    self.event_delta_table = [0] * self.parallel_check_count * self.parallel_check_count * 2


class CorrelationFeature:
  """This class defines a correlation feature."""
  def __init__(self, rule, index, creation_time):
    self.rule = rule
    self.index = index
    self.creation_time = creation_time
    self.last_trigger_time = 0.0
    self.trigger_count = 0
