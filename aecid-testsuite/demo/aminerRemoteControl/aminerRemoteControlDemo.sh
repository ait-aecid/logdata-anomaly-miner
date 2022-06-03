#removes the 'LogPrefix'
sudo aminerremotecontrol --exec "change_config_property(analysis_context, 'LogPrefix', '')"

#renames the 'NewMatchPathValueCombo' component to 'NewMatchPathValueComboDetector'
sudo aminerremotecontrol --exec "rename_registered_analysis_component(analysis_context,'NewMatchPathValueCombo','NewMatchPathValueComboDetector')"

#changes the 'learn_mode' of the 'NewMatchPathValueComboDetector' to False.
sudo aminerremotecontrol --exec "change_attribute_of_registered_analysis_component(analysis_context, 'NewMatchPathValueComboDetector',  'learn_mode', False)"

#prints the current list of paths
sudo aminerremotecontrol --exec "print_attribute_of_registered_analysis_component(analysis_context, 'NewMatchPathValueComboDetector',  'target_path_list')"

#adds a new path to the 'NewMatchPathValueComboDetector' component.
sudo aminerremotecontrol --exec "change_attribute_of_registered_analysis_component(analysis_context, 'NewMatchPathValueComboDetector',  'target_path_list', ['/model/IPAddresses/Username', '/model/IPAddresses/IP', 'new/path'])"

#changes the 'learn_mode' of the 'NewMatchPathValueComboDetector' to True to start the learning phase.
sudo aminerremotecontrol --exec "change_attribute_of_registered_analysis_component(analysis_context, 'NewMatchPathValueComboDetector',  'learn_mode', True)"
sleep 1

#changes the 'learn_mode' of the 'NewMatchPathValueComboDetector' to False to end the learning phase.
sudo aminerremotecontrol --exec "change_attribute_of_registered_analysis_component(analysis_context, 'NewMatchPathValueComboDetector',  'learn_mode', False)"

#prints the 'Resources.MaxMemoryUsage'; changes the property 'Resources.MaxMemoryUsage' to -1, which means all the available memory can be used and prints it again.
sudo aminerremotecontrol --data '["Resources.MaxMemoryUsage", -1]' --exec 'print_config_property(analysis_context,  "%s" % remote_control_data[0])' --exec 'change_config_property(analysis_context, "%s" % remote_control_data[0], remote_control_data[1])' --exec 'print_config_property(analysis_context, "%s" % remote_control_data[0])'

#add a new NewMatchPathDetector to the config.
sudo aminerremotecontrol --exec "add_handler_to_atom_filter_and_register_analysis_component(analysis_context, 'AtomFilter', NewMatchPathDetector(analysis_context.aminer_config, analysis_context.atomizer_factory.atom_handler_list, learn_mode=True), 'NewMatchPathDet')"

sudo aminerremotecontrol --exec "add_handler_to_atom_filter_and_register_analysis_component(analysis_context, 'AtomFilter', NewMatchPathDetector(analysis_context.aminer_config, analysis_context.atomizer_factory.atom_handler_list, learn_mode=True), 'NewMatchPathDet1')"

#prints the current config to the console.
#sudo aminerremotecontrol --exec "print_current_config(analysis_context)" --string-response

#saves the current config to /tmp/config.py
sudo aminerremotecontrol --exec "save_current_config(analysis_context,'/tmp/config.py')"

#lists all the events from the VolatileLogarithmicBackoffEventHistory component, but the maximal count is 10.
sudo aminerremotecontrol --exec "list_events_from_history(analysis_context,'VolatileLogarithmicBackoffEventHistory',10)" --string-response

#prints the event with the id 12 from the history.
sudo aminerremotecontrol --exec "dump_events_from_history(analysis_context,'VolatileLogarithmicBackoffEventHistory',12)" --string-response

#prints the event with the id 13 from the history.
sudo aminerremotecontrol --exec "dump_events_from_history(analysis_context,'VolatileLogarithmicBackoffEventHistory',13)" --string-response

