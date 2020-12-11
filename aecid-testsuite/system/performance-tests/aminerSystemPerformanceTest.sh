#!/bin/bash

#This script should be used to test the performance of the AMiner in different hardware setups or virtual machines with different ressources.

MACHINE_NAME="Acer Aspire 5750g"
CPU_NAME="i7-2630QM"
CPU_Number="0.1"
RAM_Used="32MB"
Persistent_Memory_Type="SSD"

AMINER_PERSISTENCE_PATH=/tmp/lib/aminer/*
t=`date +%d.%m.%Y_%H-%M-%S` 
RESULTS_DIR=/tmp/results_$t
RESULTS_PATH=/tmp/results.csv
LOGFILE=/tmp/syslog
sudo mkdir /tmp/lib 2> /dev/null
sudo mkdir /tmp/lib/aminer 2> /dev/null
sudo chown -R $USER:$USER /tmp/lib/aminer 2> /dev/null
sudo rm -r $AMINER_PERSISTENCE_PATH 2> /dev/null
sudo chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
sudo rm -r $RESULTS_PATH 2> /dev/null
mkdir $RESULTS_DIR

FILE=/tmp/performance-config.py
if ! test -f "$FILE"; then
    echo "$FILE does not exist!"
	exit
fi

if [[ $# -lt 2 ]]; then
	echo "Error, not enough parameters found!"	
	echo "Please run the script with a parameter for the runtime in seconds and a parameter for the description."
	echo "For example: ./aminerSystemPerformanceTest.sh 900 \"Low performance test with many outputs. (./multiplyLogFile.sh 400000 syslog_low_performance_many_outputs-template /tmp/syslog)\""
	exit
fi

before=`date +%s`
waitingTime=$1
description=$2
endTime=$(($before+$waitingTime))
echo ""
echo "calculating the MD5 sum of the logfile.."
MD5=`md5sum $LOGFILE | awk '{ print $1 }'`
#MD5=""
echo "counting the lines of the logfile.."
LINE_NUMBER=`wc -l < $LOGFILE | tr -d "\n"`
#LINE_NUMBER=""

python3 -c "import psutil"
if [ $? -gt 0 ]; then
	sudo pip3 install psutil
fi

echo "Performance test started.."
echo ""

python3 generateSystemLogdata.py $((waitingTime+10)) 2> /tmp/error.log &

#start AMiner
sudo -H -u aminer bash -c 'aminer --Config '$FILE' & #2> /dev/null & #> /tmp/output &'

sleep $waitingTime

touch $RESULTS_PATH
sudo chown -R aminer:aminer $RESULTS_PATH
#stop AMiner and python3
sleep 3 & wait $!
sudo pkill -x aminer
KILL_PID=$!
sleep 3
wait $KILL_PID

sudo chown -R $USER:$USER $RESULTS_PATH 2> /dev/null
printf " in $waitingTime seconds.\nThe source file contains $LINE_NUMBER log lines.\n\nmachine name, CPU name, #CPUs used, RAM used, persistent memory type\n$MACHINE_NAME, $CPU_NAME, $CPU_Number, $RAM_Used, $Persistent_Memory_Type\n\nConfig File,config_$t.py\nMD5-Hash Logfile,$MD5\nTest description,$description\n\n" >> $RESULTS_PATH

mv $RESULTS_PATH $RESULTS_DIR
cp $FILE $RESULTS_DIR/config_$t.py

echo ""
echo "Performance test finished!"
