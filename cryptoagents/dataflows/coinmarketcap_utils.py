"""
CoinMarketCap API utilities for cryptocurrency data fetching
"""
import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time
from functools import lru_cache
import pandas as pd


class CoinMarketCapAPI:
    """
    CoinMarketCap API wrapper for cryptocurrency data
    """
    
    BASE_URL = "https://pro-api.coinmarketcap.com"
    SANDBOX_URL = "https://sandbox-api.coinmarketcap.com"  # For testing
    
    def __init__(self, api_key: Optional[str] = None, use_sandbox: bool = False):
        """
        Initialize CoinMarketCap API client
        
        Args:
            api_key: CoinMarketCap API key
            use_sandbox: Use sandbox API for testing
        """
        self.api_key = api_key or os.environ.get("COINMARKETCAP_API_KEY")
        if not self.api_key:
            raise ValueError("CoinMarketCap API key not provided")
        
        self.base_url = self.SANDBOX_URL if use_sandbox else self.BASE_URL
        self.headers = {
            'X-CMC_PRO_API_KEY': self.api_key,
            'Accept': 'application/json'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 10 requests per second max
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make API request with rate limiting
        """
        # Rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            self.last_request_time = time.time()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    @lru_cache(maxsize=128)
    def get_crypto_map(self) -> Dict[str, int]:
        """
        Get mapping of cryptocurrency symbols to CoinMarketCap IDs
        Cached to avoid repeated API calls
        """
        endpoint = "/v1/cryptocurrency/map"
        params = {
            'limit': 5000,
            'sort': 'cmc_rank'
        }
        
        response = self._make_request(endpoint, params)
        
        # Create symbol to ID mapping
        symbol_map = {}
        for crypto in response.get('data', []):
            symbol = crypto['symbol'].upper()
            # Handle multiple tokens with same symbol by preferring higher rank
            if symbol not in symbol_map:
                symbol_map[symbol] = crypto['id']
        
        return symbol_map
    
    def get_crypto_id(self, symbol: str) -> int:
        """
        Get CoinMarketCap ID for a cryptocurrency symbol
        """
        symbol_map = self.get_crypto_map()
        symbol = symbol.upper()
        
        if symbol not in symbol_map:
            raise ValueError(f"Symbol {symbol} not found in CoinMarketCap")
        
        return symbol_map[symbol]
    
    def get_latest_quote(self, symbols: List[str]) -> Dict:
        """
        Get latest price quotes for cryptocurrencies
        
        Args:
            symbols: List of cryptocurrency symbols (e.g., ['BTC', 'ETH'])
        """
        # Convert symbols to IDs
        ids = []
        for symbol in symbols:
            try:
                ids.append(str(self.get_crypto_id(symbol)))
            except ValueError:
                print(f"Warning: Symbol {symbol} not found")
        
        if not ids:
            return {}
        
        endpoint = "/v2/cryptocurrency/quotes/latest"
        params = {
            'id': ','.join(ids),
            'convert': 'USD'
        }
        
        return self._make_request(endpoint, params)
    
    def get_historical_quotes(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get historical OHLCV data for a cryptocurrency
        
        Args:
            symbol: Cryptocurrency symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            DataFrame with OHLCV data
        """
        crypto_id = self.get_crypto_id(symbol)
        
        # Convert dates to timestamps
        start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        
        endpoint = "/v2/cryptocurrency/ohlcv/historical"
        params = {
            'id': crypto_id,
            'time_start': start_ts,
            'time_end': end_ts,
            'convert': 'USD',
            'interval': 'daily'
        }
        
        response = self._make_request(endpoint, params)
        
        # Convert to DataFrame
        quotes = response.get('data', {}).get('quotes', [])
        if not quotes:
            return pd.DataFrame()
        
        df_data = []
        for quote in quotes:
            df_data.append({
                'Date': quote['time_open'],
                'Open': quote['quote']['USD']['open'],
                'High': quote['quote']['USD']['high'],
                'Low': quote['quote']['USD']['low'],
                'Close': quote['quote']['USD']['close'],
                'Volume': quote['quote']['USD']['volume'],
                'Market_Cap': quote['quote']['USD']['market_cap']
            })
        
        df = pd.DataFrame(df_data)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        
        return df
    
    def get_crypto_info(self, symbols: List[str]) -> Dict:
        """
        Get detailed information about cryptocurrencies
        
        Args:
            symbols: List of cryptocurrency symbols
        """
        # Convert symbols to IDs
        ids = []
        for symbol in symbols:
            try:
                ids.append(str(self.get_crypto_id(symbol)))
            except ValueError:
                print(f"Warning: Symbol {symbol} not found")
        
        if not ids:
            return {}
        
        endpoint = "/v2/cryptocurrency/info"
        params = {
            'id': ','.join(ids)
        }
        
        return self._make_request(endpoint, params)
    
    def get_global_metrics(self) -> Dict:
        """
        Get global cryptocurrency market metrics
        """
        endpoint = "/v1/global-metrics/quotes/latest"
        params = {
            'convert': 'USD'
        }
        
        return self._make_request(endpoint, params)
    
    def get_trending_cryptocurrencies(self, limit: int = 10) -> Dict:
        """
        Get trending cryptocurrencies
        """
        endpoint = "/v1/cryptocurrency/trending/latest"
        params = {
            'limit': limit
        }
        
        return self._make_request(endpoint, params)


def get_crypto_price_data(
    ticker: str,
    start_date: str,
    end_date: str,
    api_key: Optional[str] = None
) -> pd.DataFrame:
    """
    Get cryptocurrency price data for a given date range
    
    Args:
        ticker: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        api_key: CoinMarketCap API key (optional, will use env var if not provided)
    
    Returns:
        DataFrame with OHLCV data
    """
    api = CoinMarketCapAPI(api_key)
    return api.get_historical_quotes(ticker, start_date, end_date)


def get_crypto_fundamentals(
    ticker: str,
    api_key: Optional[str] = None
) -> Dict:
    """
    Get cryptocurrency fundamental data
    
    Args:
        ticker: Cryptocurrency symbol
        api_key: CoinMarketCap API key
    
    Returns:
        Dictionary with fundamental data
    """
    api = CoinMarketCapAPI(api_key)
    
    # Get latest quote
    quote_data = api.get_latest_quote([ticker])
    
    # Get crypto info
    info_data = api.get_crypto_info([ticker])
    
    # Extract relevant data
    crypto_id = api.get_crypto_id(ticker)
    
    fundamentals = {
        'symbol': ticker,
        'name': '',
        'market_cap': 0,
        'circulating_supply': 0,
        'total_supply': 0,
        'max_supply': 0,
        'price': 0,
        'volume_24h': 0,
        'percent_change_24h': 0,
        'percent_change_7d': 0,
        'percent_change_30d': 0,
        'description': '',
        'website': '',
        'technical_doc': '',
        'tags': [],
        'platform': None,
        'date_added': '',
        'market_cap_dominance': 0,
        'fully_diluted_market_cap': 0
    }
    
    # Parse quote data
    if quote_data and 'data' in quote_data:
        quote = quote_data['data'].get(str(crypto_id), {}).get('quote', {}).get('USD', {})
        fundamentals.update({
            'price': quote.get('price', 0),
            'volume_24h': quote.get('volume_24h', 0),
            'percent_change_24h': quote.get('percent_change_24h', 0),
            'percent_change_7d': quote.get('percent_change_7d', 0),
            'percent_change_30d': quote.get('percent_change_30d', 0),
            'market_cap': quote.get('market_cap', 0),
            'market_cap_dominance': quote.get('market_cap_dominance', 0),
            'fully_diluted_market_cap': quote.get('fully_diluted_market_cap', 0)
        })
        
        # Get supply data
        supply_data = quote_data['data'].get(str(crypto_id), {})
        fundamentals.update({
            'circulating_supply': supply_data.get('circulating_supply', 0),
            'total_supply': supply_data.get('total_supply', 0),
            'max_supply': supply_data.get('max_supply', 0)
        })
    
    # Parse info data
    if info_data and 'data' in info_data:
        info = info_data['data'].get(str(crypto_id), {})
        fundamentals.update({
            'name': info.get('name', ''),
            'description': info.get('description', ''),
            'website': info.get('urls', {}).get('website', [''])[0] if info.get('urls', {}).get('website') else '',
            'technical_doc': info.get('urls', {}).get('technical_doc', [''])[0] if info.get('urls', {}).get('technical_doc') else '',
            'tags': info.get('tags', []),
            'platform': info.get('platform'),
            'date_added': info.get('date_added', '')
        })
    
    return fundamentals


def get_market_metrics(api_key: Optional[str] = None) -> Dict:
    """
    Get global cryptocurrency market metrics
    """
    api = CoinMarketCapAPI(api_key)
    metrics = api.get_global_metrics()
    
    if metrics and 'data' in metrics:
        data = metrics['data']
        quote = data.get('quote', {}).get('USD', {})
        
        return {
            'total_market_cap': quote.get('total_market_cap', 0),
            'total_volume_24h': quote.get('total_volume_24h', 0),
            'bitcoin_dominance': data.get('btc_dominance', 0),
            'ethereum_dominance': data.get('eth_dominance', 0),
            'active_cryptocurrencies': data.get('active_cryptocurrencies', 0),
            'active_exchanges': data.get('active_exchanges', 0),
            'total_market_cap_yesterday': quote.get('total_market_cap_yesterday', 0),
            'total_volume_24h_yesterday': quote.get('total_volume_24h_yesterday', 0),
            'altcoin_market_cap': quote.get('altcoin_market_cap', 0),
            'altcoin_volume_24h': quote.get('altcoin_volume_24h', 0),
            'defi_volume_24h': quote.get('defi_volume_24h', 0),
            'defi_market_cap': quote.get('defi_market_cap', 0),
            'stablecoin_volume_24h': quote.get('stablecoin_volume_24h', 0),
            'stablecoin_market_cap': quote.get('stablecoin_market_cap', 0),
            'last_updated': data.get('last_updated', '')
        }
    
    return {}


def format_crypto_data_for_agents(ticker: str, start_date: str, end_date: str, api_key: Optional[str] = None) -> Dict:
    """
    Format cryptocurrency data for use by trading agents
    
    Args:
        ticker: Cryptocurrency symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        api_key: CoinMarketCap API key
    
    Returns:
        Dictionary with formatted data for agents
    """
    # Get price data
    price_data = get_crypto_price_data(ticker, start_date, end_date, api_key)
    
    # Get fundamentals
    fundamentals = get_crypto_fundamentals(ticker, api_key)
    
    # Get market metrics
    market_metrics = get_market_metrics(api_key)
    
    return {
        'ticker': ticker,
        'price_data': price_data.to_dict() if not price_data.empty else {},
        'fundamentals': fundamentals,
        'market_metrics': market_metrics,
        'data_period': {
            'start': start_date,
            'end': end_date
        }
    }
