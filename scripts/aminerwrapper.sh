#!/bin/bash

AMINERDIR=/usr/lib/logdata-anomaly-miner
program=$(basename $0)

case "$program" in
	aminer)
	  source $AMINERDIR/.venv/bin/activate
		$AMINERDIR/aminer.py ${*:1}
		deactivate
		;;
	aminerremotecontrol)
	  source $AMINERDIR/.venv/bin/activate
		$AMINERDIR/aminerremotecontrol.py ${*:1}
		deactivate
		;;
  aminer-persistence)
	  source $AMINERDIR/.venv/bin/activate
		$AMINERDIR/aminer-persistence.py ${*:1}
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
		echo "$program"
		exit 1
		;;

esac

exit 0
