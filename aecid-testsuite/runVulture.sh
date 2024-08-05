#!/bin/bash

vulture /usr/lib/logdata-anomaly-miner --confidence=100
exit $?
