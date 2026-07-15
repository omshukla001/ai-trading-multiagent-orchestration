# Risk Engine Implementation Design

**Component:** Python Risk Engine  
**Version:** 1.0  
**Date:** 2026-07-05

---

## Purpose

Replace the 3 LLM-based risk agents (Aggressive, Neutral, Conservative) with a single deterministic Python Risk Engine that:
- Calculates position sizing mathematically
- Implements 3 risk profiles with different parameters
- Provides structured risk data to Portfolio Manager
- Reduces token usage by ~3,900 tokens per stock
- Improves runtime by ~30-40s per stock

---

## Implementation Strategy

### Drop-in Replacement Design

**Critical Requirement:** Must be compatible with existing workflow.

**Current Flow:**
```
Trader → Risk Debate (3 agents) → Portfolio Manager
```

**New Flow:**
```
Trader → Risk Engine (Python) → Portfolio Manager
```

**Compatibility Points:**
1. Input: Must read same state fields as risk agents
2. Output: Must update `risk_debate_state` in compatible format
3. Integration: Must work with existing graph structure
4. Schema: Portfolio Manager must consume output seamlessly

---

## Module Structure

### File Organization

```python
tradingagents/agents/risk_mgmt/
├── __init__.py
├── risk_engine.py          # Main risk engine
├── risk_profiles.py        # Profile definitions
├── position_calculator.py  # Position sizing math
└── risk_formatter.py       # Output formatting
```

### Class Architecture

```python
# risk_profiles.py
class RiskProfile:
    """Base class for risk profiles"""
    name: str
    risk_percent: float
    max_allocation_percent: float
    stop_multiplier_range: tuple[float, float]
    target_rr_ratio: float

class AggressiveProfile(RiskProfile):
    risk_percent = 0.02  # 2%
    max_allocation_percent = 0.25  # 25%
    stop_multiplier_range = (2.0, 3.0)  # ATR multipliers
    target_rr_ratio = 2.5

class NeutralProfile(RiskProfile):
    risk_percent = 0.015  # 1.5%
    max_allocation_percent = 0.20  # 20%
    stop_multiplier_range = (1.5, 2.0)
    target_rr_ratio = 2.0

class ConservativeProfile(RiskProfile):
    risk_percent = 0.01  # 1%
    max_allocation_percent = 0.125  # 12.5%
    stop_multiplier_range = (1.0, 1.5)
    target_rr_ratio = 1.75

# position_calculator.py
class PositionCalculator:
    """Calculate position sizes and risk metrics"""
    
    def __init__(self, capital: float = 200000):
        self.capital = capital
        self.max_risk_per_trade = 4000
        self.max_active_trades = 4
        self.min_rr_ratio = 1.5
    
    def calculate_position(
        self,
        entry_price: float,
        stop_loss: float,
        target: float,
        profile: RiskProfile,
        atr: float = None
    ) -> dict:
        """Calculate position size, quantity, allocation"""
        pass
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        atr: float,
        profile: RiskProfile,
        trader_stop: float = None
    ) -> float:
        """Calculate optimal stop loss"""
        pass
    
    def calculate_targets(
        self,
        entry_price: float,
        stop_loss: float,
        profile: RiskProfile
    ) -> tuple[float, float]:
        """Calculate target prices"""
        pass

# risk_engine.py
class RiskEngine:
    """Main risk engine coordinator"""
    
    def __init__(self):
        self.calculator = PositionCalculator()
        self.profiles = {
            'aggressive': AggressiveProfile(),
            'neutral': NeutralProfile(),
            'conservative': ConservativeProfile()
        }
    
    def analyze(self, state: dict) -> dict:
        """Main analysis method - returns risk_debate_state"""
        pass
    
    def extract_inputs(self, state: dict) -> dict:
        """Extract needed data from state"""
        pass
    
    def generate_risk_factors(self, context: dict) -> list[str]:
        """Generate risk factor list"""
        pass
    
    def generate_supporting_factors(self, context: dict) -> list[str]:
        """Generate supporting factor list"""
        pass
    
    def format_output(self, analysis: dict) -> dict:
        """Format for Portfolio Manager consumption"""
        pass

# risk_formatter.py
class RiskFormatter:
    """Format risk analysis for Portfolio Manager"""
    
    def format_debate_style(self, analysis: dict) -> dict:
        """Format as if from debate agents"""
        pass
    
    def generate_narrative(self, profile_name: str, data: dict) -> str:
        """Generate textual explanation"""
        pass
```

