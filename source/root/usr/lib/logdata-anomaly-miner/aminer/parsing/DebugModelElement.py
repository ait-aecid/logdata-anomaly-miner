import sys

import MatchElement

class DebugModelElement:
  """This class defines a model element matching any data of length
  zero at any position. Thus it can never fail to match and can
  be inserted at any position in the parsing tree, where matching
  itself does not alter parsing flow (see e.g. FirstMatchModelElement).
  It will immediately write the current state of the match to
  stderr for inspection."""


  def __init__(self, id):
    self.id=id
# To avoid having those elements hidden in production configuration,
# write a line every time the class is instantiated.
    print >>sys.stderr, 'DebugModelElement %s added' % id

  def getChildElements(self):
    return(None)

  def getMatchElement(self, path, matchContext):
    """@return Always return a match."""
    print >>sys.stderr, 'DebugModelElement path="%s/%s", unmatched="%s"' % (path, self.id, matchContext.matchData)
    return(MatchElement.MatchElement('%s/%s' % (path, self.id),
        '', '', None))
