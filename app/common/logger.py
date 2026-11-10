import logging
import os
from datetime import datetime

LOSS_DIR="logs"
os.makedirs(LOSS_DIR, exist_ok=True)

LOG_FILE=os.path.join(LOSS_DIR, f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")

logging.basicConfig(
    filename=LOG_FILE,
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger