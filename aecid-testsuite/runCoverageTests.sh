curl https://mirror.klaus-uwe.me/apache/kafka/2.5.0/kafka_2.12-2.5.0.tgz --output kafka.tgz
tar xvf kafka.tgz > /dev/null
rm kafka.tgz

kafka_2.12-2.5.0/bin/zookeeper-server-start.sh kafka_2.12-2.5.0/config/zookeeper.properties > /dev/null &
sleep 1
kafka_2.12-2.5.0/bin/kafka-server-start.sh kafka_2.12-2.5.0/config/server.properties > /dev/null &

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
sudo rm /tmp/AMinerRemoteLog.txt
sudo rm /tmp/test4unixSocket.sock
sudo rm /tmp/test5unixSocket.sock
sudo rm /tmp/test6unixSocket.sock

kafka_2.12-2.5.0/bin/kafka-server-stop.sh > /dev/null
kafka_2.12-2.5.0/bin/zookeeper-server-stop.sh > /dev/null
sudo rm -r kafka_2.12-2.5.0/
sudo rm -r /tmp/zookeeper
sudo rm -r /tmp/kafka-logs
if [[ "$exit_code1" -ne 0 || "$exit_code2" -ne 0 ]]; then
	exit 1
fi
exit 0
