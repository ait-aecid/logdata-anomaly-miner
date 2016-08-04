import datetime

from aminer.parsing import ParsedAtomHandlerInterface


class WhitelistViolationDetector(ParsedAtomHandlerInterface):
  """Objects of this class handle a list of whitelist rules to
  ensure, that each received log-atom is at least covered by a
  single whitelist rule. To avoid traversing the complete rule
  tree more than once, the whitelist rules may have match actions
  attached that set off an alarm by themselves."""

  def __init__(self, whitelistRules, anomalyEventHandlers):
    """Initialize the detector.
    @param whitelistRules: list 
    """
    self.whitelistRules=whitelistRules
    self.anomalyEventHandlers=anomalyEventHandlers

  def receiveParsedAtom(self, atomData, parserMatch):
    for rule in self.whitelistRules:
      if rule.match(parserMatch): return
    for listener in self.anomalyEventHandlers:
      listener.receiveEvent('Analysis.%s' % self.__class__.__name__,
          'No whitelisting for current atom', [atomData], parserMatch, self)
