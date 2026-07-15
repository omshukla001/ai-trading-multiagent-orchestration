"""
Detailed Validation Test - Multi-Provider Routing

Collects comprehensive metrics:
1. Total runtime per stock
2. Agent runtime breakdown
3. External API bottlenecks
4. Failure classification
5. Largest bottleneck identification

Tests on 1 stock at a time to avoid rate limits.
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict

# Enable multi-provider routing
os.environ['ENABLE_MULTI_PROVIDER'] = 'true'
os.environ['USE_OPTIMIZED_ANALYSTS'] = '1'
os.environ['USE_OPTIMIZED_RISK'] = '1'

from tradingagents.graph import TradingAgentsGraph
from tradingagents.llm_clients.provider_monitor import get_monitor


class DetailedMetricsCollector:
    """Collects detailed timing and failure metrics"""
    
    def __init__(self):
        self.stock_metrics = []
        self.api_bottlenecks = defaultdict(list)
        self.failures = defaultdict(list)
        
    def record_stock(self, ticker: str, metrics: Dict[str, Any]):
        """Record metrics for a stock"""
        self.stock_metrics.append({
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            **metrics
        })
    
    def record_api_call(self, service: str, latency: float, success: bool, error: str = None):
        """Record external API call"""
        self.api_bottlenecks[service].append({
            'latency': latency,
            'success': success,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })
    
    def record_failure(self, category: str, agent: str, error: str):
        """Record failure by category"""
        self.failures[category].append({
            'agent': agent,
            'error': error,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Generate summary report"""
        
        # Calculate API bottleneck stats
        api_stats = {}
        for service, calls in self.api_bottlenecks.items():
            if calls:
                latencies = [c['latency'] for c in calls]
                failures = sum(1 for c in calls if not c['success'])
                api_stats[service] = {
                    'total_calls': len(calls),
                    'avg_latency': round(sum(latencies) / len(latencies), 2),
                    'max_latency': round(max(latencies), 2),
                    'failures': failures,
                    'failure_rate': round(failures / len(calls) * 100, 1)
                }
        
        # Calculate failure breakdown
        failure_summary = {
            category: {
                'count': len(failures),
                'agents': list(set(f['agent'] for f in failures))
            }
            for category, failures in self.failures.items()
        }
        
        # Find largest bottleneck
        largest_bottleneck = None
        max_time = 0
        
        for stock in self.stock_metrics:
            if 'agent_breakdown' in stock:
                for agent, timing in stock['agent_breakdown'].items():
                    if timing > max_time:
                        max_time = timing
                        largest_bottleneck = {
                            'agent': agent,
                            'time': timing,
                            'stock': stock['ticker']
                        }
        
        return {
            'stock_metrics': self.stock_metrics,
            'api_bottlenecks': api_stats,
            'failure_classification': failure_summary,
            'largest_bottleneck': largest_bottleneck,
            'total_stocks': len(self.stock_metrics),
            'successful_stocks': sum(1 for s in self.stock_metrics if s.get('success', False))
        }
    
    def save_report(self, filename: str):
        """Save detailed report to file"""
        report = self.get_summary()
        
        os.makedirs('validation_results', exist_ok=True)
        filepath = f'validation_results/{filename}'
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filepath


