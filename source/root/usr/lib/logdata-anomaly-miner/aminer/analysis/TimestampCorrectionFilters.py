"""This file collects various classes useful to filter and correct the timestamp associated with a received parsed atom.

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


class SimpleMonotonicTimestampAdjust(AtomHandlerInterface):
    """Handlers of this class compare the timestamp of a newly received atom with the largest timestamp seen so far. When below, the
    timestamp of this atom is adjusted to the largest value seen, otherwise the largest value seen is updated."""

    def __init__(self, subhandler_list, stop_when_handled_flag=False):
        self.subhandler_list = subhandler_list
        self.stop_when_handled_flag = stop_when_handled_flag
        self.latest_timestamp_seen = 0

    def receive_atom(self, log_atom):
        """Pass the atom to the subhandlers.
        @return false when no subhandler was able to handle the atom."""
        self.log_total += 1
        if log_atom.get_timestamp() is not None:
            if log_atom.get_timestamp() < self.latest_timestamp_seen:
                log_atom.set_timestamp(self.latest_timestamp_seen)
            else:
                self.latest_timestamp_seen = log_atom.get_timestamp()

        result = False
        for handler in self.subhandler_list:
            handler_result = handler.receive_atom(log_atom)
            if handler_result is True:
                result = True
                if self.stop_when_handled_flag:
                    break
        if result:
            self.log_success += 1
        return result
