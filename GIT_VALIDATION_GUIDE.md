# Git-Based Validation - Execution Guide
## Phase 3A Stage 1: HDFCBANK.NS

**Status**: ✅ Ready to execute  
**Method**: Git stash/pop for clean state management  
**Provider**: OpenAI (gpt-4o / gpt-4o-mini)

---

## What This Script Does

### Clean State Management

**Baseline State** (Pre-Phase-3A):
- Uses git stash to temporarily remove Phase 3A changes
- Restores original code from git repository
- Debate rounds: 3
- Original verbose prompts: ✅
- No output token caps: ✅

**Optimized State** (Phase 3A Applied):
- Uses git stash pop to restore Phase 3A changes
- Current modified code with all optimizations
- Debate rounds: 2
- Reduced prompts: ✅
- Output token caps (800): ✅

### Validation Flow

```
1. git stash (store Phase 3A changes)
   ↓
2. Verify baseline state
   ↓
3. Run BASELINE validation (3 rounds, verbose prompts, no caps)
   ↓
4. Save baseline metrics
   ↓
5. git stash pop (restore Phase 3A changes)
   ↓
6. Verify optimized state
   ↓
7. Run OPTIMIZED validation (2 rounds, reduced prompts, 800 caps)
   ↓
8. Save optimized metrics
   ↓
9. Compare and generate report
```

---

## How to Execute

### Prerequisites

1. **OpenAI API Key** (required):
   ```bash
   export OPENAI_API_KEY="sk-your-api-key-here"
   ```

2. **Git working directory** must have Phase 3A changes uncommitted:
   - bull_researcher.py (modified)
   - bear_researcher.py (modified)
   - research_manager.py (modified)
   - trader.py (modified)
   - portfolio_manager.py (modified)
   - default_config.py (modified)

3. **Clean git state** (no other uncommitted changes you want to keep)

### Execute Validation

```bash
cd tradingagents
python validate_git_based.py
```

or

```bash
cd tradingagents
./validate_git_based.py
```

---

## Expected Timeline

- **Baseline run**: 8-12 minutes
- **Optimized run**: 5-8 minutes
- **Report generation**: <1 minute
- **Total**: 15-25 minutes

---

## Expected Cost

**OpenAI Pricing** (gpt-4o / gpt-4o-mini):
- Baseline: ~$0.15-0.25
- Optimized: ~$0.08-0.15
- **Total**: ~$0.25-0.40 USD

---

## Metrics Captured

### Performance Metrics

| Metric          | Description                              |
|-----------------|------------------------------------------|
| Total Tokens    | Input + Output tokens                    |
| Input Tokens    | Context + prompts sent to LLM            |
| Output Tokens   | LLM generated responses                  |
| Runtime         | End-to-end execution time (seconds)      |
| Cost            | Estimated USD based on OpenAI pricing    |
| Debate Rounds   | Number of Bull/Bear debate rounds        |

### Trading Output

| Field          | Description                               |
|----------------|-------------------------------------------|
| Recommendation | BUY / SELL / HOLD / OVERWEIGHT / etc      |
| Confidence     | Confidence score/level                    |
| Entry Price    | Recommended entry price                   |
| Stop Loss      | Risk management stop loss                 |
| Target Price   | Profit target                             |

### Quality Metrics

| Field             | Description                            |
|-------------------|----------------------------------------|
| Bull Reasoning    | First 1000 chars of bull arguments     |
| Bear Reasoning    | First 1000 chars of bear arguments     |
| Bull Length       | Total character count of bull thesis   |
| Bear Length       | Total character count of bear thesis   |
| Manager Synthesis | Research Manager's investment plan     |
| Trader Decision   | Trader's trade proposal                |
| PM Decision       | Portfolio Manager's final decision     |

---

## Success Criteria

### Performance Targets (Must Meet):
- ✅ Token reduction ≥ 40%
- ✅ Runtime reduction ≥ 25%

### Quality Targets (Evaluated):
- Recommendation consistency
- Confidence degradation < 15%
- Reasoning quality preserved
- Evidence-based arguments maintained

---

## Output Files

### JSON Results
`validation_results/git_validation_TIMESTAMP.json`

