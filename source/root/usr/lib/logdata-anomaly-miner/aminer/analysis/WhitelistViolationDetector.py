import datetime

from aminer.input import AtomHandlerInterface


class WhitelistViolationDetector(AtomHandlerInterface):
  """Objects of this class handle a list of whitelist rules to
  ensure, that each received log-atom is at least covered by a
  single whitelist rule. To avoid traversing the complete rule
  tree more than once, the whitelist rules may have match actions
  attached that set off an alarm by themselves."""

  def __init__(self, whitelistRules, anomalyEventHandlers):
    """Initialize the detector.
    @param whitelistRules list of rules executed in same way as
    inside Rules.OrMatchRule."""
    self.whitelistRules=whitelistRules
    self.anomalyEventHandlers=anomalyEventHandlers

  def receiveAtom(self, logAtom):
    """Receive on parsed atom and the information about the parser
    match.
    @param logAtom atom with parsed data to check
    @return True when logAtom is whitelisted, False otherwise."""
    for rule in self.whitelistRules:
      if rule.match(logAtom): return(True)
    for listener in self.anomalyEventHandlers:
      listener.receiveEvent('Analysis.%s' % self.__class__.__name__,
          'No whitelisting for current atom', [logAtom.rawData], logAtom, self)
    return(False)
