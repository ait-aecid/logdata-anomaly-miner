sudo chown -R aminer:aminer /var/lib/aminer 2> /dev/null

# extract the file from the development branch of the wiki project.
# the first ```yaml script is searched for.
git clone https://github.com/ait-aecid/logdata-anomaly-miner.wiki.git 2> /dev/null
cd logdata-anomaly-miner.wiki 2> /dev/null
git checkout development > /dev/null 2>&1
cd ..
awk '/^```yaml$/ && ++n == 1, /^```$/' < logdata-anomaly-miner.wiki/Getting-started-\(tutorial\).md | sed '/^```/ d' | sed '/^```python/ d' > /tmp/gettingStarted-config.yml
sudo rm -r logdata-anomaly-miner.wiki

sudo aminer --config /tmp/gettingStarted-config.yml > /dev/null &
sleep 5 & wait $!
sudo pkill -x aminer
rm /tmp/gettingStarted-config.yml
exit_code=$?
exit $exit_code
