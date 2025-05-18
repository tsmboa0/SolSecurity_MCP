from main import mcp
import os
from src.utils.dust_analyzer import check_wallet_dusting as analyze_dusting

HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

@mcp.tool(description="Check if a wallet has received dust from known dusting addresses.")
def check_wallet_dusting(wallet_address: str):
    """Check if a wallet has received dust from known dusting addresses.
    
    Args:
        wallet_address: The address of the wallet to check for dusting.

    Returns:
        A dictionary containing the results of the dusting check.
    """
    return analyze_dusting(wallet_address, HELIUS_API_KEY)
