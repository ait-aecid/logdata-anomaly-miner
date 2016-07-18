# This file contains interface definition useful implemented by
# classes in this directory and for use from code outside this
# directory. All classes are defined in separate files, only the
# namespace references are added here to simplify the code.

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
