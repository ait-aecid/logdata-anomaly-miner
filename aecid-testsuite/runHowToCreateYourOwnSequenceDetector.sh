#!/bin/bash

BRANCH=main

if [ $# -gt 0 ]
then
BRANCH=$1
fi

sudo chown -R aminer:aminer /var/lib/aminer 2> /dev/null

SRC_FILE=logdata-anomaly-miner.wiki/HowTo:-Create-your-own-SequenceDetector.md
VAL_SCHEMA=/usr/lib/logdata-anomaly-miner/aminer/schemas/validation/AnalysisValidationSchema.py
TMP_VAL_SCHEMA=/tmp/AnalysisValidationSchema.py
YML_CONFIG=/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py
TMP_YML_CONFIG=/tmp/YamlConfig.py
TMP_SCHEMA=/tmp/schema.py
SEQ_DET=/usr/lib/logdata-anomaly-miner/aminer/analysis/SequenceDetector.py
CONFIG=/tmp/config.yml

# extract the file from the development branch of the wiki project.
git clone https://github.com/ait-aecid/logdata-anomaly-miner.wiki.git 2> /dev/null
cd logdata-anomaly-miner.wiki 2> /dev/null
git checkout $BRANCH > /dev/null 2>&1
cd ..
awk '/^```yaml$/ && ++n == 1, /^```$/' < $SRC_FILE | sed '/^```/ d' > /tmp/base-config.yml
# text before EventHandlers:
sed -e '/EventHandlers:$/,$d' /tmp/base-config.yml > $CONFIG
# extract the config part for the SequenceDetector.
awk '/^```yaml$/ && ++n == 2, /^```$/' < $SRC_FILE | sed '/^```/ d' | sed '/^Analysis:$/ d' >> $CONFIG
# text after Analysis components:
sed -n -e '/^EventHandlers:$/,$p' /tmp/base-config.yml >> $CONFIG

# create backup of schema.
cp $VAL_SCHEMA $TMP_VAL_SCHEMA
awk '/^# skipcq: PYL-W0104$/,/^                }$/' $VAL_SCHEMA > $TMP_SCHEMA
echo , >> $TMP_SCHEMA
awk '/^```$/ && ++n == 18, /^```$/ && n++ == 19' < $SRC_FILE | sed '/^```/ d' >> $TMP_SCHEMA
awk '/^            ]$/,/^}$/' $VAL_SCHEMA >> $TMP_SCHEMA
cp $TMP_SCHEMA $VAL_SCHEMA
awk '/^```python$/ && ++n == 1, /^```$/' < $SRC_FILE | sed '/^```/ d' > $SEQ_DET

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
cp $TMP_VAL_SCHEMA $VAL_SCHEMA
cp $TMP_YML_CONFIG $YML_CONFIG
rm /tmp/base-config.yml
rm $TMP_SCHEMA
rm $TMP_VAL_SCHEMA
rm $CONFIG
rm $TMP_YML_CONFIG
rm $SEQ_DET
sudo rm -r logdata-anomaly-miner.wiki
exit $exit_code
