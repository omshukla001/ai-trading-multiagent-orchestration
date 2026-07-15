"""
Risk Formatter for TradingAgents

Formats risk analysis results for Portfolio Manager consumption.
Provides both:
1. Structured data (for programmatic use)
2. Textual narratives (for compatibility with debate-style agents)
"""

from typing import Dict, List, Any


class RiskFormatter:
    """
    Format risk analysis for Portfolio Manager consumption.
    
    Maintains compatibility with original risk debate agents while
    providing structured risk data.
    """
    
    def format_for_portfolio_manager(
        self,
        profiles_data: Dict[str, Dict[str, Any]],
        risk_factors: List[str],
        supporting_factors: List[str],
        recommended_profile: str,
        trader_plan: str,
        capital_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format complete risk analysis for Portfolio Manager.
        
        Args:
            profiles_data: Risk calculations for all profiles
            risk_factors: List of risk considerations
            supporting_factors: List of supporting factors
            recommended_profile: Recommended profile name
            trader_plan: Original trader proposal
            capital_summary: Capital and limits summary
            
        Returns:
            dict: Formatted risk_debate_state
        """
        # Generate narratives for each profile
        aggressive_narrative = self._generate_profile_narrative(
            "aggressive",
            profiles_data.get("aggressive", {}),
            trader_plan
        )
        
        neutral_narrative = self._generate_profile_narrative(
            "neutral",
            profiles_data.get("neutral", {}),
            trader_plan
        )
        
        conservative_narrative = self._generate_profile_narrative(
            "conservative",
            profiles_data.get("conservative", {}),
            trader_plan
        )
        
        # Generate combined history (as string for backward compatibility)
        history_text = self._generate_combined_history(
            aggressive_narrative,
            neutral_narrative,
            conservative_narrative,
            risk_factors,
            supporting_factors
        )
        
        return {
            "history": [history_text],  # Wrap in list for compatibility
            "aggressive_history": aggressive_narrative,
            "conservative_history": conservative_narrative,
            "neutral_history": neutral_narrative,
            "current_aggressive_response": aggressive_narrative,
            "current_conservative_response": conservative_narrative,
            "current_neutral_response": neutral_narrative,
            "latest_speaker": "Risk Engine",
            "count": 1,  # Always 1 (no debate rounds)
            
            # NEW: Structured data for PM
            "risk_analysis": {
                "profiles": profiles_data,
                "risk_factors": risk_factors,
                "supporting_factors": supporting_factors,
                "recommended_profile": recommended_profile,
                "capital_summary": capital_summary
            }
        }
    
    def _generate_profile_narrative(
        self,
        profile_name: str,
        data: Dict[str, Any],
        trader_plan: str
    ) -> str:
        """
        Generate debate-style narrative for a risk profile.
        
        Args:
            profile_name: Profile name
            data: Position calculation results
            trader_plan: Trader's proposal
            
        Returns:
            str: Formatted narrative
        """
        if not data:
            return f"{profile_name.title()} Risk Analyst: Unable to calculate position for this setup."
        
        # Calculate gains for targets
        entry = data['entry_price']
        target = data.get('target', entry)
        target_gain = ((target / entry - 1) * 100) if entry > 0 else 0
        
        # Format allocation with Indian numbering
        allocation_str = f"₹{data['allocation']:,.0f}"
        risk_str = f"₹{data['risk_amount']:,.0f}"
        max_loss_str = f"₹{data['max_loss']:,.0f}"
        
        narrative = f"""{profile_name.title()} Risk Analyst:

Based on the trader's proposal, here is my {profile_name} risk assessment:

**Position Sizing:**
- Recommended Allocation: {allocation_str}
- Quantity: {data['quantity']} shares
- Entry Price: ₹{data['entry_price']}
- Stop Loss: ₹{data['stop_loss']}

**Risk Metrics:**
- Risk Amount: {risk_str} ({data['risk_percent']:.1f}% of capital)
- Maximum Loss: {max_loss_str}
- Risk/Reward Ratio: {data['rr_ratio']:.2f}:1

**Targets:**
- Target: ₹{target} ({target_gain:+.1f}% from entry)

**Rationale:**
This {profile_name} approach balances {"aggressive growth potential" if profile_name == "aggressive" else "conservative capital preservation" if profile_name == "conservative" else "moderate risk-taking"} with prudent risk management. The position size ensures we risk no more than {data['risk_percent']:.1f}% of capital while maintaining a {'favorable' if data['rr_ratio'] >= 2.0 else 'reasonable'} {data['rr_ratio']:.2f}:1 risk/reward ratio.

{'This aggressive stance is justified for high-conviction setups where the potential upside significantly outweighs the downside risk.' if profile_name == 'aggressive' else ''}
{'This conservative approach prioritizes capital protection, suitable when market conditions are uncertain or conviction is moderate.' if profile_name == 'conservative' else ''}
{'This balanced approach offers a middle ground, appropriate for standard swing trading setups with moderate confidence.' if profile_name == 'neutral' else ''}
"""
        return narrative.strip()
    
    def _generate_combined_history(
        self,
        aggressive: str,
        neutral: str,
        conservative: str,
        risk_factors: List[str],
        supporting_factors: List[str]
    ) -> str:
        """
        Generate combined debate history.
        
        Args:
            aggressive: Aggressive narrative
            neutral: Neutral narrative
            conservative: Conservative narrative
            risk_factors: Risk considerations
            supporting_factors: Supporting considerations
            
        Returns:
            str: Combined history
        """
        risk_section = "\n".join(f"• {factor}" for factor in risk_factors)
        support_section = "\n".join(f"• {factor}" for factor in supporting_factors)
        
        history = f"""Risk Engine Analysis Summary:

The Python Risk Engine has calculated position sizing for three risk profiles, providing quantitative risk management without LLM inference.

**Risk Considerations:**
{risk_section}

**Supporting Factors:**
{support_section}

---

{aggressive}

---

{neutral}

---

{conservative}

---

All three profiles maintain proper risk/reward ratios and respect capital allocation limits. The Portfolio Manager should select the appropriate profile based on conviction level and market conditions.
"""
        return history.strip()
    
    def format_error(self, error_message: str) -> Dict[str, Any]:
        """
        Format error message for Portfolio Manager.
        
        Args:
            error_message: Error description
            
        Returns:
            dict: Formatted error state
        """
        return {
            "history": f"Risk Engine Error: {error_message}",
            "aggressive_history": "",
            "conservative_history": "",
            "neutral_history": "",
            "current_aggressive_response": "",
            "current_conservative_response": "",
            "current_neutral_response": "",
            "latest_speaker": "Risk Engine",
            "count": 1,
            "error": error_message
        }
