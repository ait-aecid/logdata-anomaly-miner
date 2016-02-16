import datetime

class WhitelistViolationDetector:
  """This class allows to handle a list of whitelist rules to
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
      listener.receiveEvent('Analysis.WhitelistViolationDetector', 'No whitelisting for current atom', [atomData], parserMatch)

  def checkTriggers(self):
    return(1<<16)


class MatchAction:
  """This is the interface of all match actions."""
  def performAction(parserMatch):
    pass


class ViolationAction(MatchAction):
  """Export the violation action so that can also be added to
  the ruleset for triggering on selected rule matches."""
  def __init__(self, anomalyEventHandlers):
    self.anomalyEventHandlers=anomalyEventHandlers

  def performAction(self, parserMatch):
    for listener in self.anomalyEventHandlers:
      listener.receiveEvent('Analysis.WhitelistViolationDetector', 'Violation detected', [parserMatch.matchString], parserMatch)