Contains:
```json
{
  "baseline": {
    "mode": "baseline",
    "success": true,
    "runtime": 450.2,
    "total_tokens": 52000,
    "input_tokens": 43000,
    "output_tokens": 9000,
    "total_cost": 0.23,
    "decision": "...",
    "trader_plan": "...",
    "bull_reasoning": "...",
    "bear_reasoning": "...",
    "per_agent_metrics": {...}
  },
  "optimized": {
    "mode": "optimized",
    "success": true,
    "runtime": 290.5,
    "total_tokens": 28000,
    "input_tokens": 23000,
    "output_tokens": 5000,
    "total_cost": 0.12,
    ...
  }
}
```

### Markdown Report
`validation_results/git_report_TIMESTAMP.md`

Contains:
- Performance metrics comparison table
- Success criteria evaluation
- Quality assessment
- Final verdict (PASS/FAIL)
- Recommendation for Stage 2

---

## State Verification

The script includes automatic state verification:

### Baseline Verification
- ✅ No `max_tokens=800` in bull_researcher.py
- ✅ Verbose prompts present (>2000 chars)
- ✅ Config default is 1 (will be overridden to 3)

### Optimized Verification
- ✅ `max_tokens=800` present in bull_researcher.py
- ✅ Reduced prompts present ("Be concise and data-driven")
- ✅ Config set to 2 debate rounds

If verification fails, the script will warn and ask for confirmation.

---

## Error Handling

### If Baseline Fails
- Phase 3A changes are automatically restored (git stash pop)
- No files left in inconsistent state
- Error logged to console

### If Optimized Fails
- Phase 3A changes remain applied (as they should)
- Baseline results are saved
- Error logged to console

### If Script Crashes
- Run manually: `git stash pop` to restore Phase 3A changes
- Check `git stash list` to see if stash exists

---

## Expected Results

### Baseline (Pre-Phase-3A):
- Total tokens: ~50,000-60,000
- Runtime: ~8-12 minutes
- Verbose bull/bear arguments (6,000-9,000 chars each)
- 3 debate rounds executed

### Optimized (Phase 3A):
- Total tokens: ~25,000-35,000
- Runtime: ~5-8 minutes
- Concise bull/bear arguments (2,000-4,000 chars each)
- 2 debate rounds executed

### Expected Improvements:
- Token reduction: **40-50%** ✅ (meets ≥40% target)
- Runtime reduction: **30-40%** ✅ (meets ≥25% target)
- Cost reduction: **40-50%**

---

## After Validation Completes

### If PASS (≥40% tokens, ≥25% runtime):
1. Review the detailed report
2. Check quality metrics (recommendations, reasoning)
3. ✅ **PROCEED TO STAGE 2**
   - Validate all 3 stocks (HDFCBANK.NS, INFY.NS, RELIANCE.NS)
   - Generate final deployment recommendation

### If FAIL (<40% tokens or <25% runtime):
1. Review the detailed report
2. Analyze why actual results differ from theory
3. ❌ **DO NOT PROCEED TO STAGE 2**
   - Investigate discrepancy
   - Consider partial rollback
   - Re-evaluate optimization strategy

---

## Safety Notes

### Git State
- The script uses `git stash` which is non-destructive
- Your Phase 3A changes are safely stored in the stash
- If anything goes wrong, run `git stash pop` to restore

### File Integrity
- Baseline run uses files from git repository (clean)
- Optimized run uses your modified files (Phase 3A)
- No files are permanently modified or deleted

### Interruption
- If interrupted (Ctrl+C), run `git stash pop` to restore
- Check `git status` to see current state
- Check `git stash list` to see if Phase 3A stash exists

---

## Troubleshooting

### "No changes to stash"
- This means Phase 3A changes were already committed
- You need to revert the commit or checkout files manually
- Alternative: Use git branches instead

### "Baseline verification failed"
- The git stash may not have worked correctly
- Check `git diff` to see current changes
- May need to manually checkout baseline files

### "OPENAI_API_KEY not set"
- Run: `export OPENAI_API_KEY="sk-..."`
- Or set in your shell profile

### "Rate limit exceeded"
- OpenAI paid tier should not hit limits
- Wait a few minutes and retry
- Check your API quota/billing

---

## Ready to Execute

**Command**:
```bash
cd tradingagents
export OPENAI_API_KEY="sk-your-key-here"
python validate_git_based.py
```

**Expected**: 15-25 minutes runtime, ~$0.30 cost, comprehensive validation report with PASS/FAIL verdict.

**Status**: ✅ Script ready, git-based state management implemented, clean baseline/optimized comparison guaranteed.
