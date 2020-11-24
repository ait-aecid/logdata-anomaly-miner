FILE=demo/AMinerRemoteControl/demo-config.py
sudo bash -c 'aminer --Config '$FILE' &' > /dev/null

PREFIX="Remote execution response: "
NOT_FOUND_WARNINGS="WARNING: config_properties['Core.PersistencePeriod'] = not found in the old config file.\nWARNING: config_properties['Log.StatisticsLevel'] = not found in the old config file.\nWARNING: config_properties['Log.DebugLevel'] = not found in the old config file.\nWARNING: config_properties['Log.StatisticsPeriod'] = not found in the old config file.\n"
ERROR="Error at:"
exit_code=0

# check if proper mail address validation is done.
properties=("'MailAlerting.TargetAddress'" "'MailAlerting.FromAddress'")
# only test 'MailAlerting.TargetAddress' to reduce runtime and expect 'MailAlerting.FromAddress' to work the same way.
properties=("'MailAlerting.TargetAddress'")
valid_addresses=("'test123@gmail.com'" "'root@localhost'" )
error_addresses=("'domain.user1@localhost'" "'root@notLocalhost'")
for property in "${properties[@]}"; do
  for address in "${valid_addresses[@]}"; do
    stdout=$(sudo aminerremotecontrol --Exec "change_config_property(analysis_context, $property, $address)")
    if [[ "$stdout" != "$PREFIX\"$property changed to $address successfully.\"" ]]; then
	    echo "$ERROR changing $property to $address."
	    echo "$stdout"
	    echo
	    exit_code=1
    fi
  done
  for address in "${error_addresses[@]}"; do
    stdout=$(sudo aminerremotecontrol --Exec "change_config_property(analysis_context, $property, $address)")
    if [[ "$stdout" != "$PREFIX'FAILURE: MailAlerting.TargetAddress and MailAlerting.FromAddress must be email addresses!'" ]]; then
	    echo "$ERROR changing $property to $address."
	    echo "$stdout"
	    echo
	    exit_code=1
    fi
  done
done

INTEGER_CONFIG_PROPERTIES=("'MailAlerting.AlertGraceTime'" "'MailAlerting.EventCollectTime'" "'MailAlerting.MinAlertGap'" "'MailAlerting.MaxAlertGap'" "'MailAlerting.MaxEventsPerMessage'" "'Core.PersistencePeriod'" "'Log.StatisticsLevel'" "'Log.DebugLevel'" "'Log.StatisticsPeriod'" "'Resources.MaxMemoryUsage'")
STRING_CONFIG_PROPERTIES=("'MailAlerting.TargetAddress'" "'MailAlerting.FromAddress'" "'MailAlerting.SubjectPrefix'" "'LogPrefix'")

for property in "${STRING_CONFIG_PROPERTIES[@]}"; do
  stdout=$(sudo aminerremotecontrol --Exec "change_config_property(analysis_context, $property, 123)")
  if [[ "$stdout" != "$PREFIX\"FAILURE: the value of the property $property must be of type <class 'str'>!\"" ]]; then
	  echo "$ERROR changing $property wrong Type."
	  echo "$stdout"
	  echo
	  exit_code=1
  fi
  stdout=$(sudo aminerremotecontrol --Exec "change_config_property(analysis_context, $property, 'root@localhost')")
  if [[ "$stdout" != "$PREFIX\"$property changed to 'root@localhost' successfully.\"" ]]; then
	    echo "$ERROR changing $property to 'root@localhost'."
	    echo "$stdout"
	    echo
	    exit_code=1
  fi
done

for property in "${INTEGER_CONFIG_PROPERTIES[@]}"; do
  stdout=$(sudo aminerremotecontrol --Exec "change_config_property(analysis_context, $property, '1')")
  if [[ "$stdout" != "$PREFIX\"FAILURE: the value of the property $property must be of type <class 'int'>!\"" && "$stdout" != "$PREFIX'FAILURE: it is not safe to run the AMiner with less than 32MB RAM.'" ]]; then
	  echo "$ERROR changing $property wrong Type."
	  echo "$stdout"
	  echo
	  exit_code=1
  fi
  stdout=$(sudo aminerremotecontrol --Exec "change_config_property(analysis_context, $property, 1)")
  if [[ "$stdout" != "$PREFIX\"$property changed to '1' successfully.\"" && "$stdout" != "$PREFIX'FAILURE: it is not safe to run the AMiner with less than 32MB RAM.'" ]]; then
	    echo "$ERROR changing $property to 1."
	    echo "$stdout"
	    echo
	    exit_code=1
  fi
done

stdout=$(sudo aminerremotecontrol --Exec "rename_registered_analysis_component(analysis_context,'NewMatchPathValueCombo','NewMatchPathValueComboDetector')")
if [[ "$stdout" != "$PREFIX\"Component 'NewMatchPathValueCombo' renamed to 'NewMatchPathValueComboDetector' successfully.\"" ]]; then
	echo "$ERROR renames the 'NewMatchPathValueCombo' component to 'NewMatchPathValueComboDetector'."
	echo "$stdout"
	echo
	exit_code=1
fi

