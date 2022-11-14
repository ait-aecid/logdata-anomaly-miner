#!/bin/bash

sudo mkdir /tmp/lib 2> /dev/null
sudo mkdir /tmp/lib/aminer 2> /dev/null
sudo chown -R $USER:$USER /tmp/lib/aminer 2> /dev/null
sudo rm -r /tmp/lib/aminer/* 2> /dev/null
sudo mkdir /tmp/lib/aminer/log 2> /dev/null
sudo chown -R aminer:aminer /tmp/lib/aminer 2> /dev/null
sudo cp ./integration/offline_mode/data/* /tmp/

exit_code=0

#start aminer
#if the aminer is stuck, Jenkins should fail it after a while.
sudo aminer --config ./integration/offline_mode/offline_mode.yml --offline-mode --from-begin > /tmp/out.txt
OUTPUT=$(cat /tmp/out.txt)

read -r -d '' VAR << END
 New path(es) detected
NewMatchPathDetector: "DefaultNewMatchPathDetector" (1 lines)
  /model/data: a1
['/model/data']
a1

END
if [[ "$OUTPUT" != *"$VAR"* ]]; then
  echo "$VAR"
  echo
  exit_code=1
fi

read -r -d '' VAR << END
 New path(es) detected
NewMatchPathDetector: "DefaultNewMatchPathDetector" (1 lines)
  /model/data: b1
['/model/data']
b1

END
if [[ "$OUTPUT" != *"$VAR"* ]]; then
  echo "$VAR"
  echo
  exit_code=1
fi

read -r -d '' VAR << END
 New path(es) detected
NewMatchPathDetector: "DefaultNewMatchPathDetector" (1 lines)
  /model/data: c1
['/model/data']
c1

END
if [[ "$OUTPUT" != *"$VAR"* ]]; then
  echo "$VAR"
  echo
  exit_code=1
fi

read -r -d '' VAR << END
 New path(es) detected
NewMatchPathDetector: "DefaultNewMatchPathDetector" (1 lines)
  /model/data: z1
['/model/data']
z1

END
if [[ "$OUTPUT" != *"$VAR"* ]]; then
  echo "$VAR"
  echo
  exit_code=1
fi

read -r -d '' VAR << END
 New path(es) detected
NewMatchPathDetector: "DefaultNewMatchPathDetector" (1 lines)
  /model/data: a2
['/model/data']
a2

END
if [[ "$OUTPUT" != *"$VAR"* ]]; then
  echo "$VAR"
  echo
  exit_code=1
fi

read -r -d '' VAR << END
 New path(es) detected
NewMatchPathDetector: "DefaultNewMatchPathDetector" (1 lines)
  /model/data: b2
['/model/data']
b2

END
if [[ "$OUTPUT" != *"$VAR"* ]]; then
  echo "$VAR"
  echo
  exit_code=1
fi

read -r -d '' VAR << END
 New path(es) detected
NewMatchPathDetector: "DefaultNewMatchPathDetector" (1 lines)
  /model/data: c2
['/model/data']
c2

END
if [[ "$OUTPUT" != *"$VAR"* ]]; then
  echo "$VAR"
  echo
  exit_code=1
fi

read -r -d '' VAR << END
 New path(es) detected
NewMatchPathDetector: "DefaultNewMatchPathDetector" (1 lines)
  /model/data: z2
['/model/data']
z2

END
if [[ "$OUTPUT" != *"$VAR"* ]]; then
  echo "$VAR"
  echo
  exit_code=1
fi

sudo rm /tmp/file1.log
sudo rm /tmp/file2.log

exit $exit_code