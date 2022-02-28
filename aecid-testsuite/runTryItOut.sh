#!/bin/bash

. ./testFunctions.sh

##################################################################
# Description of the test. Line numbers are also considering starting lines with ```, so they are incremented by one compared to the text itself.
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
# 13.) Run the rm command between 21st and 22nd ``` to remove the persisted data.
# 14.) Replace all Analysis config lines in CFG_PATH with Analysis config lines between 8th ```yaml and 26th ```, run CMD and check if no
# error is output by the aminer by comparing the output with the lines between 27th and 28th ```.
# 15.) Replace all Analysis config lines in CFG_PATH with Analysis config lines between 10th ```yaml and 34th ```, run CMD and check if no error is output by the aminer.
# 16.) Replace all Analysis config lines in CFG_PATH with Analysis config lines between 11th ```yaml and 43rd ```, run CMD and check if no error is output by the aminer.
# 17.) Replace all Parser config lines in CFG_PATH with Parser config lines between 13th ```yaml and 53rd ```, run CMD and check if no error is output by the aminer.
# 18.) Replace all Parser config lines in CFG_PATH with Parser config lines between 16th ```yaml and 60th ```, run CMD and check if no error is output by the aminer.
# 19.) Replace all Analysis config lines in CFG_PATH with Analysis config lines between 17th ```yaml and 61st ```, run CMD and check if no error is output by the aminer.
# 20.) Replace all Parser config lines in CFG_PATH with Parser config lines between 19th ```yaml and 69th ```, run CMD and check if no error is output by the aminer.
# 21.) Replace all Analysis config lines in CFG_PATH with Analysis config lines between 20th ```yaml and 70th ```, run CMD and check if no error is output by the aminer.
# 22.) Replace all Parser config lines in CFG_PATH with Parser config lines between 22nd ```yaml and 76th ```, run CMD and check if no error is output by the aminer.
# 23.) Replace all Analysis config lines in CFG_PATH with Analysis config lines between 23rd ```yaml and 77th ```, run CMD and check if no error is output by the aminer.
# 24.) Write the config between 25th ```yaml and 87th ``` to CFG_PATH, run CMD and check if no error is output by the aminer.
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

# replace /etc/aminer/config.yml (0.)
sed -i 's?/etc/aminer/config.yml?/etc/aminer/tryItOutConfig.yml?g' $INPUT_FILE
sudo chown -R $USER:$USER /etc/aminer
ls -la ./
ls -la /tmp

# write access logs (1.)
awk '/^```$/ && ++n == 4, /^```$/ && n++ == 5' < $INPUT_FILE | sed '/^```/ d' > $LOG1
cp $LOG1 $LOG2

# compare ApacheAccessParsingModel (2.)
awk '/^```python$/ && ++n == 1, /^```$/' < $INPUT_FILE | sed '/^```/ d' > $OUT
OUT1=$(cat $OUT)
IN1=$(cat ../source/root/etc/aminer/conf-available/ait-lds/ApacheAccessParsingModel.py)

compareStrings "$OUT1" "$IN1" "Failed Test in 2."
exit_code=$((exit_code | $?))

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
# change report_interval so the test does not need to wait 10 seconds
CFG_ANALYSIS=$(echo "$CFG_ANALYSIS" | sed 's/report_interval: 10/report_interval: 3/g')
CFG_EVENT_HANDLERS=$(awk '/^```yaml$/ && ++n == 6, /^```$/' < $INPUT_FILE | sed '/^```/ d')

echo "$CFG_BEFORE" > $CFG_PATH
echo "$CFG_PARSER" >> $CFG_PATH
echo "$CFG_INPUT" >> $CFG_PATH
echo "$CFG_ANALYSIS" >> $CFG_PATH
echo "$CFG_EVENT_HANDLERS" >> $CFG_PATH
#cat $CFG_PATH

# Parse the aminer CMD and run it. Check if no error is output by the aminer. (11.)
awk '/^```$/ && ++n == 17, /^```$/ && n++ == 18' < $INPUT_FILE > $OUT
CMD=$(sed -n '2p' < $OUT)
runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
if [[ $? != 0 ]]; then
	exit_code=1
fi

testConfigError $OUT "Failed Test in 11."
exit_code=$((exit_code | $?))

