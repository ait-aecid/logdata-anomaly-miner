#!/bin/bash

. ./testFunctions.sh

##################################################################
# Description of the test. Line numbers are also considering starting lines with ```, so they are incremented by one compared to the text itself.
# 1.) Extract the lines between 1st ```yaml and 3rd ``` and store it in CFG_PATH.
# 2.) Replace LogResourceList path with LOG1 in CFG_PATH.
# 3.) Parse the aminer CMD between 4th and 5th ```, replace the CFG_PATH and run it.
# 4.) Compare the first two anomalies with the output between 6th and 7th ``` (without the timestamps)
# 5.) Compare the last anomaly with the output between 8th and 9th ``` (without the timestamps)
# 6.) Parse the cat CMD in the first line between 10th and 11th ```, run it and compare the result with the second line.
# 7.) Extract the lines between 2nd ```yaml and 12th ``` and store it in CFG_PATH.
# 8.) Replace LogResourceList path with LOG2 in CFG_PATH.
# 9.) Parse the aminer CMD between 13th and 14th ```, replace the CFG_PATH and run it.
# 10.) Compare the results of the command with the outputs between 13th and 14th ```.
##################################################################

BRANCH=main

if [ $# -gt 0 ]
then
BRANCH=$1
fi

INPUT_FILE=logdata-anomaly-miner.wiki/HowTo-EntropyDetector.md
OUT=/tmp/out.txt
LOG1=/tmp/entropy_train.log
LOG2=/tmp/entropy_test.log
CFG_PATH=/tmp/config.yml
TMPFILE1=/tmp/tmpfile1
TMPFILE2=/tmp/tmpfile2

# extract the file from the development branch of the wiki project.
# the second ```python script is searched for.
#git clone https://github.com/ait-aecid/logdata-anomaly-miner.wiki.git 2> /dev/null
cd logdata-anomaly-miner.wiki 2> /dev/null
git checkout $BRANCH > /dev/null 2>&1
cp files/entropy_train.log $LOG1
cp files/entropy_test.log $LOG2
cd ..

# extract config (1.)
awk '/^```yaml$/ && ++n == 1, /^```$/' < $INPUT_FILE | sed '/^```/ d' > $CFG_PATH

# replace LogResourceList (2.)
sed "s?file:///home/ubuntu/entropy/entropy_train.log?file:///${LOG1}?g" $CFG_PATH | sudo tee $CFG_PATH > /dev/null

# parse aminer CMD and run it (3.)
awk '/^```$/ && ++n == 4, /^```$/ && n++ == 5' < $INPUT_FILE | sed '/^```/ d' > $OUT
CMD=$(cat $OUT)
IFS='#' read -ra ADDR <<< "$CMD"
CMD="sudo${ADDR[1]}"
CMD=$(sed "s?config.yml?$CFG_PATH?g" <<<"$CMD")
runAminerUntilEnd "$CMD" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
#cat $OUT
OUTPUT=$(cat $OUT)

# compare results (4.)
IN=$(awk '/^```$/ && ++n == 6, /^```$/ && n++ == 7' < $INPUT_FILE | sed '/^```/ d')
i=0
while IFS= read -r line
do
  if [[ $i -ne 22 && $i -ne 24 && $i -ne 50 && $i -ne 52 ]]; then
    echo "$line" >> $TMPFILE1
  fi
  i=$(($i+1))
done <<< "$IN"

i=0
while IFS= read -r line
do
  if [[ $i -ge 76 && $i -ne 98 && $i -ne 100 && $i -ne 126 && $i -ne 128 ]]; then
    echo "$line" >> $TMPFILE2
  fi
  if [[ $i -eq 131 ]]; then
    break
  fi
  i=$(($i+1))
done <<< "$OUTPUT"

cmp --silent $TMPFILE1 $TMPFILE2
res=$?
if [[ $res != 0 ]]; then
  echo "Failed Test in 4."
fi
exit_code=$((exit_code | res))
rm $TMPFILE1
rm $TMPFILE2

# compare last result (5.)
IN=$(awk '/^```$/ && ++n == 8, /^```$/ && n++ == 9' < $INPUT_FILE | sed '/^```/ d')
i=0
while IFS= read -r line
do
  if [[ $i -ne 22 && $i -ne 24 ]]; then
    echo "$line" >> $TMPFILE1
  fi
  i=$(($i+1))
done <<< "$IN"

i=0
while IFS= read -r line
do
  if [[ $i -ge 2082 && $i -ne 2104 && $i -ne 2106 ]]; then
    echo "$line" >> $TMPFILE2
  fi
  if [[ $i -eq 2109 ]]; then
    break
  fi
  i=$(($i+1))
done <<< "$OUTPUT"

cmp --silent $TMPFILE1 $TMPFILE2
res=$?
if [[ $res != 0 ]]; then
  echo "Failed Test in 5."
fi
exit_code=$((exit_code | res))

## compare ApacheAccessParsingModel (2.)
#awk '/^```python$/ && ++n == 1, /^```$/' < $INPUT_FILE | sed '/^```/ d' > $OUT
#OUT1=$(cat $OUT)
#IN1=$(cat ../source/root/etc/aminer/conf-available/ait-lds/ApacheAccessParsingModel.py)
#
#compareStrings "$OUT1" "$IN1" "Failed Test in 2."
#exit_code=$((exit_code | $?))
#
## link available configs (3.)
#awk '/^```$/ && ++n == 7, /^```$/ && n++ == 8' < $INPUT_FILE | sed '/^```/ d' > $OUT
#CMD=$(cat $OUT)
#sudo $CMD > $OUT 2> /dev/null
#
## copy template config and extract CFG_PATH. (4.)
#awk '/^```$/ && ++n == 9, /^```$/ && n++ == 10' < $INPUT_FILE > $OUT
#CMD=$(sed -n '2p' < $OUT)
#$CMD
#
#IFS=' ' read -ra ADDR <<< "$CMD"
#CFG_PATH=$(echo "${ADDR[-1]}")
#
## replace LearnMode: False with LearnMode: True in CFG_PATH. (5.)
#awk '/^```yaml$/ && ++n == 1, /^```$/' < $INPUT_FILE | sed '/^```/ d' > $OUT
#OUT1=$(cat $OUT)
#sed "s/#LearnMode: false/${OUT1}/g" $CFG_PATH | sudo tee $CFG_PATH > /dev/null
#
## replace LogResourceList file. (6.)
#OUT1=$(echo $LOG1)
#sed "s?file:///var/log/apache2/access.log?file:///${OUT1}?g" $CFG_PATH | sudo tee $CFG_PATH > /dev/null
#
## replace parser, input, analysis and event handler config lines (7.-10.)
#CFG_BEFORE=$(sed '/^Parser:$/Q' $CFG_PATH)
#CFG_PARSER=$(awk '/^Parser:$/,/^Input:$/' < $CFG_PATH)
#CFG_PARSER=$(echo "$CFG_PARSER" | sed '$d')
#CFG_INPUT=$(awk '/^Input:$/,/^Analysis:$/' < $CFG_PATH)
#CFG_INPUT=$(echo "$CFG_INPUT" | sed '$d')
#CFG_ANALYSIS=$(awk '/^Analysis:$/,/^EventHandlers:$/' < $CFG_PATH)
#CFG_ANALYSIS=$(echo "$CFG_ANALYSIS" | sed '$d')
#CFG_EVENT_HANDLERS=$(awk '/^EventHandlers:$/,/^$/' < $CFG_PATH)
#CFG_EVENT_HANDLERS=$(echo "$CFG_EVENT_HANDLERS" | sed '$d')
#
#CFG_PARSER=$(awk '/^```yaml$/ && ++n == 3, /^```$/' < $INPUT_FILE | sed '/^```/ d')
#CFG_INPUT=$(awk '/^```yaml$/ && ++n == 4, /^```$/' < $INPUT_FILE | sed '/^```/ d')
#CFG_ANALYSIS=$(awk '/^```yaml$/ && ++n == 5, /^```$/' < $INPUT_FILE | sed '/^```/ d')
## change report_interval so the test does not need to wait 10 seconds
#CFG_ANALYSIS=$(echo "$CFG_ANALYSIS" | sed 's/report_interval: 10/report_interval: 3/g')
#CFG_EVENT_HANDLERS=$(awk '/^```yaml$/ && ++n == 6, /^```$/' < $INPUT_FILE | sed '/^```/ d')
#
#echo "$CFG_BEFORE" | sudo tee $CFG_PATH > /dev/null
#echo "$CFG_PARSER" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_INPUT" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_ANALYSIS" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_EVENT_HANDLERS" | sudo tee -a $CFG_PATH > /dev/null
#
## Parse the aminer CMD and run it. Check if no error is output by the aminer. (11.)
#awk '/^```$/ && ++n == 17, /^```$/ && n++ == 18' < $INPUT_FILE > $OUT
#CMD=$(sed -n '2p' < $OUT)
#runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
#if [[ $? != 0 ]]; then
#	exit_code=1
#fi
#
#testConfigError $OUT "Failed Test in 11."
#exit_code=$((exit_code | $?))
#
## Compare the results with the count report. (12.)
#echo "$(awk '/^{$/ && ++n == 2, /^}$/' < $OUT)" > $OUT # remove NewMatchPathDetector output.
#IN1=$(sed -n '1,7p' < $OUT)
#IN2=$(sed -n '8p' < $OUT)
#IN3=$(sed -n '9p' < $OUT)
#awk '/^```$/ && ++n == 19, /^```$/ && n++ == 20' < $INPUT_FILE | sed '/^```/ d' > $OUT
#OUT1=$(sed -n '1,7p' < $OUT)
#OUT2=$(sed -n '8p' < $OUT)
#OUT3=$(sed -n '9p' < $OUT)
#
#compareStrings "$OUT1" "$IN1" "Failed Test in 12."
#exit_code=$((exit_code | $?))
#
#IFS=':' read -ra ADDR <<< "$IN2"
#IN2="${ADDR[0]}"
#IFS=':' read -ra ADDR <<< "$OUT2"
#OUT2="${ADDR[0]}"
#compareStrings "$OUT2" "$IN2" "Failed Test in 12."
#exit_code=$((exit_code | $?))
#
#IFS=':' read -ra ADDR <<< "$IN3"
#IN3="${ADDR[0]}"
#IFS=':' read -ra ADDR <<< "$OUT3"
#OUT3="${ADDR[0]}"
#compareStrings "$OUT3" "$IN3" "Failed Test in 12."
#exit_code=$((exit_code | $?))
#
## Remove the persisted data. (13.)
#awk '/^```$/ && ++n == 21, /^```$/ && n++ == 22' < $INPUT_FILE > $OUT
#CMD1=$(sed -n '2p' < $OUT)
#$CMD1
#
## Replace the Analysis config and compare the output. (14.)
#CFG_ANALYSIS=$(awk '/^```yaml$/ && ++n == 8, /^```$/' < $INPUT_FILE | sed '/^```/ d')
#
#echo "$CFG_BEFORE" | sudo tee $CFG_PATH > /dev/null
#echo "$CFG_PARSER" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_INPUT" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_ANALYSIS" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_EVENT_HANDLERS" | sudo tee -a $CFG_PATH > /dev/null
#
#sudo rm -r /var/lib/aminer/NewMatchPathValueDetector/accesslog_status 2> /dev/null
#
#runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
#if [[ $? != 0 ]]; then
#	exit_code=1
#fi
#
#echo "$(awk '/^{$/ && ++n == 2, /^}$/' < $OUT)" > $OUT # remove NewMatchPathDetector output.
#IN1=$(sed -n '1,22p' < $OUT)
#IN2=$(sed -n '24,26p' < $OUT)
#
#awk '/^```$/ && ++n == 27, /^```$/ && n++ == 28' < $INPUT_FILE | sed '/^```/ d' > $OUT
#OUT1=$(sed -n '1,22p' < $OUT)
#OUT2=$(sed -n '24,26p' < $OUT)
#compareStrings "$OUT1" "$IN1" "Failed Test in 14."
#exit_code=$((exit_code | $?))
#compareStrings "$OUT2" "$IN2" "Failed Test in 14."
#exit_code=$((exit_code | $?))
#
## Replace the Analysis config and compare the output. (15.)
#CFG_ANALYSIS=$(awk '/^```yaml$/ && ++n == 10, /^```$/' < $INPUT_FILE | sed '/^```/ d')
#
#echo "$CFG_BEFORE" | sudo tee $CFG_PATH > /dev/null
#echo "$CFG_PARSER" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_INPUT" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_ANALYSIS" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_EVENT_HANDLERS" | sudo tee -a $CFG_PATH > /dev/null
#
#runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
#if [[ $? != 0 ]]; then
#	exit_code=1
#fi
#
#testConfigError $OUT "Failed Test in 15."
#exit_code=$((exit_code | $?))
#
## Replace the Analysis config and compare the output. (16.)
#CFG_ANALYSIS=$(awk '/^```yaml$/ && ++n == 11, /^```$/' < $INPUT_FILE | sed '/^```/ d')
#
#echo "$CFG_BEFORE" | sudo tee $CFG_PATH > /dev/null
#echo "$CFG_PARSER" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_INPUT" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_ANALYSIS" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_EVENT_HANDLERS" | sudo tee -a $CFG_PATH > /dev/null
#
#runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
#if [[ $? != 0 ]]; then
#	exit_code=1
#fi
#
#testConfigError $OUT "Failed Test in 16."
#exit_code=$((exit_code | $?))
#
## Replace the Parser config. (17.)
#CFG_PARSER=$(awk '/^```yaml$/ && ++n == 13, /^```$/' < $INPUT_FILE | sed '/^```/ d')
#
#echo "$CFG_BEFORE" | sudo tee $CFG_PATH > /dev/null
#echo "$CFG_PARSER" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_INPUT" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_ANALYSIS" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_EVENT_HANDLERS" | sudo tee -a $CFG_PATH > /dev/null
#
#runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
#if [[ $? != 0 ]]; then
#	exit_code=1
#fi
#
## Replace the Parser config. (18.)
#CFG_PARSER=$(awk '/^```yaml$/ && ++n == 16, /^```$/' < $INPUT_FILE | sed '/^```/ d')
#
#echo "$CFG_BEFORE" | sudo tee $CFG_PATH > /dev/null
#echo "$CFG_PARSER" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_INPUT" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_ANALYSIS" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_EVENT_HANDLERS" | sudo tee -a $CFG_PATH > /dev/null
#
#runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
#if [[ $? != 0 ]]; then
#	exit_code=1
#fi
#
## Replace the Analysis config. (19.)
#CFG_ANALYSIS=$(awk '/^```yaml$/ && ++n == 17, /^```$/' < $INPUT_FILE | sed '/^```/ d')
#
#echo "$CFG_BEFORE" | sudo tee $CFG_PATH > /dev/null
#echo "$CFG_PARSER" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_INPUT" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_ANALYSIS" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_EVENT_HANDLERS" | sudo tee -a $CFG_PATH > /dev/null
#
#runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
#if [[ $? != 0 ]]; then
#	exit_code=1
#fi
#
## Replace the Parser config. (20.)
#CFG_PARSER=$(awk '/^```yaml$/ && ++n == 19, /^```$/' < $INPUT_FILE | sed '/^```/ d')
#
#echo "$CFG_BEFORE" | sudo tee $CFG_PATH > /dev/null
#echo "$CFG_PARSER" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_INPUT" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_ANALYSIS" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_EVENT_HANDLERS" | sudo tee -a $CFG_PATH > /dev/null
#
#runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
#if [[ $? != 0 ]]; then
#	exit_code=1
#fi
#
## Replace the Analysis config. (21.)
#CFG_ANALYSIS=$(awk '/^```yaml$/ && ++n == 20, /^```$/' < $INPUT_FILE | sed '/^```/ d')
#
#echo "$CFG_BEFORE" | sudo tee $CFG_PATH > /dev/null
#echo "$CFG_PARSER" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_INPUT" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_ANALYSIS" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_EVENT_HANDLERS" | sudo tee -a $CFG_PATH > /dev/null
#
#runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
#if [[ $? != 0 ]]; then
#	exit_code=1
#fi
#
## Replace the Parser config. (22.)
#CFG_PARSER=$(awk '/^```yaml$/ && ++n == 22, /^```$/' < $INPUT_FILE | sed '/^```/ d')
#
#echo "$CFG_BEFORE" | sudo tee $CFG_PATH > /dev/null
#echo "$CFG_PARSER" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_INPUT" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_ANALYSIS" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_EVENT_HANDLERS" | sudo tee -a $CFG_PATH > /dev/null
#
#runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
#if [[ $? != 0 ]]; then
#	exit_code=1
#fi
#
## Replace the Analysis config. (23.)
#CFG_ANALYSIS=$(awk '/^```yaml$/ && ++n == 23, /^```$/' < $INPUT_FILE | sed '/^```/ d')
#
#echo "$CFG_BEFORE" | sudo tee $CFG_PATH > /dev/null
#echo "$CFG_PARSER" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_INPUT" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_ANALYSIS" | sudo tee -a $CFG_PATH > /dev/null
#echo "$CFG_EVENT_HANDLERS" | sudo tee -a $CFG_PATH > /dev/null
#
#runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
#if [[ $? != 0 ]]; then
#	exit_code=1
#fi
#
## Run the final configuration. (24.)
#awk '/^```yaml$/ && ++n == 25, /^```$/' < $INPUT_FILE | sed '/^```/ d' | sudo tee $CFG_PATH > /dev/null
#
#runAminerUntilEnd "$CMD -C" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
#if [[ $? != 0 ]]; then
#	exit_code=1
#fi
#
#testConfigError $OUT "Failed Test in 24."
#exit_code=$((exit_code | $?))

rm $OUT
rm $LOG1
rm $LOG2
rm $TMPFILE1
rm $TMPFILE2
#sudo rm -r logdata-anomaly-miner.wiki
exit $exit_code
