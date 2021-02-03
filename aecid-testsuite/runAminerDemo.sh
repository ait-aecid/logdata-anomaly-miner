sudo cp unit/config/kafka_client.conf /etc/aminer/kafka-client.conf
if [[ $1 == *.py ]]; then
    cp $1 /tmp/demo-config.py
    sudo chown aminer:aminer /tmp/demo-config.py 2> /dev/null
elif [[ $1 == *.yml ]]; then
    cp $1 /tmp/demo-config.yml
    sudo chown aminer:aminer /tmp/demo-config.yml 2> /dev/null
else
    exit 2
fi
sudo chown -R aminer:aminer /tmp/lib 2> /dev/null
sudo chmod +x demo/aminer/aminerDemo.sh
sudo ./demo/aminer/aminerDemo.sh > /dev/null
exit_code=$?
sudo rm /tmp/demo-config.py 2> /dev/null
sudo rm /tmp/demo-config.yml 2> /dev/null
sudo rm /tmp/syslog
exit $exit_code
