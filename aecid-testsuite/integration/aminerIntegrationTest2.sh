#!/bin/bash

#To add more log lines following positions must be changed: main script, checkAllOutputs, isExpectedOutput. The Position is marked with a "ADD HERE" comment.

NUMBER_OF_LOG_LINES=7

. ./declarations.sh

sudoInstalled=`dpkg -s sudo | grep Status 2> /dev/null`
if [[ $sudoInstalled == "Status: install ok installed" ]]; then
	sudoInstalled=0
else
	sudoInstalled=1
fi

#: <<'END'
AMINER_PERSISTENCE_PATH=/tmp/lib/aminer/*
if [[ $sudoInstalled == 0 ]]; then
	sudo mkdir /tmp/lib 2> /dev/null
	sudo mkdir /tmp/lib/aminer 2> /dev/null
	sudo chown -R $USER:$USER /tmp/lib/aminer 2> /dev/null
	sudo rm -r $AMINER_PERSISTENCE_PATH 2> /dev/null
	sudo chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
	sudo rm /tmp/syslog 2> /dev/null
	sudo rm /tmp/auth.log 2> /dev/null
	sudo rm /tmp/output 2> /dev/null
else
	mkdir /tmp/lib 2> /dev/null
	mkdir /tmp/lib/aminer 2> /dev/null
	rm -r $AMINER_PERSISTENCE_PATH 2> /dev/null
	chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
	rm /tmp/syslog 2> /dev/null
	rm /tmp/auth.log 2> /dev/null
	rm /tmp/output 2> /dev/null
fi

echo "Integration test started.."
echo ""

FILE=/tmp/config21.py
if ! test -f "$FILE"; then
    echo "$FILE does not exist!"
	exit 1
fi
FILE=/tmp/config22.py
if ! test -f "$FILE"; then
    echo "$FILE does not exist!"
	exit 1
fi

#start AMiner
if [[ $sudoInstalled == 0 ]]; then
	sudo -H -u aminer bash -c 'AMiner --Foreground --Config /tmp/config21.py > /tmp/output &'
else
	runuser -u aminer -- AMiner --Foreground --Config $FILE > /tmp/output &
fi

time=`date +%s`

#Anomaly FixedDataModel HD Repair
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrad") > /tmp/syslog
sleep 1
#New Path
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") > /tmp/auth.log
sleep 1
#Known Path
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> /tmp/syslog
sleep 1
#Anomaly FixedDataModel HD Repair
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrad") >> /tmp/auth.log
sleep 1
#Anomaly DateTimeModel
({ date '+%m.%Y %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> /tmp/syslog
sleep 1
#Known Path
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> /tmp/auth.log
sleep 1
#Known Path
({ date '+%Y-%m-%d %T' && echo 'fedora' && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> /tmp/syslog
sleep 1
#Root Home Path
echo 'The Path of the home directory shown by pwd of the user root is: /root' >> /tmp/auth.log
sleep 1
#User Home Path
echo 'The Path of the home directory shown by pwd of the user user is: /home/user' >> /tmp/syslog
sleep 1
#Guest Home Path
echo 'The Path of the home directory shown by pwd of the user guest is: /home/guest' >> /tmp/auth.log

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
	checkAllSyslogs
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
		echo "test failed at checking syslogs.."
		exit 1
	fi
else
	echo ""
	echo "test failed at checking outputs.."
	exit 1
fi
echo ""
echo "part 1 finished"
echo ""
#END

AMINER_PERSISTENCE_PATH=/tmp/lib/aminer/*
if [[ $sudoInstalled == 0 ]]; then
	sudo chown -R $USER:$USER /tmp/lib/aminer 2> /dev/null
	sudo rm -r $AMINER_PERSISTENCE_PATH 2> /dev/null
	sudo chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
	sudo rm /tmp/syslog 2> /dev/null
	sudo rm /tmp/auth.log 2> /dev/null
else
	rm -r $AMINER_PERSISTENCE_PATH 2> /dev/null
	chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
	rm /tmp/syslog 2> /dev/null
	rm /tmp/auth.log 2> /dev/null
fi

COUNTER=0

#start AMiner
if [[ $sudoInstalled == 0 ]]; then
	sudo -H -u aminer bash -c 'AMiner --Foreground --Config /tmp/config22.py > /tmp/output &'
else
	runuser -u aminer -- AMiner --Foreground --Config /tmp/config22.py > /tmp/output &
fi

time=`date +%s`

#Anomaly FixedDataModel HD Repair
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrad") > /tmp/syslog
sleep 1
#New Path
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") > /tmp/auth.log
sleep 1
#Known Path
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> /tmp/syslog
sleep 1
#Anomaly FixedDataModel HD Repair
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrad") >> /tmp/auth.log
sleep 1
#Anomaly DateTimeModel
({ date '+%m.%Y %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> /tmp/syslog
sleep 1
#Known Path
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> /tmp/auth.log
sleep 1
#Known Path
({ date '+%Y-%m-%d %T' && echo 'fedora' && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> /tmp/syslog
sleep 1
#Root Home Path
echo 'The Path of the home directory shown by pwd of the user root is: /root' >> /tmp/auth.log
sleep 1
#User Home Path
echo 'The Path of the home directory shown by pwd of the user user is: /home/user' >> /tmp/syslog
sleep 1
#Guest Home Path
echo 'The Path of the home directory shown by pwd of the user guest is: /home/guest' >> /tmp/auth.log

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
	checkAllSyslogs
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
		echo "test failed at checking syslogs.."
		exit 1
	fi
else
	echo ""
	echo "test failed at checking outputs.."
	exit 1
fi
echo ""
echo "part 2 finished"
exit 0

