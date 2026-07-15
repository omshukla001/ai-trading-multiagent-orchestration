import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const ticker = searchParams.get("ticker") || "AAPL";

  const script = `
import yfinance as yf
import json
import pandas as pd
import numpy as np

ticker = yf.Ticker("${ticker}")
hist = ticker.history(period="1y")

if len(hist) < 50:
    print(json.dumps({"error": "Not enough data"}))
    exit()

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
macd = (ema12 - ema26).round(2)
signal = macd.ewm(span=9).mean().round(2)
histogram = (macd - signal).round(2)

# Bollinger Bands (20)
sma20 = close.rolling(20).mean()
std20 = close.rolling(20).std()
bb_upper = (sma20 + 2 * std20).round(2)
bb_lower = (sma20 - 2 * std20).round(2)
bb_mid = sma20.round(2)

# EMAs
ema20 = close.ewm(span=20).mean().round(2)
ema50 = close.ewm(span=50).mean().round(2)
ema200 = close.ewm(span=200).mean().round(2)

# Volume SMA
vol_sma20 = volume.rolling(20).mean().round(0)

# Build output (last 120 days)
results = []
dates = hist.index[-120:]
for date in dates:
    d = date.strftime("%Y-%m-%d")
    results.append({
        "date": d,
        "rsi": float(rsi.get(date, np.nan)) if not pd.isna(rsi.get(date, np.nan)) else None,
        "macd": float(macd.get(date, np.nan)) if not pd.isna(macd.get(date, np.nan)) else None,
        "macd_signal": float(signal.get(date, np.nan)) if not pd.isna(signal.get(date, np.nan)) else None,
        "macd_hist": float(histogram.get(date, np.nan)) if not pd.isna(histogram.get(date, np.nan)) else None,
        "bb_upper": float(bb_upper.get(date, np.nan)) if not pd.isna(bb_upper.get(date, np.nan)) else None,
        "bb_mid": float(bb_mid.get(date, np.nan)) if not pd.isna(bb_mid.get(date, np.nan)) else None,
        "bb_lower": float(bb_lower.get(date, np.nan)) if not pd.isna(bb_lower.get(date, np.nan)) else None,
        "ema20": float(ema20.get(date, np.nan)) if not pd.isna(ema20.get(date, np.nan)) else None,
        "ema50": float(ema50.get(date, np.nan)) if not pd.isna(ema50.get(date, np.nan)) else None,
        "ema200": float(ema200.get(date, np.nan)) if not pd.isna(ema200.get(date, np.nan)) else None,
        "vol_sma20": float(vol_sma20.get(date, np.nan)) if not pd.isna(vol_sma20.get(date, np.nan)) else None,
        "close": float(close.get(date, np.nan)) if not pd.isna(close.get(date, np.nan)) else None,
        "volume": float(volume.get(date, np.nan)) if not pd.isna(volume.get(date, np.nan)) else None,
    })

# Current signals
latest_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50
latest_macd = float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else 0
latest_signal = float(signal.iloc[-1]) if not pd.isna(signal.iloc[-1]) else 0
latest_close = float(close.iloc[-1])
latest_ema20 = float(ema20.iloc[-1])
latest_ema50 = float(ema50.iloc[-1])
latest_ema200 = float(ema200.iloc[-1])

# Trend signal
if latest_ema20 > latest_ema50 > latest_ema200 and latest_rsi > 60:
    trend = "Strong Bullish"
elif latest_ema20 > latest_ema50 and latest_rsi > 50:
    trend = "Bullish"
elif latest_ema20 < latest_ema50 < latest_ema200 and latest_rsi < 40:
    trend = "Strong Bearish"
elif latest_ema20 < latest_ema50 and latest_rsi < 50:
    trend = "Bearish"
else:
    trend = "Neutral"

print(json.dumps({
    "indicators": results,
    "signals": {
        "rsi": round(latest_rsi, 2),
        "macd": round(latest_macd, 4),
        "trend": trend,
        "aboveEma20": latest_close > latest_ema20,
        "aboveEma50": latest_close > latest_ema50,
        "aboveEma200": latest_close > latest_ema200,
        "macdBullish": latest_macd > latest_signal,
    }
}))
`;

  try {
    const pythonCmd = `cd /Users/omshukla/ai-trading-multiagent-orchestration && source venv/bin/activate 2>/dev/null; python3 -c '${script.replace(/'/g, "'\\''")}'`;
    const { stdout } = await execAsync(pythonCmd, { timeout: 30000 });
    const data = JSON.parse(stdout.trim());
    return NextResponse.json(data);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
