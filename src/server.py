from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent
from netsuite_client import NetSuiteClient
from logger import logger
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import json
import sqlparse
import sys
import traceback
import os

# Define custom McpError and ErrorData
class ErrorData(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None

class McpError(Exception):
    def __init__(self, error_data: ErrorData):
        self.error_data = error_data
        super().__init__(error_data.message)

mcp = FastMCP("NetSuite")
ns_client = NetSuiteClient()

# Input Models for Dedicated Tools
class CustomerInput(BaseModel):
    customer_id: str = Field(..., pattern=r"^\d+$", description="Numeric customer ID")

class CreateCustomerInput(BaseModel):
    company_name: str = Field(..., min_length=1, description="Company name")
    email: str = Field(..., description="Email address")
    subsidiary: str = Field(..., description="Subsidiary ID")

class SearchCustomersInput(BaseModel):
    query: str = Field(..., min_length=3, description="Search term for company name or email")
    limit: int = Field(default=10, ge=1, le=100, description="Number of results to return")
    offset: int = Field(default=0, ge=0, description="Result offset")

class SalesOrderInput(BaseModel):
    sales_order_id: str = Field(..., pattern=r"^\d+$", description="Numeric sales order ID")

class CreateSalesOrderInput(BaseModel):
    customer_id: str = Field(..., pattern=r"^\d+$", description="Numeric customer ID")
    item_id: str = Field(..., pattern=r"^\d+$", description="Numeric item ID")
    quantity: int = Field(..., ge=1, description="Quantity of items")

class InvoiceInput(BaseModel):
    invoice_id: str = Field(..., pattern=r"^\d+$", description="Numeric invoice ID")

class CreateInvoiceInput(BaseModel):
    sales_order_id: str = Field(..., pattern=r"^\d+$", description="Numeric sales order ID")
    amount: float = Field(..., gt=0, description="Invoice amount")

# Input Models for Generic Tools
class RecordInput(BaseModel):
    record_type: str = Field(..., description="NetSuite record type (e.g., customer, salesOrder)")
    record_id: str = Field(..., pattern=r"^\d+$", description="Numeric record ID")

class CreateRecordInput(BaseModel):
    record_type: str = Field(..., description="NetSuite record type (e.g., customer, salesOrder)")
    payload: Dict[str, Any] = Field(..., description="Record data as a JSON object")

class UpdateRecordInput(BaseModel):
    record_type: str = Field(..., description="NetSuite record type (e.g., customer, salesOrder)")
    record_id: str = Field(..., pattern=r"^\d+$", description="Numeric record ID")
    payload: Dict[str, Any] = Field(..., description="Updated record data as a JSON object")

class ExecuteSuiteQLInput(BaseModel):
    query: str = Field(..., description="SuiteQL SELECT query")
    limit: int = Field(default=100, ge=1, le=1000, description="Number of results to return")
    offset: int = Field(default=0, ge=0, description="Result offset")

# Tool Implementations
@mcp.tool()
async def fetch_customer(input: CustomerInput) -> Dict[str, Any]:
    logger.info(f"Calling fetch_customer with input: {input.model_dump()}")
    try:
        data = await ns_client.get(f"/services/rest/record/v1/customer/{input.customer_id}")
        logger.info(f"Fetched customer {input.customer_id} (Mock: {ns_client.is_mock})")
        return data
    except ValueError as e:
        logger.error(f"Error fetching customer {input.customer_id}: {str(e)}")
        raise McpError(ErrorData(code="INVALID_PARAMS", message=str(e)))
    except Exception as e:
        logger.error(f"Error fetching customer {input.customer_id}: {str(e)}")
        raise McpError(ErrorData(code="INTERNAL_ERROR", message=str(e)))

@mcp.tool()
async def create_customer(input: CreateCustomerInput) -> Dict[str, Any]:
    logger.info(f"Calling create_customer with input: {input.model_dump()}")
    try:
        payload = {
            "companyName": input.company_name,
            "email": input.email,
            "subsidiary": {"id": input.subsidiary}
        }
        data = await ns_client.post("/services/rest/record/v1/customer", payload)
        logger.info(f"Created customer {input.company_name} (Mock: {ns_client.is_mock})")
        return data
    except ValueError as e:
        logger.error(f"Error creating customer: {str(e)}")
        raise McpError(ErrorData(code="INVALID_PARAMS", message=str(e)))
    except Exception as e:
        logger.error(f"Error creating customer: {str(e)}")
        raise McpError(ErrorData(code="INTERNAL_ERROR", message=str(e)))

@mcp.tool()
async def search_customers(input: SearchCustomersInput) -> Dict[str, Any]:
    logger.info(f"Calling search_customers with input: {input.model_dump()}")
    try:
        suiteql = {
            "q": f"SELECT id, companyName, email FROM customer WHERE companyName LIKE '%{input.query}%' OR email LIKE '%{input.query}%'",
            "limit": input.limit,
            "offset": input.offset
        }
        data = await ns_client.post("/services/rest/query/v1/suiteql", suiteql)
        logger.info(f"Searched customers with query: {input.query} (Mock: {ns_client.is_mock})")
        return {"items": data.get("items", []), "totalResults": data.get("totalResults", 0)}
    except ValueError as e:
        logger.error(f"Error searching customers: {str(e)}")
        raise McpError(ErrorData(code="INVALID_PARAMS", message=str(e)))
    except Exception as e:
        logger.error(f"Error searching customers: {str(e)}")
        raise McpError(ErrorData(code="INTERNAL_ERROR", message=str(e)))

@mcp.tool()
async def fetch_sales_order(input: SalesOrderInput) -> Dict[str, Any]:
    logger.info(f"Calling fetch_sales_order with input: {input.model_dump()}")
    try:
        data = await ns_client.get(f"/services/rest/record/v1/salesOrder/{input.sales_order_id}")
        logger.info(f"Fetched sales order {input.sales_order_id} (Mock: {ns_client.is_mock})")
        return data
    except ValueError as e:
        logger.error(f"Error fetching sales order {input.sales_order_id}: {str(e)}")
        raise McpError(ErrorData(code="INVALID_PARAMS", message=str(e)))
    except Exception as e:
        logger.error(f"Error fetching sales order {input.sales_order_id}: {str(e)}")
        raise McpError(ErrorData(code="INTERNAL_ERROR", message=str(e)))

@mcp.tool()
async def create_sales_order(input: CreateSalesOrderInput) -> Dict[str, Any]:
    logger.info(f"Calling create_sales_order with input: {input.model_dump()}")
    try:
        payload = {
            "entity": {"id": input.customer_id},
            "item": {"items": [{"item": {"id": input.item_id}, "quantity": input.quantity}]}
        }
        data = await ns_client.post("/services/rest/record/v1/salesOrder", payload)
        logger.info(f"Created sales order for customer {input.customer_id} (Mock: {ns_client.is_mock})")
        return data
    except ValueError as e:
        logger.error(f"Error creating sales order: {str(e)}")
        raise McpError(ErrorData(code="INVALID_PARAMS", message=str(e)))
    except Exception as e:
        logger.error(f"Error creating sales order: {str(e)}")
        raise McpError(ErrorData(code="INTERNAL_ERROR", message=str(e)))

@mcp.tool()
async def fetch_invoice(input: InvoiceInput) -> Dict[str, Any]:
    logger.info(f"Calling fetch_invoice with input: {input.model_dump()}")
    try:
        data = await ns_client.get(f"/services/rest/record/v1/invoice/{input.invoice_id}")
        logger.info(f"Fetched invoice {input.invoice_id} (Mock: {ns_client.is_mock})")
        return data
    except ValueError as e:
        logger.error(f"Error fetching invoice {input.invoice_id}: {str(e)}")
        raise McpError(ErrorData(code="INVALID_PARAMS", message=str(e)))
    except Exception as e:
        logger.error(f"Error fetching invoice {input.invoice_id}: {str(e)}")
        raise McpError(ErrorData(code="INTERNAL_ERROR", message=str(e)))

@mcp.tool()
async def create_invoice(input: CreateInvoiceInput) -> Dict[str, Any]:
    logger.info(f"Calling create_invoice with input: {input.model_dump()}")
    try:
        payload = {
            "createdFrom": {"id": input.sales_order_id},
            "total": input.amount
        }
        data = await ns_client.post("/services/rest/record/v1/invoice", payload)
        logger.info(f"Created invoice from sales order {input.sales_order_id} (Mock: {ns_client.is_mock})")
        return data
    except ValueError as e:
        logger.error(f"Error creating invoice: {str(e)}")
        raise McpError(ErrorData(code="INVALID_PARAMS", message=str(e)))
    except Exception as e:
        logger.error(f"Error creating invoice: {str(e)}")
        raise McpError(ErrorData(code="INTERNAL_ERROR", message=str(e)))

@mcp.tool()
async def fetch_record(input: RecordInput) -> Dict[str, Any]:
    logger.info(f"Calling fetch_record with input: {input.model_dump()}")
    try:
        metadata = await fetch_metadata()
        valid_types = [record["type"] for record in metadata.get("records", [])]
        if input.record_type not in valid_types:
            raise McpError(ErrorData(code="INVALID_PARAMS", message=f"Invalid record type: {input.record_type}"))
        data = await ns_client.get(f"/services/rest/record/v1/{input.record_type}/{input.record_id}")
        logger.info(f"Fetched {input.record_type} {input.record_id} (Mock: {ns_client.is_mock})")
        return data
    except ValueError as e:
        logger.error(f"Error fetching {input.record_type} {input.record_id}: {str(e)}")
        raise McpError(ErrorData(code="INVALID_PARAMS", message=str(e)))
    except Exception as e:
        logger.error(f"Error fetching {input.record_type} {input.record_id}: {str(e)}")
        raise McpError(ErrorData(code="INTERNAL_ERROR", message=str(e)))

@mcp.tool()
async def create_record(input: CreateRecordInput) -> Dict[str, Any]:
    logger.info(f"Calling create_record with input: {input.model_dump()}")
    try:
        metadata = await fetch_metadata()
        valid_types = [record["type"] for record in metadata.get("records", [])]
        if input.record_type not in valid_types:
            raise McpError(ErrorData(code="INVALID_PARAMS", message=f"Invalid record type: {input.record_type}"))
        data = await ns_client.post(f"/services/rest/record/v1/{input.record_type}", input.payload)
        logger.info(f"Created {input.record_type} (Mock: {ns_client.is_mock})")
        return data
    except ValueError as e:
        logger.error(f"Error creating {input.record_type}: {str(e)}")
        raise McpError(ErrorData(code="INVALID_PARAMS", message=str(e)))
    except Exception as e:
        logger.error(f"Error creating {input.record_type}: {str(e)}")
        raise McpError(ErrorData(code="INTERNAL_ERROR", message=str(e)))

@mcp.tool()
async def update_record(input: UpdateRecordInput) -> Dict[str, Any]:
    logger.info(f"Calling update_record with input: {input.model_dump()}")
    try:
        metadata = await fetch_metadata()
        valid_types = [record["type"] for record in metadata.get("records", [])]
        if input.record_type not in valid_types:
            raise McpError(ErrorData(code="INVALID_PARAMS", message=f"Invalid record type: {input.record_type}"))
        data = await ns_client.patch(f"/services/rest/record/v1/{input.record_type}/{input.record_id}", input.payload)
        logger.info(f"Updated {input.record_type} {input.record_id} (Mock: {ns_client.is_mock})")
        return data
    except ValueError as e:
        logger.error(f"Error updating {input.record_type} {input.record_id}: {str(e)}")
        raise McpError(ErrorData(code="INVALID_PARAMS", message=str(e)))
    except Exception as e:
        logger.error(f"Error updating {input.record_type} {input.record_id}: {str(e)}")
        raise McpError(ErrorData(code="INTERNAL_ERROR", message=str(e)))

@mcp.tool()
async def execute_suiteql(input: ExecuteSuiteQLInput) -> Dict[str, Any]:
    logger.info(f"Calling execute_suiteql with input: {input.model_dump()}")
    try:
        if not input.query.strip():
            raise McpError(ErrorData(code="INVALID_PARAMS", message="Query cannot be empty"))
        parsed = sqlparse.parse(input.query)
        if not parsed or parsed[0].get_type() != "SELECT":
            raise McpError(ErrorData(code="INVALID_PARAMS", message="Only SELECT queries supported"))
        suiteql = {"q": input.query, "limit": input.limit, "offset": input.offset}
        data = await ns_client.post("/services/rest/query/v1/suiteql", suiteql)
        logger.info(f"Executed SuiteQL: {input.query} (Mock: {ns_client.is_mock})")
        return {"items": data.get("items", []), "totalResults": data.get("totalResults", 0)}
    except ValueError as e:
        logger.error(f"Error executing SuiteQL: {str(e)}")
        raise McpError(ErrorData(code="INVALID_PARAMS", message=str(e)))
    except IndexError as e:
        logger.error(f"Error parsing SuiteQL query: {str(e)}")
        raise McpError(ErrorData(code="INVALID_PARAMS", message="Invalid query syntax"))
    except Exception as e:
        logger.error(f"Error executing SuiteQL: {str(e)}")
        raise McpError(ErrorData(code="INTERNAL_ERROR", message=str(e)))

@mcp.tool()
async def fetch_metadata() -> Dict[str, Any]:
    logger.info("Calling fetch_metadata")
    try:
        data = await ns_client.get("/services/rest/record/v1/metadata-catalog")
        logger.info(f"Fetched metadata (Mock: {ns_client.is_mock})")
        return data
    except ValueError as e:
        logger.error(f"Error fetching metadata: {str(e)}")
        raise McpError(ErrorData(code="INVALID_PARAMS", message=str(e)))
    except Exception as e:
        logger.error(f"Error fetching metadata: {str(e)}")
        raise McpError(ErrorData(code="INTERNAL_ERROR", message=str(e)))

# Tool Definitions
def list_tools() -> List[Tool]:
    logger.info("Executing list_tools")
    tools = [
        Tool(name="fetch_customer", description="Fetch a customer by ID", inputSchema=CustomerInput.model_json_schema()),
        Tool(name="create_customer", description="Create a new customer", inputSchema=CreateCustomerInput.model_json_schema()),
        Tool(name="search_customers", description="Search customers by name or email", inputSchema=SearchCustomersInput.model_json_schema()),
        Tool(name="fetch_sales_order", description="Fetch a sales order by ID", inputSchema=SalesOrderInput.model_json_schema()),
        Tool(name="create_sales_order", description="Create a sales order", inputSchema=CreateSalesOrderInput.model_json_schema()),
        Tool(name="fetch_invoice", description="Fetch an invoice by ID", inputSchema=InvoiceInput.model_json_schema()),
        Tool(name="create_invoice", description="Create an invoice", inputSchema=CreateInvoiceInput.model_json_schema()),
        Tool(name="fetch_record", description="Fetch any NetSuite record by type and ID", inputSchema=RecordInput.model_json_schema()),
        Tool(name="create_record", description="Create any NetSuite record", inputSchema=CreateRecordInput.model_json_schema()),
        Tool(name="update_record", description="Update any NetSuite record", inputSchema=UpdateRecordInput.model_json_schema()),
        Tool(name="execute_suiteql", description="Execute a SuiteQL query", inputSchema=ExecuteSuiteQLInput.model_json_schema()),
        Tool(name="fetch_metadata", description="Fetch NetSuite record metadata", inputSchema={}),
    ]
    logger.info(f"Returning {len(tools)} tools")
    return tools

# Register tools manually
logger.info("Registering tools")
mcp.tools = list_tools()
logger.info("Registration complete")

if __name__ == "__main__":
    logger.info("Starting NetSuite MCP server")
    # Validate MCP_API_KEY before starting
    api_key = os.getenv("MCP_API_KEY")
    if not api_key:
        logger.error("Missing MCP_API_KEY environment variable")
        print("Error: Missing MCP_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)
    if api_key != "default_key":
        logger.error(f"Invalid MCP_API_KEY: {api_key}")
        print(f"Error: Invalid MCP_API_KEY: {api_key}", file=sys.stderr)
        sys.exit(1)
    logger.info("MCP_API_KEY validated successfully")
    try:
        mcp.run(transport="stdio")
        logger.info("NetSuite MCP server is running, waiting for client requests")
    except Exception as e:
        logger.error(f"Server failed: {str(e)}")
        print(f"Server failed with error: {str(e)}\n{traceback.format_exc()}", file=sys.stderr)
        raise