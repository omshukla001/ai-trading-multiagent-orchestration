"use client";
import {
  ComposedChart, Line, Area, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, Cell, ReferenceLine
} from "recharts";
import { StockData, IndicatorData } from "@/app/page";
import { useState, useMemo } from "react";

const CustomTooltip = ({ active, payload, label }: {
  active?: boolean;
  payload?: { name: string; value: number; color: string }[];
  label?: string;
}) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-gray-900 border border-gray-700 rounded-lg p-3 text-xs shadow-xl min-w-[160px]">
      <p className="text-gray-400 mb-2 font-medium">{label}</p>
      {payload.map((p) => (
        <div key={p.name} className="flex justify-between gap-4">
          <span style={{ color: p.color }}>{p.name}</span>
          <span className="text-white font-mono">
            {typeof p.value === "number" ? p.value.toFixed(2) : p.value}
          </span>
        </div>
      ))}
    </div>
  );
};

const INDICATOR_OPTIONS = [
  { key: "bb",    label: "BB",     title: "Bollinger Bands", color: "#3b82f6" },
  { key: "ema20", label: "EMA20",  title: "EMA 20",          color: "#22d3ee" },
  { key: "ema50", label: "EMA50",  title: "EMA 50",          color: "#f59e0b" },
  { key: "ema200",label: "EMA200", title: "EMA 200",         color: "#f43f5e" },
  { key: "vol",   label: "Volume", title: "Volume",          color: "#8b5cf6" },
  { key: "macd",  label: "MACD",   title: "MACD",            color: "#10b981" },
  { key: "rsi",   label: "RSI",    title: "RSI (14)",        color: "#a78bfa" },
];

