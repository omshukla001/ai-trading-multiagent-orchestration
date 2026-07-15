"use client";
import { IndicatorData } from "@/app/page";

const TREND_COLORS: Record<string, string> = {
  "Strong Bullish": "text-emerald-400 bg-emerald-900/30 border-emerald-700/50",
  "Bullish":        "text-green-400   bg-green-900/30   border-green-700/50",
  "Neutral":        "text-yellow-400  bg-yellow-900/30  border-yellow-700/50",
  "Bearish":        "text-orange-400  bg-orange-900/30  border-orange-700/50",
  "Strong Bearish": "text-red-400     bg-red-900/30     border-red-700/50",
};

const TREND_EMOJI: Record<string, string> = {
  "Strong Bullish": "🚀",
  "Bullish":        "📈",
  "Neutral":        "➡️",
  "Bearish":        "📉",
  "Strong Bearish": "⚠️",
};

function rsiLabel(v: number) {
  if (v >= 70) return { label: "Overbought", color: "text-red-400" };
  if (v <= 30) return { label: "Oversold",   color: "text-green-400" };
  return { label: "Neutral", color: "text-yellow-400" };
}

export default function SignalCard({ signals }: { signals: IndicatorData["signals"] }) {
  const rsi = rsiLabel(signals.rsi);
  const trendColor = TREND_COLORS[signals.trend] ?? TREND_COLORS["Neutral"];

  const checks = [
    { label: "Above EMA20",  ok: signals.aboveEma20 },
    { label: "Above EMA50",  ok: signals.aboveEma50 },
    { label: "Above EMA200", ok: signals.aboveEma200 },
    { label: "MACD Bullish", ok: signals.macdBullish },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {/* Trend */}
      <div className={`border rounded-xl p-4 ${trendColor}`}>
        <p className="text-xs opacity-70 mb-1">Overall Trend</p>
        <p className="text-lg font-bold">
          {TREND_EMOJI[signals.trend]} {signals.trend}
        </p>
      </div>

      {/* RSI */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <p className="text-xs text-gray-500 mb-1">RSI (14)</p>
        <p className={`text-2xl font-bold ${rsi.color}`}>{signals.rsi}</p>
        <p className={`text-xs mt-0.5 ${rsi.color}`}>{rsi.label}</p>
        <div className="mt-2 h-1.5 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-green-500 via-yellow-400 to-red-500"
            style={{ width: `${Math.min(signals.rsi, 100)}%` }}
          />
        </div>
      </div>

      {/* MACD */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <p className="text-xs text-gray-500 mb-1">MACD Signal</p>
        <p className={`text-lg font-bold ${signals.macdBullish ? "text-green-400" : "text-red-400"}`}>
          {signals.macdBullish ? "📈 Bullish" : "📉 Bearish"}
        </p>
        <p className="text-xs text-gray-500 mt-0.5">Value: {signals.macd?.toFixed(4)}</p>
      </div>

      {/* EMA Checklist */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <p className="text-xs text-gray-500 mb-2">EMA Checks</p>
        <div className="space-y-1">
          {checks.map((c) => (
            <div key={c.label} className="flex items-center gap-2 text-xs">
              <span className={c.ok ? "text-green-400" : "text-red-400"}>
                {c.ok ? "✓" : "✗"}
              </span>
              <span className={c.ok ? "text-gray-300" : "text-gray-500"}>{c.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
