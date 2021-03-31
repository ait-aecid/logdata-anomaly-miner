#!/bin/bash

#To add more log lines following positions must be changed: main script, checkAllOutputs, isExpectedOutput. The Position is marked with a "ADD HERE" comment.

NUMBER_OF_LOG_LINES=7

. ./declarations.sh

#<<'END'
AMINER_PERSISTENCE_PATH=/tmp/lib/aminer/*
sudo mkdir /tmp/lib 2> /dev/null
sudo mkdir /tmp/lib/aminer 2> /dev/null
sudo chown -R $USER:$USER /tmp/lib/aminer 2> /dev/null
sudo rm -r $AMINER_PERSISTENCE_PATH 2> /dev/null
sudo chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
sudo rm /tmp/syslog 2> /dev/null
sudo rm /tmp/auth.log 2> /dev/null
sudo rm /tmp/output 2> /dev/null

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

#start aminer
sudo aminer --config /tmp/config21.py > /tmp/output &

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

#stop aminer
sleep 3 & wait $!
sudo pkill -x aminer
KILL_PID=$!
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
sudo mkdir /tmp/lib 2> /dev/null
sudo mkdir /tmp/lib/aminer 2> /dev/null
sudo chown -R $USER:$USER /tmp/lib/aminer 2> /dev/null
sudo rm -r $AMINER_PERSISTENCE_PATH 2> /dev/null
sudo chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
sudo rm /tmp/syslog 2> /dev/null
sudo rm /tmp/auth.log 2> /dev/null
sudo rm /tmp/output 2> /dev/null
sudo cp ../unit/config/kafka-client.conf /etc/aminer/kafka-client.conf
curl https://mirror.klaus-uwe.me/apache/kafka/2.7.0/kafka_2.12-2.7.0.tgz --output kafka.tgz
tar xvf kafka.tgz > /dev/null
rm kafka.tgz
kafka_2.12-2.7.0/bin/zookeeper-server-start.sh kafka_2.12-2.7.0/config/zookeeper.properties > /dev/null &
sleep 1
kafka_2.12-2.7.0/bin/kafka-server-start.sh kafka_2.12-2.7.0/config/server.properties > /dev/null &
sleep 1

COUNTER=0

#start aminer
sudo aminer --config /tmp/config22.py > /tmp/output &
sleep 5

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

#stop aminer
sleep 3 & wait $!
sudo pkill -x aminer
KILL_PID=$!
sleep 3
wait $KILL_PID

result=0
checkAllOutputs
if [ $? == 0 ]; then
	checkAllSyslogs
	if [ $? == 0 ]; then
		checkAllMails
		if [ $? == 0 ]; then
			checkKafkaTopic
			if [ $? == 0 ]; then
				echo ""
				echo "all kafka outputs were found!"
				echo "finished test successfully.."
			else
				echo ""
				echo "test failed at checking kafka topic.."
				result=1
			fi
		else
			echo ""
			echo "test failed at checking mails.."
			result=1
		fi
	else
		echo ""
		echo "test failed at checking syslogs.."
		result=1
	fi
else
	echo ""
	echo "test failed at checking outputs.."
	result=1
fi
echo ""
echo "part 2 finished"
sudo kafka_2.12-2.7.0/bin/kafka-server-stop.sh > /dev/null
sudo kafka_2.12-2.7.0/bin/zookeeper-server-stop.sh > /dev/null
sudo rm -r kafka_2.12-2.7.0/
sudo rm -r /tmp/zookeeper
sudo rm -r /tmp/kafka-logs
sudo rm /etc/aminer/kafka-client.conf
exit $result
