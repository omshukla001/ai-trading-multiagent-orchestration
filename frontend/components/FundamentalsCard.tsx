"use client";
import { useState } from "react";
import { StockData } from "@/app/page";

function Row({ label, value, note, highlight }: {
  label: string; value: string; note?: string; highlight?: "green" | "red" | "yellow"
}) {
  const colors = { green: "text-green-400", red: "text-red-400", yellow: "text-yellow-400" };
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
      <span className="text-xs text-gray-400">{label}</span>
      <div className="text-right">
        <span className={`text-sm font-semibold ${highlight ? colors[highlight] : "text-white"}`}>
          {value}
        </span>
        {note && <p className="text-xs text-gray-500 mt-0.5">{note}</p>}
      </div>
    </div>
  );
}

function fmtNum(n: number | null, sym = "") {
  if (!n) return "N/A";
  if (n >= 1e12) return `${sym}${(n / 1e12).toFixed(2)}T`;
  if (n >= 1e9)  return `${sym}${(n / 1e9).toFixed(2)}B`;
  if (n >= 1e6)  return `${sym}${(n / 1e6).toFixed(2)}M`;
  if (n >= 1e3)  return `${sym}${(n / 1e3).toFixed(1)}K`;
  return `${sym}${n.toLocaleString()}`;
}

function pct(n: number) {
  return n ? `${(n * 100).toFixed(2)}%` : "N/A";
}

const TABS = ["Overview", "Price", "Financials", "Company"];

