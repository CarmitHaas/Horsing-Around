def RELEASE_TAG

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
        EC2_IP = sh(script: "curl -s http://169.254.169.254/latest/meta-data/local-ipv4", returnStdout: true).trim()
    }

    stages {
        stage('Clone') {
            steps {
                checkout scm
            }
        }

        // stage('Build Images') {
        //     steps {
        //         script {
        //             sh '''
        //             docker-compose build
        //             '''
        //         }
        //     }
        // }
        stage('Run'){
            steps {
                sh 'docker-compose up -d'
            }
        }

        stage('Test'){
            steps {
                retry(15) {
                sleep(time: 3, unit: 'SECONDS')
                sh "curl -fsSLI http://${EC2_IP}:80"
                }
            }
            post {
                always {
                    sh 'docker-compose down -v'
                }
                success {
                    sh "echo 'hurdle-archive was up and running on nginx'"
                }
            }
        }


        stage('Calculate Version') {
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

        stage('Push to ECR') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sh """
                    aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                    docker tag ${IMAGE_NAME}:latest ${ECR_REGISTRY}/${ECR_REPOSITORY}:${RELEASE_TAG}
                    docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${RELEASE_TAG}
                    """
                }
            }
        }

        stage('Git Tag') {
            when {
                branch 'main'
            }
            steps {
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
