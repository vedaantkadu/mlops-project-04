pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = 'alpine-proton-467708-f6'
        IMAGE = 'ml-anime-project'
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
    }

    stages {

        stage("Cloning from Github") {
            steps {
                checkout scmGit(
                    branches: [[name: '*/main']],
                    extensions: [],
                    userRemoteConfigs: [[
                        credentialsId: 'github-token',
                        url: 'https://github.com/vedaantkadu/mlops-project-04.git'
                    ]]
                )
            }
        }

        stage("Setup Virtual Env") {
            steps {
                sh """
                    python -m venv ${VENV_DIR}
                    ${VENV_DIR}/bin/pip install --upgrade pip
                    ${VENV_DIR}/bin/pip install -e .
                    ${VENV_DIR}/bin/pip install dvc
                """
            }
        }

        stage("DVC Pull") {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh """
                        ${VENV_DIR}/bin/dvc pull
                    """
                }
            }
        }

        stage("Build & Push Image to GCR") {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh """
                        export PATH=\$PATH:${GCLOUD_PATH}
                        gcloud auth activate-service-account --key-file=\${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        
                        # Configure Docker for GCR
                        gcloud auth configure-docker --quiet
                        
                        # Build and push to GCR
                        docker build -t gcr.io/${GCP_PROJECT}/${IMAGE}:latest .
                        docker push gcr.io/${GCP_PROJECT}/${IMAGE}:latest
                    """
                }
            }
        }

        stage("Deploy to Kubernetes") {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    sh """
                        export PATH=\$PATH:${GCLOUD_PATH}
                        gcloud auth activate-service-account --key-file=\${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud container clusters get-credentials anime-2507 --region us-central1
                        kubectl apply -f deployment.yaml
                    """
                }
            }
        }
    }
}
