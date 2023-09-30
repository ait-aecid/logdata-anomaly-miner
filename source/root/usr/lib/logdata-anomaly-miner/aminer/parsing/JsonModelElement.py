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
from typing import List, Union, Any
from json import JSONDecodeError
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.ModelElementInterface import ModelElementInterface
from aminer.AminerConfig import DEBUG_LOG_NAME


warnings.filterwarnings("ignore", category=DeprecationWarning)
debug_log_prefix = "JsonModelElement: "


def format_float(val):
    """This function formats the float-value and parses the sign and the exponent."""
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
            format_val = format(float(val), f"1.{val.find(exp) - pos_point}E")
            return format_val[:-2] + format_val[-1]
        return format(float(val), f"1.{val.find(exp) - pos_point}E")
    return float(val)


class JsonModelElement(ModelElementInterface):
    """Parse single- or multi-lined JSON data."""

    def __init__(self, element_id: str, key_parser_dict: dict, optional_key_prefix: str = "optional_key_", nullable_key_prefix: str = "+",
                 allow_all_fields: bool = False):
        """
        Initialize the JsonModelElement.
        @param element_id: The ID of the element.
        @param key_parser_dict: A dictionary of all keys with the according parsers. If a key should be optional, the associated parser must
               start with the OptionalMatchModelElement. To allow every key in a JSON object use "key": "ALLOW_ALL". To allow only empty
               arrays - [] - use "key": "EMPTY_ARRAY". To allow only empty objects - {} - use "key": "EMPTY_OBJECT".
               To allow only empty strings - "" - use "key": "EMPTY_STRING". To allow all keys in an object for a parser use
               "ALLOW_ALL_KEYS": parser. To allow only null values use "key": "NULL_OBJECT".
        @param optional_key_prefix: If some key starts with the optional_key_prefix it will be considered optional.
        @param nullable_key_prefix: The value of this key may be null instead of any expected value.
        @param allow_all_fields: Unknown fields are skipped without parsing with any parsing model.
        """
        super().__init__(element_id, key_parser_dict=key_parser_dict, optional_key_prefix=optional_key_prefix,
                         nullable_key_prefix=nullable_key_prefix, allow_all_fields=allow_all_fields)
        self.dec_escapes = False
        self.validate_key_parser_dict(key_parser_dict)

    def validate_key_parser_dict(self, dictionary: dict):
        """Validate the key_parser_dict."""
        for value in dictionary.values():
            if isinstance(value, ModelElementInterface):
                continue
            if isinstance(value, list):
                if len(value) == 0:
                    msg = "lists in key_parser_dict must have at least one entry."
                    logging.getLogger(DEBUG_LOG_NAME).error(msg)
                    raise ValueError(msg)

                for v in value:
                    if isinstance(v, dict):
                        self.validate_key_parser_dict(v)
            elif isinstance(value, dict):
                self.validate_key_parser_dict(value)
            elif value not in ("ALLOW_ALL", "EMPTY_ARRAY", "EMPTY_OBJECT", "EMPTY_STRING", "ALLOW_ALL_KEYS", "NULL_OBJECT"):
                msg = "wrong type found in key_parser_dict."
                logging.getLogger(DEBUG_LOG_NAME).error(msg)
                raise TypeError(msg)

    def is_escaped_unicode(self, text: str):  # skipcq: PYL-R0201
        """Check if the text contains only ascii characters."""
        if all(ord(c) < 128 for c in text):  # is escaped unicode ascii?
            return True
        return False

    def get_full_key(self, key, dictionary):
        """Find the full key in the dictionary."""
        options = [self.optional_key_prefix + self.nullable_key_prefix + key, self.nullable_key_prefix + self.optional_key_prefix + key,
                   self.optional_key_prefix + key, self.nullable_key_prefix + key]
        for option in options:
            if option in dictionary:
                return option
        return key

    def get_stripped_key(self, key):
        """Return the key without optional_key_prefix and nullable_key_prefix."""
        if key.startswith(self.optional_key_prefix):
            key = key[len(self.optional_key_prefix):]
        if key.startswith(self.nullable_key_prefix):
            key = key[len(self.nullable_key_prefix):]
        if key.startswith(self.optional_key_prefix):
            key = key[len(self.optional_key_prefix):]
        return key

    def is_nullable_key(self, key):
        """Check if the key is nullable."""
        return key.startswith(self.nullable_key_prefix) or (
                key.startswith(self.optional_key_prefix) and key[len(self.optional_key_prefix):].startswith(self.nullable_key_prefix))

    def get_match_element(self, path: str, match_context):
        """
        Try to parse all the match_context against JSON.
        When a match is found, the match_context is updated accordingly.
        @param path the model path to the parent model element invoking this method.
        @param match_context an instance of MatchContext class holding the data context to match against.
        @return the matchElement or None if model did not match.
        """
        current_path = f"{path}/{self.element_id}"
        old_match_data = match_context.match_data
        matches: Union[List[Union[MatchElement, None]]] = []
        try:
            index = 0
            # There can be a valid case in which the text contains for example \x2d, \\x2d or \\\\x2d, which basically should be decoded
            # into the unicode form.
            while index != -1:
                index = match_context.match_data.find(rb"\x")
                if index != -1:
                    try:
                        match_context.match_data = match_context.match_data.decode("unicode-escape").encode()
                    except UnicodeDecodeError:
                        break
            index = 0
            while index != -1:
                index = match_context.match_data.find(b"\\", index)
                if index != -1 and len(match_context.match_data) - 1 > index and match_context.match_data[
                        index + 1] not in b"\\'\"abfnrtv/":
                    match_context.match_data = match_context.match_data[:index] + b"\\" + match_context.match_data[index:]
                    index += 2
                elif index != -1:
                    index += 2
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
        remove_chars = [b' ', b'}', b']', b'"', b'\r', b'\n']
        match_data = match_context.match_data
        for c in remove_chars:
            match_data = match_data.replace(c, b"")
        if None in matches or (match_data != b"" and len(matches) > 0):
            logging.getLogger(DEBUG_LOG_NAME).debug(
                debug_log_prefix + "get_match_element_main NONE RETURNED\n" + match_context.match_data.strip(b' }]"\r\n').decode())
            match_context.match_data = old_match_data
            return None
        # remove all remaining spaces and brackets.
        match_context.update(match_context.match_data)
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
            key = self.get_full_key(key, json_dict)
            if key not in json_dict:
                index = match_context.match_data.find(key.encode())
                match_context.update(match_context.match_data[:index])
                logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN [NONE] 2" + key + str(json_dict))
                if "ALLOW_ALL_KEYS" in json_dict.keys():
                    key = "ALLOW_ALL_KEYS"
                elif self.allow_all_fields:
                    index = match_context.match_data.find(key.encode()) + len(key.encode())
                    index += len(match_context.match_data) - len(match_context.match_data[index:].lstrip(b' \n\t:"')) + \
                        len(str(json_match_data[key]))
                    match_context.update(match_context.match_data[:index])
                    if match_context.match_data.replace(b"}", b"").replace(b"]", b"").replace(b'"', b"") == b"":
                        match_context.update(match_context.match_data)
                    continue
                else:
                    return [None]
            value = json_dict[key]
            if isinstance(value, (dict, list)) and (not isinstance(json_match_data, dict) or split_key not in json_match_data):
                logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN [NONE] 3, Key: " + split_key + ", Value: " + repr(value))
                return [None]
            if isinstance(value, dict):
                if json_match_data[split_key] is None and (self.is_nullable_key(key) or json_dict[key] == "NULL_OBJECT"):
                    data = b"null"
                    matches.append(MatchElement(f"{current_path}/{key}", data, data, None))
                    index = match_context.match_data.find(data)
                    if match_context.match_data[index + 4] == 34:  # "
                        index += 1
                    match_context.update(match_context.match_data[:index + len(data)])
                    return matches

                matches += self.parse_json_dict(value, json_match_data[split_key], f"{current_path}/{split_key}", match_context)
                if json_match_data[split_key] == {}:
                    index = match_context.match_data.find(split_key.encode())
                    index = match_context.match_data.find(b"}", index)
                    data = match_context.match_data[:index]
                    match_element = MatchElement(current_path+"/"+key, data, data, None)
                    matches.append(match_element)
                    match_context.update(match_context.match_data[:index])

                if len(matches) == 0 or matches[-1] is None:
                    logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "No match found for key " + split_key)
                    return matches
            elif isinstance(value, list):
                res = self.parse_json_array(json_dict, json_match_data, key, split_key, current_path, matches, match_context, i)
                if res is not None:
                    return res
            elif value == "EMPTY_OBJECT":
                if isinstance(json_match_data[split_key], dict) and len(json_match_data[split_key].keys()) == 0:
                    index = match_context.match_data.find(b"}") + 1
                    data = match_context.match_data[:index]
                    match_element = MatchElement(current_path+"/"+key, data, data, None)
                    matches.append(match_element)
                    match_context.update(data)
                else:
                    logging.getLogger(DEBUG_LOG_NAME).debug(
                        debug_log_prefix + "EMPTY_OBJECT " + split_key + " is not empty. Keys: " + str(json_match_data[split_key].keys()))
                    matches.append(None)
            elif json_dict[key] == "EMPTY_ARRAY":
                if isinstance(json_match_data[split_key], list) and len(json_match_data[split_key]) == 0:
                    index = match_context.match_data.find(b"]") + 1
                    data = match_context.match_data[:index]
                    match_element = MatchElement(current_path+"/"+key, data, data, None)
                    matches.append(match_element)
                    match_context.update(data)
                else:
                    logging.getLogger(DEBUG_LOG_NAME).debug(
                        debug_log_prefix + "EMPTY_ARRAY " + split_key + " is not empty. Data: " + str(json_match_data[split_key]))
                    matches.append(None)
            else:
                if key != split_key and split_key not in json_match_data:
                    logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + f"Optional Key {key} not found in json_match_data")
                    continue
                if split_key not in json_match_data:
                    logging.getLogger(DEBUG_LOG_NAME).debug(
                        debug_log_prefix + f"Key {split_key} not found in json_match_data. RETURN [NONE] 4")
                    return [None]
                match_element, index, data = self.parse_json_object(
                    json_dict, json_match_data, key, split_key, current_path, match_context)
                matches.append(match_element)
                if index == -1 and match_element is None:
                    backslash = b"\\"
                    logging.getLogger(DEBUG_LOG_NAME).debug(
                        debug_log_prefix + f"Necessary element did not match! Key: {key}, MatchElement: {match_element}, Data: "
                                           f"{data.decode()}, IsFloat {isinstance(json_match_data[split_key], float)}, Index: {index}, "
                                           f"MatchContext: {match_context.match_data.replace(backslash, b'').decode()}")
                    return matches
                match_context.update(match_context.match_data[:index + len(data)])
        missing_keys = [x for x in json_dict if self.get_stripped_key(x) not in json_match_data and x != "ALLOW_ALL_KEYS" and
                        not (x.startswith(self.optional_key_prefix) or x.startswith(self.nullable_key_prefix + self.optional_key_prefix))]
        for key in missing_keys:
            logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "Missing Key: " + key)
            return [None]
        return matches

    def check_keys(self, json_dict, json_match_data, match_context):
        """Check if no keys are missing and if the value types match."""
        if "ALLOW_ALL_KEYS" in json_dict.keys():
            return True
        if json_match_data is None:
            return False
        missing_keys = [x for x in json_dict if self.get_stripped_key(x) not in json_match_data and not (x.startswith(
            self.optional_key_prefix) or x.startswith(self.nullable_key_prefix + self.optional_key_prefix))]
        for key in missing_keys:
            if (not key.startswith(self.nullable_key_prefix) or (
                    key.startswith(self.nullable_key_prefix) and key[len(self.nullable_key_prefix):] not in json_match_data)):
                index = match_context.match_data.find(key.encode())
                match_context.update(match_context.match_data[:index])
                logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN [NONE] 1. Key: " + key)
                return False
        for key in json_dict.keys():
            k = self.get_stripped_key(key)
            if not isinstance(json_match_data, dict) or (k in json_match_data and isinstance(json_match_data[k], list) and not isinstance(
                    json_dict[key], list) and json_dict[key] != "EMPTY_ARRAY"):
                index = match_context.match_data.find(key.encode())
                match_context.update(match_context.match_data[:index])
                logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN [NONE] 5. Key: " + key)
                return False
        return True

    def flatten_list(self, lst: list):
        """Flatten a list of lists using this method recursively."""
        if not isinstance(lst, list):
            return None
        res: List[Any] = []
        for val in lst:
            if isinstance(val, list):
                res += self.flatten_list(val)
            else:
                res.append(val)
        return res

    def parse_json_array(self, json_dict: dict, json_match_data: dict, key: str, split_key: str, current_path: str, matches: list,
                         match_context, i: int):
        """Parse an array in a json object."""
        if self.is_nullable_key(key) and json_match_data[split_key] is None:
            return None
        if not isinstance(json_match_data[split_key], list):
            if key.startswith(self.optional_key_prefix) and json_match_data[split_key] is None:
                data = b"null"
                index = match_context.match_data.find(split_key.encode() + b'":') + len(split_key.encode() + b'":')
                index += match_context.match_data[index:].find(b"null") + len(b"null")
                match_context.update(match_context.match_data[:index])
                matches.append(MatchElement(f"{current_path}/{key}", data, data, None))
                return matches
            logging.getLogger(DEBUG_LOG_NAME).debug(
                debug_log_prefix + "Key " + split_key + " is no array. Data: " + str(json_match_data[split_key]))
            return [None]
        search_string = b"]"
        match_array = self.flatten_list(json_match_data[split_key])
        value = self.flatten_list(json_dict[key])
        for j, data in enumerate(match_array):
            for k, val in enumerate(value):
                if isinstance(data, str):
                    enc = "utf-8"
                    if self.is_escaped_unicode(data) and self.dec_escapes:
                        enc = "unicode-escape"
                    data = data.encode(enc)
                if data is None:
                    data = b"null"
                elif not isinstance(data, bytes):
                    data = str(data).encode()
                if isinstance(val, dict):  # skipcq: PYL-R1723
                    matches += self.parse_json_dict(val, match_array[j], f"{current_path}/{split_key}", match_context)
                    if matches[-1] is None:
                        if len(value) - 1 == k:
                            logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "No match found for key " + split_key)
                            return matches
                        del matches[-1]
                        continue
                    break
                else:
                    if val == "ALLOW_ALL":
                        logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "ALLOW_ALL (ARRAY)")
                        match_element = MatchElement(current_path+"/"+key, data, data, None)
                    elif json_dict[key] == "EMPTY_ARRAY":
                        if isinstance(data, list) and len(data) == 0:
                            index = match_context.match_data.find(search_string)
                            data = match_context.match_data[:index]
                            match_element = MatchElement(
                                current_path+"/"+key, data, data, None)
                            match_context.update(data)
                        else:
                            logging.getLogger(DEBUG_LOG_NAME).debug(
                                debug_log_prefix + "EMPTY_ARRAY " + split_key + " is not empty. Data: " + json_match_data[split_key])
                            return None
                    else:
                        match_element = val.get_match_element(current_path, MatchContext(data))
                        if match_element is not None and len(match_element.match_string) != len(data):
                            logging.getLogger(DEBUG_LOG_NAME).debug(
                                debug_log_prefix + "MatchElement NONE 1. match_string: " + match_element.match_string.decode() +
                                ", data: " + data.decode())
                            match_element = None
                    index = match_context.match_data.find(data)
                    if match_element is None:
                        logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "MatchElement NONE 2. Data: " + data.decode())
                        index = -1
                    match_context.update(match_context.match_data[:index + len(data)])
                    if index == -1 and val == "ALLOW_ALL":
                        logging.getLogger(DEBUG_LOG_NAME).debug(
                            debug_log_prefix + "ALLOW_ALL (ARRAY-ELEMENT). Data: " + match_context.match_data.decode())
                        index = match_context.match_data.find(search_string)
                        match_context.update(match_context.match_data[:index])
                    if match_element is not None or (match_element is None and not key.startswith(self.optional_key_prefix)):
                        matches.append(match_element)
                        if index == -1:
                            if len(value) - 1 == k:
                                return matches
                            del matches[-1]
                            continue
                    if len(matches) == 0:
                        return [None]
                    if matches[-1] is None:
                        if len(value) - 1 == k:
                            logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN MATCHES 3")
                            return matches
                        del matches[-1]
                        continue
        if len(json_match_data.keys()) > i + 1:
            match_context.update(match_context.match_data[:match_context.match_data.find(list(json_match_data.keys())[i + 1].encode())])
        else:
            match_context.update(match_context.match_data[:match_context.match_data.find(search_string) + len(search_string)])
        return None

    def parse_json_object(self, json_dict, json_match_data, key, split_key, current_path, match_context):  # skipcq: PYL-R0201
        """Parse a literal from the json object."""
        current_path += "/" + key
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
            if self.is_nullable_key(key) or json_dict[key] == "NULL_OBJECT":
                start = 0
                if "null" in key:
                    start = match_context.match_data.find(data) + 4
                index = match_context.match_data.find(data, start)
                if match_context.match_data[index + 4] == 34:
                    index += 1
                return MatchElement(current_path, data, data, None), index, data
            return None, -1, data
        elif not isinstance(data, bytes):
            data = str(data).encode()
        if json_dict[key] == "ALLOW_ALL":
            logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "ALLOW_ALL (DICT)\n" + data.decode())
            match_element = MatchElement(current_path, data, data, None)
            last_bracket = match_context.match_data.find(b"}", len(data))
            while match_context.match_data.count(b"{", 0, last_bracket) - match_context.match_data.count(b"}", 0, last_bracket) > 0:
                last_bracket = match_context.match_data.find(b"}", last_bracket) + 1
            index = last_bracket - len(data)
        elif json_dict[key] == "EMPTY_STRING":
            if data == b"":
                match_element = MatchElement(current_path, data, data, None)
                index = match_context.match_data.find(split_key.encode()) + len(split_key)
                index += match_context.match_data[index:].find(b'""') + len(b'""')
            else:
                match_element = None
                index = -1
        else:
            match_element = json_dict[key].get_match_element(current_path, MatchContext(data))
            if match_element is not None and len(match_element.match_string) != len(data) and (
                    not isinstance(match_element.match_object, bytes) or len(match_element.match_object) != len(data)):
                logging.getLogger(DEBUG_LOG_NAME).debug(
                    debug_log_prefix + f"Data length not matching! match_string: {len(match_element.match_string)}, data: {len(data)},"
                                       f" data: {data.decode()}")
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
