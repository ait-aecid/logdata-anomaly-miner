FILE=/tmp/demo-config.py
CMD_PATH=/tmp/commands.txt
sudo cp demo/aminerRemoteControl/demo-config.py $FILE
sudo sed -i 's/StreamPrinterEventHandler(analysis_context)/StreamPrinterEventHandler(analysis_context, stream=open("\/tmp\/log.txt", "a"))/g' $FILE
sudo mkdir /tmp/lib 2> /dev/null
sudo mkdir /tmp/lib/aminer 2> /dev/null
sudo mkdir /tmp/lib/aminer/log 2> /dev/null
sudo rm -r /tmp/lib/aminer/* 2> /dev/null
sudo chown -R aminer:aminer /tmp/lib 2> /dev/null
sudo rm /tmp/syslog 2> /dev/null
touch /tmp/syslog

sudo aminer --config "$FILE" & > /dev/null
sleep 1

stdout=$(sudo aminerremotecontrol --exec-file $CMD_PATH)
expected="File $CMD_PATH does not exist"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR exec-file not exists."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

START_TIME=$(date +%s)

PREFIX="Remote execution response: "
NOT_FOUND_WARNINGS="WARNING: config_properties['Core.PersistencePeriod'] = not found in the old config file.\nWARNING: config_properties['Log.StatisticsLevel'] = not found in the old config file.\nWARNING: config_properties['Log.DebugLevel'] = not found in the old config file.\nWARNING: config_properties['Log.StatisticsPeriod'] = not found in the old config file.\n"
ERROR="Error at:"
exit_code=0
expected_list=""

echo "print_config_property(analysis_context, 'Core.PersistenceDir')" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "print_config_property(analysis_context, 'Core.PersistenceDir')")
expected="$PREFIX'\"Core.PersistenceDir\": /tmp/lib/aminer'"
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR error printing 'Core.PersistenceDir'."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "print_config_property(analysis_context, 'Core.PersistencePeriod')" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "print_config_property(analysis_context, 'Core.PersistencePeriod')")
expected="$PREFIX'\"Resource \\\\\"Core.PersistencePeriod\\\\\" could not be found.\"'"
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR error printing 'Core.PersistencePeriod'."
	echo "$stdout"
	echo "Expected: $expected"
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
    echo "change_config_property(analysis_context, $property, $address)" >> $CMD_PATH
    stdout=$(sudo aminerremotecontrol --exec "change_config_property(analysis_context, $property, $address)")
    expected="$PREFIX\"$property changed to $address successfully.\""
    expected_list="${expected_list}${expected}
"
    if [[ "$stdout" != "$expected" ]]; then
	    echo "$ERROR changing $property to $address."
	    echo "Expected: $expected"
	    echo "$stdout"
	    echo
	    exit_code=1
    fi
  done
  for address in "${error_addresses[@]}"; do
    echo "change_config_property(analysis_context, $property, $address)" >> $CMD_PATH
    stdout=$(sudo aminerremotecontrol --exec "change_config_property(analysis_context, $property, $address)")
    expected="$PREFIX'FAILURE: MailAlerting.TargetAddress and MailAlerting.FromAddress must be email addresses!'"
    expected_list="${expected_list}${expected}
"
    if [[ "$stdout" != "$expected" ]]; then
	    echo "$ERROR changing $property to $address."
	    echo "$stdout"
	    echo "Expected: $expected"
	    echo
	    exit_code=1
    fi
  done
done

INTEGER_CONFIG_PROPERTIES=("'MailAlerting.AlertGraceTime'" "'MailAlerting.EventCollectTime'" "'MailAlerting.MinAlertGap'" "'MailAlerting.MaxAlertGap'" "'MailAlerting.MaxEventsPerMessage'" "'Core.PersistencePeriod'" "'Log.StatisticsLevel'" "'Log.DebugLevel'" "'Log.StatisticsPeriod'" "'Resources.MaxMemoryUsage'")
STRING_CONFIG_PROPERTIES=("'MailAlerting.TargetAddress'" "'MailAlerting.FromAddress'" "'MailAlerting.SubjectPrefix'" "'LogPrefix'")

for property in "${STRING_CONFIG_PROPERTIES[@]}"; do
  echo "change_config_property(analysis_context, $property, 123)" >> $CMD_PATH
  stdout=$(sudo aminerremotecontrol --exec "change_config_property(analysis_context, $property, 123)")
  expected="$PREFIX\"FAILURE: the value of the property $property must be of type <class 'str'>!\""
  expected_list="${expected_list}${expected}
"
  if [[ "$stdout" != "$expected" ]]; then
	  echo "$ERROR changing $property wrong Type."
	  echo "$stdout"
	  echo "Expected: $expected"
	  echo
	  exit_code=1
  fi
  echo "change_config_property(analysis_context, $property, 'root@localhost')" >> $CMD_PATH
  stdout=$(sudo aminerremotecontrol --exec "change_config_property(analysis_context, $property, 'root@localhost')")
  expected="$PREFIX\"$property changed to 'root@localhost' successfully.\""
  expected_list="${expected_list}${expected}
"
  if [[ "$stdout" != "$expected" ]]; then
	    echo "$ERROR changing $property to 'root@localhost'."
	    echo "$stdout"
	    echo "Expected: $expected"
	    echo
	    exit_code=1
  fi
done

for property in "${INTEGER_CONFIG_PROPERTIES[@]}"; do
  echo "change_config_property(analysis_context, $property, '1')" >> $CMD_PATH
  stdout=$(sudo aminerremotecontrol --exec "change_config_property(analysis_context, $property, '1')")
  expected="$PREFIX\"FAILURE: the value of the property $property must be of type <class 'int'>!\""
  expected_list="${expected_list}${expected}
"
  if [[ "$stdout" != "$expected" && "$stdout" != "$PREFIX'FAILURE: it is not safe to run the aminer with less than 32MB RAM.'" ]]; then
	  echo "$ERROR changing $property wrong Type."
	  echo "$stdout"
	  echo "Expected: $expected"
	  echo
	  exit_code=1
  fi
  echo "change_config_property(analysis_context, $property, 1)" >> $CMD_PATH
  stdout=$(sudo aminerremotecontrol --exec "change_config_property(analysis_context, $property, 1)")
  expected="$PREFIX\"$property changed to '1' successfully.\""
  if [[ "$stdout" == "$PREFIX'FAILURE: it is not safe to run the aminer with less than 32MB RAM.'" ]]; then
    expected_list="${expected_list}${stdout}
"
  else
    expected_list="${expected_list}${expected}
"
  fi
  if [[ "$stdout" != "$expected" && "$stdout" != "$PREFIX'FAILURE: it is not safe to run the aminer with less than 32MB RAM.'" ]]; then
	    echo "$ERROR changing $property to 1."
	    echo "$stdout"
	    echo "Expected: $expected"
	    echo
	    exit_code=1
  fi
done

properties=("'Log.StatisticsLevel'" "'Log.DebugLevel'")
for property in "${properties[@]}"; do
  value=0
  echo "change_config_property(analysis_context, $property, $value)" >> $CMD_PATH
  stdout=$(sudo aminerremotecontrol --exec "change_config_property(analysis_context, $property, $value)")
  expected="$PREFIX\"$property changed to '$value' successfully.\""
  expected_list="${expected_list}${expected}
"
  if [[ "$stdout" != "$expected" ]]; then
      echo "$ERROR changing $property to $value."
      echo "$stdout"
      echo "Expected: $expected"
      echo
      exit_code=1
  fi
  value=1
  echo "change_config_property(analysis_context, $property, $value)" >> $CMD_PATH
  stdout=$(sudo aminerremotecontrol --exec "change_config_property(analysis_context, $property, $value)")
  expected="$PREFIX\"$property changed to '$value' successfully.\""
  expected_list="${expected_list}${expected}
"
  if [[ "$stdout" != "$expected" ]]; then
      echo "$ERROR changing $property to $value."
      echo "$stdout"
      echo "Expected: $expected"
      echo
      exit_code=1
  fi
  value=2
  echo "change_config_property(analysis_context, $property, $value)" >> $CMD_PATH
  stdout=$(sudo aminerremotecontrol --exec "change_config_property(analysis_context, $property, $value)")
  expected="$PREFIX\"$property changed to '$value' successfully.\""
  expected_list="${expected_list}${expected}
"
  if [[ "$stdout" != "$expected" ]]; then
      echo "$ERROR changing $property to $value."
      echo "$stdout"
      echo "Expected: $expected"
      echo
      exit_code=1
  fi
  value=-1
  echo "change_config_property(analysis_context, $property, $value)" >> $CMD_PATH
  stdout=$(sudo aminerremotecontrol --exec "change_config_property(analysis_context, $property, $value)")
  expected="$PREFIX'FAILURE: STAT_LEVEL $value is not allowed. Allowed STAT_LEVEL values are 0, 1, 2.'"
  if [[ "$stdout" == "$PREFIX'FAILURE: DEBUG_LEVEL $value is not allowed. Allowed DEBUG_LEVEL values are 0, 1, 2.'" ]]; then
    expected_list="${expected_list}${stdout}
"
  else
    expected_list="${expected_list}${expected}
"
  fi
  if [[ "$stdout" != "$expected" && "$stdout" != "$PREFIX'FAILURE: DEBUG_LEVEL $value is not allowed. Allowed DEBUG_LEVEL values are 0, 1, 2.'" ]]; then
      echo "$ERROR changing $property to $value."
      echo "$stdout"
      echo "Expected: $expected"
      echo
      exit_code=1
  fi
  value=3
  echo "change_config_property(analysis_context, $property, $value)" >> $CMD_PATH
  stdout=$(sudo aminerremotecontrol --exec "change_config_property(analysis_context, $property, $value)")
  expected="$PREFIX'FAILURE: STAT_LEVEL $value is not allowed. Allowed STAT_LEVEL values are 0, 1, 2.'"
  if [[ "$stdout" == "$PREFIX'FAILURE: DEBUG_LEVEL $value is not allowed. Allowed DEBUG_LEVEL values are 0, 1, 2.'" ]]; then
    expected_list="${expected_list}${stdout}
"
  else
    expected_list="${expected_list}${expected}
"
  fi
  if [[ "$stdout" != "$expected" && "$stdout" != "$PREFIX'FAILURE: DEBUG_LEVEL $value is not allowed. Allowed DEBUG_LEVEL values are 0, 1, 2.'" ]]; then
      echo "$ERROR changing $property to $value."
      echo "$stdout"
      echo "Expected: $expected"
      echo
      exit_code=1
  fi
done

echo "rename_registered_analysis_component(analysis_context,'NewMatchPathValueCombo','NewMatchPathValueComboDetector')" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "rename_registered_analysis_component(analysis_context,'NewMatchPathValueCombo','NewMatchPathValueComboDetector')")
expected="$PREFIX\"Component 'NewMatchPathValueCombo' renamed to 'NewMatchPathValueComboDetector' successfully.\""
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR renames the 'NewMatchPathValueCombo' component to 'NewMatchPathValueComboDetector'."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "rename_registered_analysis_component(analysis_context,'NewMatchPathValueComboDetector', 222)" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "rename_registered_analysis_component(analysis_context,'NewMatchPathValueComboDetector', 222)")
expected="$PREFIX\"FAILURE: the parameters 'old_component_name' and 'new_component_name' must be of type str.\""
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR renames the 'NewMatchPathValueComboDetector' wrong Type. (no string; integer value)"
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "rename_registered_analysis_component(analysis_context,'NonExistingDetector','NewMatchPathValueComboDetector')" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "rename_registered_analysis_component(analysis_context,'NonExistingDetector','NewMatchPathValueComboDetector')")
expected="$PREFIX\"FAILURE: the component 'NonExistingDetector' does not exist.\""
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR renames a non existing component to 'NewMatchPathValueComboDetector'."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "change_attribute_of_registered_analysis_component(analysis_context, 'NewMatchPathValueComboDetector',  'learn_mode', False)" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "change_attribute_of_registered_analysis_component(analysis_context, 'NewMatchPathValueComboDetector',  'learn_mode', False)")
expected="$PREFIX\"'NewMatchPathValueComboDetector.learn_mode' changed from False to False successfully.\""
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR changes the 'learn_mode' of the 'NewMatchPathValueComboDetector' to False."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "change_attribute_of_registered_analysis_component(analysis_context, 'NewMatchPathValueComboDetector',  'learn_mode', 'True')" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "change_attribute_of_registered_analysis_component(analysis_context, 'NewMatchPathValueComboDetector',  'learn_mode', 'True')")
expected="$PREFIX\"FAILURE: property 'NewMatchPathValueComboDetector.learn_mode' must be of type <class 'bool'>!\""
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR changes the 'learn_mode' of the 'NewMatchPathValueComboDetector' wrong Type."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "print_attribute_of_registered_analysis_component(analysis_context, 'NewMatchPathValueComboDetector',  'target_path_list')" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "print_attribute_of_registered_analysis_component(analysis_context, 'NewMatchPathValueComboDetector',  'target_path_list')")
expected="$PREFIX'\"NewMatchPathValueComboDetector.target_path_list\": [\"/model/IPAddresses/Username\", \"/model/IPAddresses/IP\"]'"
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR prints the current list of paths."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "print_attribute_of_registered_analysis_component(analysis_context, 'NewMatchPathValueComboDetector',  'other_path_list')" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "print_attribute_of_registered_analysis_component(analysis_context, 'NewMatchPathValueComboDetector',  'other_path_list')")
expected="$PREFIX\"FAILURE: the component 'NewMatchPathValueComboDetector' does not have an attribute named 'other_path_list'.\""
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR prints not existing attribute."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "add_handler_to_atom_filter_and_register_analysis_component(analysis_context, 'AtomFilter', NewMatchPathDetector(analysis_context.aminer_config, analysis_context.atomizer_factory.atom_handler_list, learn_mode=True), 'NewMatchPathDet')" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "add_handler_to_atom_filter_and_register_analysis_component(analysis_context, 'AtomFilter', NewMatchPathDetector(analysis_context.aminer_config, analysis_context.atomizer_factory.atom_handler_list, learn_mode=True), 'NewMatchPathDet')")
expected="$PREFIX\"Component 'NewMatchPathDet' added to 'AtomFilter' successfully.\""
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR add a new NewMatchPathDetector to the config."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "add_handler_to_atom_filter_and_register_analysis_component(analysis_context, 'AtomFilter', 'StringDetector', 'StringDetector')" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "add_handler_to_atom_filter_and_register_analysis_component(analysis_context, 'AtomFilter', 'StringDetector', 'StringDetector')")
expected="$PREFIX\"FAILURE: 'component' must implement the AtomHandlerInterface!\""
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR add a wrong class to the config."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "save_current_config(analysis_context,'/tmp/config.py')" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "save_current_config(analysis_context,'/tmp/config.py')")
expected="${PREFIX}\"${NOT_FOUND_WARNINGS}Successfully saved the current config to /tmp/config.py.\""
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR save the current config to /tmp/config.py."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi
sudo rm /tmp/config.py

echo "save_current_config(analysis_context,'[/path/config.py')" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "save_current_config(analysis_context,'[/path/config.py')")
expected="${PREFIX}'Exception: [/path/config.py is not a valid filename!'"
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR save the current config to an invalid path."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "save_current_config(analysis_context,'/notExistingPath/config.py')" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "save_current_config(analysis_context,'/notExistingPath/config.py')")
expected="${PREFIX}\"${NOT_FOUND_WARNINGS}FAILURE: file '/notExistingPath/config.py' could not be found or opened!\""
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR save the current config to an not existing directory path."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "persist_all()" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "persist_all()")
expected="${PREFIX}'OK'"
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR persist_all."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

# echo "create_backup(analysis_context)" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "create_backup(analysis_context)")
expected="${PREFIX}'Created backup "
# expected_list="${expected_list}${expected}
# "
if [[ "$stdout" != "$expected"* ]]; then
	echo "$ERROR creating backup."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

# echo "list_backups(analysis_context)" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "list_backups(analysis_context)")
expected="${PREFIX}'\"backups\": ["
# expected_list="${expected_list}${expected}
# "
if [[ "$stdout" != "$expected"* ]]; then
	echo "$ERROR listing backups."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

timestamp=$(date +%s)
echo "allowlist_event_in_component(analysis_context,'EnhancedNewValueCombo',($timestamp,'/model/path'),allowlisting_data=None)" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "allowlist_event_in_component(analysis_context,'EnhancedNewValueCombo',($timestamp,'/model/path'),allowlisting_data=None)")
expected="${PREFIX}\"Allowlisted path(es) /model/DailyCron/UName, /model/DailyCron/JobNumber with ($timestamp, '/model/path').\""
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR allowlist_event EnhancedNewMatchPathDetector."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "allowlist_event_in_component(analysis_context,'MissingMatch',(' ','/model/DiskReport/Space'),allowlisting_data=-1)" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "allowlist_event_in_component(analysis_context,'MissingMatch',(' ','/model/DiskReport/Space'),allowlisting_data=-1)")
expected="${PREFIX}\"Updated ' ' in '/model/DiskReport/Space' to new interval 2.\""
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR allowlist_event MissingMatchPathDetector."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "allowlist_event_in_component(analysis_context,'NewMatchPath','/model/somepath',allowlisting_data=None)" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "allowlist_event_in_component(analysis_context,'NewMatchPath','/model/somepath',allowlisting_data=None)")
expected="${PREFIX}'Allowlisted path(es) /model/somepath in Analysis.NewMatchPathDetector.'"
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR allowlist_event NewMatchPathDetector."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "allowlist_event_in_component(analysis_context,'NewMatchPathValueComboDetector','/model/somepath',allowlisting_data=None)" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "allowlist_event_in_component(analysis_context,'NewMatchPathValueComboDetector','/model/somepath',allowlisting_data=None)")
expected="${PREFIX}'Allowlisted path(es) /model/IPAddresses/Username, /model/IPAddresses/IP with /model/somepath.'"
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR allowlist_event NewMatchPathValueCombo."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "allowlist_event_in_component(analysis_context,'NewMatchIdValueComboDetector','/model/somepath',allowlisting_data=None)" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "allowlist_event_in_component(analysis_context,'NewMatchIdValueComboDetector','/model/somepath',allowlisting_data=None)")
expected="${PREFIX}'Allowlisted path(es) /model/type/path/name, /model/type/syscall/syscall with /model/somepath.'"
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR allowlist_event NewMatchIdValueComboDetector."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "allowlist_event_in_component(analysis_context,'EventCorrelationDetector','/model/somepath',allowlisting_data=None)" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "allowlist_event_in_component(analysis_context,'EventCorrelationDetector','/model/somepath',allowlisting_data=None)")
expected="${PREFIX}'Allowlisted path /model/somepath.'"
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR allowlist_event EventCorrelationDetector."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "allowlist_event_in_component(analysis_context,'NewMatchPathValue','/model/somepath',allowlisting_data=None)" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "allowlist_event_in_component(analysis_context,'NewMatchPathValue','/model/somepath',allowlisting_data=None)")
expected="${PREFIX}'Allowlisted path(es) /model/DailyCron/Job Number, /model/IPAddresses/Username with /model/somepath.'"
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR allowlist_event NewMatchPathValueDetector."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "blocklist_event_in_component(analysis_context,'EventCorrelationDetector','/model/somepath',blocklisting_data=None)" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "blocklist_event_in_component(analysis_context,'EventCorrelationDetector','/model/somepath',blocklisting_data=None)")
expected="${PREFIX}'Blocklisted path /model/somepath.'"
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR blocklist_event EventCorrelationDetector."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi

echo "blocklist_event_in_component(analysis_context,'EventCorrelationDetector','/model/somepath',blocklisting_data=None)" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "blocklist_event_in_component(analysis_context,'EventCorrelationDetector','/model/somepath',blocklisting_data=None)")
expected="${PREFIX}'Blocklisted path /model/somepath.'"
expected_list="${expected_list}${expected}
"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR blocklist_event EventCorrelationDetector."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi
EXEC_TIME=$(($(date +%s)-START_TIME))

echo "print_current_config(analysis_context)" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "print_current_config(analysis_context)")
expected="$PREFIX None"
if [[ "$stdout" == "$expected" ]]; then
	echo "$ERROR print config had an execution error."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi
stdout=$(echo "$stdout" | sed -e "s/\"next_persist_time\".*,//")
expected_list="${expected_list}${stdout}
"

echo "reopen_event_handler_streams(analysis_context)" >> $CMD_PATH
stdout=$(sudo aminerremotecontrol --exec "reopen_event_handler_streams(analysis_context)")
expected="$PREFIX'Reopened all StreamPrinterEventHandler streams.'"
if [[ "$stdout" != "$expected" ]]; then
	echo "$ERROR reopen_event_handler_streams had an execution error."
	echo "$stdout"
	echo "Expected: $expected"
	echo
	exit_code=1
fi
stdout=$(echo "$stdout" | sed -e "s/\"next_persist_time\".*,//")
expected_list="${expected_list}${stdout}
"

sudo pkill -x aminer
sleep 2 & wait $!
sudo mkdir /tmp/lib 2> /dev/null
sudo mkdir /tmp/lib/aminer 2> /dev/null
sudo rm -r /tmp/lib/aminer/* 2> /dev/null
sudo chown -R aminer:aminer /tmp/lib 2> /dev/null
sudo rm /tmp/syslog 2> /dev/null
touch /tmp/syslog
sudo aminer --config "$FILE" & > /dev/null
sleep 1

START_TIME=$(date +%s)
stdout=$(sudo aminerremotecontrol --exec-file $CMD_PATH)
stdout=$(echo "$stdout" | sed -e "s/\"next_persist_time\".*,//")
expected_list=$(echo "$expected_list" | sed -e "s/\"next_persist_time\".*,//")
if [[ "$stdout" != "$expected_list" ]]; then
	echo "$ERROR exec-file."
	echo "$stdout"
	echo
	echo "Expected: $expected_list"
	echo
	exit_code=1
fi
EXEC_FILE_TIME=$(($(date +%s)-START_TIME))

sudo pkill -x aminer
sleep 2 & wait $!
sudo rm $CMD_PATH
echo "Command execution time with --exec ${EXEC_TIME}s"
echo "Command execution time with --exec-file ${EXEC_FILE_TIME}s"
exit $exit_code
