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
        IMAGE_NAME = 'Horsing-Around'
        AWS_DEFAULT_REGION = 'us-east-1'
        EC2_IP = EC2_IP = sh(script: "curl -s http://169.254.169.254/latest/meta-data/public-ipv4", returnStdout: true).trim()
    }

    stages {
        stage('Clone') {
            steps {
                checkout scm
            }
        }

        // stage('Build') {
        //     steps {
        //         script {
        //             sh 'docker-compose build'
        //         }
        //     }
        // }

        // stage('Unit Tests') {
        //     steps {
        //         // Add your unit tests here if you have any
        //         sh 'echo "Running unit tests"'
        //     }
        // }

        // stage('Package') {
        //     steps {
        //         script {
        //             sh "docker tag ${IMAGE_NAME}:latest ${ECR_REGISTRY}/${ECR_REPOSITORY}:${BUILD_NUMBER}"
        //         }
        //     }
        // }

        stage('End-to-End Tests') {
            steps {
                script {
                    sh '''
                    docker-compose up -d
                    sleep 30
                    chmod +x e2e.sh
                    ./e2e.sh ${EC2_IP}
                    docker-compose down
                    '''
                }
            }
        }

        stage('Tag and Publish') {
            when {
                branch 'main'
            }
            steps {
                script {
                    // Calculate new version
                    def latestTag = sh(script: 'git describe --tags --abbrev=0 || echo "0.0.0"', returnStdout: true).trim()
                    def (major, minor, patch) = latestTag.tokenize('.')
                    RELEASE_TAG = "${major}.${minor}.${patch.toInteger() + 1}"

                    // Tag Docker image
                    sh "docker tag ${IMAGE_NAME}:latest ${ECR_REGISTRY}/${ECR_REPOSITORY}:${RELEASE_TAG}"
                    
                    // Push to ECR
                    withCredentials([usernamePassword(credentialsId: 'ecr-credentials', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                        sh """
                            aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                            docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${RELEASE_TAG}
                        """
                    }

                    // Git tag
                    withCredentials([usernamePassword(credentialsId: 'github-credentials', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
                        sh """
                            git config user.email "jenkins@jenkins.com"
                            git config user.name "Jenkins"
                            git tag -a ${RELEASE_TAG} -m "Release ${RELEASE_TAG}"
                            git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/CarmitHaas/Horsing-Around.git ${RELEASE_TAG}
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
    //             script {
    //                 // Update GitOps repo
    //                 withCredentials([usernamePassword(credentialsId: 'github-credentials', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
    //                     sh """
    //                         git clone https://github.com/CarmitHaas/HorsingAround.git
    //                         cd gitops-repo
    //                         sed -i 's|image: .*|image: ${ECR_REGISTRY}/${ECR_REPOSITORY}:${RELEASE_TAG}|' deployment.yaml
    //                         git add deployment.yaml
    //                         git commit -m "Update image to ${RELEASE_TAG}"
    //                         git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/CarmitHaas/HorsingAround-gitops.git
    //                     """
    //                 }
    //             }
    //         }
    //     }
    // }
    }
        post {
        failure {
            emailext (
                subject: "Build Failed: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: """<p>The build failed. Please check the Jenkins console output for details.</p>
                         <p>Build URL: ${env.BUILD_URL}</p>""",
                recipientProviders: [culprits(), developers()],
                attachLog: true,
                compressLog: true
            )
        }
        success {
            emailext (
                subject: "Build Successful: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: """<p>The build was successful. Great job!!</p>
                         <p>Build URL: ${env.BUILD_URL}</p>""",
                recipientProviders: [culprits(), developers()],
                attachLog: true,
                compressLog: true
            )
        }
    }
}

