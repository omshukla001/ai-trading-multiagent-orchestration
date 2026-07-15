"""
Risk Profiles for TradingAgents

Defines three risk profiles with different risk tolerances and allocation strategies.
Each profile specifies:
- Risk percentage per trade
- Maximum capital allocation
- Stop loss multiplier range (ATR-based)
- Target risk/reward ratio
"""

from dataclasses import dataclass


@dataclass
class RiskProfile:
    """Base class for risk profile configuration"""
    
    name: str
    risk_percent: float  # Percentage of capital to risk per trade
    max_allocation_percent: float  # Maximum percentage of capital per position
    stop_multiplier_range: tuple[float, float]  # ATR multiplier range for stops
    target_rr_ratio: float  # Minimum risk/reward ratio target
    
    def get_stop_multiplier(self) -> float:
        """Get average stop multiplier from range"""
        return (self.stop_multiplier_range[0] + self.stop_multiplier_range[1]) / 2
    
    def __repr__(self) -> str:
        return (
            f"{self.name}Profile("
            f"risk={self.risk_percent*100:.1f}%, "
            f"max_alloc={self.max_allocation_percent*100:.1f}%, "
            f"rr_target={self.target_rr_ratio}:1)"
        )


class AggressiveProfile(RiskProfile):
    """
    Aggressive risk profile for high-conviction trades.
    
    Characteristics:
    - Higher risk tolerance (2.0% per trade)
    - Larger position sizes (up to 25% of capital)
    - Wider stop losses (2-3 ATR)
    - Higher target returns (2.5:1 R:R)
    
    Best for:
    - Strong bullish/bearish setups
    - High-confidence technical patterns
    - Strong fundamental support
    - Favorable market conditions
    """
    
    def __init__(self):
        super().__init__(
            name="Aggressive",
            risk_percent=0.02,  # 2.0% risk
            max_allocation_percent=0.25,  # 25% max allocation
            stop_multiplier_range=(2.0, 3.0),  # 2-3 ATR stops
            target_rr_ratio=2.5  # 2.5:1 minimum R:R
        )


class NeutralProfile(RiskProfile):
    """
    Neutral/Balanced risk profile for standard trades.
    
    Characteristics:
    - Moderate risk tolerance (1.5% per trade)
    - Medium position sizes (up to 20% of capital)
    - Standard stop losses (1.5-2 ATR)
    - Balanced target returns (2.0:1 R:R)
    
    Best for:
    - Normal market conditions
    - Balanced technical setups
    - Moderate confidence levels
    - Standard swing trades
    """
    
    def __init__(self):
        super().__init__(
            name="Neutral",
            risk_percent=0.015,  # 1.5% risk
            max_allocation_percent=0.20,  # 20% max allocation
            stop_multiplier_range=(1.5, 2.0),  # 1.5-2 ATR stops
            target_rr_ratio=2.0  # 2.0:1 minimum R:R
        )


class ConservativeProfile(RiskProfile):
    """
    Conservative risk profile for cautious trades.
    
    Characteristics:
    - Lower risk tolerance (1.0% per trade)
    - Smaller position sizes (up to 12.5% of capital)
    - Tight stop losses (1-1.5 ATR)
    - Conservative target returns (1.75:1 R:R)
    
    Best for:
    - Uncertain market conditions
    - Lower confidence setups
    - Risk management priority
    - Capital preservation focus
    """
    
    def __init__(self):
        super().__init__(
            name="Conservative",
            risk_percent=0.01,  # 1.0% risk
            max_allocation_percent=0.125,  # 12.5% max allocation
            stop_multiplier_range=(1.0, 1.5),  # 1-1.5 ATR stops
            target_rr_ratio=1.75  # 1.75:1 minimum R:R
        )


def get_all_profiles() -> dict[str, RiskProfile]:
    """
    Get all available risk profiles.
    
    Returns:
        dict: Mapping of profile name to profile instance
    """
    return {
        "aggressive": AggressiveProfile(),
        "neutral": NeutralProfile(),
        "conservative": ConservativeProfile()
    }


def get_profile_by_name(name: str) -> RiskProfile:
    """
    Get a risk profile by name.
    
    Args:
        name: Profile name (case-insensitive)
        
    Returns:
        RiskProfile: The requested profile
        
    Raises:
        ValueError: If profile name is not recognized
    """
    profiles = get_all_profiles()
    name_lower = name.lower()
    
    if name_lower not in profiles:
        available = ", ".join(profiles.keys())
        raise ValueError(
            f"Unknown profile '{name}'. Available profiles: {available}"
        )
    
    return profiles[name_lower]


def recommend_profile(confidence: float, trend_strength: float) -> str:
    """
    Recommend a risk profile based on analysis confidence and trend strength.
    
    Args:
        confidence: Overall analysis confidence (0.0-1.0)
        trend_strength: Market trend strength (0.0-1.0)
        
    Returns:
        str: Recommended profile name
    """
    # Calculate combined score
    score = (confidence + trend_strength) / 2
    
    if score >= 0.75:
        return "aggressive"
    elif score >= 0.50:
        return "neutral"
    else:
        return "conservative"
