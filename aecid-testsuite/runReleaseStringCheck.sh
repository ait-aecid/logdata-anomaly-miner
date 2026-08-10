#!/bin/bash

METADATA_PATH=../source/root/usr/lib/logdata-anomaly-miner/metadata.py

version=$(grep "__version__ =" $METADATA_PATH)
version=$(sed 's/__version__ = //g' <<< $version)
version=$(sed 's/"//g' <<< $version)

if [[ "$version" == "" ]]; then
  echo "Could not find a version string in $METADATA_PATH."
  exit 1
fi
