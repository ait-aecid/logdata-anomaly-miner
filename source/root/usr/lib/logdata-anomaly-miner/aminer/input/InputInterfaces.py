"""This file contains interface definition useful implemented by classes in this directory and for use from code outside this
directory. All classes are defined in separate files, only the namespace references are added here to simplify the code."""
import abc
import logging
from aminer.AMinerConfig import STAT_LEVEL, STAT_LOG_NAME, DEBUG_LEVEL, DEBUG_LOG_NAME


class AtomizerFactory(metaclass=abc.ABCMeta):
    """This is the common interface of all factories to create atomizers for new data sources and integrate them into the downstream
    processing pipeline."""

    @abc.abstractmethod
    def get_atomizer_for_resource(self, resource_name):
        """Get an atomizer for a given resource.
        @return a StreamAtomizer object"""


class StreamAtomizer(metaclass=abc.ABCMeta):
    """This is the common interface of all binary stream atomizers. Atomizers in general should be good detecting and reporting
    malformed atoms but continue to function by attempting error correction or resynchronization with the stream after the bad atom.
    This type of atomizer also signals a stream source when the stream data cannot be handled at the moment to throttle reading
    of the underlying stream."""

    @abc.abstractmethod
    def consume_data(self, stream_data, end_of_stream_flag=False):
        """Consume data from the underlying stream for atomizing. Data should only be consumed after splitting of an atom. The
        caller has to keep unconsumed data till the next invocation.
        @param stream_data the data offered to be consumed or zero length data when endOfStreamFlag is True (see below).
        @param end_of_stream_flag this flag is used to indicate, that the streamData offered is the last from the input stream.
        If the streamData does not form a complete atom, no rollover is expected or rollover would have honoured the atom boundaries,
        then the StreamAtomizer should treat that as an error. With rollover, consuming of the stream end data will signal the
        invoker to continue with data from next stream. When end of stream was reached but invoker has no streamData to send,
        it will invoke this method with zero-length data, which has to be consumed with a zero-length reply.
        @return the number of consumed bytes, 0 if the atomizer would need more data for a complete atom or -1 when no data was
        consumed at the moment but data might be consumed later on. The only situation where 0 is not an allowed return value
        is when endOfStreamFlag is set and streamData not empty."""


class AtomHandlerInterface(metaclass=abc.ABCMeta):
    """This is the common interface of all handlers suitable for receiving log atoms."""
    log_success = 0
    log_total = 0

    @abc.abstractmethod
    def receive_atom(self, log_atom):
        """Receive a log atom from a source.
        @param log_atom binary raw atom data
        @return True if this handler was really able to handle and process the atom. Depending on this information, the caller
        may decide if it makes sense passing the atom also to other handlers or to retry later. This behaviour has to be documented
        at each source implementation sending LogAtoms."""

    def log_statistics(self, component_name):
        """log statistics of an AtomHandler. Override this method for more sophisticated statistics output of the AtomHandler.
        @param component_name the name of the component which is printed in the log line."""
        if STAT_LEVEL > 0:
            logging.getLogger(STAT_LOG_NAME).info("'%s' could process %d out of %d log atoms successfully in the last 60"
                                                  " minutes." % (component_name, self.log_success, self.log_total))
        self.log_success = 0
        self.log_total = 0

    def log_debug(self, msg, level):
        """logs debug messages if the needed DEBUG_LEVEL is set. 0 means no debug at all. 1 means normal debug with logging.INFO and
        above. 2 means verbose debug output with all levels allowed (logging.DEBUG and above)"""
