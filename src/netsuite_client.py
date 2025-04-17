# src/netsuite_client.py
import json
import logging
from typing import Dict, Any

# Set up logging
logger = logging.getLogger("netsuite_client")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("netsuite_client.log")
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

class NetSuiteClient:
    def __init__(self):
        self.is_mock = True  # Always mock, as no NetSuite credentials are available
        try:
            with open("mocks/netsuite.json", "r") as f:
                self.mocks = json.load(f)
            logger.info("Loaded mock data successfully")
            logger.info(f"Available mock keys: {list(self.mocks.keys())}")
        except Exception as e:
            logger.error(f"Error loading mock data: {str(e)}")
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
        # For POST requests without mock data, return a default success response
        logger.info(f"No mock data for {endpoint_key}, returning default response")
        return {"id": f"mock_{endpoint_key.split('/')[-1]}", "status": "created"}

    async def patch(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        endpoint_key = endpoint.removeprefix("/services/rest/")
        logger.info(f"PATCH request for endpoint: {endpoint}, key: {endpoint_key}")
        if endpoint_key in self.mocks:
            logger.info(f"Found mock data for {endpoint_key}")
            return self.mocks[endpoint_key]
        # For PATCH requests without mock data, return a default success response
        logger.info(f"No mock data for {endpoint_key}, returning default response")
        return {"id": f"mock_{endpoint_key.split('/')[-1]}", "status": "updated"}