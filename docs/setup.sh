#!/bin/bash

case "$1" in

	"install")
		ln -s ../README.md
		ln -s ../SECURITY.md
		ln -s ../LICENSE LICENSE.md

		git clone https://github.com/ait-aecid/logdata-anomaly-miner.wiki.git ../Wiki
                ;;

	"uninstall")
		unlink README.md
		unlink SECURITY.md
		unlink LICENSE.md

		test -d ../Wiki && rm -rf ../Wiki
		;;

	*)
		echo "usage: $0 <install | uninstall>"
		exit 1
		;;
esac
