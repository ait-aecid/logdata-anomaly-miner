void setBuildStatus(String message, String state) {
  step([
      $class: "GitHubCommitStatusSetter",
      reposSource: [$class: "ManuallyEnteredRepositorySource", url: "https://github.com/my-org/my-repo"],
      contextSource: [$class: "ManuallyEnteredCommitContextSource", context: "ci/jenkins/build-status"],
      errorHandlers: [[$class: "ChangingBuildStatusErrorHandler", result: "UNSTABLE"]],
      statusResultSource: [ $class: "ConditionalStatusResultSource", results: [[$class: "AnyBuildResult", message: message, state: state]] ]
  ]);
}

def  ubuntu18image = false
def  ubuntu20image = false
def  debianbusterimage = false
def  debianbullseyeimage = false

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


         stage("Wiki Tests - development"){
             when {
                 branch 'development'
             }
             steps {
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runTryItOut development"
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runGettingStarted development"
             }
         }

	stage("Wiki Tests - main"){
             when {
                 branch 'main'
             }
             steps {
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runTryItOut main"
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runGettingStarted main"
             }
         }

/*         stage("Coverage Tests"){
             when {
                 branch 'development'
             }
             steps {
       	         sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runCoverageTests"
             }
         }
*/
                 stage("Test Debian Bullseye") {
                    steps {
                    script {
                      debianbullseyeimage = true
                    }
                     sh "docker build -f aecid-testsuite/docker/Dockerfile_deb -t aecid/aminer-debian-bullseye:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID --build-arg=varbranch=development --build-arg=vardistri=debian:bullseye ."
                     sh "mkdir -p /tmp/simplerun-bullseye-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID && mkdir /tmp/simplerun-bullseye-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/persistency && mkdir /tmp/simplerun-bullseye-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/logs"
                     sh "cp aecid-testsuite/demo/AMiner/access.log /tmp/simplerun-bullseye-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/logs/"
                     sh "cp -r source/root/etc/aminer /tmp/simplerun-bullseye-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg"
                     sh "cp /tmp/simplerun-bullseye-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg/template_config.yml /tmp/simplerun-bullseye-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg/config.yml"
                     sh "cp /tmp/simplerun-bullseye-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg/conf-available/generic/ApacheAccessModel.py /tmp/simplerun-bullseye-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg/conf-enabled"
                     /* the result of timeout is negated with "!". This is because aminer returns 1 if timeout stops the process and otherwise 0. The way around is a valid result for a test */
                     sh "cd /tmp/simplerun-bullseye-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID && ! timeout -s INT --preserve-status 5 docker run -v $PWD/aminercfg:/etc/aminer -v $PWD/persistency:/var/lib/aminer -v $PWD/logs:/logs --rm -it aecid/aminer-debian-bullseye:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID aminer"
                   }
                 }

                 stage("Test Debian Buster") {
                    steps {
                    script {
                      debianbusterimage = true
                    }
                     sh "docker build -f aecid-testsuite/docker/Dockerfile_deb -t aecid/aminer-debian-buster:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID --build-arg=varbranch=development --build-arg=vardistri=debian:buster ."
                     sh "mkdir -p /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID && mkdir /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/persistency && mkdir /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/logs"
                     sh "cp aecid-testsuite/demo/AMiner/access.log /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/logs/"
                     sh "cp -r source/root/etc/aminer /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg"
                     sh "cp /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg/template_config.yml /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg/config.yml"
                     sh "cp /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg/conf-available/generic/ApacheAccessModel.py /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg/conf-enabled"
                     /* the result of timeout is negated with "!". This is because aminer returns 1 if timeout stops the process and otherwise 0. The way around is a valid result for a test */
                     sh "cd /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID && ! timeout -s INT --preserve-status 5 docker run -v $PWD/aminercfg:/etc/aminer -v $PWD/persistency:/var/lib/aminer -v $PWD/logs:/logs --rm -it aecid/aminer-debian-buster:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID aminer"
                   }
                 }

		stage("Test Ubuntu 18.04") {
                    when {
                       expression {
                            BRANCH_NAME == 'main' || BRANCH_NAME == 'development'
                       }
                    }
                    steps {
                     script{
                       ubuntu18image = true
                     }
                     sh "docker build -f aecid-testsuite/docker/Dockerfile_deb -t aecid/aminer-ubuntu-1804:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID --build-arg=varbranch=development --build-arg=vardistri=ubuntu:18.04 ."
                     sh "docker run --rm aecid/aminer-ubuntu-1804:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
                    }
                 }

		stage("Test Ubuntu 20.04") {
                    when {
                       expression {
                            BRANCH_NAME == 'main' || BRANCH_NAME == 'development'
                       }
                    }
                    steps {
                    script {
                      ubuntu20image = true
                    }
                     sh "docker build -f aecid-testsuite/docker/Dockerfile_deb -t aecid/aminer-ubuntu-2004:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID --build-arg=varbranch=development --build-arg=vardistri=ubuntu:20.04 ."
                     sh "docker run --rm aecid/aminer-ubuntu-1804:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
                   }
                 }
    }
    post {
        always {
           script {
           sh "docker rmi aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
           if( debianbullseyeimage == true ){
               sh "docker rmi aecid/aminer-debian-bullseye:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
               sh "cd / && test -d /tmp/simplerun-bullseye-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID && rm -rf /tmp/simplerun-bullseye-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
           }
           if( debianbusterimage == true ){
               sh "docker rmi aecid/aminer-debian-buster:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
               sh "cd / && test -d /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID && rm -rf /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
           }
           if( ubuntu18image == true ){
               sh "docker rmi aecid/aminer-ubuntu-1804:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
           }
           if( ubuntu20image == true ){
               sh "docker rmi aecid/aminer-ubuntu-2004:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
           }
         }
        }
 
	success {
        setBuildStatus("Build succeeded", "SUCCESS");
    }
    failure {
        setBuildStatus("Build failed", "FAILURE");
    }
  }

} 
