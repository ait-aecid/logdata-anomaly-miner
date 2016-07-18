# This file contains various methods and class definitions useful
# for various components from parsing, analysis and event handling.
# Larger separate blocks of code should be split into own subfiles
# or submodules, e.g. persistency.

import random

def getLogInt(maxBits):
  """Get a log-distributed random integer integer in range 0 to
  maxBits-1."""
  randBits=random.randint(0, (1<<maxBits)-1)
  result=0
  while (randBits&1)!=0:
    result+=1
    randBits>>=1
  return(result)


class LogarithmicBackoffHistory:
  """This class keeps a history list of items with logarithmic
  storage characteristics. When adding objects, the list will
  be filled to the maximum size with the newest items at the end.
  When filled, adding a new element will move with probability
  1/2 the last element to the next lower position before putting
  the new item to the end position. With a chance of 1/4, the
  last 2 elements are moved, with 1/8 the last 3, ... Thus the
  list will in average span a time range of 2^maxItems items with
  growing size of holes towards the earliest element."""
  def __init__(self, maxItems, initialList=[]):
    self.maxItems=maxItems
    if len(initialList)>maxItems: initialList=initialList[:maxItems]
    self.history=initialList

  def addObject(self, newObject):
    """Add a new object to the list according to the rules described
    in the class docstring."""
    if len(self.history)<self.maxItems:
      self.history.append(newObject)
    else:
      movePos=getLogInt(self.maxItems)
      if movePos!=0:
        self.history=self.history[:self.maxItems-movePos]+self.history[self.maxItems+1-movePos:]+[newObject]
      else:
        self.history[-1]=newObject

  def getHistory(self):
    """Get the whole history list. Make sure to clone the list
    before modification when influences on this object are not
    intended."""
    return(self.history)
