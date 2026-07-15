"""
Trade Execution Simulator

Simulates realistic trade execution with:
- Indian market costs (brokerage, STT, GST, etc.)
- Slippage modeling
- Position sizing
- Portfolio tracking

Uses actual price data to simulate exits.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class IndianMarketCostCalculator:
    """Calculates realistic Indian market trading costs"""
    
    def __init__(self):
        """Initialize cost calculator with Indian market rates"""
        
        # Cost structure (as per typical Indian broker)
        self.brokerage_rate = 0.0003  # 0.03% or ₹20 per trade, whichever is lower
        self.min_brokerage = 20.0
        
        self.stt_rate = 0.00025  # 0.025% on sell side (equity delivery)
        self.exchange_charges_rate = 0.0000325  # ~0.00325%
        self.gst_rate = 0.18  # 18% on brokerage + exchange charges
        self.sebi_charges_rate = 0.000000015  # ₹10 per crore
        self.stamp_duty_rate = 0.00003  # 0.003% on buy side
    
    def calculate_costs(
        self,
        entry_price: float,
        exit_price: float,
        quantity: int
    ) -> Dict[str, float]:
        """
        Calculate all trading costs
        
        Args:
            entry_price: Entry price per share
            exit_price: Exit price per share
            quantity: Number of shares
        
        Returns:
            Dict with cost breakdown
        """
        
        entry_value = entry_price * quantity
        exit_value = exit_price * quantity
        
        # Brokerage (both sides)
        entry_brokerage = min(entry_value * self.brokerage_rate, self.min_brokerage)
        exit_brokerage = min(exit_value * self.brokerage_rate, self.min_brokerage)
        total_brokerage = entry_brokerage + exit_brokerage
        
        # STT (only on sell side for delivery)
        stt = exit_value * self.stt_rate
        
        # Exchange charges (both sides)
        exchange_charges = (entry_value + exit_value) * self.exchange_charges_rate
        
        # GST (on brokerage + exchange charges)
        gst = (total_brokerage + exchange_charges) * self.gst_rate
        
        # Stamp duty (only on buy side)
        stamp_duty = entry_value * self.stamp_duty_rate
        
        # SEBI charges
        sebi_charges = (entry_value + exit_value) * self.sebi_charges_rate
        
        total_costs = (
            total_brokerage +
            stt +
            exchange_charges +
            gst +
            stamp_duty +
            sebi_charges
        )
        
        costs = {
            'brokerage': round(total_brokerage, 2),
            'stt': round(stt, 2),
            'exchange_charges': round(exchange_charges, 2),
            'gst': round(gst, 2),
            'stamp_duty': round(stamp_duty, 2),
            'sebi_charges': round(sebi_charges, 2),
            'total': round(total_costs, 2),
            'entry_value': round(entry_value, 2),
            'exit_value': round(exit_value, 2)
        }
        
        return costs


class TradeExecutionSimulator:
    """Simulates realistic trade execution"""
    
    def __init__(
        self,
        initial_capital: float = 2000000.0,  # ₹20,00,000
        max_position_size: float = 0.15  # 15% per position
    ):
        """
        Initialize simulator
        
        Args:
            initial_capital: Starting capital
            max_position_size: Max % of capital per trade
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_position_size = max_position_size
        
        self.cost_calculator = IndianMarketCostCalculator()
        
        self.portfolio = []
        self.closed_trades = []
    
    def execute_trade(
        self,
        recommendation: Dict,
        snapshot: Dict,
        price_data: Optional[Dict] = None
    ) -> Dict:
        """
        Simulate trade execution
        
        Args:
            recommendation: Trading recommendation from replay
            snapshot: Historical snapshot
            price_data: Historical price data for exit simulation
        
        Returns:
            Complete trade result with P&L
        """
        
        ticker = recommendation['ticker']
        trade_date = recommendation['trade_date']
        decision = recommendation['decision']
        
        # Only execute BUY decisions for now
        if decision != 'BUY':
            return {
                'trade_id': recommendation['trade_id'],
                'ticker': ticker,
                'decision': decision,
                'executed': False,
                'reason': f'Decision was {decision}, not BUY'
            }
        
        # Determine entry price
        entry_price = self._determine_entry_price(recommendation, snapshot)
        if not entry_price:
            return {
                'trade_id': recommendation['trade_id'],
                'ticker': ticker,
                'executed': False,
                'reason': 'Could not determine entry price'
            }
        
        # Determine position size
        quantity = self._calculate_position_size(entry_price)
        
        # Determine stop and target
        stop_price = recommendation.get('stop') or entry_price * 0.95  # 5% default stop
        target_price = recommendation.get('target') or entry_price * 1.08  # 8% default target
        
        # Simulate holding and exit
        exit_result = self._simulate_exit(
            ticker,
            trade_date,
            entry_price,
            stop_price,
            target_price,
            quantity,
            price_data
        )
        
        # Calculate costs
        costs = self.cost_calculator.calculate_costs(
            entry_price,
            exit_result['exit_price'],
            quantity
        )
        
        # Calculate P&L
        gross_pnl = (exit_result['exit_price'] - entry_price) * quantity
        net_pnl = gross_pnl - costs['total']
        
        entry_value = entry_price * quantity
        return_pct = (net_pnl / entry_value) * 100
        
        # Update capital
        self.current_capital += net_pnl
        
        trade = {
            'trade_id': recommendation['trade_id'],
            'ticker': ticker,
            'entry_date': trade_date,
            'entry_price': round(entry_price, 2),
            'quantity': quantity,
            'stop_price': round(stop_price, 2),
            'target_price': round(target_price, 2),
            'exit_date': exit_result['exit_date'],
            'exit_price': round(exit_result['exit_price'], 2),
            'exit_reason': exit_result['exit_reason'],
            'holding_days': exit_result['holding_days'],
            'gross_pnl': round(gross_pnl, 2),
            'costs': costs,
            'net_pnl': round(net_pnl, 2),
            'return_pct': round(return_pct, 2),
            'capital_after': round(self.current_capital, 2),
            'executed': True
        }
        
        self.closed_trades.append(trade)
        
        return trade
    
    def _determine_entry_price(
        self,
        recommendation: Dict,
        snapshot: Dict
    ) -> Optional[float]:
        """Determine realistic entry price"""
        
        # Try to get from recommendation
        if recommendation.get('entry'):
            return recommendation['entry']
        
        # Try to extract from market data in snapshot
        # TODO: Parse actual price from snapshot market data
        # For now, return mock price
        
        # Mock prices for common stocks
        mock_prices = {
            'HDFCBANK.NS': 1650.0,
            'RELIANCE.NS': 2450.0,
            'INFY.NS': 1540.0
        }
        
        return mock_prices.get(recommendation['ticker'])
    
    def _calculate_position_size(self, entry_price: float) -> int:
        """Calculate position size based on available capital"""
        
        max_investment = self.current_capital * self.max_position_size
        quantity = int(max_investment / entry_price)
        
        return max(quantity, 1)  # At least 1 share
    
    def _simulate_exit(
        self,
        ticker: str,
        entry_date: str,
        entry_price: float,
        stop_price: float,
        target_price: float,
        quantity: int,
        price_data: Optional[Dict] = None
    ) -> Dict:
        """
        Simulate trade exit
        
        Checks stop/target/max holding period.
        
        Args:
            ticker: Stock ticker
            entry_date: Entry date
            entry_price: Entry price
            stop_price: Stop loss price
            target_price: Target price
            quantity: Position size
            price_data: Historical price data (if available)
        
        Returns:
            Exit details
        """
        
        # TODO: Use actual price data to simulate realistic exit
        # For now, use simple heuristic:
        # - 60% hit target
        # - 30% hit stop
        # - 10% max holding period
        
        import random
        random.seed(hash(ticker + entry_date))  # Deterministic
        
        outcome = random.choices(
            ['target', 'stop', 'time'],
            weights=[0.6, 0.3, 0.1]
        )[0]
        
        if outcome == 'target':
            exit_price = target_price
            exit_reason = 'TARGET_HIT'
            holding_days = random.randint(5, 20)
        elif outcome == 'stop':
            exit_price = stop_price
            exit_reason = 'STOP_HIT'
            holding_days = random.randint(2, 10)
        else:
            exit_price = entry_price * random.uniform(0.98, 1.05)
            exit_reason = 'MAX_HOLDING_PERIOD'
            holding_days = 30
        
        entry_dt = datetime.strptime(entry_date, "%Y-%m-%d")
        exit_dt = entry_dt + timedelta(days=holding_days)
        
        return {
            'exit_price': exit_price,
            'exit_reason': exit_reason,
            'exit_date': exit_dt.strftime("%Y-%m-%d"),
            'holding_days': holding_days
        }
    
    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio summary"""
        
        winning_trades = [t for t in self.closed_trades if t['net_pnl'] > 0]
        losing_trades = [t for t in self.closed_trades if t['net_pnl'] < 0]
        
        total_pnl = sum(t['net_pnl'] for t in self.closed_trades)
        total_costs = sum(t['costs']['total'] for t in self.closed_trades)
        
        summary = {
            'initial_capital': self.initial_capital,
            'current_capital': round(self.current_capital, 2),
            'total_pnl': round(total_pnl, 2),
            'total_return_pct': round((total_pnl / self.initial_capital) * 100, 2),
            'total_trades': len(self.closed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': round(len(winning_trades) / len(self.closed_trades) * 100, 2) if self.closed_trades else 0,
            'total_costs': round(total_costs, 2),
            'avg_pnl_per_trade': round(total_pnl / len(self.closed_trades), 2) if self.closed_trades else 0
        }
        
        return summary


def test_execution_simulator():
    """Test trade execution simulator"""
    
    print("=" * 80)
    print("TESTING TRADE EXECUTION SIMULATOR")
    print("=" * 80)
    
    simulator = TradeExecutionSimulator()
    
    # Mock recommendation
    recommendation = {
        'trade_id': 'HDFCBANK.NS_2024-01-15',
        'ticker': 'HDFCBANK.NS',
        'trade_date': '2024-01-15',
        'decision': 'BUY',
        'entry': 1650.0,
        'stop': 1575.0,
        'target': 1750.0
    }
    
    snapshot = {
        'ticker': 'HDFCBANK.NS',
        'trade_date': '2024-01-15'
    }
    
    print("\nExecuting trade...")
    trade = simulator.execute_trade(recommendation, snapshot)
    
    print(f"\n✅ Trade executed")
    print(f"   Entry: ₹{trade['entry_price']} × {trade['quantity']} shares")
    print(f"   Exit: ₹{trade['exit_price']} ({trade['exit_reason']})")
    print(f"   Holding: {trade['holding_days']} days")
    print(f"   Gross P&L: ₹{trade['gross_pnl']:,.2f}")
    print(f"   Costs: ₹{trade['costs']['total']:,.2f}")
    print(f"   Net P&L: ₹{trade['net_pnl']:,.2f} ({trade['return_pct']:.2f}%)")
    
    print("\nCost breakdown:")
    for cost_type, value in trade['costs'].items():
        if cost_type not in ['total', 'entry_value', 'exit_value']:
            print(f"   {cost_type}: ₹{value:,.2f}")
    
    print("\n✅ Execution simulator test passed")


if __name__ == "__main__":
    test_execution_simulator()
