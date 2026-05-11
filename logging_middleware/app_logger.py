import logging
import os
from datetime import datetime

# Setup professional logging configuration
LOG_FILE = os.path.join(os.path.dirname(__file__), "system_activity.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def log_api_event(endpoint, method, status_code, message="Success"):
    """Logs API requests and status results to a local file."""
    log_msg = f"[{method}] {endpoint} | Status: {status_code} | Info: {message}"
    if status_code >= 400:
        logging.error(log_msg)
    else:
        logging.info(log_msg)

if __name__ == "__main__":
    # Test logs to initialize the file
    print("Initializing system logs...")
    log_api_event("/auth", "POST", 200, "User Authenticated")
    log_api_event("/notifications", "GET", 200, "Fetched 10 notifications")
    print(f"Log file created at: {LOG_FILE}")