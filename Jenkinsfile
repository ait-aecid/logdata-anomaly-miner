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
             }
         }
    }
} 
