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
  def __init__(self, maxItems, initialList=[]):
    self.maxItems=maxItems
    if len(initialList)>maxItems: initialList=initialList[:maxItems]
    self.history=initialList
  
  def addObject(self, newObject):
    if len(self.history)<self.maxItems:
      self.history.append(newObject)
    else:
      movePos=getLogInt(self.maxItems)
      if movePos!=0:
        self.history=self.history[:self.maxItems-movePos]+self.history[self.maxItems+1-movePos:]+[newObject]

  def getHistory(self):
    return(self.history)
