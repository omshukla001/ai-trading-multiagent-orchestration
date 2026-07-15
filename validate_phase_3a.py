"""
Phase 3A Validation Script

Tests low-risk optimizations:
1. Debate rounds (3 → 2)
2. Output token limits (Bull/Bear 800, Manager 900, Trader 600, PM 500)
3. Prompt verbosity reduction

Compares before vs after on 3 stocks:
- HDFCBANK.NS
- INFY.NS
- RELIANCE.NS

Metrics tracked:
- Runtime
- Input tokens (estimated)
- Output tokens (estimated)
- Cost (estimated)
- Recommendation quality

NOTE: This requires the optimizations to already be implemented in the code.
The "before" baseline is from Phase 2 theoretical estimates.
"""

import os
import sys
import time
from datetime import datetime

# Enable optimized analysts and risk engine
os.environ['USE_OPTIMIZED_ANALYSTS'] = '1'
os.environ['USE_OPTIMIZED_RISK'] = '1'

# Enable audit mode to track metrics
os.environ['AUDIT_MODE'] = '1'

from tradingagents.graph import TradingAgentsGraph
from audit_framework import get_audit_collector, reset_audit_collector


# Baseline estimates from Phase 2
BASELINE_PER_STOCK = {
    'total_tokens': 56000,  # Mid-range estimate
    'input_tokens': 47000,
    'output_tokens': 9000,
    'total_cost': 0.0331,
    'runtime': 101,  # seconds
}

# Expected after Phase 3A
EXPECTED_AFTER_3A = {
    'total_tokens': 36000,  # ~36% reduction
    'input_tokens': 27000,
    'output_tokens': 6000,
    'total_cost': 0.021,  # ~37% reduction
    'runtime': 67,  # seconds (~34% reduction)
}


