"use client";

import { useState } from "react";
import SearchBar from "@/components/SearchBar";
import StockHeader from "@/components/StockHeader";
import PriceChart from "@/components/PriceChart";
import TechnicalIndicators from "@/components/TechnicalIndicators";
import FundamentalsCard from "@/components/FundamentalsCard";
import AgentPipeline from "@/components/AgentPipeline";
import SignalCard from "@/components/SignalCard";

export interface StockData {
  ticker: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  marketCap: number;
  volume: number;
  high52: number;
  low52: number;
  pe: number;
  eps: number;
  dividend: number;
  beta: number;
  sector: string;
  industry: string;
  priceData: { date: string; open: number; high: number; low: number; close: number; volume: number }[];
}

export interface IndicatorData {
  indicators: {
    date: string;
    rsi: number | null;
    macd: number | null;
    macd_signal: number | null;
    macd_hist: number | null;
    bb_upper: number | null;
    bb_mid: number | null;
    bb_lower: number | null;
    ema20: number | null;
    ema50: number | null;
    ema200: number | null;
    close: number | null;
    volume: number | null;
    vol_sma20: number | null;
  }[];
  signals: {
    rsi: number;
    macd: number;
    trend: string;
    aboveEma20: boolean;
    aboveEma50: boolean;
    aboveEma200: boolean;
    macdBullish: boolean;
  };
}

export default function Home() {
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [indicatorData, setIndicatorData] = useState<IndicatorData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [period, setPeriod] = useState("6mo");

  const fetchData = async (ticker: string, selectedPeriod = period) => {
    setLoading(true);
    setError(null);
    try {
      const [stockRes, indicatorRes] = await Promise.all([
        fetch(`/api/stock?ticker=${ticker}&period=${selectedPeriod}`),
        fetch(`/api/indicators?ticker=${ticker}`),
      ]);
      const stock = await stockRes.json();
      const indicators = await indicatorRes.json();
      if (stock.error) throw new Error(stock.error);
      if (indicators.error) throw new Error(indicators.error);
      setStockData(stock);
      setIndicatorData(indicators);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to fetch data");
    } finally {
      setLoading(false);
    }
  };

  const handlePeriodChange = (p: string) => {
    setPeriod(p);
    if (stockData) fetchData(stockData.ticker, p);
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Top Nav */}
      <nav className="border-b border-gray-800 bg-gray-900/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-sm font-bold">
              AI
            </div>
            <div>
              <h1 className="text-base font-bold text-white">AI Trading Agents</h1>
              <p className="text-xs text-gray-400">Multi-Agent Orchestration Dashboard</p>
            </div>
          </div>
          <SearchBar onSearch={(t) => fetchData(t)} loading={loading} />
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Welcome state */}
        {!stockData && !loading && (
          <div className="flex flex-col items-center justify-center py-32 text-center">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-3xl mb-6">
              📈
            </div>
            <h2 className="text-3xl font-bold mb-3">AI-Powered Stock Analysis</h2>
            <p className="text-gray-400 max-w-md text-sm">
              Enter any ticker symbol above — US stocks, Indian NSE/BSE, crypto, or global markets — 
              to see real-time charts, technical indicators, and AI agent insights.
            </p>
            <div className="mt-6 flex flex-wrap gap-2 justify-center">
              {["AAPL", "NVDA", "RELIANCE.NS", "BTC-USD", "INFY.NS", "TSLA"].map((t) => (
                <button
                  key={t}
                  onClick={() => fetchData(t)}
                  className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm font-mono text-blue-400 transition-colors"
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-32">
            <div className="flex flex-col items-center gap-4">
              <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-gray-400">Fetching market data...</p>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-900/30 border border-red-700 rounded-xl p-4 text-red-300 text-sm">
            ⚠️ {error}
          </div>
        )}

        {/* Dashboard */}
        {stockData && !loading && (
          <>
            <StockHeader stock={stockData} onPeriodChange={handlePeriodChange} period={period} />

            {/* Signals row */}
            {indicatorData && (
              <SignalCard signals={indicatorData.signals} />
            )}

            {/* Main chart */}
            <PriceChart data={stockData.priceData} indicatorData={indicatorData} />

            {/* Technical indicators */}
            {indicatorData && (
              <TechnicalIndicators data={indicatorData} />
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Fundamentals */}
              <FundamentalsCard stock={stockData} />

              {/* Agent pipeline */}
              <AgentPipeline ticker={stockData.ticker} />
            </div>
          </>
        )}
      </main>
    </div>
  );
}
