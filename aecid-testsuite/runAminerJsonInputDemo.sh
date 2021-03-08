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
  /model/menu/id: b'file'
  /model/menu/value: b'File'
  /model/menu/popup/menuitem/buttonNames: 0
  /model/menu/popup/menuitem/buttonOnclick: 0
  /model/menu/popup/menuitem/buttonNames: 1
  /model/menu/popup/menuitem/buttonOnclick: 1
  /model/menu/popup/menuitem/buttonNames: 2
  /model/menu/popup/menuitem/buttonOnclick: 2
['/model', '/model/menu/id', '/model/menu/value', '/model/menu/popup/menuitem/buttonNames', '/model/menu/popup/menuitem/buttonOnclick']
Original log line: b'{"menu": {\n  "id": "file",\n  "value": "File",\n  "popup": {\n    "menuitem": [\n      {"value": "New", "onclick": "CreateNewDoc()"},\n      {"value": "Open", "onclick": "OpenDoc()"},\n      {"value": "Close", "onclick": "CloseDoc()"}\n    ]\n  }\n}}'
END
if [[ "$OUTPUT" != *"$VAR"* ]]; then
  echo "$VAR"
  echo
  exit_code=1
fi

read -r -d '' VAR << END
New value combination(s) detected
NewMatchPathValueComboDetector: "NewMatchPathValueCombo" (1 lines)
  /model: {'menu': {'id': 'file', 'value': 'File', 'popup': {'menuitem': [{'value': 'New', 'onclick': 'CreateNewDoc()'}, {'value': 'Open', 'onclick': 'OpenDoc()'}, {'value': 'Close', 'onclick': 'CloseDoc()'}]}}}
  /model/menu/id: b'file'
  /model/menu/value: b'File'
  /model/menu/popup/menuitem/buttonNames: 0
  /model/menu/popup/menuitem/buttonOnclick: 0
  /model/menu/popup/menuitem/buttonNames: 1
  /model/menu/popup/menuitem/buttonOnclick: 1
  /model/menu/popup/menuitem/buttonNames: 2
  /model/menu/popup/menuitem/buttonOnclick: 2
(b'file', b'File')
Original log line: b'{"menu": {\n  "id": "file",\n  "value": "File",\n  "popup": {\n    "menuitem": [\n      {"value": "New", "onclick": "CreateNewDoc()"},\n      {"value": "Open", "onclick": "OpenDoc()"},\n      {"value": "Close", "onclick": "CloseDoc()"}\n    ]\n  }\n}}'
END
if [[ "$OUTPUT" != *"$VAR"* ]]; then
  echo "$VAR"
  echo
  exit_code=1
fi

read -r -d '' VAR << END
New value(s) detected
NewMatchPathValueDetector: "NewMatchPathValue" (1 lines)
  /model: {'menu': {'id': 'file', 'value': 'File', 'popup': {'menuitem': [{'value': 'New', 'onclick': 'CreateNewDoc()'}, {'value': 'Open', 'onclick': 'OpenDoc()'}, {'value': 'Close', 'onclick': 'CloseDoc()'}]}}}
  /model/menu/id: b'file'
  /model/menu/value: b'File'
  /model/menu/popup/menuitem/buttonNames: 0
  /model/menu/popup/menuitem/buttonOnclick: 0
  /model/menu/popup/menuitem/buttonNames: 1
  /model/menu/popup/menuitem/buttonOnclick: 1
  /model/menu/popup/menuitem/buttonNames: 2
  /model/menu/popup/menuitem/buttonOnclick: 2
{'/model/menu/id': 'file'}
Original log line: b'{"menu": {\n  "id": "file",\n  "value": "File",\n  "popup": {\n    "menuitem": [\n      {"value": "New", "onclick": "CreateNewDoc()"},\n      {"value": "Open", "onclick": "OpenDoc()"},\n      {"value": "Close", "onclick": "CloseDoc()"}\n    ]\n  }\n}}'
END
if [[ "$OUTPUT" != *"$VAR"* ]]; then
  echo "$VAR"
  echo
  exit_code=1
fi

read -r -d '' VAR << END
New value(s) detected
NewMatchPathValueDetector: "NewMatchPathValue" (1 lines)
  /model: {'menu': {'id': 'file', 'value': 'File', 'popup': {'menuitem': [{'value': 'New', 'onclick': 'CreateNewDoc()'}, {'value': 'Open', 'onclick': 'OpenDoc()'}, {'value': 'Close', 'onclick': 'CloseDoc()'}]}}}
  /model/menu/id: b'file'
  /model/menu/value: b'File'
  /model/menu/popup/menuitem/buttonNames: 0
  /model/menu/popup/menuitem/buttonOnclick: 0
  /model/menu/popup/menuitem/buttonNames: 1
  /model/menu/popup/menuitem/buttonOnclick: 1
  /model/menu/popup/menuitem/buttonNames: 2
  /model/menu/popup/menuitem/buttonOnclick: 2
{'/model/menu/value': 'File'}
Original log line: b'{"menu": {\n  "id": "file",\n  "value": "File",\n  "popup": {\n    "menuitem": [\n      {"value": "New", "onclick": "CreateNewDoc()"},\n      {"value": "Open", "onclick": "OpenDoc()"},\n      {"value": "Close", "onclick": "CloseDoc()"}\n    ]\n  }\n}}'
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
