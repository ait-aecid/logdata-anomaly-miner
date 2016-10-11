# This file contains interface definition useful implemented by
# classes in this directory and for use from code outside this
# directory. All classes are defined in separate files, only the
# namespace references are added here to simplify the code.

class AtomizerFactory:
  """This is the common interface of all factories to create atomizers
  for new data sources and integrate them into the downstream
  processing pipeline."""

  def getAtomizerForResource(self, resourceName):
    """Get an atomizer for a given resource.
    @return a StreamAtomizer object"""
    raise Exception('Interface method called')


class StreamAtomizer:
  """This is the common interface of all binary stream atomizers.
  Atomizers in general should be good detecting and reporting
  malformed atoms but continue to function by attempting error
  correction or resynchronization with the stream after the bad
  atom.
  This type of atomizer also signals a stream source when the
  stream data cannot be handled at the moment to throttle reading
  of the underlying stream."""

  def consumeData(self, streamData, endOfStreamFlag=False):
    """Consume data from the underlying stream for atomizing.
    Data should only be consumed after splitting of an atom. The
    caller has to keep unconsumed data till the next invocation.
    @param streamData the data offered to be consumed or zero
    length data when endOfStreamFlag is True (see below).
    @param endOfStreamFlag this flag is used to indicate, that
    the streamData offered is the last from the input stream.
    If the streamData does not form a complete atom, no rollover
    is expected or rollover would have honoured the atom boundaries,
    then the StreamAtomizer should treat that as an error. With
    rollover, consuming of the stream end data will signal the
    invoker to continue with data from next stream. When end of
    stream was reached but invoker has no streamData to send,
    it will invoke this method with zero-length data, which has
    to be consumed with a zero-length reply.
    @return the number of consumed bytes, 0 if the atomizer would
    need more data for a complete atom or -1 when no data was
    consumed at the moment but data might be consumed later on.
    The only situation where 0 is not an allowed return value
    is when endOfStreamFlag is set and streamData not empty."""
    raise Exception('Interface method called')

class UnparsedAtomHandler:
  """This is the common interface of all handlers of unparsed
  data."""

  def receiveUnparsedAtom(self, message, atomData, unparsedAtomData,
      parserMatch):
    """Receive information about a single unparsed atom.
    @param message message indicating the cause of parsing failure.
    @param atomData the full atom data as analyzed by the parser.
    When atomizing did not work or an atom was truncated, the
    data might be shorter than expected.
    @param unparsedAtomData the part of atomData that did not
    match any parsing procedures. A parser not working from the
    ends of atomData, thus carving out multiple unparsed parts
    from atomData may use a list of strings, otherwise a single
    string should be used. When detection of parsed and unparsed
    parts was not possible, None should be given.
    @param the incomplete match structure if the parser supports
    such operation mode, None otherwise."""
    raise Exception('Interface method called')


from ByteStreamLineAtomizer import ByteStreamLineAtomizer
from LogStream import LogDataResource
from LogStream import LogStream
from SimpleByteStreamLineAtomizerFactory import SimpleByteStreamLineAtomizerFactory
from SimpleUnparsedAtomHandler import SimpleUnparsedAtomHandler
