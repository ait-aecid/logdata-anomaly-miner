#!/bin/bash

. ./testFunctions.sh

##################################################################
# Description of the test. Line numbers are also considering starting lines with ```, so they are incremented by one compared to the text itself.
# 1.) Read the log lines between the 1st and 2nd ``` and save it to /tmp/access.log (LOG)
# 2.) Read 1st ```python and 3rd ``` and write the FrequencyDetector to ../source/root/usr/lib/logdata-anomaly-miner/aminer/analysis/FrequencyDetector.py
# 3.) Check if the parameter definitions between 4th and 5th are the same as in ../source/root/usr/lib/logdata-anomaly-miner/aminer/schemas/normalisation/AnalysisNormalisationSchema.py
#     (each line on its own)
# 4.) Add the FrequencyDetector parameters between 6th and 7th are the same as in ../source/root/usr/lib/logdata-anomaly-miner/aminer/schemas/validation/AnalysisValidationSchema.py
# 5.) Add the code between 2nd ```python and 8th ``` to the ../source/root/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py
# 6.) Write the config to CFG_PATH from 1st ```yaml to 9th ``` and replace LogResourceList to LOG.
# 7.) Read CMD from the second line between the 1st ```bash to 10th ``` and run it with sudo.
# 8.) Compare the outputs with the ones between 11th and 12th ```.
# 9.) Read line between 3rd ```python and 13th ``` and add it between 23rd and 24th line in the CFG_PATH
# 10.) Remove lines 36-38 in the $FREQ_DET and append the method between 4th ```python and 14th ``` + newline between.
# 11.) Run CMD and check if the output is the same as the one between 15th and 16th ```.
# 12.) Remove the previously added lines and add the lines between 5th ```python and 17th ```.
# 13.) Run CMD and compare the output to the one between 18th and 19th ```.
# 14.) Remove the previously added lines and add the lines between 6th ```python and 20th ```.
# 15.) Run CMD and compare the output to the one between 21st and 22nd ```.
# 16.) Remove the previously added lines and add the lines between 7th ```python and 23rd ```.
# 17.) Run CMD and compare the output to the one between 1st ```json and 24th ```.
# 18.) Replace the do_persist method with the lines between 8th ```python and 25th ``` and run CMD.
# 19.) Run CMD in 2nd ```bash and 26th ``` and compare it to the output in the second line.
# 20.) Add lines between 9th ```python and 27th ```.
##################################################################

BRANCH=main

