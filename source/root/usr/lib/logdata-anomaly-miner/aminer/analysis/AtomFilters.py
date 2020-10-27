"""This file collects various classes useful to filter log atoms
and pass them to different handlers.

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

from aminer.input import AtomHandlerInterface


class SubhandlerFilter(AtomHandlerInterface):
    """Handlers of this class pass the received atoms to one or more subhandlers. Depending on configuration, the atom is passed
    to all subhandlers or only up to the first suitable to handle the atom."""

    def __init__(self, subhandler_list, stop_when_handled_flag=False):
        """@param subhandler_list when not None, initialize this filter
        with the given list of handlers."""
        if subhandler_list is None:
            self.subhandler_list = []
        else:
            if (not isinstance(subhandler_list, list)) or \
                    (not all(isinstance(handler, AtomHandlerInterface) for handler in subhandler_list)):
                raise Exception('Only subclasses of AtomHandlerInterface allowed in subhandlerList')
            self.subhandler_list = [None] * len(subhandler_list)
            for handler_pos, handler_element in enumerate(subhandler_list):
                self.subhandler_list[handler_pos] = (handler_element, stop_when_handled_flag)

    def add_handler(self, atom_handler, stop_when_handled_flag=False):
        """Add a handler to the list of handlers."""
        self.subhandler_list.append((atom_handler, stop_when_handled_flag))

    def receive_atom(self, log_atom):
        """Pass the atom to the subhandlers.
        @return false when no subhandler was able to handle the atom."""
        result = False
        self.log_total += 1
        for handler, stop_when_handled_flag in self.subhandler_list:
            handler_result = handler.receive_atom(log_atom)
            if handler_result is True:
                result = True
                self.log_success += 1
                if stop_when_handled_flag:
                    break
        return result


class MatchPathFilter(AtomHandlerInterface):
    """This class just splits incoming matches according to existance of pathes in the match."""

    def __init__(self, parsed_atom_handler_lookup_list, default_parsed_atom_handler=None):
        """Initialize the filter.
        @param parsed_atom_handler_lookup_list has to contain tuples with search path string and handler. When the handler is None,
        the filter will just drop a received atom without forwarding.
        @param default_parsed_atom_handler invoke this handler when no handler was found for given match path or do not invoke any
        handler when None."""
        self.parsed_atom_handler_lookup_list = parsed_atom_handler_lookup_list
        self.default_parsed_atom_handler = default_parsed_atom_handler

    def receive_atom(self, log_atom):
        """Receive an atom and pass it to the subhandlers.
        @return False when logAtom did not contain match data or was not forwarded to any handler, True otherwise."""
        self.log_total += 1
        if log_atom.parser_match is None:
            return False
        match_dict = log_atom.parser_match.get_match_dictionary()
        for path_name, target_handler in self.parsed_atom_handler_lookup_list:
            if path_name in match_dict:
                if target_handler is not None:
                    target_handler.receive_atom(log_atom)
                self.log_success += 1
                return True
        if self.default_parsed_atom_handler is None:
            return False
        self.default_parsed_atom_handler.receive_atom(log_atom)
        self.log_success += 1
        return True


class MatchValueFilter(AtomHandlerInterface):
    """This class just splits incoming matches using a given match value and forward them to different handlers."""

    def __init__(self, target_path, parsed_atom_handler_dict, default_parsed_atom_handler=None):
        """Initialize the splitter.
        @param default_parsed_atom_handler invoke this default handler when no value handler was found or do not invoke any handler
        when None."""
        self.target_path = target_path
        self.parsed_atom_handler_dict = parsed_atom_handler_dict
        self.default_parsed_atom_handler = default_parsed_atom_handler

    def receive_atom(self, log_atom):
        self.log_total += 1
        if log_atom.parser_match is None:
            return False
        target_value = log_atom.parser_match.get_match_dictionary().get(self.target_path, None)
        if target_value is not None:
            target_value = target_value.match_object
        target_handler = self.parsed_atom_handler_dict.get(target_value, self.default_parsed_atom_handler)
        if target_handler is None:
            return False
        target_handler.receive_atom(log_atom)
        self.log_success += 1
        return True
