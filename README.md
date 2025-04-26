[![MseeP Badge](https://mseep.net/pr/kkartik14-mcp-netsuite-badge.jpg)](https://mseep.ai/app/kkartik14-mcp-netsuite)

# MCP-Netsuite
This is an mock MCP server for Oracle Netsuite

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Kkartik14/MCP-Netsuite
   cd MCP-Netsuite
   ```
2. Create a virtual environment with uv
   ```bash
   uv venv
   source .venv/bin/activate
   ```
3. Install Dependencies
    ```bash
    uv sync
    ```
4. Testing the Server
    ```bash
    uv run python tests/test_client.py
    ```