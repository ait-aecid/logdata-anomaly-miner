#!/bin/bash

. ./testFunctions.sh

METADATA_PATH=../source/root/usr/lib/logdata-anomaly-miner/metadata.py
CONF_PATH=../docs/conf.py
ls -la /home/aminer
echo "DDDD"
ls -la /home/aminer/source
version=$(grep "__version__ =" $METADATA_PATH)
version=$(sed 's/__version__ = //g' <<< $version)
version=$(sed 's/"//g' <<< $version)

release=$(grep "release =" $CONF_PATH)
release=$(sed "s/release = //g" <<< $release)
release=$(sed "s/'//g" <<< $release)

if [[ "$version" == "" || "$release" == "" ]]; then
  exit 1
fi

if [[ "$version" != "$release" ]]; then
  echo "Version $version not equal with $release."
  if [[ $# -eq 1 ]]; then
    if [[ "$1" != "-u" && "$1" != "--update" ]]; then
      echo "Unknown Parameter $1. Exiting.."
      exit 1
    else
      compareVersionStrings "$version" "$release"
      res=$?
      if [[ $res -eq 1 ]]; then
        sed -i "s/release = '$release'/release = '$version'/g" $CONF_PATH
        echo "Updated version string in $CONF_PATH from $release to $version."
      elif [[ $res -eq 2 ]]; then
        sed -i "s/__version__ = \"$version\"/__version__ = \"$release\"/g" $METADATA_PATH
        echo "Updated version string in $METADATA_PATH from $version to $release."
      fi
    fi
  fi
  exit 1
fi

