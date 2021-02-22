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


class JsonConverterHandler(EventHandlerInterface):
    """This class implements an event record listener, that will convert event data to JSON format."""

    def __init__(self, json_event_handlers, analysis_context):
        self.json_event_handlers = json_event_handlers
        self.analysis_context = analysis_context

    def receive_event(self, event_type, event_message, sorted_log_lines, event_data, log_atom, event_source):
        """Receive information about a detected event."""
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
            json_error = ''

            log_data = {}
            if isinstance(log_atom.raw_data, bytes):
                log_data['RawLogData'] = [bytes.decode(log_atom.raw_data)]
            else:
                log_data['RawLogData'] = [log_atom.raw_data]
            if log_atom.get_timestamp() is None:
                log_atom.set_timestamp(time.time())
            log_data['Timestamps'] = [round(log_atom.atom_time, 2)]
            log_data['DetectionTimestamp'] = time.time()
            log_data['LogLinesCount'] = len(sorted_log_lines)
            if log_atom.parser_match is not None and hasattr(event_source, 'output_log_line') and event_source.output_log_line:
                log_data['AnnotatedMatchElement'] = log_atom.parser_match.match_element.annotate_match('')

            analysis_component = {'AnalysisComponentIdentifier': self.analysis_context.get_id_by_component(event_source)}
            if event_source.__class__.__name__ == 'ExtractedData_class':
                analysis_component['AnalysisComponentType'] = 'DistributionDetector'
            else:
                analysis_component['AnalysisComponentType'] = str(event_source.__class__.__name__)
            analysis_component['AnalysisComponentName'] = self.analysis_context.get_name_by_component(event_source)
            analysis_component['Message'] = event_message
            analysis_component['PersistenceFileName'] = event_source.persistence_id
            if hasattr(event_source, 'autoIncludeFlag'):
                analysis_component['TrainingMode'] = event_source.auto_include_flag

            detector_analysis_component = event_data.get('AnalysisComponent', None)
            if detector_analysis_component is not None:
                for key in detector_analysis_component:
                    if key in analysis_component.keys():
                        json_error += "AnalysisComponent attribute '%s' is already in use and can not be overwritten!\n" % key
                        continue
                    analysis_component[key] = detector_analysis_component.get(key, None)

            if 'LogData' not in event_data:
                event_data['LogData'] = log_data
            event_data['AnalysisComponent'] = analysis_component
            if json_error != '':
                event_data['JsonError'] = json_error

        json_data = json.dumps(event_data, indent=2)
        res = [''] * len(sorted_log_lines)
        res[0] = str(json_data)

        for listener in self.json_event_handlers:
            listener.receive_event(event_type, event_message, res, json_data, log_atom, event_source)
