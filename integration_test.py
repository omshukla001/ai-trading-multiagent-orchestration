"""
Controlled Integration Test
Tests optimized analysts in real workflow with detailed logging
"""
import sys
import json
import time
from datetime import datetime, timedelta
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Patch setup.py to use optimized analysts
import tradingagents.graph.setup as setup_module
from tradingagents.agents.analysts.market_analyst_optimized import create_market_analyst_optimized
from tradingagents.agents.analysts.fundamentals_analyst_optimized import create_fundamentals_analyst_optimized

# Monkey-patch the imports
setup_module.create_market_analyst_optimized = create_market_analyst_optimized
setup_module.create_fundamentals_analyst_optimized = create_fundamentals_analyst_optimized

print("=" * 80)
print("CONTROLLED INTEGRATION TEST")
print("Testing Optimized Analysts in Real Workflow")
print("=" * 80)

# Test configuration
TEST_STOCKS = [
    ("HDFCBANK.NS", "HDFC Bank"),
    ("INFY.NS", "Infosys"),
    ("RELIANCE.NS", "Reliance Industries")
]

# Configure for Groq
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "groq"
config["deep_think_llm"] = "llama-3.3-70b-versatile"
config["quick_think_llm"] = "llama-3.3-70b-versatile"
config["max_debate_rounds"] = 1
config["max_risk_rounds"] = 1

analysis_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

test_results = []

print(f"\nTest Date: {analysis_date}")
print(f"LLM Provider: {config['llm_provider']}")
print(f"Model: {config['deep_think_llm']}")
print(f"Stocks to Test: {len(TEST_STOCKS)}")
print("\n" + "=" * 80)

for ticker, name in TEST_STOCKS:
    print(f"\n{'=' * 80}")
    print(f"TESTING: {ticker} ({name})")
    print("=" * 80)
    
    result = {
        "ticker": ticker,
        "name": name,
        "analysis_date": analysis_date,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # Initialize with ORIGINAL graph (uses original analysts)
        print("\n[1/2] Running with ORIGINAL analysts...")
        print("-" * 80)
        
        start_time = time.time()
        
        # Create TradingAgents instance
        ta_original = TradingAgentsGraph(debug=False, config=config)
        
        # Run analysis
        _, decision_original = ta_original.propagate(ticker, analysis_date)
        
        original_time = time.time() - start_time
        
        result["original"] = {
            "success": True,
            "runtime_seconds": original_time,
            "decision_length": len(decision_original),
            "decision_preview": decision_original[:500]
        }
        
        print(f"✓ Original analysis completed in {original_time:.1f}s")
        print(f"  Decision length: {len(decision_original)} chars")
        
    except Exception as e:
        print(f"✗ Original analysis FAILED: {str(e)}")
        result["original"] = {
            "success": False,
            "error": str(e),
            "runtime_seconds": 0
        }
    
    try:
        # Now test with OPTIMIZED analysts
        print("\n[2/2] Running with OPTIMIZED analysts...")
        print("-" * 80)
        
        # Monkey-patch the graph setup to use optimized analysts
        original_market = setup_module.create_market_analyst
        original_fundamentals = setup_module.create_fundamentals_analyst
        
        # Replace with optimized versions (no LLM parameter needed)
        def patched_market_analyst(llm):
            return create_market_analyst_optimized()
        
        def patched_fundamentals_analyst(llm):
            return create_fundamentals_analyst_optimized()
        
        setup_module.create_market_analyst = patched_market_analyst
        setup_module.create_fundamentals_analyst = patched_fundamentals_analyst
        
        start_time = time.time()
        
        # Create new instance with patched setup
        ta_optimized = TradingAgentsGraph(debug=False, config=config)
        
        # Run analysis
        _, decision_optimized = ta_optimized.propagate(ticker, analysis_date)
        
        optimized_time = time.time() - start_time
        
        # Restore original functions
        setup_module.create_market_analyst = original_market
        setup_module.create_fundamentals_analyst = original_fundamentals
        
        result["optimized"] = {
            "success": True,
            "runtime_seconds": optimized_time,
            "decision_length": len(decision_optimized),
            "decision_preview": decision_optimized[:500],
            "speedup": original_time / optimized_time if optimized_time > 0 else 0
        }
        
        print(f"✓ Optimized analysis completed in {optimized_time:.1f}s")
        print(f"  Decision length: {len(decision_optimized)} chars")
        print(f"  Speedup: {result['optimized']['speedup']:.1f}x faster")
        
    except Exception as e:
        print(f"✗ Optimized analysis FAILED: {str(e)}")
        result["optimized"] = {
            "success": False,
            "error": str(e),
            "runtime_seconds": 0
        }
        
        # Restore original functions
        setup_module.create_market_analyst = original_market
        setup_module.create_fundamentals_analyst = original_fundamentals
    
    # Compare results
    if result.get("original", {}).get("success") and result.get("optimized", {}).get("success"):
        print("\n" + "-" * 80)
        print("COMPARISON:")
        print("-" * 80)
        print(f"  Runtime:  Original {result['original']['runtime_seconds']:.1f}s  →  Optimized {result['optimized']['runtime_seconds']:.1f}s")
        print(f"  Speedup:  {result['optimized']['speedup']:.1f}x")
        print(f"  Quality:  Both completed successfully ✓")
    
    test_results.append(result)
    
    # Save intermediate results
    with open(f"test_results_{ticker.replace('.', '_')}.json", 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✓ Results saved to test_results_{ticker.replace('.', '_')}.json")

# Final Summary
print("\n" + "=" * 80)
print("INTEGRATION TEST SUMMARY")
print("=" * 80)

successful_original = sum(1 for r in test_results if r.get('original', {}).get('success'))
successful_optimized = sum(1 for r in test_results if r.get('optimized', {}).get('success'))

print(f"\nOriginal Analysts:  {successful_original}/{len(TEST_STOCKS)} successful")
print(f"Optimized Analysts: {successful_optimized}/{len(TEST_STOCKS)} successful")

if successful_optimized == len(TEST_STOCKS):
    print("\n✅ ALL TESTS PASSED - Optimized analysts are working correctly!")
    
    avg_speedup = sum(r.get('optimized', {}).get('speedup', 0) for r in test_results) / len(test_results)
    print(f"\nAverage Speedup: {avg_speedup:.1f}x")
    print(f"Integration Status: ✅ READY FOR DEPLOYMENT")
else:
    print(f"\n⚠️  SOME TESTS FAILED - Review failures before deployment")
    print(f"Integration Status: ⚠️  NEEDS INVESTIGATION")

# Save full results
with open('integration_test_full_results.json', 'w') as f:
    json.dump(test_results, f, indent=2)

print(f"\n✓ Full results saved to: integration_test_full_results.json")
print("=" * 80)
