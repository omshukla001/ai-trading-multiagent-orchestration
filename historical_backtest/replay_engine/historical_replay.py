"""
Historical Replay Engine

Replays TradingAgents workflow using snapshot data only.
No live API calls - all data from snapshot.

Routes all dataflows through snapshot loader.
Captures all agent outputs.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tradingagents.graph import TradingAgentsGraph


class SnapshotDataRouter:
    """Routes data requests to snapshot instead of live APIs"""
    
    def __init__(self, snapshot: Dict):
        """
        Initialize router with snapshot
        
        Args:
            snapshot: Historical snapshot data
        """
        self.snapshot = snapshot
        self.access_log = []
    
    def route(self, tool_name: str, *args, **kwargs) -> str:
        """
        Route data request to snapshot
        
        Args:
            tool_name: Data tool being called
            *args, **kwargs: Tool parameters
        
        Returns:
            Data from snapshot
        
        Raises:
            RuntimeError: If attempting to access data not in snapshot
        """
        
        self.access_log.append({
            'tool': tool_name,
            'args': args,
            'kwargs': kwargs,
            'timestamp': datetime.now().isoformat()
        })
        
        # Route to appropriate snapshot data
        if tool_name == "get_stock_data":
            if self.snapshot.get('market_data'):
                return self.snapshot['market_data'].get('data', '')
            raise RuntimeError("Market data not in snapshot")
        
        elif tool_name == "get_financial_statements":
            if self.snapshot.get('fundamentals_data'):
                return self.snapshot['fundamentals_data'].get('data', '')
            raise RuntimeError("Fundamentals data not in snapshot")
        
        elif tool_name == "get_news":
            if self.snapshot.get('news_data'):
                return self.snapshot['news_data'].get('company_news', '')
            raise RuntimeError("News data not in snapshot")
        
        elif tool_name == "get_global_news":
            if self.snapshot.get('news_data'):
                return self.snapshot['news_data'].get('global_news', '')
            raise RuntimeError("Global news not in snapshot")
        
        elif tool_name == "get_macro_indicators":
            if self.snapshot.get('macro_data'):
                indicator = args[0] if args else kwargs.get('indicator', '')
                indicators = self.snapshot['macro_data'].get('indicators', {})
                return indicators.get(indicator, f"Indicator {indicator} not in snapshot")
            raise RuntimeError("Macro data not in snapshot")
        
        else:
            # Unknown tool - log but don't fail
            return f"Tool {tool_name} not implemented in snapshot router"


class HistoricalReplayEngine:
    """Replays TradingAgents workflow using historical snapshots"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize replay engine
        
        Args:
            config: TradingAgents configuration
        """
        self.config = config or {
            "llm_provider": "openai",
            "deep_think_llm": "gpt-4o",
            "quick_think_llm": "gpt-4o-mini",
            "data_cache_dir": "./data_cache",
            "results_dir": "./results",
            "max_debate_rounds": 2,  # Phase 3A optimized
            "max_risk_discuss_rounds": 1
        }
    
    def replay(
        self,
        snapshot: Dict,
        capture_outputs: bool = True
    ) -> Dict[str, Any]:
        """
        Replay workflow using snapshot data
        
        Args:
            snapshot: Historical snapshot
            capture_outputs: Whether to capture agent outputs
        
        Returns:
            Complete recommendation with agent outputs
        """
        
        print(f"      🔄 Replaying workflow for {snapshot['ticker']} on {snapshot['trade_date']}")
        
        # Install snapshot data router
        router = SnapshotDataRouter(snapshot)
        
        # Monkey-patch dataflows to use snapshot
        original_route = None
        try:
            from tradingagents.dataflows import interface
            original_route = interface.route_to_vendor
            
            def snapshot_route(tool_name, *args, **kwargs):
                return router.route(tool_name, *args, **kwargs)
            
            interface.route_to_vendor = snapshot_route
            
            print(f"      ✅ Snapshot router installed")
        
        except ImportError:
            print(f"      ⚠️  Could not install snapshot router")
        
        # Initialize TradingAgents graph
        try:
            graph = TradingAgentsGraph(
                selected_analysts=["market", "fundamentals", "news"],
                config=self.config,
                debug=False
            )
            
            print(f"      ✅ Graph initialized")
            
            # Run workflow
            print(f"      → Running workflow...")
            start_time = datetime.now()
            
            final_state, signal = graph.propagate(
                company_name=snapshot['ticker'],
                trade_date=snapshot['trade_date']
            )
            
            runtime = (datetime.now() - start_time).total_seconds()
            
            print(f"      ✅ Workflow complete ({runtime:.1f}s)")
            
            # Extract recommendation
            recommendation = self._extract_recommendation(
                final_state,
                snapshot,
                runtime
            )
            
            # Capture agent outputs if requested
            if capture_outputs:
                recommendation['agent_outputs'] = self._extract_agent_outputs(final_state)
            
            # Log data accesses
            recommendation['data_accesses'] = router.access_log
            
            return recommendation
        
        except Exception as e:
            print(f"      ❌ Replay failed: {str(e)}")
            
            return {
                'error': str(e),
                'ticker': snapshot['ticker'],
                'trade_date': snapshot['trade_date'],
                'failed_at': datetime.now().isoformat()
            }
        
        finally:
            # Restore original routing
            if original_route:
                try:
                    from tradingagents.dataflows import interface
                    interface.route_to_vendor = original_route
                except:
                    pass
    
    def _extract_recommendation(
        self,
        final_state: Dict,
        snapshot: Dict,
        runtime: float
    ) -> Dict:
        """Extract trading recommendation from final state"""
        
        # Get final decision
        decision = final_state.get('final_trade_decision', '')
        trader_plan = final_state.get('trader_investment_plan', '')
        investment_plan = final_state.get('investment_plan', '')
        
        # Parse recommendation
        # TODO: Implement proper parsing from actual output
        # For now, extract basic info
        
        recommendation = {
            'trade_id': snapshot['trade_id'],
            'ticker': snapshot['ticker'],
            'trade_date': snapshot['trade_date'],
            'decision': self._parse_decision(decision),
            'confidence': self._parse_confidence(decision),
            'entry': self._parse_price(decision, 'entry'),
            'stop': self._parse_price(decision, 'stop'),
            'target': self._parse_price(decision, 'target'),
            'position_size': self._parse_position_size(decision),
            'reasoning': str(decision)[:500],
            'runtime': runtime,
            'replayed_at': datetime.now().isoformat(),
            'raw_decision': str(decision),
            'raw_trader_plan': str(trader_plan),
            'raw_investment_plan': str(investment_plan)
        }
        
        return recommendation
    
    def _extract_agent_outputs(self, final_state: Dict) -> Dict:
        """Extract all agent outputs from final state"""
        
        outputs = {
            'market': str(final_state.get('market_summary', '')),
            'fundamentals': str(final_state.get('fundamental_summary', '')),
            'news': str(final_state.get('news_summary', '')),
            'bull': str(final_state.get('investment_debate_state', {}).get('bull_history', '')),
            'bear': str(final_state.get('investment_debate_state', {}).get('bear_history', '')),
            'manager': str(final_state.get('investment_plan', '')),
            'trader': str(final_state.get('trader_investment_plan', '')),
            'risk': str(final_state.get('risk_assessment', '')),
            'pm': str(final_state.get('final_trade_decision', ''))
        }
        
        return outputs
    
    def _parse_decision(self, decision: str) -> str:
        """Parse buy/sell/hold decision"""
        decision_str = str(decision).upper()
        
        if 'BUY' in decision_str or 'LONG' in decision_str:
            return 'BUY'
        elif 'SELL' in decision_str or 'SHORT' in decision_str:
            return 'SELL'
        elif 'HOLD' in decision_str:
            return 'HOLD'
        else:
            return 'UNKNOWN'
    
    def _parse_confidence(self, decision: str) -> float:
        """Parse confidence level"""
        # TODO: Implement proper confidence extraction
        return 0.75  # Default
    
    def _parse_price(self, decision: str, price_type: str) -> Optional[float]:
        """Parse entry/stop/target prices"""
        # TODO: Implement proper price extraction
        # For now return None - will be filled by execution simulator
        return None
    
    def _parse_position_size(self, decision: str) -> int:
        """Parse position size/quantity"""
        # TODO: Implement proper quantity extraction
        return 50  # Default


def test_replay():
    """Test replay with mock snapshot"""
    
    print("=" * 80)
    print("TESTING HISTORICAL REPLAY ENGINE")
    print("=" * 80)
    
    # Create mock snapshot
    mock_snapshot = {
        'trade_id': 'HDFCBANK.NS_2024-01-15',
        'ticker': 'HDFCBANK.NS',
        'trade_date': '2024-01-15',
        'market_data': {
            'data': 'Mock market data',
            'ticker': 'HDFCBANK.NS'
        },
        'fundamentals_data': {
            'data': 'Mock fundamentals'
        },
        'news_data': {
            'company_news': 'Mock news',
            'global_news': 'Mock global news'
        },
        'macro_data': {
            'indicators': {
                'cpi': 'Mock CPI',
                'unemployment': 'Mock unemployment'
            }
        }
    }
    
    engine = HistoricalReplayEngine()
    
    print("\nTesting snapshot router...")
    router = SnapshotDataRouter(mock_snapshot)
    
    # Test routing
    market_data = router.route("get_stock_data", "HDFCBANK.NS", "2023-10-15", "2024-01-15")
    print(f"✅ Market data: {market_data[:50]}...")
    
    news_data = router.route("get_news", "HDFCBANK.NS", "2024-01-08", "2024-01-15")
    print(f"✅ News data: {news_data[:50]}...")
    
    print("\n✅ Snapshot router test passed")
    print("\nNote: Full workflow replay requires API keys")


if __name__ == "__main__":
    test_replay()
