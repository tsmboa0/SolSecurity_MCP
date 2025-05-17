from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("mix_server")


# Entry point to run the server
if __name__ == "__main__":
    mcp.run()