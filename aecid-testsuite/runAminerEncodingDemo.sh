#!/bin/bash

ERR=/tmp/err.txt
if [[ $1 == *.py ]]; then
    cp $1 /tmp/demo-config.py
    echo "config_properties['Log.Encoding'] = 'latin-1'" >> /tmp/demo-config.py
    sudo chown aminer:aminer /tmp/demo-config.py 2> /dev/null
elif [[ $1 == *.yml ]]; then
    cp $1 /tmp/demo-config.yml
    echo "Log.Encoding: 'latin-1'" >> /tmp/demo-config.yml
    sudo chown aminer:aminer /tmp/demo-config.yml 2> /dev/null
else
    exit 2
fi
sudo chown -R aminer:aminer /tmp/lib 2> /dev/null
sudo chmod +x demo/aminer/aminerDemo.sh
sudo ./demo/aminer/aminerDemo.sh > /dev/null 2> $ERR
exit_code=$?

OUTPUT=$(cat $ERR)
if grep -Fq "Traceback" $ERR; then
	exit_code=1
fi
cat $ERR

sudo rm /tmp/demo-config.py 2> /dev/null
sudo rm /tmp/demo-config.yml 2> /dev/null
sudo rm $ERR
exit $exit_code
