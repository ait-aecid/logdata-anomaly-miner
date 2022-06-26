"""This module contains methods which can be executed from the aminerRemoteControl class.

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
import resource
import os
import shutil
from time import time
from datetime import datetime
import logging
import re
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util import PersistenceUtil
from aminer import AnalysisChild, AminerConfig
from aminer.AminerConfig import KEY_PERSISTENCE_PERIOD, KEY_LOG_STAT_LEVEL, KEY_LOG_DEBUG_LEVEL, KEY_LOG_STAT_PERIOD,\
    KEY_RESOURCES_MAX_MEMORY_USAGE, KEY_LOG_PREFIX, KEY_PERSISTENCE_DIR, DEFAULT_PERSISTENCE_DIR, KEY_LOG_SOURCES_LIST, DEBUG_LOG_NAME

attr_str = '"%s": %s,\n'
component_not_found = 'Event history component not found.'


class AminerRemoteControlExecutionMethods:
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

    MAIL_CONFIG_PROPERTIES = [CONFIG_KEY_MAIL_TARGET_ADDRESS, CONFIG_KEY_MAIL_FROM_ADDRESS]
    INTEGER_CONFIG_PROPERTY_LIST = [
        CONFIG_KEY_MAIL_ALERT_GRACE_TIME, CONFIG_KEY_EVENT_COLLECT_TIME, CONFIG_KEY_ALERT_MIN_GAP, CONFIG_KEY_ALERT_MAX_GAP,
        CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE, KEY_PERSISTENCE_PERIOD, KEY_LOG_STAT_LEVEL, KEY_LOG_DEBUG_LEVEL, KEY_LOG_STAT_PERIOD,
        KEY_RESOURCES_MAX_MEMORY_USAGE
    ]
    STRING_CONFIG_PROPERTY_LIST = [
        CONFIG_KEY_MAIL_TARGET_ADDRESS, CONFIG_KEY_MAIL_FROM_ADDRESS, CONFIG_KEY_MAIL_SUBJECT_PREFIX, KEY_LOG_PREFIX
    ]

    def print_response(self, value):
        """Add a value to the response string."""
        self.REMOTE_CONTROL_RESPONSE += str(value)

    def change_config_property(self, analysis_context, property_name, value):
        """Change a config_property in an running aminer instance."""
        result = 0
        config_keys_mail_alerting = [
            self.CONFIG_KEY_MAIL_TARGET_ADDRESS, self.CONFIG_KEY_MAIL_FROM_ADDRESS, self.CONFIG_KEY_MAIL_SUBJECT_PREFIX,
            self.CONFIG_KEY_EVENT_COLLECT_TIME, self.CONFIG_KEY_ALERT_MIN_GAP, self.CONFIG_KEY_ALERT_MAX_GAP,
            self.CONFIG_KEY_ALERT_MAX_EVENTS_PER_MESSAGE, self.CONFIG_KEY_MAIL_ALERT_GRACE_TIME]
        if not isinstance(analysis_context, AnalysisChild.AnalysisContext):
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the analysis_context must be of type %s." % AnalysisChild.AnalysisContext.__class__
            return

        if property_name not in self.INTEGER_CONFIG_PROPERTY_LIST + self.STRING_CONFIG_PROPERTY_LIST:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the property '%s' does not exist in the current config!" % property_name
            return

        if property_name in self.INTEGER_CONFIG_PROPERTY_LIST:
            t = int
        else:
            t = str
        if not isinstance(value, t):
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the value of the property '%s' must be of type %s!" % (property_name, t)
            return

        if property_name in [KEY_PERSISTENCE_DIR, KEY_LOG_SOURCES_LIST]:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: the property '%s' can only be changed at " \
                                            "startup in the aminer root process!" % property_name
            return
        if property_name == KEY_RESOURCES_MAX_MEMORY_USAGE:
            result = self.change_config_property_max_memory(analysis_context, value)
        elif property_name in config_keys_mail_alerting:
            result = self.change_config_property_mail_alerting(analysis_context, property_name, value)
        elif property_name in (KEY_LOG_PREFIX, KEY_PERSISTENCE_PERIOD, KEY_LOG_STAT_PERIOD):
            analysis_context.aminer_config.config_properties[property_name] = value
            result = 0
        elif property_name == KEY_LOG_STAT_LEVEL:
            result = self.change_config_property_log_stat_level(analysis_context, value)
        elif property_name == KEY_LOG_DEBUG_LEVEL:
            result = self.change_config_property_log_debug_level(analysis_context, value)
        else:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: property %s could not be changed. Please check the property_name " \
                                            "again." % property_name
            return
        if result == 0:
            msg = "'%s' changed to '%s' successfully." % (property_name, value)
            self.REMOTE_CONTROL_RESPONSE += msg
            logging.getLogger(DEBUG_LOG_NAME).info(msg)

    def change_config_property_mail_alerting(self, analysis_context, property_name, value):
        """Change any mail property."""
        is_email = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)|^[a-zA-Z0-9]+@localhost$")
        if property_name in self.MAIL_CONFIG_PROPERTIES and not is_email.match(value):
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: MailAlerting.TargetAddress and MailAlerting.FromAddress must be email addresses!"
            return 1
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
                self.REMOTE_CONTROL_RESPONSE += "FAILURE: it is not safe to run the aminer with less than 32MB RAM."
                return 1
            resource.setrlimit(resource.RLIMIT_AS, (max_memory_mb * 1024 * 1024, resource.RLIM_INFINITY))
            analysis_context.aminer_config.config_properties[KEY_RESOURCES_MAX_MEMORY_USAGE] = max_memory_mb
            return 0
        except ValueError:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: property 'maxMemoryUsage' must be of type Integer!"
            return 1

    def change_config_property_log_stat_level(self, analysis_context, stat_level):
        """Set the statistic logging level."""
        if stat_level in (0, 1, 2):
            analysis_context.aminer_config.config_properties[KEY_LOG_STAT_LEVEL] = stat_level
            AminerConfig.STAT_LEVEL = stat_level
            return 0
        self.REMOTE_CONTROL_RESPONSE += "FAILURE: STAT_LEVEL %d is not allowed. Allowed STAT_LEVEL values are 0, 1, 2." % stat_level
        return 1

    def change_config_property_log_debug_level(self, analysis_context, debug_level):
        """Set the debug log level."""
        if debug_level in (0, 1, 2):
            analysis_context.aminer_config.config_properties[KEY_LOG_DEBUG_LEVEL] = debug_level
            AminerConfig.DEBUG_LEVEL = debug_level
            debug_logger = logging.getLogger(DEBUG_LOG_NAME)
            if debug_level == 0:
                debug_logger.setLevel(logging.ERROR)
            elif debug_level == 1:
                debug_logger.setLevel(logging.INFO)
            else:
                debug_logger.setLevel(logging.DEBUG)
            return 0
        self.REMOTE_CONTROL_RESPONSE += "FAILURE: DEBUG_LEVEL %d is not allowed. Allowed DEBUG_LEVEL values are 0, 1, 2." % debug_level
        return 1

    def change_attribute_of_registered_analysis_component(self, analysis_context, component_name, attribute, value):
        """
        Change a specific attribute of a registered component.
        @param analysis_context the analysis context of the aminer.
        @param component_name the name to be registered in the analysis_context.
        @param attribute the name of the attribute to be printed.
        @param value the new value of the attribute.
        """
        attr = getattr(analysis_context.get_component_by_name(component_name), attribute)
        if type(attr) is type(value):
            setattr(analysis_context.get_component_by_name(component_name), attribute, value)
            msg = "'%s.%s' changed from %s to %s successfully." % (component_name, attribute, repr(attr), value)
            self.REMOTE_CONTROL_RESPONSE += msg
            logging.getLogger(DEBUG_LOG_NAME).info(msg)
        else:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: property '%s.%s' must be of type %s!" % (component_name, attribute, type(attr))

    def rename_registered_analysis_component(self, analysis_context, old_component_name, new_component_name):
        """
        Rename an analysis component by removing and readding it to the analysis_context.
        @param analysis_context the analysis context of the aminer.
        @param old_component_name the current name of the component.
        @param new_component_name the new name of the component.
        """
        if type(old_component_name) is not str or type(new_component_name) is not str:
            self.REMOTE_CONTROL_RESPONSE = "FAILURE: the parameters 'old_component_name' and 'new_component_name' must be of type str."
        else:
            component = analysis_context.get_component_by_name(old_component_name)
            if component is None:
                self.REMOTE_CONTROL_RESPONSE += "FAILURE: the component '%s' does not exist." % old_component_name
            else:
                analysis_context.registered_components_by_name[old_component_name] = None
                analysis_context.registered_components_by_name[new_component_name] = component
                msg = "Component '%s' renamed to '%s' successfully." % (old_component_name, new_component_name)
                self.REMOTE_CONTROL_RESPONSE += msg
                logging.getLogger(DEBUG_LOG_NAME).info(msg)

    def print_config_property(self, analysis_context, property_name):
        """
        Print a specific config property.
        @param analysis_context the analysis context of the aminer.
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
        @param analysis_context the analysis context of the aminer.
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
                for at in attr:
                    if hasattr(at, '__dict__') and self.isinstance_aminer_class(at):
                        new_attr = "\n[\n  " + at.__class__.__name__ + "  {\n" + self.get_all_vars(at, '  ') + "  }\n]"
                    else:
                        if isinstance(at, str):
                            new_attr = '"%s"' % at
                        else:
                            new_attr = str(at)
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
        Print the entire aminer config.
        @param analysis_context the analysis context of the aminer.
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
                for at in attr:
                    if hasattr(at, '__dict__') and self.isinstance_aminer_class(at):
                        result += indent + '"%s": {\n' % var + indent + '  "' + at.__class__.__name__ + \
                                  '": {\n' + self.get_all_vars(at, indent + '    ') + indent + '  ' + "}\n" + indent + '},\n'
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
        class_list = [
            aminer.analysis.AtomFilters.SubhandlerFilter, aminer.analysis.AtomFilters.MatchPathFilter,
            aminer.analysis.AtomFilters.MatchValueFilter, aminer.analysis.HistogramAnalysis.LinearNumericBinDefinition,
            aminer.analysis.HistogramAnalysis.BinDefinition, aminer.analysis.HistogramAnalysis.ModuloTimeBinDefinition,
            aminer.analysis.Rules.MatchAction, aminer.analysis.Rules.MatchRule, aminer.analysis.HistogramAnalysis.HistogramData,
            aminer.analysis.TimeCorrelationViolationDetector.CorrelationRule, aminer.analysis.TimeCorrelationDetector.CorrelationFeature,
            aminer.events.EventInterfaces.EventHandlerInterface, aminer.util.History.ObjectHistory]
        for c in class_list:
            if isinstance(obj, c):
                return True
        return False

    def save_current_config(self, analysis_context, destination_file):
        """
        Save the current live config into a file.
        @param analysis_context the analysis context of the aminer.
        @param destination_file the path to the file in which the config is saved.
        """
        msg = AminerConfig.save_config(analysis_context, destination_file)
        self.REMOTE_CONTROL_RESPONSE = msg
        logging.getLogger(DEBUG_LOG_NAME).info(msg)

    def persist_all(self):
        """Persist all data by calling the function in PersistenceUtil."""
        PersistenceUtil.persist_all()
        self.REMOTE_CONTROL_RESPONSE = 'OK'
        logging.getLogger(DEBUG_LOG_NAME).info('Called persist_all() via remote control.')

    def create_backup(self, analysis_context):
        """Create a backup with the current datetime string."""
        backup_time = time()
        backup_time_str = datetime.fromtimestamp(backup_time).strftime('%Y-%m-%d-%H-%M-%S')
        persistence_dir = analysis_context.aminer_config.config_properties[KEY_PERSISTENCE_DIR]
        persistence_dir = persistence_dir.rstrip('/')
        backup_path = persistence_dir + '/backup/'
        backup_path_with_date = os.path.join(backup_path, backup_time_str)
        shutil.copytree(persistence_dir, backup_path_with_date, ignore=shutil.ignore_patterns('backup*'))
        msg = 'Created backup %s' % backup_time_str
        self.REMOTE_CONTROL_RESPONSE = 'Created backup %s' % backup_time_str
        logging.getLogger(DEBUG_LOG_NAME).info(msg)

    def list_backups(self, analysis_context):
        """List all available backups from the persistence directory."""
        persistence_dir = analysis_context.aminer_config.config_properties.get(KEY_PERSISTENCE_DIR, DEFAULT_PERSISTENCE_DIR)
        for _dirpath, dirnames, _filenames in os.walk(os.path.join(persistence_dir, 'backup')):
            self.REMOTE_CONTROL_RESPONSE = '"backups": %s' % dirnames
            break
        self.REMOTE_CONTROL_RESPONSE = self.REMOTE_CONTROL_RESPONSE.replace("'", '"')

    def allowlist_event_in_component(self, analysis_context, component_name, event_data, allowlisting_data=None):
        """
        Allowlists one or multiple specific events from the history in the component it occurred in.
        @param analysis_context the analysis context of the aminer.
        @param component_name the name to be registered in the analysis_context.
        @param event_data the event_data for the allowlist_event method.
        @param allowlisting_data this data is passed on into the allowlist_event method.
        """
        component = analysis_context.get_component_by_name(component_name)
        if component is None:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: component '%s' does not exist!" % component
            return
        if component.__class__.__name__ not in [
                "EnhancedNewMatchPathValueComboDetector", "MissingMatchPathValueDetector", "NewMatchPathDetector",
                "NewMatchPathValueComboDetector", "NewMatchIdValueComboDetector", "EventCorrelationDetector",
                "NewMatchPathValueDetector"]:
            self.REMOTE_CONTROL_RESPONSE += \
                "FAILURE: component class '%s' does not support allowlisting! Only the following classes support allowlisting: " \
                "EnhancedNewMatchPathValueComboDetector, MissingMatchPathValueDetector, NewMatchPathDetector," \
                " NewMatchIdValueComboDetector, NewMatchPathValueComboDetector, NewMatchPathValueDetector and EventCorrelationDetector." \
                % component.__class__.__name__
            return
        try:
            msg = component.allowlist_event("Analysis.%s" % component.__class__.__name__, event_data, allowlisting_data)
            self.REMOTE_CONTROL_RESPONSE += msg
            logging.getLogger(DEBUG_LOG_NAME).info(msg)
        # skipcq: PYL-W0703
        except Exception as e:
            self.REMOTE_CONTROL_RESPONSE += "Exception: " + repr(e)

    def blocklist_event_in_component(self, analysis_context, component_name, event_data, blocklisting_data=None):
        """
        Blocklists one or multiple specific events from the history in the component it occurred in.
        @param analysis_context the analysis context of the aminer.
        @param component_name the name to be registered in the analysis_context.
        @param event_data the event_data for the allowlist_event method.
        @param blocklisting_data this data is passed on into the blocklist_event method.
        """
        component = analysis_context.get_component_by_name(component_name)
        if component is None:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: component '%s' does not exist!" % component
            return
        if component.__class__.__name__ not in ["EventCorrelationDetector"]:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: component class '%s' does not support blocklisting! Only the following classes " \
                                            "support blocklisting: EventCorrelationDetector." % component.__class__.__name__
            return
        try:
            msg = component.blocklist_event("Analysis.%s" % component.__class__.__name__, event_data, blocklisting_data)
            self.REMOTE_CONTROL_RESPONSE += msg
            logging.getLogger(DEBUG_LOG_NAME).info(msg)
        # skipcq: PYL-W0703
        except Exception as e:
            self.REMOTE_CONTROL_RESPONSE += "Exception: " + repr(e)

    def print_persistency_event_in_component(self, analysis_context, component_name, event_data):
        """
        Prints the persistency specified in event_data of component_name.
        @param analysis_context the analysis context of the aminer.
        @param component_name the name to be registered in the analysis_context.
        @param event_data the event_data for the print_persistency_event method.
        """
        component = analysis_context.get_component_by_name(component_name)
        if component is None:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: component '%s' does not exist!" % component
            return
        if component.__class__.__name__ not in ["EventFrequencyDetector", "MinimalTransitionTimeDetector",
                                                "PathValueTimeIntervalDetector"]:
            self.REMOTE_CONTROL_RESPONSE += \
                "FAILURE: component class '%s' does not support the print_persistency_event! Only the following classes support it: " \
                "EventFrequencyDetector, MinimalTransitionTimeDetector and PathValueTimeIntervalDetector." \
                % component.__class__.__name__
            return
        try:
            msg = component.print_persistence_event("Analysis.%s" % component.__class__.__name__, event_data)
            self.REMOTE_CONTROL_RESPONSE += msg
            logging.getLogger(DEBUG_LOG_NAME).info(msg)
        # skipcq: PYL-W0703
        except Exception as e:
            self.REMOTE_CONTROL_RESPONSE += "Exception: " + repr(e)

    def add_to_persistency_event_in_component(self, analysis_context, component_name, event_data):
        """
        Add information specified in event_data to the persistency of component_name.
        @param analysis_context the analysis context of the aminer.
        @param component_name the name to be registered in the analysis_context.
        @param event_data the event_data for the add_to_persistency_event method.
        """
        component = analysis_context.get_component_by_name(component_name)
        if component is None:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: component '%s' does not exist!" % component
            return
        if component.__class__.__name__ not in ["NewMatchPathValueComboDetector", "MinimalTransitionTimeDetector",
                                                "PathValueTimeIntervalDetector"]:
            self.REMOTE_CONTROL_RESPONSE += \
                "FAILURE: component class '%s' does not support the add_to_persistency_event! Only the following classes support it: " \
                "NewMatchPathValueComboDetector, MinimalTransitionTimeDetector and PathValueTimeIntervalDetector." \
                % component.__class__.__name__
            return
        try:
            msg = component.add_to_persistence_event("Analysis.%s" % component.__class__.__name__, event_data)
            self.REMOTE_CONTROL_RESPONSE += msg
            logging.getLogger(DEBUG_LOG_NAME).info(msg)
        # skipcq: PYL-W0703
        except Exception as e:
            self.REMOTE_CONTROL_RESPONSE += "Exception: " + repr(e)

    def remove_from_persistency_event_in_component(self, analysis_context, component_name, event_data):
        """
        Remove information specified in event_data from the persistency of component_name.
        @param analysis_context the analysis context of the aminer.
        @param component_name the name to be registered in the analysis_context.
        @param event_data the event_data for the remove_from_persistency_event method.
        """
        component = analysis_context.get_component_by_name(component_name)
        if component is None:
            self.REMOTE_CONTROL_RESPONSE += "FAILURE: component '%s' does not exist!" % component
            return
        if component.__class__.__name__ not in ["MinimalTransitionTimeDetector", "PathValueTimeIntervalDetector"]:
            self.REMOTE_CONTROL_RESPONSE += \
                "FAILURE: component class '%s' does not support the remove_from_persistency_event! Only the following classes support it: "\
                "MinimalTransitionTimeDetector and PathValueTimeIntervalDetector." \
                % component.__class__.__name__
            return
        try:
            msg = component.remove_from_persistence_event("Analysis.%s" % component.__class__.__name__, event_data)
            self.REMOTE_CONTROL_RESPONSE += msg
            logging.getLogger(DEBUG_LOG_NAME).info(msg)
        # skipcq: PYL-W0703
        except Exception as e:
            self.REMOTE_CONTROL_RESPONSE += "Exception: " + repr(e)

    def add_handler_to_atom_filter_and_register_analysis_component(self, analysis_context, atom_handler, component, component_name):
        """
        Add a new component to the analysis_context.
        @param analysis_context the analysis context of the aminer.
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
        msg = "Component '%s' added to '%s' successfully." % (component_name, atom_handler)
        self.REMOTE_CONTROL_RESPONSE += msg
        logging.getLogger(DEBUG_LOG_NAME).info(msg)

    def dump_events_from_history(self, analysis_context, history_component_name, dump_event_id):
        """
        Detailed print of a specific event from the history.
        @param analysis_context the analysis context of the aminer.
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
            logging.getLogger(DEBUG_LOG_NAME).info(result_string)

    def ignore_events_from_history(self, analysis_context, history_component_name, event_ids):
        """
        Ignore one or multiple specific events from the history. These ignores do not affect the components itself.
        @param analysis_context the analysis context of the aminer.
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
        msg = 'OK\n%d elements ignored' % delete_count
        self.REMOTE_CONTROL_RESPONSE = msg
        logging.getLogger(DEBUG_LOG_NAME).info(msg)

    def list_events_from_history(self, analysis_context, history_component_name, max_event_count=None):
        """
        List the latest events of a specific history component.
        @param analysis_context the analysis context of the aminer.
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
        @param analysis_context the analysis context of the aminer.
        @param history_component_name the registered name of the history component.
        @param id_spec_list a list of numeric ids of the events to be allowlisted.
        @param allowlisting_data this data is passed on into the allowlist_event method.
        """
        from aminer.events.EventInterfaces import EventSourceInterface
        history_handler = analysis_context.get_component_by_name(history_component_name)
        if history_handler is None:
            self.REMOTE_CONTROL_RESPONSE = component_not_found
            return
        if id_spec_list is None or not isinstance(id_spec_list, list):
            self.REMOTE_CONTROL_RESPONSE = \
                'Request requires remote_control_data with ID specification list and optional allowlisting information.'
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
                    logging.getLogger(DEBUG_LOG_NAME).info(result_string)
                    allowlisted_flag = True
                except NotImplementedError:
                    result_string += 'FAIL %d: component does not support allowlisting.' % event_id
                # skipcq: PYL-W0703
                except Exception as wl_exception:
                    result_string += 'FAIL %d: %s\n' % (event_id, str(wl_exception))
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

    def reopen_event_handler_streams(self, analysis_context):
        """Reopen all StreamPrinterEventHandler streams for log rotation."""
        analysis_context.close_event_handler_streams(reopen=True)
        msg = "Reopened all StreamPrinterEventHandler streams."
        self.REMOTE_CONTROL_RESPONSE = msg
        logging.getLogger(DEBUG_LOG_NAME).info(msg)


def _repr_recursive(attr):
    """
    Return a valid JSON representation of an config attribute with the types list, dict, set or tuple.
    @param attr the attribute to be represented.
    """
    if attr is None:
        return None
    if isinstance(attr, (bool, type(AminerConfig))):
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
            value = _repr_recursive(key)
            if isinstance(value, str):
                value = value.replace('\\"', "'")
            new_attr[str(key)] = value
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
    if type(attr) in (int, str, float, bool, type(AminerConfig), type(None)):
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
    if not isinstance(attr, (list, dict, tuple, set)) and not rep.startswith('"') and not rep.isdecimal():
        try:
            float(rep)
        except:  # skipcq: FLK-E722
            rep = '"%s"' % rep
    return rep