# Compare the results with the count report. (12.)
echo "$(awk '/^{$/ && ++n == 2, /^}$/' < $OUT)" > $OUT # remove NewMatchPathDetector output.
IN1=$(sed -n '1,7p' < $OUT)
IN2=$(sed -n '8p' < $OUT)
IN3=$(sed -n '9p' < $OUT)
awk '/^```$/ && ++n == 19, /^```$/ && n++ == 20' < $INPUT_FILE | sed '/^```/ d' > $OUT
OUT1=$(sed -n '1,7p' < $OUT)
OUT2=$(sed -n '8p' < $OUT)
OUT3=$(sed -n '9p' < $OUT)

compareStrings "$OUT1" "$IN1" "Failed Test in 12."
exit_code=$((exit_code | $?))

IFS=':' read -ra ADDR <<< "$IN2"
IN2="${ADDR[0]}"
IFS=':' read -ra ADDR <<< "$OUT2"
OUT2="${ADDR[0]}"
compareStrings "$OUT2" "$IN2" "Failed Test in 12."
exit_code=$((exit_code | $?))

IFS=':' read -ra ADDR <<< "$IN3"
IN3="${ADDR[0]}"
IFS=':' read -ra ADDR <<< "$OUT3"
OUT3="${ADDR[0]}"
compareStrings "$OUT3" "$IN3" "Failed Test in 12."
exit_code=$((exit_code | $?))

# Remove the persisted data. (13.)
awk '/^```$/ && ++n == 21, /^```$/ && n++ == 22' < $INPUT_FILE > $OUT
CMD1=$(sed -n '2p' < $OUT)
$CMD1

# Replace the Analysis config and compare the output. (14.)
CFG_ANALYSIS=$(awk '/^```yaml$/ && ++n == 8, /^```$/' < $INPUT_FILE | sed '/^```/ d')

echo "$CFG_BEFORE" > $CFG_PATH
echo "$CFG_PARSER" >> $CFG_PATH
echo "$CFG_INPUT" >> $CFG_PATH
echo "$CFG_ANALYSIS" >> $CFG_PATH
echo "$CFG_EVENT_HANDLERS" >> $CFG_PATH

sudo rm -r /var/lib/aminer/NewMatchPathValueDetector/accesslog_status 2> /dev/null

runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
if [[ $? != 0 ]]; then
	exit_code=1
fi

echo "$(awk '/^{$/ && ++n == 2, /^}$/' < $OUT)" > $OUT # remove NewMatchPathDetector output.
IN1=$(sed -n '1,22p' < $OUT)
IN2=$(sed -n '24,26p' < $OUT)

awk '/^```$/ && ++n == 27, /^```$/ && n++ == 28' < $INPUT_FILE | sed '/^```/ d' > $OUT
OUT1=$(sed -n '1,22p' < $OUT)
OUT2=$(sed -n '24,26p' < $OUT)
compareStrings "$OUT1" "$IN1" "Failed Test in 14."
exit_code=$((exit_code | $?))
compareStrings "$OUT2" "$IN2" "Failed Test in 14."
exit_code=$((exit_code | $?))

# Replace the Analysis config and compare the output. (15.)
CFG_ANALYSIS=$(awk '/^```yaml$/ && ++n == 10, /^```$/' < $INPUT_FILE | sed '/^```/ d')

echo "$CFG_BEFORE" > $CFG_PATH
echo "$CFG_PARSER" >> $CFG_PATH
echo "$CFG_INPUT" >> $CFG_PATH
echo "$CFG_ANALYSIS" >> $CFG_PATH
echo "$CFG_EVENT_HANDLERS" >> $CFG_PATH

runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
if [[ $? != 0 ]]; then
	exit_code=1
fi

testConfigError $OUT "Failed Test in 15."
exit_code=$((exit_code | $?))

# Replace the Analysis config and compare the output. (16.)
CFG_ANALYSIS=$(awk '/^```yaml$/ && ++n == 11, /^```$/' < $INPUT_FILE | sed '/^```/ d')

echo "$CFG_BEFORE" > $CFG_PATH
echo "$CFG_PARSER" >> $CFG_PATH
echo "$CFG_INPUT" >> $CFG_PATH
echo "$CFG_ANALYSIS" >> $CFG_PATH
echo "$CFG_EVENT_HANDLERS" >> $CFG_PATH

runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
if [[ $? != 0 ]]; then
	exit_code=1
fi

testConfigError $OUT "Failed Test in 16."
exit_code=$((exit_code | $?))

# Replace the Parser config. (17.)
CFG_PARSER=$(awk '/^```yaml$/ && ++n == 13, /^```$/' < $INPUT_FILE | sed '/^```/ d')

