#!/usr/bin/env python3
"""
Simple Token Usage Test for Optimized Analysts
Uses Groq to run one stock through the workflow
"""

import os
import sys
from datetime import datetime, timedelta

# Enable optimized analysts
os.environ['USE_OPTIMIZED_ANALYSTS'] = '1'

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ticker = "HDFCBANK.NS"

# Configure for Groq
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "groq"
config["deep_think_llm"] = "llama-3.3-70b-versatile"
config["quick_think_llm"] = "llama-3.3-70b-versatile"
config["max_debate_rounds"] = 1
config["max_risk_rounds"] = 1

analysis_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

print("=" * 80)
print(f"SIMPLE TOKEN TEST - OPTIMIZED ANALYSTS")
print("=" * 80)
print(f"Stock: {ticker}")
print(f"Date: {analysis_date}")
print(f"Model: {config['deep_think_llm']}")
print("=" * 80 + "\n")

ta = TradingAgentsGraph(debug=True, config=config)

try:
    print("\n🚀 Running analysis...\n")
    _, decision = ta.propagate(ticker, analysis_date)
    
    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\nDecision: {decision}")
    print("\n" + "=" * 80)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
