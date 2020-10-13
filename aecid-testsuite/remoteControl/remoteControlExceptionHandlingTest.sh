#This test can be run with the existing demo-config of the AMinerRemoteControl module.

echo "removes the 'LogPrefix'."
sudo aminerRemoteControl --Exec "changeConfigProperty(analysisContext, 'LogPrefix', '')"
echo

echo "removes the 'LogPrefix' wrong Type."
sudo aminerRemoteControl --Exec "changeConfigProperty(analysisContext, 'LogPrefix', None)"
echo

echo "renames the 'NewMatchPathValueCombo' component to 'NewMatchPathValueComboDetector'."
sudo aminerRemoteControl --Exec "renameRegisteredAnalysisComponent(analysisContext,'NewMatchPathValueCombo','NewMatchPathValueComboDetector')"
echo

echo "renames the 'NewMatchPathValueComboDetector' wrong Type. (no string; integer value)"
sudo aminerRemoteControl --Exec "renameRegisteredAnalysisComponent(analysisContext,'NewMatchPathValueComboDetector', 222)"
echo

echo "renames a non existing component to 'NewMatchPathValueComboDetector'."
sudo aminerRemoteControl --Exec "renameRegisteredAnalysisComponent(analysisContext,'NonExistingDetector','NewMatchPathValueComboDetector')"
echo

echo "changes the 'autoIncludeFlag' of the 'NewMatchPathValueComboDetector' to False."
sudo aminerRemoteControl --Exec "changeAttributeOfRegisteredAnalysisComponent(analysisContext, 'NewMatchPathValueComboDetector',  'auto_include_flag', False)"
echo

echo "changes the 'auto_include_flag' of the 'NewMatchPathValueComboDetector' wrong Type."
sudo aminerRemoteControl --Exec "changeAttributeOfRegisteredAnalysisComponent(analysisContext, 'NewMatchPathValueComboDetector',  'auto_include_flag', 'True')"
echo

echo "prints the current list of paths."
sudo aminerRemoteControl --Exec "printAttributeOfRegisteredAnalysisComponent(analysisContext, 'NewMatchPathValueComboDetector',  'target_path_list')"
echo

echo "prints not existing attribute."
sudo aminerRemoteControl --Exec "printAttributeOfRegisteredAnalysisComponent(analysisContext, 'NewMatchPathValueComboDetector',  'otherPathList')"
echo

echo "add a new NewMatchPathDetector to the config."
sudo aminerRemoteControl --Exec "addHandlerToAtomFilterAndRegisterAnalysisComponent(analysisContext, 'AtomFilter', NewMatchPathDetector(analysisContext.aminer_config, analysisContext.atomizer_factory.atom_handler_list, auto_include_flag=True), 'NewMatchPathDet')"
echo

echo "add a wrong class to the config."
sudo aminerRemoteControl --Exec "addHandlerToAtomFilterAndRegisterAnalysisComponent(analysisContext, 'AtomFilter', 'StringDetector', 'StringDetector')"
echo

echo "save the current config to /tmp/config.py"
sudo aminerRemoteControl --Exec "saveCurrentConfig(analysisContext,'/tmp/config.py')"
echo

echo "save the current config to an invalid path."
sudo aminerRemoteControl --Exec "saveCurrentConfig(analysisContext,'[dd/path/config.py')"
echo

echo "save the current config to an not existing directory path."
sudo aminerRemoteControl --Exec "saveCurrentConfig(analysisContext,'/notExistingPath/config.py')"
