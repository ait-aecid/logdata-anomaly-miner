"""This class defines various handler interfaces for handling
of raw, parsed and unparsed atoms."""

class ParsedAtomHandlerInterface:
  """This is the common interface of all handlers suitable for
  receiving of parsed atoms."""

  def receiveParsedAtom(self, atomData, match):
    """Receive on parsed atom and the information about the parser
    match.
    @return True if this handler was really able to handle and
    process the match. Depending on this information, the caller
    may decide if it makes sense passing the parsed atom also
    to other handlers."""
    raise Exception('Not implemented')
