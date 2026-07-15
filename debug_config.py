#!/usr/bin/env python3
"""
Minimal debug script to trace configuration flow
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

print("="*80)
print("CONFIGURATION DEBUG TEST")
print("="*80)

# Check available API keys
print("\n1. Available API Keys:")
print(f"   GOOGLE_API_KEY: {'✅ SET' if os.environ.get('GOOGLE_API_KEY') else '❌ NOT SET'}")
print(f"   GROQ_API_KEY: {'✅ SET' if os.environ.get('GROQ_API_KEY') else '❌ NOT SET'}")
print(f"   OPENAI_API_KEY: {'✅ SET' if os.environ.get('OPENAI_API_KEY') else '❌ NOT SET'}")

# Import and check DEFAULT_CONFIG
print("\n2. DEFAULT_CONFIG:")
from tradingagents.default_config import DEFAULT_CONFIG
print(f"   llm_provider: {DEFAULT_CONFIG.get('llm_provider')}")
print(f"   deep_think_llm: {DEFAULT_CONFIG.get('deep_think_llm')}")
print(f"   quick_think_llm: {DEFAULT_CONFIG.get('quick_think_llm')}")

# Create custom config
print("\n3. Creating custom config:")
config = DEFAULT_CONFIG.copy()
print(f"   BEFORE override - llm_provider: {config.get('llm_provider')}")
print(f"   BEFORE override - deep_think_llm: {config.get('deep_think_llm')}")

config["llm_provider"] = "google"
config["deep_think_llm"] = "gemini-3.5-flash"
config["quick_think_llm"] = "gemini-3.5-flash"

print(f"   AFTER override - llm_provider: {config.get('llm_provider')}")
print(f"   AFTER override - deep_think_llm: {config.get('deep_think_llm')}")
print(f"   AFTER override - quick_think_llm: {config.get('quick_think_llm')}")

# Try to create TradingAgentsGraph
print("\n4. Creating TradingAgentsGraph:")
try:
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    
    # Enable debug
    os.environ['DEBUG_CONFIG'] = '1'
    
    ta = TradingAgentsGraph(debug=True, config=config)
    
    print("\n✅ TradingAgentsGraph created successfully")
    print(f"   Using provider: {ta.config.get('llm_provider')}")
    print(f"   Using deep model: {ta.config.get('deep_think_llm')}")
    print(f"   Using quick model: {ta.config.get('quick_think_llm')}")
    
except Exception as e:
    print(f"\n❌ Failed to create TradingAgentsGraph: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("DEBUG TEST COMPLETE")
print("="*80)
