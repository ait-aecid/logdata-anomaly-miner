"""This module contains classes for execution of py child
process main analysis loop."""

import base64
import errno
import fcntl
import json
import os
import select
import socket
import struct
import sys
import time
import traceback
import resource
import subprocess
import logging

from aminer import AMinerConfig
from aminer.input.LogStream import LogStream
from aminer.util import PersistencyUtil
from aminer.util import SecureOSFunctions
from aminer.util import TimeTriggeredComponentInterface
from aminer.util import JsonUtil
from builtins import str
from aminer.AMinerRemoteControlExecutionMethods import AMinerRemoteControlExecutionMethods


class AnalysisContext:
  """This class collects information about the current analysis
  context to access it during analysis or remote management."""

  TIME_TRIGGER_CLASS_REALTIME = 1
  TIME_TRIGGER_CLASS_ANALYSISTIME = 2

  def __init__(self, aminer_config):
    self.aminer_config = aminer_config
# This is the factory to create atomiziers for incoming data streams
# and link them to the analysis pipeline.
    self.atomizer_factory = None
# This is the current log processing and analysis time regarding
# the data stream being analyzed. While None, the analysis time
# e.g. used to trigger components (see analysisTimeTriggeredComponents),
# is the same as current system time. For forensic analysis this
# time has to be updated to values derived from the log data input
# to reflect the current log processing time, which will be in
# the past and may progress much faster than real system time.
    self.analysis_time = None
# Keep a registry of all analysis and filter configuration for
# later use. Remote control interface may then access them for
# runtime reconfiguration.
    self.next_registry_id = 0
    self.registered_components = {}
# Keep also a list of components by name.
    self.registered_components_by_name = {}
# Keep lists of components that should receive timer interrupts
# when real time or analysis time has elapsed.
    self.real_time_triggered_components = []
    self.analysis_time_triggered_components = []
    
    logging.basicConfig(filename=AMinerConfig.LOG_FILE, level=logging.DEBUG,
      format='%(asctime)s %(levelname)s %(message)s', datefmt='%d.%m.%Y %H:%M:%S')
    logging.info("AMiner started.")

  def add_time_triggered_component(self, component, trigger_class=None):
    """Add a time-triggered component to the registry."""
    if not isinstance(component, TimeTriggeredComponentInterface):
      raise Exception('Attempting to register component of class %s not implementing aminer.util.TimeTriggeredComponentInterface' % (
              component.__class__.__name__))
    if trigger_class is None:
      trigger_class = component.get_time_trigger_class()
    if trigger_class == AnalysisContext.TIME_TRIGGER_CLASS_REALTIME:
      self.real_time_triggered_components.append(component)
    elif trigger_class == AnalysisContext.TIME_TRIGGER_CLASS_ANALYSISTIME:
      self.analysis_time_triggered_components.append(component)
    else:
      raise Exception('Attempting to timer component for unknown class %s' % trigger_class)

  def register_component(self, component, component_name=None, register_time_trigger_class_override=None):
    """Register a new component. A component implementing the
    TimeTriggeredComponentInterface will also be added to the
    appropriate lists unless registerTimeTriggerClassOverride
    is specified.
    @param component_name an optional name assigned to the
    component when registering. When no name is specified,
    the detector class name plus an identifier will be used.
    When a component with the same name was already
    registered, this will cause an error.
    @param register_time_trigger_class_override if not none, ignore
    the time trigger class supplied by the component and register
    it for the classes specified in the override list. Use an
    empty list to disable registration."""
    if component_name is None:
      component_name = str(component.__class__.__name__) + str(self.next_registry_id)
    if component_name in self.registered_components_by_name:
      raise Exception('Component with same name already registered')
    if register_time_trigger_class_override is not None and not isinstance(component, TimeTriggeredComponentInterface):
      raise Exception('Requesting override on component not implementing TimeTriggeredComponentInterface')

    self.registered_components[self.next_registry_id] = (component, component_name)
    self.next_registry_id += 1
    self.registered_components_by_name[component_name] = component
    if isinstance(component, TimeTriggeredComponentInterface):
      if register_time_trigger_class_override is None:
        self.add_time_triggered_component(component)
      else:
        for trigger_class in register_time_trigger_class_override:
          self.add_time_triggered_component(component, trigger_class)

  def get_registered_component_ids(self):
    """Get a list of currently known component IDs."""
    return self.registered_components.keys()

  def get_component_by_id(self, id_string):
    """Get a component by ID.
    @return None if not found."""
    component_info = self.registered_components.get(id_string, None)
    if component_info is None:
      return None
    return component_info[0]

  def get_registered_component_names(self):
    """Get a list of currently known component names."""
    return list(self.registered_components_by_name.keys())

  def get_component_by_name(self, name):
    """Get a component by name.
    @return None if not found."""
    return self.registered_components_by_name.get(name, None)

  def get_name_by_component(self, component):
    """Get the name of a component.
    @return None if not found."""
    for component_name, component_iter in self.registered_components_by_name.items():
      if component_iter == component:
        return component_name
    return None

  def get_id_by_component(self, component):
    """Get the name of a component.
    @return None if not found."""
    for component_id, component_iter in self.registered_components.items():
      if component_iter[0] == component:
        return component_id
    return None

  def build_analysis_pipeline(self):
    """Convenience method to create the pipeline."""
    self.aminer_config.build_analysis_pipeline(self)


