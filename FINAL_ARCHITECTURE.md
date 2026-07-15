# TradingAgents - Final Production Architecture

**Version:** 2.0 - Optimized  
**Date:** 2026-07-05  
**Type:** AI-Assisted Trading Decision Support System

---

## System Objective

Build a professional analysis framework that:
- Provides systematic multi-factor analysis
- Reduces emotional bias in trading decisions
- Implements consistent risk management
- Improves signal quality through multi-agent reasoning
- Optimizes for cost, speed, and decision quality

**This is a decision support tool, NOT an automated trading system.**

---

## Architecture Overview

### Current State (Before Optimization)

**9 LLM Agents:**
1. Market Analyst (LLM)
2. Fundamentals Analyst (LLM)
3. News Analyst (LLM)
4. Bull Researcher (LLM)
5. Bear Researcher (LLM)
6. Research Manager (LLM)
7. Aggressive Risk Analyst (LLM)
8. Neutral Risk Analyst (LLM)
9. Conservative Risk Analyst (LLM)
10. Trader (LLM)
11. Portfolio Manager (LLM)

**Problems:**
- High token usage (~15-20k per stock)
- Slow runtime (~200-250s per stock)
- Expensive (~$0.015-0.020 per stock)
- Redundant calculations in deterministic components

### Target State (After Optimization)

**3 Python Agents + 6 LLM Agents = 9 Total**

**Python Agents (0 LLM calls):**
1. ✅ Market Analyst → Pure Python technical analysis
2. ✅ Fundamentals Analyst → Pure Python ratio calculations
3. ✅ Risk Engine → Pure Python position sizing

**LLM Agents (Preserved for reasoning):**
4. News Analyst → Strategic news interpretation
5. Bull Researcher → Bullish case development
6. Bear Researcher → Bearish case development
7. Research Manager → Synthesis & investment plan
8. Trader → Concrete transaction proposal
9. Portfolio Manager → Final decision synthesis

**Benefits:**
- Token reduction: ~45-50% (15-20k → 8-10k)
- Runtime reduction: ~30-40% (200-250s → 120-150s)
- Cost reduction: ~50% ($0.015-0.020 → $0.007-0.010)
- Improved consistency in technical/fundamental analysis
- Preserved strategic reasoning quality

---

## Detailed Component Architecture

### PYTHON LAYER (Deterministic Analysis)

#### 1. Market Analyst (Python)

**Purpose:** Technical analysis using rule-based indicators

**Inputs:**
- Stock symbol
- Date range
- Historical OHLCV data

**Calculations:**
```python
Technical Indicators:
- RSI (14): Momentum oscillator
- MACD (12,26,9): Trend & momentum
- EMA (20, 50, 200): Trend identification
- Bollinger Bands (20, 2): Volatility & extremes
- ATR (14): Volatility measurement
- Volume Analysis: Breakout confirmation
- Support/Resistance: Key price levels

Trend Classification:
- Strong Bullish: EMA20 > EMA50 > EMA200, RSI > 60
- Bullish: EMA20 > EMA50, RSI 50-70
- Neutral: Mixed signals, RSI 40-60
- Bearish: EMA20 < EMA50, RSI 30-50
- Strong Bearish: EMA20 < EMA50 < EMA200, RSI < 40
```

**Output Schema:**
```python
{
    "trend": "Bullish",
    "trend_strength": 0.75,
    "indicators": {
        "rsi": 64.2,
        "macd": 12.5,
        "macd_signal": 10.3,
        "macd_hist": 2.2,
        "ema_20": 1450.5,
        "ema_50": 1420.3,
        "ema_200": 1380.0,
        "bb_upper": 1480.0,
        "bb_middle": 1450.0,
        "bb_lower": 1420.0,
        "atr": 35.0,
        "volume_ratio": 1.35
    },
    "support_levels": [1420, 1400, 1380],
    "resistance_levels": [1480, 1500, 1520],
    "signals": [
        "RSI in bullish zone (60-70)",
        "MACD bullish crossover",
        "Price above all EMAs",
        "Volume 35% above average"
    ],
    "confidence": 0.75,
    "report": "Technical analysis report text..."
}
```

