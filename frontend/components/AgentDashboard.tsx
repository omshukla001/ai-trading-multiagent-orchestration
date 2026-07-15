'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  Play,
  Loader2,
  CheckCircle2,
  TrendingUp,
  TrendingDown,
  Minus,
  Shield,
  Target,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  BarChart3,
  DollarSign,
  Activity,
  Zap,
  Clock,
  PieChart,
} from 'lucide-react';

// ── Types ────────────────────────────────────────────────────────────────────

export interface AgentReport {
  ticker: string;
  name: string;
  currencySymbol: string;
  timestamp: string;
  newsCount?: number;
  redditPostCount?: number;
  newsHeadlines?: string[];
  redditTitles?: string[];
  marketAnalysis: {
    signal: 'bullish' | 'bearish' | 'neutral';
    summary: string;
    indicators: {
      name: string;
      value: string;
      signal: 'bullish' | 'bearish' | 'neutral';
      detail: string;
    }[];
  };
  fundamentalsAnalysis: {
    signal: 'bullish' | 'bearish' | 'neutral';
    summary: string;
    metrics: {
      name: string;
      value: string;
      signal: 'bullish' | 'bearish' | 'neutral';
      detail: string;
    }[];
  };
  sentimentAnalysis: {
    signal: 'bullish' | 'bearish' | 'neutral';
    summary: string;
    detail: string;
  };
  bullCase: { thesis: string; keyPoints: string[]; targetPrice: number };
  bearCase: { thesis: string; keyPoints: string[]; targetPrice: number };
  researchSummary: string;
  riskAssessment: {
    level: 'low' | 'medium' | 'high' | 'very_high';
    score: number;
    factors: {
      name: string;
      level: 'low' | 'medium' | 'high';
      detail: string;
    }[];
  };
  decision: {
    action: 'STRONG BUY' | 'BUY' | 'HOLD' | 'SELL' | 'STRONG SELL';
    confidence: number;
    reasoning: string;
    entryPrice: number;
    targetPrice: number;
    stopLoss: number;
    timeHorizon: string;
    positionSize: string;
  };
}

// ── Constants ────────────────────────────────────────────────────────────────

const STAGES = ['Data Analysis', 'Research', 'Trading', 'Risk', 'Decision'];
const STAGE_ICONS = ['📊', '🔬', '💼', '🛡️', '✅'];

// ── Helpers ──────────────────────────────────────────────────────────────────

function signalBadgeClasses(signal: 'bullish' | 'bearish' | 'neutral'): string {
  switch (signal) {
    case 'bullish':
      return 'bg-green-500/20 text-green-400 border border-green-500/30';
    case 'bearish':
      return 'bg-red-500/20 text-red-400 border border-red-500/30';
    case 'neutral':
      return 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30';
  }
}

function signalDotColor(signal: 'bullish' | 'bearish' | 'neutral'): string {
  switch (signal) {
    case 'bullish':
      return 'bg-green-400';
    case 'bearish':
      return 'bg-red-400';
    case 'neutral':
      return 'bg-yellow-400';
  }
}

function signalLabel(signal: 'bullish' | 'bearish' | 'neutral'): string {
  return signal.charAt(0).toUpperCase() + signal.slice(1);
}

function actionBadgeClasses(
  action: AgentReport['decision']['action'],
): string {
  switch (action) {
    case 'STRONG BUY':
      return 'bg-green-500 text-white';
    case 'BUY':
      return 'bg-emerald-500 text-white';
    case 'HOLD':
      return 'bg-yellow-500 text-gray-900';
    case 'SELL':
      return 'bg-orange-500 text-white';
    case 'STRONG SELL':
      return 'bg-red-500 text-white';
  }
}

function riskLevelClasses(level: string): string {
  switch (level) {
    case 'low':
      return 'bg-green-500/20 text-green-400 border border-green-500/30';
    case 'medium':
      return 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30';
    case 'high':
      return 'bg-orange-500/20 text-orange-400 border border-orange-500/30';
    case 'very_high':
      return 'bg-red-500/20 text-red-400 border border-red-500/30';
    default:
      return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
  }
}

