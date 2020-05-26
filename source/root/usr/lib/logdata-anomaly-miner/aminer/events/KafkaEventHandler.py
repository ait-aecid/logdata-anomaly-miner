"""This module defines an event handler that forwards Json-objects to Kafka."""

from kafka import KafkaProducer
from kafka.errors import KafkaError
import sys
from aminer.events import EventHandlerInterface


class KafkaEventHandler(EventHandlerInterface):
    """This class implements an event record listener, that will forward Json-objects to a Kafka queue."""

    def __init__(self, analysis_context, topic, options):
        self.analysis_context = analysis_context
        self.producer = KafkaProducer(**options, value_serializer=lambda v: v.encode())
        self.topic = topic

    def receive_event(self, event_type, event_message, sorted_log_lines, event_data, log_atom, event_source):
        """Receive information about a detected event in json format"""
        if not isinstance(event_data, str) and not isinstance(event_data, bytes):
            print('WARNING: KafkaEventHandler received non-string event data. Use the JsonConverterHandler to serialize it first.',
                  file=sys.stderr)
            return False
        try:
            self.producer.send(self.topic, event_data)
        except KafkaError as err:
            print("Error: " + str(err))
            self.producer.close()
            self.producer = None
            return False
        return True
