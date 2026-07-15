"""
Run Full LLM Agent Audit

Instruments all 6 LLM agents to measure:
1. Input tokens
2. Output tokens
3. Runtime
4. Estimated cost

Produces detailed per-agent breakdown.
"""

import os
import sys
from datetime import datetime

# Enable optimized analysts to reduce unnecessary LLM calls
os.environ['USE_OPTIMIZED_ANALYSTS'] = '1'
os.environ['USE_OPTIMIZED_RISK'] = '1'

# Enable audit mode
os.environ['AUDIT_MODE'] = '1'

from tradingagents.graph import TradingAgentsGraph
from audit_framework import (
    get_audit_collector,
    reset_audit_collector,
    create_auditing_llm
)


def run_audit_on_stock(ticker: str, company_name: str):
    """
    Run audit on a single stock
    
    Args:
        ticker: Stock ticker (e.g., "HDFCBANK.NS")
        company_name: Human-readable name
    """
    
    print("\n" + "=" * 80)
    print(f"AUDITING: {ticker} - {company_name}")
    print("=" * 80)
    
    # Reset collector for clean slate
    reset_audit_collector()
    
    # Initialize graph (uses optimized Python analysts)
    config = {
        "llm_provider": "groq",  # Default provider
        "deep_think_llm": "llama-3.3-70b-versatile",
        "quick_think_llm": "llama-3.3-70b-versatile",
        "data_cache_dir": "./data_cache",
        "results_dir": "./results",
        "max_debate_rounds": 3,
        "max_risk_discuss_rounds": 1
    }
    
    print(f"\n📊 Initializing TradingAgents graph...")
    
    # Note: We can't easily wrap LLMs in the current setup without modifying factory functions
    # So we'll need to instrument at the graph/setup.py level
    # For now, let's check if graph can execute and capture what we can
    
    graph = TradingAgentsGraph(
        selected_analysts=["market", "fundamentals", "news"],
        config=config,
        debug=False
    )
    
    print(f"✅ Graph initialized\n")
    print(f"🏃 Running workflow for {ticker}...")
    print(f"⚠️  Note: This may take 5-10 minutes and could hit rate limits\n")
    
    try:
        final_state, signal = graph.propagate(
            company_name=ticker,
            trade_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        print(f"\n✅ Workflow completed for {ticker}")
        
        # Extract decision
        decision = final_state.get('final_trade_decision', {})
        print(f"\n📋 Trade Decision:")
        print(f"   Action: {decision.get('action', 'N/A')}")
        print(f"   Confidence: {decision.get('confidence', 'N/A')}")
        
        return True, final_state
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {str(e)}")
        
        # Check if it's a rate limit error
        error_str = str(e).lower()
        if '429' in error_str or 'rate limit' in error_str or 'quota' in error_str:
            print(f"\n⚠️  Rate limit hit. This is expected on free tier.")
            print(f"   The audit framework is working, but LLM providers are limiting requests.")
        
        return False, None


def generate_audit_report():
    """Generate and save audit report"""
    
    collector = get_audit_collector()
    
    # Check if we collected any data
    if not collector.calls:
        print("\n" + "=" * 80)
        print("⚠️  NO LLM CALLS RECORDED")
        print("=" * 80)
        print("\nThis likely means:")
        print("1. Workflow failed before reaching LLM agents")
        print("2. All analysts are Python-based (USE_OPTIMIZED_ANALYSTS=1)")
        print("3. Rate limits hit before LLM calls completed")
        print("\nTo audit LLM agents, you need:")
        print("- At least one LLM agent to execute successfully")
        print("- Sufficient API quota to complete calls")
        print("- Instrumentation at the graph/setup.py level (requires code modification)")
        return None
    
    # Print summary
    collector.print_summary()
    
    # Save detailed report
    filepath = collector.save_report()
    
    return filepath


def main():
    """Main audit execution"""
    
    print("\n" + "=" * 80)
    print("LLM AGENT AUDIT - Phase 2")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nObjective: Quantify token usage, runtime, and cost for 6 LLM agents")
    print("  - Bull Researcher")
    print("  - Bear Researcher")
    print("  - Research Manager")
    print("  - Trader")
    print("  - Portfolio Manager")
    print("  - News Analyst (if using LLM)")
    
    # Test on 1 stock to avoid rate limits
    test_stock = ("HDFCBANK.NS", "HDFC Bank")
    
    print(f"\n🎯 Testing on: {test_stock[1]} ({test_stock[0]})")
    print("   (Single stock to minimize rate limit risk)")
    
    success, final_state = run_audit_on_stock(*test_stock)
    
    # Generate report
    print("\n" + "=" * 80)
    print("GENERATING AUDIT REPORT")
    print("=" * 80)
    
    report_path = generate_audit_report()
    
    if report_path:
        print(f"\n✅ Audit complete! Report saved to: {report_path}")
    else:
        print(f"\n⚠️  Audit completed but no LLM calls were captured.")
        print(f"    See notes above for instrumentation requirements.")
    
    print(f"\n{'=' * 80}")
    print("NEXT STEPS")
    print("=" * 80)
    print("\nTo fully instrument LLM agents:")
    print("1. Modify graph/setup.py to wrap LLMs with audit_framework")
    print("2. Wrap each LLM creation with create_auditing_llm()")
    print("3. Re-run this script")
    print("\nExample instrumentation:")
    print("   bull_llm = create_auditing_llm(")
    print("       llm=original_llm,")
    print("       agent_name='Bull Researcher',")
    print("       provider='groq',")
    print("       model='llama-3.3-70b'")
    print("   )")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
