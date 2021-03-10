#!/bin/bash

sudoInstalled=`dpkg -s sudo | grep Status 2> /dev/null`
if [[ $sudoInstalled == "Status: install ok installed" ]]; then
	sudoInstalled=0
else
	sudoInstalled=1
fi

if [[ $sudoInstalled == 0 ]]; then
	sudo mkdir /tmp/lib 2> /dev/null
	sudo mkdir /tmp/lib/aminer 2> /dev/null
	sudo chown -R $USER:$USER /tmp/lib/aminer 2> /dev/null
	sudo rm -r /tmp/lib/aminer/* 2> /dev/null
	sudo mkdir /tmp/lib/aminer/log 2> /dev/null
	sudo chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
	sudo rm /tmp/syslog 2> /dev/null
else
	mkdir /tmp/lib 2> /dev/null
	mkdir /tmp/lib/aminer 2> /dev/null
	rm -r /tmp/lib/aminer/* 2> /dev/null
	mkdir /tmp/lib/aminer/log 2> /dev/null
	chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
	rm /tmp/syslog 2> /dev/null
fi

echo "Demo started.."
echo ""

FILE=/tmp/json-input-demo-config.yml
if ! test -f "$FILE"; then
  echo "$FILE does not exist!"
	exit 1
fi

#start aminer
if [[ $sudoInstalled == 0 ]]; then
	sudo aminer --config "$FILE" &
else
	aminer --config "$FILE" &
fi

# start json in same line
read -r -d '' VAR << END
{"menu": {
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
echo "$VAR" >> /tmp/syslog

# start json in new line
read -r -d '' VAR << END
{
  "menu": {
    "id": "file",
    "value": "File",
    "popup": {
      "menuitem": [
        {"value": "New", "onclick": "CreateNewDoc()"},
        {"value": "Open", "onclick": "OpenDoc()"},
        {"value": "Close", "onclick": "CloseDoc()"}
      ]
    }
  }
}
END

# start everything in new line
read -r -d '' VAR << END
{
  "menu":
  {
    "id": "file",
    "value": "File",
    "popup":
    {
      "menuitem":
      [
        {
          "value": "New",
          "onclick": "CreateNewDoc()"
        },
        {
          "value": "Open",
          "onclick": "OpenDoc()"},
        {
          "value": "Close",
          "onclick": "CloseDoc()"}
      ]
    }
  }
}
END
echo "$VAR" >> /tmp/syslog

#stop aminer
sleep 8 & wait $!
if [[ $sudoInstalled == 0 ]]; then
	sudo pkill -x aminer
else
    pkill -x aminer
fi
KILL_PID=$!
sleep 3
wait $KILL_PID
