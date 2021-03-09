"""
This module defines a model element that takes any string up to a specific delimiter string.

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
from json import JSONDecodeError
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.ModelElementInterface import ModelElementInterface


class JsonModelElement(ModelElementInterface):
    """Parse single- or multi-lined JSON data."""

    def __init__(self, element_id, key_parser_dict, optional_key_prefix='optional_key_'):
        """
        Initialize the JsonModelElement.
        @param element_id: The ID of the element.
        @param key_parser_dict: A dictionary of all keys with the according parsers. If a key should be optional, the associated parser must
            start with the OptionalMatchModelElement. To allow every key in a JSON object use "key": "ALLOW_ALL".
        @param optional_key_prefix: If some key starts with the optional_key_prefix it will be considered optional.
        """
        self.element_id = element_id
        self.key_parser_dict = key_parser_dict
        self.optional_key_prefix = optional_key_prefix

    def get_id(self):
        """Get the element ID."""
        return self.element_id

    def get_child_elements(self):
        """Return all model elements of the sequence."""
        return self.key_parser_dict

    def get_match_element(self, path, match_context):
        """
        Try to parse all of the match_context against JSON.
        When a match is found, the match_context is updated accordingly.
        @param path the model path to the parent model element invoking this method.
        @param match_context an instance of MatchContext class holding the data context to match against.
        @return the matchElement or None if model did not match.
        """
        current_path = "%s/%s" % (path, self.element_id)
        old_match_data = match_context.match_data
        matches = []
        try:
            json_match_data = json.loads(match_context.match_data)
        except JSONDecodeError:
            return None
        matches += self.parse_json_dict(self.key_parser_dict, json_match_data, current_path, match_context)
        if None in matches:
            match_context.match_data = old_match_data
            return None
        # remove all remaining spaces and brackets.
        match_context.match_data = b''
        return MatchElement(current_path, str(json_match_data), json_match_data, matches)

    def parse_json_dict(self, json_dict, json_match_data, current_path, match_context):
        """Parse a json dictionary."""
        matches = []
        missing_keys = [x for x in json_dict if x not in json_match_data]
        for key in missing_keys:
            if not key.startswith(self.optional_key_prefix):
                index = match_context.match_data.find(key.encode())
                match_context.update(match_context.match_data[:index])
                return [None]
        for key in json_match_data.keys():
            if self.optional_key_prefix + key in json_dict:
                key = self.optional_key_prefix + key
            if key not in json_dict:
                index = match_context.match_data.find(key.encode())
                match_context.update(match_context.match_data[:index])
                return [None]
            value = json_dict[key]
            if isinstance(value, (dict, list)) and (not isinstance(json_match_data, dict) or key not in json_match_data):
                return [None]
            if isinstance(value, dict):
                matches += self.parse_json_dict(value, json_match_data[key], "%s/%s" % (current_path, key), match_context)
                if matches[-1] is None:
                    return matches
            elif isinstance(value, list):
                for json_object in json_match_data[key]:
                    matches += self.parse_json_dict(value[0], json_object, "%s/%s" % (current_path, key), match_context)
                    if matches[-1] is None:
                        return matches
            else:
                split_data = key.split(self.optional_key_prefix, 1)
                if len(split_data) != 1 and split_data[-1] not in json_match_data:
                    continue
                if split_data[-1] not in json_match_data:
                    return [None]
                data = json_match_data[split_data[-1]]
                if isinstance(data, str):
                    data = data.encode()
                elif not isinstance(data, bytes):
                    data = str(data).encode()
                if json_dict[key] == "ALLOW_ALL":
                    match_element = MatchElement(current_path, str(data), data, None)
                else:
                    match_element = json_dict[key].get_match_element(current_path, MatchContext(data))
                    if match_element is not None and len(match_element.match_string) != len(data):
                        match_element = None
                index = match_context.match_data.find(data)
                if match_element is None:
                    index = 0
                match_context.update(match_context.match_data[:index + len(data)])
                if match_element is not None or (match_element is None and not key.startswith(self.optional_key_prefix)):
                    matches.append(match_element)
                    if index == 0:
                        return matches
        missing_keys = [x for x in json_dict if x not in json_match_data]
        for key in missing_keys:
            if not key.startswith(self.optional_key_prefix):
                return [None]
        return matches
