"""
                logging.gitLogger(DEBUG_LOG_NAME).error(msg)
This module defines an event handler that forwards anomalies to ZeroMQ.

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

import sys
import logging
from aminer.AminerConfig import DEBUG_LOG_NAME
from aminer.events.EventInterfaces import EventHandlerInterface
import zmq


class ZmqEventHandler(EventHandlerInterface):
    """This class implements an event record listener, that will forward Json-objects to a ZeroMQ queue."""

    def __init__(self, analysis_context, topic=None, url="ipc:///tmp/aminer"):
        self.analysis_context = analysis_context
        self.url = url
        self.topic = topic
        self.producer = None
        self.context = None
        self.zmq_imported = False
        logging.getLogger(DEBUG_LOG_NAME).info("ZmqEventHandler initialized")

    def receive_event(self, _event_type, _event_message, _sorted_log_lines, event_data, _log_atom, event_source):
        """Receive information about a detected event in json format."""
        if hasattr(event_source, 'output_event_handlers') and event_source.output_event_handlers is not None and self not in \
                event_source.output_event_handlers:
            return True
        component_name = self.analysis_context.get_name_by_component(event_source)
        if component_name in self.analysis_context.suppress_detector_list:
            return True
        if self.zmq_imported is False:
            try:
                self.context = zmq.Context()
                self.producer = self.context.socket(zmq.PUB)
                self.producer.bind(self.url)
                logging.getLogger(DEBUG_LOG_NAME).info("Created socket on %s", self.url)
                self.zmq_imported = True
            except ImportError:
                msg = 'ZeroMQ module not found.'
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                print('ERROR: ' + msg, file=sys.stderr)
                return False
        if not isinstance(event_data, str) and not isinstance(event_data, bytes):
            msg = 'ZmqEventHandler received non-string event data. Use the JsonConverterHandler to serialize it first.'
            logging.getLogger(DEBUG_LOG_NAME).warning(msg)
            print('WARNING: ' + msg, file=sys.stderr)
            return False
        try:
            if self.topic:
                self.producer.send_string(self.topic, flags=zmq.SNDMORE)
            '''
            please note that if the JsonConvertHandler was used(json: true)
            then it is possible to use the socket.recv_json() for the
            consumer. recv_json() will decode the json-string
            '''
            self.producer.send_string(event_data)
        except zmq.ZMQError as err:
            msg = str(err)
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            print("Error: " + msg, file=sys.stderr)
            self.producer.disconnect()
            self.producer = None
            self.zmq_imported = False
            return False
        return True
