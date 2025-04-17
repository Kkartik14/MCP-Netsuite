from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv()

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = kwargs.get("api_key") or os.getenv("MCP_API_KEY", "default_key")
        if api_key != os.getenv("MCP_API_KEY", "default_key"):
            raise ValueError("Invalid API key")
        return f(*args, **kwargs)
    return decorated