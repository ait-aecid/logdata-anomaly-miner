void setBuildStatus(String message, String state) {
  step([
      $class: "GitHubCommitStatusSetter",
      reposSource: [$class: "ManuallyEnteredRepositorySource", url: "https://github.com/my-org/my-repo"],
      contextSource: [$class: "ManuallyEnteredCommitContextSource", context: "ci/jenkins/build-status"],
      errorHandlers: [[$class: "ChangingBuildStatusErrorHandler", result: "UNSTABLE"]],
      statusResultSource: [ $class: "ConditionalStatusResultSource", results: [[$class: "AnyBuildResult", message: message, state: state]] ]
  ]);
}


pipeline {
     agent any
     stages {

          stage("Build Test-Container"){
             steps {
                 sh "docker build -f aecid-testsuite/Dockerfile -t aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID ."
             }
          }
         
         stage("UnitTest"){
             steps {
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runUnittests"
       	         sh 'docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runSuspendModeTest'
       	         sh 'docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runRemoteControlTest'
             }
         }
         stage("Run Demo-Configs"){
             parallel {
                 stage("demo-config and jsonConverterHandler-demo-config") {
                     steps {
       	                 sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runAMinerDemo demo/AMiner/demo-config.py"
       	                 sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runAMinerDemo demo/AMiner/demo-config.yml"
                     }
                 }
                 stage("template_config") {
                     steps {
       	         	sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runAMinerDemo demo/AMiner/template_config.py"
       	         	sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runAMinerDemo demo/AMiner/template_config.yml"
                     }
                 }
                 stage("jsonConverterHandler") {
                     steps {
       	                 sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runAMinerDemo demo/AMiner/jsonConverterHandler-demo-config.py"
                     }
                 }


             }
         }

         stage("Integrations Test"){
             steps {
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runAMinerIntegrationTest aminerIntegrationTest.sh config.py"
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runAMinerIntegrationTest aminerIntegrationTest2.sh config21.py config22.py"
             }
         }


         stage("Wiki Tests"){
             when {
                 branch 'development'
             }
             steps {
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runTryItOut"
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runGettingStarted"
             }
         }

         stage("Coverage Tests"){
             when {
                 branch 'development'
             }
             steps {
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runCoverageTests"
             }
         }
    }
    post {
        always {
           sh "docker rmi aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
        }
	success {
        setBuildStatus("Build succeeded", "SUCCESS");
    }
    failure {
        setBuildStatus("Build failed", "FAILURE");
    }
  }

} 
