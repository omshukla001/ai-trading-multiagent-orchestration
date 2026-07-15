# Risk Layer Audit - TradingAgents

**Date:** 2026-07-05  
**Phase:** PHASE 1 - Risk Layer Analysis  
**Goal:** Understand current risk workflow to enable Python optimization

---

## Current Risk Architecture

### Workflow

```
Market + Fundamentals + News Analysts
            ↓
    Bull Researcher
    Bear Researcher
            ↓
    Research Manager
            ↓
        Trader
            ↓
    ┌───────────────────┐
    │   RISK LAYER      │
    │                   │
    │ • Aggressive      │
    │ • Neutral         │
    │ • Conservative    │
    └───────────────────┘
            ↓
    Portfolio Manager
```

### Risk Layer Components

**3 Separate LLM Agents:**
1. Aggressive Risk Analyst
2. Neutral Risk Analyst  
3. Conservative Risk Analyst

**Debate Flow:**
- Agents debate in rounds (max: `max_risk_rounds`)
- Each agent responds to other agents' arguments
- Maintains conversation history
- Portfolio Manager synthesizes debate into final decision

---

## Agent 1: Aggressive Risk Analyst

### **Inputs**

| Input | Source | Purpose |
|-------|--------|---------|
| `trader_decision` | Trader agent output | Transaction proposal to evaluate |
| `market_research_report` | Market Analyst | Technical analysis, trends, indicators |
| `sentiment_report` | Social Media Analyst | Reddit, StockTwits sentiment |
| `news_report` | News Analyst | Latest market news, world affairs |
| `fundamentals_report` | Fundamentals Analyst | Financial ratios, company health |
| `instrument_context` | State metadata | Ticker, date, market context |
| `history` | Risk debate state | Full conversation history |
| `aggressive_history` | Risk debate state | Own previous arguments |
| `current_conservative_response` | Conservative agent | Latest conservative argument |
| `current_neutral_response` | Neutral agent | Latest neutral argument |

### **Role & Logic**

**Personality:** High-reward, high-risk champion

**Unique Logic:**
- Emphasizes **potential upside** and **growth potential**
- Challenges **conservative** and **neutral** caution
- Argues for **bold strategies** despite elevated risk
- Counters opposing views with **data-driven rebuttals**
- Highlights where caution might **miss opportunities**

**Reasoning Pattern:**
```
1. Read trader's proposal
2. Identify high-reward opportunities
3. Counter conservative/neutral concerns
4. Use market data to justify aggressive stance
5. Challenge assumptions of other analysts
6. Advocate for risk-taking to outpace market
```

### **Output Format**

```python
{
    "risk_debate_state": {
        "history": str,                      # Full debate history
        "aggressive_history": str,           # Own arguments
        "conservative_history": str,         # Conservative's arguments
        "neutral_history": str,              # Neutral's arguments
        "latest_speaker": "Aggressive",
        "current_aggressive_response": str,  # Latest argument
        "current_conservative_response": str,
        "current_neutral_response": str,
        "count": int                         # Debate round counter
    }
}
```

**Typical Token Usage:**
- Input: ~800-1,200 tokens (context + history)
- Output: ~200-400 tokens (argument)
- **Total: ~1,200 tokens per call**

---

## Agent 2: Neutral Risk Analyst

### **Inputs**

| Input | Source | Purpose |
|-------|--------|---------|
| `trader_decision` | Trader agent output | Transaction proposal to evaluate |
| `market_research_report` | Market Analyst | Technical analysis |
| `sentiment_report` | Social Media Analyst | Sentiment data |
| `news_report` | News Analyst | Market news |
| `fundamentals_report` | Fundamentals Analyst | Financial metrics |
| `instrument_context` | State metadata | Context |
| `history` | Risk debate state | Full conversation |
| `neutral_history` | Risk debate state | Own arguments |
| `current_aggressive_response` | Aggressive agent | Latest aggressive argument |
| `current_conservative_response` | Conservative agent | Latest conservative argument |

### **Role & Logic**

**Personality:** Balanced mediator

**Unique Logic:**
- Provides **balanced perspective** between extremes
- Weighs **both benefits and risks** equally
- Challenges **both** aggressive and conservative views
- Points out where each side is **overly optimistic/cautious**
- Advocates for **moderate, sustainable strategy**
- Considers **broader market trends** and **diversification**

**Reasoning Pattern:**
```
1. Analyze trader's proposal objectively
2. Identify weaknesses in aggressive arguments
3. Identify weaknesses in conservative arguments
4. Propose balanced middle-ground approach
5. Use data to support moderation
6. Advocate for growth with risk safeguards
```

