"""This module defines a filter for parsed paths and values.

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

import logging
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.AminerConfig import CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX
from aminer import AminerConfig
from aminer.AminerConfig import DEBUG_LOG_NAME


class MatchFilter(AtomHandlerInterface):
    """This class creates events for specified paths and values."""

    def __init__(self, aminer_config, target_path_list, anomaly_event_handlers, target_value_list=None, output_logline=True,
                 log_resource_ignore_list=None):
        """
        Initialize the detector.
        @param aminer_config configuration from analysis_context.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that values are analyzed by their combined
               occurrences. When no paths are specified, the events given by the full path list are analyzed.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param target_value_list if not None, only match log atom if the match value is contained in the list.
        @param output_logline specifies whether the full parsed log atom should be provided in the output.
        """
        # avoid "defined outside init" issue
        self.next_persist_time, self.log_success, self.log_total = [None]*3
        super().__init__(
            aminer_config=aminer_config, target_path_list=target_path_list, anomaly_event_handlers=anomaly_event_handlers,
            target_value_list=target_value_list, output_logline=output_logline, log_resource_ignore_list=log_resource_ignore_list,
            mutable_default_args=["log_resource_ignore_list"]
        )
        if len(target_path_list) == 0:
            msg = "target_path_list must not be empty."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)

    def receive_atom(self, log_atom):
        """Forward all log atoms that involve specified path and optionally value."""
        for source in self.log_resource_ignore_list:
            if log_atom.source.resource_name == source:
                return
        self.log_total += 1
        match_dict = log_atom.parser_match.get_match_dictionary()
        for target_path in self.target_path_list:
            match = match_dict.get(target_path)
            if match is None:
                continue
            matches = []
            if isinstance(match, list):
                matches = match
            else:
                matches.append(match)
            affected_log_atom_values = []
            for match in matches:
                if isinstance(match.match_object, bytes):
                    affected_log_atom_values.append(match.match_object.decode(AminerConfig.ENCODING))
                else:
                    affected_log_atom_values.append(match.match_object)
            if self.target_value_list and not all(x in self.target_value_list for x in affected_log_atom_values):
                continue
            try:
                data = log_atom.raw_data.decode(AminerConfig.ENCODING)
            except UnicodeError:
                data = repr(log_atom.raw_data)
            original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
            analysis_component = {"AffectedLogAtomPaths": [target_path], "AffectedLogAtomValues": [str(affected_log_atom_values)]}
            sorted_log_lines = [original_log_line_prefix + data]
            event_data = {"AnalysisComponent": analysis_component}
            for listener in self.anomaly_event_handlers:
                listener.receive_event(
                    f"Analysis.{self.__class__.__name__}", "Log Atom Filtered", sorted_log_lines, event_data, log_atom, self)
            self.log_success += 1
