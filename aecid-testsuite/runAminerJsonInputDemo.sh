cp demo/aminerJsonInputDemo/json-input-demo-config.yml /tmp/json-input-demo-config.yml
sudo chown -R aminer:aminer /tmp/lib 2> /dev/null
sudo chmod +x demo/aminerJsonInputDemo/aminerJsonInputDemo.sh
sudo ./demo/aminerJsonInputDemo/aminerJsonInputDemo.sh > /tmp/out.txt
exit_code=$?

OUTPUT=$(cat /tmp/out.txt)

read -r -d '' VAR << END
New path(es) detected
NewMatchPathDetector: "DefaultNewMatchPathDetector" (1 lines)
  /model: {'menu': {'id': 'file', 'value': 'File', 'popup': {'menuitem': [{'value': 'New', 'onclick': 'CreateNewDoc()'}, {'value': 'Open', 'onclick': 'OpenDoc()'}, {'value': 'Close', 'onclick': 'CloseDoc()'}]}}}
  /model/menu/id/id: file
  /model/menu/value/value: File
  /model/menu/popup/menuitem/value/buttonNames: 0
  /model/menu/popup/menuitem/onclick/buttonOnclick: 0
  /model/menu/popup/menuitem/value/buttonNames: 1
  /model/menu/popup/menuitem/onclick/buttonOnclick: 1
  /model/menu/popup/menuitem/value/buttonNames: 2
  /model/menu/popup/menuitem/onclick/buttonOnclick: 2
['/model', '/model/menu/popup/menuitem/value/buttonNames', '/model/menu/popup/menuitem/onclick/buttonOnclick', '/model/menu/id/id', '/model/menu/value/value', '/model/menu/popup/menuitem/value/buttonNames/0', '/model/menu/popup/menuitem/onclick/buttonOnclick/0', '/model/menu/popup/menuitem/value/buttonNames/1', '/model/menu/popup/menuitem/onclick/buttonOnclick/1', '/model/menu/popup/menuitem/value/buttonNames/2', '/model/menu/popup/menuitem/onclick/buttonOnclick/2']
Original log line: {"menu": {
  "id": "file",
  "value": "File",
  "popup": {
    "menuitem": [
      {"value": "New", "onclick": "CreateNewDoc()"},
      {"value": "Open", "onclick": "OpenDoc()"},
      {"value": "Close", "onclick": "CloseDoc()"}
    ]
  }
}}
END
if [[ "$OUTPUT" != *"$VAR"* ]]; then
  echo "$VAR"
  echo
  exit_code=1
fi

read -r -d '' VAR << END
New value combination(s) detected
NewMatchPathValueComboDetector: "NewMatchPathValueCombo" (1 lines)
  (b'file', b'File')
Original log line: {"menu": {
  "id": "file",
  "value": "File",
  "popup": {
    "menuitem": [
      {"value": "New", "onclick": "CreateNewDoc()"},
      {"value": "Open", "onclick": "OpenDoc()"},
      {"value": "Close", "onclick": "CloseDoc()"}
    ]
  }
}}
END
if [[ "$OUTPUT" != *"$VAR"* ]]; then
  echo "$VAR"
  echo
  exit_code=1
fi

read -r -d '' VAR << END
New value(s) detected
NewMatchPathValueDetector: "NewMatchPathValue" (1 lines)
  {'/model/menu/id/id': 'file'}
END
if [[ "$OUTPUT" != *"$VAR"* ]]; then
  echo "$VAR"
  echo
  exit_code=1
fi

read -r -d '' VAR << END
New value(s) detected
NewMatchPathValueDetector: "NewMatchPathValue" (1 lines)
  {'/model/menu/value/value': 'File'}
END
if [[ "$OUTPUT" != *"$VAR"* ]]; then
  echo "$VAR"
  echo
  exit_code=1
fi

sudo rm /tmp/json-input-demo-config.yml 2> /dev/null
sudo rm /tmp/syslog
sudo rm /tmp/out.txt
exit $exit_code
