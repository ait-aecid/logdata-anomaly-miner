# Add also the namespace references to classes defined in this
# directory.

class ModelElementInterface:
  """This is the superinterface of all model elements."""

  def getId(self):
    """Get the element ID."""
    raise Exception('Interface method called')

  def getChildElements(self):
    """Get all possible child model elements of this element.
    If this element implements a branching model element, then
    not all child element IDs will be found in mathces produced
    by getMatchElement.
    @return a list with all children"""
    raise Exception('Interface method called')

  def getMatchElement(self, path, matchContext):
    """Try to find a match on given data for this model element
    and all its children. When a match is found, the matchContext
    is updated accordingly.
    @param path the model path to the parent model element invoking
    this method.
    @param matchContext an instance of MatchContext class holding
    the data context to match against.
    @return the matchElement or None if model did not match."""


from AnyByteDataModelElement import AnyByteDataModelElement
from DateTimeModelElement import DateTimeModelElement
from DebugModelElement import DebugModelElement
from DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from DelimitedDataModelElement import DelimitedDataModelElement
from FirstMatchModelElement import FirstMatchModelElement
from FixedDataModelElement import FixedDataModelElement
from FixedWordlistDataModelElement import FixedWordlistDataModelElement
from HexStringModelElement import HexStringModelElement
from IpAddressDataModelElement import IpAddressDataModelElement
from MatchContext import DebugMatchContext
from MatchContext import MatchContext
from MatchElement import MatchElement
from MultiLocaleDateTimeModelElement import MultiLocaleDateTimeModelElement
from OptionalMatchModelElement import OptionalMatchModelElement
from ParserMatch import ParserMatch
from RepeatedElementDataModelElement import RepeatedElementDataModelElement
from SequenceModelElement import SequenceModelElement
from VariableByteDataModelElement import VariableByteDataModelElement
from WhiteSpaceLimitedDataModelElement import WhiteSpaceLimitedDataModelElement
