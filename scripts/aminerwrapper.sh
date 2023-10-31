#!/bin/bash

AMINERDIR=/usr/lib/logdata-anomaly-miner

case "$1" in
	aminer)
		$AMINERDIR/aminer.py ${*:2}
		;;
	aminerremotecontrol)
		$AMINERDIR/aminerremotecontrol.py ${*:2}
		;;
        aminer-persistence)
		$AMINERDIR/aminer-persistence.py ${*:2}
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
		exit 1
		;;

esac

exit 0
