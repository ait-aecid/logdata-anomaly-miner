sudo mkdir /tmp/lib 2> /dev/null
sudo mkdir /tmp/lib/aminer 2> /dev/null
sudo rm -r /tmp/lib/aminer/* 2> /dev/null
sudo chown -R aminer:aminer /tmp/lib 2> /dev/null
sudo rm /tmp/syslog 2> /dev/null

FILE=demo/AMinerRemoteControl/demo-config.py
sudo bash -c 'aminer --Config '$FILE' &' > /dev/null

PREFIX="Remote execution response: "
NOT_FOUND_WARNINGS="WARNING: config_properties['Core.PersistencePeriod'] = not found in the old config file.\nWARNING: config_properties['Log.StatisticsLevel'] = not found in the old config file.\nWARNING: config_properties['Log.DebugLevel'] = not found in the old config file.\nWARNING: config_properties['Log.StatisticsPeriod'] = not found in the old config file.\n"
ERROR="Error at:"
exit_code=0

stdout=$(sudo aminerremotecontrol --Exec "print_config_property(analysis_context, 'Core.PersistenceDir')")
if [[ "$stdout" != "$PREFIX'\"Core.PersistenceDir\": /tmp/lib/aminer'" ]]; then
	echo "$ERROR error printing 'Core.PersistenceDir'."
	echo "$stdout"
	echo
	exit_code=1
fi

stdout=$(sudo aminerremotecontrol --Exec "print_config_property(analysis_context, 'Core.PersistencePeriod')")
if [[ "$stdout" != "$PREFIX'\"Resource \\\\\"Core.PersistencePeriod\\\\\" could not be found.\"'" ]]; then
	echo "$ERROR error printing 'Core.PersistencePeriod'."
	echo "$stdout"
	echo
	exit_code=1
fi

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

properties=("'Log.StatisticsLevel'" "'Log.DebugLevel'")
for property in "${properties[@]}"; do
  value=0
  stdout=$(sudo aminerremotecontrol --Exec "change_config_property(analysis_context, $property, $value)")
  if [[ "$stdout" != "$PREFIX\"$property changed to '$value' successfully.\"" ]]; then
      echo "$ERROR changing $property to $value."
      echo "$stdout"
      echo
      exit_code=1
  fi
  value=1
  stdout=$(sudo aminerremotecontrol --Exec "change_config_property(analysis_context, $property, $value)")
  if [[ "$stdout" != "$PREFIX\"$property changed to '$value' successfully.\"" ]]; then
      echo "$ERROR changing $property to $value."
      echo "$stdout"
      echo
      exit_code=1
  fi
  value=2
  stdout=$(sudo aminerremotecontrol --Exec "change_config_property(analysis_context, $property, $value)")
  if [[ "$stdout" != "$PREFIX\"$property changed to '$value' successfully.\"" ]]; then
      echo "$ERROR changing $property to $value."
      echo "$stdout"
      echo
      exit_code=1
  fi
  value=-1
  stdout=$(sudo aminerremotecontrol --Exec "change_config_property(analysis_context, $property, $value)")
  if [[ "$stdout" != "$PREFIX'FAILURE: STAT_LEVEL $value is not allowed. Allowed STAT_LEVEL values are 0, 1, 2.'" && "$stdout" != "$PREFIX'FAILURE: DEBUG_LEVEL $value is not allowed. Allowed DEBUG_LEVEL values are 0, 1, 2.'" ]]; then
      echo "$ERROR changing $property to $value."
      echo "$stdout"
      echo
      exit_code=1
  fi
  value=3
  stdout=$(sudo aminerremotecontrol --Exec "change_config_property(analysis_context, $property, $value)")
  if [[ "$stdout" != "$PREFIX'FAILURE: STAT_LEVEL $value is not allowed. Allowed STAT_LEVEL values are 0, 1, 2.'" && "$stdout" != "$PREFIX'FAILURE: DEBUG_LEVEL $value is not allowed. Allowed DEBUG_LEVEL values are 0, 1, 2.'" ]]; then
      echo "$ERROR changing $property to $value."
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

stdout=$(sudo aminerremotecontrol --Exec "print_current_config(analysis_context)")
if [[ "$stdout" == "$PREFIX None" ]]; then
	echo "$ERROR print config had an execution error."
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

stdout=$(sudo aminerremotecontrol --Exec "persist_all()")
if [[ "$stdout" != "${PREFIX}'OK'" ]]; then
	echo "$ERROR persist_all."
	echo "$stdout"
	echo
	exit_code=1
fi

stdout=$(sudo aminerremotecontrol --Exec "create_backup(analysis_context)")
if [[ "$stdout" != "${PREFIX}'Created backup "* ]]; then
	echo "$ERROR creating backup."
	echo "$stdout"
	echo
	exit_code=1
fi

stdout=$(sudo aminerremotecontrol --Exec "list_backups(analysis_context)")
if [[ "$stdout" != "${PREFIX}'\"backups\": ["* ]]; then
	echo "$ERROR listing backups."
	echo "$stdout"
	echo
	exit_code=1
fi

timestamp=$(date +%s)
stdout=$(sudo aminerremotecontrol --Exec "allowlist_event_in_component(analysis_context,'EnhancedNewValueCombo',($timestamp,'/model/path'),allowlisting_data=None)")
if [[ "$stdout" != "${PREFIX}\"Allowlisted path(es) /model/DailyCron/UName, /model/DailyCron/JobNumber with ($timestamp, '/model/path').\"" ]]; then
	echo "$ERROR allowlist_event EnhancedNewMatchPathDetector."
	echo "$stdout"
	echo
	exit_code=1
fi

stdout=$(sudo aminerremotecontrol --Exec "allowlist_event_in_component(analysis_context,'MissingMatch',(' ','/model/DiskReport/Space'),allowlisting_data=-1)")
if [[ "$stdout" != "${PREFIX}\"Updated ' ' in '/model/DiskReport/Space' to new interval 2.\"" ]]; then
	echo "$ERROR allowlist_event MissingMatchPathDetector."
	echo "$stdout"
	echo
	exit_code=1
fi

stdout=$(sudo aminerremotecontrol --Exec "allowlist_event_in_component(analysis_context,'NewMatchPath',('/model/somepath','/model/DiskReport/Space','/model/DiskReport/Space1'),allowlisting_data=None)")
if [[ "$stdout" != "${PREFIX}'Allowlisted path(es) /model/somepath, /model/DiskReport/Space1 in Analysis.NewMatchPathDetector'" ]]; then
	echo "$ERROR allowlist_event NewMatchPathDetector."
	echo "$stdout"
	echo
	exit_code=1
fi

stdout=$(sudo aminerremotecontrol --Exec "allowlist_event_in_component(analysis_context,'NewMatchPathValueComboDetector','/model/somepath',allowlisting_data=None)")
if [[ "$stdout" != "${PREFIX}'Allowlisted path(es) /model/IPAddresses/Username, /model/IPAddresses/IP with /model/somepath.'" ]]; then
	echo "$ERROR allowlist_event NewMatchPathValueCombo."
	echo "$stdout"
	echo
	exit_code=1
fi

stdout=$(sudo aminerremotecontrol --Exec "allowlist_event_in_component(analysis_context,'NewMatchIdValueComboDetector','/model/somepath',allowlisting_data=None)")
if [[ "$stdout" != "${PREFIX}'Allowlisted path(es) /model/type/path/name, /model/type/syscall/syscall with /model/somepath.'" ]]; then
	echo "$ERROR allowlist_event NewMatchIdValueComboDetector."
	echo "$stdout"
	echo
	exit_code=1
fi

stdout=$(sudo aminerremotecontrol --Exec "allowlist_event_in_component(analysis_context,'EventCorrelationDetector','/model/somepath',allowlisting_data=None)")
if [[ "$stdout" != "${PREFIX}'Allowlisted path /model/somepath.'" ]]; then
	echo "$ERROR allowlist_event EventCorrelationDetector."
	echo "$stdout"
	echo
	exit_code=1
fi

stdout=$(sudo aminerremotecontrol --Exec "allowlist_event_in_component(analysis_context,'NewMatchPathValue','/model/somepath',allowlisting_data=None)")
if [[ "$stdout" != "${PREFIX}'Allowlisted path(es) /model/DailyCron/Job Number, /model/IPAddresses/Username with /model/somepath.'" ]]; then
	echo "$ERROR allowlist_event NewMatchPathValueDetector."
	echo "$stdout"
	echo
	exit_code=1
fi

sudo pkill -x aminer
sleep 2 & wait $!

exit $exit_code
