#!/bin/bash

. ./testFunctions.sh

##################################################################
# NOTE: not all outputs were compared! If one output fails all other outputs should be corrected as well!

# Description of the test. Line numbers are also considering starting lines with ```, so they are incremented by one compared to the text itself.
# 1.) Write the config to CFG_PATH from 1st ```yaml to 1st ```.
# 2.) Replace LogResourceList path with LOG in CFG_PATH. Lower the check_interval and realert_interval to proper values.
# 3.) Write log lines from 4th to 5th ``` into LOG and LOG_ALICE and LOG_BOB.
# 4.) Extract the first aminer command between 6th and 7th ```, replace the CFG_PATH and run it.
# 5.) Compare the result with the output between 6th and 7th ```.
# 6.) Extract the CMD between 8th and 9th ```, run it and compare the results to the output.
# 7.) Extract the CMD between 10th and 11th ```, run it and compare the results to the output.
# 8.) Set LearnMode: False in CFG_PATH
# 9.) Extract the second aminer command between 16th and 17th ``` and run it in background.
# 10.) Write LOG_ALICE and LOG_BOB to LOG simultaneously, wait for WAIT_TIME. Repeat 5 times.
# 11.) Compare the results with the outputs between between 20th and 21st ```.
# 12.) Write LOG_BOB to LOG and wait until realert_interval is over and compare the results with the outputs between between 24th and 25th ```.
# 13.) Extract the CMD between 35th and 36th ```, run it and compare the results to the output.
##################################################################

BRANCH=main

if [ $# -gt 0 ]
then
BRANCH=$1
fi

INPUT_FILE=logdata-anomaly-miner.wiki/HowTo-MissingMatchPathValueDetector.md
OUT=/tmp/out.txt
OUT_AMINER=/tmp/aminer_output.txt
LOG=/tmp/access.log
CFG_PATH=/tmp/config.yml

# extract the file from the development branch of the wiki project.
# the first ```yaml script is searched for.
git clone https://github.com/ait-aecid/logdata-anomaly-miner.wiki.git 2> /dev/null
cd logdata-anomaly-miner.wiki 2> /dev/null
git checkout $BRANCH > /dev/null 2>&1
cd ..
sudo rm -rf /var/lib/aminer/*
exit_code=0

# write config (1.)
awk '/^```yaml$/ && ++n == 1, /^```$/' < $INPUT_FILE | sed '/^```/ d' > $CFG_PATH

# adapt config (2.)
sed "s?file:///var/log/apache2/access.log?file:///${LOG}?g" $CFG_PATH | sudo tee $CFG_PATH > /dev/null
echo "Core.PersistencePeriod: 1" >> $CFG_PATH

# write log lines (3.)
awk '/^```$/ && ++n == 4, /^```$/ && n++ == 5' < $INPUT_FILE | sed '/^```/ d' > $OUT
LOG_ALICE="$(sed -n '2p' < $OUT)"
LOG_BOB="${LOG_ALICE/alice/bob}"
echo "$LOG_ALICE" > $LOG
# extract and run aminer command (4.)
awk '/^```$/ && ++n == 6, /^```$/ && n++ == 7' < $INPUT_FILE | sed '/^```/ d' > $OUT
CMD=$(sed -n '1p' < $OUT)
CMD=${CMD#*$ }
OLD_CFG_PATH=/${CMD#*/}
AMINER_CMD="${CMD/"$OLD_CFG_PATH"/"$CFG_PATH"}"

# $CMD > $OUT_AMINER &
$AMINER_CMD > $OUT_AMINER &
PID=$!
sleep 8

# compare results (5.)
IN=$(tail -n +2 $OUT)
OUTPUT=$(cat $OUT_AMINER)
compareStrings "$IN" "$OUTPUT" "Failed Test in 5."
exit_code=$((exit_code | $?))

