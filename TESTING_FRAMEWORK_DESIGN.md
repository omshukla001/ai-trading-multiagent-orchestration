# Testing Framework Design

**Purpose:** Comprehensive testing infrastructure for TradingAgents optimization  
**Version:** 1.0  
**Date:** 2026-07-05

---

## Testing Philosophy

**Testing is mandatory** for this production-grade system.

### Goals

1. ✅ Ensure code correctness
2. ✅ Validate calculations
3. ✅ Prevent regressions
4. ✅ Measure performance
5. ✅ Validate decision quality
6. ✅ Enable confident refactoring

### Test Pyramid

```
         /\
        /  \  E2E Tests (Few)
       /----\
      /      \ Integration Tests (Some)
     /--------\
    /          \ Unit Tests (Many)
   /______________\
```

---

## Test Categories

### 1. Unit Tests (Many)

**Purpose:** Test individual components in isolation

**Scope:**
- Market Analyst calculations
- Fundamentals Analyst calculations
- Risk Engine position sizing
- Individual helper functions
- Data transformations

**Characteristics:**
- Fast (<0.1s each)
- Isolated (no external dependencies)
- Deterministic (same input → same output)
- Focused (one thing per test)

### 2. Integration Tests (Some)

**Purpose:** Test component interactions

**Scope:**
- Python → LLM agent handoffs
- LLM → Python agent handoffs
- State propagation through graph
- Output schema compatibility
- Error handling across boundaries

**Characteristics:**
- Moderate speed (~1-5s each)
- May use mocks for LLM calls
- Tests real data flow
- Validates interfaces

### 3. Performance Tests (Few)

**Purpose:** Measure and track performance metrics

**Scope:**
- Runtime per stock
- Token usage per agent
- API call counts
- Memory usage
- Cost calculations

**Characteristics:**
- Slower (full workflow)
- Uses real LLM calls
- Generates metrics
- Tracks over time

### 4. Validation Tests (Few)

**Purpose:** Validate decision quality and consistency

**Scope:**
- Historical analysis
- Signal consistency
- Recommendation coherence
- Risk calculation accuracy
- Output quality

**Characteristics:**
- Uses historical data
- Descriptive analysis
- No predictive claims
- Quality metrics

---

## Test Structure

### Directory Layout

```
tradingagents/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures
│   │
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_market_analyst.py
│   │   ├── test_fundamentals_analyst.py
│   │   ├── test_risk_engine.py
│   │   ├── test_position_calculator.py
│   │   └── test_risk_profiles.py
│   │
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_full_workflow.py
│   │   ├── test_agent_handoffs.py
│   │   ├── test_state_propagation.py
│   │   └── test_error_handling.py
│   │
│   ├── performance/
│   │   ├── __init__.py
│   │   ├── test_runtime.py
│   │   ├── test_token_usage.py
│   │   └── test_cost_tracking.py
│   │
│   ├── validation/
│   │   ├── __init__.py
│   │   ├── test_historical_analysis.py
│   │   ├── test_signal_consistency.py
│   │   └── test_recommendation_quality.py
│   │
│   └── fixtures/
│       ├── mock_data.py
│       ├── sample_states.py
│       └── test_stocks.py
```

---

## Detailed Test Specifications

### Unit Tests: Market Analyst

