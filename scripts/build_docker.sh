#!/bin/bash

scripts/addbuildid.sh

docker build -t aecid/logdata-anomaly-miner:latest -t aecid/logdata-anomaly-miner:$(grep '__version__ =' source/root/usr/lib/logdata-anomaly-miner/metadata.py | awk -F '"' '{print $2}') .
