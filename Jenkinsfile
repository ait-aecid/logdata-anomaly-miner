pipeline {
    agent {
	docker {image 'debian:latest' }
    } 
    stages {
        stage('Stage 1') {
            steps {
                sh 'echo Hello world!' 
            }
        }
    }
}
