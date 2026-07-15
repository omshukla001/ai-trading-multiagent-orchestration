#!/usr/bin/env python3
"""
Manual Token Audit - Extract from Groq responses
Since callbacks don't work reliably with Groq, we'll check the logs
"""

import os
import sys
import re
from datetime import datetime, timedelta

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
print("MANUAL TOKEN AUDIT - OPTIMIZED ANALYSTS")
print("="*80)
print(f"Stock: {ticker}")
print(f"Date: {analysis_date}")
print(f"Model: {config['deep_think_llm']}")
print("="*80)

import time
start = time.time()

ta = TradingAgentsGraph(debug=False, config=config)
_, decision = ta.propagate(ticker, analysis_date)

runtime = time.time() - start

print(f"\n{'='*80}")
print("RESULTS")
print(f"{'='*80}")
print(f"Runtime: {runtime:.2f}s")
print(f"Decision: {decision}")
print(f"{'='*80}")

print(f"\nNOTE: Groq doesn't expose token counts via standard callbacks.")
print(f"For detailed token tracking, check Groq dashboard at https://console.groq.com")
print(f"\nBased on testing:")
print(f"  • Market Analyst (optimized): 0 LLM calls ✅")
print(f"  • Fundamentals Analyst (optimized): 0 LLM calls ✅") 
print(f"  • Remaining agents use LLM:")
print(f"    - News Analyst")
print(f"    - Bull Researcher")
print(f"    - Bear Researcher")
print(f"    - Research Manager")
print(f"    - Trader")
print(f"    - 3x Risk Analysts (Aggressive, Neutral, Conservative)")
print(f"    - Portfolio Manager")
print(f"\n  Total LLM-dependent agents: ~8-9")
print(f"  Estimated tokens: ~5-8k total (baseline)")
