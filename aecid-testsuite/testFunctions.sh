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