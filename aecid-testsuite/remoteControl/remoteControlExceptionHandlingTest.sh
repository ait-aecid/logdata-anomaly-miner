#This test can be run with the existing demo-config of the aminerRemoteControl module.

echo "removes the 'LogPrefix'."
sudo aminerRemoteControl --Exec "change_config_property(analysis_context, 'LogPrefix', '')"
echo

echo "removes the 'LogPrefix' wrong Type."
sudo aminerRemoteControl --Exec "change_config_property(analysis_context, 'LogPrefix', None)"
echo

echo "renames the 'NewMatchPathValueCombo' component to 'NewMatchPathValueComboDetector'."
sudo aminerRemoteControl --Exec "rename_registered_analysis_component(analysis_context,'NewMatchPathValueCombo','NewMatchPathValueComboDetector')"
echo

echo "renames the 'NewMatchPathValueComboDetector' wrong Type. (no string; integer value)"
sudo aminerRemoteControl --Exec "rename_registered_analysis_component(analysis_context,'NewMatchPathValueComboDetector', 222)"
echo

echo "renames a non existing component to 'NewMatchPathValueComboDetector'."
sudo aminerRemoteControl --Exec "rename_registered_analysis_component(analysis_context,'NonExistingDetector','NewMatchPathValueComboDetector')"
echo

echo "changes the 'auto_include_flag' of the 'NewMatchPathValueComboDetector' to False."
sudo aminerRemoteControl --Exec "change_attribute_of_registered_analysis_component(analysis_context, 'NewMatchPathValueComboDetector',  'auto_include_flag', False)"
echo

echo "changes the 'auto_include_flag' of the 'NewMatchPathValueComboDetector' wrong Type."
sudo aminerRemoteControl --Exec "change_attribute_of_registered_analysis_component(analysis_context, 'NewMatchPathValueComboDetector',  'auto_include_flag', 'True')"
echo

echo "prints the current list of paths."
sudo aminerRemoteControl --Exec "print_attribute_of_registered_analysis-component(analysis_context, 'NewMatchPathValueComboDetector',  'target_path_list')"
echo

echo "prints not existing attribute."
sudo aminerRemoteControl --Exec "print_attribute_of_registered_analysis-component(analysis_context, 'NewMatchPathValueComboDetector',  'other_path_list')"
echo

echo "add a new NewMatchPathDetector to the config."
sudo aminerRemoteControl --Exec "add_handler_to_atom_filter_and_register_analysis_component(analysis_context, 'AtomFilter', NewMatchPathDetector(analysis_context.aminer_config, analysis_context.atomizer_factory.atom_handler_list, auto_include_flag=True), 'NewMatchPathDet')"
echo

echo "add a wrong class to the config."
sudo aminerRemoteControl --Exec "add_handler_to_atom_filter_and_register_analysis_component(analysis_context, 'AtomFilter', 'StringDetector', 'StringDetector')"
echo

echo "save the current config to /tmp/config.py"
sudo aminerRemoteControl --Exec "save_current_config(analysis_context,'/tmp/config.py')"
echo

echo "save the current config to an invalid path."
sudo aminerRemoteControl --Exec "save_current_config(analysis_context,'[dd/path/config.py')"
echo

echo "save the current config to an not existing directory path."
sudo aminerRemoteControl --Exec "save_current_config(analysis_context,'/notExistingPath/config.py')"
