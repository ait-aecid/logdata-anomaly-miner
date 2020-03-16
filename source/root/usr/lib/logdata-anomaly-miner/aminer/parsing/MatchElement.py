"""This module provides only the MatchElement class to store results
from parser element matching process."""

class MatchElement(object):
  """This class allows storage and handling of data related to
  a match found by a model element."""

  def __init__(self, path, matchString, matchObject, children):
    """Initialize the MatchElement.
    @param path when None, this element is anonymous. Hence it
    cannot be added to the result data and cannot have children.
    @param matchString the part of the input bytes string covered
    by the given match.
    @param matchObject the matchString converted to an object for
    matchers detecting more complex data types, e.g., integer
    numbers or IP addresses."""
    if (not path) and children:
      raise Exception("Anonymous match may not have children")
    self.path = path
    self.matchString = matchString
    self.matchObject = matchObject
    self.children = children


  def getPath(self):
    """Get the path of this element.
    @return the path string."""
    return self.path


  def getMatchString(self):
    """Get the logatom string part this match element is matching."""
    return self.matchString


  def getMatchObject(self):
    """Get the matched data converted to an object of suitable type."""
    return self.matchObject


  def getChildren(self):
    """Get the submatch children of this match, if any.
    @return a list of submatches or None"""
    return self.children


  def annotateMatch(self, indentStr):
    """Annotate a given match element showing the match path elements
    and the parsed values.
    @param indentStr if None, all elements are separated just
    with a single space, no matter how deep the nesting level
    of those elements is. If not None, all elements are put into
    an own lines, that is prefixed by the given indentStr and
    indenting is increased by two spaces for earch level."""
    nextIndent = None
    result = None
    if indentStr is None:
      result = '%s: %s' % (self.path, repr(self.matchObject))
    else:
      result = '%s%s: %s' % (indentStr, self.path, repr(self.matchObject))
      nextIndent = indentStr+'  '
    if self.children != None:
      for childMatch in self.children:
        if nextIndent is None:
          result += ' '+childMatch.annotateMatch(None)
        else:
          result += '\n'+childMatch.annotateMatch(nextIndent)
    return result

  def serializeObject(self):
    """Create a serialization of this match element and all the
    children. With sane and unique path elements, the serialized
    object will also be unique."""
    chld = []
    if self.children:
      for childMatch in self.children:
        chld.append(childMatch.serializeObject())
    return {
        "path": self.path, "matchobject": self.matchObject,
        "matchString": self.matchString, "children": chld}

  def __str__(self):
    """Get a string representation of this match element excluding
    the children"""
    numChildren = 0
    if self.children != None:
      numChildren = len(self.children)
    return 'MatchElement: path = %s, string = %s, object = %s, children = %d' % (
        self.path, repr(self.matchString), repr(self.matchObject), numChildren)
