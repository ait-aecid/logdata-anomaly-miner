#!/bin/bash

BRANCH=main

if [ $# -gt 0 ]
then
BRANCH=$1
fi

sudo chown -R aminer:aminer /var/lib/aminer 2> /dev/null
OUT=/tmp/output.txt

# extract the file from the development branch of the wiki project.
# the first ```yaml script is searched for.
git clone https://github.com/ait-aecid/logdata-anomaly-miner.wiki.git 2> /dev/null
cd logdata-anomaly-miner.wiki 2> /dev/null
git checkout $BRANCH > /dev/null 2>&1
cd ..
# create log file
mkdir -p /var/log/apache2
echo '127.0.0.1 - - [17/May/2021:11:25:14 +0000] "GET / HTTP/1.1" 200 11229 "-" "Wget/1.20.3 (linux-gnu)"' > /var/log/apache2/access.log
# load the aminer command.
awk '/^```$/ && ++n == 9, /^```$/ && n++ == 10' < logdata-anomaly-miner.wiki/Getting-started-\(tutorial\).md > /tmp/gettingStarted-config.yml
CMD=$(sed -n '4p' < /tmp/gettingStarted-config.yml)
CMD=${CMD#*$ }
CFG_PATH=/${CMD#*/}
# test the first yaml config.
awk '/^```yaml$/ && ++n == 1, /^```$/' < logdata-anomaly-miner.wiki/Getting-started-\(tutorial\).md | sed '/^```/ d' > /tmp/gettingStarted-config.yml
sudo cp /tmp/gettingStarted-config.yml $CFG_PATH

$CMD > $OUT &
sleep 5 & wait $!
sudo pkill -x aminer
if [[ $? != 0 ]]; then
	exit_code=1
fi

OUTPUT=$(cat $OUT)
sed "5p;d" $OUT

if [[ "$OUTPUT" != *"$VAR"* ]]; then
  echo "$VAR"
  echo
  exit_code=1
fi

# test the second yaml config.
awk '/^```yaml$/ && ++n == 2, /^```$/' < logdata-anomaly-miner.wiki/Getting-started-\(tutorial\).md | sed '/^```/ d' > /tmp/gettingStarted-config.yml
sudo cp /tmp/gettingStarted-config.yml $CFG_PATH
sudo $CMD > /dev/null &
sleep 5 & wait $!
sudo pkill -x aminer
if [[ $? != 0 ]]; then
	exit_code=1
fi

# test the fifth yaml config.
awk '/^```yaml$/ && ++n == 5, /^```$/' < logdata-anomaly-miner.wiki/Getting-started-\(tutorial\).md | sed '/^```/ d' > /tmp/gettingStarted-config.yml
sudo cp /tmp/gettingStarted-config.yml $CFG_PATH
sudo $CMD > /dev/null &
sleep 5 & wait $!
sudo pkill -x aminer
if [[ $? != 0 ]]; then
	exit_code=1
fi

sudo rm -r logdata-anomaly-miner.wiki
rm /tmp/gettingStarted-config.yml
rm $OUT
sudo rm $CFG_PATH
exit $exit_code
