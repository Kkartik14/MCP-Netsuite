import logging
import os

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file = os.path.join(os.path.dirname(__file__), "logs", "netsuite_mcp.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)  # Create logs directory if it doesn't exist
handler = logging.FileHandler(log_file)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)