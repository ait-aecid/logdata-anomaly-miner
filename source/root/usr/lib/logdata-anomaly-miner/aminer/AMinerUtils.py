import ctypes
import errno
import os
import socket
import struct
import sys

from aminer.util import TimeTriggeredComponentInterface


class AnalysisContext:
  """This class collects information about the current analysis
  context to access it during analysis or remote management."""

  TIME_TRIGGER_CLASS_REALTIME=1
  TIME_TRIGGER_CLASS_ANALYSISTIME=2

  def __init__(self, aminerConfig):
    self.aminerConfig=aminerConfig
# This is the factory to create atomiziers for incoming data streams
# and link them to the analysis pipeline.
    self.atomizerFactory=None
# This is the current log processing and analysis time regarding
# the data stream being analyzed. While None, the analysis time
# e.g. used to trigger components (see analysisTimeTriggeredComponents),
# is the same as current system time. For forensic analysis this
# time has to be updated to values derived from the log data input
# to reflect the current log processing time, which will be in
# the past and may progress much faster than real system time.
    self.analysisTime=None
# Keep a registry of all analysis and filter configuration for
# later use. Remote control interface may then access them for
# runtime reconfiguration.
    self.nextRegistryId=0
    self.registeredComponents={}
# Keep also a list of components by name.
    self.registeredComponentsByName={}
# Keep lists of components that should receive timer interrupts
# when real time or analysis time has elapsed.
    self.realTimeTriggeredComponents=[]
    self.analysisTimeTriggeredComponents=[]


  def addTimeTriggeredComponent(self, component, triggerClass=None):
    if not(isinstance(component, TimeTriggeredComponentInterface)):
      raise Exception('Attempting to register component of class %s not implementing aminer.util.TimeTriggeredComponentInterface' % component.__class__.__name__)
    if triggerClass==None:
      triggerClass=component.getTimeTriggerClass()
    if triggerClass==AnalysisContext.TIME_TRIGGER_CLASS_REALTIME:
      self.realTimeTriggeredComponents.append(component)
    elif triggerClass==AnalysisContext.TIME_TRIGGER_CLASS_ANALYSISTIME:
      self.analysisTimeTriggeredComponents.append(component)
    else:
      raise Exception('Attempting to timer component for unknown class %s' % triggerClass)

  def registerComponent(self, component, componentName=None,
      registerTimeTriggerClassOverride=None):
    """Register a new component. A component implementing the
    TimeTriggeredComponentInterface will also be added to the
    appropriate lists unless registerTimeTriggerClassOverride
    is specified.
    @param componentName when not none, the component is also
    added to the named components. When a component with the same
    name was already registered, this will cause an error.
    @param registerTimeTriggerClassOverride if not none, ignore
    the time trigger class supplied by the component and register
    it for the classes specified in the override list. Use an
    empty list to disable registration."""
    if (componentName!=None) and (self.registeredComponentsByName.has_key(componentName)):
      raise Exception('Component with same name already registered')
    if (registerTimeTriggerClassOverride!=None) and (not(isinstance(component, TimeTriggeredComponentInterface))):
      raise Exception('Requesting override on component not implementing TimeTriggeredComponentInterface')

    self.registeredComponents[self.nextRegistryId]=(component, componentName)
    self.nextRegistryId+=1
    if componentName!=None:
      self.registeredComponentsByName[componentName]=component
    if isinstance(component, TimeTriggeredComponentInterface):
      if registerTimeTriggerClassOverride==None:
        self.addTimeTriggeredComponent(component)
      else:
        for triggerClass in registerTimeTriggerClassOverride:
          self.addTimeTriggeredComponent(component, triggerClass)

  def getRegisteredComponentIds(self):
    """Get a list of currently known component IDs."""
    return(self.registeredComponents.keys())
  def getComponentById(self, id):
    """Get a component by ID.
    @return None if not found."""
    componentInfo=self.registeredComponents.get(id, None)
    if componentInfo==None: return(None)
    return(componentInfo[0])
  def getRegisteredComponentNames(self):
    """Get a list of currently known component names."""
    return(self.registeredComponentsByName.keys())
  def getComponentByName(self, name):
    """Get a component by name.
    @return None if not found."""
    return(self.registeredComponentsByName.get(name, None))

  def buildAnalysisPipeline(self):
    """Convenience method to create the pipeline."""
    self.aminerConfig.buildAnalysisPipeline(self)
