"""
Single Stock Analysis for Testing
"""
import sys
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from datetime import datetime, timedelta

if len(sys.argv) < 2:
    print("Usage: python test_single_stock.py <TICKER>")
    print("Example: python test_single_stock.py HDFCBANK.NS")
    sys.exit(1)

ticker = sys.argv[1]

# Configure for Groq (fast and generous free tier)
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "groq"
config["deep_think_llm"] = "llama-3.3-70b-versatile"
config["quick_think_llm"] = "llama-3.3-70b-versatile"
config["max_debate_rounds"] = 1
config["max_risk_rounds"] = 1

analysis_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

print("=" * 80)
print(f"ANALYZING: {ticker}")
print("=" * 80)
print(f"Date: {analysis_date}")
print(f"Model: llama-3.3-70b-versatile (Groq)")
print("=" * 80 + "\n")

ta = TradingAgentsGraph(debug=True, config=config)

try:
    _, decision = ta.propagate(ticker, analysis_date)
    
    print("\n" + "=" * 80)
    print("FINAL DECISION")
    print("=" * 80)
    print(decision)
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