### **Output Format**

```python
{
    "risk_debate_state": {
        "history": str,
        "aggressive_history": str,
        "conservative_history": str,
        "neutral_history": str,              # Own arguments
        "latest_speaker": "Neutral",
        "current_aggressive_response": str,
        "current_conservative_response": str,
        "current_neutral_response": str,     # Latest argument
        "count": int
    }
}
```

**Typical Token Usage:**
- Input: ~800-1,200 tokens
- Output: ~200-400 tokens
- **Total: ~1,200 tokens per call**

---

## Agent 3: Conservative Risk Analyst

### **Inputs**

| Input | Source | Purpose |
|-------|--------|---------|
| `trader_decision` | Trader agent output | Transaction proposal to evaluate |
| `market_research_report` | Market Analyst | Technical data |
| `sentiment_report` | Social Media Analyst | Sentiment |
| `news_report` | News Analyst | News |
| `fundamentals_report` | Fundamentals Analyst | Fundamentals |
| `instrument_context` | State metadata | Context |
| `history` | Risk debate state | Full conversation |
| `conservative_history` | Risk debate state | Own arguments |
| `current_aggressive_response` | Aggressive agent | Latest aggressive argument |
| `current_neutral_response` | Neutral agent | Latest neutral argument |

### **Role & Logic**

**Personality:** Asset protector, risk minimizer

**Unique Logic:**
- Prioritizes **stability**, **security**, **risk mitigation**
- Examines **potential losses** and **downside scenarios**
- Critically assesses **high-risk elements**
- Points out where decisions may **expose to undue risk**
- Suggests **cautious alternatives** for long-term gains
- Counters aggressive/neutral optimism with **threat analysis**

**Reasoning Pattern:**
```
1. Evaluate trader's proposal for risks
2. Identify potential threats and losses
3. Challenge aggressive/neutral optimism
4. Highlight overlooked downsides
5. Advocate for stability over growth
6. Propose risk-mitigated alternatives
```

### **Output Format**

```python
{
    "risk_debate_state": {
        "history": str,
        "aggressive_history": str,
        "conservative_history": str,         # Own arguments
        "neutral_history": str,
        "latest_speaker": "Conservative",
        "current_aggressive_response": str,
        "current_conservative_response": str, # Latest argument
        "current_neutral_response": str,
        "count": int
    }
}
```

**Typical Token Usage:**
- Input: ~800-1,200 tokens
- Output: ~200-400 tokens
- **Total: ~1,200 tokens per call**

---

## Portfolio Manager Consumption

### **How Risk Debate is Used**

The Portfolio Manager receives the **complete risk debate history** and synthesizes it into a final decision.

### **Inputs from Risk Layer**

```python
{
    "risk_debate_state": {
        "history": str,                    # FULL debate transcript
        "aggressive_history": str,         # All aggressive arguments
        "conservative_history": str,       # All conservative arguments
        "neutral_history": str,            # All neutral arguments
        "current_aggressive_response": str,
        "current_conservative_response": str,
        "current_neutral_response": str,
        "count": int
    }
}
```

**Key Point:** Portfolio Manager uses the **full textual debate** to make decisions, NOT structured risk calculations.

### **Portfolio Manager Logic**

```
1. Reads trader's proposal
2. Reads research manager's investment plan
3. Reads FULL risk debate history
4. Synthesizes all viewpoints
5. Makes final decision (Buy/Overweight/Hold/Underweight/Sell)
6. Provides executive summary and investment thesis
```

### **Output Schema**

```python
class PortfolioDecision(BaseModel):
    rating: PortfolioRating              # Buy/Overweight/Hold/Underweight/Sell
    executive_summary: str               # 2-4 sentence action plan
    investment_thesis: str               # Detailed reasoning
    price_target: float | None
    time_horizon: str | None
    confidence_level: str | None
    risk_factors: list[str] | None
    supporting_factors: list[str] | None
```

---

## Analysis: Shared vs Unique Logic

### **Shared Logic Across All 3 Agents**

| Aspect | Common Pattern |
|--------|----------------|
| **Inputs** | All receive identical data: trader proposal, analyst reports, instrument context |
| **Data Sources** | All use: market report, sentiment, news, fundamentals |
| **Debate Mechanism** | All respond to other agents' arguments |
| **History Tracking** | All maintain conversation history |
| **Output Format** | All update `risk_debate_state` dict |
| **Token Pattern** | All consume ~1,200 tokens per call |
| **Core Task** | All evaluate the same trader proposal |

