#!/bin/bash

bandit -r /usr/lib/logdata-anomaly-miner --ini /home/aminer/logdata-anomaly-miner/.bandit
exit $?
