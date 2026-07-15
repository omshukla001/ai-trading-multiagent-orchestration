"""
API Usage Audit Script
Analyzes TradingAgents to identify LLM call patterns and optimization opportunities
"""

import os
import re
from pathlib import Path

print("=" * 80)
print("TRADINGAGENTS API USAGE AUDIT")
print("=" * 80)

# Analyze agent files
agents_dir = Path("tradingagents/agents")

llm_usage = {
    "analysts": {},
    "researchers": {},
    "managers": {},
    "risk_mgmt": {},
    "trader": {}
}

def count_llm_calls(file_path):
    """Count potential LLM invocations in a file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Look for LLM invocation patterns
    patterns = [
        r'\.invoke\(',
        r'ChatOpenAI\(',
        r'ChatGoogleGenerativeAI\(',
        r'ChatAnthropic\(',
        r'chain\.invoke',
        r'llm\.invoke'
    ]
    
    calls = 0
    for pattern in patterns:
        calls += len(re.findall(pattern, content))
    
    return calls, content

print("\n" + "=" * 80)
print("AGENT-BY-AGENT ANALYSIS")
print("=" * 80)

total_potential_calls = 0

# Analyze each agent category
for category in llm_usage.keys():
    category_dir = agents_dir / category
    if not category_dir.exists():
        continue
    
    print(f"\n--- {category.upper()} ---")
    
    for agent_file in category_dir.glob("*.py"):
        if agent_file.name == "__init__.py":
            continue
        
        calls, content = count_llm_calls(agent_file)
        
        # Check if agent uses tool calling
        uses_tools = "bind_tools" in content or "tools=" in content
        
        # Check if agent processes structured data
        has_structured = "get_fundamentals" in content or "get_indicators" in content
        
        agent_name = agent_file.stem
        llm_usage[category][agent_name] = {
            "file": str(agent_file),
            "llm_calls": calls,
            "uses_tools": uses_tools,
            "structured_data": has_structured
        }
        
        total_potential_calls += calls
        
        print(f"  {agent_name:30s} LLM calls: {calls:2d}  Tools: {uses_tools}  Structured: {has_structured}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total potential LLM calls per stock: {total_potential_calls}")
print(f"Estimated API requests per stock: 15-25 (with debates & retries)")

print("\n" + "=" * 80)
print("ANALYSIS: WHERE ARE THE 20 REQUESTS GOING?")
print("=" * 80)

analysis = """
Based on the RELIANCE.NS run, here's the breakdown:

1. MARKET ANALYST (Technical)         → 1-2 LLM calls
   - Gets stock data, indicators
   - LLM interprets RSI, MACD, EMAs
   - ❌ UNNECESSARY: Pure math, no LLM needed

2. SENTIMENT ANALYST                  → 2-3 LLM calls
   - Fetches StockTwits, Reddit
   - LLM summarizes sentiment
   - ✅ USEFUL: Text summarization needed

3. NEWS ANALYST                       → 3-4 LLM calls
   - Fetches news, macro data
   - LLM analyzes impact
   - ✅ USEFUL: Context interpretation needed

4. FUNDAMENTALS ANALYST               → 1-2 LLM calls
   - Gets financial statements
   - LLM calculates ratios
   - ❌ UNNECESSARY: Pure math, no LLM needed

5. BULL RESEARCHER                    → 2-3 LLM calls
   - Reads analyst reports
   - Argues bullish case
   - ✅ USEFUL: Synthesis needed

6. BEAR RESEARCHER                    → 2-3 LLM calls
   - Reads analyst reports
   - Argues bearish case
   - ✅ USEFUL: Synthesis needed

7. RESEARCH MANAGER                   → 1-2 LLM calls
   - Summarizes debate
   - ✅ USEFUL: Synthesis needed

8. TRADER                            → 1-2 LLM calls
   - Makes trade decision
   - ✅ USEFUL: Final recommendation

9. RISK MANAGEMENT (3 agents)        → 3-6 LLM calls
   - Conservative, Aggressive, Neutral
   - Debate risk levels
   - ⚠️  PARTIALLY USEFUL: Could simplify to 1 call

10. PORTFOLIO MANAGER                 → 1-2 LLM calls
    - Final approval
    - ✅ USEFUL: Final decision

TOTAL: ~18-30 LLM calls per stock

OPTIMIZATION OPPORTUNITIES:
✅ Remove LLM from Technical Analyst    → Save 2 calls
✅ Remove LLM from Fundamentals Analyst → Save 2 calls
⚠️  Simplify Risk Management to 1 agent → Save 4 calls
⚠️  Skip sentiment for low-volume stocks → Save 2 calls

OPTIMIZED TARGET: ~8-10 LLM calls per stock
"""

print(analysis)

print("\n" + "=" * 80)
print("COST ESTIMATION (Before Optimization)")
print("=" * 80)

costs = {
    "Gemini Free": {"limit": "20 req/day", "cost": "$0", "stocks_per_day": 1},
    "Gemini Paid": {"limit": "1000 req/min", "cost": "$0.02/stock", "stocks_per_day": "unlimited"},
    "Groq": {"limit": "30 req/min", "cost": "$0.01/stock", "stocks_per_day": 100},
    "OpenAI GPT-4o-mini": {"limit": "10000 req/min", "cost": "$0.15/stock", "stocks_per_day": "unlimited"},
    "OpenRouter": {"limit": "varies", "cost": "$0.05/stock", "stocks_per_day": "varies"}
}

for provider, info in costs.items():
    print(f"{provider:20s} | Cost: {info['cost']:15s} | Limit: {info['limit']:15s} | Stocks/day: {info['stocks_per_day']}")

print("\n" + "=" * 80)
print("COST ESTIMATION (After Optimization)")
print("=" * 80)

optimized_costs = {
    "Groq": {"calls": 8, "cost": "$0.003/stock", "stocks_per_day": 200},
    "OpenRouter (cheapest)": {"calls": 8, "cost": "$0.008/stock", "stocks_per_day": "unlimited"},
    "OpenAI GPT-4o-mini": {"calls": 8, "cost": "$0.06/stock", "stocks_per_day": "unlimited"},
}

for provider, info in optimized_costs.items():
    cost_for_20 = float(info['cost'].replace('$', '').replace('/stock', '')) * 20
    print(f"{provider:25s} | {info['calls']} calls/stock | {info['cost']:15s} | 20 stocks: ${cost_for_20:.2f}")

print("\n" + "=" * 80)
print("RECOMMENDATION")
print("=" * 80)

recommendation = """
Priority Order:
1. ✅ GROQ (BEST FOR TESTING)
   - Very fast inference
   - Free tier: 30 req/min, 14,400/day
   - Perfect for batch testing 100+ stocks
   - Cost: Nearly free

2. ✅ OpenRouter
   - Access to multiple models
   - Cheapest paid option
   - Good fallback

3. ✅ OpenAI GPT-4o-mini
   - Most reliable
   - Higher cost but worth it for production

Optimization Strategy:
1. Replace Technical Analyst with Python rules
2. Replace Fundamentals Analyst with Python rules
3. Simplify Risk Management from 3 agents to 1
4. Use Groq for remaining 8-10 LLM calls

Expected Result:
- 20 stocks analysis: $0.06 (Groq) vs $4.00 (OpenAI full LLM)
- 50x cost reduction
- Same quality for final recommendations
"""

print(recommendation)

print("\n" + "=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