**Token Usage:** 0 (Python)  
**Runtime:** ~1-2s

#### 2. Fundamentals Analyst (Python)

**Purpose:** Financial ratio analysis and valuation

**Inputs:**
- Stock symbol
- Date
- Financial statements data

**Calculations:**
```python
Valuation Metrics:
- P/E Ratio: Price to Earnings
- P/B Ratio: Price to Book
- PEG Ratio: P/E to Growth
- P/S Ratio: Price to Sales

Profitability:
- Profit Margin: Net profit / Revenue
- Operating Margin: Operating profit / Revenue
- ROE: Return on Equity
- ROA: Return on Assets

Financial Health:
- Debt/Equity Ratio
- Current Ratio: Current assets / Current liabilities
- Quick Ratio: (Current assets - Inventory) / Current liabilities

Growth:
- Revenue Growth (YoY)
- EPS Growth (YoY)
- Profit Growth (YoY)

Cash Flow:
- Free Cash Flow
- Operating Cash Flow
```

**Output Schema:**
```python
{
    "valuation_score": 0.70,
    "profitability_score": 0.80,
    "health_score": 0.85,
    "growth_score": 0.65,
    "overall_score": 0.75,
    "metrics": {
        "pe_ratio": 25.3,
        "pb_ratio": 4.2,
        "peg_ratio": 1.8,
        "profit_margin": 0.18,
        "operating_margin": 0.22,
        "roe": 0.20,
        "roa": 0.12,
        "debt_equity": 0.45,
        "current_ratio": 1.8,
        "revenue_growth": 0.15,
        "eps_growth": 0.18
    },
    "strengths": [
        "Strong ROE (20%)",
        "Healthy margins",
        "Low debt levels"
    ],
    "concerns": [
        "P/E slightly elevated",
        "Growth slowing"
    ],
    "confidence": 0.75,
    "report": "Fundamental analysis report text..."
}
```

**Token Usage:** 0 (Python)  
**Runtime:** ~0.5-1s

#### 3. Risk Engine (Python)

**Purpose:** Position sizing and risk management

**Inputs:**
- Capital: ₹200,000
- Entry price
- Stop loss price
- Target prices
- Current price
- ATR (volatility)
- Confidence score
- Market condition

**Risk Rules:**
```python
Capital: ₹200,000
Max Risk per Trade: 2% (₹4,000)
Max Active Trades: 4
Minimum Risk/Reward: 1:2
Stop Loss Buffer: 1-3 ATR based on profile
```

**Calculations:**
```python
1. Risk Amount:
   risk_amount = min(
       capital * risk_percent,
       max_risk_per_trade
   )

2. Position Size:
   price_risk = abs(entry_price - stop_loss)
   quantity = floor(risk_amount / price_risk)

3. Capital Allocation:
   allocation = quantity * entry_price

4. Risk/Reward Ratio:
   risk = entry_price - stop_loss
   reward = target - entry_price
   rr_ratio = reward / risk

5. Volatility Adjustment:
   stop_distance = atr * multiplier
   adjusted_stop = entry - stop_distance
```

**Risk Profiles:**

| Profile | Risk % | Max Allocation | Stop Loss | Target |
|---------|--------|----------------|-----------|--------|
| Aggressive | 2.0% | 25% (₹50k) | 2-3 ATR | R:R 1:2.5 |
| Neutral | 1.5% | 20% (₹40k) | 1.5-2 ATR | R:R 1:2 |
| Conservative | 1.0% | 12.5% (₹25k) | 1-1.5 ATR | R:R 1:1.5 |

