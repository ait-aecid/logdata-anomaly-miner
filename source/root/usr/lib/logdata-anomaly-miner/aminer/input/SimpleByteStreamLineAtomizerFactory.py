"""
This module defines a factory for instanciating line atomizers.

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

from aminer.input.InputInterfaces import AtomizerFactory
from aminer.input.ByteStreamLineAtomizer import ByteStreamLineAtomizer


class SimpleByteStreamLineAtomizerFactory(AtomizerFactory):
    """
    This factory just creates the same atomizer for each new resource.
    All parsed and unparsed atoms are delivered via two lists of handlers.
    """

    def __init__(
            self, parsing_model, atom_handler_list, event_handler_list, default_timestamp_path_list=None, eol_sep=b'\n', json_format=False):
        """
        Create the factory to forward data and events to the given lists for each newly created atomizer.
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

    def get_atomizer_for_resource(self, resource_name):  # skipcq: PYL-W0613
        """
        Get an atomizer for a given resource.
        @param resource_name the resource name for atomizer selection is ignored in this type of factory.
        @return a StreamAtomizer object
        """
        return ByteStreamLineAtomizer(self.parsing_model, self.atom_handler_list, self.event_handler_list, 1 << 16,
                                      self.default_timestamp_path_list, self.eol_sep, self.json_format)
