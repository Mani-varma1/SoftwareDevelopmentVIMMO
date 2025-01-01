pipeline {
    agent {
        docker {
            image 'continuumio/miniconda3:latest'
            args '-u root -v /var/run/docker.sock:/var/run/docker.sock'  // Mount Docker socket
        }
    }

    environment {
        CONDA_ENV_NAME = 'VIMMO'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Docker') {
            steps {
                sh '''
                    # Add Docker's official GPG key
                    apt-get update
                    apt-get install -y ca-certificates curl gnupg
                    install -m 0755 -d /etc/apt/keyrings
                    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
                    chmod a+r /etc/apt/keyrings/docker.gpg

                    # Add Docker repository
                    echo \
                      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
                      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
                      tee /etc/apt/sources.list.d/docker.list > /dev/null

                    # Install Docker and Docker Compose
                    apt-get update
                    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
                '''
            }
        }

        stage('Setup Environment') {
            steps {
                sh '''
                    conda env create -f environment.yaml
                    conda activate ${CONDA_ENV_NAME}
                    pip install -e .[test]
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                    conda activate ${CONDA_ENV_NAME}
                    pytest -m "not integration"
                '''
            }
        }

        stage('Run Integration Tests') {
            steps {
                sh '''
                    # Start application using Docker
                    docker-compose up -d --build

                    # Wait for application to be ready
                    echo "Waiting for services to be ready..."
                    sleep 30  # Adjust based on your app's startup time

                    # Run integration tests
                    conda activate ${CONDA_ENV_NAME}
                    pytest -m "integration"
                '''
            }
        }
    }

    post {
        always {
            sh '''
                # Cleanup Docker
                docker-compose down --volumes --remove-orphans

                # Cleanup Conda environment
                conda deactivate
                conda env remove -n ${CONDA_ENV_NAME} -y || true
            '''
        }
    }
}