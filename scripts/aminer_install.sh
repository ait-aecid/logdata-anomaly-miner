#!/bin/bash

# if set to 1 this installer will delete the 
# source directory after installation
DELDIR=1
BRANCH="main"
URL="https://github.com/ait-aecid/logdata-anomaly-miner.git"
AMINERDST=`mktemp -d`
AMINERSRC=0
DISON=0

help() {
	echo "Usage: $0 [-h] [-b BRANCH] [-u GITURL] [-s LOCAL_GITREPO_PATH] [-d DIRECTORY]" 1>&2
}


while getopts "hb:u:s:d:" options; do
	case "${options}" in
		b)
			BRANCH=${OPTARG}
			;;
		h)
			help
			exit 1
			;;
		u)
			URL=${OPTARG}
			;;
		s)
			AMINERSRC=${OPTARG}
			DELDIR=0
			if [ ! -d $AMINERSRC ]
			then
				echo "Local Git-Repository $AMINERSRC does not exist."
				exit 1
			fi
			;;
		d)
			DISON=1
			AMINERDST=${OPTARG}
			if [ -d $AMINERDST ]
			then
				echo "This directory($AMINERDST) already exists. Please remove it first"
				exit 1
			fi
			DELDIR=0
			;;
		:)
			echo "$0: Must supply an argument to -$OPTARG." >&2
			exit 1
			;;
	esac
done


if [ -e /etc/debian_version ]
then
	SUDO=`which sudo`
	if [ $? -ne 0 ]
	then
		echo "Please install and configure sudo first"
		exit 1
	fi
	sudo /usr/bin/apt-get update
	sudo DEBIAN_FRONTEND=nointeractive /usr/bin/apt-get install -y -q ansible git
else
	echo "Currently only debian based distributions are supported"
	exit 1
fi

if [ $AMINERSRC -eq 0 ]
then
	git clone -b $BRANCH $URL $AMINERDST
else
	if [ $DISON -eq 1 ]
	then
		cp -rap $AMINERSRC $AMINERDST
	else	
		AMINERDST=$AMINERSRC
	fi
fi

cd $AMINERDST
test -d roles || mkdir roles
git clone -b $BRANCH https://github.com/ait-aecid/aminer-ansible roles/aminer


cat > playbook.yml << EOF
- hosts: localhost
  vars:
         aminer_gitrepo: False
         # We assume that we cloned the aminer to /home/developer/aminer 
         aminer_repopath: "${AMINERDST}"
  roles:
         - aminer
EOF

# Use this command to deploy the aminer-files
# You can add your changes in the aminer-directory
# and repeatedly execute this command to deploy
# your changes
sudo ansible-playbook playbook.yml

if [ $DELDIR -eq 1 ]
then
	test -d $AMINERDST && rm -rf $AMINERDST
fi

exit 0
