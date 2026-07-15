"use client";
import { StockData } from "@/app/page";

function Row({ label, value, note }: { label: string; value: string; note?: string }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
      <span className="text-sm text-gray-400">{label}</span>
      <div className="text-right">
        <span className="text-sm font-semibold text-white">{value}</span>
        {note && <p className="text-xs text-gray-500">{note}</p>}
      </div>
    </div>
  );
}

function fmtCap(n: number) {
  if (!n) return "N/A";
  if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
  if (n >= 1e9)  return `$${(n / 1e9).toFixed(2)}B`;
  if (n >= 1e6)  return `$${(n / 1e6).toFixed(2)}M`;
  return `$${n.toLocaleString()}`;
}

export default function FundamentalsCard({ stock }: { stock: StockData }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <h3 className="text-sm font-semibold text-white mb-4">📊 Fundamentals</h3>

      <Row label="Company"      value={stock.name} />
      <Row label="Sector"       value={stock.sector   || "N/A"} />
      <Row label="Industry"     value={stock.industry || "N/A"} />
      <Row label="Market Cap"   value={fmtCap(stock.marketCap)} />
      <Row label="P/E Ratio"    value={stock.pe ? stock.pe.toFixed(2) : "N/A"}
                                note={stock.pe ? (stock.pe < 15 ? "Undervalued" : stock.pe > 30 ? "Premium" : "Fair") : undefined} />
      <Row label="EPS"          value={stock.eps ? `$${stock.eps.toFixed(2)}` : "N/A"} />
      <Row label="Dividend Yield" value={stock.dividend ? `${(stock.dividend * 100).toFixed(2)}%` : "N/A"} />
      <Row label="Beta"         value={stock.beta ? stock.beta.toFixed(2) : "N/A"}
                                note={stock.beta ? (stock.beta > 1.5 ? "High volatility" : stock.beta < 0.5 ? "Low volatility" : "Market correlated") : undefined} />
      <Row label="52W High"     value={stock.high52 ? `$${stock.high52.toFixed(2)}` : "N/A"} />
      <Row label="52W Low"      value={stock.low52  ? `$${stock.low52.toFixed(2)}`  : "N/A"} />

      {/* 52-week range bar */}
      {stock.high52 && stock.low52 && stock.price && (
        <div className="mt-4">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>${stock.low52.toFixed(0)}</span>
            <span className="text-white font-medium">${stock.price.toFixed(2)}</span>
            <span>${stock.high52.toFixed(0)}</span>
          </div>
          <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-red-500 via-yellow-400 to-green-500 rounded-full"
              style={{
                width: `${Math.min(100, Math.max(0, ((stock.price - stock.low52) / (stock.high52 - stock.low52)) * 100))}%`,
              }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-1 text-center">52-Week Price Position</p>
        </div>
      )}
    </div>
  );
}