# extract and run CMD and compare output (6.)
awk '/^```$/ && ++n == 8, /^```$/ && n++ == 9' < $INPUT_FILE | sed '/^```/ d' > $OUT
CMD="$(sed -n '1p' < $OUT)"
IFS='$' read -ra ADDR <<< "$CMD"
CMD="${ADDR[1]}"
OUTPUT=$($CMD)
IN="$(sed -n '2p' < $OUT)"
compareStrings "$IN" "$OUTPUT" "Failed Test in 6."
exit_code=$((exit_code | $?))

# extract and run CMD and compare output (7.)
#awk '/^```$/ && ++n == 10, /^```$/ && n++ == 11' < $INPUT_FILE | sed '/^```/ d' > $OUT
#CMD="$(sed -n '1p' < $OUT)"
#IFS='$' read -ra ADDR <<< "$CMD"
#CMD="${ADDR[1]}"
#OUTPUT=$($CMD)
#IN="$(sed -n '2p' < $OUT)"
#compareStrings "$IN" "$OUTPUT" "Failed Test in 7."
#exit_code=$((exit_code | $?))

sudo pkill -x aminer
wait $PID

# set LearnMode False (8.)
sed "s/LearnMode: True/LearnMode: False/g" $CFG_PATH | sudo tee $CFG_PATH > /dev/null

# run aminer CMD (9.)
rm $LOG
$AMINER_CMD > $OUT_AMINER &
PID=$!

# write log lines (10.)
cat <<EOT > $LOG
::1 - - [18/Jul/2020:20:28:01 +0000] "GET / HTTP/1.1" 200 11012 "-" "alice"
::1 - - [18/Jul/2020:20:28:02 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:03 +0000] "GET / HTTP/1.1" 200 11012 "-" "alice"
::1 - - [18/Jul/2020:20:28:04 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:05 +0000] "GET / HTTP/1.1" 200 11012 "-" "alice"
::1 - - [18/Jul/2020:20:28:06 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:07 +0000] "GET / HTTP/1.1" 200 11012 "-" "alice"
::1 - - [18/Jul/2020:20:28:08 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:09 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:10 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:11 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:12 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:13 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
EOT

sleep 8

# compare results (11.)
awk '/^```$/ && ++n == 20, /^```$/ && n++ == 21' < $INPUT_FILE | sed '/^```/ d' > $OUT
IN=$(tail -n +2 $OUT)
OUTPUT=$(cat $OUT_AMINER)
compareStrings "$IN" "$OUTPUT" "Failed Test in 11."
exit_code=$((exit_code | $?))

# add data and compare results (12.)
cat <<EOT > $LOG
::1 - - [18/Jul/2020:20:28:14 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:15 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:16 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:17 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:18 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:19 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:20 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:21 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:22 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:23 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:24 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:25 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:26 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:27 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:28 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:29 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:30 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:31 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:32 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:33 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:34 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:35 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:36 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:37 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:38 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:39 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:40 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:41 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:42 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
::1 - - [18/Jul/2020:20:28:43 +0000] "GET / HTTP/1.1" 200 11012 "-" "bob"
EOT

sleep 2

awk '/^```$/ && ++n == 24, /^```$/ && n++ == 25' < $INPUT_FILE | sed '/^```/ d' > $OUT
IN=$(cat $OUT)
OUTPUT=$(tail -n 4 $OUT_AMINER)
compareStrings "$IN" "$OUTPUT" "Failed Test in 12."
exit_code=$((exit_code | $?))

# extract command, run it and compare results (13.)
awk '/^```$/ && ++n == 35, /^```$/ && n++ == 36' < $INPUT_FILE | sed '/^```/ d' > $OUT
CMD="$(sed -n '1p' < $OUT)"
IFS='$' read -ra ADDR <<< "$CMD"
CMD="${ADDR[1]}"
OUTPUT=$($CMD)
IN="$(sed -n '2p' < $OUT)"
compareStrings "$IN" "$OUTPUT" "Failed Test in 13."
exit_code=$((exit_code | $?))

sudo pkill -x aminer
wait $PID

sudo rm -r logdata-anomaly-miner.wiki
rm $CFG_PATH
rm $OUT
rm $OUT_AMINER
rm $LOG
exit $exit_code
