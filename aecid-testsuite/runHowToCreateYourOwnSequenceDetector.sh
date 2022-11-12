#!/bin/bash

. ./testFunctions.sh

##################################################################
# Description of the test. Line numbers are also considering starting lines with ```, so they are incremented by one compared to the text itself.
# 1.) Read the log lines between the 1st and 2nd ``` and save it to /var/log/apache2/access.log (LOG)
# 2.) Read 1st ```python and 3rd ``` and replace the FrequencyDetector in ../source/root/usr/lib/logdata-anomaly-miner/aminer/analysis/FrequencyDetector.py (store backup and restore it after the test)
# 3.) Check if the parameter definitions between 4th and 5th are the same as in ../source/root/usr/lib/logdata-anomaly-miner/aminer/schemas/normalisation/AnalysisNormalisationSchema.py
#     (each line on its own)
# 4.) Check if the FrequencyDetector parameters between 6th and 7th are the same as in ../source/root/usr/lib/logdata-anomaly-miner/aminer/schemas/validation/AnalysisValidationSchema.py
# 5.) Check if the Code between 2nd ```python and 8th ``` is the same as in ../source/root/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py
# 6.) Write the config to CFG_PATH from 1st ```yaml to 9th ``` and replace LogResourceList to LOG.
# 7.) Read CMD from the second line between the 1st ```bash to 10th ``` and run it with sudo.
# 8.) Compare the outputs with the ones between 11th and 12th ```.
# 9.) Read line between 3rd ```python and 13th ``` and add it between 23rd and 24th line in the CFG_PATH
# 10.) Remove lines 36-38 in the CFG_PATH and append the method between 4th ```python and 14th ``` + newline between.
# 11.) Run CMD and check if the output is the same as the one between 15th and 16th ```.
# 12.) Remove the previously added lines and add the lines between 5th ```python and 17th ```.
# 13.) Run CMD and compare the output to the one between 18th and 19th ```.
# 14.) Remove the previously added lines and add the lines between 6th ```python and 20th ```.
# 15.) Run CMD and compare the output to the one between 21st and 22nd ```.
# 16.) Remove the previously added lines and add the lines between 7th ```python and 23rd ```.
# 17.) Run CMD and compare the output to the one between 1st ```json and 24th ```.
# 18.) Replace the do_persist method with the lines between 8th ```python and 25th ``` and run CMD.
# 19.) Run CMD in 1st ```bash and 26th ``` and compare it to the output in the second line.
# 20.) Add lines between 9th ```python and 27th ```.
##################################################################

BRANCH=main

if [ $# -gt 0 ]
then
BRANCH=$1
fi

sudo chown -R aminer:aminer /var/lib/aminer 2> /dev/null

SRC_FILE=logdata-anomaly-miner.wiki/HowTo-Create-your-own-SequenceDetector.md
VAL_SCHEMA=/usr/lib/logdata-anomaly-miner/aminer/schemas/validation/AnalysisValidationSchema.yml
TMP_VAL_SCHEMA=/tmp/AnalysisValidationSchema.yml
YML_CONFIG=/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py
TMP_YML_CONFIG=/tmp/YamlConfig.py
TMP_SCHEMA=/tmp/schema.py
SEQ_DET=/usr/lib/logdata-anomaly-miner/aminer/analysis/SequenceDetector.py
TMP_SEQ_DET=/tmp/SequenceDetector.py
CFG_PATH=/etc/aminer/config.yml

# extract the file from the development branch of the wiki project.
git clone https://github.com/ait-aecid/logdata-anomaly-miner.wiki.git 2> /dev/null
cd logdata-anomaly-miner.wiki 2> /dev/null
git checkout $BRANCH > /dev/null 2>&1
cd ..
awk '/^```yaml$/ && ++n == 1, /^```$/' < $SRC_FILE | sed '/^```/ d' > /tmp/base-config.yml
# text before EventHandlers:
sed -e '/EventHandlers:$/,$d' /tmp/base-config.yml | sudo tee $CFG_PATH > /dev/null
# extract the config part for the SequenceDetector.
awk '/^```yaml$/ && ++n == 2, /^```$/' < $SRC_FILE | sed '/^```/ d' | sed '/^Analysis:$/ d' | sudo tee -a $CFG_PATH > /dev/null
# text after Analysis components:
sed -n -e '/^EventHandlers:$/,$p' /tmp/base-config.yml | sudo tee -a $CFG_PATH > /dev/null

# create backup of schema.
sudo cp $VAL_SCHEMA $TMP_VAL_SCHEMA
awk '/^{$/,/^                }$/' $VAL_SCHEMA > $TMP_SCHEMA
echo , >> $TMP_SCHEMA
awk '/^```$/ && ++n == 18, /^```$/ && n++ == 19' < $SRC_FILE | sed '/^```/ d' >> $TMP_SCHEMA
awk '/^            ]$/,/^}$/' $VAL_SCHEMA >> $TMP_SCHEMA
sudo cp $TMP_SCHEMA $VAL_SCHEMA
awk '/^```python$/ && ++n == 1, /^```$/' < $SRC_FILE | sed '/^```/ d' > $TMP_SEQ_DET
sudo cp $TMP_SEQ_DET $SEQ_DET

# create backup of YamlConfig.py
sudo cp $YML_CONFIG $TMP_YML_CONFIG
# add code to YamlConfig.py
printf "            " > $TMP_SCHEMA
awk '/^```python$/ && ++n == 2, /^```$/' < $SRC_FILE | sed '/^```/ d' >> $TMP_SCHEMA
sudo sed -i "                    /max_rule_attributes=item/r $TMP_SCHEMA" $YML_CONFIG

runAminerUntilEnd "sudo aminer --config $CFG_PATH -C" "" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "/dev/null"
exit_code=$?
# reset schema to backup.
sudo cp $TMP_VAL_SCHEMA $VAL_SCHEMA
sudo cp $TMP_YML_CONFIG $YML_CONFIG
sudo rm /tmp/base-config.yml
sudo rm $TMP_SCHEMA
sudo rm $TMP_VAL_SCHEMA
sudo rm $CFG_PATH
sudo rm $TMP_YML_CONFIG
sudo rm $SEQ_DET
sudo rm -r logdata-anomaly-miner.wiki
exit $exit_code
