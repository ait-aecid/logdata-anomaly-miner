#!/bin/bash

TESTDIR=/home/aminer/aecid-testsuite

if [ $# -gt 0 ]
then
sudo service rsyslog start
sudo service postfix start
fi

case "$1" in
	runSuspendModeTest)
		cd $TESTDIR
		./${1}.sh ${*:2}
		exit $?
		;;
	runUnittests)
		cd $TESTDIR
		./${1}.sh ${*:2}
		exit $?
		;;
	runAMinerDemo)
		cd $TESTDIR
		./${1}.sh ${*:2}
		exit $?
		;;
	runAMinerIntegrationTest)
		cd $TESTDIR
		./${1}.sh ${*:2}
		exit $?
		;;
	runCoverageTests)
		cd $TESTDIR
		./${1}.sh ${*:2}
		exit $?
		;;
	ALL)
		cd $TESTDIR
                ./runSuspendModeTest.sh
                ./runUnittests.sh
                ./runAMinerDemo.sh demo/AMiner/demo-config.py
                ./runAMinerDemo.sh demo/AMiner/jsonConverterHandler-demo-config.py
                ./runAMinerDemo.sh demo/AMiner/template_config.py
                ./runAMinerDemo.sh demo/AMiner/template_config.yml
                ./runAMinerDemo.sh demo/AMiner/demo-config.yml
                ./runAMinerIntegrationTest.sh aminerIntegrationTest.sh config.py
                ./runAMinerIntegrationTest.sh aminerIntegrationTest2.sh config21.py config22.py
                ./runCoverageTests.sh
                exit $?
		;;
	SHELL)
		bash
		exit 0
		;;
	*)
		echo "Usage: [ ALL | SHELL | runSuspendModeTest | runUnittests | runAMinerDemo | runAMinerIntegrationTest | runCoverageTests] <options>"
		exit 1
		;;
        
esac

exit 0
