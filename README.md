# CryptoAgents: Multi-Agent LLM Cryptocurrency Trading Framework

## Overview

CryptoAgents is a sophisticated multi-agent LLM framework specifically designed for cryptocurrency trading. It leverages specialized AI agents working as a coordinated trading desk to analyze crypto markets, conduct research debates, execute trades, and manage risk in the 24/7 cryptocurrency ecosystem.

## Key Features

- **Trading Desk Simulation**: Multi-agent system mimicking a professional trading desk with specialized roles
- **Crypto Analyst Team**: Market, Social, News, and Fundamentals analysts working in parallel
- **Research Team Debates**: Bull vs Bear researchers with Research Manager coordination
- **Risk Management Team**: Aggressive, Conservative, and Neutral risk analysts
- **Portfolio Management**: Final decision-making with Portfolio Manager oversight
- **CoinMarketCap Integration**: Real-time cryptocurrency data and market metrics
- **24/7 Market Analysis**: Designed for continuous crypto market operations
- **Interactive CLI**: Rich terminal interface for real-time analysis monitoring
- **Configurable Depth**: Adjustable research and debate rounds (Shallow/Medium/Deep)

## Trading Desk Architecture

CryptoAgents simulates a professional trading desk with specialized teams:

```
┌─────────────────────────────────────────────────────────────────┐
│                      CryptoAgents Trading Desk                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ I. CRYPTO ANALYST TEAM (Parallel Analysis)                     │
│  ┌───────────────┐ ┌─────────────────┐ ┌─────────────┐        │
│  │ Crypto Market │ │ Crypto Social   │ │ Crypto News │        │
│  │   Analyst     │ │   Analyst       │ │  Analyst    │        │
│  └───────┬───────┘ └─────────┬───────┘ └──────┬──────┘        │
│          │                   │                 │                │
│  ┌───────▼─────────────────────▼─────────────────▼──────┐      │
│  │              Crypto Fundamentals Analyst             │      │
│  └───────────────────────┬───────────────────────────────┘      │
│                          │                                      │
│ II. RESEARCH TEAM (Debate & Strategy)                          │
│  ┌─────────────┐        │        ┌─────────────┐              │
│  │    Bull     │◄───────┴────────►│    Bear     │              │
│  │ Researcher  │                  │ Researcher  │              │
│  └──────┬──────┘                  └──────┬──────┘              │
│         │                                 │                    │
│  ┌──────▼─────────────────────────────────▼──────┐            │
│  │              Research Manager                  │            │
│  └──────────────────────┬─────────────────────────┘            │
│                         │                                      │
│ III. TRADING TEAM                                              │
│  ┌──────────────────────▼─────────────────────────┐            │
│  │                    Trader                      │            │
│  └──────────────────────┬─────────────────────────┘            │
│                         │                                      │
│ IV. RISK MANAGEMENT TEAM (Multi-Perspective)                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ Aggressive  │ │   Neutral   │ │Conservative │              │
│  │  Analyst    │ │  Analyst    │ │  Analyst    │              │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘              │
│         │               │               │                      │
│ V. PORTFOLIO MANAGEMENT                                        │
│  ┌──────▼───────────────▼───────────────▼──────┐              │
│  │              Portfolio Manager               │              │
│  └─────────────────────────────────────────────┘              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sserrano44/CryptoAgents.git
cd CryptoAgents
```

2. Create a virtual environment:
```bash
conda create -n cryptoagents python=3.13
conda activate cryptoagents
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up API keys:

Option 1: Using environment variables
```bash
export OPENAI_API_KEY=your_openai_api_key
export COINMARKETCAP_API_KEY=your_coinmarketcap_api_key
```

Option 2: Using .env file (recommended)
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=your_openai_api_key
# COINMARKETCAP_API_KEY=your_coinmarketcap_api_key
```

## Usage

### Interactive CLI (Recommended)

The easiest way to use CryptoAgents is through the interactive CLI:

