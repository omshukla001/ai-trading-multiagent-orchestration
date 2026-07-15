"""
Test script for analyzing Indian stocks with TradingAgents
"""
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from datetime import datetime, timedelta

# Configure for Google Gemini
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "google"  # Use Google Gemini
config["deep_think_llm"] = "gemini-3.5-flash"  # Fast model for testing
config["quick_think_llm"] = "gemini-3.5-flash"
config["max_debate_rounds"] = 1  # Reduce rounds for faster testing
config["max_risk_rounds"] = 1

print("=" * 80)
print("TradingAgents - Indian Stock Market Test")
print("=" * 80)
print(f"\nConfiguration:")
print(f"  LLM Provider: {config['llm_provider']}")
print(f"  Model: {config['deep_think_llm']}")
print(f"  Debate Rounds: {config['max_debate_rounds']}")
print(f"  Risk Rounds: {config['max_risk_rounds']}")
print("\n" + "=" * 80)

# Initialize TradingAgents
print("\n[1/3] Initializing TradingAgents...")
ta = TradingAgentsGraph(debug=True, config=config)
print("✓ Initialized successfully")

# Test with a popular Indian stock - Reliance Industries (NSE)
ticker = "RELIANCE.NS"  # Reliance Industries on NSE
# Use a recent date for analysis (5 days ago)
analysis_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

print(f"\n[2/3] Analyzing {ticker} as of {analysis_date}...")
print(f"      Company: Reliance Industries Limited")
print(f"      Exchange: NSE (National Stock Exchange of India)")
print("\n" + "-" * 80)

try:
    # Run analysis
    _, decision = ta.propagate(ticker, analysis_date)
    
    print("\n" + "=" * 80)
    print("[3/3] Analysis Complete!")
    print("=" * 80)
    print("\n" + "=" * 80)
    print("FINAL DECISION")
    print("=" * 80)
    print(decision)
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ Error during analysis: {str(e)}")
    print(f"\nError type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    
print("\n" + "=" * 80)
print("Test Complete")
print("=" * 80)