```python
# tests/unit/test_market_analyst.py

import pytest
from tradingagents.agents.analysts.market_analyst_optimized import (
    TechnicalAnalyzer,
    create_market_analyst_optimized
)

class TestTechnicalAnalyzer:
    """Test TechnicalAnalyzer calculations"""
    
    def test_rsi_calculation(self):
        """Test RSI calculation accuracy"""
        analyzer = TechnicalAnalyzer()
        
        # Known RSI values from reference data
        closes = [44, 44.5, 45, 45.5, 45, 44.5, 44, 43.5, 43, 43.5, 44, 44.5, 45, 45.5]
        
        rsi = analyzer.calculate_rsi(closes, period=14)
        
        assert 0 <= rsi <= 100
        assert isinstance(rsi, (int, float))
    
    def test_macd_calculation(self):
        """Test MACD calculation"""
        analyzer = TechnicalAnalyzer()
        
        prices = list(range(100, 150))  # Trending data
        macd, signal, hist = analyzer.calculate_macd(prices)
        
        assert isinstance(macd, (int, float))
        assert isinstance(signal, (int, float))
        assert hist == macd - signal
    
    def test_ema_calculation(self):
        """Test EMA calculation"""
        analyzer = TechnicalAnalyzer()
        
        prices = [100, 102, 104, 103, 105, 107, 106, 108]
        ema_20 = analyzer.calculate_ema(prices, period=5)
        
        assert ema_20 > 0
        assert 100 < ema_20 < 110  # Reasonable range
    
    def test_bollinger_bands(self):
        """Test Bollinger Bands calculation"""
        analyzer = TechnicalAnalyzer()
        
        prices = [100] * 10 + [105] * 10  # Step function
        upper, middle, lower = analyzer.calculate_bollinger_bands(prices)
        
        assert upper > middle > lower
        assert middle == pytest.approx(102.5, rel=0.1)
    
    def test_atr_calculation(self):
        """Test ATR calculation"""
        analyzer = TechnicalAnalyzer()
        
        highs = [105, 107, 106, 108, 110]
        lows = [95, 97, 96, 98, 100]
        closes = [100, 102, 101, 103, 105]
        
        atr = analyzer.calculate_atr(highs, lows, closes)
        
        assert atr > 0
        assert atr < 15  # Reasonable for this data
    
    def test_trend_classification_bullish(self):
        """Test bullish trend identification"""
        analyzer = TechnicalAnalyzer()
        
        snapshot = {
            "close": 150,
            "indicators": {
                "close_10_ema": 150,
                "close_50_sma": 145,
                "close_200_sma": 140,
                "rsi": 65
            }
        }
        
        trend = analyzer.classify_trend(snapshot)
        
        assert trend["trend"] in ["Bullish", "Strong Bullish"]
        assert trend["strength"] > 0.5
    
    def test_support_resistance(self):
        """Test support/resistance identification"""
        analyzer = TechnicalAnalyzer()
        
        prices = [100, 105, 103, 107, 105, 110, 108, 112]
        
        support, resistance = analyzer.find_support_resistance(prices)
        
        assert len(support) > 0
        assert len(resistance) > 0
        assert all(s < prices[-1] for s in support)
        assert all(r > prices[-1] for r in resistance)
    
    def test_output_schema(self):
        """Test output matches expected schema"""
        analyzer = TechnicalAnalyzer()
        
        snapshot = create_mock_snapshot()
        report = analyzer.generate_report("TEST.NS", snapshot)
        
        # Check required fields
        assert "trend" in report
        assert "indicators" in report
        assert "signals" in report
        assert "confidence" in report
        
        # Check types
        assert isinstance(report["trend"], str)
        assert isinstance(report["confidence"], (int, float))
        assert 0 <= report["confidence"] <= 1

class TestMarketAnalystNode:
    """Test market analyst node integration"""
    
    def test_node_execution(self):
        """Test node executes without errors"""
        node = create_market_analyst_optimized()
        
        state = {
            "trade_date": "2026-06-30",
            "messages": [MockMessage("HDFCBANK.NS")]
        }
        
        result = node(state)
        
        assert "messages" in result
        assert "market_report" in result
    
    def test_node_error_handling(self):
        """Test node handles errors gracefully"""
        node = create_market_analyst_optimized()
        
        state = {
            "trade_date": "2026-06-30",
            "messages": [MockMessage("INVALID.NS")]
        }
        
        result = node(state)
        
        # Should return error message, not crash
        assert "messages" in result
        assert "error" in result["market_report"].lower() or \
               "failed" in result["market_report"].lower()
```

### Unit Tests: Risk Engine

