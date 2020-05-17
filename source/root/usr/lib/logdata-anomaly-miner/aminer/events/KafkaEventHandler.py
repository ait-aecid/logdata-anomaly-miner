"""This module defines an event handler that forwards Json-objects to Kafka."""

from kafka import KafkaProducer
from kafka.errors import KafkaError
import configparser
import sys
import json

from aminer.input.LogAtom import LogAtom


class KafkaEventHandler():
    """This class implements an event record listener, that will forward Json-objects to a Kafka queue."""

    def __init__(self, analysis_context, topic, options):
        self.producer = KafkaProducer(**options, value_serializer=lambda v: v.encode('utf-8'))
        self.topic = topic

    def receive_event(self, event_type, event_message, sorted_log_lines, json_dump, log_atom, event_source):
        """Receive information about a detected event in json format"""
        if not isinstance(json_dump, str) and not isinstance(json_dump, bytes):
            print('WARNING: KafkaEventHandler received non-string event data. Use the JsonConverterHandler to serialize it first.',
                  file=sys.stderr)
            return False
        try:
            self.producer.send(self.topic, json_dump)
        except KafkaError as err:
            print("Error: " + str(err))
            self.producer.close()
            self.producer = None
            return False
        return True
