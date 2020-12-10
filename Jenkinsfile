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
                 sh "docker build -f aecid-testsuite/Dockerfile -t aecid/logdata-anomaly-miner-testing:$BUILD_NUMBER ."
             }
          }
         
         stage("UnitTest"){
             steps {
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$BUILD_NUMBER runUnittests"
       	         sh 'docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$BUILD_NUMBER runSuspendModeTest'
             }
         }
         stage("Run Demo-Configs"){
             steps {
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$BUILD_NUMBER runAMinerDemo demo/AMiner/demo-config.py"
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$BUILD_NUMBER runAMinerDemo demo/AMiner/jsonConverterHandler-demo-config.py"
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$BUILD_NUMBER runAMinerDemo demo/AMiner/template_config.py"
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$BUILD_NUMBER runAMinerDemo demo/AMiner/template_config.yml"
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$BUILD_NUMBER runAMinerDemo demo/AMiner/demo-config.yml"
             }
         }

         stage("Integrations Test"){
             steps {
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$BUILD_NUMBER runAMinerIntegrationTest aminerIntegrationTest.sh config.py"
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$BUILD_NUMBER runAMinerIntegrationTest aminerIntegrationTest2.sh config21.py config22.py"
             }
         }

         stage("Coverage Tests"){
             steps {
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$BUILD_NUMBER runCoverageTests"
             }
         }
    }
    post {
        always {
           sh "docker rmi aecid/logdata-anomaly-miner-testing:$BUILD_NUMBER"
        }
	success {
        setBuildStatus("Build succeeded", "SUCCESS");
    }
    failure {
        setBuildStatus("Build failed", "FAILURE");
    }
  }

} 
