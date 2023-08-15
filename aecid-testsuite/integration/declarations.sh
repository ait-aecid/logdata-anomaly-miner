#!/bin/bash

source ../config

# declare all expected values without the variable ones. These arrays are used to compare with the incoming log lines.
declare -a NEW_PATH_HD_REPAIR_1=(" New path(es) detected" "NewMatchPathDetector: \"NewPath\" (1 lines)" "  /model/DiskUpgrade: " ": System rebooted for hard disk upgrade" "  /model/DiskUpgrade/DTM: " "  /model/DiskUpgrade/UNameSpace1: " "  /model/DiskUpgrade/UName: " "  /model/DiskUpgrade/UNameSpace2: " " /model/DiskUpgrade/User: " "  /model/DiskUpgrade/HDRepair:  System rebooted for hard disk upgrade" "['/model/DiskUpgrade', '/model/DiskUpgrade/DTM', '/model/DiskUpgrade/UNameSpace1', '/model/DiskUpgrade/UName', '/model/DiskUpgrade/UNameSpace2', '/model/DiskUpgrade/User', '/model/DiskUpgrade/HDRepair']" "Original log line: ")
declare -a UNPARSED_ATOM_1=(" Unparsed atom received" "SimpleUnparsedAtomHandler: \"UnparsedHandler\" (1 lines)" " System rebooted for hard disk upgrad")
declare -a UNPARSED_ATOM_2=(" Unparsed atom received" "SimpleUnparsedAtomHandler: \"UnparsedHandler\" (1 lines)" ": System rebooted for hard disk upgrade")
declare -a NEW_PATH_HOME_PATH_ROOT_1=(" New path(es) detected" "NewMatchPathDetector: \"NewPath\" (1 lines)" "  /model/HomePath: The Path of the home directory shown by pwd of the user root is: /root" "  /model/HomePath/Pwd: The Path of the home directory shown by pwd of the user " "  /model/HomePath/Username: root" "  /model/HomePath/Is:  is: " "  /model/HomePath/Path: /root" "['/model/HomePath', '/model/HomePath/Pwd', '/model/HomePath/Username', '/model/HomePath/Is', '/model/HomePath/Path']" "Original log line: The Path of the home directory shown by pwd of the user root is: /root")
declare -a NEW_VALUE_COMBINATION_HOME_PATH_ROOT_1=(" New value combination(s) detected" "NewMatchPathValueComboDetector: \"NewValueCombo\" (1 lines)" "(b'root', b'/root')" "Original log line: The Path of the home directory shown by pwd of the user root is: /root")
declare -a NEW_VALUE_COMBINATION_HOME_PATH_USER_1=(" New value combination(s) detected" "NewMatchPathValueComboDetector: \"NewValueCombo\" (1 lines)" "(b'user', b'/home/user')" "Original log line: The Path of the home directory shown by pwd of the user user is: /home/user")
declare -a NEW_VALUE_COMBINATION_HOME_PATH_GUEST_1=(" New value combination(s) detected" "NewMatchPathValueComboDetector: \"NewValueCombo\" (1 lines)" "(b'guest', b'/home/guest')" "Original log line: The Path of the home directory shown by pwd of the user guest is: /home/guest")
declare -a JSON_OUTPUT=()
read -r -d '' VAR << END
  {
  "LogData": {
    "RawLogData": [
      "
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
 localhost root: System rebooted for hard disk upgrad"
    ],
    "Timestamps": [
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
    ],
    "DetectionTimestamp":
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
,
    "LogLinesCount": 1
  },
  "AnalysisComponent": {
    "AnalysisComponentIdentifier": 0,
    "AnalysisComponentType": "SimpleUnparsedAtomHandler",
    "AnalysisComponentName": "UnparsedHandler",
    "Message": "Unparsed atom received",
    "PersistenceFileName": null,
    "LogResource": "file:///tmp/syslog"
  }
}
{
  "AnalysisComponent": {
    "AnalysisComponentIdentifier": 1,
    "AnalysisComponentType": "NewMatchPathDetector",
    "AnalysisComponentName": "NewPath",
    "Message": "New path(es) detected",
    "PersistenceFileName": "Default",
    "TrainingMode": true,
    "AffectedLogAtomPaths": [
      "/model/DiskUpgrade",
      "/model/DiskUpgrade/DTM",
      "/model/DiskUpgrade/UNameSpace1",
      "/model/DiskUpgrade/UName",
      "/model/DiskUpgrade/UNameSpace2",
      "/model/DiskUpgrade/User",
      "/model/DiskUpgrade/HDRepair"
    ],
    "LogResource": "file:///tmp/auth.log"
  },
  "LogData": {
    "RawLogData": [
      "
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
 localhost root: System rebooted for hard disk upgrade"
    ],
    "Timestamps": [
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
    ],
    "DetectionTimestamp":
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
,
    "LogLinesCount": 1,
    "AnnotatedMatchElement": {
      "/model/DiskUpgrade": "
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
",
      "/model/DiskUpgrade/DTM": "
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
      "/model/DiskUpgrade/UNameSpace1": " ",
      "/model/DiskUpgrade/UName": "localhost",
      "/model/DiskUpgrade/UNameSpace2": " ",
      "/model/DiskUpgrade/User": "root:",
      "/model/DiskUpgrade/HDRepair": " System rebooted for hard disk upgrade"
    }
  }
}
{
  "LogData": {
    "RawLogData": [
      "
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
 localhost root: System rebooted for hard disk upgrad"
    ],
    "Timestamps": [
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
    ],
    "DetectionTimestamp":
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
,
    "LogLinesCount": 1
  },
  "AnalysisComponent": {
    "AnalysisComponentIdentifier": 0,
    "AnalysisComponentType": "SimpleUnparsedAtomHandler",
    "AnalysisComponentName": "UnparsedHandler",
    "Message": "Unparsed atom received",
    "PersistenceFileName": null,
    "LogResource": "file:///tmp/auth.log"
  }
}
{
  "LogData": {
    "RawLogData": [
      "
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
 localhost root: System rebooted for hard disk upgrade"
    ],
    "Timestamps": [
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
    ],
    "DetectionTimestamp":
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
,
    "LogLinesCount": 1
  },
  "AnalysisComponent": {
    "AnalysisComponentIdentifier": 0,
    "AnalysisComponentType": "SimpleUnparsedAtomHandler",
    "AnalysisComponentName": "UnparsedHandler",
    "Message": "Unparsed atom received",
    "PersistenceFileName": null,
    "LogResource": "file:///tmp/syslog"
  }
}
{
  "AnalysisComponent": {
    "AnalysisComponentIdentifier": 1,
    "AnalysisComponentType": "NewMatchPathDetector",
    "AnalysisComponentName": "NewPath",
    "Message": "New path(es) detected",
    "PersistenceFileName": "Default",
    "TrainingMode": true,
    "AffectedLogAtomPaths": [
      "/model/HomePath",
      "/model/HomePath/Pwd",
      "/model/HomePath/Username",
      "/model/HomePath/Is",
      "/model/HomePath/Path"
    ],
    "LogResource": "file:///tmp/auth.log"
  },
  "LogData": {
    "RawLogData": [
      "The Path of the home directory shown by pwd of the user root is: /root"
    ],
    "Timestamps": [
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
    ],
    "DetectionTimestamp":
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
,
    "LogLinesCount": 1,
    "AnnotatedMatchElement": {
      "/model/HomePath": "The Path of the home directory shown by pwd of the user root is: /root",
      "/model/HomePath/Pwd": "The Path of the home directory shown by pwd of the user ",
      "/model/HomePath/Username": "root",
      "/model/HomePath/Is": " is: ",
      "/model/HomePath/Path": "/root"
    }
  }
}
{
  "AnalysisComponent": {
    "AnalysisComponentIdentifier": 2,
    "AnalysisComponentType": "NewMatchPathValueComboDetector",
    "AnalysisComponentName": "NewValueCombo",
    "Message": "New value combination(s) detected",
    "PersistenceFileName": "Default",
    "TrainingMode": true,
    "AffectedLogAtomPaths": [
      "/model/HomePath/Username",
      "/model/HomePath/Path"
    ],
    "AffectedLogAtomValues": [
      "root",
      "/root"
    ],
    "LogResource": "file:///tmp/auth.log"
  },
  "LogData": {
    "RawLogData": [
      "The Path of the home directory shown by pwd of the user root is: /root"
    ],
    "Timestamps": [
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
    ],
    "DetectionTimestamp":
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
,
    "LogLinesCount": 1,
    "AnnotatedMatchElement": {
      "/model/HomePath": "The Path of the home directory shown by pwd of the user root is: /root",
      "/model/HomePath/Pwd": "The Path of the home directory shown by pwd of the user ",
      "/model/HomePath/Username": "root",
      "/model/HomePath/Is": " is: ",
      "/model/HomePath/Path": "/root"
    }
  }
}
{
  "AnalysisComponent": {
    "AnalysisComponentIdentifier": 2,
    "AnalysisComponentType": "NewMatchPathValueComboDetector",
    "AnalysisComponentName": "NewValueCombo",
    "Message": "New value combination(s) detected",
    "PersistenceFileName": "Default",
    "TrainingMode": true,
    "AffectedLogAtomPaths": [
      "/model/HomePath/Username",
      "/model/HomePath/Path"
    ],
    "AffectedLogAtomValues": [
      "user",
      "/home/user"
    ],
    "LogResource": "file:///tmp/syslog"
  },
  "LogData": {
    "RawLogData": [
      "The Path of the home directory shown by pwd of the user user is: /home/user"
    ],
    "Timestamps": [
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
    ],
    "DetectionTimestamp":
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
,
    "LogLinesCount": 1,
    "AnnotatedMatchElement": {
      "/model/HomePath": "The Path of the home directory shown by pwd of the user user is: /home/user",
      "/model/HomePath/Pwd": "The Path of the home directory shown by pwd of the user ",
      "/model/HomePath/Username": "user",
      "/model/HomePath/Is": " is: ",
      "/model/HomePath/Path": "/home/user"
    }
  }
}
{
  "AnalysisComponent": {
    "AnalysisComponentIdentifier": 2,
    "AnalysisComponentType": "NewMatchPathValueComboDetector",
    "AnalysisComponentName": "NewValueCombo",
    "Message": "New value combination(s) detected",
    "PersistenceFileName": "Default",
    "TrainingMode": true,
    "AffectedLogAtomPaths": [
      "/model/HomePath/Username",
      "/model/HomePath/Path"
    ],
    "AffectedLogAtomValues": [
      "guest",
      "/home/guest"
    ],
    "LogResource": "file:///tmp/auth.log"
  },
  "LogData": {
    "RawLogData": [
      "The Path of the home directory shown by pwd of the user guest is: /home/guest"
    ],
    "Timestamps": [
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
    ],
    "DetectionTimestamp":
END
JSON_OUTPUT+=("$VAR")
read -r -d '' VAR << END
,
    "LogLinesCount": 1,
    "AnnotatedMatchElement": {
      "/model/HomePath": "The Path of the home directory shown by pwd of the user guest is: /home/guest",
      "/model/HomePath/Pwd": "The Path of the home directory shown by pwd of the user ",
      "/model/HomePath/Username": "guest",
      "/model/HomePath/Is": " is: ",
      "/model/HomePath/Path": "/home/guest"
    }
  }
}
END
JSON_OUTPUT+=("$VAR")

