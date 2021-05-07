#!/usr/bin/bash

BRANCH=$1
SOURCE=$2
DEST=$3

case $BRANCH in
	development)
		test -d $DEST/development && rm -rf $DEST/development
		cp -r $SOURCE $DEST/development
		;;
	main)
		VERSION=$(grep '__version__ =' source/root/usr/lib/logdata-anomaly-miner/metadata.py | awk -F '"' '{print $2}')
		if [ $(echo $VERSION | grep -P "\d+\.\d+\.\d+") ]
		then
		    test -d $DEST/$VERSION && rm -rf $DEST/$VERSION
		    cp -r $SOURCE $DEST/$VERSION
		    test -e $DEST/current && unlink $DEST/current
		    ln -s $DEST/$VERSION $DEST/current
		else
			echo "Unable to identify the aminer-version!"
			exit 1
		fi
		;;
	*)
		echo "usage: $0 main|development"
		exit 1
		;;
esac

exit 0