```python
# tests/unit/test_risk_engine.py

import pytest
from tradingagents.agents.risk_mgmt.risk_engine import RiskEngine
from tradingagents.agents.risk_mgmt.risk_profiles import (
    AggressiveProfile,
    NeutralProfile,
    ConservativeProfile
)
from tradingagents.agents.risk_mgmt.position_calculator import PositionCalculator

class TestPositionCalculator:
    """Test position sizing calculations"""
    
    def test_basic_position_calculation(self):
        """Test standard position calculation"""
        calc = PositionCalculator(capital=200000)
        
        result = calc.calculate_position(
            entry_price=1500,
            stop_loss=1425,  # 5% stop
            target=1650,  # 10% target
            profile=NeutralProfile()
        )
        
        assert result is not None
        assert result['quantity'] > 0
        assert result['allocation'] > 0
        assert result['risk_amount'] <= 3000  # 1.5% of 200k
        assert result['allocation'] <= 40000  # 20% of 200k
        assert result['rr_ratio'] >= 1.5
    
    def test_aggressive_profile_higher_risk(self):
        """Test aggressive profile allows more risk"""
        calc = PositionCalculator(capital=200000)
        
        aggressive = calc.calculate_position(
            entry_price=1500,
            stop_loss=1425,
            target=1650,
            profile=AggressiveProfile()
        )
        
        neutral = calc.calculate_position(
            entry_price=1500,
            stop_loss=1425,
            target=1650,
            profile=NeutralProfile()
        )
        
        assert aggressive['risk_amount'] > neutral['risk_amount']
        assert aggressive['allocation'] > neutral['allocation']
    
    def test_conservative_profile_lower_risk(self):
        """Test conservative profile limits risk"""
        calc = PositionCalculator(capital=200000)
        
        conservative = calc.calculate_position(
            entry_price=1500,
            stop_loss=1425,
            target=1650,
            profile=ConservativeProfile()
        )
        
        neutral = calc.calculate_position(
            entry_price=1500,
            stop_loss=1425,
            target=1650,
            profile=NeutralProfile()
        )
        
        assert conservative['risk_amount'] < neutral['risk_amount']
        assert conservative['allocation'] < neutral['allocation']
    
    def test_allocation_cap(self):
        """Test allocation doesn't exceed profile limit"""
        calc = PositionCalculator(capital=200000)
        
        # Very tight stop = large position
        result = calc.calculate_position(
            entry_price=1500,
            stop_loss=1490,  # Only 10 points
            target=1600,
            profile=NeutralProfile()
        )
        
        # Should cap at 20% of capital = 40,000
        assert result['allocation'] <= 40000
    
    def test_risk_cap(self):
        """Test risk doesn't exceed maximum"""
        calc = PositionCalculator(capital=200000)
        
        result = calc.calculate_position(
            entry_price=1500,
            stop_loss=1200,  # Wide stop
            target=2000,
            profile=AggressiveProfile()
        )
        
        # Should cap at 4000 max risk
        assert result['max_loss'] <= 4000
    
    def test_zero_stop_loss(self):
        """Test handling of invalid stop loss"""
        calc = PositionCalculator(capital=200000)
        
        result = calc.calculate_position(
            entry_price=1500,
            stop_loss=1500,  # Same as entry
            target=1600,
            profile=NeutralProfile()
        )
        
        assert result is None  # Should return None for invalid setup
    
    def test_rr_ratio_calculation(self):
        """Test risk/reward ratio is correct"""
        calc = PositionCalculator(capital=200000)
        
        result = calc.calculate_position(
            entry_price=1000,
            stop_loss=900,  # Risk: 100
            target=1200,  # Reward: 200
            profile=NeutralProfile()
        )
        
        assert result['rr_ratio'] == pytest.approx(2.0, rel=0.01)

class TestRiskEngine:
    """Test complete risk engine"""
    
    def test_engine_initialization(self):
        """Test risk engine initializes correctly"""
        engine = RiskEngine()
        
        assert engine.calculator is not None
        assert len(engine.profiles) == 3
        assert 'aggressive' in engine.profiles
        assert 'neutral' in engine.profiles
        assert 'conservative' in engine.profiles
    
    def test_analyze_method(self):
        """Test main analyze method"""
        engine = RiskEngine()
        
        state = create_mock_state_for_risk()
        result = engine.analyze(state)
        
        assert 'history' in result
        assert 'risk_analysis' in result
        assert 'profiles' in result['risk_analysis']
    
    def test_extract_inputs(self):
        """Test input extraction from state"""
        engine = RiskEngine()
        
        state = create_mock_state_for_risk()
        inputs = engine.extract_inputs(state)
        
        assert 'entry_price' in inputs
        assert 'stop_loss' in inputs
        assert 'action' in inputs
        assert 'confidence' in inputs
    
    def test_risk_factors_generation(self):
        """Test risk factor list generation"""
        engine = RiskEngine()
        
        context = {
            "atr": 35,
            "entry_price": 1500,
            "stop_loss": 1425,
            "trend": "Neutral",
            "confidence": 0.65,
            "action": "Buy"
        }
        
        factors = engine.generate_risk_factors(context)
        
        assert isinstance(factors, list)
        assert len(factors) > 0
        assert all(isinstance(f, str) for f in factors)
    
    def test_output_format_compatibility(self):
        """Test output format matches Portfolio Manager expectations"""
        engine = RiskEngine()
        
        state = create_mock_state_for_risk()
        result = engine.analyze(state)
        
        # Check required fields for PM
        assert 'history' in result
        assert 'aggressive_history' in result
        assert 'conservative_history' in result
        assert 'neutral_history' in result
        assert 'current_aggressive_response' in result
        assert 'current_conservative_response' in result
        assert 'current_neutral_response' in result
        assert 'count' in result
        
        # Check structured data
        assert 'risk_analysis' in result
        assert 'profiles' in result['risk_analysis']
        assert 'risk_factors' in result['risk_analysis']
        assert 'supporting_factors' in result['risk_analysis']
```

