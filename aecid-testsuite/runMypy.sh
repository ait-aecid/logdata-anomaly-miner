exit_code=0
mypy ../source/root/usr/lib/logdata-anomaly-miner/aminer/analysis/ --ignore-missing-imports
exit_code=$(($exit_code + $?))
mypy ../source/root/usr/lib/logdata-anomaly-miner/aminer/events/ --ignore-missing-imports
exit_code=$(($exit_code + $?))
mypy ../source/root/usr/lib/logdata-anomaly-miner/aminer/input/ --ignore-missing-imports
exit_code=$(($exit_code + $?))
mypy ../source/root/usr/lib/logdata-anomaly-miner/aminer/parsing/ --ignore-missing-imports
exit_code=$(($exit_code + $?))
mypy ../source/root/usr/lib/logdata-anomaly-miner/aminer/util/ --ignore-missing-imports
exit_code=$(($exit_code + $?))
mypy ../source/root/usr/lib/logdata-anomaly-miner/aminer/ --ignore-missing-imports
exit_code=$(($exit_code + $?))
exit $exit_code
