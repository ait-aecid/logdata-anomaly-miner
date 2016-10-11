from aminer.input import UnparsedAtomHandler

class SimpleUnparsedAtomHandler(UnparsedAtomHandler):
  """Handlers of this class will just forward received unparsed
  atoms to the registered event handlers."""

  def __init__(self, eventHandlers):
    self.eventHandlers=eventHandlers

  def receiveUnparsedAtom(self, message, atomData, unparsedAtomData,
      parserMatch):
    for listener in self.eventHandlers:
      listener.receiveEvent('Input.UnparsedAtomHandler', message,
          [atomData], [unparsedAtomData, parserMatch], self)
    return(True)
