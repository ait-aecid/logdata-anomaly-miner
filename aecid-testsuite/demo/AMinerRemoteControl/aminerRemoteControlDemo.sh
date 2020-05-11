#removes the 'LogPrefix'
sudo AMinerRemoteControl --Exec "changeConfigProperty(analysisContext, 'LogPrefix', '')"

#renames the 'NewMatchPathValueCombo' component to 'NewMatchPathValueComboDetector'
sudo AMinerRemoteControl --Exec "renameRegisteredAnalysisComponent(analysisContext,'NewMatchPathValueCombo','NewMatchPathValueComboDetector')"

#changes the 'autoIncludeFlag' of the 'NewMatchPathValueComboDetector' to False.
sudo AMinerRemoteControl --Exec "changeAttributeOfRegisteredAnalysisComponent(analysisContext, 'NewMatchPathValueComboDetector',  'auto_include_flag', False)"

#prints the current list of paths
sudo AMinerRemoteControl --Exec "printAttributeOfRegisteredAnalysisComponent(analysisContext, 'NewMatchPathValueComboDetector',  'target_path_list')"

#adds a new path to the 'NewMatchPathValueComboDetector' component.
sudo AMinerRemoteControl --Exec "changeAttributeOfRegisteredAnalysisComponent(analysisContext, 'NewMatchPathValueComboDetector',  'target_path_list', ['/model/IPAddresses/Username', '/model/IPAddresses/IP', 'new/path'])"

#changes the 'auto_include_flag' of the 'NewMatchPathValueComboDetector' to True to start the learning phase.
sudo AMinerRemoteControl --Exec "changeAttributeOfRegisteredAnalysisComponent(analysisContext, 'NewMatchPathValueComboDetector',  'auto_include_flag', True)"
sleep 1

#changes the 'auto_include_flag' of the 'NewMatchPathValueComboDetector' to False to end the learning phase.
sudo AMinerRemoteControl --Exec "changeAttributeOfRegisteredAnalysisComponent(analysisContext, 'NewMatchPathValueComboDetector',  'auto_include_flag', False)"

#prints the 'Resources.MaxMemoryUsage'; changes the property 'Resources.MaxMemoryUsage' to -1, which means all the available memory can be used and prints it again.
sudo AMinerRemoteControl --Data '["Resources.MaxMemoryUsage", -1]' --Exec 'printConfigProperty(analysisContext,  "%s" % remoteControlData[0])' --Exec 'changeConfigProperty(analysisContext, "%s" % remoteControlData[0], remoteControlData[1])' --Exec 'printConfigProperty(analysisContext, "%s" % remoteControlData[0])'

#add a new NewMatchPathDetector to the config.
sudo AMinerRemoteControl --Exec "addHandlerToAtomFilterAndRegisterAnalysisComponent(analysisContext, 'AtomFilter', NewMatchPathDetector(analysisContext.aminer_config, analysisContext.atomizer_factory.atom_handler_list, auto_include_flag=True), 'NewMatchPathDet')"

sudo AMinerRemoteControl --Exec "addHandlerToAtomFilterAndRegisterAnalysisComponent(analysisContext, 'AtomFilter', NewMatchPathDetector(analysisContext.aminer_config, analysisContext.atomizer_factory.atom_handler_list, auto_include_flag=True), 'NewMatchPathDet1')"

#prints the current config to the console.
#sudo AMinerRemoteControl --Exec "printCurrentConfig(analysisContext)" --StringResponse

#saves the current config to /tmp/config.py
sudo AMinerRemoteControl --Exec "saveCurrentConfig(analysisContext,'/tmp/config.py')"

#lists all the events from the VolatileLogarithmicBackoffEventHistory component, but the maximal count is 10.
sudo AMinerRemoteControl --Exec "listEventsFromHistory(analysisContext,'VolatileLogarithmicBackoffEventHistory',10)" --StringResponse

