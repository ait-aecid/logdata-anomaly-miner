"""This module defines a log atom."""

class LogAtom:
  """This class defines a log atom used for parsing."""
  def __init__(self, raw_data, parser_match, atom_time, source):
    """Create a log atom from scratch."""
    self.raw_data = raw_data
    self.parser_match = parser_match
    self.atom_time = atom_time
    self.source = source

  def get_parser_match(self):
    """Get the parser match associated with this LogAtom.
    @return the match or None for (yet) unparsed LogAtoms."""
    return self.parser_match

  def set_timestamp(self, timestamp):
    """Update the default timestamp value associated with this
    LogAtom. The method can be called more than once to allow
    correction of fine-adjusting of timestamps by analysis filters
    after initial parsing procedure."""
    self.atom_time = timestamp

  def get_timestamp(self):
    """Get the default timestamp value for this LogAtom.
    @return the timestamp as number of seconds since 1970."""
    return self.atom_time

  def is_parsed(self):
    """Check if this atom is parsed by checking if parserMatch
    object is attached."""
    return self.parser_match is not None
