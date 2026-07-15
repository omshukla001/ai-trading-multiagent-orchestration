"""
Optimized Market/Technical Analyst - Pure Python Implementation
NO LLM USAGE - Deterministic rule-based analysis
Reduces token usage from 15k+ to ~200 tokens
"""

from langchain_core.messages import AIMessage
from tradingagents.dataflows.market_data_validator import build_verified_market_snapshot


class TechnicalAnalyzer:
    """
    Pure Python technical analysis engine
    Replaces LLM-based interpretation with rule-based scoring
    """
    
    def __init__(self):
        self.score = 50  # Neutral baseline
        self.signals = []
        self.confidence = 0.5
    
    def analyze_trend(self, snapshot: dict) -> dict:
        """Analyze trend using moving averages"""
        indicators = snapshot['indicators']
        close = snapshot['close']
        
        ema_10 = indicators.get('close_10_ema', close)
        sma_50 = indicators.get('close_50_sma', close)
        sma_200 = indicators.get('close_200_sma', close)
        
        trend_score = 0
        trend_signals = []
        
        # Short-term trend (Price vs EMA10)
        if close > ema_10:
            trend_score += 5
            trend_signals.append(f"Price above EMA10 ({close:.2f} > {ema_10:.2f})")
        else:
            trend_score -= 5
            trend_signals.append(f"Price below EMA10 ({close:.2f} < {ema_10:.2f})")
        
        # Medium-term trend (EMA10 vs SMA50)
        if ema_10 > sma_50:
            trend_score += 10
            trend_signals.append(f"EMA10 > SMA50 (bullish alignment)")
        else:
            trend_score -= 10
            trend_signals.append(f"EMA10 < SMA50 (bearish alignment)")
        
        # Long-term trend (Price vs SMA200)
        if close > sma_200:
            trend_score += 10
            trend_signals.append(f"Above 200 SMA (long-term bull)")
        else:
            trend_score -= 10
            trend_signals.append(f"Below 200 SMA (long-term bear)")
        
        # Classify trend
        if trend_score >= 15:
            trend = "Strong Bullish"
        elif trend_score >= 5:
            trend = "Bullish"
        elif trend_score <= -15:
            trend = "Strong Bearish"
        elif trend_score <= -5:
            trend = "Bearish"
        else:
            trend = "Neutral/Sideways"
        
        return {
            "trend": trend,
            "score": trend_score,
            "signals": trend_signals
        }
    
    def analyze_momentum(self, snapshot: dict) -> dict:
        """Analyze momentum using RSI and MACD"""
        indicators = snapshot['indicators']
        
        rsi = indicators.get('rsi', 50)
        macd = indicators.get('macd', 0)
        macds = indicators.get('macds', 0)
        macdh = indicators.get('macdh', 0)
        
        momentum_score = 0
        momentum_signals = []
        
        # RSI Analysis
        if rsi < 30:
            momentum_score += 20
            momentum_signals.append(f"RSI oversold ({rsi:.1f}) - bullish reversal signal")
        elif rsi < 40:
            momentum_score += 10
            momentum_signals.append(f"RSI low ({rsi:.1f}) - building upside momentum")
        elif rsi > 70:
            momentum_score -= 20
            momentum_signals.append(f"RSI overbought ({rsi:.1f}) - bearish reversal risk")
        elif rsi > 60:
            momentum_score += 5
            momentum_signals.append(f"RSI bullish ({rsi:.1f}) - strong momentum")
        elif rsi > 40 and rsi < 60:
            momentum_signals.append(f"RSI neutral ({rsi:.1f})")
        
        # MACD Analysis
        if macdh > 0:
            if macdh > 2:
                momentum_score += 15
                momentum_signals.append(f"Strong MACD bullish crossover (histogram: {macdh:.2f})")
            else:
                momentum_score += 10
                momentum_signals.append(f"MACD bullish crossover (histogram: {macdh:.2f})")
        else:
            if macdh < -2:
                momentum_score -= 15
                momentum_signals.append(f"Strong MACD bearish crossover (histogram: {macdh:.2f})")
            else:
                momentum_score -= 10
                momentum_signals.append(f"MACD bearish crossover (histogram: {macdh:.2f})")
        
        # Momentum classification
        if momentum_score >= 20:
            momentum = "Very Strong"
        elif momentum_score >= 10:
            momentum = "Strong"
        elif momentum_score <= -20:
            momentum = "Very Weak"
        elif momentum_score <= -10:
            momentum = "Weak"
        else:
            momentum = "Neutral"
        
        return {
            "momentum": momentum,
            "score": momentum_score,
            "rsi": rsi,
            "macd_histogram": macdh,
            "signals": momentum_signals
        }
    
    def analyze_volatility(self, snapshot: dict) -> dict:
        """Analyze volatility using Bollinger Bands and ATR"""
        indicators = snapshot['indicators']
        close = snapshot['close']
        
        boll_ub = indicators.get('boll_ub', close * 1.05)
        boll_lb = indicators.get('boll_lb', close * 0.95)
        boll_mid = indicators.get('boll', close)
        atr = indicators.get('atr', 0)
        
        volatility_score = 0
        volatility_signals = []
        
        # Bollinger Band position
        band_width = boll_ub - boll_lb
        position_in_band = (close - boll_lb) / band_width if band_width > 0 else 0.5
        
        if position_in_band > 0.9:
            volatility_score -= 10
            volatility_signals.append(f"Near upper Bollinger Band ({position_in_band*100:.0f}% position) - overbought")
        elif position_in_band > 0.7:
            volatility_score += 5
            volatility_signals.append(f"Upper band zone ({position_in_band*100:.0f}%) - strong upside")
        elif position_in_band < 0.1:
            volatility_score += 10
            volatility_signals.append(f"Near lower Bollinger Band ({position_in_band*100:.0f}% position) - oversold")
        elif position_in_band < 0.3:
            volatility_score -= 5
            volatility_signals.append(f"Lower band zone ({position_in_band*100:.0f}%) - weak")
        else:
            volatility_signals.append(f"Mid-band ({position_in_band*100:.0f}% position)")
        
        # ATR analysis
        atr_pct = (atr / close * 100) if close > 0 else 0
        if atr_pct > 3:
            volatility_signals.append(f"High volatility (ATR: {atr_pct:.1f}%) - larger stops needed")
        elif atr_pct > 1.5:
            volatility_signals.append(f"Moderate volatility (ATR: {atr_pct:.1f}%)")
        else:
            volatility_signals.append(f"Low volatility (ATR: {atr_pct:.1f}%) - tight range")
        
        return {
            "volatility": "High" if atr_pct > 3 else "Moderate" if atr_pct > 1.5 else "Low",
            "score": volatility_score,
            "atr_percent": atr_pct,
            "bb_position": position_in_band,
            "signals": volatility_signals
        }
    
    def analyze_volume(self, snapshot: dict) -> dict:
        """Analyze volume patterns"""
        indicators = snapshot['indicators']
        volume = snapshot['volume']
        vwma = indicators.get('vwma', 0)
        close = snapshot['close']
        
        volume_score = 0
        volume_signals = []
        
        # Price vs VWMA
        if close > vwma and vwma > 0:
            volume_score += 10
            volume_signals.append(f"Price above VWMA ({close:.2f} > {vwma:.2f}) - buying pressure")
        elif close < vwma and vwma > 0:
            volume_score -= 10
            volume_signals.append(f"Price below VWMA ({close:.2f} < {vwma:.2f}) - selling pressure")
        
        # Volume interpretation
        if volume > 10000000:
            volume_signals.append(f"High volume ({volume:,}) - institutional participation")
        elif volume > 5000000:
            volume_signals.append(f"Moderate volume ({volume:,})")
        else:
            volume_signals.append(f"Low volume ({volume:,}) - limited interest")
        
        return {
            "volume_pressure": "Bullish" if volume_score > 0 else "Bearish" if volume_score < 0 else "Neutral",
            "score": volume_score,
            "signals": volume_signals
        }
    
    def generate_report(self, ticker: str, snapshot: dict) -> str:
        """Generate comprehensive technical analysis report"""
        
        # Run all analyses
        trend_analysis = self.analyze_trend(snapshot)
        momentum_analysis = self.analyze_momentum(snapshot)
        volatility_analysis = self.analyze_volatility(snapshot)
        volume_analysis = self.analyze_volume(snapshot)
        
        # Calculate total score
        total_score = (
            trend_analysis['score'] +
            momentum_analysis['score'] +
            volatility_analysis['score'] +
            volume_analysis['score']
        )
        
        # Normalize to 0-100
        self.score = max(0, min(100, 50 + total_score))
        
        # Determine signal
        if self.score >= 70:
            signal = "STRONG BUY"
            self.confidence = 0.8
        elif self.score >= 60:
            signal = "BUY"
            self.confidence = 0.7
        elif self.score <= 30:
            signal = "STRONG SELL"
            self.confidence = 0.8
        elif self.score <= 40:
            signal = "SELL"
            self.confidence = 0.7
        else:
            signal = "HOLD"
            self.confidence = 0.5
        
        # Build report
        close = snapshot['close']
        indicators = snapshot['indicators']
        
        report = f"""# Technical Analysis Report: {ticker}

**Current Price**: ₹{close:.2f}
**Overall Signal**: {signal}
**Technical Score**: {self.score:.0f}/100
**Confidence**: {self.confidence*100:.0f}%

---

## Trend Analysis
**Classification**: {trend_analysis['trend']}
**Score**: {trend_analysis['score']:+d}/25

Key Observations:
"""
        for signal in trend_analysis['signals']:
            report += f"- {signal}\n"
        
        report += f"""
---

## Momentum Analysis
**Classification**: {momentum_analysis['momentum']}
**Score**: {momentum_analysis['score']:+d}/35

RSI: {momentum_analysis['rsi']:.1f}
MACD Histogram: {momentum_analysis['macd_histogram']:.2f}

Key Observations:
"""
        for signal in momentum_analysis['signals']:
            report += f"- {signal}\n"
        
        report += f"""
---

## Volatility & Range Analysis
**Classification**: {volatility_analysis['volatility']}
**Score**: {volatility_analysis['score']:+d}/20

ATR: {volatility_analysis['atr_percent']:.2f}%
Bollinger Band Position: {volatility_analysis['bb_position']*100:.0f}%

Key Observations:
"""
        for signal in volatility_analysis['signals']:
            report += f"- {signal}\n"
        
        report += f"""
---

## Volume Analysis
**Pressure**: {volume_analysis['volume_pressure']}
**Score**: {volume_analysis['score']:+d}/10

Key Observations:
"""
        for signal in volume_analysis['signals']:
            report += f"- {signal}\n"
        
        # Add summary table
        report += f"""
---

## Summary Table

| Metric | Value | Score | Status |
|--------|-------|-------|--------|
| **Trend** | {trend_analysis['trend']} | {trend_analysis['score']:+d}/25 | {'🟢' if trend_analysis['score'] > 0 else '🔴' if trend_analysis['score'] < 0 else '⚪'} |
| **Momentum** | {momentum_analysis['momentum']} | {momentum_analysis['score']:+d}/35 | {'🟢' if momentum_analysis['score'] > 0 else '🔴' if momentum_analysis['score'] < 0 else '⚪'} |
| **RSI** | {momentum_analysis['rsi']:.1f} | - | {'🟢' if momentum_analysis['rsi'] < 40 else '🔴' if momentum_analysis['rsi'] > 70 else '⚪'} |
| **Volatility** | {volatility_analysis['volatility']} | {volatility_analysis['score']:+d}/20 | {'🟢' if volatility_analysis['score'] > 0 else '🔴' if volatility_analysis['score'] < 0 else '⚪'} |
| **Volume** | {volume_analysis['volume_pressure']} | {volume_analysis['score']:+d}/10 | {'🟢' if volume_analysis['score'] > 0 else '🔴' if volume_analysis['score'] < 0 else '⚪'} |
| **TOTAL** | **{signal}** | **{self.score:.0f}/100** | {'🟢 BULLISH' if self.score >= 60 else '🔴 BEARISH' if self.score <= 40 else '⚪ NEUTRAL'} |

---

## Technical Levels

- **Support Levels**: ₹{indicators.get('boll_lb', close*0.95):.2f} (BB Lower), ₹{indicators.get('close_50_sma', close*0.97):.2f} (SMA50)
- **Resistance Levels**: ₹{indicators.get('boll_ub', close*1.05):.2f} (BB Upper), ₹{indicators.get('close_200_sma', close*1.03):.2f} (SMA200)
- **ATR (14)**: ₹{indicators.get('atr', close*0.02):.2f} ({volatility_analysis['atr_percent']:.2f}% of price)

---

*Analysis generated using rule-based Python engine. No LLM tokens used.*
"""
        
        return report


def create_market_analyst_optimized():
    """
    Factory function to create optimized market analyst node
    Compatible with existing LangGraph architecture
    """
    
    def market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["messages"][0].content if state["messages"] else "UNKNOWN"
        
        # Get market data (same as before)
        try:
            snapshot = build_verified_market_snapshot(
                symbol=ticker,
                curr_date=current_date,
                look_back_days=30
            )
            
            # Parse snapshot into structured format
            snapshot_data = {
                "close": snapshot.get('latest_close', 0),
                "volume": snapshot.get('latest_volume', 0),
                "indicators": snapshot.get('indicators', {})
            }
            
            # Run Python-based analysis
            analyzer = TechnicalAnalyzer()
            report = analyzer.generate_report(ticker, snapshot_data)
            
            # Return AIMessage for compatibility with LangChain
            result = AIMessage(content=report)
            
            return {
                "messages": [result],
                "market_report": report,
            }
            
        except Exception as e:
            error_report = f"Technical analysis failed: {str(e)}"
            result = AIMessage(content=error_report)
            return {
                "messages": [result],
                "market_report": error_report,
            }
    
    return market_analyst_node
