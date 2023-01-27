#!/bin/bash

. ./testFunctions.sh

##################################################################
# Description of the test. Line numbers are also considering starting lines with ```, so they are incremented by one compared to the text itself.
# 1.) Read the log lines between the 2nd and 3rd ``` and save it to /tmp/access.log (LOG)
# 2.) Read 2nd ```bash and 3rd ```, extract CMD from the first line after # , run CMD and compare the output with the 2nd to 4th line of the previous output.
# 3.) Read commands between 3rd ```bash and 5th ```, get the CMD after # and check if aminer_install.sh exists and is executable.
# 4.) Read the CMD between 4th ```bash and 6th ``` and get the CMD after # .
# 5.) Replace the path in the second string with the current directory and run the CMD.
# 6.) Read the CMD between 5th ```bash and 7th ```, get the CMD after #  and run it.
# 7.) Read the CMD between 6th ```bash and 8th ```, get the CMD after #  and run it.
# 8.) Read between 1st ```yaml and 9th ``` and store it in CFG_PATH.
# 9.) Read CFG_PATH, replace the line with json: True and compare it with the 1st ```yaml in Getting-started-(tutorial).md.
# 10.) Read 7th ```bash and 10th ```. Extract CMD in first line and run it as sudo.
# 11.) Compare the outputs (replace lines with timestamps and dates).
# 12.) Read 1st ```python and 12th ``` and write it to SEQ_DET.
# 13.) Read 2nd ```yaml and 13th ``` and write it at 18th line in CFG_PATH.
# 14.) Check if line between 15th and 16th ``` can be found in /usr/lib/logdata-anomaly-miner/aminer/schemas/normalisation/AnalysisNormalisationSchema.py
# 15.) Add code between 18th and 19th ``` to /usr/lib/logdata-anomaly-miner/aminer/schemas/validation/AnalysisValidationSchema.py
# 16.) Add 2nd ```python and 21st ``` to the YML_CONFIG.
# 17.) Run aminer CMD and check if the output contains "Detector template received a log atom!" times the number of log lines.
# 18.) Read 3rd ```python and 24th ``` and replace the receive_atom method in the SEQ_DET.
# 19.) Run aminer CMD and check if the output contains data between 25th and 26th ```.
# 20.) Read 4th ```python and 27th ``` and replace the receive_atom method in the SEQ_DET.
# 21.) Run aminer CMD and check if the output is the same as between 28th and 29th ```.
# 22.) Read 5th ```python and 30th ``` and replace the receive_atom method in the SEQ_DET.
# 23.) Replace Analysis in CFG_PATH with the config between 3rd ```yaml and 31st ```.
# 24.) Run aminer CMD and check if the output is the same as between 32nd and 33th ```.
# 25.) Add code between 34th and 35th ``` in the __init__ method.
# 26.) Read 6th ```python and 36th ``` and replace the receive_atom method in the SEQ_DET.
# 27.) Run aminer CMD and check if the output is the same as between 37th and 38th ```.
# 28.) Read 7th ```python and 39th ``` and replace the receive_atom method in the SEQ_DET.
# 29.) Add lines between 14th ```bash and 42nd ``` to the LOG.
# 30.) Run aminer CMD and check if the output is the same as between 40th and 41st ``` plus the text between 43th and 44th ```.
# 31.) Read 8th ```python and 45th ``` and replace the receive_atom method in the SEQ_DET.
# 32.) Compare the output with the json between 1st ```json and 46th ```.
# 33.) Replace the do_persist method with the code between 9th ```python and 47th ```.
# 34.) Run the CMD in the first line between 15th ```bash and 48th ``` and compare the output with the second line.
##################################################################

BRANCH=main

