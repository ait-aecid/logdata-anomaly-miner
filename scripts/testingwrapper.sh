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
	runAminerDemo)
		cd $TESTDIR
		./${1}.sh ${*:2}
		exit $?
		;;
	runAminerJsonInputDemo)
		cd $TESTDIR
		./${1}.sh ${*:2}
		exit $?
		;;
	runAminerIntegrationTest)
		cd $TESTDIR
		./${1}.sh ${*:2}
		exit $?
		;;
	runCoverageTests)
		cd $TESTDIR
		./${1}.sh ${*:2}
		exit $?
		;;
	runRemoteControlTest)
		cd $TESTDIR
		./${1}.sh ${*:2}
		exit $?
		;;
	runGettingStarted)
		cd $TESTDIR
		./${1}.sh ${*:2}
		exit $?
		;;
	runTryItOut)
		cd $TESTDIR
		./${1}.sh ${*:2}
		exit $?
		;;
	runHowToCreateYourOwnSequenceDetector)
		cd $TESTDIR
		./${1}.sh ${*:2}
		exit $?
		;;
	runHowToCreateYourOwnFrequencyDetector)
		cd $TESTDIR
		./${1}.sh ${*:2}
		exit $?
		;;
	runHowToMissingMatchPathValueDetector)
		cd $TESTDIR
		./${1}.sh ${*:2}
		exit $?
		;;
	runJsonDemo)
		cd $TESTDIR
		./${1}.sh ${*:2}
		exit $?
		;;
	runAminerEncodingDemo)
		cd $TESTDIR
		./${1}.sh ${*:2}
		exit $?
		;;
	runOfflineMode)
		cd $TESTDIR
		./${1}.sh ${*:2}
		exit $?
		;;
	runMypy)
		cd $TESTDIR
		./${1}.sh ${*:2}
		exit $?
		;;
	ALL)
		cd $TESTDIR
		        ./runMypy.sh
                ./runSuspendModeTest.sh
                ./runUnittests.sh
                ./runRemoteControlTest.sh
                ./runAminerDemo.sh demo/aminer/demo-config.py
                ./runAminerDemo.sh demo/aminer/jsonConverterHandler-demo-config.py
                ./runAminerDemo.sh demo/aminer/template_config.py
                ./runAminerDemo.sh demo/aminer/template_config.yml
                ./runAminerDemo.sh demo/aminer/demo-config.yml
                ./runAminerEncodingDemo.sh demo/aminer/demo-config.py
                ./runAminerEncodingDemo.sh demo/aminer/demo-config.yml
                ./runAminerJsonInputDemo.sh
                ./runJsonDemo.sh demo/aminerJsonInputDemo/json-aminer-demo.yml
                ./runJsonDemo.sh demo/aminerJsonInputDemo/json-elastic-demo.yml
                ./runJsonDemo.sh demo/aminerJsonInputDemo/json-eve-demo.yml
                ./runJsonDemo.sh demo/aminerJsonInputDemo/json-journal-demo.yml
                ./runJsonDemo.sh demo/aminerJsonInputDemo/json-wazuh-demo.yml
                ./runAminerIntegrationTest.sh aminerIntegrationTest.sh config.py
                ./runAminerIntegrationTest.sh aminerIntegrationTest2.sh config21.py config22.py
                ./runOfflineMode.sh
                ./runGettingStarted.sh
                ./runTryItOut.sh
                ./runHowToCreateYourOwnSequenceDetector.sh
                ./runHowToCreateYourOwnFrequencyDetector.sh
                ./runHowToMissingMatchPathValueDetector.sh
                ./runCoverageTests.sh
                exit $?
		;;
	SHELL)
		bash
		exit 0
		;;
	*)
		echo "Usage: [ ALL | SHELL | runSuspendModeTest | runUnittests | runAminerDemo | runJsonDemo | runAminerJsonInputDemo "
		echo "         runAminerIntegrationTest | runOfflineMode | runCoverageTests | runRemoteControlTest | runTryItOut "
		echo "         runGettingStarted | runHowToCreateYourOwnSequenceDetector | runHowToCreateYourOwnFrequencyDetector"
		echo "         runHowToMissingMatchPathValueDetector | runAminerEncodingDemo | runMypy] <options>"
		exit 1
		;;
        
esac

exit 0
