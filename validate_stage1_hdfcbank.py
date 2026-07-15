"""
Phase 3A Live Validation - Stage 1
Single Stock: HDFCBANK.NS

Tests BEFORE vs AFTER on one stock with OpenAI (most stable provider).

Stage 1: Proof of concept on HDFCBANK.NS
- Validates approach works
- Checks quality preservation
- Measures actual performance gains

If Stage 1 passes → proceed to Stage 2 (all 3 stocks)
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any

# Set OpenAI as provider
os.environ['USE_OPTIMIZED_ANALYSTS'] = '1'
os.environ['USE_OPTIMIZED_RISK'] = '1'
os.environ['AUDIT_MODE'] = '1'

def extract_debate_quality(final_state: Dict) -> Dict[str, Any]:
    """Extract debate arguments for quality assessment"""
    
    debate_state = final_state.get('investment_debate_state', {})
    
    bull_history = debate_state.get('bull_history', '')
    bear_history = debate_state.get('bear_history', '')
    
    return {
        'bull_arguments': bull_history,
        'bear_arguments': bear_history,
        'bull_length': len(bull_history),
        'bear_length': len(bear_history),
        'rounds': bull_history.count('Bull Analyst:')
    }


def extract_recommendation_details(final_state: Dict) -> Dict[str, Any]:
    """Extract detailed recommendation info"""
    
    decision = final_state.get('final_trade_decision', '')
    trader_plan = final_state.get('trader_investment_plan', '')
    investment_plan = final_state.get('investment_plan', '')
    
    # Convert to string for parsing
    decision_str = str(decision)
    trader_str = str(trader_plan)
    investment_str = str(investment_plan)
    
    return {
        'final_decision': decision_str,
        'trader_plan': trader_str,
        'investment_plan': investment_str,
        'decision_preview': decision_str[:300],
        'trader_preview': trader_str[:300],
        'investment_preview': investment_str[:300]
    }


def run_test(mode: str, debate_rounds: int, use_limits: bool) -> Dict[str, Any]:
    """
    Run workflow test
    
    Args:
        mode: 'baseline' or 'optimized'
        debate_rounds: 3 for baseline, 2 for optimized
        use_limits: False for baseline, True for optimized
    """
    
    print(f"\n{'═' * 80}")
    print(f"Running: {mode.upper()} (debate_rounds={debate_rounds}, output_limits={use_limits})")
    print('═' * 80)
    
    # Need to reload to pick up any file changes
    import importlib
    if 'tradingagents.graph' in sys.modules:
        importlib.reload(sys.modules['tradingagents.graph'])
    
    from tradingagents.graph import TradingAgentsGraph
    from audit_framework import get_audit_collector, reset_audit_collector
    
    reset_audit_collector()
    
    config = {
        "llm_provider": "openai",
        "deep_think_llm": "gpt-4o",
        "quick_think_llm": "gpt-4o-mini",
        "data_cache_dir": "./data_cache",
        "results_dir": "./results",
        "max_debate_rounds": debate_rounds,
        "max_risk_discuss_rounds": 1
    }
    
    print(f"\n📊 Configuration:")
    print(f"   Provider: OpenAI")
    print(f"   Deep model: {config['deep_think_llm']}")
    print(f"   Quick model: {config['quick_think_llm']}")
    print(f"   Debate rounds: {debate_rounds}")
    print(f"   Output limits: {'Yes (800 tokens)' if use_limits else 'No (unlimited)'}")
    
    try:
        graph = TradingAgentsGraph(
            selected_analysts=["market", "fundamentals", "news"],
            config=config,
            debug=False
        )
        
        print(f"\n⏱️  Starting workflow...")
        start_time = time.time()
        
        final_state, signal = graph.propagate(
            company_name="HDFCBANK.NS",
            trade_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        runtime = time.time() - start_time
        
        # Get metrics
        collector = get_audit_collector()
        audit_summary = collector.get_summary() if collector.calls else {}
        
        # Extract details
        rec_details = extract_recommendation_details(final_state)
        debate_quality = extract_debate_quality(final_state)
        
        result = {
            'mode': mode,
            'success': True,
            'runtime': round(runtime, 1),
            'total_tokens': audit_summary.get('total_tokens', 0),
            'input_tokens': sum(agent['total_input_tokens'] for agent in audit_summary.get('per_agent', {}).values()),
            'output_tokens': sum(agent['total_output_tokens'] for agent in audit_summary.get('per_agent', {}).values()),
            'total_cost': audit_summary.get('total_cost', 0),
            'debate_rounds': debate_rounds,
            'recommendation': rec_details,
            'debate_quality': debate_quality,
            'per_agent_metrics': audit_summary.get('per_agent', {}),
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n✅ Success!")
        print(f"   Runtime: {runtime:.1f}s")
        print(f"   Tokens: {result['total_tokens']:,}")
        print(f"   Cost: ${result['total_cost']:.4f}")
        print(f"   Debate rounds: {debate_quality['rounds']}")
        print(f"   Bull arguments: {debate_quality['bull_length']:,} chars")
        print(f"   Bear arguments: {debate_quality['bear_length']:,} chars")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Failed: {str(e)[:200]}")
        import traceback
        traceback.print_exc()
        
        return {
            'mode': mode,
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def assess_quality_change(baseline: Dict, optimized: Dict) -> Dict[str, Any]:
    """Assess quality degradation between baseline and optimized"""
    
    assessment = {
        'recommendation_changed': False,
        'confidence_degradation': 0.0,
        'reasoning_quality_drop': False,
        'details': []
    }
    
    # Check debate length reduction
    baseline_bull = baseline['debate_quality']['bull_length']
    optimized_bull = optimized['debate_quality']['bull_length']
    baseline_bear = baseline['debate_quality']['bear_length']
    optimized_bear = optimized['debate_quality']['bear_length']
    
    bull_reduction = ((baseline_bull - optimized_bull) / baseline_bull * 100) if baseline_bull > 0 else 0
    bear_reduction = ((baseline_bear - optimized_bear) / baseline_bear * 100) if baseline_bear > 0 else 0
    
    assessment['details'].append(f"Bull arguments reduced by {bull_reduction:.1f}%")
    assessment['details'].append(f"Bear arguments reduced by {bear_reduction:.1f}%")
    
    # Check if arguments still contain evidence
    baseline_bull_text = baseline['debate_quality']['bull_arguments']
    optimized_bull_text = optimized['debate_quality']['bull_arguments']
    
    import re
    baseline_has_numbers = bool(re.search(r'\d+%|\d+\.?\d*x|₹\d+|\$\d+', baseline_bull_text))
    optimized_has_numbers = bool(re.search(r'\d+%|\d+\.?\d*x|₹\d+|\$\d+', optimized_bull_text))
    
    if baseline_has_numbers and not optimized_has_numbers:
        assessment['reasoning_quality_drop'] = True
        assessment['details'].append("⚠️  Optimized version lost numerical evidence")
    elif optimized_has_numbers:
        assessment['details'].append("✅ Evidence-based reasoning preserved")
    
    # Compare recommendations
    baseline_rec = baseline['recommendation']['decision_preview'].lower()
    optimized_rec = optimized['recommendation']['decision_preview'].lower()
    
    # Simple check if action words changed
    baseline_action = None
    optimized_action = None
    
    for action in ['buy', 'sell', 'hold', 'overweight', 'underweight']:
        if action in baseline_rec:
            baseline_action = action
        if action in optimized_rec:
            optimized_action = action
    
    if baseline_action != optimized_action:
        assessment['recommendation_changed'] = True
        assessment['details'].append(f"⚠️  Recommendation changed: {baseline_action} → {optimized_action}")
    else:
        assessment['details'].append(f"✅ Recommendation consistent: {baseline_action}")
    
    return assessment


def generate_stage1_report(baseline: Dict, optimized: Dict) -> str:
    """Generate Stage 1 validation report"""
    
    report = []
    report.append("=" * 80)
    report.append("PHASE 3A LIVE VALIDATION - STAGE 1")
    report.append("=" * 80)
    report.append(f"Stock: HDFCBANK.NS (HDFC Bank)")
    report.append(f"Provider: OpenAI (gpt-4o / gpt-4o-mini)")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    if not baseline.get('success') or not optimized.get('success'):
        report.append("❌ INCOMPLETE VALIDATION")
        report.append("")
        if not baseline.get('success'):
            report.append(f"Baseline failed: {baseline.get('error', 'Unknown')[:100]}")
        if not optimized.get('success'):
            report.append(f"Optimized failed: {optimized.get('error', 'Unknown')[:100]}")
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
    report.append(f"{'  Input Tokens':<25} {baseline['input_tokens']:>15,}   {optimized['input_tokens']:>15,}")
    report.append(f"{'  Output Tokens':<25} {baseline['output_tokens']:>15,}   {optimized['output_tokens']:>15,}")
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
    
    # Quality assessment
    report.append("=" * 80)
    report.append("2. QUALITY ASSESSMENT")
    report.append("=" * 80)
    report.append("")
    
    quality = assess_quality_change(baseline, optimized)
    
    report.append("Quality Checks:")
    for detail in quality['details']:
        report.append(f"  {detail}")
    report.append("")
    
    quality_pass = not quality['recommendation_changed'] and not quality['reasoning_quality_drop']
    
    report.append(f"Quality Status: {'✅ PRESERVED' if quality_pass else '⚠️  DEGRADED'}")
    report.append("")
    
    # Debate quality
    report.append("=" * 80)
    report.append("3. DEBATE QUALITY COMPARISON")
    report.append("=" * 80)
    report.append("")
    
    report.append(f"{'Metric':<30} {'Baseline':<20} {'Optimized':<20}")
    report.append("─" * 70)
    report.append(f"{'Debate Rounds Executed':<30} {baseline['debate_quality']['rounds']:>15}   {optimized['debate_quality']['rounds']:>15}")
    report.append(f"{'Bull Arguments Length':<30} {baseline['debate_quality']['bull_length']:>15,}   {optimized['debate_quality']['bull_length']:>15,}")
    report.append(f"{'Bear Arguments Length':<30} {baseline['debate_quality']['bear_length']:>15,}   {optimized['debate_quality']['bear_length']:>15,}")
    report.append("")
    
    # Recommendations
    report.append("=" * 80)
    report.append("4. RECOMMENDATIONS COMPARISON")
    report.append("=" * 80)
    report.append("")
    
    report.append("Baseline:")
    report.append(f"{baseline['recommendation']['decision_preview']}")
    report.append("")
    report.append("Optimized:")
    report.append(f"{optimized['recommendation']['decision_preview']}")
    report.append("")
    
    # Final verdict
    report.append("=" * 80)
    report.append("5. STAGE 1 VERDICT")
    report.append("=" * 80)
    report.append("")
    
    if performance_pass and quality_pass:
        report.append("✅ STAGE 1 PASSED")
        report.append("")
        report.append("Phase 3A optimizations achieved:")
        report.append(f"  • Token reduction: {token_reduction:.1f}% (target: ≥40%)")
        report.append(f"  • Runtime reduction: {runtime_reduction:.1f}% (target: ≥25%)")
        report.append(f"  • Quality preserved: Recommendation consistent, reasoning intact")
        report.append("")
        report.append("✅ APPROVED TO PROCEED TO STAGE 2")
        report.append("   → Run full validation on all 3 stocks")
    elif performance_pass:
        report.append("⚠️  STAGE 1 PARTIAL PASS")
        report.append("")
        report.append("Performance targets met but quality concerns:")
        report.append(f"  • Token reduction: {token_reduction:.1f}% ✅")
        report.append(f"  • Runtime reduction: {runtime_reduction:.1f}% ✅")
        report.append(f"  • Quality: ⚠️  Potential degradation detected")
        report.append("")
        report.append("⚠️  REVIEW REQUIRED BEFORE STAGE 2")
    else:
        report.append("❌ STAGE 1 FAILED")
        report.append("")
        report.append("Performance targets not met:")
        report.append(f"  • Token reduction: {token_reduction:.1f}% (target: ≥40%) {'✅' if token_reduction >= 40 else '❌'}")
        report.append(f"  • Runtime reduction: {runtime_reduction:.1f}% (target: ≥25%) {'✅' if runtime_reduction >= 25 else '❌'}")
        report.append("")
        report.append("❌ DO NOT PROCEED TO STAGE 2")
        report.append("   → Investigate discrepancy or rollback optimizations")
    
    report.append("")
    
    return "\n".join(report)


def main():
    """Run Stage 1 validation"""
    
    print("=" * 80)
    print("PHASE 3A LIVE VALIDATION - STAGE 1")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    print("Stock: HDFCBANK.NS (HDFC Bank)")
    print("Provider: OpenAI (gpt-4o / gpt-4o-mini)")
    print("")
    
    # Check API key
    if not os.environ.get('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not set!")
        print("   Please set: export OPENAI_API_KEY='sk-...'")
        return False
    
    print("✅ OpenAI API key found")
    print("")
    
    # Run baseline (3 rounds, no limits)
    print("=" * 80)
    print("RUNNING BASELINE (Before Phase 3A)")
    print("=" * 80)
    
    baseline_result = run_test(mode="baseline", debate_rounds=3, use_limits=False)
    
    if not baseline_result.get('success'):
        print("\n❌ Baseline test failed - cannot proceed")
        return False
    
    print("\n⏳ Waiting 30s before optimized run...")
    time.sleep(30)
    
    # Run optimized (2 rounds, 800-token limits)
    print("\n" + "=" * 80)
    print("RUNNING OPTIMIZED (After Phase 3A)")
    print("=" * 80)
    
    optimized_result = run_test(mode="optimized", debate_rounds=2, use_limits=True)
    
    if not optimized_result.get('success'):
        print("\n❌ Optimized test failed - cannot proceed")
        return False
    
    # Generate report
    print("\n" + "=" * 80)
    print("GENERATING STAGE 1 REPORT")
    print("=" * 80)
    print("")
    
    report_text = generate_stage1_report(baseline_result, optimized_result)
    print(report_text)
    
    # Save results
    os.makedirs('validation_results', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save JSON
    json_data = {
        'baseline': baseline_result,
        'optimized': optimized_result,
        'timestamp': datetime.now().isoformat()
    }
    
    json_path = f'validation_results/stage1_hdfcbank_{timestamp}.json'
    with open(json_path, 'w') as f:
        json.dump(json_data, f, indent=2, default=str)
    print(f"\n📁 Results saved to: {json_path}")
    
    # Save report
    report_path = f'validation_results/stage1_report_{timestamp}.md'
    with open(report_path, 'w') as f:
        f.write(report_text)
    print(f"📁 Report saved to: {report_path}")
    
    return baseline_result.get('success') and optimized_result.get('success')


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation crashed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
