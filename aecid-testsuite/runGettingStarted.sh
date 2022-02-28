#!/bin/bash

. ./testFunctions.sh

##################################################################
# Description of the test. Line numbers are also considering starting lines with ```, so they are incremented by one compared to the text itself.
# 1.) Read the first log line between the 4th and 5th ``` in the third line and save it to /var/log/apache2/access.log
# 2.) Link the ApacheAccessLog by running the command between the 5th ```bash and 7th ``` after "$ ".
# 3.) Extract the first aminer command and the CFG_PATH between 9th and 10th ```.
# 4.) Write the config to CFG_PATH from 1st ```yaml to 8th ```.
# 5.) Extract the resulting outputs between 9th and 10th ``` by comparing following lines with the ones from the output:
#     - 6,33 with 2,29
#     - 36,64 with 32,61
# 6.) Compare the outputs between 9th and 10th ``` and the outputs between 19th and 20th ```.
# 7.) Write the config to CFG_PATH from 2nd ```yaml to 11th ```.
# 8.) Read 1st ```python to 14th ``` and compare the ApacheAccessModel with the ApacheAccessModel in source/root/etc/aminer/conf-available/generic/ApacheAccessModel.py
# 9.) Write new lines to the access.log from the 4th and 5th line between 21st and 22nd ```.
# 10.) Read the new command without clearing the persisted data from the 2nd line between 23rd and 24th ```. Run the command and compare the lines 4,32 with the output lines 2,30.
# 11.) Read all log lines between the 27th and 28th ``` and save it to /var/log/apache2/access.log
# 12.) Extract the resulting outputs and CFG_PATH (1st line) between 30th and 31st ``` by comparing following lines with the ones from the output:
#     - 4,31 with 2,29
#     - 34,62 with 33,61
#     - 65,93 with 64,92
#     - 96,124 with 95,123
#     - 127,155 with 126,154
#     - 158,186 with 157,185
#     - 189,217 with 188,216
# 13.) Write the config to CFG_PATH from 5th ```yaml to 29th ```.
# 14.) Set LearnMode to False.
# 15.) Parse the last CMD between 34th and 35th ```.
# 16.) Append the new logline and extract the resulting outputs between 40th and 41st ``` by comparing following lines with the ones from the output:
#     - 4,32 with 2,30
##################################################################

BRANCH=main

