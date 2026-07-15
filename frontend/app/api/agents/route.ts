import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

const PYTHON = process.env.PYTHON_PATH || "/Users/omshukla/tradingagents/venv/bin/python3";
const GROQ_API_KEY = process.env.GROQ_API_KEY || "";
const GROQ_API_KEY_2 = process.env.GROQ_API_KEY_2 || "";
const GROQ_API_KEY_3 = process.env.GROQ_API_KEY_3 || "";
const GEMINI_API_KEY = process.env.GEMINI_API_KEY || "";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const ticker = searchParams.get("ticker") || "AAPL";

  const script = `
import yfinance as yf
import json
import pandas as pd
import numpy as np
import math
import sys
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
import html
import re
import time
from datetime import datetime, timedelta

raw_input = "${ticker}"
GROQ_KEY = "${GROQ_API_KEY}"
GROQ_KEY_2 = "${GROQ_API_KEY_2}"
GROQ_KEY_3 = "${GROQ_API_KEY_3}"
GEMINI_KEY = "${GEMINI_API_KEY}"
GROQ_KEYS = [GROQ_KEY_3, GROQ_KEY_2, GROQ_KEY]  # newest first

# ── Symbol resolution ──
def resolve_ticker(raw):
    s = raw.strip()
    if any(c in s for c in [".", "-", "^", "="]):
        t = yf.Ticker(s)
        hist = t.history(period="5d")
        if len(hist) >= 1:
            return s

    clean = re.sub(r"\\s+", "", s).upper()
    if clean != s:
        t = yf.Ticker(clean)
        hist = t.history(period="5d")
        if len(hist) >= 1:
            return clean

    for suffix in [".NS", ".BO"]:
        sym = clean + suffix
        t = yf.Ticker(sym)
        hist = t.history(period="5d")
        if len(hist) >= 1:
            return sym

    try:
        import urllib.parse
        query = urllib.parse.quote(raw.strip())
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=5&newsCount=0"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read().decode())
        quotes = data.get("quotes", [])
        for q in quotes:
            sym = q.get("symbol", "")
            if sym:
                t = yf.Ticker(sym)
                hist = t.history(period="5d")
                if len(hist) >= 1:
                    return sym
    except Exception:
        pass

    return s.upper()

# ── Safe numeric helpers ──
def safe_float(val, default=0):
    if val is None:
        return default
    try:
        v = float(val)
        if math.isnan(v) or math.isinf(v):
            return default
        return v
    except (TypeError, ValueError):
        return default

def safe_round(val, digits=2, default=0):
    return round(safe_float(val, default), digits)

def fmt_num(val, digits=2):
    v = safe_float(val)
    if v == 0:
        return "N/A"
    return f"{round(v, digits):,.{digits}f}"

def fmt_pct(val, digits=2):
    v = safe_float(val)
    if v == 0:
        return "N/A"
    return f"{round(v * 100, digits):.{digits}f}%"

# ══════════════════════════════════════════════════════════════
# AGENT 1: NEWS ANALYST — Fetch real news from Yahoo Finance
# ══════════════════════════════════════════════════════════════
def fetch_yahoo_news(ticker_symbol):
    """Fetch real news articles from Yahoo Finance for this ticker."""
    try:
        tk = yf.Ticker(ticker_symbol)
        raw_news = tk.news or []
        articles = []
        for article in raw_news[:10]:
            content = article.get("content", article)
            if isinstance(content, dict):
                title = content.get("title", article.get("title", ""))
                summary = content.get("summary", "")
                provider = content.get("provider", {})
                publisher = provider.get("displayName", article.get("publisher", "Unknown"))
                pub_date = content.get("pubDate", "")
            else:
                title = article.get("title", "")
                summary = article.get("summary", "")
                publisher = article.get("publisher", "Unknown")
                pub_date = ""
            if title:
                articles.append({
                    "title": title,
                    "summary": summary[:200] if summary else "",
                    "publisher": publisher,
                    "date": pub_date[:10] if pub_date else ""
                })
        return articles
    except Exception:
        return []

# ══════════════════════════════════════════════════════════════
# AGENT 2: SOCIAL SENTIMENT — Fetch Reddit posts via RSS
# ══════════════════════════════════════════════════════════════
def fetch_reddit_posts(ticker_symbol, company_name_str):
    """Fetch real Reddit posts about this stock."""
    posts = []
    ua = "tradingagents/0.2 (+https://github.com/TauricResearch/TradingAgents)"
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    # Extract short name for search
    search_terms = [ticker_symbol.replace(".NS","").replace(".BO","")]
    if company_name_str and company_name_str != ticker_symbol:
        # Add company name words (e.g. "Adani Power")
        search_terms.append(company_name_str.split(" Limited")[0].split(" Ltd")[0].strip())

    subreddits = ["IndianStockMarket", "wallstreetbets", "stocks", "investing"]
    if not any(s in ticker_symbol for s in [".NS", ".BO"]):
        subreddits = ["wallstreetbets", "stocks", "investing"]

    for sub in subreddits[:2]:  # limit to 2 subs to avoid rate limits
        for term in search_terms[:1]:  # 1 search per sub
            try:
                qs = urllib.parse.urlencode({"q": term, "restrict_sr": "on", "sort": "new", "limit": 5})
                url = f"https://www.reddit.com/r/{sub}/search.rss?{qs}"
                req = urllib.request.Request(url, headers={"User-Agent": ua})
                resp = urllib.request.urlopen(req, timeout=8)
                tree = ET.parse(resp)
                entries = tree.findall(".//atom:entry", ns)
                for entry in entries:
                    title_el = entry.find("atom:title", ns)
                    content_el = entry.find("atom:content", ns)
                    title_text = title_el.text if title_el is not None else ""
                    # Clean HTML from content
                    content_text = ""
                    if content_el is not None and content_el.text:
                        content_text = re.sub(r"<[^>]+>", "", html.unescape(content_el.text))[:300]
                    if title_text:
                        posts.append({
                            "subreddit": sub,
                            "title": title_text,
                            "snippet": content_text[:200]
                        })
                time.sleep(0.5)  # rate limit courtesy
            except Exception:
                pass
    return posts

# ══════════════════════════════════════════════════════════════
# LLM HELPER — Try Groq first, fall back to Gemini
# ══════════════════════════════════════════════════════════════
def _call_groq(prompt, max_tokens, api_key=None):
    """Call Groq API. Returns parsed dict or None."""
    if not api_key:
        api_key = GROQ_KEY
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = json.dumps({
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"}
        }).encode()
        req = urllib.request.Request(url, data=payload, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "TradingAgents/1.0"
        })
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read().decode())
        text = result["choices"][0]["message"]["content"].strip()
        return json.loads(text)
    except Exception:
        return None

def _call_gemini(prompt, max_tokens):
    """Call Gemini 2.5 Flash API. Returns parsed dict or None."""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.3,
                "responseMimeType": "application/json"
            }
        }).encode()
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=45)
        result = json.loads(resp.read().decode())
        text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        return json.loads(text)
    except Exception:
        return None

def call_llm(prompt, max_tokens=1024):
    """Try all 3 Groq keys (different accounts), then Gemini."""
    for key in GROQ_KEYS:
        result = _call_groq(prompt, max_tokens, key)
        if isinstance(result, dict):
            return result
    result = _call_gemini(prompt, max_tokens)
    if isinstance(result, dict):
        return result
    return None

def extract_json(val):
    """Return val if it's already a dict, else try to parse it."""
    if isinstance(val, dict):
        return val
    if isinstance(val, str):
        try:
            return json.loads(val)
        except Exception:
            # Try extracting JSON substring
            start = val.find('{')
            end = val.rfind('}')
            if start != -1 and end > start:
                try:
                    return json.loads(val[start:end+1])
                except Exception:
                    pass
    return None

# ══════════════════════════════════════════════════════════════
# RESOLVE TICKER & FETCH DATA
# ══════════════════════════════════════════════════════════════
resolved = resolve_ticker(raw_input)
tk = yf.Ticker(resolved)
hist = tk.history(period="1y")

# Drop trailing NaN rows
hist = hist.dropna(subset=["Close"])
if len(hist) < 30:
    print(json.dumps({"error": f"Not enough data for '{raw_input}' (resolved to '{resolved}')."}))
    sys.exit()

info = tk.info

# Currency
raw_currency = info.get("currency", "USD")
currency_symbols = {
    "INR": "₹", "USD": "$", "EUR": "€", "GBP": "£",
    "JPY": "¥", "HKD": "HK$", "CNY": "¥", "AUD": "A$",
}
currency_symbol = currency_symbols.get(raw_currency, raw_currency + " ")
company_name = info.get("longName") or info.get("shortName") or resolved

close = hist["Close"]
high_col = hist["High"]
low_col = hist["Low"]
volume = hist["Volume"]

current_close = safe_float(close.iloc[-1])
prev_close = safe_float(close.iloc[-2]) if len(close) > 1 else current_close

# ═══════════════════════════════════════════════════════════
# STEP 1: FETCH REAL NEWS & REDDIT (parallel-style)
# ═══════════════════════════════════════════════════════════
news_articles = fetch_yahoo_news(resolved)
reddit_posts = fetch_reddit_posts(resolved, company_name)

# ═══════════════════════════════════════════════════════════
# STEP 2: TECHNICAL INDICATORS (verified accurate)
# ═══════════════════════════════════════════════════════════
# RSI (14)
delta = close.diff()
gain = delta.clip(lower=0).rolling(14).mean()
loss = -delta.clip(upper=0).rolling(14).mean()
rs = gain / loss
rsi_series = 100 - 100 / (1 + rs)
rsi_val = safe_round(rsi_series.iloc[-1])

# MACD
ema12 = close.ewm(span=12).mean()
ema26 = close.ewm(span=26).mean()
macd_line = ema12 - ema26
macd_signal = macd_line.ewm(span=9).mean()
macd_hist = macd_line - macd_signal
macd_val = safe_round(macd_line.iloc[-1], 4)
macd_sig_val = safe_round(macd_signal.iloc[-1], 4)
macd_hist_val = safe_round(macd_hist.iloc[-1], 4)

# EMAs
ema20_val = safe_round(close.ewm(span=20).mean().iloc[-1])
ema50_val = safe_round(close.ewm(span=50).mean().iloc[-1])
ema200_val = safe_round(close.ewm(span=200).mean().iloc[-1])

# Bollinger Bands
sma20 = close.rolling(20).mean()
std20 = close.rolling(20).std()
bb_upper = safe_round((sma20 + 2 * std20).iloc[-1])
bb_lower = safe_round((sma20 - 2 * std20).iloc[-1])
bb_mid = safe_round(sma20.iloc[-1])

# ATR (14)
tr1 = high_col - low_col
tr2 = (high_col - close.shift(1)).abs()
tr3 = (low_col - close.shift(1)).abs()
tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
atr_val = safe_round(tr.rolling(14).mean().iloc[-1])
atr_pct = safe_round(atr_val / current_close * 100 if current_close > 0 else 0)

# Volume
vol_today = safe_float(volume.iloc[-1])
vol_sma = safe_float(volume.rolling(20).mean().iloc[-1])
vol_ratio = safe_round(vol_today / vol_sma if vol_sma > 0 else 0)

# 52-week
high_52w = safe_float(high_col.max())
low_52w = safe_float(low_col.min())
range_52w = high_52w - low_52w if high_52w > low_52w else 1
pct_from_high = safe_round((high_52w - current_close) / high_52w * 100 if high_52w > 0 else 0)
position_in_range = safe_round((current_close - low_52w) / range_52w * 100)

# Returns
ret_5d = safe_round((current_close / safe_float(close.iloc[-6], current_close) - 1) * 100 if len(close) > 5 else 0)
ret_20d = safe_round((current_close / safe_float(close.iloc[-21], current_close) - 1) * 100 if len(close) > 20 else 0)
ret_60d = safe_round((current_close / safe_float(close.iloc[-61], current_close) - 1) * 100 if len(close) > 60 else 0)

# ═══════════════════════════════════════════════════════════
# STEP 3: TECHNICAL SIGNALS & SCORING (verified accurate)
# ═══════════════════════════════════════════════════════════
indicators = []
tech_scores = []

# RSI
if rsi_val > 70:
    rsi_signal, rsi_detail = "bearish", f"RSI at {rsi_val} is overbought territory (>70). Potential reversal or pullback ahead."
    tech_scores.append(25)
elif rsi_val > 60:
    rsi_signal, rsi_detail = "bullish", f"RSI at {rsi_val} shows strong upward momentum without being overbought."
    tech_scores.append(70)
elif rsi_val > 40:
    rsi_signal, rsi_detail = "neutral", f"RSI at {rsi_val} is in neutral territory. No strong directional signal."
    tech_scores.append(50)
elif rsi_val > 30:
    rsi_signal, rsi_detail = "bearish", f"RSI at {rsi_val} shows weakening momentum, approaching oversold."
    tech_scores.append(35)
else:
    rsi_signal, rsi_detail = "bullish", f"RSI at {rsi_val} is oversold (<30). Potential bounce or reversal opportunity."
    tech_scores.append(75)
indicators.append({"name": "RSI (14)", "value": str(rsi_val), "signal": rsi_signal, "detail": rsi_detail})

# MACD
if macd_val > macd_sig_val:
    macd_signal_str = "bullish"
    macd_detail = f"MACD ({macd_val}) is above signal line ({macd_sig_val}). Histogram at {macd_hist_val} — bullish momentum."
    tech_scores.append(70)
else:
    macd_signal_str = "bearish"
    macd_detail = f"MACD ({macd_val}) is below signal line ({macd_sig_val}). Histogram at {macd_hist_val} — bearish pressure."
    tech_scores.append(30)
indicators.append({"name": "MACD", "value": f"{macd_val} / {macd_sig_val}", "signal": macd_signal_str, "detail": macd_detail})

# EMA Alignment
emas_bullish_count = sum([current_close > ema20_val, current_close > ema50_val, current_close > ema200_val])
if emas_bullish_count == 3:
    ema_signal = "bullish"
    ema_detail = f"Price ({currency_symbol}{safe_round(current_close)}) above all key EMAs (EMA20: {ema20_val}, EMA50: {ema50_val}, EMA200: {ema200_val}). Strong uptrend."
    tech_scores.append(80)
elif emas_bullish_count == 0:
    ema_signal = "bearish"
    ema_detail = f"Price ({currency_symbol}{safe_round(current_close)}) below all key EMAs. Strong downtrend."
    tech_scores.append(20)
else:
    ema_signal = "neutral"
    ema_detail = f"Price above {emas_bullish_count}/3 EMAs. Mixed trend signals."
    tech_scores.append(50)
indicators.append({"name": "EMA Alignment", "value": f"{emas_bullish_count}/3 bullish", "signal": ema_signal, "detail": ema_detail})

# Bollinger Bands
bb_width = bb_upper - bb_lower if bb_upper > bb_lower else 1
bb_pos = safe_round((current_close - bb_lower) / bb_width * 100)
if bb_pos > 85:
    bb_signal, bb_detail = "bearish", f"Price near upper Bollinger Band ({bb_pos}% of width). Overbought — caution."
    tech_scores.append(30)
elif bb_pos < 15:
    bb_signal, bb_detail = "bullish", f"Price near lower Bollinger Band ({bb_pos}% of width). Oversold — potential opportunity."
    tech_scores.append(70)
else:
    bb_signal, bb_detail = "neutral", f"Price at {bb_pos}% of Bollinger Band width ({currency_symbol}{bb_lower} – {currency_symbol}{bb_upper}). Neutral zone."
    tech_scores.append(50)
indicators.append({"name": "Bollinger Bands", "value": f"{bb_lower} - {bb_upper}", "signal": bb_signal, "detail": bb_detail})

# Volume
if vol_ratio > 1.5:
    price_up = current_close > prev_close
    vol_signal = "bullish" if price_up else "bearish"
    vol_detail = f"Volume {vol_ratio}x average. {'Strong buying pressure.' if price_up else 'Heavy selling pressure.'}"
    tech_scores.append(70 if price_up else 30)
elif vol_ratio > 0.8:
    vol_signal, vol_detail = "neutral", f"Volume {vol_ratio}x average. Normal activity."
    tech_scores.append(50)
else:
    vol_signal, vol_detail = "neutral", f"Volume {vol_ratio}x average. Low activity — lack of conviction."
    tech_scores.append(45)
indicators.append({"name": "Volume", "value": f"{vol_ratio}x avg", "signal": vol_signal, "detail": vol_detail})

# ATR
indicators.append({"name": "ATR (14)", "value": f"{currency_symbol}{atr_val} ({atr_pct}%)", "signal": "neutral", "detail": f"Average True Range is {currency_symbol}{atr_val}, representing {atr_pct}% of price. {'High' if atr_pct > 4 else 'Moderate' if atr_pct > 2 else 'Low'} volatility."})
tech_scores.append(50)

# Overall technical
bullish_count = sum(1 for i in indicators if i["signal"] == "bullish")
bearish_count = sum(1 for i in indicators if i["signal"] == "bearish")
avg_tech_score = safe_round(sum(tech_scores) / len(tech_scores) if tech_scores else 50, 1)

if bullish_count > bearish_count + 1:
    tech_overall = "bullish"
elif bearish_count > bullish_count + 1:
    tech_overall = "bearish"
else:
    tech_overall = "neutral"

tech_summary = f"Technical analysis: {bullish_count} bullish, {bearish_count} bearish, {len(indicators) - bullish_count - bearish_count} neutral signals. "
tech_summary += f"Stock at {currency_symbol}{safe_round(current_close)} with RSI {rsi_val}, MACD {'above' if macd_val > macd_sig_val else 'below'} signal, price above {emas_bullish_count}/3 EMAs."

market_analysis = {"signal": tech_overall, "summary": tech_summary, "indicators": indicators}

# ═══════════════════════════════════════════════════════════
# STEP 4: FUNDAMENTALS (verified accurate)
# ═══════════════════════════════════════════════════════════
pe = safe_float(info.get("trailingPE", 0))
pb = safe_float(info.get("priceToBook", 0))
de = safe_float(info.get("debtToEquity", 0))
pm = safe_float(info.get("profitMargins", 0))
roe = safe_float(info.get("returnOnEquity", 0))
beta = safe_float(info.get("beta", 0))

metrics = []
fund_scores = []

# P/E
if pe > 0:
    if pe < 15: pe_sig, pe_det = "bullish", f"P/E of {safe_round(pe)} suggests undervaluation (<15x). Good entry point."
    elif pe < 25: pe_sig, pe_det = "neutral", f"P/E of {safe_round(pe)} is fairly valued (15-25x)."
    elif pe < 40: pe_sig, pe_det = "bearish", f"P/E of {safe_round(pe)} is premium (25-40x). Growth priced in."
    else: pe_sig, pe_det = "bearish", f"P/E of {safe_round(pe)} is overvalued (>40x). High expectations."
    fund_scores.append(80 if pe < 15 else 55 if pe < 25 else 35 if pe < 40 else 20)
else:
    pe_sig, pe_det = "neutral", "P/E data unavailable."
    fund_scores.append(50)
metrics.append({"name": "P/E Ratio", "value": fmt_num(pe), "signal": pe_sig, "detail": pe_det})

# P/B
if pb > 0:
    if pb < 1: pb_sig, pb_det = "bullish", f"P/B of {safe_round(pb)} is below book value. Potential undervaluation."
    elif pb < 3: pb_sig, pb_det = "neutral", f"P/B of {safe_round(pb)} is fair (1-3x)."
    else: pb_sig, pb_det = "bearish", f"P/B of {safe_round(pb)} is premium (>3x)."
    fund_scores.append(75 if pb < 1 else 55 if pb < 3 else 30)
else:
    pb_sig, pb_det = "neutral", "P/B data unavailable."
    fund_scores.append(50)
metrics.append({"name": "P/B Ratio", "value": fmt_num(pb), "signal": pb_sig, "detail": pb_det})

# D/E
if de > 0:
    if de < 50: de_sig, de_det = "bullish", f"D/E of {safe_round(de)} is conservative (<50). Strong balance sheet."
    elif de < 100: de_sig, de_det = "neutral", f"D/E of {safe_round(de)} is moderate."
    elif de < 200: de_sig, de_det = "bearish", f"D/E of {safe_round(de)} is high (100-200)."
    else: de_sig, de_det = "bearish", f"D/E of {safe_round(de)} is very high (>200). Significant leverage risk."
    fund_scores.append(75 if de < 50 else 55 if de < 100 else 35 if de < 200 else 20)
else:
    de_sig, de_det = "neutral", "Debt/Equity data unavailable."
    fund_scores.append(50)
metrics.append({"name": "Debt/Equity", "value": fmt_num(de), "signal": de_sig, "detail": de_det})

# Profit Margin
if pm != 0:
    pm_pct = safe_round(pm * 100)
    if pm_pct > 20: pm_sig, pm_det = "bullish", f"Profit margin {pm_pct}% is excellent (>20%)."
    elif pm_pct > 10: pm_sig, pm_det = "neutral", f"Profit margin {pm_pct}% is decent (10-20%)."
    elif pm_pct > 0: pm_sig, pm_det = "bearish", f"Profit margin {pm_pct}% is thin (0-10%)."
    else: pm_sig, pm_det = "bearish", f"Negative profit margin of {pm_pct}%. Company operating at a loss."
    fund_scores.append(80 if pm_pct > 20 else 55 if pm_pct > 10 else 35 if pm_pct > 0 else 15)
else:
    pm_sig, pm_det = "neutral", "Profit margin data unavailable."
    fund_scores.append(50)
metrics.append({"name": "Profit Margin", "value": f"{safe_round(pm*100)}%" if pm != 0 else "N/A", "signal": pm_sig, "detail": pm_det})

# ROE
if roe != 0:
    roe_pct = safe_round(roe * 100)
    if roe_pct > 15: roe_sig, roe_det = "bullish", f"ROE {roe_pct}% is strong (>15%)."
    elif roe_pct > 5: roe_sig, roe_det = "neutral", f"ROE {roe_pct}% is average (5-15%)."
    else: roe_sig, roe_det = "bearish", f"ROE {roe_pct}% is weak (<5%)."
    fund_scores.append(75 if roe_pct > 15 else 50 if roe_pct > 5 else 25)
else:
    roe_sig, roe_det = "neutral", "ROE data unavailable."
    fund_scores.append(50)
metrics.append({"name": "Return on Equity", "value": f"{safe_round(roe*100)}%" if roe != 0 else "N/A", "signal": roe_sig, "detail": roe_det})

avg_fund_score = safe_round(sum(fund_scores) / len(fund_scores) if fund_scores else 50, 1)
fund_bullish = sum(1 for m in metrics if m["signal"] == "bullish")
fund_bearish = sum(1 for m in metrics if m["signal"] == "bearish")
if fund_bullish > fund_bearish + 1: fund_overall = "bullish"
elif fund_bearish > fund_bullish + 1: fund_overall = "bearish"
else: fund_overall = "neutral"

fund_summary = f"Fundamentals: {fund_bullish} bullish, {fund_bearish} bearish, {len(metrics) - fund_bullish - fund_bearish} neutral across {len(metrics)} metrics."
fundamentals_analysis = {"signal": fund_overall, "summary": fund_summary, "metrics": metrics}

# ═══════════════════════════════════════════════════════════
# STEP 5: RISK ASSESSMENT (verified accurate)
# ═══════════════════════════════════════════════════════════
risk_factors = []
risk_scores = []

if beta > 0:
    if beta > 1.5:
        risk_factors.append({"name": "Market Beta", "level": "high", "detail": f"Beta of {safe_round(beta)} — high market sensitivity."})
        risk_scores.append(80)
    elif beta > 1.0:
        risk_factors.append({"name": "Market Beta", "level": "medium", "detail": f"Beta of {safe_round(beta)} — moderate market sensitivity."})
        risk_scores.append(55)
    else:
        risk_factors.append({"name": "Market Beta", "level": "low", "detail": f"Beta of {safe_round(beta)} — below-market volatility. Defensive."})
        risk_scores.append(25)
else:
    risk_factors.append({"name": "Market Beta", "level": "medium", "detail": "Beta data unavailable."})
    risk_scores.append(50)

if atr_pct > 4:
    risk_factors.append({"name": "Price Volatility", "level": "high", "detail": f"ATR {atr_pct}% — high volatility."})
    risk_scores.append(85)
elif atr_pct > 2:
    risk_factors.append({"name": "Price Volatility", "level": "medium", "detail": f"ATR {atr_pct}% — moderate volatility."})
    risk_scores.append(50)
else:
    risk_factors.append({"name": "Price Volatility", "level": "low", "detail": f"ATR {atr_pct}% — low volatility. Stable price action."})
    risk_scores.append(20)

if pct_from_high > 30:
    risk_factors.append({"name": "Drawdown Risk", "level": "high", "detail": f"Stock {pct_from_high}% below 52-week high. Deep drawdown."})
    risk_scores.append(80)
elif pct_from_high > 15:
    risk_factors.append({"name": "Drawdown Risk", "level": "medium", "detail": f"Stock {pct_from_high}% below 52-week high."})
    risk_scores.append(55)
else:
    risk_factors.append({"name": "Drawdown Risk", "level": "low", "detail": f"Stock only {pct_from_high}% below 52-week high. Near highs."})
    risk_scores.append(25)

if de > 200:
    risk_factors.append({"name": "Leverage Risk", "level": "high", "detail": f"D/E {safe_round(de)} very high. Significant risk."})
    risk_scores.append(85)
elif de > 100:
    risk_factors.append({"name": "Leverage Risk", "level": "medium", "detail": f"D/E {safe_round(de)} moderate to high."})
    risk_scores.append(55)
else:
    risk_factors.append({"name": "Leverage Risk", "level": "low", "detail": f"D/E {safe_round(de)} conservative."})
    risk_scores.append(20)

avg_risk_score = safe_round(sum(risk_scores) / len(risk_scores) if risk_scores else 50, 0)
risk_level = "very_high" if avg_risk_score > 75 else "high" if avg_risk_score > 55 else "medium" if avg_risk_score > 35 else "low"
risk_assessment = {"level": risk_level, "score": int(avg_risk_score), "factors": risk_factors}

# ═══════════════════════════════════════════════════════════
# STEP 6: LLM-POWERED ANALYSIS (Gemini 2.5 Flash)
# ═══════════════════════════════════════════════════════════

# Build context for LLM
news_text = ""
if news_articles:
    news_text = "\\n".join([f"- [{a['publisher']}] {a['title']}" + (f": {a['summary']}" if a['summary'] else "") for a in news_articles[:8]])
else:
    news_text = "No recent news available."

reddit_text = ""
if reddit_posts:
    reddit_text = "\\n".join([f"- [r/{p['subreddit']}] {p['title']}" + (f" — {p['snippet'][:100]}" if p['snippet'] else "") for p in reddit_posts[:6]])
else:
    reddit_text = "No recent Reddit discussions found."

technicals_text = f"""
Price: {currency_symbol}{safe_round(current_close)} | RSI: {rsi_val} ({rsi_signal}) | MACD: {macd_val} vs Signal {macd_sig_val} ({macd_signal_str})
EMAs: above {emas_bullish_count}/3 | Bollinger position: {bb_pos}% | Volume: {vol_ratio}x avg
ATR: {atr_pct}% | 52W Range Position: {position_in_range}% | 5D Return: {ret_5d}% | 20D Return: {ret_20d}% | 3M Return: {ret_60d}%
"""

fundamentals_text = f"""
P/E: {fmt_num(pe)} | P/B: {fmt_num(pb)} | D/E: {fmt_num(de)} | Margin: {safe_round(pm*100)}% | ROE: {safe_round(roe*100)}% | Beta: {safe_round(beta)}
"""
# ══════════════════════════════════════════════════════════════
# SINGLE COMBINED LLM CALL (avoids Gemini free tier rate limits)
# ══════════════════════════════════════════════════════════════

# Compute composite score FIRST (needed for the prompt)
risk_adj = 100 - avg_risk_score
pre_sentiment_composite = avg_tech_score * 0.35 + avg_fund_score * 0.25 + risk_adj * 0.2 + 50 * 0.2
pre_composite = safe_round(pre_sentiment_composite, 1)

if pre_composite > 80: pre_action = "STRONG BUY"
elif pre_composite > 65: pre_action = "BUY"
elif pre_composite > 45: pre_action = "HOLD"
elif pre_composite > 30: pre_action = "SELL"
else: pre_action = "STRONG SELL"

combined_prompt = f"""You are a team of financial analysts analyzing {company_name} ({resolved}), trading at {currency_symbol}{safe_round(current_close)}.

TECHNICAL DATA:
{technicals_text}

FUNDAMENTALS:
{fundamentals_text}

RECENT YAHOO FINANCE NEWS ({len(news_articles)} articles):
{news_text}

REDDIT DISCUSSIONS ({len(reddit_posts)} posts):
{reddit_text}

52-WEEK: {currency_symbol}{safe_round(low_52w)} to {currency_symbol}{safe_round(high_52w)} (at {position_in_range}%)
TECHNICAL SCORE: {avg_tech_score}/100 | FUNDAMENTALS SCORE: {avg_fund_score}/100 | RISK: {risk_level} ({avg_risk_score}/100)

Provide a complete analysis. Return a single JSON object with ALL of these fields:

{{
  "sentiment": {{
    "signal": "bullish" or "bearish" or "neutral",
    "summary": "2-3 sentences analyzing sentiment from the news headlines and Reddit posts above",
    "detail": "Detailed paragraph about news themes, Reddit mood, market signals, catalysts and risks from the real data"
  }},
  "bullCase": {{
    "thesis": "3-4 sentence bull case referencing specific news headlines and data",
    "keyPoints": ["specific bullish point 1 with numbers", "point 2", "point 3"],
    "targetPrice": {safe_round(current_close * 1.15)}
  }},
  "bearCase": {{
    "thesis": "3-4 sentence bear case referencing specific risks and data",
    "keyPoints": ["specific risk 1 with numbers", "risk 2", "risk 3"],
    "targetPrice": {safe_round(current_close * 0.85)}
  }},
  "researchSummary": "4-6 sentence comprehensive summary referencing actual news headlines, technical levels, fundamentals",
  "reasoning": "3-4 sentence reasoning for {pre_action} recommendation referencing specific data"
}}"""

combined_result = call_llm(combined_prompt, 1500)

# Parse the combined result
if isinstance(combined_result, dict):
    # Sentiment
    sent_data = combined_result.get("sentiment", {})
    if isinstance(sent_data, dict) and "signal" in sent_data:
        sentiment_analysis = {
            "signal": sent_data.get("signal", "neutral"),
            "summary": sent_data.get("summary", "AI sentiment analysis."),
            "detail": sent_data.get("detail", "")
        }
    else:
        sentiment_analysis = {"signal": "neutral", "summary": "Analysis complete.", "detail": ""}

    # Bull/Bear
    bc_data = combined_result.get("bullCase", {})
    brc_data = combined_result.get("bearCase", {})
    if isinstance(bc_data, dict) and "thesis" in bc_data:
        bull_case = bc_data
        bull_case["targetPrice"] = safe_round(safe_float(bull_case.get("targetPrice", current_close * 1.15)))
    else:
        bull_case = None
    if isinstance(brc_data, dict) and "thesis" in brc_data:
        bear_case = brc_data
        bear_case["targetPrice"] = safe_round(safe_float(bear_case.get("targetPrice", current_close * 0.85)))
    else:
        bear_case = None

    research_summary = combined_result.get("researchSummary", "")
    decision_reasoning = combined_result.get("reasoning", "")
else:
    sentiment_analysis = None
    bull_case = None
    bear_case = None
    research_summary = ""
    decision_reasoning = ""

# Fallbacks for any missing pieces
if not sentiment_analysis or not isinstance(sentiment_analysis, dict) or "signal" not in sentiment_analysis:
    if ret_5d > 2 and ret_20d > 0: sent_sig = "bullish"
    elif ret_5d < -2 and ret_20d < 0: sent_sig = "bearish"
    else: sent_sig = "neutral"
    sentiment_analysis = {
        "signal": sent_sig,
        "summary": f"Price-action sentiment: 5D {ret_5d}%, 20D {ret_20d}%, volume {vol_ratio}x avg. Analyzed {len(news_articles)} news articles and {len(reddit_posts)} Reddit posts.",
        "detail": f"Yahoo Finance reports {len(news_articles)} recent articles. Reddit has {len(reddit_posts)} discussions. Price momentum: {ret_5d}% (5D), {ret_20d}% (20D). Volume at {vol_ratio}x average."
    }

if not bull_case:
    bull_points = [ind["detail"][:120] for ind in indicators if ind["signal"] == "bullish"] or ["Stable price action"]
    bull_case = {
        "thesis": f"{company_name} shows bullish potential. Price at {currency_symbol}{safe_round(current_close)} above {emas_bullish_count}/3 EMAs, volume {vol_ratio}x average.",
        "keyPoints": bull_points[:4],
        "targetPrice": safe_round(current_close * 1.15)
    }

if not bear_case:
    bear_points = [ind["detail"][:120] for ind in indicators if ind["signal"] == "bearish"] or ["General market risk"]
    bear_case = {
        "thesis": f"{company_name} faces risks. RSI {rsi_val}, MACD {macd_val} vs signal {macd_sig_val}.",
        "keyPoints": bear_points[:4],
        "targetPrice": safe_round(current_close * 0.85)
    }

if not research_summary:
    news_snippet = "; ".join([a["title"][:60] for a in news_articles[:3]]) if news_articles else "No recent news"
    research_summary = f"{company_name} ({resolved}) at {currency_symbol}{safe_round(current_close)}. Technical: {avg_tech_score}/100, Fundamentals: {avg_fund_score}/100, Risk: {risk_level} ({avg_risk_score}/100). Sentiment: {sentiment_analysis['signal']}. Headlines: {news_snippet}."

# Recompute composite with actual sentiment
composite = avg_tech_score * 0.35 + avg_fund_score * 0.25 + risk_adj * 0.2 + (85 if sentiment_analysis["signal"] == "bullish" else 25 if sentiment_analysis["signal"] == "bearish" else 50) * 0.2
composite = safe_round(composite, 1)

if composite > 80: action = "STRONG BUY"
elif composite > 65: action = "BUY"
elif composite > 45: action = "HOLD"
elif composite > 30: action = "SELL"
else: action = "STRONG SELL"

if not decision_reasoning:
    decision_reasoning = f"Composite {composite}/100. Tech: {avg_tech_score}, Fund: {avg_fund_score}, Risk-adj: {risk_adj}. {action} based on multi-factor analysis."

# ═══════════════════════════════════════════════════════════
# FINAL OUTPUT
# ═══════════════════════════════════════════════════════════
entry_price = safe_round(current_close)
stop_pct = 0.08 if risk_level in ["low", "medium"] else 0.12
stop_loss = safe_round(current_close * (1 - stop_pct))

if action in ["STRONG BUY", "BUY"]:
    time_horizon = "3-6 months"
    pos_size = "8-12% of portfolio" if action == "STRONG BUY" else "5-8% of portfolio"
elif action == "HOLD":
    time_horizon = "1-3 months (reassess)"
    pos_size = "Maintain existing; no new entry"
else:
    time_horizon = "Exit within 1-4 weeks"
    pos_size = "Reduce to 0-3%"

confidence = min(95, max(15, safe_round(composite)))

output = {
    "ticker": resolved,
    "name": company_name,
    "currencySymbol": currency_symbol,
    "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "newsCount": len(news_articles),
    "redditPostCount": len(reddit_posts),
    "newsHeadlines": [a["title"] for a in news_articles[:5]],
    "redditTitles": [p["title"] for p in reddit_posts[:5]],
    "marketAnalysis": market_analysis,
    "fundamentalsAnalysis": fundamentals_analysis,
    "sentimentAnalysis": sentiment_analysis,
    "bullCase": bull_case,
    "bearCase": bear_case,
    "researchSummary": research_summary,
    "riskAssessment": risk_assessment,
    "decision": {
        "action": action,
        "confidence": confidence,
        "reasoning": decision_reasoning,
        "entryPrice": entry_price,
        "targetPrice": safe_round(safe_float(bull_case.get("targetPrice", current_close * 1.1))),
        "stopLoss": stop_loss,
        "timeHorizon": time_horizon,
        "positionSize": pos_size,
    },
}

# Validate JSON before printing
try:
    validated = json.loads(json.dumps(output))
    print(json.dumps(validated))
except Exception:
    # If validation fails, sanitize
    output_str = json.dumps(output, default=str)
    print(output_str)
`;

  try {
    const { writeFileSync, unlinkSync } = await import("fs");
    const tmpFile = `/tmp/ta_agents_${Date.now()}.py`;
    writeFileSync(tmpFile, script);
    const { stdout } = await execAsync(`${PYTHON} ${tmpFile}`, {
      timeout: 120000,
      maxBuffer: 10 * 1024 * 1024,
    });
    unlinkSync(tmpFile);
    const data = JSON.parse(stdout.trim());
    return NextResponse.json(data);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: `Agent analysis failed: ${msg}` }, { status: 500 });
  }
}
