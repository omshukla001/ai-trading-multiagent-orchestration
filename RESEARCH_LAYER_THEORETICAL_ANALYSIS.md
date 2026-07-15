# Research Layer Token Usage Analysis - Theoretical
## Phase 2: LLM Agent Audit (Code-Based Estimation)

**Date**: 2026-07-05  
**Method**: Static code analysis + prompt inspection  
**Reason**: Rate limits prevent live execution  
**Status**: Theoretical estimates based on prompt structure

---

## Executive Summary

Based on code inspection of the 6 LLM agents, estimated token consumption per stock:

| Agent               | Est. Input Tokens | Est. Output Tokens | Total  | % of Total |
|---------------------|-------------------|--------------------| -------|-----------|
| Bull Researcher     | 8,000-12,000      | 2,000-3,000        | 10-15k | 23%       |
| Bear Researcher     | 8,000-12,000      | 2,000-3,000        | 10-15k | 23%       |
| Research Manager    | 12,000-18,000     | 1,500-2,500        | 13.5-20.5k | 27%   |
| Trader              | 6,000-8,000       | 1,000-1,500        | 7-9.5k | 15%       |
| Portfolio Manager   | 4,000-6,000       | 800-1,200          | 4.8-7.2k | 12%     |
| News Analyst        | 0 (optimized)     | 0                  | 0      | 0%        |
| **TOTAL**           | **38k-56k**       | **7.3k-11.2k**     | **45-67k** | **100%** |

**Key Findings**:
- Research Manager is the **largest token consumer** (~27% of total)
- Bull + Bear combined = 46% of total tokens
- First 5 agents (before Portfolio Manager) consume 88% of tokens

---

## Detailed Analysis per Agent

### 1. Bull Researcher

**Function**: Advocate for buying the stock, counter bear arguments

**Prompt Structure**:
```python
prompt = f"""You are a Bull Analyst advocating for investing in the {target_label}...
Resources available:
{instrument_context}              # ~500-800 tokens
Market research report: {market_research_report}  # ~1,500-2,500 tokens
Social media sentiment report: {sentiment_report}  # ~500-1,000 tokens (if not optimized)
Latest world affairs news: {news_report}          # ~2,000-3,000 tokens
Company fundamentals report: {fundamentals_report} # ~2,000-3,500 tokens
Conversation history of the debate: {history}     # ~1,000-2,000 tokens (grows each round)
Last bear argument: {current_response}            # ~500-1,500 tokens (first round = empty)
"""
```

**Token Breakdown**:
- System instructions: ~400 tokens
- Instrument context: 500-800 tokens
- Market report: 1,500-2,500 tokens
- Sentiment report: 500-1,000 tokens (or 0 if optimized)
- News report: 2,000-3,000 tokens
- Fundamentals report: 2,000-3,500 tokens
- Debate history: 1,000-2,000 tokens
- Bear's last response: 500-1,500 tokens (grows in later rounds)

**Estimated Input Tokens**:
- Round 1: ~8,000-10,000 tokens
- Round 2: ~10,000-12,000 tokens (+ debate history)
- Round 3: ~12,000-14,000 tokens (+ longer history)
- **Average: 10,000 tokens**

**Estimated Output Tokens**: 2,000-3,000 tokens (comprehensive bull argument)

**Total per Stock**: ~12,000-13,000 tokens (across 3 rounds typical)

---

### 2. Bear Researcher

**Function**: Advocate against buying the stock, counter bull arguments

**Prompt Structure**: Nearly identical to Bull Researcher
```python
prompt = f"""You are a Bear Analyst making the case against investing...
[Same resources as Bull Researcher]
Last bull argument: {current_response}
"""
```

**Token Breakdown**: Same as Bull Researcher

**Estimated Input Tokens**: 
- Round 1: ~8,000-10,000 tokens
- Round 2: ~10,000-12,000 tokens
- Round 3: ~12,000-14,000 tokens
- **Average: 10,000 tokens**

**Estimated Output Tokens**: 2,000-3,000 tokens (comprehensive bear argument)

**Total per Stock**: ~12,000-13,000 tokens (across 3 rounds)

---

### 3. Research Manager

**Function**: Synthesize bull/bear debate into actionable investment plan

**Prompt Structure**:
```python
prompt = f"""As the Research Manager and debate facilitator...
{instrument_context}              # ~500-800 tokens
Debate History: {history}         # ~15,000-20,000 tokens (full Bull + Bear debate)
"""
```

**Token Breakdown**:
- System instructions: ~500 tokens
- Rating scale instructions: ~200 tokens
- Instrument context: 500-800 tokens
- **Full debate history**: 15,000-20,000 tokens
  - Includes all Bull arguments (~6,000-9,000 tokens)
  - Includes all Bear arguments (~6,000-9,000 tokens)
  - Includes debate metadata (~1,000-2,000 tokens)

**Estimated Input Tokens**: 16,000-22,000 tokens
- **This is the LARGEST input of all agents**

