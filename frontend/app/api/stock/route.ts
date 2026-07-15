import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

// Use the Python that has yfinance installed
const PYTHON = "/Users/omshukla/tradingagents/venv/bin/python3";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const ticker = searchParams.get("ticker") || "AAPL";
  const period = searchParams.get("period") || "6mo";

  const script = `
import yfinance as yf
import json
import sys

raw_input = "${ticker}"
period = "${period}"
# 1d needs minute-level interval, 5d needs hourly
interval = "1m" if period == "1d" else "1h" if period == "5d" else "1d"

# ── Symbol resolution ──
# If the user typed a company name or an ambiguous ticker, resolve it.
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

    # Try with .NS suffix (NSE India) — common for Indian stocks
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

    # Nothing worked — return the original uppercased input
    return s.upper()

resolved = resolve_ticker(raw_input)

ticker = yf.Ticker(resolved)
hist = ticker.history(period=period, interval=interval)
info = ticker.info

if len(hist) == 0:
    print(json.dumps({"error": f"No data found for '{raw_input}'. Try a valid ticker like ADANIPOWER.NS, RELIANCE.NS, or AAPL."}))
    sys.exit()

import math

def safe_float(val, default=0):
    """Convert a value to float, returning default for None/NaN/Inf."""
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
    """Round a value safely, returning default for None/NaN/Inf."""
    return round(safe_float(val, default), digits)

price_data = []
for date, row in hist.iterrows():
    price_data.append({
        "date": date.strftime("%Y-%m-%d %H:%M") if interval in ("1m", "1h") else date.strftime("%Y-%m-%d"),
        "open": safe_round(row["Open"]),
        "high": safe_round(row["High"]),
        "low": safe_round(row["Low"]),
        "close": safe_round(row["Close"]),
        "volume": int(safe_float(row["Volume"])),
    })

# Detect currency symbol from yfinance info
raw_currency = info.get("currency", "USD")
currency_symbols = {
    "INR": "₹", "USD": "$", "EUR": "€", "GBP": "£",
    "JPY": "¥", "HKD": "HK$", "CNY": "¥", "AUD": "A$",
    "CAD": "C$", "SGD": "S$",
}
currency_symbol = currency_symbols.get(raw_currency, raw_currency + " ")

# Current price — try multiple fields
last_close = price_data[-1]["close"] if price_data else 0
current_price = safe_float(info.get("currentPrice")) or safe_float(info.get("regularMarketPrice")) or safe_float(info.get("previousClose")) or last_close

result = {
    "ticker": resolved,
    "name": info.get("longName") or info.get("shortName") or resolved,
    "currency": raw_currency,
    "currencySymbol": currency_symbol,
    "price": safe_round(current_price),
    "change": safe_round(info.get("regularMarketChange")),
    "changePercent": safe_round(info.get("regularMarketChangePercent")),
    "marketCap": info.get("marketCap") if safe_float(info.get("marketCap")) != 0 else None,
    "volume": int(safe_float(info.get("regularMarketVolume"))) or int(safe_float(info.get("averageVolume"))) or None,
    "high52": safe_float(info.get("fiftyTwoWeekHigh")),
    "low52": safe_float(info.get("fiftyTwoWeekLow")),
    "pe": safe_float(info.get("trailingPE")),
    "eps": safe_float(info.get("trailingEps")),
    "dividend": safe_float(info.get("dividendYield")),
    "beta": safe_float(info.get("beta")),
    "sector": info.get("sector") or None,
    "industry": info.get("industry") or None,
    # Extra fundamental fields
    "previousClose":     safe_float(info.get("previousClose")),
    "open":              safe_float(info.get("open")),
    "dayHigh":           safe_float(info.get("dayHigh")),
    "dayLow":            safe_float(info.get("dayLow")),
    "bookValue":         safe_float(info.get("bookValue")),
    "priceToBook":       safe_float(info.get("priceToBook")),
    "returnOnEquity":    safe_float(info.get("returnOnEquity")),
    "debtToEquity":      safe_float(info.get("debtToEquity")),
    "grossMargins":      safe_float(info.get("grossMargins")),
    "operatingMargins":  safe_float(info.get("operatingMargins")),
    "profitMargins":     safe_float(info.get("profitMargins")),
    "totalRevenue":      info.get("totalRevenue") if safe_float(info.get("totalRevenue")) != 0 else None,
    "totalDebt":         info.get("totalDebt") if safe_float(info.get("totalDebt")) != 0 else None,
    "totalCash":         info.get("totalCash") if safe_float(info.get("totalCash")) != 0 else None,
    "employees":         info.get("fullTimeEmployees") or None,
    "revenuePerShare":   safe_float(info.get("revenuePerShare")),
    "priceData": price_data,
}
print(json.dumps(result))
`;

  try {
    // Write script to temp file to avoid shell quoting issues
    const { writeFileSync, unlinkSync } = await import("fs");
    const tmpFile = `/tmp/ta_stock_${Date.now()}.py`;
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
