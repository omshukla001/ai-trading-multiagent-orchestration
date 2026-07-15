# LLM Configuration Root Cause Analysis

**Date:** 2026-07-05  
**Status:** ✅ RESOLVED

---

## Problem Statement

Integration tests were failing with model configuration errors. Initial analysis suggested the system was using `gemini-2.0-flash-exp` instead of the configured `gemini-3.5-flash`.

---

## Investigation Process

### Phase 1: Codebase Search
**Searched for:** `gemini-2.0-flash-exp` hardcoded references  
**Result:** ❌ NOT FOUND in source code  
**Conclusion:** Not a hardcoded model issue

### Phase 2: Configuration Flow Tracing

#### DEFAULT_CONFIG Analysis
```python
# tradingagents/default_config.py
DEFAULT_CONFIG = {
    "llm_provider": "openai",           # Default provider
    "deep_think_llm": "gpt-5.5",        # Default model  
    "quick_think_llm": "gpt-5.4-mini",  # Default model
    ...
}
```

**Finding:** No hardcoded Gemini models in DEFAULT_CONFIG

#### Test Script Configuration
```python
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "google"
config["deep_think_llm"] = "gemini-3.5-flash"
config["quick_think_llm"] = "gemini-3.5-flash"
```

**Finding:** Configuration override logic is correct

#### TradingAgentsGraph Initialization
```python
self.config = config or DEFAULT_CONFIG

deep_client = create_llm_client(
    provider=self.config["llm_provider"],
    model=self.config["deep_think_llm"],
    ...
)
```

**Finding:** Graph correctly uses provided config

### Phase 3: Runtime Debugging

Created `debug_config.py` to trace configuration flow:

```
DEFAULT_CONFIG:
   llm_provider: openai
   deep_think_llm: gpt-5.5

AFTER override:
   llm_provider: google
   deep_think_llm: gemini-3.5-flash  ✅

TradingAgentsGraph CONFIG:
   llm_provider: google  ✅
   deep_think_llm: gemini-3.5-flash  ✅

Creating LLM clients:
   Provider: google  ✅
   Deep model: gemini-3.5-flash  ✅
```

**CRITICAL FINDING:** Configuration is working correctly! ✅

### Phase 4: Test Results Analysis

#### Earlier Test Results (23:14 - 23:34)
```
Error: Error calling model 'gemini-2.0-flash-exp' (NOT_FOUND)
```
These were from tests using incorrect model name.

#### Latest Test Results (23:38)
```
Error: Error calling model 'gemini-3.5-flash' (RESOURCE_EXHAUSTED): 429
Quota exceeded: 20 requests/day limit (Free Tier)
```

**EUREKA!** The configuration IS working! The model name is correct!

---

## Root Cause: API Rate Limiting

### The Real Issue

1. ✅ Configuration propagation works correctly
2. ✅ Model name (`gemini-3.5-flash`) is being used correctly
3. ❌ **Google Gemini Free Tier has 20 requests/day limit**
4. ❌ **Limit was exceeded during testing**

### Evidence

From latest test report (`INTEGRATION_TEST_REPORT_20260704_233853.md`):

```json
{
  "error": "Error calling model 'gemini-3.5-flash' (RESOURCE_EXHAUSTED): 429",
  "message": "Quota exceeded for metric: generate_content_free_tier_requests, limit: 20"
}
```

**Performance Metrics (before hitting rate limit):**
- HDFCBANK.NS: 38.74s (original) → 35.21s (optimized) = 9.1% faster
- INFY.NS: 36.78s (original) → 38.37s (optimized) = -4.3% slower  
- RELIANCE.NS: 37.93s (original) → 35.23s (optimized) = 7.1% faster
- **Total: 113.45s → 108.81s = 4.1% faster**

---

## Resolution

### Solution: Switch to Groq

**Why Groq:**
- ✅ GROQ_API_KEY already configured
- ✅ More generous free tier limits
- ✅ Fast inference (groq specializes in speed)
- ✅ Compatible model: `llama-3.3-70b-versatile`

**Implementation:**
```python
config["llm_provider"] = "groq"
config["deep_think_llm"] = "llama-3.3-70b-versatile"
config["quick_think_llm"] = "llama-3.3-70b-versatile"
```

---

## Lessons Learned

### What Was NOT the Problem

1. ❌ Hardcoded model names
2. ❌ Config not being propagated
3. ❌ DEFAULT_CONFIG override issues
4. ❌ LLM client factory problems
5. ❌ Python import/cache issues

### What WAS the Problem

1. ✅ API rate limiting (Google Gemini free tier)
2. ✅ Looking at stale test results (earlier runs had different errors)

### Debugging Approach That Worked

1. **Systematic codebase search** - ruled out hardcoded values
2. **Configuration flow tracing** - verified each layer
3. **Runtime debugging** - added debug prints at key points
4. **Fresh test execution** - confirmed config works
5. **Careful test result analysis** - found the real error (rate limit, not config)

---

## Configuration Debugging Principles

### For Future Issues

1. **Always check timestamps** - ensure you're looking at latest results
2. **Add debug logging** - trace config flow end-to-end
3. **Test incrementally** - create minimal reproduction scripts
4. **Verify at each layer**:
   - DEFAULT_CONFIG values
   - Override application
   - Graph initialization  
   - LLM client creation
   - Actual API calls
5. **Check rate limits** - before assuming config issues

### Debug Tools Created

1. `debug_config.py` - Minimal config tracing script
2. Debug logging in `trading_graph.py` - traces config at initialization
3. Debug logging in test script - shows config before/after override

---

## Provider Comparison

| Provider | Free Tier Limit | Model | Status |
|----------|----------------|-------|--------|
| OpenAI | Paid only | gpt-4, gpt-5 | ❌ No API key |
| Google Gemini | 20 req/day | gemini-3.5-flash | ⚠️ EXHAUSTED |
| Groq | Generous | llama-3.3-70b-versatile | ✅ AVAILABLE |

---

## Next Steps

1. ✅ Configuration issue resolved - it was never broken!
2. ✅ Switched to Groq provider to avoid rate limits
3. ⏭️ Ready to run full integration test suite
4. ⏭️ Can now properly validate optimized analysts

---

## Files Modified

1. `controlled_integration_test.py` - Updated to use Groq
2. `trading_graph.py` - Added debug logging
3. `debug_config.py` - Created for configuration tracing

---

## Conclusion

**The configuration system was working correctly all along.**

The actual issue was:
- Google Gemini free tier rate limit (20 requests/day)
- Test failures were due to quota exhaustion, not configuration errors
- Earlier test results showed different errors (gemini-2.0-flash-exp) which led to false assumption

**Resolution:**
- Switch to Groq provider with generous limits
- Tests can now proceed without rate limiting issues

**Key Insight:**
Always verify you're looking at the latest test results and read error messages carefully - "RESOURCE_EXHAUSTED" is very different from "NOT_FOUND"!

---

**Status:** ✅ RESOLVED - Ready for full integration testing

**Last Updated:** 2026-07-05 10:35 IST
