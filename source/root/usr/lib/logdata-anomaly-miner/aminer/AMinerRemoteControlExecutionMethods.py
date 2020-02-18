"""This module contains methods which can be executed from the
AMinerRemoteControl class."""
import aminer
from aminer import AMinerConfig, AnalysisChild
import resource
import subprocess
from aminer.input import LogAtom
from aminer.input import AtomHandlerInterface

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

        if not propertyName in analysisContext.aminerConfig.configProperties:
            self.REMOTE_CONTROL_RESPONSE = "FAILURE: the property '%s' does not exist in the current config!"%propertyName
            return

        t = type(analysisContext.aminerConfig.configProperties[propertyName])
        if not isinstance(value, t):
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the value of the property '%s' must be of type %s!" % (
                propertyName, t)
            return

        if propertyName == AMinerConfig.KEY_PERSISTENCE_DIR or propertyName == AMinerConfig.KEY_LOG_SOURCES_LIST:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the property '%s' can only be changed at " \
                                            "startup in the AMiner root process!" % propertyName
        elif propertyName == AMinerConfig.KEY_RESOURCES_MAX_MEMORY_USAGE:
            result = self.changeConfigPropertyMaxMemory(analysisContext, value)
        elif propertyName == AMinerConfig.KEY_RESOURCES_MAX_PERCENT_CPU_USAGE:
            result = self.changeConfigPropertyMaxCpuPercentUsage(analysisContext, value)
        elif propertyName in configKeysMailAlerting:
            result = self.changeConfigPropertyMailAlerting(analysisContext, propertyName, value)
        elif propertyName == AMinerConfig.KEY_LOG_PREFIX:
            result = self.changeConfigPropertyLogPrefix(analysisContext, value)
        else:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: property %s could not be changed. Please check the propertyName " \
                                            "again." % propertyName
            return
        if result == 0:
            self.REMOTE_CONTROL_RESPONSE += "'%s' changed to '%s' successfully." % (propertyName, value)

    def changeConfigPropertyMailAlerting(self, analysisContext, propertyName, value):
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

    def changeConfigPropertyLogPrefix(self, analysisContext, logPrefix):
        analysisContext.aminerConfig.configProperties[AMinerConfig.KEY_LOG_PREFIX] = str(logPrefix)
        return 0

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
        if type(oldComponentName) is not str or type(newComponentName) is not str:
            self.REMOTE_CONTROL_RESPONSE = "FAILURE: the parameters 'oldComponentName' and 'newComponentName' must be of type str."
            return
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
        if type(componentName) is not str or type(attribute) is not str:
            self.REMOTE_CONTROL_RESPONSE = "FAILURE: the parameters 'componentName' and 'attribute' must be of type str."
            return
        if hasattr(analysisContext.getComponentByName(componentName), attribute):
            attr = getattr(analysisContext.getComponentByName(componentName), attribute)
            if hasattr(attr, '__dict__') and self.isinstanceAminerClass(attr):
                newAttr = self.getAllVars(attr, '  ')
            elif isinstance(attr, list):
                for l in attr:
                    if hasattr(l, '__dict__') and self.isinstanceAminerClass(l):
                        newAttr = "\n[\n  " + l.__class__.__name__ + "  {\n" + self.getAllVars(l, '  ') + "  }\n]"
                    else:
                        newAttr = "%s = %s\n" % (attribute, repr(l))
            self.REMOTE_CONTROL_RESPONSE += "%s.%s = %s" % (componentName, attribute, newAttr)
        else:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the component '%s' does not have an attribute named '%s'"%(componentName, attribute)

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
            component = analysisContext.getComponentById(componentId)
            self.REMOTE_CONTROL_RESPONSE += self.getAllVars(component, '  ')
            self.REMOTE_CONTROL_RESPONSE += "}\n\n"

    def getAllVars(self, obj, indent):
        result = ''
        for var in vars(obj):
            attr = getattr(obj, var)
            if hasattr(attr, '__dict__') and self.isinstanceAminerClass(attr):
                result += indent + "%s = {\n"%var + self.getAllVars(attr, indent + '  ') + indent + "}\n"
            elif isinstance(attr, list):
                for l in attr:
                    if hasattr(l, '__dict__') and self.isinstanceAminerClass(l):
                        result += indent + "%s = [\n"%var + indent + '  ' + l.__class__.__name__ + " {\n" + self.getAllVars(l, indent + '    ') + indent + '  ' + "}\n" + indent + ']\n'
                    else:
                        result += indent + "%s = %s\n" % (var, repr(attr))
                        break
            else:
                result += indent + "%s = %s\n" % (var, repr(attr))
        return result

    def isinstanceAminerClass(self, obj):
        from aminer.analysis.TimeCorrelationDetector import CorrelationFeature
        from aminer.analysis.TimeCorrelationViolationDetector import CorrelationRule
        classList = [aminer.analysis.AtomFilters.SubhandlerFilter, aminer.analysis.AtomFilters.MatchPathFilter, aminer.analysis.AtomFilters.MatchValueFilter,
                     aminer.analysis.HistogramAnalysis.BinDefinition, aminer.analysis.HistogramAnalysis.HistogramData, aminer.analysis.Rules.MatchAction,
                     aminer.analysis.Rules.MatchRule, CorrelationRule, CorrelationFeature, aminer.events.EventHandlerInterface, aminer.util.ObjectHistory]
        for c in classList:
            if isinstance(obj, c):
                return True
        return False



        # result = ''
        # for var in vars(obj):
        #     attr = getattr(obj, var)
        #     if hasattr(attr, '__dict__'):
        #         ret = ''
        #         for v in vars(attr):
        #             ret = '    %s = %s\n'%(v, repr(attr))
        #         if ret == '':
        #             result += indent + '%s = %s\n'%(var, repr(attr))
        #         else:
        #             result += '%s = {\n'%var
        #             result += ret
        #             result += '}\n'
        #     #
        #     else:
        #         result += indent + "%s = %s\n" % (var, repr(attr))
        return result

    def saveCurrentConfig(self, analysisContext, destinationFile):
        self.REMOTE_CONTROL_RESPONSE = AMinerConfig.saveConfig(analysisContext, destinationFile)

    def whitelistEventInComponent(self, analysisContext, componentName, eventData, whitelistingData=None):
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
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: component with same name already registered! (%s)" % componentName
            return
        if not isinstance(component, AtomHandlerInterface):
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: 'component' must implement the AtomHandlerInterface!"
            return
        atomFilter.addHandler(component)
        analysisContext.registerComponent(component, componentName)
        self.REMOTE_CONTROL_RESPONSE += "Component '%s' added to '%s' successfully." % (
            componentName, atomHandler)

    def dumpEventsFromHistory(self, analysisContext, historyComponentName, dumpEventId):
        self.REMOTE_CONTROL_RESPONSE = None
        historyHandler = analysisContext.getComponentByName(historyComponentName)
        if historyHandler is None:
            self.REMOTE_CONTROL_RESPONSE = 'Event history component not found'
        else:
            historyData = historyHandler.getHistory()
            resultString = 'FAIL: not found'
            for eventPos in range(0, len(historyData)):
                eventId, eventType, eventMessage, sortedLogLines, eventData, eventSource = historyData[eventPos]
                if eventId != dumpEventId:
                    continue
                appendLogLinesFlag = True
                resultString = 'OK\nEvent %d: %s (%s)' % (eventId, eventMessage, eventType)
                if eventType == 'Analysis.NewMatchPathDetector':
                    resultString += '\n  Logline: %s' % (sortedLogLines[0],)
                elif eventType == 'Analysis.NewMatchPathValueComboDetector':
                    resultString += '\nParser match:\n' + eventData[0].parserMatch.matchElement.annotateMatch('  ')
                elif eventType == 'Analysis.WhitelistViolationDetector':
                    resultString += '\nParser match:\n' + eventData.parserMatch.matchElement.annotateMatch('  ')
                elif eventType == 'ParserModel.UnparsedData':
                    resultString += '\n  Unparsed line: %s' % sortedLogLines[0]
                    appendLogLinesFlag = False
                else:
                    resultString += '\n  Data: %s' % str(eventData)

                if appendLogLinesFlag and (sortedLogLines != None) and (len(sortedLogLines) != 0):
                    resultString += '\n  Log lines:\n    %s' % '\n    '.join(sortedLogLines)
                break
            self.REMOTE_CONTROL_RESPONSE = resultString

    def ignoreEventsFromHistory(self, analysisContext, historyComponentName, eventIds):
        historyHandler = analysisContext.getComponentByName(historyComponentName)
        if historyHandler is None:
            self.REMOTE_CONTROL_RESPONSE = 'Event history component not found'
            return
        historyData = historyHandler.getHistory()
        idSpecList = []
        for element in eventIds:
            if isinstance(element, list):
                idSpecList.append(element)
        deleteCount = 0
        eventPos = 0
        while eventPos < len(historyData):
            eventId, eventType, eventMessage, sortedLogLines, eventData, eventSource = historyData[eventPos]
            mayDeleteFlag = False
            if eventId in eventIds:
                mayDeleteFlag = True
            else:
                for idRange in idSpecList:
                    if (eventId >= idRange[0]) and (eventId <= idRange[1]):
                        mayDeleteFlag = True
            if mayDeleteFlag:
                historyData[:] = historyData[:eventPos] + historyData[eventPos + 1:]
                deleteCount += 1
            else:
                eventPos += 1
        self.REMOTE_CONTROL_RESPONSE = 'OK\n%d elements ignored' % deleteCount

    def listEventsFromHistory(self, analysisContext, historyComponentName, maxEventCount=None):
        historyHandler = analysisContext.getComponentByName(historyComponentName)
        if historyHandler is None:
            self.REMOTE_CONTROL_RESPONSE = 'Event history component not found'
        else:
            historyData = historyHandler.getHistory()
            maxEvents = len(historyData)
            if maxEventCount is None or maxEvents < maxEventCount:
                maxEventCount = maxEvents
            resultString = 'OK'
            for eventId, eventType, eventMessage, sortedLogLines, eventData, eventSource in historyData[:maxEventCount]:
                resultString += ('\nEvent %d: %s; Log data: %s' % (eventId, eventMessage, repr(sortedLogLines)))[:240]
            self.REMOTE_CONTROL_RESPONSE = resultString

    def whitelistEventsFromHistory(self, analysisContext, historyComponentName, idSpecList, whitelistingData=None):
        from aminer.events import EventSourceInterface
        historyHandler = analysisContext.getComponentByName(historyComponentName)
        if historyHandler is None:
            self.REMOTE_CONTROL_RESPONSE = 'Event history component not found'
            return
        elif idSpecList is None or not isinstance(idSpecList, list):
            self.REMOTE_CONTROL_RESPONSE = 'Request requires remoteControlData with ID specification list and optional whitelisting information'
            return
        historyData = historyHandler.getHistory()
        resultString = ''
        lookupCount = 0
        whitelistCount = 0
        eventPos = 0
        while eventPos < len(historyData):
            eventId, eventType, eventMessage, sortedLogLines, eventData, eventSource = historyData[eventPos]
            foundFlag = False
            if eventId in idSpecList:
                foundFlag = True
            else:
                for idRange in idSpecList:
                    if ((isinstance(idRange, list)) and (eventId >= idRange[0]) and
                            (eventId <= idRange[1])):
                        foundFlag = True
            if not foundFlag:
                eventPos += 1
                continue
            lookupCount += 1
            whitelistedFlag = False
            if isinstance(eventSource, EventSourceInterface):
                # This should be the default for all detectors.
                try:
                    message = eventSource.whitelistEvent(
                        eventType, sortedLogLines, eventData, whitelistingData)
                    resultString += 'OK %d: %s\n' % (eventId, message)
                    whitelistedFlag = True
                except Exception as wlException:
                    if isinstance(wlException, NotImplementedError):
                        resultString += 'FAIL %d: component does not support whitelisting' % eventId
                    else:
                        resultString += 'FAIL %d: %s\n' % (eventId, str(wlException))
            elif eventType == 'Analysis.WhitelistViolationDetector':
                resultString += 'FAIL %d: No automatic modification of whitelist rules, manual changes required\n' % eventId
                whitelistedFlag = True
            elif eventType == 'ParserModel.UnparsedData':
                resultString += 'FAIL %d: No automatic modification of parsers yet\n' % eventId
            else:
                resultString += 'FAIL %d: Unsupported event type %s\n' % (eventId, eventType)
            if whitelistedFlag:
                # Clear the whitelisted event.
                historyData[:] = historyData[:eventPos] + historyData[eventPos + 1:]
                whitelistCount += 1
            else:
                eventPos += 1
        if lookupCount == 0:
            resultString = 'FAIL: Not a single event ID from specification found'
        self.REMOTE_CONTROL_RESPONSE = resultString
