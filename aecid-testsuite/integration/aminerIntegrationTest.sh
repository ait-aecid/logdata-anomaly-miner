#!/bin/bash

#To add more log lines following positions must be changed: main script, checkAllOutputs, isExpectedOutput. The Position is marked with a "ADD HERE" comment.

. ./declarations.sh
AMINER_PERSISTENCE_PATH=/tmp/lib/aminer/*
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
	sudo rm -r $AMINER_PERSISTENCE_PATH 2> /dev/null
	sudo chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
	sudo rm /tmp/output 2> /dev/null
else
	mkdir /tmp/lib 2> /dev/null
	mkdir /tmp/lib/aminer 2> /dev/null
	rm -r $AMINER_PERSISTENCE_PATH 2> /dev/null
	chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
	rm /tmp/output 2> /dev/null
fi

echo "Integration test started.."
echo ""

FILE=/tmp/config.py
if ! test -f "$FILE"; then
    echo "$FILE does not exist!"
	exit 1
fi

#start AMiner
if [[ $sudoInstalled == 0 ]]; then
	sudo -H -u aminer bash -c 'AMiner --Foreground --Config '$FILE' > /tmp/output &'
else
	runuser -u aminer -- AMiner --Foreground --Config $FILE > /tmp/output &
fi

time=`date +%s`

touch /tmp/syslog
#Anomaly FixedDataModel HD Repair
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrad") > /tmp/syslog
#New Path
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> /tmp/syslog
#Known Path
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> /tmp/syslog
#Anomaly FixedDataModel HD Repair
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrad") >> /tmp/syslog
#Anomaly DateTimeModel
({ date '+%m.%Y %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> /tmp/syslog
#Known Path
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> /tmp/syslog
#Known Path
({ date '+%Y-%m-%d %T' && echo 'fedora' && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> /tmp/syslog
#Root Home Path
echo 'The Path of the home directory shown by pwd of the user root is: /root' >> /tmp/syslog
#User Home Path
echo 'The Path of the home directory shown by pwd of the user user is: /home/user' >> /tmp/syslog
#Guest Home Path
echo 'The Path of the home directory shown by pwd of the user guest is: /home/guest' >> /tmp/syslog

#ADD HERE

#stop AMiner
sleep 3 & wait $!
if [[ $sudoInstalled == 0 ]]; then
	sudo pkill -f AMiner
	KILL_PID=$!
else
	pkill -f AMiner
	KILL_PID=$!
fi
sleep 3
wait $KILL_PID

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