def run_stock_test(ticker: str, company_name: str):
    """Run workflow on a single stock and collect metrics"""
    
    print(f"\n{'─' * 80}")
    print(f"Testing: {ticker} - {company_name}")
    print('─' * 80)
    
    # Reset collector for clean metrics
    reset_audit_collector()
    
    # Initialize graph with default config (which now has max_debate_rounds=2)
    config = {
        "llm_provider": "groq",
        "deep_think_llm": "llama-3.3-70b-versatile",
        "quick_think_llm": "llama-3.3-70b-versatile",
        "data_cache_dir": "./data_cache",
        "results_dir": "./results",
        "max_debate_rounds": 2,  # Phase 3A optimization
        "max_risk_discuss_rounds": 1
    }
    
    print(f"  Config: {config['max_debate_rounds']} debate rounds")
    print(f"  Optimizations: Prompt verbosity reduced, output limits added")
    
    graph = TradingAgentsGraph(
        selected_analysts=["market", "fundamentals", "news"],
        config=config,
        debug=False
    )
    
    try:
        start_time = time.time()
        
        final_state, signal = graph.propagate(
            company_name=ticker,
            trade_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        runtime = time.time() - start_time
        
        # Extract decision
        decision = final_state.get('final_trade_decision', {})
        
        # Get audit metrics
        collector = get_audit_collector()
        summary = collector.get_summary() if collector.calls else None
        
        result = {
            'ticker': ticker,
            'success': True,
            'runtime': round(runtime, 1),
            'action': decision.get('action', 'N/A'),
            'confidence': decision.get('confidence', 'N/A'),
            'audit_summary': summary
        }
        
        print(f"  ✅ Success: {result['action']} ({result['runtime']}s)")
        
        return result
        
    except Exception as e:
        error_str = str(e)
        print(f"  ❌ Failed: {error_str[:100]}")
        
        if '429' in error_str.lower() or 'rate limit' in error_str.lower():
            print(f"  ⚠️  Rate limit hit - Expected on free tier")
        
        return {
            'ticker': ticker,
            'success': False,
            'error': error_str,
            'runtime': 0
        }


def print_comparison(results: list):
    """Print before/after comparison"""
    
    print("\n" + "=" * 80)
    print("PHASE 3A VALIDATION RESULTS")
    print("=" * 80)
    
    successful = [r for r in results if r.get('success')]
    
    if not successful:
        print("\n⚠️  No successful runs to analyze")
        print("   This is likely due to rate limits on free tier")
        print("   Optimizations are implemented but cannot be validated yet")
        return
    
    # Calculate averages
    avg_runtime = sum(r['runtime'] for r in successful) / len(successful)
    
    # Get audit data if available
    has_audit = any(r.get('audit_summary') for r in successful)
    
    if has_audit:
        # Calculate token metrics from audit data
        total_tokens = 0
        total_cost = 0
        for r in successful:
            if r.get('audit_summary'):
                total_tokens += r['audit_summary'].get('total_tokens', 0)
                total_cost += r['audit_summary'].get('total_cost', 0)
        
        avg_tokens = total_tokens / len(successful) if successful else 0
        avg_cost = total_cost / len(successful) if successful else 0
        
        print(f"\n📊 Performance Metrics (Average per stock):")
        print(f"\n   Metric              Baseline    Optimized    Change")
        print(f"   {'─' * 60}")
        print(f"   Total Tokens        {BASELINE_PER_STOCK['total_tokens']:,}       {int(avg_tokens):,}      {((avg_tokens - BASELINE_PER_STOCK['total_tokens']) / BASELINE_PER_STOCK['total_tokens'] * 100):+.1f}%")
        print(f"   Cost                ${BASELINE_PER_STOCK['total_cost']:.4f}     ${avg_cost:.4f}    {((avg_cost - BASELINE_PER_STOCK['total_cost']) / BASELINE_PER_STOCK['total_cost'] * 100):+.1f}%")
        print(f"   Runtime             {BASELINE_PER_STOCK['runtime']}s          {int(avg_runtime)}s        {((avg_runtime - BASELINE_PER_STOCK['runtime']) / BASELINE_PER_STOCK['runtime'] * 100):+.1f}%")
    else:
        print(f"\n📊 Performance Metrics:")
        print(f"   Average Runtime: {avg_runtime:.1f}s")
        print(f"   Baseline Runtime: {BASELINE_PER_STOCK['runtime']}s")
        print(f"   Improvement: {((avg_runtime - BASELINE_PER_STOCK['runtime']) / BASELINE_PER_STOCK['runtime'] * 100):+.1f}%")
    
    print(f"\n📋 Recommendations:")
    for r in successful:
        print(f"   {r['ticker']:15} → {r['action']:10} (Confidence: {r.get('confidence', 'N/A')})")
    
    print(f"\n✅ Success Rate: {len(successful)}/{len(results)} stocks")
    
    # Compare with expected
    if has_audit and avg_tokens > 0:
        print(f"\n🎯 Target Achievement:")
        expected_reduction = ((BASELINE_PER_STOCK['total_tokens'] - EXPECTED_AFTER_3A['total_tokens']) / 
                             BASELINE_PER_STOCK['total_tokens'] * 100)
        actual_reduction = ((BASELINE_PER_STOCK['total_tokens'] - avg_tokens) / 
                           BASELINE_PER_STOCK['total_tokens'] * 100)
        
        print(f"   Expected token reduction: {expected_reduction:.1f}%")
        print(f"   Actual token reduction:   {actual_reduction:.1f}%")
        
        if actual_reduction >= expected_reduction * 0.8:  # 80% of target
            print(f"   ✅ Target achieved!")
        else:
            print(f"   ⚠️  Below target (need {expected_reduction:.1f}%, got {actual_reduction:.1f}%)")


def main():
    """Run validation on 3 stocks"""
    
    print("=" * 80)
    print("PHASE 3A VALIDATION - LOW-RISK OPTIMIZATIONS")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n📋 Optimizations Applied:")
    print("   1. Debate rounds: 3 → 2")
    print("   2. Output token limits: Bull/Bear 800, Manager 900, Trader 600, PM 500")
    print("   3. Prompt verbosity: Reduced by ~70-80%")
    
    print("\n📊 Expected Impact:")
    print(f"   Token reduction: ~36% ({BASELINE_PER_STOCK['total_tokens']:,} → {EXPECTED_AFTER_3A['total_tokens']:,})")
    print(f"   Cost reduction: ~37% (${BASELINE_PER_STOCK['total_cost']:.4f} → ${EXPECTED_AFTER_3A['total_cost']:.4f})")
    print(f"   Runtime improvement: ~34% ({BASELINE_PER_STOCK['runtime']}s → {EXPECTED_AFTER_3A['runtime']}s)")
    
    # Test stocks
    test_stocks = [
        ("HDFCBANK.NS", "HDFC Bank"),
        ("INFY.NS", "Infosys"),
        ("RELIANCE.NS", "Reliance Industries")
    ]
    
    print(f"\n🎯 Test Set: {len(test_stocks)} NSE stocks")
    for ticker, name in test_stocks:
        print(f"   • {ticker} - {name}")
    
    results = []
    
    for ticker, name in test_stocks:
        result = run_stock_test(ticker, name)
        results.append(result)
        
        # Wait between stocks to avoid rate limits
        if ticker != test_stocks[-1][0]:
            print("\n⏳ Waiting 60s to avoid rate limits...")
            time.sleep(60)
    
    # Print comparison
    print_comparison(results)
    
    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    print(f"Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Save audit report if we have data
    collector = get_audit_collector()
    if collector.calls:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = collector.save_report(f"phase_3a_validation_{timestamp}.json")
        print(f"\n📁 Detailed audit saved to: {filepath}")
    
    return len([r for r in results if r.get('success')]) > 0


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Validation crashed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
