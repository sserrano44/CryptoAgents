"""
Default configuration for CryptoAgents - Cryptocurrency Trading Framework
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

CRYPTO_CONFIG = {
    # Project directories
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "data_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "crypto_data"
    ),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/crypto_cache",
    ),
    
    # API Configuration
    "coinmarketcap_api_key": os.environ.get("COINMARKETCAP_API_KEY"),
    "use_sandbox": False,  # Set to True for testing with CoinMarketCap sandbox
    
    # LLM settings
    "deep_think_llm": "o4-mini",
    "quick_think_llm": "gpt-4o-mini",
    
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    
    # Tool settings
    "online_tools": True,
    
    # Cryptocurrency-specific settings
    "supported_cryptos": [
        "BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOGE", "DOT", "MATIC", "AVAX",
        "LINK", "UNI", "ATOM", "LTC", "ETC", "XLM", "ALGO", "VET", "FIL", "AAVE"
    ],
    
    # Trading parameters
    "max_position_size_pct": 10.0,  # Maximum position size as % of portfolio
    "stop_loss_pct": 5.0,  # Default stop loss percentage
    "take_profit_pct": 10.0,  # Default take profit percentage
    
    # Risk management for crypto
    "volatility_multiplier": 2.0,  # Crypto is more volatile than stocks
    "max_daily_trades": 5,  # Limit daily trades
    "min_market_cap": 1000000,  # Minimum market cap in USD
    
    # Data fetching parameters
    "default_lookback_days": 30,  # Default historical data period
    "technical_indicators": [
        "rsi", "macd", "boll", "atr", "close_50_sma", "close_200_sma", "mfi"
    ],
    
    # Market hours (crypto trades 24/7)
    "market_hours": "24/7",
    "timezone": "UTC",
}

# Crypto-specific prompts and instructions
CRYPTO_PROMPTS = {
    "market_context": """
    Remember that cryptocurrency markets operate 24/7, unlike traditional stock markets.
    Consider the following crypto-specific factors:
    - Higher volatility compared to traditional assets
    - Influence of Bitcoin and Ethereum on altcoin movements
    - Impact of DeFi metrics and on-chain data
    - Regulatory news and developments
    - Exchange-specific risks and liquidity
    - Smart contract risks for DeFi tokens
    """,
    
    "risk_warning": """
    Cryptocurrency trading involves substantial risk. Prices can be extremely volatile,
    and investors may lose their entire investment. This system is for research and
    educational purposes only and should not be considered financial advice.
    """,
    
    "fundamental_analysis": """
    For cryptocurrency fundamental analysis, consider:
    - Tokenomics (supply mechanics, inflation/deflation)
    - Project development activity and GitHub commits
    - Community size and engagement
    - Real-world adoption and partnerships
    - Competitive landscape within the crypto sector
    - Technical innovation and unique value proposition
    """
}

def get_crypto_config():
    """Get the cryptocurrency configuration"""
    config = CRYPTO_CONFIG.copy()
    
    # Validate required API keys
    if not config.get("coinmarketcap_api_key"):
        print("Warning: COINMARKETCAP_API_KEY not set in environment variables")
    
    return config

def validate_crypto_symbol(symbol: str) -> bool:
    """
    Validate if a cryptocurrency symbol is supported
    
    Args:
        symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
    
    Returns:
        bool: True if supported, False otherwise
    """
    return symbol.upper() in CRYPTO_CONFIG["supported_cryptos"]

def get_crypto_trading_params(symbol: str) -> dict:
    """
    Get trading parameters for a specific cryptocurrency
    
    Args:
        symbol: Cryptocurrency symbol
    
    Returns:
        dict: Trading parameters
    """
    # Base parameters
    params = {
        "symbol": symbol.upper(),
        "max_position_size_pct": CRYPTO_CONFIG["max_position_size_pct"],
        "stop_loss_pct": CRYPTO_CONFIG["stop_loss_pct"],
        "take_profit_pct": CRYPTO_CONFIG["take_profit_pct"],
    }
    
    # Adjust parameters based on crypto type
    if symbol.upper() in ["BTC", "ETH"]:
        # Major cryptos - can use larger position sizes
        params["max_position_size_pct"] = 15.0
        params["stop_loss_pct"] = 3.0
    elif symbol.upper() in ["DOGE", "SHIB"]:
        # Meme coins - higher risk, smaller positions
        params["max_position_size_pct"] = 5.0
        params["stop_loss_pct"] = 10.0
        params["take_profit_pct"] = 20.0
    
    return params
