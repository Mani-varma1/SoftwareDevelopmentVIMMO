pipeline {
    agent {
        docker {
            image 'alpine:latest'
            args '-u 0:0' // Run the container as root
        }
    }

    environment {
        CONDA_ENV_NAME = 'VIMMO'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Setup Conda Environment') {
            steps {
                echo 'Setting up Conda environment...'
                sh '''
                # Install Miniconda if not present
                if ! command -v conda &> /dev/null; then
                    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
                    bash miniconda.sh -b -p $HOME/miniconda
                    export PATH="$HOME/miniconda/bin:$PATH"
                fi

                # Initialize Conda and create environment
                export PATH="$HOME/miniconda/bin:$PATH"
                source $HOME/miniconda/etc/profile.d/conda.sh
                conda init bash
                conda env create -f environment.yaml
                conda activate ${CONDA_ENV_NAME}

                # Install dependencies
                pip install -e .[test]
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                echo 'Running unit tests...'
                sh '''
                export PATH="$HOME/miniconda/bin:$PATH"
                source $HOME/miniconda/etc/profile.d/conda.sh
                conda activate ${CONDA_ENV_NAME}
                pytest -m "not integration"
                '''
            }
        }

        stage('Build Docker Application and Run Integration Tests') {
            steps {
                echo 'Starting application and running integration tests using Docker Compose...'
                sh '''
                docker-compose up -d --build
                echo 'Waiting for the application to be ready...'
                sleep 180 # Adjust based on application startup time
                pytest
                '''
            }
        }
    }

    post {
        always {
            echo 'Cleaning up resources...'
            sh 'docker-compose down'

            sh '''
                # Deactivate and remove Conda environment
                export PATH="$HOME/miniconda/bin:$PATH"
                source $HOME/miniconda/etc/profile.d/conda.sh
                conda deactivate
                conda env remove -n ${CONDA_ENV_NAME}
            '''
        }

        success {
            echo 'Pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed. Check the logs for details.'
        }
    }
}
