if [[ $# -lt 3 ]]; then
	echo "Error, not enough parameters found!"
	echo "Please run the script as follows: ./multiplyLogFile.sh numberOfCopies templateFile targetFile"
	echo "For example: ./multiplyLogFile.sh 2700000 syslog-template /tmp/syslog"
	exit
fi
iterations=$1
src=$2
target=$3

sudo rm $target 2> /dev/null

# read the sourcefile into an array.
mapfile -t srcArray < $src

i=0
while [ $i -lt $iterations ]; do
	if [ $i -eq 0 ]; then
		printf "%s\n" "${srcArray[@]}" > $target
	else
		printf "%s\n" "${srcArray[@]}" >> $target
	fi
	i=$((i + 1))
done
