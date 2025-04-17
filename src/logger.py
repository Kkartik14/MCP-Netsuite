import logging

logger = logging.getLogger("netsuite_mcp")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("netsuite_mcp.log")
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)