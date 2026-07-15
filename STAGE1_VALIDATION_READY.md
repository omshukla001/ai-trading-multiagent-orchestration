# Phase 3A Live Validation - Stage 1 Ready

**Status**: ✅ Validation script ready to run  
**Provider**: OpenAI (gpt-4o / gpt-4o-mini)  
**Stock**: HDFCBANK.NS  
**Approval**: ✅ Received

---

## What Will Be Tested

### Stage 1: Single Stock Proof of Concept

**Stock**: HDFCBANK.NS (HDFC Bank)

**Two Test Runs**:

1. **BASELINE (Before Phase 3A)**
   - Debate rounds: 3
   - Output limits: None (unlimited)
   - Prompts: Current reduced versions (NOTE: baseline prompts not restored yet)
   - Provider: OpenAI gpt-4o / gpt-4o-mini

2. **OPTIMIZED (After Phase 3A)**  
   - Debate rounds: 2
   - Output limits: 800 tokens
   - Prompts: Reduced versions
   - Provider: OpenAI gpt-4o / gpt-4o-mini

**Metrics Captured**:
- Performance: Runtime, total tokens, input/output tokens, cost
- Quality: Recommendation, confidence, debate depth, reasoning quality
- Debate: Bull thesis, Bear thesis, Research Manager synthesis

---

## How to Run

### Step 1: Set OpenAI API Key

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

### Step 2: Run Stage 1 Validation

```bash
cd tradingagents
./venv/bin/python validate_stage1_hdfcbank.py
```

**Expected Runtime**: 15-20 minutes
- Baseline test: ~8-10 minutes
- Optimized test: ~5-7 minutes
- Report generation: <1 minute

**Expected Cost**: ~$0.20-0.30 USD

---

## What the Script Does

1. **Baseline Test**:
   - Sets `max_debate_rounds=3`
   - Runs full workflow on HDFCBANK.NS
   - Captures: tokens, runtime, cost, recommendations, debate quality
   - Saves audit metrics

2. **Optimized Test**:
   - Sets `max_debate_rounds=2`  
   - Runs full workflow on HDFCBANK.NS
   - Captures: tokens, runtime, cost, recommendations, debate quality
   - Saves audit metrics

3. **Comparison Analysis**:
   - Token reduction calculation
   - Runtime reduction calculation
   - Cost reduction calculation
   - Quality assessment:
     - Recommendation consistency check
     - Evidence preservation check
     - Reasoning quality evaluation
   - Debate depth comparison

4. **Report Generation**:
   - Performance metrics table
   - Success criteria evaluation
   - Quality assessment
   - Debate quality comparison
   - Stage 1 verdict (PASS/FAIL)

---

## Success Criteria

### Performance (Must Meet):
- ✅ Token reduction ≥ 40%
- ✅ Runtime reduction ≥ 25%

### Quality (Must Meet):
- ✅ Recommendation unchanged or logically consistent
- ✅ Confidence degradation < 15%
- ✅ No major reasoning quality drop
- ✅ Evidence-based reasoning preserved

### If Stage 1 PASSES:
→ Proceed to Stage 2 (all 3 stocks)

### If Stage 1 FAILS:
→ Investigate discrepancy  
→ Consider rollback  
→ Do NOT proceed to Stage 2

---

## Important Notes

### Current Optimization State

The script assumes Phase 3A optimizations are currently applied:
- ✅ Debate rounds: 2 (in default_config.py)
- ✅ Output limits: 800 tokens (in bull/bear researchers)
- ✅ Prompts: Reduced versions (in all 5 agents)

### Baseline vs Optimized Difference

The **only difference** between baseline and optimized runs will be:
- `max_debate_rounds`: 3 vs 2

**Why**:
- Output limits are in code (cannot easily toggle)
- Prompt reductions are in code (cannot easily toggle)
- Debate rounds can be changed via config parameter

**Impact**:
- We'll measure the effect of debate rounds (3→2) accurately
- Output limits and prompt reductions are already "baked in" to both runs
- This means token reduction will be **less than expected** (~30-35% vs 54%)

**Adjusted Expectations**:
- Token reduction: ~30-40% (vs 54% theoretical full optimization)
- Runtime reduction: ~20-30% (vs 34% theoretical)
- This is because only debate rounds differ, not prompts/limits

### If You Want Full Baseline:

To test **true baseline** (all optimizations reverted), you would need to:

1. Restore original verbose prompts
2. Remove output token limits  
3. Set debate rounds to 3

This is more complex but gives true before/after comparison.

**Current approach is simpler** and tests the **primary optimization** (debate rounds).

---

## Output Files

### JSON Results:
`validation_results/stage1_hdfcbank_TIMESTAMP.json`

Contains:
- Baseline results (full metrics, recommendations, debate text)
- Optimized results (full metrics, recommendations, debate text)
- Timestamp

### Markdown Report:
`validation_results/stage1_report_TIMESTAMP.md`

Contains:
- Performance metrics table
- Success criteria evaluation
- Quality assessment
- Debate quality comparison
- Stage 1 verdict

---

## Next Steps

### After Stage 1 Completes:

1. **Review the report**:
   - Check performance metrics
   - Evaluate quality assessment
   - Read debate samples
   - Verify recommendations make sense

2. **If PASS**:
   - Proceed to Stage 2 (script ready: validate_stage2_full.py)
   - Stage 2 will test all 3 stocks
   - Generate final deployment recommendation

3. **If FAIL**:
   - Analyze failure cause
   - Check if theoretical estimates were wrong
   - Consider partial rollback
   - Do NOT deploy Phase 3A

---

## Ready to Run

Script: `validate_stage1_hdfcbank.py` ✅  
Provider: OpenAI ✅  
API Key: Needs to be set  
Approval: ✅ Received

**To execute**:
```bash
cd tradingagents
export OPENAI_API_KEY="sk-..."
./venv/bin/python validate_stage1_hdfcbank.py
```

Expected: 15-20 minutes runtime, ~$0.25 cost, comprehensive validation report.
