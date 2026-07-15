"""
Paper Trading Engine - Phase 3 Task 2

Track recommendations and calculate performance metrics over time.

Stores:
- Stock ticker
- Recommendation date
- Action (Buy/Sell/Hold)
- Entry price
- Stop loss
- Target
- Actual results after 1d/3d/7d

Calculates:
- Win rate
- Average return
- Maximum drawdown
- Profit factor
- Sharpe ratio

Usage:
    # Log a recommendation
    engine = PaperTradingEngine()
    engine.log_recommendation(
        ticker="HDFCBANK.NS",
        date="2026-07-05",
        action="Buy",
        entry=1650.0,
        stop=1585.0,
        target=1780.0
    )
    
    # Update with actual results (run daily)
    engine.update_results()
    
    # Generate performance report
    engine.generate_report()
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import yfinance as yf


@dataclass
class Trade:
    """Single trade recommendation"""
    id: Optional[int] = None
    ticker: str = ""
    recommendation_date: str = ""
    action: str = ""
    entry_price: float = 0.0
    stop_loss: float = 0.0
    target: float = 0.0
    quantity: int = 0
    allocation: float = 0.0
    risk_amount: float = 0.0
    rr_ratio: float = 0.0
    
    # Actual results
    price_1d: Optional[float] = None
    price_3d: Optional[float] = None
    price_7d: Optional[float] = None
    
    return_1d: Optional[float] = None
    return_3d: Optional[float] = None
    return_7d: Optional[float] = None
    
    status: str = "OPEN"  # OPEN, WIN, LOSS, STOPPED, EXPIRED
    exit_price: Optional[float] = None
    exit_date: Optional[str] = None
    final_return: Optional[float] = None
    
    created_at: str = ""
    updated_at: str = ""


class PaperTradingEngine:
    """
    Paper trading engine to track and evaluate recommendations.
    
    Stores all recommendations in SQLite database and tracks actual
    market performance to calculate real-world metrics.
    """
    
    def __init__(self, db_path: str = "paper_trading.db"):
        """
        Initialize paper trading engine.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Create trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                recommendation_date TEXT NOT NULL,
                action TEXT NOT NULL,
                entry_price REAL NOT NULL,
                stop_loss REAL NOT NULL,
                target REAL NOT NULL,
                quantity INTEGER,
                allocation REAL,
                risk_amount REAL,
                rr_ratio REAL,
                
                price_1d REAL,
                price_3d REAL,
                price_7d REAL,
                
                return_1d REAL,
                return_3d REAL,
                return_7d REAL,
                
                status TEXT DEFAULT 'OPEN',
                exit_price REAL,
                exit_date TEXT,
                final_return REAL,
                
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Create index on ticker and date
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_ticker_date 
            ON trades(ticker, recommendation_date)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_status 
            ON trades(status)
        ''')
        
        self.conn.commit()
    
    def log_recommendation(
        self,
        ticker: str,
        recommendation_date: str,
        action: str,
        entry_price: float,
        stop_loss: float,
        target: float,
        quantity: int = 0,
        allocation: float = 0.0,
        risk_amount: float = 0.0,
        rr_ratio: float = 0.0
    ) -> int:
        """
        Log a new trading recommendation.
        
        Args:
            ticker: Stock ticker symbol
            recommendation_date: Date of recommendation (YYYY-MM-DD)
            action: Buy/Sell/Hold
            entry_price: Entry price
            stop_loss: Stop loss price
            target: Target price
            quantity: Number of shares
            allocation: Capital allocated
            risk_amount: Amount at risk
            rr_ratio: Risk/reward ratio
            
        Returns:
            int: Trade ID
        """
        now = datetime.now().isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO trades (
                ticker, recommendation_date, action,
                entry_price, stop_loss, target,
                quantity, allocation, risk_amount, rr_ratio,
                status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ticker, recommendation_date, action,
            entry_price, stop_loss, target,
            quantity, allocation, risk_amount, rr_ratio,
            'OPEN', now, now
        ))
        
        self.conn.commit()
        trade_id = cursor.lastrowid
        
        print(f"✅ Logged recommendation: {ticker} {action} @ ₹{entry_price:.2f} (ID: {trade_id})")
        return trade_id
    
    def update_results(self, days_back: int = 30):
        """
        Update actual market results for open trades.
        
        Fetches current prices and calculates returns for 1d/3d/7d periods.
        Updates trade status based on stop loss / target hit.
        
        Args:
            days_back: Number of days to look back for updates
        """
        cursor = self.conn.cursor()
        
        # Get open trades from last N days
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        cursor.execute('''
            SELECT * FROM trades 
            WHERE status = 'OPEN' 
            AND recommendation_date >= ?
            ORDER BY recommendation_date DESC
        ''', (cutoff_date,))
        
        trades = cursor.fetchall()
        
        print(f"\nUpdating {len(trades)} open trades...")
        
        for row in trades:
            trade = self._row_to_trade(row)
            self._update_trade_result(trade)
        
        self.conn.commit()
        print("✅ Update complete\n")
    
    def _update_trade_result(self, trade: Trade):
        """Update a single trade with actual market data"""
        try:
            rec_date = datetime.strptime(trade.recommendation_date, "%Y-%m-%d")
            today = datetime.now()
            days_elapsed = (today - rec_date).days
            
            # Fetch price history
            ticker_obj = yf.Ticker(trade.ticker)
            end_date = today.strftime("%Y-%m-%d")
            history = ticker_obj.history(
                start=trade.recommendation_date,
                end=end_date
            )
            
            if len(history) == 0:
                print(f"  ⚠️  No data for {trade.ticker}")
                return
            
            # Get prices at different intervals
            updates = {}
            
            if days_elapsed >= 1 and trade.price_1d is None:
                if len(history) > 1:
                    price_1d = float(history['Close'].iloc[1])
                    return_1d = ((price_1d - trade.entry_price) / trade.entry_price) * 100
                    updates['price_1d'] = price_1d
                    updates['return_1d'] = return_1d
            
            if days_elapsed >= 3 and trade.price_3d is None:
                if len(history) > 3:
                    price_3d = float(history['Close'].iloc[min(3, len(history)-1)])
                    return_3d = ((price_3d - trade.entry_price) / trade.entry_price) * 100
                    updates['price_3d'] = price_3d
                    updates['return_3d'] = return_3d
            
            if days_elapsed >= 7 and trade.price_7d is None:
                if len(history) > 7:
                    price_7d = float(history['Close'].iloc[min(7, len(history)-1)])
                    return_7d = ((price_7d - trade.entry_price) / trade.entry_price) * 100
                    updates['price_7d'] = price_7d
                    updates['return_7d'] = return_7d
            
            # Check if stop or target hit
            if trade.status == 'OPEN':
                current_price = float(history['Close'].iloc[-1])
                
                if trade.action == "Buy":
                    if current_price <= trade.stop_loss:
                        updates['status'] = 'STOPPED'
                        updates['exit_price'] = current_price
                        updates['exit_date'] = today.strftime("%Y-%m-%d")
                        updates['final_return'] = ((current_price - trade.entry_price) / trade.entry_price) * 100
                    elif current_price >= trade.target:
                        updates['status'] = 'WIN'
                        updates['exit_price'] = current_price
                        updates['exit_date'] = today.strftime("%Y-%m-%d")
                        updates['final_return'] = ((current_price - trade.entry_price) / trade.entry_price) * 100
                elif trade.action == "Sell":
                    if current_price >= trade.stop_loss:
                        updates['status'] = 'STOPPED'
                        updates['exit_price'] = current_price
                        updates['exit_date'] = today.strftime("%Y-%m-%d")
                        updates['final_return'] = ((trade.entry_price - current_price) / trade.entry_price) * 100
                    elif current_price <= trade.target:
                        updates['status'] = 'WIN'
                        updates['exit_price'] = current_price
                        updates['exit_date'] = today.strftime("%Y-%m-%d")
                        updates['final_return'] = ((trade.entry_price - current_price) / trade.entry_price) * 100
                
                # Mark as expired after 7 days if not closed
                if days_elapsed > 7 and updates.get('status') == 'OPEN':
                    updates['status'] = 'EXPIRED'
                    updates['exit_price'] = current_price
                    updates['exit_date'] = today.strftime("%Y-%m-%d")
                    updates['final_return'] = ((current_price - trade.entry_price) / trade.entry_price) * 100
            
            # Update database
            if updates:
                updates['updated_at'] = datetime.now().isoformat()
                
                set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
                values = list(updates.values()) + [trade.id]
                
                cursor = self.conn.cursor()
                cursor.execute(f'''
                    UPDATE trades SET {set_clause}
                    WHERE id = ?
                ''', values)
                
                print(f"  ✅ Updated {trade.ticker} (ID: {trade.id}) - Status: {updates.get('status', 'OPEN')}")
        
        except Exception as e:
            print(f"  ❌ Error updating {trade.ticker}: {str(e)}")
    
    def calculate_metrics(self, days_back: int = 30) -> Dict[str, any]:
        """
        Calculate performance metrics.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            dict: Performance metrics
        """
        cursor = self.conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        # Get all closed trades
        cursor.execute('''
            SELECT * FROM trades 
            WHERE status IN ('WIN', 'STOPPED', 'EXPIRED')
            AND recommendation_date >= ?
        ''', (cutoff_date,))
        
        closed_trades = [self._row_to_trade(row) for row in cursor.fetchall()]
        
        if not closed_trades:
            return {
                'error': 'No closed trades to analyze',
                'total_trades': 0
            }
        
        # Calculate metrics
        total_trades = len(closed_trades)
        wins = [t for t in closed_trades if t.status == 'WIN']
        losses = [t for t in closed_trades if t.status in ('STOPPED', 'LOSS')]
        
        win_rate = (len(wins) / total_trades) * 100 if total_trades > 0 else 0
        
        returns = [t.final_return for t in closed_trades if t.final_return is not None]
        avg_return = sum(returns) / len(returns) if returns else 0
        
        winning_returns = [t.final_return for t in wins if t.final_return is not None]
        losing_returns = [t.final_return for t in losses if t.final_return is not None]
        
        avg_win = sum(winning_returns) / len(winning_returns) if winning_returns else 0
        avg_loss = sum(losing_returns) / len(losing_returns) if losing_returns else 0
        
        # Profit factor
        total_profit = sum(r for r in returns if r > 0)
        total_loss = abs(sum(r for r in returns if r < 0))
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        # Max drawdown
        cumulative_returns = []
        cumsum = 0
        for r in returns:
            cumsum += r
            cumulative_returns.append(cumsum)
        
        max_drawdown = 0
        peak = cumulative_returns[0] if cumulative_returns else 0
        for val in cumulative_returns:
            if val > peak:
                peak = val
            drawdown = peak - val
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return {
            'total_trades': total_trades,
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': round(win_rate, 2),
            'avg_return': round(avg_return, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'max_drawdown': round(max_drawdown, 2),
            'total_profit': round(total_profit, 2),
            'total_loss': round(total_loss, 2)
        }
    
    def generate_report(self, days_back: int = 30, output_file: Optional[str] = None):
        """
        Generate performance report.
        
        Args:
            days_back: Number of days to include in report
            output_file: Optional output file path for markdown report
        """
        print("=" * 80)
        print("PAPER TRADING PERFORMANCE REPORT")
        print("=" * 80)
        print(f"Period: Last {days_back} days")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        metrics = self.calculate_metrics(days_back)
        
        if 'error' in metrics:
            print(f"❌ {metrics['error']}")
            return
        
        print("OVERALL PERFORMANCE:")
        print("─" * 80)
        print(f"  Total Trades: {metrics['total_trades']}")
        print(f"  Wins: {metrics['wins']} | Losses: {metrics['losses']}")
        print(f"  Win Rate: {metrics['win_rate']:.2f}%")
        print(f"  Average Return: {metrics['avg_return']:+.2f}%")
        print(f"  Average Win: {metrics['avg_win']:+.2f}%")
        print(f"  Average Loss: {metrics['avg_loss']:+.2f}%")
        print(f"  Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"  Max Drawdown: {metrics['max_drawdown']:.2f}%")
        
        # Get recent trades
        cursor = self.conn.cursor()
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        cursor.execute('''
            SELECT * FROM trades 
            WHERE recommendation_date >= ?
            ORDER BY recommendation_date DESC
            LIMIT 20
        ''', (cutoff_date,))
        
        recent_trades = [self._row_to_trade(row) for row in cursor.fetchall()]
        
        print(f"\nRECENT TRADES ({len(recent_trades)}):")
        print("─" * 80)
        
        for trade in recent_trades:
            status_icon = {"WIN": "✅", "STOPPED": "❌", "EXPIRED": "⏱️ ", "OPEN": "🔄"}.get(trade.status, "❓")
            
            return_str = ""
            if trade.final_return is not None:
                return_str = f" | Return: {trade.final_return:+.2f}%"
            
            print(f"  {status_icon} {trade.ticker} {trade.action} @ ₹{trade.entry_price:.2f} "
                  f"({trade.recommendation_date}) - {trade.status}{return_str}")
        
        # Save to file if requested
        if output_file:
            self._save_markdown_report(metrics, recent_trades, output_file)
            print(f"\n📄 Report saved to: {output_file}")
    
    def _save_markdown_report(self, metrics: Dict, trades: List[Trade], filepath: str):
        """Save report as markdown"""
        with open(filepath, 'w') as f:
            f.write("# Paper Trading Performance Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Performance Metrics\n\n")
            f.write(f"- **Total Trades**: {metrics['total_trades']}\n")
            f.write(f"- **Win Rate**: {metrics['win_rate']:.2f}%\n")
            f.write(f"- **Average Return**: {metrics['avg_return']:+.2f}%\n")
            f.write(f"- **Profit Factor**: {metrics['profit_factor']:.2f}\n")
            f.write(f"- **Max Drawdown**: {metrics['max_drawdown']:.2f}%\n\n")
            
            f.write("## Recent Trades\n\n")
            f.write("| Date | Ticker | Action | Entry | Status | Return |\n")
            f.write("|------|--------|--------|-------|--------|--------|\n")
            
            for trade in trades[:20]:
                return_val = f"{trade.final_return:+.2f}%" if trade.final_return else "N/A"
                f.write(f"| {trade.recommendation_date} | {trade.ticker} | {trade.action} | "
                       f"₹{trade.entry_price:.2f} | {trade.status} | {return_val} |\n")
    
    def _row_to_trade(self, row) -> Trade:
        """Convert database row to Trade object"""
        return Trade(**dict(row))
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    # Example usage
    engine = PaperTradingEngine()
    
    # Log a test recommendation
    engine.log_recommendation(
        ticker="HDFCBANK.NS",
        recommendation_date=datetime.now().strftime("%Y-%m-%d"),
        action="Buy",
        entry_price=1650.0,
        stop_loss=1585.0,
        target=1780.0,
        quantity=30,
        allocation=49500.0,
        risk_amount=1950.0,
        rr_ratio=2.0
    )
    
    # Update results
    engine.update_results()
    
    # Generate report
    engine.generate_report(output_file="paper_trading_report.md")
    
    engine.close()
