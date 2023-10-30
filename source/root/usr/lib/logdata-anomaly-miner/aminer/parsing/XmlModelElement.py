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
import warnings
import logging
import defusedxml.ElementTree as xml
from typing import List, Union, Any
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.ModelElementInterface import ModelElementInterface
from aminer.AminerConfig import DEBUG_LOG_NAME


warnings.filterwarnings("ignore", category=DeprecationWarning)
debug_log_prefix = "XmlModelElement: "


def decode_xml(xml_string, obj=None, attribute_prefix="+"):
    """Decode xml data from a string recursively."""
    children = [elem.tag for elem in xml_string]
    if obj is None and len(children) > 0:
        obj = {}
        obj[xml_string.tag] = [{children[0]: decode_xml(elem, obj)} for elem in xml_string]
        return obj
    if len(children) > 0:
        res = {}
        for key, value in xml_string.attrib.items():
            res[attribute_prefix + key] = value
        for elem in xml_string:
            res[elem.tag] = decode_xml(elem, obj)
        return res
    return xml_string.text


class XmlModelElement(ModelElementInterface):
    """Parse single- or multi-lined XML data."""

    def __init__(self, element_id: str, key_parser_dict: dict, attribute_prefix: str = "+", optional_attribute_prefix: str = "_",
                 empty_allowed_prefix: str = "?", xml_header_expected: bool = False):
        """
        Initialize the XmlModelElement.
        @param element_id: The ID of the element.
        @param key_parser_dict: A dictionary of all keys with the according parsers (excluding the root element). If an attribute should be
               optional, the associated key must start with the optional_attribute_prefix. To allow every child element in a XML document
               use "key": "ALLOW_ALL". To allow empty elements the key must start with empty_allowed_prefix.
        @param attribute_prefix: This prefix indicates that the element is an attribute of the previous element.
        @param optional_attribute_prefix: If some attribute starts with this prefix it will be considered optional.
        @param empty_allowed_prefix: If an element starts with this prefix, it may be empty.
        @param xml_header_expected: True if the xml header is expected.
        """
        super().__init__(element_id, key_parser_dict=key_parser_dict, attribute_prefix=attribute_prefix,
                         optional_attribute_prefix=optional_attribute_prefix, empty_allowed_prefix=empty_allowed_prefix,
                         xml_header_expected=xml_header_expected)
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
            elif value != "ALLOW_ALL":
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
        test_key = key.lstrip(self.attribute_prefix)
        options = [self.attribute_prefix + self.optional_attribute_prefix + test_key,
                   self.optional_attribute_prefix + self.attribute_prefix + test_key,
                   self.attribute_prefix + test_key, self.empty_allowed_prefix + test_key]
        for option in options:
            if option in dictionary:
                return option
        return key

    def get_stripped_key(self, key):
        """Return the key without optional_key_prefix and nullable_key_prefix."""
        if key.startswith(self.optional_attribute_prefix):
            key = key[len(self.optional_attribute_prefix):]
        if key.startswith(self.attribute_prefix + self.optional_attribute_prefix):
            key = self.attribute_prefix + key[len(self.attribute_prefix + self.optional_attribute_prefix):]
        if key.startswith(self.empty_allowed_prefix):
            key = key[len(self.empty_allowed_prefix):]
        return key

    def is_nullable_key(self, key):
        """Check if the key is nullable."""
        return key.startswith(self.empty_allowed_prefix) or (
                key.startswith(self.optional_attribute_prefix)
                and key[len(self.optional_attribute_prefix):].startswith(self.attribute_prefix)) or (
                key.startswith(self.attribute_prefix)
                and key[len(self.attribute_prefix):].startswith(self.optional_attribute_prefix))

    def get_match_element(self, path: str, match_context):
        """
        Try to parse all the match_context against XML.
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
            xml_string = match_context.match_data
            xml_match_data = decode_xml(xml.fromstring(xml_string))
            if xml_string.startswith(b"<?xml "):
                xml_string = xml_string.split(b"?>", 1)[1]
            if not isinstance(xml_match_data, dict):
                return None
        except xml.ParseError as e:
            logging.getLogger(debug_log_prefix + DEBUG_LOG_NAME).debug(e)
            return None
        self.dec_escapes = True
        if self.is_escaped_unicode(match_context.match_data.decode()):
            match_context.match_data = match_context.match_data.decode("unicode-escape").encode()
            self.dec_escapes = False
        matches += self.parse_dict(self.key_parser_dict, xml_match_data, current_path, match_context)
        remove_chars = b' \r\n'
        match_data = match_context.match_data
        for c in remove_chars:
            match_data = match_data.replace(bytes(chr(c), encoding="utf-8"), b"")
        if None in matches or (match_data != b"" and len(matches) > 0):
            logging.getLogger(DEBUG_LOG_NAME).debug(
                debug_log_prefix + "get_match_element_main NONE RETURNED\n" + match_context.match_data.decode())
            match_context.match_data = old_match_data
            return None
        # remove all remaining spaces and brackets.
        match_context.update(match_context.match_data)
        if len(matches) == 0:
            resulting_matches = None
        else:
            resulting_matches = matches
        return MatchElement(current_path, xml_string, xml_match_data, resulting_matches)  # type: ignore[arg-type]

    def parse_dict(self, xml_dict: dict, xml_match_data: dict, current_path: str, match_context):
        """Parse a dictionary."""
        matches: List[Union[MatchElement, None]] = []
        if not self.check_keys(xml_dict, xml_match_data, match_context):
            return [None]
        for i, key in enumerate(xml_match_data.keys()):
            split_key = key
            key = self.get_full_key(key, xml_dict)
            if key not in xml_dict:
                index = match_context.match_data.find(key.encode())
                match_context.update(match_context.match_data[:index])
                logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN [NONE] 2" + key + str(xml_dict))
                return [None]
            value = xml_dict[key]
            if isinstance(value, (dict, list)) and (not isinstance(xml_match_data, dict) or split_key not in xml_match_data):
                logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN [NONE] 3, Key: " + split_key + ", Value: " + repr(value))
                return [None]
            if isinstance(value, dict):
                if xml_match_data[split_key] is None and self.is_nullable_key(key):
                    data = b"null"
                    matches.append(MatchElement(f"{current_path}/{key}", data, data, None))
                    index = match_context.match_data.find(data)
                    if match_context.match_data[index + 4] == 34:  # "
                        index += 1
                    match_context.update(match_context.match_data[:index + len(data)])
                    return matches

                matches += self.parse_dict(value, xml_match_data[split_key], f"{current_path}/{split_key}", match_context)
                if xml_match_data[split_key] == {}:
                    index = match_context.match_data.find(split_key.encode())
                    match_element = MatchElement(
                        current_path+"/"+key, match_context.match_data[:index], match_context.match_data[:index], None)
                    matches.append(match_element)
                    match_context.update(match_context.match_data[:index])

                if len(matches) == 0 or matches[-1] is None:
                    logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "No match found for key " + split_key)
                    return matches
            elif isinstance(value, list):
                res = self.parse_array(xml_dict, xml_match_data, key, split_key, current_path, matches, match_context, i)
                if res is not None:
                    return res
            else:
                if key != split_key and split_key not in xml_match_data:
                    logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + f"Optional Key {key} not found in xml_match_data")
                    continue
                if split_key not in xml_match_data:
                    logging.getLogger(DEBUG_LOG_NAME).debug(
                        debug_log_prefix + f"Key {split_key} not found in xml_match_data. RETURN [NONE] 4")
                    return [None]
                if xml_dict[key] == "ALLOW_ALL":
                    match_context.update(match_context.match_data[:match_context.match_data.find(
                        f"</{self.get_stripped_key(split_key)}>".encode()) + len(f"</{self.get_stripped_key(split_key)}>")])
                else:
                    match_element, index, data = self.parse_object(xml_dict, xml_match_data, key, split_key, current_path, match_context)
                    matches.append(match_element)
                    if index == -1 and match_element is None:
                        backslash = b"\\"
                        logging.getLogger(DEBUG_LOG_NAME).debug(
                            debug_log_prefix + f"Necessary element did not match! Key: {key}, MatchElement: {match_element}, Data: "
                                               f"{data.decode()}, IsFloat {isinstance(xml_match_data[split_key], float)}, Index: {index}, "
                                               f"MatchContext: {match_context.match_data.replace(backslash, b'').decode()}")
                        return matches
                    match_context.update(match_context.match_data[:index + len(data) + len(f"</{self.get_stripped_key(split_key)}>")])
        missing_keys = [x for x in xml_dict if self.get_stripped_key(x) not in xml_match_data and not (
                x.startswith(self.optional_attribute_prefix) or x.startswith(self.attribute_prefix + self.optional_attribute_prefix))]
        for key in missing_keys:
            logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "Missing Key: " + key)
            return [None]
        return matches

    def check_keys(self, xml_dict, xml_match_data, match_context):
        """Check if no keys are missing and if the value types match."""
        if xml_match_data is None:
            return False
        missing_keys = [x for x in xml_dict if self.get_stripped_key(x) not in xml_match_data and not (x.startswith(
            self.optional_attribute_prefix) or x.startswith(self.attribute_prefix + self.optional_attribute_prefix))]
        for key in missing_keys:
            if (not key.startswith(self.empty_allowed_prefix) or (
                    key.startswith(self.empty_allowed_prefix) and key[len(self.empty_allowed_prefix):] not in xml_match_data)):
                index = match_context.match_data.find(key.encode())
                match_context.update(match_context.match_data[:index])
                logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN [NONE] 1. Key: " + key)
                return False
        for key in xml_dict.keys():
            k = self.get_stripped_key(key)
            if not isinstance(xml_match_data, dict) or (k in xml_match_data and isinstance(xml_match_data[k], list) and not isinstance(
                    xml_dict[key], list)):
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

    def parse_array(self, xml_dict: dict, xml_match_data: dict, key: str, split_key: str, current_path: str, matches: list,
                    match_context, i: int):
        """Parse an array in a xml object."""
        if self.is_nullable_key(key) and xml_match_data[split_key] is None:
            return None
        if not isinstance(xml_match_data[split_key], list):
            logging.getLogger(DEBUG_LOG_NAME).debug(
                debug_log_prefix + "Key " + split_key + " is no array. Data: " + str(xml_match_data[split_key]))
            return [None]
        search_string = b"</" + self.get_stripped_key(split_key).encode() + b">"
        match_array = self.flatten_list(xml_match_data[split_key])
        value = self.flatten_list(xml_dict[key])
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
                    matches += self.parse_dict(val, match_array[j], f"{current_path}/{split_key}", match_context)
                    if matches[-1] is None:
                        if len(value) - 1 == k:
                            logging.getLogger(DEBUG_LOG_NAME).debug(debug_log_prefix + "No match found for key " + split_key)
                            return matches
                        del matches[-1]
                        continue
                    break
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
        if len(xml_match_data.keys()) > i + 1:
            match_context.update(match_context.match_data[:match_context.match_data.find(
                list(xml_match_data.keys())[i + 1].encode())])
        else:
            match_context.update(match_context.match_data[:match_context.match_data.find(search_string) + len(search_string)])
        return None

    def parse_object(self, xml_dict, xml_match_data, key, split_key, current_path, match_context):  # skipcq: PYL-R0201
        """Parse a literal from the xml object."""
        current_path += "/" + key
        data = xml_match_data[split_key]
        enc = "utf-8"
        if isinstance(data, str):
            if self.is_escaped_unicode(data) and self.dec_escapes:
                enc = "unicode-escape"
            data = data.encode(enc)
        elif isinstance(data, bool):
            data = str(data).replace("T", "t").replace("F", "f").encode()
        elif data is None:
            data = b"null"
            if self.is_nullable_key(key):
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

        match_element = xml_dict[key].get_match_element(current_path, MatchContext(data))
        if match_element is not None and len(match_element.match_string) != len(data) and (
                not isinstance(match_element.match_object, bytes) or len(match_element.match_object) != len(data)):
            logging.getLogger(DEBUG_LOG_NAME).debug(
                debug_log_prefix + f"Data length not matching! match_string: {len(match_element.match_string)}, data: {len(data)},"
                                   f" data: {data.decode()}")
            match_element = None
        index = max([match_context.match_data.replace(b"\\", b"").find(split_key.encode()),
                     match_context.match_data.find(split_key.encode()), match_context.match_data.decode().find(split_key)])
        index += match_context.match_data[index:].find(split_key.encode()) + len(split_key.encode())
        try:
            index += max([match_context.match_data.replace(b"\\", b"")[index:].find(data), match_context.match_data[index:].find(data),
                          match_context.match_data.decode(enc)[index:].find(data.decode(enc))])
        except UnicodeDecodeError:
            index += max([match_context.match_data.replace(b"\\", b"")[index:].find(data), match_context.match_data[index:].find(data),
                          match_context.match_data.decode()[index:].find(data.decode())])
        index += len(match_context.match_data[index:]) - len(match_context.match_data[index:].lstrip(b" \r\t\n"))
        if match_element is None:
            index = -1
        return match_element, index, data
