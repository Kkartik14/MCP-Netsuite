import json
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger("netsuite_client")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("netsuite_client.log")
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

load_dotenv()

class NetSuiteClient:
    def __init__(self):
        self.is_mock = True  
        try:
            with open("mocks/netsuite.json", "r") as f:
                self.mocks = json.load(f)
            logger.info("Loaded mock data successfully")
            logger.info(f"Available mock keys: {list(self.mocks.keys())}")
        except Exception as e:
            logger.error(f"Error loading mock data: {str(e)}")
            raise

    def get(self, endpoint, params=None):
        if self.is_mock:
            endpoint_key = endpoint.removeprefix("/services/rest/")
            logger.info(f"Looking up mock data for endpoint: {endpoint}, key: {endpoint_key}")
            if endpoint_key in self.mocks:
                logger.info(f"Found mock data for {endpoint_key}")
                return self.mocks[endpoint_key]
            logger.error(f"Mock data not found for {endpoint_key}")
            raise ValueError(f"Mock data not found for {endpoint}")
        raise NotImplementedError("Real NetSuite API requires credentials")

    def post(self, endpoint, data):
        if self.is_mock:
            endpoint_key = endpoint.removeprefix("/services/rest/")
            logger.info(f"Looking up mock data for endpoint: {endpoint}, key: {endpoint_key}")
            if endpoint_key in self.mocks:
                logger.info(f"Found mock data for {endpoint_key}")
                return self.mocks[endpoint_key]
            logger.info(f"No mock data for {endpoint_key}, returning default response")
            return {"id": "mock_id", "status": "created"}
        raise NotImplementedError("Real NetSuite API requires credentials")