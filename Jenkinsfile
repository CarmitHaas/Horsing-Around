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
                    SERVER_IP = sh(script: 'curl -s http://checkip.amazonaws.com', returnStdout: true).trim()
                    echo "Server IP is ${SERVER_IP}"
                }
            }
        }

    //    stage('Unit Test') {
    //         steps {
    //             script {
    //             sh '''
    //                 python3 -m venv venv
    //                 . venv/bin/activate
    //                 pip install -r requirements.txt
    //                 pip install pytest
    //                 export PYTHONPATH=$PYTHONPATH:$(pwd)
    //                 pytest tests/ -v
    //                 deactivate
    //                     '''
    //             }
    //         }
    //     }

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
                    sh """
                    docker-compose -f docker-compose.ci.yml up -d
                    chmod +x e2e.sh
                    bash ./e2e.sh ${SERVER_IP}
                    docker-compose -f docker-compose.ci.yml down
                    """
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
                        sh 'git fetch --tags'
                    }
                    def latestTag = sh(script: 'git describe --tags --abbrev=0 || echo 1.0.0', returnStdout: true).trim()
                    def (major, minor, patch) = latestTag.tokenize('.')
                    if (latestTag == '1.0.0' && !sh(script: 'git tag', returnStdout: true).trim()) {
                        RELEASE_TAG = '1.0.0'
                    } else {
                        RELEASE_TAG = "${major}.${minor}.${(patch as int) + 1}"
                    }
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
                    withCredentials([usernamePassword(credentialsId: 'ecr-credentials', usernameVariable: 'ECR_USERNAME', passwordVariable: 'ECR_PASSWORD')]) {
                        sh """
                        echo \${ECR_PASSWORD} | docker login -u \${ECR_USERNAME} --password-stdin ${ECR_REGISTRY}
                        docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${ECR_REGISTRY}/${ECR_REPOSITORY}:${RELEASE_TAG}
                        docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest
                        docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${RELEASE_TAG}
                        docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest
                        """
                    }

                    sshagent(['github']) {
                        sh """
                        git config user.email "jenkins@jenkins.com"
                        git config user.name "Jenkins"
                        git tag -a ${RELEASE_TAG} -m "Release ${RELEASE_TAG}"
                        git push origin ${RELEASE_TAG}
                        """
                    }
                }
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'ecr-credentials', usernameVariable: 'ECR_USERNAME', passwordVariable: 'ECR_PASSWORD')]) {
                    sshagent(['github']) {
                        sh """
                set -ex
                git clone git@github.com:CarmitHaas/gitops-HA.git
                cd gitops-HA
                sed -i '/deployment:/,/image:/{s|repository: .*|repository: ${ECR_REGISTRY}/${ECR_REPOSITORY}|;s|tag: .*|tag: ${RELEASE_TAG}|}' horsing-around-umbrella/values.yaml
                git config user.email "jenkins@jenkins.com"
                git config user.name "Jenkins"
                git add .
                git diff --cached
                git commit -m "Update image to ${RELEASE_TAG}" || true
                git push origin main
                """
                    }
                }
            }
        }
    }

    post {
        always {
            sh '''
            docker-compose down -v || true
            docker rmi ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest || true
            docker system prune -af
            '''
            cleanWs()
        }
    }
}
