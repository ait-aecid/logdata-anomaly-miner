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
import warnings
import logging
from typing import List, Union
from json import JSONDecodeError
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.ModelElementInterface import ModelElementInterface
from aminer.AminerConfig import DEBUG_LOG_NAME


warnings.filterwarnings("ignore", category=DeprecationWarning)
debug_log_prefix = "JsonModelElement: "


def format_float(val):
    exp = None
    if "e" in val:
        exp = "e"
    elif "E" in val:
        exp = "E"
    if "+" in val:
        sign = "+"
    else:
        sign = "-"
    if exp is not None:
        pos_point = val.find(exp)
        if "." in val:
            pos_point = val.find(".")
        if len(val) - val.find(sign) <= 2:
            result = format(float(val), "1.%dE" % (val.find(exp) - pos_point))[:-2]
            result += format(float(val), "1.%dE" % (val.find(exp) - pos_point))[-1]
            return result
        return format(float(val), "1.%dE" % (val.find(exp) - pos_point))
    return float(val)


class JsonModelElement(ModelElementInterface):
    """Parse single- or multi-lined JSON data."""

    def __init__(self, element_id: str, key_parser_dict: dict, optional_key_prefix: str = "optional_key_"):
        """
        Initialize the JsonModelElement.
        @param element_id: The ID of the element.
        @param key_parser_dict: A dictionary of all keys with the according parsers. If a key should be optional, the associated parser must
            start with the OptionalMatchModelElement. To allow every key in a JSON object use "key": "ALLOW_ALL". To allow only empty arrays
            - [] - use "key": "EMPTY_LIST". To allow only empty objects - {} - use "key": "EMPTY_OBJECT".
        @param optional_key_prefix: If some key starts with the optional_key_prefix it will be considered optional.
        """
        if not isinstance(element_id, str):
            msg = "element_id has to be of the type string."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if len(element_id) < 1:
            msg = "element_id must not be empty."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.element_id = element_id

        if not isinstance(key_parser_dict, dict):
            msg = "key_parser_dict has to be of the type dict."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        self.children: List[dict] = []
        self.find_children_in_dict(key_parser_dict, self.children)
        self.key_parser_dict = key_parser_dict

        if not isinstance(optional_key_prefix, str):
            msg = "optional_key_prefix has to be of the type string."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if len(optional_key_prefix) < 1:
            msg = "element_id must not be empty."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.optional_key_prefix = optional_key_prefix
        self.dec_escapes = False

    def get_id(self):
        """Get the element ID."""
        return self.element_id

    def get_child_elements(self):
        """Return all model elements of the sequence."""
        return self.children

    def find_children_in_dict(self, dictionary: dict, children: list):
        """Find all children and append them to the children list."""
        for value in dictionary.values():
            if isinstance(value, ModelElementInterface):
                children.append(value)
            elif isinstance(value, list):
                if len(value) != 1:
                    msg = "lists in key_parser_dict must have exactly one entry."
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)
                value_list: List[dict] = []
                for v in value:
                    if isinstance(v, dict):
                        self.find_children_in_dict(v, value_list)
                    else:
                        value_list.append(v)
                children.append(value_list)
            elif isinstance(value, dict):
                self.find_children_in_dict(value, children)
            elif value not in ("ALLOW_ALL", "EMPTY_LIST", "EMPTY_OBJECT"):
                msg = "wrong type found in key_parser_dict."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)

    def is_escaped_unicode(self, text: str):  # skipcq: PYL-R0201
        """Check if the text contains only ascii characters."""
        if all(ord(c) < 128 for c in text):  # is escaped unicode ascii?
            return True
        return False

    def get_match_element(self, path: str, match_context):
        """
        Try to parse all of the match_context against JSON.
        When a match is found, the match_context is updated accordingly.
        @param path the model path to the parent model element invoking this method.
        @param match_context an instance of MatchContext class holding the data context to match against.
        @return the matchElement or None if model did not match.
        """
        current_path = "%s/%s" % (path, self.element_id)
        old_match_data = match_context.match_data
        matches: Union[List[Union[MatchElement, None]]] = []
        try:
            json_match_data = json.loads(match_context.match_data, parse_float=format_float)
            if not isinstance(json_match_data, dict):
                return None
        except JSONDecodeError as e:
            logging.getLogger(debug_log_prefix + DEBUG_LOG_NAME).debug(e)
            return None
        self.dec_escapes = True
        if self.is_escaped_unicode(match_context.match_data.decode()):
            match_context.match_data = match_context.match_data.decode("unicode-escape").encode()
            self.dec_escapes = False
        matches += self.parse_json_dict(self.key_parser_dict, json_match_data, current_path, match_context)
        remove_chars = b' }]"\r\n'
        match_data = match_context.match_data
        for c in remove_chars:
            match_data = match_data.replace(bytes(chr(c), encoding="utf-8"), b"")
        if None in matches or (match_data != b"" and len(matches) > 0):
            logging.getLogger(DEBUG_LOG_NAME).debug(
                debug_log_prefix + "get_match_element_main NONE RETURNED", match_context.match_data.strip(b' }]"\r\n').decode())
            match_context.match_data = old_match_data
            return None
        # remove all remaining spaces and brackets.
        match_context.match_data = b""
        if len(matches) == 0:
            resulting_matches = None
        else:
            resulting_matches = matches
        return MatchElement(current_path, str(json_match_data).encode(), json_match_data, resulting_matches)

    def parse_json_dict(self, json_dict: dict, json_match_data: dict, current_path: str, match_context):
        """Parse a json dictionary."""
        matches: List[Union[MatchElement, None]] = []
        if not self.check_keys(json_dict, json_match_data, match_context):
            return [None]

        for i, key in enumerate(json_match_data.keys()):
            split_key = key
            if self.optional_key_prefix + key in json_dict:
                key = self.optional_key_prefix + key
            if key not in json_dict:
                index = match_context.match_data.find(key.encode())
                match_context.update(match_context.match_data[:index])
                logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN [NONE] 2", key, json_dict)
                return [None]
            value = json_dict[key]
            if isinstance(value, (dict, list)) and (not isinstance(json_match_data, dict) or split_key not in json_match_data):
                logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN [NONE] 3")
                return [None]
            if isinstance(value, dict):
                matches += self.parse_json_dict(value, json_match_data[split_key], "%s/%s" % (current_path, split_key), match_context)
                if len(matches) == 0 or matches[-1] is None:
                    logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN MATCHES 1")
                    return matches
            elif isinstance(value, list):
                res = self.parse_json_list(json_dict, json_match_data, key, split_key, current_path, matches, match_context, i)
                if res is not None:
                    return res
            elif value == "EMPTY_OBJECT":
                if isinstance(json_match_data[split_key], dict) and len(json_match_data[split_key].keys()) == 0:
                    index = match_context.match_data.find(b"}") + 1
                    match_element = MatchElement(current_path, match_context.match_data[:index], match_context.match_data[:index], None)
                    matches.append(match_element)
                    match_context.update(match_context.match_data[:index])
                else:
                    matches.append(None)
            elif json_dict[key] == "EMPTY_LIST":
                if isinstance(json_match_data[split_key], list) and len(json_match_data[split_key]) == 0:
                    index = match_context.match_data.find(b"]") + 1
                    match_element = MatchElement(current_path, match_context.match_data[:index], match_context.match_data[:index], None)
                    matches.append(match_element)
                    match_context.update(match_context.match_data[:index])
                else:
                    matches.append(None)
            else:
                if key != split_key and split_key not in json_match_data:
                    logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "Optional Key %s not found in json_match_data" % key)
                    continue
                if split_key not in json_match_data:
                    logging.getLogger(DEBUG_LOG_NAME).debug(
                        debug_log_prefix + "Key %s not found in json_match_data. RETURN [NONE] 4" % split_key)
                    return [None]
                match_element, index, data = self.parse_json_object(
                    json_dict, json_match_data, key, split_key, current_path, match_context)
                if match_element is not None or (match_element is None and not key.startswith(self.optional_key_prefix)):
                    matches.append(match_element)
                    if index == -1 and match_element is None:
                        logging.getLogger(DEBUG_LOG_NAME).debug(
                            debug_log_prefix +
                            "Necessary element did not match! MatchElement: %s\nData: %s\nMatchContext: %s\nIsFloat %s, Index: %d" % (
                                match_element, data.decode(), match_context.match_data.replace(b"\\", b"").decode(),
                                isinstance(json_match_data[split_key], float), index))
                        return matches
                match_context.update(match_context.match_data[:index + len(data)])
        missing_keys = [x for x in json_dict if x not in json_match_data]
        for key in missing_keys:
            if not key.startswith(self.optional_key_prefix):
                logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "Missing Key:", key)
                return [None]
        return matches

    def check_keys(self, json_dict, json_match_data, match_context):
        """Check if no keys are missing and if the value types match."""
        missing_keys = [x for x in json_dict if x not in json_match_data]
        for key in missing_keys:
            if not key.startswith(self.optional_key_prefix):
                index = match_context.match_data.find(key.encode())
                match_context.update(match_context.match_data[:index])
                logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN [NONE] 1", key)
                return False
        for key in json_dict.keys():
            k = key
            if key.startswith(self.optional_key_prefix):
                k = key.replace(self.optional_key_prefix, "")
            if k in json_match_data and isinstance(json_match_data[k], list) and not isinstance(json_dict[key], list) and json_dict[
                    key] != "EMPTY_LIST":
                index = match_context.match_data.find(key.encode())
                match_context.update(match_context.match_data[:index])
                logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN [NONE] 5", key)
                return False
        return True

    def parse_json_list(self, json_dict, json_match_data, key, split_key, current_path, matches, match_context, i):
        """Parse a list in a json object."""
        for data in json_match_data[split_key]:
            if isinstance(data, str):
                enc = "utf-8"
                if self.is_escaped_unicode(data) and self.dec_escapes:
                    enc = "unicode-escape"
                data = data.encode(enc)
            if data is None:
                data = b"null"
            elif not isinstance(data, bytes):
                data = str(data).encode()
            if isinstance(json_dict[key][0], dict):
                for match_data in json_match_data[split_key]:
                    matches += self.parse_json_dict(
                        json_dict[key][0], match_data, "%s/%s" % (current_path, split_key), match_context)
                    if matches[-1] is None:
                        logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN MATCHES 2")
                        return matches
            else:
                if json_dict[key][0] == "ALLOW_ALL":
                    logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "ALLOW_ALL (LIST)")
                    match_element = MatchElement(current_path, data, data, None)
                elif json_dict[key] == "EMPTY_LIST":
                    if isinstance(data, list) and len(data) == 0:
                        index = match_context.match_data.find(b"]")
                        match_element = MatchElement(current_path, match_context.match_data[:index], match_context.match_data[:index], None)
                        match_context.update(match_context.match_data[:index])
                    else:
                        return None
                else:
                    match_element = json_dict[key][0].get_match_element(current_path, MatchContext(data))
                    if match_element is not None and len(match_element.match_string) != len(data):
                        logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "MatchElement NONE 1")
                        match_element = None
                index = match_context.match_data.find(data)
                if match_element is None:
                    logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "MatchElement NONE 2", data.decode())
                    index = -1
                match_context.update(match_context.match_data[:index + len(data)])
                if index == -1 and json_dict[key][0] == "ALLOW_ALL":
                    logging.getLogger(DEBUG_LOG_NAME).debug(
                        debug_log_prefix + "ALLOW_ALL (LIST-ELEMENT)", match_context.match_data.decode())
                    index = match_context.match_data.find(b"]")
                    match_context.update(match_context.match_data[:index])
                if match_element is not None or (match_element is None and not key.startswith(self.optional_key_prefix)):
                    matches.append(match_element)
                    if index == -1:
                        return matches
                if matches[-1] is None:
                    logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN MATCHES 3")
                    return matches
        if len(json_match_data.keys()) > i + 1:
            logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "LIST - Searching next key")
            match_context.update(match_context.match_data[:match_context.match_data.find(
                list(json_match_data.keys())[i + 1].encode())])
        else:
            logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "LIST - No more keys found")
            match_context.update(match_context.match_data[:match_context.match_data.find(b"]")])
        return None

    def parse_json_object(self, json_dict, json_match_data, key, split_key, current_path, match_context):  # skipcq: PYL-R0201
        """Parse a literal from the json object."""
        data = json_match_data[split_key]
        enc = "utf-8"
        if isinstance(data, str):
            if self.is_escaped_unicode(data) and self.dec_escapes:
                enc = "unicode-escape"
            data = data.encode(enc)
        elif isinstance(data, bool):
            data = str(data).replace("T", "t").replace("F", "f").encode()
        elif data is None:
            data = b"null"
        elif not isinstance(data, bytes):
            data = str(data).encode()
        if json_dict[key] == "ALLOW_ALL":
            logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "ALLOW_ALL (DICT)", data.decode())
            match_element = MatchElement(current_path, data, data, None)
            last_bracket = match_context.match_data.find(b"}", len(data))
            while match_context.match_data.count(b"{", 0, last_bracket) - match_context.match_data.count(b"}", 0, last_bracket) > 0:
                last_bracket = match_context.match_data.find(b"}", last_bracket) + 1
            index = last_bracket - len(data)
        else:
            match_element = json_dict[key].get_match_element(current_path, MatchContext(data))
            if match_element is not None and len(match_element.match_string) != len(data) and (
                    not isinstance(match_element.match_object, bytes) or len(match_element.match_object) != len(data)):
                logging.getLogger(DEBUG_LOG_NAME).debug(
                    debug_log_prefix + "Data length not matching! match_string: %d, data: %d, data: %s" % (
                        len(match_element.match_string), len(data), data.decode()))
                match_element = None
            index = max([match_context.match_data.replace(b"\\", b"").find(split_key.encode()),
                         match_context.match_data.find(split_key.encode()), match_context.match_data.decode().find(split_key)])
            index += match_context.match_data[index:].find(split_key.encode() + b'":') + len(split_key.encode() + b'":')
            try:
                index += max([match_context.match_data.replace(b"\\", b"")[index:].find(data), match_context.match_data[index:].find(data),
                              match_context.match_data.decode(enc)[index:].find(data.decode(enc))])
            except UnicodeDecodeError:
                index += max([match_context.match_data.replace(b"\\", b"")[index:].find(data), match_context.match_data[index:].find(data),
                              match_context.match_data.decode()[index:].find(data.decode())])
            index += len(match_context.match_data[index:]) - len(match_context.match_data[index:].lstrip(b" \r\t\n"))
            if match_context.match_data[index:].find(b'"') == 0:
                index += len(b'"')
            # for example float scientific representation is converted to normal float..
            if index == -1 and match_element is not None and isinstance(json_match_data[split_key], float):
                indices = [match_context.match_data.find(b",", len(match_element.match_string) // 3),
                           match_context.match_data.find(b"]"), match_context.match_data.find(b"}")]
                indices = [x for x in indices if x >= 0]
                index = min(indices)
            if match_element is None:
                index = -1
        return match_element, index, data
