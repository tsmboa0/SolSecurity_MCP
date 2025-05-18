from typing import List, Dict, Any
import httpx
import os
from contextlib import contextmanager

CONFIG = {
    "NATIVE_DUST_THRESHOLD": 0.00001,
    "TOKEN_DUST_THRESHOLD": 0.01,
    "MIN_TRANSACTION_HISTORY": 50
}

@contextmanager
def get_http_client():
    """Context manager for HTTP client with proper cleanup."""
    client = httpx.Client(
        timeout=httpx.Timeout(60.0, connect=30.0),
        verify=True
    )
    try:
        yield client
    finally:
        client.close()

def get_wallet_transactions(wallet_address: str, helius_api_key: str, limit: int) -> List[Dict[str, Any]]:
    """Fetch recent transactions for a given wallet address."""
    url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/transactions"
    
    params = {
        "api-key": helius_api_key,
        "limit": limit,
        "type": "TRANSFER",
    }
    
    with get_http_client() as client:
        response = client.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Helius error when fetching wallet transactions: {response.text}")
        
        transactions = response.json()
        print(f"Fetched {len(transactions)} transactions from Helius API.")
        if not isinstance(transactions, list):
            raise ValueError("Expected list of transactions from Helius API")
            
        transfers = []
        for tx in transactions:
            if not isinstance(tx, dict):
                continue
            
            # Native transfers  
            if len(tx.get("nativeTransfers", [])) > 0:
                for transfer in tx.get("nativeTransfers", []):
                    if not isinstance(transfer, dict):
                        continue
                    # Filetr transactions to get only those associated with the user's wallet    
                    if transfer["fromUserAccount"]==wallet_address or transfer["toUserAccount"] == wallet_address:
                        try:
                            transfers.append({
                                "from": transfer["fromUserAccount"],
                                "to": transfer["toUserAccount"],
                                "amount": float(transfer["amount"]) / 1_000_000_000,
                                "type": "native"
                            })
                        except (KeyError, ValueError, TypeError):
                            continue


            # Token transfers
            if len(tx.get("tokenTransfers", [])) > 0:
                for transfer in tx.get("tokenTransfers", []):
                    if not isinstance(transfer, dict):
                        continue
                    # Filetr transactions to get only those associated with the user's wallet    
                    if transfer["fromUserAccount"]==wallet_address or transfer["toUserAccount"] == wallet_address:   
                        try:
                            transfers.append({
                                "from": transfer["fromUserAccount"],
                                "to": transfer["toUserAccount"],
                                "amount": int(transfer["tokenAmount"]),
                                "type": "token"
                            })
                        except (KeyError, ValueError, TypeError):
                            continue
        return transfers

def extract_senders_and_recipients(transfers: List[Dict[str, Any]], wallet_address: str) -> Dict[str, int]:
    """
    Extract the senders and recipients from the transaction history.
    
    Args:
        transfers: List of transfer details
        wallet_address: The user's wallet address
        
    Returns:
        Dictionary containing the senders (along with the amount and type) and recipients
    """
    recipients = []
    senders_details = []
    # Count outgoing transfers (user sending to other addresses)
    for transfer in transfers:
        if transfer["from"] == wallet_address:
            recipient = transfer["to"]
            recipients.append(recipient)
        else:
            sender = transfer["from"]
            senders_details.append({
                "address": sender,
                "amount": transfer["amount"],
                "type": transfer["type"]
            })
    
    return {
        "senders": senders_details,
        "recipients": recipients
    }

def detect_poisoned_senders(senders, receivers):
    """
    Detect sender addresses mimicking receiver addresses.
    Focus on similarities in first or last 4 characters.
    Ignore exact full matches.
    """
    poisoned_senders = []
    mimicked_addresses = []

    for sender in senders:
        s_addr = sender["address"].lower()
        s_first4 = s_addr[:4]
        s_last4 = s_addr[-4:]

        for r_addr in receivers:
            if s_addr == r_addr.lower():
                # Exact match — likely legitimate
                continue

            r_first4 = r_addr[:4].lower()
            r_last4 = r_addr[-4:].lower()
            # If sender mimics beginning or end of receiver
            if s_first4 == r_first4 or s_last4 == r_last4:
                poisoned_senders.append(sender)
                mimicked_addresses.append(r_addr)

    return {
        "poisoned_senders": poisoned_senders,
        "mimicked_addresses": mimicked_addresses
    }

