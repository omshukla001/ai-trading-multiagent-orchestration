# Phase 3A Live Validation Guide
## Required Before Deployment

**Status**: Implementation complete, awaiting live validation  
**Blocker**: Free tier rate limits  
**Solution**: Use paid provider for validation

---

## Why Live Validation is Required

**Current Status**:
- ✅ Optimizations implemented
- ✅ Code verified
- ✅ Theoretical analysis complete (54% token reduction expected)
- ❌ **Live quality validation missing**

**Risk Without Live Validation**:
- Cannot confirm recommendations maintain quality
- Cannot verify actual token reduction matches theory
- Cannot validate confidence scores remain reliable
- Cannot confirm reasoning depth is preserved

**User Directive**: "Theoretical validation is not sufficient. Quality preservation is NOT proven without live runs."

---

## Validation Requirements

### Test Configuration

**Stocks to Test**: 3 NSE stocks
- HDFCBANK.NS (HDFC Bank)
- INFY.NS (Infosys)
- RELIANCE.NS (Reliance Industries)

**Two Test Runs Required**:

1. **BASELINE (Before Phase 3A)**
   - Debate rounds: 3
   - Output limits: None (unlimited)
   - Prompts: Original verbose versions
   
2. **OPTIMIZED (After Phase 3A)**
   - Debate rounds: 2
   - Output limits: 800 tokens
   - Prompts: Reduced versions

### Metrics to Capture

**Performance Metrics**:
1. Runtime (seconds)
2. Total tokens (input + output)
3. Cost (USD)

**Quality Metrics**:
4. Final recommendation (BUY/SELL/HOLD/etc)
5. Confidence score
6. Entry price
7. Stop loss
8. Target price
9. Reasoning quality (subjective assessment)

### Success Criteria

**Performance Targets** (Must Meet):
- ✅ Token reduction ≥ 40%
- ✅ Runtime reduction ≥ 25%

