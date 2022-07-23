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


class JsonConverterHandler(EventHandlerInterface):
    """This class implements an event record listener, that will convert event data to JSON format."""

    def __init__(self, json_event_handlers, analysis_context, pretty_print=True):
        """
        Initialize the event handler.
        @param json_event_handlers the event handlers to which the json converted data is sent.
        @param analysis_context the analysis context used to get the component.
        @param pretty_print if true, the json is printed pretty; otherwise the json is printed with less space needed.
        """
        self.json_event_handlers = json_event_handlers
        self.analysis_context = analysis_context
        self.pretty_print = pretty_print

    def receive_event(self, event_type, event_message, sorted_loglines, event_data, log_atom, event_source):
        """
        Receive information about a detected event.
        @param event_type is a string with the event type class this event belongs to. This information can be used to interpret
               type-specific event_data objects. Together with the eventMessage and sorted_loglines, this can be used to create generic log
               messages.
        @param event_message the first output line of the event.
        @param sorted_loglines sorted list of log lines that were considered when generating the event, as far as available to the time
               of the event. The list has to contain at least one line.
        @param event_data type-specific event data object, should not be used unless listener really knows about the event_type.
        @param log_atom the log atom which produced the event.
        @param event_source reference to detector generating the event.
        """
        if hasattr(event_source, 'output_event_handlers') and event_source.output_event_handlers is not None and self not in \
                event_source.output_event_handlers:
            return
        component_name = self.analysis_context.get_name_by_component(event_source)
        if component_name in self.analysis_context.suppress_detector_list:
            return
        if 'StatusInfo' in event_data:
            # No anomaly; do nothing on purpose
            pass
        else:
            log_data = {}
            try:
                data = log_atom.raw_data.decode(AminerConfig.ENCODING)
            except UnicodeError:
                data = repr(log_atom.raw_data)
            log_data['RawLogData'] = [data]
            if log_atom.get_timestamp() is None:
                log_atom.set_timestamp(time.time())
            log_data['Timestamps'] = [round(log_atom.atom_time, 2)]
            log_data['DetectionTimestamp'] = round(time.time(), 2)
            log_data['LogLinesCount'] = len(sorted_loglines)
            if log_atom.parser_match is not None and hasattr(event_source, 'output_logline') and event_source.output_logline:
                log_data['AnnotatedMatchElement'] = {}
                for path, match in log_atom.parser_match.get_match_dictionary().items():
                    if isinstance(match, list):
                        for match_element_id, match_element in enumerate(match):
                            if isinstance(match_element.match_object, bytes):
                                log_data['AnnotatedMatchElement'][path + '/' + str(match_element_id)] = match_element.match_object.decode(
                                    AminerConfig.ENCODING)
                            else:
                                log_data['AnnotatedMatchElement'][path + '/' + str(match_element_id)] = str(match_element.match_object)
                    elif isinstance(match.match_object, bytes):
                        log_data['AnnotatedMatchElement'][path] = match.match_object.decode(AminerConfig.ENCODING)
                    else:
                        log_data['AnnotatedMatchElement'][path] = str(match.match_object)

            analysis_component = {'AnalysisComponentIdentifier': self.analysis_context.get_id_by_component(event_source)}
            if event_source.__class__.__name__ == 'ExtractedData_class':
                analysis_component['AnalysisComponentType'] = 'DistributionDetector'
            else:
                analysis_component['AnalysisComponentType'] = str(event_source.__class__.__name__)
            analysis_component['AnalysisComponentName'] = self.analysis_context.get_name_by_component(event_source)
            analysis_component['Message'] = event_message
            if hasattr(event_source, "persistence_id"):
                analysis_component['PersistenceFileName'] = event_source.persistence_id
            if hasattr(event_source, 'learn_mode'):
                analysis_component['TrainingMode'] = event_source.learn_mode

            detector_analysis_component = event_data.get('AnalysisComponent')
            if detector_analysis_component is not None:
                for key in detector_analysis_component:
                    if key in analysis_component:
                        continue
                    analysis_component[key] = detector_analysis_component.get(key)

            if 'LogData' not in event_data:
                event_data['LogData'] = log_data
            event_data['AnalysisComponent'] = analysis_component

        if self.pretty_print is True:
            json_data = json.dumps(event_data, indent=2)
        else:
            json_data = json.dumps(event_data)
        res = [''] * len(sorted_loglines)
        res[0] = str(json_data)

        for listener in self.json_event_handlers:
            if hasattr(event_source, "output_event_handlers") and event_source.output_event_handlers is not None \
                    and listener not in event_source.output_event_handlers:
                import copy
                event_source = copy.copy(event_source)
                event_source.output_event_handlers.append(listener)
            listener.receive_event(event_type, None, res, json_data, log_atom, event_source)
