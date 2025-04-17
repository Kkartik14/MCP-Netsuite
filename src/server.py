from mcp.server.fastmcp import FastMCP
from netsuite_client import NetSuiteClient
from auth import require_api_key
from cache import cache_response
from logger import logger
import logging
from typing import Dict, Any, List

mcp = FastMCP("NetSuite")
ns_client = NetSuiteClient()

@mcp.resource("netsuite://customer/{customer_id}")
@require_api_key
@cache_response(ttl=300)
def fetch_customer(customer_id: str) -> Dict[str, Any]:
    """Fetch a customer by ID"""
    if not customer_id.isdigit():
        raise ValueError("Customer ID must be numeric")
    try:
        data = ns_client.get(f"/services/rest/record/v1/customer/{customer_id}")
        logger.info(f"Fetched customer {customer_id} (Mock: {ns_client.is_mock})")
        return data
    except Exception as e:
        logger.error(f"Error fetching customer {customer_id}: {str(e)}")
        raise

@mcp.resource("netsuite://customers/search/{query}")
@require_api_key
def search_customers(query: str) -> Dict[str, Any]:
    """Search customers by name or email
    
    Args:
        query: Search term for company name or email
    """
    if not query or len(query) < 3:
        raise ValueError("Query must be at least 3 characters")
    try:

        limit = 10
        offset = 0
        suiteql = {
            "q": f"SELECT id, companyName, email FROM customer WHERE companyName LIKE '%{query}%' OR email LIKE '%{query}%'"
        }
        data = ns_client.post("/services/rest/query/v1/suiteql", suiteql)
        results = data.get("items", [])[offset:offset + limit]
        logger.info(f"Searched customers with query: {query} (Mock: {ns_client.is_mock})")
        return {"items": results, "totalResults": data.get("totalResults", len(results))}
    except Exception as e:
        logger.error(f"Error searching customers: {str(e)}")
        raise

@mcp.tool()
@require_api_key
def create_salesorder(customer_id: str, item_id: str, quantity: int) -> Dict[str, Any]:
    """Create a sales order for a customer"""
    if not (customer_id.isdigit() and item_id.isdigit() and quantity > 0):
        raise ValueError("Invalid input parameters")
    try:
        payload = {
            "entity": {"id": customer_id},
            "item": {"items": [{"item": {"id": item_id}, "quantity": quantity}]}
        }
        data = ns_client.post("/services/rest/record/v1/salesOrder", payload)
        logger.info(f"Created sales order for customer {customer_id} (Mock: {ns_client.is_mock})")
        return data
    except Exception as e:
        logger.error(f"Error creating sales order: {str(e)}")
        raise

@mcp.tool()
@require_api_key
def execute_suiteql(query: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    """Execute a SuiteQL query"""
    if not query.strip().startswith("SELECT"):
        raise ValueError("Only SELECT queries supported")
    try:
        suiteql = {"q": query, "limit": limit, "offset": offset}
        data = ns_client.post("/services/rest/query/v1/suiteql", suiteql)
        logger.info(f"Executed SuiteQL: {query} (Mock: {ns_client.is_mock})")
        return {"items": data.get("items", []), "totalResults": data.get("totalResults", 0)}
    except Exception as e:
        logger.error(f"Error executing SuiteQL: {str(e)}")
        raise

@mcp.resource("netsuite://metadata/records")
@require_api_key
@cache_response(ttl=3600)
def fetch_metadata() -> Dict[str, Any]:
    """Fetch NetSuite record metadata"""
    try:
        data = ns_client.get("/services/rest/record/v1/metadata-catalog")
        logger.info(f"Fetched metadata (Mock: {ns_client.is_mock})")
        return data
    except Exception as e:
        logger.error(f"Error fetching metadata: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting NetSuite MCP server...")
    mcp.run(transport="stdio")