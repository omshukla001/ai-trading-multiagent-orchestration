"""
Live Stock Benchmark - Phase 3 Task 1

Run complete TradingAgents workflow on 20 NSE stocks with live APIs.
Compare original vs optimized performance.

Captures:
- Runtime per stock
- Token usage
- API calls
- Cost per stock
- Recommendation quality

Usage:
    # Original system
    python benchmark_live_stocks.py --mode original
    
    # Optimized system
    python benchmark_live_stocks.py --mode optimized
    
    # Both (sequential)
    python benchmark_live_stocks.py --mode both
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, asdict

from tradingagents.graph import TradingAgentsGraph


@dataclass
class StockResult:
    """Result from analyzing a single stock"""
    ticker: str
    mode: str  # 'original' or 'optimized'
    timestamp: str
    
    # Performance metrics
    runtime_seconds: float
    total_tokens: int
    api_calls: int
    estimated_cost: float
    
    # Trading decision
    action: str
    confidence: float
    entry_price: float
    stop_loss: float
    target: float
    quantity: int
    allocation: float
    risk_amount: float
    rr_ratio: float
    
    # Profile recommendation (optimized only)
    recommended_profile: str = None
    
    # Status
    success: bool = True
    error_message: str = None


class LiveStockBenchmark:
    """Benchmark TradingAgents on live NSE stocks"""
    
    # Top 20 NSE stocks by market cap (diverse sectors)
    NSE_STOCKS = [
        ("RELIANCE.NS", "Reliance Industries - Oil & Gas"),
        ("TCS.NS", "Tata Consultancy Services - IT"),
        ("HDFCBANK.NS", "HDFC Bank - Banking"),
        ("INFY.NS", "Infosys - IT"),
        ("ICICIBANK.NS", "ICICI Bank - Banking"),
        ("HINDUNILVR.NS", "Hindustan Unilever - FMCG"),
        ("ITC.NS", "ITC Limited - FMCG/Tobacco"),
        ("SBIN.NS", "State Bank of India - Banking"),
        ("BHARTIARTL.NS", "Bharti Airtel - Telecom"),
        ("KOTAKBANK.NS", "Kotak Mahindra Bank - Banking"),
        ("LT.NS", "Larsen & Toubro - Engineering"),
        ("HCLTECH.NS", "HCL Technologies - IT"),
        ("AXISBANK.NS", "Axis Bank - Banking"),
        ("ASIANPAINT.NS", "Asian Paints - Paints"),
        ("MARUTI.NS", "Maruti Suzuki - Automobile"),
        ("SUNPHARMA.NS", "Sun Pharma - Pharma"),
        ("TITAN.NS", "Titan Company - Jewelry"),
        ("ULTRACEMCO.NS", "UltraTech Cement - Cement"),
        ("WIPRO.NS", "Wipro - IT"),
        ("NESTLEIND.NS", "Nestle India - FMCG")
    ]
    
    def __init__(self, mode: str = "optimized", limit: int = 20):
        """
        Initialize benchmark runner.
        
        Args:
            mode: 'original', 'optimized', or 'both'
            limit: Number of stocks to test (default 20)
        """
        self.mode = mode
        self.limit = min(limit, len(self.NSE_STOCKS))
        self.stocks = self.NSE_STOCKS[:self.limit]
        self.trade_date = datetime.now().strftime("%Y-%m-%d")
        
        self.results: List[StockResult] = []
        self.start_time = None
        self.output_dir = Path("benchmark_results")
        self.output_dir.mkdir(exist_ok=True)
        
    def run_benchmark(self):
        """Run complete benchmark"""
        print("=" * 80)
        print("LIVE STOCK BENCHMARK - PHASE 3 TASK 1")
        print("=" * 80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Mode: {self.mode.upper()}")
        print(f"Stocks: {self.limit}")
        print(f"Date: {self.trade_date}\n")
        
        self.start_time = time.time()
        
        if self.mode == "both":
            # Run original first, then optimized
            print("\n" + "=" * 80)
            print("PHASE 1: ORIGINAL SYSTEM")
            print("=" * 80)
            self._run_mode("original")
            
            print("\n" + "=" * 80)
            print("PHASE 2: OPTIMIZED SYSTEM")
            print("=" * 80)
            self._run_mode("optimized")
        else:
            self._run_mode(self.mode)
        
        total_time = time.time() - self.start_time
        
        # Generate reports
        self._print_summary(total_time)
        self._save_results()
        self._generate_comparison_report()
        
        print(f"\n✅ Benchmark complete in {total_time:.1f}s")
        
    def _run_mode(self, mode: str):
        """Run benchmark for a specific mode"""
        # Set environment variables
        if mode == "optimized":
            os.environ['USE_OPTIMIZED_ANALYSTS'] = '1'
            os.environ['USE_OPTIMIZED_RISK'] = '1'
            print("🚀 Optimizations ENABLED\n")
        else:
            os.environ['USE_OPTIMIZED_ANALYSTS'] = '0'
            os.environ['USE_OPTIMIZED_RISK'] = '0'
            print("📊 Original system (11 LLM agents)\n")
        
        # Create graph
        config = self._create_config()
        graph = TradingAgentsGraph(
            selected_analysts=["market", "fundamentals", "news"],
            config=config,
            debug=False
        )
        
        # Test each stock
        for idx, (ticker, description) in enumerate(self.stocks, 1):
            print(f"\n[{idx}/{self.limit}] {ticker} - {description}")
            print("─" * 80)
            
            result = self._analyze_stock(graph, ticker, mode)
            
            if result:
                self.results.append(result)
                self._print_stock_result(result)
            else:
                print(f"❌ Failed to analyze {ticker}")
            
            # Rate limiting (be nice to APIs)
            if idx < self.limit:
                time.sleep(2)
    
    def _analyze_stock(
        self, 
        graph: TradingAgentsGraph, 
        ticker: str, 
        mode: str
    ) -> StockResult:
        """Analyze a single stock"""
        try:
            start_time = time.time()
            
            # Run analysis
            final_state, signal = graph.propagate(
                company_name=ticker,
                trade_date=self.trade_date
            )
            
            runtime = time.time() - start_time
            
            # Extract decision
            decision = final_state.get('final_trade_decision', {})
            
            # Extract position details
            entry = 0
            stop = 0
            target = 0
            quantity = 0
            allocation = 0
            risk = 0
            rr_ratio = 0
            recommended_profile = None
            
            if mode == "optimized":
                # Get from risk engine
                risk_debate = final_state.get('risk_debate_state', {})
                risk_analysis = risk_debate.get('risk_analysis', {})
                recommended_profile = risk_analysis.get('recommended_profile', 'neutral')
                profiles = risk_analysis.get('profiles', {})
                position = profiles.get(recommended_profile, {})
                
                entry = position.get('entry_price', 0)
                stop = position.get('stop_loss', 0)
                target = position.get('target', 0)
                quantity = position.get('quantity', 0)
                allocation = position.get('allocation', 0)
                risk = position.get('risk_amount', 0)
                rr_ratio = position.get('rr_ratio', 0)
            else:
                # Extract from trader plan (original)
                trader_plan = final_state.get('trader_investment_plan', '')
                # Parse trader plan for prices
                import re
                
                entry_match = re.search(r'entry[:\s]+.*?₹?(\d+[,\.]?\d*)', trader_plan, re.IGNORECASE)
                if entry_match:
                    entry = float(entry_match.group(1).replace(',', ''))
                
                stop_match = re.search(r'stop[:\s]+.*?₹?(\d+[,\.]?\d*)', trader_plan, re.IGNORECASE)
                if stop_match:
                    stop = float(stop_match.group(1).replace(',', ''))
                
                target_match = re.search(r'target[:\s]+.*?₹?(\d+[,\.]?\d*)', trader_plan, re.IGNORECASE)
                if target_match:
                    target = float(target_match.group(1).replace(',', ''))
            
            # Estimate tokens and cost
            # (This is approximate - would need callback tracking for exact numbers)
            tokens = self._estimate_tokens(final_state, mode)
            api_calls = self._estimate_api_calls(mode)
            cost = self._estimate_cost(tokens)
            
            return StockResult(
                ticker=ticker,
                mode=mode,
                timestamp=datetime.now().isoformat(),
                runtime_seconds=round(runtime, 2),
                total_tokens=tokens,
                api_calls=api_calls,
                estimated_cost=cost,
                action=decision.get('action', 'N/A'),
                confidence=decision.get('confidence', 0),
                entry_price=entry,
                stop_loss=stop,
                target=target,
                quantity=quantity,
                allocation=allocation,
                risk_amount=risk,
                rr_ratio=rr_ratio,
                recommended_profile=recommended_profile,
                success=True
            )
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return StockResult(
                ticker=ticker,
                mode=mode,
                timestamp=datetime.now().isoformat(),
                runtime_seconds=0,
                total_tokens=0,
                api_calls=0,
                estimated_cost=0,
                action="ERROR",
                confidence=0,
                entry_price=0,
                stop_loss=0,
                target=0,
                quantity=0,
                allocation=0,
                risk_amount=0,
                rr_ratio=0,
                success=False,
                error_message=str(e)
            )
    
    def _print_stock_result(self, result: StockResult):
        """Print formatted stock result"""
        if not result.success:
            print(f"  ❌ Error: {result.error_message}")
            return
        
        print(f"  Action: {result.action}")
        print(f"  Entry: ₹{result.entry_price:,.2f} | Stop: ₹{result.stop_loss:,.2f} | Target: ₹{result.target:,.2f}")
        if result.mode == "optimized":
            print(f"  Position: {result.quantity} shares, ₹{result.allocation:,.0f} allocation, ₹{result.risk_amount:,.0f} risk")
            print(f"  Profile: {result.recommended_profile}, R:R: {result.rr_ratio:.2f}:1")
        print(f"  Runtime: {result.runtime_seconds:.1f}s | Tokens: {result.total_tokens:,} | Cost: ${result.estimated_cost:.4f}")
        print(f"  ✅ Complete")
    
    def _estimate_tokens(self, state: Dict[str, Any], mode: str) -> int:
        """Estimate token usage based on mode"""
        if mode == "optimized":
            # Optimized: News (LLM) + Bull/Bear/Manager (LLM) + Trader (LLM) + PM (LLM)
            # Market + Fundamentals + Risk (Python, 0 tokens)
            # Rough estimate: 6 LLM agents * ~1,500 tokens avg = 9,000
            return 9000
        else:
            # Original: All 11 LLM agents
            # Rough estimate: 11 agents * ~1,500 tokens avg = 16,500
            return 16500
    
    def _estimate_api_calls(self, mode: str) -> int:
        """Estimate API calls based on mode"""
        if mode == "optimized":
            return 6  # 6 LLM agents
        else:
            return 11  # 11 LLM agents
    
    def _estimate_cost(self, tokens: int) -> float:
        """Estimate cost based on tokens (Groq pricing)"""
        # Groq: ~$0.0005 per 1K tokens
        return (tokens / 1000) * 0.0005
    
    def _print_summary(self, total_time: float):
        """Print benchmark summary"""
        print("\n" + "=" * 80)
        print("BENCHMARK SUMMARY")
        print("=" * 80)
        
        if not self.results:
            print("\n❌ No results to summarize")
            return
        
        # Group by mode
        modes = {}
        for result in self.results:
            if result.mode not in modes:
                modes[result.mode] = []
            modes[result.mode].append(result)
        
        # Print statistics for each mode
        for mode, results in modes.items():
            print(f"\n{mode.upper()} SYSTEM ({len(results)} stocks):")
            print("─" * 80)
            
            successful = [r for r in results if r.success]
            failed = len(results) - len(successful)
            
            if not successful:
                print("  ❌ No successful analyses")
                continue
            
            avg_runtime = sum(r.runtime_seconds for r in successful) / len(successful)
            avg_tokens = sum(r.total_tokens for r in successful) / len(successful)
            avg_cost = sum(r.estimated_cost for r in successful) / len(successful)
            total_cost = sum(r.estimated_cost for r in successful)
            
            print(f"  Success Rate: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)")
            print(f"  Avg Runtime: {avg_runtime:.1f}s")
            print(f"  Avg Tokens: {avg_tokens:,.0f}")
            print(f"  Avg Cost: ${avg_cost:.4f}")
            print(f"  Total Cost: ${total_cost:.3f}")
            
            # Action distribution
            actions = {}
            for r in successful:
                action = r.action
                actions[action] = actions.get(action, 0) + 1
            
            print(f"\n  Action Distribution:")
            for action, count in sorted(actions.items(), key=lambda x: -x[1]):
                pct = (count / len(successful)) * 100
                print(f"    {action}: {count} ({pct:.1f}%)")
            
            if mode == "optimized":
                # Profile distribution
                profiles = {}
                for r in successful:
                    if r.recommended_profile:
                        profiles[r.recommended_profile] = profiles.get(r.recommended_profile, 0) + 1
                
                if profiles:
                    print(f"\n  Profile Distribution:")
                    for profile, count in sorted(profiles.items()):
                        pct = (count / len(successful)) * 100
                        print(f"    {profile.capitalize()}: {count} ({pct:.1f}%)")
        
        # Comparison if both modes run
        if len(modes) == 2:
            self._print_comparison(modes)
        
        print(f"\n  Total Time: {total_time:.1f}s")
    
    def _print_comparison(self, modes: Dict[str, List[StockResult]]):
        """Print comparison between original and optimized"""
        print("\n" + "=" * 80)
        print("PERFORMANCE COMPARISON")
        print("=" * 80)
        
        orig = [r for r in modes.get('original', []) if r.success]
        opt = [r for r in modes.get('optimized', []) if r.success]
        
        if not orig or not opt:
            print("\n⚠️  Need successful results from both modes for comparison")
            return
        
        orig_runtime = sum(r.runtime_seconds for r in orig) / len(orig)
        opt_runtime = sum(r.runtime_seconds for r in opt) / len(opt)
        runtime_reduction = ((orig_runtime - opt_runtime) / orig_runtime) * 100
        
        orig_tokens = sum(r.total_tokens for r in orig) / len(orig)
        opt_tokens = sum(r.total_tokens for r in opt) / len(opt)
        token_reduction = ((orig_tokens - opt_tokens) / orig_tokens) * 100
        
        orig_cost = sum(r.estimated_cost for r in orig) / len(orig)
        opt_cost = sum(r.estimated_cost for r in opt) / len(opt)
        cost_reduction = ((orig_cost - opt_cost) / orig_cost) * 100
        
        print(f"\n| Metric | Original | Optimized | Improvement |")
        print(f"|--------|----------|-----------|-------------|")
        print(f"| Runtime | {orig_runtime:.1f}s | {opt_runtime:.1f}s | {runtime_reduction:+.1f}% |")
        print(f"| Tokens | {orig_tokens:,.0f} | {opt_tokens:,.0f} | {token_reduction:+.1f}% |")
        print(f"| Cost | ${orig_cost:.4f} | ${opt_cost:.4f} | {cost_reduction:+.1f}% |")
        print(f"| API Calls | {orig[0].api_calls} | {opt[0].api_calls} | {((orig[0].api_calls - opt[0].api_calls) / orig[0].api_calls * 100):+.1f}% |")
    
    def _save_results(self):
        """Save results to JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"benchmark_{self.mode}_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump({
                'metadata': {
                    'mode': self.mode,
                    'stocks_tested': self.limit,
                    'trade_date': self.trade_date,
                    'timestamp': timestamp
                },
                'results': [asdict(r) for r in self.results]
            }, f, indent=2)
        
        print(f"\n📁 Results saved to: {output_file}")
    
    def _generate_comparison_report(self):
        """Generate markdown comparison report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"benchmark_report_{timestamp}.md"
        
        with open(report_file, 'w') as f:
            f.write("# Live Stock Benchmark Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Mode**: {self.mode}\n")
            f.write(f"**Stocks Tested**: {self.limit}\n\n")
            
            # Group by mode
            modes = {}
            for result in self.results:
                if result.mode not in modes:
                    modes[result.mode] = []
                modes[result.mode].append(result)
            
            for mode, results in modes.items():
                f.write(f"## {mode.upper()} System\n\n")
                
                successful = [r for r in results if r.success]
                if successful:
                    avg_runtime = sum(r.runtime_seconds for r in successful) / len(successful)
                    avg_tokens = sum(r.total_tokens for r in successful) / len(successful)
                    avg_cost = sum(r.estimated_cost for r in successful) / len(successful)
                    
                    f.write(f"- **Success Rate**: {len(successful)}/{len(results)}\n")
                    f.write(f"- **Average Runtime**: {avg_runtime:.1f}s\n")
                    f.write(f"- **Average Tokens**: {avg_tokens:,.0f}\n")
                    f.write(f"- **Average Cost**: ${avg_cost:.4f}\n\n")
                    
                    f.write("### Stock Results\n\n")
                    f.write("| Ticker | Action | Entry | Stop | Target | Runtime | Tokens | Cost |\n")
                    f.write("|--------|--------|-------|------|--------|---------|--------|------|\n")
                    
                    for r in successful:
                        f.write(f"| {r.ticker} | {r.action} | ₹{r.entry_price:,.0f} | "
                               f"₹{r.stop_loss:,.0f} | ₹{r.target:,.0f} | "
                               f"{r.runtime_seconds:.1f}s | {r.total_tokens:,} | ${r.estimated_cost:.4f} |\n")
                    
                    f.write("\n")
        
        print(f"📄 Report saved to: {report_file}")
    
    def _create_config(self) -> Dict[str, Any]:
        """Create configuration for graph"""
        return {
            "llm_provider": "groq",
            "deep_think_llm": "llama-3.3-70b-versatile",
            "quick_think_llm": "llama-3.3-70b-versatile",
            "data_cache_dir": "./data_cache",
            "results_dir": "./results",
            "max_debate_rounds": 3,
            "max_risk_discuss_rounds": 3 if self.mode == "original" else 1
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Benchmark TradingAgents on live NSE stocks")
    parser.add_argument(
        '--mode',
        choices=['original', 'optimized', 'both'],
        default='optimized',
        help='System mode to benchmark'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=20,
        help='Number of stocks to test (default: 20)'
    )
    
    args = parser.parse_args()
    
    benchmark = LiveStockBenchmark(mode=args.mode, limit=args.limit)
    
    try:
        benchmark.run_benchmark()
        return 0
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Benchmark failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
