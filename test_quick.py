#!/usr/bin/env python3
"""Quick test to check what's wrong"""

import os
from dotenv import load_dotenv
load_dotenv()

print("Testing CryptoAgents initialization...")

try:
    from cryptoagents.crypto_trading_graph_standalone import CryptoTradingAgentsGraph
    from cryptoagents.config import CRYPTO_CONFIG
    
    print("✅ Imports successful")
    
    # Test config
    config = CRYPTO_CONFIG.copy()
    print("✅ Config loaded")
    
    # Test graph creation
    print("🚀 Creating crypto graph...")
    crypto_graph = CryptoTradingAgentsGraph(debug=True, config=config)
    print("✅ Graph created")
    
    # Test simple analysis with timeout
    print("📊 Testing BTC analysis...")
    import signal
    
    def timeout_handler(signum, frame):
        raise Exception("Analysis timed out")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30 second timeout
    
    try:
        result = crypto_graph.analyze_crypto("BTC", "2024-12-01")
        print(f"✅ Analysis complete: {result.get('final_decision', 'No decision')}")
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
    finally:
        signal.alarm(0)  # Cancel alarm
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()