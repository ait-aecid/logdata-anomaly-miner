"""This module defines a model element that allows branches
depending on the value of the previous model value."""

from aminer.parsing import ModelElementInterface
from aminer.parsing.MatchElement import MatchElement

class ElementValueBranchModelElement(ModelElementInterface):
  """This class defines an element that selects a branch path
  based on a previous model value."""

  def __init__(self, elementId, valueModel, valuePath, branchModelDict,
               defaultBranch=None):
    """Create the branch model element.
    @param valuePath the relative path to the target value from
    the valueModel element on. When the path does not resolve
    to a value, this model element will not match. A path value
    of None indicates, that the match element of the valueModel
    should be used directly.
    @param branchModelDict a dictionary to select a branch for
    the value identified by valuePath.
    @param defaultBranch when lookup in branchModelDict fails,
    use this as default branch or fail when None."""
    self.elementId = elementId
    self.valueModel = valueModel
    self.valuePath = valuePath
    self.branchModelDict = branchModelDict
    self.defaultBranch = defaultBranch

  def getId(self):
    """Get the element ID."""
    return self.elementId

  def get_child_elements(self):
    """Get all possible child model elements of this element.
    If this element implements a branching model element, then
    not all child element IDs will be found in matches produced
    by getMatchElement.
    @return a list with all children"""
    allChildren = [self.valueModel]+list(self.branchModelDict.values())
    if self.defaultBranch is not None:
      allChildren.append(self.defaultBranch)
    return allChildren

  def get_match_element(self, path, matchContext):
    """Try to find a match on given data for the test model and
    the selected branch.
    @param path the model path to the parent model element invoking
    this method.
    @param matchContext an instance of MatchContext class holding
    the data context to match against.
    @return the matchElement or None if the test model did not
    match, no branch was selected or the branch did not match."""
    currentPath = "%s/%s" % (path, self.elementId)
    startData = matchContext.matchData
    modelMatch = self.valueModel.get_match_element(currentPath, matchContext)
    if modelMatch is None:
      return None

# Now extract the test path value from the modelMatch. From here
# on, the matchContext is already modified so we must NEVER just
# return but revert the changes in the context first.
    remainingValuePath = self.valuePath
    testMatch = modelMatch
    currentTestPath = testMatch.getPath()
    while remainingValuePath is not None:
      nextPartPos = remainingValuePath.find('/')
      if nextPartPos <= 0:
        currentTestPath += '/'+remainingValuePath
        remainingValuePath = None
      else:
        currentTestPath += '/'+remainingValuePath[:nextPartPos]
        remainingValuePath = remainingValuePath[nextPartPos+1:]
      matchChildren = testMatch.getChildren()
      testMatch = None
      if matchChildren is None:
        break
      for child in matchChildren:
        if child.getPath() == currentTestPath:
          testMatch = child
          break

    branchMatch = None
    if testMatch is not None:
      if isinstance(testMatch.getMatchObject(), bytes):
        branchModel = self.branchModelDict.get(testMatch.getMatchObject().decode(), \
          self.defaultBranch)
      else:
        branchModel = self.branchModelDict.get(testMatch.getMatchObject(), \
          self.defaultBranch)
      if branchModel is not None:
        branchMatch = branchModel.get_match_element(currentPath, matchContext)
    if branchMatch is None:
      matchContext.matchData = startData
      return None
    return MatchElement(currentPath, \
        startData[:len(startData)-len(matchContext.matchData)], \
        startData[:len(startData)-len(matchContext.matchData)], [modelMatch, branchMatch])
