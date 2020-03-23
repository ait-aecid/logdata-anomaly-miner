"""This module contains methods which can be executed from the
AMinerRemoteControl class."""
import aminer
from aminer import AMinerConfig, AnalysisChild
import resource
import subprocess
from aminer.input import LogAtom
from aminer.input import AtomHandlerInterface

attr_str = "%s = %s\n"
component_not_found = 'Event history component not found'

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

    def print_response(self, value):
        self.REMOTE_CONTROL_RESPONSE += str(value)

    def change_config_property(self, analysis_context, property_name, value):
        result = 0
        config_keys_mail_alerting = {self.CONFIG_KEY_MAIL_TARGET_ADDRESS,
                                  self.CONFIG_KEY_MAIL_FROM_ADDRESS,
                                  self.CONFIG_KEY_MAIL_SUBJECT_PREFIX,
                                  self.CONFIG_KEY_EVENT_COLLECT_TIME,
                                  self.CONFIG_KEY_ALERT_MIN_GAP,
                                  self.CONFIG_KEY_ALERT_MAX_GAP,
                                  self.CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE}
        if not isinstance(analysis_context, AnalysisChild.AnalysisContext):
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the analysisContext must be of type %s." % AnalysisChild.AnalysisContext.__class__
            return

        if not property_name in analysis_context.aminer_config.configProperties:
            self.REMOTE_CONTROL_RESPONSE = "FAILURE: the property '%s' does not exist in the current config!" % property_name
            return

        t = type(analysis_context.aminer_config.configProperties[property_name])
        if not isinstance(value, t):
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the value of the property '%s' must be of type %s!" % (
                property_name, t)
            return

        if property_name == AMinerConfig.KEY_PERSISTENCE_DIR or property_name == AMinerConfig.KEY_LOG_SOURCES_LIST:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the property '%s' can only be changed at " \
                                            "startup in the AMiner root process!" % property_name
        elif property_name == AMinerConfig.KEY_RESOURCES_MAX_MEMORY_USAGE:
            result = self.change_config_property_max_memory(analysis_context, value)
        elif property_name == AMinerConfig.KEY_RESOURCES_MAX_PERCENT_CPU_USAGE:
            result = self.change_config_property_max_cpu_percent_usage(analysis_context, value)
        elif property_name in config_keys_mail_alerting:
            result = self.change_config_property_mail_alerting(analysis_context, property_name, value)
        elif property_name == AMinerConfig.KEY_LOG_PREFIX:
            result = self.change_config_property_log_prefix(analysis_context, value)
        else:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: property %s could not be changed. Please check the propertyName " \
                                            "again." % property_name
            return
        if result == 0:
            self.REMOTE_CONTROL_RESPONSE += "'%s' changed to '%s' successfully." % (property_name, value)

    def change_config_property_mail_alerting(self, analysis_context, property_name, value):
        analysis_context.aminerConfig.configProperties[property_name] = value
        for analysis_component_id in analysis_context.get_registered_component_ids():
            component = analysis_context.get_component_by_id(analysis_component_id)
            if component.__class__.__name__ == "DefaultMailNotificationEventHandler":
                setattr(component, property_name, value)
        return 0

    def change_config_property_max_memory(self, analysis_context, max_memory_mb):
        try:
            max_memory_mb = int(max_memory_mb)
            if max_memory_mb < 32 and max_memory_mb != -1:
                self.REMOTE_CONTROL_RESPONSE += "FAILURE: it is not safe to run the AMiner with less than 32MB RAM."
                return 1
            resource.setrlimit(resource.RLIMIT_AS, (max_memory_mb * 1024 * 1024, resource.RLIM_INFINITY))
            analysis_context.aminerConfig.configProperties[AMinerConfig.KEY_RESOURCES_MAX_MEMORY_USAGE] = max_memory_mb
            return 0
        except ValueError:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: property 'maxMemoryUsage' must be of type Integer!"
            return 1

    def change_config_property_max_cpu_percent_usage(self, max_cpu_percent_usage):
        try:
            max_cpu_percent_usage = int(max_cpu_percent_usage)
            # limit
            with subprocess.Popen(['pgrep', '-f', 'AMiner'], stdout=subprocess.PIPE, shell=False) as child:
                response = child.communicate()[0].split()
            pid = response[len(response) - 1]
            package_installed_cmd = ['dpkg', '-l', 'cpulimit']
            cpulimit_cmd = ['cpulimit', '-p', pid.decode(), '-l', str(max_cpu_percent_usage)]

            with subprocess.Popen(package_installed_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as out:
                stdout, stderr = out.communicate()

            if 'dpkg-query: no packages found matching cpulimit.' in stdout.decode():
                self.REMOTE_CONTROL_RESPONSE = 'FATAL: cpulimit package must be installed, '
                + 'when using the property %s.' % AMinerConfig.KEY_RESOURCES_MAX_PERCENT_CPU_USAGE
                return 1
            else:
                with subprocess.Popen(cpulimit_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as out:
                    return 0
        except ValueError:
            self.REMOTE_CONTROL_RESPONSE = 'FATAL: %s must be an integer, terminating.' % (
                AMinerConfig.KEY_RESOURCES_MAX_PERCENT_CPU_USAGE)
            return 1

    def change_config_property_log_prefix(self, analysis_context, log_prefix):
        analysis_context.aminerConfig.configProperties[AMinerConfig.KEY_LOG_PREFIX] = str(log_prefix)
        return 0

    def change_attribute_of_registered_analysis_component(self, analysis_context, component_name, attribute, value):
        attr = getattr(analysis_context.get_component_by_name(component_name), attribute)
        if type(attr) == type(value):
            setattr(analysis_context.get_component_by_name(component_name), attribute, value)
            self.REMOTE_CONTROL_RESPONSE += "'%s.%s' changed from %s to %s successfully." % (component_name,
                                                                                             attribute, repr(attr), value)
        else:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: property '%s.%s' must be of type %s!" % (component_name,
                                                                                               attribute, type(attr))

    def rename_registered_analysis_component(self, analysis_context, old_component_name, new_component_name):
        if type(old_component_name) is not str or type(new_component_name) is not str:
            self.REMOTE_CONTROL_RESPONSE = "FAILURE: the parameters 'oldComponentName' and 'newComponentName' must be of type str."
        else:
            component = analysis_context.get_component_by_name(old_component_name)
            if component is None:
                self.REMOTE_CONTROL_RESPONSE += "FAILURE: component '%s' does not exist!" % old_component_name
            else:
                analysis_context.registeredComponentsByName[old_component_name] = None
                analysis_context.registeredComponentsByName[new_component_name] = component
                self.REMOTE_CONTROL_RESPONSE += "Component '%s' renamed to '%s' successfully." % (
                    old_component_name, new_component_name)

    def print_config_property(self, analysis_context, property_name):
        self.REMOTE_CONTROL_RESPONSE = property_name + " : " + str(
            analysis_context.aminerConfig.configProperties[property_name])

    def print_attribute_of_registered_analysis_component(self, analysis_context, component_name, attribute):
        if type(component_name) is not str or type(attribute) is not str:
            self.REMOTE_CONTROL_RESPONSE = "FAILURE: the parameters 'componentName' and 'attribute' must be of type str."
            return
        if hasattr(analysis_context.get_component_by_name(component_name), attribute):
            attr = getattr(analysis_context.get_component_by_name(component_name), attribute)
            if hasattr(attr, '__dict__') and self.isinstance_aminer_class(attr):
                new_attr = self.get_all_vars(attr, '  ')
            elif isinstance(attr, list):
                for l in attr:
                    if hasattr(l, '__dict__') and self.isinstance_aminer_class(l):
                        new_attr = "\n[\n  " + l.__class__.__name__ + "  {\n" + self.get_all_vars(l, '  ') + "  }\n]"
                    else:
                        new_attr = attr_str % (attribute, repr(l))
            self.REMOTE_CONTROL_RESPONSE += "%s.%s = %s" % (component_name, attribute, new_attr)
        else:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the component '%s' does not have an attribute named '%s'"%(component_name, attribute)

    def print_current_config(self, analysis_context):
        for config_property in analysis_context.aminerConfig.configProperties:
            if isinstance(analysis_context.aminerConfig.configProperties[config_property], str):
                self.REMOTE_CONTROL_RESPONSE += "%s = '%s'\n" % (config_property,
                                                                 analysis_context.aminerConfig.configProperties[config_property])
            else:
                self.REMOTE_CONTROL_RESPONSE += attr_str % (config_property,
                                                               analysis_context.aminerConfig.configProperties[config_property])
        for component_id in analysis_context.get_registered_component_ids():
            self.REMOTE_CONTROL_RESPONSE += "%s {\n" % analysis_context.get_name_by_component(
                analysis_context.get_component_by_id(component_id))
            component = analysis_context.get_component_by_id(component_id)
            self.REMOTE_CONTROL_RESPONSE += self.get_all_vars(component, '  ')
            self.REMOTE_CONTROL_RESPONSE += "}\n\n"

    def get_all_vars(self, obj, indent):
        result = ''
        for var in vars(obj):
            attr = getattr(obj, var)
            if hasattr(attr, '__dict__') and self.isinstance_aminer_class(attr):
                result += indent + "%s = {\n" % var + self.get_all_vars(attr, indent + '  ') + indent + "}\n"
            elif isinstance(attr, list):
                for l in attr:
                    if hasattr(l, '__dict__') and self.isinstance_aminer_class(l):
                        result += indent + "%s = [\n" % var + indent + '  ' + l.__class__.__name__ + " {\n" + self.get_all_vars(l, indent + '    ') + indent + '  ' + "}\n" + indent + ']\n'
                    else:
                        result += indent + attr_str % (var, repr(attr))
                        break
            else:
                result += indent + attr_str % (var, repr(attr))
        return result

    def isinstance_aminer_class(self, obj):
        from aminer.analysis.TimeCorrelationDetector import CorrelationFeature
        from aminer.analysis.TimeCorrelationViolationDetector import CorrelationRule
        class_list = [aminer.analysis.AtomFilters.SubhandlerFilter, aminer.analysis.AtomFilters.MatchPathFilter, aminer.analysis.AtomFilters.MatchValueFilter,
                     aminer.analysis.HistogramAnalysis.BinDefinition, aminer.analysis.HistogramAnalysis.HistogramData, aminer.analysis.Rules.MatchAction,
                     aminer.analysis.Rules.MatchRule, CorrelationRule, CorrelationFeature, aminer.events.EventHandlerInterface, aminer.util.ObjectHistory]
        for c in class_list:
            if isinstance(obj, c):
                return True
        return False

    def save_current_config(self, analysis_context, destination_file):
        self.REMOTE_CONTROL_RESPONSE = AMinerConfig.save_config(analysis_context, destination_file)

    def whitelist_event_in_component(self, analysis_context, component_name, event_data, whitelisting_data=None):
        component = analysis_context.get_component_by_name(component_name)
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
                self.REMOTE_CONTROL_RESPONSE += component.whitelist_event("Analysis.%s" % component.__class__.__name__,
                                                                          [component.__class__.__name__], event_data, whitelisting_data)
            else:
                self.REMOTE_CONTROL_RESPONSE += component.whitelist_event("Analysis.%s" % component.__class__.__name__,
                                                                          [component.__class__.__name__], [LogAtom("", None, 1666.0, None), event_data], whitelisting_data)
        except Exception as e:
            self.REMOTE_CONTROL_RESPONSE += "Exception: " + repr(e)

    def add_handler_to_atom_filter_and_register_analysis_component(self, analysis_context, atom_handler, component, component_name):
        atom_filter = analysis_context.get_component_by_name(atom_handler)
        if atom_filter is None:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: atomHandler '%s' does not exist!" % atom_handler
            return
        if analysis_context.get_component_by_name(component_name) is not None:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: component with same name already registered! (%s)" % component_name
            return
        if not isinstance(component, AtomHandlerInterface):
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: 'component' must implement the AtomHandlerInterface!"
            return
        atom_filter.add_handler(component)
        analysis_context.register_component(component, component_name)
        self.REMOTE_CONTROL_RESPONSE += "Component '%s' added to '%s' successfully." % (
            component_name, atom_handler)

    def dump_events_from_history(self, analysis_context, history_component_name, dump_event_id):
        self.REMOTE_CONTROL_RESPONSE = None
        history_handler = analysis_context.get_component_by_name(history_component_name)
        if history_handler is None:
            self.REMOTE_CONTROL_RESPONSE = component_not_found
        else:
            history_data = history_handler.get_history()
            result_string = 'FAIL: not found'
            for event_pos in range(0, len(history_data)):
                event_id, event_type, event_message, sorted_log_lines, event_data, event_source = history_data[event_pos]
                if event_id != dump_event_id:
                    continue
                append_log_lines_flag = True
                result_string = 'OK\nEvent %d: %s (%s)' % (event_id, event_message, event_type)
                if event_type == 'Analysis.NewMatchPathDetector':
                    result_string += '\n  Logline: %s' % (sorted_log_lines[0],)
                elif event_type == 'Analysis.NewMatchPathValueComboDetector':
                    result_string += '\nParser match:\n' + event_data[0].parserMatch.matchElement.annotate_match('  ')
                elif event_type == 'Analysis.WhitelistViolationDetector':
                    result_string += '\nParser match:\n' + event_data.parserMatch.matchElement.annotate_match('  ')
                elif event_type == 'ParserModel.UnparsedData':
                    result_string += '\n  Unparsed line: %s' % sorted_log_lines[0]
                    append_log_lines_flag = False
                else:
                    result_string += '\n  Data: %s' % str(event_data)

                if append_log_lines_flag and (sorted_log_lines != None) and (len(sorted_log_lines) != 0):
                    result_string += '\n  Log lines:\n    %s' % '\n    '.join(sorted_log_lines)
                break
            self.REMOTE_CONTROL_RESPONSE = result_string

    def ignore_events_from_history(self, analysis_context, history_component_name, event_ids):
        history_handler = analysis_context.get_component_by_name(history_component_name)
        if history_handler is None:
            self.REMOTE_CONTROL_RESPONSE = component_not_found
            return
        history_data = history_handler.get_history()
        id_spec_list = []
        for element in event_ids:
            if isinstance(element, list):
                id_spec_list.append(element)
        delete_count = 0
        event_pos = 0
        while event_pos < len(history_data):
            event_id, event_type, event_message, sorted_log_lines, event_data, event_source = history_data[event_pos]
            may_delete_flag = False
            if event_id in event_ids:
                may_delete_flag = True
            else:
                for id_range in id_spec_list:
                    if (event_id >= id_range[0]) and (event_id <= id_range[1]):
                        may_delete_flag = True
            if may_delete_flag:
                history_data[:] = history_data[:event_pos] + history_data[event_pos + 1:]
                delete_count += 1
            else:
                event_pos += 1
        self.REMOTE_CONTROL_RESPONSE = 'OK\n%d elements ignored' % delete_count

    def list_events_from_history(self, analysis_context, history_component_name, max_event_count=None):
        history_handler = analysis_context.get_component_by_name(history_component_name)
        if history_handler is None:
            self.REMOTE_CONTROL_RESPONSE = component_not_found
        else:
            history_data = history_handler.get_history()
            max_events = len(history_data)
            if max_event_count is None or max_events < max_event_count:
                max_event_count = max_events
            result_string = 'OK'
            for event_id, event_type, event_message, sorted_log_lines, event_data, event_source in history_data[:max_event_count]:
                result_string += ('\nEvent %d: %s; Log data: %s' % (event_id, event_message, repr(sorted_log_lines)))[:240]
            self.REMOTE_CONTROL_RESPONSE = result_string

    def whitelist_events_from_history(self, analysis_context, history_component_name, id_spec_list, whitelisting_data=None):
        from aminer.events import EventSourceInterface
        history_handler = analysis_context.get_component_by_name(history_component_name)
        if history_handler is None:
            self.REMOTE_CONTROL_RESPONSE = component_not_found
            return
        elif id_spec_list is None or not isinstance(id_spec_list, list):
            self.REMOTE_CONTROL_RESPONSE = 'Request requires remoteControlData with ID specification list and optional whitelisting information'
            return
        history_data = history_handler.get_history()
        result_string = ''
        lookup_count = 0
        event_pos = 0
        while event_pos < len(history_data):
            event_id, event_type, event_message, sorted_log_lines, event_data, event_source = history_data[event_pos]
            found_flag = False
            if event_id in id_spec_list:
                found_flag = True
            else:
                for id_range in id_spec_list:
                    if ((isinstance(id_range, list)) and (event_id >= id_range[0]) and
                            (event_id <= id_range[1])):
                        found_flag = True
            if not found_flag:
                event_pos += 1
                continue
            lookup_count += 1
            whitelisted_flag = False
            if isinstance(event_source, EventSourceInterface):
                # This should be the default for all detectors.
                try:
                    message = event_source.whitelist_event(
                        event_type, sorted_log_lines, event_data, whitelisting_data)
                    result_string += 'OK %d: %s\n' % (event_id, message)
                    whitelisted_flag = True
                except Exception as wlException:
                    if isinstance(wlException, NotImplementedError):
                        result_string += 'FAIL %d: component does not support whitelisting' % event_id
                    else:
                        result_string += 'FAIL %d: %s\n' % (event_id, str(wlException))
            elif event_type == 'Analysis.WhitelistViolationDetector':
                result_string += 'FAIL %d: No automatic modification of whitelist rules, manual changes required\n' % event_id
                whitelisted_flag = True
            elif event_type == 'ParserModel.UnparsedData':
                result_string += 'FAIL %d: No automatic modification of parsers yet\n' % event_id
            else:
                result_string += 'FAIL %d: Unsupported event type %s\n' % (event_id, event_type)
            if whitelisted_flag:
                # Clear the whitelisted event.
                history_data[:] = history_data[:event_pos] + history_data[event_pos + 1:]
            else:
                event_pos += 1
        if lookup_count == 0:
            result_string = 'FAIL: Not a single event ID from specification found'
        self.REMOTE_CONTROL_RESPONSE = result_string
