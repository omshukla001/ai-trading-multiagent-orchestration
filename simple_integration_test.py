"""
Simple Controlled Integration Test
Tests one stock with optimized analysts
"""
import sys
import os

# Add flag to enable optimized analysts
os.environ['USE_OPTIMIZED_ANALYSTS'] = '1'

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from datetime import datetime, timedelta
import time

if len(sys.argv) < 2:
    print("Usage: python simple_integration_test.py <TICKER>")
    print("Example: python simple_integration_test.py HDFCBANK.NS")
    sys.exit(1)

ticker = sys.argv[1]

# Configure for Groq
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "groq"
config["deep_think_llm"] = "llama-3.3-70b-versatile"
config["quick_think_llm"] = "llama-3.3-70b-versatile"
config["max_debate_rounds"] = 1
config["max_risk_rounds"] = 1

analysis_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

print("=" * 80)
print(f"INTEGRATION TEST: {ticker}")
print("=" * 80)
print(f"Date: {analysis_date}")
print(f"Using: Optimized Analysts (Python-based)")
print(f"Model: {config['deep_think_llm']}")
print("=" * 80 + "\n")

try:
    start_time = time.time()
    
    ta = TradingAgentsGraph(debug=True, config=config)
    _, decision = ta.propagate(ticker, analysis_date)
    
    runtime = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("TEST RESULT: ✅ SUCCESS")
    print("=" * 80)
    print(f"Runtime: {runtime:.1f} seconds")
    print(f"Decision length: {len(decision)} characters")
    print("\n" + "=" * 80)
    print("FINAL DECISION")
    print("=" * 80)
    print(decision)
    print("=" * 80)
    
    # Save result
    with open(f'test_result_{ticker.replace(".", "_")}.txt', 'w') as f:
        f.write(f"Ticker: {ticker}\n")
        f.write(f"Date: {analysis_date}\n")
        f.write(f"Runtime: {runtime:.1f}s\n")
        f.write(f"\n{'=' * 80}\n")
        f.write(decision)
    
    print(f"\n✓ Result saved to: test_result_{ticker.replace('.', '_')}.txt")
    
except Exception as e:
    print("\n" + "=" * 80)
    print("TEST RESULT: ❌ FAILED")
    print("=" * 80)
    print(f"Error: {str(e)}")
    print("=" * 80)
    
    import traceback
    traceback.print_exc()
