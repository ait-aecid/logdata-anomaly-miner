#!/bin/bash

python3 -m flake8 /usr/lib/logdata-anomaly-miner --config /home/aminer/logdata-anomaly-miner/.flake8
exit $?
