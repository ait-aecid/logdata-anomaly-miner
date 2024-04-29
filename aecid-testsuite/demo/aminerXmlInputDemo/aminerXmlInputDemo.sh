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

FILE=/tmp/xml-input-demo-config.yml
if ! test -f "$FILE"; then
  echo "$FILE does not exist!"
	exit 1
fi

read -r -d '' VAR << END
<?xml version="1.0" encoding="UTF-8"?>
<messages>
    <note id="501">
        <to>Tove</to>
        <from>Jani</from>
        <heading/>
        <body>
            <text1>Don't forget me this weekend!</text1>
            <text2>Don't forget me this weekend!</text2>
        </body>
    </note>
    <note id="502" opt="text">
        <to>Jani</to>
        <from>Tove</from>
        <heading>Re: </heading>
        <body>
            <text1>I will not</text1>
            <text2>I will not</text2>
        </body>
    </note>
</messages>
END
echo "$VAR" >> $LOGFILE

runAminerUntilEnd "sudo aminer --config $FILE" "$LOGFILE" "/tmp/lib/aminer/AnalysisChild/RepositioningData" "$FILE"
exit $?
