source config

sudo cp unit/data/kafka-client.conf /etc/aminer/kafka-client.conf
curl $KAFKA_URL --output kafka.tgz
tar xvf kafka.tgz > /dev/null
rm kafka.tgz

$KAFKA_VERSIONSTRING/bin/zookeeper-server-start.sh $KAFKA_VERSIONSTRING/config/zookeeper.properties > /dev/null &
sleep 1
$KAFKA_VERSIONSTRING/bin/kafka-server-start.sh $KAFKA_VERSIONSTRING/config/server.properties > /dev/null &

sudo python3 -m unittest discover -s unit -p '*Test.py' > /dev/null
exit_code=$?
test -e /var/mail/mail && sudo rm -f /var/mail/mail
sudo rm /tmp/test4unixSocket.sock
sudo rm /tmp/test5unixSocket.sock
sudo rm /tmp/test6unixSocket.sock

$KAFKA_VERSIONSTRING/bin/kafka-server-stop.sh > /dev/null
$KAFKA_VERSIONSTRING/bin/zookeeper-server-stop.sh > /dev/null
sudo rm -r $KAFKA_VERSIONSTRING/
sudo rm -r /tmp/zookeeper
sudo rm -r /tmp/kafka-logs
sudo rm /etc/aminer/kafka-client.conf
exit $exit_code
