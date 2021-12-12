#!/bin/bash

##################################################################
# Description of the test. Line numbers are also considering starting lines with ```, so they are incremented by one compared to the text itself.
# TODO: remove line numbers from loglines
# 1.) Write log lines from 4th to 5th ``` into /tmp/access_00 and /tmp/access_01.
# 2.) Read 1st ```python to 6th ``` and compare it with ApacheAccessParsingModel.
# 3.) Run the linking command between 7th and 8th ```.
# 4.) Run the copy command from the 2nd line between 9th and 10th ``` and extract the CFG_PATH from that line.
# 5.) Extract the line between 1st ```yaml and 11th ``` and replace LearnMode: False with it in CFG_PATH.
# 6.) Replace LogResourceList path with "/tmp/access_00" in CFG_PATH.
# 7.) Replace all Parser config lines in CFG_PATH with Parser config lines between 3rd ```yaml and 13th ```.
# 8.) Replace all Input config lines in CFG_PATH with Input config lines between 4th ```yaml and 14th ```.
# 9.) Replace all Analysis config lines in CFG_PATH with Analysis config lines between 5th ```yaml and 15th ```.
# 10.) Replace all EventHandlers config lines in CFG_PATH with EventHandlers config lines between 6th ```yaml and 16th ```.
# 11.) Parse the aminer CMD between 17th and 18th ``` and run it. Check if no error is output by the aminer.
# 12.) Compare the results with the count report between 19th and 20th ``` (without actual numbers and timestamps - replace them with constant values).
# 13.) Run the rm command between 21st and 22nd ```.
# 14.) Replace access_00 with access_01 in CFG_PATH.
# 15.) Replace all Analysis config lines in CFG_PATH with Analysis config lines between 8th ```yaml and 26th ```, run CMD and check if no error is output by the aminer.
# 16.) Change learn_mode: False to learn_mode: True.
# 17.) Replace all Analysis config lines in CFG_PATH with Analysis config lines between 10th ```yaml and 34th ```, run CMD and check if no error is output by the aminer.
# 18.) Replace all Analysis config lines in CFG_PATH with Analysis config lines between 11th ```yaml and 43rd ```, run CMD and check if no error is output by the aminer.
# 19.) Replace all Parser config lines in CFG_PATH with Parser config lines between 13th ```yaml and 53rd ```, run CMD and check if no error is output by the aminer.
# TODO: add the apacheAccessModel to the parser config in 13th ```yaml and 53rd ```.!!!!!!!!!!!!!!!!!!!!!!

# 20.) Replace all Parser config lines in CFG_PATH with Parser config lines between 16th ```yaml and 60th ```, run CMD and check if no error is output by the aminer.
# 21.) Replace all Analysis config lines in CFG_PATH with Analysis config lines between 17th ```yaml and 61st ```, run CMD and check if no error is output by the aminer.
# 22.) Replace all Parser config lines in CFG_PATH with Parser config lines between 19th ```yaml and 69th ```, run CMD and check if no error is output by the aminer.
# 23.) Replace all Analysis config lines in CFG_PATH with Analysis config lines between 20th ```yaml and 70th ```, run CMD and check if no error is output by the aminer.
# 24.) Replace all Parser config lines in CFG_PATH with Parser config lines between 22nd ```yaml and 76th ```, run CMD and check if no error is output by the aminer.
# TODO: add the apacheAccessModel and eximModel to the parser config in 22nd ```yaml and 76th ```.!!!!!!!!!!!!!!!!!!!!!!

# 25.) Replace all Analysis config lines in CFG_PATH with Analysis config lines between 23rd ```yaml and 77th ```, run CMD and check if no error is output by the aminer.
# TODO: replace 2nd ```python with ```yaml.
# TODO: rename MultiSource -> multi_source

# 26.) Write the config between 25th ```yaml and 87th ``` to CFG_PATH, run CMD and check if no error is output by the aminer.
##################################################################

BRANCH=main

