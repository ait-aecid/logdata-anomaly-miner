node {
     checkout scm
     def testImage = docker.build("aminer-test","-f aecid-testsuite/Dockerfile .")
     stage("UnitTest"){
       testImage.inside("-u aminer --entrypoint= "){
       	sh 'cd aecid-testsuite && ./runUnittests.sh'
       }
    }
} 
