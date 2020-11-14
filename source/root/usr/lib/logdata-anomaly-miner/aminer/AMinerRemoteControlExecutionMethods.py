"""This module contains methods which can be executed from the AMinerRemoteControl class.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""
import aminer
from aminer import AMinerConfig, AnalysisChild
import resource
import logging
from aminer.input import LogAtom
from aminer.input import AtomHandlerInterface

attr_str = '"%s": %s,\n'
component_not_found = 'Event history component not found'


class AMinerRemoteControlExecutionMethods:
    """This class defines all possible methods for the remote control."""

    REMOTE_CONTROL_RESPONSE = ''
    ERROR_MESSAGE_RESOURCE_NOT_FOUND = '"Resource \\"%s\\" could not be found."'

    CONFIG_KEY_MAIL_TARGET_ADDRESS = 'MailAlerting.TargetAddress'
    CONFIG_KEY_MAIL_FROM_ADDRESS = 'MailAlerting.FromAddress'
    CONFIG_KEY_MAIL_SUBJECT_PREFIX = 'MailAlerting.SubjectPrefix'
    CONFIG_KEY_MAIL_ALERT_GRACE_TIME = 'MailAlerting.AlertGraceTime'
    CONFIG_KEY_EVENT_COLLECT_TIME = 'MailAlerting.EventCollectTime'
    CONFIG_KEY_ALERT_MIN_GAP = 'MailAlerting.MinAlertGap'
    CONFIG_KEY_ALERT_MAX_GAP = 'MailAlerting.MaxAlertGap'
    CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE = 'MailAlerting.MaxEventsPerMessage'

    def print_response(self, value):
        """Add a value to the response string."""
        self.REMOTE_CONTROL_RESPONSE += str(value)

    def change_config_property(self, analysis_context, property_name, value):
        """Change a config_property in an running aminer instance."""
        result = 0
        config_keys_mail_alerting = {
            self.CONFIG_KEY_MAIL_TARGET_ADDRESS, self.CONFIG_KEY_MAIL_FROM_ADDRESS, self.CONFIG_KEY_MAIL_SUBJECT_PREFIX,
            self.CONFIG_KEY_EVENT_COLLECT_TIME, self.CONFIG_KEY_ALERT_MIN_GAP, self.CONFIG_KEY_ALERT_MAX_GAP,
            self.CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE}
        if not isinstance(analysis_context, AnalysisChild.AnalysisContext):
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the analysis_context must be of type %s." % AnalysisChild.AnalysisContext.__class__
            return

        if property_name not in analysis_context.aminer_config.config_properties:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the property '%s' does not exist in the current config!" % property_name
            return

        t = type(analysis_context.aminer_config.config_properties[property_name])
        if not isinstance(value, t):
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the value of the property '%s' must be of type %s!" % (
                property_name, t)
            return

        if property_name in [AMinerConfig.KEY_PERSISTENCE_DIR, AMinerConfig.KEY_LOG_SOURCES_LIST]:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the property '%s' can only be changed at " \
                                            "startup in the AMiner root process!" % property_name
            return
        if property_name == AMinerConfig.KEY_RESOURCES_MAX_MEMORY_USAGE:
            result = self.change_config_property_max_memory(analysis_context, value)
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

    @staticmethod
    def change_config_property_mail_alerting(analysis_context, property_name, value):
        """Change any mail property."""
        analysis_context.aminer_config.config_properties[property_name] = value
        for analysis_component_id in analysis_context.get_registered_component_ids():
            component = analysis_context.get_component_by_id(analysis_component_id)
            if component.__class__.__name__ == "DefaultMailNotificationEventHandler":
                setattr(component, property_name, value)
        return 0

    def change_config_property_max_memory(self, analysis_context, max_memory_mb):
        """Change the maximal allowed RAM usage of the aminer instance."""
        try:
            max_memory_mb = int(max_memory_mb)
            if max_memory_mb < 32 and max_memory_mb != -1:
                self.REMOTE_CONTROL_RESPONSE += "FAILURE: it is not safe to run the AMiner with less than 32MB RAM."
                return 1
            resource.setrlimit(resource.RLIMIT_AS, (max_memory_mb * 1024 * 1024, resource.RLIM_INFINITY))
            analysis_context.aminer_config.config_properties[AMinerConfig.KEY_RESOURCES_MAX_MEMORY_USAGE] = max_memory_mb
            return 0
        except ValueError:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: property 'maxMemoryUsage' must be of type Integer!"
            return 1

    @staticmethod
    def change_config_property_log_prefix(analysis_context, log_prefix):
        """Change the config_property LogPrefix."""
        analysis_context.aminer_config.config_properties[AMinerConfig.KEY_LOG_PREFIX] = str(log_prefix)
        return 0

    def change_attribute_of_registered_analysis_component(self, analysis_context, component_name, attribute, value):
        """
        Change a specific attribute of a registered component.
        @param analysis_context the analysis context of the AMiner.
        @param component_name the name to be registered in the analysis_context.
        @param attribute the name of the attribute to be printed.
        @param value the new value of the attribute.
        """
        attr = getattr(analysis_context.get_component_by_name(component_name), attribute, None)
        if type(attr) is type(value):
            setattr(analysis_context.get_component_by_name(component_name), attribute, value)
            self.REMOTE_CONTROL_RESPONSE += "'%s.%s' changed from %s to %s successfully." % (component_name,
                                                                                             attribute, repr(attr), value)
        else:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: property '%s.%s' must be of type %s!" % (component_name,
                                                                                               attribute, type(attr))

    def rename_registered_analysis_component(self, analysis_context, old_component_name, new_component_name):
        """
        Rename an analysis component by removing and readding it to the analysis_context.
        @param analysis_context the analysis context of the AMiner.
        @param old_component_name the current name of the component.
        @param new_component_name the new name of the component.
        """
        if type(old_component_name) is not str or type(new_component_name) is not str:
            self.REMOTE_CONTROL_RESPONSE = "FAILURE: the parameters 'oldComponentName' and 'newComponentName' must be of type str."
        else:
            component = analysis_context.get_component_by_name(old_component_name)
            if component is None:
                self.REMOTE_CONTROL_RESPONSE += "FAILURE: the component '%s' does not exist." % old_component_name
            else:
                analysis_context.registered_components_by_name[old_component_name] = None
                analysis_context.registered_components_by_name[new_component_name] = component
                self.REMOTE_CONTROL_RESPONSE += "Component '%s' renamed to '%s' successfully." % (
                    old_component_name, new_component_name)

    def change_log_stat_level(self, level):
        """Change the STAT_LEVEL."""
        level = int(level)
        if level in (0, 1, 2):
            AMinerConfig.STAT_LEVEL = level
            self.REMOTE_CONTROL_RESPONSE += "Changed STAT_LEVEL to %d" % level
        else:
            self.REMOTE_CONTROL_RESPONSE += "Could not change STAT_LEVEL to %d. Allowed STAT_LEVEL values are 0, 1, 2." % level

    def change_log_debug_level(self, level):
        """Change the DEBUG_LEVEL."""
        level = int(level)
        if level in (0, 1, 2):
            AMinerConfig.DEBUG_LEVEL = level
            debug_logger = logging.getLogger(AMinerConfig.DEBUG_LOG_NAME)
            if AMinerConfig.DEBUG_LEVEL == 0:
                debug_logger.setLevel(logging.ERROR)
            elif AMinerConfig.DEBUG_LEVEL == 1:
                debug_logger.setLevel(logging.INFO)
            else:
                debug_logger.setLevel(logging.DEBUG)
            self.REMOTE_CONTROL_RESPONSE += "Changed DEBUG_LEVEL to %d" % level
        else:
            self.REMOTE_CONTROL_RESPONSE += "Could not change DEBUG_LEVEL to %d. Allowed DEBUG_LEVEL values are 0, 1, 2." % level

    def print_config_property(self, analysis_context, property_name):
        """
        Print a specific config property.
        @param analysis_context the analysis context of the AMiner.
        @param property_name the name of the property to be printed.
        """
        if property_name not in analysis_context.aminer_config.config_properties:
            self.REMOTE_CONTROL_RESPONSE = self.ERROR_MESSAGE_RESOURCE_NOT_FOUND % property_name
            return
        val = analysis_context.aminer_config.config_properties[property_name]
        if isinstance(val, list):
            val = str(val).replace('"False"', 'false').replace('"True"', 'true').replace('"None"', 'null').strip(' ').replace("'", '"')
        else:
            val = str(val).replace('"False"', 'false').replace('"True"', 'true').replace('"None"', 'null').strip(' ')
            if val.isdigit():
                val = int(val)
            elif '.' in val:
                try:
                    val = float(val)
                except:  # skipcq: FLK-E722
                    pass
        self.REMOTE_CONTROL_RESPONSE = '"%s": %s' % (property_name, val)

    def print_attribute_of_registered_analysis_component(self, analysis_context, component_name, attribute):
        """
        Print a specific attribute of a registered component.
        @param analysis_context the analysis context of the AMiner.
        @param component_name the name to be registered in the analysis_context.
        @param attribute the name of the attribute to be printed.
        """
        if type(component_name) is not str or type(attribute) is not str:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the parameters 'component_name' and 'attribute' must be of type str."
            return
        if analysis_context.get_component_by_name(component_name) is None:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the component '%s' does not exist." % component_name
            return
        if hasattr(analysis_context.get_component_by_name(component_name), attribute):
            attr = getattr(analysis_context.get_component_by_name(component_name), attribute, None)
            if isinstance(attr, set):
                attr = list(attr)
            if hasattr(attr, '__dict__') and self.isinstance_aminer_class(attr):
                new_attr = self.get_all_vars(attr, '  ')
                if isinstance(new_attr, str):
                    new_attr = '"%s"' % new_attr
                self.REMOTE_CONTROL_RESPONSE += '"%s.%s": %s' % (component_name, attribute, new_attr)
            elif isinstance(attr, list):
                self.REMOTE_CONTROL_RESPONSE += '"%s.%s": [' % (component_name, attribute)
                for l in attr:
                    if hasattr(l, '__dict__') and self.isinstance_aminer_class(l):
                        new_attr = "\n[\n  " + l.__class__.__name__ + "  {\n" + self.get_all_vars(l, '  ') + "  }\n]"
                    else:
                        if isinstance(l, str):
                            new_attr = '"%s"' % l
                        else:
                            new_attr = str(l)
                    self.REMOTE_CONTROL_RESPONSE += "%s, " % new_attr
                self.REMOTE_CONTROL_RESPONSE = self.REMOTE_CONTROL_RESPONSE.rstrip(", ")
                self.REMOTE_CONTROL_RESPONSE += "]"
            else:
                if attr is None or isinstance(attr, (str, bool)):
                    attr = '"%s"' % attr
                self.REMOTE_CONTROL_RESPONSE += '"%s.%s": %s' % (component_name, attribute, attr)
            self.REMOTE_CONTROL_RESPONSE = self.REMOTE_CONTROL_RESPONSE.replace('"False"', 'false').replace('"True"', 'true').replace(
                '"None"', 'null')
        else:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the component '%s' does not have an attribute named '%s'." % \
                                            (component_name, attribute)

    def print_current_config(self, analysis_context):
        """
        Print the entire AMiner config.
        @param analysis_context the analysis context of the AMiner.
        """
        for config_property in analysis_context.aminer_config.config_properties:
            if isinstance(analysis_context.aminer_config.config_properties[config_property], str):
                self.REMOTE_CONTROL_RESPONSE += '"%s": "%s",\n' % (
                    config_property, analysis_context.aminer_config.config_properties[config_property])
            else:
                self.REMOTE_CONTROL_RESPONSE += attr_str % (
                    config_property, analysis_context.aminer_config.config_properties[config_property])
        for component_id in analysis_context.get_registered_component_ids():
            self.REMOTE_CONTROL_RESPONSE += '"%s": {\n' % analysis_context.get_name_by_component(
                analysis_context.get_component_by_id(component_id))
            component = analysis_context.get_component_by_id(component_id)
            self.REMOTE_CONTROL_RESPONSE += self.get_all_vars(component, '  ')
            self.REMOTE_CONTROL_RESPONSE += "},\n\n"
        self.REMOTE_CONTROL_RESPONSE = self.REMOTE_CONTROL_RESPONSE.replace("'", '"').replace('"False"', 'false').replace(
            '"True"', 'true').replace('"None"', 'null').replace('\\"', "'").rstrip(',\n\n\n') + '\n\n'

    def get_all_vars(self, obj, indent):
        """Return all variables in string representation."""
        result = ''
        for var in vars(obj):
            attr = getattr(obj, var, None)
            if attr is not None and isinstance(attr, (tuple, set)):
                attr = list(attr)
            if attr is not None and hasattr(attr, '__dict__') and self.isinstance_aminer_class(attr):
                result += indent + '"%s": {\n' % var + self.get_all_vars(attr, indent + '  ') + indent + "},\n"
            elif isinstance(attr, list):
                for l in attr:
                    if hasattr(l, '__dict__') and self.isinstance_aminer_class(l):
                        result += indent + '"%s": {\n' % var + indent + '  "' + l.__class__.__name__ + \
                                  '": {\n' + self.get_all_vars(l, indent + '    ') + indent + '  ' + "}\n" + indent + '},\n'
                    else:
                        rep = _reformat_attr(attr)
                        result += indent + attr_str % (var, rep)
                        break
            else:
                rep = _reformat_attr(attr)
                result += indent + attr_str % (var, rep)
        return result.rstrip(',\n') + '\n'

    @staticmethod
    def isinstance_aminer_class(obj):
        """Test if an object is of an instance of a aminer class."""
        from aminer.analysis.TimeCorrelationDetector import CorrelationFeature
        from aminer.analysis.TimeCorrelationViolationDetector import CorrelationRule
        class_list = [
            aminer.analysis.AtomFilters.SubhandlerFilter, aminer.analysis.AtomFilters.MatchPathFilter,
            aminer.analysis.AtomFilters.MatchValueFilter, aminer.analysis.HistogramAnalysis.BinDefinition,
            aminer.analysis.HistogramAnalysis.HistogramData, aminer.analysis.Rules.MatchAction, aminer.analysis.Rules.MatchRule,
            CorrelationRule, CorrelationFeature, aminer.events.EventHandlerInterface, aminer.util.ObjectHistory]
        for c in class_list:
            if isinstance(obj, c):
                return True
        return False

    def save_current_config(self, analysis_context, destination_file):
        """
        Save the current live config into a file.
        @param analysis_context the analysis context of the AMiner.
        @param destination_file the path to the file in which the config is saved.
        """
        self.REMOTE_CONTROL_RESPONSE = AMinerConfig.save_config(analysis_context, destination_file)

    def allowlist_event_in_component(self, analysis_context, component_name, event_data, allowlisting_data=None):
        """
        Allowlists one or multiple specific events from the history in the component it occurred in.
        @param analysis_context the analysis context of the AMiner.
        @param component_name the name to be registered in the analysis_context.
        @param event_data the event_data for the allowlist_event method.
        @param allowlisting_data this data is passed on into the allowlist_event method.
        """
        component = analysis_context.get_component_by_name(component_name)
        if component is None:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: component '%s' does not exist!" % component
            return
        if component.__class__.__name__ not in ["EnhancedNewMatchPathValueComboDetector", "MissingMatchPathValueDetector",
                                                "NewMatchPathDetector", "NewMatchPathValueComboDetector"]:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: component class '%s' does not support allowlisting! Only the following classes " \
                                            "support allowlisting: EnhancedNewMatchPathValueComboDetector, MissingMatchPathValueDetector," \
                                            " NewMatchPathDetector and NewMatchPathValueComboDetector." % component.__class__.__name__
            return
        try:
            if component.__class__.__name__ == "MissingMatchPathValueDetector":
                self.REMOTE_CONTROL_RESPONSE += component.allowlist_event("Analysis.%s" % component.__class__.__name__,
                                                                          [component.__class__.__name__], event_data, allowlisting_data)
            else:
                self.REMOTE_CONTROL_RESPONSE += component.allowlist_event(
                    "Analysis.%s" % component.__class__.__name__, [component.__class__.__name__],
                    [LogAtom("", None, 1666.0, None), event_data], allowlisting_data)
        # skipcq: PYL-W0703
        except Exception as e:
            self.REMOTE_CONTROL_RESPONSE += "Exception: " + repr(e)

    def add_handler_to_atom_filter_and_register_analysis_component(self, analysis_context, atom_handler, component, component_name):
        """
        Add a new component to the analysis_context.
        @param analysis_context the analysis context of the AMiner.
        @param atom_handler the registered name of the atom_handler component to add the new component to.
        @param component the component to be added.
        @param component_name the name to be registered in the analysis_context.
        """
        atom_filter = analysis_context.get_component_by_name(atom_handler)
        if atom_filter is None:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: atom_handler '%s' does not exist!" % atom_handler
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
        """
        Detailed print of a specific event from the history.
        @param analysis_context the analysis context of the AMiner.
        @param history_component_name the registered name of the history component.
        @param dump_event_id a numeric id of the events to be printed.
        """
        self.REMOTE_CONTROL_RESPONSE = None
        history_handler = analysis_context.get_component_by_name(history_component_name)
        if history_handler is None:
            self.REMOTE_CONTROL_RESPONSE = component_not_found
        else:
            history_data = history_handler.get_history()
            result_string = 'FAIL: not found'
            for event_pos in enumerate(history_data):
                event_id, event_type, event_message, sorted_log_lines, event_data, _event_source = history_data[event_pos]
                if event_id != dump_event_id:
                    continue
                append_log_lines_flag = True
                result_string = 'OK\nEvent %d: %s (%s)' % (event_id, event_message, event_type)
                if event_type == 'Analysis.NewMatchPathDetector':
                    result_string += '\n  Logline: %s' % (sorted_log_lines[0],)
                elif event_type == 'Analysis.NewMatchPathValueComboDetector':
                    result_string += '\nParser match:\n' + event_data[0].parser_match.matchElement.annotate_match('  ')
                elif event_type == 'Analysis.AllowlistViolationDetector':
                    result_string += '\nParser match:\n' + event_data.parser_match.matchElement.annotate_match('  ')
                elif event_type == 'ParserModel.UnparsedData':
                    result_string += '\n  Unparsed line: %s' % sorted_log_lines[0]
                    append_log_lines_flag = False
                else:
                    result_string += '\n  Data: %s' % str(event_data)

                if append_log_lines_flag and (sorted_log_lines is not None) and (len(sorted_log_lines) != 0):
                    result_string += '\n  Log lines:\n    %s' % '\n    '.join(sorted_log_lines)
                break
            self.REMOTE_CONTROL_RESPONSE = result_string

    def ignore_events_from_history(self, analysis_context, history_component_name, event_ids):
        """
        Ignore one or multiple specific events from the history. These ignores do not affect the components itself.
        @param analysis_context the analysis context of the AMiner.
        @param history_component_name the registered name of the history component.
        @param event_ids a list of numeric ids of the events to be ignored.
        """
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
            event_id, _event_type, _event_message, _sorted_log_lines, _event_data, _event_source = history_data[event_pos]
            may_delete_flag = False
            if event_id in event_ids:
                may_delete_flag = True
            else:
                for id_range in id_spec_list:
                    if id_range[0] <= event_id <= id_range[1]:
                        may_delete_flag = True
            if may_delete_flag:
                history_data[:] = history_data[:event_pos] + history_data[event_pos + 1:]
                delete_count += 1
            else:
                event_pos += 1
        self.REMOTE_CONTROL_RESPONSE = 'OK\n%d elements ignored' % delete_count

    def list_events_from_history(self, analysis_context, history_component_name, max_event_count=None):
        """
        List the latest events of a specific history component.
        @param analysis_context the analysis context of the AMiner.
        @param history_component_name the registered name of the history component.
        @param max_event_count the number of the newest events to be listed.
        """
        history_handler = analysis_context.get_component_by_name(history_component_name)
        if history_handler is None:
            self.REMOTE_CONTROL_RESPONSE = component_not_found
        else:
            history_data = history_handler.get_history()
            max_events = len(history_data)
            if max_event_count is None or max_events < max_event_count:
                max_event_count = max_events
            result_string = 'OK'
            for event_id, _event_type, event_message, sorted_log_lines, _event_data, _event_source in history_data[:max_event_count]:
                result_string += ('\nEvent %d: %s; Log data: %s' % (event_id, event_message, repr(sorted_log_lines)))[:240]
            self.REMOTE_CONTROL_RESPONSE = result_string

    def allowlist_events_from_history(self, analysis_context, history_component_name, id_spec_list, allowlisting_data=None):
        """
        Allowlists one or multiple specific events from the history in the component it occurred in.
        @param analysis_context the analysis context of the AMiner.
        @param history_component_name the registered name of the history component.
        @param id_spec_list a list of numeric ids of the events to be allowlisted.
        @param allowlisting_data this data is passed on into the allowlist_event method.
        """
        from aminer.events import EventSourceInterface
        history_handler = analysis_context.get_component_by_name(history_component_name)
        if history_handler is None:
            self.REMOTE_CONTROL_RESPONSE = component_not_found
            return
        if id_spec_list is None or not isinstance(id_spec_list, list):
            self.REMOTE_CONTROL_RESPONSE = \
                'Request requires remote_control_data with ID specification list and optional allowlisting information'
            return
        history_data = history_handler.get_history()
        result_string = ''
        lookup_count = 0
        event_pos = 0
        while event_pos < len(history_data):
            event_id, event_type, _event_message, sorted_log_lines, event_data, event_source = history_data[event_pos]
            found_flag = False
            if event_id in id_spec_list:
                found_flag = True
            else:
                for id_range in id_spec_list:
                    if isinstance(id_range, list) and (id_range[0] <= event_id <= id_range[1]):
                        found_flag = True
            if not found_flag:
                event_pos += 1
                continue
            lookup_count += 1
            allowlisted_flag = False
            if isinstance(event_source, EventSourceInterface):
                # This should be the default for all detectors.
                try:
                    message = event_source.allowlist_event(
                        event_type, sorted_log_lines, event_data, allowlisting_data)
                    result_string += 'OK %d: %s\n' % (event_id, message)
                    allowlisted_flag = True
                except NotImplementedError:
                    result_string += 'FAIL %d: component does not support allowlisting' % event_id
                # skipcq: PYL-W0703
                except Exception as wlException:
                    result_string += 'FAIL %d: %s\n' % (event_id, str(wlException))
            elif event_type == 'Analysis.AllowlistViolationDetector':
                result_string += 'FAIL %d: No automatic modification of allowlist rules, manual changes required\n' % event_id
                allowlisted_flag = True
            elif event_type == 'ParserModel.UnparsedData':
                result_string += 'FAIL %d: No automatic modification of parsers yet\n' % event_id
            else:
                result_string += 'FAIL %d: Unsupported event type %s\n' % (event_id, event_type)
            if allowlisted_flag:
                # Clear the allowlisted event.
                history_data[:] = history_data[:event_pos] + history_data[event_pos + 1:]
            else:
                event_pos += 1
        if lookup_count == 0:
            result_string = 'FAIL: Not a single event ID from specification found'
        self.REMOTE_CONTROL_RESPONSE = result_string


def _repr_recursive(attr):
    """
    Return a valid JSON representation of an config attribute with the types list, dict, set or tuple.
    @param attr the attribute to be represented.
    """
    if attr is None:
        return None
    if isinstance(attr, (bool, type(AMinerConfig))):
        rep = str(attr)
    elif isinstance(attr, (int, str, float)):
        rep = attr
    elif isinstance(attr, bytes):
        rep = attr.decode()
    elif isinstance(attr, (list, tuple, set)):
        if isinstance(attr, (tuple, set)):
            attr = list(attr)
        for i, a in enumerate(attr):
            attr[i] = _repr_recursive(a)
        rep = str(attr).replace('\\"', "'").replace("'[", "[").replace("]'", "]").replace("'", '"').replace('"False"', 'false').replace(
            '"True"', 'true').replace('"None"', 'null')
    elif isinstance(attr, dict):
        new_attr = {}
        for key in attr.keys():
            new_attr[str(key)] = _repr_recursive(key).replace('\\"', "'")
        rep = str(new_attr).replace("'[", "[").replace("]'", "]")
    else:
        rep = attr.__class__.__name__
    return rep


def _reformat_attr(attr):
    """
    Return a valid JSON representation of an config attribute with any type.
    If the type is list, dict, set or tuple _repr_recursive is called.
    @param attr the attribute to be represented.
    """
    if type(attr) in (int, str, float, bool, type(AMinerConfig), type(None)):
        rep = str(attr)
    elif isinstance(attr, bytes):
        rep = attr.decode()
    elif isinstance(attr, (list, dict, set, tuple)):
        rep = _repr_recursive(attr)
    else:
        rep = attr.__class__.__name__

    if rep.startswith("'") and rep.endswith("'") and rep.count("'") == 2:
        rep = rep.replace("'", '"')
    elif rep.strip('"').startswith("'") and rep.strip('"').endswith("'") and rep.strip('"').count("'") == 2:
        rep = rep.strip('"').replace("'", '"')
    else:
        rep = rep.strip('"').replace("'", '\\"')
    if not isinstance(attr, (list, dict, tuple, set)):
        if not rep.startswith('"') and not rep.isdecimal():
            try:
                float(rep)
            except:  # skipcq: FLK-E722
                rep = '"%s"' % rep
    return rep