**Output Schema:**
```python
{
    "profiles": {
        "aggressive": {
            "allocation": 50000,
            "quantity": 35,
            "risk_amount": 4000,
            "risk_percent": 2.0,
            "stop_loss": 1380.0,
            "entry_price": 1500.0,
            "target_1": 1650.0,
            "target_2": 1750.0,
            "rr_ratio": 2.5,
            "max_loss": 4000
        },
        "neutral": {
            "allocation": 40000,
            "quantity": 28,
            "risk_amount": 3000,
            "risk_percent": 1.5,
            "stop_loss": 1400.0,
            "entry_price": 1500.0,
            "target_1": 1600.0,
            "target_2": 1680.0,
            "rr_ratio": 2.0,
            "max_loss": 3000
        },
        "conservative": {
            "allocation": 25000,
            "quantity": 18,
            "risk_amount": 2000,
            "risk_percent": 1.0,
            "stop_loss": 1420.0,
            "entry_price": 1500.0,
            "target_1": 1570.0,
            "target_2": 1630.0,
            "rr_ratio": 1.75,
            "max_loss": 2000
        }
    },
    "risk_factors": [
        "High volatility (ATR: 35)",
        "Stop loss 8% below entry",
        "Market condition: Neutral"
    ],
    "supporting_factors": [
        "Strong analyst confidence: 0.85",
        "Positive risk/reward: 2:1 minimum",
        "Volume above average"
    ],
    "recommended_profile": "neutral"
}
```

**Token Usage:** 0 (Python)  
**Runtime:** ~0.1s

---

### LLM LAYER (Strategic Reasoning)

#### 4. News Analyst (LLM)

**Purpose:** Interpret market news and sentiment

**Preserved because:**
- News interpretation requires contextual understanding
- Sentiment analysis beyond keyword matching
- Cross-reference multiple sources
- Identify hidden implications

**Token Usage:** ~1,200-1,500  
**Runtime:** ~10-15s

#### 5-6. Bull & Bear Researchers (LLM)

**Purpose:** Develop competing investment theses

**Preserved because:**
- Strategic argument construction
- Scenario analysis
- Challenge assumptions
- Devil's advocate reasoning
- This debate improves decision quality

**Token Usage:** ~2,000-2,500 (both)  
**Runtime:** ~20-25s (both)

#### 7. Research Manager (LLM)

**Purpose:** Synthesize research into coherent plan

**Preserved because:**
- Strategic synthesis
- Weighing conflicting evidence
- Holistic assessment
- Investment plan formulation

**Token Usage:** ~1,500-2,000  
**Runtime:** ~15-20s

#### 8. Trader (LLM)

**Purpose:** Convert plan to concrete proposal

**Preserved because:**
- Tactical decision-making
- Entry/exit timing strategy
- Position sizing judgment
- Practical execution planning

**Token Usage:** ~800-1,000  
**Runtime:** ~10-12s

#### 9. Portfolio Manager (LLM)

**Purpose:** Final decision synthesis

**Preserved because:**
- Holistic judgment
- Risk/reward assessment
- Strategic timing
- Final conviction rating

**Token Usage:** ~1,500-2,000  
**Runtime:** ~15-20s

---

## Workflow Architecture

### Complete Analysis Flow

```
┌─────────────────────────────────────────────────────┐
│            DATA GATHERING (Parallel)                │
│                                                     │
│  • Market Data (yfinance)                          │
│  • News Data (APIs)                                │
│  • Fundamental Data (financial APIs)               │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│         PYTHON ANALYSIS LAYER (Parallel)            │
│                                                     │
│  Market Analyst ────┐                              │
│  (Python)           │                              │
│  • Technical        │                              │
│  • Indicators       │                              │
│  • Trend            │                              │
│                     ├──→ Combined Context          │
│  Fundamentals ──────┤                              │
│  Analyst (Python)   │                              │
│  • Ratios           │                              │
│  • Valuation        │                              │
│  • Health           │                              │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│            LLM STRATEGIC ANALYSIS                   │
│                                                     │
│  News Analyst (LLM)                                │
│  • Market sentiment                                 │
│  • News interpretation                              │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│          RESEARCH DEBATE (Parallel)                 │
│                                                     │
│  Bull Researcher ──────┐                           │
│  (LLM)                 │                           │
│  • Bullish case        │                           │
│  • Growth scenarios    ├──→ Competing Theses       │
│                        │                           │
│  Bear Researcher ──────┘                           │
│  (LLM)                                             │
│  • Bearish case                                    │
│  • Risk scenarios                                  │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│          SYNTHESIS & PLANNING                       │
│                                                     │
│  Research Manager (LLM)                            │
│  • Weigh evidence                                  │
│  • Synthesize plan                                 │
│  • Strategic direction                             │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│            RISK MANAGEMENT (Python)                 │
│                                                     │
│  Risk Engine                                        │
│  • Position sizing                                  │
│  • Stop loss calculation                            │
│  • 3 risk profiles                                  │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│          TRADE EXECUTION PLANNING                   │
│                                                     │
│  Trader (LLM)                                      │
│  • Concrete proposal                                │
│  • Entry/exit levels                                │
│  • Sizing recommendation                            │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│            FINAL DECISION                           │
│                                                     │
│  Portfolio Manager (LLM)                           │
│  • Final rating                                     │
│  • Executive summary                                │
│  • Investment thesis                                │
│  • Risk factors                                     │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│         STRUCTURED OUTPUT                           │
│                                                     │
│  • Buy/Hold/Sell recommendation                    │
│  • Entry/Stop/Target levels                        │
│  • Position size & quantity                        │
│  • Risk profile selection                          │
│  • Confidence score                                 │
│  • Detailed reasoning                               │
└─────────────────────────────────────────────────────┘
```

