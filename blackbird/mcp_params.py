import os
from dotenv import load_dotenv

load_dotenv(override=True)

tavily_api_key = os.getenv("TAVILY_API_KEY")
polygon_api_key = os.getenv("POLYGON_API_KEY")

if not tavily_api_key:
    raise ValueError("TAVILY_API_KEY is required. Set it in .env")
if not polygon_api_key:
    raise ValueError("POLYGON_API_KEY is required. Set it in .env")

market_mcp = {
    "command": "uv",
    "args": ["run", "market_server.py"]
}

trader_mcp_server_params = [
    {"command": "uv", "args": ["run", "accounts_server.py"]},
    {"command": "uv", "args": ["run", "push_server.py"]},
    market_mcp,
]

def researcher_mcp_server_params(name: str):
    os.makedirs("./memory", exist_ok=True)
    
    return [
        {"command": "uvx", "args": ["mcp-server-fetch"]},
        {
            "command": "npx",
            "args": ["-y", "tavily-mcp"],
            "env": {"TAVILY_API_KEY": tavily_api_key},
        },
        {
            "command": "npx",
            "args": ["-y", "mcp-memory-libsql"],
            "env": {"LIBSQL_URL": f"file:./memory/{name}.db"},
        },
    ]