**Quality Targets** (Must Meet):
- ✅ Recommendation consistency ≥ 80% (at most 1 of 3 stocks changes recommendation)
- ✅ Confidence degradation < 15% (confidence scores don't drop significantly)
- ✅ No major drop in reasoning quality (subjective - are arguments still evidence-based?)

---

## Option 1: Use Groq Paid Tier (Recommended)

**Cost**: ~$0.10-0.20 for full validation (6 test runs)

**Setup**:
```bash
# Get paid API key from https://console.groq.com/
export GROQ_API_KEY="gsk-your-paid-key-here"
```

**Pros**:
- Fast inference (70B model)
- Reliable
- Affordable
- Already configured in codebase

**Cons**:
- Requires payment

---

## Option 2: Use OpenAI

**Cost**: ~$0.30-0.50 for full validation

**Setup**:
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

**Configuration Change Needed**:
```python
# In test scripts, change config:
config = {
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o",
    "quick_think_llm": "gpt-4o-mini",
    ...
}
```

**Pros**:
- Highly reliable
- No rate limits on paid tier
- High quality responses

**Cons**:
- More expensive than Groq
- Slower than Groq

---

## Option 3: Use Cerebras Paid Tier

**Cost**: ~$0.15-0.25 for full validation

**Setup**:
```bash
export CEREBRAS_API_KEY="csk-your-paid-key-here"
```

**Pros**:
- Fast
- Affordable

**Cons**:
- Requires payment
- May still have limits

---

## How to Run Validation

### Step 1: Set Up Paid API

Choose a provider and set the API key:

```bash
cd tradingagents

# Option 1: Groq (recommended)
export GROQ_API_KEY="gsk-your-paid-key-here"

# OR Option 2: OpenAI
export OPENAI_API_KEY="sk-your-key-here"

# OR Option 3: Cerebras
export CEREBRAS_API_KEY="csk-your-paid-key-here"
```

### Step 2: Run Baseline Test (Before Phase 3A)

**Temporarily revert optimizations**:

```bash
# 1. Change debate rounds back to 3
# Edit tradingagents/default_config.py line 105:
"max_debate_rounds": 3,  # Change from 2 to 3

# 2. Remove output token limits
# Edit tradingagents/agents/researchers/bull_researcher.py line ~46:
response = llm.invoke(prompt)  # Remove , max_tokens=800

# Edit tradingagents/agents/researchers/bear_researcher.py line ~48:
response = llm.invoke(prompt)  # Remove , max_tokens=800

# 3. Restore verbose prompts (or skip - impact is small)
# This is tedious, can skip if needed
```

**Run baseline test**:

```bash
# Enable environment
export USE_OPTIMIZED_ANALYSTS=1
export USE_OPTIMIZED_RISK=1
export AUDIT_MODE=1

# Create simple test script
python -c "
from tradingagents.graph import TradingAgentsGraph
from datetime import datetime
from audit_framework import get_audit_collector, reset_audit_collector
import json

stocks = [('HDFCBANK.NS', 'HDFC Bank'), ('INFY.NS', 'Infosys'), ('RELIANCE.NS', 'Reliance')]
results = []

for ticker, name in stocks:
    reset_audit_collector()
    
    config = {
        'llm_provider': 'groq',
        'deep_think_llm': 'llama-3.3-70b-versatile',
        'quick_think_llm': 'llama-3.3-70b-versatile',
        'max_debate_rounds': 3,
        'data_cache_dir': './data_cache',
        'results_dir': './results'
    }
    
    graph = TradingAgentsGraph(
        selected_analysts=['market', 'fundamentals', 'news'],
        config=config
    )
    
    import time
    start = time.time()
    final_state, signal = graph.propagate(
        company_name=ticker,
        trade_date=datetime.now().strftime('%Y-%m-%d')
    )
    runtime = time.time() - start
    
    collector = get_audit_collector()
    summary = collector.get_summary()
    
    results.append({
        'ticker': ticker,
        'runtime': runtime,
        'tokens': summary['total_tokens'],
        'cost': summary['total_cost'],
        'decision': str(final_state.get('final_trade_decision', ''))[:200]
    })
    
    print(f'{ticker}: {runtime:.1f}s, {summary[\"total_tokens\"]:,} tokens')

with open('baseline_results.json', 'w') as f:
    json.dump(results, f, indent=2)
"
```

### Step 3: Run Optimized Test (After Phase 3A)

**Re-apply optimizations**:

```bash
# 1. Change debate rounds back to 2
# Edit tradingagents/default_config.py line 105:
"max_debate_rounds": 2,  # Change from 3 to 2

# 2. Re-add output token limits
# Edit tradingagents/agents/researchers/bull_researcher.py line ~46:
response = llm.invoke(prompt, max_tokens=800)

# Edit tradingagents/agents/researchers/bear_researcher.py line ~48:
response = llm.invoke(prompt, max_tokens=800)
```

**Run optimized test**:

```bash
# Same script but with different output file
python -c "
from tradingagents.graph import TradingAgentsGraph
from datetime import datetime
from audit_framework import get_audit_collector, reset_audit_collector
import json

stocks = [('HDFCBANK.NS', 'HDFC Bank'), ('INFY.NS', 'Infosys'), ('RELIANCE.NS', 'Reliance')]
results = []

for ticker, name in stocks:
    reset_audit_collector()
    
    config = {
        'llm_provider': 'groq',
        'deep_think_llm': 'llama-3.3-70b-versatile',
        'quick_think_llm': 'llama-3.3-70b-versatile',
        'max_debate_rounds': 2,
        'data_cache_dir': './data_cache',
        'results_dir': './results'
    }
    
    graph = TradingAgentsGraph(
        selected_analysts=['market', 'fundamentals', 'news'],
        config=config
    )
    
    import time
    start = time.time()
    final_state, signal = graph.propagate(
        company_name=ticker,
        trade_date=datetime.now().strftime('%Y-%m-%d')
    )
    runtime = time.time() - start
    
    collector = get_audit_collector()
    summary = collector.get_summary()
    
    results.append({
        'ticker': ticker,
        'runtime': runtime,
        'tokens': summary['total_tokens'],
        'cost': summary['total_cost'],
        'decision': str(final_state.get('final_trade_decision', ''))[:200]
    })
    
    print(f'{ticker}: {runtime:.1f}s, {summary[\"total_tokens\"]:,} tokens')

with open('optimized_results.json', 'w') as f:
    json.dump(results, f, indent=2)
"
```

### Step 4: Compare Results

```python
# Compare baseline vs optimized
python -c "
import json

with open('baseline_results.json') as f:
    baseline = json.load(f)

with open('optimized_results.json') as f:
    optimized = json.load(f)

print('COMPARISON REPORT')
print('=' * 80)
print()

for b, o in zip(baseline, optimized):
    token_reduction = (b['tokens'] - o['tokens']) / b['tokens'] * 100
    runtime_reduction = (b['runtime'] - o['runtime']) / b['runtime'] * 100
    
    print(f'{b[\"ticker\"]}:')
    print(f'  Tokens:  {b[\"tokens\"]:,} → {o[\"tokens\"]:,} ({token_reduction:+.1f}%)')
    print(f'  Runtime: {b[\"runtime\"]:.1f}s → {o[\"runtime\"]:.1f}s ({runtime_reduction:+.1f}%)')
    print(f'  Cost:    \${b[\"cost\"]:.4f} → \${o[\"cost\"]:.4f}')
    print()

avg_token_reduction = sum((b['tokens'] - o['tokens']) / b['tokens'] * 100 for b, o in zip(baseline, optimized)) / len(baseline)
avg_runtime_reduction = sum((b['runtime'] - o['runtime']) / b['runtime'] * 100 for b, o in zip(baseline, optimized)) / len(baseline)

print(f'Average token reduction: {avg_token_reduction:.1f}%')
print(f'Average runtime reduction: {avg_runtime_reduction:.1f}%')
print()
print(f'Target: ≥40% tokens, ≥25% runtime')
print(f'Pass: {\"✅\" if avg_token_reduction >= 40 and avg_runtime_reduction >= 25 else \"❌\"}')
"
```

---

## Estimated Timeline

- **Baseline run**: 15-20 minutes (3 stocks × 5-7 min each)
- **Optimized run**: 10-15 minutes (3 stocks × 3-5 min each)
- **Comparison**: 2 minutes
- **Total**: ~30-40 minutes

---

## Estimated Cost

### Groq (Recommended)
- Baseline: 3 stocks × ~50k tokens × $0.59/1M = **$0.09**
- Optimized: 3 stocks × ~25k tokens × $0.59/1M = **$0.04**
- **Total: ~$0.13**

### OpenAI
- Baseline: 3 stocks × ~50k tokens × $2.50/1M = **$0.38**
- Optimized: 3 stocks × ~25k tokens × $2.50/1M = **$0.19**
- **Total: ~$0.57**

### Cerebras
- Baseline: 3 stocks × ~50k tokens × $0.60/1M = **$0.09**
- Optimized: 3 stocks × ~25k tokens × $0.60/1M = **$0.05**
- **Total: ~$0.14**

---

## Decision Point

**After validation completes**:

### If Pass (≥40% tokens, ≥25% runtime, quality maintained):
- ✅ **DEPLOY Phase 3A to production**
- Document actual metrics
- Monitor first 20 production stocks
- Mark Phase 3 complete

### If Fail (below targets or quality degraded):
- ❌ **ROLLBACK Phase 3A**
- Investigate why actual results differ from theory
- Consider partial optimization (e.g., keep 2 rounds but restore verbose prompts)
- Re-test

---

## Current Blockers

**Blocker**: Free tier rate limits prevent validation  
**Resolution Required**: Use paid API provider  
**Cost**: ~$0.13-0.57 depending on provider  
**Time**: ~30-40 minutes to complete

**User Decision Needed**:
1. Which paid provider to use? (Groq recommended)
2. Approval to spend ~$0.15 on validation?
3. Should we proceed with validation now?

---

**Status**: Awaiting approval to proceed with paid tier validation.
