# This file contains interface definition useful implemented by
# classes in this directory and for use from code outside this
# directory. All classes are defined in separate files, only the
# namespace references are added here to simplify the code.


class ParsedAtomHandlerInterface:
  """This is the common interface of all handlers suitable for
  receiving of parsed atoms."""

  def receiveParsedAtom(self, atomData, parserMatch):
    """Receive on parsed atom and the information about the parser
    match.
    @param atomData binary raw atom data
    @param parserMatch for atomData
    @return True if this handler was really able to handle and
    process the match. Depending on this information, the caller
    may decide if it makes sense passing the parsed atom also
    to other handlers."""
    raise Exception('Interface method called')


# Add also the namespace references to classes defined in this
# directory.

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
