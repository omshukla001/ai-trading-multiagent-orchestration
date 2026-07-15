"""
Risk Management Module for TradingAgents

Python-based risk engine that replaces 3 LLM agents with deterministic calculations.

Components:
- RiskEngine: Main coordinator
- PositionCalculator: Position sizing calculations
- RiskProfiles: Risk profile definitions
- RiskFormatter: Output formatting

Performance:
- 0 LLM calls (vs 3 agents)
- ~0 tokens (vs ~3,900 tokens)
- <0.5s runtime (vs ~30-40s)
- $0 cost (vs ~$0.0025 per stock)
"""

from .risk_engine import RiskEngine, create_risk_engine
from .risk_profiles import (
    RiskProfile,
    AggressiveProfile,
    NeutralProfile,
    ConservativeProfile,
    get_all_profiles,
    get_profile_by_name,
    recommend_profile
)
from .position_calculator import PositionCalculator
from .risk_formatter import RiskFormatter

__all__ = [
    # Main engine
    "RiskEngine",
    "create_risk_engine",
    
    # Profiles
    "RiskProfile",
    "AggressiveProfile",
    "NeutralProfile",
    "ConservativeProfile",
    "get_all_profiles",
    "get_profile_by_name",
    "recommend_profile",
    
    # Components
    "PositionCalculator",
    "RiskFormatter",
]
