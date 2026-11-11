# ==============================================================================
# Custom Jenkins Dockerfile - Docker-in-Docker (DinD / DooD) & LLMOps Runner
# Enables Jenkins to build, run, and orchestrate Docker containers natively.
# ==============================================================================

FROM jenkins/jenkins:lts-jdk17

# Switch to root user to install Docker and build utilities
USER root

# Avoid interactive prompts during apt package installation
ENV DEBIAN_FRONTEND=noninteractive

# 1. Install prerequisite system packages & Python 3 for LLMOps / MLOps pipelines
RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    sudo \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# 2. Add Docker official GPG key and APT repository
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null

# 3. Install Docker CLI, Docker Compose plugin, and Docker Buildx
RUN apt-get update && apt-get install -y --no-install-recommends \
    docker-ce-cli \
    docker-buildx-plugin \
    docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

# 4. Create docker group and add the jenkins user to it
RUN groupadd -f docker && \
    usermod -aG docker jenkins

# 5. Grant passwordless sudo to jenkins user (for socket permissions & CI pipelines)
RUN echo "jenkins ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# 6. Expose Jenkins standard ports:
#    8080  - Web Dashboard UI
#    50000 - Inbound Agent Listener (JNLP)
EXPOSE 8080 50000

# 7. Switch back to the non-root jenkins user
USER jenkins

# Set default Jenkins home directory
WORKDIR /var/jenkins_home