if [ $# -gt 0 ]
then
BRANCH=$1
fi

sudo chown -R aminer:aminer /var/lib/aminer 2> /dev/null
INPUT=logdata-anomaly-miner.wiki/HowTo-Create-your-own-SequenceDetector.md
SRC_FILE=logdata-anomaly-miner.wiki/HowTo-Create-your-own-SequenceDetector.md
VAL_SCHEMA=/usr/lib/logdata-anomaly-miner/aminer/schemas/validation/AnalysisValidationSchema.py
TMP_VAL_SCHEMA=/tmp/AnalysisValidationSchema.py
NOR_SCHEMA=/usr/lib/logdata-anomaly-miner/aminer/schemas/normalisation/AnalysisNormalisationSchema.py
OUT=/tmp/out.txt
YML_CONFIG=/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py
TMP_YML_CONFIG=/tmp/YamlConfig.py
TMP_SCHEMA=/tmp/schema.py
SEQ_DET=/usr/lib/logdata-anomaly-miner/aminer/analysis/SequenceDetector.py
TMP_SEQ_DET=/tmp/SequenceDetector.py
CFG_PATH=/etc/aminer/config.yml
LOG=/tmp/access.log

# extract the file from the development branch of the wiki project.
git clone https://github.com/ait-aecid/logdata-anomaly-miner.wiki.git 2> /dev/null
cd logdata-anomaly-miner.wiki 2> /dev/null
git checkout $BRANCH > /dev/null 2>&1
cd ..

# create log file (1.)
awk '/^```$/ && ++n == 2, /^```$/ && n++ == 3' < $INPUT | sed '/^```/ d' > $LOG

# extract version command and compare output. (2.)
#awk '/^```bash$/ && ++n == 2, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
#CMD=$(sed -n '1p' < $OUT)
#CMD="sudo ${CMD#* }"
#OUT1=$(sed -n '2,4p' < $OUT)
#$CMD > $OUT &
#PID=$!
#sleep 5
#sudo pkill -x aminer
#wait $PID
#OUT2=`cat $OUT`
#compareStrings "$OUT1" "$OUT2" "Failed Test in 2."
#exit_code=$?

# 3.) Read commands between 3rd ```bash and 5th ```, get the CMD after # and check if aminer_install.sh exists and is executable.
FILE="aminer_install.sh"
awk '/^```bash$/ && ++n == 3, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
CMD=$(sed -n '1p' < $OUT)
CMD="${CMD#* } -q"
$CMD
if [ ! -f "$FILE" ]; then
  echo "$FILE does not exist."
  exit_code=1
fi
CMD=$(sed -n '2p' < $OUT)
CMD="${CMD#* }"
$CMD
if [ ! -x "$FILE" ]; then
  echo "$FILE is not executable."
  exit_code=1
fi

# 4.) Read the CMD between 4th ```bash and 6th ``` and get the CMD after # . (skipping this step)
#awk '/^```bash$/ && ++n == 4, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
#CMD=$(sed -n '1p' < $OUT)
#CMD="${CMD#* }"

# 5.) Replace the path in the second string with the current directory and run the CMD. (skipping this step)
#PWD=$(pwd)
#CMD=$(echo "${CMD?/home/ubuntu/aminer?"$PWD"}" )
#$CMD

# 6.) Read the CMD between 5th ```bash and 7th ```, get the CMD after #  and run it. (skipping this step)
#awk '/^```bash$/ && ++n == 5, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
#CMD=$(sed -n '1p' < $OUT)
#CMD="${CMD#* }"
#$CMD

# 7.) Read the CMD between 6th ```bash and 8th ```, get the CMD after #  and run it.
awk '/^```bash$/ && ++n == 6, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
CMD=$(sed -n '1p' < $OUT)
CMD="${CMD#* }"
$CMD 2> /dev/null

# 8.) Read between 1st ```yaml and 9th ``` and store it in CFG_PATH.
awk '/^```yaml$/ && ++n == 1, /^```$/' < $INPUT | sed '/^```/ d' | sudo tee $CFG_PATH > /dev/null

# 9.) Read CFG_PATH, replace the line with json: True and compare it with the 1st ```yaml in Getting-started-(tutorial).md.
OUT1=$(sudo cat $CFG_PATH | sed -n '1,21p')
CMD=$(sudo cat $CFG_PATH | sed -n '23p')
OUT1="$OUT1
$CMD"
awk '/^```yaml$/ && ++n == 1, /^```$/' < logdata-anomaly-miner.wiki/Getting-started-\(tutorial\).md | sed '/^```/ d' > $OUT
OUT2=`cat $OUT`
compareStrings "$OUT1" "$OUT2" "Failed Test in 9."
exit_code=$((exit_code | $?))
sudo sed -i 's?file:///home/ubuntu/access.log?file:///tmp/access.log?g' $CFG_PATH

# 10.) Read 7th ```bash and 10th ```. Extract CMD in first line and run it as sudo.
awk '/^```bash$/ && ++n == 7, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
CMD=$(sed -n '1p' < $OUT)
CMD="sudo ${CMD#* }"
runAminerUntilEnd "$CMD" "" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
exit_code=$((exit_code | $?))

# 11.) Compare the outputs (replace lines with timestamps and dates).
OUT1=$(sed -n '2,44p' < $OUT)
OUT2=$(sed -n '46,98p' < $OUT)
OUT1="$OUT1
$OUT2"
OUT2=$(sed -n '100,131p' < $OUT)
OUT1="$OUT1
$OUT2"

OUT2=$(sed -n '2,44p' < $OUT)
OUT3=$(sed -n '46,98p' < $OUT)
OUT2="$OUT2
$OUT3"
OUT3=$(sed -n '100,131p' < $OUT)
OUT2="$OUT2
$OUT3"
compareStrings "$OUT1" "$OUT2" "Failed Test in 11."
exit_code=$((exit_code | $?))

# 12.) Read 1st ```python and 12th ``` and write it to SEQ_DET.
awk '/^```python$/ && ++n == 1, /^```$/' < $INPUT | sed '/^```/ d' > $TMP_SEQ_DET
sudo cp $TMP_SEQ_DET $SEQ_DET

# 13.) Read 2nd ```yaml and 13th ``` and write it at 18th line in CFG_PATH.
awk '/^```yaml/ && ++n == 2, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
IN1=$(tail -n 4 < $OUT)
OUT1=$(head -n 17 < $CFG_PATH)
OUT2=$(tail -n 5 < $CFG_PATH)
echo "$OUT1

$IN1
$OUT2" > $CFG_PATH

# 14.) Check if line between 15th and 16th ``` can be found in /usr/lib/logdata-anomaly-miner/aminer/schemas/normalisation/AnalysisNormalisationSchema.py
awk '/^```$/ && ++n == 15, /^```$/ && n++ == 16' < $INPUT > $OUT
LINE=$(sed -n '2p' < $OUT)
if ! fgrep -q "$LINE" $NOR_SCHEMA; then
    echo "$LINE not found in $NOR_SCHEMA"
    echo "Failed Test in 14."
    echo
    exit_code=1
fi

# 15.) Add code between 18th and 19th ``` to /usr/lib/logdata-anomaly-miner/aminer/schemas/validation/AnalysisValidationSchema.py
sudo cp $VAL_SCHEMA $TMP_VAL_SCHEMA
awk '/^{$/,/^                }$/' $VAL_SCHEMA > $TMP_SCHEMA
echo , >> $TMP_SCHEMA
awk '/^```$/ && ++n == 18, /^```$/ && n++ == 19' < $INPUT | sed '/^```/ d' >> $TMP_SCHEMA
awk '/^            ]$/,/^}$/' $VAL_SCHEMA >> $TMP_SCHEMA
sudo cp $TMP_SCHEMA $VAL_SCHEMA

# 16.) Add 2nd ```python and 21st ``` to the YML_CONFIG.
# create backup of YamlConfig.py
cp $YML_CONFIG $TMP_YML_CONFIG
# add code to YamlConfig.py
printf "            " > $TMP_SCHEMA
awk '/^```python$/ && ++n == 2, /^```$/' < $INPUT | sed '/^```/ d' >> $TMP_SCHEMA
sudo sed -i "                    /anomaly_threshold=item/r $TMP_SCHEMA" $YML_CONFIG

# 17.) Run aminer CMD and check if the output contains "Detector template received a log atom!" times the number of log lines.
runAminerUntilEnd "$CMD" "" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
exit_code=$((exit_code | $?))
CNT=$(grep -o "Detector template received a log atom!" $OUT | wc -l)
if [ $CNT != 8 ]; then
    echo "Failed Test in 17. $CNT != 8"
    echo
    exit_code=1
fi

# 18.) Read 3rd ```python and 24th ``` and replace the receive_atom method in the SEQ_DET.
sed -i -e "34,36d" $TMP_SEQ_DET
awk '/^```python$/ && ++n == 3, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
IN1=`cat $OUT`
echo -e "\n$IN1" >> $TMP_SEQ_DET
sudo cp $TMP_SEQ_DET $SEQ_DET

# 19.) Run aminer CMD and check if the output contains data between 25th and 26th ```.
runAminerUntilEnd "$CMD" "" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
exit_code=$((exit_code | $?))
OUT1=$(tail -n 27 < $OUT)
awk '/^```$/ && ++n == 25, /^```$/ && n++ == 26' < $INPUT | sed '/^```/ d' > $OUT
OUT2=`cat $OUT`
compareStrings "$OUT1" "$OUT2" "Failed Test in 19."
exit_code=$((exit_code | $?))

# 20.) Read 4th ```python and 27th ``` and replace the receive_atom method in the SEQ_DET.
sed -i -e "61,65d" $TMP_SEQ_DET
awk '/^```python$/ && ++n == 4, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
IN1=`cat $OUT`
echo -e "\n$IN1" >> $TMP_SEQ_DET
sudo cp $TMP_SEQ_DET $SEQ_DET

# 21.) Run aminer CMD and check if the output is the same as between 28th and 29th ```.
runAminerUntilEnd "$CMD" "" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
exit_code=$((exit_code | $?))
OUT1=$(tail -n 8 < $OUT)
awk '/^```$/ && ++n == 28, /^```$/ && n++ == 29' < $INPUT | sed '/^```/ d' > $OUT
OUT2=`cat $OUT`
compareStrings "$OUT1" "$OUT2" "Failed Test in 21."
exit_code=$((exit_code | $?))

# 22.) Read 5th ```python and 30th ``` and replace the receive_atom method in the SEQ_DET.
sed -i -e "61,65d" $TMP_SEQ_DET
awk '/^```python$/ && ++n == 5, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
IN1=`cat $OUT`
echo -e "\n$IN1" >> $TMP_SEQ_DET
sudo cp $TMP_SEQ_DET $SEQ_DET

# 23.) Replace Analysis in CFG_PATH with the config between 3rd ```yaml and 31st ```.
OUT1=$(head -n 18 $CFG_PATH)
awk '/^```yaml/ && ++n == 3, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
IN1=$(tail -n 4 $OUT)
OUT2=$(tail -n 5 $CFG_PATH)
echo "$OUT1

$IN1
$OUT2" > $CFG_PATH

# 24.) Run aminer CMD and check if the output is the same as between 32nd and 33th ```.
runAminerUntilEnd "$CMD" "" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
exit_code=$((exit_code | $?))
OUT1=$(tail -n 8 < $OUT)
awk '/^```$/ && ++n == 32, /^```$/ && n++ == 33' < $INPUT | sed '/^```/ d' > $OUT
OUT2=`cat $OUT`
compareStrings "$OUT1" "$OUT2" "Failed Test in 24."
exit_code=$((exit_code | $?))

# 25.) Add code between 34th and 35th ``` in the __init__ method.
awk '/^```$/ && ++n == 34, /^```$/ && n++ == 35' < $INPUT | sed '/^```/ d' > $OUT
IN1=$(head -n 1 $OUT)
sed -i "30 i \        $IN1" $TMP_SEQ_DET
IN1=$(tail -n 1 $OUT)
sed -i "31 i \        $IN1" $TMP_SEQ_DET
sudo cp $TMP_SEQ_DET $SEQ_DET

# 26.) Read 6th ```python and 36th ``` and replace the receive_atom method in the SEQ_DET.
sed -i -e "82d" $TMP_SEQ_DET
awk '/^```python$/ && ++n == 6, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
IN1=$(tail -n 7 $OUT)
echo -e "\n$IN1" >> $TMP_SEQ_DET
sudo cp $TMP_SEQ_DET $SEQ_DET

# 27.) Run aminer CMD and check if the output is the same as between 37th and 38th ```.
runAminerUntilEnd "$CMD" "" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
exit_code=$((exit_code | $?))
OUT1=$(tail -n 6 < $OUT)
awk '/^```$/ && ++n == 37, /^```$/ && n++ == 38' < $INPUT | sed '/^```/ d' > $OUT
OUT2=`cat $OUT`
compareStrings "$OUT1" "$OUT2" "Failed Test in 27."
exit_code=$((exit_code | $?))

# 28.) Read 7th ```python and 39th ``` and replace the receive_atom method in the SEQ_DET.
awk '/^```python$/ && ++n == 7, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
IN1=$(tail -n 4 $OUT)
echo -e "\n$IN1" >> $TMP_SEQ_DET
sudo cp $TMP_SEQ_DET $SEQ_DET

# 29.) Add lines between 14th ```bash and 42nd ``` to the LOG.
echo "192.168.10.190 - - [29/Feb/2020:14:10:35 +0000] \"GET /services/portal/ HTTP/1.1\" 200 4345 \"-\" \"-\"" >> $LOG
echo "192.168.10.190 - - [29/Feb/2020:14:10:45 +0000] \"GET /kronolith/ HTTP/1.1\" 200 3452 \"-\" \"-\"" >> $LOG
echo "192.168.10.190 - - [29/Feb/2020:14:10:54 +0000] \"GET /nag/ HTTP/1.1\" 200 25623 \"-\" \"-\"" >> $LOG

# 30.) Run aminer CMD and check if the output is the same as between 40th and 41st ``` plus the text between 43th and 44th ```.
runAminerUntilEnd "$CMD" "" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
exit_code=$((exit_code | $?))
OUT1=$(tail -n 15 < $OUT)
awk '/^```$/ && ++n == 40, /^```$/ && n++ == 41' < $INPUT | sed '/^```/ d' > $OUT
OUT2=`cat $OUT`
awk '/^```$/ && ++n == 43, /^```$/ && n++ == 44' < $INPUT | sed '/^```/ d' > $OUT
OUT3=`cat $OUT`
OUT2="$OUT2
$OUT3"
compareStrings "$OUT1" "$OUT2" "Failed Test in 30."
exit_code=$((exit_code | $?))

# 31.) Read 8th ```python and 45th ``` and replace the receive_atom method in the SEQ_DET.
sed -i -e "89,94d" $TMP_SEQ_DET
awk '/^```python$/ && ++n == 8, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
IN1=`cat $OUT`
echo -e "\n$IN1" >> $TMP_SEQ_DET
sudo cp $TMP_SEQ_DET $SEQ_DET

# 32.) Compare the output with the json between 1st ```json and 46th ```.
runAminerUntilEnd "$CMD" "" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
exit_code=$((exit_code | $?))
OUT1=$(tail -n 40 $OUT)
echo "$OUT1" > $OUT
OUT1=$(tail -n 3 $OUT)
OUT2=$(head -n 36 $OUT)
OUT1="$OUT2
$OUT1"
awk '/^```json/ && ++n == 1, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
OUT2=$(tail -n 40 $OUT)
echo "$OUT2" > $OUT
OUT2=$(tail -n 3 $OUT)
OUT3=$(head -n 36 $OUT)
OUT2="$OUT3
$OUT2"
compareStrings "$OUT1" "$OUT2" "Failed Test in 32."
exit_code=$((exit_code | $?))

# 33.) Replace the do_persist method with the code between 9th ```python and 47th ```.
sed -i -e "55,57d" $TMP_SEQ_DET
awk '/^```python$/ && ++n == 9, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
IN1=`cat $OUT`
echo -e "\n$IN1" >> $TMP_SEQ_DET
sudo cp $TMP_SEQ_DET $SEQ_DET
runAminerUntilEnd "$CMD" "" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
exit_code=$((exit_code | $?))

# 34.) Run the CMD in the first line between 15th ```bash and 48th ``` and compare the output with the second line.
awk '/^```bash$/ && ++n == 15, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
CMD=$(sed -n '1p' < $OUT)
CMD="sudo ${CMD#* }"
OUT1=$(sed -n '2p' < $OUT)
$CMD > $OUT
IN1=`cat $OUT`
# not working, because sets have no real order.
#compareStrings "$OUT1" "$IN1" "Failed Test in 34."
#exit_code=$((exit_code | $?))

# reset schema to backup.
sudo cp $TMP_VAL_SCHEMA $VAL_SCHEMA
sudo cp $TMP_YML_CONFIG $YML_CONFIG
sudo rm $TMP_VAL_SCHEMA
sudo rm $CFG_PATH
sudo rm $TMP_YML_CONFIG
sudo rm $TMP_SEQ_DET
sudo rm $SEQ_DET
sudo rm $OUT
sudo rm $TMP_SCHEMA
sudo rm -r logdata-anomaly-miner.wiki
sudo rm aminer_install.sh
exit $exit_code
