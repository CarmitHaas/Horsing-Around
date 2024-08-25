def RELEASE_TAG
def SERVER_IP
pipeline {
    agent any
    
    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }
    
    environment {
        ECR_REGISTRY = '644435390668.dkr.ecr.us-east-1.amazonaws.com'
        ECR_REPOSITORY = 'carmit-portfolio'
        IMAGE_NAME = 'horsing-around'
        AWS_DEFAULT_REGION = 'us-east-1'
        // E2E_USERNAME = credentials('e2e-username')
        // E2E_PASSWORD = credentials('e2e-password')
        E2E_USERNAME = 'admin'
        E2E_PASSWORD = 'admin'
    }

    stages {
        stage('Clone') {
            steps {
                checkout scm
            }
        }

        stage('Set Server IP') {
    steps {
        script {
            SERVER_IP = sh(script: "curl -s http://checkip.amazonaws.com", returnStdout: true).trim()
            echo "Server IP is ${SERVER_IP}"
        }
    }
}

       stage('Unit Test') {
            steps {
                script {
                    sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    pip install pytest mock
                    export PYTHONPATH=$PYTHONPATH:$(pwd)
                    pytest -v tests/
                    deactivate
                    '''
                }
            }
        }

        stage('Build Web App') {
            steps {
                script {
                    sh '''
                    docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} -f Dockerfile .
                    '''
                }
            }
        }

      stage('End-to-end Test') {
        steps {
            script {
                sh '''
                docker-compose -f docker-compose.ci.yml up -d
                chmod +x e2e.sh
                bash ./e2e.sh ${SERVER_IP} ${E2E_USERNAME} ${E2E_PASSWORD}
                docker-compose -f docker-compose.ci.yml down
                '''
                }

        }
      }
        stage('Tag') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sshagent(['github']) {
                        sh "git fetch --tags"
                    }
                    def latestTag = sh(script: "git describe --tags --abbrev=0 || echo 0.0.0", returnStdout: true).trim()
                    def (major, minor, patch) = latestTag.tokenize('.')
                    RELEASE_TAG = "${major}.${minor}.${(patch as int) + 1}"
                    echo "New version: ${RELEASE_TAG}"
                }
            }
        }

        stage('Publish') {
            when {
                branch 'main'
            }
            steps {
                script {
                    withAWS(credentials: 'aws-credentials', region: AWS_DEFAULT_REGION) {
                        sh """
                        aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                        docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${ECR_REGISTRY}/${ECR_REPOSITORY}:${RELEASE_TAG}
                        docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${RELEASE_TAG}
                        """
                    }
                }
            }
        }
    }
    //     stage('Deploy') {
    //         when {
    //             branch 'main'
    //         }
    //         steps {
    //             sshagent(['github']) {
    //                 sh """
    //                 git clone https://github.com/CarmitHaas/HorsingAround-gitops.git
    //                 cd HorsingAround-gitops
    //                 sed -i 's|image: .*|image: ${ECR_REGISTRY}/${ECR_REPOSITORY}:${RELEASE_TAG}|' deployment.yaml
    //                 git config user.email "jenkins@jenkins.com"
    //                 git config user.name "Jenkins"
    //                 git add deployment.yaml
    //                 git commit -m "Update image to ${RELEASE_TAG}"
    //                 git push origin main
    //                 """
    //             }
    //         }
    //     }
    // }

    post {
        always {
            sh '''
            docker-compose down -v || true
            docker system prune -af
            '''
            cleanWs()
        }
    }
}
