#!/usr/bin/env python3
"""
Validation Data Caching

Pre-fetches and caches all external data for HDFCBANK.NS before validation.

This ensures both baseline and optimized runs use IDENTICAL inputs:
- Market data (OHLCV, technical indicators)
- Fundamentals data (financial statements, ratios)
- News data (company news + global news)
- Macro data (if available)

Prevents validation contamination from:
- Live API changes between runs
- News feed updates
- Market data variations
- Time-dependent external factors
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Set up environment
os.environ['USE_OPTIMIZED_ANALYSTS'] = '1'
os.environ['USE_OPTIMIZED_RISK'] = '1'


def cache_market_data(ticker: str, trade_date: str) -> dict:
    """Cache market data for the ticker"""
    print(f"\n📊 Caching market data for {ticker}...")
    
    try:
        from tradingagents.dataflows.interface import route_to_vendor
        
        # Calculate date range (90 days lookback)
        end_date = datetime.strptime(trade_date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=90)
        
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Fetch market data
        market_data = route_to_vendor(
            "get_stock_data",
            ticker,
            start_str,
            end_str
        )
        
        print(f"   ✅ Market data cached ({len(str(market_data))} chars)")
        
        return {
            'ticker': ticker,
            'start_date': start_str,
            'end_date': end_str,
            'data': str(market_data),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"   ⚠️  Failed to cache market data: {str(e)[:100]}")
        return {
            'ticker': ticker,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def cache_fundamentals_data(ticker: str, trade_date: str) -> dict:
    """Cache fundamentals data for the ticker"""
    print(f"\n📈 Caching fundamentals data for {ticker}...")
    
    try:
        from tradingagents.dataflows.interface import route_to_vendor
        
        # Fetch financial statements
        financials = route_to_vendor("get_financial_statements", ticker)
        
        print(f"   ✅ Fundamentals cached ({len(str(financials))} chars)")
        
        return {
            'ticker': ticker,
            'trade_date': trade_date,
            'data': str(financials),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"   ⚠️  Failed to cache fundamentals: {str(e)[:100]}")
        return {
            'ticker': ticker,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def cache_news_data(ticker: str, trade_date: str) -> dict:
    """Cache news data for the ticker"""
    print(f"\n📰 Caching news data for {ticker}...")
    
    try:
        from tradingagents.dataflows.interface import route_to_vendor
        
        # Calculate news window (7 days lookback)
        end_date = datetime.strptime(trade_date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=7)
        
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Fetch company news
        company_news = route_to_vendor(
            "get_news",
            ticker,
            start_str,
            end_str
        )
        
        # Fetch global news
        global_news = route_to_vendor(
            "get_global_news",
            end_str,
            7,  # lookback days
            10  # limit
        )
        
        print(f"   ✅ Company news cached ({len(str(company_news))} chars)")
        print(f"   ✅ Global news cached ({len(str(global_news))} chars)")
        
        return {
            'ticker': ticker,
            'start_date': start_str,
            'end_date': end_str,
            'company_news': str(company_news),
            'global_news': str(global_news),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"   ⚠️  Failed to cache news: {str(e)[:100]}")
        return {
            'ticker': ticker,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def cache_sentiment_data(ticker: str, trade_date: str) -> dict:
    """Cache sentiment/social media data for the ticker"""
    print(f"\n💬 Caching sentiment data for {ticker}...")
    
    try:
        from tradingagents.dataflows.interface import route_to_vendor
        
        # Calculate lookback
        end_date = datetime.strptime(trade_date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=7)
        
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Fetch sentiment data (may not be available for all vendors)
        try:
            sentiment = route_to_vendor("get_sentiment", ticker, start_str, end_str)
            print(f"   ✅ Sentiment data cached ({len(str(sentiment))} chars)")
            return {
                'ticker': ticker,
                'start_date': start_str,
                'end_date': end_str,
                'data': str(sentiment),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"   ⚠️  Sentiment not available: {str(e)[:50]}")
            return {
                'ticker': ticker,
                'note': 'Sentiment data not available',
                'timestamp': datetime.now().isoformat()
            }
        
    except Exception as e:
        print(f"   ⚠️  Failed to cache sentiment: {str(e)[:100]}")
        return {
            'ticker': ticker,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def cache_benchmark_data(ticker: str, trade_date: str) -> dict:
    """Cache benchmark (index) data"""
    print(f"\n📊 Caching benchmark data...")
    
    try:
        from tradingagents.dataflows.interface import route_to_vendor
        
        # Determine benchmark based on ticker
        benchmark = "^NSEI"  # Nifty 50 for .NS stocks
        if not ticker.endswith('.NS'):
            benchmark = "SPY"  # S&P 500 for US stocks
        
        # Calculate date range
        end_date = datetime.strptime(trade_date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=90)
        
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Fetch benchmark data
        benchmark_data = route_to_vendor("get_stock_data", benchmark, start_str, end_str)
        
        print(f"   ✅ Benchmark ({benchmark}) cached ({len(str(benchmark_data))} chars)")
        
        return {
            'benchmark': benchmark,
            'ticker_reference': ticker,
            'start_date': start_str,
            'end_date': end_str,
            'data': str(benchmark_data),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"   ⚠️  Failed to cache benchmark: {str(e)[:100]}")
        return {
            'benchmark': benchmark if 'benchmark' in locals() else 'unknown',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def cache_sector_data(ticker: str, trade_date: str) -> dict:
    """Cache sector/industry data (if available)"""
    print(f"\n🏭 Caching sector data for {ticker}...")
    
    try:
        # For now, just capture that sector data was requested
        # Actual implementation depends on data vendor capabilities
        print(f"   ⚠️  Sector data caching not implemented (vendor-specific)")
        
        return {
            'ticker': ticker,
            'note': 'Sector data caching requires vendor-specific implementation',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"   ⚠️  Failed to cache sector data: {str(e)[:100]}")
        return {
            'ticker': ticker,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
    """Cache macro indicators (optional)"""
    print(f"\n🌍 Caching macro data...")
    
    try:
        from tradingagents.dataflows.interface import route_to_vendor
        
        indicators = ['cpi', 'unemployment', 'fed_funds_rate', '10y_treasury']
        macro_data = {}
        
        for indicator in indicators:
            try:
                data = route_to_vendor(
                    "get_macro_indicators",
                    indicator,
                    trade_date,
                    30  # lookback days
                )
                macro_data[indicator] = str(data)
                print(f"   ✅ {indicator} cached")
            except Exception as e:
                print(f"   ⚠️  {indicator} failed: {str(e)[:50]}")
                macro_data[indicator] = f"Error: {str(e)}"
        
        return {
            'trade_date': trade_date,
            'indicators': macro_data,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"   ⚠️  Failed to cache macro data: {str(e)[:100]}")
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def cache_all_data(ticker: str, trade_date: str) -> dict:
    """Cache all external data for validation"""
    
    print("=" * 80)
    print("CACHING VALIDATION DATA - COMPREHENSIVE")
    print("=" * 80)
    print(f"Ticker: {ticker}")
    print(f"Trade Date: {trade_date}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n⚠️  VALIDATION_CACHE_ONLY mode - All external data will be cached")
    
    cached_data = {
        'metadata': {
            'ticker': ticker,
            'trade_date': trade_date,
            'cached_at': datetime.now().isoformat(),
            'purpose': 'Phase 3A validation - ensures identical inputs for baseline and optimized runs',
            'cache_version': '1.0',
            'validation_mode': 'DETERMINISTIC'
        },
        'mandatory': {
            'market_data': None,
            'fundamentals_data': None,
            'news_data': None,
            'macro_data': None
        },
        'recommended': {
            'sentiment_data': None,
            'benchmark_data': None,
            'sector_data': None
        }
    }
    
    # Cache mandatory data
    print("\n📌 MANDATORY DATA:")
    cached_data['mandatory']['market_data'] = cache_market_data(ticker, trade_date)
    cached_data['mandatory']['fundamentals_data'] = cache_fundamentals_data(ticker, trade_date)
    cached_data['mandatory']['news_data'] = cache_news_data(ticker, trade_date)
    cached_data['mandatory']['macro_data'] = cache_macro_data(trade_date)
    
    # Cache recommended data
    print("\n📌 RECOMMENDED DATA:")
    try:
        # Benchmark data
        end_date = datetime.strptime(trade_date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=90)
        benchmark = "^NSEI" if ticker.endswith('.NS') else "SPY"
        
        print(f"\n📊 Caching benchmark ({benchmark})...")
        from tradingagents.dataflows.interface import route_to_vendor
        benchmark_data = route_to_vendor(
            "get_stock_data", 
            benchmark, 
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        cached_data['recommended']['benchmark_data'] = {
            'benchmark': benchmark,
            'data': str(benchmark_data),
            'timestamp': datetime.now().isoformat()
        }
        print(f"   ✅ Benchmark cached ({len(str(benchmark_data))} chars)")
    except Exception as e:
        print(f"   ⚠️  Benchmark caching failed: {str(e)[:50]}")
        cached_data['recommended']['benchmark_data'] = {'error': str(e)}
    
    # Sentiment data (may not be available)
    print(f"\n💬 Caching sentiment data...")
    cached_data['recommended']['sentiment_data'] = {
        'note': 'Sentiment data vendor-specific',
        'timestamp': datetime.now().isoformat()
    }
    print(f"   ⚠️  Sentiment data not implemented (vendor-specific)")
    
    # Sector data (may not be available)
    print(f"\n🏭 Caching sector data...")
    cached_data['recommended']['sector_data'] = {
        'note': 'Sector data vendor-specific', 
        'timestamp': datetime.now().isoformat()
    }
    print(f"   ⚠️  Sector data not implemented (vendor-specific)")
    
    # Save to file
    os.makedirs('validation_cache', exist_ok=True)
    cache_file = f'validation_cache/cached_data_{ticker}_{trade_date}.json'
    
    print(f"\n💾 Saving cached data...")
    with open(cache_file, 'w') as f:
        json.dump(cached_data, f, indent=2)
    
    print(f"✅ Cached data saved to: {cache_file}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("CACHE SUMMARY")
    print("=" * 80)
    
    market_ok = 'error' not in cached_data['mandatory']['market_data']
    fundamentals_ok = 'error' not in cached_data['mandatory']['fundamentals_data']
    news_ok = 'error' not in cached_data['mandatory']['news_data']
    macro_ok = 'error' not in cached_data['mandatory']['macro_data']
    benchmark_ok = 'error' not in cached_data['recommended']['benchmark_data']
    
    print(f"\n{'Data Source':<25} {'Status':<15} {'Size (chars)':<15}")
    print("─" * 55)
    print(f"{'[MANDATORY]':<25}")
    print(f"{'  Market Data':<25} {'✅ Cached' if market_ok else '❌ Failed':<15} {len(cached_data['mandatory']['market_data'].get('data', '')):>14,}")
    print(f"{'  Fundamentals':<25} {'✅ Cached' if fundamentals_ok else '❌ Failed':<15} {len(cached_data['mandatory']['fundamentals_data'].get('data', '')):>14,}")
    print(f"{'  Company News':<25} {'✅ Cached' if news_ok else '❌ Failed':<15} {len(cached_data['mandatory']['news_data'].get('company_news', '')):>14,}")
    print(f"{'  Global News':<25} {'✅ Cached' if news_ok else '❌ Failed':<15} {len(cached_data['mandatory']['news_data'].get('global_news', '')):>14,}")
    print(f"{'  Macro Data':<25} {'✅ Cached' if macro_ok else '❌ Failed':<15} {'Multiple' if macro_ok else 'N/A':>14}")
    print(f"{'[RECOMMENDED]':<25}")
    print(f"{'  Benchmark Data':<25} {'✅ Cached' if benchmark_ok else '⚠️  Partial':<15} {len(str(cached_data['recommended']['benchmark_data'].get('data', ''))):>14,}")
    print(f"{'  Sentiment Data':<25} {'⚠️  N/A':<15} {'N/A':>14}")
    print(f"{'  Sector Data':<25} {'⚠️  N/A':<15} {'N/A':>14}")
    
    mandatory_ok = market_ok and fundamentals_ok and news_ok and macro_ok
    
    print(f"\n{'Mandatory Status:':<25} {'✅ ALL CACHED' if mandatory_ok else '❌ INCOMPLETE'}")
    print(f"{'Recommended Status:':<25} {'✅ BENCHMARK OK' if benchmark_ok else '⚠️  PARTIAL'}")
    print(f"\n{'Overall Readiness:':<25} {'✅ READY FOR VALIDATION' if mandatory_ok else '❌ NOT READY'}")
    
    if not mandatory_ok:
        print("\n❌ VALIDATION CANNOT PROCEED")
        print("   Mandatory data sources failed. Fix errors before running validation.")
    else:
        print("\n✅ VALIDATION CAN PROCEED")
        print("   All mandatory data cached. Validation will be deterministic.")
    
    print(f"\n📁 Cache file: {cache_file}")
    print(f"   File size: {Path(cache_file).stat().st_size:,} bytes")
    print(f"\n🔒 Use with VALIDATION_CACHE_ONLY=true to ensure no live API calls")
    
    return cached_data, cache_file


def main():
    """Cache data for HDFCBANK.NS validation"""
    
    # Validation parameters
    ticker = "HDFCBANK.NS"
    trade_date = "2024-01-15"  # Historical date with stable data
    
    # Cache all data
    cached_data, cache_file = cache_all_data(ticker, trade_date)
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("\n1. Verify cache file exists and has data")
    print(f"   ls -lh {cache_file}")
    print("\n2. Run validation with cached data")
    print(f"   python validate_git_based.py")
    print("\n3. Both baseline and optimized runs will use this cached data")
    print("   ensuring fair A/B comparison")
    
    return cache_file


if __name__ == "__main__":
    try:
        cache_file = main()
        print(f"\n✅ Data caching complete: {cache_file}")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Caching failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
