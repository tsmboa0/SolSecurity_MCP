import json
import time
import os
import httpx

FLIPSIDE_URL = "https://api.flipsidecrypto.com/api/v2/queries/9fe973d5-ea06-493a-b5a5-3b92f7880e7c/data/latest"

http_client = httpx.Client()


# Function to get recent transactions for a given wallet address
def get_wallet_transactions(wallet_address, helius_api_key, limit=20):
    """Fetch recent transactions for a given wallet address."""
    url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/transactions?api-key={helius_api_key}"
    
    params = {
        "limit": limit,  # Number of recent transactions to fetch
        "type": "TRANSFER",  # Focus on transfer transactions
    }
    
    response = http_client.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Helius error when fetching wallet transactions: {response.text}")
    
    transactions = response.json()
    return [tx["signature"] for tx in transactions]

# Function to get transfer details for a list of transaction IDs
def get_helius_transfers(tx_ids, helius_api_key):
    """Get transfer details for a list of transaction IDs."""
    url = f"https://api.helius.xyz/v0/transactions?api-key={helius_api_key}"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    
    response = http_client.post(url, headers=headers, json={"transactions": tx_ids})
    if response.status_code != 200:
        raise Exception(f"Helius error: {response.text}")
    
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

# Function to get known dusting wallets from Flipside Crypto
def get_duster_wallets():
    """Fetch known dusting wallets from Flipside Crypto."""
    response = http_client.get(FLIPSIDE_URL)
    if response.status_code != 200:
        raise Exception(f"Flipside error: {response.text}")
    
    return {row["DUSTER_WALLET"] for row in response.json()}

# Function to check if a wallet has received dust from known dusting addresses      
def check_wallet_dusting(wallet_address, helius_api_key, tx_limit=20):
    """Check if a wallet has received dust from known dusting addresses."""
    print(f"Analyzing wallet: {wallet_address}")
    print("Fetching recent transactions...")
    
    # Get recent transaction IDs for the wallet
    tx_ids = get_wallet_transactions(wallet_address, helius_api_key, limit=tx_limit)
    if not tx_ids:
        print("No recent transactions found for this wallet.")
        return {}
    
    print(f"Found {len(tx_ids)} recent transactions")
    
    # Get transfer details for these transactions
    print("Fetching transfer details...")
    transfers = get_helius_transfers(tx_ids, helius_api_key)
    
    # Get known dusting wallets
    print("Getting duster wallets from Flipside...")
    duster_wallets = get_duster_wallets()
    
    # Check for incoming transfers from dusting wallets
    print("\nAnalyzing transfers:")
    results = {}
    dusting_count = 0
    
    # Only consider transfers where our wallet is the recipient
    wallet_incoming_txs = {t["tx_id"] for t in transfers if t["to"].lower() == wallet_address.lower()}
    
    for tx_id in tx_ids:
        if tx_id not in wallet_incoming_txs:
            continue
            
        tx_senders = [t["from"] for t in transfers if t["tx_id"] == tx_id]
        is_dusting = any(sender in duster_wallets for sender in tx_senders)
        
        if is_dusting:
            dusting_count += 1
            
        results[tx_id] = {
            "is_dusting": is_dusting,
            "senders": tx_senders
        }
        print(f"  {tx_id[:12]}...{tx_id[-8:]}: {'🚨 DUSTING' if is_dusting else '✅ clean'}")
    
    print(f"\nSummary: Found {dusting_count} potential dusting transactions out of {len(wallet_incoming_txs)} incoming transfers")
    return results

