"""
This module defines a writer that forwards match information to a stream.

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

from aminer.AnalysisChild import AnalysisContext
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface
import _io


class MatchValueStreamWriter(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """
    This class extracts values from a given match and writes them to a stream.
    This can be used to forward these values to another program (when stream is a wrapped network socket) or to a file for further analysis.
    A stream is used instead of a file descriptor to increase performance. To flush it from time to time, add the writer object also to the
    time trigger list.
    """

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, stream, target_path_list, separator, missing_value_string):
        """
        Initialize the writer.
        @param stream the stream on which the match results are written.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that all values occurring in these paths are
               considered for value range generation.
        @param separator a string to be added between match values in the output stream.
        @param missing_value_string a string which is added if no match was found.
        """
        # avoid "defined outside init" issue
        self.log_success, self.log_total = [None]*2
        super().__init__(stream=stream, target_path_list=target_path_list, separator=separator, missing_value_string=missing_value_string)
        if self.target_path_list is None:
            raise TypeError("target_path_list must not be None.")

    def receive_atom(self, log_atom):
        """Forward match value information to the stream."""
        self.log_total += 1
        match_dict = log_atom.parser_match.get_match_dictionary()
        add_sep_flag = False
        contains_data = False
        result = b""
        for i, path in enumerate(self.target_path_list):
            if add_sep_flag:
                result += self.separator
            match = match_dict.get(path)
            if match is None:
                result += self.missing_value_string
            else:
                matches = []
                cnt = self.target_path_list.count(path)
                if isinstance(match, list):
                    if cnt > 1:
                        index = [j for j, x in enumerate(self.target_path_list) if x == path].index(i)
                        if index < [x.path for x in match if x.path == path].count(path) and index < len(match):
                            matches.append(match[index])
                        else:
                            matches.append(None)
                    else:
                        matches += match
                elif cnt > 1 and i > self.target_path_list.index(path):
                    matches.append(None)
                else:
                    matches.append(match)
                for match in matches:
                    if match is None:
                        result += self.missing_value_string + self.separator
                    else:
                        result += match.match_string + self.separator
                        contains_data = True
                if len(self.separator) > 0:
                    result = result[:-len(self.separator)]
            add_sep_flag = True
        if contains_data:
            if not isinstance(self.stream, _io.BytesIO):
                self.stream.write(result.decode("ascii", "ignore"))
                self.stream.write("\n")
            else:
                self.stream.write(result)
                self.stream.write(b"\n")
            self.log_success += 1

    def do_timer(self, _trigger_time):
        """Flush the timer."""
        self.stream.flush()
        return 10

    def do_persist(self):
        """Flush the timer."""
        self.stream.flush()
