# Custom Jenkins Docker-in-Docker (DinD / DooD) Runner

This directory contains the custom Jenkins Docker configuration designed for **LLMOps / MLOps CI/CD pipelines**. It equips Jenkins with the Docker CLI, Docker Compose, Docker Buildx, and Python 3 tools inside the container so Jenkins can build and deploy the StayEase AI container directly.

---

## 🚀 Quick Start

### Option 1: Start with Docker Compose (Recommended)
From within the `custom_jenkins` folder:
```bash
docker compose up -d --build
```

### Option 2: Build and Run Standalone
```bash
# 1. Build the custom Jenkins image
docker build -t custom-jenkins:latest .

# 2. Run the container with the host Docker socket mounted
docker run -d \
  --name custom_jenkins_dind \
  -p 8080:8080 \
  -p 50000:50000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v jenkins_home_data:/var/jenkins_home \
  --privileged \
  custom-jenkins:latest
```

---

## 🔑 Unlocking Jenkins

Once the container is running:
1. Open [`http://localhost:8080`](http://localhost:8080) in your browser.
2. Retrieve the initial admin password:
   ```bash
   docker exec -it custom_jenkins_dind cat /var/jenkins_home/secrets/initialAdminPassword
   ```
3. Paste the password into the browser and select **Install suggested plugins**.

---

## 🛠️ Verification inside the Jenkins Container

To verify that Docker and Python are working inside Jenkins:
```bash
docker exec -it custom_jenkins_dind docker --version
docker exec -it custom_jenkins_dind docker compose version
docker exec -it custom_jenkins_dind python3 --version
```

