import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const ticker = searchParams.get("ticker") || "AAPL";
  const period = searchParams.get("period") || "6mo";

  const script = `
import yfinance as yf
import json
from datetime import datetime

ticker = yf.Ticker("${ticker}")
hist = ticker.history(period="${period}")
info = ticker.info

price_data = []
for date, row in hist.iterrows():
    price_data.append({
        "date": date.strftime("%Y-%m-%d"),
        "open": round(float(row["Open"]), 2),
        "high": round(float(row["High"]), 2),
        "low": round(float(row["Low"]), 2),
        "close": round(float(row["Close"]), 2),
        "volume": int(row["Volume"]),
    })

result = {
    "ticker": "${ticker}",
    "name": info.get("longName", "${ticker}"),
    "price": round(info.get("currentPrice") or info.get("regularMarketPrice") or (price_data[-1]["close"] if price_data else 0), 2),
    "change": round(info.get("regularMarketChange", 0), 2),
    "changePercent": round(info.get("regularMarketChangePercent", 0), 2),
    "marketCap": info.get("marketCap", 0),
    "volume": info.get("regularMarketVolume", 0),
    "high52": info.get("fiftyTwoWeekHigh", 0),
    "low52": info.get("fiftyTwoWeekLow", 0),
    "pe": info.get("trailingPE", 0),
    "eps": info.get("trailingEps", 0),
    "dividend": info.get("dividendYield", 0),
    "beta": info.get("beta", 0),
    "sector": info.get("sector", "N/A"),
    "industry": info.get("industry", "N/A"),
    "priceData": price_data,
}
print(json.dumps(result))
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
