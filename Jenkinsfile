pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.9'
        FRAMEWORK_DIR = "${WORKSPACE}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup') {
            steps {
                sh '''
                    python3 -m pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install flask flask-cors
                '''
            }
        }
        
        stage('Start API Server') {
            steps {
                sh '''
                    python ide-integration/backend/api_server.py &
                    sleep 5
                '''
            }
        }
        
        stage('Security Scan') {
            steps {
                sh '''
                    python scripts/ci_scan.py \
                        --path . \
                        --output security-report.json \
                        --fail-on-critical
                '''
            }
        }
        
        stage('Check Results') {
            steps {
                sh '''
                    python scripts/check_ci_results.py security-report.json
                '''
            }
        }
    }
    
    post {
        always {
            archiveArtifacts 'security-report.json'
            publishHTML([
                reportDir: '.',
                reportFiles: 'security-report.json',
                reportName: 'Security Report'
            ])
        }
        success {
            echo '✅ Security scan passed!'
        }
        failure {
            echo '❌ Security scan failed! Vulnerabilities found.'
            emailext(
                subject: "Security Scan Failed - ${env.JOB_NAME}",
                body: """
                    Security scan failed for build ${env.BUILD_NUMBER}
                    
                    Check the security report for details.
                """,
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}


