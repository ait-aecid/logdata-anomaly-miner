#!/bin/bash

. ./testFunctions.sh

LOGFILE=/tmp/syslog
sudo mkdir /tmp/lib 2> /dev/null
sudo mkdir /tmp/lib/aminer 2> /dev/null
sudo chown -R $USER:$USER /tmp/lib/aminer 2> /dev/null
sudo rm -r /tmp/lib/aminer/* 2> /dev/null
sudo mkdir /tmp/lib/aminer/log 2> /dev/null
sudo chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
sudo rm $LOGFILE 2> /dev/null

echo "Demo started.."
echo ""

FILE=/tmp/json-input-demo-config.yml
if ! test -f "$FILE"; then
  echo "$FILE does not exist!"
	exit 1
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
echo "$VAR" >> $LOGFILE

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
echo "$VAR" >> $LOGFILE

runAminerUntilEnd "sudo aminer --config $FILE" "$LOGFILE" "/tmp/lib/aminer/AnalysisChild/RepositioningData" "$FILE"
exit $?
