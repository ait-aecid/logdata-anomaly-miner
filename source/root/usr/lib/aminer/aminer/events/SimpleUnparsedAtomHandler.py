class SimpleUnparsedAtomHandler:

  def __init__(self, anomalyEventHandlers):
    self.anomalyEventHandlers=anomalyEventHandlers

  def receiveUnparsedAtom(self, atomData, unparsedAtomData, match):
    for listener in self.anomalyEventHandlers:
      listener.receiveEvent('ParserModel.UnparsedData', 'Unparsed data', [atomData], match)
