import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json

TOOL_DESCRIPTIONS = {
    "fetch_customer": "Fetch a customer by ID",
    "create_customer": "Create a new customer",
    "search_customers": "Search customers by name or email",
    "fetch_sales_order": "Fetch a sales order by ID",
    "create_sales_order": "Create a sales order",
    "fetch_invoice": "Fetch an invoice by ID",
    "create_invoice": "Create an invoice",
    "fetch_record": "Fetch any NetSuite record by type and ID",
    "create_record": "Create any NetSuite record",
    "update_record": "Update any NetSuite record",
    "execute_suiteql": "Execute a SuiteQL query",
    "fetch_metadata": "Fetch NetSuite record metadata"
}

async def run_client():
    server_params = StdioServerParameters(
        command="python",
        args=["src/server.py"],
        env={"MCP_API_KEY": "default_key"}
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("Listing tools:")
            tools_result = await session.list_tools()
            tools_with_descriptions = []
            for tool in tools_result.tools:
                tool_dict = tool.__dict__.copy()
                tool_dict["description"] = TOOL_DESCRIPTIONS.get(tool_dict["name"], "")
                tools_with_descriptions.append(tool_dict)
            print(json.dumps(tools_with_descriptions, indent=2))

            print("\nFetching customer:")
            result = await session.call_tool(
                "fetch_customer",
                {"input": {"customer_id": "123456"}}
            )
            content_texts = [item.text for item in result.content if hasattr(item, 'text')]
            print(json.dumps(content_texts, indent=2))

            print("\nCreating sales order:")
            result = await session.call_tool(
                "create_sales_order",
                {"input": {"customer_id": "123456", "item_id": "789", "quantity": 2}}
            )
            content_texts = [item.text for item in result.content if hasattr(item, 'text')]
            print(json.dumps(content_texts, indent=2))

            print("\nExecuting SuiteQL:")
            result = await session.call_tool(
                "execute_suiteql",
                {"input": {"query": "SELECT id, companyName FROM customer", "limit": 10, "offset": 0}}
            )
            content_texts = [item.text for item in result.content if hasattr(item, 'text')]
            print(json.dumps(content_texts, indent=2))

if __name__ == "__main__":
    asyncio.run(run_client())