```bash
# Run the interactive CLI
python cli/main.py analyze

# Or simply
python -m cli.main analyze
```

The CLI provides:
- **Step-by-step configuration**: Symbol selection, analysis date, team selection
- **Real-time monitoring**: Live progress tracking of all agents
- **Rich terminal interface**: Beautiful formatted reports and status updates
- **Configurable analysis depth**: Choose from Shallow/Medium/Deep research levels
- **Model selection**: Pick different LLM engines for quick vs deep thinking

### Programmatic Usage

```python
from cryptoagents.graph.trading_graph import TradingAgentsGraph
from cryptoagents.config import CRYPTO_CONFIG

# Initialize the trading graph with selected analysts
analysts = ["market", "social", "news", "fundamentals"]
graph = TradingAgentsGraph(analysts, config=CRYPTO_CONFIG, debug=True)

# Create initial state
initial_state = graph.propagator.create_initial_state("BTC", "2024-12-01")

# Run analysis
final_state = graph.graph.invoke(initial_state)
print(f"Final Decision: {final_state['final_trade_decision']}")
```

### Custom Configuration

```python
# Create custom configuration
config = CRYPTO_CONFIG.copy()
config["deep_think_llm"] = "gpt-4o"  # Use more powerful model
config["quick_think_llm"] = "gpt-4o-mini"  # Fast model for quick tasks
config["max_debate_rounds"] = 5  # Deeper research debates
config["max_position_size_pct"] = 10.0  # Adjust position sizing

# Initialize with custom config
graph = TradingAgentsGraph(analysts, config=config, debug=True)
```

### Testing and Validation

```bash
# Run integration tests
python test_integration.py

# Run a quick test analysis
python test_quick.py
```

## Configuration

Key configuration options in `cryptoagents/config.py`:

### Trading Parameters
- `supported_cryptos`: List of supported cryptocurrency symbols (BTC, ETH, ADA, DOT, LINK, UNI, AAVE, MATIC, SOL, AVAX)
- `max_position_size_pct`: Maximum position size as % of portfolio (15.0%)
- `stop_loss_pct`: Default stop loss percentage (3.0%)
- `volatility_multiplier`: Adjustment for crypto volatility (1.5)

### Agent Configuration
- `quick_think_llm`: Fast model for initial analysis ("gpt-4o-mini")
- `deep_think_llm`: Powerful model for complex reasoning ("gpt-4o")
- `max_debate_rounds`: Research team debate rounds (3)
- `max_risk_discuss_rounds`: Risk management discussion rounds (3)

### Data Sources
- `coinmarketcap_api_key`: CoinMarketCap API key
- `online_tools`: Enable real-time data fetching (True/False)

## API Requirements

### CoinMarketCap API
- Sign up at https://coinmarketcap.com/api/
- Basic plan provides 10,000 credits/month
- Supports up to 333 calls/day

### OpenAI API
- Sign up at https://platform.openai.com/
- Requires API credits for LLM calls

## Cryptocurrency-Specific Features

### 1. Market Analysis
- 24/7 price tracking
- Volatility-adjusted technical indicators
- Cross-exchange price comparison
- Bitcoin/Ethereum correlation analysis

### 2. Fundamental Analysis
- Tokenomics evaluation
- Supply metrics (circulating, total, max)
- Market cap and dominance
- Project metadata and descriptions

### 3. News & Social Sentiment
- Crypto-specific news sources
- Reddit sentiment analysis
- Social media monitoring
- FUD/FOMO detection

### 4. Risk Management
- Higher volatility thresholds
- Position sizing for crypto assets
- Exchange risk considerations
- Liquidity analysis

## Supported Cryptocurrencies

**Default supported cryptocurrencies:**
- **BTC** (Bitcoin), **ETH** (Ethereum), **ADA** (Cardano)
- **DOT** (Polkadot), **LINK** (Chainlink), **UNI** (Uniswap)
- **AAVE** (Aave), **MATIC** (Polygon), **SOL** (Solana), **AVAX** (Avalanche)

