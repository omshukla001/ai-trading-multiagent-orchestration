"""
Research Layer Audit - Phase 2

Comprehensive audit of 6 LLM agents to quantify:
1. Input tokens per agent
2. Output tokens per agent  
3. Runtime per agent
4. Cost per agent

Strategy: Run on minimal test case to avoid rate limits,
then extrapolate to full production usage.
"""

import os
import sys
from datetime import datetime

# Enable audit mode
os.environ['AUDIT_MODE'] = '1'
os.environ['USE_OPTIMIZED_ANALYSTS'] = '1'
os.environ['USE_OPTIMIZED_RISK'] = '1'

from tradingagents.graph import TradingAgentsGraph
from audit_framework import get_audit_collector, reset_audit_collector


def run_minimal_audit():
    """
    Run audit on 1 stock with minimal configuration
    Handles rate limits gracefully
    """
    
    print("\n" + "=" * 80)
    print("RESEARCH LAYER AUDIT - Phase 2")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n📊 Objective:")
    print("   Quantify token usage, runtime, and cost for 6 LLM agents:")
    print("   1. Bull Researcher")
    print("   2. Bear Researcher")
    print("   3. Research Manager")
    print("   4. Trader")
    print("   5. Portfolio Manager")
    print("   6. News Analyst (if using LLM)")
    
    # Reset collector
    reset_audit_collector()
    
    # Use single stock to minimize rate limit risk
    test_stock = "RELIANCE.NS"
    
    print(f"\n🎯 Test Stock: {test_stock}")
    print(f"   (Single stock to minimize API usage)")
    
    # Initialize graph
    config = {
        "llm_provider": "groq",
        "deep_think_llm": "llama-3.3-70b-versatile",
        "quick_think_llm": "llama-3.3-70b-versatile",
        "data_cache_dir": "./data_cache",
        "results_dir": "./results",
        "max_debate_rounds": 3,
        "max_risk_discuss_rounds": 1
    }
    
    print(f"\n🔧 Initializing graph with audit instrumentation...")
    
    try:
        graph = TradingAgentsGraph(
            selected_analysts=["market", "fundamentals", "news"],
            config=config,
            debug=False
        )
        print(f"✅ Graph initialized")
    except Exception as e:
        print(f"❌ Graph initialization failed: {str(e)}")
        return False
    
    print(f"\n🏃 Running workflow (this may take 5-10 minutes)...")
    print(f"⚠️  Note: May hit rate limits on free tier\n")
    
    success = False
    error_message = None
    
    try:
        final_state, signal = graph.propagate(
            company_name=test_stock,
            trade_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        print(f"\n✅ Workflow completed successfully!")
        
        # Extract decision
        decision = final_state.get('final_trade_decision', {})
        print(f"\n📋 Trade Decision for {test_stock}:")
        print(f"   Action: {decision.get('action', 'N/A')}")
        print(f"   Confidence: {decision.get('confidence', 'N/A')}")
        
        success = True
        
    except Exception as e:
        error_str = str(e)
        error_message = error_str
        
        print(f"\n❌ Workflow failed: {error_str[:200]}")
        
        # Check error type
        if '429' in error_str.lower() or 'rate limit' in error_str.lower():
            print(f"\n⚠️  Rate Limit Error Detected")
            print(f"   This is expected on free tier with heavy prompts")
            print(f"   Analyzing partial data collected before failure...")
        elif 'timeout' in error_str.lower():
            print(f"\n⚠️  Timeout Error")
            print(f"   Network or API timeout occurred")
        else:
            print(f"\n❌ Unexpected Error")
            print(f"   See full error above")
    
    # Generate report regardless of success
    print(f"\n" + "=" * 80)
    print("GENERATING AUDIT REPORT")
    print("=" * 80)
    
    collector = get_audit_collector()
    
    if not collector.calls:
        print(f"\n⚠️  NO LLM CALLS RECORDED")
        print(f"\nPossible reasons:")
        print(f"  1. Rate limit hit before any LLM agent executed")
        print(f"  2. All analysts are Python-based (optimized mode)")
        print(f"  3. Workflow failed in data collection phase")
        
        if error_message:
            print(f"\nError details: {error_message[:300]}")
        
        print(f"\n💡 Recommendation:")
        print(f"   Wait 1 hour for rate limits to reset, then retry")
        
        return False
    
    # Print summary
    collector.print_summary()
    
    # Save report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = collector.save_report(f"research_audit_{timestamp}.json")
    
    print(f"\n" + "=" * 80)
    print("AUDIT ANALYSIS")
    print("=" * 80)
    
    summary = collector.get_full_summary()
    
    # Identify bottlenecks
    print(f"\n🔥 Top 3 Cost Drivers:")
    for i, item in enumerate(summary['ranked_by_cost'][:3], 1):
        print(f"   {i}. {item['agent']:25} ${item['cost']:.4f} ({item['percentage_of_total_cost']}%)")
    
    print(f"\n🎫 Top 3 Token Consumers:")
    for i, item in enumerate(summary['ranked_by_tokens'][:3], 1):
        print(f"   {i}. {item['agent']:25} {item['tokens']:,} tokens ({item['percentage_of_total_tokens']}%)")
    
    print(f"\n⏱️  Top 3 Runtime Bottlenecks:")
    for i, item in enumerate(summary['ranked_by_runtime'][:3], 1):
        print(f"   {i}. {item['agent']:25} {item['runtime']:.2f}s ({item['percentage_of_total_runtime']}%)")
    
    # Optimization recommendations
    print(f"\n" + "=" * 80)
    print("OPTIMIZATION RECOMMENDATIONS")
    print("=" * 80)
    
    # Analyze top cost driver
    if summary['ranked_by_cost']:
        top_cost_agent = summary['ranked_by_cost'][0]
        print(f"\n💡 Highest Cost Agent: {top_cost_agent['agent']}")
        print(f"   Cost: ${top_cost_agent['cost']:.4f}")
        print(f"   Percentage of total: {top_cost_agent['percentage_of_total_cost']}%")
        
        agent_stats = summary['per_agent'][top_cost_agent['agent']]
        print(f"   Average tokens per call: {agent_stats['avg_tokens_per_call']:.0f}")
        
        print(f"\n   Recommendations:")
        print(f"   • Consider prompt optimization to reduce token usage")
        print(f"   • Evaluate if full analysis depth is necessary")
        print(f"   • Consider caching if agent is called multiple times")
    
    # Check for imbalanced usage
    costs = [item['cost'] for item in summary['ranked_by_cost']]
    if costs:
        max_cost = costs[0]
        min_cost = costs[-1]
        if min_cost > 0 and (max_cost / min_cost) > 3:
            print(f"\n⚠️  Cost Imbalance Detected:")
            print(f"   Highest cost is {max_cost/min_cost:.1f}x the lowest")
            print(f"   Consider balancing workload across agents")
    
    print(f"\n✅ Audit complete!")
    print(f"   Report saved to: {filepath}")
    
    return True


if __name__ == "__main__":
    try:
        success = run_minimal_audit()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Audit crashed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
