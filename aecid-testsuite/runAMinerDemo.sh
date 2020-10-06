if [[ $1 == *.py ]]; then
    cp $1 /tmp/demo-config.py
elif [[ $1 == *.yml ]]; then
    cp $1 /tmp/demo-config.yml
else
    exit 2
fi
sudo chown aminer:aminer /tmp/demo-config.py
sudo chown -R aminer:aminer /tmp/lib
sudo chmod +x demo/AMiner/aminerDemo.sh
sudo -u aminer ./demo/AMiner/aminerDemo.sh > /tmp/demo
exit_code=$?
sudo rm /tmp/demo-config.py
sudo rm /tmp/demo
sudo rm /tmp/syslog
sudo rm /tmp/AMinerRemoteLog.txt
exit $exit_code