#prints the event with the id 12 from the history.
sudo AMinerRemoteControl --Exec "dumpEventsFromHistory(analysisContext,'VolatileLogarithmicBackoffEventHistory',12)" --StringResponse

#prints the event with the id 13 from the history.
sudo AMinerRemoteControl --Exec "dumpEventsFromHistory(analysisContext,'VolatileLogarithmicBackoffEventHistory',13)" --StringResponse

#prints the event with the id 15 from the history.
sudo AMinerRemoteControl --Exec "dumpEventsFromHistory(analysisContext,'VolatileLogarithmicBackoffEventHistory',15)" --StringResponse

#ignores the events with the ids 12,13 and 15 from the history.
sudo AMinerRemoteControl --Exec "ignoreEventsFromHistory(analysisContext,'VolatileLogarithmicBackoffEventHistory',[12,13,15])" --StringResponse

#whitelists the events with the ids 21,22 and 23 from the history.
sudo AMinerRemoteControl --Exec "whitelistEventsFromHistory(analysisContext,'VolatileLogarithmicBackoffEventHistory',[21,22,23])" --StringResponse

# Currently following rules must be met to not create a whitelistViolation:
# User root (logged in, logged out) or User 'username' (logged in, logged out) x minutes ago.
# whitelistRules = [Rules.OrMatchRule([Rules.AndMatchRule([Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes'), Rules.NegationMatchRule(Rules.ValueMatchRule('/model/LoginDetails/Username', b'root'))]), Rules.AndMatchRule([Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes')),Rules.PathExistsMatchRule('/model/LoginDetails')]),Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/LoginDetails'))])]

# In the first step we print the current whitelistRules. Maybe it is necessary to enlarge AnalysisChildRemoteControlHandler.maxControlPacketSize.
#sudo AMinerRemoteControl --Exec "printAttributeOfRegisteredAnalysisComponent(analysisContext,'Whitelist','whitelistRules')" --StringResponse

# In the second step we add the user admin to not be tracked like the root user by adding another rule.
sudo AMinerRemoteControl --Exec "changeAttributeOfRegisteredAnalysisComponent(analysisContext,'Whitelist','whitelist_rules',[Rules.OrMatchRule([Rules.AndMatchRule([Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes'), Rules.NegationMatchRule(Rules.ValueMatchRule('/model/LoginDetails/Username', b'root'))]), Rules.AndMatchRule([Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes'), Rules.NegationMatchRule(Rules.ValueMatchRule('/model/LoginDetails/Username', b'admin'))]),Rules.AndMatchRule([Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes')),Rules.PathExistsMatchRule('/model/LoginDetails')]),Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/LoginDetails'))])])"

# In the third step we rename the user admin to the user administrator and leave all other rules.
sudo AMinerRemoteControl --Exec "changeAttributeOfRegisteredAnalysisComponent(analysisContext,'Whitelist','whitelist_rules',[Rules.OrMatchRule([Rules.AndMatchRule([Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes'), Rules.NegationMatchRule(Rules.ValueMatchRule('/model/LoginDetails/Username', b'root'))]), Rules.AndMatchRule([Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes'), Rules.NegationMatchRule(Rules.ValueMatchRule('/model/LoginDetails/Username', b'administrator'))]),Rules.AndMatchRule([Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes')),Rules.PathExistsMatchRule('/model/LoginDetails')]),Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/LoginDetails'))])])"

# In the last step we remove all special rules and only allow User 'username' (logged in, logged out) x minutes ago.
sudo AMinerRemoteControl --Exec "changeAttributeOfRegisteredAnalysisComponent(analysisContext,'Whitelist','whitelist_rules',[Rules.OrMatchRule([Rules.AndMatchRule([Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/LoginDetails/PastTime/Time/Minutes')),Rules.PathExistsMatchRule('/model/LoginDetails')]),Rules.NegationMatchRule(Rules.PathExistsMatchRule('/model/LoginDetails'))])])"

