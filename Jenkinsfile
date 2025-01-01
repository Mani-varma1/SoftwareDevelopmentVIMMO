pipeline {
    agent {
        docker {
            image 'continuumio/miniconda3:latest'
            args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
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
                sh '''#!/bin/bash
                    # Initialize conda for shell interaction
                    conda init bash
                    source ~/.bashrc
                    
                    # Create and activate environment
                    conda env create -f environment.yaml
                    
                    # Activate environment with full path to avoid conda init issues
                    source $(conda info --base)/etc/profile.d/conda.sh
                    conda activate ${CONDA_ENV_NAME}
                    
                    # Install package
                    pip install -e .[test]
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''#!/bin/bash
                    source $(conda info --base)/etc/profile.d/conda.sh
                    conda activate ${CONDA_ENV_NAME}
                    pytest -m "not integration"
                '''
            }
        }

        stage('Run Integration Tests') {
            steps {
                sh '''#!/bin/bash
                    source $(conda info --base)/etc/profile.d/conda.sh
                    conda activate ${CONDA_ENV_NAME}
                    
                    # Use docker compose v2 command syntax
                    docker compose up -d --build
                    
                    echo "Waiting for services to be ready..."
                    sleep 30
                    
                    pytest -m "integration"
                '''
            }
        }
    }

    post {
        always {
            sh '''#!/bin/bash
                # Use docker compose v2 command syntax
                docker compose down --volumes --remove-orphans || true
                
                # Cleanup Conda environment
                source $(conda info --base)/etc/profile.d/conda.sh
                conda deactivate
                conda env remove -n ${CONDA_ENV_NAME} -y || true
            '''
        }
    }
}