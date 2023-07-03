"""
This module defines a detector for unsorted timestamps.

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

import os

from aminer.input.InputInterfaces import AtomHandlerInterface
from datetime import datetime
from aminer.AminerConfig import CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX
from aminer import AminerConfig


class TimestampsUnsortedDetector(AtomHandlerInterface):
    """
    This class creates events when unsorted timestamps are detected.
    This is useful mostly to detect algorithm malfunction or configuration errors, e.g. invalid timezone configuration.
    """

    def __init__(self, aminer_config, anomaly_event_handlers, exit_on_error_flag=False, output_logline=True):
        """
        Initialize the detector.
        @param aminer_config configuration from analysis_context.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param exit_on_error_flag exit the aminer forcefully if a log atom with a wrong timestamp is found.
        @param output_logline specifies whether the full parsed log atom should be provided in the output.
        """
        # avoid "defined outside init" issue
        self.log_success, self.log_total = [None]*2
        super().__init__(aminer_config=aminer_config, anomaly_event_handlers=anomaly_event_handlers, exit_on_error_flag=exit_on_error_flag,
                         output_logline=output_logline)
        self.last_timestamp = 0

    def receive_atom(self, log_atom):
        """
        Receive on parsed atom and the information about the parser match.
        @param log_atom the parsed log atom
        @return True if this handler was really able to handle and process the match. Depending on this information, the caller
        may decide if it makes sense passing the parsed atom also to other handlers.
        """
        self.log_total += 1
        if log_atom.get_timestamp() is None:
            return False
        if log_atom.get_timestamp() < self.last_timestamp:
            try:
                data = log_atom.raw_data.decode(AminerConfig.ENCODING)
            except UnicodeError:
                data = repr(log_atom.raw_data)
            original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
            if self.output_logline:
                sorted_log_lines = [log_atom.parser_match.match_element.annotate_match("") + os.linesep + original_log_line_prefix + data]
            else:
                sorted_log_lines = [original_log_line_prefix + data]
            analysis_component = {"LastTimestamp": self.last_timestamp}
            event_data = {"AnalysisComponent": analysis_component}
            for listener in self.anomaly_event_handlers:
                listener.receive_event(
                    f"Analysis.{self.__class__.__name__}",
                    f"Timestamp {datetime.fromtimestamp(log_atom.get_timestamp()).strftime('%Y-%m-%d %H:%M:%S')} below "
                    f"{datetime.fromtimestamp(self.last_timestamp).strftime('%Y-%m-%d %H:%M:%S')}", sorted_log_lines, event_data,
                    log_atom, self)
            if self.exit_on_error_flag:
                import sys
                sys.exit(1)
        self.last_timestamp = log_atom.get_timestamp()
        self.log_success += 1
        return True
