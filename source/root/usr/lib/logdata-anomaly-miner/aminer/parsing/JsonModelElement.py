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
from json import JSONDecodeError
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.ModelElementInterface import ModelElementInterface


warnings.filterwarnings("ignore", category=DeprecationWarning)
debug_log_prefix = "JsonModelElement: "


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
        except JSONDecodeError as e:
            logging.getLogger(debug_log_prefix + AminerConfig.DEBUG_LOG_NAME).debug(e)
            return None
        match_context.match_data = match_context.match_data.decode('unicode-escape').encode()
        matches += self.parse_json_dict(self.key_parser_dict, json_match_data, current_path, match_context)
        if None in matches or match_context.match_data.strip(b' }]"\r\n') != b'':
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(
                debug_log_prefix + "get_match_element_main NONE RETURNED", match_context.match_data.strip(b' }]"\r\n').decode())
            #############
            print("RETURN NONE!!!!", match_context.match_data.strip(b' }]"\r\n').decode())
            #############
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
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN [NONE] 1", key)
                #############
                print("RET NONE1", key)
                #############
                return [None]
        for i, key in enumerate(json_match_data.keys()):
            split_key = key
            if self.optional_key_prefix + key in json_dict:
                key = self.optional_key_prefix + key
            if key not in json_dict:
                index = match_context.match_data.find(key.encode())
                match_context.update(match_context.match_data[:index])
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN [NONE] 2", key, json_dict)
                ############
                print("RET NONE2", key, json_dict)
                ############
                return [None]
            value = json_dict[key]
            if isinstance(value, (dict, list)) and (not isinstance(json_match_data, dict) or split_key not in json_match_data):
                ###########
                print("RET NONE3")
                ###########
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN [NONE] 3")
                return [None]
            if isinstance(value, dict):
                matches += self.parse_json_dict(value, json_match_data[split_key], "%s/%s" % (current_path, split_key), match_context)
                if matches[-1] is None:
                    ###########
                    print("RETURN MATCHES 1")
                    ###########
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN MATCHES 1")
                    return matches
            elif isinstance(value, list):
                for data in json_match_data[split_key]:
                    if isinstance(data, str):
                        data = data.encode()
                    elif not isinstance(data, bytes):
                        data = str(data).encode()
                    if isinstance(json_dict[key][0], dict):
                        for match_data in json_match_data[split_key]:
                            matches += self.parse_json_dict(
                                json_dict[key][0], match_data, "%s/%s" % (current_path, split_key), match_context)
                            if matches[-1] is None:
                                ##########
                                print("RET2")
                                ###########
                                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN MATCHES 2")
                                return matches
                    else:
                        if json_dict[key][0] == "ALLOW_ALL":
                            ###########
                            print("ALLOW_ALL", data.decode())
                            ###########
                            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(debug_log_prefix + "ALLOW_ALL (LIST)")
                            match_element = MatchElement(current_path, data, data, None)
                        else:
                            match_element = json_dict[key][0].get_match_element(current_path, MatchContext(data))
                            if match_element is not None and len(match_element.match_string) != len(data):
                                ##########
                                print("EEEEEEEEEE")
                                ##########
                                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(debug_log_prefix + "MatchElement NONE 1")
                                match_element = None
                        index = match_context.match_data.find(data)
                        print(index)
                        if match_element is None:
                            ##############
                            print("HHHHHHHHHHHHHHHHHHHHH", data.decode())
                            ##############
                            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(debug_log_prefix + "MatchElement NONE 2", data.decode())
                            index = -1
                        match_context.update(match_context.match_data[:index + len(data)])
                        if index == -1 and json_dict[key][0] == "ALLOW_ALL":
                            ###################
                            print(match_context.match_data.decode())
                            print("MMMMMMMMMMMMMM")
                            ##################
                            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(
                                debug_log_prefix + "ALLOW_ALL (LIST-ELEMENT)", match_context.match_data.decode())
                            index = match_context.match_data.find(b']')
                            match_context.update(match_context.match_data[:index])
                        ###########
                        print(match_context.match_data.decode())
                        ###########
                        if match_element is not None or (match_element is None and not key.startswith(self.optional_key_prefix)):
                            matches.append(match_element)
                            if index == -1:
                                return matches
                        if matches[-1] is None:
                            ##########
                            print("RET1")
                            ##########
                            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(debug_log_prefix + "RETURN MATCHES 3")
                            return matches
                if len(json_match_data.keys()) > i + 1:
                    #############
                    print("GGGGGGGGGGGGG", len(json_match_data.keys()), i + 1, match_context.match_data[:match_context.match_data.find(
                        list(json_match_data.keys())[i + 1].encode())].decode())
                    print(list(json_match_data.keys())[i + 1])
                    #############
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(debug_log_prefix + "LIST - Searching next key")
                    match_context.update(match_context.match_data[:match_context.match_data.find(
                        list(json_match_data.keys())[i + 1].encode())])
                else:
                    ############
                    print("LLLLLLLLLLLLLLLLL")
                    ############
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(debug_log_prefix + "LIST - No more keys found")
                    match_context.update(match_context.match_data[:match_context.match_data.find(b']')])
            else:
                if key != split_key and split_key not in json_match_data:
                    ############
                    print("CONTINUE!!!!")
                    ############
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(
                        debug_log_prefix + "Optional Key %s not found in json_match_data" % key)
                    continue
                if split_key not in json_match_data:
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(
                        debug_log_prefix + "Key %s not found in json_match_data. RETURN [NONE] 4" % split_key)
                    #############
                    print("SPLIT_KEY not FOUND!!", split_key)
                    ############
                    return [None]
                data = json_match_data[split_key]
                if isinstance(data, str):
                    # print("DATA", data)
                    data = data.encode('unicode-escape')
                elif isinstance(data, bool):
                    data = str(data).replace("T", "t").replace("F", "f").encode()
                elif not isinstance(data, bytes):
                    data = str(data).encode()
                if json_dict[key] == "ALLOW_ALL":
                    #############
                    print("ALLOW_ALL", data.decode())
                    ############
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(debug_log_prefix + "ALLOW_ALL (DICT)", data.decode())
                    match_element = MatchElement(current_path, data, data, None)
                else:
                    match_element = json_dict[key].get_match_element(current_path, MatchContext(data))
                    if match_element is not None and len(match_element.match_string) != len(data) and (
                            not isinstance(match_element.match_object, bytes) or len(match_element.match_object) != len(data)):
                        #############
                        print("FFFFFFF")
                        #############
                        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(
                            debug_log_prefix + "Data length not matching! match_string: %d, data: %d, data: %s" % (
                                len(match_element.match_string), len(data), data.decode()))
                        match_element = None
                index = max([match_context.match_data.replace(b'\\', b'').find(data), match_context.match_data.find(data),
                             match_context.match_data.decode().find(data.decode()), match_context.match_data.decode(
                        'unicode-escape').find(data.decode('unicode-escape'))])
                # for example float scientific representation is converted to normal float..
                if index == -1 and match_element is not None and isinstance(json_match_data[split_key], float):
                    indices = [match_context.match_data.find(b',', len(match_element.match_string) // 3),
                               match_context.match_data.find(b']'), match_context.match_data.find(b'}')]
                    indices = [x for x in indices if x >= 0]
                    index = min(indices)
                if match_element is None:
                    index = -1
                #################
                # if isinstance(json_match_data[split_key], bytes):
                #     print("UPDATE", index, len(data), len(json_match_data[split_key]), data.decode('unicode-escape'), match_element is None)
                # print("UPDATE!!!!", match_context.match_data.decode('unicode-escape'))
                ##################
                match_context.update(match_context.match_data[:index + len(data)])
                if index == -1 and json_dict[key] == "ALLOW_ALL":
                    #################
                    #print(match_context.match_data.decode())
                    print("JJJJJJJJJJJJJJ")
                    ############
                    logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(debug_log_prefix + "ALLOW_ALL search end bracket")
                    match_context.update(match_context.match_data[:match_context.match_data.find(b'}')])
                ############
                #print(match_context.match_data.decode())
                ############
                if match_element is not None or (match_element is None and not key.startswith(self.optional_key_prefix)):
                    matches.append(match_element)
                    if index == -1 and match_element is None:
                        logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(
                            debug_log_prefix +
                            "Necessary element did not match! MatchElement: %s\nData: %s\nMatchContext: %s\nIsFloat %s, Index: %d" % (
                                match_element, data.decode(), match_context.match_data.replace(b'\\', b'').decode(),
                                isinstance(json_match_data[split_key], float), index))
                        ##################
                        print(match_element)
                        print("RET6")
                        print(data.decode())
                        print(match_context.match_data.replace(b'\\', b'').decode())
                        print(isinstance(json_match_data[split_key], float))
                        print(index)
                        ##################
                        return matches
        #############
        #print("END!!!")
        ############
        missing_keys = [x for x in json_dict if x not in json_match_data]
        for key in missing_keys:
            if not key.startswith(self.optional_key_prefix):
                ##########
                print("RET3")
                ##########
                logging.getLogger(AminerConfig.DEBUG_LOG_NAME).debug(debug_log_prefix + "Missing Key:", key)
                return [None]
        return matches