def test_single_stock_detailed(ticker: str, name: str, graph: TradingAgentsGraph, 
                                metrics_collector: DetailedMetricsCollector) -> Dict[str, Any]:
    """
    Test single stock with detailed instrumentation
    
    Returns:
        Metrics dict with timing breakdown
    """
    
    print(f"\n{'─' * 80}")
    print(f"Testing: {ticker} - {name}")
    print('─' * 80)
    
    result = {
        'ticker': ticker,
        'name': name,
        'success': False,
        'total_runtime': 0,
        'agent_breakdown': {},
        'error': None
    }
    
    try:
        overall_start = time.time()
        
        # Track agent timing (approximate - we can't hook into graph directly)
        # We'll use provider metrics as proxy
        monitor = get_monitor()
        before_metrics = monitor.get_summary()
        
        final_state, signal = graph.propagate(
            company_name=ticker,
            trade_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        overall_end = time.time()
        result['total_runtime'] = round(overall_end - overall_start, 2)
        
        # Get provider metrics delta
        after_metrics = monitor.get_summary()
        
        # Extract agent timing from provider metrics
        if 'per_agent' in after_metrics:
            for agent_name, agent_data in after_metrics['per_agent'].items():
                # Calculate average runtime for this agent
                if agent_data['requests'] > 0:
                    avg_runtime = agent_data.get('avg_runtime', 0)
                    result['agent_breakdown'][agent_name] = round(avg_runtime, 2)
        
        # Extract decision
        decision = final_state.get('final_trade_decision', {})
        result['action'] = decision.get('action', 'N/A')
        result['confidence'] = decision.get('confidence', 'N/A')
        result['success'] = True
        
        print(f"  ✅ {ticker}: {result['action']} ({result['total_runtime']}s)")
        
    except Exception as e:
        result['error'] = str(e)
        result['total_runtime'] = round(time.time() - overall_start, 2) if 'overall_start' in locals() else 0
        
        # Classify failure
        error_str = str(e).lower()
        if '429' in error_str or 'rate limit' in error_str or 'quota' in error_str:
            metrics_collector.record_failure('LLM Failures', 'Rate Limit', str(e))
        elif 'timeout' in error_str:
            metrics_collector.record_failure('Timeout Failures', ticker, str(e))
        elif 'schema' in error_str or 'validation' in error_str:
            metrics_collector.record_failure('Graph Failures', ticker, str(e))
        else:
            metrics_collector.record_failure('Data Provider Failures', ticker, str(e))
        
        print(f"  ❌ {ticker}: FAILED - {str(e)[:100]}")
    
    metrics_collector.record_stock(ticker, result)
    return result


def run_validation_test():
    """Run detailed validation test"""
    
    print("=" * 80)
    print("VALIDATION TEST - DETAILED METRICS COLLECTION")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if validation mode is enabled
    if os.environ.get('VALIDATION_MODE', 'false').lower() == 'true':
        print("⚠️  VALIDATION MODE: All agents using Cerebras")
    
    print()
    
    # Test on 1 stock to avoid rate limits
    test_stock = [
        ("HDFCBANK.NS", "HDFC Bank")
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
    
    print("Initializing TradingAgents graph...")
    graph = TradingAgentsGraph(
        selected_analysts=["market", "fundamentals", "news"],
        config=config,
        debug=False
    )
    print("✅ Graph initialized\n")
    
    metrics_collector = DetailedMetricsCollector()
    
    # Test each stock
    for ticker, name in test_stock:
        test_single_stock_detailed(ticker, name, graph, metrics_collector)
        
        # Wait between stocks to avoid rate limits
        if ticker != test_stock[-1][0]:
            print("\n⏳ Waiting 60s to avoid rate limits...")
            time.sleep(60)
    
    # Generate and save report
    print("\n" + "=" * 80)
    print("VALIDATION REPORT")
    print("=" * 80)
    
    summary = metrics_collector.get_summary()
    
    # Print summary
    print(f"\n📊 Overall Results:")
    print(f"   Success Rate: {summary['successful_stocks']}/{summary['total_stocks']}")
    
    print(f"\n⏱️  Runtime Breakdown:")
    for stock in summary['stock_metrics']:
        print(f"\n   {stock['ticker']} ({stock.get('total_runtime', 0)}s total):")
        if 'agent_breakdown' in stock and stock['agent_breakdown']:
            for agent, runtime in sorted(stock['agent_breakdown'].items(), 
                                        key=lambda x: x[1], reverse=True):
                print(f"      • {agent}: {runtime}s")
        else:
            print(f"      No agent breakdown available")
    
    print(f"\n🌐 External API Bottlenecks:")
    if summary['api_bottlenecks']:
        for service, stats in summary['api_bottlenecks'].items():
            print(f"   {service}:")
            print(f"      • Calls: {stats['total_calls']}")
            print(f"      • Avg latency: {stats['avg_latency']}s")
            print(f"      • Max latency: {stats['max_latency']}s")
            print(f"      • Failures: {stats['failures']} ({stats['failure_rate']}%)")
    else:
        print("   No API calls tracked")
    
    print(f"\n❌ Failure Classification:")
    if summary['failure_classification']:
        for category, data in summary['failure_classification'].items():
            print(f"   {category}: {data['count']} failures")
            print(f"      Agents: {', '.join(data['agents'])}")
    else:
        print("   No failures recorded")
    
    print(f"\n🔥 Largest Bottleneck:")
    if summary['largest_bottleneck']:
        bottleneck = summary['largest_bottleneck']
        print(f"   Agent: {bottleneck['agent']}")
        print(f"   Time: {bottleneck['time']}s")
        print(f"   Stock: {bottleneck['stock']}")
    else:
        print("   No bottleneck data available")
    
    # Save detailed report
    report_filename = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = metrics_collector.save_report(report_filename)
    print(f"\n📁 Detailed report saved to: {filepath}")
    
    # Show provider metrics
    print("\n" + "=" * 80)
    print("PROVIDER METRICS")
    print("=" * 80)
    monitor = get_monitor()
    monitor.print_summary()
    monitor.save_metrics(f"validation_provider_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    return summary['successful_stocks'] > 0


if __name__ == "__main__":
    try:
        success = run_validation_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Validation test crashed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
