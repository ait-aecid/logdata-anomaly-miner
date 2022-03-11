#!/bin/bash

. ./testFunctions.sh

BRANCH=main

if [ $# -gt 0 ]
then
BRANCH=$1
fi

sudo chown -R aminer:aminer /var/lib/aminer 2> /dev/null

CFG_PATH=/etc/aminer/config.yml

# extract the file from the development branch of the wiki project.
# the first ```yaml script is searched for.
git clone https://github.com/ait-aecid/logdata-anomaly-miner.wiki.git 2> /dev/null
cd logdata-anomaly-miner.wiki 2> /dev/null
git checkout $BRANCH > /dev/null 2>&1
cd ..
awk '/^```yaml$/ && ++n == 1, /^```$/' < logdata-anomaly-miner.wiki/HowTo-MissingMatchPathValueDetector.md | sed '/^```/ d' | sudo tee $CFG_PATH > /dev/null

runAminerUntilEnd "sudo aminer --config $CFG_PATH -C" "" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "/dev/null"
exit_code=$?

sudo rm -r logdata-anomaly-miner.wiki
sudo rm $CFG_PATH
exit $exit_code
