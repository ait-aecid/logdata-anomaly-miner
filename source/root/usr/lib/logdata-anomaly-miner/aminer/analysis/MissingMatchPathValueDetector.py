"""
This module provides the MissingMatchPathValueDetector to generate events when expected values were not seen for an extended period of time.
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

import time
import logging

from aminer import AminerConfig
from aminer.AminerConfig import STAT_LEVEL, STAT_LOG_NAME
from aminer.AnalysisChild import AnalysisContext
from aminer.events import EventSourceInterface
from aminer.input import AtomHandlerInterface
from aminer.util import PersistenceUtil
from aminer.util import TimeTriggeredComponentInterface


class MissingMatchPathValueDetector(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface):
    """
    This class creates events when an expected value is not seen within a given timespan.
    For example because the service was deactivated or logging disabled unexpectedly. This is complementary to the function provided by
    NewMatchPathValueDetector. For each unique value extracted by target_path, a tracking record is added to expected_values_dict.
    It stores three numbers: the timestamp the extracted value was last seen, the maximum allowed gap between observations and the next
    alerting time when currently in error state. When in normal (alerting) state, the value is zero.
    """

    def __init__(self, aminer_config, target_path, anomaly_event_handlers, persistence_id='Default', auto_include_flag=False,
                 default_interval=3600, realert_interval=86400, output_log_line=True):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param target_path to extract a source identification value from each logatom.
        """
        self.target_path = target_path
        self.anomaly_event_handlers = anomaly_event_handlers
        self.auto_include_flag = auto_include_flag
        self.default_interval = default_interval
        self.realert_interval = realert_interval
        # This timestamps is compared with timestamp values from log atoms for activation of alerting logic. The first timestamp from logs
        # above this value will trigger alerting.
        self.next_check_timestamp = 0
        self.last_seen_timestamp = 0
        self.next_persist_time = None
        self.output_log_line = output_log_line
        self.aminer_config = aminer_config
        self.persistence_id = persistence_id

        self.log_success = 0
        self.log_total = 0
        self.log_learned_values = 0
        self.log_new_learned_values = []

        PersistenceUtil.add_persistable_component(self)
        self.persistence_file_name = AminerConfig.build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        self.expected_values_dict = {}
        if persistence_data is not None:
            for key in persistence_data:
                value = persistence_data[key]
                if self.target_path is not None:  # skipcq: PTC-W0048
                    if value[3] != self.target_path:
                        continue
                elif self.target_path_list is not None and value[3] not in self.target_path_list:
                    continue
                if value[1] != default_interval:
                    value[1] = default_interval
                    value[2] = value[0] + default_interval
                self.expected_values_dict[key] = value
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug('%s loaded persistence data.', self.__class__.__name__)
        self.analysis_string = 'Analysis.%s'

    def receive_atom(self, log_atom):
        """
        Receive a log atom from a source.
        @param log_atom binary raw atom data
        @return True if this handler was really able to handle and process the atom. Depending on this information, the caller
        may decide if it makes sense passing the atom also to other handlers or to retry later. This behaviour has to be documented
        at each source implementation sending LogAtoms.
        """
        self.log_total += 1
        value = self.get_channel_key(log_atom)
        if value is None:
            return False
        target_path, value = value
        timestamp = log_atom.get_timestamp()
        if timestamp is None:
            timestamp = time.time()
        detector_info = self.expected_values_dict.get(value)
        if detector_info is not None:
            # Just update the last seen value and switch from non-reporting error state to normal state.
            detector_info[0] = timestamp
            if detector_info[2] != 0:
                if timestamp >= detector_info[2]:
                    detector_info[2] = 0
                # Delta of this detector might be lower than the default maximum recheck time.
                self.next_check_timestamp = min(self.next_check_timestamp, timestamp + detector_info[1])

        elif self.auto_include_flag:
            self.expected_values_dict[value] = [timestamp, self.default_interval, 0, target_path]
            self.next_check_timestamp = min(self.next_check_timestamp, timestamp + self.default_interval)
            self.log_learned_values += 1
            self.log_new_learned_values.append(value)

        # Always enforce persistence syncs from time to time, the timestamps in the records change even when no new hosts are added.
        if self.next_persist_time is None:
            self.next_persist_time = time.time() + self.aminer_config.config_properties.get(
                AminerConfig.KEY_PERSISTENCE_PERIOD, AminerConfig.DEFAULT_PERSISTENCE_PERIOD)
        self.check_timeouts(timestamp, log_atom)
        self.log_success += 1
        return True

    def get_channel_key(self, log_atom):
        """Get the key identifying the channel this log_atom is coming from."""
        match_element = log_atom.parser_match.get_match_dictionary().get(self.target_path)
        if match_element is None:
            return None
        if isinstance(match_element.match_object, bytes):
            affected_log_atom_values = match_element.match_object.decode()
        else:
            affected_log_atom_values = match_element.match_object
        return self.target_path, str(affected_log_atom_values)

    def check_timeouts(self, timestamp, log_atom):
        """Check if there was any timeout on a channel, thus triggering event dispatching."""
        old_last_seen_timestamp = self.last_seen_timestamp
        self.last_seen_timestamp = max(self.last_seen_timestamp, timestamp)
        if self.last_seen_timestamp > self.next_check_timestamp:
            missing_value_list = []
            # Start with a large recheck interval. It will be lowered if any of the expectation intervals is below that.
            if self.next_check_timestamp == 0:
                self.next_check_timestamp = self.last_seen_timestamp + self.realert_interval
            for value, detector_info in self.expected_values_dict.items():
                value_overdue_time = int(self.last_seen_timestamp - detector_info[0] - detector_info[1])
                if detector_info[2] != 0:
                    next_check_delta = detector_info[2] - self.last_seen_timestamp
                    if next_check_delta > 0:
                        # Already alerted but not ready for realerting yet.
                        self.next_check_timestamp = min(self.next_check_timestamp, detector_info[2])
                        continue
                else:
                    # No alerting yet, see if alerting is required.
                    if value_overdue_time < 0:
                        old = self.next_check_timestamp
                        self.next_check_timestamp = min(self.next_check_timestamp, self.last_seen_timestamp - value_overdue_time)
                        if old > self.next_check_timestamp or self.next_check_timestamp < detector_info[2]:
                            continue
                # avoid early re-alerting
                if value_overdue_time > 0:
                    missing_value_list.append([value, value_overdue_time, detector_info[1]])
                    # Set the next alerting time.
                    detector_info[2] = self.last_seen_timestamp + self.realert_interval
                    self.expected_values_dict[value] = detector_info
                # Workaround:
                # also check for long gaps between same tokens where the last_seen_timestamp gets updated
                # on the arrival of tokens following a longer gap
                elif self.last_seen_timestamp > old_last_seen_timestamp + detector_info[1]:
                    value_overdue_time = self.last_seen_timestamp - old_last_seen_timestamp - detector_info[1]
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
                    e['Value'] = str(value)
                    e['OverdueTime'] = str(overdue_time)
                    e['Interval'] = str(interval)
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
                for listener in self.anomaly_event_handlers:
                    self.send_event_to_handlers(listener, event_data, log_atom, [''.join(message_part)])
        return True

    def send_event_to_handlers(self, anomaly_event_handler, event_data, log_atom, message_part):
        """Send an event to the event handlers."""
        anomaly_event_handler.receive_event(self.analysis_string % self.__class__.__name__, 'Interval too large between values',
                                            message_part, event_data, log_atom, self)

    def set_check_value(self, value, interval, target_path):
        """Add or overwrite a value to be monitored by the detector."""
        self.expected_values_dict[value] = [self.last_seen_timestamp, interval, 0, target_path]
        self.next_check_timestamp = 0
        # Explicitely trigger a persistence sync to avoid staying in unsynced state too long when no new received atoms trigger it. But do
        # not sync immediately, that would make bulk calls to this method quite inefficient.
        if self.next_persist_time is None:
            self.next_persist_time = time.time() + self.aminer_config.config_properties.get(
                AminerConfig.KEY_PERSISTENCE_PERIOD, AminerConfig.DEFAULT_PERSISTENCE_PERIOD)

    def remove_check_value(self, value):
        """Remove checks for given value."""
        del self.expected_values_dict[value]
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug('%s removed check value %s.', self.__class__.__name__, str(value))

    def get_time_trigger_class(self):
        """Get the trigger class this component can be registered for. This detector only needs persisteny triggers in real time."""
        return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def do_timer(self, trigger_time):
        """Check current ruleset should be persisted."""
        if self.next_persist_time is None:
            return self.aminer_config.config_properties.get(AminerConfig.KEY_PERSISTENCE_PERIOD, AminerConfig.DEFAULT_PERSISTENCE_PERIOD)
        delta = self.next_persist_time - trigger_time
        if delta < 0:
            PersistenceUtil.store_json(self.persistence_file_name, self.expected_values_dict)
            self.next_persist_time = None
            delta = self.aminer_config.config_properties.get(AminerConfig.KEY_PERSISTENCE_PERIOD, AminerConfig.DEFAULT_PERSISTENCE_PERIOD)
        return delta

    def do_persist(self):
        """Immediately write persistence data to storage."""
        PersistenceUtil.store_json(self.persistence_file_name, self.expected_values_dict)
        self.next_persist_time = None
        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug('%s persisted data.', self.__class__.__name__)

    def allowlist_event(self, event_type, event_data, allowlisting_data):
        """
        Allowlist an event generated by this source using the information emitted when generating the event.
        @return a message with information about allowlisting using given allowlisting_data was not possible.
        """
        if event_type != self.analysis_string % self.__class__.__name__:
            msg = 'Event not from this source'
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if not isinstance(allowlisting_data, int):
            msg = 'Allowlisting data has to integer with new interval, -1 to reset to defaults, other negative value to remove the entry'
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        new_interval = allowlisting_data
        if new_interval == -1:
            new_interval = self.default_interval
        if new_interval < 0:
            self.remove_check_value(event_data[0])
        else:
            self.set_check_value(event_data[0], new_interval, event_data[1])
        return "Updated '%s' in '%s' to new interval %d." % (event_data[0], event_data[1], new_interval)

    def log_statistics(self, component_name):
        """
        Log statistics of an AtomHandler. Override this method for more sophisticated statistics output of the AtomHandler.
        @param component_name the name of the component which is printed in the log line.
        """
        if STAT_LEVEL == 1:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %d new values in the last 60"
                " minutes.", component_name, self.log_success, self.log_total, self.log_learned_values)
        elif STAT_LEVEL == 2:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully and learned %d new values in the last 60"
                " minutes. Following new values were learned: %s", component_name, self.log_success, self.log_total,
                self.log_learned_values, self.log_new_learned_values)
        self.log_success = 0
        self.log_total = 0
        self.log_learned_values = 0
        self.log_new_learned_values = []


