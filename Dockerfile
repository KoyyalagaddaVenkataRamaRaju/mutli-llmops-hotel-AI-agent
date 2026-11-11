# ==============================================================================
# StayEase Enterprise AI Agent OS - Multi-Container / Standalone Dockerfile
# Dual Services: FastAPI Backend (8000) + Streamlit Luxury UI (8501)
# ==============================================================================

FROM python:3.11-slim

# Set environment configurations
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    BACKEND_HOST=0.0.0.0 \
    BACKEND_PORT=8000 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Install essential system utilities (curl for container healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency specifications first to leverage Docker layer caching
COPY requirements.txt setup.py ./

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e .

# Copy application source code and pre-seeded database
COPY . .

# Expose ports: 8501 (Streamlit Frontend Cockpit) & 8000 (FastAPI Operations API)
EXPOSE 8501 8000

# Container Healthcheck verifying both frontend and backend endpoints
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health && curl -f http://localhost:8000/stats || exit 1

# Start the unified orchestrator (launches FastAPI uvicorn + Streamlit UI)
CMD ["python", "app/main.py"]

