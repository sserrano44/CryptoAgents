# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Running the System
```bash
# Primary interface - Interactive CLI with real-time monitoring
python cli/main.py analyze

# Alternative CLI invocation
python -m cli.main analyze

# Simple programmatic entry point
python main.py

# Standalone graph (avoids import conflicts)
python cryptoagents/crypto_trading_graph_standalone.py
```

### Testing & Validation
```bash
# Integration test suite - verifies all components work together
python test_integration.py

# Quick functionality test
python test_quick.py

# Test specific crypto analysis
python -c "from cryptoagents.config import validate_crypto_symbol; print(validate_crypto_symbol('BTC'))"
```

### Environment Setup
```bash
# Create conda environment (Python 3.13 required)
conda create -n cryptoagents python=3.13
conda activate cryptoagents

# Install dependencies
pip install -r requirements.txt

# Install CryptoAgents package in development mode (REQUIRED)
pip install -e .

# Configure API keys
cp .env.example .env
# Edit .env with OPENAI_API_KEY and COINMARKETCAP_API_KEY
```

### Environment Requirements
- **CRITICAL**: The CryptoAgents conda environment must be active when running Python
- **REQUIRED**: Package must be installed with `pip install -e .` for imports to work

## Memories

- When running python the environment CryptoAgents needs to be active
- supported_cryptos is set at CRYPTO_CONFIG

## Architecture Overview

### Multi-Agent Trading Desk Simulation
CryptoAgents implements a professional trading desk with a **5-phase workflow**:

1. **Crypto Analyst Team** (Parallel): Market, Social, News, Fundamentals analysts
2. **Research Team** (Debate): Bull vs Bear researchers + Research Manager
3. **Trading Team**: Trader converts research to execution plans
4. **Risk Management Team**: Aggressive, Conservative, Neutral risk analysts
5. **Portfolio Management**: Final decision by Portfolio Manager

### LangGraph Orchestration
- **State Management**: `CryptoTradingState` flows through all agents
- **Conditional Routing**: Dynamic agent selection based on user configuration
- **Stream Processing**: Real-time updates via `graph.stream()` for CLI monitoring
- **Signal Processing**: Trading signals interpreted via `process_signal()`

### Configuration System
**Central config**: `cryptoagents/config.py`
- **Supported Cryptos**: 20 major cryptocurrencies (BTC, ETH, BNB, XRP, ADA, SOL, etc.)
- **LLM Models**: `o4-mini` (deep thinking), `gpt-4o-mini` (quick thinking)
- **Risk Parameters**: 10% max position, 5% stop loss, 2.0x volatility multiplier
- **Debate Rounds**: Configurable depth (1-5 rounds) for research team

## Key Implementation Patterns

### Agent Selection & Initialization
```python
# User selects which analysts to include
analysts = ["market", "social", "news", "fundamentals"]
graph = TradingAgentsGraph(analysts, config=CRYPTO_CONFIG, debug=True)
```

### State Propagation
```python
# Initial state creation
initial_state = graph.propagator.create_initial_state("BTC", "2024-12-01")

# State flows through: analyst_reports � research_debate � trading_plan � risk_assessment � final_decision
```

### CLI Real-Time Monitoring
The CLI uses `rich.Live` with custom layouts to display:
- **Progress Table**: Agent status (pending/in_progress/completed)
- **Messages Panel**: Recent LLM calls and tool invocations  
- **Analysis Panel**: Current report sections as they complete
- **Statistics Footer**: Tool calls, LLM calls, generated reports count

### Data Sources Integration
- **CoinMarketCap API**: Primary crypto data source (`cryptoagents/dataflows/coinmarketcap_utils.py`)
- **Google News**: Crypto news aggregation
- **Reddit**: Social sentiment from crypto communities
- **Technical Indicators**: RSI, MACD, Bollinger Bands via `stockstats`

## File Structure Significance

### Core Components
- `cli/main.py`: Rich terminal interface with real-time agent monitoring
- `cryptoagents/graph/trading_graph.py`: LangGraph orchestration and agent routing
- `cryptoagents/config.py`: Centralized configuration for crypto trading parameters
- `cryptoagents/dataflows/interface.py`: Unified data interface for all crypto data sources

### Agent Implementations
- `cryptoagents/agents/crypto_analysts/`: Specialized crypto analysis agents
- `cryptoagents/agents/research/`: Bull/Bear researchers and Research Manager
- `cryptoagents/agents/risk/`: Risk management team with different risk appetites

### Critical Configuration
- **Analyst Selection**: Users choose which analysts to include in analysis
- **Research Depth**: 1-5 debate rounds between Bull/Bear researchers
- **LLM Models**: Separate models for quick vs deep thinking tasks
- **Risk Parameters**: Crypto-specific risk management settings

## Development Guidelines

### When Adding New Agents
1. Implement in appropriate subdirectory under `cryptoagents/agents/`
2. Follow the `create_*_analyst()` function pattern
3. Add to agent selection logic in CLI and graph configuration
4. Update state management in `trading_graph.py` if new state fields needed

### When Modifying Configuration
- Always update `cryptoagents/config.py` as the single source of truth
- Update `validate_crypto_symbol()` if adding new supported cryptocurrencies
- Consider impact on CLI validation in `cli/utils.py`

### When Adding Data Sources
- Implement new APIs in `cryptoagents/dataflows/`
- Add integration points to `interface.py`
- Consider rate limiting and caching for external APIs
- Update toolkit creation in `crypto_toolkit.py`

### Testing New Features
- Add integration tests to `test_integration.py`
- Ensure CLI workflow works end-to-end
- Test with multiple cryptocurrency symbols
- Verify all agent combinations work correctly

## Important Constraints

### API Requirements
- **OpenAI API Key**: Required for LLM agent operations
- **CoinMarketCap API Key**: Required for crypto data (10,000 credits/month on basic plan)

### Supported Cryptocurrencies
The system validates against a specific list in `config.py`. When users select unsupported symbols, validation prevents execution.

### LangGraph State Management
State flows unidirectionally through the trading desk phases. Agents cannot modify previous phase results, maintaining audit trail integrity.

### CLI User Experience
The CLI is designed as the primary interface. When modifying agent behavior, ensure progress updates are properly emitted for real-time monitoring.