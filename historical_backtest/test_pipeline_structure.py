#!/usr/bin/env python3
"""
Quick validation test for Stage 1 pipeline structure

Tests all components without requiring API keys.
Uses mock data to verify the pipeline architecture.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    
    print("=" * 80)
    print("TESTING PIPELINE IMPORTS")
    print("=" * 80)
    
    tests = []
    
    # Test 1: Data collector
    try:
        from data_collection.historical_data_collector import (
            HistoricalDataCollector,
            generate_stage1_trade_dates
        )
        print("✅ Data collector imports OK")
        tests.append(True)
    except Exception as e:
        print(f"❌ Data collector import failed: {e}")
        tests.append(False)
    
    # Test 2: Replay engine
    try:
        from replay_engine.historical_replay import (
            HistoricalReplayEngine,
            SnapshotDataRouter
        )
        print("✅ Replay engine imports OK")
        tests.append(True)
    except Exception as e:
        print(f"❌ Replay engine import failed: {e}")
        tests.append(False)
    
    # Test 3: Execution simulator
    try:
        from execution_simulator.trade_simulator import (
            TradeExecutionSimulator,
            IndianMarketCostCalculator
        )
        print("✅ Execution simulator imports OK")
        tests.append(True)
    except Exception as e:
        print(f"❌ Execution simulator import failed: {e}")
        tests.append(False)
    
    # Test 4: Main pipeline
    try:
        from stage1_pipeline import Stage1Pipeline
        print("✅ Main pipeline imports OK")
        tests.append(True)
    except Exception as e:
        print(f"❌ Main pipeline import failed: {e}")
        tests.append(False)
    
    return all(tests)


def test_components():
    """Test individual components with mock data"""
    
    print("\n" + "=" * 80)
    print("TESTING COMPONENTS")
    print("=" * 80)
    
    tests = []
    
    # Test 1: Trade date generation
    try:
        from data_collection.historical_data_collector import generate_stage1_trade_dates
        
        trade_dates = generate_stage1_trade_dates()
        assert len(trade_dates) == 20, f"Expected 20 dates, got {len(trade_dates)}"
        assert all('ticker' in t and 'date' in t for t in trade_dates)
        
        print("✅ Trade date generation: 20 dates")
        tests.append(True)
    except Exception as e:
        print(f"❌ Trade date generation failed: {e}")
        tests.append(False)
    
    # Test 2: Snapshot router
    try:
        from replay_engine.historical_replay import SnapshotDataRouter
        
        mock_snapshot = {
            'ticker': 'TEST.NS',
            'trade_date': '2024-01-15',
            'market_data': {'data': 'mock_market'},
            'fundamentals_data': {'data': 'mock_fundamentals'},
            'news_data': {'company_news': 'mock_news', 'global_news': 'mock_global'},
            'macro_data': {'indicators': {'cpi': 'mock_cpi'}}
        }
        
        router = SnapshotDataRouter(mock_snapshot)
        
        # Test routing
        market = router.route("get_stock_data", "TEST.NS", "2023-10-15", "2024-01-15")
        assert market == 'mock_market'
        
        news = router.route("get_news", "TEST.NS", "2024-01-08", "2024-01-15")
        assert news == 'mock_news'
        
        print("✅ Snapshot router: Routes to mock data")
        tests.append(True)
    except Exception as e:
        print(f"❌ Snapshot router failed: {e}")
        tests.append(False)
    
    # Test 3: Cost calculator
    try:
        from execution_simulator.trade_simulator import IndianMarketCostCalculator
        
        calc = IndianMarketCostCalculator()
        costs = calc.calculate_costs(
            entry_price=1650.0,
            exit_price=1750.0,
            quantity=50
        )
        
        assert 'brokerage' in costs
        assert 'stt' in costs
        assert 'total' in costs
        assert costs['total'] > 0
        
        print(f"✅ Cost calculator: ₹{costs['total']:.2f} total costs")
        tests.append(True)
    except Exception as e:
        print(f"❌ Cost calculator failed: {e}")
        tests.append(False)
    
    # Test 4: Trade simulator
    try:
        from execution_simulator.trade_simulator import TradeExecutionSimulator
        
        simulator = TradeExecutionSimulator()
        
        mock_recommendation = {
            'trade_id': 'TEST_001',
            'ticker': 'HDFCBANK.NS',
            'trade_date': '2024-01-15',
            'decision': 'BUY',
            'entry': 1650.0,
            'stop': 1575.0,
            'target': 1750.0
        }
        
        mock_snapshot = {'ticker': 'HDFCBANK.NS', 'trade_date': '2024-01-15'}
        
        trade = simulator.execute_trade(mock_recommendation, mock_snapshot)
        
        assert trade['executed'] == True
        assert 'net_pnl' in trade
        assert 'costs' in trade
        
        print(f"✅ Trade simulator: P&L ₹{trade['net_pnl']:,.2f}")
        tests.append(True)
    except Exception as e:
        print(f"❌ Trade simulator failed: {e}")
        tests.append(False)
    
    # Test 5: Pipeline initialization
    try:
        from stage1_pipeline import Stage1Pipeline
        
        pipeline = Stage1Pipeline(output_dir="historical_backtest/test_output")
        
        assert pipeline.output_dir.exists()
        assert (pipeline.output_dir / "snapshots").exists()
        assert (pipeline.output_dir / "agent_outputs").exists()
        assert (pipeline.output_dir / "trades").exists()
        
        print(f"✅ Pipeline init: Output dir {pipeline.output_dir}")
        tests.append(True)
    except Exception as e:
        print(f"❌ Pipeline init failed: {e}")
        tests.append(False)
    
    return all(tests)


def main():
    """Run all tests"""
    
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "STAGE 1 PIPELINE VALIDATION" + " " * 30 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    # Test imports
    imports_ok = test_imports()
    
    # Test components
    components_ok = test_components()
    
    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Imports:    {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"Components: {'✅ PASS' if components_ok else '❌ FAIL'}")
    print()
    
    if imports_ok and components_ok:
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 25 + "✅ ALL TESTS PASSED" + " " * 34 + "║")
        print("╚" + "═" * 78 + "╝")
        print()
        print("Pipeline is ready for testing with real data.")
        print()
        print("Next step:")
        print("  export OPENAI_API_KEY='sk-your-key'")
        print("  python historical_backtest/stage1_pipeline.py")
        return 0
    else:
        print("❌ VALIDATION FAILED")
        print("Fix errors before running full pipeline.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
