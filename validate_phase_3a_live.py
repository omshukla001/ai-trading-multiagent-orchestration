"""
Phase 3A Controlled Live Validation

CRITICAL: This requires PAID API access to avoid rate limits.

Tests BEFORE vs AFTER Phase 3A optimizations on 3 stocks.

BEFORE (Baseline):
- Debate rounds: 3
- Output limits: None
- Prompts: Original verbose versions

AFTER (Optimized):  
- Debate rounds: 2
- Output limits: 800 tokens
- Prompts: Reduced versions

This script will:
1. Temporarily revert optimizations
2. Run baseline test
3. Re-apply optimizations
4. Run optimized test
5. Compare results

IMPORTANT: Set paid provider API key before running.
"""

import os
import sys
import json
import time
import shutil
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# Enable optimizations globally
os.environ['USE_OPTIMIZED_ANALYSTS'] = '1'
os.environ['USE_OPTIMIZED_RISK'] = '1'
os.environ['AUDIT_MODE'] = '1'


def backup_optimized_files():
    """Backup Phase 3A optimized files"""
    
    backup_dir = Path("phase_3a_backup")
    backup_dir.mkdir(exist_ok=True)
    
    files_to_backup = [
        "tradingagents/agents/researchers/bull_researcher.py",
        "tradingagents/agents/researchers/bear_researcher.py",
        "tradingagents/agents/managers/research_manager.py",
        "tradingagents/agents/trader/trader.py",
        "tradingagents/agents/managers/portfolio_manager.py",
        "tradingagents/default_config.py",
    ]
    
    print("📦 Backing up optimized files...")
    for file in files_to_backup:
        src = Path(file)
        if src.exists():
            dst = backup_dir / src.name
            shutil.copy2(src, dst)
            print(f"   ✅ {src.name}")
    
    return backup_dir


def restore_baseline_files():
    """Restore baseline (pre-optimization) files from git"""
    
    print("\n🔄 Restoring baseline files from git...")
    
    files_to_restore = [
        "tradingagents/agents/researchers/bull_researcher.py",
        "tradingagents/agents/researchers/bear_researcher.py",
        "tradingagents/agents/managers/research_manager.py",
        "tradingagents/agents/trader/trader.py",
        "tradingagents/agents/managers/portfolio_manager.py",
    ]
    
    import subprocess
    
    for file in files_to_restore:
        try:
            # Get the version from before Phase 3A optimizations
            # Use git to restore the original version
            result = subprocess.run(
                ['git', 'show', f'HEAD~5:{file}'],
                capture_output=True,
                text=True,
                check=True
            )
            
            Path(file).write_text(result.stdout)
            print(f"   ✅ {Path(file).name}")
        except subprocess.CalledProcessError:
            print(f"   ⚠️  Could not restore {file} from git")
            print(f"      Manual restoration may be needed")
            return False
    
    # Also change config back to 3 rounds
    config_file = Path("tradingagents/default_config.py")
    config_content = config_file.read_text()
    config_content = config_content.replace('"max_debate_rounds": 2', '"max_debate_rounds": 3')
    config_file.write_text(config_content)
    print(f"   ✅ default_config.py (max_debate_rounds: 2 → 3)")
    
    return True


def restore_optimized_files(backup_dir: Path):
    """Restore Phase 3A optimized files from backup"""
    
    print("\n🔄 Restoring optimized files...")
    
    for backup_file in backup_dir.glob("*.py"):
        if backup_file.name == "default_config.py":
            dst = Path("tradingagents") / backup_file.name
        else:
            # Determine correct destination based on filename
            if "bull_researcher" in backup_file.name or "bear_researcher" in backup_file.name:
                dst = Path("tradingagents/agents/researchers") / backup_file.name
            elif "research_manager" in backup_file.name or "portfolio_manager" in backup_file.name:
                dst = Path("tradingagents/agents/managers") / backup_file.name
            elif "trader" in backup_file.name:
                dst = Path("tradingagents/agents/trader") / backup_file.name
            else:
                continue
        
        shutil.copy2(backup_file, dst)
        print(f"   ✅ {backup_file.name}")
    
    print("\n✅ Optimized files restored")


