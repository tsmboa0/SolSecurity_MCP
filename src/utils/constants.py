"""
Known top 20 dusting wallets from Flipside API
"""

KNOWN_DUSTING_WALLETS = [
    "FLiPGqowc82LLR173hKiFYBq2fCxLZEST5iHbHwj8xKb",
    "FLiPgGTXtBtEJoytikaywvWgbz5a56DdHKZU72HSYMFF",
    "6vMuna31vRDs9u9RAEF8UeCSs9CNu6j4LkXpe4Ko1gBQ",
    "5Hr7wZg7oBpVhH5nngRqzr5W7ZFUfCsfEhbziZJak7fr",
    "3U6GsNZM2uuUy4CHqizW3HC2zQZRkyQxiou8uX7PjMak",
    "2pHeSjQJtWSDnK8gw7anfLQnK1LqscnT1h2Zbtb66LYR",
    "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
    "6FwAyRbvKwY4uAzgeWaXUHEqfSDaFcdcZsbBh1TQtnuA",
    "ChGA1Wbh9WN8MDiQ4ggA5PzBspS2Z6QheyaxdVo3XdW6",
    "H5ft7mjHYafZJCP9UPRu7yP66enrL9t8Hc9ohwyoC9bL",
    "2Tq5W7ydAHFuHbSJ1KTcKAsRaHBAQzoCFiVuNwtagns2",
    "imgXJgVM2oFdVyLXuZSwdsPEB5e9PBZcst51tF3T7nR",
    "4p16wya1Vw2u9w22oah4yXQgySb6eWKRRLMsEXCreish",
    "2pde9wUAZVQRcXvt5uFfvc3kp2s2zHn43zF5SCMqPthh",
    "BZYLAhFCCLMAcy8GcJ3fuw3QzAyfenRZoKoA1i3fvx46",
    "6sum82jvwcYyz1XbEuTfs9UNjymE5rDAhuR9w1RfHeGP",
    "3sZA1qjF4GBr1XnvFTbU5HXkxpYKRdf1LRvmXqvyuZiK",
    "Fmy4EtM1F22g9WsCeE5UC3XmNArGwDmXCpPz6KnmSbbA",
    "Enc6rB84ZwGxZU8aqAF41dRJxg3yesiJgD7uJFVhMraM",
    "8BxX8691h5pffmdhfRTLaQeiHJkdgQiyKvNrrEdM8ri6",
    "2pde9wUAZVQRcXvt5uFfvc3kp2s2zHn43zF5SCMqPthh",
    "BZYLAhFCCLMAcy8GcJ3fuw3QzAyfenRZoKoA1i3fvx46",
    "6sum82jvwcYyz1XbEuTfs9UNjymE5rDAhuR9w1RfHeGP",
    "3sZA1qjF4GBr1XnvFTbU5HXkxpYKRdf1LRvmXqvyuZiK",
    "Fmy4EtM1F22g9WsCeE5UC3XmNArGwDmXCpPz6KnmSbbA",
]


"""
SQL Query to get all dusting wallets from fliside
"""
DUSTING_SQL = """
WITH dust_senders AS (
    SELECT 
        TX_FROM AS DUSTER_WALLET,
        COUNT(*) AS dust_count
    FROM solana.core.fact_transfers
    WHERE AMOUNT < 0.000001
    AND BLOCK_TIMESTAMP >= DATEADD('day', -7, CURRENT_TIMESTAMP())
    GROUP BY TX_FROM
    HAVING COUNT(*) > 100
)
SELECT DUSTER_WALLET
FROM dust_senders
ORDER BY dust_count DESC
LIMIT 20
"""