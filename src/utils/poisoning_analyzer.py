from flipside import Flipside
import time
import os
import httpx

# Replace with your actual Flipside API key
FLIPSIDE_API_KEY = os.getenv("FLIPSIDE_API_KEY")
flipside = Flipside(FLIPSIDE_API_KEY, "https://api-v2.flipsidecrypto.xyz")

http_client = httpx.Client()

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

def check_tx_risks(tx_ids: list[str]):
    results = []

    for tx_id in tx_ids:
        sql = f"""
            WITH tab0 AS (
                SELECT 
                    block_timestamp AS block_timestamp1,
                    tx_id AS tx_id1,
                    tx_to AS tx_to1,
                    tx_from AS tx_from1,
                    amount AS amount1
                FROM solana.core.fact_transfers
                WHERE tx_id LIKE '{tx_id}' 
                    AND mint = 'So11111111111111111111111111111111111111111'
                HAVING amount < 5
                ),

                TAB1 AS (
                SELECT 
                    tx_id,
                    block_timestamp,
                    tx_from,
                    tx_to,
                    price * amount AS volume_usd
                FROM solana.core.fact_transfers t
                LEFT JOIN solana.price.ez_prices_hourly p
                    ON p.token_address = t.mint 
                    AND DATE_TRUNC('hour', t.block_timestamp) = p.hour
                WHERE t.block_timestamp > CURRENT_DATE - 1000
                    AND price * amount > 1000
                    AND tx_id NOT IN (
                    SELECT tx_id 
                    FROM solana.defi.ez_dex_swaps 
                    WHERE block_timestamp > CURRENT_DATE - 1
                    )
                    AND tx_from IN (
                    SELECT tx_to1 
                    FROM tab0
                    )
                ),

                tab2 AS (
                SELECT 
                    tx_to AS to1,
                    MIN(block_timestamp) AS first_fund
                FROM solana.core.fact_transfers
                WHERE tx_to IN (SELECT tx_from1 FROM tab0)
                GROUP BY 1
                ),

                tab3 AS (
                SELECT 
                    *,
                    CASE 
                    WHEN LEFT(tx_from, 6) = LEFT(tx_to1, 6) OR RIGHT(tx_from, 6) = RIGHT(tx_to1, 6) THEN 5
                    WHEN LEFT(tx_from, 5) = LEFT(tx_to1, 5) AND RIGHT(tx_from, 1) = RIGHT(tx_to1, 1) THEN 5
                    WHEN LEFT(tx_from, 4) = LEFT(tx_to1, 4) AND RIGHT(tx_from, 2) = RIGHT(tx_to1, 2) THEN 5
                    WHEN LEFT(tx_from, 3) = LEFT(tx_to1, 3) AND RIGHT(tx_from, 3) = RIGHT(tx_to1, 3) THEN 5
                    WHEN LEFT(tx_from, 2) = LEFT(tx_to1, 2) AND RIGHT(tx_from, 4) = RIGHT(tx_to1, 4) THEN 5
                    WHEN LEFT(tx_from, 1) = LEFT(tx_to1, 1) AND RIGHT(tx_from, 5) = RIGHT(tx_to1, 5) THEN 5
                    WHEN LEFT(tx_from, 4) = LEFT(tx_to1, 4) AND RIGHT(tx_from, 1) = RIGHT(tx_to1, 1) THEN 4
                    WHEN LEFT(tx_from, 3) = LEFT(tx_to1, 3) AND RIGHT(tx_from, 2) = RIGHT(tx_to1, 2) THEN 4
                    WHEN LEFT(tx_from, 2) = LEFT(tx_to1, 2) AND RIGHT(tx_from, 3) = RIGHT(tx_to1, 3) THEN 4
                    WHEN LEFT(tx_from, 1) = LEFT(tx_to1, 1) AND RIGHT(tx_from, 4) = RIGHT(tx_to1, 4) THEN 4
                    WHEN LEFT(tx_from, 2) = LEFT(tx_to1, 2) AND RIGHT(tx_from, 2) = RIGHT(tx_to1, 2) THEN 3
                    WHEN LEFT(tx_from, 3) = LEFT(tx_to1, 3) OR RIGHT(tx_from, 3) = RIGHT(tx_to1, 3) THEN 3
                    WHEN LEFT(tx_from, 2) = LEFT(tx_to1, 2) AND RIGHT(tx_from, 1) = RIGHT(tx_to1, 1) THEN 2
                    WHEN LEFT(tx_from, 1) = LEFT(tx_to1, 1) AND RIGHT(tx_from, 2) = RIGHT(tx_to1, 2) THEN 2
                    WHEN LEFT(tx_from, 2) = LEFT(tx_to1, 2) OR RIGHT(tx_from, 2) = RIGHT(tx_to1, 2) THEN 2
                    WHEN LEFT(tx_from, 1) = LEFT(tx_to1, 1) AND RIGHT(tx_from, 1) = RIGHT(tx_to1, 1) THEN 1
                    WHEN LEFT(tx_from, 1) = LEFT(tx_to1, 1) OR RIGHT(tx_from, 1) = RIGHT(tx_to1, 1) THEN 1
                    ELSE 0
                    END AS visual_risk_score,

                    visual_risk_score * 10000 AS visual_coincidence_odds,

                    CASE 
                    WHEN visual_risk_score = 5 THEN 26.25
                    WHEN visual_risk_score = 4 THEN 0.90
                    WHEN visual_risk_score = 3 THEN 0.02
                    WHEN visual_risk_score = 2 THEN 0.0003
                    WHEN visual_risk_score = 1 THEN 0.000004
                    ELSE 0
                    END AS vanity_copy_cost_usd,

                    ROUND(DATEDIFF(SECOND, block_timestamp, block_timestamp1) / 60.0, 2) AS minutes_diff,

                    CASE
                    WHEN visual_risk_score = 1 THEN 0.00001
                    WHEN visual_risk_score = 2 THEN 0.001
                    WHEN visual_risk_score = 3 THEN 0.01
                    WHEN visual_risk_score = 4 THEN 0.05
                    WHEN visual_risk_score = 5 THEN 0.5
                    ELSE 0
                    END AS amount_risk_score

                FROM tab1 
                LEFT JOIN tab0 
                    ON block_timestamp1 > block_timestamp 
                    AND block_timestamp1 < block_timestamp + INTERVAL '1 DAY' 
                    AND LEFT(tx_from, 1) = LEFT(tx_to1, 1) 
                    AND RIGHT(tx_from, 1) = RIGHT(tx_to1, 1)
                WHERE tx_id1 IS NOT NULL
                )

                SELECT 
                tx_id,
                tx_from,
                tx_to,
                block_timestamp,
                visual_risk_score,
                ROUND(
                    CASE
                        WHEN visual_risk_score > 2 THEN 100
                        ELSE
                        (LEAST(100, GREATEST(5, 100 * EXP(-0.2 * minutes_diff))) * 0.5 +
                        CASE WHEN amount1 >= amount_risk_score THEN 0
                            ELSE (1 - (amount1 / amount_risk_score)) * 100 END * 0.3 +
                        CASE WHEN DATEDIFF('minute', first_fund, block_timestamp1) < 1440 THEN 20
                            ELSE 0 END * 0.2)
                    END,
                    2) AS final_risk_score,
                    CASE 
                WHEN final_risk_score >= 80 THEN 'High Risk'
                WHEN final_risk_score >= 50 THEN 'Medium Risk'
                WHEN final_risk_score >= 20 THEN 'Medium-Low Risk'
                ELSE 'Low Risk'  END AS risk_label

                FROM tab3
                LEFT JOIN tab2 ON to1 = tx_from1
            """

        try:
            query_result = flipside.query(sql)
            if query_result and query_result.records:
                query_result.records[0]["tx_id"] = tx_id
                results.append(query_result.records[0])
            else:
                results.append({
                    "tx_id": tx_id,
                    "visual_risk_score": 0,
                    "final_risk_score": 0,
                    "risk_label": "Clean"
                })
        except Exception as e:
            print(f"Query failed for tx {tx_id}: {e}")
            results.append({
                "tx_id": tx_id,
                "visual_risk_score": 0,
                "final_risk_score": 0,
                "risk_label": "Clean"
            })

    return results

