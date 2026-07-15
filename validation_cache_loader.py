"""
Validation Cache Loader

Replaces live API calls with cached data during validation.

When VALIDATION_CACHE_ONLY=true:
- All dataflows route to cached data
- Any attempted live API call aborts validation
- Guarantees deterministic replay
"""

import json
import os
from pathlib import Path
from typing import Any, Optional


class ValidationCacheLoader:
    """Loads and serves cached validation data"""
    
    def __init__(self, cache_file: str):
        """
        Initialize cache loader
        
        Args:
            cache_file: Path to cached data JSON file
        """
        self.cache_file = cache_file
        self.cached_data = None
        self.strict_mode = os.environ.get('VALIDATION_CACHE_ONLY', 'false').lower() == 'true'
        self.load_cache()
    
    def load_cache(self):
        """Load cached data from file"""
        cache_path = Path(self.cache_file)
        
        if not cache_path.exists():
            raise FileNotFoundError(
                f"Cache file not found: {self.cache_file}\n"
                f"Run cache_validation_data.py first to generate cache."
            )
        
        with open(cache_path) as f:
            self.cached_data = json.load(f)
        
        print(f"✅ Loaded validation cache: {self.cache_file}")
        print(f"   Trade date: {self.cached_data['metadata']['trade_date']}")
        print(f"   Ticker: {self.cached_data['metadata']['ticker']}")
        print(f"   Strict mode: {'YES' if self.strict_mode else 'NO'}")
    
    def get_stock_data(self, ticker: str, start_date: str, end_date: str) -> str:
        """Get cached market data"""
        
        market_data = self.cached_data['mandatory']['market_data']
        
        if 'error' in market_data:
            raise ValueError(f"Cached market data has error: {market_data['error']}")
        
        # Verify ticker matches
        if market_data['ticker'] != ticker:
            # Check if it's benchmark data
            benchmark_data = self.cached_data['recommended'].get('benchmark_data', {})
            if benchmark_data.get('benchmark') == ticker:
                return benchmark_data.get('data', '')
            
            if self.strict_mode:
                raise ValueError(
                    f"Ticker mismatch in cache: requested {ticker}, cached {market_data['ticker']}"
                )
        
        return market_data.get('data', '')
    
    def get_financial_statements(self, ticker: str) -> str:
        """Get cached fundamentals data"""
        
        fundamentals = self.cached_data['mandatory']['fundamentals_data']
        
        if 'error' in fundamentals:
            raise ValueError(f"Cached fundamentals has error: {fundamentals['error']}")
        
        return fundamentals.get('data', '')
    
    def get_news(self, ticker: str, start_date: str, end_date: str) -> str:
        """Get cached news data"""
        
        news_data = self.cached_data['mandatory']['news_data']
        
        if 'error' in news_data:
            raise ValueError(f"Cached news has error: {news_data['error']}")
        
        return news_data.get('company_news', '')
    
    def get_global_news(self, curr_date: str, look_back_days: Optional[int] = None, 
                        limit: Optional[int] = None) -> str:
        """Get cached global news"""
        
        news_data = self.cached_data['mandatory']['news_data']
        
        if 'error' in news_data:
            raise ValueError(f"Cached news has error: {news_data['error']}")
        
        return news_data.get('global_news', '')
    
    def get_macro_indicators(self, indicator: str, curr_date: str, 
                            look_back_days: Optional[int] = None) -> str:
        """Get cached macro indicators"""
        
        macro_data = self.cached_data['mandatory']['macro_data']
        
        if 'error' in macro_data:
            if self.strict_mode:
                raise ValueError(f"Cached macro data has error: {macro_data['error']}")
            return f"Macro data not available: {indicator}"
        
        indicators = macro_data.get('indicators', {})
        return indicators.get(indicator, f"Indicator not cached: {indicator}")
    
    def route_to_cached_data(self, tool_name: str, *args, **kwargs) -> str:
        """
        Route data request to cached data
        
        Args:
            tool_name: Name of the data tool/vendor
            *args, **kwargs: Tool parameters
        
        Returns:
            Cached data string
        
        Raises:
            ValueError: If tool not supported or cache missing data
        """
        
        if tool_name == "get_stock_data":
            return self.get_stock_data(*args)
        elif tool_name == "get_financial_statements":
            return self.get_financial_statements(*args)
        elif tool_name == "get_news":
            return self.get_news(*args)
        elif tool_name == "get_global_news":
            return self.get_global_news(*args, **kwargs)
        elif tool_name == "get_macro_indicators":
            return self.get_macro_indicators(*args, **kwargs)
        elif tool_name == "get_prediction_markets":
            # Prediction markets may not be cached (optional)
            if self.strict_mode:
                return "Prediction markets data not available in validation cache"
            raise ValueError(f"Prediction markets not cached")
        else:
            error_msg = f"Unsupported data tool in validation cache: {tool_name}"
            if self.strict_mode:
                raise ValueError(
                    f"{error_msg}\n"
                    f"VALIDATION_CACHE_ONLY mode - all data must be cached"
                )
            raise ValueError(error_msg)


def install_cache_loader(cache_file: str) -> ValidationCacheLoader:
    """
    Install validation cache loader to intercept dataflows
    
    Args:
        cache_file: Path to cached data JSON
    
    Returns:
        ValidationCacheLoader instance
    """
    
    loader = ValidationCacheLoader(cache_file)
    
    # Monkey-patch route_to_vendor to use cached data
    try:
        from tradingagents.dataflows import interface
        
        # Store original function
        original_route = interface.route_to_vendor
        
        # Create wrapper that routes to cache
        def cached_route(tool_name: str, *args, **kwargs) -> str:
            """Wrapper that routes to cached data"""
            try:
                return loader.route_to_cached_data(tool_name, *args, **kwargs)
            except ValueError as e:
                if loader.strict_mode:
                    print(f"\n❌ VALIDATION_CACHE_ONLY violation!")
                    print(f"   Attempted live API call: {tool_name}")
                    print(f"   Error: {str(e)}")
                    raise RuntimeError(
                        f"Live API call attempted in VALIDATION_CACHE_ONLY mode: {tool_name}\n"
                        f"Aborting validation to maintain determinism."
                    ) from e
                # Fall back to original if not strict mode
                return original_route(tool_name, *args, **kwargs)
        
        # Replace with cached version
        interface.route_to_vendor = cached_route
        
        print("✅ Validation cache loader installed")
        print("   All dataflows will use cached data")
        if loader.strict_mode:
            print("   🔒 STRICT MODE: Live API calls will abort validation")
        
    except ImportError as e:
        print(f"⚠️  Could not install cache loader: {e}")
        print("   Dataflows may still call live APIs")
    
    return loader


def uninstall_cache_loader():
    """Restore original dataflows (if needed for cleanup)"""
    # This would restore the original route_to_vendor
    # Implementation depends on how we store the original
    pass


# Global cache loader instance
_cache_loader: Optional[ValidationCacheLoader] = None


def get_cache_loader() -> Optional[ValidationCacheLoader]:
    """Get global cache loader instance"""
    return _cache_loader


def set_cache_loader(loader: ValidationCacheLoader):
    """Set global cache loader instance"""
    global _cache_loader
    _cache_loader = loader
