"""This module defines a detector for log atoms not matching
any whitelisted rule."""

import os

from aminer.input import AtomHandlerInterface
from aminer.analysis import CONFIG_KEY_LOG_LINE_PREFIX

class WhitelistViolationDetector(AtomHandlerInterface):
  """Objects of this class handle a list of whitelist rules to
  ensure, that each received log-atom is at least covered by a
  single whitelist rule. To avoid traversing the complete rule
  tree more than once, the whitelist rules may have match actions
  attached that set off an alarm by themselves."""

  def __init__(self, aminerConfig, whitelistRules, anomalyEventHandlers, outputLogLine=True):
    """Initialize the detector.
    @param whitelistRules list of rules executed in same way as
    inside Rules.OrMatchRule."""
    self.whitelistRules = whitelistRules
    self.anomalyEventHandlers = anomalyEventHandlers
    self.outputLogLine = outputLogLine
    self.aminerConfig = aminerConfig

  def receiveAtom(self, logAtom):
    """Receive on parsed atom and the information about the parser
    match.
    @param logAtom atom with parsed data to check
    @return True when logAtom is whitelisted, False otherwise."""
    eventData = dict()
    for rule in self.whitelistRules:
      if rule.match(logAtom):
        return True
    if self.outputLogLine:
      originalLogLinePrefix = self.aminerConfig.configProperties.get(CONFIG_KEY_LOG_LINE_PREFIX)
      if originalLogLinePrefix is None:
          originalLogLinePrefix = ''
      sortedLogLines = [logAtom.parserMatch.matchElement.annotateMatch('')+os.linesep+ 
        originalLogLinePrefix+repr(logAtom.rawData)]
    else:
      sortedLogLines = [logAtom.parserMatch.matchElement.annotateMatch('')]
    for listener in self.anomalyEventHandlers:
      listener.receiveEvent('Analysis.%s' % self.__class__.__name__, \
          'No whitelisting for current atom', sortedLogLines, eventData, logAtom, self)
    return False
