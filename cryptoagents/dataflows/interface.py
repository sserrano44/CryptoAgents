from typing import Annotated, Dict, List, Optional
from .reddit_utils import fetch_top_from_category
from .googlenews_utils import getNewsData
from .coinmarketcap_utils import (
    CoinMarketCapAPI,
    get_crypto_price_data,
    get_crypto_fundamentals,
    get_market_metrics,
    format_crypto_data_for_agents
)
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import json
import os
import pandas as pd
from tqdm import tqdm
from openai import OpenAI
from .config import get_config, set_config, DATA_DIR


# ========================================
# CRYPTOCURRENCY INTERFACE FUNCTIONS
# ========================================

def get_crypto_news(
    ticker: Annotated[str, "Cryptocurrency symbol, e.g. 'BTC', 'ETH'"],
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:
    """
    Retrieve news about a cryptocurrency within a time frame
    Uses Google News as CoinMarketCap doesn't provide news directly
    """
    # Get cryptocurrency name for better search results
    try:
        api = CoinMarketCapAPI()
        info = api.get_crypto_info([ticker])
        crypto_id = api.get_crypto_id(ticker)
        crypto_name = info['data'][str(crypto_id)]['name']
        
        # Search for both symbol and name
        query = f"{ticker} {crypto_name} cryptocurrency"
    except:
        # Fallback to just symbol
        query = f"{ticker} cryptocurrency"
    
    start_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")
    
    # Use Google News for crypto news
    news_results = getNewsData(query, before, curr_date)
    
    news_str = ""
    for news in news_results:
        news_str += (
            f"### {news['title']} (source: {news['source']}) \n\n{news['snippet']}\n\n"
        )
    
    if len(news_results) == 0:
        return ""
    
    return f"## {ticker} Cryptocurrency News, from {before} to {curr_date}:\n\n{news_str}"


def get_crypto_market_sentiment(
    ticker: Annotated[str, "Cryptocurrency symbol"],
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "Number of days to look back"],
) -> str:
    """
    Get cryptocurrency market sentiment and metrics
    """
    try:
        api = CoinMarketCapAPI()
        
        # Get current fundamentals
        fundamentals = get_crypto_fundamentals(ticker)
        
        # Get global market metrics
        market_metrics = get_market_metrics()
        
        # Format sentiment report
        sentiment_report = f"## {ticker} Market Sentiment Analysis\n\n"
        
        # Price performance
        sentiment_report += "### Price Performance\n"
        sentiment_report += f"- 24h Change: {fundamentals['percent_change_24h']:.2f}%\n"
        sentiment_report += f"- 7d Change: {fundamentals['percent_change_7d']:.2f}%\n"
        sentiment_report += f"- 30d Change: {fundamentals['percent_change_30d']:.2f}%\n\n"
        
        # Market position
        sentiment_report += "### Market Position\n"
        sentiment_report += f"- Market Cap: ${fundamentals['market_cap']:,.0f}\n"
        sentiment_report += f"- 24h Volume: ${fundamentals['volume_24h']:,.0f}\n"
        sentiment_report += f"- Market Cap Dominance: {fundamentals['market_cap_dominance']:.2f}%\n\n"
        
        # Global market context
        sentiment_report += "### Global Crypto Market Context\n"
        sentiment_report += f"- Total Market Cap: ${market_metrics['total_market_cap']:,.0f}\n"
        sentiment_report += f"- Bitcoin Dominance: {market_metrics['bitcoin_dominance']:.2f}%\n"
        sentiment_report += f"- Total 24h Volume: ${market_metrics['total_volume_24h']:,.0f}\n"
        sentiment_report += f"- DeFi Market Cap: ${market_metrics['defi_market_cap']:,.0f}\n"
        
        return sentiment_report
        
    except Exception as e:
        return f"Error fetching market sentiment for {ticker}: {str(e)}"


