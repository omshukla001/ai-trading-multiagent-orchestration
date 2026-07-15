import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

const PYTHON = "/Users/omshukla/tradingagents/venv/bin/python3";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const ticker = searchParams.get("ticker") || "AAPL";

  const script = `
import yfinance as yf
import json
import pandas as pd
import numpy as np
import sys

raw_input = "${ticker}"

# ── Symbol resolution ──
def resolve_ticker(raw):
    """Resolve a raw user input to a valid Yahoo Finance ticker symbol."""
    s = raw.strip()

    # Already looks like a valid Yahoo ticker (has exchange suffix, special chars, etc.)
    if any(c in s for c in [".", "-", "^", "="]):
        t = yf.Ticker(s)
        hist = t.history(period="5d")
        if len(hist) >= 1:
            return s

    # Try the raw input as-is (e.g., "AAPL", "NVDA")
    s_upper = s.upper().replace(" ", "")
    t = yf.Ticker(s_upper)
    hist = t.history(period="5d")
    if len(hist) >= 1:
        return s_upper

    # Try with .NS suffix (NSE India)
    ns_sym = s_upper + ".NS"
    t = yf.Ticker(ns_sym)
    hist = t.history(period="5d")
    if len(hist) >= 1:
        return ns_sym

    # Try with .BO suffix (BSE India)
    bo_sym = s_upper + ".BO"
    t = yf.Ticker(bo_sym)
    hist = t.history(period="5d")
    if len(hist) >= 1:
        return bo_sym

    # Use yfinance search as last resort
    try:
        import urllib.request, urllib.parse
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

resolved = resolve_ticker(raw_input)

ticker = yf.Ticker(resolved)
hist = ticker.history(period="1y")

if len(hist) < 20:
    print(json.dumps({"error": f"Not enough data for '{raw_input}' (resolved to '{resolved}'). Try a valid ticker like ADANIPOWER.NS, RELIANCE.NS, or AAPL."}))
    sys.exit()

close = hist["Close"]
volume = hist["Volume"]

# RSI (14)
delta = close.diff()
gain = delta.clip(lower=0).rolling(14).mean()
loss = -delta.clip(upper=0).rolling(14).mean()
rs = gain / loss
rsi = (100 - 100 / (1 + rs)).round(2)

# MACD
ema12 = close.ewm(span=12).mean()
ema26 = close.ewm(span=26).mean()
macd = (ema12 - ema26).round(4)
signal = macd.ewm(span=9).mean().round(4)
histogram = (macd - signal).round(4)

# Bollinger Bands (20)
sma20 = close.rolling(20).mean()
std20 = close.rolling(20).std()
bb_upper = (sma20 + 2 * std20).round(2)
bb_lower = (sma20 - 2 * std20).round(2)
bb_mid = sma20.round(2)

# EMAs
ema20  = close.ewm(span=20).mean().round(2)
ema50  = close.ewm(span=50).mean().round(2)
ema200 = close.ewm(span=200).mean().round(2)

# Volume SMA
vol_sma20 = volume.rolling(20).mean().round(0)

def safe(val):
    try:
        v = float(val)
        return None if (v != v) else round(v, 4)  # NaN check
    except:
        return None

results = []
for date in hist.index[-120:]:
    d = date.strftime("%Y-%m-%d")
    results.append({
        "date":       d,
        "rsi":        safe(rsi.get(date)),
        "macd":       safe(macd.get(date)),
        "macd_signal":safe(signal.get(date)),
        "macd_hist":  safe(histogram.get(date)),
        "bb_upper":   safe(bb_upper.get(date)),
        "bb_mid":     safe(bb_mid.get(date)),
        "bb_lower":   safe(bb_lower.get(date)),
        "ema20":      safe(ema20.get(date)),
        "ema50":      safe(ema50.get(date)),
        "ema200":     safe(ema200.get(date)),
        "vol_sma20":  safe(vol_sma20.get(date)),
        "close":      safe(close.get(date)),
        "volume":     safe(volume.get(date)),
    })

latest_rsi    = safe(rsi.iloc[-1])    or 50
latest_macd   = safe(macd.iloc[-1])   or 0
latest_signal = safe(signal.iloc[-1]) or 0
latest_close  = safe(close.iloc[-1])  or 0
latest_ema20  = safe(ema20.iloc[-1])  or 0
latest_ema50  = safe(ema50.iloc[-1])  or 0
latest_ema200 = safe(ema200.iloc[-1]) or 0

if latest_ema20 > latest_ema50 > latest_ema200 and latest_rsi > 60:
    trend = "Strong Bullish"
elif latest_ema20 > latest_ema50 > latest_ema200 and latest_rsi > 45:
    trend = "Bullish"
elif latest_ema20 > latest_ema50 and latest_rsi > 55:
    trend = "Bullish"
elif latest_ema20 < latest_ema50 < latest_ema200 and latest_rsi < 40:
    trend = "Strong Bearish"
elif latest_ema20 < latest_ema50 < latest_ema200 and latest_rsi < 55:
    trend = "Bearish"
elif latest_ema20 < latest_ema50 and latest_rsi < 45:
    trend = "Bearish"
else:
    trend = "Neutral"

print(json.dumps({
    "indicators": results,
    "signals": {
        "rsi":          round(latest_rsi, 2),
        "macd":         round(latest_macd, 4),
        "trend":        trend,
        "aboveEma20":   latest_close > latest_ema20,
        "aboveEma50":   latest_close > latest_ema50,
        "aboveEma200":  latest_close > latest_ema200,
        "macdBullish":  latest_macd > latest_signal,
    }
}))
`;

  try {
    const { writeFileSync, unlinkSync } = await import("fs");
    const tmpFile = `/tmp/ta_indicators_${Date.now()}.py`;
    writeFileSync(tmpFile, script);
    const { stdout } = await execAsync(`${PYTHON} ${tmpFile}`, { timeout: 60000 });
    unlinkSync(tmpFile);
    const data = JSON.parse(stdout.trim());
    return NextResponse.json(data);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: `Python error: ${msg}` }, { status: 500 });
  }
}
