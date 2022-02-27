#!/bin/bash

. ./testFunctions.sh

sudo mkdir /tmp/lib 2> /dev/null
sudo mkdir /tmp/lib/aminer 2> /dev/null
sudo chown -R $USER:$USER /tmp/lib/aminer 2> /dev/null
sudo rm -r /tmp/lib/aminer/* 2> /dev/null
sudo mkdir /tmp/lib/aminer/log 2> /dev/null
sudo chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null

echo "Demo started.."
echo ""

FILE=$1
if ! test -f "$FILE"; then
  echo "$FILE does not exist!"
	exit 1
fi

FOUND=false
LOGFILE=""
while read p; do
  if [[ $FOUND = true ]]; then
    LOGFILE="$p"
    break
  fi
  if [[ "$p" == "LogResourceList:" ]]; then
    FOUND=true
  fi
done < $FILE
IFS="'" read -ra ADDR <<< "$LOGFILE"
LOGFILE="${ADDR[1]:7}"  # remove the file:// prefix.

runAminerUntilEnd "sudo aminer --config $FILE" "$LOGFILE" "/tmp/lib/aminer/AnalysisChild/RepositioningData" "$FILE"
exit $?