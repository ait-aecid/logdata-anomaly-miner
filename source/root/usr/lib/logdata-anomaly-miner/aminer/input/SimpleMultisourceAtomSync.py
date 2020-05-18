"""This module defines a handler that synchronizes different
streams."""

import time
from aminer.input import AtomHandlerInterface


class SimpleMultisourceAtomSync(AtomHandlerInterface):
    """This class synchronizes different atom streams by forwarding the atoms only from the source delivering the oldest ones. This
    is done using the atom timestamp value. Atoms without a timestamp are forwarded immediately. When no atoms are received from a
    source for some time, no more atoms are expected from that source. This will allow forwarding of blocked atoms from
    other sources afterwards."""

    def __init__(self, atom_handler_list, sync_wait_time=5):
        """@param atom_handler_list forward atoms to all handlers in the list, no matter if the log_atom was handled or not.
        @return true as soon as forwarding was attempted, no matter if one downstream handler really consumed the atom."""
        self.atom_handler_list = atom_handler_list
        self.sync_wait_time = sync_wait_time
        # Last forwarded log atom timestamp
        self.last_forward_timestamp = 0
        # The dictionary containing the currently active sources. Each entry is a list with two values:
        # * the largest timestamp of a LogAtom forwarded from this source so far.
        # * the current LogAtom pending to be forwarded or None if all atoms were forwarded
        self.sources_dict = {}
        # The local clock time when blocking was enabled for any source. Start in blocking mode to have chance to see atom from each
        # available source before forwarding the first ones.
        self.blocking_end_time = time.time() + self.sync_wait_time
        self.blocking_sources = 0
        self.timestamps_unsorted_flag = False
        self.last_forwarded_source = None
        self.buffer_empty_counter = 0

    def receive_atom(self, log_atom):
        if self.last_forwarded_source is not None and log_atom.source != self.last_forwarded_source and self.buffer_empty_counter < (
                2 * len(self.sources_dict.keys())):
            self.buffer_empty_counter += 1
            return False

        self.buffer_empty_counter = 0
        self.last_forwarded_source = None
        timestamp = log_atom.atom_time
        if timestamp is None:
            self.forward_atom(log_atom)
            self.last_forwarded_source = log_atom.source
            return True

        source_info = self.sources_dict.get(log_atom.source, None)
        if source_info is None:
            source_info = [timestamp, log_atom]
            self.sources_dict[log_atom.source] = source_info
        else:
            if timestamp < source_info[0]:
                # Atoms not sorted, not our problem. Forward it immediately.
                self.timestamps_unsorted_flag = True
                self.forward_atom(log_atom)
                self.last_forwarded_source = log_atom.source
                return True
            if source_info[1] is None:
                source_info[1] = log_atom

        # Source information with the oldest pending atom.
        oldest_source_info = None
        has_idle_sources_flag = False
        for source_info in self.sources_dict.values():
            if source_info[1] is None:
                has_idle_sources_flag = True
                continue
            if oldest_source_info is None:
                oldest_source_info = source_info
                continue
            if source_info[1].atom_time < oldest_source_info[1].atom_time:
                oldest_source_info = source_info
        if self.blocking_end_time != 0:
            # We cannot do anything while blocking to catch more atoms.
            if self.blocking_end_time > time.time():
                return False
            # Blocking has expired, cleanup the blockers.
            expired_sources = []
            for source, source_info in self.sources_dict.items():
                if source_info[1] is None:
                    expired_sources.append(source)
            for source in expired_sources:
                del self.sources_dict[source]
            self.blocking_end_time = 0
            self.blocking_sources = 0
            has_idle_sources_flag = False

        if has_idle_sources_flag:
            # We cannot let this item pass. Before entering blocking state, give all other sources also the chance to submit an atom.
            if self.blocking_sources == len(self.sources_dict):
                self.blocking_end_time = time.time() + self.sync_wait_time
            else:
                self.blocking_sources += 1
            return False

        # No idle sources, just forward atom from the oldest one if that is really the currently active source.
        if log_atom != oldest_source_info[1]:
            return False
        self.forward_atom(log_atom)
        self.last_forwarded_source = log_atom.source
        oldest_source_info[1] = None
        if timestamp > oldest_source_info[0]:
            oldest_source_info[0] = timestamp
        self.blocking_sources = 0
        return True

    def forward_atom(self, log_atom):
        """Forward atom to all atom handlers."""
        for handler in self.atom_handler_list:
            handler.receive_atom(log_atom)