---

## Detailed Algorithm

### Input Extraction

```python
def extract_inputs(state: dict) -> dict:
    """
    Extract all necessary data from workflow state
    """
    # From trader proposal
    trader_plan = state.get("trader_investment_plan", "")
    
    # Parse trader proposal for structured data
    action = extract_action(trader_plan)  # Buy/Hold/Sell
    entry_price = extract_entry_price(trader_plan)
    stop_loss = extract_stop_loss(trader_plan)
    
    # From market analyst (optimized)
    market_report = state.get("market_report", {})
    if isinstance(market_report, dict):
        atr = market_report.get("indicators", {}).get("atr")
        current_price = market_report.get("indicators", {}).get("close")
        trend = market_report.get("trend")
        trend_strength = market_report.get("trend_strength", 0.5)
    
    # From fundamentals analyst (optimized)
    fundamentals_report = state.get("fundamentals_report", {})
    if isinstance(fundamentals_report, dict):
        fundamental_score = fundamentals_report.get("overall_score", 0.5)
    
    # From research analysis
    investment_plan = state.get("investment_plan", "")
    
    # Aggregate confidence
    confidence = calculate_confidence(
        trend_strength,
        fundamental_score,
        action
    )
    
    return {
        "action": action,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "current_price": current_price,
        "atr": atr,
        "trend": trend,
        "confidence": confidence,
        "trader_plan": trader_plan
    }
```

### Position Size Calculation

```python
def calculate_position(
    entry_price: float,
    stop_loss: float,
    target: float,
    profile: RiskProfile,
    capital: float = 200000
) -> dict:
    """
    Calculate position size using risk-based formula
    """
    # 1. Calculate risk amount
    risk_amount = min(
        capital * profile.risk_percent,
        4000  # Hard cap
    )
    
    # 2. Calculate price risk per share
    price_risk = abs(entry_price - stop_loss)
    
    if price_risk == 0:
        return None  # Invalid setup
    
    # 3. Calculate quantity
    quantity = math.floor(risk_amount / price_risk)
    
    # 4. Calculate allocation
    allocation = quantity * entry_price
    
    # 5. Check allocation limit
    max_allocation = capital * profile.max_allocation_percent
    if allocation > max_allocation:
        # Reduce quantity to fit allocation limit
        quantity = math.floor(max_allocation / entry_price)
        allocation = quantity * entry_price
        risk_amount = quantity * price_risk
    
    # 6. Calculate actual risk percent
    actual_risk_percent = (risk_amount / capital) * 100
    
    # 7. Calculate R:R ratio
    reward = target - entry_price
    risk = entry_price - stop_loss
    rr_ratio = reward / risk if risk > 0 else 0
    
    # 8. Calculate max loss
    max_loss = quantity * price_risk
    
    return {
        "allocation": round(allocation, 2),
        "quantity": quantity,
        "risk_amount": round(risk_amount, 2),
        "risk_percent": round(actual_risk_percent, 2),
        "stop_loss": round(stop_loss, 2),
        "entry_price": round(entry_price, 2),
        "target": round(target, 2),
        "rr_ratio": round(rr_ratio, 2),
        "max_loss": round(max_loss, 2)
    }
```

### Stop Loss Calculation

