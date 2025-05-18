from server import mcp
from dotenv import load_dotenv
import os

from src.utils.poisoning_analyzer import check_wallet_poisoning
# Load environment variables from .env file
load_dotenv()

# Import the MCP tools
import src.mcp_tools.poisoning_tool
import src.mcp_tools.dusting_tool

# Entry point to run the server
if __name__ == "__main__":
    print("Starting SolSecurity MCP server...")   
    # Run the MCP server
    mcp.run(transport='stdio')
    