if [ $# -gt 0 ]
then
BRANCH=$1
fi

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
OUT2=$(sed -n '36,64p' < $OUT)

runAminerUntilEnd "$CMD -C" "$LOG" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
if [[ $? != 0 ]]; then
	exit_code=1
fi

IN1=$(sed -n '2,29p' < $OUT)
IN2=$(sed -n '33,62p' < $OUT)

compareStrings "$OUT1" "$IN1" "Failed Test in 5."
exit_code=$((exit_code | $?))
compareStrings "$OUT2" "$IN2" "Failed Test in 5."
exit_code=$((exit_code | $?))

# compare the outputs (6.)
awk '/^```$/ && ++n == 9, /^```$/ && n++ == 10' < $INPUT_FILE > $OUT
OUT1=$(sed -n '5,$p' < $OUT)
awk '/^```$/ && ++n == 19, /^```$/ && n++ == 20' < $INPUT_FILE > $OUT
OUT2=$(sed -n '2,$p' < $OUT)

compareStrings "$OUT1" "$OUT2" "Failed Test in 6."
exit_code=$((exit_code | $?))

# write the second yaml config (7.)
awk '/^```yaml$/ && ++n == 2, /^```$/' < $INPUT_FILE | sed '/^```/ d' > $CFG_PATH

# compare ApacheAccessModel (8.)
awk '/^```python$/ && ++n == 1, /^```$/' < $INPUT_FILE | sed '/^```/ d' > $OUT
OUT1=$(cat $OUT)
IN1=$(cat ../source/root/etc/aminer/conf-available/generic/ApacheAccessModel.py)

compareStrings "$OUT1" "$IN1" "Failed Test in 8."
exit_code=$((exit_code | $?))

# write new loglines. (9.)
awk '/^```$/ && ++n == 21, /^```$/ && n++ == 22' < $INPUT_FILE > $LOG
OUT1=$(sed -n '4,5p' < $LOG)
echo "$OUT1" > $LOG

# read new command (10.)
awk '/^```$/ && ++n == 23, /^```$/ && n++ == 24' < $INPUT_FILE > $OUT
CMD=$(sed -n '2p' < $OUT)
CMD=${CMD#*$ }

OUT1=$(sed -n '4,32p' < $OUT)

runAminerUntilEnd "$CMD" "$LOG" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
if [[ $? != 0 ]]; then
	exit_code=1
fi

IN1=$(sed -n '2,30p' < $OUT)

compareStrings "$OUT1" "$IN1" "Failed Test in 10."
exit_code=$((exit_code | $?))

# rewrite access.log (11.)
awk '/^```$/ && ++n == 27, /^```$/ && n++ == 28' < $INPUT_FILE | sed '/^```/ d' > $LOG

# extract resulting outputs and CFG_PATH and compare them. (12.)
awk '/^```$/ && ++n == 30, /^```$/ && n++ == 31' < $INPUT_FILE > $OUT
CMD=$(sed -n '2p' < $OUT)
CMD=${CMD#*$ }
CFG_PATH=/${CMD#*/}

OUT1=$(sed -n '4,31p' < $OUT)
OUT2=$(sed -n '34,62p' < $OUT)
OUT3=$(sed -n '65,93p' < $OUT)
OUT4=$(sed -n '96,124p' < $OUT)
OUT5=$(sed -n '127,155p' < $OUT)
OUT6=$(sed -n '158,186p' < $OUT)
OUT7=$(sed -n '189,217p' < $OUT)

# test the fifth yaml config. (13.)
awk '/^```yaml$/ && ++n == 5, /^```$/' < $INPUT_FILE | sed '/^```/ d' > $CFG_PATH
runAminerUntilEnd "$CMD" "$LOG" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
if [[ $? != 0 ]]; then
	exit_code=1
fi

IN1=$(sed -n '2,29p' < $OUT)
IN2=$(sed -n '33,61p' < $OUT)
IN3=$(sed -n '64,92p' < $OUT)
IN4=$(sed -n '95,123p' < $OUT)
IN5=$(sed -n '126,154p' < $OUT)
IN6=$(sed -n '157,185p' < $OUT)
IN7=$(sed -n '188,216p' < $OUT)

compareStrings "$OUT1" "$IN1" "Failed Test in 13."
exit_code=$((exit_code | $?))
compareStrings "$OUT2" "$IN2" "Failed Test in 13."
exit_code=$((exit_code | $?))
compareStrings "$OUT3" "$IN3" "Failed Test in 13."
exit_code=$((exit_code | $?))
compareStrings "$OUT4" "$IN4" "Failed Test in 13."
exit_code=$((exit_code | $?))
compareStrings "$OUT5" "$IN5" "Failed Test in 13."
exit_code=$((exit_code | $?))
compareStrings "$OUT6" "$IN6" "Failed Test in 13."
exit_code=$((exit_code | $?))
compareStrings "$OUT7" "$IN7" "Failed Test in 13."
exit_code=$((exit_code | $?))

# set LearnModel to False. (14.)
sed -i 's/LearnMode: True/LearnMode: False/g' $CFG_PATH

# read new command (15.)
awk '/^```$/ && ++n == 34, /^```$/ && n++ == 35' < $INPUT_FILE > $OUT
CMD=$(sed -n '2p' < $OUT)
CMD=${CMD#*$ }

# extract logline and resulting outputs and compare them. (16.)
awk '/^```$/ && ++n == 40, /^```$/ && n++ == 41' < $INPUT_FILE > $OUT
OUT1=$(sed -n '32p' < $OUT)
OUT1=$(echo "$OUT1" | sed "s/b'//g")
OUT1=$(echo "$OUT1" | sed "s/'//g")
echo "$OUT1" >> $LOG

OUT1=$(sed -n '4,32p' < $OUT)

runAminerUntilEnd "$CMD" "$LOG" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
if [[ $? != 0 ]]; then
	exit_code=1
fi

IN1=$(sed -n '2,30p' < $OUT)

compareStrings "$OUT1" "$IN1" "Failed Test in 16."
exit_code=$((exit_code | $?))

sudo rm -r logdata-anomaly-miner.wiki
rm $OUT
sudo rm $CFG_PATH
exit $exit_code