export default function PriceChart({
  data,
  indicatorData,
}: {
  data: StockData["priceData"];
  indicatorData: IndicatorData | null;
}) {
  const [active, setActive] = useState<Set<string>>(
    new Set(["bb", "ema20", "ema50"])
  );

  const toggle = (key: string) => {
    setActive((prev) => {
      const next = new Set(prev);
      next.has(key) ? next.delete(key) : next.add(key);
      return next;
    });
  };

  const on = (key: string) => active.has(key);

  // Build a lookup map from indicator date → indicator row (O(1) lookup)
  const indMap = useMemo(() => {
    const map: Record<string, IndicatorData["indicators"][0]> = {};
    if (!indicatorData) return map;
    for (const row of indicatorData.indicators) {
      map[row.date] = row; // key is "YYYY-MM-DD"
    }
    return map;
  }, [indicatorData]);

  // Merge: for intraday dates like "2026-07-15 09:30", extract just the date part
  const merged = useMemo(() => {
    return data.map((d) => {
      // Extract YYYY-MM-DD from either "YYYY-MM-DD" or "YYYY-MM-DD HH:MM"
      const dateKey = d.date.substring(0, 10);
      const ind = indMap[dateKey];
      return {
        ...d,
        bb_upper:    ind?.bb_upper    ?? null,
        bb_mid:      ind?.bb_mid      ?? null,
        bb_lower:    ind?.bb_lower    ?? null,
        ema20:       ind?.ema20       ?? null,
        ema50:       ind?.ema50       ?? null,
        ema200:      ind?.ema200      ?? null,
        vol_sma20:   ind?.vol_sma20   ?? null,
        rsi:         ind?.rsi         ?? null,
        macd:        ind?.macd        ?? null,
        macd_signal: ind?.macd_signal ?? null,
        macd_hist:   ind?.macd_hist   ?? null,
      };
    });
  }, [data, indMap]);

  // X axis ticks
  const ticks = useMemo(() => {
    const count = Math.min(8, data.length);
    const step  = Math.ceil(data.length / count);
    return data.filter((_, i) => i % step === 0).map((d) => d.date);
  }, [data]);

  const showVol  = on("vol");
  const showMacd = on("macd");
  const showRsi  = on("rsi");
  const subCount = [showVol, showMacd, showRsi].filter(Boolean).length;

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-4">
      {/* Header + toggles */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-white">Price Chart</h3>
        <div className="flex flex-wrap gap-1.5">
          {INDICATOR_OPTIONS.map((ind) => (
            <button
              key={ind.key}
              onClick={() => toggle(ind.key)}
              title={ind.title}
              className="px-2.5 py-1 rounded-md text-xs font-medium border transition-all"
              style={
                on(ind.key)
                  ? { backgroundColor: ind.color + "22", borderColor: ind.color, color: ind.color }
                  : { backgroundColor: "transparent", borderColor: "#374151", color: "#6b7280" }
              }
            >
              {on(ind.key) ? "✓ " : ""}{ind.label}
            </button>
          ))}
          <button
            onClick={() => setActive(new Set(INDICATOR_OPTIONS.map((i) => i.key)))}
            className="px-2.5 py-1 rounded-md text-xs font-medium border border-gray-700 text-gray-400 hover:border-blue-500 hover:text-blue-400 transition-all"
          >All</button>
          <button
            onClick={() => setActive(new Set())}
            className="px-2.5 py-1 rounded-md text-xs font-medium border border-gray-700 text-gray-400 hover:border-red-500 hover:text-red-400 transition-all"
          >Clear</button>
        </div>
      </div>

      {/* ── Main price chart ── */}
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={merged} margin={{ right: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis dataKey="date" ticks={ticks} tick={{ fill: "#6b7280", fontSize: 10 }} />
          <YAxis tick={{ fill: "#6b7280", fontSize: 10 }} domain={["auto", "auto"]} width={60} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 11 }} />

          {on("bb") && <>
            <Area type="monotone" dataKey="bb_upper" stroke="none" fill="#3b82f6" fillOpacity={0.07} name="BB Upper Fill" legendType="none" />
            <Area type="monotone" dataKey="bb_lower" stroke="none" fill="#3b82f6" fillOpacity={0.07} name="BB Lower Fill" legendType="none" />
            <Line type="monotone" dataKey="bb_upper" stroke="#3b82f6" dot={false} strokeWidth={1} name="BB Upper" strokeDasharray="4 2" opacity={0.8} connectNulls />
            <Line type="monotone" dataKey="bb_lower" stroke="#3b82f6" dot={false} strokeWidth={1} name="BB Lower" strokeDasharray="4 2" opacity={0.8} connectNulls />
            <Line type="monotone" dataKey="bb_mid"   stroke="#6366f1" dot={false} strokeWidth={1} name="BB Mid"   strokeDasharray="3 3" opacity={0.7} connectNulls />
          </>}

          {on("ema20")  && <Line type="monotone" dataKey="ema20"  stroke="#22d3ee" dot={false} strokeWidth={1.5} name="EMA20"  strokeDasharray="5 3" connectNulls />}
          {on("ema50")  && <Line type="monotone" dataKey="ema50"  stroke="#f59e0b" dot={false} strokeWidth={1.5} name="EMA50"  strokeDasharray="5 3" connectNulls />}
          {on("ema200") && <Line type="monotone" dataKey="ema200" stroke="#f43f5e" dot={false} strokeWidth={1.5} name="EMA200" strokeDasharray="5 3" connectNulls />}

          {/* Close price — always visible */}
          <Line type="monotone" dataKey="close" stroke="#10b981" dot={false} strokeWidth={2} name="Close" connectNulls />
        </ComposedChart>
      </ResponsiveContainer>

      {/* ── Sub-charts ── */}
      {subCount > 0 && (
        <div className={`grid gap-4 ${subCount >= 2 ? "grid-cols-1 lg:grid-cols-2" : "grid-cols-1"}`}>

          {/* Volume */}
          {showVol && (
            <div>
              <p className="text-xs text-gray-400 mb-1 font-medium">📊 Volume</p>
              <ResponsiveContainer width="100%" height={130}>
                <ComposedChart data={merged} margin={{ right: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                  <XAxis dataKey="date" ticks={ticks} tick={{ fill: "#6b7280", fontSize: 9 }} />
                  <YAxis tick={{ fill: "#6b7280", fontSize: 9 }} width={50} tickFormatter={(v) => `${(v / 1e6).toFixed(0)}M`} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="volume" fill="#8b5cf6" opacity={0.6} name="Volume" radius={[1,1,0,0]} />
                  <Line type="monotone" dataKey="vol_sma20" stroke="#f59e0b" dot={false} strokeWidth={1.5} name="Vol SMA20" connectNulls />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* RSI */}
          {showRsi && (
            <div>
              <p className="text-xs text-gray-400 mb-1 font-medium">📈 RSI (14)</p>
              <ResponsiveContainer width="100%" height={130}>
                <ComposedChart data={merged} margin={{ right: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                  <XAxis dataKey="date" ticks={ticks} tick={{ fill: "#6b7280", fontSize: 9 }} />
                  <YAxis domain={[0, 100]} tick={{ fill: "#6b7280", fontSize: 9 }} width={30} />
                  <Tooltip content={<CustomTooltip />} />
                  <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="4 2" strokeWidth={1} />
                  <ReferenceLine y={50} stroke="#6b7280" strokeDasharray="3 3" strokeWidth={1} />
                  <ReferenceLine y={30} stroke="#22c55e" strokeDasharray="4 2" strokeWidth={1} />
                  <Line type="monotone" dataKey="rsi" stroke="#a78bfa" dot={false} strokeWidth={2} name="RSI" connectNulls />
                </ComposedChart>
              </ResponsiveContainer>
              <div className="flex justify-between text-xs mt-1">
                <span className="text-green-400">30 Oversold</span>
                <span className="text-red-400">70 Overbought</span>
              </div>
            </div>
          )}

          {/* MACD */}
          {showMacd && (
            <div className={subCount === 3 ? "lg:col-span-2" : ""}>
              <p className="text-xs text-gray-400 mb-1 font-medium">📉 MACD (12, 26, 9)</p>
              <ResponsiveContainer width="100%" height={130}>
                <ComposedChart data={merged} margin={{ right: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                  <XAxis dataKey="date" ticks={ticks} tick={{ fill: "#6b7280", fontSize: 9 }} />
                  <YAxis tick={{ fill: "#6b7280", fontSize: 9 }} width={45} domain={["auto","auto"]} />
                  <Tooltip content={<CustomTooltip />} />
                  <ReferenceLine y={0} stroke="#4b5563" strokeWidth={1} />
                  <Bar dataKey="macd_hist" name="Histogram" radius={[1,1,0,0]}>
                    {merged.map((entry, i) => (
                      <Cell key={i} fill={(entry.macd_hist ?? 0) >= 0 ? "#22c55e" : "#ef4444"} fillOpacity={0.7} />
                    ))}
                  </Bar>
                  <Line type="monotone" dataKey="macd"        stroke="#60a5fa" dot={false} strokeWidth={1.5} name="MACD"   connectNulls />
                  <Line type="monotone" dataKey="macd_signal" stroke="#f59e0b" dot={false} strokeWidth={1.5} name="Signal" connectNulls />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      <p className="text-xs text-gray-600 text-center">
        Toggle indicators above · Close price always visible
      </p>
    </div>
  );
}
