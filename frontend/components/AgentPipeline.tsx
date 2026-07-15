"use client";
import { useState } from "react";

const AGENTS = [
  {
    layer: "📊 Data Layer",
    color: "border-blue-700/50 bg-blue-900/20",
    badge: "bg-blue-900/40 text-blue-300",
    agents: [
      { name: "Market Analyst",       role: "Technical indicators (RSI, MACD, Bollinger Bands)",   type: "Python" },
      { name: "Fundamentals Analyst", role: "P/E ratio, EPS, balance sheet analysis",              type: "Python" },
      { name: "Sentiment Analyst",    role: "Reddit, StockTwits sentiment aggregation",            type: "LLM" },
      { name: "News Analyst",         role: "Global news & macroeconomic interpretation",          type: "LLM" },
    ],
  },
  {
    layer: "🔬 Research Layer",
    color: "border-purple-700/50 bg-purple-900/20",
    badge: "bg-purple-900/40 text-purple-300",
    agents: [
      { name: "Bull Researcher",   role: "Builds strongest bullish investment thesis",    type: "LLM" },
      { name: "Bear Researcher",   role: "Argues against — surfaces risks and downside",  type: "LLM" },
      { name: "Research Manager",  role: "Synthesizes bull/bear debate into a plan",      type: "LLM" },
    ],
  },
  {
    layer: "💼 Trading Layer",
    color: "border-emerald-700/50 bg-emerald-900/20",
    badge: "bg-emerald-900/40 text-emerald-300",
    agents: [
      { name: "Trader", role: "Creates concrete transaction proposal with entry/exit/size", type: "LLM" },
    ],
  },
  {
    layer: "🛡️ Risk Layer",
    color: "border-orange-700/50 bg-orange-900/20",
    badge: "bg-orange-900/40 text-orange-300",
    agents: [
      { name: "Aggressive Analyst",   role: "High-risk tolerance position sizing",   type: "Python" },
      { name: "Neutral Analyst",      role: "Balanced risk assessment",              type: "Python" },
      { name: "Conservative Analyst", role: "Low-risk tolerance calculations",       type: "Python" },
    ],
  },
  {
    layer: "✅ Decision Layer",
    color: "border-yellow-700/50 bg-yellow-900/20",
    badge: "bg-yellow-900/40 text-yellow-300",
    agents: [
      { name: "Portfolio Manager", role: "Final approval with veto power → BUY / SELL / HOLD", type: "LLM" },
    ],
  },
];

export default function AgentPipeline({ ticker }: { ticker: string }) {
  const [expanded, setExpanded] = useState<number | null>(null);

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-white">🤖 Multi-Agent Pipeline</h3>
        <p className="text-xs text-gray-500 mt-0.5">
          11 specialized agents collaborate to analyze <span className="text-blue-400 font-mono">{ticker}</span>
        </p>
      </div>

      <div className="space-y-2">
        {AGENTS.map((layer, li) => (
          <div key={li}>
            <button
              onClick={() => setExpanded(expanded === li ? null : li)}
              className={`w-full text-left border rounded-lg p-3 transition-all ${layer.color} hover:opacity-90`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-white">{layer.layer}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${layer.badge}`}>
                    {layer.agents.length} agent{layer.agents.length > 1 ? "s" : ""}
                  </span>
                </div>
                <span className="text-gray-400 text-xs">{expanded === li ? "▲" : "▼"}</span>
              </div>
            </button>

            {expanded === li && (
              <div className="ml-3 mt-1 space-y-1 pl-3 border-l border-gray-700">
                {layer.agents.map((agent, ai) => (
                  <div key={ai} className="py-1.5">
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-white font-medium">{agent.name}</span>
                      <span className={`text-xs px-1.5 py-0.5 rounded font-mono ${
                        agent.type === "LLM"
                          ? "bg-purple-900/50 text-purple-300"
                          : "bg-blue-900/50 text-blue-300"
                      }`}>
                        {agent.type}
                      </span>
                    </div>
                    <p className="text-xs text-gray-400 mt-0.5">{agent.role}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Flow arrow */}
      <div className="mt-4 pt-4 border-t border-gray-800 flex items-center justify-center gap-1 text-xs text-gray-500">
        <span className="text-blue-400">Data</span>
        <span>→</span>
        <span className="text-purple-400">Debate</span>
        <span>→</span>
        <span className="text-emerald-400">Trade</span>
        <span>→</span>
        <span className="text-orange-400">Risk</span>
        <span>→</span>
        <span className="text-yellow-400 font-bold">Decision</span>
      </div>

      <p className="text-center text-xs text-gray-600 mt-2">
        Expand each layer to see individual agents
      </p>
    </div>
  );
}
