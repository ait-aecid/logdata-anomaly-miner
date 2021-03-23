#!/bin/bash

sudo mkdir /tmp/lib 2> /dev/null
sudo mkdir /tmp/lib/aminer 2> /dev/null
sudo chown -R $USER:$USER /tmp/lib/aminer 2> /dev/null
sudo rm -r /tmp/lib/aminer/* 2> /dev/null
sudo mkdir /tmp/lib/aminer/log 2> /dev/null
sudo chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
sudo rm /tmp/syslog 2> /dev/null

echo "Demo started.."
echo ""

FILE=$1
if ! test -f "$FILE"; then
  echo "$FILE does not exist!"
	exit 1
fi

#start aminer
sudo aminer --config "$FILE" &

#stop aminer
sleep 10 & wait $!
sudo pkill -x aminer
KILL_PID=$!
sleep 3
wait $KILL_PID
