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
        SERVER_IP = '3.238.68.15'
    }

     
    stages {
        stage('Clone') {
            steps {
                checkout scm
            }
        }

       stage('Build Images') {
    steps {
        script {
            sh '''
            docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .
            docker build -t ${IMAGE_NAME}-nginx:${BUILD_NUMBER} -f Dockerfile.nginx .
            docker images
            
            # Check nginx configuration
            docker run --rm ${IMAGE_NAME}-nginx:${BUILD_NUMBER} nginx -t
            '''
        }
    }
}

stage('End-to-End Tests') {
    steps {
        script {
            sh '''
            echo "Starting services..."
            docker-compose -f docker-compose.ci.yml up -d

            echo "Waiting for services to start..."
            sleep 30

            echo "Checking container status..."
            docker ps -a

            echo "Checking container logs..."
            docker-compose -f docker-compose.ci.yml logs

            echo "Checking network..."
            docker network ls
            docker network inspect $(docker network ls --filter name=horsing-around --format "{{.ID}}")

            echo "Checking nginx configuration..."
            docker exec $(docker ps -q --filter name=nginx) nginx -T

            echo "Checking web application logs..."
            docker logs $(docker ps -q --filter name=web)

            echo "Running e2e tests..."
            chmod +x e2e.sh
            ./e2e.sh ${SERVER_IP}
            '''
        }
    }
}
//   stage('End-to-End Tests') {
//             steps {
//                 script {
//                     sh '''
//                     docker-compose -f docker-compose.ci.yml up -d
                    
//                     # Wait for services to be ready
                

//                     # Run the e2e tests
//                     chmod +x e2e.sh
//                     ./e2e.sh ${SERVER_IP}
//                     '''
//                 }
//             }
//         }

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
                     sshagent(['github']) {
                        sh """
                            git config user.email "jenkins@jenkins.com"
                            git config user.name "Jenkins"
                            git tag -a ${RELEASE_TAG} -m "Release ${RELEASE_TAG}"
                            git push git@github.com:CarmitHaas/Horsing-Around.git ${RELEASE_TAG}
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
    //                sshagent(['github-ssh-key']) {
    //                     sh """
    //                         git clone git@github.com:CarmitHaas/HorsingAround-gitops.git
    //                         cd HorsingAround-gitops
    //                         sed -i 's|image: .*|image: ${ECR_REGISTRY}/${ECR_REPOSITORY}:${RELEASE_TAG}|' deployment.yaml
    //                         git add deployment.yaml
    //                         git commit -m "Update image to ${RELEASE_TAG}"
    //                         git push origin main
    //                     """
    // //                 }
    //             }
    //         }
    //     }
    // }
    }

    post {
        always {
            sh 'docker-compose -f docker-compose.ci.yml down || true'
        }
       
    }
}
//         post {
//         failure {
//             emailext (
//                 subject: "Build Failed: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
//                 body: """<p>The build failed. Please check the Jenkins console output for details.</p>
//                          <p>Build URL: ${env.BUILD_URL}</p>""",
//                 recipientProviders: [culprits(), developers()],
//                 attachLog: true,
//                 compressLog: true
//             )
//         }
//         success {
//             emailext (
//                 subject: "Build Successful: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
//                 body: """<p>The build was successful. Great job!!</p>
//                          <p>Build URL: ${env.BUILD_URL}</p>""",
//                 recipientProviders: [culprits(), developers()],
//                 attachLog: true,
//                 compressLog: true
//             )
//         }
//     }
// }

