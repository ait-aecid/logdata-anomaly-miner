#!/bin/bash

function testConfigError() {
  RET=0
  if [[ !$# -eq 2  ]]; then
    echo echo "testConfigError() needs exactly 2 parameters!"
		return 1
	fi
	if [[ `grep -ic "VerboseUnparsedAtomHandler" $1` != 0 ]] || `grep -Fq "Traceback" $1` || `grep -Fq "{'Parser'" $1` || `grep -Fq "FATAL" $1` || `grep -Fq "Config-Error" $1`; then
      echo "$2"
	    RET=1
	    cat $1
	    echo
	    echo
  fi
	return $RET
}

function compareStrings() {
  RET=0
  if [[ !$# -eq 3  ]]; then
    echo echo "compareStrings() needs exactly 3 parameters!"
		return 1
	fi
	if [[ "$1" != "$2" ]]; then
    echo "$1"
    echo
    echo "$3"
    echo
    echo "$2"
    echo
    RET=1
  fi
  return $RET
}

function compareVersionStrings(){
  if [[ !$# -eq 2 ]]; then
    echo "compareVersionStrings() needs exactly 2 parameters!"
		return -1
	fi
  IFS='-' read -ra VERSION <<< "$1"
  VERSION="${VERSION[0]}"
  IFS='.' read -ra V1 <<< "$VERSION"
  IFS='-' read -ra VERSION <<< "$2"
	VERSION="${VERSION[0]}"
  IFS='.' read -ra V2 <<< "$VERSION"
  LEN1=${#V1[@]}
  LEN2=${#V2[@]}
  LEN=$(( LEN1 < LEN2 ? LEN1 : LEN2 )) # minimum length
  for ((i=0; i < $LEN; i++)); do
    if [[ "${V1[i]}" -lt "${V2[i]}" ]]; then
      return 2
    elif [[ "${V1[i]}" -gt "${V2[i]}" ]]; then
      return 1
    fi
  done
  return 0
}

function runAminerUntilEnd() {
  CMD=$1
  LOGFILE=$2
  REP_PATH=$3
  CFG_PATH=$4
  if [[ $CFG_PATH == *.py ]]; then
    echo "config_properties['Core.PersistencePeriod'] = 1" | sudo tee -a $CFG_PATH > /dev/null
  elif [[ $CFG_PATH == *.yml ]]; then
    echo "Core.PersistencePeriod: 1" | sudo tee -a $CFG_PATH > /dev/null
  else
    return 2
  fi
  sudo rm $REP_PATH 2> /dev/null
  if [ $# -ge 5 ]; then
    OUT=$5
    $CMD > $OUT &
  elif [ $# -eq 4 ]; then
    $CMD &
  fi
  PID=$!
  FILE_SIZE=`stat --printf="%s" $LOGFILE 2> /dev/null`
  IN=`cat $REP_PATH 2> /dev/null`
  IFS=',' read -ra ADDR <<< "$IN"
  CURRENT_SIZE=`echo ${ADDR[1]} | sed 's/ *$//g'` # trim all whitespaces
  CNTR=0
  while [[ ("$CURRENT_SIZE" != "$FILE_SIZE" || "$CURRENT_SIZE" == "") && $CNTR -lt 120 ]]; do
     sleep 1
     IN=`cat $REP_PATH 2> /dev/null`
     IFS=',' read -ra ADDR <<< "$IN"
     CURRENT_SIZE=`echo ${ADDR[1]} | sed 's/ *$//g'` # trim all whitespaces
     CNTR=$((++CNTR))
     echo $CURRENT_SIZE $FILE_SIZE $CNTR
  done
  sleep 3
  sudo sed -i '$d' $CFG_PATH # delete PersistencePeriod config in file.
  if [ $# -lt 6 ]; then
    sudo pkill -x aminer
    wait $PID
    RES=$?
    return $RES
  fi
  return $PID
}
