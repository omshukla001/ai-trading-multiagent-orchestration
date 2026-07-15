#!/usr/bin/env python3
"""
Simple test of optimized analysts
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

print("="*80)
print(f"TESTING: {ticker}")
print(f"Date: {analysis_date}")
print("="*80)

try:
    ta = TradingAgentsGraph(debug=False, config=config)
    _, decision = ta.propagate(ticker, analysis_date)
    print(f"\n✅ SUCCESS: {decision}")
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
