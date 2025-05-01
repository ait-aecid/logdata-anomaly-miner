#!/bin/bash

echo localhost | sudo tee /etc/hostname > /dev/null
cd integration
script=$1
sudo chmod +x $script
cntr=0

for var in "$@"
do
	if [[ $cntr -gt 0 ]]; then
    cp "$var" /tmp/"$var"
	fi
	cntr=$(($cntr+1))
done

cp zmq_subscriber.py /tmp

sudo ./$script
exit_code=$?

cntr=0
for var in "$@"
do
	if [[ $cntr -gt 0 ]]; then
    sudo rm /tmp/"$var"
	fi
	cntr=$(($cntr+1))
done

test -e /var/mail/mail && sudo rm -f /var/mail/mail
cd ..
sudo rm /tmp/syslog
sudo rm /tmp/output
sudo rm /tmp/zmq_subscriber.py
test -e /tmp/out && sudo rm /tmp/out
test -e /tmp/auth.log && sudo rm /tmp/auth.log
exit $exit_code
