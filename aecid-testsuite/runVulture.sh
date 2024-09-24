#!/bin/bash

vulture /usr/lib/logdata-anomaly-miner --min-confidence=100
exit $?
