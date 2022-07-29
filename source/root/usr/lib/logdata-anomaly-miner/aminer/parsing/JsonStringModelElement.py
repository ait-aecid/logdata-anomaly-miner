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

"""
The JsonAccessObject transforms a dictionary. It takes a dictionary "d" and
flattens the dictionary to: key.another_key.somelist[0].foo = bar
During the flatten()-process, it will create a self.collection dictionary with
the format: collection[flattened-key]{levels[],value}
"""
class JsonAccessObject:
    def __init__(self, d: dict):
       self.levels = deque()
       self.delimiter = '.'
       self.collection = {}
       self.flatten(d)

    def join_levels(self):
        ret = ""
        for i in self.levels:
            if not i.startswith("[") and len(ret) != 0:
                ret += self.delimiter
            ret += i
        return ret

    def create_collection_entry(self, index: str, levels: deque, value):
        subentry = {}
        subentry['levels'] = levels.copy()
        subentry['value'] = value
        self.collection[index] = subentry


    def flatten(self, d: dict, islist=-1):
        if islist > -1:
            for k in d:
                if isinstance(k,dict):
                    self.levels.append("[%d]"%islist)
                    islist = islist+1
                    self.flatten(k)
                    self.levels.pop()
                elif isinstance(k,list):
                    self.flatten(k,list)
                else:
#                    print("%s[%d]: %s" % (self.join_levels(),islist,k))
                    self.create_collection_entry("%s[%d]" % (self.join_levels(),islist), self.levels, k)
                    islist = islist + 1
        else:
            for (k,v) in d.items():
                if isinstance(v,dict):
                    self.levels.append(k)
                    self.flatten(v)
                    if len(self.levels) != 0:
                        self.levels.pop()
                elif isinstance(v,list):
                   self.levels.append(k)
                   self.flatten(v,0)
                   if len(self.levels) != 0:
                       self.levels.pop()
                else:
                    if len(self.levels) == 0:
#                        print("%s : %s" % (k,v))
                        self.create_collection_entry(k, deque([k]), v)
                    else:
                        if islist > -1:
                            self.levels.append(k+"[%d]"%islist)
                            islist = islist+1
                        else:
                            self.levels.append(k)
#                        print("%s : %s" % (self.join_levels(),v))
                        self.create_collection_entry(self.join_levels(), self.levels, v)
                        self.levels.pop()



class JsonStringModelElement(ModelElementInterface):
    """This class matches any byte but at least one. Thus a match will always span the complete data from beginning to end."""

    def __init__(self, element_id: str, key_parser_dict: dict, strict_mode: bool):
        self.children = []

        
        self.strict_mode = strict_mode
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


    def fill_children(self):
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
        current_path = "%s/%s" % (path, self.element_id)
        logging.getLogger(DEBUG_LOG_NAME).info("%s/%s",path,match_context.match_data.decode('utf-8'))
        matches = []
        try:
            jdict = orjson.loads(match_context.match_data)
            if self.strict_mode:
                jdictjao = JsonAccessObject(jdict)
                if len(jdictjao.collection) != len(self.jao.collection):
                    logging.getLogger(DEBUG_LOG_NAME).debug("json-subparser-error: strict mode enabled and fields detected that do not exist in parser-config")
                try:
                    for (k,v) in self.jao.collection.items():
                        child_match = v['value'].get_match_element(current_path, MatchContext(str(jdictjao.collection[k]['value']).encode('utf-8')))
                        if child_match is None:
                            logging.getLogger(DEBUG_LOG_NAME).debug("json-subparser-error: %s", k)
                            return None
                        matches += [child_match]
                except KeyError:
                    logging.getLogger(DEBUG_LOG_NAME).debug("json-subparser-error: field \"%s\" not found but strict-enabled", k)
                    return None
            else:
                for (k,v) in self.jao.collection.items():
                    tmp = jdict.copy()
                    try:
                        for level in v['levels']:
                            tmp = tmp[level]
                    except KeyError:
                        logging.getLogger(DEBUG_LOG_NAME).debug("json-subparser:: %s not found", k)
                    child_match = v['value'].get_match_element(current_path, MatchContext(str(tmp).encode('utf-8')))
                    if child_match is None:
                        logging.getLogger(DEBUG_LOG_NAME).debug("json-subparser-error: %s", k)
                        return None
                    matches += [child_match]
        except orjson.JSONDecodeError as exception:
            logging.getLogger(DEBUG_LOG_NAME).error("%s: %s",exception.msg,match_context.match_data.decode('utf-8'))
            return None

        match_data = match_context.match_data
        if not match_data:
            return None
        match_context.update(match_data)
        return MatchElement(current_path, match_data, match_data, matches)
