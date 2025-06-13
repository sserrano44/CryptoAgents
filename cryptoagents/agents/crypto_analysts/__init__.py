"""
Cryptocurrency-specific analyst agents
"""
# Import only what we need to avoid parent module imports
from .crypto_market_analyst import create_crypto_market_analyst
from .crypto_fundamentals_analyst import create_crypto_fundamentals_analyst
from .crypto_news_analyst import create_crypto_news_analyst
from .crypto_social_analyst import create_crypto_social_analyst

__all__ = [
    'create_crypto_market_analyst',
    'create_crypto_fundamentals_analyst', 
    'create_crypto_news_analyst',
    'create_crypto_social_analyst'
]
