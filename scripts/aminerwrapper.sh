#!/bin/bash

AMINERDIR=/usr/lib/logdata-anomaly-miner

case "$1" in
	aminer)
		$AMINERDIR/aminer.py ${*:2}
		;;
	aminerremotecontrol)
		$AMINERDIR/aminerremotecontrol.py ${*:2}
		;;
	*)
		echo "Usage: [ aminer | aminerremotecontrol ] <options>"
		exit 1
		;;
        
esac

exit 0