---

## Performance Targets

### Current Performance (Before Optimization)

| Metric | Value |
|--------|-------|
| Total LLM Agents | 11 |
| Python Agents | 0 |
| Token Usage | ~15-20k per stock |
| Runtime | ~200-250s |
| Cost (Groq) | ~$0.015-0.020 |
| API Calls | ~11+ |

### Target Performance (After Optimization)

| Metric | Target | Expected |
|--------|--------|----------|
| Total Agents | 9 | 9 (3 Python + 6 LLM) |
| Token Usage | <10k | ~8-10k |
| Runtime | <150s | ~120-150s |
| Cost (Groq) | <$0.010 | ~$0.007-0.010 |
| API Calls | <8 | ~6-7 |

### Improvement

| Metric | Improvement |
|--------|-------------|
| Token Reduction | ~45-50% |
| Runtime Reduction | ~30-40% |
| Cost Reduction | ~50% |
| Agent Count | -2 agents |
| Code Efficiency | Significantly improved |

---

## Testing Architecture

### 1. Unit Tests

**Test Each Python Component:**

```python
test_market_analyst.py:
- test_rsi_calculation()
- test_macd_calculation()
- test_ema_calculation()
- test_bollinger_bands()
- test_atr_calculation()
- test_trend_classification()
- test_support_resistance()
- test_volume_analysis()
- test_output_schema()

test_fundamentals_analyst.py:
- test_pe_ratio_calculation()
- test_valuation_metrics()
- test_profitability_ratios()
- test_health_ratios()
- test_growth_calculations()
- test_score_aggregation()
- test_output_schema()

test_risk_engine.py:
- test_position_size_calculation()
- test_risk_amount_calculation()
- test_stop_loss_calculation()
- test_target_calculation()
- test_rr_ratio()
- test_aggressive_profile()
- test_neutral_profile()
- test_conservative_profile()
- test_capital_limits()
- test_output_schema()
```

### 2. Integration Tests

**Test Full Workflow:**

```python
test_full_workflow.py:
- test_workflow_completion()
- test_agent_compatibility()
- test_state_propagation()
- test_output_consistency()
- test_error_handling()
- test_edge_cases()

test_agent_integration.py:
- test_python_to_llm_handoff()
- test_llm_to_python_handoff()
- test_risk_engine_integration()
- test_portfolio_manager_integration()
```

### 3. Performance Tests

**Benchmark Performance:**

```python
test_performance.py:
- test_runtime_per_stock()
- test_token_usage()
- test_api_call_count()
- test_cost_calculation()
- test_parallel_execution()
- test_cache_effectiveness()
```

### 4. Historical Analysis

**Analyze Historical Behavior:**

```python
test_historical.py:
- test_signal_consistency()
- test_recommendation_distribution()
- test_risk_calculation_accuracy()
- test_stop_loss_effectiveness()
- test_target_achievement_rate()
```

### 5. Validation Tests

**Test Decision Quality:**

```python
test_validation.py:
- test_recommendation_rationale()
- test_confidence_calibration()
- test_risk_alignment()
- test_signal_strength_correlation()
```

---

## Indian Market Integration

### Stock Exchanges

