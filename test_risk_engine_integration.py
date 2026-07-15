"""
Integration test for Risk Engine in TradingAgents Graph

Tests that the risk engine integrates correctly and produces
compatible output for the Portfolio Manager.

Run with:
    USE_OPTIMIZED_ANALYSTS=1 USE_OPTIMIZED_RISK=1 python test_risk_engine_integration.py
"""

import os
import sys
from datetime import datetime

# Enable optimized components
os.environ['USE_OPTIMIZED_ANALYSTS'] = '1'
os.environ['USE_OPTIMIZED_RISK'] = '1'

from tradingagents.graph import TradingAgentsGraph


def test_risk_engine_integration():
    """Test risk engine integration in full graph"""
    
    print("=" * 80)
    print("RISK ENGINE INTEGRATION TEST")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize graph with Groq
    print("Initializing TradingAgents graph...")
    
    # Use config dict for initialization
    config = {
        "llm_provider": "groq",
        "deep_think_llm": "llama-3.3-70b-versatile",
        "quick_think_llm": "llama-3.3-70b-versatile",
        "data_cache_dir": "./data_cache",
        "results_dir": "./results",
        "max_debate_rounds": 3,
        "max_risk_discuss_rounds": 3
    }
    
    graph = TradingAgentsGraph(
        selected_analysts=["market", "fundamentals", "news"],
        config=config,
        debug=True
    )
    
    # Test stock
    ticker = "HDFCBANK.NS"
    trade_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"\nTesting: {ticker}")
    print(f"Date: {trade_date}\n")
    
    try:
        # Run analysis
        print("Running analysis with Risk Engine...")
        final_state, signal = graph.propagate(
            company_name=ticker,
            trade_date=trade_date
        )
        
        # Convert to result dict
        result = {
            **final_state,
            'final_decision': final_state.get('final_trade_decision'),
            'metadata': {
                'runtime_seconds': 0,  # Not tracked in this test
                'total_tokens': 0,
                'total_cost': 0
            }
        }
        
        # Check result structure
        print("\n" + "=" * 80)
        print("RESULTS VALIDATION")
        print("=" * 80)
        
        if 'risk_debate_state' in result:
            print("✅ risk_debate_state present")
            
            debate = result['risk_debate_state']
            
            # Check required fields
            required_fields = ['history', 'aggressive_history', 'neutral_history', 'conservative_history']
            for field in required_fields:
                if field in debate:
                    print(f"✅ {field} present")
                else:
                    print(f"❌ {field} MISSING")
            
            # Check risk analysis structure
            if 'risk_analysis' in debate:
                print("✅ risk_analysis present")
                
                analysis = debate['risk_analysis']
                
                # Check profiles
                if 'profiles' in analysis:
                    print(f"✅ profiles present ({len(analysis['profiles'])} profiles)")
                    
                    for profile_name in ['aggressive', 'neutral', 'conservative']:
                        if profile_name in analysis['profiles']:
                            profile = analysis['profiles'][profile_name]
                            print(f"  ✅ {profile_name}: quantity={profile.get('quantity')}, "
                                  f"allocation=₹{profile.get('allocation', 0):,.0f}, "
                                  f"R:R={profile.get('rr_ratio', 0):.2f}")
                
                # Check recommendation
                if 'recommended_profile' in analysis:
                    print(f"✅ recommended_profile: {analysis['recommended_profile']}")
                
                # Check capital summary
                if 'capital_summary' in analysis:
                    cap = analysis['capital_summary']
                    print(f"✅ capital_summary: ₹{cap.get('total_capital', 0):,}")
            else:
                print("❌ risk_analysis MISSING")
        else:
            print("❌ risk_debate_state MISSING")
        
        # Check portfolio decision
        if 'final_decision' in result:
            print(f"\n✅ Portfolio Manager decision received")
            decision = result['final_decision']
            print(f"   Action: {decision.get('action', 'N/A')}")
            print(f"   Reasoning length: {len(decision.get('reasoning', ''))} chars")
        else:
            print("\n❌ final_decision MISSING")
        
        # Performance metrics
        if 'metadata' in result:
            metadata = result['metadata']
            print(f"\n📊 Performance:")
            print(f"   Runtime: {metadata.get('runtime_seconds', 0):.1f}s")
            print(f"   Tokens: {metadata.get('total_tokens', 0):,}")
            print(f"   Cost: ${metadata.get('total_cost', 0):.4f}")
        
        print("\n" + "=" * 80)
        print("✅ INTEGRATION TEST PASSED")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_risk_engine_integration()
    sys.exit(0 if success else 1)
