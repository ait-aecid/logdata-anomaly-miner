"""This module contains multiple History classes used by the aminer.

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
import random
import abc
from aminer.input.InputInterfaces import AtomHandlerInterface


def get_log_int(max_bits):
    """Get a log-distributed random integer integer in range 0 to maxBits-1."""
    rand_bits = random.randint(0, (1 << max_bits) - 1)  # nosec B311
    result = 0
    while (rand_bits & 1) != 0:
        result += 1
        rand_bits >>= 1
    return result


class ObjectHistory(metaclass=abc.ABCMeta):
    """This is the superinterface of all object histories.

    The idea behind that is to use that type of history best suited for
    a purpose considering amount of data, possibility for history size
    limits to be reached, priorization which elements should be dropped
    first.
    """

    @abc.abstractmethod
    def add_object(self, new_object):
        """Add an object to this history.

        This method call may evict other objects from the history.
        """

    @abc.abstractmethod
    def get_history(self):
        """Get the whole history list.

        Make sure to clone the list before modification when influences
        on this object are not intended.
        """

    @abc.abstractmethod
    def clear_history(self):
        """Clean the whole history."""


class LogarithmicBackoffHistory(ObjectHistory):
    """This class keeps a history list of items with logarithmic storage
    characteristics.

    When adding objects, the list will be filled to the maximum size with the newest items at the end. When filled, adding a new element
    will replace with probability 1/2 the last element. With a chance of 1/4, the last element will be moved to the next lower position,
    before putting the new element at the end of the list. With a chance of 1/8, the last two elements are moved, ... Thus the list will in
    average span a time range of 2^maxItems items with growing size of holes towards the earliest element.
    """

    def __init__(self, max_items, initial_list=None):
        self.max_items = max_items
        if initial_list is None:
            initial_list = []
        else:
            initial_list = initial_list[:max_items]
        self.history = initial_list

    def add_object(self, new_object):
        """Add a new object to the list according to the rules described in the
        class docstring."""
        if len(self.history) < self.max_items:
            self.history.append(new_object)
        else:
            move_pos = get_log_int(self.max_items - 1)
            self.history = self.history[:self.max_items - move_pos - 1] + self.history[self.max_items - move_pos:] + [new_object]

    def get_history(self):
        """Get the whole history list.

        Make sure to clone the list before modification when influences
        on this object are not intended.
        """
        return self.history

    def clear_history(self):
        """Clean the whole history."""
        self.history[:] = []


class VolatileLogarithmicBackoffAtomHistory(AtomHandlerInterface, LogarithmicBackoffHistory):
    """This class is a volatile filter to keep a history of log atoms.

    Example usages can be for analysis by other components or for
    external access via remote control interface.
    """

    def __init__(self, max_items):
        """Initialize the history component."""
        LogarithmicBackoffHistory.__init__(self, max_items)
        AtomHandlerInterface.__init__(self)

    def receive_atom(self, log_atom):
        """Receive an atom and add it to the history log."""
        self.add_object(log_atom)
        return True