def run_stock_test(ticker: str, company_name: str, mode: str, config_overrides: Dict = None) -> Dict[str, Any]:
    """Run workflow on a single stock"""
    
    print(f"\n{'═' * 80}")
    print(f"Testing: {ticker} - {company_name} ({mode.upper()})")
    print('═' * 80)
    
    # Need to reload modules to pick up file changes
    import importlib
    import tradingagents.graph
    importlib.reload(tradingagents.graph)
    
    from tradingagents.graph import TradingAgentsGraph
    from audit_framework import get_audit_collector, reset_audit_collector
    
    # Reset collector
    reset_audit_collector()
    
    # Base config
    config = {
        "llm_provider": "groq",
        "deep_think_llm": "llama-3.3-70b-versatile",
        "quick_think_llm": "llama-3.3-70b-versatile",
        "data_cache_dir": "./data_cache",
        "results_dir": "./results",
        "max_debate_rounds": 3 if mode == "baseline" else 2,
        "max_risk_discuss_rounds": 1
    }
    
    # Apply overrides
    if config_overrides:
        config.update(config_overrides)
    
    print(f"\n📊 Configuration:")
    print(f"   Debate rounds: {config['max_debate_rounds']}")
    print(f"   Mode: {mode}")
    
    try:
        graph = TradingAgentsGraph(
            selected_analysts=["market", "fundamentals", "news"],
            config=config,
            debug=False
        )
        
        start_time = time.time()
        
        final_state, signal = graph.propagate(
            company_name=ticker,
            trade_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        runtime = time.time() - start_time
        
        # Extract recommendation
        decision = final_state.get('final_trade_decision', {})
        trader_plan = final_state.get('trader_investment_plan', {})
        investment_plan = final_state.get('investment_plan', {})
        
        # Parse decision
        action = str(decision).split('action')[-1] if isinstance(decision, dict) else 'N/A'
        confidence = str(decision).split('confidence')[-1] if isinstance(decision, dict) else 'N/A'
        
        # Get audit metrics
        collector = get_audit_collector()
        audit_summary = collector.get_summary() if collector.calls else None
        
        result = {
            'ticker': ticker,
            'company_name': company_name,
            'mode': mode,
            'success': True,
            'runtime': round(runtime, 1),
            'total_tokens': audit_summary['total_tokens'] if audit_summary else 0,
            'total_cost': audit_summary['total_cost'] if audit_summary else 0,
            'decision': str(decision)[:500],
            'trader_plan': str(trader_plan)[:500],
            'investment_plan': str(investment_plan)[:500],
            'action': action,
            'confidence': confidence,
            'audit_summary': audit_summary,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n✅ Success!")
        print(f"   Runtime: {runtime:.1f}s")
        if audit_summary:
            print(f"   Tokens: {audit_summary['total_tokens']:,}")
            print(f"   Cost: ${audit_summary['total_cost']:.4f}")
        
        return result
        
    except Exception as e:
        error_str = str(e)
        print(f"\n❌ Failed: {error_str[:150]}")
        
        return {
            'ticker': ticker,
            'company_name': company_name,
            'mode': mode,
            'success': False,
            'error': error_str,
            'runtime': 0,
            'timestamp': datetime.now().isoformat()
        }


def compare_results(baseline: List[Dict], optimized: List[Dict]) -> str:
    """Generate comparison report"""
    
    report = []
    report.append("=" * 80)
    report.append("PHASE 3A LIVE VALIDATION REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Check success rates
    baseline_success = [r for r in baseline if r.get('success')]
    optimized_success = [r for r in optimized if r.get('success')]
    
    if not baseline_success or not optimized_success:
        report.append("⚠️  INCOMPLETE VALIDATION")
        report.append("")
        report.append(f"Baseline: {len(baseline_success)}/{len(baseline)} success")
        report.append(f"Optimized: {len(optimized_success)}/{len(optimized)} success")
        report.append("")
        report.append("Cannot perform comparison without successful runs on both sides.")
        return "\n".join(report)
    
    # Performance comparison
    report.append("=" * 80)
    report.append("1. PERFORMANCE METRICS")
    report.append("=" * 80)
    report.append("")
    
    avg_baseline_tokens = sum(r['total_tokens'] for r in baseline_success) / len(baseline_success)
    avg_optimized_tokens = sum(r['total_tokens'] for r in optimized_success) / len(optimized_success)
    
    avg_baseline_runtime = sum(r['runtime'] for r in baseline_success) / len(baseline_success)
    avg_optimized_runtime = sum(r['runtime'] for r in optimized_success) / len(optimized_success)
    
    avg_baseline_cost = sum(r['total_cost'] for r in baseline_success) / len(baseline_success)
    avg_optimized_cost = sum(r['total_cost'] for r in optimized_success) / len(optimized_success)
    
    token_reduction = ((avg_baseline_tokens - avg_optimized_tokens) / avg_baseline_tokens * 100)
    runtime_reduction = ((avg_baseline_runtime - avg_optimized_runtime) / avg_baseline_runtime * 100)
    cost_reduction = ((avg_baseline_cost - avg_optimized_cost) / avg_baseline_cost * 100)
    
    report.append(f"{'Metric':<25} {'Baseline':<15} {'Optimized':<15} {'Change':<15}")
    report.append("─" * 80)
    report.append(f"{'Total Tokens':<25} {int(avg_baseline_tokens):>10,}   {int(avg_optimized_tokens):>10,}   {token_reduction:>+10.1f}%")
    report.append(f"{'Runtime (seconds)':<25} {int(avg_baseline_runtime):>10}   {int(avg_optimized_runtime):>10}   {runtime_reduction:>+10.1f}%")
    report.append(f"{'Cost (USD)':<25} ${avg_baseline_cost:>9.4f}   ${avg_optimized_cost:>9.4f}   {cost_reduction:>+10.1f}%")
    report.append("")
    
    # Success criteria
    report.append("Performance Targets:")
    report.append(f"  Token reduction ≥ 40%:   {token_reduction:.1f}%  {'✅ PASS' if token_reduction >= 40 else '❌ FAIL'}")
    report.append(f"  Runtime reduction ≥ 25%: {runtime_reduction:.1f}%  {'✅ PASS' if runtime_reduction >= 25 else '❌ FAIL'}")
    report.append("")
    
    # Quality comparison
    report.append("=" * 80)
    report.append("2. RECOMMENDATION QUALITY")
    report.append("=" * 80)
    report.append("")
    
    # Per-stock comparison
    for i, (b, o) in enumerate(zip(baseline_success, optimized_success)):
        if b['ticker'] == o['ticker']:
            report.append(f"\n{b['ticker']} - {b['company_name']}")
            report.append("─" * 40)
            report.append(f"{'':20} {'Baseline':<30} {'Optimized':<30}")
            report.append(f"{'Decision':<20} {str(b.get('decision', 'N/A'))[:28]:<30} {str(o.get('decision', 'N/A'))[:28]:<30}")
            report.append(f"{'Trader Plan':<20} {str(b.get('trader_plan', 'N/A'))[:28]:<30} {str(o.get('trader_plan', 'N/A'))[:28]:<30}")
    
    report.append("")
    report.append("=" * 80)
    report.append("3. VALIDATION OUTCOME")
    report.append("=" * 80)
    report.append("")
    
    performance_pass = token_reduction >= 40 and runtime_reduction >= 25
    
    if performance_pass:
        report.append("✅ VALIDATION PASSED")
        report.append("")
        report.append("Phase 3A optimizations achieved performance targets.")
        report.append("Recommendation: APPROVED FOR DEPLOYMENT")
    else:
        report.append("❌ VALIDATION FAILED")
        report.append("")
        report.append("Performance targets not met.")
        report.append("Recommendation: INVESTIGATE OR ROLLBACK")
    
    report.append("")
    
    return "\n".join(report)


def main():
    """Run controlled validation"""
    
    print("=" * 80)
    print("PHASE 3A CONTROLLED LIVE VALIDATION")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    print("⚠️  WARNING: This requires PAID API access")
    print("   Set GROQ_API_KEY or other paid provider key")
    print("")
    
    # Check API key
    if not os.environ.get('GROQ_API_KEY'):
        print("❌ No API key found!")
        print("   Set one of: GROQ_API_KEY, OPENAI_API_KEY, CEREBRAS_API_KEY")
        print("")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return False
    
    # Test stocks
    test_stocks = [
        ("HDFCBANK.NS", "HDFC Bank"),
        ("INFY.NS", "Infosys"),
        ("RELIANCE.NS", "Reliance Industries")
    ]
    
    print(f"\nTest Set: {len(test_stocks)} stocks")
    for ticker, name in test_stocks:
        print(f"  • {ticker} - {name}")
    print("")
    
    # Backup optimized files
    backup_dir = backup_optimized_files()
    
    # Run baseline tests
    print("\n" + "=" * 80)
    print("PHASE 1: BASELINE TESTS (Before Phase 3A)")
    print("=" * 80)
    
    if not restore_baseline_files():
        print("\n❌ Could not restore baseline files")
        print("   Manual intervention required")
        return False
    
    baseline_results = []
    for ticker, name in test_stocks:
        result = run_stock_test(ticker, name, "baseline")
        baseline_results.append(result)
        
        if ticker != test_stocks[-1][0]:
            print("\n⏳ Waiting 90s between tests...")
            time.sleep(90)
    
    # Restore optimized files
    print("\n" + "=" * 80)
    print("PHASE 2: OPTIMIZED TESTS (After Phase 3A)")
    print("=" * 80)
    
    restore_optimized_files(backup_dir)
    
    optimized_results = []
    for ticker, name in test_stocks:
        result = run_stock_test(ticker, name, "optimized")
        optimized_results.append(result)
        
        if ticker != test_stocks[-1][0]:
            print("\n⏳ Waiting 90s between tests...")
            time.sleep(90)
    
    # Generate comparison report
    print("\n" + "=" * 80)
    print("GENERATING COMPARISON REPORT")
    print("=" * 80)
    
    report_text = compare_results(baseline_results, optimized_results)
    print("\n" + report_text)
    
    # Save results
    os.makedirs('validation_results', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save JSON
    json_data = {
        'baseline': baseline_results,
        'optimized': optimized_results,
        'timestamp': datetime.now().isoformat()
    }
    
    json_path = f'validation_results/phase_3a_live_validation_{timestamp}.json'
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2, default=str)
    print(f"\n📁 Results saved to: {json_path}")
    
    # Save report
    report_path = f'validation_results/phase_3a_live_report_{timestamp}.md'
    with open(report_path, 'w') as f:
        f.write(report_text)
    print(f"📁 Report saved to: {report_path}")
    
    # Check if validation passed
    successful_baseline = [r for r in baseline_results if r.get('success')]
    successful_optimized = [r for r in optimized_results if r.get('success')]
    
    return len(successful_baseline) > 0 and len(successful_optimized) > 0


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted")
        print("   Optimized files may need manual restoration")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation crashed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
