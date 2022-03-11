#!/bin/bash

#To add more log lines following positions must be changed: main script, checkAllOutputs, isExpectedOutput. The Position is marked with a "ADD HERE" comment.

. ../testFunctions.sh
. ./declarations.sh
AMINER_PERSISTENCE_PATH=/tmp/lib/aminer/*
LOGFILE=/tmp/syslog

sudo mkdir /tmp/lib 2> /dev/null
sudo mkdir /tmp/lib/aminer 2> /dev/null
sudo chown -R $USER:$USER /tmp/lib/aminer 2> /dev/null
sudo rm -r $AMINER_PERSISTENCE_PATH 2> /dev/null
sudo chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null

echo "Integration test started.."
echo ""

CFG_PATH=/tmp/config.py
if ! test -f "$CFG_PATH"; then
    echo "$CFG_PATH does not exist!"
	exit 1
fi

time=`date +%s`

#Anomaly FixedDataModel HD Repair
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrad") > $LOGFILE
#New Path
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> $LOGFILE
#Known Path
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> $LOGFILE
#Anomaly FixedDataModel HD Repair
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrad") >> $LOGFILE
#Anomaly DateTimeModel
({ date '+%m.%Y %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> $LOGFILE
#Known Path
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> $LOGFILE
#Known Path
({ date '+%Y-%m-%d %T' && echo 'fedora' && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> $LOGFILE
#Root Home Path
echo 'The Path of the home directory shown by pwd of the user root is: /root' >> $LOGFILE
#User Home Path
echo 'The Path of the home directory shown by pwd of the user user is: /home/user' >> $LOGFILE
#Guest Home Path
echo 'The Path of the home directory shown by pwd of the user guest is: /home/guest' >> $LOGFILE

#ADD HERE

runAminerUntilEnd "sudo aminer --config $CFG_PATH" "$LOGFILE" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "/tmp/output"

checkAllOutputs
if [ $? == 0 ]; then
	checkAllMails
	if [ $? == 0 ]; then
		echo ""
		echo "all mails were found in the mailbox!"
		echo "finished test successfully.."
	else
		echo ""
		echo "test failed at checking mails.."
		exit 1
	fi
else
	echo ""
	echo "test failed at checking outputs.."
	exit 1
fi
exit 0
