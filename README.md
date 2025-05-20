# SolSecurity MCP: Advanced Solana Wallet Security Analysis

## 🚨 Why You Need This Tool Right Now

In the rapidly evolving world of Web3, security threats are becoming increasingly sophisticated. Recent statistics show that over $1.7 billion was lost to crypto scams in 2023 alone, with address poisoning and dusting attacks being among the most prevalent threats. These attacks are particularly dangerous because they're often invisible to the untrained eye and can lead to devastating financial losses.

### Real-World Impact: The $2.9 Million Address Poisoning Attack

In November 2023, a single user lost over $2.9 million in a sophisticated address poisoning attack. The attacker created an address that looked nearly identical to the user's frequently used address, and the user, thinking they were sending to a trusted address, transferred their funds to the attacker's wallet. This devastating loss could have been prevented with proper address verification and real-time security analysis.

### The Growing Threat

1. **Address Poisoning Attacks**: Attackers create addresses that look similar to your frequently used addresses, hoping you'll accidentally send funds to the wrong address. These attacks are becoming more sophisticated, with attackers using advanced techniques to make their addresses look legitimate.

2. **Dusting Attacks**: Attackers send tiny amounts of tokens to your wallet to track your transactions and potentially link your addresses to your identity. This can lead to targeted phishing attacks or more sophisticated scams.

### Why Traditional Security Measures Aren't Enough

- Most wallet interfaces only show basic transaction information
- Manual address verification is error-prone and time-consuming
- Existing security tools often lack real-time analysis capabilities
- Many users don't realize they've been targeted until it's too late

## 🛡️ What SolSecurity MCP Does

SolSecurity MCP is a powerful security analysis tool that provides real-time protection against these threats by:

1. **Advanced Address Poisoning Detection**
   - Analyzes transaction patterns
   - Identifies suspicious address similarities
   - Calculates risk scores based on multiple factors
   - Provides detailed analysis of potential threats

2. **Comprehensive Dusting Analysis**
   - Detects dust transactions from known malicious addresses
   - Analyzes transaction patterns for suspicious activity
   - Provides detailed reports on potential threats
   - Helps prevent identity linking attacks

3. **Real-time Risk Assessment**
   - Immediate analysis of wallet activity
   - Detailed risk scoring system
   - Clear threat categorization
   - Actionable security recommendations

## 🚀 Features

- **Real-time Analysis**: Get instant security insights for any Solana wallet
- **Comprehensive Reports**: Detailed analysis of transaction patterns and risks
- **Risk Scoring**: Clear categorization of threats (High, Medium, Low Risk)
- **User-friendly Interface**: Easy-to-understand results and recommendations
- **API Integration**: Seamless integration with existing security systems

## 🏗️ Architecture

SolSecurity MCP is built using a modular architecture that separates the data-fetching logic from the API interface. The core components include:

- **API Clients**: Specialized HTTP clients for Helius RPC and Flipside Analytics
- **MCP Tools**: Function-based tools that transform raw API responses into structured data
- **FastMCP Server**: A lightweight server that exposes the tools via HTTP
- **Error Handling**: Robust error management to ensure reliability

## 💻 Installation

### Prerequisites
- Python 3.11 or higher
- uv (Python package installer and environment manager)

### Option 1: Local Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/solsecurity_mcp.git
cd solsecurity_mcp
```

2. Create a virtual environment and install dependencies:
```bash
uv venv
uv pip install -e .
uv pip install flipside (do this extra step to avoid dependency issues)
```

3. Add these to your .env file:
```bash
HELIUS_API_KEY="your_helius_api_key"
FLIPSIDE_API_KEY="your_flipside_api_key" (optional)
```

4. Run the server:
```bash
uv run main.py
```

## 🔧 Usage

### For Individual Users

Simply provide your wallet address, and SolSecurity MCP will analyze your transactions for potential threats:

```python
from src.mcp_tools.poisoning_tool import check_wallet_poisoning
from src.mcp_tools.dusting_tool import check_wallet_dusting

# Check for poisoning attacks
poisoning_results = check_wallet_poisoning("your_wallet_address", "helius api key")

# Check for dusting attacks
dusting_results = check_wallet_dusting("your_wallet_address", "helius api key")
```

## Integrating with Claude for desktop

run this code in your terminal (if you use Visual studio code)

```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

Then modify the json file like this:

