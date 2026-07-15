#!/usr/bin/env python3
"""
Phase 3A Git-Based Validation with Deterministic Cache

Uses git to create clean baseline and optimized states.
Uses cached data to ensure identical inputs for both runs.

Flow:
1. Load cached validation data (VALIDATION_CACHE_ONLY mode)
2. Stash current changes (Phase 3A optimized)
3. Run BASELINE validation with cached data (pre-Phase-3A from git)
4. Restore Phase 3A changes
5. Run OPTIMIZED validation with cached data (Phase 3A applied)
6. Compare results

This ensures true before/after comparison with deterministic inputs.
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

# Enable environment
os.environ['USE_OPTIMIZED_ANALYSTS'] = '1'
os.environ['USE_OPTIMIZED_RISK'] = '1'
os.environ['AUDIT_MODE'] = '1'

# Check if cache-only mode is enabled
VALIDATION_CACHE_ONLY = os.environ.get('VALIDATION_CACHE_ONLY', 'false').lower() == 'true'


def find_cache_file(ticker: str, trade_date: str) -> Optional[str]:
    """
    Find the cache file for validation
    
    Args:
        ticker: Stock ticker (e.g., HDFCBANK.NS)
        trade_date: Trade date (e.g., 2024-01-15)
    
    Returns:
        Path to cache file or None if not found
    """
    cache_dir = Path("validation_cache")
    
    if not cache_dir.exists():
        return None
    
    cache_file = cache_dir / f"cached_data_{ticker}_{trade_date}.json"
    
    if cache_file.exists():
        return str(cache_file)
    
    return None


def load_validation_cache(ticker: str, trade_date: str) -> Optional[Any]:
    """
    Load validation cache and install cache loader
    
    Args:
        ticker: Stock ticker
        trade_date: Trade date
    
    Returns:
        Cache loader instance or None if cache not found/required
    """
    
    if not VALIDATION_CACHE_ONLY:
        print("ℹ️  VALIDATION_CACHE_ONLY=false - will use live APIs")
        return None
    
    print("\n" + "=" * 80)
    print("VALIDATION CACHE INITIALIZATION")
    print("=" * 80)
    print(f"Mode: VALIDATION_CACHE_ONLY=true")
    print(f"Ticker: {ticker}")
    print(f"Trade Date: {trade_date}")
    
    # Find cache file
    cache_file = find_cache_file(ticker, trade_date)
    
    if not cache_file:
        print(f"\n❌ ERROR: Cache file not found")
        print(f"   Expected: validation_cache/cached_data_{ticker}_{trade_date}.json")
        print(f"\n   Run this first:")
        print(f"   python cache_validation_data.py")
        raise FileNotFoundError(
            f"VALIDATION_CACHE_ONLY=true but cache not found.\n"
            f"Generate cache first with: python cache_validation_data.py"
        )
    
    print(f"\n📁 Cache file: {cache_file}")
    
    # Install cache loader
    try:
        from validation_cache_loader import install_cache_loader
        
        loader = install_cache_loader(cache_file)
        
        print("\n✅ Validation cache ready")
        print("   All dataflows will use cached data")
        print("   🔒 Any live API call will abort validation")
        
        return loader
        
    except ImportError as e:
        print(f"\n❌ ERROR: Cannot import validation_cache_loader")
        print(f"   {e}")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: Failed to load validation cache")
        print(f"   {e}")
        raise


def check_git_cleanliness() -> bool:
    """
    Check if git repo is clean before stashing.
    
    Returns True if safe to proceed, False otherwise.
    """
    print("\n🔍 Checking git repository cleanliness...")
    
    # Get git status
    returncode, stdout, stderr = run_command(['git', 'status', '--porcelain'], check=False)
    
    if returncode != 0:
        print("❌ Not a git repository or git not available")
        return False
    
    # Parse status
    lines = [line for line in stdout.strip().split('\n') if line]
    
    if not lines:
        print("⚠️  No changes to stash (repo is already clean)")
        print("   This means Phase 3A optimizations may not be present")
        response = input("Continue anyway? (y/N): ")
        return response.lower() == 'y'
    
    # Check for untracked or modified files that aren't Phase 3A related
    phase_3a_files = {
        'tradingagents/agents/managers/portfolio_manager.py',
        'tradingagents/agents/managers/research_manager.py',
        'tradingagents/agents/researchers/bear_researcher.py',
        'tradingagents/agents/researchers/bull_researcher.py',
        'tradingagents/agents/trader/trader.py',
        'tradingagents/default_config.py',
    }
    
    modified_files = set()
    untracked_files = []
    
    for line in lines:
        status = line[:2]
        filepath = line[3:].strip()
        
        if status.startswith('??'):
            untracked_files.append(filepath)
        elif status.strip() in ['M', 'MM', 'A', 'AM', 'D']:
            modified_files.add(filepath)
    
    # Check if only Phase 3A files are modified
    non_phase3a_files = modified_files - phase_3a_files
    
    print(f"   Modified files: {len(modified_files)}")
    print(f"   Phase 3A files: {len(modified_files & phase_3a_files)}")
    print(f"   Other modified: {len(non_phase3a_files)}")
    print(f"   Untracked files: {len(untracked_files)}")
    
    if non_phase3a_files:
        print("\n⚠️  WARNING: Non-Phase-3A files are modified:")
        for f in list(non_phase3a_files)[:10]:
            print(f"     - {f}")
        print("\n   These changes will be included in the stash.")
        print("\n   Options:")
        print("   1. Commit or stash these changes separately first")
        print("   2. Create a temporary validation branch")
        print("   3. Continue anyway (may affect validation)")
        print("")
        response = input("Create validation branch? (y/N): ")
        
        if response.lower() == 'y':
            return create_validation_branch()
        else:
            response = input("Continue with stash anyway? (y/N): ")
            return response.lower() == 'y'
    
    print("✅ Git repository is clean (only Phase 3A files modified)")
    return True


def create_validation_branch() -> bool:
    """Create a temporary validation branch"""
    print("\n🌿 Creating validation branch...")
    
    branch_name = f"validation-phase3a-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Create and checkout new branch
        run_command(['git', 'checkout', '-b', branch_name])
        print(f"✅ Created branch: {branch_name}")
        print("   Note: You're now on the validation branch")
        print("   After validation, switch back with: git checkout main/master")
        return True
    except Exception as e:
        print(f"❌ Failed to create branch: {e}")
        return False


def freeze_market_inputs() -> Dict[str, str]:
    """
    Freeze market inputs for consistent A/B comparison.
    
    Returns dict with frozen parameters.
    """
    print("\n🧊 Freezing market inputs for consistent comparison...")
    
    # Use a fixed date in the past to ensure data is available
    # and won't change between runs
    frozen_date = "2024-01-15"  # A stable historical date
    
    # Calculate lookback windows
    from datetime import datetime, timedelta
    base_date = datetime.strptime(frozen_date, "%Y-%m-%d")
    news_start = (base_date - timedelta(days=7)).strftime("%Y-%m-%d")
    data_start = (base_date - timedelta(days=90)).strftime("%Y-%m-%d")
    
    frozen_inputs = {
        'trade_date': frozen_date,
        'news_start_date': news_start,
        'data_start_date': data_start,
        'frozen': True
    }
    
    print(f"   Trade date: {frozen_date}")
    print(f"   News window: {news_start} to {frozen_date}")
    print(f"   Data window: {data_start} to {frozen_date}")
    print("   ✅ All inputs frozen (same for baseline and optimized)")
    
    return frozen_inputs


def git_stash_phase3a():
    """Stash Phase 3A changes"""
    print("\n📦 Stashing Phase 3A optimizations...")
    
    # Stash with message
    run_command(['git', 'stash', 'push', '-m', 'Phase 3A optimizations for validation'])
    
    print("✅ Phase 3A changes stashed")
    print("   Current state: BASELINE (pre-Phase-3A)")


def git_stash_pop():
    """Restore Phase 3A changes from stash"""
    print("\n📦 Restoring Phase 3A optimizations...")
    
    # Pop the stash
    run_command(['git', 'stash', 'pop'])
    
    print("✅ Phase 3A changes restored")
    print("   Current state: OPTIMIZED (Phase 3A applied)")


def verify_baseline_state():
    """Verify we're in baseline state"""
    print("\n🔍 Verifying baseline state...")
    
    # Check bull_researcher for max_tokens
    bull_file = Path("tradingagents/agents/researchers/bull_researcher.py")
    content = bull_file.read_text()
    
    has_max_tokens = 'max_tokens=800' in content
    has_verbose_prompt = 'Key points to focus on:' in content or len(content) > 2000
    
    # Check default_config for debate rounds
    config_file = Path("tradingagents/default_config.py")
    config_content = config_file.read_text()
    has_3_rounds = '"max_debate_rounds": 1' in config_content  # Default is 1, we'll override to 3
    
    print(f"   Output token caps: {'❌ Present (should be absent)' if has_max_tokens else '✅ Absent'}")
    print(f"   Verbose prompts: {'✅ Present' if has_verbose_prompt else '❌ Absent (should be present)'}")
    print(f"   Config debate rounds: {'✅ Default (1)' if has_3_rounds else '⚠️  Modified'}")
    
    if has_max_tokens:
        print("\n⚠️  WARNING: Baseline state has output caps (should not have them)")
        print("   This means Phase 3A changes may not have been fully stashed")
        return False
    
    return True


