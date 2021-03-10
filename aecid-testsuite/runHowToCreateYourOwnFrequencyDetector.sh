#!/bin/bash

BRANCH=main

if [ $# -gt 0 ]
then
BRANCH=$1
fi

sudo chown -R aminer:aminer /var/lib/aminer 2> /dev/null

SRC_FILE=logdata-anomaly-miner.wiki/HowTo:-Create-your-own-FrequencyDetector.md
VAL_SCHEMA=/usr/lib/logdata-anomaly-miner/aminer/schemas/validation/AnalysisValidationSchema.py
TMP_VAL_SCHEMA=/tmp/AnalysisValidationSchema.py
YML_CONFIG=/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py
TMP_YML_CONFIG=/tmp/YamlConfig.py
TMP_SCHEMA=/tmp/schema.py
FREQ_DET=/usr/lib/logdata-anomaly-miner/aminer/analysis/FrequencyDetector.py
TMP_FREQ_DET=/tmp/FrequencyDetector.py
CONFIG=/tmp/config.yml

# extract the file from the development branch of the wiki project.
git clone https://github.com/ait-aecid/logdata-anomaly-miner.wiki.git 2> /dev/null
cd logdata-anomaly-miner.wiki 2> /dev/null
git checkout $BRANCH > /dev/null 2>&1
cd ..
awk '/^```yaml$/ && ++n == 1, /^```$/' < $SRC_FILE | sed '/^```/ d' > $CONFIG

# create backup of schema.
sudo cp $VAL_SCHEMA $TMP_VAL_SCHEMA
awk '/^# skipcq: PYL-W0104$/,/^                }$/' $VAL_SCHEMA > $TMP_SCHEMA
echo , >> $TMP_SCHEMA
awk '/^```$/ && ++n == 6, /^```$/ && n++ == 7' < $SRC_FILE | sed '/^```/ d' >> $TMP_SCHEMA
awk '/^            ]$/,/^}$/' $VAL_SCHEMA >> $TMP_SCHEMA
sudo cp $TMP_SCHEMA $VAL_SCHEMA
awk '/^```python$/ && ++n == 1, /^```$/' < $SRC_FILE | sed '/^```/ d' > $TMP_FREQ_DET
sudo cp $TMP_FREQ_DET $FREQ_DET

# create backup of YamlConfig.py
cp $YML_CONFIG $TMP_YML_CONFIG
# add code to YamlConfig.py
printf "            " > $TMP_SCHEMA
awk '/^```python$/ && ++n == 2, /^```$/' < $SRC_FILE | sed '/^```/ d' >> $TMP_SCHEMA
sudo sed -i "                    /num_sections_waiting_time_for_TSA=item/r $TMP_SCHEMA" $YML_CONFIG

sudo aminer --config $CONFIG > /dev/null &
sleep 5 & wait $!
sudo pkill -x aminer
exit_code=$?
# reset schema to backup.
sudo cp $TMP_VAL_SCHEMA $VAL_SCHEMA
sudo cp $TMP_YML_CONFIG $YML_CONFIG
sudo rm $TMP_VAL_SCHEMA
sudo rm $CONFIG
sudo rm $TMP_YML_CONFIG
sudo rm $FREQ_DET
sudo rm -r logdata-anomaly-miner.wiki
exit $exit_code
