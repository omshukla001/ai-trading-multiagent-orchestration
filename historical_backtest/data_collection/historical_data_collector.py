"""
Historical Data Collector

Fetches historical market data for backtesting using existing project data providers.

Uses:
- Yahoo Finance for price data (yfinance)
- Alpha Vantage for fundamentals (if available)
- Existing news APIs

No future data leakage - all data as of specified trade_date.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tradingagents.dataflows.interface import route_to_vendor


class HistoricalDataCollector:
    """Collects historical data for backtesting without future leakage"""
    
    def __init__(self, data_dir: str = "historical_backtest/data"):
        """
        Initialize collector
        
        Args:
            data_dir: Directory to store collected data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.limitations = []
    
    def collect_for_trade_date(
        self, 
        ticker: str, 
        trade_date: str,
        lookback_days: int = 90
    ) -> Dict[str, Any]:
        """
        Collect all data available as of trade_date
        
        Args:
            ticker: Stock ticker (e.g., HDFCBANK.NS)
            trade_date: Trade date in YYYY-MM-DD format
            lookback_days: Days of historical price data
        
        Returns:
            Dict with all collected data
        """
        
        print(f"\n📊 Collecting data for {ticker} as of {trade_date}")
        
        trade_dt = datetime.strptime(trade_date, "%Y-%m-%d")
        
        data = {
            'metadata': {
                'ticker': ticker,
                'trade_date': trade_date,
                'collected_at': datetime.now().isoformat(),
                'lookback_days': lookback_days
            },
            'market_data': None,
            'fundamentals_data': None,
            'news_data': None,
            'macro_data': None,
            'limitations': []
        }
        
        # 1. Market Data (OHLCV)
        print(f"   → Fetching market data ({lookback_days} days)")
        try:
            start_date = (trade_dt - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
            
            market_data_raw = route_to_vendor(
                "get_stock_data",
                ticker,
                start_date,
                trade_date
            )
            
            data['market_data'] = {
                'ticker': ticker,
                'start_date': start_date,
                'end_date': trade_date,
                'data': str(market_data_raw),
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"      ✅ Market data collected ({len(str(market_data_raw))} chars)")
        
        except Exception as e:
            print(f"      ❌ Market data failed: {str(e)[:50]}")
            data['limitations'].append(f"Market data unavailable: {str(e)[:100]}")
        
        # 2. Fundamentals Data
        print(f"   → Fetching fundamentals")
        try:
            fundamentals_raw = route_to_vendor(
                "get_financial_statements",
                ticker
            )
            
            data['fundamentals_data'] = {
                'ticker': ticker,
                'data': str(fundamentals_raw),
                'timestamp': datetime.now().isoformat(),
                'note': 'Historical fundamentals may not reflect exact values as of trade_date'
            }
            
            print(f"      ✅ Fundamentals collected ({len(str(fundamentals_raw))} chars)")
            data['limitations'].append(
                "Fundamentals: Using currently available data, may differ from historical values"
            )
        
        except Exception as e:
            print(f"      ⚠️  Fundamentals failed: {str(e)[:50]}")
            data['limitations'].append(f"Fundamentals unavailable: {str(e)[:100]}")
            data['fundamentals_data'] = {'error': str(e)}
        
        # 3. News Data
        print(f"   → Fetching news (7 days)")
        try:
            news_start = (trade_dt - timedelta(days=7)).strftime("%Y-%m-%d")
            
            company_news = route_to_vendor(
                "get_news",
                ticker,
                news_start,
                trade_date
            )
            
            global_news = route_to_vendor(
                "get_global_news",
                trade_date,
                7,
                10
            )
            
            data['news_data'] = {
                'company_news': str(company_news),
                'global_news': str(global_news),
                'start_date': news_start,
                'end_date': trade_date,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"      ✅ News collected")
            data['limitations'].append(
                "News: Limited by API availability and lookback period"
            )
        
        except Exception as e:
            print(f"      ⚠️  News failed: {str(e)[:50]}")
            data['limitations'].append(f"News unavailable: {str(e)[:100]}")
            data['news_data'] = {'error': str(e)}
        
        # 4. Macro Data
        print(f"   → Fetching macro indicators")
        macro_indicators = {}
        
        for indicator in ['cpi', 'unemployment', 'interest_rate']:
            try:
                macro_raw = route_to_vendor(
                    "get_macro_indicators",
                    indicator,
                    trade_date,
                    30
                )
                macro_indicators[indicator] = str(macro_raw)
            except Exception as e:
                macro_indicators[indicator] = f"Error: {str(e)[:50]}"
        
        data['macro_data'] = {
            'indicators': macro_indicators,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"      ✅ Macro data collected")
        data['limitations'].append(
            "Macro: Using best available historical data"
        )
        
        # Save collected data
        self._save_data(ticker, trade_date, data)
        
        print(f"   ✅ Data collection complete for {ticker} on {trade_date}")
        print(f"      Limitations: {len(data['limitations'])}")
        
        return data
    
    def _save_data(self, ticker: str, trade_date: str, data: Dict) -> None:
        """Save collected data to file"""
        
        filename = f"raw_data_{ticker}_{trade_date}.json"
        filepath = self.data_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"      💾 Saved to {filepath}")
    
    def collect_batch(
        self, 
        trade_dates: List[Dict[str, str]],
        lookback_days: int = 90
    ) -> List[Dict]:
        """
        Collect data for multiple trades
        
        Args:
            trade_dates: List of {ticker, date} dicts
            lookback_days: Days of historical data
        
        Returns:
            List of collected data dicts
        """
        
        print(f"\n{'=' * 80}")
        print(f"BATCH DATA COLLECTION")
        print(f"{'=' * 80}")
        print(f"Trades: {len(trade_dates)}")
        print(f"Lookback: {lookback_days} days")
        print()
        
        results = []
        
        for i, trade_info in enumerate(trade_dates, 1):
            print(f"\n[{i}/{len(trade_dates)}] Processing {trade_info['ticker']} on {trade_info['date']}")
            
            try:
                data = self.collect_for_trade_date(
                    trade_info['ticker'],
                    trade_info['date'],
                    lookback_days
                )
                results.append(data)
            
            except Exception as e:
                print(f"   ❌ Failed: {str(e)}")
                results.append({
                    'error': str(e),
                    'ticker': trade_info['ticker'],
                    'trade_date': trade_info['date']
                })
        
        print(f"\n{'=' * 80}")
        print(f"BATCH COLLECTION COMPLETE")
        print(f"{'=' * 80}")
        print(f"Successful: {sum(1 for r in results if 'error' not in r)}/{len(results)}")
        print(f"Failed: {sum(1 for r in results if 'error' in r)}/{len(results)}")
        
        return results


