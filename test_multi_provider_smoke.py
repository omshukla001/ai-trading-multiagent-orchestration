"""
Smoke Test - Multi-Provider Routing

Quick validation on 3 stocks:
- HDFCBANK.NS
- INFY.NS
- RELIANCE.NS

Validates:
1. Workflow executes end-to-end
2. Provider routing works
3. No crashes
4. Recommendations generated
"""

import os
import sys
import time
from datetime import datetime

# Enable multi-provider routing
os.environ['ENABLE_MULTI_PROVIDER'] = 'true'
os.environ['USE_OPTIMIZED_ANALYSTS'] = '1'
os.environ['USE_OPTIMIZED_RISK'] = '1'

from tradingagents.graph import TradingAgentsGraph
from tradingagents.llm_clients.provider_monitor import get_monitor


def smoke_test():
    """Run smoke test on 3 stocks"""
    
    print("=" * 80)
    print("SMOKE TEST - MULTI-PROVIDER ROUTING")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    stocks = [
        ("HDFCBANK.NS", "HDFC Bank"),
        ("INFY.NS", "Infosys"),
        ("RELIANCE.NS", "Reliance Industries")
    ]
    
    # Initialize graph
    config = {
        "llm_provider": "groq",  # Fallback default
        "deep_think_llm": "llama-3.3-70b-versatile",
        "quick_think_llm": "llama-3.3-70b-versatile",
        "data_cache_dir": "./data_cache",
        "results_dir": "./results",
        "max_debate_rounds": 3,
        "max_risk_discuss_rounds": 1
    }
    
    graph = TradingAgentsGraph(
        selected_analysts=["market", "fundamentals", "news"],
        config=config,
        debug=False
    )
    
    results = []
    
    for ticker, name in stocks:
        print(f"\n{'─' * 80}")
        print(f"Testing: {ticker} - {name}")
        print('─' * 80)
        
        try:
            start = time.time()
            
            final_state, signal = graph.propagate(
                company_name=ticker,
                trade_date=datetime.now().strftime("%Y-%m-%d")
            )
            
            runtime = time.time() - start
            
            # Extract decision
            decision = final_state.get('final_trade_decision', {})
            
            result = {
                'ticker': ticker,
                'action': decision.get('action', 'N/A'),
                'runtime': round(runtime, 1),
                'success': True
            }
            
            print(f"  ✅ {ticker}: {result['action']} ({result['runtime']}s)")
            
            results.append(result)
            
        except Exception as e:
            print(f"  ❌ {ticker}: FAILED - {str(e)}")
            results.append({
                'ticker': ticker,
                'success': False,
                'error': str(e)
            })
    
    # Print summary
    print("\n" + "=" * 80)
    print("SMOKE TEST RESULTS")
    print("=" * 80)
    
    successful = sum(1 for r in results if r.get('success'))
    print(f"\nSuccess Rate: {successful}/{len(stocks)}")
    
    for r in results:
        status = "✅" if r.get('success') else "❌"
        print(f"{status} {r['ticker']}: {r.get('action', 'FAILED')}")
    
    # Show provider metrics
    monitor = get_monitor()
    monitor.print_summary()
    monitor.save_metrics("smoke_test_metrics.json")
    
    return successful == len(stocks)


if __name__ == "__main__":
    try:
        success = smoke_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Smoke test crashed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
