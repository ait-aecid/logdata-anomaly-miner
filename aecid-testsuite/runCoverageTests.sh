source config

curl $KAFKA_URL --output kafka.tgz
tar xvf kafka.tgz > /dev/null
rm kafka.tgz

$KAFKA_VERSIONSTRING/bin/zookeeper-server-start.sh $KAFKA_VERSIONSTRING/config/zookeeper.properties > /dev/null &
sleep 1
$KAFKA_VERSIONSTRING/bin/kafka-server-start.sh $KAFKA_VERSIONSTRING/config/server.properties > /dev/null &

sudo coverage run --source=./aminer -m unittest discover -s unit -p '*Test.py' > /dev/null
exit_code1=$?
touch /tmp/report
echo 'Statement Coverage:' > /tmp/report
sudo coverage report >> /tmp/report
sudo coverage run --source=./aminer --branch -m unittest discover -s unit -p '*Test.py' > /dev/null
exit_code2=$?
echo 'Branch Coverage:' >> /tmp/report
sudo coverage report >> /tmp/report
cat /tmp/report
rm /tmp/report
test -e /var/mail/mail && sudo rm -f /var/mail/mail
sudo rm /tmp/test4unixSocket.sock
sudo rm /tmp/test5unixSocket.sock
sudo rm /tmp/test6unixSocket.sock

$KAFKA_VERSIONSTRING/bin/kafka-server-stop.sh > /dev/null
$KAFKA_VERSIONSTRING/bin/zookeeper-server-stop.sh > /dev/null
sudo rm -r $KAFKA_VERSIONSTRING/
sudo rm -r /tmp/zookeeper
sudo rm -r /tmp/kafka-logs
if [[ "$exit_code1" -ne 0 || "$exit_code2" -ne 0 ]]; then
	exit 1
fi
exit 0
