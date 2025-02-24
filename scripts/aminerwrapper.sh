#!/bin/bash

AMINERDIR=/usr/lib/logdata-anomaly-miner

case "$1" in
	aminer)
	  $AMINERDIR/.venv/bin/activate
		$AMINERDIR/aminer.py ${*:2}
		deactivate
		;;
	aminerremotecontrol)
	  $AMINERDIR/.venv/bin/activate
		$AMINERDIR/aminerremotecontrol.py ${*:2}
		deactivate
		;;
    aminer-persistence)
	  $AMINERDIR/.venv/bin/activate
		$AMINERDIR/aminer-persistence.py ${*:2}
		deactivate
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
