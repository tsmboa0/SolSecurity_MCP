from typing import Any
from main import mcp
import os
from src.utils.poisoning_analyzer import check_wallet_poisoning

HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

@mcp.tool(description="Check if a wallet has been involved in any poisoning attacks.")
def analyze_wallet_poisoning(wallet_address: str):
    """Check if a wallet has been involved in any poisoning attacks.
    
    Args:
        wallet_address: The address of the wallet to check for poisoning attacks.

    Returns:
        A dictionary containing the results of the poisoning analysis, including:
        - total_transactions: Total number of transactions analyzed
        - high_risk_count: Number of high-risk transactions
        - medium_risk_count: Number of medium-risk transactions
        - medium_low_risk_count: Number of medium-low risk transactions
        - clean_count: Number of clean transactions
        - transaction_details: Detailed results for each transaction
    """
    return check_wallet_poisoning(wallet_address, HELIUS_API_KEY)
