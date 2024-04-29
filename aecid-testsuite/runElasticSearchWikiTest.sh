#!/bin/bash

. ./testFunctions.sh

##################################################################
# Description of the test. Line numbers are also considering starting lines with ```, so they are incremented by one compared to the text itself.

# 1.) Write second line of 3rd to 4th ``` into LOG.
# 2.) Write the config to CFG_PATH from 1st ```yaml to 5th ```.
# 3.) Replace LogResourceList path with LOG in CFG_PATH and the report interval of the ParserCount.
# 4.) Extract the CMD between 10th and 11th ```
# 5.) Compare the results with the outputs between between 12th and 13th ```.
##################################################################

BRANCH=main

if [ $# -gt 0 ]
then
BRANCH=$1
fi

INPUT=logdata-anomaly-miner.wiki/Importing-logs-via-ElasticSearch-interface.md
OUT=/tmp/out.txt
LOG=/tmp/access.log
CFG_PATH=/etc/aminer/config.yml
TMPFILE1=/tmp/tmpfile1
TMPFILE2=/tmp/tmpfile2

# extract the file from the development branch of the wiki project.
git clone https://github.com/ait-aecid/logdata-anomaly-miner.wiki.git 2> /dev/null
cd logdata-anomaly-miner.wiki 2> /dev/null
git checkout $BRANCH > /dev/null 2>&1
cd ..
exit_code=0

# write log data into file (1.)
awk '/^```$/ && ++n == 3, /^```$/ && n++ == 4' < $INPUT | sed '/^```/ d' > $LOG
sed -i '1d' $LOG

# write the config to CFG_PATH (2.)
awk '/^```yaml$/ && ++n == 1, /^```$/' < $INPUT | sed '/^```/ d' | sudo -u $USER tee $CFG_PATH > /dev/null

# replace LogResourceList (3.)
sed "s?unix:///var/lib/aelastic/aminer.sock?file:///${LOG}?g" $CFG_PATH | sudo -u $USER tee $CFG_PATH > /dev/null
sed "s?report_interval: 5?report_interval: 555555555?g" $CFG_PATH | sudo -u $USER tee $CFG_PATH > /dev/null

# extract CMD (4.)
awk '/^```$/ && ++n == 10, /^```$/ && n++ == 11' < $INPUT | sed '/^```/ d' > $OUT
CMD=$(cat $OUT)
IFS='$' read -ra ADDR <<< "$CMD"
CMD="${ADDR[1]}"
runAminerUntilEnd "$CMD" "$LOG" "/var/lib/aminer/AnalysisChild/RepositioningData" "$CFG_PATH" "$OUT"
OUTPUT=$(cat $OUT)

# compare results (5.)
IN=$(awk '/^```$/ && ++n == 12, /^```$/ && n++ == 13' < $INPUT | sed '/^```/ d')
i=0
while IFS= read -r line
do
  if [[ $i -ne 52 && $i -ne 54 ]]; then
    echo "$line" >> $TMPFILE1
  fi
  i=$(($i+1))
done <<< "$IN"

i=0
while IFS= read -r line
do
  if [[ $i -ne 52 && $i -ne 54 ]]; then
    echo "$line" >> $TMPFILE2
  fi
  i=$(($i+1))
done <<< "$OUTPUT"

cmp --silent $TMPFILE1 $TMPFILE2
res=$?
if [[ $res != 0 ]]; then
  cat $TMPFILE1
  echo
  echo "Failed Test in 5."
  echo
  cat $TMPFILE2
fi
exit_code=$((exit_code | res))
rm $TMPFILE1
rm $TMPFILE2


rm $OUT
rm $LOG
sudo rm -r logdata-anomaly-miner.wiki
exit $exit_code
