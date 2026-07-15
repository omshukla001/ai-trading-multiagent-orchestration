"""
Unit Tests for Risk Engine

Comprehensive tests for position calculator, risk profiles,
and risk engine integration.

Run with:
    pytest tests/unit/test_risk_engine.py -v
"""

import pytest
from tradingagents.agents.risk_mgmt.risk_engine import RiskEngine
from tradingagents.agents.risk_mgmt.risk_profiles import (
    AggressiveProfile,
    NeutralProfile,
    ConservativeProfile,
    get_all_profiles,
    recommend_profile
)
from tradingagents.agents.risk_mgmt.position_calculator import PositionCalculator


class TestRiskProfiles:
    """Test risk profile definitions"""
    
    def test_aggressive_profile_values(self):
        """Test aggressive profile has correct parameters"""
        profile = AggressiveProfile()
        
        assert profile.name == "Aggressive"
        assert profile.risk_percent == 0.02  # 2%
        assert profile.max_allocation_percent == 0.25  # 25%
        assert profile.target_rr_ratio == 2.5
    
    def test_neutral_profile_values(self):
        """Test neutral profile has correct parameters"""
        profile = NeutralProfile()
        
        assert profile.name == "Neutral"
        assert profile.risk_percent == 0.015  # 1.5%
        assert profile.max_allocation_percent == 0.20  # 20%
        assert profile.target_rr_ratio == 2.0
    
    def test_risk_hierarchy(self):
        """Test profiles have correct risk hierarchy"""
        aggressive = AggressiveProfile()
        neutral = NeutralProfile()
        conservative = ConservativeProfile()
        
        # Risk should decrease
        assert aggressive.risk_percent > neutral.risk_percent
        assert neutral.risk_percent > conservative.risk_percent


class TestPositionCalculator:
    """Test position sizing calculations"""
    
    @pytest.fixture
    def calculator(self):
        return PositionCalculator(capital=200000)
    
    def test_basic_position_calculation(self, calculator):
        """Test standard position calculation"""
        result = calculator.calculate_position(
            entry_price=1500,
            stop_loss=1425,
            target=1650,
            profile=NeutralProfile()
        )
        
        assert result is not None
        assert result['quantity'] > 0
        assert result['risk_amount'] <= 3000  # 1.5% of 200k
        assert result['rr_ratio'] >= 1.5
    
    def test_risk_cap(self, calculator):
        """Test risk doesn't exceed maximum"""
        result = calculator.calculate_position(
            entry_price=1500,
            stop_loss=1200,
            target=2000,
            profile=AggressiveProfile()
        )
        
        assert result['max_loss'] <= 4000


class TestRiskEngine:
    """Test complete risk engine"""
    
    @pytest.fixture
    def engine(self):
        return RiskEngine()
    
    @pytest.fixture
    def mock_state(self):
        return {
            "trader_investment_plan": "Action: BUY, Entry: 1500, Stop: 1425",
            "market_report": {
                "trend_strength": 0.75,
                "indicators": {"close": 1495, "atr": 35}
            },
            "fundamentals_report": {"overall_score": 0.70}
        }
    
    def test_analyze_method(self, engine, mock_state):
        """Test main analyze method"""
        result = engine.analyze(mock_state)
        
        assert 'history' in result
        assert 'risk_analysis' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