```python
def calculate_stop_loss(
    entry_price: float,
    atr: float,
    profile: RiskProfile,
    trader_stop: float = None,
    action: str = "Buy"
) -> float:
    """
    Calculate optimal stop loss based on ATR and profile
    """
    if trader_stop is not None:
        # Use trader's stop as base
        return trader_stop
    
    if atr is None or atr == 0:
        # Fallback to percentage-based stop
        if action == "Buy":
            return entry_price * 0.92  # 8% stop
        else:
            return entry_price * 1.08
    
    # Use ATR-based stop
    min_mult, max_mult = profile.stop_multiplier_range
    multiplier = (min_mult + max_mult) / 2  # Average
    
    stop_distance = atr * multiplier
    
    if action == "Buy":
        stop_loss = entry_price - stop_distance
    else:
        stop_loss = entry_price + stop_distance
    
    return round(stop_loss, 2)
```

### Target Calculation

```python
def calculate_targets(
    entry_price: float,
    stop_loss: float,
    profile: RiskProfile,
    action: str = "Buy"
) -> tuple[float, float]:
    """
    Calculate target prices based on R:R ratio
    """
    risk = abs(entry_price - stop_loss)
    
    # Target 1: Minimum R:R
    reward_1 = risk * profile.target_rr_ratio
    
    # Target 2: Extended R:R (add 50%)
    reward_2 = risk * (profile.target_rr_ratio * 1.5)
    
    if action == "Buy":
        target_1 = entry_price + reward_1
        target_2 = entry_price + reward_2
    else:
        target_1 = entry_price - reward_1
        target_2 = entry_price - reward_2
    
    return (
        round(target_1, 2),
        round(target_2, 2)
    )
```

### Risk Factor Generation

```python
def generate_risk_factors(context: dict) -> list[str]:
    """
    Generate list of risk considerations
    """
    factors = []
    
    # Volatility risk
    if context.get("atr"):
        atr_percent = (context["atr"] / context["entry_price"]) * 100
        if atr_percent > 3:
            factors.append(f"High volatility (ATR: {atr_percent:.1f}%)")
        elif atr_percent < 1:
            factors.append(f"Low volatility (ATR: {atr_percent:.1f}%)")
    
    # Stop loss distance
    stop_distance = abs(
        context["entry_price"] - context["stop_loss"]
    ) / context["entry_price"] * 100
    
    if stop_distance > 10:
        factors.append(f"Wide stop loss ({stop_distance:.1f}% from entry)")
    elif stop_distance < 3:
        factors.append(f"Tight stop loss ({stop_distance:.1f}% from entry)")
    
    # Market condition
    trend = context.get("trend", "Unknown")
    factors.append(f"Market trend: {trend}")
    
    # Confidence level
    confidence = context.get("confidence", 0.5)
    if confidence < 0.6:
        factors.append(f"Moderate confidence ({confidence:.2f})")
    
    # Action-specific risks
    if context["action"] == "Buy":
        factors.append("Long position - exposed to downside risk")
    elif context["action"] == "Sell":
        factors.append("Short position - exposed to upside risk")
    
    return factors
```

### Supporting Factor Generation

```python
def generate_supporting_factors(context: dict) -> list[str]:
    """
    Generate list of supporting considerations
    """
    factors = []
    
    # Confidence
    confidence = context.get("confidence", 0.5)
    if confidence > 0.7:
        factors.append(f"Strong analyst confidence: {confidence:.2f}")
    
    # Risk/Reward
    rr_ratio = context.get("rr_ratio", 0)
    if rr_ratio >= 2.0:
        factors.append(f"Favorable risk/reward: {rr_ratio:.1f}:1")
    
    # Trend alignment
    trend = context.get("trend", "")
    action = context.get("action", "")
    
    if (trend == "Bullish" and action == "Buy") or \
       (trend == "Bearish" and action == "Sell"):
        factors.append("Trade aligned with market trend")
    
    # Technical signals
    if context.get("technical_signals"):
        factors.extend(context["technical_signals"][:2])  # Top 2
    
    return factors
```

---

## Output Format

### Structure for Portfolio Manager

The Risk Engine must output in a format the Portfolio Manager can consume.

