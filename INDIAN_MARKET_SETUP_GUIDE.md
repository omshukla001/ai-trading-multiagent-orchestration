# TradingAgents - Indian Market Setup Guide

## Current Status: API Key Required

⚠️ **Action Required**: You need a valid Google Gemini API key to proceed.

### Getting Your API Key (2 minutes):

1. **Visit**: https://aistudio.google.com/apikey
2. **Sign in** with your Google account
3. **Click**: "Create API Key" or "Get API Key"
4. **Copy** the key (format: `AIzaSy` + 33 more characters = 39 chars total)

**Important**: 
- The key you provided starts with `AQ.Ab8RN6J4-...` which is not a valid Google Gemini key format
- Valid Google keys look like: `AIzaSyDK8x9_abc123XYZ...` (39 characters)

---

## What You'll Get: Example Indian Stock Analysis

Once configured, here's what a typical analysis will look like:

### Input:
```python
Ticker: RELIANCE.NS
Date: 2026-06-29
Capital: ₹200,000
Risk per trade: 2% (₹4,000 max)
```

### Output Example:

```
================================================================================
TRADE RECOMMENDATION - RELIANCE.NS
================================================================================

Stock: Reliance Industries Ltd
Market: NSE (National Stock Exchange)
Sector: Energy/Conglomerate
Signal: BUY
Confidence: 78%

================================================================================
FUNDAMENTAL ANALYSIS
================================================================================
Market Cap: ₹18,50,000 Cr
P/E Ratio: 24.5
Revenue Growth (YoY): 12%
Debt/Equity: 0.45
ROE: 11.2%

Key Strengths:
✓ Strong balance sheet
✓ Diversified revenue streams (Oil, Retail, Telecom)
✓ Consistent cash flow generation
✓ Market leadership in multiple sectors

Concerns:
⚠ Oil price dependency
⚠ High valuation compared to sector peers

================================================================================
TECHNICAL ANALYSIS
================================================================================
Current Price: ₹1,450
52-Week High: ₹1,580
52-Week Low: ₹1,210

Technical Indicators:
• RSI (14): 62 - Bullish but not overbought
• MACD: Bullish crossover
• EMA 20: ₹1,420 (Price above)
• EMA 50: ₹1,390 (Price above)
• EMA 200: ₹1,350 (Price above - Strong uptrend)
• Volume: Above average (bullish confirmation)

Support Levels: ₹1,420, ₹1,390, ₹1,350
Resistance Levels: ₹1,480, ₹1,520, ₹1,580

Pattern: Ascending triangle breakout confirmed

================================================================================
NEWS & SENTIMENT ANALYSIS
================================================================================
Recent News (Last 7 Days):
• [Positive] Reliance announces $5B investment in renewable energy
• [Neutral] Q4 earnings meet street expectations
• [Positive] Jio subscriber additions beat estimates

Market Sentiment: BULLISH (65% positive)
- Institutional buying increased
- FII inflows positive
- Strong retail interest

Sector Momentum: Energy sector showing strength (+3.2% this week)

================================================================================
RISK MANAGEMENT ASSESSMENT
================================================================================
Position Sizing Analysis:
Capital Available: ₹2,00,000
Risk per Trade: 2% = ₹4,000
Stop Loss Distance: ₹50 (from ₹1,450 to ₹1,400)

Recommended Position:
Shares to Buy: 80 shares
Total Investment: ₹1,16,000 (58% of capital)
Risk Amount: ₹4,000 (exactly 2% of capital)

Risk/Reward Ratio: 1:2.5
Expected Upside: ₹125 per share
Expected Downside (SL): ₹50 per share

================================================================================
FINAL RECOMMENDATION
================================================================================

🎯 TRADE SETUP:

Action: BUY
Entry Zone: ₹1,440 - ₹1,460
Optimal Entry: ₹1,450

Stop Loss: ₹1,400 (3.5% below entry)
Target 1: ₹1,525 (5.2% gain)
Target 2: ₹1,575 (8.6% gain)

Holding Period: 7-14 days (swing trade)

Capital Allocation: ₹1,16,000 (80 shares)
Maximum Risk: ₹4,000 (2% of capital)

Risk/Reward: 1:2.5 (Excellent)

================================================================================
STRATEGY NOTES
================================================================================

Entry Strategy:
• Buy in 2 tranches: 50% at ₹1,450, 50% on dip to ₹1,440
• Avoid buying above ₹1,460

Exit Strategy:
• Exit 50% at Target 1 (₹1,525)
• Move SL to breakeven
• Exit remaining 50% at Target 2 (₹1,575)
• Strict SL at ₹1,400 - NO exceptions

Market Conditions Required:
✓ NIFTY 50 above 21,500 (market strength)
✓ Banking sector strong (RIL correlation)
✓ Crude oil prices stable

Red Flags (Cancel Trade):
❌ Break below ₹1,420 before entry
❌ NIFTY breakdown below 21,200
❌ Major negative news (earnings miss, regulatory issues)

================================================================================
PROBABILITY ASSESSMENT
================================================================================

Success Probability: 78%
Based on:
• Technical setup strength: 85%
• Fundamental support: 75%
• Market conditions: 80%
• News sentiment: 70%
• Sector momentum: 75%

Historical Performance:
Similar setups in RELIANCE.NS: 72% win rate over last 2 years
Average gain on winners: 7.2%
Average loss on losers: 2.8%

================================================================================
```

