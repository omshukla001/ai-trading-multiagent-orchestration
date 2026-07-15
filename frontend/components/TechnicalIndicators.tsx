"use client";
import {
  ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, ResponsiveContainer, Cell
} from "recharts";
import { IndicatorData } from "@/app/page";

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: { name: string; value: number; color: string }[]; label?: string }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-gray-900 border border-gray-700 rounded-lg p-3 text-xs shadow-xl">
      <p className="text-gray-400 mb-1">{label}</p>
      {payload.map((p) => (
        <div key={p.name} className="flex justify-between gap-4">
          <span style={{ color: p.color }}>{p.name}</span>
          <span className="text-white font-mono">{p.value?.toFixed(4)}</span>
        </div>
      ))}
    </div>
  );
};

export default function TechnicalIndicators({ data }: { data: IndicatorData }) {
  const recent = data.indicators.slice(-90);

  const tickCount = 6;
  const step = Math.ceil(recent.length / tickCount);
  const ticks = recent.filter((_, i) => i % step === 0).map((d) => d.date);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* RSI */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white">RSI (14)</h3>
            <p className="text-xs text-gray-500 mt-0.5">Relative Strength Index</p>
          </div>
          <div className={`text-sm font-bold px-2 py-1 rounded ${
            data.signals.rsi >= 70 ? "bg-red-900/40 text-red-400" :
            data.signals.rsi <= 30 ? "bg-green-900/40 text-green-400" :
            "bg-yellow-900/40 text-yellow-400"
          }`}>
            {data.signals.rsi}
          </div>
        </div>
        <ResponsiveContainer width="100%" height={180}>
          <ComposedChart data={recent}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="date" ticks={ticks} tick={{ fill: "#6b7280", fontSize: 9 }} />
            <YAxis domain={[0, 100]} tick={{ fill: "#6b7280", fontSize: 9 }} />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="4 2" strokeWidth={1} label={{ value: "70", fill: "#ef4444", fontSize: 9 }} />
            <ReferenceLine y={30} stroke="#22c55e" strokeDasharray="4 2" strokeWidth={1} label={{ value: "30", fill: "#22c55e", fontSize: 9 }} />
            <ReferenceLine y={50} stroke="#6b7280" strokeDasharray="4 2" strokeWidth={1} />
            <Line type="monotone" dataKey="rsi" stroke="#a78bfa" dot={false} strokeWidth={2} name="RSI" connectNulls />
          </ComposedChart>
        </ResponsiveContainer>
        <div className="flex justify-between mt-2 text-xs text-gray-500">
          <span className="text-green-400">← Oversold (≤30)</span>
          <span className="text-red-400">Overbought (≥70) →</span>
        </div>
      </div>

      {/* MACD */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white">MACD (12, 26, 9)</h3>
            <p className="text-xs text-gray-500 mt-0.5">Moving Average Convergence Divergence</p>
          </div>
          <div className={`text-xs font-bold px-2 py-1 rounded ${
            data.signals.macdBullish ? "bg-green-900/40 text-green-400" : "bg-red-900/40 text-red-400"
          }`}>
            {data.signals.macdBullish ? "Bullish" : "Bearish"}
          </div>
        </div>
        <ResponsiveContainer width="100%" height={180}>
          <ComposedChart data={recent}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="date" ticks={ticks} tick={{ fill: "#6b7280", fontSize: 9 }} />
            <YAxis tick={{ fill: "#6b7280", fontSize: 9 }} domain={["auto", "auto"]} />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={0} stroke="#4b5563" strokeWidth={1} />
            <Bar dataKey="macd_hist" name="Histogram" radius={1}>
              {recent.map((entry, i) => (
                <Cell key={i} fill={(entry.macd_hist ?? 0) >= 0 ? "#22c55e" : "#ef4444"} fillOpacity={0.7} />
              ))}
            </Bar>
            <Line type="monotone" dataKey="macd"        stroke="#60a5fa" dot={false} strokeWidth={1.5} name="MACD" connectNulls />
            <Line type="monotone" dataKey="macd_signal" stroke="#f59e0b" dot={false} strokeWidth={1.5} name="Signal" connectNulls />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
