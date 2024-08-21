pipeline {
    agent any
    options {
        timestamps()
        timeout(time: 60, unit: 'MINUTES')
    }
    
    environment {
        GIT_SSH_COMMAND = 'ssh -o StrictHostKeyChecking=no' // Skip host key checking
        ECR_REGISTRY = '644435390668.dkr.ecr.us-east-1.amazonaws.com'
        ECR_REPOSITORY = 'carmit-portfolio'
        IMAGE_NAME = 'Horsing-Around:1.0'
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
        public_ip = 34.231.225.228:80
    }

    stages {
        stage('Pull') {
            steps {
                checkout scm
            }
        }

        stage('Build and Test') {
            steps {
                script {
                    sh '''
                    docker-compose up --build
                    sleep 30
                    chmod +x e2e.sh
                    bash ../e2e.sh \${public_ip}
                    '''
                }
            }
        }

        stage('Publish to ECR') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'ecr-credentials', usernameVariable: 'ECR_USERNAME', passwordVariable: 'ECR_PASSWORD')]) {
                        sh """
                            echo \${ECR_PASSWORD} | docker login -u \${ECR_USERNAME} --password-stdin ${ECR_REGISTRY}
                            docker tag ${IMAGE_NAME} ${ECR_REGISTRY}/${ECR_REPOSITORY}:${BUILD_NUMBER}
                            docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${BUILD_NUMBER}
                        """
                    }
                }
            }
        }
    }
        // stage('Deploy') {
        //       when {
        //         expression {
    //                 sh(returnStdout: true, script: 'git log -1 --pretty=%B').trim().contains("#test")
    //             }
    //         }
    //         steps {
    //             script {
    //               def time_stamp = sh(script: "date -u +'%Y%m%d-%H%M'", returnStdout: true).trim()

    //                 withCredentials([sshUserPrivateKey(credentialsId: 'mypemkey', keyFileVariable: 'SSH_KEY')]) {
    //                     sh '''
    //                         cp "$SSH_KEY" terraform/Carmit-ID.pem
    //                         chmod 600 terraform/Carmit-ID.pem
    //                         ssh-keygen -y -f terraform/Carmit-ID.pem > terraform/Carmit-ID.pem.pub
    //                     '''

    //                     dir('terraform') {
    //                         sh 'terraform init'
    //                         sh "terraform workspace select -or-create ${time_stamp}"
    //                         sh "terraform apply -var=environment=${time_stamp} -auto-approve"
    //                     }
    //                 }
    //             }
    //         }
    //     }

    //     stage('E2E Tests') {
    //           when {
    //             expression {
    //                 sh(returnStdout: true, script: 'git log -1 --pretty=%B').trim().contains("#test")
    //             }
    //         }
    //         steps {
    //             sh """
    //                 chmod +x e2e.sh
    //                 cd terraform
    //                 public_ip=\$(terraform output instance_public_ips | tr -d '[]," ')
    //                 bash ../e2e.sh \${public_ip}
    //             """
    //         }
    //     }
    // }

        post {
        failure {
            script {
                updateGitlabCommitStatus name: "${env.STAGE_NAME}", state: 'failed'
            }
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