function riskLevelDot(level: string): string {
  switch (level) {
    case 'low':
      return 'bg-green-400';
    case 'medium':
      return 'bg-yellow-400';
    case 'high':
      return 'bg-orange-400';
    case 'very_high':
      return 'bg-red-400';
    default:
      return 'bg-gray-400';
  }
}

function riskLevelLabel(level: string): string {
  return level
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

function riskBarColor(score: number): string {
  if (score <= 30) return 'from-green-500 to-green-400';
  if (score <= 60) return 'from-yellow-500 to-yellow-400';
  if (score <= 80) return 'from-orange-500 to-orange-400';
  return 'from-red-500 to-red-400';
}

function confidenceBarColor(pct: number): string {
  if (pct < 30) return 'from-red-500 via-red-400 to-red-400';
  if (pct < 60) return 'from-red-500 via-yellow-400 to-yellow-400';
  return 'from-red-500 via-yellow-400 to-green-400';
}

// ── Component ────────────────────────────────────────────────────────────────

export default function AgentDashboard({ ticker }: { ticker: string }) {
  const [report, setReport] = useState<AgentReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasRun, setHasRun] = useState(false);
  const [activeStage, setActiveStage] = useState(-1);

  // Expanded indicator / metric toggles
  const [expandedMarketIdx, setExpandedMarketIdx] = useState<number | null>(null);
  const [expandedFundIdx, setExpandedFundIdx] = useState<number | null>(null);

  // Reset state when ticker changes
  useEffect(() => {
    setReport(null);
    setLoading(false);
    setError(null);
    setHasRun(false);
    setActiveStage(-1);
    setExpandedMarketIdx(null);
    setExpandedFundIdx(null);
  }, [ticker]);

  // Pipeline animation during loading
  useEffect(() => {
    if (!loading) return;
    setActiveStage(0);
    const interval = setInterval(() => {
      setActiveStage((prev) => Math.min(prev + 1, STAGES.length - 1));
    }, 2000);
    return () => clearInterval(interval);
  }, [loading]);

  const runAnalysis = useCallback(async () => {
    setLoading(true);
    setError(null);
    setHasRun(true);
    setReport(null);

    try {
      const res = await fetch(`/api/agents?ticker=${ticker}`);
      if (!res.ok) {
        throw new Error(`Analysis failed (${res.status}): ${res.statusText}`);
      }
      const data: AgentReport = await res.json();
      setReport(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  }, [ticker]);

  // ── Sub-renders ──────────────────────────────────────────────────────────

  const renderPipeline = () => {
    if (!hasRun) return null;
    const isComplete = !loading && report !== null;

    return (
      <div className="mb-8">
        <div className="flex items-center justify-center gap-0">
          {STAGES.map((stage, i) => {
            const isDone = isComplete || (!loading && i <= activeStage);
            const isActive = loading && i === activeStage;
            const isPending = loading && i > activeStage;
            const isPast = loading && i < activeStage;

            return (
              <div key={stage} className="flex items-center">
                {/* Stage pill */}
                <div
                  className={`
                    flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium
                    transition-all duration-500 select-none
                    ${
                      isComplete || isDone || isPast
                        ? 'bg-green-500/20 text-green-400 border border-green-500/40'
                        : isActive
                          ? 'bg-gradient-to-r from-blue-600/30 to-purple-600/30 text-blue-300 border border-blue-500/50 animate-pulse shadow-lg shadow-blue-500/20'
                          : 'bg-gray-800 text-gray-500 border border-gray-700'
                    }
                  `}
                >
                  {isComplete || isDone || isPast ? (
                    <CheckCircle2 className="w-4 h-4 text-green-400" />
                  ) : (
                    <span className="text-base leading-none">{STAGE_ICONS[i]}</span>
                  )}
                  <span className="hidden sm:inline">{stage}</span>
                </div>

                {/* Connector */}
                {i < STAGES.length - 1 && (
                  <div
                    className={`
                      w-6 lg:w-10 h-px mx-1 transition-colors duration-500
                      ${
                        isComplete || isPast || isDone
                          ? 'bg-green-500/50'
                          : isActive
                            ? 'bg-blue-500/50'
                            : 'bg-gray-700'
                      }
                    `}
                  />
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderDecisionCard = () => {
    if (!report) return null;
    const { decision, currencySymbol } = report;

    return (
      <div className="mb-8">
        {/* Hero decision card */}
        <div className="relative rounded-2xl border border-gray-700 bg-gray-900 overflow-hidden transition-all duration-300 hover:border-gray-600">
          {/* Gradient accent bar */}
          <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500" />

          <div className="p-6 lg:p-8 flex flex-col lg:flex-row gap-6 lg:gap-10 items-start lg:items-center">
            {/* Left – Action badge */}
            <div className="flex flex-col items-center gap-2 shrink-0">
              <span
                className={`
                  inline-block rounded-xl px-6 py-3 text-2xl lg:text-3xl font-extrabold tracking-wide
                  ${actionBadgeClasses(decision.action)}
                  shadow-lg
                `}
              >
                {decision.action}
              </span>
              <span className="text-xs text-gray-500 uppercase tracking-widest">
                Recommendation
              </span>
            </div>

            {/* Right – Metrics */}
            <div className="flex-1 w-full space-y-5">
              {/* Confidence bar */}
              <div>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="text-gray-400 font-medium">Confidence</span>
                  <span className="text-white font-semibold">
                    {Math.round(decision.confidence)}%
                  </span>
                </div>
                <div className="w-full h-3 rounded-full bg-gray-800 overflow-hidden">
                  <div
                    className={`h-full rounded-full bg-gradient-to-r ${confidenceBarColor(decision.confidence)} transition-all duration-700`}
                    style={{ width: `${Math.min(decision.confidence, 100)}%` }}
                  />
                </div>
              </div>

              {/* Entry / Target / Stop Loss */}
              <div className="grid grid-cols-3 gap-3">
                <div className="rounded-lg bg-gray-800/60 border border-gray-700 p-3 text-center">
                  <div className="text-xs text-gray-500 mb-1 flex items-center justify-center gap-1">
                    <Target className="w-3 h-3" /> Entry
                  </div>
                  <div className="text-white font-semibold font-mono">
                    {currencySymbol}
                    {decision.entryPrice.toLocaleString()}
                  </div>
                </div>
                <div className="rounded-lg bg-gray-800/60 border border-gray-700 p-3 text-center">
                  <div className="text-xs text-gray-500 mb-1 flex items-center justify-center gap-1">
                    <TrendingUp className="w-3 h-3" /> Target
                  </div>
                  <div className="text-green-400 font-semibold font-mono">
                    {currencySymbol}
                    {decision.targetPrice.toLocaleString()}
                  </div>
                </div>
                <div className="rounded-lg bg-gray-800/60 border border-gray-700 p-3 text-center">
                  <div className="text-xs text-gray-500 mb-1 flex items-center justify-center gap-1">
                    <Shield className="w-3 h-3" /> Stop Loss
                  </div>
                  <div className="text-red-400 font-semibold font-mono">
                    {currencySymbol}
                    {decision.stopLoss.toLocaleString()}
                  </div>
                </div>
              </div>

              {/* Time Horizon | Position Size */}
              <div className="flex items-center gap-4 text-xs text-gray-500">
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {decision.timeHorizon}
                </span>
                <span className="text-gray-700">|</span>
                <span className="flex items-center gap-1">
                  <PieChart className="w-3 h-3" />
                  {decision.positionSize}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Reasoning */}
        <p className="mt-4 text-sm text-gray-400 leading-relaxed px-1">
          {decision.reasoning}
        </p>
      </div>
    );
  };

  const renderMarketAnalysis = () => {
    if (!report) return null;
    const { marketAnalysis } = report;

    return (
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 transition-all duration-300 hover:border-gray-700">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-white font-semibold flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-400" />
            📊 Technical Analysis
          </h3>
          <span
            className={`text-xs font-medium px-2.5 py-1 rounded-full ${signalBadgeClasses(marketAnalysis.signal)}`}
          >
            {signalLabel(marketAnalysis.signal)}
          </span>
        </div>

        <p className="text-sm text-gray-300 mb-4">{marketAnalysis.summary}</p>
        <hr className="border-gray-800 mb-4" />

        {/* Indicators */}
        <div className="space-y-1">
          {marketAnalysis.indicators.map((ind, i) => (
            <div key={ind.name}>
              <button
                onClick={() =>
                  setExpandedMarketIdx(expandedMarketIdx === i ? null : i)
                }
                className="w-full flex items-center gap-3 py-2 px-2 rounded-lg hover:bg-gray-800/60 transition-colors group"
              >
                <span
                  className={`w-2.5 h-2.5 rounded-full shrink-0 ${signalDotColor(ind.signal)}`}
                />
                <span className="text-sm text-gray-300 flex-1 text-left">
                  {ind.name}
                </span>
                <span className="text-sm text-gray-400 font-mono">
                  {ind.value}
                </span>
                {expandedMarketIdx === i ? (
                  <ChevronUp className="w-4 h-4 text-gray-500" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-gray-600 group-hover:text-gray-400 transition-colors" />
                )}
              </button>
              {expandedMarketIdx === i && (
                <p className="text-xs text-gray-500 pl-8 pr-2 pb-2 leading-relaxed">
                  {ind.detail}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderFundamentals = () => {
    if (!report) return null;
    const { fundamentalsAnalysis } = report;

    return (
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 transition-all duration-300 hover:border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-white font-semibold flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-emerald-400" />
            💰 Fundamental Analysis
          </h3>
          <span
            className={`text-xs font-medium px-2.5 py-1 rounded-full ${signalBadgeClasses(fundamentalsAnalysis.signal)}`}
          >
            {signalLabel(fundamentalsAnalysis.signal)}
          </span>
        </div>

        <p className="text-sm text-gray-300 mb-4">
          {fundamentalsAnalysis.summary}
        </p>
        <hr className="border-gray-800 mb-4" />

        <div className="space-y-1">
          {fundamentalsAnalysis.metrics.map((m, i) => (
            <div key={m.name}>
              <button
                onClick={() =>
                  setExpandedFundIdx(expandedFundIdx === i ? null : i)
                }
                className="w-full flex items-center gap-3 py-2 px-2 rounded-lg hover:bg-gray-800/60 transition-colors group"
              >
                <span
                  className={`w-2.5 h-2.5 rounded-full shrink-0 ${signalDotColor(m.signal)}`}
                />
                <span className="text-sm text-gray-300 flex-1 text-left">
                  {m.name}
                </span>
                <span className="text-sm text-gray-400 font-mono">
                  {m.value}
                </span>
                {expandedFundIdx === i ? (
                  <ChevronUp className="w-4 h-4 text-gray-500" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-gray-600 group-hover:text-gray-400 transition-colors" />
                )}
              </button>
              {expandedFundIdx === i && (
                <p className="text-xs text-gray-500 pl-8 pr-2 pb-2 leading-relaxed">
                  {m.detail}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderSentiment = () => {
    if (!report) return null;
    const { sentimentAnalysis } = report;

    return (
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 transition-all duration-300 hover:border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-white font-semibold flex items-center gap-2">
            <Activity className="w-5 h-5 text-purple-400" />
            📡 Sentiment Analysis
          </h3>
          <div className="flex items-center gap-2">
            {report.newsCount !== undefined && (
              <span className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded">
                📰 {report.newsCount} news
              </span>
            )}
            {report.redditPostCount !== undefined && (
              <span className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded">
                📱 {report.redditPostCount} reddit
              </span>
            )}
            <span
              className={`text-xs font-medium px-2.5 py-1 rounded-full ${signalBadgeClasses(sentimentAnalysis.signal)}`}
            >
              {signalLabel(sentimentAnalysis.signal)}
            </span>
          </div>
        </div>

        <p className="text-sm text-gray-300 mb-3">
          {sentimentAnalysis.summary}
        </p>
        <p className="text-xs text-gray-500 leading-relaxed mb-3">
          {sentimentAnalysis.detail}
        </p>

        {/* Real News Headlines */}
        {report.newsHeadlines && report.newsHeadlines.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-800">
            <p className="text-xs text-gray-400 font-medium mb-2">📰 Live News (Yahoo Finance):</p>
            <div className="space-y-1">
              {report.newsHeadlines.slice(0, 4).map((headline, i) => (
                <p key={i} className="text-xs text-gray-500 pl-3 border-l-2 border-blue-500/30">
                  {headline}
                </p>
              ))}
            </div>
          </div>
        )}

        {/* Reddit Posts */}
        {report.redditTitles && report.redditTitles.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-800">
            <p className="text-xs text-gray-400 font-medium mb-2">📱 Reddit Discussions:</p>
            <div className="space-y-1">
              {report.redditTitles.slice(0, 3).map((title, i) => (
                <p key={i} className="text-xs text-gray-500 pl-3 border-l-2 border-orange-500/30">
                  {title}
                </p>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderRiskAssessment = () => {
    if (!report) return null;
    const { riskAssessment } = report;

    return (
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 transition-all duration-300 hover:border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-white font-semibold flex items-center gap-2">
            <Shield className="w-5 h-5 text-orange-400" />
            🛡️ Risk Assessment
          </h3>
          <span
            className={`text-xs font-medium px-2.5 py-1 rounded-full ${riskLevelClasses(riskAssessment.level)}`}
          >
            {riskLevelLabel(riskAssessment.level)}
          </span>
        </div>

        {/* Risk score bar */}
        <div className="mb-4">
          <div className="flex justify-between text-sm mb-1.5">
            <span className="text-gray-400">Risk Score</span>
            <span className="text-white font-semibold">
              {riskAssessment.score}/100
            </span>
          </div>
          <div className="w-full h-2.5 rounded-full bg-gray-800 overflow-hidden">
            <div
              className={`h-full rounded-full bg-gradient-to-r ${riskBarColor(riskAssessment.score)} transition-all duration-700`}
              style={{ width: `${Math.min(riskAssessment.score, 100)}%` }}
            />
          </div>
        </div>

        <hr className="border-gray-800 mb-4" />

        {/* Factors */}
        <div className="space-y-3">
          {riskAssessment.factors.map((f) => (
            <div key={f.name} className="flex items-start gap-3">
              <span
                className={`w-2.5 h-2.5 rounded-full shrink-0 mt-1.5 ${riskLevelDot(f.level)}`}
              />
              <div>
                <div className="text-sm text-gray-300 font-medium">
                  {f.name}
                </div>
                <div className="text-xs text-gray-500">{f.detail}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderBullBear = () => {
    if (!report) return null;
    const { bullCase, bearCase, currencySymbol, researchSummary } = report;

    return (
      <div className="mb-8 space-y-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Bull */}
          <div className="rounded-xl border border-green-800/50 bg-green-950/30 p-5 transition-all duration-300 hover:border-green-700/60">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-green-400 font-semibold flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                📈 Bull Case
              </h3>
              <span className="text-green-400 font-mono font-semibold text-sm">
                Target: {currencySymbol}
                {bullCase.targetPrice.toLocaleString()}
              </span>
            </div>
            <p className="text-sm text-gray-300 mb-3">{bullCase.thesis}</p>
            <ul className="space-y-1.5">
              {bullCase.keyPoints.map((kp, i) => (
                <li
                  key={i}
                  className="flex items-start gap-2 text-sm text-gray-400"
                >
                  <span className="text-green-500 mt-1 shrink-0">●</span>
                  {kp}
                </li>
              ))}
            </ul>
          </div>

          {/* Bear */}
          <div className="rounded-xl border border-red-800/50 bg-red-950/30 p-5 transition-all duration-300 hover:border-red-700/60">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-red-400 font-semibold flex items-center gap-2">
                <TrendingDown className="w-5 h-5" />
                📉 Bear Case
              </h3>
              <span className="text-red-400 font-mono font-semibold text-sm">
                Target: {currencySymbol}
                {bearCase.targetPrice.toLocaleString()}
              </span>
            </div>
            <p className="text-sm text-gray-300 mb-3">{bearCase.thesis}</p>
            <ul className="space-y-1.5">
              {bearCase.keyPoints.map((kp, i) => (
                <li
                  key={i}
                  className="flex items-start gap-2 text-sm text-gray-400"
                >
                  <span className="text-red-500 mt-1 shrink-0">●</span>
                  {kp}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Research Summary */}
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
          <h3 className="text-white font-semibold mb-2 flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-400" />
            Research Summary
          </h3>
          <p className="text-sm text-gray-400 leading-relaxed">
            {researchSummary}
          </p>
        </div>
      </div>
    );
  };

  const renderEmptyState = () => (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="text-7xl mb-6 animate-bounce">🤖</div>
      <h2 className="text-2xl font-bold text-white mb-2">
        Multi-Agent Analysis Pipeline
      </h2>
      <p className="text-gray-400 max-w-md mb-4">
        Click{' '}
        <span className="text-blue-400 font-semibold">"Run Analysis"</span> to
        activate the multi-agent pipeline for{' '}
        <span className="text-white font-semibold">{ticker}</span>
      </p>
      <p className="text-sm text-gray-600 max-w-lg">
        11 specialized AI agents will analyze technical indicators, fundamentals,
        market sentiment, risk factors, and generate a comprehensive trading
        recommendation.
      </p>
    </div>
  );

  const renderError = () => {
    if (!error) return null;

    return (
      <div className="mb-6 rounded-xl border border-red-800/60 bg-red-950/30 p-5 flex items-start gap-4">
        <AlertTriangle className="w-6 h-6 text-red-400 shrink-0 mt-0.5" />
        <div className="flex-1">
          <h4 className="text-red-400 font-semibold mb-1">Analysis Failed</h4>
          <p className="text-sm text-red-300/80">{error}</p>
        </div>
        <button
          onClick={runAnalysis}
          className="shrink-0 rounded-lg bg-red-500/20 border border-red-500/30 px-4 py-2 text-sm text-red-400 font-medium
            hover:bg-red-500/30 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  };

  // ── Main render ────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-gray-950 text-white p-4 lg:p-8">
      <div className="max-w-6xl mx-auto">
        {/* ─── Header ─────────────────────────────────────────────────── */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl lg:text-3xl font-bold flex items-center gap-3">
              🤖 AI Multi-Agent Analysis
            </h1>
            <p className="text-gray-500 text-sm mt-1">
              11 specialized agents analyze{' '}
              <span className="text-blue-400 font-semibold">{ticker}</span>
            </p>
          </div>

          <button
            onClick={runAnalysis}
            disabled={loading}
            className={`
              inline-flex items-center gap-2 rounded-xl px-6 py-3 text-sm font-semibold text-white
              bg-gradient-to-r from-blue-600 to-purple-600
              hover:from-blue-500 hover:to-purple-500
              disabled:opacity-60 disabled:cursor-not-allowed
              transition-all duration-300 shadow-lg shadow-purple-500/20
              hover:shadow-purple-500/40
            `}
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Analyzing…
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Run Analysis ▶
              </>
            )}
          </button>
        </div>

        {/* ─── Pipeline Progress ──────────────────────────────────────── */}
        {renderPipeline()}

        {/* ─── Error State ────────────────────────────────────────────── */}
        {renderError()}

        {/* ─── Content ────────────────────────────────────────────────── */}
        {!hasRun && !loading && renderEmptyState()}

        {loading && !report && (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <Loader2 className="w-12 h-12 text-blue-400 animate-spin mb-4" />
            <p className="text-gray-400">
              Agents are analyzing{' '}
              <span className="text-white font-semibold">{ticker}</span>…
            </p>
            <p className="text-xs text-gray-600 mt-1">
              This usually takes 10–30 seconds
            </p>
          </div>
        )}

        {report && (
          <>
            {/* Decision Card */}
            {renderDecisionCard()}

            {/* Analysis Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-8">
              {renderMarketAnalysis()}
              {renderFundamentals()}
              {renderSentiment()}
              {renderRiskAssessment()}
            </div>

            {/* Bull vs Bear */}
            {renderBullBear()}
          </>
        )}
      </div>
    </div>
  );
}