#prints the event with the id 15 from the history.
sudo aminerremotecontrol --exec "dump_events_from_history(analysis_context,'VolatileLogarithmicBackoffEventHistory',15)" --string-response

#ignores the events with the ids 12,13 and 15 from the history.
sudo aminerremotecontrol --exec "ignore_events_from_history(analysis_context,'VolatileLogarithmicBackoffEventHistory',[12,13,15])" --string-response

#allowlists the events with the ids 21,22 and 23 from the history.
sudo aminerremotecontrol --exec "allowlist_events_from_history(analysis_context,'VolatileLogarithmicBackoffEventHistory',[21,22,23])" --string-response

# Currently following rules must be met to not create a allowlistViolation:
# User root (logged in, logged out) or User 'username' (logged in, logged out) x minutes ago.
# allowlist_rules = [Rules.OrMatchRule([Rules.AndMatchRule([Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes'), Rules.NegationMatchRule(Rules.ValueMatchRule('/model/LoginDetails/Username', b'root'))]), Rules.AndMatchRule([Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes')),Rules.PathExistsMatchRule('/model/LoginDetails')]),Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/LoginDetails'))])]

# In the first step we print the current allowlist_rules. Maybe it is necessary to enlarge AnalysisChildRemoteControlHandler.maxControlPacketSize.
#sudo aminerremotecontrol --exec "print_attribute_of_registered_analysis_component(analysis_context,'Allowlist','allowlist_rules')" --string-response

# In the second step we add the user admin to not be tracked like the root user by adding another rule.
sudo aminerremotecontrol --exec "change_attribute_of_registered_analysis_component(analysis_context,'Allowlist','allowlist_rules',[Rules.OrMatchRule([Rules.AndMatchRule([Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes'), Rules.NegationMatchRule(Rules.ValueMatchRule('/model/LoginDetails/Username', b'root'))]), Rules.AndMatchRule([Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes'), Rules.NegationMatchRule(Rules.ValueMatchRule('/model/LoginDetails/Username', b'admin'))]),Rules.AndMatchRule([Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes')),Rules.PathExistsMatchRule('/model/LoginDetails')]),Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/LoginDetails'))])])"

# In the third step we rename the user admin to the user administrator and leave all other rules.
sudo aminerremotecontrol --exec "change_attribute_of_registered_analysis_component(analysis_context,'Allowlist','allowlist_rules',[Rules.OrMatchRule([Rules.AndMatchRule([Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes'), Rules.NegationMatchRule(Rules.ValueMatchRule('/model/LoginDetails/Username', b'root'))]), Rules.AndMatchRule([Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes'), Rules.NegationMatchRule(Rules.ValueMatchRule('/model/LoginDetails/Username', b'administrator'))]),Rules.AndMatchRule([Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes')),Rules.PathExistsMatchRule('/model/LoginDetails')]),Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/LoginDetails'))])])"

# In the last step we remove all special rules and only allow User 'username' (logged in, logged out) x minutes ago.
sudo aminerremotecontrol --exec "change_attribute_of_registered_analysis_component(analysis_context,'Allowlist','allowlist_rules',[Rules.OrMatchRule([Rules.AndMatchRule([Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes')),Rules.PathExistsMatchRule('/model/LoginDetails')]),Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/LoginDetails'))])])"

# Adds a new path to the known_path_set
sudo aminerremotecontrol --exec "allowlist_event_in_component(analysis_context,'NewMatchPathDet',['/new/path1','/new/path2'])" --string-response

# Persist all data.
sudo aminerremotecontrol --exec "persist_all()"

# List all backups.
sudo aminerremotecontrol --exec "list_backups(analysis_context)"

# Create a backup.
sudo aminerremotecontrol --exec "create_backup(analysis_context)"

# suspend the aminer.
sudo aminerremotecontrol --exec "suspend"

# activate the aminer.
sudo aminerremotecontrol --exec "activate"

# reopen all StreamPrinterEventHandler streams.
sudo aminerremotecontrol --exec "reopen_event_handler_streams(analysis_context)"