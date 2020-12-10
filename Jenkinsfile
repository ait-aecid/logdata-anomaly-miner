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
                 sh 'docker build -f aecid-testsuite/Dockerfile -t aecid/logdata-anomaly-miner-testing:latest .'
             }
          }
         
         stage("UnitTest"){
             steps {
       	         sh 'docker run -m=2G --rm aecid/logdata-anomaly-miner-testing runUnittests'
       	         sh 'docker run -m=2G --rm aecid/logdata-anomaly-miner-testing runSuspendModeTest'
             }
         }
         stage("Run Demo-Configs"){
             steps {
       	         sh 'docker run -m=2G --rm aecid/logdata-anomaly-miner-testing runAMinerDemo demo/AMiner/demo-config.py'
       	         sh 'docker run -m=2G --rm aecid/logdata-anomaly-miner-testing runAMinerDemo demo/AMiner/jsonConverterHandler-demo-config.py'
       	         sh 'docker run -m=2G --rm aecid/logdata-anomaly-miner-testing runAMinerDemo demo/AMiner/template_config.py'
       	         sh 'docker run -m=2G --rm aecid/logdata-anomaly-miner-testing runAMinerDemo demo/AMiner/template_config.yml'
       	         sh 'docker run -m=2G --rm aecid/logdata-anomaly-miner-testing runAMinerDemo demo/AMiner/demo-config.yml'
             }
         }

         stage("Integrations Test"){
             steps {
       	         sh 'docker run -m=2G --rm aecid/logdata-anomaly-miner-testing runAMinerIntegrationTest aminerIntegrationTest.sh config.py'
       	         sh 'docker run -m=2G --rm aecid/logdata-anomaly-miner-testing runAMinerIntegrationTest aminerIntegrationTest2.sh config21.py config22.py'
             }
         }

         stage("Coverage Tests"){
             steps {
       	         sh 'docker run -m=2G --rm aecid/logdata-anomaly-miner-testing runCoverageTests'
             }
         }
    }
    post {
	success {
        setBuildStatus("Build succeeded", "SUCCESS");
    }
    failure {
        setBuildStatus("Build failed", "FAILURE");
    }
  }

} 
