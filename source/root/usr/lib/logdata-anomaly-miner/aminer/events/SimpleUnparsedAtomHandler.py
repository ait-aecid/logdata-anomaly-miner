from aminer.events import EventHandlerInterface

class SimpleUnparsedAtomHandler(EventHandlerInterface):
  """Handlers of this class will just forward received unparsed
  atoms to the registered event handlers."""

  def __init__(self, eventHandlers):
    self.eventHandlers=eventHandlers

  def receiveUnparsedAtom(self, atomData, unparsedAtomData, match):
    for listener in self.eventHandlers:
      listener.receiveEvent('ParserModel.UnparsedData', 'Unparsed data',
          [atomData], match, self)
