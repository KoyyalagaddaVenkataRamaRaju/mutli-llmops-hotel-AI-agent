pipeline {
    agent any

    environment {
        APP_NAME    = "stayease-ai-os"
        IMAGE_TAG   = "latest"
        BACKEND_URL = "http://127.0.0.1:8000"
    }

    stages {
        stage('1. Checkout Repository') {
            steps {
                echo '📥 Checking out StayEase AI Agent OS from GitHub...'
                checkout scmGit(
                    branches: [[name: '*/main']],
                    extensions: [],
                    userRemoteConfigs: [[
                        credentialsId: 'LLMOps',
                        url: 'https://github.com/KoyyalagaddaVenkataRamaRaju/mutli-llmops-hotel-AI-agent.git'
                    ]]
                )
            }
        }

        stage('2. Python Validation & Linting') {
            steps {
                echo '🐍 Validating Python 3 syntax & core project modules...'
                sh '''
                    echo "Python runtime version:"
                    python3 --version

                    # Compile and validate core entrypoints
                    python3 -m py_compile app/main.py app/backend/api.py app/frontend/ui.py
                    echo "✅ All Python files compiled with zero syntax errors."
                '''
            }
        }

        stage('3. Verify Database Integrity') {
            steps {
                echo '🗄️ Verifying SQLite database and hotel assets...'
                sh '''
                    python3 -c "
import sqlite3, os
db_file = 'hotel.db'
if not os.path.exists(db_file):
    raise FileNotFoundError(f'Critical file {db_file} not found!')
conn = sqlite3.connect(db_file)
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM rooms')
rooms_cnt = cur.fetchone()[0]
print(f'✅ SQLite Check Passed: {rooms_cnt} rooms verified.')
conn.close()
"
                '''
            }
        }

        stage('4. Docker Build Image') {
            steps {
                echo "🐳 Building Docker container image: ${APP_NAME}:${IMAGE_TAG}..."
                sh '''
                    docker build -t ${APP_NAME}:${IMAGE_TAG} .
                    echo "Docker image built successfully:"
                    docker images | grep ${APP_NAME}
                '''
            }
        }

        stage('5. Container Smoke Test') {
            steps {
                echo '🧪 Launching container smoke test...'
                sh '''
                    # Clean up any lingering test container
                    docker rm -f stayease-ci-smoke-test || true

                    # Start temporary container on test ports
                    docker run -d --name stayease-ci-smoke-test -p 8505:8501 -p 8005:8000 ${APP_NAME}:${IMAGE_TAG}

                    # Wait for services to initialize
                    sleep 12

                    # Check container status
                    docker ps | grep stayease-ci-smoke-test

                    # Tear down test container
                    docker stop stayease-ci-smoke-test
                    docker rm stayease-ci-smoke-test
                    echo "✅ Smoke test completed successfully."
                '''
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up temporary test containers...'
            sh 'docker rm -f stayease-ci-smoke-test || true'
        }
        success {
            echo '🎉 StayEase LLMOps CI/CD Pipeline Completed Successfully!'
        }
        failure {
            echo '❌ Pipeline failed! Please inspect the console log above.'
        }
    }
}

