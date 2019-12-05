"""This module contains methods which can be executed from the
AMinerRemoteControl class."""
from aminer import AMinerConfig, AnalysisChild
import resource

class AMinerRemoteControlExecutionMethods(object):

    REMOTE_CONTROL_RESPONSE = ''
    
    CONFIG_KEY_MAIL_TARGET_ADDRESS = 'MailAlerting.TargetAddress'
    CONFIG_KEY_MAIL_FROM_ADDRESS = 'MailAlerting.FromAddress'
    CONFIG_KEY_MAIL_SUBJECT_PREFIX = 'MailAlerting.SubjectPrefix'
    CONFIG_KEY_MAIL_ALERT_GRACE_TIME = 'MailAlerting.AlertGraceTime'
    CONFIG_KEY_EVENT_COLLECT_TIME = 'MailAlerting.EventCollectTime'
    CONFIG_KEY_ALERT_MIN_GAP = 'MailAlerting.MinAlertGap'
    CONFIG_KEY_ALERT_MAX_GAP = 'MailAlerting.MaxAlertGap'
    CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE = 'MailAlerting.MaxEventsPerMessage'
    
    def printResponse(self, value):
      self.REMOTE_CONTROL_RESPONSE += str(value)
    
    def changeConfigProperty(self, analysisContext, propertyName, value):
      result = 0
      configKeysMailAlerting = {self.CONFIG_KEY_MAIL_TARGET_ADDRESS, 
                                self.CONFIG_KEY_MAIL_FROM_ADDRESS,
                                self.CONFIG_KEY_MAIL_SUBJECT_PREFIX,
                                self.CONFIG_KEY_MAIL_ALERT_GRACE_TIME,
                                self.CONFIG_KEY_EVENT_COLLECT_TIME,
                                self.CONFIG_KEY_ALERT_MIN_GAP,
                                self.CONFIG_KEY_ALERT_MAX_GAP,
                                self.CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE}
      if (not isinstance(analysisContext, AnalysisChild.AnalysisContext)):
        self.REMOTE_CONTROL_RESPONSE += "FAILURE: the analysisContext must be of type %s\n" % AnalysisChild.AnalysisContext.__class__
        return
      
      elif (propertyName == AMinerConfig.KEY_RESOURCES_MAX_MEMORY_USAGE):
        result = self.changeConfigPropertyMaxMemory(analysisContext, value)
      elif (propertyName in configKeysMailAlerting):
        result = self.changeConfigPropertyMailAlerting(analysisContext, propertyName, value)
      elif (propertyName == AMinerConfig.KEY_LOG_PREFIX):
        if (isinstance(value, str)):
          analysisContext.aminerConfig.configProperties[AMinerConfig.KEY_LOG_PREFIX] = str(value)
        else:
          self.REMOTE_CONTROL_RESPONSE += "FAILURE: property 'LogPrefix' must be of type String!\n"
      elif (propertyName == AMinerConfig.KEY_LOG_SOURCES_LIST):
        self.changeConfigPropertyLogResourcesList(analysisContext, value)
      
      else:
        self.REMOTE_CONTROL_RESPONSE += "FAILURE: property %s could not be changed. Please check the propertyName again.\n" % propertyName
        return
      if (result == 0):
        self.REMOTE_CONTROL_RESPONSE += "%s changed to %s successfully."%(propertyName, value)
      
      
    def changeConfigPropertyMailAlerting(self, analysisContext, propertyName, value):
      raise Exception("not implemented yet..")
    
    def changeConfigPropertyLogResourcesList(self, analysisContext, value):
      raise Exception("not implemented yet..")
      
    def changeConfigPropertyMaxMemory(self, analysisContext, maxMemoryMB):
      try:
        maxMemoryMB = int(maxMemoryMB)
        if (maxMemoryMB < 32):
          self.REMOTE_CONTROL_RESPONSE += "FAILURE: it is not safe to run the AMiner with less than 32MB RAM."
          return 1
        resource.setrlimit(resource.RLIMIT_AS, (maxMemoryMB*1024*1024, resource.RLIM_INFINITY))
        analysisContext.aminerConfig.configProperties[AMinerConfig.KEY_RESOURCES_MAX_MEMORY_USAGE] = maxMemoryMB
        return 0
      except ValueError:
        self.REMOTE_CONTROL_RESPONSE += "FAILURE: property 'maxMemoryUsage' must be of type Integer!\n"
        return 1
      
    def changeConfigPropertyMaxCpuPercentUsage(self, analysisContext, maxCpuPercentUsage):
      raise Exception("not implemented yet..")
    
    def changeAttributeOfRegisteredAnalysisComponent(self, componentName, attribute, value):
      # value must be of the same type af the oldValue of attribute
      raise Exception("not implemented yet..")
    
    def renameRegisteredAnalysisComponent(self, oldComponentName, newComponentName):
      raise Exception("not implemented yet..")
    
    # to be continued with methods from the AecidCli..
    