stdout=$(sudo aminerremotecontrol --Exec "rename_registered_analysis_component(analysis_context,'NewMatchPathValueComboDetector', 222)")
if [[ "$stdout" != "$PREFIX\"FAILURE: the parameters 'old_component_name' and 'new_component_name' must be of type str.\"" ]]; then
	echo "$ERROR renames the 'NewMatchPathValueComboDetector' wrong Type. (no string; integer value)"
	echo "$stdout"
	echo
	exit_code=1
fi

stdout=$(sudo aminerremotecontrol --Exec "rename_registered_analysis_component(analysis_context,'NonExistingDetector','NewMatchPathValueComboDetector')")
if [[ "$stdout" != "$PREFIX\"FAILURE: the component 'NonExistingDetector' does not exist.\"" ]]; then
	echo "$ERROR renames a non existing component to 'NewMatchPathValueComboDetector'."
	echo "$stdout"
	echo
	exit_code=1
fi

stdout=$(sudo aminerremotecontrol --Exec "change_attribute_of_registered_analysis_component(analysis_context, 'NewMatchPathValueComboDetector',  'auto_include_flag', False)")
if [[ "$stdout" != "$PREFIX\"'NewMatchPathValueComboDetector.auto_include_flag' changed from False to False successfully.\"" ]]; then
	echo "$ERROR changes the 'auto_include_flag' of the 'NewMatchPathValueComboDetector' to False."
	echo "$stdout"
	echo
	exit_code=1
fi

stdout=$(sudo aminerremotecontrol --Exec "change_attribute_of_registered_analysis_component(analysis_context, 'NewMatchPathValueComboDetector',  'auto_include_flag', 'True')")
if [[ "$stdout" != "$PREFIX\"FAILURE: property 'NewMatchPathValueComboDetector.auto_include_flag' must be of type <class 'bool'>!\"" ]]; then
	echo "$ERROR changes the 'auto_include_flag' of the 'NewMatchPathValueComboDetector' wrong Type."
	echo "$stdout"
	echo
	exit_code=1
fi

stdout=$(sudo aminerremotecontrol --Exec "print_attribute_of_registered_analysis_component(analysis_context, 'NewMatchPathValueComboDetector',  'target_path_list')")
if [[ "$stdout" != "$PREFIX'\"NewMatchPathValueComboDetector.target_path_list\": [\"/model/IPAddresses/Username\", \"/model/IPAddresses/IP\"]'" ]]; then
	echo "$ERROR prints the current list of paths."
	echo "$stdout"
	echo
	exit_code=1
fi

stdout=$(sudo aminerremotecontrol --Exec "print_attribute_of_registered_analysis_component(analysis_context, 'NewMatchPathValueComboDetector',  'other_path_list')")
if [[ "$stdout" != "$PREFIX\"FAILURE: the component 'NewMatchPathValueComboDetector' does not have an attribute named 'other_path_list'.\"" ]]; then
	echo "$ERROR prints not existing attribute."
	echo "$stdout"
	echo
	exit_code=1
fi

stdout=$(sudo aminerremotecontrol --Exec "add_handler_to_atom_filter_and_register_analysis_component(analysis_context, 'AtomFilter', NewMatchPathDetector(analysis_context.aminer_config, analysis_context.atomizer_factory.atom_handler_list, auto_include_flag=True), 'NewMatchPathDet')")
if [[ "$stdout" != "$PREFIX\"Component 'NewMatchPathDet' added to 'AtomFilter' successfully.\"" ]]; then
	echo "$ERROR add a new NewMatchPathDetector to the config."
	echo "$stdout"
	echo
	exit_code=1
fi

stdout=$(sudo aminerremotecontrol --Exec "add_handler_to_atom_filter_and_register_analysis_component(analysis_context, 'AtomFilter', 'StringDetector', 'StringDetector')")
if [[ "$stdout" != "$PREFIX\"FAILURE: 'component' must implement the AtomHandlerInterface!\"" ]]; then
	echo "$ERROR add a wrong class to the config."
	echo "$stdout"
	echo
	exit_code=1
fi

stdout=$(sudo aminerremotecontrol --Exec "save_current_config(analysis_context,'/tmp/config.py')")
if [[ "$stdout" != "${PREFIX}\"${NOT_FOUND_WARNINGS}Successfully saved the current config to /tmp/config.py.\"" ]]; then
	echo "$ERROR save the current config to /tmp/config.py."
	echo "$stdout"
	echo
	exit_code=1
fi
sudo rm /tmp/config.py

stdout=$(sudo aminerremotecontrol --Exec "save_current_config(analysis_context,'[dd/path/config.py')")
if [[ "$stdout" != "${PREFIX}\"${NOT_FOUND_WARNINGS}FAILURE: file '[dd/path/config.py' could not be found or opened!\"" ]]; then
	echo "$ERROR save the current config to an invalid path."
	echo "$stdout"
	echo
	exit_code=1
fi

stdout=$(sudo aminerremotecontrol --Exec "save_current_config(analysis_context,'/notExistingPath/config.py')")
if [[ "$stdout" != "${PREFIX}\"${NOT_FOUND_WARNINGS}FAILURE: file '/notExistingPath/config.py' could not be found or opened!\"" ]]; then
	echo "$ERROR save the current config to an not existing directory path."
	echo "$stdout"
	echo
	exit_code=1
fi

sudo pkill -x aminer
sleep 2 & wait $!

exit $exit_code