class MissingMatchPathListValueDetector(MissingMatchPathValueDetector):
    """
    This detector works similar to the MissingMatchPathValueDetector.
    It only can lookup values from a list of pathes until one path really exists. It then uses this value as key to detect logAtoms
    belonging to the same data stream. This is useful when e.g. due to different log formats, the hostname, servicename or any other
    relevant channel identifier has alternative pathes.
    """

    def __init__(self, aminer_config, target_path_list, anomaly_event_handlers, persistence_id='Default', auto_include_flag=False,
                 default_interval=3600, realert_interval=86400, output_log_line=True):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param target_path to extract a source identification value from each logatom.
        """
        self.target_path_list = target_path_list
        super(MissingMatchPathListValueDetector, self).__init__(aminer_config, None, anomaly_event_handlers, persistence_id,
                                                                auto_include_flag, default_interval, realert_interval, output_log_line)

    def get_channel_key(self, log_atom):
        """Get the key identifying the channel this log_atom is coming from."""
        for target_path in self.target_path_list:
            match_element = log_atom.parser_match.get_match_dictionary().get(target_path)
            if match_element is None:
                continue
            if isinstance(match_element.match_object, bytes):
                affected_log_atom_values = match_element.match_object.decode()
            else:
                affected_log_atom_values = match_element.match_object
            return target_path, str(affected_log_atom_values)
        return None

    def send_event_to_handlers(self, anomaly_event_handler, event_data, log_atom, message_part):
        """Send an event to the event handlers."""
        anomaly_event_handler.receive_event(self.analysis_string % self.__class__.__name__, 'Interval too large between values',
                                            message_part, event_data, log_atom, self)