**Note**: While the system is configured for these 10 cryptocurrencies by default, you can analyze any cryptocurrency available on CoinMarketCap by modifying the `supported_cryptos` list in the configuration.

## Trading Desk Workflow

The CryptoAgents system follows a structured workflow mimicking a professional trading desk:

### Phase I: Crypto Analyst Team
- **Parallel Analysis**: Market, Social, News, and Fundamentals analysts work simultaneously
- **Comprehensive Data Gathering**: Each analyst focuses on their specialty area
- **Independent Reports**: Each analyst produces detailed analysis reports

### Phase II: Research Team
- **Bull vs Bear Debate**: Two researchers argue opposing viewpoints
- **Research Manager**: Synthesizes debates and makes initial investment recommendation
- **Configurable Depth**: 1-5 rounds of debate based on selected analysis depth

### Phase III: Trading Team
- **Trader Execution**: Converts research recommendations into specific trading plans
- **Risk Assessment**: Initial risk evaluation and position sizing

### Phase IV: Risk Management Team
- **Multi-Perspective Analysis**: Aggressive, Neutral, and Conservative risk analysts
- **Risk Debate**: Discussion of risk factors and mitigation strategies
- **Risk-Adjusted Recommendations**: Balanced risk assessment

### Phase V: Portfolio Management
- **Final Decision**: Portfolio Manager makes final trading decision
- **Comprehensive Review**: Considers all previous analysis and risk assessments
- **Execution Plan**: Final buy/sell/hold decision with specific parameters

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure environment variables are set
   - Check API key validity
   - Verify API limits haven't been exceeded

2. **Symbol Not Found**
   - Use supported crypto symbols: BTC, ETH, ADA, DOT, LINK, UNI, AAVE, MATIC, SOL, AVAX
   - Check `cryptoagents/config.py` for the complete list of supported symbols

3. **Rate Limiting**
   - Reduce batch size
   - Add delays between requests
   - Use caching for repeated queries

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Disclaimer

**IMPORTANT**: Cryptocurrency trading involves substantial risk. Prices can be extremely volatile, and investors may lose their entire investment. This system is for research and educational purposes only and should not be considered financial advice.

## License

This project is licensed under the same terms as the original TradingAgents framework.

## Project Structure

```
CryptoAgents/
├── cryptoagents/
│   ├── agents/                     # Agent implementations
│   │   ├── crypto_analysts/        # Crypto analyst agents
│   │   ├── research/              # Research team agents  
│   │   ├── risk/                  # Risk management agents
│   │   └── utils/                 # Agent utilities
│   ├── dataflows/                 # Data interfaces
│   │   ├── interface.py           # Main crypto data interface
│   │   ├── crypto_toolkit.py      # Crypto analysis tools
│   │   └── coinmarketcap_utils.py # CoinMarketCap API
│   ├── graph/                     # LangGraph orchestration
│   │   └── trading_graph.py       # Main trading graph
│   └── config.py                  # Crypto configuration
├── cli/                           # Interactive CLI
│   ├── main.py                    # CLI entry point
│   ├── utils.py                   # CLI utilities
│   └── models.py                  # CLI data models
├── test_integration.py            # Integration tests
└── README.md                      # This file
```

## Acknowledgments

- Inspired by professional trading desk operations
- CoinMarketCap for comprehensive cryptocurrency data
- OpenAI for advanced LLM capabilities
- LangGraph for multi-agent orchestration

## Future Enhancements

- [ ] On-chain data integration (blockchain metrics)
- [ ] DeFi protocol analysis capabilities  
- [ ] Exchange API integration for real trading
- [ ] Advanced backtesting framework
- [ ] Portfolio optimization algorithms
- [ ] Real-time alerts and notifications
- [ ] Web dashboard interface
- [ ] Advanced risk metrics and VaR calculations