### **Unique Logic Per Agent**

| Agent | Unique Perspective | Reasoning Focus |
|-------|-------------------|-----------------|
| **Aggressive** | High-risk, high-reward | Upside potential, growth opportunities, challenge caution |
| **Neutral** | Balanced moderation | Weigh pros and cons, critique both extremes |
| **Conservative** | Risk minimization | Downside protection, stability, threat analysis |

### **The Key Insight**

**The differences are PURELY in tone and argumentation style, NOT in calculations.**

All three agents:
- Receive the same inputs
- Access the same data
- Perform the same task (evaluate trader proposal)
- Output conversational arguments

**None of them perform quantitative risk calculations** like:
- Position sizing formulas
- Risk/reward ratios
- Capital allocation math
- Stop-loss calculations
- Volatility adjustments

---

## Redundant LLM Reasoning

### **Problem 1: Identical Inputs**

All 3 agents receive and process:
- Market report (~500-800 tokens)
- Sentiment report (~300-500 tokens)
- News report (~400-600 tokens)
- Fundamentals report (~300-500 tokens)
- Trader proposal (~200-300 tokens)
- Instrument context (~100-200 tokens)

**Total redundant input processing:** ~1,800-2,900 tokens × 3 agents = **~5,400-8,700 tokens**

### **Problem 2: Debate Overhead**

Each round of debate:
- Aggressive responds to Conservative & Neutral
- Neutral responds to Aggressive & Conservative
- Conservative responds to Aggressive & Neutral

**Result:** Circular argumentation consuming ~3,600 tokens per round

With `max_risk_rounds=1`, this happens once. But the argumentation is:
- Subjective (not quantitative)
- Based on tone/style, not math
- Already covered by analyst reports

### **Problem 3: No Quantitative Output**

The risk agents produce:
- ❌ NO position size calculations
- ❌ NO risk/reward ratios
- ❌ NO capital allocation formulas
- ❌ NO stop-loss levels (trader provides this)
- ❌ NO volatility-adjusted sizing

They produce:
- ✅ Conversational arguments
- ✅ Qualitative opinions
- ✅ Debate rhetoric

**But Portfolio Manager doesn't need this for risk management!**

---

## What Portfolio Manager Actually Needs

Looking at the Portfolio Manager's task:

```python
class PortfolioDecision(BaseModel):
    rating: PortfolioRating              # BUY/HOLD/SELL
    executive_summary: str               # Action plan
    investment_thesis: str               # Reasoning
    price_target: float | None           # Target price
    time_horizon: str | None             # Time horizon
    confidence_level: str | None         # Confidence
    risk_factors: list[str] | None       # Risks
    supporting_factors: list[str] | None # Supports
```

**What PM needs from risk layer:**
1. **Quantitative risk assessment** (position size, risk %, allocation)
2. **Multiple risk profiles** (aggressive/neutral/conservative numbers)
3. **Risk factors** (list of concerns)
4. **Supporting factors** (list of positives)

**What PM currently gets:**
1. ❌ Conversational debate (not structured data)
2. ❌ Rhetorical arguments (not calculations)
3. ❌ Qualitative opinions (not quantitative metrics)

---

## Token Usage Analysis

### **Current: 3 LLM Agents**

| Agent | Input Tokens | Output Tokens | Total |
|-------|--------------|---------------|-------|
| Aggressive | ~1,000 | ~300 | ~1,300 |
| Neutral | ~1,000 | ~300 | ~1,300 |
| Conservative | ~1,000 | ~300 | ~1,300 |
| **TOTAL** | **~3,000** | **~900** | **~3,900** |

**Per round:** ~3,900 tokens  
**With `max_risk_rounds=1`:** ~3,900 tokens  
**Cost per stock (Groq):** ~$0.0025

### **Proposed: 1 Python Risk Engine**

| Component | Input Tokens | Output Tokens | Total |
|-----------|--------------|---------------|-------|
| Python Risk Engine | 0 | 0 | 0 |
| **TOTAL** | **0** | **0** | **0** |

**Token Reduction:** 3,900 → 0 = **100% reduction**  
**Cost Reduction:** $0.0025 → $0 = **100% reduction**

---

## Recommendation

### **Replace Risk Debate Layer with Python Risk Engine**

**Rationale:**
1. ✅ Risk agents don't perform quantitative calculations
2. ✅ All agents receive identical inputs (redundant)
3. ✅ Debate is qualitative, not actionable
4. ✅ Portfolio Manager needs structured risk data, not rhetoric
5. ✅ Position sizing, risk %, allocation are deterministic math
6. ✅ 3,900 tokens saved per stock (45% of remaining LLM usage)

