#!/usr/bin/env python3
"""
Controlled Integration Testing for Optimized Analysts

This script performs controlled testing of optimized analysts within the real TradingAgents workflow.

IMPORTANT: This is a NON-DESTRUCTIVE test. It does NOT modify production files.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import traceback
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded environment from: {env_path}")
else:
    print(f"⚠️  No .env file found at: {env_path}")
    load_dotenv()

# Verify API keys (check for any available provider)
available_keys = []
if os.environ.get('ANTHROPIC_API_KEY'):
    available_keys.append('ANTHROPIC')
if os.environ.get('GOOGLE_API_KEY'):
    available_keys.append('GOOGLE')
if os.environ.get('GROQ_API_KEY'):
    available_keys.append('GROQ')
if os.environ.get('OPENAI_API_KEY'):
    available_keys.append('OPENAI')

if not available_keys:
    print("❌ No API keys found in environment")
    print("\nPlease ensure your .env file contains at least one of:")
    print("  ANTHROPIC_API_KEY=your_key_here")
    print("  GOOGLE_API_KEY=your_key_here")
    print("  GROQ_API_KEY=your_key_here")
    print("  OPENAI_API_KEY=your_key_here")
    sys.exit(1)
else:
    print(f"✅ API keys found: {', '.join(available_keys)}")


class ControlledIntegrationTester:
    """Controlled integration testing framework"""
    
    def __init__(self):
        self.test_stocks = ["HDFCBANK.NS", "INFY.NS", "RELIANCE.NS"]
        self.results = {
            "original": {},
            "optimized": {}
        }
        self.output_dir = Path("controlled_test_results")
        self.output_dir.mkdir(exist_ok=True)
        
    def setup_test_environment(self, use_optimized: bool) -> None:
        """Set up environment for testing"""
        mode = "optimized" if use_optimized else "original"
        print(f"\n{'='*60}")
        print(f"Setting up {mode.upper()} test environment")
        print(f"{'='*60}")
        
        # Set environment variable
        os.environ['USE_OPTIMIZED_ANALYSTS'] = '1' if use_optimized else '0'
        
        # Clear module cache for clean import
        modules_to_clear = [
            'tradingagents.graph.setup',
            'tradingagents.agents.analysts.market_analyst_optimized',
            'tradingagents.agents.analysts.fundamentals_analyst_optimized',
        ]
        
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
        
        print(f"✅ Environment configured for {mode} mode")
        
    def run_single_stock_test(self, ticker: str, use_optimized: bool) -> Dict[str, Any]:
        """Run a single stock test and capture metrics"""
        from datetime import datetime, timedelta
        
        mode = "optimized" if use_optimized else "original"
        print(f"\n{'='*60}")
        print(f"Testing {ticker} with {mode.upper()} analysts")
        print(f"{'='*60}")
        
        start_time = time.time()
        test_result = {
            "ticker": ticker,
            "mode": mode,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "runtime_seconds": 0,
            "error": None,
            "recommendation": None,
            "confidence": None,
            "api_calls": 0,
            "tokens_used": 0,
            "agents_executed": [],
            "analysis_quality": {},
        }
        
        try:
            # Import fresh modules
            from tradingagents.graph.trading_graph import TradingAgentsGraph
            from tradingagents.default_config import DEFAULT_CONFIG
            from datetime import datetime, timedelta
            
            # Configure with GROQ (has generous free tier limits) instead of Google (rate-limited)
            config = DEFAULT_CONFIG.copy()
            
            # DEBUG: Print DEFAULT_CONFIG values BEFORE override
            print(f"\n🔍 DEBUG - DEFAULT_CONFIG BEFORE override:")
            print(f"   llm_provider: {config.get('llm_provider')}")
            print(f"   deep_think_llm: {config.get('deep_think_llm')}")
            print(f"   quick_think_llm: {config.get('quick_think_llm')}")
            
            config["llm_provider"] = "groq"
            config["deep_think_llm"] = "llama-3.3-70b-versatile"
            config["quick_think_llm"] = "llama-3.3-70b-versatile"
            config["max_debate_rounds"] = 1
            config["max_risk_rounds"] = 1
            
            # DEBUG: Print config values AFTER override
            print(f"\n🔍 DEBUG - Config AFTER override:")
            print(f"   llm_provider: {config.get('llm_provider')}")
            print(f"   deep_think_llm: {config.get('deep_think_llm')}")
            print(f"   quick_think_llm: {config.get('quick_think_llm')}")
            
            # Use analysis date from 5 days ago (market data availability)
            analysis_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
            
            print(f"\n🔄 Creating TradingAgentsGraph for {ticker}...")
            print(f"   Analysis date: {analysis_date}")
            print(f"   Mode: {mode}")
            
            # Enable debug mode and DEBUG_CONFIG
            os.environ['DEBUG_CONFIG'] = '1'
            ta = TradingAgentsGraph(debug=True, config=config)
            
            print(f"🚀 Executing workflow...")
            
            # Run the propagation
            final_state, decision = ta.propagate(ticker, analysis_date)
            
            runtime = time.time() - start_time
            test_result["runtime_seconds"] = round(runtime, 2)
            
            # Extract results
            if decision:
                test_result["recommendation"] = str(decision.get("action", "UNKNOWN"))
                test_result["confidence"] = decision.get("confidence", 0)
                test_result["analysis_quality"]["decision"] = decision
            
            # Extract signals from final state
            if final_state and isinstance(final_state, dict):
                # Extract analyst signals
                signals = final_state.get("analyst_signals", [])
                test_result["analysis_quality"]["analyst_signals_count"] = len(signals)
                if signals:
                    test_result["analysis_quality"]["signals"] = [
                        {
                            "analyst": s.get("analyst", "unknown"),
                            "signal": s.get("signal", "unknown"),
                            "confidence": s.get("confidence", 0)
                        }
                        for s in signals[:5]  # First 5 signals only
                    ]
                
                # Extract research reports
                reports = final_state.get("research_reports", [])
                test_result["analysis_quality"]["research_reports_count"] = len(reports)
                
                # Extract risk analyses
                risks = final_state.get("risk_analyses", [])
                test_result["analysis_quality"]["risk_analyses_count"] = len(risks)
                
                # Track agents executed
                if "messages" in final_state:
                    messages = final_state["messages"]
                    for msg in messages:
                        if hasattr(msg, 'name') and msg.name:
                            if msg.name not in test_result["agents_executed"]:
                                test_result["agents_executed"].append(msg.name)
            
            test_result["success"] = True
            print(f"\n✅ Test PASSED for {ticker} ({mode})")
            print(f"   Runtime: {runtime:.2f}s")
            print(f"   Recommendation: {test_result['recommendation']}")
            print(f"   Confidence: {test_result['confidence']}")
            
        except Exception as e:
            runtime = time.time() - start_time
            test_result["runtime_seconds"] = round(runtime, 2)
            test_result["success"] = False
            test_result["error"] = str(e)
            test_result["traceback"] = traceback.format_exc()
            
            print(f"\n❌ Test FAILED for {ticker} ({mode})")
            print(f"   Error: {str(e)}")
            print(f"   Runtime: {runtime:.2f}s")
        
        return test_result
    
    def run_all_tests(self) -> None:
        """Run complete test suite"""
        print("\n" + "="*80)
        print("CONTROLLED INTEGRATION TESTING - OPTIMIZED ANALYSTS")
        print("="*80)
        print(f"\nTest Suite: {len(self.test_stocks)} stocks × 2 modes = {len(self.test_stocks) * 2} total tests")
        print(f"Stocks: {', '.join(self.test_stocks)}")
        print(f"Modes: ORIGINAL (baseline) → OPTIMIZED (test)")
        print("\n" + "="*80)
        
        # PHASE 1: Run original workflow (baseline)
        print("\n" + "🔵"*40)
        print("PHASE 1: BASELINE - Testing ORIGINAL workflow")
        print("🔵"*40)
        
        self.setup_test_environment(use_optimized=False)
        
        for ticker in self.test_stocks:
            result = self.run_single_stock_test(ticker, use_optimized=False)
            self.results["original"][ticker] = result
            
            # Save intermediate results
            self.save_results()
            
            # Brief pause between tests
            time.sleep(2)
        
        # PHASE 2: Run optimized workflow (test)
        print("\n" + "🟢"*40)
        print("PHASE 2: TEST - Testing OPTIMIZED workflow")
        print("🟢"*40)
        
        self.setup_test_environment(use_optimized=True)
        
        for ticker in self.test_stocks:
            result = self.run_single_stock_test(ticker, use_optimized=True)
            self.results["optimized"][ticker] = result
            
            # Save intermediate results
            self.save_results()
            
            # Brief pause between tests
            time.sleep(2)
        
        # PHASE 3: Compare and analyze
        print("\n" + "📊"*40)
        print("PHASE 3: COMPARISON & ANALYSIS")
        print("📊"*40)
        
        self.compare_results()
        self.generate_report()
    
    def compare_results(self) -> None:
        """Compare original vs optimized results"""
        print("\n" + "="*80)
        print("COMPARISON: ORIGINAL vs OPTIMIZED")
        print("="*80)
        
        for ticker in self.test_stocks:
            orig = self.results["original"].get(ticker, {})
            opt = self.results["optimized"].get(ticker, {})
            
            print(f"\n📈 {ticker}")
            print("-" * 60)
            
            # Success comparison
            orig_success = "✅" if orig.get("success") else "❌"
            opt_success = "✅" if opt.get("success") else "❌"
            print(f"  Success:         {orig_success} Original  |  {opt_success} Optimized")
            
            # Runtime comparison
            orig_time = orig.get("runtime_seconds", 0)
            opt_time = opt.get("runtime_seconds", 0)
            if orig_time > 0:
                speedup = ((orig_time - opt_time) / orig_time * 100)
                print(f"  Runtime:         {orig_time:.2f}s Original  |  {opt_time:.2f}s Optimized  ({speedup:+.1f}%)")
            
            # Recommendation comparison
            orig_rec = orig.get("recommendation", "N/A")
            opt_rec = opt.get("recommendation", "N/A")
            match = "✅ MATCH" if orig_rec == opt_rec else "⚠️  DIFFERENT"
            print(f"  Recommendation:  {orig_rec} Original  |  {opt_rec} Optimized  {match}")
            
            # Confidence comparison
            orig_conf = orig.get("confidence", 0)
            opt_conf = opt.get("confidence", 0)
            if orig_conf and opt_conf:
                conf_diff = opt_conf - orig_conf
                print(f"  Confidence:      {orig_conf:.2f} Original  |  {opt_conf:.2f} Optimized  ({conf_diff:+.2f})")
            
            # Error comparison
            if not orig.get("success"):
                print(f"  ⚠️  Original Error: {orig.get('error', 'Unknown')}")
            if not opt.get("success"):
                print(f"  ⚠️  Optimized Error: {opt.get('error', 'Unknown')}")
    
    def save_results(self) -> None:
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"controlled_test_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
    
    def generate_report(self) -> None:
        """Generate detailed analysis report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"INTEGRATION_TEST_REPORT_{timestamp}.md"
        
        with open(report_file, 'w') as f:
            f.write("# Controlled Integration Test Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            f.write("## Test Summary\n\n")
            
            # Count successes
            orig_success_count = sum(1 for r in self.results["original"].values() if r.get("success"))
            opt_success_count = sum(1 for r in self.results["optimized"].values() if r.get("success"))
            
            f.write(f"- **Test Stocks:** {', '.join(self.test_stocks)}\n")
            f.write(f"- **Original Success Rate:** {orig_success_count}/{len(self.test_stocks)}\n")
            f.write(f"- **Optimized Success Rate:** {opt_success_count}/{len(self.test_stocks)}\n\n")
            
            # Performance metrics
            f.write("## Performance Metrics\n\n")
            f.write("| Stock | Original Time | Optimized Time | Speedup |\n")
            f.write("|-------|---------------|----------------|----------|\n")
            
            total_orig_time = 0
            total_opt_time = 0
            
            for ticker in self.test_stocks:
                orig = self.results["original"].get(ticker, {})
                opt = self.results["optimized"].get(ticker, {})
                
                orig_time = orig.get("runtime_seconds", 0)
                opt_time = opt.get("runtime_seconds", 0)
                
                total_orig_time += orig_time
                total_opt_time += opt_time
                
                speedup = ((orig_time - opt_time) / orig_time * 100) if orig_time > 0 else 0
                
                f.write(f"| {ticker} | {orig_time:.2f}s | {opt_time:.2f}s | {speedup:+.1f}% |\n")
            
            f.write(f"| **TOTAL** | **{total_orig_time:.2f}s** | **{total_opt_time:.2f}s** | ")
            total_speedup = ((total_orig_time - total_opt_time) / total_orig_time * 100) if total_orig_time > 0 else 0
            f.write(f"**{total_speedup:+.1f}%** |\n\n")
            
            # Recommendation comparison
            f.write("## Recommendation Comparison\n\n")
            f.write("| Stock | Original | Optimized | Match |\n")
            f.write("|-------|----------|-----------|-------|\n")
            
            for ticker in self.test_stocks:
                orig = self.results["original"].get(ticker, {})
                opt = self.results["optimized"].get(ticker, {})
                
                orig_rec = orig.get("recommendation", "N/A")
                opt_rec = opt.get("recommendation", "N/A")
                
                match = "✅" if orig_rec == opt_rec else "⚠️"
                
                f.write(f"| {ticker} | {orig_rec} | {opt_rec} | {match} |\n")
            
            f.write("\n")
            
            # Detailed results
            f.write("## Detailed Test Results\n\n")
            
            for ticker in self.test_stocks:
                f.write(f"### {ticker}\n\n")
                
                f.write("#### Original Workflow\n\n")
                orig = self.results["original"].get(ticker, {})
                f.write(f"```json\n{json.dumps(orig, indent=2)}\n```\n\n")
                
                f.write("#### Optimized Workflow\n\n")
                opt = self.results["optimized"].get(ticker, {})
                f.write(f"```json\n{json.dumps(opt, indent=2)}\n```\n\n")
            
            # Failure analysis
            f.write("## Failure Analysis\n\n")
            
            failures = []
            for mode in ["original", "optimized"]:
                for ticker, result in self.results[mode].items():
                    if not result.get("success"):
                        failures.append({
                            "mode": mode,
                            "ticker": ticker,
                            "error": result.get("error"),
                            "traceback": result.get("traceback")
                        })
            
            if failures:
                for failure in failures:
                    f.write(f"### {failure['ticker']} - {failure['mode'].upper()}\n\n")
                    f.write(f"**Error:** {failure['error']}\n\n")
                    f.write(f"```\n{failure.get('traceback', 'N/A')}\n```\n\n")
            else:
                f.write("✅ No failures detected!\n\n")
            
            # Conclusion
            f.write("## Conclusion\n\n")
            
            if opt_success_count == len(self.test_stocks) and orig_success_count == len(self.test_stocks):
                f.write("✅ **All tests passed for both workflows!**\n\n")
                
                if total_speedup > 0:
                    f.write(f"🚀 **Performance Improvement:** {total_speedup:.1f}% faster\n\n")
                
                # Check recommendation consistency
                mismatches = sum(1 for ticker in self.test_stocks 
                               if self.results["original"][ticker].get("recommendation") != 
                                  self.results["optimized"][ticker].get("recommendation"))
                
                if mismatches == 0:
                    f.write("✅ **Recommendation Quality:** All recommendations match baseline\n\n")
                    f.write("### ✅ READY FOR PRODUCTION DEPLOYMENT\n\n")
                else:
                    f.write(f"⚠️  **Recommendation Quality:** {mismatches} mismatches detected\n\n")
                    f.write("### ⚠️  REQUIRES FURTHER INVESTIGATION\n\n")
            else:
                f.write("❌ **Some tests failed. Further investigation required.**\n\n")
                f.write("### ❌ NOT READY FOR PRODUCTION DEPLOYMENT\n\n")
        
        print(f"\n📝 Report generated: {report_file}")


def main():
    """Main execution"""
    print("\n" + "="*80)
    print("CONTROLLED INTEGRATION TESTING")
    print("="*80)
    print("\nThis script will:")
    print("1. Run ORIGINAL workflow on 3 stocks (baseline)")
    print("2. Run OPTIMIZED workflow on 3 stocks (test)")
    print("3. Compare results and generate detailed report")
    print("\nIMPORTANT: This test does NOT modify any production files.")
    print("="*80)
    print("\nStarting automated test suite...")
    print("="*80 + "\n")
    
    tester = ControlledIntegrationTester()
    
    try:
        tester.run_all_tests()
        
        print("\n" + "="*80)
        print("✅ CONTROLLED INTEGRATION TESTING COMPLETE")
        print("="*80)
        print(f"\nResults saved in: {tester.output_dir}")
        print("\nNext steps:")
        print("1. Review the detailed report")
        print("2. Compare original vs optimized outputs")
        print("3. Investigate any failures or mismatches")
        print("4. If all tests pass, proceed with production deployment")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
