curl https://mirror.klaus-uwe.me/apache/kafka/2.5.0/kafka_2.12-2.5.0.tgz --output kafka.tgz
tar xvf kafka.tgz
rm kafka.tgz
bin/zookeeper-server-start.sh config/zookeeper.properties &
sleep 1
bin/kafka-server-start.sh config/server.properties &

sudo python3 -m unittest discover -s unit -p '*Test.py' > /dev/null
test -e /var/mail/mail && sudo rm -f /var/mail/mail
sudo rm /tmp/AMinerRemoteLog.txt
sudo rm /tmp/test4unixSocket.sock
sudo rm /tmp/test5unixSocket.sock
sudo rm /tmp/test6unixSocket.sock

bin/kafka-server-stop.sh
bin/zookeeper-server-stop.sh
