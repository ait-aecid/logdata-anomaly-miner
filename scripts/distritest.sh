#!/bin/bash

sudo sed -i '/imklog/s/^/#/' /etc/rsyslog.conf
sudo rsyslogd
sudo service apache2 start
curl localhost
curl -XPOST localhost
curl -I localhost
sudo chown aminer:aminer /var/lib/aminer
sudo chmod 700 /var/lib/aminer
sudo timeout --preserve-status 20s aminer --config /home/aminer/gettingStarted-config.yml
exit $?
