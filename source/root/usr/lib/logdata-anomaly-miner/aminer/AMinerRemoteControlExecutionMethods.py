"""This module contains methods which can be executed from the
AMinerRemoteControl class."""

############################### Könnte Import Error lösen
#import sys
#sys.path = sys.path[1:]+['/usr/lib/logdata-anomaly-miner']

from aminer import AMinerConfig, AnalysisChild
import resource
import subprocess

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
                                self.CONFIG_KEY_EVENT_COLLECT_TIME,
                                self.CONFIG_KEY_ALERT_MIN_GAP,
                                self.CONFIG_KEY_ALERT_MAX_GAP,
                                self.CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE}
      if (not isinstance(analysisContext, AnalysisChild.AnalysisContext)):
        self.REMOTE_CONTROL_RESPONSE += "FAILURE: the analysisContext must be of type %s." % AnalysisChild.AnalysisContext.__class__
        return
      
      if (propertyName == AMinerConfig.KEY_PERSISTENCE_DIR):
        result = self.changeConfigPropertyPersistenceDir(analysisContext, value)
      elif (propertyName == AMinerConfig.KEY_RESOURCES_MAX_MEMORY_USAGE):
        result = self.changeConfigPropertyMaxMemory(analysisContext, value)
      elif (propertyName == AMinerConfig.KEY_RESOURCES_MAX_PERCENT_CPU_USAGE):
        result = self.changeConfigPropertyMaxCpuPercentUsage(analysisContext, value)
      elif (propertyName in configKeysMailAlerting):
        result = self.changeConfigPropertyMailAlerting(analysisContext, propertyName, value)
      elif (propertyName == AMinerConfig.KEY_LOG_PREFIX):
        if (isinstance(value, str)):
          analysisContext.aminerConfig.configProperties[AMinerConfig.KEY_LOG_PREFIX] = str(value)
        else:
          self.REMOTE_CONTROL_RESPONSE += "FAILURE: property 'LogPrefix' must be of type String!"
      elif (propertyName == AMinerConfig.KEY_LOG_SOURCES_LIST):
        self.changeConfigPropertyLogResourcesList(analysisContext, value)
      
      else:
        self.REMOTE_CONTROL_RESPONSE += "FAILURE: property %s could not be changed. Please check the propertyName again." % propertyName
        return
      if (result == 0):
        self.REMOTE_CONTROL_RESPONSE += "%s changed to %s successfully."%(propertyName, value)
      
    def changeConfigPropertyPersistenceDir(self, analysisContext, newPersistenceDir):
      raise Exception("not implemented yet..")
      
    def changeConfigPropertyMailAlerting(self, analysisContext, propertyName, value):
      #go through every DefaultMailNotificationEventHandler and set the new property.
      raise Exception("not implemented yet..")
    
    def changeConfigPropertyLogResourcesList(self, analysisContext, newLogResourceList):
      raise Exception("not implemented yet..")
      
    def changeConfigPropertyMaxMemory(self, analysisContext, maxMemoryMB):
      try:
        maxMemoryMB = int(maxMemoryMB)
        if (maxMemoryMB < 32 and maxMemoryMB != -1):
          self.REMOTE_CONTROL_RESPONSE += "FAILURE: it is not safe to run the AMiner with less than 32MB RAM."
          return 1
        resource.setrlimit(resource.RLIMIT_AS, (maxMemoryMB*1024*1024, resource.RLIM_INFINITY))
        analysisContext.aminerConfig.configProperties[AMinerConfig.KEY_RESOURCES_MAX_MEMORY_USAGE] = maxMemoryMB
        return 0
      except ValueError:
        self.REMOTE_CONTROL_RESPONSE += "FAILURE: property 'maxMemoryUsage' must be of type Integer!"
        return 1
      
    def changeConfigPropertyMaxCpuPercentUsage(self, maxCpuPercentUsage):
      try:
        maxCpuPercentUsage = int(maxCpuPercentUsage)
        # limit
        with subprocess.Popen(['pgrep', '-f', 'AMiner'], stdout=subprocess.PIPE, shell=False) as child:
          response = child.communicate()[0].split()
        pid = response[len(response)-1]
        packageInstalledCmd = ['dpkg', '-l', 'cpulimit']
        cpulimitCmd = ['cpulimit', '-p', pid.decode(), '-l', str(maxCpuPercentUsage)]
        
        with subprocess.Popen(packageInstalledCmd, 
           stdout=subprocess.PIPE, 
           stderr=subprocess.STDOUT) as out:
          stdout,stderr = out.communicate()
        
        if 'dpkg-query: no packages found matching cpulimit.' in stdout.decode():
          self.REMOTE_CONTROL_RESPONSE = 'FATAL: cpulimit package must be installed, ' 
          + 'when using the property %s.' % AMinerConfig.KEY_RESOURCES_MAX_PERCENT_CPU_USAGE
          return 1
        else:
          with subprocess.Popen(cpulimitCmd, 
           stdout=subprocess.PIPE, 
           stderr=subprocess.STDOUT) as out:
            return 0
      except ValueError:
        self.REMOTE_CONTROL_RESPONSE = 'FATAL: %s must be an integer, terminating.' %(
          AMinerConfig.KEY_RESOURCES_MAX_PERCENT_CPU_USAGE)
        return 1
    
    def changeAttributeOfRegisteredAnalysisComponent(self, analysisContext, componentName, attribute, value):
      attr = getattr(analysisContext.getComponentByName(componentName), attribute)
      if (type(attr) == type(value)):
        setattr(analysisContext.getComponentByName(componentName), attribute, value)
        self.REMOTE_CONTROL_RESPONSE += "'%s.%s' changed from %s to %s successfully."%(componentName, 
            attribute, repr(attr), value)
      else:
        self.REMOTE_CONTROL_RESPONSE += "FAILURE: property '%s.%s' must be of type %s!"%(componentName,
            attribute, type(attr))
    
    def renameRegisteredAnalysisComponent(self, analysisContext, oldComponentName, newComponentName):
      component = analysisContext.getComponentByName(oldComponentName)
      if component == None:
        self.REMOTE_CONTROL_RESPONSE += "FAILURE: component '%s' does not exist!"%oldComponentName
        return
      else:
        analysisContext.registeredComponentsByName[oldComponentName] = None
        analysisContext.registeredComponentsByName[newComponentName] = component
        self.REMOTE_CONTROL_RESPONSE += "Component '%s' renamed to '%s' successfully."%(oldComponentName, newComponentName)
    
    def printConfigProperty(self, analysisContext, propertyName):
      self.REMOTE_CONTROL_RESPONSE = propertyName + " : " + str(analysisContext.aminerConfig.configProperties[propertyName])
      
    def printCurrentConfig(self, analysisContext):
      for configProperty in analysisContext.aminerConfig.configProperties:
        self.REMOTE_CONTROL_RESPONSE += "%s\n"%configProperty
      print(analysisContext.aminerConfig.configProperties)
    
    def saveCurrentConfig(self, analysisContext, destinationFile):
      self.REMOTE_CONTROL_RESPONSE = AMinerConfig.saveConfig(analysisContext, destinationFile)
      self.REMOTE_CONTROL_RESPONSE += "Successfully saved the current config to %s."%destinationFile
    
    # to be continued with methods from the AecidCli..
    