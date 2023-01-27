void setBuildStatus(String message, String state) {
    step([
        $class: "GitHubCommitStatusSetter",
        reposSource: [$class: "ManuallyEnteredRepositorySource", url: "https://github.com/ait-aecid/logdata-anomaly-miner"],
        contextSource: [$class: "ManuallyEnteredCommitContextSource", context: "ci/jenkins/build-status"],
        errorHandlers: [[$class: "ChangingBuildStatusErrorHandler", result: "UNSTABLE"]],
        statusResultSource: [ $class: "ConditionalStatusResultSource", results: [[$class: "AnyBuildResult", message: message, state: state]] ]
    ]);
}

def  ubuntu18image = false
def  ubuntu20image = false
def  debianbusterimage = false
def  debianbullseyeimage = false
def  productionimage = false
def  docsimage = false

pipeline {
    agent any
    stages {
        stage("Build Test-Container") {
            steps {
                sh "docker build -f aecid-testsuite/Dockerfile -t aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID ."
            }
        }
        stage("Static Analysis & Basic Functionality") {
            parallel {
                stage("Mypy"){
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runMypy"
                    }
                }
                stage("Release String Check"){
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runReleaseStringCheck"
                    }
                }
                stage("Suspend Mode"){
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runSuspendModeTest"
                    }
                }
                stage("Remote Control"){
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runRemoteControlTest"
                    }
                }
                stage("Integration Test 1"){
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runAminerIntegrationTest aminerIntegrationTest.sh config.py"
                    }
                }
                stage("Integration Test 2"){
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runAminerIntegrationTest aminerIntegrationTest2.sh config21.py config22.py"
                    }
                }
                stage("Offline Mode"){
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runOfflineMode"
                    }
                }
            }
        }

        stage("Unittests") {
             steps {
                 sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runUnittests"
             }
        }

        stage("Aminer Demo Tests") {
            parallel {
                stage("demo-config.py") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runAminerDemo demo/aminer/demo-config.py"
                    }
                }
                stage("demo-config.yml") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runAminerDemo demo/aminer/demo-config.yml"
                    }
                }
                stage("jsonConverterHandler-demo-config.py") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runAminerDemo demo/aminer/jsonConverterHandler-demo-config.py"
                    }
                }
                stage("template_config.py") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runAminerDemo demo/aminer/template_config.py"
                    }
                }
                stage("template_config.yml") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runAminerDemo demo/aminer/template_config.yml"
                    }
                }
                stage("Encoding Demo .py") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runAminerEncodingDemo demo/aminer/demo-config.py"
                    }
                }
                stage("Encoding Demo .yml") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runAminerEncodingDemo demo/aminer/demo-config.yml"
                    }
                }
            }
        }

        stage("Json Input Tests") {
            parallel {
                stage("Json Input Demo") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runAminerJsonInputDemo"
                    }
                }
                stage("Aminer") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runJsonDemo demo/aminerJsonInputDemo/json-aminer-demo.yml"
                    }
                }
                stage("Elastic") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runJsonDemo demo/aminerJsonInputDemo/json-elastic-demo.yml"
                    }
                }
                stage("Eve") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runJsonDemo demo/aminerJsonInputDemo/json-eve-demo.yml"
                    }
                }
                stage("Journal") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runJsonDemo demo/aminerJsonInputDemo/json-journal-demo.yml"
                    }
                }
                stage("Wazuh") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runJsonDemo demo/aminerJsonInputDemo/json-wazuh-demo.yml"
                    }
                }
                stage("Windows") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runJsonDemo demo/aminerJsonInputDemo/windows.yml"
                    }
                }
            }
        }

        stage("System, Documentation and Wiki Tests") {
            parallel {
                stage("Available Configs") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runConfAvailableTest"
                    }
                }
                stage("Debian Bullseye") {
                    steps {
                        script {
                            debianbullseyeimage = true
                        }
                        sh "docker build -f aecid-testsuite/docker/Dockerfile_deb -t aecid/aminer-debian-bullseye:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID --build-arg=varbranch=development --build-arg=vardistri=debian:bullseye ."
                        sh "mkdir -p /tmp/simplerun-bullseye-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID && mkdir /tmp/simplerun-bullseye-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/persistency && mkdir /tmp/simplerun-bullseye-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/logs"
                        sh "cp aecid-testsuite/demo/aminer/access.log /tmp/simplerun-bullseye-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/logs/"
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
                        sh "cp aecid-testsuite/demo/aminer/access.log /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/logs/"
                        sh "cp -r source/root/etc/aminer /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg"
                        sh "cp /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg/template_config.yml /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg/config.yml"
                        sh "cp /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg/conf-available/generic/ApacheAccessModel.py /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg/conf-enabled"
                        /* the result of timeout is negated with "!". This is because aminer returns 1 if timeout stops the process and otherwise 0. The way around is a valid result for a test */
                        sh "cd /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID && ! timeout -s INT --preserve-status 5 docker run -v $PWD/aminercfg:/etc/aminer -v $PWD/persistency:/var/lib/aminer -v $PWD/logs:/logs --rm -it aecid/aminer-debian-buster:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID aminer"
                    }
                }
                stage("Test Production Docker Image") {
                    steps {
                        script {
                            productionimage = true
                        }
                        sh "docker build -f Dockerfile -t aecid/aminer-production:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID ."
                        sh "mkdir -p /tmp/production-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID && mkdir /tmp/production-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/persistency && mkdir /tmp/production-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/logs"
                        sh "cp aecid-testsuite/demo/aminer/access.log /tmp/production-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/logs/"
                        sh "cp -r source/root/etc/aminer /tmp/production-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg"
                        sh "cp /tmp/production-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg/template_config.yml /tmp/production-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg/config.yml"
                        sh "cp /tmp/production-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg/conf-available/generic/ApacheAccessModel.py /tmp/production-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID/aminercfg/conf-enabled"
                        /* the result of timeout is negated with "!". This is because aminer returns 1 if timeout stops the process and otherwise 0. The way around is a valid result for a test */
                        sh "cd /tmp/production-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID && ! timeout -s INT --preserve-status 5 docker run -v $PWD/aminercfg:/etc/aminer -v $PWD/persistency:/var/lib/aminer -v $PWD/logs:/logs --rm -it aecid/aminer-production:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID aminer"
                    }
                }
                stage("Test Ubuntu 18.04") {
                    when {
                        expression {
                            BRANCH_NAME == "main" || BRANCH_NAME == "development"
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
                            BRANCH_NAME == "main" || BRANCH_NAME == "development"
                        }
                    }
                    steps {
                        script {
                            ubuntu20image = true
                        }
                        sh "docker build -f aecid-testsuite/docker/Dockerfile_deb -t aecid/aminer-ubuntu-2004:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID --build-arg=varbranch=development --build-arg=vardistri=ubuntu:20.04 ."
                        sh "docker run --rm aecid/aminer-ubuntu-2004:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
                   }
                }
                stage("Build Documentation") {
                    when {
                        expression {
                            BRANCH_NAME == "main" || BRANCH_NAME == "development"
                        }
                    }
                    environment {
                        BUILDDOCSDIR = sh(script: 'mktemp -p $WORKSPACE_TMP -d | tr -d [:space:]', returnStdout: true)
                    }
                    steps {
                        script {
                            docsimage = true
                        }
                    sh "docker build -f Dockerfile -t aecid/aminer-docs:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID ."
                    sh "chmod 777 ${env.BUILDDOCSDIR}"
                    sh "chmod g+s ${env.BUILDDOCSDIR}"
                    sh "docker run --rm -v ${env.BUILDDOCSDIR}:/docs/_build aecid/aminer-docs:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID mkdocs"
                    sh "scripts/deploydocs.sh ${env.BRANCH_NAME} ${env.BUILDDOCSDIR}/html /var/www/aeciddocs/logdata-anomaly-miner"
                    }
                }
                stage("Try It Out") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runTryItOut development"
                    }
                }
                stage("Getting Started") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runGettingStarted development"
                    }
                }
                stage("Sequence Detector") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runHowToCreateYourOwnSequenceDetector development"
                    }
                }
                stage("Frequency Detector") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runHowToCreateYourOwnFrequencyDetector development"
                    }
                }
                stage("MissingMatchPathDetector") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runHowToMissingMatchPathValueDetector development"
                    }
                }
                stage("EntropyDetector") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runHowToEntropyDetector development"
                    }
                }
            }
        }
        stage("Wiki Tests - main") {
            when {
                branch "main"
            }
            parallel {
                stage("Try It Out") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runTryItOut main"
                    }
                }
                stage("Getting Started") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runGettingStarted main"
                    }
                }
                stage("Sequence Detector") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runHowToCreateYourOwnSequenceDetector main"
                    }
                }
                stage("Frequency Detector") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runHowToCreateYourOwnFrequencyDetector main"
                    }
                }
                stage("MissingMatchPathDetector") {
                    steps {
                        sh "docker run -m=2G --rm aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID runHowToMissingMatchPathValueDetector main"
                    }
                }
            }
        }
    }
    post {
        always {
            script {
                sh "docker rmi aecid/logdata-anomaly-miner-testing:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
                if( debianbullseyeimage == true ) {
                    sh "docker rmi aecid/aminer-debian-bullseye:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
                    sh "cd / && test -d /tmp/simplerun-bullseye-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID && rm -rf /tmp/simplerun-bullseye-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
                }
                if( debianbusterimage == true ) {
                    sh "docker rmi aecid/aminer-debian-buster:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
                    sh "cd / && test -d /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID && rm -rf /tmp/simplerun-buster-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
                }
                if( productionimage == true ) {
                    sh "docker rmi aecid/aminer-production:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
                    sh "cd / && test -d /tmp/production-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID && rm -rf /tmp/production-$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
                }
                if( ubuntu18image == true ) {
                    sh "docker rmi aecid/aminer-ubuntu-1804:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
                }
                if( ubuntu20image == true ) {
                    sh "docker rmi aecid/aminer-ubuntu-2004:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
                }
                if( docsimage == true){
                    sh "docker rmi aecid/aminer-docs:$JOB_BASE_NAME-$EXECUTOR_NUMBER-$BUILD_ID"
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