class AnalysisChild(TimeTriggeredComponentInterface):
  """This class defines the child performing the complete analysis
  workflow. When splitting privileges between analysis and monitor
  process, this class should only be initialized within the analysis
  process!"""
  
  def __init__(self, program_name, aminer_config):
    self.program_name = program_name
    self.analysis_context = AnalysisContext(aminer_config)
    self.run_analysis_loop_flag = True
    self.log_streams_by_name = {}
    self.persistence_file_name = AMinerConfig.build_persistence_file_name(
        self.analysis_context.aminer_config,
        self.__class__.__name__+'/RepositioningData')
    self.next_persist_time = time.time() + 600

    self.repositioning_data_dict = {}
    self.master_control_socket = None
    self.remote_control_socket = None

# This dictionary provides a lookup list from file descriptor
# to associated object for handling the data to and from the given
# descriptor. Currently supported handler objects are:
# * Parent process socket
# * Remote control listening socket
# * LogStreams
# * Remote control connections
    self.tracked_fds_dict = {}

# Override the signal handler to allow graceful shutdown.
    def graceful_shutdown_handler(_signo, _stack_frame):
      """This is the signal handler function to react on typical
      shutdown signals."""
      print('%s: caught signal, shutting down' % program_name, file=sys.stderr)
      self.run_analysis_loop_flag = False

    import signal
    signal.signal(signal.SIGHUP, graceful_shutdown_handler)
    signal.signal(signal.SIGINT, graceful_shutdown_handler)
    signal.signal(signal.SIGTERM, graceful_shutdown_handler)

# Do this on at the end of the initialization to avoid having
# partially initialized objects inside the registry.
    self.analysis_context.add_time_triggered_component(self)

  def run_analysis(self, master_fd):
    """This method runs the analysis thread.
    @param master_fd the main communication socket to the parent
    to receive logfile updates from the parent.
    @return 0 on success, e.g. normal termination via signal or
    1 on error."""

# The masterControlSocket is the socket to communicate with the
# master process to receive commands or logstream data. Expect
# the parent/child communication socket on fd 3. This also duplicates
# the fd, so close the old one.
    self.master_control_socket = socket.fromfd(
        master_fd, socket.AF_UNIX, socket.SOCK_DGRAM, 0)
    os.close(master_fd)
    self.tracked_fds_dict[self.master_control_socket.fileno()] = \
        self.master_control_socket

