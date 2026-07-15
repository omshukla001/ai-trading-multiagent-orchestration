"""
Test Risk Engine Output Format

Validates that the risk engine produces output compatible with Portfolio Manager
without running the full workflow or making API calls.
"""

import os
os.environ['USE_OPTIMIZED_RISK'] = '1'

from tradingagents.agents.risk_mgmt import create_risk_engine


def test_risk_engine_output_format():
    """Test risk engine output structure and format"""
    
    print("=" * 80)
    print("RISK ENGINE OUTPUT FORMAT TEST")
    print("=" * 80 + "\n")
    
    # Create risk engine node
    risk_engine_node = create_risk_engine()
    
    # Mock state from trader
    mock_state = {
        "trade_date": "2026-07-05",
        "ticker": "HDFCBANK.NS",
        "trader_investment_plan": """
            **Action**: Buy
            **Entry Price**: ₹1,500.00
            **Stop Loss**: ₹1,425.00 (5% below entry)
            **Target**: ₹1,650.00 (10% above entry, 2:1 R:R)
            **Reasoning**: Strong bullish momentum with RSI at 65, above 50-day MA.
            **Position Sizing**: Allocate 5% of portfolio
        """,
        "market_report": {
            "trend": "Bullish",
            "trend_strength": 0.75,
            "indicators": {
                "close": 1495,
                "atr": 35.5,
                "rsi": 65,
                "ma_50": 1450
            }
        },
        "fundamentals_report": {
            "overall_score": 0.70,
            "valuation_score": 0.65,
            "growth_score": 0.75
        }
    }
    
    print("Executing risk engine with mock trader state...")
    result = risk_engine_node(mock_state)
    
    # Validate output structure
    print("\n" + "=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80 + "\n")
    
    passed_checks = 0
    total_checks = 0
    
    def check(condition, description):
        nonlocal passed_checks, total_checks
        total_checks += 1
        if condition:
            print(f"✅ {description}")
            passed_checks += 1
            return True
        else:
            print(f"❌ {description}")
            return False
    
    # Check top-level structure
    check('risk_debate_state' in result, "risk_debate_state present")
    
    if 'risk_debate_state' in result:
        debate = result['risk_debate_state']
        
        # Check required fields for Portfolio Manager
        check('history' in debate, "history field present")
        check('aggressive_history' in debate, "aggressive_history field present")
        check('neutral_history' in debate, "neutral_history field present")
        check('conservative_history' in debate, "conservative_history field present")
        check('risk_analysis' in debate, "risk_analysis field present")
        
        # Check history format
        if 'history' in debate:
            check(isinstance(debate['history'], list), "history is a list")
            check(len(debate['history']) > 0, "history contains entries")
        
        # Check risk analysis structure
        if 'risk_analysis' in debate:
            analysis = debate['risk_analysis']
            
            check('profiles' in analysis, "profiles present in analysis")
            check('recommended_profile' in analysis, "recommended_profile present")
            check('risk_factors' in analysis, "risk_factors present")
            check('supporting_factors' in analysis, "supporting_factors present")
            check('capital_summary' in analysis, "capital_summary present")
            
            # Check profiles
            if 'profiles' in analysis:
                profiles = analysis['profiles']
                check('aggressive' in profiles, "aggressive profile present")
                check('neutral' in profiles, "neutral profile present")
                check('conservative' in profiles, "conservative profile present")
                
                # Check aggressive profile structure
                if 'aggressive' in profiles:
                    agg = profiles['aggressive']
                    check('quantity' in agg, "aggressive.quantity present")
                    check('allocation' in agg, "aggressive.allocation present")
                    check('stop_loss' in agg, "aggressive.stop_loss present")
                    check('target_1' in agg, "aggressive.target_1 present")
                    check('target_2' in agg, "aggressive.target_2 present")
                    check('max_loss' in agg, "aggressive.max_loss present")
                    check('rr_ratio' in agg, "aggressive.rr_ratio present")
                    
                    # Check values are reasonable
                    if 'quantity' in agg:
                        check(agg['quantity'] > 0, f"aggressive.quantity > 0 ({agg['quantity']})")
                    if 'allocation' in agg:
                        check(0 < agg['allocation'] <= 50000, 
                              f"aggressive.allocation reasonable (₹{agg['allocation']:,.0f})")
                    if 'rr_ratio' in agg:
                        check(agg['rr_ratio'] >= 1.5, 
                              f"aggressive.rr_ratio >= 1.5 ({agg['rr_ratio']:.2f})")
            
            # Check capital summary
            if 'capital_summary' in analysis:
                cap = analysis['capital_summary']
                check('total_capital' in cap, "capital_summary.total_capital present")
                check('max_risk_per_trade' in cap, "capital_summary.max_risk_per_trade present")
                check('max_active_trades' in cap, "capital_summary.max_active_trades present")
                
                if 'total_capital' in cap:
                    check(cap['total_capital'] == 200000, 
                          f"capital = ₹2,00,000 ({cap['total_capital']:,})")
                if 'max_risk_per_trade' in cap:
                    check(cap['max_risk_per_trade'] == 4000,
                          f"max risk = ₹4,000 ({cap['max_risk_per_trade']:,})")
    
    # Print summary
    print("\n" + "=" * 80)
    print(f"SUMMARY: {passed_checks}/{total_checks} checks passed")
    print("=" * 80)
    
    if passed_checks == total_checks:
        print("\n✅ ALL TESTS PASSED - Risk Engine output format is correct!")
        return True
    else:
        print(f"\n❌ {total_checks - passed_checks} checks failed")
        return False


if __name__ == "__main__":
    import sys
    success = test_risk_engine_output_format()
    sys.exit(0 if success else 1)
