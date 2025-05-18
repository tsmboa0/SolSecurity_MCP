import os
import httpx
import time
from time import sleep
from dotenv import load_dotenv
from .constants import KNOWN_DUSTING_WALLETS, DUSTING_SQL
from flipside import Flipside
from typing import List

load_dotenv()

FLIPSIDE_API_KEY = os.getenv("FLIPSIDE_API_KEY")

# Configure client with timeouts
http_client = httpx.Client(
    timeout=httpx.Timeout(60.0, connect=30.0),
    verify=True
)


def get_duster_wallets() -> List[str]:
    """
    Returns a list of known dusting wallets by querying Flipside data.
    
    Returns:
        List[str]: List of wallet addresses identified as potential dusters
    """
    # Get API key from environment variable
    api_key = os.environ.get("FLIPSIDE_API_KEY")
    if not api_key:
        print("FLIPSIDE_API_KEY environment variable not set, proceeding with KNOWN_DUSTING_WALLETS")
        return KNOWN_DUSTING_WALLETS
    
    # Initialize Flipside client
    flipside = Flipside(api_key, "https://api-v2.flipsidecrypto.xyz")
    
    try:
        # Execute the query with proper error handling
        print("Submitting query to Flipside...")
        query_result_set = flipside.query(DUSTING_SQL)
        
        # Wait for query to complete with timeout
        timeout = 60  # seconds
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = flipside.get_query_status(query_result_set.query_id)
            if status.status == "FINISHED":
                break
            elif status.status in ["FAILED", "CANCELLED"]:
                raise Exception(f"Query failed with status: {status.status}")
            print(f"Query status: {status.status}. Waiting...")
            time.sleep(2)
        
        # Get results
        print("Query complete. Fetching results...")
        result = flipside.get_query_results(
            query_result_set.query_id,
            page_size=100,
            page_number=1
        )
        
        # Extract wallet addresses from results
        duster_wallets = []
        if result and hasattr(result, 'records') and result.records:
            for record in result.records:
                duster_wallets.append(record['DUSTER_WALLET'])
            print(f"Found {len(duster_wallets)} potential dusting wallets")
        else:
            print("No dusting wallets found in query results")
            
        return duster_wallets
        
    except Exception as e:
        print(f"Error querying Flipside API: {str(e)}")
        # Return a fallback list of known dusters if query fails
        return KNOWN_DUSTING_WALLETS
    

# Function to get recent transactions for a given wallet address
def get_wallet_transactions(wallet_address, helius_api_key=None, limit=10):
    """Fetch recent transactions for a given wallet address."""
    if helius_api_key is None:
        helius_api_key = os.getenv("HELIUS_API_KEY")
        if not helius_api_key:
            raise ValueError("HELIUS_API_KEY not found in environment variables")
            
    url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/transactions"
    
    params = {
        "api-key": helius_api_key,
        "limit": limit,  # Number of recent transactions to fetch
        "type": "TRANSFER",  # Focus on transfer transactions
    }
    
    response = http_client.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Helius error when fetching wallet transactions: {response.text}")
    
    transfers = []
    for tx in response.json():
        tx_id = tx.get("signature")
        for transfer in tx.get("nativeTransfers", []):
            transfers.append({
                "tx_id": tx_id,
                "from": transfer["fromUserAccount"],
                "to": transfer["toUserAccount"],
                "amount": transfer["amount"]
            })
    return transfers


# Function to check if a wallet has received dust from known dusting addresses      
def check_wallet_dusting(wallet_address, helius_api_key=None, tx_limit=10):
    """Check if a wallet has received dust from known dusting addresses."""
    print(f"Analyzing wallet: {wallet_address} for dusting...")
    print("Fetching recent transactions...")
    
    # Get recent transaction IDs for the wallet
    recent_transfers = get_wallet_transactions(wallet_address, helius_api_key, limit=tx_limit)
    if not recent_transfers:
        print("No recent transactions found for this wallet.")
        return {}
    
    print(f"Found {len(recent_transfers)} recent transactions")
    
    # Get known dusting wallets
    print("Getting duster wallets from Flipside...")
    duster_wallets = get_duster_wallets()
    
    # Check for incoming transfers from dusting wallets
    print("\nAnalyzing transfers:")
    results = {
        "dusting_count": 0,
        "dusting_transactions": []
    }
    dusting_count = 0
    
    # Only consider transfers where our wallet is the recipient
    wallet_incoming_txs = {t["tx_id"] for t in recent_transfers if t["to"].lower() == wallet_address.lower()}
    
    for transfer in recent_transfers:
        if transfer["tx_id"] not in wallet_incoming_txs:
            continue
            
        tx_senders = [t["from"] for t in recent_transfers if t["tx_id"] == transfer["tx_id"]]
        is_dusting = any(sender in duster_wallets for sender in tx_senders)
        
        if is_dusting:
            dusting_count += 1
            
        results[transfer["tx_id"]] = {
            "is_dusting": is_dusting,
            "senders": tx_senders
        }
        print(f"  {transfer['tx_id'][:12]}...{transfer['tx_id'][-8:]}: {'🚨 DUSTING' if is_dusting else '✅ clean'}")
    
    print(f"\nSummary: Found {dusting_count} potential dusting transactions out of {len(wallet_incoming_txs)} incoming transfers")
    return results

