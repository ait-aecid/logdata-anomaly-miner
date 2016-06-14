import MatchElement

"""This class allows storage of data relevant during the matching
process, e.g. the root node and the remaining unmatched data.
Then searching for non-atomic matches, e.g. sequences, the context
might be modified by model subelements, even if the main model
element will not return a match. In that case, those non-atomic
model elements have to care to restore the context before returning.
"""
class MatchContext:
  """@param matchData the data that will be tested by the mext
model element."""
  def __init__(self, matchData):
    self.matchData=matchData
    self.rootMatchElement=MatchElement.MatchElement('/', None, None, [])

  def update(self, matchString):
    self.matchData=self.matchData[len(matchString):]