```json
{
    "mcpServers": {
        "solsecurity": {
            "command": "uv",
            "args": [
                "--directory",
                "/ABSOLUTE/PATH/TO/PARENT/FOLDER/solsecurity",
                "run",
                "main.py"
            ]
        }
    }
}
```

Voila! Your MCP server is up.

### For Service Providers

Integrate SolSecurity MCP into your applications to provide real-time security analysis:

```bash
curl -X POST http://localhost:8000/check_wallet_poisoning \
  -H "Content-Type: application/json" \
  -d '{"wallet_address": "your_wallet_address"}'
```

## 📊 Example Results for address poisoning

```json
{
  "message": "Analysis summary",
  "total_transactions_analyzed": 0,
  "confirmed_poisoning_attempts": 0,
  "poisoned_addresses": [],
  "dusting_attempts": 0,
  "mimicked_addresses": []
}
```

## 📊 Example Results for account dusting

```json
{
  "dusting_count": 0,
  "dusting_transactions": []
}
```

## 🔒 Security Best Practices

1. **Regular Checks**: Run security analysis regularly on your wallets
2. **Multiple Wallets**: Use different wallets for different purposes
3. **Transaction Verification**: Always double-check addresses before sending
4. **Stay Updated**: Keep the tool updated for the latest security features

## Funny Tips 😃: 

I didn't know my address was heavily targetted with dusting and poisoning attacks till i tested it with this tool 😅. I realized that I these bad guys sends an address similar to mine everytime I send tokens to someone. Yes, it's that bad!

Check out the full twitter post about what i found out using this tool. [x.com/tsmboa]

## 🤝 Contributing

We welcome contributions! Here's how you can help improve SolSecurity MCP:

1. **Fork the Repository**: Create your own fork of the project.
2. **Create a Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Commit Your Changes**: `git commit -m 'Add some amazing feature'`
4. **Push to the Branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**: Submit your changes for review.


## 📝 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

This tool is provided for security analysis purposes only. While it helps identify potential threats, it cannot guarantee complete protection against all types of attacks. Always follow security best practices and use multiple layers of security.

## 🔗 Links
- [Security Blog](https://tsmboa.substack.com/p/understanding-the-threats-account)

## 🤖 LangChain Integration

SolSecurity MCP can be easily integrated with LangChain to provide AI-powered security analysis. Here's how to use it:

```python
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.mcp_tools.poisoning_tool import check_wallet_poisoning
from src.mcp_tools.dusting_tool import check_wallet_dusting

# Create tools for the agent
tools = [
    Tool(
        name="check_wallet_poisoning",
        func=check_wallet_poisoning,
        description="Check if a wallet has been involved in any poisoning attacks. Input should be a Solana wallet address."
    ),
    Tool(
        name="check_wallet_dusting",
        func=check_wallet_dusting,
        description="Check if a wallet has received dust from known dusting addresses. Input should be a Solana wallet address."
    )
]

# Create the agent
llm = ChatOpenAI(temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that analyzes Solana wallet security. Use the tools provided to check for potential threats."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Example usage
result = agent_executor.invoke({
    "input": "Can you check if this wallet 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU has any security risks?"
})
```

This integration allows you to:
- Get natural language responses about wallet security
- Combine multiple security checks in a single query
- Get AI-powered explanations of security risks
- Automate security analysis workflows

## 🌟 Why Choose SolSecurity MCP?

- **Proactive Protection**: Don't wait for an attack to happen
- **Real-time Analysis**: Get instant security insights
- **Comprehensive Coverage**: Protection against multiple attack vectors
- **Easy Integration**: Works with your existing security setup
- **Active Development**: Regular updates and improvements

## 🎯 Target Users

- Individual crypto holders
- Crypto businesses
- Security researchers
- Wallet developers
- Exchange operators
- DeFi protocols

## 📈 Future Roadmap

- Integration with more blockchain networks
- Advanced machine learning for threat detection
- Real-time alert system
- API for automated security checks

## 🔧 Technology Stack

SolSecurity MCP leverages cutting-edge technologies to provide comprehensive security analysis:

- **Helius RPC**: For real-time transaction data and wallet analysis
- **Flipside Analytics**: For advanced blockchain data analysis and risk assessment
- **Python**: For robust and efficient processing
- **FastAPI**: For high-performance API endpoints