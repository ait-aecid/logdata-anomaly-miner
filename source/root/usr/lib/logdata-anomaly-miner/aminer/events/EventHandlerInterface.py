class EventHandlerInterface:
  """This is the common interface of all components that can be
  notified on significant log data mining events. To avoid interference
  with the analysis process, the listener may only perform fast
  actions within the call. Longer running tasks have to be performed
  asynchronously."""

  def receiveEvent(self, eventType, eventMessage, sortedLogLines, eventData):
    """Receive information about a detected event.
    @param eventType is a string with the event type class this
    event belongs to. This information can be used to interpret
    type-specific eventData objects. Together with the eventMessage
    and sortedLogLines, this can be used to create generic log messages.
    @param sortedLogLines sorted list of log lines that were considered
    when generating the event, as far as available to the time
    of the event. The list has to contain at least one line.
    @param eventData type-specific event data object, should not
    be used unless listener really knows about the eventType."""
    raise Exception('Not implemented')


  def checkTriggers(self):
    """This method is triggered at least each minute to perform
    cleanup operation triggers."""
    raise Exception('Not implemented')
