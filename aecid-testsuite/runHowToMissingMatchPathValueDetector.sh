#!/bin/bash

BRANCH=main

if [ $# -gt 0 ]
then
BRANCH=$1
fi

sudo chown -R aminer:aminer /var/lib/aminer 2> /dev/null

CONFIG=/tmp/config.yml

# extract the file from the development branch of the wiki project.
# the first ```yaml script is searched for.
git clone https://github.com/ait-aecid/logdata-anomaly-miner.wiki.git 2> /dev/null
cd logdata-anomaly-miner.wiki 2> /dev/null
git checkout $BRANCH > /dev/null 2>&1
cd ..
awk '/^```yaml$/ && ++n == 1, /^```$/' < logdata-anomaly-miner.wiki/HowTo-MissingMatchPathValueDetector.md | sed '/^```/ d' > $CONFIG

sudo aminer --config $CONFIG > /dev/null &
sleep 5 & wait $!
sudo pkill -x aminer
exit_code=$?

sudo rm -r logdata-anomaly-miner.wiki
#rm $CONFIG
exit $exit_code