echo "$CFG_BEFORE" > $CFG_PATH
echo "$CFG_PARSER" >> $CFG_PATH
echo "$CFG_INPUT" >> $CFG_PATH
echo "$CFG_ANALYSIS" >> $CFG_PATH
echo "$CFG_EVENT_HANDLERS" >> $CFG_PATH

runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
if [[ $? != 0 ]]; then
	exit_code=1
fi

# Replace the Parser config. (18.)
CFG_PARSER=$(awk '/^```yaml$/ && ++n == 16, /^```$/' < $INPUT_FILE | sed '/^```/ d')

echo "$CFG_BEFORE" > $CFG_PATH
echo "$CFG_PARSER" >> $CFG_PATH
echo "$CFG_INPUT" >> $CFG_PATH
echo "$CFG_ANALYSIS" >> $CFG_PATH
echo "$CFG_EVENT_HANDLERS" >> $CFG_PATH

runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
if [[ $? != 0 ]]; then
	exit_code=1
fi

# Replace the Analysis config. (19.)
CFG_ANALYSIS=$(awk '/^```yaml$/ && ++n == 17, /^```$/' < $INPUT_FILE | sed '/^```/ d')

echo "$CFG_BEFORE" > $CFG_PATH
echo "$CFG_PARSER" >> $CFG_PATH
echo "$CFG_INPUT" >> $CFG_PATH
echo "$CFG_ANALYSIS" >> $CFG_PATH
echo "$CFG_EVENT_HANDLERS" >> $CFG_PATH

runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
if [[ $? != 0 ]]; then
	exit_code=1
fi

# Replace the Parser config. (20.)
CFG_PARSER=$(awk '/^```yaml$/ && ++n == 19, /^```$/' < $INPUT_FILE | sed '/^```/ d')

echo "$CFG_BEFORE" > $CFG_PATH
echo "$CFG_PARSER" >> $CFG_PATH
echo "$CFG_INPUT" >> $CFG_PATH
echo "$CFG_ANALYSIS" >> $CFG_PATH
echo "$CFG_EVENT_HANDLERS" >> $CFG_PATH

runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
if [[ $? != 0 ]]; then
	exit_code=1
fi

# Replace the Analysis config. (21.)
CFG_ANALYSIS=$(awk '/^```yaml$/ && ++n == 20, /^```$/' < $INPUT_FILE | sed '/^```/ d')

echo "$CFG_BEFORE" > $CFG_PATH
echo "$CFG_PARSER" >> $CFG_PATH
echo "$CFG_INPUT" >> $CFG_PATH
echo "$CFG_ANALYSIS" >> $CFG_PATH
echo "$CFG_EVENT_HANDLERS" >> $CFG_PATH

runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
if [[ $? != 0 ]]; then
	exit_code=1
fi

# Replace the Parser config. (22.)
CFG_PARSER=$(awk '/^```yaml$/ && ++n == 22, /^```$/' < $INPUT_FILE | sed '/^```/ d')

echo "$CFG_BEFORE" > $CFG_PATH
echo "$CFG_PARSER" >> $CFG_PATH
echo "$CFG_INPUT" >> $CFG_PATH
echo "$CFG_ANALYSIS" >> $CFG_PATH
echo "$CFG_EVENT_HANDLERS" >> $CFG_PATH

runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
if [[ $? != 0 ]]; then
	exit_code=1
fi

# Replace the Analysis config. (23.)
CFG_ANALYSIS=$(awk '/^```yaml$/ && ++n == 23, /^```$/' < $INPUT_FILE | sed '/^```/ d')

echo "$CFG_BEFORE" > $CFG_PATH
echo "$CFG_PARSER" >> $CFG_PATH
echo "$CFG_INPUT" >> $CFG_PATH
echo "$CFG_ANALYSIS" >> $CFG_PATH
echo "$CFG_EVENT_HANDLERS" >> $CFG_PATH

runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
if [[ $? != 0 ]]; then
	exit_code=1
fi

# Run the final configuration. (24.)
awk '/^```yaml$/ && ++n == 25, /^```$/' < $INPUT_FILE | sed '/^```/ d' > $CFG_PATH

runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
if [[ $? != 0 ]]; then
	exit_code=1
fi

testConfigError $OUT "Failed Test in 24."
exit_code=$((exit_code | $?))

rm $OUT
rm $LOG1
rm $LOG2
sudo rm -r logdata-anomaly-miner.wiki
exit $exit_code
