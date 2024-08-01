"""This module defines a factory for instanciating line atomizers.

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
from aminer.input.InputInterfaces import AtomizerFactory
from aminer.input.ByteStreamLineAtomizer import ByteStreamLineAtomizer


class SimpleByteStreamLineAtomizerFactory(AtomizerFactory):
    """This factory just creates the same atomizer for each new resource.

    All parsed and unparsed atoms are delivered via two lists of
    handlers.
    """

    def __init__(self, parsing_model, atom_handler_list, event_handler_list, default_timestamp_path_list=None, eol_sep=b'\n',
                 json_format=False, xml_format=False, parser_model_dict=None, log_resources=None, use_real_time=False,
                 continuous_timestamp_missing_warning=True):
        """Create the factory to forward data and events to the given lists for
        each newly created atomizer.

        @param default_timestamp_path_list if not empty list, the value of this timestamp field is extracted from parsed atoms and stored
        as default timestamp for that atom.
        """
        self.parsing_model = parsing_model
        self.atom_handler_list = atom_handler_list
        self.event_handler_list = event_handler_list
        if default_timestamp_path_list is None:
            self.default_timestamp_path_list = []
        else:
            self.default_timestamp_path_list = default_timestamp_path_list
        self.eol_sep = eol_sep
        self.json_format = json_format
        self.xml_format = xml_format
        if json_format is True and xml_format is True:
            msg = "json_format and xml_format can not be true at the same time."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        self.parser_model_dict = parser_model_dict
        self.log_resources = log_resources
        self.use_real_time = use_real_time
        self.continuous_timestamp_missing_warning = continuous_timestamp_missing_warning

    def get_atomizer_for_resource(self, resource_name):
        """Get an atomizer for a given resource.

        @param resource_name the resource name for atomizer selection is ignored in this type of factory.
        @return a StreamAtomizer object
        """
        if self.log_resources is not None and resource_name in self.log_resources.keys():
            resource = self.log_resources[resource_name]
            json = resource["json"]
            xml = resource["xml"]
            if json is None:
                json = self.json_format
            if xml is None:
                xml = self.xml_format
            parser = self.parsing_model
            if resource["parser_id"] is not None:
                parser = self.parser_model_dict[resource["parser_id"]]
            return ByteStreamLineAtomizer(
                parser, self.atom_handler_list, self.event_handler_list, 1 << 16, self.default_timestamp_path_list, self.eol_sep, json,
                xml, self.use_real_time, resource_name, self.continuous_timestamp_missing_warning)
        return ByteStreamLineAtomizer(
            self.parsing_model, self.atom_handler_list, self.event_handler_list, 1 << 16, self.default_timestamp_path_list, self.eol_sep,
            self.json_format, self.xml_format, self.use_real_time, resource_name, self.continuous_timestamp_missing_warning)
