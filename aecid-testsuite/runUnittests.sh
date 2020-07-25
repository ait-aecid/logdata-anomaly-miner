curl https://mirror.klaus-uwe.me/apache/kafka/2.5.0/kafka_2.12-2.5.0.tgz --output kafka.tgz
tar xvf kafka.tgz > /dev/null
rm kafka.tgz

kafka_2.12-2.5.0/bin/zookeeper-server-start.sh kafka_2.12-2.5.0/config/zookeeper.properties > /dev/null &
sleep 1
kafka_2.12-2.5.0/bin/kafka-server-start.sh kafka_2.12-2.5.0/config/server.properties > /dev/null &

sudo python3 -m unittest discover -s unit -p '*Test.py' > /dev/null
exit_code=$?
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
exit $exit_code
