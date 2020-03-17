"""This moduel defines a debug model element that can be used to
check whether a specific poistion in the parsing tree is reached
by log atoms."""

import sys

from aminer.parsing.MatchElement import MatchElement
from aminer.parsing import ModelElementInterface

class DebugModelElement(ModelElementInterface):
  """This class defines a model element matching any data of length
  zero at any position. Thus it can never fail to match and can
  be inserted at any position in the parsing tree, where matching
  itself does not alter parsing flow (see e.g. FirstMatchModelElement).
  It will immediately write the current state of the match to
  stderr for inspection."""


  def __init__(self, element_id):
    self.element_id = element_id
# To avoid having those elements hidden in production configuration,
# write a line every time the class is instantiated.
    print('DebugModelElement %s added' % element_id, file=sys.stderr)

  def get_child_elements(self):
    """Get all possible child model elements of this element.
    @return empty list as there are no children of this element."""
    return None

  def get_match_element(self, path, match_context):
    """@return Always return a match."""
    print('DebugModelElement path = "%s/%s", unmatched = "%s"' % \
          (path, self.element_id, repr(match_context.matchData)), file=sys.stderr)
    return MatchElement('%s/%s' % (path, self.element_id), \
        '', '', None)
