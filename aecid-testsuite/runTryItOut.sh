#!/bin/bash

BRANCH=main

if [ $# -gt 0 ]
then
BRANCH=$1
fi


sudo chown -R aminer:aminer /var/lib/aminer 2> /dev/null

# extract the file from the development branch of the wiki project.
# the second ```python script is searched for.
git clone https://github.com/ait-aecid/logdata-anomaly-miner.wiki.git 2> /dev/null
cd logdata-anomaly-miner.wiki 2> /dev/null
git checkout $BRANCH > /dev/null 2>&1
cd ..
awk '/^```python$/ && ++n == 2, /^```$/' < logdata-anomaly-miner.wiki/aminer-TryItOut.md | sed '/^```/ d' > /tmp/tryItOut-config.yml
# text before comment:
sed -e '/# commented analysis components/,$d' /tmp/tryItOut-config.yml > /tmp/before
# text after commented components:
sed -n -e '/^EventHandlers:$/,$p' /tmp/tryItOut-config.yml > /tmp/after
# commented components
awk '/# commented analysis components$/,/^EventHandlers:$/' < /tmp/tryItOut-config.yml | sed '/^EventHandlers:/ d' | sed '/# commented analysis components/ d' > /tmp/commented
cat /tmp/before > /tmp/tryItOut-config.yml
sed -e 's/#//g' -e 's/ commented analysis components/# commented analysis components/g' /tmp/commented >> /tmp/tryItOut-config.yml
cat /tmp/after >> /tmp/tryItOut-config.yml

sudo aminer --config /tmp/tryItOut-config.yml > /dev/null &
sleep 5 & wait $!
sudo pkill -x aminer
exit_code=$?
rm /tmp/tryItOut-config.yml
rm /tmp/before
rm /tmp/after
rm /tmp/commented
sudo rm -r logdata-anomaly-miner.wiki
exit $exit_code