def get_crypto_fundamentals_report(
    ticker: Annotated[str, "Cryptocurrency symbol"],
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
) -> str:
    """
    Get comprehensive cryptocurrency fundamentals report
    """
    try:
        fundamentals = get_crypto_fundamentals(ticker)
        
        report = f"## {ticker} Cryptocurrency Fundamentals\n\n"
        
        # Basic information
        report += f"### Basic Information\n"
        report += f"- Name: {fundamentals['name']}\n"
        report += f"- Symbol: {fundamentals['symbol']}\n"
        report += f"- Date Added: {fundamentals['date_added']}\n"
        if fundamentals['website']:
            report += f"- Website: {fundamentals['website']}\n"
        if fundamentals['technical_doc']:
            report += f"- Technical Documentation: {fundamentals['technical_doc']}\n"
        report += f"- Tags: {', '.join(fundamentals['tags']) if fundamentals['tags'] else 'N/A'}\n\n"
        
        # Supply metrics
        report += f"### Supply Metrics\n"
        report += f"- Circulating Supply: {fundamentals['circulating_supply']:,.0f}\n"
        report += f"- Total Supply: {fundamentals['total_supply']:,.0f}\n"
        report += f"- Max Supply: {fundamentals['max_supply']:,.0f if fundamentals['max_supply'] else 'Unlimited'}\n\n"
        
        # Valuation metrics
        report += f"### Valuation Metrics\n"
        report += f"- Current Price: ${fundamentals['price']:,.4f}\n"
        report += f"- Market Cap: ${fundamentals['market_cap']:,.0f}\n"
        report += f"- Fully Diluted Market Cap: ${fundamentals['fully_diluted_market_cap']:,.0f}\n"
        report += f"- 24h Trading Volume: ${fundamentals['volume_24h']:,.0f}\n\n"
        
        # Platform information
        if fundamentals['platform']:
            report += f"### Platform Information\n"
            report += f"- Platform: {fundamentals['platform'].get('name', 'Unknown')}\n"
            report += f"- Token Address: {fundamentals['platform'].get('token_address', 'N/A')}\n\n"
        
        # Description
        if fundamentals['description']:
            report += f"### Project Description\n"
            report += f"{fundamentals['description'][:500]}...\n\n"
        
        return report
        
    except Exception as e:
        return f"Error fetching fundamentals for {ticker}: {str(e)}"


