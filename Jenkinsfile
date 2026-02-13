pipeline {
    agent any

    stages {
        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'sonarqubeScannerInstallation'
                    withSonarQubeEnv('sonarqubeInstallation') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=addons_vazztec_odoo \
                            -Dsonar.projectName=addons_vazztec_odoo \
                            -Dsonar.sources=.
                        """
                    }
                }
            }
        }
    }
}