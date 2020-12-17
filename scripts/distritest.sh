#!/bin/bash

sudo service rsyslog start
sudo service apache2 start
curl localhost
curl -XPOST localhost
curl -I localhost
sudo timeout 20s aminer --config /home/aminer/gettingStarted-config.yml
