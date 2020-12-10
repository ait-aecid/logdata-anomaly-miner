pipeline {
     agent {
         dockerfile {
            filename "aecid-testsuite/Dockerfile"
         }
     }
     stages {
         stage("UnitTest"){
             steps {
                 sh 'docker images'
       	         // sh 'docker run -m=2G --rm aecid/logdata-anomaly-miner-testing runUnittests'
             }
          }
    }
} 
