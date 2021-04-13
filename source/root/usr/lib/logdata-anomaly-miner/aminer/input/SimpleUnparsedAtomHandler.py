"""
This module defines a handler that forwards unparsed atoms to the event handlers.

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

from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.AminerConfig import ENCODING


class SimpleUnparsedAtomHandler(AtomHandlerInterface):
    """Handlers of this class will just forward received unparsed atoms to the registered event handlers."""

    def __init__(self, event_handlers):
        self.event_handlers = event_handlers
        self.persistence_id = None

    def receive_atom(self, log_atom):
        """Receive an unparsed atom to create events for each."""
        if log_atom.is_parsed():
            return False
        event_data = {}
        try:
            data = log_atom.raw_data.decode(ENCODING)
        except UnicodeError:
            data = repr(log_atom.raw_data)
        for listener in self.event_handlers:
            listener.receive_event('Input.UnparsedAtomHandler', 'Unparsed atom received', [data], event_data, log_atom, self)
        return True
