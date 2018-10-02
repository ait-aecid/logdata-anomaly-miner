"""This module defines a factory for instanciating line atomizers."""

from aminer.input import AtomizerFactory
from aminer.input.ByteStreamLineAtomizer import ByteStreamLineAtomizer

class SimpleByteStreamLineAtomizerFactory(AtomizerFactory):
  """This factory just creates the same atomizer for each new
  resource. All parsed and unparsed atoms are delivered via two
  lists of handlers."""

  def __init__(self, parsingModel, atomHandlerList, eventHandlerList,
               defaultTimestampPath=None):
    """Create the factory to forward data and events to the given
    lists for each newly created atomizer.
    @param defaultTimestampPath if not None, the value of this
    timestamp field is extracted from parsed atoms and stored
    as default timestamp for that atom."""
    self.parsingModel = parsingModel
    self.atomHandlerList = atomHandlerList
    self.eventHandlerList = eventHandlerList
    self.defaultTimestampPath = defaultTimestampPath

  def getAtomizerForResource(self, resourceName):
    """Get an atomizer for a given resource.
    @param resourceName the resource name for atomizer selection
    is ignored in this type of factory.
    @return a StreamAtomizer object"""
    return ByteStreamLineAtomizer(self.parsingModel, self.atomHandlerList, \
        self.eventHandlerList, 1 << 16, self.defaultTimestampPath)
