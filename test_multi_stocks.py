"""
Multi-Stock Testing Script for Indian Markets
Tests TradingAgents across different sectors without modifications
"""
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from datetime import datetime, timedelta
import json
import os

# Configure for Google Gemini
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "google"
config["deep_think_llm"] = "gemini-3.5-flash"
config["quick_think_llm"] = "gemini-3.5-flash"
config["max_debate_rounds"] = 1
config["max_risk_rounds"] = 1

# Define test stocks by sector
TEST_STOCKS = {
    "Banking": ["HDFCBANK.NS", "ICICIBANK.NS"],
    "IT": ["TCS.NS", "INFY.NS"],
    "Defence": ["BEL.NS", "HAL.NS"],
    "Energy": ["RELIANCE.NS", "ONGC.NS"],
    "Momentum": ["TATAPOWER.NS", "ADANIENT.NS"]
}

# Use recent date for analysis
analysis_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

print("=" * 80)
print("TRADINGAGENTS INDIAN MARKET TESTING FRAMEWORK")
print("=" * 80)
print(f"\nTest Date: {analysis_date}")
print(f"Total Stocks to Test: {sum(len(stocks) for stocks in TEST_STOCKS.values())}")
print(f"Capital: ₹2,00,000")
print(f"Trading Style: Swing Trading (3-14 days)")
print("\n" + "=" * 80)

# Initialize TradingAgents
print("\nInitializing TradingAgents...")
ta = TradingAgentsGraph(debug=False, config=config)
print("✓ Ready\n")

# Results storage
results = []
results_dir = "test_results"
os.makedirs(results_dir, exist_ok=True)

# Test each stock
for sector, stocks in TEST_STOCKS.items():
    print("\n" + "=" * 80)
    print(f"SECTOR: {sector}")
    print("=" * 80)
    
    for ticker in stocks:
        print(f"\n--- Testing: {ticker} ---")
        
        try:
            # Run analysis
            _, decision = ta.propagate(ticker, analysis_date)
            
            # Parse the decision
            result = {
                "ticker": ticker,
                "sector": sector,
                "analysis_date": analysis_date,
                "decision": decision,
                "status": "SUCCESS"
            }
            
            # Save individual result
            output_file = f"{results_dir}/{ticker.replace('.', '_')}_{analysis_date}.txt"
            with open(output_file, 'w') as f:
                f.write(f"STOCK: {ticker}\n")
                f.write(f"SECTOR: {sector}\n")
                f.write(f"DATE: {analysis_date}\n")
                f.write("=" * 80 + "\n\n")
                f.write(decision)
            
            print(f"✓ Analysis complete → {output_file}")
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            result = {
                "ticker": ticker,
                "sector": sector,
                "analysis_date": analysis_date,
                "error": str(e),
                "status": "FAILED"
            }
        
        results.append(result)

# Save summary
summary_file = f"{results_dir}/summary_{analysis_date}.json"
with open(summary_file, 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 80)
print("TESTING COMPLETE")
print("=" * 80)
print(f"\nResults saved to: {results_dir}/")
print(f"Summary: {summary_file}")
print(f"\nSuccessful: {sum(1 for r in results if r['status'] == 'SUCCESS')}/{len(results)}")
print(f"Failed: {sum(1 for r in results if r['status'] == 'FAILED')}/{len(results)}")
