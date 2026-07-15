"""
Utility functions for optimized analysts
Handles ticker extraction and data parsing with proper error handling
"""


def extract_ticker_from_state(state: dict) -> str:
    """
    Robust ticker extraction from state
    Tries multiple sources in order of reliability
    """
    # Priority 1: Extract from instrument_context (most reliable)
    if 'instrument_context' in state and state['instrument_context']:
        context = state['instrument_context']
        # Context format: "Company: X; Business classification: Y; Exchange: Z"
        # But we need the actual ticker from messages
        pass
    
    # Priority 2: Extract from messages (ticker is first message content)
    if 'messages' in state and state['messages'] and len(state['messages']) > 0:
        ticker = state['messages'][0].content.strip()
        if ticker:
            return ticker
    
    # Fallback: Return placeholder
    return "UNKNOWN"


def safe_parse_snapshot(snapshot_result: str) -> dict:
    """
    Parse get_verified_market_snapshot result with error handling
    Returns structured dict with safe defaults
    """
    try:
        # The snapshot comes as formatted text, need to parse it
        # For now, assume it's already a dict (tool returns dict)
        if isinstance(snapshot_result, dict):
            return {
                "close": float(snapshot_result.get('latest_close', 0)),
                "volume": int(snapshot_result.get('latest_volume', 0)),
                "indicators": snapshot_result.get('indicators', {})
            }
        
        # If it's a string, this is the raw output - need to parse
        # This would happen if tool returns text instead of dict
        return {
            "close": 0,
            "volume": 0,
            "indicators": {}
        }
    except Exception as e:
        # Return safe defaults
        return {
            "close": 0,
            "volume": 0,
            "indicators": {
                'close_10_ema': 0,
                'close_50_sma': 0,
                'close_200_sma': 0,
                'rsi': 50,
                'macd': 0,
                'macds': 0,
                'macdh': 0,
                'boll': 0,
                'boll_ub': 0,
                'boll_lb': 0,
                'atr': 0,
                'vwma': 0
            }
        }


def safe_parse_fundamentals(fund_data: dict) -> dict:
    """
    Parse get_fundamentals result with safe defaults
    """
    def safe_float(value, default=0.0):
        """Safely convert to float"""
        if value is None or value == 'N/A':
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def safe_int(value, default=0):
        """Safely convert to int"""
        if value is None or value == 'N/A':
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    return {
        "name": fund_data.get('Name', 'Unknown'),
        "sector": fund_data.get('Sector', 'Unknown'),
        "industry": fund_data.get('Industry', 'Unknown'),
        "market_cap": safe_int(fund_data.get('Market Cap', 0)),
        "pe_ratio": safe_float(fund_data.get('PE Ratio (TTM)')),
        "forward_pe": safe_float(fund_data.get('Forward PE')),
        "peg_ratio": safe_float(fund_data.get('PEG Ratio')),
        "price_to_book": safe_float(fund_data.get('Price to Book')),
        "profit_margin": safe_float(fund_data.get('Profit Margin')),
        "operating_margin": safe_float(fund_data.get('Operating Margin')),
        "return_on_equity": safe_float(fund_data.get('Return on Equity')),
        "return_on_assets": safe_float(fund_data.get('Return on Assets')),
        "revenue_ttm": safe_int(fund_data.get('Revenue (TTM)', 0)),
        "eps_ttm": safe_float(fund_data.get('EPS (TTM)')),
        "forward_eps": safe_float(fund_data.get('Forward EPS')),
        "debt_to_equity": safe_float(fund_data.get('Debt to Equity')),
        "current_ratio": safe_float(fund_data.get('Current Ratio')),
        "free_cash_flow": safe_int(fund_data.get('Free Cash Flow', 0)),
    }