---

## System Features Once Configured:

### 1. **Multi-Agent Analysis**
- 4 Analyst Agents (Fundamentals, Technical, News, Sentiment)
- 2 Researcher Agents (Bull vs Bear debate)
- 1 Trader Agent (synthesizes recommendations)
- 3 Risk Management Agents (Conservative, Aggressive, Neutral)
- 1 Portfolio Manager (final approval)

### 2. **Indian Market Support**
✅ NSE stocks (`.NS` suffix): RELIANCE.NS, TCS.NS, INFY.NS
✅ BSE stocks (`.BO` suffix): RELIANCE.BO, HDFC.BO
✅ Yahoo Finance data (free, no API key needed)
✅ Technical indicators (RSI, MACD, EMA, Volume)
✅ INR-based risk management

### 3. **Commodities Support** (International proxies via Yahoo Finance)
- Gold: `GC=F`
- Silver: `SI=F`
- Crude Oil: `CL=F`

---

## What Needs Customization (Phase 4):

### Current Limitations:
1. ❌ News sources are US-focused (not Moneycontrol/ET/BS)
2. ❌ Benchmark is SPY (should be NIFTY 50)
3. ❌ No direct MCX integration (using international proxies)
4. ❌ Social sentiment from Reddit/StockTwits (not Indian sources)

### Customization Plan:
1. Replace news sources with Indian media scrapers
2. Change alpha benchmark from SPY to ^NSEI (NIFTY 50)
3. Add MCX commodity support
4. Integrate Zerodha Kite API (optional)
5. Add RBI policy tracking
6. Customize prompts for Indian market context

---

## Next Steps:

### Step 1: Get Valid API Key
**You MUST do this first:**
1. Go to: **https://aistudio.google.com/apikey**
2. Sign in with Google
3. Create API key
4. Copy the key (format: `AIzaSy...` 39 characters)

### Step 2: Test Basic System
```bash
cd /Users/omshukla/tradingagents
source venv/bin/activate

# Edit .env file
nano .env

# Replace GOOGLE_API_KEY= with your new key
# Then run:
python test_api_key.py
```

### Step 3: Run Indian Stock Analysis
```bash
python test_indian_stock.py
```

### Step 4: Customize for Indian Markets
(We'll do this together after Step 3 works)

---

## Cost Estimate:

**Using Google Gemini (gemini-3.5-flash):**
- Cost per analysis: ~$0.10-0.30
- 10 stock analyses: ~$2-3
- **API calls**: Free tier: 15 requests/minute, 1500/day

**Alternative - OpenAI (gpt-4o-mini):**
- Cost per analysis: ~$0.20-0.50
- 10 stock analyses: ~$3-5

---

## Support:

If you're having trouble getting the API key, you can alternatively:
1. Use OpenAI: https://platform.openai.com/api-keys
2. Use Anthropic Claude: https://console.anthropic.com/
3. Use local models (free, but slower): Configure Ollama

---

**Ready to proceed once you have a valid API key!**
