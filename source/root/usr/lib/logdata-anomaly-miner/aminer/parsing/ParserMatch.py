"""
This module defines a matching parser model element.

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
from aminer.AminerConfig import DEBUG_LOG_NAME
from aminer.parsing.MatchElement import MatchElement
from collections import deque


class ParserMatch:
    """
    Objects of this class store information about a complete model match.
    Unlike the MatchElement, this class also provides fields to store information commonly used when dealing with the match.
    """

    def __init__(self, match_element: MatchElement):
        """
        Initialize the match.
        @param match_element the root MatchElement from the parsing process.
        """
        if not isinstance(match_element, MatchElement):
            msg = "match_element has to be of the type MatchElement."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        self.match_element = match_element
        self.match_dictionary = None

    def get_match_element(self):
        """Return the matching element."""
        return self.match_element

    def get_match_dictionary(self):
        """Return a dictionary of all children matches."""
        if self.match_dictionary is not None:
            return self.match_dictionary
        stack = deque()
        stack.append([self.match_element])
        result_dict = {}
        while stack:
            match_list = stack.pop()
            counter_dict = {}
            for test_match in match_list:
                if test_match.path in counter_dict.keys():
                    counter_dict[test_match.path] = 0
                else:
                    counter_dict[test_match.path] = None
            for test_match in match_list:
                path = test_match.path
                if counter_dict[test_match.path] is not None:
                    path += "/%d" % counter_dict[path]
                    counter_dict[test_match.path] += 1
                result_dict[path] = test_match
                children = test_match.children
                if children is not None:
                    stack.append(children)
        self.match_dictionary = result_dict
        return result_dict

    def __str__(self):
        return "ParserMatch: %s" % (self.match_element.annotate_match("  "))
