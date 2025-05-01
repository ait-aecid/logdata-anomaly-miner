#!/bin/bash

vulture /usr/lib/logdata-anomaly-miner --min-confidence=100 --exclude "/usr/lib/logdata-anomaly-miner/.venv/*"
exit $?
