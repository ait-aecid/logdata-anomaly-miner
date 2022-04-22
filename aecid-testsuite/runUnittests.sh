source config

sudo cp unit/data/kafka-client.conf /etc/aminer/kafka-client.conf
curl $KAFKA_URL --output kafka.tgz
tar xvf kafka.tgz > /dev/null
rm kafka.tgz

$KAFKA_VERSIONSTRING/bin/zookeeper-server-start.sh $KAFKA_VERSIONSTRING/config/zookeeper.properties > /dev/null &
sleep 1
$KAFKA_VERSIONSTRING/bin/kafka-server-start.sh $KAFKA_VERSIONSTRING/config/server.properties > /dev/null &

exit_code=0
sudo python3 -bb -m unittest discover -s unit/analysis -p '*Test.py' > /dev/null &
ANALYSIS_PID=$!
sudo python3 -bb -m unittest discover -s unit/events -p '*Test.py' > /dev/null &
EVENTS_PID=$!
sudo python3 -bb -m unittest discover -s unit/input -p '*Test.py' > /dev/null &
INPUT_PID=$!
sudo python3 -bb -m unittest discover -s unit/parsing -p '*Test.py' > /dev/null &
PARSING_PID=$!
sudo python3 -bb -m unittest discover -s unit/util -p '*Test.py' > /dev/null &
UTIL_PID=$!
wait $ANALYSIS_PID
if [[ $? -ne 0 ]]; then
  exit_code=1
  echo "Failed in Analysis unittests."
fi
wait $PARSING_PID
if [[ $? -ne 0 ]]; then
  exit_code=1
  echo "Failed in Parsing unittests."
fi
wait $UTIL_PID
if [[ $? -ne 0 ]]; then
  exit_code=1
  echo "Failed in Util unittests."
fi
wait $INPUT_PID
if [[ $? -ne 0 ]]; then
  exit_code=1
  echo "Failed in Input unittests."
fi
wait $EVENTS_PID
if [[ $? -ne 0 ]]; then
  exit_code=1
  echo "Failed in Events unittests."
fi
test -e /var/mail/mail && sudo rm -f /var/mail/mail
sudo rm /tmp/test4unixSocket.sock
sudo rm /tmp/test5unixSocket.sock
sudo rm /tmp/test6unixSocket.sock
sudo rm -r /tmp/lib/aminer/*

$KAFKA_VERSIONSTRING/bin/kafka-server-stop.sh > /dev/null
$KAFKA_VERSIONSTRING/bin/zookeeper-server-stop.sh > /dev/null
sudo rm -r $KAFKA_VERSIONSTRING/
sudo rm -r /tmp/zookeeper
sudo rm -r /tmp/kafka-logs
sudo rm /etc/aminer/kafka-client.conf
exit $exit_code
