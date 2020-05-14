"""This module defines a factory for instanciating line atomizers."""

from aminer.input import AtomizerFactory
from aminer.input.ByteStreamLineAtomizer import ByteStreamLineAtomizer


class SimpleByteStreamLineAtomizerFactory(AtomizerFactory):
  """This factory just creates the same atomizer for each new
  resource. All parsed and unparsed atoms are delivered via two
  lists of handlers."""

  def __init__(self, parsing_model, atom_handler_list, event_handler_list,
               default_timestamp_path=None):
    """Create the factory to forward data and events to the given
    lists for each newly created atomizer.
    @param default_timestamp_path if not None, the value of this
    timestamp field is extracted from parsed atoms and stored
    as default timestamp for that atom."""
    self.parsing_model = parsing_model
    self.atom_handler_list = atom_handler_list
    self.event_handler_list = event_handler_list
    self.default_timestamp_path = default_timestamp_path

  def get_atomizer_for_resource(self, resource_name):
    """Get an atomizer for a given resource.
    @param resource_name the resource name for atomizer selection
    is ignored in this type of factory.
    @return a StreamAtomizer object"""
    return ByteStreamLineAtomizer(self.parsing_model, self.atom_handler_list, self.event_handler_list, 1 << 16, self.default_timestamp_path)
