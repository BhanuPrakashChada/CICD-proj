pipeline {
    agent { label 'Jenkins-Agent' }
    tools {
        python 'Python3'
        docker 'docker'
    }
    environment {
        APP_NAME = "sys-monitoring"
        DOCKER_USER = credentials("DOCKER_HUB_USERNAME")
        DOCKER_PASS = credentials("DOCKER_HUB_TOKEN")
        IMAGE_NAME = "${DOCKER_USER}/${APP_NAME}"
        IMAGE_TAG = "${RELEASE}-${BUILD_NUMBER}"
        JENKINS_API_TOKEN = credentials("JENKINS_API_TOKEN")
        KUBE_NAMESPACE = "default"  
        KUBE_CLUSTER = "minikube"
        KUBE_CONFIG = credentials("KUBE_CONFIG")
        KUBE_CONTEXT = "minikube"

    }
    stages {
        stage("Cleanup Workspace") {
            steps {
                cleanWs()
            }
        }

        stage("Start Minikube") {
            steps {
                script {
                    sh "minikube start"
                }
            }
        }

        stage("Checkout from SCM") {
            steps {
                git branch: 'main', credentialsId: 'github', url: 'https://github.com/BhanuPrakashChada/CICD-proj'
            }
        }

        stage("Build Application") {
            steps {
                script {
                    sh 'pip install -r requirements.txt'
                    sh 'python setup.py build'
                }
            }
        }

        stage('Unit Tests') {
            steps {
                script {
                    sh 'python -m unittest discover -s tests/unittest -p "test_unit*.py"'
                }
            }
            post {
                success { 
                    slackSend channel: '#bhanu_Jenkinstest', color: 'good', message: "Unittest Success", teamDomain: 'testnotifgroup', tokenCredentialId: 'slack-token'
                }
                failure { 
                    slackSend channel: '#bhanu_Jenkinstest', color: 'danger', message: "Unittest Failed", teamDomain: 'testnotifgroup', tokenCredentialId: 'slack-token'
                }
            }

        }

        stage('Integration Tests') {
            steps {
                script {
                    sh 'python -m unittest discover -s tests/integration -p "test_integration*.py"'
                }
            }
            post {
                success { 
                    slackSend channel: '#bhanu_Jenkinstest', color: 'good', message: "Integration_test Success", teamDomain: 'testnotifgroup', tokenCredentialId: 'slack-token'
                }
                failure { 
                    slackSend channel: '#bhanu_Jenkinstest', color: 'danger', message: "Integartion_test Failed", teamDomain: 'testnotifgroup', tokenCredentialId: 'slack-token'
                }
            }
        }

        stage("Static Code Analysis") {
            steps {
                script {
                    sh 'flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics'
                }
            }
        }

        stage("Security Scans") {
            steps {
                script {
                    sh 'bandit -r . -ll'
                }
            }
        }

        stage("Build & Push Docker Image") {
            steps {
                script {
                    sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                    sh "docker login -u ${DOCKER_USER} -p ${DOCKER_PASS}"
                    sh "docker push ${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest"
                    sh "docker push ${IMAGE_NAME}:latest"
                }
            }
        }

        stage("Scale Deployment") {
            steps {
                script {
                    sh "kubectl scale deployment ${KUBE_DEPLOYMENT_NAME} --replicas=5 --namespace=${KUBE_NAMESPACE}"
                }
            }
        }

        stage("Health Checks") {
            steps {
                script {
                    sh "kubectl wait --for=condition=ready pod -l app=${KUBE_DEPLOYMENT_NAME} --timeout=300s --namespace=${KUBE_NAMESPACE}"
                }
            }
        }

        stage("Deploy to Kubernetes") {
            steps {
                script {
                    sh "kubectl config use-context ${KUBE_CONTEXT}"
                    sh "kubectl apply -f kubernetes/deployment.yaml --namespace=${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/service.yaml --namespace=${KUBE_NAMESPACE}"
                }
            }
        }

        stage("settingup Prometheus"){
            steps {
                script{
                    sh "kubectl apply -f kubernetes/prometheus/prometheus-config.yaml --namespace=${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/prometheus/prometheus-deployment.yaml --namespace=${KUBE_NAMESPACE}"
                }
            }
        }

        post {
            always {
                prometheusMonitoring()
            }
        }

        post {
                success { 
                    slackSend channel: '#bhanu_Jenkinstest', color: 'good', message: "CICD pipeline Success", teamDomain: 'testnotifgroup', tokenCredentialId: 'slack-token'
                }
                failure { 
                    slackSend channel: '#bhanu_Jenkinstest', color: 'danger', message: "Pipeline Failed!! PLease check logs for more details", teamDomain: 'testnotifgroup', tokenCredentialId: 'slack-token'
                }
            }

    }
}
