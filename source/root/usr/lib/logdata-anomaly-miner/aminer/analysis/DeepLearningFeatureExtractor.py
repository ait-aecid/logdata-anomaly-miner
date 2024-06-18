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
from aminer.AminerConfig import STAT_LEVEL, STAT_LOG_NAME, CONFIG_KEY_LOG_LINE_PREFIX, DEBUG_LOG_NAME
from aminer.AnalysisChild import AnalysisContext
from aminer.util import PersistenceUtil
from aminer.events.EventInterfaces import EventSourceInterface
from aminer.input.InputInterfaces import AtomHandlerInterface, PersistableComponentInterface
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface
from collections import OrderedDict



class DeepLearningFeatureExtractor(AtomHandlerInterface, TimeTriggeredComponentInterface, EventSourceInterface, PersistableComponentInterface):
    """This class creates events when new value sequences were found."""
    
    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, anomaly_event_handlers, target_path_list, ignore_list, id_path_list, window_size, publisher_address, subscriber_address, publisher_topic, subscriber_topic, allow_missing_id=False, persistence_id='Default', learn_mode=False, output_logline=True):
        """
        Initialize the detector.
        @param aminer_config configuration from analysis_context.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that values are analyzed by their combined
               occurrences. When no paths are specified, the events given by the full path list are analyzed.
        @param ignore_list list of paths that are not considered for analysis, 
               i.e., events that contain one of these paths are omitted. The default value is [] as None is not iterable.
        @param id_path_list the path will be used to group the events before generating sequences.
        @param window_size the number of events in each sequence.
        @param publisher_address the address used by the detector to publish event sequences to be consumed by AMiner-Deep.
               The format of the address, the transport should zmq supported transport. {transport}://{host}:{port}
        @param subscriber_address the address used by the detector to consume AMiner-Deep output.
               The format of the address, the transport should zmq supported transport. {transport}://{host}:{port}
        @param publisher_topic, this part of the configurations need to be align with aminer-deep configrations,
               avoid using :,-,_,[]
        @param subscriber_topic, this part of the configurations need to be align with aminer-deep configrations,
               avoid using :,-,_,[]
        @param persistence_id name of persistence document.
        @param learn_mode specifies whether the model is trained or used for detection
        @param output_logline specifies whether the full parsed log atom should be provided in the output.
        @param allow_missing_id specifies whether log atoms without id path should be omitted (only if id path is set).
        """
        super().__init__(
            mutable_default_args=["target_path_list", "scoring_path_list", "ignore_list", "constraint_list", "log_resource_ignore_list"],
            aminer_config=aminer_config, anomaly_event_handlers=anomaly_event_handlers, target_path_list=target_path_list,
            ignore_list=ignore_list, id_path_list=id_path_list, window_size=window_size,
            publisher_address=publisher_address, subscriber_address=subscriber_address, publisher_topic=publisher_topic,
            subscriber_topic=subscriber_topic, persistence_id=persistence_id, learn_mode=learn_mode,
            output_logline=output_logline, allow_missing_id=allow_missing_id
        )
        self.persistence_id = persistence_id
        self.next_persist_time = None
        self.event_encoding = {}
        self.group_event_list = {}
        self.context = zmq.Context.instance()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.bind(self.publisher_address)
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.bind(self.subscriber_address)
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, subscriber_topic) 
        self.pub_top = publisher_topic 
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
        """Receive a log atom from a source."""
        for source in self.log_resource_ignore_list:
            if log_atom.source.resource_name.decode() == source:
                return False
        parser_match = log_atom.parser_match
        self.log_total += 1
        if self.learn_mode is True and self.stop_learning_timestamp is not None and \
                self.stop_learning_timestamp < log_atom.atom_time:
            logging.getLogger(DEBUG_LOG_NAME).info("Stopping learning in the %s.", self.__class__.__name__)
            self.learn_mode = False

        # Skip paths from ignore list.
        for ignore_path in self.ignore_list:
            if ignore_path in parser_match.get_match_dictionary().keys():
                return False

        if self.target_path_list is None or len(self.target_path_list) == 0:
            # Event is defined by the full path of log atom.
            constraint_path_flag = False
            for constraint_path in self.constraint_list:
                if parser_match.get_match_dictionary().get(constraint_path) is not None:
                    constraint_path_flag = True
                    break
            if not constraint_path_flag and self.constraint_list != []:
                return False
            log_event = tuple(parser_match.get_match_dictionary().keys())
        else:
            # Event is defined by value combos in target_path_list
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
                # the match variable is not needed any more and reused for the iteration.
                for match in matches:
                    if isinstance(match.match_object, bytes):
                        value = match.match_object.decode(AminerConfig.ENCODING)
                    else:
                        value = str(match.match_object)
                    if value is not None:
                        all_values_none = False
                    values.append(value)
            if all_values_none is True:
                return False
            log_event = tuple(values)

        # In case that id_path_list is set, use it to differentiate sequences by their id.
        # Otherwise, the empty tuple () is used as the only key of the current_sequences dict.
        id_tuple = ()
        for id_path in self.id_path_list:
            id_match = parser_match.get_match_dictionary().get(id_path)
            if id_match is None:
                if self.allow_missing_id is True:
                    # Omit this path
                    pass
                else:
                    # Omit log atom if one of the id paths is not found.
                    return False
            else:
                matches = []
                if isinstance(id_match, list):
                    matches = id_match
                else:
                    matches.append(id_match)
                for match in matches:
                    if isinstance(match.match_object, bytes):
                        id_tuple += (match.match_object.decode(AminerConfig.ENCODING),)
                    else:
                        id_tuple += (match.match_object,)

        if not id_tuple in self.group_event_list:
            self.group_event_list[id_tuple] = [-1] * self.window_size
        if log_event not in self.event_encoding:
            self.event_encoding[log_event] = len(self.event_encoding)
        self.group_event_list[id_tuple].append(self.event_encoding[log_event])
        len_current_group = len(self.group_event_list[id_tuple])
        if len(self.group_event_list[id_tuple]) < self.window_size:
            # Do nothing since not enough events are available yet
            pass
        else:
            self.group_event_list[id_tuple] = self.group_event_list[id_tuple][-self.window_size:]
            #print(str(id_tuple) + ': ' + str(self.group_event_list[id_tuple]))
            print('sending')
            #try:
            time.sleep(1)
            #self.pub_socket.send_string("aminer test test test")
            self.pub_socket.send_string("{}:{}:{}:{}".format(self.pub_top, id_tuple, self.learn_mode, json.dumps(self.group_event_list[id_tuple])))
            time.sleep(1)
            #context = zmq.Context()
            #socket = context.socket(zmq.PUB)
            #socket.bind("tcp://127.0.0.1:5556")
            #time.sleep(1)
            #socket.send_string("aminer Message x")
            #time.sleep(1)
            #except err:
            #    print("Problem with ZMQ. Aborting.")
            #    logging.getLogger(DEBUG_LOG_NAME).error("Problem with ZMQ. Aborting.")
            #    self.pub_socket.close()
            if False: # self.learn_mode is False:
                print('waiting')
                msg = self.sub_socket.recv_string()
                print('done')
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

    def load_persistence_data(self):
        # TODO persist encoding
        return None

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
