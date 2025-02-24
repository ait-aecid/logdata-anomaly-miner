#!/bin/bash

AMINERDIR=/usr/lib/logdata-anomaly-miner
program=$(basename $0)

case "$program" in
	aminer)
		$AMINERDIR/.venv/bin/python3 $AMINERDIR/aminer.py "${@:1}"
		;;
	aminerremotecontrol)
		$AMINERDIR/.venv/bin/python3 $AMINERDIR/aminerremotecontrol.py "${@:1}"
		;;
  aminer-persistence)
		$AMINERDIR/.venv/bin/python3 $AMINERDIR/aminer-persistence.py "${@:1}"
		;;
	supervisor)
		/usr/bin/supervisord
		;;
	mkdocs)
		cd /docs
		make html
		;;
	*)
		echo "Usage: [ aminer | aminerremotecontrol | aminer-persistence | supervisor | mkdocs ] <options>"
		echo "$program"
		exit 1
		;;

esac

exit 0
