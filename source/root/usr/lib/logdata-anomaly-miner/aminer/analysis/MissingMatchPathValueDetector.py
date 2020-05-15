"""This module provides the MissingMatchPathValueDetector to generate
events when expected values were not seen for an extended period
of time."""

import time

from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events import EventSourceInterface
from aminer.input import AtomHandlerInterface
from aminer.util import PersistencyUtil
from aminer.util import TimeTriggeredComponentInterface
from aminer.analysis import CONFIG_KEY_LOG_LINE_PREFIX
import os


class MissingMatchPathValueDetector(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface):
  """This class creates events when an expected value is not seen
  within a given timespan, e.g. because the service was deactivated
  or logging disabled unexpectedly. This is complementary to the
  function provided by NewMatchPathValueDetector.

  For each unique value extracted by targetPath, a tracking record
  is added to expectedValuesDict. It stores three numbers: the
  timestamp the extracted value was last seen, the maximum allowed
  gap between observations and the next alerting time when currently
  in error state. When in normal (alerting) state, the value is
  zero."""

  def __init__(self, aminer_config, target_path, anomaly_event_handlers, persistence_id='Default', auto_include_flag=False,
               default_interval=3600, realert_interval=86400, output_log_line=True):
    """Initialize the detector. This will also trigger reading
    or creation of persistence storage location.
    @param target_path to extract a source identification value
    from each logatom."""
    self.target_path = target_path
    self.anomaly_event_handlers = anomaly_event_handlers
    self.auto_include_flag = auto_include_flag
    self.default_interval = default_interval
    self.realert_interval = realert_interval
# This timestamps is compared with timestamp values from log atoms
# for activation of alerting logic. The first timestamp from logs
# above this value will trigger alerting.
    self.next_check_timestamp = 0
    self.last_seen_timestamp = 0
    self.next_persist_time = None
    self.output_log_line = output_log_line
    self.aminer_config = aminer_config
    self.persistence_id = persistence_id

    PersistencyUtil.add_persistable_component(self)
    self.persistence_file_name = AMinerConfig.build_persistence_file_name(
        aminer_config, self.__class__.__name__, persistence_id)
    persistence_data = PersistencyUtil.load_json(self.persistence_file_name)
    if persistence_data is None:
      self.expected_values_dict = {}
    else:
      self.expected_values_dict = persistence_data
    self.analysis_string = 'Analysis.%s'

  def receive_atom(self, log_atom):
    """Receive a log atom from a source.
    @param atomData binary raw atom data
    @return True if this handler was really able to handle and
    process the atom. Depending on this information, the caller
    may decide if it makes sense passing the atom also to other
    handlers or to retry later. This behaviour has to be documented
    at each source implementation sending LogAtoms."""
    value = self.get_channel_key(log_atom)
    if value is None:
      return False
    timestamp = log_atom.get_timestamp()
    if timestamp is None:
      timestamp = time.time()
    detector_info = self.expected_values_dict.get(value, None)
    if detector_info is not None:
# Just update the last seen value and switch from non-reporting
# error state to normal state.
      detector_info[0] = timestamp
      if detector_info[2] != 0:
        if timestamp >= detector_info[2]:
          detector_info[2] = 0
# Delta of this detector might be lower than the default maximum
# recheck time.
        self.next_check_timestamp = min(
            self.next_check_timestamp, timestamp + detector_info[1])

    elif self.auto_include_flag:
      self.expected_values_dict[value] = [timestamp, self.default_interval, 0]
      self.next_check_timestamp = min(self.next_check_timestamp, timestamp + self.default_interval)

# Always enforce persistency syncs from time to time, the timestamps
# in the records change even when no new hosts are added.
    if self.next_persist_time is None:
      self.next_persist_time = time.time() + 600
    self.check_timeouts(timestamp, log_atom)

    return True

  def get_channel_key(self, log_atom):
    """Get the key identifying the channel this logAtom is coming
    from."""
    match_element = log_atom.parser_match.get_match_dictionary().get(
        self.target_path, None)
    if match_element is None:
      return None
    return match_element.match_object

  def check_timeouts(self, timestamp, log_atom):
    """Check if there was any timeout on a channel, thus triggering
    event dispatching."""
    self.last_seen_timestamp = max(self.last_seen_timestamp, timestamp)
    if self.last_seen_timestamp > self.next_check_timestamp:
      missing_value_list = []
# Start with a large recheck interval. It will be lowered if any
# of the expectation intervals is below that.
      if not self.next_check_timestamp:
        self.next_check_timestamp = self.last_seen_timestamp + 86400
      for value, detector_info in self.expected_values_dict.items():
        value_overdue_time = self.last_seen_timestamp - detector_info[0] - detector_info[1]
        if detector_info[2] != 0:
          next_check_delta = detector_info[2]-self.last_seen_timestamp
          if next_check_delta > 0:
# Already alerted but not ready for realerting yet.
            self.next_check_timestamp = min(
                self.next_check_timestamp, detector_info[2])
            continue
        else:
# No alerting yet, see if alerting is required.
          if value_overdue_time < 0:
            old = self.next_check_timestamp
            self.next_check_timestamp = min(self.next_check_timestamp, self.last_seen_timestamp - value_overdue_time)
            if old > self.next_check_timestamp or self.next_check_timestamp < detector_info[2]:
              continue
        missing_value_list.append([value, value_overdue_time, detector_info[1]])