# These strings are used in the isExpectedOutput()-function to identify the next array to be compared with.
NEW_PATH_HD_REPAIR="new_path_hd_repair"
UNPARSED_ATOM_HD_REPAIR="unparsed_atom_hd_repair"
UNPARSED_ATOM_DATE_TIME="unparsed_atom_date_time"
UNPARSED_ATOM_UNAME="unparsed_atom_uname"
NEW_PATH_HOME_PATH_ROOT="new_path_home_path_root"
NEW_VALUE_COMBINATION_HOME_PATH_ROOT="new_value_combination_home_path_root"
NEW_VALUE_COMBINATION_HOME_PATH_USER="new_value_combination_home_path_user"
NEW_VALUE_COMBINATION_HOME_PATH_GUEST="new_value_combination_home_path_guest"
COUNTER=0

# This function checks if the input value starts with a date of the format YYYY-mm-dd HH:MM:SS.
# $1 = String parameter to check
function isDate() {
	if [[ $# -gt 0 && "$1" =~ [0-9]{4}\-[0-9]{2}\-[0-9]{2}\ [0-9]{2}:[0-9]{2}:[0-9]{2}* ]]; then
		return 0
	fi
	return 1
}

# This function checks if the input value contains the local UName.
# $1 = String parameter to check
function isUname() {
	if [[ $# -gt 0 && "$1" == *" `cat /etc/hostname`"* ]]; then
		return 0
	fi
	return 1
}

# This function checks if the input value contains name of the currently logged in user.
# $1 = String parameter to check
function isUser() {
	if [[ $# -gt 0 && "$1" == *" ` id -u -n`:"* ]]; then
		return 0
	fi
	return 1
}

# This function checks if the input value starts with a date followed by the local UName and the name of the currently logged in user.
# The return values vary depending at which point the error occurs.
# $1 = String parameter to check
function startswithPredefinedMarkers() {
	if [ $# -eq 0 ]; then
		return 1
	fi
	isDate "$1"
	if [ $? != 0 ]; then
		return 2
	fi
	isUname "$1"
	if [ $? != 0 ]; then
		return 3
	fi
	isUser "$1"
	if [ $? != 0 ]; then
		return 4
	fi
	return 0
}

# This function reads the output of the aminer, which is saved at /tmp/output, until an empty line occurs.
# Every time a paragraph was read, the global variable $COUNTER is set to the iteration variable $i.
# On the next call of this function all lines until $i equals $COUNTER are skipped.
# $1 = String identifier for the expected values
# $2 = Prefix position
function isExpectedOutput() {
	before=$COUNTER
	i=0
	temp=0

	#ADD HERE
	if [[ $# -gt 0 && $1 == $NEW_PATH_HD_REPAIR ]]; then
		EXPECTED=("${NEW_PATH_HD_REPAIR_1[@]}")
	elif [[ $# -gt 0 && $1 == $UNPARSED_ATOM_HD_REPAIR ]]; then
		EXPECTED=("${UNPARSED_ATOM_1[@]}")
	elif [[ $# -gt 0 && $1 == $UNPARSED_ATOM_DATE_TIME ]]; then
		EXPECTED=("${UNPARSED_ATOM_2[@]}")
	elif [[ $# -gt 0 && $1 == $UNPARSED_ATOM_UNAME ]]; then
		EXPECTED=("${UNPARSED_ATOM_2[@]}")
	elif [[ $# -gt 0 && $1 == $NEW_PATH_HOME_PATH_ROOT ]]; then
		EXPECTED=("${NEW_PATH_HOME_PATH_ROOT_1[@]}")
	elif [[ $# -gt 0 && $1 == $NEW_VALUE_COMBINATION_HOME_PATH_ROOT ]]; then
		EXPECTED=("${NEW_VALUE_COMBINATION_HOME_PATH_ROOT_1[@]}")
	elif [[ $# -gt 0 && $1 == $NEW_VALUE_COMBINATION_HOME_PATH_USER ]]; then
		EXPECTED=("${NEW_VALUE_COMBINATION_HOME_PATH_USER_1[@]}")
	elif [[ $# -gt 0 && $1 == $NEW_VALUE_COMBINATION_HOME_PATH_GUEST ]]; then
		EXPECTED=("${NEW_VALUE_COMBINATION_HOME_PATH_GUEST_1[@]}")
	else
		echo "No valid expected value found!"
		return 1
	fi
	input="/tmp/output"
	while IFS= read -r line
	do
		#echo "i $i"
		# Skip already processed lines.
		if [ $i -lt $COUNTER ]; then
			i=$((i + 1))
			continue
		# Paragraphs always terminate with an empty line. This line also must be skipped.
		elif [[ $i -eq $COUNTER && $line == "" ]]; then
			i=$((i + 1))
			temp=1
			continue
		fi
		#echo "$line"
		# Every paragraph must start with an date of the format YYYY-mm-dd HH:MM:SS.
		if [ `expr $i - $COUNTER - $temp` -eq 0 ]; then
			isDate "$line"
			ret=$?
			if [[ $? != 0 ]]; then
				echo "isDate() return value: $ret"
				return 2
			fi
		fi
		# When the prefix position is reached, the predefined markers are checked (date -> uname -> user).
		# To avoid this check, just use an negative or too high value for the prefix position.
		if [ `expr $i - $before - $temp` -eq $2 ]; then
			startswithPredefinedMarkers "$line"
			ret=$?
			#echo startswith $?
			if [[ $ret != 0 ]]; then
				echo "Startswith() return value: $ret"
				return 2
			fi
		fi
		# At the end of an paragraph stop reading the file and go to return from the function.
  		if [ "$line" == "" ]; then
			break
		# When the current line contains the expected value at the expected position,
		# read until the following values do not match or the EXPECTED array ends.
		elif [[ "$line" == *"${EXPECTED[$i - $before - $temp]}"* ]]; then
			i=$((i + 1))
			while [[ "$line" == *"${EXPECTED[$i - $before - $temp]}"* && "${EXPECTED[$i - $before - $temp]}" != "" ]]
			do
				i=$((i + 1))
			done
		# An error occured, when the line does not match or is not empty.
		else
			echo "line: $line"
			echo "expected: ${EXPECTED[$i - $before - $temp]}"
			return 2
  		fi
	done < "$input"
	COUNTER=$i
	# Check if all elements of the EXPECTED array were processed.
	if [ `expr $i - $before - $temp` == "${#EXPECTED[@]}" ]; then
		return 0
	fi
	return 3
}

# This function checks if the output of the StreamPrinterEventHandler is as expected.
# The order of the events is fixed and must be expanded every time a new log line is added to the integration test.
function checkAllOutputs() {
	res=0

	isExpectedOutput $UNPARSED_ATOM_HD_REPAIR 2
	ret=$?
	if [ $ret == 0 ]; then
		echo "Unparsed Atom found as expected."
	else
		echo "Expected Unparsed Atom was not found! Return value: $ret"
		res=1
		echo ""
	fi

	isExpectedOutput $NEW_PATH_HD_REPAIR -1
	ret=$?
	if [ $ret == 0 ]; then
		echo "NewMatchPath found as expected."
	else
		echo "Expected NewMatchPath was not found! Return value: $ret"
		res=1
		echo ""
	fi

	isExpectedOutput $UNPARSED_ATOM_HD_REPAIR 2
	ret=$?
	if [ $ret == 0 ]; then
		echo "Unparsed Atom found as expected."
	else
		echo "Expected Unparsed Atom was not found! Return value: $ret"
		res=1
		echo ""
	fi

	isExpectedOutput $UNPARSED_ATOM_UNAME -1
	ret=$?
	if [ $ret == 0 ]; then
		echo "Unparsed Atom found as expected."
	else
		echo "Expected Unparsed Atom was not found! Return value: $ret"
		res=1
		echo ""
	fi

	isExpectedOutput $NEW_PATH_HOME_PATH_ROOT -1
	ret=$?
	if [ $ret == 0 ]; then
		echo "NewMatchPath found as expected."
	else
		echo "Expected NewMatchPath was not found! Return value: $ret"
		res=1
		echo ""
	fi

	isExpectedOutput $NEW_VALUE_COMBINATION_HOME_PATH_ROOT -1
	ret=$?
	if [ $ret == 0 ]; then
		echo "NewValueCombination found as expected."
	else
		echo "Expected NewValueCombination was not found! Return value: $ret"
		res=1
		echo ""
	fi

	isExpectedOutput $NEW_VALUE_COMBINATION_HOME_PATH_USER -1
	ret=$?
	if [ $ret == 0 ]; then
		echo "NewValueCombination found as expected."
	else
		echo "Expected NewValueCombination was not found! Return value: $ret"
		res=1
		echo ""
	fi

	isExpectedOutput $NEW_VALUE_COMBINATION_HOME_PATH_GUEST -1
	ret=$?
	if [ $ret == 0 ]; then
		echo "NewValueCombination found as expected."
	else
		echo "Expected NewValueCombination was not found! Return value: $ret"
		res=1
		echo ""
	fi

	#ADD HERE
	return $res
}

# This function checks if the output of the DefaultMailNotificationEventHandler is as expected.
# The $linecount variable is the fixed count of log lines and must be changed every time a new log line is added.
# At each loop run one mail is read into /tmp/out from which further checks are made.
function checkAllMails() {
	res=0
	linecount=10

	dpkg -s mailutils &> /dev/null
	if [ ! $? -eq 0 ]; then
    	echo -e "\e[31mMailutils-package is not installed! Installing it now..]"
		sudo apt install mailutils -y
	fi

	echo ""
	echo "waiting for mails to arrive.."
	echo ""

	i=1
	while [ $i -lt $linecount ]
	do
		sudo echo p | mail > /tmp/out
		input="/tmp/out"
		t=false
		aminerMail=false
		while IFS= read -r searched
		do
			# Between all mail headers and the content and after the content of the mail always is an empty line.
			# The paragraph found in the content must also be found in the previously created /tmp/output file.
			if [ "$searched" == "" ]; then
				if [ $t == false ]; then
					t=true
				else
					break
				fi
			fi
			# If the first empty line was found and the subject equals "aminer Alerts:" the following paragraph
			# must be found in the previously created /tmp/output file.
			if [[ $t == true && $aminerMail == true ]]; then

				expected="/tmp/output"
				found=false
				while IFS= read -r line
				do
					if [[ "$line" == "$searched" ]]; then
						found=true
						break
					fi
				done < "$expected"
			# Set the aminerMail boolean to True, when the expected subject was found
			elif [[ "$searched" == *"Subject: aminer Alerts:"* ]]; then
				#echo "Subject found!"
				aminerMail=true
			# Stop searching, when the subject is not the expected aminer subject.
			elif [[ "$searched" != *"Subject: aminer Alerts:"* && "$searched" == *"Subject:"* ]]; then
				echo "wrong mail"
				i=$(($i-1))
				break
			fi
			# If the time is lesser than the start time of the integration test, an old mail is found.
			if [[ "$searched" == *"Date: "* ]]; then
				d="${searched:6}"
				dat=`date -d "$d" +%s`
				if [[ $dat -lt $time ]]; then
					echo "old mail"
					i=$(($i-1))
					break
				fi
			fi
			# An error occured, when a line was not found in the /tmp/output file.
			if [[ $t == true && $aminerMail == true && $found == false ]]; then
				echo "$searched"
				echo "$line"
				echo "not found!"
				res=1
			fi
		done < "$input"
		i=$(($i+1))
	done

	echo "finished waiting.."
	return $res
}

# This function checks if the output of the Syslog is as expected.
function checkAllSyslogs(){
	sudo tail -n 1000 /var/log/syslog > /tmp/out

	lastLine=`tail -n 1 /tmp/output`
	if [[ $lastLine == "" ]]; then
		sudo sed -i "$ d" /tmp/output
	fi

	cntr=0
	input="/tmp/out"
	i=0
	j=0
	while IFS= read -r searched
	do
		# every syslog starts with a 15 characters long datetime.
		d="${searched:0:15}"
		dat=`date -d "$d" +%s`
		# Ignore all old syslogs and just process the current ones.
		if [[ !($dat -lt $time) ]]; then
			expected="/tmp/output"
			found=false
			g=0
			while IFS= read -r line
			do
				if [ $g == $cntr ]; then
					# Increase the counters, when a paragraph finished.
					if [ "$line" == "" ]; then
						j=0
						i=$(($i+1))
						cntr=$(($cntr + 1))
						g=$(($g+1))
						continue
					fi
					# The first line of a paragraph always starts with the count of paragraphs logged.
					if [[ ($j == 0 && "$searched" == *": [$i] $line"*) ]]; then
						found=true
						cntr=$(($cntr + 1))
						break
					# All other lines also contain a counter for the lines in the paragraph
					elif [[ "$searched" == *": [$i-$j] $line"* ]]; then
						found=true
						cntr=$(($cntr + 1))
						break
					fi
				fi
				g=$(($g+1))
			done < "$expected"

			if [ $found == true ]; then
				j=$(($j+1))
			fi
		fi
	done < "$input"
	echo "finished waiting.."
	# $NUMBER_OF_LOG_LINES must always be the number of paragraphs in /tmp/output minus one,
	# as there is no empty line before the first paragraph.
	if [ $i == $NUMBER_OF_LOG_LINES ]; then
		return 0
	fi
	return 1
}

# This function checks if the output of the Kafka Topic is as expected.
function checkKafkaTopic(){
  out=$($KAFKA_VERSIONSTRING/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test_topic --from-beginning --timeout-ms 3000)
  for t in "${JSON_OUTPUT[@]}"
  do
    if [[ $out != *"$t"* ]]; then
      echo "searched: $t"
      echo
      echo "remaining output: $out"
      return 1
    fi
    # cut the output string to remove timestamps and datetimes.
    out=${out#*$t}
  done
  return 0
}
