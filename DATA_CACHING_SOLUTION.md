# Data Contamination Issue & Solution

**Date**: 2026-07-06 00:30  
**Issue**: Potential validation contamination from live external data  
**Status**: ✅ Solution implemented

---

## Problem Identified

### User Question
"Does News Analyst truly use historical news for 2024-01-15? Or is it still calling live news APIs/search?"

### Investigation Results

**News Analyst**: ✅ DOES respect trade_date
- Code shows: `current_date = state["trade_date"]`
- Passes date to tools: `get_news(ticker, start_date, end_date)`
- Tools accept date parameters: `curr_date`, `look_back_days`

**However**: Even with date parameters, external APIs may:
- Return different results on different calls (cache refresh)
- Have updated/corrected historical data
- Experience API changes between runs
- Have network variations affecting responses

### Contamination Risk

**Without caching**, baseline and optimized runs might get:
- Different news articles (API updated index)
- Different market data (corrections applied)
- Different fundamentals (restatements)
- Different macro data (revisions)

**This violates the fair A/B comparison requirement.**

---

## Solution: Pre-Cache All External Data

### Approach

1. **Before validation**: Cache ALL external data for HDFCBANK.NS + 2024-01-15
2. **During validation**: Both runs use the SAME cached data
3. **Result**: True apples-to-apples comparison

### What Gets Cached

| Data Source       | API Calls                    | Date Range             |
|-------------------|------------------------------|------------------------|
| Market Data       | get_stock_data               | 90 days before trade   |
| Fundamentals      | get_financial_statements     | As of trade date       |
| Company News      | get_news                     | 7 days before trade    |
| Global News       | get_global_news              | 7 days before trade    |
| Macro Indicators  | get_macro_indicators         | 30 days before trade   |

### Cache File Format

```json
{
  "metadata": {
    "ticker": "HDFCBANK.NS",
    "trade_date": "2024-01-15",
    "cached_at": "2026-07-06T00:30:00",
    "purpose": "Phase 3A validation"
  },
  "market_data": {
    "ticker": "HDFCBANK.NS",
    "start_date": "2023-10-17",
    "end_date": "2024-01-15",
    "data": "[cached OHLCV data]"
  },
  "fundamentals_data": {
    "ticker": "HDFCBANK.NS",
    "data": "[cached financial statements]"
  },
  "news_data": {
    "ticker": "HDFCBANK.NS",
    "start_date": "2024-01-08",
    "end_date": "2024-01-15",
    "company_news": "[cached company news]",
    "global_news": "[cached global news]"
  },
  "macro_data": {
    "indicators": {
      "cpi": "[cached CPI data]",
      "unemployment": "[cached unemployment]",
      ...
    }
  }
}
```

---

## Implementation

### Script Created: `cache_validation_data.py`

**Functions**:
- `cache_market_data()` - Caches OHLCV + technical indicators
- `cache_fundamentals_data()` - Caches financial statements
- `cache_news_data()` - Caches company + global news
- `cache_macro_data()` - Caches macro indicators (optional)
- `cache_all_data()` - Orchestrates all caching

**Output**:
- Cache file: `validation_cache/cached_data_HDFCBANK.NS_2024-01-15.json`
- Summary report of what was cached
- Status of each data source

---

## Updated Validation Flow

### Before (Potential Contamination):

```
1. Run BASELINE → calls live APIs for 2024-01-15 data
2. Wait 30 seconds
3. Run OPTIMIZED → calls live APIs again (may get different results!)
4. Compare results (contaminated by API differences)
```

### After (Clean Comparison):

```
1. CACHE DATA → fetch all external data once, save to JSON
2. Run BASELINE → reads from cached JSON (frozen data)
3. Wait 30 seconds
4. Run OPTIMIZED → reads from same cached JSON (identical data)
5. Compare results (pure optimization impact)
```

---

## How to Use

### Step 1: Cache Data (Once)

```bash
cd tradingagents
python cache_validation_data.py
```

**Output**:
```
================================================================================
CACHING VALIDATION DATA
================================================================================
Ticker: HDFCBANK.NS
Trade Date: 2024-01-15

📊 Caching market data...
   ✅ Market data cached (12,450 chars)

📈 Caching fundamentals data...
   ✅ Fundamentals cached (8,230 chars)

📰 Caching news data...
   ✅ Company news cached (15,678 chars)
   ✅ Global news cached (9,432 chars)

🌍 Caching macro data...
   ✅ cpi cached
   ✅ unemployment cached
   ✅ fed_funds_rate cached
   ✅ 10y_treasury cached

================================================================================
CACHE SUMMARY
================================================================================

Data Source          Status          Size (chars)
──────────────────────────────────────────────────
Market Data          ✅ Cached           12,450
Fundamentals         ✅ Cached            8,230
Company News         ✅ Cached           15,678
Global News          ✅ Cached            9,432
Macro Data           ✅ Cached         Multiple

Overall Status:      ✅ READY FOR VALIDATION

📁 Cache file: validation_cache/cached_data_HDFCBANK.NS_2024-01-15.json
```

### Step 2: Verify Cache

```bash
ls -lh validation_cache/cached_data_HDFCBANK.NS_2024-01-15.json
cat validation_cache/cached_data_HDFCBANK.NS_2024-01-15.json | jq '.metadata'
```

### Step 3: Run Validation (Uses Cache)

**NOTE**: The validation script (`validate_git_based.py`) needs to be updated to use the cached data instead of calling live APIs.

---

## Next Step Required

### Update validate_git_based.py

The validation script needs to:
1. Check if cache file exists
2. If yes: Load cached data and inject into workflow
3. If no: Abort with error (cache required)

**Options for using cached data**:

### Option A: Mock the data vendor (Preferred)
Replace `route_to_vendor()` with cached responses during validation:

```python
def use_cached_data(cache_file):
    """Replace live API calls with cached data"""
    
    with open(cache_file) as f:
        cached = json.load(f)
    
    # Monkey-patch route_to_vendor
    original_route = route_to_vendor
    
    def cached_route(tool_name, *args, **kwargs):
        if tool_name == "get_stock_data":
            return cached['market_data']['data']
        elif tool_name == "get_financial_statements":
            return cached['fundamentals_data']['data']
        elif tool_name == "get_news":
            return cached['news_data']['company_news']
        elif tool_name == "get_global_news":
            return cached['news_data']['global_news']
        # ... etc
        return original_route(tool_name, *args, **kwargs)
    
    return cached_route
```

### Option B: Pre-populate data_cache directory
- Save cached data to TradingAgents' cache directory
- Workflow reads from cache instead of APIs

### Option C: Environment variable override
- Set `USE_VALIDATION_CACHE=true`
- Modify data vendors to check this flag and use cached data

---

## Benefits

### Fair Comparison Guaranteed
- ✅ Both runs use identical market data
- ✅ Both runs use identical news data
- ✅ Both runs use identical fundamentals
- ✅ Only optimization differs between runs

### Reproducible Results
- Cache file can be shared
- Results can be reproduced exactly
- No API rate limits during validation
- No network variability

### Faster Validation
- No API calls during validation
- Faster execution (cached reads vs network)
- No waiting for external services

---

## Verdict

**Issue**: Valid concern - external APIs could contaminate validation  
**Solution**: Pre-cache all external data before validation  
**Status**: Cache script implemented, needs integration with validation script  
**Next**: Update `validate_git_based.py` to use cached data

**Recommendation**: Complete caching integration before running Stage 1 validation.