**Current Portfolio Manager expects:**
```python
risk_debate_state = {
    "history": str,  # Full debate text
    "aggressive_history": str,
    "conservative_history": str,
    "neutral_history": str,
    "current_aggressive_response": str,
    "current_conservative_response": str,
    "current_neutral_response": str,
    "count": int
}
```

**Risk Engine Output:**
```python
{
    "risk_debate_state": {
        "history": formatted_summary,  # Structured summary
        "aggressive_history": aggressive_analysis,
        "conservative_history": conservative_analysis,
        "neutral_history": neutral_analysis,
        "current_aggressive_response": aggressive_text,
        "current_conservative_response": conservative_text,
        "current_neutral_response": neutral_text,
        "count": 1,  # Always 1 (no debate rounds)
        "latest_speaker": "Risk Engine",
        
        # NEW: Structured data for PM
        "risk_analysis": {
            "profiles": {
                "aggressive": {...},
                "neutral": {...},
                "conservative": {...}
            },
            "risk_factors": [...],
            "supporting_factors": [...],
            "recommended_profile": "neutral"
        }
    }
}
```

### Text Generation for History Fields

```python
def generate_profile_narrative(profile_name: str, data: dict) -> str:
    """
    Generate debate-style text from structured data
    """
    template = f"""
{profile_name.title()} Risk Analyst:

Based on the trader's proposal and market analysis, here is my {profile_name} risk assessment:

**Position Sizing:**
- Recommended Allocation: ₹{data['allocation']:,}
- Quantity: {data['quantity']} shares
- Entry Price: ₹{data['entry_price']}
- Stop Loss: ₹{data['stop_loss']}

**Risk Metrics:**
- Risk Amount: ₹{data['risk_amount']:,} ({data['risk_percent']}% of capital)
- Maximum Loss: ₹{data['max_loss']:,}
- Risk/Reward Ratio: {data['rr_ratio']}:1

**Targets:**
- Target 1: ₹{data['target_1']} ({((data['target_1']/data['entry_price']-1)*100):.1f}% gain)
- Target 2: ₹{data['target_2']} ({((data['target_2']/data['entry_price']-1)*100):.1f}% gain)

**Rationale:**
This {profile_name} approach balances {"aggressive growth" if profile_name == "aggressive" else "conservative safety" if profile_name == "conservative" else "moderate risk-taking"} with prudent risk management. The position size ensures we risk no more than {data['risk_percent']}% of capital while maintaining a favorable {data['rr_ratio']}:1 risk/reward ratio.
"""
    return template.strip()
```

---

## Integration with Graph

### Modify `setup.py`

```python
# In tradingagents/graph/setup.py

from tradingagents.agents.risk_mgmt.risk_engine import create_risk_engine

class GraphSetup:
    def setup_graph(self, selected_analysts=...):
        # ... existing code ...
        
        # Create risk engine (Python)
        risk_engine_node = create_risk_engine()
        
        # Add risk engine node
        workflow.add_node("Risk Engine", risk_engine_node)
        
        # Connect: Trader → Risk Engine → Portfolio Manager
        workflow.add_edge("Trader", "Risk Engine")
        workflow.add_edge("Risk Engine", "Portfolio Manager")
        
        # REMOVE old risk agents:
        # - Aggressive Analyst
        # - Neutral Analyst
        # - Conservative Analyst
```

### Create Risk Engine Node

```python
# In tradingagents/agents/risk_mgmt/risk_engine.py

def create_risk_engine():
    """
    Factory function to create risk engine node
    Compatible with existing LangGraph architecture
    """
    engine = RiskEngine()
    
    def risk_engine_node(state: dict) -> dict:
        """
        Main node function called by LangGraph
        """
        try:
            # Run risk analysis
            result = engine.analyze(state)
            
            return {
                "risk_debate_state": result
            }
            
        except Exception as e:
            # Fallback with error
            return {
                "risk_debate_state": {
                    "history": f"Risk Engine Error: {str(e)}",
                    "aggressive_history": "",
                    "conservative_history": "",
                    "neutral_history": "",
                    "current_aggressive_response": "",
                    "current_conservative_response": "",
                    "current_neutral_response": "",
                    "count": 1,
                    "error": str(e)
                }
            }
    
    return risk_engine_node
```