# Locate the real analysis configuration.
    self.analysis_context.build_analysis_pipeline()
    if self.analysis_context.atomizer_factory is None:
      print('FATAL: build_analysis_pipeline() did not initialize atomizer_factory, terminating', file=sys.stderr)
      return 1

    real_time_triggered_components = self.analysis_context.real_time_triggered_components
    analysis_time_triggered_components = self.analysis_context.analysis_time_triggered_components
    
    max_memory_mb = self.analysis_context.aminer_config.config_properties.get(AMinerConfig.KEY_RESOURCES_MAX_MEMORY_USAGE, None)
    if max_memory_mb is not None:
      try:
        max_memory_mb = int(max_memory_mb)
        resource.setrlimit(resource.RLIMIT_AS, (max_memory_mb*1024*1024, resource.RLIM_INFINITY))
      except ValueError:
        print('FATAL: %s must be an integer, terminating'
          % AMinerConfig.KEY_RESOURCES_MAX_MEMORY_USAGE, file=sys.stderr)
        return 1
      
    max_cpu_percent_usage = self.analysis_context.aminer_config.config_properties.get(AMinerConfig.KEY_RESOURCES_MAX_PERCENT_CPU_USAGE)
    if max_cpu_percent_usage is not None:
      try:
        max_cpu_percent_usage = int(max_cpu_percent_usage)
        # limit
        pid = os.getpid()
        package_installed_cmd = ['dpkg', '-l', 'cpulimit']
        cpulimit_cmd = ['cpulimit', '-p', str(pid), '-l', str(max_cpu_percent_usage)]
        
        with subprocess.Popen(package_installed_cmd,
           stdout=subprocess.PIPE, 
           stderr=subprocess.STDOUT) as out:
          stdout, _stderr = out.communicate()
        
        if 'dpkg-query: no packages found matching cpulimit' in stdout.decode():
          print('FATAL: cpulimit package must be installed, when using the property %s'
            % AMinerConfig.KEY_RESOURCES_MAX_PERCENT_CPU_USAGE, file=sys.stderr)
          return 1
        _out = subprocess.Popen(cpulimit_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      except ValueError:
        print('FATAL: %s must be an integer, terminating' 
          % AMinerConfig.KEY_RESOURCES_MAX_PERCENT_CPU_USAGE, file=sys.stderr)
        return 1

# Load continuation data for last known log streams. The loaded
# data has to be a dictionary with repositioning information for
# each stream. The data is used only when creating the first stream
# with that name.
    self.repositioning_data_dict = PersistencyUtil.load_json(
        self.persistence_file_name)
    if self.repositioning_data_dict is None:
      self.repositioning_data_dict = {}

# A list of LogStreams where handleStream() blocked due to downstream
# not being able to consume the data yet.
    blocked_log_streams = []

# Always start when number is None.
    next_real_time_trigger_time = None
    next_analysis_time_trigger_time = None

    delayed_return_status = 0
    while self.run_analysis_loop_flag:
# Build the list of inputs to select for anew each time: the LogStream
# file descriptors may change due to rollover.
      input_select_fd_list = []
      output_select_fd_list = []
      for fd_handler_object in self.tracked_fds_dict.values():
        if isinstance(fd_handler_object, LogStream):
          stream_fd = fd_handler_object.get_current_fd()
          if stream_fd < 0:
            continue
          input_select_fd_list.append(stream_fd)
        elif isinstance(fd_handler_object, AnalysisChildRemoteControlHandler):
          fd_handler_object.add_select_fds(
              input_select_fd_list, output_select_fd_list)
        else:
# This has to be a socket, just add the file descriptor.
          input_select_fd_list.append(fd_handler_object.fileno())

# Loop over the list in reverse order to avoid skipping elements
# in remove.
      for log_stream in reversed(blocked_log_streams):
        current_stream_fd = log_stream.handle_stream()
        if current_stream_fd >= 0:
          self.tracked_fds_dict[current_stream_fd] = log_stream
          input_select_fd_list.append(current_stream_fd)
          blocked_log_streams.remove(log_stream)

      read_list = None
      write_list = None
      try:
        (read_list, write_list, _except_list) = select.select(
            input_select_fd_list, output_select_fd_list, [], 1)
      except select.error as select_error:
# Interrupting signals, e.g. for shutdown are OK.
        if select_error[0] == errno.EINTR:
          continue
        print('Unexpected select result %s' % str(select_error), file=sys.stderr)
        delayed_return_status = 1
        break
      for read_fd in read_list:
        fd_handler_object = self.tracked_fds_dict[read_fd]
        if isinstance(fd_handler_object, LogStream):
# Handle this LogStream. Only when downstream processing blocks,
# add the stream to the blocked stream list.
          handle_result = fd_handler_object.handle_stream()
          if handle_result < 0:
# No need to care if current internal file descriptor in LogStream
# has changed in handleStream(), this will be handled when unblocking.
            del self.tracked_fds_dict[read_fd]
            blocked_log_streams.append(fd_handler_object)
          elif handle_result != read_fd:
# The current fd has changed, update the tracking list.
            del self.tracked_fds_dict[read_fd]
            self.tracked_fds_dict[handle_result] = fd_handler_object
          continue

        if isinstance(fd_handler_object, AnalysisChildRemoteControlHandler):
          try:
            fd_handler_object.do_receive()
          except ConnectionError as receiveException:
            print('Unclean termination of remote control: %s' % str(receiveException), file=sys.stderr)
          if fd_handler_object.is_dead():
            del self.tracked_fds_dict[read_fd]
# Reading is only attempted when output buffer was already flushed.
# Try processing the next request to fill the output buffer for
# next round.
          else:
            fd_handler_object.do_process(self.analysis_context)
          continue

        if fd_handler_object == self.master_control_socket:
          self.handle_master_control_socket_receive()
          continue

        if fd_handler_object == self.remote_control_socket:
# We received a remote connection, accept it unconditionally.
# Users should make sure, that they do not exhaust resources by
# hogging open connections.
          (control_client_socket, _remote_address) = \
              self.remote_control_socket.accept()
# Keep track of information received via this remote control socket.
          remote_control_handler = AnalysisChildRemoteControlHandler(
              control_client_socket)
          self.tracked_fds_dict[control_client_socket.fileno()] = remote_control_handler
          continue
        raise Exception('Unhandled object type %s' % type(fd_handler_object))

      for write_fd in write_list:
        fd_handler_object = self.tracked_fds_dict[write_fd]
        if isinstance(fd_handler_object, AnalysisChildRemoteControlHandler):
          buffer_flushed_flag = False
          try:
            buffer_flushed_flag = fd_handler_object.do_send()
          except OSError as sendError:
            print('Error sending data via remote control: %s' % str(sendError), file=sys.stderr)
            try:
              fd_handler_object.terminate()
            except ConnectionError as terminateException:
              print('Unclean termination of remote control: %s' % str(terminateException), file=sys.stderr)
          if buffer_flushed_flag:
            fd_handler_object.do_process(self.analysis_context)
          if fd_handler_object.is_dead():
            del self.tracked_fds_dict[write_fd]
          continue
        raise Exception('Unhandled object type %s' % type(fd_handler_object))


# Handle the real time events.
      real_time = time.time()
      if next_real_time_trigger_time is None or real_time >= next_real_time_trigger_time:
        next_trigger_offset = 3600
        for component in real_time_triggered_components:
          next_trigger_request = component.do_timer(real_time)
          next_trigger_offset = min(next_trigger_offset, next_trigger_request)
        next_real_time_trigger_time = real_time+next_trigger_offset

# Handle the analysis time events. The analysis time will be different
# when an analysis time component is registered.
      analysis_time = self.analysis_context.analysis_time
      if analysis_time is None:
        analysis_time = real_time
      if next_analysis_time_trigger_time is None or analysis_time >= next_analysis_time_trigger_time:
        next_trigger_offset = 3600
        for component in analysis_time_triggered_components:
          next_trigger_request = component.do_timer(real_time)
          next_trigger_offset = min(next_trigger_offset, next_trigger_request)
        next_analysis_time_trigger_time = analysis_time+next_trigger_offset

# Analysis loop is only left on shutdown. Try to persist everything
# and leave.
    PersistencyUtil.persist_all()
    return delayed_return_status

  def handle_master_control_socket_receive(self):
    """Receive information from the parent process via the master
    control socket. This method may only be invoked when receiving
    is guaranteed to be nonblocking and to return data."""

# We cannot fail with None here as the socket was in the readList.
    (received_fd, received_type_info, annotation_data) = \
        SecureOSFunctions.receive_annoted_file_descriptor(self.master_control_socket)
    if received_type_info == b'logstream':
      repositioning_data = self.repositioning_data_dict.get(annotation_data, None)
      if repositioning_data is not None:
        del self.repositioning_data_dict[annotation_data]
      res = None
      if annotation_data.startswith(b'file://'):
        from aminer.input.LogStream import FileLogDataResource
        res = FileLogDataResource(annotation_data, received_fd,
                                  repositioning_data=repositioning_data)
      elif annotation_data.startswith(b'unix://'):
        from aminer.input.LogStream import UnixSocketLogDataResource
        res = UnixSocketLogDataResource(annotation_data, received_fd)
      else:
        raise Exception('Filedescriptor of unknown type received')
# Make fd nonblocking.
      fd_flags = fcntl.fcntl(res.get_file_descriptor(), fcntl.F_GETFL)
      fcntl.fcntl(res.get_file_descriptor(), fcntl.F_SETFL, fd_flags | os.O_NONBLOCK)
      log_stream = self.log_streams_by_name.get(res.get_resource_name())
      if log_stream is None:
        stream_atomizer = self.analysis_context.atomizer_factory.get_atomizer_for_resource(
            res.get_resource_name())
        log_stream = LogStream(res, stream_atomizer)
        self.tracked_fds_dict[res.get_file_descriptor()] = log_stream
        self.log_streams_by_name[res.get_resource_name()] = log_stream
      else:
        log_stream.add_next_resource(res)
    elif received_type_info == b'remotecontrol':
      if self.remote_control_socket is not None:
        raise Exception('Received another remote control '
            'socket: multiple remote control not (yet?) supported.')
      self.remote_control_socket = socket.fromfd(
          received_fd, socket.AF_UNIX, socket.SOCK_STREAM, 0)
      os.close(received_fd)
      self.tracked_fds_dict[self.remote_control_socket.fileno()] = \
          self.remote_control_socket
    else:
      raise Exception('Unhandled type info on received fd: %s' % (
          repr(received_type_info)))

  def get_time_trigger_class(self):
    """Get the trigger class this component can be registered
    for. See AnalysisContext class for different trigger classes
    available."""
    return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

  def do_timer(self, trigger_time):
    """This method is called to perform trigger actions and to
    determine the time for next invocation. The caller may decide
    to invoke this method earlier than requested during the previous
    call. Classes implementing this method have to handle such
    cases. Each class should try to limit the time spent in this
    method as it might delay trigger signals to other components.
    For extensive compuational work or IO, a separate thread should
    be used.
    @param trigger_time the time this trigger is invoked. This
    might be the current real time when invoked from real time
    timers or the forensic log timescale time value.
    @return the number of seconds when next invocation of this
    trigger is required."""
    delta = self.next_persist_time - trigger_time
    if delta <= 0:
      self.repositioning_data_dict = {}
      for log_stream_name, log_stream in self.log_streams_by_name.items():
        repositioning_data = log_stream.get_repositioning_data()
        if repositioning_data is not None:
          self.repositioning_data_dict[log_stream_name] = repositioning_data
      PersistencyUtil.store_json(
          self.persistence_file_name, self.repositioning_data_dict)
      delta = 600
      self.next_persist_time = trigger_time + delta
    return delta


class AnalysisChildRemoteControlHandler:
  """This class stores information about one open remote control
  connection. The handler can be in 3 different states:
  * receive request: the control request was not completely received.
    The main process may use select() to wait for input data without
    blocking or polling.
  * execute: the request is complete and is currently under execution.
    In that mode all other aminer analysis activity is blocked.
  * respond: send back results from execution.

  All sent and received control packets have following common
  structure:
  * Total length in bytes (4 bytes): The maximal length is currently
    limited to 64k
  * Type code (4 bytes)
  * Data

  The handler processes following types:
  * Execute request ('EEEE'): Data is loaded as json artefact
    containing a list with two elements. The first one is the
    Python code to be executed. The second one is available within
    the execution namespace as 'remoteControlData'.

  The handler produces following requests:
  * Execution response ('RRRR'): The response contains a json
    artefact with a two element list. The first element is the
    content of 'remoteControlResponse' from the Python execution
    namespace. The second one is the exception message and traceback
    as string if an error has occured.

  Method naming:
  * do...(): Those methods perform an action consuming input or
    output buffer data.
  * may...(): Those methods return true if it would make sense
    to call a do...() method with the same name.
  * put...(): Those methods put a request on the buffers."""

  max_control_packet_size = 1 << 32

  def __init__(self, control_client_socket):
    self.control_client_socket = control_client_socket
    self.remote_control_fd = control_client_socket.fileno()
    self.input_buffer = b''
    self.output_buffer = b''

  def may_receive(self):
    """Check if this handler may receive more requests."""
    return len(self.output_buffer) == 0

  def do_process(self, analysis_context):
    """Process the next request, if any."""
    request_data = self.do_get()
    if request_data is None:
      return
    request_type = request_data[4:8]
    if request_type == b'EEEE':
      json_remote_control_response = None
      exception_data = None
      try:
        json_request_data = (json.loads(request_data[8:].decode()))
        json_request_data = JsonUtil.decode_object(json_request_data)
        if (json_request_data is None) or (not isinstance(json_request_data, list)) or (len(json_request_data) != 2):
          raise Exception('Invalid request data')
        methods = AMinerRemoteControlExecutionMethods()
        import aminer.analysis
        exec_locals = {'analysisContext': analysis_context, 'remoteControlData': json_request_data[1],
                      'printCurrentConfig': methods.print_current_config, 'printConfigProperty': methods.print_config_property,
                      'printAttributeOfRegisteredAnalysisComponent': methods.print_attribute_of_registered_analysis_component,
                      'changeConfigProperty': methods.change_config_property,
                      'changeAttributeOfRegisteredAnalysisComponent': methods.change_attribute_of_registered_analysis_component,
                      'renameRegisteredAnalysisComponent': methods.rename_registered_analysis_component,
                      'addHandlerToAtomFilterAndRegisterAnalysisComponent': methods.add_handler_to_atom_filter_and_register_analysis_component,
                      'saveCurrentConfig': methods.save_current_config,
                      'whitelistEventInComponent': methods.whitelist_event_in_component,
                      'dumpEventsFromHistory': methods.dump_events_from_history,
                      'ignoreEventsFromHistory': methods.ignore_events_from_history,
                      'listEventsFromHistory': methods.list_events_from_history,
                      'whitelistEventsFromHistory': methods.whitelist_events_from_history,
                      'HistogramAnalysis': aminer.analysis.HistogramAnalysis,
                      'MatchValueAverageChangeDetector': aminer.analysis.MatchValueAverageChangeDetector,
                      'MatchValueStreamWriter': aminer.analysis.MatchValueStreamWriter,
                      'MissingMatchPathValueDetector': aminer.analysis.MissingMatchPathValueDetector,
                      'NewMatchPathDetector': aminer.analysis.NewMatchPathDetector,
                      'NewMatchPathValueComboDetector': aminer.analysis.NewMatchPathValueComboDetector,
                      'Rules': aminer.analysis.Rules,
                      'TimeCorrelationDetector': aminer.analysis.TimeCorrelationDetector,
                      'TimeCorrelationViolationDetector': aminer.analysis.TimeCorrelationViolationDetector,
                      'TimestampCorrectionFilters': aminer.analysis.TimestampCorrectionFilters,
                      'TimestampsUnsortedDetector': aminer.analysis.TimestampsUnsortedDetector,
                      'WhitelistViolationDetector': aminer.analysis.WhitelistViolationDetector}
        # write this to the log file!
        logging.basicConfig(filename=AMinerConfig.LOG_FILE, level=logging.DEBUG,
            format='%(asctime)s %(levelname)s %(message)s', datefmt='%d.%m.%Y %H:%M:%S')
        logging.addLevelName(15, "REMOTECONTROL")
        logging.log(15, json_request_data[0].decode())

        exec(json_request_data[0], {'__builtins__': None}, exec_locals)
        json_remote_control_response = json.dumps(exec_locals.get('remoteControlResponse', None))
        if methods.REMOTE_CONTROL_RESPONSE == '':
          methods.REMOTE_CONTROL_RESPONSE = None
        if exec_locals.get('remoteControlResponse', None) is None:
          json_remote_control_response = json.dumps(methods.REMOTE_CONTROL_RESPONSE)
        else:
          json_remote_control_response = json.dumps(exec_locals.get('remoteControlResponse', None) + methods.REMOTE_CONTROL_RESPONSE)
      # skipcq: FLK-E722
      except:
        exception_data = traceback.format_exc()
# This is little dirty but avoids having to pass over remoteControlResponse
# dumping again.
      if json_remote_control_response is None:
        json_remote_control_response = 'null'
      json_response = '[%s, %s]' % (json.dumps(exception_data), json_remote_control_response)
      if len(json_response)+8 > self.max_control_packet_size:
# Damn: the response would be larger than packet size. Fake a
# secondary exception and return part of the json string included.
# Binary search of size could be more efficient, knowing the maximal
# size increase a string could have in json.
        max_include_size = len(json_response)
        min_include_size = 0
        min_include_response_data = None
        while True:
          test_size = (max_include_size+min_include_size) >> 1
          if test_size == min_include_size:
            break
          emergency_response_data = json.dumps(['Exception: Response too large\nPartial response data: %s...' %
                                                json_response[:test_size], None])
          if len(emergency_response_data)+8 > self.max_control_packet_size:
            max_include_size = test_size-1
          else:
            min_include_size = test_size
            min_include_response_data = emergency_response_data
        json_response = min_include_response_data
# Now size is OK, send the data
      json_response = json_response.encode()
      self.output_buffer += struct.pack("!I", len(json_response) + 8) + b'RRRR' + json_response
    else:
      raise Exception('Invalid request type %s' % repr(request_type))

  def may_get(self):
    """Check if a call to doGet would make sense.
    @return True if the input buffer already contains a complete
    wellformed packet or definitely malformed one."""
    if len(self.input_buffer) < 4:
      return False
    request_length = struct.unpack("!I", self.input_buffer[:4])[0]
    return (request_length <= len(self.input_buffer)) or \
           (request_length >= self.max_control_packet_size)

  def do_get(self):
    """Get the next packet from the input buffer and remove it.
    @return the packet data including the length preamble or None
    when request not yet complete."""
    if len(self.input_buffer) < 4:
      return None
    request_length = struct.unpack("!I", self.input_buffer[:4])[0]
    if (request_length < 0) or (request_length >= self.max_control_packet_size):
      raise Exception('Invalid length value 0x%x in malformed request starting with b64:%s' %
                      (request_length, base64.b64encode(self.input_buffer[:60])))
    if request_length > len(self.input_buffer):
      return None
    request_data = self.input_buffer[:request_length]
    self.input_buffer = self.input_buffer[request_length:]
    return request_data

  def do_receive(self):
    """Receive data from the remote side and add it to the input
    buffer. This method call expects to read at least one byte
    of data. A zero byte read indicates EOF and will cause normal
    handler termination when all input and output buffers are
    empty. Any other state or error causes handler termination
    before reporting the error.
    @return True if read was successful, false if EOF is reached
    without reading any data and all buffers are empty.
    @throws Exception when unexpected errors occured while receiving
    or shuting down the connection."""
    data = os.read(self.remote_control_fd, 1 << 16)
    self.input_buffer += data
    if not data:
      self.terminate()

  def do_send(self):
    """Send data from the output buffer to the remote side.
    @return True if output buffer was emptied."""
    send_length = os.write(self.remote_control_fd, self.output_buffer)
    if send_length == len(self.output_buffer):
      self.output_buffer = b''
      return True
    self.output_buffer = self.output_buffer[send_length:]
    return False

  def put_request(self, request_type, request_data):
    """Add a request of given type to the send queue.
    @param request_type is a byte string denoting the type of the
    request. Currently only 'EEEE' is supported.
    @param request_data is a byte string denoting the content of
    the request."""
    if not isinstance(request_type, bytes):
      raise Exception('Request type is not a byte string')
    if len(request_type) != 4:
      raise Exception('Request type has to be 4 bytes long')
    if not isinstance(request_data, bytes):
      raise Exception('Request data is not a byte string')
    if len(request_data)+8 > self.max_control_packet_size:
      raise Exception('Data too large to fit into single packet')
    self.output_buffer += struct.pack("!I", len(request_data) + 8) + request_type + request_data

  def put_execute_request(self, remote_control_code, remote_control_data):
    """Add a request to send exception data to the send queue."""
    remote_control_data = json.dumps([JsonUtil.encode_object(remote_control_code), JsonUtil.encode_object(remote_control_data)])
    self.put_request(b'EEEE', remote_control_data.encode())

  def add_select_fds(self, input_select_fd_list, output_select_fd_list):
    """Update the file descriptor lists for selecting on read
    and write file descriptors."""
    if self.output_buffer:
      output_select_fd_list.append(self.remote_control_fd)
    else:
      input_select_fd_list.append(self.remote_control_fd)

  def terminate(self):
    """End this remote control session."""
    self.control_client_socket.close()
# Avoid accidential reuse.
    self.control_client_socket = None
    self.remote_control_fd = -1
    if self.input_buffer or self.output_buffer:
      raise Exception('Unhandled input data')

  def is_dead(self):
    """Check if this remote control connection is already dead."""
    return self.remote_control_fd == -1
