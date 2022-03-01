#!/bin/bash

#To add more log lines following positions must be changed: main script, checkAllOutputs, isExpectedOutput. The Position is marked with a "ADD HERE" comment.

. ./declarations.sh
NUMBER_OF_LOG_LINES=7
OUT=/tmp/output
SYSLOG=/tmp/syslog
AUTH=/tmp/auth.log

#<<'END'
AMINER_PERSISTENCE_PATH=/tmp/lib/aminer/*
sudo mkdir /tmp/lib 2> /dev/null
sudo mkdir /tmp/lib/aminer 2> /dev/null
sudo chown -R $USER:$USER /tmp/lib/aminer 2> /dev/null
sudo rm -r $AMINER_PERSISTENCE_PATH 2> /dev/null
sudo chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
sudo rm $SYSLOG 2> /dev/null
sudo rm $AUTH 2> /dev/null
sudo rm $OUT 2> /dev/null

echo "Integration test started.."
echo ""

CFG_PATH21=/tmp/config21.py
if ! test -f "$CFG_PATH21"; then
    echo "$CFG_PATH21 does not exist!"
	exit 1
fi
CFG_PATH22=/tmp/config22.py
if ! test -f "$CFG_PATH22"; then
    echo "$CFG_PATH22 does not exist!"
	exit 1
fi

# starting download to reduce wait time
curl $KAFKA_URL --output kafka.tgz 2> /dev/null &
DOWNLOAD_PID=$!

#start aminer
sudo aminer --config $CFG_PATH21 > $OUT &
PID=$!

#Anomaly FixedDataModel HD Repair
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrad") > $SYSLOG
sleep 1
#New Path
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") > $AUTH
sleep 1
#Known Path
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> $SYSLOG
sleep 1
#Anomaly FixedDataModel HD Repair
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrad") >> $AUTH
sleep 1
#Anomaly DateTimeModel
({ date '+%m.%Y %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> $SYSLOG
sleep 1
#Known Path
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> $AUTH
sleep 1
#Known Path
({ date '+%Y-%m-%d %T' && echo 'fedora' && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> $SYSLOG
sleep 1
#Root Home Path
echo 'The Path of the home directory shown by pwd of the user root is: /root' >> $AUTH
sleep 1
#User Home Path
echo 'The Path of the home directory shown by pwd of the user user is: /home/user' >> $SYSLOG
sleep 1
#Guest Home Path
echo 'The Path of the home directory shown by pwd of the user guest is: /home/guest' >> $AUTH

#ADD HERE

#stop aminer
sleep 3
sudo pkill -x aminer
wait $PID

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
sudo rm $SYSLOG 2> /dev/null
sudo rm $AUTH 2> /dev/null
sudo rm $OUT 2> /dev/null
sudo cp ../unit/data/kafka-client.conf /etc/aminer/kafka-client.conf
wait $DOWNLOAD_PID
tar xvf kafka.tgz > /dev/null
rm kafka.tgz
$KAFKA_VERSIONSTRING/bin/zookeeper-server-start.sh $KAFKA_VERSIONSTRING/config/zookeeper.properties > /dev/null &
sleep 1
$KAFKA_VERSIONSTRING/bin/kafka-server-start.sh $KAFKA_VERSIONSTRING/config/server.properties > /dev/null &
sleep 1

COUNTER=0

#start aminer
sleep 10
sudo aminer --config $CFG_PATH22 -f > $OUT &
PID=$!
sleep 8

#Anomaly FixedDataModel HD Repair
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrad") > $SYSLOG
sleep 2
#New Path
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") > $AUTH
sleep 2
#Known Path
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> $SYSLOG
sleep 2
#Anomaly FixedDataModel HD Repair
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrad") >> $AUTH
sleep 2
#Anomaly DateTimeModel
({ date '+%m.%Y %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> $SYSLOG
sleep 2
#Known Path
({ date '+%Y-%m-%d %T' && cat /etc/hostname && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> $AUTH
sleep 2
#Known Path
({ date '+%Y-%m-%d %T' && echo 'fedora' && id -u -n | tr -d "\n" && echo :; } | tr "\n" " " && echo "System rebooted for hard disk upgrade") >> $SYSLOG
sleep 2
#Root Home Path
echo 'The Path of the home directory shown by pwd of the user root is: /root' >> $AUTH
sleep 2
#User Home Path
echo 'The Path of the home directory shown by pwd of the user user is: /home/user' >> $SYSLOG
sleep 2
#Guest Home Path
echo 'The Path of the home directory shown by pwd of the user guest is: /home/guest' >> $AUTH

#ADD HERE

#stop aminer
sleep 10
sudo pkill -x aminer
wait $PID
sleep 3 # leave the kafka handler some time.

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
sudo $KAFKA_VERSIONSTRING/bin/kafka-server-stop.sh > /dev/null
sudo $KAFKA_VERSIONSTRING/bin/zookeeper-server-stop.sh > /dev/null
sudo rm -r $KAFKA_VERSIONSTRING/
sudo rm -r /tmp/zookeeper
sudo rm -r /tmp/kafka-logs
sudo rm /etc/aminer/kafka-client.conf
exit $result
