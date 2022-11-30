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
# 23.) Replace Analysis in YML_CONFIG with the config between 3rd ```yaml and 31st ```.
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
# 35.) Read 10th ```python and 49th ``` and add the code in the __init__ method in the SEQ_DET.
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

###################### delete this!
cp /home/user/Documents/HowTo-Create-your-own-SequenceDetector.md logdata-anomaly-miner.wiki/HowTo-Create-your-own-SequenceDetector.md
VAL_SCHEMA=/usr/lib/logdata-anomaly-miner/aminer/schemas/validation/AnalysisValidationSchema.yml
TMP_VAL_SCHEMA=/tmp/AnalysisValidationSchema.yml
NOR_SCHEMA=/usr/lib/logdata-anomaly-miner/aminer/schemas/normalisation/AnalysisNormalisationSchema.yml

## merge this only after yml was renamed to py!
##################### delete this!

# create log file (1.)
awk '/^```$/ && ++n == 2, /^```$/ && n++ == 3' < $INPUT | sed '/^```/ d' > $LOG

# extract version command and compare output. (2.)
awk '/^```bash$/ && ++n == 2, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
CMD=$(sed -n '1p' < $OUT)
CMD="sudo ${CMD#* }"
OUT1=$(sed -n '2,4p' < $OUT)
$CMD > $OUT &
PID=$!
sleep 5
sudo pkill -x aminer
wait $PID
OUT2=`cat $OUT`
compareStrings "$OUT1" "$OUT2" "Failed Test in 2."
exit_code=$?

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
awk '/^```yaml$/ && ++n == 1, /^```$/' < $INPUT | sed '/^```/ d' > $CFG_PATH
sudo sed -i 's?file:///var/log/apache2/access.log?file:///tmp/access.log?g' $CFG_PATH

# 9.) Read CFG_PATH, replace the line with json: True and compare it with the 1st ```yaml in Getting-started-(tutorial).md.
OUT1=$(sed -n '1,21p' < $CFG_PATH)
CMD=$(sed -n '23p' < $CFG_PATH)
OUT1="$OUT1
$CMD"
awk '/^```yaml$/ && ++n == 1, /^```$/' < logdata-anomaly-miner.wiki/Getting-started-\(tutorial\).md | sed '/^```/ d' > $OUT
OUT2=`cat $OUT`
compareStrings "$OUT1" "$OUT2" "Failed Test in 9."

# 10.) Read 7th ```bash and 10th ```. Extract CMD in first line and run it as sudo.
awk '/^```bash$/ && ++n == 7, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
CMD=$(sed -n '1p' < $OUT)
CMD="sudo ${CMD#* }"
runAminerUntilEnd "$CMD" "" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
cat $OUT

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
# 23.) Replace Analysis in YML_CONFIG with the config between 3rd ```yaml and 31st ```.
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
# 35.) Read 10th ```python and 49th ``` and add the code in the __init__ method in the SEQ_DET.


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
