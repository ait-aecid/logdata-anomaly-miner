"""This module defines an event handler that adds a confidence score to the
anomaly output. The score is calculated through analysis of a list of strings
defined in the detector through the function get_weight_analysis_field_path and
weights the single strings based on the weights dictionary. The weights can
optionally be automatically calculated.

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

import copy
import logging

from aminer.events.EventInterfaces import EventHandlerInterface
from aminer.events.EventInterfaces import EventSourceInterface
from aminer.AminerConfig import DEBUG_LOG_NAME
from aminer.AnalysisChild import AnalysisContext


class ScoringEventHandler(EventHandlerInterface):
    """This class implements an event record listener, that will add a
    confidence score to the anomaly output."""

    def __init__(self, event_handlers, analysis_context, weights=None, auto_weights=False, auto_weights_history_length=1000):
        """
        Initialize the ScoringEventHandler component.
        @param weights A dictionary that specifies the weights of values for the scoring. The keys are the strings of the analyzed list and
        the corresponding values are the assigned weights. Strings that are not present in this dictionary have the weight 0.5 if not
        automatically weighted.
        @param auto_weights boolean value that states if the weights should be automatically calculated through the formula
        10 / (10 + number of value appearances).
        @param auto_weights_history_length integer value that specifies the number of values that are considered in the calculation of the
        weights.
        """
        if not event_handlers:
            msg = "event_handlers must not be empty or None."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        if not isinstance(event_handlers, list) or any(not isinstance(x, EventHandlerInterface) for x in event_handlers):
            msg = "event_handlers must be a list of EventHandlerInterface."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if not isinstance(analysis_context, AnalysisContext):
            msg = "analysis_child must be of type AnalysisChild."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if weights is not None and (not isinstance(weights, dict) or any(not isinstance(x, (int, float)) for x in list(weights.values()))):
            msg = "weights must be a dictionary with numerical values."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if not isinstance(auto_weights, bool):
            msg = "auto_weights must be of type boolean."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if isinstance(auto_weights_history_length, bool) or not isinstance(auto_weights_history_length, int):
            msg = "auto_weights must be of type boolean."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if auto_weights_history_length < 1:
            msg = "auto_weights must be greater than zero."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.analysis_context = analysis_context
        self.event_handlers = event_handlers
        self.weights = weights
        self.auto_weights = auto_weights
        self.auto_weights_history_length = auto_weights_history_length

        if self.auto_weights:
            self.history_list = [[] for _ in range(self.auto_weights_history_length)]
            self.history_list_index = 0

    def receive_event(self, event_type, event_message, sorted_log_lines, event_data, log_atom, event_source):
        """Receive information about a detected event."""
        path_valid = True
        if isinstance(event_source, EventSourceInterface):
            analysis_field_path = event_source.get_weight_analysis_field_path()
            output_field_path = event_source.get_weight_output_field_path()
        else:
            analysis_field_path = []
            output_field_path = []

        if not analysis_field_path:
            path_valid = False
        else:
            analysis_list = event_data
            for path in analysis_field_path:
                if path in analysis_list:
                    analysis_list = analysis_list[path]
                else:
                    path_valid = False
                    break

        # Calculate and add the confidence to the output if the path is valid
        if path_valid:
            event_data_confidence = event_data
            for path in output_field_path[:-1]:
                if path not in event_data_confidence:
                    event_data_confidence[path] = {}
                event_data_confidence = event_data_confidence[path]

            # Calculate the absolute confidence
            confidence_absolut = sum(self.get_weight(val) for val in analysis_list)
            # Add the absolute and mean confidence to the message
            event_data_confidence[output_field_path[-1]] = {'confidence_absolut': confidence_absolut,
                                                            'confidence_mean': confidence_absolut / len(analysis_list)}

            # Update the history list and increase the count index
            if self.auto_weights:
                self.history_list[self.history_list_index] = analysis_list
                self.history_list_index += 1
                if self.history_list_index >= self.auto_weights_history_length:
                    self.history_list_index %= self.auto_weights_history_length

        # Send the message to the following event handlers
        for listener in self.event_handlers:
            if hasattr(event_source, "output_event_handlers") and event_source.output_event_handlers is not None \
                    and listener not in event_source.output_event_handlers:
                event_source = copy.copy(event_source)
                event_source.output_event_handlers.append(listener)
            listener.receive_event(event_type, event_message, sorted_log_lines, event_data, log_atom, event_source)

    def get_weight(self, value):
        """Return the weight of the value parameter."""
        if self.weights is not None and value in self.weights:
            # Return the specified weight if the value is in the weight list
            return self.weights[value]
        if not self.auto_weights:
            # Return 0.5 if the value is not in the weight list and the weights are not automatically calculated
            return 0.5
        # Else calculate the weight through 10 / (10 + number of value appearances)
        return 10 / (10 + sum(value in value_list for value_list in self.history_list))
