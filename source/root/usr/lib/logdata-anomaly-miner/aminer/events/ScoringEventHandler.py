"""This module defines an event handler that converts an event to JSON.

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

import json
import time

from aminer.events.EventInterfaces import EventHandlerInterface
from aminer import AminerConfig


class ScoringEventHandler(EventHandlerInterface):
    """This class implements an event record listener, that will convert event data to JSON format."""

    def __init__(self, event_handlers, analysis_context, analyzed_field, confidence_field, weights):
        self.analysis_context = analysis_context
        self.event_handlers = event_handlers
        self.analyzed_field = analyzed_field
        self.confidence_field = confidence_field
        self.weights = weights
        self.analyzed_field = self.analyzed_field.split('/')
        self.confidence_field = self.confidence_field.split('/')

    def receive_event(self, event_type, event_message, sorted_log_lines, event_data, log_atom, event_source):
        """Receive information about a detected event."""
        path_valid = True
        event_data_analysis = event_data
        for path in self.analyzed_field:
            if path in event_data_analysis:
                event_data_analysis = event_data_analysis[path]
            else:
                path_valid = False
                break

        if path_valid:
            event_data_confidence = event_data
            for path in self.confidence_field[:-1]:
                if not isinstance(event_data_confidence, dict) or path not in event_data_confidence:
                    if not isinstance(event_data_confidence, dict):
                        event_data_confidence[path + '_original'] = event_data_confidence[path]
                    event_data_confidence[path] = {}
                event_data_confidence = event_data_confidence[path]
            if self.confidence_field[-1] in event_data_confidence:
                event_data_confidence[self.confidence_field[-1] + '_original'] = event_data_confidence[self.confidence_field[-1]]

            confidence_absolut = sum([self.weights[val] if val in self.weights else 0.5 for val in event_data_analysis])
            event_data_confidence[self.confidence_field[-1]] = {'confidence_absolut': confidence_absolut, 'confidence_percentile': confidence_absolut / len(event_data_analysis)}

        for listener in self.event_handlers:
            if hasattr(event_source, "output_event_handlers") and event_source.output_event_handlers is not None \
                    and listener not in event_source.output_event_handlers:
                import copy
                event_source = copy.copy(event_source)
                event_source.output_event_handlers.append(listener)
            listener.receive_event(event_type, event_message, sorted_log_lines, event_data, log_atom, event_source)