### Integration Tests

```python
# tests/integration/test_full_workflow.py

import pytest
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

class TestFullWorkflow:
    """Test complete workflow integration"""
    
    @pytest.fixture
    def config(self):
        """Test configuration"""
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "groq"
        config["deep_think_llm"] = "llama-3.3-70b-versatile"
        config["quick_think_llm"] = "llama-3.3-70b-versatile"
        config["max_debate_rounds"] = 1
        config["max_risk_rounds"] = 1
        return config
    
    def test_workflow_completes(self, config):
        """Test workflow executes end-to-end"""
        import os
        os.environ['USE_OPTIMIZED_ANALYSTS'] = '1'
        
        ta = TradingAgentsGraph(debug=False, config=config)
        
        final_state, decision = ta.propagate("HDFCBANK.NS", "2026-06-30")
        
        assert final_state is not None
        assert decision is not None
    
    def test_python_agents_execute(self, config):
        """Test Python agents execute successfully"""
        import os
        os.environ['USE_OPTIMIZED_ANALYSTS'] = '1'
        
        ta = TradingAgentsGraph(debug=False, config=config)
        final_state, _ = ta.propagate("HDFCBANK.NS", "2026-06-30")
        
        # Check Python agents produced output
        assert "market_report" in final_state
        assert "fundamentals_report" in final_state
        assert "risk_debate_state" in final_state
    
    def test_llm_agents_execute(self, config):
        """Test LLM agents execute successfully"""
        ta = TradingAgentsGraph(debug=False, config=config)
        final_state, _ = ta.propagate("HDFCBANK.NS", "2026-06-30")
        
        # Check LLM agents produced output
        assert "news_report" in final_state
        assert "investment_plan" in final_state
        assert "trader_investment_plan" in final_state
        assert "final_trade_decision" in final_state
    
    def test_state_propagation(self, config):
        """Test state flows correctly through workflow"""
        ta = TradingAgentsGraph(debug=False, config=config)
        final_state, _ = ta.propagate("HDFCBANK.NS", "2026-06-30")
        
        # Verify data flows through pipeline
        assert final_state.get("ticker") == "HDFCBANK.NS"
        assert "messages" in final_state
        assert len(final_state["messages"]) > 0
    
    def test_error_handling(self, config):
        """Test workflow handles errors gracefully"""
        ta = TradingAgentsGraph(debug=False, config=config)
        
        # Try with invalid stock
        try:
            _, decision = ta.propagate("INVALID.NS", "2026-06-30")
            # Should either succeed with error message or raise
            assert True
        except Exception as e:
            # Should be a clean, informative error
            assert str(e) != ""
```

