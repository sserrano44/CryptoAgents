"""
Test script for CryptoAgents integration
Tests basic functionality without making actual API calls
"""
import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that all crypto modules can be imported"""
    print("Testing imports...")
    
    try:
        from cryptoagents.dataflows.coinmarketcap_utils import CoinMarketCapAPI
        print("✅ CoinMarketCap utils imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import CoinMarketCap utils: {e}")
        return False
    
    try:
        from cryptoagents.dataflows.interface import (
            get_crypto_news,
            get_crypto_market_sentiment,
            get_crypto_fundamentals_report
        )
        print("✅ Crypto interface imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import crypto interface: {e}")
        return False
    
    try:
        from cryptoagents.config import CRYPTO_CONFIG, validate_crypto_symbol
        print("✅ Crypto config imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import crypto config: {e}")
        return False
    
    try:
        # Import directly from the module files to avoid parent imports
        from cryptoagents.agents.crypto_analysts.crypto_market_analyst import create_crypto_market_analyst
        from cryptoagents.agents.crypto_analysts.crypto_fundamentals_analyst import create_crypto_fundamentals_analyst
        from cryptoagents.agents.crypto_analysts.crypto_news_analyst import create_crypto_news_analyst
        from cryptoagents.agents.crypto_analysts.crypto_social_analyst import create_crypto_social_analyst
        print("✅ Crypto analysts imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import crypto analysts: {e}")
        return False
    
    try:
        from cryptoagents.dataflows.crypto_toolkit import create_crypto_toolkit
        print("✅ Crypto toolkit imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import crypto toolkit: {e}")
        return False
    
    try:
        from cryptoagents.crypto_trading_graph_standalone import CryptoTradingAgentsGraph
        print("✅ Crypto trading graph imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import crypto trading graph: {e}")
        return False
    
    return True


def test_config():
    """Test crypto configuration"""
    print("\nTesting configuration...")
    
    from cryptoagents.config import CRYPTO_CONFIG, validate_crypto_symbol, get_crypto_trading_params
    
    # Test config structure
    required_keys = [
        "coinmarketcap_api_key",
        "supported_cryptos",
        "max_position_size_pct",
        "stop_loss_pct",
        "volatility_multiplier"
    ]
    
    for key in required_keys:
        if key in CRYPTO_CONFIG:
            print(f"✅ Config has '{key}'")
        else:
            print(f"❌ Config missing '{key}'")
            return False
    
    # Test symbol validation
    test_symbols = ["BTC", "ETH", "INVALID"]
    for symbol in test_symbols:
        is_valid = validate_crypto_symbol(symbol)
        if symbol == "INVALID" and not is_valid:
            print(f"✅ Correctly rejected invalid symbol: {symbol}")
        elif symbol != "INVALID" and is_valid:
            print(f"✅ Correctly validated symbol: {symbol}")
        else:
            print(f"❌ Symbol validation error for: {symbol}")
    
    # Test trading params
    btc_params = get_crypto_trading_params("BTC")
    print(f"✅ BTC trading params: max_position={btc_params['max_position_size_pct']}%, stop_loss={btc_params['stop_loss_pct']}%")
    
    return True


def test_api_structure():
    """Test API structure without making actual calls"""
    print("\nTesting API structure...")
    
    # Mock environment variable for testing
    os.environ["COINMARKETCAP_API_KEY"] = "test_key_for_structure_testing"
    
    try:
        from cryptoagents.dataflows.coinmarketcap_utils import CoinMarketCapAPI
        
        # Test initialization
        api = CoinMarketCapAPI(api_key="test_key", use_sandbox=True)
        print("✅ CoinMarketCap API initialized successfully")
        
        # Check methods exist
        methods = [
            "get_crypto_map",
            "get_crypto_id",
            "get_latest_quote",
            "get_historical_quotes",
            "get_crypto_info",
            "get_global_metrics"
        ]
        
        for method in methods:
            if hasattr(api, method):
                print(f"✅ API has method: {method}")
            else:
                print(f"❌ API missing method: {method}")
                return False
        
    except Exception as e:
        print(f"❌ API structure test failed: {e}")
        return False
    
    return True


def test_toolkit():
    """Test crypto toolkit creation"""
    print("\nTesting crypto toolkit...")
    
    # Mock environment variable
    os.environ["COINMARKETCAP_API_KEY"] = "test_key"
    
    try:
        from cryptoagents.dataflows.crypto_toolkit import create_crypto_toolkit
        from cryptoagents.config import CRYPTO_CONFIG
        
        config = CRYPTO_CONFIG.copy()
        config["online_tools"] = False  # Disable online tools for testing
        
        toolkit = create_crypto_toolkit(config)
        print("✅ Crypto toolkit created successfully")
        
        # Check tool categories
        market_tools = toolkit.get_market_analysis_tools()
        fundamental_tools = toolkit.get_fundamental_analysis_tools()
        news_tools = toolkit.get_news_analysis_tools()
        social_tools = toolkit.get_social_analysis_tools()
        
        print(f"✅ Market analysis tools: {len(market_tools)}")
        print(f"✅ Fundamental analysis tools: {len(fundamental_tools)}")
        print(f"✅ News analysis tools: {len(news_tools)}")
        print(f"✅ Social analysis tools: {len(social_tools)}")
        
    except Exception as e:
        print(f"❌ Toolkit test failed: {e}")
        return False
    
    return True


def main():
    """Run all tests"""
    print("="*60)
    print("CryptoAgents Integration Test")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("API Structure", test_api_structure),
        ("Toolkit", test_toolkit)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} Test ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        symbol = "✅" if result else "❌"
        print(f"{symbol} {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! CryptoAgents is ready to use.")
        print("\nNext steps:")
        print("1. Set your API keys:")
        print("   export OPENAI_API_KEY=your_key")
        print("   export COINMARKETCAP_API_KEY=your_key")
        print("2. Run: python crypto_main.py")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
