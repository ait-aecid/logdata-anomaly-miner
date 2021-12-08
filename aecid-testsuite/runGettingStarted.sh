#!/bin/bash

##################################################################
# Description of the test. Line numbers are also considering starting lines with ```, so they are incremented by one compared to the text itself.
# 1.) Read the first log line between the 4th and 5th ``` in the third line and save it to /var/log/apache2/access.log
# 2.) Link the ApacheAccessLog by running the command between the 5th ```bash and 7th ``` after "$ ".
# 3.) Extract the first aminer command and the CFG_PATH between 9th and 10th ```.
# 4.) Write the config to CFG_PATH from 1st ```yaml to 8th ```.
# 5.) Extract the resulting outputs between 9th and 10th ``` by comparing following lines with the ones from the output:
#     - 6,33 with 2,29
#     - 37,65 with 32,61
# 6.) Write the config to CFG_PATH from 2nd ```yaml to 11th ```.
# 7.) Read 1st ```python to 14th ``` and compare the ApacheAccessModel with the ApacheAccessModel in source/root/etc/aminer/conf-available/generic/ApacheAccessModel.py
# 8.) Write new lines to the access.log from the 4th and 5th line between 21st and 22nd ```.
# 9.) Read the new command without clearing the persisted data from the 2nd line between 23rd and 24th ```. Run the command and compare the lines 4,32 with the output lines 2,30.
# 10.)


##################################################################

BRANCH=main

if [ $# -gt 0 ]
then
BRANCH=$1
fi

sudo chown -R aminer:aminer /var/lib/aminer 2> /dev/null
INPUT_FILE=logdata-anomaly-miner.wiki/Getting-started-\(tutorial\).md
OUT=/tmp/out.txt
OUT2=/tmp/out2.txt
LOG=/var/log/apache2/access.log

# extract the file from the development branch of the wiki project.
# the first ```yaml script is searched for.
git clone https://github.com/ait-aecid/logdata-anomaly-miner.wiki.git 2> /dev/null
cd logdata-anomaly-miner.wiki 2> /dev/null
git checkout $BRANCH > /dev/null 2>&1
cd ..

# create log file (1.)
mkdir -p /var/log/apache2
awk '/^```$/ && ++n == 4, /^```$/ && n++ == 5' < $INPUT_FILE > $LOG
sed -i -n '3p' $LOG

# link the ApacheAccessModel (2.)
awk '/^```bash$/ && ++n == 5, /^```$/' < $INPUT_FILE > $OUT
CMD=$(sed -n '2p' < $OUT)
CMD=${CMD#*$ }
$CMD 2> /dev/null

# load the aminer command. (3.)
awk '/^```$/ && ++n == 9, /^```$/ && n++ == 10' < $INPUT_FILE > $OUT
CMD=$(sed -n '4p' < $OUT)
CMD=${CMD#*$ }
CFG_PATH=/${CMD#*/}

# write the yaml config. (4.)
awk '/^```yaml$/ && ++n == 1, /^```$/' < $INPUT_FILE | sed '/^```/ d' > $CFG_PATH

# extract resulting outputs and compare them. (5.)
OUT1=$(sed -n '6,33p' < $OUT)
OUT2=$(sed -n '37,65p' < $OUT)

$CMD > $OUT &
sleep 5 & wait $!
sudo pkill -x aminer
if [[ $? != 0 ]]; then
	exit_code=1
fi

IN1=$(sed -n '2,29p' < $OUT)
IN2=$(sed -n '33,61p' < $OUT)

if [[ "$OUT1" != "$IN1" ]]; then
  echo "$OUT1"
  echo
  echo "NOT EQUAL WITH (5.)"
  echo
  echo "$IN1"
  echo
  exit_code=1
fi

if [[ "$OUT2" != "$IN2" ]]; then
  echo "$OUT2"
  echo
  echo "NOT EQUAL WITH (5.)"
  echo
  echo "$IN2"
  echo
  exit_code=1
fi

# write the second yaml config (6.)
awk '/^```yaml$/ && ++n == 2, /^```$/' < $INPUT_FILE | sed '/^```/ d' > $CFG_PATH

# compare ApacheAccessModel (7.)
awk '/^```python$/ && ++n == 1, /^```$/' < $INPUT_FILE | sed '/^```/ d' > $OUT
OUT1=$(cat $OUT)
IN1=$(cat ../source/root/etc/aminer/conf-available/generic/ApacheAccessModel.py)

if [[ "$OUT1" != "$IN1" ]]; then
  echo "$OUT1"
  echo
  echo "NOT EQUAL WITH (7.)"
  echo
  echo "$IN1"
  echo
  exit_code=1
fi

# write new loglines. (8.)
awk '/^```$/ && ++n == 21, /^```$/ && n++ == 22' < $INPUT_FILE > $LOG
OUT1=$(sed -n '4,5p' < $LOG)
echo "$OUT1" > $LOG

# read new command (9.)
awk '/^```$/ && ++n == 23, /^```$/ && n++ == 24' < $INPUT_FILE > $OUT
CMD=$(sed -n '2p' < $OUT)
CMD=${CMD#*$ }

OUT1=$(sed -n '4,32p' < $OUT)

sudo $CMD > $OUT &
sleep 5 & wait $!
sudo pkill -x aminer
if [[ $? != 0 ]]; then
	exit_code=1
fi

IN1=$(sed -n '2,30p' < $OUT)

if [[ "$OUT1" != "$IN1" ]]; then
  echo "$OUT1"
  echo
  echo "NOT EQUAL WITH (9.)"
  echo
  echo "$IN1"
  echo
  exit_code=1
fi

exit 1

# test the fifth yaml config.
awk '/^```yaml$/ && ++n == 5, /^```$/' < $INPUT_FILE | sed '/^```/ d' > /tmp/gettingStarted-config.yml
sudo cp /tmp/gettingStarted-config.yml $CFG_PATH
sudo $CMD > /dev/null &
sleep 5 & wait $!
sudo pkill -x aminer
if [[ $? != 0 ]]; then
	exit_code=1
fi

sudo rm -r logdata-anomaly-miner.wiki
rm $OUT
rm $OUT2
sudo rm $CFG_PATH
exit $exit_code
