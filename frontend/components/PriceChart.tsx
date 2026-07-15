"use client";
import {
  ComposedChart, Line, Area, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from "recharts";
import { StockData, IndicatorData } from "@/app/page";
import { useState } from "react";

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: { name: string; value: number; color: string }[]; label?: string }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-gray-900 border border-gray-700 rounded-lg p-3 text-xs shadow-xl">
      <p className="text-gray-400 mb-2 font-medium">{label}</p>
      {payload.map((p) => (
        <div key={p.name} className="flex justify-between gap-4">
          <span style={{ color: p.color }}>{p.name}</span>
          <span className="text-white font-mono">{typeof p.value === "number" ? p.value.toFixed(2) : p.value}</span>
        </div>
      ))}
    </div>
  );
};

const VIEWS = ["Price + BB", "Volume", "EMA Lines"];

export default function PriceChart({
  data,
  indicatorData,
}: {
  data: StockData["priceData"];
  indicatorData: IndicatorData | null;
}) {
  const [view, setView] = useState("Price + BB");

  // Merge price + indicator data by date
  const merged = data.map((d) => {
    const ind = indicatorData?.indicators.find((i) => i.date === d.date);
    return {
      ...d,
      bb_upper: ind?.bb_upper ?? null,
      bb_mid: ind?.bb_mid ?? null,
      bb_lower: ind?.bb_lower ?? null,
      ema20: ind?.ema20 ?? null,
      ema50: ind?.ema50 ?? null,
      ema200: ind?.ema200 ?? null,
      vol_sma20: ind?.vol_sma20 ?? null,
    };
  });

  // X axis: show fewer labels on dense data
  const tickCount = Math.min(8, data.length);
  const step = Math.ceil(data.length / tickCount);
  const ticks = data.filter((_, i) => i % step === 0).map((d) => d.date);

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-white">Price Chart</h3>
        <div className="flex gap-1">
          {VIEWS.map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                view === v ? "bg-blue-600 text-white" : "bg-gray-800 text-gray-400 hover:bg-gray-700"
              }`}
            >
              {v}
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={340}>
        {view === "Volume" ? (
          <ComposedChart data={merged}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="date" ticks={ticks} tick={{ fill: "#6b7280", fontSize: 10 }} />
            <YAxis yAxisId="vol" orientation="right" tick={{ fill: "#6b7280", fontSize: 10 }} tickFormatter={(v) => `${(v / 1e6).toFixed(0)}M`} />
            <YAxis yAxisId="price" tick={{ fill: "#6b7280", fontSize: 10 }} domain={["auto", "auto"]} />
            <Tooltip content={<CustomTooltip />} />
            <Bar yAxisId="vol" dataKey="volume" fill="#3b82f6" opacity={0.6} name="Volume" />
            <Line yAxisId="vol" type="monotone" dataKey="vol_sma20" stroke="#f59e0b" dot={false} strokeWidth={1.5} name="Vol SMA20" />
            <Line yAxisId="price" type="monotone" dataKey="close" stroke="#8b5cf6" dot={false} strokeWidth={1.5} name="Close" />
          </ComposedChart>
        ) : view === "EMA Lines" ? (
          <ComposedChart data={merged}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="date" ticks={ticks} tick={{ fill: "#6b7280", fontSize: 10 }} />
            <YAxis tick={{ fill: "#6b7280", fontSize: 10 }} domain={["auto", "auto"]} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Line type="monotone" dataKey="close"  stroke="#e2e8f0" dot={false} strokeWidth={1.5} name="Close" />
            <Line type="monotone" dataKey="ema20"  stroke="#22d3ee" dot={false} strokeWidth={1.5} name="EMA20" strokeDasharray="4 2" />
            <Line type="monotone" dataKey="ema50"  stroke="#f59e0b" dot={false} strokeWidth={1.5} name="EMA50" strokeDasharray="4 2" />
            <Line type="monotone" dataKey="ema200" stroke="#f43f5e" dot={false} strokeWidth={1.5} name="EMA200" strokeDasharray="4 2" />
          </ComposedChart>
        ) : (
          <ComposedChart data={merged}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="date" ticks={ticks} tick={{ fill: "#6b7280", fontSize: 10 }} />
            <YAxis tick={{ fill: "#6b7280", fontSize: 10 }} domain={["auto", "auto"]} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            {/* Bollinger Band fill */}
            <Area type="monotone" dataKey="bb_upper" stroke="none" fill="#3b82f6" fillOpacity={0.08} name="BB Upper" legendType="none" />
            <Area type="monotone" dataKey="bb_lower" stroke="none" fill="#3b82f6" fillOpacity={0.08} name="BB Lower" legendType="none" />
            <Line type="monotone" dataKey="bb_upper" stroke="#3b82f6" dot={false} strokeWidth={1} name="BB Upper" strokeDasharray="3 3" opacity={0.6} />
            <Line type="monotone" dataKey="bb_lower" stroke="#3b82f6" dot={false} strokeWidth={1} name="BB Lower" strokeDasharray="3 3" opacity={0.6} />
            <Line type="monotone" dataKey="bb_mid"   stroke="#6366f1" dot={false} strokeWidth={1} name="BB Mid" strokeDasharray="4 2" opacity={0.7} />
            <Line type="monotone" dataKey="close"    stroke="#10b981" dot={false} strokeWidth={2} name="Close" />
          </ComposedChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}
