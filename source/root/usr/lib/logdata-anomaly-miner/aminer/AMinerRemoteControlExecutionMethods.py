"""This module contains methods which can be executed from the
AMinerRemoteControl class."""

from aminer import AMinerConfig, AnalysisChild
import resource
import subprocess
from aminer.input import LogAtom

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
        if not isinstance(analysisContext, AnalysisChild.AnalysisContext):
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the analysisContext must be of type %s." % AnalysisChild.AnalysisContext.__class__
            return

        if propertyName == AMinerConfig.KEY_PERSISTENCE_DIR:
            result = self.changeConfigPropertyPersistenceDir(analysisContext, value)
        elif propertyName == AMinerConfig.KEY_RESOURCES_MAX_MEMORY_USAGE:
            result = self.changeConfigPropertyMaxMemory(analysisContext, value)
        elif propertyName == AMinerConfig.KEY_RESOURCES_MAX_PERCENT_CPU_USAGE:
            result = self.changeConfigPropertyMaxCpuPercentUsage(analysisContext, value)
        elif propertyName in configKeysMailAlerting:
            result = self.changeConfigPropertyMailAlerting(analysisContext, propertyName, value)
        elif propertyName == AMinerConfig.KEY_LOG_PREFIX:
            if isinstance(value, str):
                analysisContext.aminerConfig.configProperties[AMinerConfig.KEY_LOG_PREFIX] = str(value)
            else:
                self.REMOTE_CONTROL_RESPONSE += "FAILURE: property 'LogPrefix' must be of type String!"
        elif propertyName == AMinerConfig.KEY_LOG_SOURCES_LIST:
            self.changeConfigPropertyLogResourcesList(analysisContext, value)

        else:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: property %s could not be changed. Please check the propertyName " \
                                            "again." % propertyName
            return
        if result == 0:
            self.REMOTE_CONTROL_RESPONSE += "'%s' changed to '%s' successfully." % (propertyName, value)

    def changeConfigPropertyMailAlerting(self, analysisContext, propertyName, value):
        t = type(analysisContext.aminerConfig.configProperties[propertyName])
        if not isinstance(value, t):
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the value of the property '%s' must be of type %s!" % (
                propertyName, t)
            return 1
        analysisContext.aminerConfig.configProperties[propertyName] = value
        for analysisComponentId in analysisContext.getRegisteredComponentIds():
            component = analysisContext.getComponentById(analysisComponentId)
            if component.__class__.__name__ == "DefaultMailNotificationEventHandler":
                setattr(component, propertyName, value)
        return 0

    def changeConfigPropertyMaxMemory(self, analysisContext, maxMemoryMB):
        try:
            maxMemoryMB = int(maxMemoryMB)
            if maxMemoryMB < 32 and maxMemoryMB != -1:
                self.REMOTE_CONTROL_RESPONSE += "FAILURE: it is not safe to run the AMiner with less than 32MB RAM."
                return 1
            resource.setrlimit(resource.RLIMIT_AS, (maxMemoryMB * 1024 * 1024, resource.RLIM_INFINITY))
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
            pid = response[len(response) - 1]
            packageInstalledCmd = ['dpkg', '-l', 'cpulimit']
            cpulimitCmd = ['cpulimit', '-p', pid.decode(), '-l', str(maxCpuPercentUsage)]

            with subprocess.Popen(packageInstalledCmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as out:
                stdout, stderr = out.communicate()

            if 'dpkg-query: no packages found matching cpulimit.' in stdout.decode():
                self.REMOTE_CONTROL_RESPONSE = 'FATAL: cpulimit package must be installed, '
                + 'when using the property %s.' % AMinerConfig.KEY_RESOURCES_MAX_PERCENT_CPU_USAGE
                return 1
            else:
                with subprocess.Popen(cpulimitCmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as out:
                    return 0
        except ValueError:
            self.REMOTE_CONTROL_RESPONSE = 'FATAL: %s must be an integer, terminating.' % (
                AMinerConfig.KEY_RESOURCES_MAX_PERCENT_CPU_USAGE)
            return 1

    def changeAttributeOfRegisteredAnalysisComponent(self, analysisContext, componentName, attribute, value):
        attr = getattr(analysisContext.getComponentByName(componentName), attribute)
        if type(attr) == type(value):
            setattr(analysisContext.getComponentByName(componentName), attribute, value)
            self.REMOTE_CONTROL_RESPONSE += "'%s.%s' changed from %s to %s successfully." % (componentName,
                attribute, repr(attr), value)
        else:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: property '%s.%s' must be of type %s!" % (componentName,
                attribute, type(attr))

    def renameRegisteredAnalysisComponent(self, analysisContext, oldComponentName, newComponentName):
        component = analysisContext.getComponentByName(oldComponentName)
        if component is None:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: component '%s' does not exist!" % oldComponentName
            return
        else:
            analysisContext.registeredComponentsByName[oldComponentName] = None
            analysisContext.registeredComponentsByName[newComponentName] = component
            self.REMOTE_CONTROL_RESPONSE += "Component '%s' renamed to '%s' successfully." % (
                oldComponentName, newComponentName)

    def printConfigProperty(self, analysisContext, propertyName):
        self.REMOTE_CONTROL_RESPONSE = propertyName + " : " + str(
            analysisContext.aminerConfig.configProperties[propertyName])

    def printAttributeOfRegisteredAnalysisComponent(self, analysisContext, componentName, attribute):
        self.REMOTE_CONTROL_RESPONSE += "%s.%s = %s" % (componentName, attribute, repr(getattr(
            analysisContext.getComponentByName(componentName), attribute)))

    def printCurrentConfig(self, analysisContext):
        for configProperty in analysisContext.aminerConfig.configProperties:
            if isinstance(analysisContext.aminerConfig.configProperties[configProperty], str):
                self.REMOTE_CONTROL_RESPONSE += "%s = '%s'\n" % (configProperty,
                    analysisContext.aminerConfig.configProperties[configProperty])
            else:
                self.REMOTE_CONTROL_RESPONSE += "%s = %s\n" % (configProperty,
                    analysisContext.aminerConfig.configProperties[configProperty])
        for componentId in analysisContext.getRegisteredComponentIds():
            self.REMOTE_CONTROL_RESPONSE += "%s {\n" % analysisContext.getNameByComponent(
                analysisContext.getComponentById(componentId))
            for var in vars(analysisContext.getComponentById(componentId)):
                self.REMOTE_CONTROL_RESPONSE += "  %s = %s\n" % (var, repr(getattr(
                    analysisContext.getComponentById(componentId), var)))
            self.REMOTE_CONTROL_RESPONSE += "}\n\n"

    def saveCurrentConfig(self, analysisContext, destinationFile):
        self.REMOTE_CONTROL_RESPONSE = AMinerConfig.saveConfig(analysisContext, destinationFile)
        self.REMOTE_CONTROL_RESPONSE += "Successfully saved the current config to %s." % destinationFile

    def whitelistEvent(self, analysisContext, componentName, eventData, whitelistingData=None):
        component = analysisContext.getComponentByName(componentName)
        if component is None:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: component '%s' does not exist!" % component
            return
        if component.__class__.__name__ not in ["EnhancedNewMatchPathValueComboDetector", "MissingMatchPathValueDetector",
            "NewMatchPathDetector", "NewMatchPathValueComboDetector"]:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: component class '%s' does not support whitelisting! Only "\
                "the following classes support whitelisting: EnhancedNewMatchPathValueComboDetector, " \
                "MissingMatchPathValueDetector, NewMatchPathDetector and NewMatchPathValueComboDetector." % component.__class__.__name__
            return
        try:
            if component.__class__.__name__ == "MissingMatchPathValueDetector":
                self.REMOTE_CONTROL_RESPONSE += component.whitelistEvent("Analysis.%s" % component.__class__.__name__,
                    [component.__class__.__name__], eventData, whitelistingData)
            else:
                self.REMOTE_CONTROL_RESPONSE += component.whitelistEvent("Analysis.%s"%component.__class__.__name__,
                    [component.__class__.__name__], [LogAtom("", None, 1666.0, None), eventData], whitelistingData)
        except Exception as e:
            self.REMOTE_CONTROL_RESPONSE += "Exception: " + repr(e)

    def addHandlerToAtomFilterAndRegisterAnalysisComponent(self, analysisContext, atomHandler, component, componentName):
        atomFilter = analysisContext.getComponentByName(atomHandler)
        if atomFilter is None:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: atomHandler '%s' does not exist!" % atomHandler
            return
        if analysisContext.getComponentByName(componentName) is not None:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: Component with same name already registered! (%s)" % componentName
            return
        atomFilter.addHandler(component)
        analysisContext.registeredComponentsByName[atomHandler] = atomFilter
        analysisContext.registerComponent(component, componentName)
        self.REMOTE_CONTROL_RESPONSE += "Component '%s' added to '%s' successfully." % (
            componentName, atomHandler)

    def dumpEventsFromHistory(self, analysisContext, historyComponentName, eventIds):
        self.REMOTE_CONTROL_RESPONSE = "not implemented yet.."

    def ignoreEventsFromHistory(self, analysisContext, historyComponentName, eventIds):
        self.REMOTE_CONTROL_RESPONSE = "not implemented yet.."

    def listEventsFromHistory(self, analysisContext, historyComponentName, maxEventCount=None):
        self.REMOTE_CONTROL_RESPONSE = "not implemented yet.."
