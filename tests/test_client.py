import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_client():
    server_params = StdioServerParameters(
        command="python",
        args=["src/server.py"],
        env={"MCP_API_KEY": "default_key"}
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # List tools
            tools_result = await session.list_tools()
            tools = tools_result.tools
            tool_names = [tool.name for tool in tools]
            print("Available tools:", tool_names)
            # Call a tool
            result = await session.call_tool(
                "create_salesorder",
                {"customer_id": "123456", "item_id": "789", "quantity": 2}
            )
            content_texts = [item.text for item in result.content if hasattr(item, 'text')]
            print("Create sales order result:", content_texts[0] if content_texts else "No content")
            # Read resources
            _, resource_data = await session.read_resource("netsuite://customer/123456")
            # Extract text from the nested TextResourceContents object
            resource_text = resource_data[1][0].text if resource_data[1] else "No content"
            print("Customer resource:", resource_text)
            _, resource_data = await session.read_resource("netsuite://customers/search/acme")
            resource_text = resource_data[1][0].text if resource_data[1] else "No content"
            print("Search customers (acme):", resource_text)
            _, resource_data = await session.read_resource("netsuite://metadata/records")
            resource_text = resource_data[1][0].text if resource_data[1] else "No content"
            print("Metadata resource:", resource_text)

if __name__ == "__main__":
    asyncio.run(run_client())