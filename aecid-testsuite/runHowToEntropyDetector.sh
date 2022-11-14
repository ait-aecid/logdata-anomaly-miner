#!/bin/bash

. ./testFunctions.sh

##################################################################
# Description of the test. Line numbers are also considering starting lines with ```, so they are incremented by one compared to the text itself.
# 1.) Extract the lines between 1st ```yaml and 3rd ``` and store it in CFG_PATH.
# 2.) Replace LogResourceList path with LOG1 in CFG_PATH and the report interval of the ParserCount.
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
git clone https://github.com/ait-aecid/logdata-anomaly-miner.wiki.git 2> /dev/null
cd logdata-anomaly-miner.wiki 2> /dev/null
git checkout $BRANCH > /dev/null 2>&1
cp files/entropy_train.log $LOG1
cp files/entropy_test.log $LOG2
cd ..

# extract config (1.)
awk '/^```yaml$/ && ++n == 1, /^```$/' < $INPUT_FILE | sed '/^```/ d' | sudo tee $CFG_PATH > /dev/null

# replace LogResourceList (2.)
sed "s?file:///home/ubuntu/entropy/entropy_train.log?file:///${LOG1}?g" $CFG_PATH | sudo tee $CFG_PATH > /dev/null
sed "s?report_interval: 5?report_interval: 555555555?g" $CFG_PATH | sudo tee $CFG_PATH > /dev/null

# parse aminer CMD and run it (3.)
awk '/^```$/ && ++n == 4, /^```$/ && n++ == 5' < $INPUT_FILE | sed '/^```/ d' > $OUT
CMD=$(cat $OUT)
IFS='#' read -ra ADDR <<< "$CMD"
CMD="sudo${ADDR[1]}"
CMD=$(sed "s?config.yml?$CFG_PATH?g" <<<"$CMD")
runAminerUntilEnd "$CMD" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
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
  cat "$TMPFILE1"
  echo
  echo
  cat "$TMPFILE2"
  exit_code=1
fi
exit_code=$((exit_code | res))
rm $TMPFILE1
rm $TMPFILE2

# parse cat CMD, run it and compare to the second line (6.)
awk '/^```$/ && ++n == 10, /^```$/ && n++ == 11' < $INPUT_FILE | sed '/^```/ d' > $OUT
CMD=$(cat $OUT)
IFS='#' read -ra ADDR <<< "$CMD"
CMD="${ADDR[1]}"
OUTPUT="$(eval sudo $CMD)"
IN="$(tail -n 1 $OUT)"
compareStrings "$OUTPUT" "$IN" "Failed Test in 6."
exit_code=$((exit_code | $?))

# extract second config (7.)
awk '/^```yaml$/ && ++n == 2, /^```$/' < $INPUT_FILE | sed '/^```/ d' | sudo tee $CFG_PATH > /dev/null

# replace LogResourceList (8.)
sed "s?file:///home/ubuntu/demo-detectors/entropy/entropy_test.log?file:///${LOG2}?g" $CFG_PATH | sudo tee $CFG_PATH > /dev/null

# parse aminer CMD and run it (9.)
awk '/^```$/ && ++n == 13, /^```$/ && n++ == 14' < $INPUT_FILE | sed '/^```/ d' > $OUT
CMD=$(cat $OUT)
IFS='#' read -ra ADDR <<< "$CMD"
CMD="sudo${ADDR[1]}"
CMD=$(sed "s?config_test.yml?$CFG_PATH?g" <<<"$CMD")
runAminerUntilEnd "$CMD" "$LOG1" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
OUTPUT=$(head -n 28 $OUT) # skipping ParserCount output from runAminerUntilEndTest.

# compare results (10.)
awk '/^```$/ && ++n == 13, /^```$/ && n++ == 14' < $INPUT_FILE | sed '/^```/ d' > $OUT
IN="$(tail -n +2 $OUT)"

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
  if [[ $i -ne 22 && $i -ne 24 ]]; then
    echo "$line" >> $TMPFILE2
  fi
  i=$(($i+1))
done <<< "$OUTPUT"

cmp --silent $TMPFILE1 $TMPFILE2
res=$?
if [[ $res != 0 ]]; then
  echo "Failed Test in 10."
  cat $TMPFILE1
  echo
  cat $TMPFILE2
fi
exit_code=$((exit_code | res))

rm $OUT
rm $LOG1
rm $LOG2
rm $TMPFILE1
rm $TMPFILE2
sudo rm -r logdata-anomaly-miner.wiki
exit $exit_code
