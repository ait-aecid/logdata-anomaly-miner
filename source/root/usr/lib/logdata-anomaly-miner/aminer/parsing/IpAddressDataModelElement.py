"""This module defines a model element that represents an IP
address."""

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface

class IpAddressDataModelElement(ModelElementInterface):
  """This class defines a model element that matches an IPv4 IP
  address."""
  def __init__(self, elementId):
    """Create an element to match IPv4 IP addresses."""
    self.elementId = elementId

  def get_child_elements(self):
    """Get all possible child model elements of this element.
    @return None as there are no children of this element."""
    return None

  def get_match_element(self, path, matchContext):
    """Read an IP address at the current data position. When found,
    the matchObject will be """
    data = matchContext.matchData

    numberCount = 0
    digitCount = 0
    matchLen = 0
    extractedAddress = 0
    for testByte in data:
      matchLen += 1
      if testByte in b'0123456789':
        digitCount += 1
        continue
      if digitCount == 0:
        return None

      ipBits = int(data[matchLen-digitCount-1:matchLen-1])
      if ipBits > 0xff:
        return None
      extractedAddress = (extractedAddress << 8)|ipBits
      digitCount = 0
      numberCount += 1
      if numberCount == 4:
# We are now after the first byte not belonging to the IP. So
# go back one step
        matchLen -= 1
        break
      if testByte != ord(b'.'):
        return None

    if digitCount != 0:
      ipBits = int(data[matchLen-digitCount:matchLen])
      if ipBits > 0xff:
        return None
      extractedAddress = (extractedAddress << 8)|ipBits

    matchString = data[:matchLen]
    matchContext.update(matchString)
    return MatchElement("%s/%s" % (path, self.elementId), \
        matchString, extractedAddress, None)
