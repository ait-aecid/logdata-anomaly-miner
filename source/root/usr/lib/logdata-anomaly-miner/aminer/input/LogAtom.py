class LogAtom:
  def __init__(self, rawData, parserMatch, atomTime, source):
    """Create a log atom from scratch."""
    self.rawData=rawData
    self.parserMatch=parserMatch
    self.atomTime=atomTime
    self.source=source

  def setTimestamp(self, timestamp):
    """Update the default timestamp value associated with this
    LogAtom. The method can be called more than once to allow
    correction of fine-adjusting of timestamps by analysis filters
    after initial parsing procedure."""
    self.atomTime=timestamp

  def getTimestamp(self):
    """Get the default timestamp value for this LogAtom.
    @return the timestamp as number of seconds since 1970."""
    return(self.atomTime)

  def isParsed(self):
    """Check if this atom is parsed by checking if parserMatch
    object is attached."""
    return(self.parserMatch!=None)
