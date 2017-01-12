"""This module provides base64 string matching."""

import base64

from aminer.parsing import ModelElementInterface
from aminer.parsing import MatchElement

class Base64StringModelElement(ModelElementInterface):
  """This class just tries to strip off as many base64 bytes as
  possible from a given data string."""
  def __init__(self, pathId):
    self.pathId = pathId

  def getChildElements(self):
    return None

  def getMatchElement(self, path, matchContext):
    """Find the maximum number of bytes forming a integer number
    according to the parameters specified
    @return a match when at least one byte being a digit was found"""
    data = matchContext.matchData
    matchLen = 0
    atEndFlag = False
    for testByte in data:
      bVal = ord(testByte)
      if atEndFlag:
        if ((matchLen&0x3) == 0) or (bVal != 0x3d):
          break
      elif (not ((bVal >= 0x30) and (bVal <= 0x39)) and
            not ((bVal >= 0x41) and (bVal <= 0x5a)) and
            not ((bVal >= 0x61) and (bVal <= 0x7a)) and
            (bVal not in [0x2b, 0x2f])):
        if (bVal != 0x3d) or ((matchLen&0x2) == 0):
          break
        atEndFlag = True
      matchLen += 1

    matchLen = matchLen&(-4)
    if matchLen == 0:
      return None

    matchString = data[:matchLen]
    matchContext.update(matchString)
    return MatchElement.MatchElement(
        "%s/%s" % (path, self.pathId), matchString,
        base64.b64decode(matchString), None)
