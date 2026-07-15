"""
Position Calculator for TradingAgents

Calculates position sizes, risk amounts, and trade parameters based on:
- Entry price
- Stop loss
- Target prices
- Capital available
- Risk profile
- Volatility (ATR)

All calculations follow systematic risk management rules.
"""

import math
from typing import Optional, Dict, Any

from .risk_profiles import RiskProfile


class PositionCalculator:
    """
    Calculate position sizes and risk parameters for trades.
    
    Rules:
    - Capital: ₹200,000 (default)
    - Max risk per trade: ₹4,000 (hard cap)
    - Max active trades: 4
    - Minimum R:R ratio: 1.5:1
    """
    
    def __init__(
        self,
        capital: float = 200000,
        max_risk_per_trade: float = 4000,
        max_active_trades: int = 4,
        min_rr_ratio: float = 1.5
    ):
        """
        Initialize position calculator.
        
        Args:
            capital: Total capital available (₹)
            max_risk_per_trade: Maximum risk per trade (₹)
            max_active_trades: Maximum concurrent positions
            min_rr_ratio: Minimum risk/reward ratio
        """
        self.capital = capital
        self.max_risk_per_trade = max_risk_per_trade
        self.max_active_trades = max_active_trades
        self.min_rr_ratio = min_rr_ratio
    
    def calculate_position(
        self,
        entry_price: float,
        stop_loss: float,
        target: float,
        profile: RiskProfile,
        atr: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate complete position details.
        
        Args:
            entry_price: Entry price per share (₹)
            stop_loss: Stop loss price per share (₹)
            target: Target price per share (₹)
            profile: Risk profile to use
            atr: Average True Range (optional, for validation)
            
        Returns:
            dict: Position details or None if invalid setup
            {
                'allocation': float,      # Capital allocated (₹)
                'quantity': int,          # Number of shares
                'risk_amount': float,     # Amount at risk (₹)
                'risk_percent': float,    # Risk as % of capital
                'stop_loss': float,       # Stop loss price
                'entry_price': float,     # Entry price
                'target': float,          # Target price
                'rr_ratio': float,        # Risk/reward ratio
                'max_loss': float         # Maximum loss (₹)
            }
        """
        # Validate inputs
        if not self._validate_inputs(entry_price, stop_loss, target):
            return None
        
        # Calculate price risk per share
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return None  # Invalid: stop at entry
        
        # Calculate risk amount based on profile
        risk_amount = min(
            self.capital * profile.risk_percent,
            self.max_risk_per_trade
        )
        
        # Calculate quantity based on risk
        quantity = math.floor(risk_amount / price_risk)
        
        if quantity <= 0:
            return None  # Invalid: can't buy any shares
        
        # Calculate allocation
        allocation = quantity * entry_price
        
        # Check allocation limit
        max_allocation = self.capital * profile.max_allocation_percent
        if allocation > max_allocation:
            # Reduce quantity to fit allocation limit
            quantity = math.floor(max_allocation / entry_price)
            allocation = quantity * entry_price
            risk_amount = quantity * price_risk
        
        # Calculate actual risk percent
        actual_risk_percent = (risk_amount / self.capital) * 100
        
        # Calculate R:R ratio
        reward = abs(target - entry_price)
        risk = abs(entry_price - stop_loss)
        rr_ratio = reward / risk if risk > 0 else 0
        
        # Calculate targets based on R:R ratio
        # Target 1: Primary target (based on profile's target R:R)
        # Target 2: Extended target (profile R:R + 0.5)
        action = "Buy" if target > entry_price else "Sell"
        target_1, target_2 = self.calculate_targets(
            entry_price, stop_loss, profile, action
        )
        
        # Calculate max loss
        max_loss = quantity * price_risk
        
        return {
            'allocation': round(allocation, 2),
            'quantity': quantity,
            'risk_amount': round(risk_amount, 2),
            'risk_percent': round(actual_risk_percent, 2),
            'stop_loss': round(stop_loss, 2),
            'entry_price': round(entry_price, 2),
            'target': round(target, 2),
            'target_1': round(target_1, 2),
            'target_2': round(target_2, 2),
            'rr_ratio': round(rr_ratio, 2),
            'max_loss': round(max_loss, 2)
        }
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        atr: Optional[float],
        profile: RiskProfile,
        trader_stop: Optional[float] = None,
        action: str = "Buy"
    ) -> float:
        """
        Calculate optimal stop loss price.
        
        Priority:
        1. Use trader's stop if provided
        2. Use ATR-based stop if ATR available
        3. Fall back to percentage-based stop
        
        Args:
            entry_price: Entry price
            atr: Average True Range
            profile: Risk profile
            trader_stop: Stop from trader (optional)
            action: "Buy" or "Sell"
            
        Returns:
            float: Stop loss price
        """
        # Use trader's stop if provided
        if trader_stop is not None and trader_stop > 0:
            return round(trader_stop, 2)
        
        # Use ATR-based stop if available
        if atr is not None and atr > 0:
            multiplier = profile.get_stop_multiplier()
            stop_distance = atr * multiplier
            
            if action.lower() == "buy":
                stop_loss = entry_price - stop_distance
            else:
                stop_loss = entry_price + stop_distance
            
            return round(max(stop_loss, 0.01), 2)  # Ensure positive
        
        # Fallback to percentage-based stop
        percentage_stop = 0.08  # 8% default
        
        if action.lower() == "buy":
            stop_loss = entry_price * (1 - percentage_stop)
        else:
            stop_loss = entry_price * (1 + percentage_stop)
        
        return round(stop_loss, 2)
    
    def calculate_targets(
        self,
        entry_price: float,
        stop_loss: float,
        profile: RiskProfile,
        action: str = "Buy"
    ) -> tuple[float, float]:
        """
        Calculate target prices based on risk/reward ratio.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            profile: Risk profile
            action: "Buy" or "Sell"
            
        Returns:
            tuple: (target_1, target_2) prices
        """
        risk = abs(entry_price - stop_loss)
        
        # Target 1: Minimum R:R from profile
        reward_1 = risk * profile.target_rr_ratio
        
        # Target 2: Extended R:R (1.5x of target 1)
        reward_2 = risk * (profile.target_rr_ratio * 1.5)
        
        if action.lower() == "buy":
            target_1 = entry_price + reward_1
            target_2 = entry_price + reward_2
        else:
            target_1 = entry_price - reward_1
            target_2 = entry_price - reward_2
        
        return (
            round(max(target_1, 0.01), 2),
            round(max(target_2, 0.01), 2)
        )
    
    def validate_trade_setup(
        self,
        entry_price: float,
        stop_loss: float,
        target: float,
        rr_ratio: float
    ) -> tuple[bool, str]:
        """
        Validate if trade setup meets minimum criteria.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            target: Target price
            rr_ratio: Risk/reward ratio
            
        Returns:
            tuple: (is_valid, message)
        """
        # Check R:R ratio
        if rr_ratio < self.min_rr_ratio:
            return (
                False,
                f"R:R ratio {rr_ratio:.2f}:1 below minimum {self.min_rr_ratio}:1"
            )
        
        # Check stop loss is reasonable (not too far)
        stop_distance_percent = abs(entry_price - stop_loss) / entry_price * 100
        if stop_distance_percent > 15:
            return (
                False,
                f"Stop loss too far ({stop_distance_percent:.1f}% from entry)"
            )
        
        # Check target is achievable (not too far)
        target_distance_percent = abs(target - entry_price) / entry_price * 100
        if target_distance_percent > 50:
            return (
                False,
                f"Target too far ({target_distance_percent:.1f}% from entry)"
            )
        
        return (True, "Valid trade setup")
    
    def _validate_inputs(
        self,
        entry_price: float,
        stop_loss: float,
        target: float
    ) -> bool:
        """
        Validate input parameters.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            target: Target price
            
        Returns:
            bool: True if valid
        """
        # Check all prices are positive
        if entry_price <= 0 or stop_loss <= 0 or target <= 0:
            return False
        
        # Check stop and target are on correct sides
        # For buy: stop < entry < target
        # For sell: target < entry < stop
        if stop_loss < entry_price < target:
            return True  # Valid buy setup
        elif target < entry_price < stop_loss:
            return True  # Valid sell setup
        else:
            return False  # Invalid setup
    
    def get_capital_summary(self) -> Dict[str, Any]:
        """
        Get summary of capital allocation rules.
        
        Returns:
            dict: Capital allocation parameters
        """
        return {
            'total_capital': self.capital,
            'max_risk_per_trade': self.max_risk_per_trade,
            'max_risk_percent': (self.max_risk_per_trade / self.capital) * 100,
            'max_active_trades': self.max_active_trades,
            'max_total_exposure': self.capital,  # If all trades allocated
            'min_rr_ratio': self.min_rr_ratio
        }