# Set the next alerting time.
        detector_info[2] = self.last_seen_timestamp + self.realert_interval
        self.expected_values_dict[value] = detector_info
      if missing_value_list:
        message_part = []
        affected_log_atom_values = []
        for value, overdue_time, interval in missing_value_list:
          e = {}
          if self.__class__.__name__ == 'MissingMatchPathValueDetector':
            e['TargetPath'] = self.target_path
            message_part.append('  %s: %s overdue %ss (interval %s)' % (self.target_path, repr(value), overdue_time, interval))
          else:
            target_paths = ''
            for target_path in self.target_path_list:
              target_paths += target_path + ', '
            e['TargetPathList'] = self.target_path_list
            message_part.append('  %s: %s overdue %ss (interval %s)' % (target_paths[:-2], repr(value), overdue_time, interval))
          e['Value'] = repr(value)
          e['OverdueTime'] = overdue_time
          e['Interval'] = interval
          affected_log_atom_values.append(e)
        analysis_component = {'AffectedLogAtomPathes': list(log_atom.parser_match.get_match_dictionary()),
          'AffectedLogAtomValues': affected_log_atom_values}
        if self.output_log_line:
          match_paths_values = {}
          for match_path, match_element in log_atom.parser_match.get_match_dictionary().items():
            match_value = match_element.match_object
            if isinstance(match_value, bytes):
              match_value = match_value.decode()
            match_paths_values[match_path] = match_value
          analysis_component['ParsedLogAtom'] = match_paths_values
        event_data = {'AnalysisComponent': analysis_component}
        original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX)
        if original_log_line_prefix is None:
          original_log_line_prefix = ''
        if self.output_log_line:
          message_part.append(log_atom.parser_match.match_element.annotate_match('') + os.linesep + original_log_line_prefix + repr(log_atom.raw_data))
        else:
          message_part.append(os.linesep + original_log_line_prefix + repr(log_atom.raw_data))
        for listener in self.anomaly_event_handlers:
          self.send_event_to_handlers(listener, event_data, log_atom, [''.join(message_part)])
    return True

  def send_event_to_handlers(self, anomaly_event_handler, event_data, log_atom, message_part):
    anomaly_event_handler.receive_event(self.analysis_string % self.__class__.__name__,
        'Interval too large between values', message_part, event_data, log_atom, self)

  def set_check_value(self, value, interval):
    """Add or overwrite a value to be monitored by the detector."""
    self.expected_values_dict[value] = [self.last_seen_timestamp, interval, 0]
    self.next_check_timestamp = 0
# Explicitely trigger a persistency sync to avoid staying in unsynced
# state too long when no new received atoms trigger it. But do
# not sync immediately, that would make bulk calls to this method
# quite inefficient.
    if self.next_persist_time is None:
      self.next_persist_time = time.time() + 600

  def remove_check_value(self, value):
    """Remove checks for given value."""
    del self.expected_values_dict[value]

  def get_time_trigger_class(self):
    """Get the trigger class this component can be registered
    for. This detector only needs persisteny triggers in real
    time."""
    return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

  def do_timer(self, trigger_time):
    """Check current ruleset should be persisted"""
    if self.next_persist_time is None:
      return 600
    delta = self.next_persist_time - trigger_time
    if delta <= 0:
      PersistencyUtil.store_json(self.persistence_file_name, self.expected_values_dict)
      self.next_persist_time = None
      delta = 600
    return delta

  def do_persist(self):
    """Immediately write persistence data to storage."""
    PersistencyUtil.store_json(self.persistence_file_name, self.expected_values_dict)
    self.next_persist_time = None

  def whitelist_event(self, event_type, sorted_log_lines, event_data, whitelisting_data):
    """Whitelist an event generated by this source using the information
    emitted when generating the event.
    @return a message with information about whitelisting
    @throws Exception when whitelisting of this special event
    using given whitelistingData was not possible."""
    if event_type != self.analysis_string % self.__class__.__name__:
      raise Exception('Event not from this source')
    if not isinstance(whitelisting_data, int):
      raise Exception('Whitelisting data has to integer with new interval, -1 to reset to defaults, other negative '
                      'value to remove the entry')
    new_interval = whitelisting_data
    if new_interval == -1:
      new_interval = self.default_interval
    for key_name, in event_data:
      if new_interval < 0:
        self.remove_check_value(key_name)
      else:
        self.set_check_value(key_name, new_interval)
    return 'Updated %d entries' % len(event_data)


class MissingMatchPathListValueDetector(MissingMatchPathValueDetector):
  """This detector works similar to the MissingMatchPathValueDetector.
  It only can lookup values from a list of pathes until one path
  really exists. It then uses this value as key to detect logAtoms
  belonging to the same data stream. This is useful when e.g.
  due to different log formats, the hostname, servicename or any
  other relevant channel identifier has alternative pathes."""

  def __init__(self, aminer_config, target_path_list, anomaly_event_handlers, persistence_id='Default', auto_include_flag=False,
               default_interval=3600, realert_interval=86400):
    """Initialize the detector. This will also trigger reading
    or creation of persistence storage location.
    @param targetPath to extract a source identification value
    from each logatom."""
    super(MissingMatchPathListValueDetector, self).__init__(
        aminer_config, None, anomaly_event_handlers, persistence_id,
        auto_include_flag, default_interval, realert_interval)
    self.target_path_list = target_path_list

  def get_channel_key(self, log_atom):
    """Get the key identifying the channel this logAtom is coming
    from."""
    for target_path in self.target_path_list:
      match_element = log_atom.parser_match.get_match_dictionary().get(
          target_path, None)
      if match_element is None:
        continue
      return match_element.match_object
    return None

  def send_event_to_handlers(self, anomaly_event_handler, event_data, log_atom, message_part):
    anomaly_event_handler.receive_event(self.analysis_string % self.__class__.__name__,
        'Interval too large between values', message_part, event_data, log_atom, self)