def get_crypto_price_data_window(
    symbol: Annotated[str, "Cryptocurrency symbol"],
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "How many days to look back"],
) -> str:
    """
    Get cryptocurrency price data for a window of time
    """
    try:
        # Calculate date range
        end_date = datetime.strptime(curr_date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=look_back_days)
        
        # Get price data
        df = get_crypto_price_data(
            symbol,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        
        if df.empty:
            return f"No price data available for {symbol} in the specified date range"
        
        # Format as string
        with pd.option_context(
            "display.max_rows", None,
            "display.max_columns", None,
            "display.width", None
        ):
            df_string = df.to_string()
        
        return (
            f"## Cryptocurrency Market Data for {symbol} "
            f"from {start_date.strftime('%Y-%m-%d')} to {curr_date}:\n\n"
            + df_string
        )
        
    except Exception as e:
        return f"Error fetching price data for {symbol}: {str(e)}"


def get_crypto_technical_indicators(
    symbol: Annotated[str, "Cryptocurrency symbol"],
    indicator: Annotated[str, "Technical indicator name"],
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "How many days to look back"],
) -> str:
    """
    Calculate technical indicators for cryptocurrency
    """
    try:
        # Get price data
        end_date = datetime.strptime(curr_date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=look_back_days + 50)  # Extra days for indicator calculation
        
        df = get_crypto_price_data(
            symbol,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        
        if df.empty:
            return f"No price data available for {symbol} to calculate indicators"
        
        # Prepare data for stockstats
        df_stats = df.copy()
        df_stats.columns = [col.lower() for col in df_stats.columns]
        
        # Calculate indicators using stockstats
        from stockstats import StockDataFrame
        stock = StockDataFrame.retype(df_stats)
        
        # Get indicator values
        indicator_values = stock[indicator]
        
        # Filter to requested date range
        indicator_values = indicator_values[indicator_values.index >= (end_date - timedelta(days=look_back_days))]
        
        # Format result
        result_str = f"## {indicator} values for {symbol} from {(end_date - timedelta(days=look_back_days)).strftime('%Y-%m-%d')} to {curr_date}:\n\n"
        
        for date, value in indicator_values.items():
            result_str += f"{date.strftime('%Y-%m-%d')}: {value:.4f}\n"
        
        # Add indicator description
        indicator_descriptions = {
            "rsi": "RSI: Relative Strength Index measures momentum. Values above 70 indicate overbought, below 30 indicate oversold.",
            "macd": "MACD: Moving Average Convergence Divergence shows trend changes through the relationship between two moving averages.",
            "boll": "Bollinger Bands: Middle band (20-day SMA) with upper/lower bands showing volatility.",
            "atr": "ATR: Average True Range measures volatility. Higher values indicate higher volatility.",
            "close_50_sma": "50-day Simple Moving Average: Medium-term trend indicator.",
            "close_200_sma": "200-day Simple Moving Average: Long-term trend indicator.",
        }
        
        if indicator in indicator_descriptions:
            result_str += f"\n{indicator_descriptions[indicator]}"
        
        return result_str
        
    except Exception as e:
        return f"Error calculating {indicator} for {symbol}: {str(e)}"


def get_reddit_crypto_sentiment(
    ticker: Annotated[str, "Cryptocurrency symbol"],
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "How many days to look back"],
    max_limit_per_day: Annotated[int, "Maximum posts per day"] = 10,
) -> str:
    """
    Get cryptocurrency sentiment from Reddit
    """
    start_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")
    
    posts = []
    curr_date_dt = datetime.strptime(before, "%Y-%m-%d")
    
    # Search for crypto-specific subreddits
    crypto_query = f"{ticker} cryptocurrency"
    
    while curr_date_dt <= start_date:
        curr_date_str = curr_date_dt.strftime("%Y-%m-%d")
        
        # Try to fetch from crypto-specific categories
        fetch_result = fetch_top_from_category(
            "cryptocurrency",  # Assuming this category exists in reddit_utils
            curr_date_str,
            max_limit_per_day,
            crypto_query,
            data_path=os.path.join(DATA_DIR, "reddit_data") if os.path.exists(os.path.join(DATA_DIR, "reddit_data")) else None
        )
        posts.extend(fetch_result)
        curr_date_dt += relativedelta(days=1)
    
    if len(posts) == 0:
        return f"No Reddit sentiment data found for {ticker}"
    
    news_str = ""
    for post in posts:
        if post["content"] == "":
            news_str += f"### {post['title']}\n\n"
        else:
            news_str += f"### {post['title']}\n\n{post['content']}\n\n"
    
    return f"## {ticker} Cryptocurrency Reddit Sentiment, from {before} to {curr_date}:\n\n{news_str}"


def get_crypto_market_overview(
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
) -> str:
    """
    Get overall cryptocurrency market overview
    """
    try:
        metrics = get_market_metrics()
        
        overview = "## Global Cryptocurrency Market Overview\n\n"
        
        # Market size
        overview += "### Market Size\n"
        overview += f"- Total Market Cap: ${metrics['total_market_cap']:,.0f}\n"
        overview += f"- 24h Trading Volume: ${metrics['total_volume_24h']:,.0f}\n"
        overview += f"- Active Cryptocurrencies: {metrics['active_cryptocurrencies']:,}\n"
        overview += f"- Active Exchanges: {metrics['active_exchanges']:,}\n\n"
        
        # Market dominance
        overview += "### Market Dominance\n"
        overview += f"- Bitcoin Dominance: {metrics['bitcoin_dominance']:.2f}%\n"
        overview += f"- Ethereum Dominance: {metrics['ethereum_dominance']:.2f}%\n"
        overview += f"- Altcoin Market Cap: ${metrics['altcoin_market_cap']:,.0f}\n\n"
        
        # Sector breakdown
        overview += "### Sector Performance\n"
        overview += f"- DeFi Market Cap: ${metrics['defi_market_cap']:,.0f}\n"
        overview += f"- DeFi 24h Volume: ${metrics['defi_volume_24h']:,.0f}\n"
        overview += f"- Stablecoin Market Cap: ${metrics['stablecoin_market_cap']:,.0f}\n"
        overview += f"- Stablecoin 24h Volume: ${metrics['stablecoin_volume_24h']:,.0f}\n\n"
        
        # Market changes
        overview += "### 24h Market Changes\n"
        total_cap_change = (
            (metrics['total_market_cap'] - metrics['total_market_cap_yesterday']) 
            / metrics['total_market_cap_yesterday'] * 100
        )
        volume_change = (
            (metrics['total_volume_24h'] - metrics['total_volume_24h_yesterday']) 
            / metrics['total_volume_24h_yesterday'] * 100
        )
        
        overview += f"- Market Cap Change: {total_cap_change:+.2f}%\n"
        overview += f"- Volume Change: {volume_change:+.2f}%\n"
        overview += f"- Last Updated: {metrics['last_updated']}\n"
        
        return overview
        
    except Exception as e:
        return f"Error fetching market overview: {str(e)}"


