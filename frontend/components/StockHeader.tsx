"use client";
import { StockData } from "@/app/page";
import { TrendingUp, TrendingDown } from "lucide-react";

const PERIODS = [
  { label: "1M", value: "1mo" },
  { label: "3M", value: "3mo" },
  { label: "6M", value: "6mo" },
  { label: "1Y", value: "1y" },
  { label: "2Y", value: "2y" },
];

function fmt(n: number) {
  if (!n) return "N/A";
  if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
  if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
  if (n >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
  return `$${n.toLocaleString()}`;
}

function fmtVol(n: number) {
  if (!n) return "N/A";
  if (n >= 1e9) return `${(n / 1e9).toFixed(2)}B`;
  if (n >= 1e6) return `${(n / 1e6).toFixed(2)}M`;
  if (n >= 1e3) return `${(n / 1e3).toFixed(0)}K`;
  return n.toString();
}

export default function StockHeader({
  stock,
  period,
  onPeriodChange,
}: {
  stock: StockData;
  period: string;
  onPeriodChange: (p: string) => void;
}) {
  const up = stock.change >= 0;

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        {/* Left: name + price */}
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono bg-blue-600/20 text-blue-400 border border-blue-700/40 px-2 py-0.5 rounded">
              {stock.ticker}
            </span>
            <span className="text-xs text-gray-500">{stock.sector}</span>
          </div>
          <h2 className="text-xl font-bold text-white">{stock.name}</h2>
          <div className="flex items-center gap-3 mt-1">
            <span className="text-3xl font-bold">${stock.price?.toFixed(2)}</span>
            <div className={`flex items-center gap-1 text-sm font-medium ${up ? "text-green-400" : "text-red-400"}`}>
              {up ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              {up ? "+" : ""}{stock.change?.toFixed(2)} ({up ? "+" : ""}{stock.changePercent?.toFixed(2)}%)
            </div>
          </div>
        </div>

        {/* Right: period selector */}
        <div className="flex gap-1">
          {PERIODS.map((p) => (
            <button
              key={p.value}
              onClick={() => onPeriodChange(p.value)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                period === p.value
                  ? "bg-blue-600 text-white"
                  : "bg-gray-800 text-gray-400 hover:bg-gray-700"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 mt-4 pt-4 border-t border-gray-800">
        {[
          { label: "Market Cap", value: fmt(stock.marketCap) },
          { label: "Volume", value: fmtVol(stock.volume) },
          { label: "52W High", value: `$${stock.high52?.toFixed(2)}` },
          { label: "52W Low", value: `$${stock.low52?.toFixed(2)}` },
          { label: "P/E Ratio", value: stock.pe ? stock.pe.toFixed(2) : "N/A" },
          { label: "Beta", value: stock.beta ? stock.beta.toFixed(2) : "N/A" },
        ].map((s) => (
          <div key={s.label}>
            <p className="text-xs text-gray-500 mb-0.5">{s.label}</p>
            <p className="text-sm font-semibold text-white">{s.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