def check_wallet_poisoning(wallet_address: str, helius_api_key: str, tx_limit: int = 20):
    """Check if a wallet has been involved in any poisoning attacks.
    
    Args:
        wallet_address: The address of the wallet to check
        helius_api_key: The API key for the Helius API
        tx_limit: Number of recent transactions to analyze (default: 20)
    
    Returns:
        A dictionary containing the results of the poisoning analysis
    """
    print(f"Analyzing wallet: {wallet_address}")
    print("Fetching recent transactions...")
    
    # Get recent transaction IDs for the wallet
    tx_ids = get_wallet_transactions(wallet_address, helius_api_key, limit=tx_limit)
    if not tx_ids:
        print("No recent transactions found for this wallet.")
        return {}
    
    print(f"Found {len(tx_ids)} recent transactions")
    
    # Analyze the transactions for poisoning risks
    print("Analyzing transactions for poisoning risks...")
    results = check_tx_risks(tx_ids)
    
    # Count risky transactions
    high_risk = sum(1 for r in results if r["risk_label"] == "High Risk")
    medium_risk = sum(1 for r in results if r["risk_label"] == "Medium Risk")
    medium_low_risk = sum(1 for r in results if r["risk_label"] == "Medium-Low Risk")
    
    print(f"\nSummary:")
    print(f"High Risk Transactions: {high_risk}")
    print(f"Medium Risk Transactions: {medium_risk}")
    print(f"Medium-Low Risk Transactions: {medium_low_risk}")
    print(f"Clean Transactions: {len(results) - (high_risk + medium_risk + medium_low_risk)}")
    
    return {
        "wallet_address": wallet_address,
        "total_transactions": len(results),
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "medium_low_risk_count": medium_low_risk,
        "clean_count": len(results) - (high_risk + medium_risk + medium_low_risk),
        "transaction_details": results
    }