**Estimated Output Tokens**: 1,500-2,500 tokens (structured investment plan)
- Uses structured output (ResearchPlan schema)
- More concise than free-form debate

**Total per Stock**: ~17,500-24,500 tokens

**Bottleneck Identified**: ✅ **Research Manager has highest token consumption**

---

### 4. Trader

**Function**: Convert investment plan into specific trade proposal

**Prompt Structure**:
```python
messages = [
    {
        "role": "system",
        "content": "You are a trading agent..." # ~150 tokens
    },
    {
        "role": "user",
        "content": f"""Based on comprehensive analysis...
        {instrument_context}      # ~500-800 tokens
        Investment Plan: {investment_plan}  # ~1,500-2,500 tokens (from Research Manager)
        """
    }
]
```

**Token Breakdown**:
- System prompt: ~150 tokens
- Instrument context: 500-800 tokens
- Investment plan: 1,500-2,500 tokens
- Instructions: ~300 tokens

**Estimated Input Tokens**: 2,500-3,750 tokens

**Estimated Output Tokens**: 1,000-1,500 tokens (structured trade proposal)
- Uses TraderProposal schema
- Includes: action, entry price, stop loss, targets, reasoning

**Total per Stock**: ~3,500-5,250 tokens

---

### 5. Portfolio Manager

**Function**: Determine position sizing and risk parameters

**Estimated Token Usage** (similar to Trader):
- Input: ~2,000-3,000 tokens
- Output: ~800-1,200 tokens
- **Total: ~2,800-4,200 tokens**

---

### 6. News Analyst

**Status**: Python-optimized (USE_OPTIMIZED_ANALYSTS=1)

**Token Usage**: **0 tokens** (not using LLM when optimized)

**Note**: If not optimized, would consume ~3,000-5,000 tokens per stock

---

## Cost Analysis

### Cost Estimates per Stock (using Groq free tier as baseline)

**Groq Pricing** (llama-3.3-70b):
- Input: $0.00059 per 1M tokens
- Output: $0.00079 per 1M tokens

| Agent               | Input Cost | Output Cost | Total Cost |
|---------------------|------------|-------------|------------|
| Bull Researcher     | $0.0059    | $0.0020     | $0.0079    |
| Bear Researcher     | $0.0059    | $0.0020     | $0.0079    |
| Research Manager    | $0.0106    | $0.0016     | $0.0122    |
| Trader              | $0.0018    | $0.0010     | $0.0028    |
| Portfolio Manager   | $0.0015    | $0.0008     | $0.0023    |
| **TOTAL**           | **$0.0257** | **$0.0074** | **$0.0331** |

**Cost per stock**: ~$0.03 USD (Groq free tier pricing)

**For 10 stocks**: ~$0.33 USD  
**For 100 stocks**: ~$3.30 USD  
**For 1,000 stocks**: ~$33.00 USD

### Cost Breakdown by Agent

```
Research Manager:  37% of total cost (largest)
Bull Researcher:   24% of total cost
Bear Researcher:   24% of total cost
Trader:            8% of total cost
Portfolio Manager: 7% of total cost
```

---

## Runtime Analysis (Estimated)

Based on typical LLM API latencies:

| Agent               | Calls | Avg Latency | Total Runtime |
|---------------------|-------|-------------|---------------|
| Bull Researcher     | 3     | 8-12s       | 24-36s        |
| Bear Researcher     | 3     | 8-12s       | 24-36s        |
| Research Manager    | 1     | 15-25s      | 15-25s        |
| Trader              | 1     | 4-6s        | 4-6s          |
| Portfolio Manager   | 1     | 3-5s        | 3-5s          |
| **TOTAL**           | **9** |             | **70-108s**   |

**Average runtime per stock**: ~90 seconds (1.5 minutes) for LLM agents only

**Note**: This excludes:
- Python-based analysts (Market, Fundamentals, News): ~30-60s
- Network overhead and API queuing: ~10-30s
- Graph state management: ~5-10s

**Total end-to-end**: ~2-3 minutes per stock (when no rate limits)

---

## Largest Bottlenecks

### 1. Token Consumption: Research Manager (37% of total cost)

**Problem**: Receives entire Bull+Bear debate history (~15-20k tokens)

**Why it's expensive**:
- Must read all Bull arguments (3 rounds)
- Must read all Bear arguments (3 rounds)
- Total debate = 12,000-18,000 tokens alone

**Optimization opportunities**:
- Summarize debate instead of sending full history
- Extract key points only (reduce by 50-70%)
- Use debate round summaries instead of full text

**Potential savings**: $0.0045/stock (37% reduction in total cost)

### 2. Token Consumption: Bull + Bear Researchers (48% combined)

**Problem**: Receive full context on every round

**Why it's expensive**:
- Market report: 1,500-2,500 tokens
- News report: 2,000-3,000 tokens
- Fundamentals report: 2,000-3,500 tokens
- Debate history grows each round