def verify_optimized_state():
    """Verify we're in optimized state"""
    print("\n🔍 Verifying optimized state...")
    
    # Check bull_researcher for max_tokens
    bull_file = Path("tradingagents/agents/researchers/bull_researcher.py")
    content = bull_file.read_text()
    
    has_max_tokens = 'max_tokens=800' in content
    has_reduced_prompt = 'Be concise and data-driven' in content
    
    # Check default_config for debate rounds
    config_file = Path("tradingagents/default_config.py")
    config_content = config_file.read_text()
    has_2_rounds = '"max_debate_rounds": 2' in config_content
    
    print(f"   Output token caps: {'✅ Present (800)' if has_max_tokens else '❌ Absent'}")
    print(f"   Reduced prompts: {'✅ Present' if has_reduced_prompt else '❌ Absent'}")
    print(f"   Debate rounds: {'✅ Set to 2' if has_2_rounds else '⚠️  Not set to 2'}")
    
    if not (has_max_tokens and has_reduced_prompt):
        print("\n⚠️  WARNING: Optimized state missing Phase 3A changes")
        return False
    
    return True


def run_validation_test(mode: str, debate_rounds: int, frozen_inputs: Dict[str, str]) -> Dict[str, Any]:
    """
    Run workflow validation with frozen inputs
    
    Args:
        mode: 'baseline' or 'optimized'
        debate_rounds: Number of debate rounds to use
        frozen_inputs: Frozen market data parameters for consistency
    """
    
    print(f"\n{'═' * 80}")
    print(f"RUNNING: {mode.upper()} VALIDATION")
    print('═' * 80)
    print(f"Debate rounds: {debate_rounds}")
    print(f"Stock: HDFCBANK.NS")
    print(f"Provider: OpenAI (gpt-4o / gpt-4o-mini)")
    print(f"Trade date: {frozen_inputs['trade_date']} (frozen)")
    
    # Reload modules to pick up file changes
    import importlib
    if 'tradingagents.graph' in sys.modules:
        del sys.modules['tradingagents.graph']
    if 'tradingagents.agents.researchers.bull_researcher' in sys.modules:
        del sys.modules['tradingagents.agents.researchers.bull_researcher']
    if 'tradingagents.agents.researchers.bear_researcher' in sys.modules:
        del sys.modules['tradingagents.agents.researchers.bear_researcher']
    
    from tradingagents.graph import TradingAgentsGraph
    from audit_framework import get_audit_collector, reset_audit_collector
    
    # Reset audit collector
    reset_audit_collector()
    
    # Config
    config = {
        "llm_provider": "openai",
        "deep_think_llm": "gpt-4o",
        "quick_think_llm": "gpt-4o-mini",
        "data_cache_dir": "./data_cache",
        "results_dir": "./results",
        "max_debate_rounds": debate_rounds,
        "max_risk_discuss_rounds": 1
    }
    
    print(f"\n⏱️  Starting workflow...")
    
    try:
        graph = TradingAgentsGraph(
            selected_analysts=["market", "fundamentals", "news"],
            config=config,
            debug=False
        )
        
        start_time = time.time()
        
        # Use frozen trade date
        final_state, signal = graph.propagate(
            company_name="HDFCBANK.NS",
            trade_date=frozen_inputs['trade_date']
        )
        
        runtime = time.time() - start_time
        
        # Get audit metrics
        collector = get_audit_collector()
        audit_summary = collector.get_summary() if collector.calls else {}
        
        # Extract details
        decision = final_state.get('final_trade_decision', '')
        trader_plan = final_state.get('trader_investment_plan', '')
        investment_plan = final_state.get('investment_plan', '')
        debate_state = final_state.get('investment_debate_state', {})
        
        bull_history = debate_state.get('bull_history', '')
        bear_history = debate_state.get('bear_history', '')
        
        result = {
            'mode': mode,
            'success': True,
            'runtime': round(runtime, 1),
            'total_tokens': audit_summary.get('total_tokens', 0),
            'input_tokens': sum(agent.get('total_input_tokens', 0) for agent in audit_summary.get('per_agent', {}).values()),
            'output_tokens': sum(agent.get('total_output_tokens', 0) for agent in audit_summary.get('per_agent', {}).values()),
            'total_cost': audit_summary.get('total_cost', 0),
            'debate_rounds': debate_rounds,
            'trade_date': frozen_inputs['trade_date'],
            'frozen_inputs': frozen_inputs,
            'decision': str(decision)[:500],
            'trader_plan': str(trader_plan)[:500],
            'investment_plan': str(investment_plan)[:500],
            'bull_reasoning': bull_history[:1000],
            'bear_reasoning': bear_history[:1000],
            'bull_length': len(bull_history),
            'bear_length': len(bear_history),
            'per_agent_metrics': audit_summary.get('per_agent', {}),
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n✅ {mode.upper()} validation complete!")
        print(f"   Runtime: {runtime:.1f}s")
        print(f"   Total tokens: {result['total_tokens']:,}")
        print(f"   Cost: ${result['total_cost']:.4f}")
        print(f"   Bull reasoning: {result['bull_length']:,} chars")
        print(f"   Bear reasoning: {result['bear_length']:,} chars")
        
        return result
        
    except Exception as e:
        print(f"\n❌ {mode.upper()} validation failed: {str(e)[:200]}")
        import traceback
        traceback.print_exc()
        
        return {
            'mode': mode,
            'success': False,
            'error': str(e),
            'frozen_inputs': frozen_inputs,
            'timestamp': datetime.now().isoformat()
        }


def generate_comparison_report(baseline: Dict, optimized: Dict) -> str:
    """Generate detailed comparison report"""
    
    report = []
    report.append("=" * 80)
    report.append("PHASE 3A GIT-BASED VALIDATION REPORT")
    report.append("=" * 80)
    report.append(f"Stock: HDFCBANK.NS (HDFC Bank)")
    report.append(f"Provider: OpenAI (gpt-4o / gpt-4o-mini)")
    report.append(f"Trade Date: {baseline.get('trade_date', 'N/A')} (frozen for both runs)")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append("⚠️  IMPORTANT: Both runs used identical frozen market inputs")
    report.append("   This ensures fair A/B comparison (optimization impact only)")
    report.append("")
    
    if not baseline.get('success') or not optimized.get('success'):
        report.append("❌ INCOMPLETE VALIDATION")
        report.append("")
        if not baseline.get('success'):
            report.append(f"Baseline failed: {baseline.get('error', 'Unknown')[:150]}")
        if not optimized.get('success'):
            report.append(f"Optimized failed: {optimized.get('error', 'Unknown')[:150]}")
        return "\n".join(report)
    
    # Performance metrics
    report.append("=" * 80)
    report.append("1. PERFORMANCE METRICS")
    report.append("=" * 80)
    report.append("")
    
    token_reduction = ((baseline['total_tokens'] - optimized['total_tokens']) / baseline['total_tokens'] * 100)
    runtime_reduction = ((baseline['runtime'] - optimized['runtime']) / baseline['runtime'] * 100)
    cost_reduction = ((baseline['total_cost'] - optimized['total_cost']) / baseline['total_cost'] * 100)
    
    report.append(f"{'Metric':<25} {'Baseline':<20} {'Optimized':<20} {'Change':<15}")
    report.append("─" * 80)
    report.append(f"{'Total Tokens':<25} {baseline['total_tokens']:>15,}   {optimized['total_tokens']:>15,}   {token_reduction:>+10.1f}%")
    report.append(f"{'  Input Tokens':<25} {baseline['input_tokens']:>15,}   {optimized['input_tokens']:>15,}   ")
    report.append(f"{'  Output Tokens':<25} {baseline['output_tokens']:>15,}   {optimized['output_tokens']:>15,}   ")
    report.append(f"{'Runtime (seconds)':<25} {baseline['runtime']:>15.1f}   {optimized['runtime']:>15.1f}   {runtime_reduction:>+10.1f}%")
    report.append(f"{'Cost (USD)':<25} ${baseline['total_cost']:>14.4f}   ${optimized['total_cost']:>14.4f}   {cost_reduction:>+10.1f}%")
    report.append(f"{'Debate Rounds':<25} {baseline['debate_rounds']:>15}   {optimized['debate_rounds']:>15}   -33.3%")
    report.append("")
    
    # Success criteria
    performance_pass = token_reduction >= 40 and runtime_reduction >= 25
    
    report.append("Performance Targets:")
    report.append(f"  Token reduction ≥ 40%:   {token_reduction:.1f}%  {'✅ PASS' if token_reduction >= 40 else '❌ FAIL'}")
    report.append(f"  Runtime reduction ≥ 25%: {runtime_reduction:.1f}%  {'✅ PASS' if runtime_reduction >= 25 else '❌ FAIL'}")
    report.append("")
    
    # Per-agent breakdown
    report.append("=" * 80)
    report.append("2. PER-AGENT METRICS")
    report.append("=" * 80)
    report.append("")
    
    baseline_agents = baseline.get('per_agent_metrics', {})
    optimized_agents = optimized.get('per_agent_metrics', {})
    
    if baseline_agents and optimized_agents:
        report.append(f"{'Agent':<25} {'Baseline Tokens':<20} {'Optimized Tokens':<20} {'Reduction':<15}")
        report.append("─" * 80)
        
        for agent_name in sorted(set(baseline_agents.keys()) | set(optimized_agents.keys())):
            baseline_agent = baseline_agents.get(agent_name, {})
            optimized_agent = optimized_agents.get(agent_name, {})
            
            base_tokens = baseline_agent.get('total_tokens', 0)
            opt_tokens = optimized_agent.get('total_tokens', 0)
            
            if base_tokens > 0:
                reduction = ((base_tokens - opt_tokens) / base_tokens * 100)
                report.append(f"{agent_name:<25} {base_tokens:>15,}   {opt_tokens:>15,}   {reduction:>+10.1f}%")
            else:
                report.append(f"{agent_name:<25} {base_tokens:>15,}   {opt_tokens:>15,}   {'N/A':>10}")
        
        report.append("")
        
        # Show call counts for LLM agents
        report.append("LLM Call Counts:")
        report.append(f"{'Agent':<25} {'Baseline Calls':<20} {'Optimized Calls':<20} {'Change':<15}")
        report.append("─" * 80)
        
        for agent_name in sorted(set(baseline_agents.keys()) | set(optimized_agents.keys())):
            baseline_agent = baseline_agents.get(agent_name, {})
            optimized_agent = optimized_agents.get(agent_name, {})
            
            base_calls = baseline_agent.get('calls', 0)
            opt_calls = optimized_agent.get('calls', 0)
            
            if base_calls > 0:
                change = opt_calls - base_calls
                report.append(f"{agent_name:<25} {base_calls:>15}   {opt_calls:>15}   {change:>+10}")
            else:
                report.append(f"{agent_name:<25} {base_calls:>15}   {opt_calls:>15}   {'N/A':>10}")
        
        report.append("")
    else:
        report.append("⚠️  Per-agent metrics not available")
        report.append("")
    
    # Quality comparison
    report.append("=" * 80)
    report.append("3. QUALITY ASSESSMENT")
    report.append("=" * 80)
    report.append("")
    
    report.append("Debate Quality:")
    report.append(f"  Bull reasoning length: {baseline['bull_length']:,} → {optimized['bull_length']:,} chars")
    report.append(f"  Bear reasoning length: {baseline['bear_length']:,} → {optimized['bear_length']:,} chars")
    report.append("")
    
    report.append("Recommendations:")
    report.append(f"  Baseline:  {baseline['decision'][:100]}...")
    report.append(f"  Optimized: {optimized['decision'][:100]}...")
    report.append("")
    
    # Verification
    report.append("=" * 80)
    report.append("4. INPUT CONSISTENCY VERIFICATION")
    report.append("=" * 80)
    report.append("")
    
    inputs_match = baseline.get('trade_date') == optimized.get('trade_date')
    
    if VALIDATION_CACHE_ONLY:
        report.append(f"Cache Mode: 🔒 VALIDATION_CACHE_ONLY=true")
        report.append(f"  All data from cached snapshot (100% deterministic)")
        report.append("")
    
    report.append(f"Trade Date Match: {'✅ YES' if inputs_match else '❌ NO'}")
    report.append(f"  Baseline:  {baseline.get('trade_date', 'N/A')}")
    report.append(f"  Optimized: {optimized.get('trade_date', 'N/A')}")
    report.append("")
    
    if not inputs_match:
        report.append("⚠️  WARNING: Inputs differ between runs!")
        report.append("   Comparison may be invalid (market data changed)")
        report.append("")
    
    # Final verdict
    report.append("=" * 80)
    report.append("5. VALIDATION VERDICT")
    report.append("=" * 80)
    report.append("")
    
    if performance_pass and inputs_match:
        report.append("✅ STAGE 1 PASSED")
        report.append("")
        report.append(f"Phase 3A achieved:")
        report.append(f"  • Token reduction: {token_reduction:.1f}% (target: ≥40%)")
        report.append(f"  • Runtime reduction: {runtime_reduction:.1f}% (target: ≥25%)")
        report.append(f"  • Cost reduction: {cost_reduction:.1f}%")
        report.append(f"  • Input consistency: Verified")
        report.append("")
        report.append("✅ APPROVED TO PROCEED TO STAGE 2")
    elif performance_pass and not inputs_match:
        report.append("⚠️  STAGE 1 INCONCLUSIVE")
        report.append("")
        report.append("Performance targets met BUT inputs differed:")
        report.append(f"  • Token reduction: {token_reduction:.1f}% ✅")
        report.append(f"  • Runtime reduction: {runtime_reduction:.1f}% ✅")
        report.append(f"  • Input consistency: ❌ FAILED")
        report.append("")
        report.append("⚠️  RE-RUN REQUIRED with frozen inputs")
    else:
        report.append("❌ STAGE 1 FAILED")
        report.append("")
        report.append(f"Performance targets not met:")
        report.append(f"  • Token reduction: {token_reduction:.1f}% (target: ≥40%)")
        report.append(f"  • Runtime reduction: {runtime_reduction:.1f}% (target: ≥25%)")
        report.append("")
        report.append("❌ DO NOT PROCEED TO STAGE 2")
    
    report.append("")
    
    return "\n".join(report)


def main():
    """Run git-based validation with safeguards and cache"""
    
    print("=" * 80)
    print("PHASE 3A GIT-BASED VALIDATION")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # Check API key
    if not os.environ.get('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not set!")
        print("   Set: export OPENAI_API_KEY='sk-...'")
        return False
    
    print("✅ OpenAI API key found")
    
    # Change to tradingagents directory
    if Path.cwd().name != 'tradingagents':
        os.chdir('tradingagents')
    
    # Control 2: Freeze market inputs (get frozen params first)
    frozen_inputs = freeze_market_inputs()
    ticker = "HDFCBANK.NS"
    
    # Control 0: Load validation cache (if VALIDATION_CACHE_ONLY=true)
    cache_loader = None
    try:
        cache_loader = load_validation_cache(ticker, frozen_inputs['trade_date'])
    except FileNotFoundError as e:
        print(f"\n❌ Cache error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected cache error: {e}")
        return False
    
    # Control 1: Check git cleanliness
    if not check_git_cleanliness():
        print("\n❌ Git cleanliness check failed")
        print("   Aborting validation")
        return False
    
    try:
        # Step 1: Stash Phase 3A changes
        git_stash_phase3a()
        
        # Verify baseline state
        if not verify_baseline_state():
            print("\n⚠️  Warning: Baseline state verification failed")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                git_stash_pop()
                return False
        
        # Step 2: Run baseline validation with frozen inputs
        print("\n" + "=" * 80)
        print("PHASE 1: BASELINE VALIDATION (Pre-Phase-3A)")
        print("=" * 80)
        
        baseline_result = run_validation_test(
            mode="baseline", 
            debate_rounds=3,
            frozen_inputs=frozen_inputs
        )
        
        if not baseline_result.get('success'):
            print("\n❌ Baseline validation failed")
            git_stash_pop()
            return False
        
        # Wait between tests
        print("\n⏳ Waiting 30s before optimized run...")
        time.sleep(30)
        
        # Step 3: Restore Phase 3A changes
        git_stash_pop()
        
        # Verify optimized state
        if not verify_optimized_state():
            print("\n⚠️  Warning: Optimized state verification failed")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                return False
        
        # Step 4: Run optimized validation with same frozen inputs
        print("\n" + "=" * 80)
        print("PHASE 2: OPTIMIZED VALIDATION (Phase 3A Applied)")
        print("=" * 80)
        print("⚠️  Using SAME frozen inputs as baseline for fair comparison")
        
        optimized_result = run_validation_test(
            mode="optimized", 
            debate_rounds=2,
            frozen_inputs=frozen_inputs
        )
        
        if not optimized_result.get('success'):
            print("\n❌ Optimized validation failed")
            return False
        
        # Step 5: Verify inputs were identical
        print("\n🔍 Verifying input consistency...")
        if baseline_result.get('trade_date') == optimized_result.get('trade_date'):
            print("✅ Trade dates match (fair comparison)")
        else:
            print("⚠️  Trade dates differ (comparison may be invalid)")
        
        # Step 6: Generate comparison report
        print("\n" + "=" * 80)
        print("GENERATING COMPARISON REPORT")
        print("=" * 80)
        
        report_text = generate_comparison_report(baseline_result, optimized_result)
        print("\n" + report_text)
        
        # Save results
        os.makedirs('validation_results', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save JSON
        json_data = {
            'baseline': baseline_result,
            'optimized': optimized_result,
            'frozen_inputs': frozen_inputs,
            'timestamp': datetime.now().isoformat()
        }
        
        json_path = f'validation_results/git_validation_{timestamp}.json'
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2, default=str)
        print(f"\n📁 Results saved to: {json_path}")
        
        # Save report
        report_path = f'validation_results/git_report_{timestamp}.md'
        with open(report_path, 'w') as f:
            f.write(report_text)
        print(f"📁 Report saved to: {report_path}")
        
        return baseline_result.get('success') and optimized_result.get('success')
        
    except Exception as e:
        print(f"\n❌ Validation crashed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Try to restore Phase 3A changes
        try:
            print("\n🔄 Attempting to restore Phase 3A changes...")
            git_stash_pop()
        except:
            print("⚠️  Could not auto-restore. Run manually: git stash pop")
        
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted")
        print("   Run 'git stash pop' to restore Phase 3A changes")
        sys.exit(1)
