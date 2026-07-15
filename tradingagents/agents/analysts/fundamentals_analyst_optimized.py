"""
Optimized Fundamentals Analyst - Pure Python Implementation
NO LLM USAGE - Deterministic rule-based analysis
Calculates financial ratios and generates scoring without LLM
"""

from langchain_core.messages import AIMessage
from tradingagents.agents.utils.agent_utils import get_fundamentals


class FundamentalsAnalyzer:
    """
    Pure Python fundamental analysis engine
    Replaces LLM-based interpretation with rule-based scoring
    """
    
    def __init__(self):
        self.score = 50  # Neutral baseline
        self.rating = "Neutral"
    
    def analyze_valuation(self, data: dict) -> dict:
        """Analyze valuation metrics"""
        score = 0
        signals = []
        
        pe_ratio = data.get('pe_ratio')
        forward_pe = data.get('forward_pe')
        peg_ratio = data.get('peg_ratio')
        price_to_book = data.get('price_to_book')
        
        # P/E Analysis
        if pe_ratio and pe_ratio > 0:
            if pe_ratio < 15:
                score += 15
                signals.append(f"Attractive P/E ({pe_ratio:.1f}) - undervalued")
            elif pe_ratio < 25:
                score += 5
                signals.append(f"Reasonable P/E ({pe_ratio:.1f})")
            elif pe_ratio < 40:
                score -= 5
                signals.append(f"High P/E ({pe_ratio:.1f}) - elevated valuation")
            else:
                score -= 15
                signals.append(f"Very high P/E ({pe_ratio:.1f}) - overvalued")
        
        # PEG Ratio (Price/Earnings to Growth)
        if peg_ratio and peg_ratio > 0:
            if peg_ratio < 1.0:
                score += 10
                signals.append(f"Excellent PEG ({peg_ratio:.2f}) - growth undervalued")
            elif peg_ratio < 1.5:
                score += 5
                signals.append(f"Good PEG ({peg_ratio:.2f}) - fair growth value")
            elif peg_ratio > 2.0:
                score -= 10
                signals.append(f"High PEG ({peg_ratio:.2f}) - growth overvalued")
        
        # Price to Book
        if price_to_book and price_to_book > 0:
            if price_to_book < 1.5:
                score += 5
                signals.append(f"Low P/B ({price_to_book:.2f}) - asset-backed value")
            elif price_to_book > 5:
                score -= 5
                signals.append(f"High P/B ({price_to_book:.2f}) - premium valuation")
        
        return {
            "score": score,
            "signals": signals,
            "metrics": {
                "pe_ratio": pe_ratio,
                "forward_pe": forward_pe,
                "peg_ratio": peg_ratio,
                "price_to_book": price_to_book
            }
        }
    
    def analyze_profitability(self, data: dict) -> dict:
        """Analyze profitability metrics"""
        score = 0
        signals = []
        
        profit_margin = data.get('profit_margin', 0) * 100  # Convert to percentage
        operating_margin = data.get('operating_margin', 0) * 100
        roe = data.get('return_on_equity', 0) * 100
        roa = data.get('return_on_assets', 0) * 100
        
        # Profit Margin
        if profit_margin > 20:
            score += 15
            signals.append(f"Excellent profit margin ({profit_margin:.1f}%)")
        elif profit_margin > 10:
            score += 10
            signals.append(f"Good profit margin ({profit_margin:.1f}%)")
        elif profit_margin > 5:
            score += 5
            signals.append(f"Moderate profit margin ({profit_margin:.1f}%)")
        elif profit_margin < 0:
            score -= 15
            signals.append(f"Negative profit margin ({profit_margin:.1f}%) - unprofitable")
        else:
            score -= 5
            signals.append(f"Low profit margin ({profit_margin:.1f}%)")
        
        # Return on Equity
        if roe > 20:
            score += 10
            signals.append(f"Strong ROE ({roe:.1f}%) - efficient capital use")
        elif roe > 15:
            score += 5
            signals.append(f"Good ROE ({roe:.1f}%)")
        elif roe < 10:
            score -= 5
            signals.append(f"Low ROE ({roe:.1f}%)")
        
        # Operating Margin
        if operating_margin > 20:
            signals.append(f"Strong operating efficiency ({operating_margin:.1f}%)")
        elif operating_margin < 5:
            signals.append(f"Weak operating efficiency ({operating_margin:.1f}%)")
        
        return {
            "score": score,
            "signals": signals,
            "metrics": {
                "profit_margin": profit_margin,
                "operating_margin": operating_margin,
                "roe": roe,
                "roa": roa
            }
        }
    
    def analyze_growth(self, data: dict, quarterly_data: dict = None) -> dict:
        """Analyze growth metrics"""
        score = 0
        signals = []
        
        # Annual revenue (TTM)
        revenue = data.get('revenue_ttm', 0)
        eps = data.get('eps_ttm', 0)
        forward_eps = data.get('forward_eps', 0)
        
        # Calculate growth if quarterly data available
        revenue_growth = 0
        eps_growth = 0
        
        if quarterly_data:
            # This would calculate YoY growth from quarterly data
            # For now, estimate from forward metrics
            pass
        
        # Estimate growth from forward EPS
        if eps and forward_eps and eps > 0:
            eps_growth = ((forward_eps / eps) - 1) * 100
            
            if eps_growth > 20:
                score += 15
                signals.append(f"Strong earnings growth expected ({eps_growth:.1f}%)")
            elif eps_growth > 10:
                score += 10
                signals.append(f"Good earnings growth expected ({eps_growth:.1f}%)")
            elif eps_growth > 0:
                score += 5
                signals.append(f"Moderate earnings growth expected ({eps_growth:.1f}%)")
            else:
                score -= 10
                signals.append(f"Earnings decline expected ({eps_growth:.1f}%)")
        
        # Revenue scale
        if revenue > 1e13:  # > ₹10 trillion
            signals.append(f"Mega-cap company (₹{revenue/1e12:.1f}T revenue)")
        elif revenue > 1e12:  # > ₹1 trillion
            signals.append(f"Large-cap company (₹{revenue/1e12:.2f}T revenue)")
        
        return {
            "score": score,
            "signals": signals,
            "metrics": {
                "revenue_ttm": revenue,
                "eps_ttm": eps,
                "forward_eps": forward_eps,
                "estimated_eps_growth": eps_growth
            }
        }
    
    def analyze_financial_health(self, data: dict) -> dict:
        """Analyze financial health and leverage"""
        score = 0
        signals = []
        
        debt_to_equity = data.get('debt_to_equity', 0)
        current_ratio = data.get('current_ratio', 0)
        free_cash_flow = data.get('free_cash_flow', 0)
        
        # Debt to Equity
        if debt_to_equity < 0.3:
            score += 10
            signals.append(f"Very low debt (D/E: {debt_to_equity:.2f}) - strong balance sheet")
        elif debt_to_equity < 0.7:
            score += 5
            signals.append(f"Low debt (D/E: {debt_to_equity:.2f}) - healthy leverage")
        elif debt_to_equity < 1.5:
            signals.append(f"Moderate debt (D/E: {debt_to_equity:.2f})")
        elif debt_to_equity < 3:
            score -= 5
            signals.append(f"High debt (D/E: {debt_to_equity:.2f}) - financial risk")
        else:
            score -= 10
            signals.append(f"Very high debt (D/E: {debt_to_equity:.2f}) - significant risk")
        
        # Current Ratio (Liquidity)
        if current_ratio > 2:
            score += 5
            signals.append(f"Strong liquidity (CR: {current_ratio:.2f})")
        elif current_ratio > 1.2:
            signals.append(f"Adequate liquidity (CR: {current_ratio:.2f})")
        elif current_ratio < 1:
            score -= 10
            signals.append(f"Weak liquidity (CR: {current_ratio:.2f}) - short-term risk")
        
        # Free Cash Flow
        if free_cash_flow > 1e11:  # > ₹100B
            score += 10
            signals.append(f"Strong FCF (₹{free_cash_flow/1e9:.0f}B) - self-funding growth")
        elif free_cash_flow > 0:
            score += 5
            signals.append(f"Positive FCF (₹{free_cash_flow/1e9:.1f}B)")
        else:
            score -= 5
            signals.append(f"Negative FCF (₹{free_cash_flow/1e9:.1f}B) - burning cash")
        
        return {
            "score": score,
            "signals": signals,
            "metrics": {
                "debt_to_equity": debt_to_equity,
                "current_ratio": current_ratio,
                "free_cash_flow": free_cash_flow
            }
        }
    
    def generate_report(self, ticker: str, data: dict) -> str:
        """Generate comprehensive fundamentals analysis report"""
        
        # Run all analyses
        valuation = self.analyze_valuation(data)
        profitability = self.analyze_profitability(data)
        growth = self.analyze_growth(data)
        health = self.analyze_financial_health(data)
        
        # Calculate total score
        total_score = (
            valuation['score'] +
            profitability['score'] +
            growth['score'] +
            health['score']
        )
        
        # Normalize to 0-100
        self.score = max(0, min(100, 50 + total_score))
        
        # Determine rating
        if self.score >= 80:
            self.rating = "Strong Buy"
        elif self.score >= 65:
            self.rating = "Buy"
        elif self.score >= 50:
            self.rating = "Hold"
        elif self.score >= 35:
            self.rating = "Sell"
        else:
            self.rating = "Strong Sell"
        
        # Build report
        company_name = data.get('name', ticker)
        sector = data.get('sector', 'Unknown')
        industry = data.get('industry', 'Unknown')
        market_cap = data.get('market_cap', 0)
        
        report = f"""# Fundamental Analysis Report: {ticker}

**Company**: {company_name}
**Sector**: {sector}
**Industry**: {industry}
**Market Cap**: ₹{market_cap/1e12:.2f} Trillion

**Overall Rating**: {self.rating}
**Fundamental Score**: {self.score:.0f}/100

---

## Valuation Analysis
**Score**: {valuation['score']:+d}/35

Key Metrics:
- P/E Ratio: {valuation['metrics']['pe_ratio']:.1f} (Forward: {valuation['metrics']['forward_pe']:.1f})
- PEG Ratio: {valuation['metrics']['peg_ratio']:.2f}
- Price/Book: {valuation['metrics']['price_to_book']:.2f}

Observations:
"""
        for signal in valuation['signals']:
            report += f"- {signal}\n"
        
        report += f"""
---

## Profitability Analysis
**Score**: {profitability['score']:+d}/30

Key Metrics:
- Profit Margin: {profitability['metrics']['profit_margin']:.1f}%
- Operating Margin: {profitability['metrics']['operating_margin']:.1f}%
- Return on Equity: {profitability['metrics']['roe']:.1f}%

Observations:
"""
        for signal in profitability['signals']:
            report += f"- {signal}\n"
        
        report += f"""
---

## Growth Analysis
**Score**: {growth['score']:+d}/20

Key Metrics:
- TTM Revenue: ₹{growth['metrics']['revenue_ttm']/1e12:.2f}T
- EPS (TTM): ₹{growth['metrics']['eps_ttm']:.2f}
- Forward EPS: ₹{growth['metrics']['forward_eps']:.2f}
- Expected Growth: {growth['metrics']['estimated_eps_growth']:.1f}%

Observations:
"""
        for signal in growth['signals']:
            report += f"- {signal}\n"
        
        report += f"""
---

## Financial Health Analysis
**Score**: {health['score']:+d}/25

Key Metrics:
- Debt/Equity: {health['metrics']['debt_to_equity']:.2f}
- Current Ratio: {health['metrics']['current_ratio']:.2f}
- Free Cash Flow: ₹{health['metrics']['free_cash_flow']/1e9:.1f}B

Observations:
"""
        for signal in health['signals']:
            report += f"- {signal}\n"
        
        # Add summary table
        report += f"""
---

## Summary Table

| Category | Score | Status |
|----------|-------|--------|
| **Valuation** | {valuation['score']:+d}/35 | {'🟢' if valuation['score'] > 5 else '🔴' if valuation['score'] < -5 else '⚪'} |
| **Profitability** | {profitability['score']:+d}/30 | {'🟢' if profitability['score'] > 5 else '🔴' if profitability['score'] < -5 else '⚪'} |
| **Growth** | {growth['score']:+d}/20 | {'🟢' if growth['score'] > 5 else '🔴' if growth['score'] < -5 else '⚪'} |
| **Health** | {health['score']:+d}/25 | {'🟢' if health['score'] > 5 else '🔴' if health['score'] < -5 else '⚪'} |
| **TOTAL** | **{self.score:.0f}/100** | **{self.rating}** |

---

*Analysis generated using rule-based Python engine. No LLM tokens used.*
"""
        
        return report


