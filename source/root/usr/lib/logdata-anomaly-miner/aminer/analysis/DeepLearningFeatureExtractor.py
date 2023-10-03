"""
This module defines a Sequence detector using a deep learning model. 
Its involves other components outside aminer pipline communcated using 
PUB-SUB model using zmq library.
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
import os
import logging
import zmq
import json

from aminer import AminerConfig
from aminer.AminerConfig import STAT_LEVEL, STAT_LOG_NAME, CONFIG_KEY_LOG_LINE_PREFIX
from aminer.AnalysisChild import AnalysisContext
from aminer.util import PersistenceUtil
from aminer.events.EventInterfaces import EventSourceInterface
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface
from collections import OrderedDict



class DeepLearningFeatureExtractor(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface):
    """This class creates events when new value sequences were found."""
    
    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, anomaly_event_handlers, target_path_list, ignore_list, group_by_list, window_size, publisher_address, subscriber_address, publisher_topic, subscriber_topic, event_encoding=False, persistence_id='Default', learn_mode=False, output_logline=True):
        """
        Initialize the detector.
        @param aminer_config configuration from analysis_context.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that values are analyzed by their combined
               occurrences. When no paths are specified, the events given by the full path list are analyzed.
        @param ignore_list list of paths that are not considered for analysis, 
               i.e., events that contain one of these paths are omitted. The default value is [] as None is not iterable.
        @param group_by_list the path will be used to group the events before generating sequence ex: processId.
        @param window_size the number of event in each sequence.
        @param publisher_address the address used by the detector to publish events sequences to consumed by AMiner-Deep.
               The format of the address, the transport should zmq supported transport. {transport}://{host}:{port}
        @param subscriber_address the address used by the detector to consume AMiner-Deep output.
               The format of the address, the transport should zmq supported transport. {transport}://{host}:{port}
        @param publisher_topic, this part of the configrations need to be align with aminer-deep configrations,
               avoid using :,-,_,[]
        @param subscriber_topic, this part of the configrations need to be align with aminer-deep configrations,
               avoid using :,-,_,[]
        @param event_encoding, to support the process with ordinal encoding for the analysed events, 
               if False, orginal code will be used, otherwise 
        @param persistence_id name of persistence document.
        @param learn_mode in case the learn mode is true, the detector will not waite for the aminer-deep output instead, 
               it will push the log event only.
        @param output_logline specifies whether the full parsed log atom should be provided in the output.
        """
        self.aminer_config = aminer_config
        self.anomaly_event_handlers = anomaly_event_handlers
        self.target_path_list = target_path_list
        self.ignore_list = ignore_list
        self.group_by_path_list = group_by_list
        self.window_size = window_size
        self.persistence_id = persistence_id
        self.next_persist_time = None
        self.learn_mode = learn_mode
        self.output_logline = output_logline
        self.publisher_address = publisher_address
        self.subscriber_address = subscriber_address
        self.group_event_list = {}
        self.context = zmq.Context.instance()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.connect(self.publisher_address)
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.connect(self.subscriber_address)
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, subscriber_topic) 
        self.pub_top = publisher_topic 
        self.event_encoding = event_encoding
        self.event_encoding_list = {}
    
        self.persistence_file_name = AminerConfig.build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)

        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        if persistence_data is not None:
            for encode in persistence_data:
                encode_elem_tuple = []
                for encode_elem in encode:
                    encode_elem_tuple.append(tuple(encode_elem))
                self.event_encoding_list.add(tuple(encode_elem_tuple))

    def receive_atom(self, log_atom):
        # Catch parsed log objects into parser_match
        parser_match = log_atom.parser_match
        
        # Skip paths from ignore list. 
        for ignore_path in self.ignore_list:
            if ignore_path in parser_match.get_match_dictionary().keys():
                return
    
        # Get the log data from target_path_list
        values = []
        all_values_none = True
        for path in self.target_path_list:
            match = parser_match.get_match_dictionary().get(path)
            if match is None:
                continue
            matches = []
            if isinstance(match, list):
                matches = match
            else:
                matches.append(match)
            for match in matches:
                if isinstance(match.match_object, bytes):
                    value = match.match_object.decode(AminerConfig.ENCODING)
                else:
                    value = str(match.match_object)
                if value is not None:
                    all_values_none = False
                values.append(value)
        if all_values_none is True:
            return
        log_event = tuple(values)
        
        """
        Get the group by values based on group_by_path_list, if the group_by_path_list not configured or empty
        all events will be in the same group.
        """
        if bool(self.group_by_path_list):            
            g_values = []
            g_all_values_none = True
            for path in self.group_by_path_list:
                match = parser_match.get_match_dictionary().get(path)
                if match is None:
                    continue
                matches = []
                if isinstance(match, list):
                    matches = match
                else:
                    matches.append(match)
                for match in matches:
                    if isinstance(match.match_object, bytes):
                        value = match.match_object.decode(AminerConfig.ENCODING)
                    else:
                        value = str(match.match_object)
                    if value is not None:
                        g_all_values_none = False
                    g_values.append(value)
            if all_values_none is True:
                return
            group_by_values = tuple(g_values)
        else:
            group_by_values = (0)

        """ In case of first event in the group, create empty list in the group_event_list """
        if not group_by_values in self.group_event_list:
            self.group_event_list[group_by_values] = []
        """
         Append the log values to the event group, in case the event_encoding is True, use encoding value, 
         else, use event value  
        """
        if self.event_encoding:
            if not log_event in self.event_encoding_list:
                self.event_encoding_list[log_event] = self.generate_event_encoding()
            self.group_event_list[group_by_values].append(self.event_encoding_list[log_event])
        else:
            self.group_event_list[group_by_values].append(log_event)
        """
         Genrate the sequence based on the the window size, and send it to AMiner-deep, in case the lean_mode is True,
         detector will continue without waiting for AMiner-deep, else, receive the output and alart in case of anomaly 
         is detected
        """
        len_current_group = len(self.group_event_list[group_by_values])
        if len_current_group > self.window_size:
            current_sequence = list(self.group_event_list[group_by_values][len_current_group-(self.window_size+1):len_current_group])
            """
            To avoid overloading the memory by the analyzed events, this part will keep only window_size numbers of events.
            """
            self.group_event_list[group_by_values] = current_sequence
            self.pub_socket.send_string("{}:{}:{}".format(self.pub_top, group_by_values, json.dumps(current_sequence)))
            if self.learn_mode is False:
                msg = self.sub_socket.recv_string()
                top, result = msg.split(":")
                result = json.loads(result)
                group, current_sequence, label, result = result
                result = bool(result)
                if result is True:
                    if self.output_logline:
                        sorted_log_lines = [log_atom.parser_match.match_element.annotate_match('')]
                    else:
                        sorted_log_lines = log_event
                    analysis_component = {'AffectedLogAtomPaths': self.target_path_list, 'AffectedLogAtomValues': list(log_event)}
                    sequence_info = {'AffectedSequence': current_sequence,
                                     'AffectedLogEventGroup': group,
                                     'WindowSize': self.window_size
                                    }
                    event_data = {'AnalysisComponent': analysis_component, 'SequenceData': sequence_info}
                    for listener in self.anomaly_event_handlers:
                        listener.receive_event('Analysis.%s' % self.__class__.__name__, 'New anomaly detected', sorted_log_lines, 
                                               event_data, log_atom, self)

    def get_time_trigger_class(self):
        """
        Get the trigger class this component should be registered for.
        This trigger is used only for persistence, so real-time triggering is needed.
        """
        return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def do_timer(self, trigger_time):
        """Check current ruleset should be persisted."""
        if self.next_persist_time is None:
            return 600

        delta = self.next_persist_time - trigger_time
        if delta < 0:
            self.do_persist()
            delta = 600
        return delta

    def generate_event_encoding(self):
        """
        Define the encoding technique, that will be used by the detector
        Hereby, simple ordinal encoding is defined.
        """
        if len(self.event_encoding_list) == 0:
            return 0
        else:
            return len(self.event_encoding_list) + 1

    def do_persist(self):
        """Immediately write persistence data to storage."""
        if self.event_encoding:
            PersistenceUtil.store_json(self.persistence_file_name, list(self.event_encoding_list))
            self.next_persist_time = None
        pass

    def allowlist_event(self):
        """Allowlist an event."""
        pass