def get_crypto_correlation_analysis(
    symbols: Annotated[List[str], "List of cryptocurrency symbols to analyze"],
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "How many days to look back"],
) -> str:
    """
    Analyze correlations between multiple cryptocurrencies
    """
    try:
        end_date = datetime.strptime(curr_date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=look_back_days)
        
        # Collect price data for all symbols
        price_data = {}
        for symbol in symbols:
            df = get_crypto_price_data(
                symbol,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
            if not df.empty:
                price_data[symbol] = df['Close']
        
        if len(price_data) < 2:
            return "Not enough data to calculate correlations"
        
        # Create correlation matrix
        df_combined = pd.DataFrame(price_data)
        correlation_matrix = df_combined.corr()
        
        # Format report
        report = f"## Cryptocurrency Correlation Analysis\n"
        report += f"Period: {start_date.strftime('%Y-%m-%d')} to {curr_date}\n\n"
        
        report += "### Correlation Matrix\n"
        report += correlation_matrix.to_string() + "\n\n"
        
        report += "### Interpretation\n"
        report += "- Values close to 1: Strong positive correlation\n"
        report += "- Values close to -1: Strong negative correlation\n"
        report += "- Values close to 0: Little to no correlation\n\n"
        
        # Find highest and lowest correlations
        report += "### Key Findings\n"
        for i in range(len(symbols)):
            for j in range(i+1, len(symbols)):
                corr_value = correlation_matrix.iloc[i, j]
                report += f"- {symbols[i]}/{symbols[j]}: {corr_value:.3f}\n"
        
        return report
        
    except Exception as e:
        return f"Error calculating correlations: {str(e)}"


def get_google_news(
    query: Annotated[str, "Query to search with"],
    curr_date: Annotated[str, "Curr date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:
    """
    Get news from Google News for any query
    """
    query = query.replace(" ", "+")
    
    start_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")
    
    news_results = getNewsData(query, before, curr_date)
    
    news_str = ""
    for news in news_results:
        news_str += (
            f"### {news['title']} (source: {news['source']}) \n\n{news['snippet']}\n\n"
        )
    
    if len(news_results) == 0:
        return ""
    
    return f"## {query} Google News, from {before} to {curr_date}:\n\n{news_str}"


# OpenAI-based functions for online data gathering
def get_crypto_news_openai(ticker: str, curr_date: str) -> str:
    """
    Get cryptocurrency news using OpenAI's web search
    """
    client = OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-4-mini",
        messages=[
            {
                "role": "system",
                "content": f"Search for recent news about {ticker} cryptocurrency from 7 days before {curr_date} to {curr_date}. Focus on price movements, major developments, partnerships, regulatory news, and technical updates."
            }
        ],
        tools=[
            {
                "type": "web_search",
                "web_search": {
                    "query": f"{ticker} cryptocurrency news {curr_date}"
                }
            }
        ],
        temperature=0.7,
        max_tokens=4096
    )
    
    return response.choices[0].message.content


def get_crypto_social_sentiment_openai(ticker: str, curr_date: str) -> str:
    """
    Get cryptocurrency social media sentiment using OpenAI
    """
    client = OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-4-mini",
        messages=[
            {
                "role": "system",
                "content": f"Search social media (Twitter, Reddit, Discord) for sentiment about {ticker} cryptocurrency from 7 days before {curr_date} to {curr_date}. Look for community sentiment, major influencer opinions, and trending discussions."
            }
        ],
        tools=[
            {
                "type": "web_search",
                "web_search": {
                    "query": f"{ticker} crypto Twitter Reddit sentiment {curr_date}"
                }
            }
        ],
        temperature=0.7,
        max_tokens=4096
    )
    
    return response.choices[0].message.content