if [ $# -gt 0 ]
then
BRANCH=$1
fi

sudo chown -R aminer:aminer /var/lib/aminer 2> /dev/null
INPUT=logdata-anomaly-miner.wiki/HowTo-Create-your-own-FrequencyDetector.md
VAL_SCHEMA=/usr/lib/logdata-anomaly-miner/aminer/schemas/validation/AnalysisValidationSchema.py
TMP_VAL_SCHEMA=/tmp/AnalysisValidationSchema.py
NOR_SCHEMA=/usr/lib/logdata-anomaly-miner/aminer/schemas/normalisation/AnalysisNormalisationSchema.py
OUT=/tmp/out.txt

SRC_FILE=logdata-anomaly-miner.wiki/HowTo-Create-your-own-FrequencyDetector.md
VAL_SCHEMA=/usr/lib/logdata-anomaly-miner/aminer/schemas/validation/AnalysisValidationSchema.py
TMP_VAL_SCHEMA=/tmp/AnalysisValidationSchema.py
YML_CONFIG=/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py
TMP_YML_CONFIG=/tmp/YamlConfig.py
TMP_SCHEMA=/tmp/schema.py
FREQ_DET=/usr/lib/logdata-anomaly-miner/aminer/analysis/FrequencyDetector.py
TMP_FREQ_DET=/tmp/FrequencyDetector.py
CFG_PATH=/etc/aminer/config.yml
LOG=/tmp/access.log

# extract the file from the development branch of the wiki project.
git clone https://github.com/ait-aecid/logdata-anomaly-miner.wiki.git 2> /dev/null
cd logdata-anomaly-miner.wiki 2> /dev/null
git checkout $BRANCH > /dev/null 2>&1
cd ..

# create log file (1.)
awk '/^```$/ && ++n == 1, /^```$/ && n++ == 2' < $INPUT | sed '/^```/ d' > $LOG

# 2.) create FrequencyDetector
awk '/^```python$/ && ++n == 1, /^```$/' < $INPUT | sed '/^```/ d' > $TMP_FREQ_DET
sudo cp $TMP_FREQ_DET $FREQ_DET

# 3.) compare parameter definitions with AnalysisNormalisationSchema
awk '/^```$/ && ++n == 4, /^```$/ && n++ == 5' < $INPUT > $OUT
LINE=$(sed -n '2p' < $OUT)
if ! fgrep -q "$LINE" $NOR_SCHEMA; then
    echo "$LINE not found in $NOR_SCHEMA"
    echo "Failed Test in 3."
    echo
    exit_code=1
fi
LINE=$(sed -n '3p' < $OUT)
if ! fgrep -q "$LINE" $NOR_SCHEMA; then
    echo "$LINE not found in $NOR_SCHEMA"
    echo "Failed Test in 3."
    echo
    exit_code=1
fi

# 4.) Add the FrequencyDetector parameters to the AnalysisValidationSchema
sudo cp $VAL_SCHEMA $TMP_VAL_SCHEMA
awk '/^{$/,/^                }$/' $VAL_SCHEMA > $TMP_SCHEMA
echo , >> $TMP_SCHEMA
awk '/^```$/ && ++n == 6, /^```$/ && n++ == 7' < $INPUT | sed '/^```/ d' >> $TMP_SCHEMA
awk '/^            ]$/,/^}$/' $VAL_SCHEMA >> $TMP_SCHEMA
sudo cp $TMP_SCHEMA $VAL_SCHEMA

# 5.) Add code to the YamlConfig.py
# create backup of YamlConfig.py
cp $YML_CONFIG $TMP_YML_CONFIG
# add code to YamlConfig.py
printf "            " > $TMP_SCHEMA
awk '/^```python$/ && ++n == 2, /^```$/' < $INPUT | sed '/^```/ d' >> $TMP_SCHEMA
sudo sed -i "                    /anomaly_threshold=item/r $TMP_SCHEMA" $YML_CONFIG

# 6.) Write the config to CFG_PATH and replace LogResourceList to LOG.
awk '/^```yaml$/ && ++n == 1, /^```$/' < $INPUT | sed '/^```/ d' | sudo -u $USER tee $CFG_PATH > /dev/null
sudo sed -i 's?file:///home/ubuntu/apache.log?file:///tmp/access.log?g' $CFG_PATH

# 7.) Read CMD from the second line between the 1st ```bash to 10th ``` and run it with sudo.
awk '/^```bash$/ && ++n == 1, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
CMD=$(sed -n '2p' < $OUT)
CMD="sudo ${CMD#* } --config $CFG_PATH"
runAminerUntilEnd "$CMD" "" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
exit_code=$?

# 8.) Compare the outputs with the ones between 11th and 12th ```.
OUT1=$(tail -n 14 $OUT)
awk '/^```$/ && ++n == 11, /^```$/ && n++ == 12' < $INPUT | sed '/^```/ d' > $OUT
IN1=`cat $OUT`
compareStrings "$OUT1" "$IN1" "Failed Test in 8."
exit_code=$((exit_code | $?))

# 9.) Read line between 3rd ```python and 13th ``` and add it between 23rd and 24th line in the FREQ_DET
awk '/^```python$/ && ++n == 3, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
IN1=`cat $OUT`
sed -i "23 i \        $IN1" $TMP_FREQ_DET
sudo cp $TMP_FREQ_DET $FREQ_DET

# 10.) Remove lines 36-38 in the FREQ_DET and append the method between 4th ```python and 14th ``` + newline between.
sed -i -e "35,38d" $TMP_FREQ_DET
awk '/^```python$/ && ++n == 4, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
IN1=`cat $OUT`
echo -e "\n$IN1" >> $TMP_FREQ_DET
sudo cp $TMP_FREQ_DET $FREQ_DET

# 11.) Run CMD and check if the output is the same as the one between 15th and 16th ```.
runAminerUntilEnd "$CMD" "" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
exit_code=$((exit_code | $?))
OUT1=$(tail -n 18 $OUT)
awk '/^```$/ && ++n == 15, /^```$/ && n++ == 16' < $INPUT | sed '/^```/ d' > $OUT
IN1=`cat $OUT`
compareStrings "$OUT1" "$IN1" "Failed Test in 11."
exit_code=$((exit_code | $?))

# 12.) Remove the previously added lines and add the lines between 5th ```python and 17th ```.
tac $TMP_FREQ_DET | sed '1,13d' | tac > $OUT
cp $OUT $TMP_FREQ_DET
awk '/^```python$/ && ++n == 5, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
IN1=`cat $OUT`
echo -e "$IN1" >> $TMP_FREQ_DET

# 13.) Run CMD and compare the output to the one between 18th and 19th ```.
sed -i "23 i \        self.counts = {}" $TMP_FREQ_DET
sudo cp $TMP_FREQ_DET $FREQ_DET
runAminerUntilEnd "$CMD" "" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
exit_code=$((exit_code | $?))
OUT1=$(tail -n 14 $OUT)
awk '/^```$/ && ++n == 18, /^```$/ && n++ == 19' < $INPUT | sed '/^```/ d' > $OUT
IN1=`cat $OUT`
compareStrings "$OUT1" "$IN1" "Failed Test in 13."
exit_code=$((exit_code | $?))

# 14.) Remove the previously added lines and add the lines between 6th ```python and 20th ```.
tail -n 6 $TMP_FREQ_DET > $OUT
IN=`cat $OUT`
tac $TMP_FREQ_DET | sed '1,14d' | tac > $OUT
cp $OUT $TMP_FREQ_DET
awk '/^```python$/ && ++n == 6, /^```$/' < $INPUT | sed '/^```/ d' | sed '1,2d;23d' > $OUT
IN1=`cat $OUT`
echo -e "$IN1" >> $TMP_FREQ_DET
echo -e "$IN" >> $TMP_FREQ_DET
sudo cp $TMP_FREQ_DET $FREQ_DET

# 15.) Run CMD and compare the output to the one between 21st and 22nd ```.
sed -i "23 i \        self.counts_prev = {}" $TMP_FREQ_DET
sudo cp $TMP_FREQ_DET $FREQ_DET
runAminerUntilEnd "$CMD" "" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
exit_code=$((exit_code | $?))
OUT1=$(tail -n 17 $OUT)
awk '/^```$/ && ++n == 21, /^```$/ && n++ == 22' < $INPUT | sed '/^```/ d' > $OUT
IN1=`cat $OUT`
compareStrings "$OUT1" "$IN1" "Failed Test in 15."
exit_code=$((exit_code | $?))

# 16.) Remove the previously added lines and add the lines between 7th ```python and 23rd ```.
tail -n 6 $TMP_FREQ_DET > $OUT
IN=`cat $OUT`
tac $TMP_FREQ_DET | sed '1,26d' | tac > $OUT
cp $OUT $TMP_FREQ_DET
awk '/^```python$/ && ++n == 7, /^```$/' < $INPUT | sed '/^```/ d' | sed '1,2d;38d' > $OUT
IN1=`cat $OUT`
echo -e "$IN1" >> $TMP_FREQ_DET
echo -e "$IN" >> $TMP_FREQ_DET
tac $TMP_FREQ_DET | sed '1d' | tac > $OUT # remove print
cp $OUT $TMP_FREQ_DET
sudo cp $TMP_FREQ_DET $FREQ_DET

# 17.) Run CMD and compare the output to the one between 1st ```json and 24th ```.
runAminerUntilEnd "$CMD" "" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
exit_code=$((exit_code | $?))
# delete detectionTimestamp from comparison
tac $OUT | sed '32d' | tac > $TMP_SCHEMA
cp $TMP_SCHEMA $OUT
OUT1=$(tail -n 60 $OUT)
awk '/^```json$/ && ++n == 1, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
# delete detectionTimestamp from comparison
sed -i -e "30d" $OUT
IN1=`cat $OUT`
compareStrings "$OUT1" "$IN1" "Failed Test in 17."
exit_code=$((exit_code | $?))

# 18.) Replace the do_persist method with the lines between 8th ```python and 25th ``` and run CMD.
sed -i -e "56,59d" $TMP_FREQ_DET
awk '/^```python$/ && ++n == 8, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
IN1=`cat $OUT`
echo -e "\n    $IN1" >> $TMP_FREQ_DET
sudo cp $TMP_FREQ_DET $FREQ_DET

runAminerUntilEnd "$CMD" "" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
exit_code=$((exit_code | $?))

# 19.) Run CMD in 2nd ```bash and 26th ``` and compare it to the output in the second line.
awk '/^```bash$/ && ++n == 2, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
CMD1=$(sed -n '1p' < $OUT)
CMD1="${CMD1#* }"
$CMD1 > $OUT
OUT1=`cat $OUT`

awk '/^```bash$/ && ++n == 2, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
IN1=$(sed -n '2p' < $OUT)
compareStrings "$OUT1" "$IN1" "Failed Test in 19."
exit_code=$((exit_code | $?))

# 20.) Add lines between 9th ```python and 27th ```.
CMD="sudo aminer -f"
awk '/^```python$/ && ++n == 9, /^```$/' < $INPUT | sed '/^```/ d' > $OUT
IN1=`cat $OUT`
sed -i "/        PersistenceUtil.add_persistable_component(self)/r $OUT" $TMP_FREQ_DET
sudo cp $TMP_FREQ_DET $FREQ_DET
runAminerUntilEnd "$CMD" "" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
exit_code=$((exit_code | $?))

sudo cp $TMP_VAL_SCHEMA $VAL_SCHEMA
sudo cp $TMP_YML_CONFIG $YML_CONFIG
sudo rm $TMP_VAL_SCHEMA
sudo rm $CFG_PATH
sudo rm $TMP_YML_CONFIG
sudo rm $TMP_FREQ_DET
sudo rm $FREQ_DET
sudo rm $OUT
sudo rm $TMP_SCHEMA
sudo rm -r logdata-anomaly-miner.wiki
exit $exit_code
