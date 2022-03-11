#!/bin/bash

. ./testFunctions.sh

BRANCH=main

if [ $# -gt 0 ]
then
BRANCH=$1
fi

sudo chown -R aminer:aminer /var/lib/aminer 2> /dev/null

SRC_FILE=logdata-anomaly-miner.wiki/HowTo:-Create-your-own-SequenceDetector.md
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
sudo sed -i "                    /num_sections_waiting_time_for_tsa=item/r $TMP_SCHEMA" $YML_CONFIG

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
