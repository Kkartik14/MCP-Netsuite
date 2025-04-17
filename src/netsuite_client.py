import json
import logging
from typing import Dict, Any
import os
import sys

# Set up logging
logger = logging.getLogger("netsuite_client")
logger.setLevel(logging.INFO)
log_file = os.path.join(os.path.dirname(__file__), "..", "logs", "netsuite_client.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)
handler = logging.FileHandler(log_file)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

class NetSuiteClient:
    def __init__(self):
        self.is_mock = os.getenv("NETSUITE_MOCK", "true").lower() == "true"
        try:
            # Use parent directory to reach mocks/ from src/
            mock_file = os.path.join(os.path.dirname(__file__), "..", "mocks", "netsuite.json")
            logger.debug(f"Attempting to load mock data from: {mock_file}")
            with open(mock_file, "r") as f:
                self.mocks = json.load(f)
            logger.info("Loaded mock data successfully")
            logger.info(f"Available mock keys: {list(self.mocks.keys())}")
        except Exception as e:
            logger.error(f"Error loading mock data: {str(e)}")
            print(f"NetSuiteClient init failed: {str(e)}", file=sys.stderr)
            raise

    async def get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        endpoint_key = endpoint.removeprefix("/services/rest/")
        logger.info(f"GET request for endpoint: {endpoint}, key: {endpoint_key}")
        if endpoint_key in self.mocks:
            logger.info(f"Found mock data for {endpoint_key}")
            return self.mocks[endpoint_key]
        logger.error(f"Mock data not found for {endpoint_key}")
        raise ValueError(f"Mock data not found for endpoint: {endpoint}")

    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        endpoint_key = endpoint.removeprefix("/services/rest/")
        logger.info(f"POST request for endpoint: {endpoint}, key: {endpoint_key}")
        if endpoint_key in self.mocks:
            logger.info(f"Found mock data for {endpoint_key}")
            return self.mocks[endpoint_key]
        logger.info(f"No mock data for {endpoint_key}, returning default response")
        return {"id": f"mock_{endpoint_key.split('/')[-1]}", "status": "created"}

    async def patch(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        endpoint_key = endpoint.removeprefix("/services/rest/")
        logger.info(f"PATCH request for endpoint: {endpoint}, key: {endpoint_key}")
        if endpoint_key in self.mocks:
            logger.info(f"Found mock data for {endpoint_key}")
            return self.mocks[endpoint_key]
        logger.info(f"No mock data for {endpoint_key}, returning default response")
        return {"id": f"mock_{endpoint_key.split('/')[-1]}", "status": "updated"}