def create_fundamentals_analyst_optimized():
    """
    Factory function to create optimized fundamentals analyst node
    Compatible with existing LangGraph architecture
    """
    
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["messages"][0].content if state["messages"] else "UNKNOWN"
        
        try:
            # Get fundamental data
            fund_data = get_fundamentals(ticker=ticker, curr_date=current_date)
            
            # Parse fundamental data
            data = {
                "name": fund_data.get('Name', ticker),
                "sector": fund_data.get('Sector', 'Unknown'),
                "industry": fund_data.get('Industry', 'Unknown'),
                "market_cap": fund_data.get('Market Cap', 0),
                "pe_ratio": fund_data.get('PE Ratio (TTM)'),
                "forward_pe": fund_data.get('Forward PE'),
                "peg_ratio": fund_data.get('PEG Ratio'),
                "price_to_book": fund_data.get('Price to Book'),
                "profit_margin": fund_data.get('Profit Margin'),
                "operating_margin": fund_data.get('Operating Margin'),
                "return_on_equity": fund_data.get('Return on Equity'),
                "return_on_assets": fund_data.get('Return on Assets'),
                "revenue_ttm": fund_data.get('Revenue (TTM)', 0),
                "eps_ttm": fund_data.get('EPS (TTM)'),
                "forward_eps": fund_data.get('Forward EPS'),
                "debt_to_equity": fund_data.get('Debt to Equity'),
                "current_ratio": fund_data.get('Current Ratio'),
                "free_cash_flow": fund_data.get('Free Cash Flow', 0),
            }
            
            # Run Python-based analysis
            analyzer = FundamentalsAnalyzer()
            report = analyzer.generate_report(ticker, data)
            
            # Return AIMessage for compatibility with LangChain
            result = AIMessage(content=report)
            
            return {
                "messages": [result],
                "fundamentals_report": report,
            }
            
        except Exception as e:
            error_report = f"Fundamental analysis failed: {str(e)}"
            result = AIMessage(content=error_report)
            return {
                "messages": [result],
                "fundamentals_report": error_report,
            }
    
    return fundamentals_analyst_node