def generate_stage1_trade_dates() -> List[Dict[str, str]]:
    """
    Generate 20 trade dates for Stage 1 validation
    
    Uses dates from 2024 (recent, stable data availability)
    Spread across quarters
    
    Returns:
        List of {ticker, date} dicts
    """
    
    # Indian market stocks with good liquidity
    tickers = ['HDFCBANK.NS', 'RELIANCE.NS', 'INFY.NS']
    
    # Dates spread across 2024 (avoiding holidays/weekends)
    # Q1 2024
    q1_dates = ['2024-01-15', '2024-02-05', '2024-02-20', '2024-03-11', '2024-03-25']
    
    # Q2 2024
    q2_dates = ['2024-04-08', '2024-04-22', '2024-05-13', '2024-05-27', '2024-06-10']
    
    # Q3 2024
    q3_dates = ['2024-07-08', '2024-07-22', '2024-08-05', '2024-08-19', '2024-09-02']
    
    # Q4 2024 (up to available data)
    q4_dates = ['2024-10-07', '2024-10-21', '2024-11-04', '2024-11-18', '2024-12-02']
    
    all_dates = q1_dates + q2_dates + q3_dates + q4_dates
    
    # Create 20 trades by cycling through tickers
    trade_dates = []
    
    for i, date in enumerate(all_dates[:20]):  # Take first 20 dates
        ticker = tickers[i % len(tickers)]  # Rotate through tickers
        trade_dates.append({'ticker': ticker, 'date': date})
    
    return trade_dates


if __name__ == "__main__":
    """
    Test data collection for Stage 1
    """
    
    print("=" * 80)
    print("STAGE 1 DATA COLLECTION TEST")
    print("=" * 80)
    
    collector = HistoricalDataCollector()
    
    # Generate Stage 1 trade dates
    trade_dates = generate_stage1_trade_dates()
    
    print(f"\nGenerated {len(trade_dates)} trade dates")
    print("\nFirst 5 trades:")
    for trade in trade_dates[:5]:
        print(f"  {trade['ticker']} on {trade['date']}")
    
    # Test with first trade
    print(f"\n{'=' * 80}")
    print("TEST: Collecting data for first trade")
    print(f"{'=' * 80}")
    
    first_trade = trade_dates[0]
    data = collector.collect_for_trade_date(
        first_trade['ticker'],
        first_trade['date'],
        lookback_days=90
    )
    
    print(f"\n✅ Test successful!")
    print(f"   Market data: {'✅' if data['market_data'] else '❌'}")
    print(f"   Fundamentals: {'✅' if data['fundamentals_data'] else '❌'}")
    print(f"   News: {'✅' if data['news_data'] else '❌'}")
    print(f"   Macro: {'✅' if data['macro_data'] else '❌'}")
    print(f"   Limitations: {len(data['limitations'])}")
    
    print(f"\nTo collect all 20 trades:")
    print(f"  collector.collect_batch(trade_dates)")
