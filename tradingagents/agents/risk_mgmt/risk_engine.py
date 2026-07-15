"""
Risk Engine for TradingAgents

Main coordinator for risk analysis and position sizing.
Replaces 3 LLM-based risk agents with deterministic Python calculations.

Performance:
- 0 LLM calls (vs 3 agents)
- ~0 tokens (vs ~3,900 tokens)
- <0.5s runtime (vs ~30-40s)
- $0 cost (vs ~$0.0025)
"""

import re
from typing import Dict, Any, Optional, List

from langchain_core.messages import AIMessage

from .risk_profiles import (
    get_all_profiles,
    recommend_profile,
    RiskProfile
)
from .position_calculator import PositionCalculator
from .risk_formatter import RiskFormatter


class RiskEngine:
    """
    Python-based risk engine for TradingAgents.
    
    Calculates position sizing and risk management parameters
    across three risk profiles (aggressive, neutral, conservative).
    
    Provides structured risk data to Portfolio Manager while
    maintaining compatibility with original debate-style interface.
    """
    
    def __init__(
        self,
        capital: float = 200000,
        max_risk_per_trade: float = 4000
    ):
        """
        Initialize risk engine.
        
        Args:
            capital: Total capital (₹)
            max_risk_per_trade: Maximum risk per trade (₹)
        """
        self.calculator = PositionCalculator(
            capital=capital,
            max_risk_per_trade=max_risk_per_trade
        )
        self.formatter = RiskFormatter()
        self.profiles = get_all_profiles()
    
    def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method - analyzes trader proposal and calculates risk.
        
        Args:
            state: Workflow state containing trader proposal and analysis
            
        Returns:
            dict: risk_debate_state for Portfolio Manager
        """
        try:
            # Extract inputs from state
            inputs = self._extract_inputs(state)
            
            if not inputs:
                return self.formatter.format_error(
                    "Unable to extract required inputs from trader proposal"
                )
            
            # Calculate position for each profile
            profiles_data = {}
            for profile_name, profile in self.profiles.items():
                position = self.calculator.calculate_position(
                    entry_price=inputs['entry_price'],
                    stop_loss=inputs['stop_loss'],
                    target=inputs['target'],
                    profile=profile,
                    atr=inputs.get('atr')
                )
                
                if position:
                    profiles_data[profile_name] = position
            
            # If no valid positions calculated, return error
            if not profiles_data:
                return self.formatter.format_error(
                    "Unable to calculate valid position sizing for any profile"
                )
            
            # Generate risk and supporting factors
            risk_factors = self._generate_risk_factors(inputs)
            supporting_factors = self._generate_supporting_factors(inputs)
            
            # Recommend profile based on confidence
            recommended = recommend_profile(
                confidence=inputs.get('confidence', 0.5),
                trend_strength=inputs.get('trend_strength', 0.5)
            )
            
            # Format for Portfolio Manager
            capital_summary = self.calculator.get_capital_summary()
            
            return self.formatter.format_for_portfolio_manager(
                profiles_data=profiles_data,
                risk_factors=risk_factors,
                supporting_factors=supporting_factors,
                recommended_profile=recommended,
                trader_plan=inputs['trader_plan'],
                capital_summary=capital_summary
            )
            
        except Exception as e:
            return self.formatter.format_error(str(e))
    
    def _extract_inputs(self, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract necessary inputs from workflow state.
        
        Args:
            state: Workflow state
            
        Returns:
            dict: Extracted inputs or None if extraction fails
        """
        try:
            # Get trader proposal
            trader_plan = state.get("trader_investment_plan", "")
            
            if not trader_plan:
                return None
            
            # Extract action
            action = self._extract_action(trader_plan)
            
            # Extract prices
            entry_price = self._extract_entry_price(trader_plan, state)
            stop_loss = self._extract_stop_loss(trader_plan, state)
            target = self._extract_target(trader_plan, entry_price)
            
            # Extract market context
            market_report = state.get("market_report", {})
            atr = None
            trend_strength = 0.5
            
            if isinstance(market_report, dict):
                indicators = market_report.get("indicators", {})
                atr = indicators.get("atr")
                trend_strength = market_report.get("trend_strength", 0.5)
            
            # Extract fundamental context
            fundamentals_report = state.get("fundamentals_report", {})
            fundamental_score = 0.5
            
            if isinstance(fundamentals_report, dict):
                fundamental_score = fundamentals_report.get("overall_score", 0.5)
            
            # Calculate aggregate confidence
            confidence = (trend_strength + fundamental_score) / 2
            
            return {
                "action": action,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "target": target,
                "atr": atr,
                "trend_strength": trend_strength,
                "fundamental_score": fundamental_score,
                "confidence": confidence,
                "trader_plan": trader_plan
            }
            
        except Exception as e:
            return None
    
    def _extract_action(self, trader_plan: str) -> str:
        """Extract action (Buy/Hold/Sell) from trader plan"""
        plan_upper = trader_plan.upper()
        
        if "BUY" in plan_upper:
            return "Buy"
        elif "SELL" in plan_upper:
            return "Sell"
        else:
            return "Hold"
    
    def _extract_entry_price(self, trader_plan: str, state: Dict) -> float:
        """Extract entry price from trader plan or market data"""
        # Try to extract from trader plan
        match = re.search(r"\*?\*?entry\*?\*?[:\s]+\*?\*?price\*?\*?[:\s]+₹?(\d+[,\.]?\d*)", trader_plan, re.IGNORECASE)
        if match:
            price_str = match.group(1).replace(',', '')
            return float(price_str)
        
        # Fall back to current price from market data
        market_report = state.get("market_report", {})
        if isinstance(market_report, dict):
            indicators = market_report.get("indicators", {})
            current_price = indicators.get("close")
            if current_price:
                return float(current_price)
        
        # Default fallback
        return 1500.0
    
    def _extract_stop_loss(self, trader_plan: str, state: Dict) -> float:
        """Extract stop loss from trader plan"""
        # Try to extract from trader plan
        match = re.search(r"\*?\*?stop\*?\*?[:\s]+\*?\*?loss\*?\*?[:\s]+₹?(\d+[,\.]?\d*)", trader_plan, re.IGNORECASE)
        if match:
            stop_str = match.group(1).replace(',', '')
            return float(stop_str)
        
        # Calculate default stop (8% below entry)
        entry = self._extract_entry_price(trader_plan, state)
        return entry * 0.92
    
    def _extract_target(self, trader_plan: str, entry_price: float) -> float:
        """Extract target price from trader plan"""
        # Try to extract from trader plan (handle markdown formatting)
        match = re.search(r"\*?\*?target\*?\*?[:\s]+₹?(\d+[,\.]?\d*)", trader_plan, re.IGNORECASE)
        if match:
            # Remove commas from number
            target_str = match.group(1).replace(',', '')
            return float(target_str)
        
        # Default target (10% above entry)
        return entry_price * 1.10
    
    def _generate_risk_factors(self, context: Dict[str, Any]) -> List[str]:
        """
        Generate list of risk considerations.
        
        Args:
            context: Input context
            
        Returns:
            list: Risk factors
        """
        factors = []
        
        # Volatility risk
        if context.get("atr"):
            atr_percent = (context["atr"] / context["entry_price"]) * 100
            if atr_percent > 3:
                factors.append(f"High volatility (ATR: {atr_percent:.1f}%)")
            elif atr_percent < 1:
                factors.append(f"Low volatility (ATR: {atr_percent:.1f}%)")
            else:
                factors.append(f"Moderate volatility (ATR: {atr_percent:.1f}%)")
        
        # Stop loss distance
        stop_distance = abs(
            context["entry_price"] - context["stop_loss"]
        ) / context["entry_price"] * 100
        
        if stop_distance > 10:
            factors.append(f"Wide stop loss ({stop_distance:.1f}% from entry)")
        elif stop_distance < 3:
            factors.append(f"Tight stop loss ({stop_distance:.1f}% from entry)")
        
        # Confidence level
        confidence = context.get("confidence", 0.5)
        if confidence < 0.6:
            factors.append(f"Moderate confidence ({confidence:.2f})")
        
        # Action-specific risks
        if context["action"] == "Buy":
            factors.append("Long position - exposed to downside risk")
        elif context["action"] == "Sell":
            factors.append("Short position - exposed to upside risk")
        
        return factors
    
    def _generate_supporting_factors(self, context: Dict[str, Any]) -> List[str]:
        """
        Generate list of supporting considerations.
        
        Args:
            context: Input context
            
        Returns:
            list: Supporting factors
        """
        factors = []
        
        # Confidence
        confidence = context.get("confidence", 0.5)
        if confidence > 0.7:
            factors.append(f"Strong analyst confidence: {confidence:.2f}")
        elif confidence > 0.5:
            factors.append(f"Moderate analyst confidence: {confidence:.2f}")
        
        # Risk/Reward
        risk = abs(context["entry_price"] - context["stop_loss"])
        reward = abs(context["target"] - context["entry_price"])
        rr_ratio = reward / risk if risk > 0 else 0
        
        if rr_ratio >= 2.0:
            factors.append(f"Favorable risk/reward: {rr_ratio:.1f}:1")
        elif rr_ratio >= 1.5:
            factors.append(f"Acceptable risk/reward: {rr_ratio:.1f}:1")
        
        # Systematic approach
        factors.append("Systematic position sizing applied")
        factors.append("Capital preservation prioritized")
        
        return factors


def create_risk_engine():
    """
    Factory function to create risk engine node for LangGraph.
    
    Returns:
        callable: Risk engine node function
    """
    engine = RiskEngine()
    
    def risk_engine_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Risk engine node for LangGraph workflow.
        
        Args:
            state: Workflow state
            
        Returns:
            dict: Updated state with risk_debate_state
        """
        try:
            # Run risk analysis
            result = engine.analyze(state)
            
            return {
                "risk_debate_state": result
            }
            
        except Exception as e:
            # Return error state
            return {
                "risk_debate_state": engine.formatter.format_error(str(e))
            }
    
    return risk_engine_node
