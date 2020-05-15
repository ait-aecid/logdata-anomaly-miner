"""This module defines various interfaces for log atom parsing
and namespace shortcuts to the ModelElements."""


class ModelElementInterface:
  """This is the superinterface of all model elements."""

  # skipcq: PYL-R0201
  def get_id(self):
    """Get the element ID."""
    raise Exception('Interface method called')

  # skipcq: PYL-R0201
  def get_child_elements(self):
    """Get all possible child model elements of this element.
    If this element implements a branching model element, then
    not all child element IDs will be found in matches produced
    by getMatchElement.
    @return a list with all children"""
    raise Exception('Interface method called')

  def get_match_element(self, path, match_context):
    """Try to find a match on given data for this model element
    and all its children. When a match is found, the matchContext
    is updated accordingly.
    @param path the model path to the parent model element invoking
    this method.
    @param match_context an instance of MatchContext class holding
    the data context to match against.
    @return the match_element or None if model did not match."""


from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement  # skipcq: FLK-E402
from aminer.parsing.Base64StringModelElement import Base64StringModelElement  # skipcq: FLK-E402
from aminer.parsing.DateTimeModelElement import DateTimeModelElement  # skipcq: FLK-E402
from aminer.parsing.DebugModelElement import DebugModelElement  # skipcq: FLK-E402
from aminer.parsing.DecimalFloatValueModelElement import DecimalFloatValueModelElement  # skipcq: FLK-E402
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement  # skipcq: FLK-E402
from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement  # skipcq: FLK-E402
from aminer.parsing.ElementValueBranchModelElement import ElementValueBranchModelElement  # skipcq: FLK-E402
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement  # skipcq: FLK-E402
from aminer.parsing.FixedDataModelElement import FixedDataModelElement  # skipcq: FLK-E402
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement  # skipcq: FLK-E402
from aminer.parsing.HexStringModelElement import HexStringModelElement  # skipcq: FLK-E402
from aminer.parsing.IpAddressDataModelElement import IpAddressDataModelElement  # skipcq: FLK-E402
from aminer.parsing.MatchContext import DebugMatchContext  # skipcq: FLK-E402
from aminer.parsing.MatchContext import MatchContext  # skipcq: FLK-E402
from aminer.parsing.MatchElement import MatchElement  # skipcq: FLK-E402
from aminer.parsing.MultiLocaleDateTimeModelElement import MultiLocaleDateTimeModelElement  # skipcq: FLK-E402
from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement  # skipcq: FLK-E402
from aminer.parsing.ParserMatch import ParserMatch  # skipcq: FLK-E402
from aminer.parsing.RepeatedElementDataModelElement import RepeatedElementDataModelElement  # skipcq: FLK-E402
from aminer.parsing.SequenceModelElement import SequenceModelElement  # skipcq: FLK-E402
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement  # skipcq: FLK-E402
from aminer.parsing.WhiteSpaceLimitedDataModelElement import WhiteSpaceLimitedDataModelElement  # skipcq: FLK-E402