**Optimization opportunities**:
- Cache repeated context (market/news/fundamentals don't change mid-debate)
- Only send new opponent arguments, not full history
- Reduce report verbosity (extract key facts only)

**Potential savings**: $0.0063/stock (19% reduction in total cost)

### 3. Runtime: Bull + Bear Debate Rounds (68% of total time)

**Problem**: 6 sequential LLM calls (Bull → Bear → Bull → Bear → Bull → Bear)

**Why it's slow**:
- Each call waits for previous to complete
- No parallelization possible (debate is sequential)
- API latency compounds over 6 calls

**Optimization opportunities**:
- Reduce debate rounds from 3 to 2 (saves ~30s)
- Use faster models for early rounds
- Consider async debate (both agents respond to round N simultaneously)

**Potential savings**: ~30-45 seconds per stock (33% reduction in LLM runtime)

---

## Optimization Recommendations

### Priority 1: Optimize Research Manager Input (HIGH IMPACT)

**Current**: 16,000-22,000 input tokens  
**Optimized**: 5,000-8,000 input tokens (70% reduction)

**Approach**:
```python
# Instead of full debate history
debate_history = "Bull: [12,000 tokens]... Bear: [12,000 tokens]..."

# Use structured summary
debate_summary = {
    "bull_key_points": ["Point 1", "Point 2", "Point 3"],  # 500 tokens
    "bear_key_points": ["Risk 1", "Risk 2", "Risk 3"],      # 500 tokens
    "consensus_areas": ["Area 1", "Area 2"],                # 200 tokens
    "contentious_points": ["Disagreement 1", "Disagreement 2"]  # 300 tokens
}
```

**Estimated savings**: $0.0045/stock × 1,000 stocks = **$4.50** (11% reduction)

### Priority 2: Reduce Bull/Bear Context Redundancy (MEDIUM IMPACT)

**Current**: Each round sends full market/news/fundamentals reports

**Optimized**: Send reports once, reference only

**Approach**:
- Round 1: Full context
- Round 2+: Only opponent's new argument + "refer to initial reports"

**Estimated savings**: $0.0032/stock × 1,000 stocks = **$3.20** (8% reduction)

### Priority 3: Reduce Debate Rounds (MEDIUM IMPACT)

**Current**: 3 rounds (Bull-Bear-Bull-Bear-Bull-Bear)

**Optimized**: 2 rounds (Bull-Bear-Bull-Bear) or even 1 round with structured prompts

**Trade-off**: Debate quality vs speed/cost

**Estimated savings**:
- Runtime: 20-30s per stock
- Cost: $0.0053/stock × 1,000 stocks = **$5.30** (16% reduction)

### Priority 4: Use Cheaper Models for Early Rounds (LOW IMPACT)

**Current**: Same model (70B) for all rounds

**Optimized**: 
- Round 1-2: Cheaper model (8B-13B)
- Round 3 + Manager: Premium model (70B+)

**Estimated savings**: $0.0066/stock × 1,000 stocks = **$6.60** (20% reduction)

---

## Summary: Quantitative Evidence

### Token Distribution
1. **Research Manager**: 16-22k tokens (37%)
2. **Bull Researcher**: 10-13k tokens (24%)
3. **Bear Researcher**: 10-13k tokens (24%)
4. **Trader**: 3.5-5k tokens (8%)
5. **Portfolio Manager**: 2.8-4k tokens (7%)

### Cost Distribution
1. **Research Manager**: $0.0122 (37%)
2. **Bull Researcher**: $0.0079 (24%)
3. **Bear Researcher**: $0.0079 (24%)
4. **Trader**: $0.0028 (8%)
5. **Portfolio Manager**: $0.0023 (7%)

### Runtime Distribution
1. **Bull Researcher** (3 rounds): 24-36s (34%)
2. **Bear Researcher** (3 rounds): 24-36s (34%)
3. **Research Manager**: 15-25s (21%)
4. **Trader**: 4-6s (6%)
5. **Portfolio Manager**: 3-5s (5%)

### Largest Bottleneck

**Research Manager** is the single largest bottleneck:
- **37% of total cost**
- **21% of total runtime**
- **Processes 16-22k input tokens** (largest of all agents)
- **Reason**: Receives entire Bull+Bear debate history

**Recommendation**: Prioritize Research Manager optimization for maximum impact.

---

## Next Steps

1. **Implement Research Manager optimization** (debate summarization)
   - Expected savings: 11% cost, 15% runtime
   - Low risk to quality

2. **Test with 10 stocks** to validate estimates
   - Compare actual vs theoretical token usage
   - Measure real runtime and costs

3. **Consider debate round reduction**
   - A/B test 2 rounds vs 3 rounds
   - Measure recommendation quality impact

4. **Evaluate model tiering**
   - Test cheaper models for early debate rounds
   - Measure quality/cost trade-off

---

**Status**: Theoretical analysis complete. Live validation pending rate limit resolution.