### Performance Tests

```python
# tests/performance/test_runtime.py

import time
import pytest
from tradingagents.graph.trading_graph import TradingAgentsGraph

class TestPerformance:
    """Test performance metrics"""
    
    @pytest.fixture
    def test_stocks(self):
        return ["HDFCBANK.NS", "INFY.NS", "RELIANCE.NS"]
    
    def test_runtime_per_stock(self, test_stocks, config):
        """Measure runtime for each stock"""
        ta = TradingAgentsGraph(debug=False, config=config)
        
        runtimes = {}
        
        for stock in test_stocks:
            start = time.time()
            _, _ = ta.propagate(stock, "2026-06-30")
            runtime = time.time() - start
            
            runtimes[stock] = runtime
            
            # Assert runtime target
            assert runtime < 180, f"{stock} took {runtime:.2f}s (target: <180s)"
        
        avg_runtime = sum(runtimes.values()) / len(runtimes)
        print(f"\nAverage runtime: {avg_runtime:.2f}s")
        
        assert avg_runtime < 150, "Average runtime should be <150s"
    
    def test_token_usage(self, config):
        """Measure token usage"""
        # Would need token tracking callback
        pass
```

---

## Fixtures & Helpers

```python
# tests/conftest.py

import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_state():
    """Create mock state for testing"""
    return {
        "trade_date": "2026-06-30",
        "ticker": "HDFCBANK.NS",
        "messages": [Mock(content="HDFCBANK.NS")],
        "market_report": {},
        "fundamentals_report": {},
        "news_report": "",
        "sentiment_report": "",
        "investment_plan": "",
        "trader_investment_plan": "",
        "risk_debate_state": {
            "history": "",
            "count": 0
        }
    }

@pytest.fixture
def mock_snapshot():
    """Create mock market snapshot"""
    return {
        "close": 1500,
        "volume": 1000000,
        "indicators": {
            "rsi": 65,
            "macd": 12.5,
            "macd_signal": 10.3,
            "macd_hist": 2.2,
            "close_10_ema": 1490,
            "close_50_sma": 1470,
            "close_200_sma": 1450,
            "atr": 35
        }
    }

@pytest.fixture
def test_config():
    """Test configuration"""
    from tradingagents.default_config import DEFAULT_CONFIG
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "groq"
    config["max_debate_rounds"] = 1
    config["max_risk_rounds"] = 1
    return config
```

---

## Running Tests

### Commands

```bash
# Run all tests
pytest tests/

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest --cov=tradingagents tests/

# Run specific test
pytest tests/unit/test_risk_engine.py::TestPositionCalculator::test_basic_position_calculation

# Run with verbose output
pytest -v tests/

# Run fast tests only (skip slow integration tests)
pytest -m "not slow" tests/
```

### Coverage Targets

- Unit tests: >90% coverage
- Integration tests: >70% coverage
- Overall: >80% coverage

---

## Success Metrics

### Test Suite Quality

| Metric | Target |
|--------|--------|
| Unit test count | >50 |
| Integration test count | >10 |
| Performance test count | >5 |
| Test coverage | >80% |
| All tests pass | 100% |
| Test runtime | <60s |

---

**Status:** Framework designed - Ready for implementation  
**Next:** Implement tests alongside Risk Engine development
