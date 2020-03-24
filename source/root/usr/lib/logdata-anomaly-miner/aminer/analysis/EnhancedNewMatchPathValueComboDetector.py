"""This file defines the EnhancedNewMatchPathValueComboDetector
detector to extract values from LogAtoms and check, if the value
combination was already seen before."""

import time
import os

from aminer.analysis.NewMatchPathValueComboDetector import NewMatchPathValueComboDetector
from aminer.util import PersistencyUtil
from datetime import datetime
from aminer.analysis import CONFIG_KEY_LOG_LINE_PREFIX

class EnhancedNewMatchPathValueComboDetector(NewMatchPathValueComboDetector):
  """This class creates events when a new value combination for
  a given list of match data pathes were found. It is similar
  to the NewMatchPathValueComboDetector basic detector but also
  provides support for storing meta information about each detected
  value combination, e.g.
  * the first time a tuple was detected using the LogAtom default
    timestamp.
  * the last time a tuple was seen
  * the number of times the tuple was seen
  * user data for annotation.
  Due to the additional features, this detector is slower than
  the basic detector."""

  def __init__(
      self, aminer_config, target_path_list, anomaly_event_handlers,
      persistence_id='Default', allow_missing_values_flag=False,
      auto_include_flag=False, tuple_transformation_function=None, output_log_line=True):
    """Initialize the detector. This will also trigger reading
    or creation of persistence storage location.
    @param target_path_list the list of values to extract from each
    match to create the value combination to be checked.
    @param allow_missing_values_flag when set to True, the detector
    will also use matches, where one of the pathes from targetPathList
    does not refer to an existing parsed data object.
    @param auto_include_flag when set to True, this detector will
    report a new value only the first time before including it
    in the known values set automatically.
    @param tuple_transformation_function when not None, this function
    will be invoked on each extracted value combination list to
    transform it. It may modify the list directly or create a
    new one to return it."""
    super(EnhancedNewMatchPathValueComboDetector, self).__init__(
        aminer_config, target_path_list, anomaly_event_handlers, persistence_id,
        allow_missing_values_flag, auto_include_flag)
    self.tuple_transformation_function = tuple_transformation_function
    self.output_log_line = output_log_line
    self.aminer_config = aminer_config
    self.date_string = "%Y-%m-%d %H:%M:%S"


  def load_persistency_data(self):
    """Load the persistency data from storage."""
    self.known_values_dict = {}
    persistence_data = PersistencyUtil.load_json(self.persistence_file_name)
    if persistence_data != None:
# Dictionary and tuples were stored as list of lists. Transform
# the first lists to tuples to allow hash operation needed by set.
      for value_tuple, extra_data in persistence_data:
        self.known_values_dict[tuple(value_tuple)] = extra_data


  def receive_atom(self, log_atom):
    """Receive on parsed atom and the information about the parser
    match.
    @return True if a value combination was extracted and checked
    against the list of known combinations, no matter if the checked
    values were new or not."""
    match_dict = log_atom.parser_match.get_match_dictionary()
    match_value_list = []
    event_data = dict()
    for target_path in self.target_path_list:
      match_element = match_dict.get(target_path, None)
      if match_element is None:
        if not self.allow_missing_values_flag:
          return False
        match_value_list.append(None)
      else:
        match_value_list.append(match_element.match_object)

    if self.tuple_transformation_function != None:
      match_value_list = self.tuple_transformation_function(match_value_list)
    match_value_tuple = tuple(match_value_list)

    current_timestamp = log_atom.get_timestamp()
    if current_timestamp is None:
      current_timestamp = datetime.fromtimestamp(time.time()).strftime(self.date_string)
    if not isinstance(current_timestamp, datetime) and not isinstance(current_timestamp, str):
      current_timestamp = datetime.fromtimestamp(current_timestamp).strftime(self.date_string)
    if isinstance(current_timestamp, datetime):
      current_timestamp = current_timestamp.strftime(self.date_string)
    if self.known_values_dict.get(match_value_tuple, None) is None:
      self.known_values_dict[match_value_tuple] = [current_timestamp, current_timestamp, 1]
    else:
      extra_data = self.known_values_dict.get(match_value_tuple, None)
      extra_data[1] = current_timestamp
      extra_data[2] += 1

    affected_log_atom_values = []
    l = {}
    match_value_list = []
    for match_value in list(match_value_tuple):
      if isinstance(match_value, bytes):
        match_value = match_value.decode()
      match_value_list.append(match_value)
    l['MatchValueList'] = match_value_list
    values = self.known_values_dict.get(match_value_tuple, None)
    l['TimeFirstOccurrence'] = values[0]
    l['TimeLastOccurence'] = values[1]
    l['NumberOfOccurences'] = values[2]
    affected_log_atom_values.append(l)

    analysis_component = dict()
    analysis_component['AffectedLogAtomValues'] = affected_log_atom_values
    event_data['AnalysisComponent'] = analysis_component
    if (self.auto_include_flag and self.known_values_dict.get(match_value_tuple, None)[2] is 1) or not self.auto_include_flag:
      for listener in self.anomaly_event_handlers:
        original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX)
        if original_log_line_prefix is None:
          original_log_line_prefix = ''
        if self.output_log_line:
          sorted_log_lines = [str(self.known_values_dict) + os.linesep +
                            original_log_line_prefix + repr(log_atom.raw_data)]
        else:
          sorted_log_lines = [str(self.known_values_dict)]
        listener.receive_event(
          'Analysis.%s' % self.__class__.__name__, 'New value combination(s) detected',
          sorted_log_lines, event_data, log_atom, self)
    if self.auto_include_flag:
      if self.next_persist_time is None:
        self.next_persist_time = time.time() + 600
    return True

  def do_persist(self):
    """Immediately write persistence data to storage."""
    persistency_data = []
    for dict_record in self.known_values_dict.items():
      persistency_data.append(dict_record)
    PersistencyUtil.store_json(self.persistence_file_name, persistency_data)
    self.next_persist_time = None


  def whitelist_event(
      self, event_type, sorted_log_lines, event_data, whitelisting_data):
    """Whitelist an event generated by this source using the information
    emitted when generating the event.
    @return a message with information about whitelisting
    @throws Exception when whitelisting of this special event
    using given whitelistingData was not possible."""
    if event_type != 'Analysis.%s' % self.__class__.__name__:
      raise Exception('Event not from this source')
    if whitelisting_data != None:
      raise Exception('Whitelisting data not understood by this detector')
    current_timestamp = datetime.fromtimestamp(event_data[0].get_timestamp()).strftime(self.date_string)
    self.known_values_dict[event_data[1]] = [
        current_timestamp, current_timestamp, 1]
    return 'Whitelisted path(es) %s with %s in %s' % (
        ', '.join(self.target_path_list), event_data[1], sorted_log_lines[0])

