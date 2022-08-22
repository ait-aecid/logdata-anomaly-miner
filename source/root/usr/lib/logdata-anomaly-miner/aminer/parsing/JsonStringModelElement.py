"""
This module defines a model element that matches any byte.

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
import orjson
from collections import deque

from aminer.AminerConfig import DEBUG_LOG_NAME
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.MatchElement import MatchElement
from aminer.parsing.ModelElementInterface import ModelElementInterface


class JsonAccessObject:
    """
    The JsonAccessObject transforms a dictionary. It takes a dictionary "d" and
    flattens the dictionary to: key.another_key.somelist[0].foo = bar
    During the flatten()-process, it will create a self.collection dictionary with
    the format: collection[flattened-key]{levels[],value}
    """

    def __init__(self, d: dict):
        self.debug = False
        self.levels = deque()
        self.delimiter = '.'
        self.collection = {}
        self.flatten(d)

    def join_levels(self):
        """joins levels using a specific delimiter"""
        ret = ""
        for i in self.levels:
            if not i.startswith("[") and len(ret) != 0:
                ret += self.delimiter
            ret += i
        return ret

    def create_collection_entry(self, index: str, levels: deque, value):
        """adds entry to the collection"""
        subentry = {}
        subentry['levels'] = levels.copy()
        subentry['value'] = value
        self.collection[index] = subentry

    def flatten(self, d: dict, islist=-1):
        """recursive function for flattening a dictionary"""
        if islist > -1:
            for k in d:
                if isinstance(k, dict):
                    # skipcq: FLK-E228
                    self.levels.append(f"[{islist}]")
                    islist = islist+1
                    self.flatten(k)
                    self.levels.pop()
                elif isinstance(k, list):
                    self.flatten(k, list)
                else:
                    if self.debug:
                        print(f"{ self.join_levels() }[{ islist }]: { k }")
                    self.create_collection_entry("f{ self.join_levels() }[{ islist }]", self.levels, k)
                    islist = islist + 1
        else:
            for (k, v) in d.items():
                if isinstance(v, dict):
                    self.levels.append(k)
                    self.flatten(v)
                    if len(self.levels) != 0:
                        self.levels.pop()
                elif isinstance(v, list):
                    self.levels.append(k)
                    self.flatten(v, 0)
                    if len(self.levels) != 0:
                        self.levels.pop()
                else:
                    if len(self.levels) == 0:
                        if self.debug:
                            print(f"{ k } : { v }")
                        self.create_collection_entry(k, deque([k]), v)
                    else:
                        if islist > -1:
                            # skipcq: FLK-E228
                            self.levels.append(f"{k}[{ islist}]")
                            islist = islist+1
                        else:
                            self.levels.append(k)
                        if self.debug:
                            print(f"{ self.join_levels() } : { v }")
                        self.create_collection_entry(self.join_levels(), self.levels, v)
                        self.levels.pop()


class JsonStringModelElement(ModelElementInterface):
    """This class matches any byte but at least one. Thus a match will always span the complete data from beginning to end."""

    def __init__(self, element_id: str, key_parser_dict: dict, strict_mode: bool = False, ignore_null: bool = True):
        self.children = []

        self.strict_mode = strict_mode
        self.ignore_null = ignore_null

        if not isinstance(key_parser_dict, dict):
            msg = "key_parser_dict has to be of the type dict."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        self.jao = JsonAccessObject(key_parser_dict)
        if not isinstance(element_id, str):
            msg = "element_id has to be of the type string."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise TypeError(msg)
        if len(element_id) < 1:
            msg = "element_id must not be empty."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.element_id = element_id
        self.fill_children()
        super().__init__(element_id, key_parser_dict=key_parser_dict, strict_mode=strict_mode,
                         ignore_null=ignore_null)

    def fill_children(self):
        """creates list of children from config-json"""
        for entry in self.jao.collection.values():
            self.children.append(entry['value'])

    def get_id(self):
        """Get the element ID."""
        return self.element_id

    def get_child_elements(self):  # skipcq: PYL-R0201
        """
        Get all possible child model elements of this element.
        @return None as there are no children of this element.
        """
        return self.children

    def get_match_element(self, path: str, match_context):
        """Just return a match including all data from the context."""
        current_path = f"{ path }/ { self.element_id }"
        logging.getLogger(DEBUG_LOG_NAME).info("JsonStringModelElement %s/%s", path, match_context.match_data.decode('utf-8'))
        matches = []
        try:
            jdict = orjson.loads(match_context.match_data)
            if self.strict_mode:
                jdictjao = JsonAccessObject(jdict)
                if len(jdictjao.collection) != len(self.jao.collection):
                    msg = "JsonStringModelElement-subparser-error: "
                    msg += "strict mode enabled and fields detected that do not exist in parser-config"
                    logging.getLogger(DEBUG_LOG_NAME).debug(msg)
                    return None
                try:
                    for (k, v) in self.jao.collection.items():
                        # empty string if value is null
                        parse_line = b""
                        if jdictjao.collection[k]['value'] is not None:
                            parse_line = str(jdictjao.collection[k]['value']).encode('utf-8')
                        else:
                            if self.ignore_null:
                                logging.getLogger(DEBUG_LOG_NAME).debug("JsonStringModelElement: ignore null at %s", k)
                                continue
                        child_match = v['value'].get_match_element(current_path, MatchContext(parse_line))
                        if child_match is None:
                            msg = "JsonStringModelElement-subparser-error: %s -> %s"
                            logging.getLogger(DEBUG_LOG_NAME).debug(msg, k, str(jdictjao.collection[k]['value']))
                            return None
                        matches += [child_match]
                except KeyError:
                    msg = "JsonStringModelElement-subparser-error: field \"%s\" not found but strict-enabled"
                    logging.getLogger(DEBUG_LOG_NAME).debug(msg, k)
                    return None
            else:
                for (k, v) in self.jao.collection.items():
                    tmp = jdict.copy()
                    try:
                        for level in v['levels']:
                            tmp = tmp[level]
                    except KeyError:
                        logging.getLogger(DEBUG_LOG_NAME).debug("JsonStringModelElement-subparser: %s not found", k)
                    parse_line = b""
                    # empty string if value is null
                    if tmp is not None:
                        parse_line = str(tmp).encode('utf-8')
                    else:
                        if self.ignore_null:
                            logging.getLogger(DEBUG_LOG_NAME).debug("JsonStringModelElement: ignore null at %s", k)
                            continue
                    child_match = v['value'].get_match_element(current_path, MatchContext(parse_line))
                    if child_match is None:
                        logging.getLogger(DEBUG_LOG_NAME).debug("JsonStringModelElement-subparser-error: %s -> %s", k, tmp)
                        return None
                    matches += [child_match]
        except orjson.JSONDecodeError as exception:
            logging.getLogger(DEBUG_LOG_NAME).error("JsonStringModelElement %s: %s",
                                exception.msg, match_context.match_data.decode('utf-8'))
            return None

        match_data = match_context.match_data
        if not match_data:
            return None
        match_context.update(match_data)
        return MatchElement(current_path, match_data, match_data, matches)