---

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_risk_engine.py

def test_position_calculation():
    """Test position size calculation"""
    calc = PositionCalculator(capital=200000)
    
    result = calc.calculate_position(
        entry_price=1500,
        stop_loss=1425,
        target=1650,
        profile=NeutralProfile()
    )
    
    assert result['quantity'] > 0
    assert result['allocation'] <= 40000  # 20% of 200k
    assert result['risk_amount'] <= 3000  # 1.5% of 200k
    assert result['rr_ratio'] >= 1.5

def test_stop_loss_calculation():
    """Test stop loss calculation"""
    calc = PositionCalculator()
    
    stop = calc.calculate_stop_loss(
        entry_price=1500,
        atr=35,
        profile=NeutralProfile(),
        action="Buy"
    )
    
    assert stop < 1500  # Stop below entry for Buy
    assert stop > 1400  # Reasonable range

def test_risk_profiles():
    """Test all three risk profiles"""
    profiles = [
        AggressiveProfile(),
        NeutralProfile(),
        ConservativeProfile()
    ]
    
    # Aggressive should have highest risk
    assert profiles[0].risk_percent > profiles[1].risk_percent
    assert profiles[1].risk_percent > profiles[2].risk_percent
    
    # Aggressive should have highest allocation
    assert profiles[0].max_allocation_percent > profiles[2].max_allocation_percent

def test_output_schema():
    """Test output matches expected schema"""
    engine = RiskEngine()
    
    state = create_mock_state()
    result = engine.analyze(state)
    
    assert "history" in result
    assert "aggressive_history" in result
    assert "risk_analysis" in result
    assert "profiles" in result["risk_analysis"]
    assert "aggressive" in result["risk_analysis"]["profiles"]
```

### Integration Tests

```python
# tests/integration/test_risk_engine_integration.py

def test_risk_engine_in_workflow():
    """Test risk engine works in full workflow"""
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    
    config = get_test_config()
    ta = TradingAgentsGraph(config=config)
    
    _, decision = ta.propagate("HDFCBANK.NS", "2026-06-30")
    
    assert decision is not None
    # Risk engine should have executed successfully

def test_portfolio_manager_consumption():
    """Test Portfolio Manager can consume risk engine output"""
    # Verify PM gets structured risk data
    pass
```

---

## Migration Plan

### Step 1: Build Risk Engine Module
1. Create `risk_engine.py`
2. Create `risk_profiles.py`
3. Create `position_calculator.py`
4. Create `risk_formatter.py`

### Step 2: Write Tests
1. Write unit tests
2. Write integration tests
3. Ensure 80%+ coverage

### Step 3: Integrate into Graph
1. Modify `setup.py`
2. Remove old risk agents
3. Add risk engine node
4. Update edges

### Step 4: Validation
1. Test on 5 stocks
2. Compare output with old system
3. Verify Portfolio Manager compatibility
4. Measure performance improvement

### Step 5: Documentation
1. Update API docs
2. Update user guide
3. Add migration notes

---

## Expected Results

### Performance Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Token Usage | ~3,900 | 0 | 100% |
| Runtime | ~30-40s | <0.5s | ~99% |
| Cost | ~$0.0025 | $0 | 100% |
| LLM Calls | 3 | 0 | 100% |

### Code Quality

- ✅ Deterministic calculations
- ✅ Testable logic
- ✅ Fast execution
- ✅ Maintainable code
- ✅ Clear documentation

---

## Next Actions

1. ✅ Design complete
2. → Implement Risk Engine modules
3. → Write comprehensive tests
4. → Integrate into workflow
5. → Validate performance
6. → Document and deploy

---

**Status:** Design complete - Ready for implementation  
**Next:** Begin coding Risk Engine modules