**NSE (National Stock Exchange):**
- Primary exchange
- Symbol format: `SYMBOL.NS`
- Examples: `HDFCBANK.NS`, `INFY.NS`, `RELIANCE.NS`

**BSE (Bombay Stock Exchange):**
- Secondary exchange
- Symbol format: `SYMBOL.BO`
- Examples: `HDFCBANK.BO`, `INFY.BO`

### Commodities (MCX)

**Metals:**
- Gold: `GC=F` (international proxy)
- Silver: `SI=F` (international proxy)

**Energy:**
- Crude Oil: `CL=F` (international proxy)

### Benchmarks

**Replace SPY with:**
- NIFTY 50: `^NSEI`
- SENSEX: `^BSESN`

### News Sources

**Indian Financial News:**
- Moneycontrol API
- Economic Times
- Business Standard
- Mint
- Reuters India

---

## Implementation Plan

### Phase 1: Risk Engine Implementation
1. ✅ Design Python Risk Engine
2. Create `risk_engine.py` module
3. Implement 3 risk profiles
4. Add unit tests
5. Integrate into graph

### Phase 2: Testing Framework
1. Set up pytest infrastructure
2. Write unit tests for all Python components
3. Write integration tests
4. Write performance benchmarks
5. Create validation framework

### Phase 3: Validation Testing
1. Test on 10 diverse stocks
2. Measure runtime, tokens, cost
3. Validate output consistency
4. Test error handling
5. Performance optimization

### Phase 4: Historical Analysis
1. Gather historical data (60-90 days)
2. Run analysis on historical dates
3. Track signal characteristics
4. Analyze decision patterns
5. Generate validation report

### Phase 5: Documentation & Deployment
1. API documentation
2. User guide
3. Configuration guide
4. Deployment scripts
5. Monitoring setup

---

## Success Metrics

### Technical Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Runtime | <150s | Performance tests |
| Token Usage | <10k | API monitoring |
| Cost per Stock | <$0.010 | Cost tracking |
| API Calls | <8 | Call counter |
| Test Coverage | >80% | Pytest coverage |

### Quality Metrics

| Metric | Measurement |
|--------|-------------|
| Signal Consistency | Historical analysis |
| Decision Coherence | Integration tests |
| Risk Alignment | Validation tests |
| Output Validity | Schema validation |
| Error Rate | Production monitoring |

---

## File Structure

```
tradingagents/
├── tradingagents/
│   ├── agents/
│   │   ├── analysts/
│   │   │   ├── market_analyst_optimized.py ✅
│   │   │   ├── fundamentals_analyst_optimized.py ✅
│   │   │   └── analyst_utils.py
│   │   ├── risk_mgmt/
│   │   │   ├── risk_engine.py (NEW)
│   │   │   └── risk_profiles.py (NEW)
│   │   └── ...
│   ├── graph/
│   │   ├── setup.py (MODIFY - integrate risk engine)
│   │   └── ...
│   └── ...
├── tests/
│   ├── unit/
│   │   ├── test_market_analyst.py
│   │   ├── test_fundamentals_analyst.py
│   │   └── test_risk_engine.py
│   ├── integration/
│   │   ├── test_full_workflow.py
│   │   └── test_agent_integration.py
│   ├── performance/
│   │   └── test_performance.py
│   └── validation/
│       └── test_historical.py
├── docs/
│   ├── FINAL_ARCHITECTURE.md
│   ├── RISK_LAYER_AUDIT.md
│   ├── API_DOCUMENTATION.md
│   └── USER_GUIDE.md
└── ...
```

---

## Next Steps

1. **Immediate:** Design and implement Python Risk Engine
2. **Next:** Build comprehensive testing framework
3. **Then:** Validation testing on diverse stocks
4. **Finally:** Historical analysis and documentation

---

## Disclaimer

This system is a decision support tool for systematic analysis. It does not guarantee profitability or predict future market movements. All trading involves substantial risk of loss. Users should:

- Exercise independent judgment
- Understand the risks
- Use appropriate position sizing
- Maintain diversification
- Consider their risk tolerance
- Consult qualified advisors

Past performance (including historical analysis) does not guarantee future results.

---

**Status:** Architecture validated - Ready for implementation  
**Next:** PHASE 2 - Risk Engine Implementation Design
