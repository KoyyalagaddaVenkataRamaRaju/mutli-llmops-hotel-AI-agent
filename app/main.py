import os
import socket
import subprocess
import sys
import time
from dotenv import load_dotenv
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

load_dotenv()

BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", 8000))

def free_port(port: int = 8000):
    """
    Checks if the specified port is already bound.
    If occupied by an orphaned or existing process, terminates it to prevent [Errno 10048].
    Cross-platform safe (Windows & Linux / Docker).
    """
    check_host = "127.0.0.1" if BACKEND_HOST in ("0.0.0.0", "") else BACKEND_HOST
    try:
        with socket.create_connection((check_host, port), timeout=0.3):
            logger.info(f"Port {port} is currently bound. Freeing socket address...")
            if os.name == 'nt':
                cmd = f'netstat -ano | findstr :{port}'
                out = subprocess.check_output(cmd, shell=True, text=True)
                for line in out.strip().splitlines():
                    parts = line.strip().split()
                    if len(parts) >= 5 and "LISTENING" in parts:
                        pid = int(parts[-1])
                        if pid != os.getpid():
                            logger.info(f"Releasing port {port} by terminating process PID {pid}...")
                            subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            time.sleep(1.2)
                            break
            else:
                subprocess.run(f"fuser -k {port}/tcp", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(1.0)
    except Exception:
        pass

def start_backend():
    # Guarantee port 8000 is free before starting
    free_port(BACKEND_PORT)
    logger.info("Starting StayEase FastAPI backend on http://%s:%d...", BACKEND_HOST, BACKEND_PORT)
    return subprocess.Popen([
        sys.executable,
        "-m",
        "uvicorn",
        "app.backend.api:app",
        "--host",
        BACKEND_HOST,
        "--port",
        str(BACKEND_PORT),
    ])

def wait_for_backend(process, timeout=30):
    deadline = time.monotonic() + timeout
    check_host = "127.0.0.1" if BACKEND_HOST in ("0.0.0.0", "") else BACKEND_HOST
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Backend exited prematurely with code {process.returncode}")
        try:
            with socket.create_connection((check_host, BACKEND_PORT), timeout=0.5):
                logger.info("Backend successfully initialized and listening on http://%s:%d", check_host, BACKEND_PORT)
                return
        except OSError:
            time.sleep(0.3)
    raise TimeoutError(f"Backend did not start on {BACKEND_HOST}:{BACKEND_PORT} within {timeout}s")

def run_frontend():
    try:
        frontend_port = int(os.getenv("PORT", os.getenv("STREAMLIT_SERVER_PORT", 8501)))
        frontend_host = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")
        free_port(frontend_port)
        logger.info("Starting StayEase Enterprise Streamlit UI on %s:%d...", frontend_host, frontend_port)
        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app/frontend/ui.py",
            f"--server.port={frontend_port}",
            f"--server.address={frontend_host}",
            "--server.headless=true"
        ], check=True)
    except Exception as e:
        logger.error("Error occurred while running Streamlit frontend: %s", e)
        raise CustomException("Failed to run frontend service", error_detail=e)

if __name__ == "__main__":
    backend_process = None
    try:
        backend_process = start_backend()
        wait_for_backend(backend_process)
        run_frontend()

    except KeyboardInterrupt:
        logger.info("Received shutdown signal. Stopping services...")
    except Exception as e:
        logger.exception("Exception occurred during service execution: %s", str(e))
    finally:
        if backend_process is not None and backend_process.poll() is None:
            logger.info("Terminating backend process...")
            backend_process.terminate()
            try:
                backend_process.wait(timeout=4)
            except subprocess.TimeoutExpired:
                backend_process.kill()
                backend_process.wait()
        logger.info("StayEase Enterprise PMS services terminated.")
