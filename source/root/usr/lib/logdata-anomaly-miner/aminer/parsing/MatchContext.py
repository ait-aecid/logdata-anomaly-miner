"""
This module defines the match context.

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
from typing import Union
from aminer.AminerConfig import DEBUG_LOG_NAME
from aminer import AminerConfig


class MatchContext:
    """
    This class allows storage of data relevant during the matching process, e.g. the root node and the remaining unmatched data.
    Then searching for non-atomic matches, e.g. sequences, the context might be modified by model subelements, even if the main model
    element will not return a match. In that case, those non-atomic model elements have to care to restore the context before returning.
    """

    def __init__(self, match_data: bytes):
        """
        Create a MatchContext with the full unmatched string data.
        @param match_data the data that will be tested by the next model element.
        """
        if not isinstance(match_data, bytes):
            msg = "match_data has to be of the type bytes."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        self.match_data = match_data

    def update(self, match_string: bytes):
        """
        Update the match context by removing the given matched string data from the context data still to be matched.
        This method does not check, if the removed data is the same as the trailing match data for performance reasons. This is done
        only in the DebugMatchContext class.
        """
        self.match_data = self.match_data[len(match_string):]


class DebugMatchContext(MatchContext):
    """This class defines a slower MatchContext for debugging purposes."""

    def __init__(self, match_data: bytes):
        self.debug_info = ""
        self.last_match_data: Union[None, bytes] = None
        self.shortest_unmatched_data = match_data
        super(DebugMatchContext, self).__init__(match_data)

    def update(self, match_string: bytes):
        """Update the context and store debugging information."""
        if not isinstance(match_string, bytes):
            msg = "match_string has to be of the type bytes."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if len(match_string) < 1:
            return
        try:
            match_data = self.match_data.decode(AminerConfig.ENCODING)
            m_string = match_string.decode(AminerConfig.ENCODING)
        except UnicodeError:
            match_data = repr(self.match_data)
            m_string = repr(match_string)
        if self.last_match_data != self.match_data:
            self.last_match_data = self.match_data
            if self.debug_info != "":
                self.debug_info += "  "
            self.debug_info += f'Starting match update on "{match_data}"\n'
        if not self.match_data.startswith(match_string):
            self.debug_info += f'  Current data {match_data} does not start with "{m_string}"\n'
            msg = "Illegal state"
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.match_data = self.match_data[len(match_string):]
        self.last_match_data = self.match_data
        if (self.shortest_unmatched_data is None) or (len(self.match_data) < len(self.shortest_unmatched_data)):
            self.shortest_unmatched_data = self.match_data
        self.debug_info += f'  Removed: "{m_string}", remaining {len(self.match_data)} bytes\n'

    def get_debug_info(self):
        """Get the current debugging information and reset it."""
        while self.debug_info.find("\n\n") != -1:
            self.debug_info = self.debug_info.replace("\n\n", "\n")
        result = self.debug_info
        self.debug_info = ""
        try:
            data = self.shortest_unmatched_data.decode(AminerConfig.ENCODING)
        except UnicodeError:
            data = repr(self.shortest_unmatched_data)
        result += f'  Shortest unmatched data: "{data}"\n'
        return result

    def get_shortest_unmatched_data(self):
        """
        Get the shortest match_data found while updating the internal state.
        This is useful to find out where the parsing process has terminated.
        """
        return self.shortest_unmatched_data
