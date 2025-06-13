"""
CryptoAgents - Cryptocurrency Trading with Multi-Agent LLMs
Main entry point for cryptocurrency trading analysis
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from cryptoagents.crypto_trading_graph_standalone import CryptoTradingAgentsGraph
from cryptoagents.config import CRYPTO_CONFIG, CRYPTO_PROMPTS

# Load environment variables from .env file
load_dotenv()


def print_banner():
    """Print CryptoAgents banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║                      CryptoAgents v1.0                        ║
    ║         Multi-Agent LLM Cryptocurrency Trading Framework      ║
    ║                                                               ║
    ║              Powered by CoinMarketCap API                     ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def validate_environment():
    """Validate required environment variables"""
    required_vars = ["OPENAI_API_KEY", "COINMARKETCAP_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease set the following environment variables:")
        print("  export OPENAI_API_KEY=your_openai_api_key")
        print("  export COINMARKETCAP_API_KEY=your_coinmarketcap_api_key")
        sys.exit(1)
    
    print("✅ Environment validated successfully")


def main():
    """Main function to run crypto trading analysis"""
    print_banner()
    
    # Validate environment
    validate_environment()
    
    # Example usage
    print("\n" + CRYPTO_PROMPTS["risk_warning"])
    print("\n" + "="*60)
    
    # Create custom config (optional)
    config = CRYPTO_CONFIG.copy()
    
    # You can modify config here if needed
    # config["deep_think_llm"] = "gpt-4"  # Use more powerful model
    # config["online_tools"] = True  # Enable online tools
    
    # Initialize the crypto trading graph
    print("\n🚀 Initializing CryptoAgents Trading System...")
    crypto_graph = CryptoTradingAgentsGraph(debug=True, config=config)
    
    # Example 1: Analyze a single cryptocurrency
    print("\n📊 Example 1: Analyzing Bitcoin (BTC)")
    print("-" * 60)
    
    try:
        btc_result = crypto_graph.analyze_crypto("BTC", "2024-12-01")
        
        print("\n📈 Analysis Complete!")
        print(f"Decision: {btc_result['final_decision']}")
        
    except Exception as e:
        print(f"\n❌ Error analyzing BTC: {str(e)}")
    
    # Example 2: Analyze multiple cryptocurrencies
    print("\n📊 Example 2: Batch Analysis of Top Cryptos")
    print("-" * 60)
    
    crypto_portfolio = ["ETH", "BNB", "SOL", "ADA"]
    
    try:
        results = crypto_graph.batch_analyze(crypto_portfolio, "2024-12-01")
        
        print("\n📋 Portfolio Analysis Summary:")
        print("-" * 40)
        for result in results:
            if "error" not in result:
                print(f"{result['crypto']:6} | Decision: {result['final_decision']}")
            else:
                print(f"{result['crypto']:6} | Error: {result['error']}")
        
    except Exception as e:
        print(f"\n❌ Error in batch analysis: {str(e)}")
    
    # Example 3: Custom cryptocurrency analysis
    print("\n📊 Example 3: Custom Crypto Analysis")
    print("-" * 60)
    print("You can analyze any cryptocurrency by symbol...")
    
    # Uncomment to try interactive mode
    # while True:
    #     crypto_symbol = input("\nEnter cryptocurrency symbol (or 'quit' to exit): ").upper()
    #     if crypto_symbol == 'QUIT':
    #         break
    #     
    #     try:
    #         result = crypto_graph.analyze_crypto(crypto_symbol)
    #         print(f"\nDecision for {crypto_symbol}: {result['final_decision']}")
    #     except Exception as e:
    #         print(f"Error: {str(e)}")
    
    print("\n✅ CryptoAgents analysis complete!")
    print("\n" + CRYPTO_PROMPTS["risk_warning"])


if __name__ == "__main__":
    main()
