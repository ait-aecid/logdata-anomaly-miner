# skipcq: FLK-D400
"""
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
from datetime import datetime
from aminer.AminerConfig import CONFIG_KEY_LOG_LINE_PREFIX
from aminer import AminerConfig


class EventData:
    """This class is used to create a string for different event handlers."""

    def __init__(self, event_type, event_message, sorted_log_lines, event_data, log_atom, event_source, analysis_context):
        self.event_type = event_type
        self.event_message = event_message
        self.sorted_log_lines = sorted_log_lines
        self.event_data = event_data
        self.event_source = event_source
        self.analysis_context = analysis_context
        if analysis_context is not None:
            self.description = '"%s"' % analysis_context.get_name_by_component(event_source)
        else:
            self.description = ""
        if log_atom is None:
            return
        self.log_atom = log_atom

    def receive_event_string(self):
        """Receive an event string."""
        message = ""
        if self.event_message is not None:
            indent = "  "
            if hasattr(self, "log_atom"):
                if self.log_atom.get_timestamp() is None:
                    import time
                    self.log_atom.set_timestamp(time.time())
                message += "%s " % datetime.fromtimestamp(self.log_atom.get_timestamp()).strftime("%Y-%m-%d %H:%M:%S")
                message += "%s\n" % self.event_message
                message += "%s: %s (%d lines)\n" % (self.event_source.__class__.__name__, self.description, len(self.sorted_log_lines))
            else:
                message += "%s (%d lines)\n" % (self.event_message, len(self.sorted_log_lines))
        else:
            indent = ""
        for line in self.sorted_log_lines:
            if isinstance(line, bytes):  # skipcq: PTC-W0048
                if line != b"":
                    message += indent + line.decode(AminerConfig.ENCODING) + "\n"
            else:
                original_log_line_prefix = self.analysis_context.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX)
                if original_log_line_prefix is not None and line.startswith(original_log_line_prefix):
                    message += line + "\n"
                elif line != "":
                    message += indent + line + "\n"
        if self.event_message is None:
            # remove last newline
            message = message[:-1]
        return message
