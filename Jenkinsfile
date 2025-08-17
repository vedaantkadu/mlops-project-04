pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        GCP_PROJECT = 'alpine-proton-467708-f6'
        IMAGE = 'ml-anime-project'
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
        CLUSTER_NAME = 'mlops-anime-project'
        CLUSTER_REGION = 'us-central1'
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

                        # Build and push Docker image
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

                        # Get cluster credentials
                        gcloud container clusters get-credentials ${CLUSTER_NAME} --region ${CLUSTER_REGION}

                        # Apply deployment with Autopilot-safe options
                        kubectl apply -f deployment.yaml --validate=false --request-timeout=2m
                    """
                }
            }
        }
    }
}