if [ $# -gt 0 ]
then
BRANCH=$1
fi

sudo chown -R aminer:aminer /var/lib/aminer 2> /dev/null
INPUT_FILE=logdata-anomaly-miner.wiki/aminer-TryItOut.md
OUT=/tmp/out.txt
LOG1=/tmp/access_00
LOG2=/tmp/access_01

# extract the file from the development branch of the wiki project.
# the second ```python script is searched for.
git clone https://github.com/ait-aecid/logdata-anomaly-miner.wiki.git 2> /dev/null
cd logdata-anomaly-miner.wiki 2> /dev/null
git checkout $BRANCH > /dev/null 2>&1
cd ..

# write access logs (1.)
awk '/^```$/ && ++n == 4, /^```$/ && n++ == 5' < $INPUT_FILE | sed '/^```/ d' > $LOG1
cp $LOG1 $LOG2

# compare ApacheAccessParsingModel (2.)
awk '/^```python$/ && ++n == 1, /^```$/' < $INPUT_FILE | sed '/^```/ d' > $OUT
OUT1=$(cat $OUT)
IN1=$(cat ../source/root/etc/aminer/conf-available/ait-lds/ApacheAccessParsingModel.py)

if [[ "$OUT1" != "$IN1" ]]; then
  echo "$OUT1"
  echo
  echo "NOT EQUAL WITH (2.)"
  echo
  echo "$IN1"
  echo
  exit_code=1
fi

# link available configs (3.)
awk '/^```$/ && ++n == 7, /^```$/ && n++ == 8' < $INPUT_FILE | sed '/^```/ d' > $OUT
CMD=$(cat $OUT)
sudo $CMD > $OUT 2> /dev/null

# copy template config and extract CFG_PATH. (4.)
awk '/^```$/ && ++n == 9, /^```$/ && n++ == 10' < $INPUT_FILE > $OUT
CMD=$(sed -n '2p' < $OUT)
$CMD

IFS=' ' read -ra ADDR <<< "$CMD"
CFG_PATH=$(echo "${ADDR[-1]}")

# replace LearnMode: False with LearnMode: True in CFG_PATH. (5.)
awk '/^```yaml$/ && ++n == 1, /^```$/' < $INPUT_FILE | sed '/^```/ d' > $OUT
OUT1=$(cat $OUT)
sed -i "s/#LearnMode: false/${OUT1}/g" $CFG_PATH
echo "$CFG_PATH"
echo "$OUT1"

# replace LogResourceList file. (6.)
OUT1=$(echo $LOG1)
sed -i "s?file:///var/log/apache2/access.log?file:///${OUT1}?g" $CFG_PATH

# replace parser, input, analysis and event handler config lines (7.-10.)
CFG_BEFORE=$(sed '/^Parser:$/Q' $CFG_PATH)
CFG_PARSER=$(awk '/^Parser:$/,/^Input:$/' < $CFG_PATH)
CFG_PARSER=$(echo "$CFG_PARSER" | sed '$d')
CFG_INPUT=$(awk '/^Input:$/,/^Analysis:$/' < $CFG_PATH)
CFG_INPUT=$(echo "$CFG_INPUT" | sed '$d')
CFG_ANALYSIS=$(awk '/^Analysis:$/,/^EventHandlers:$/' < $CFG_PATH)
CFG_ANALYSIS=$(echo "$CFG_ANALYSIS" | sed '$d')
CFG_EVENT_HANDLERS=$(awk '/^EventHandlers:$/,/^$/' < $CFG_PATH)
CFG_EVENT_HANDLERS=$(echo "$CFG_EVENT_HANDLERS" | sed '$d')

CFG_PARSER=$(awk '/^```yaml$/ && ++n == 3, /^```$/' < $INPUT_FILE | sed '/^```/ d')
CFG_INPUT=$(awk '/^```yaml$/ && ++n == 4, /^```$/' < $INPUT_FILE | sed '/^```/ d')
CFG_ANALYSIS=$(awk '/^```yaml$/ && ++n == 5, /^```$/' < $INPUT_FILE | sed '/^```/ d')
CFG_EVENT_HANDLERS=$(awk '/^```yaml$/ && ++n == 6, /^```$/' < $INPUT_FILE | sed '/^```/ d')

echo "$CFG_BEFORE" > $CFG_PATH
echo "$CFG_PARSER" >> $CFG_PATH
echo "$CFG_INPUT" >> $CFG_PATH
echo "$CFG_ANALYSIS" >> $CFG_PATH
echo "$CFG_EVENT_HANDLERS" >> $CFG_PATH
cat $CFG_PATH
sudo aminer -c "$CFG_PATH"


exit 1

awk '/^```python$/ && ++n == 2, /^```$/' < $INPUT_FILE | sed '/^```/ d' > /tmp/tryItOut-config.yml
# text before comment:
sed -e '/# commented analysis components/,$d' /tmp/tryItOut-config.yml > /tmp/before
# text after commented components:
sed -n -e '/^EventHandlers:$/,$p' /tmp/tryItOut-config.yml > /tmp/after
# commented components
awk '/# commented analysis components$/,/^EventHandlers:$/' < /tmp/tryItOut-config.yml | sed '/^EventHandlers:/ d' | sed '/# commented analysis components/ d' > /tmp/commented
cat /tmp/before > /tmp/tryItOut-config.yml
sed -e 's/#//g' -e 's/ commented analysis components/# commented analysis components/g' /tmp/commented >> /tmp/tryItOut-config.yml
cat /tmp/after >> /tmp/tryItOut-config.yml

sudo aminer --config /tmp/tryItOut-config.yml > /dev/null &
sleep 5 & wait $!
sudo pkill -x aminer
exit_code=$?

rm /tmp/tryItOut-config.yml
rm /tmp/before
rm /tmp/after
rm /tmp/commented
sudo rm -r logdata-anomaly-miner.wiki
exit $exit_code
