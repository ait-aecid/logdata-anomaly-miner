#!/bin/bash

exit_code=0
mypy /usr/lib/logdata-anomaly-miner/aminer/analysis/ --ignore-missing-imports --disable-error-code attr-defined --implicit-optional
exit_code=$(($exit_code + $?))
mypy /usr/lib/logdata-anomaly-miner/aminer/events/ --ignore-missing-imports --disable-error-code attr-defined --implicit-optional
exit_code=$(($exit_code + $?))
mypy /usr/lib/logdata-anomaly-miner/aminer/input/ --ignore-missing-imports --disable-error-code attr-defined --implicit-optional
exit_code=$(($exit_code + $?))
mypy /usr/lib/logdata-anomaly-miner/aminer/parsing/ --ignore-missing-imports --disable-error-code attr-defined --implicit-optional
exit_code=$(($exit_code + $?))
mypy /usr/lib/logdata-anomaly-miner/aminer/util/ --ignore-missing-imports --disable-error-code attr-defined --implicit-optional
exit_code=$(($exit_code + $?))
mypy /usr/lib/logdata-anomaly-miner/aminer/ --ignore-missing-imports --disable-error-code attr-defined --implicit-optional
exit_code=$(($exit_code + $?))
exit $exit_code
