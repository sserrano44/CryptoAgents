"""
Cryptocurrency Trading Toolkit
Provides all crypto-specific tools for the trading agents
"""
from typing import Dict, Any
from langchain_core.tools import Tool
from . import interface as crypto_interface
from ..config import get_crypto_config


class CryptoToolkit:
    """
    Toolkit providing cryptocurrency-specific tools for trading agents
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the crypto toolkit
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or get_crypto_config()
        self._create_tools()
    
    def _create_tools(self):
        """Create tool instances for all crypto functions"""
        
        # Price and market data tools
        self.get_crypto_price_data_window = Tool(
            name="get_crypto_price_data_window",
            description="Get cryptocurrency price data for a specified time window",
            func=crypto_interface.get_crypto_price_data_window
        )
        
        self.get_crypto_technical_indicators = Tool(
            name="get_crypto_technical_indicators",
            description="Calculate technical indicators for cryptocurrency",
            func=crypto_interface.get_crypto_technical_indicators
        )
        
        self.get_crypto_correlation_analysis = Tool(
            name="get_crypto_correlation_analysis",
            description="Analyze correlations between multiple cryptocurrencies",
            func=crypto_interface.get_crypto_correlation_analysis
        )
        
        # Fundamental analysis tools
        self.get_crypto_fundamentals_report = Tool(
            name="get_crypto_fundamentals_report",
            description="Get comprehensive cryptocurrency fundamentals report",
            func=crypto_interface.get_crypto_fundamentals_report
        )
        
        self.get_crypto_market_sentiment = Tool(
            name="get_crypto_market_sentiment",
            description="Get cryptocurrency market sentiment and metrics",
            func=crypto_interface.get_crypto_market_sentiment
        )
        
        self.get_crypto_market_overview = Tool(
            name="get_crypto_market_overview",
            description="Get overall cryptocurrency market overview",
            func=crypto_interface.get_crypto_market_overview
        )
        
        # News and social tools
        self.get_crypto_news = Tool(
            name="get_crypto_news",
            description="Retrieve news about a cryptocurrency",
            func=crypto_interface.get_crypto_news
        )
        
        self.get_reddit_crypto_sentiment = Tool(
            name="get_reddit_crypto_sentiment",
            description="Get cryptocurrency sentiment from Reddit",
            func=crypto_interface.get_reddit_crypto_sentiment
        )
        
        # Online tools (when enabled)
        if self.config.get("online_tools", False):
            self.get_crypto_news_openai = Tool(
                name="get_crypto_news_openai",
                description="Get cryptocurrency news using OpenAI's web search",
                func=crypto_interface.get_crypto_news_openai
            )
            
            self.get_crypto_social_sentiment_openai = Tool(
                name="get_crypto_social_sentiment_openai",
                description="Get cryptocurrency social media sentiment using OpenAI",
                func=crypto_interface.get_crypto_social_sentiment_openai
            )
        
        # Legacy tools for compatibility (using Google News)
        self.get_google_news = Tool(
            name="get_google_news",
            description="Get news from Google News",
            func=crypto_interface.get_google_news
        )
    
    def get_all_tools(self) -> list:
        """
        Get all available tools
        
        Returns:
            List of all tool instances
        """
        tools = [
            self.get_crypto_price_data_window,
            self.get_crypto_technical_indicators,
            self.get_crypto_correlation_analysis,
            self.get_crypto_fundamentals_report,
            self.get_crypto_market_sentiment,
            self.get_crypto_market_overview,
            self.get_crypto_news,
            self.get_reddit_crypto_sentiment,
            self.get_google_news,
        ]
        
        # Add online tools if enabled
        if self.config.get("online_tools", False):
            tools.extend([
                self.get_crypto_news_openai,
                self.get_crypto_social_sentiment_openai,
            ])
        
        return tools
    
    def get_market_analysis_tools(self) -> list:
        """Get tools for market analysis"""
        tools = [
            self.get_crypto_price_data_window,
            self.get_crypto_technical_indicators,
        ]
        
        if self.config.get("online_tools", False):
            tools.append(self.get_crypto_correlation_analysis)
        
        return tools
    
    def get_fundamental_analysis_tools(self) -> list:
        """Get tools for fundamental analysis"""
        return [
            self.get_crypto_fundamentals_report,
            self.get_crypto_market_sentiment,
            self.get_crypto_market_overview,
        ]
    
    def get_news_analysis_tools(self) -> list:
        """Get tools for news analysis"""
        tools = [
            self.get_crypto_news,
            self.get_google_news,
            self.get_crypto_market_overview,
        ]
        
        if self.config.get("online_tools", False):
            tools.insert(0, self.get_crypto_news_openai)
        
        return tools
    
    def get_social_analysis_tools(self) -> list:
        """Get tools for social media analysis"""
        tools = [
            self.get_reddit_crypto_sentiment,
            self.get_google_news,  # Fallback for social signals
        ]
        
        if self.config.get("online_tools", False):
            tools.insert(0, self.get_crypto_social_sentiment_openai)
        
        return tools


def create_crypto_toolkit(config: Dict[str, Any] = None) -> CryptoToolkit:
    """
    Factory function to create a crypto toolkit
    
    Args:
        config: Configuration dictionary
    
    Returns:
        CryptoToolkit instance
    """
    return CryptoToolkit(config)