export default function FundamentalsCard({ stock }: { stock: StockData }) {
  const [tab, setTab] = useState("Overview");
  const sym = stock.currencySymbol ?? "$";

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <h3 className="text-sm font-semibold text-white mb-3">📊 Fundamentals</h3>

      {/* Tab bar */}
      <div className="flex gap-1 mb-4 bg-gray-800 p-1 rounded-lg">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 text-xs py-1.5 rounded-md font-medium transition-colors ${
              tab === t ? "bg-gray-700 text-white" : "text-gray-400 hover:text-gray-300"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Overview */}
      {tab === "Overview" && <>
        <Row label="Company"    value={stock.name} />
        <Row label="Sector"     value={stock.sector   ?? "N/A"} />
        <Row label="Industry"   value={stock.industry ?? "N/A"} />
        <Row label="Currency"   value={`${stock.currency} (${sym})`} />
        <Row label="Market Cap" value={fmtNum(stock.marketCap, sym)} />
        <Row label="Employees"  value={stock.employees ? stock.employees.toLocaleString() : "N/A"} />
        <Row
          label="P/E Ratio"
          value={stock.pe ? stock.pe.toFixed(2) : "N/A"}
          note={stock.pe ? (stock.pe < 15 ? "Undervalued" : stock.pe > 35 ? "Expensive" : "Fair value") : undefined}
          highlight={stock.pe ? (stock.pe < 15 ? "green" : stock.pe > 35 ? "red" : undefined) : undefined}
        />
        <Row label="EPS"       value={stock.eps ? `${sym}${stock.eps.toFixed(2)}` : "N/A"} />
        <Row label="Div Yield" value={stock.dividend ? `${(stock.dividend * 100).toFixed(2)}%` : "N/A"} />
        <Row
          label="Beta"
          value={stock.beta ? stock.beta.toFixed(3) : "N/A"}
          note={stock.beta ? (stock.beta > 1.5 ? "High volatility" : stock.beta < 0.5 ? "Low volatility" : "Avg volatility") : undefined}
        />
      </>}

      {/* Price tab */}
      {tab === "Price" && <>
        <Row label="Current Price"  value={`${sym}${stock.price?.toFixed(2)}`} />
        <Row label="Previous Close" value={stock.previousClose ? `${sym}${stock.previousClose.toFixed(2)}` : "N/A"} />
        <Row label="Open"           value={stock.open    ? `${sym}${stock.open.toFixed(2)}`    : "N/A"} />
        <Row label="Day High"       value={stock.dayHigh ? `${sym}${stock.dayHigh.toFixed(2)}` : "N/A"} highlight="green" />
        <Row label="Day Low"        value={stock.dayLow  ? `${sym}${stock.dayLow.toFixed(2)}`  : "N/A"} highlight="red" />
        <Row label="52W High"       value={stock.high52  ? `${sym}${stock.high52.toFixed(2)}`  : "N/A"} />
        <Row label="52W Low"        value={stock.low52   ? `${sym}${stock.low52.toFixed(2)}`   : "N/A"} />
        <Row label="Book Value"     value={stock.bookValue   ? `${sym}${stock.bookValue.toFixed(2)}`  : "N/A"} />
        <Row label="Price/Book"     value={stock.priceToBook ? stock.priceToBook.toFixed(2) : "N/A"}
          note={stock.priceToBook ? (stock.priceToBook < 1 ? "Below book — cheap" : stock.priceToBook > 5 ? "Premium to book" : undefined) : undefined}
        />

        {/* 52-week range bar */}
        {stock.high52 && stock.low52 && stock.price && (
          <div className="mt-4">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>{sym}{stock.low52.toFixed(0)}</span>
              <span className="text-white font-medium">{sym}{stock.price.toFixed(2)}</span>
              <span>{sym}{stock.high52.toFixed(0)}</span>
            </div>
            <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-red-500 via-yellow-400 to-green-500 rounded-full transition-all"
                style={{
                  width: `${Math.min(100, Math.max(2,
                    ((stock.price - stock.low52) / (stock.high52 - stock.low52)) * 100
                  ))}%`,
                }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1 text-center">52-Week Price Range</p>
          </div>
        )}
      </>}

      {/* Financials tab */}
      {tab === "Financials" && <>
        <Row label="Total Revenue"     value={fmtNum(stock.totalRevenue, sym)} />
        <Row label="Revenue / Share"   value={stock.revenuePerShare ? `${sym}${stock.revenuePerShare.toFixed(2)}` : "N/A"} />
        <Row label="Total Debt"        value={fmtNum(stock.totalDebt, sym)} />
        <Row label="Total Cash"        value={fmtNum(stock.totalCash, sym)} />
        <Row label="Debt/Equity"
          value={stock.debtToEquity ? stock.debtToEquity.toFixed(2) : "N/A"}
          note={stock.debtToEquity ? (stock.debtToEquity > 100 ? "High leverage" : stock.debtToEquity < 30 ? "Low debt" : "Moderate debt") : undefined}
          highlight={stock.debtToEquity ? (stock.debtToEquity > 100 ? "red" : stock.debtToEquity < 30 ? "green" : undefined) : undefined}
        />
        <Row label="Return on Equity"  value={pct(stock.returnOnEquity)}
          highlight={stock.returnOnEquity > 0.15 ? "green" : stock.returnOnEquity < 0 ? "red" : undefined}
        />
        <Row label="Gross Margin"      value={pct(stock.grossMargins)}
          highlight={stock.grossMargins > 0.4 ? "green" : stock.grossMargins < 0.1 ? "red" : undefined}
        />
        <Row label="Operating Margin"  value={pct(stock.operatingMargins)}
          highlight={stock.operatingMargins > 0.2 ? "green" : stock.operatingMargins < 0 ? "red" : undefined}
        />
        <Row label="Profit Margin"     value={pct(stock.profitMargins)}
          highlight={stock.profitMargins > 0.15 ? "green" : stock.profitMargins < 0 ? "red" : undefined}
        />
      </>}

      {/* Company tab */}
      {tab === "Company" && <>
        <Row label="Full Name"   value={stock.name} />
        <Row label="Ticker"      value={stock.ticker} />
        <Row label="Sector"      value={stock.sector   ?? "N/A"} />
        <Row label="Industry"    value={stock.industry ?? "N/A"} />
        <Row label="Employees"   value={stock.employees ? stock.employees.toLocaleString() + " people" : "N/A"} />
        <Row label="Currency"    value={`${stock.currency} (${sym})`} />
        <Row label="Market Cap"  value={fmtNum(stock.marketCap, sym)} />
        <Row label="Volume"      value={fmtNum(stock.volume)} />
        {/* Index note */}
        {!stock.sector && (
          <p className="text-xs text-gray-600 mt-3 text-center">
            📌 Index — sector/financials not available for indices
          </p>
        )}
      </>}
    </div>
  );
}