**Preserve:**
- ✅ Bull Researcher, Bear Researcher, Research Manager (valuable debate)
- ✅ Trader (concrete proposal generation)
- ✅ Portfolio Manager (final synthesis)

**Replace:**
- ❌ Aggressive Risk Analyst → Python Risk Engine (aggressive profile)
- ❌ Neutral Risk Analyst → Python Risk Engine (neutral profile)
- ❌ Conservative Risk Analyst → Python Risk Engine (conservative profile)

---

## Python Risk Engine Requirements

### **Inputs**

From trader proposal:
- `action`: Buy/Hold/Sell
- `entry_price`: Entry price
- `stop_loss`: Stop-loss level
- `position_sizing`: Sizing guidance (optional)

From market data:
- `current_price`: Latest close
- `volatility`: ATR or historical volatility
- `volume`: Average volume

From analyst reports:
- `confidence_score`: Aggregated confidence (0.0-1.0)
- `market_condition`: Bullish/Neutral/Bearish

Configuration:
- `capital`: ₹200,000
- `max_risk_per_trade`: 2% (₹4,000)
- `max_active_trades`: 4
- `min_risk_reward`: 1:2

### **Calculations**

1. **Risk Amount**
   ```python
   risk_per_trade = capital * max_risk_per_trade
   actual_risk = abs(entry_price - stop_loss) * quantity
   ```

2. **Position Size**
   ```python
   quantity = risk_amount / (entry_price - stop_loss)
   ```

3. **Capital Allocation**
   ```python
   allocation = quantity * entry_price
   ```

4. **Risk/Reward Ratio**
   ```python
   risk = entry_price - stop_loss
   reward = target_price - entry_price
   ratio = reward / risk
   ```

### **Profiles**

**Aggressive:**
- Risk: 2.0% of capital (₹4,000)
- Allocation: Up to 25% of capital (₹50,000)
- Stop: Wider (2-3 ATR)

**Neutral:**
- Risk: 1.5% of capital (₹3,000)
- Allocation: Up to 20% of capital (₹40,000)
- Stop: Standard (1.5-2 ATR)

**Conservative:**
- Risk: 1.0% of capital (₹2,000)
- Allocation: Up to 12.5% of capital (₹25,000)
- Stop: Tight (1-1.5 ATR)

### **Output Format**

```python
{
    "risk_analysis": {
        "aggressive": {
            "allocation": 50000,
            "quantity": 35,
            "risk_amount": 4000,
            "risk_percent": 2.0,
            "reward_ratio": 2.5,
            "stop_loss": 1380.0,
            "entry_price": 1500.0,
            "target_price": 1800.0
        },
        "neutral": {
            "allocation": 40000,
            "quantity": 28,
            "risk_amount": 3000,
            "risk_percent": 1.5,
            "reward_ratio": 2.0,
            "stop_loss": 1400.0,
            "entry_price": 1500.0,
            "target_price": 1700.0
        },
        "conservative": {
            "allocation": 25000,
            "quantity": 18,
            "risk_amount": 2000,
            "risk_percent": 1.0,
            "reward_ratio": 2.0,
            "stop_loss": 1420.0,
            "entry_price": 1500.0,
            "target_price": 1660.0
        }
    },
    "risk_factors": [
        "High volatility (ATR: 45)",
        "Stop loss 8% below entry",
        "Market condition: Neutral"
    ],
    "supporting_factors": [
        "Strong analyst confidence: 0.85",
        "Positive risk/reward: 2:1 minimum",
        "Volume above average"
    ]
}
```

---

## Summary

| Aspect | Current (3 LLM Agents) | Proposed (Python Engine) |
|--------|------------------------|--------------------------|
| **Token Usage** | ~3,900 per stock | 0 |
| **Cost** | ~$0.0025 per stock | $0 |
| **Runtime** | ~30-40s | <0.1s |
| **Output** | Conversational debate | Structured risk data |
| **Quantitative** | ❌ No calculations | ✅ Position sizing, risk %, allocation |
| **Profiles** | ✅ 3 perspectives | ✅ 3 numerical profiles |
| **PM Integration** | Text synthesis | Structured data consumption |

**Expected Improvements:**
- Token reduction: **~45%** (3,900 / 8,500 tokens)
- Runtime reduction: **~20-25%** (30-40s saved)
- Cost reduction: **~$0.0025 per stock**

---

**Next Phase:** Design Python Risk Engine architecture and implementation plan.

**Status:** ✅ Audit complete - Ready for PHASE 2
