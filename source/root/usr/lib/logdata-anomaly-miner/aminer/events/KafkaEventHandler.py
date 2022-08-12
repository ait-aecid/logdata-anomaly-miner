"""
This module defines an event handler that forwards Json-objects to Kafka.

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


class KafkaEventHandler(EventHandlerInterface):
    """This class implements an event record listener, that will forward Json-objects to a Kafka queue."""

    def __init__(self, analysis_context, topic, options):
        """
        Initialize the event handler.
        @param analysis_context the analysis context used to get the component.
        @param topic the Kafka topic to which the data is sent.
        @param options Kafka specific options.
        """
        self.analysis_context = analysis_context
        self.options = options
        self.topic = topic
        self.producer = None
        self.kafka_imported = False

    def receive_event(self, _event_type, _event_message, _sorted_loglines, event_data, _log_atom, event_source):
        """
        Receive information about a detected event in json format.
        @param _event_type is a string with the event type class this event belongs to. This information can be used to interpret
               type-specific event_data objects. Together with the eventMessage and sorted_loglines, this can be used to create generic log
               messages.
        @param _event_message the first output line of the event.
        @param _sorted_loglines sorted list of log lines that were considered when generating the event, as far as available to the time
               of the event. The list has to contain at least one line.
        @param event_data type-specific event data object, should not be used unless listener really knows about the event_type.
        @param _log_atom the log atom which produced the event.
        @param event_source reference to detector generating the event.
        """
        if hasattr(event_source, 'output_event_handlers') and event_source.output_event_handlers is not None and self not in \
                event_source.output_event_handlers:
            return True
        component_name = self.analysis_context.get_name_by_component(event_source)
        if component_name in self.analysis_context.suppress_detector_list:
            return True
        if self.kafka_imported is False:
            try:
                from kafka import KafkaProducer
                from kafka.errors import KafkaError
                self.producer = KafkaProducer(**self.options, value_serializer=lambda v: v.encode())
                self.kafka_imported = True
            except ImportError:
                msg = 'Kafka module not found.'
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                print('ERROR: ' + msg, file=sys.stderr)
                return False
        if not isinstance(event_data, str) and not isinstance(event_data, bytes):
            msg = 'KafkaEventHandler received non-string event data. Use the JsonConverterHandler to serialize it first.'
            logging.getLogger(DEBUG_LOG_NAME).warning(msg)
            print('WARNING: ' + msg, file=sys.stderr)
            return False
        try:
            self.producer.send(self.topic, event_data)
        except KafkaError as err:
            msg = str(err)
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            print("Error: " + msg, file=sys.stderr)
            self.producer.close()
            self.producer = None
            return False
        return True