def detect_dust_senders(poisoned_senders):
    """
    Filter poisoned senders who sent amounts <= dust_threshold.
    """
    dust_senders = []

    for sender in poisoned_senders:
        if sender["type"] == "native" and sender["amount"] <= CONFIG["NATIVE_DUST_THRESHOLD"]:
            dust_senders.append(sender)
        elif sender["type"] == "token" and sender["amount"] <= CONFIG["TOKEN_DUST_THRESHOLD"]:
            dust_senders.append(sender)
        else:
            pass

    return dust_senders

def deduplicate_mimicked_addresses(addresses: list[str]) -> list[str]:
    seen = set()
    deduped = []
    for addr in addresses:
        if addr not in seen:
            seen.add(addr)
            deduped.append(addr)
    return deduped

def deduplicate_poisoned_senders(senders: list[dict]) -> list[dict]:
    seen = set()
    deduped = []
    for sender in senders:
        key = (sender["address"], sender["amount"], sender["type"])
        if key not in seen:
            seen.add(key)
            deduped.append(sender)
    return deduped





def check_wallet_poisoning(wallet_address: str, helius_api_key: str) -> Dict[str, Any]:
    """
    Check if a wallet has been targeted by address poisoning attacks.
    
    Args:
        wallet_address: The address of the wallet to check
        helius_api_key: The API key for the Helius API
        trusted_addresses: Optional list of trusted addresses to whitelist
        tx_limit: Maximum number of transactions to analyze (default: 20)
    
    Returns:
        A dictionary containing the results of the poisoning analysis
    """ 
    results = {
        "message": "",
        "total_transactions_analyzed": 0,
        "confirmed_poisoning_attempts": 0,
        "poisoned_addresses": [],
        "dusting_attempts": 0,
        "mimicked_addresses": []
    }
    try:    
        # Step 1: Get user transactions
        print("getting user transactions history")
        recent_transfers = get_wallet_transactions(wallet_address, helius_api_key, CONFIG["MIN_TRANSACTION_HISTORY"])
        if not recent_transfers:
            results["message"] = "No frequent transaction found to analyze"
            return results
        
        results["total_transactions_analyzed"]= len(recent_transfers)
        
        # Step 2 Extract all senders and recepients associated to the user's wallet
        print("Extracting all senders and recievers")
        extracted_addresses = extract_senders_and_recipients(recent_transfers, wallet_address)

        senders = extracted_addresses["senders"]
        recipients = extracted_addresses["recipients"]

        # Step 3 Analyse extracted senders and recievers for potential address poisoning attack
        print("Analyzing details for potential address poisoning attacks")
        poisoning_analysis_results = detect_poisoned_senders(senders, recipients)
        if not poisoning_analysis_results:
            results["message"] = f"Analyzed {len(recent_transfers)} recent transfers and no address poisoning threats found"
            return results
        
        poisoned_senders = poisoning_analysis_results["poisoned_senders"]
        mimicked_addresses = poisoning_analysis_results["mimicked_addresses"]
        
        
        results["poisoned_addresses"] = deduplicate_poisoned_senders(poisoned_senders)
        results["confirmed_poisoning_attempts"]=len(deduplicate_poisoned_senders(poisoned_senders))

        # Step 4 Ananlyze the suspected dusting addresses further for dusting attacks
        print("Analyzing suspected poisoned addresses for dusting attacks")
        dusting_analysis_results = detect_dust_senders(poisoned_senders)
        if not dusting_analysis_results:
            results["message"]= f"Found {len(poisoned_senders)} potential poisoning attempts but no dusting seen. Be very cautious"
            return results
        
        results["message"] = f"Found {len(deduplicate_poisoned_senders(poisoned_senders))} confirmed poisoning attacks and {len(dusting_analysis_results)} dusting attacks after analyzing {len(recent_transfers)} latest transactions"

        results["dusting_attempts"] = len(dusting_analysis_results)
        results["mimicked_addresses"] = deduplicate_mimicked_addresses(mimicked_addresses)
        
        return results
        
    except Exception as e:
        # Handle any errors gracefully
        return {
            "status": "error",
            "message": f"Error analyzing wallet: {str(e)}",
        }
