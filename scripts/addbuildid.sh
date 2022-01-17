#!/bin/sh

METAPATH="source/root/usr/lib/logdata-anomaly-miner/metadata.py"
DOCSCONF="docs/conf.py"

# fallback if git is not installed
if [ ! `command -v git` ]
then
	echo "Git is not installed. Won't set the BUILD_ID"
	exit 1
fi

BUILD_ID=`git describe --tags --long 2> /dev/null`

# fallback if this is not a git installation
if [ $? -ne 0 ]
then
	echo "This seems not to be a git installation."
	exit 1
fi

BUILD_ID=`echo $BUILD_ID | sed 's/^[Vv]//'`

echo "BUILD_ID: $BUILD_ID"

if [ -e $METAPATH ]
then
sed  -i  "s/__version__\s*=\s*\".*\"/__version__ = \"$BUILD_ID\"/g" $METAPATH
fi

if [ -e $DOCSCONF ]
then
sed  -i  "s/release\s*=\s*'.*'/release = '$BUILD_ID'/g" $DOCSCONF
fi

exit 0
