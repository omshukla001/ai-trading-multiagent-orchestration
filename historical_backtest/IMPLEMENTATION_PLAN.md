# Phase 4 Historical Backtesting - Implementation Plan

**Date**: July 6, 2026  
**Status**: Stage 1 In Progress  
**Target**: 20 trades for framework validation

---

## Implementation Architecture

```
historical_backtest/
├── __init__.py                    ✅ Created
├── data_collection/
│   ├── __init__.py
│   ├── historical_data_collector.py   # Fetches historical data
│   ├── point_in_time_reconstructor.py # Ensures no future leakage
│   └── data_limitations.md            # Documents data constraints
├── snapshot_engine/
│   ├── __init__.py
│   ├── snapshot_creator.py            # Creates immutable snapshots
│   ├── snapshot_validator.py          # Validates snapshot integrity
│   └── snapshot_loader.py             # Loads snapshots for replay
├── replay_engine/
│   ├── __init__.py
│   ├── historical_replay.py           # Replays through full workflow
│   ├── validation_mode.py             # Validation-only configuration
│   └── agent_ablation.py              # Agent contribution measurement
├── execution_simulator/
│   ├── __init__.py
│   ├── trade_simulator.py             # Simulates realistic execution
│   ├── cost_calculator.py             # Brokerage, fees, slippage
│   └── portfolio_tracker.py           # Tracks capital, exposure
├── exit_engine/
│   ├── __init__.py
│   ├── exit_evaluator.py              # Evaluates exit conditions
│   └── exit_simulator.py              # Simulates exits
├── benchmarks/
│   ├── __init__.py
│   ├── buy_and_hold.py
│   ├── technical_strategies.py        # EMA, RSI, MACD, etc.
│   └── random_strategy.py             # Control baseline
├── metrics/
│   ├── __init__.py
│   ├── performance_calculator.py      # Returns, Sharpe, etc.
│   ├── trade_analyzer.py              # Win rate, profit factor
│   └── drawdown_calculator.py         # Max DD, recovery
├── agent_analysis/
│   ├── __init__.py
│   ├── agent_tracker.py               # Tracks all agent outputs
│   └── contribution_measurer.py       # Measures agent impact
├── trade_analysis/
│   ├── __init__.py
│   ├── failure_analyzer.py            # Analyzes losing trades
│   ├── success_analyzer.py            # Analyzes winning trades
│   └── confidence_calibrator.py       # AI vs actual performance
├── reports/
│   ├── __init__.py
│   ├── report_generator.py            # Generates all reports
│   ├── visualization.py               # Charts and graphs
│   └── templates/                     # Report templates
└── tests/
    ├── __init__.py
    ├── test_snapshot_engine.py
    ├── test_replay_engine.py
    ├── test_execution_simulator.py
    ├── test_benchmarks.py
    ├── test_data_leakage.py
    └── test_end_to_end.py
```

---

## Stage 1: 20 Trades Implementation

### Phase 1: Data Collection (Now)

**File**: `data_collection/historical_data_collector.py`

Features:
- Fetches historical price data (OHLCV) from Yahoo Finance
- Retrieves historical fundamentals (if available)
- Collects historical news (within API limitations)
- Documents data limitations

**File**: `data_collection/point_in_time_reconstructor.py`

Features:
- Ensures no future data leakage
- Creates point-in-time snapshots
- Validates date boundaries

### Phase 2: Snapshot Engine

**File**: `snapshot_engine/snapshot_creator.py`

Features:
- Creates immutable JSON snapshots for each trade date
- Includes market, fundamentals, news, macro data
- Timestamps and versioning

**File**: `snapshot_engine/snapshot_validator.py`

Features:
- Validates snapshot completeness
- Checks for data leakage
- Verifies data integrity

### Phase 3: Replay Engine

**File**: `replay_engine/historical_replay.py`

Features:
- Loads snapshot
- Initializes TradingAgents graph
- Routes all data requests to snapshot (no live APIs)
- Captures all agent outputs
- Returns complete trade decision

**File**: `replay_engine/validation_mode.py`

Features:
- Configuration layer for validation
- Disables live API calls
- Routes dataflows to snapshots
- Enables agent ablation mode

### Phase 4: Execution Simulator

**File**: `execution_simulator/trade_simulator.py`

Features:
- Initial capital: ₹20,00,000
- Position sizing from Risk Engine
- Realistic execution simulation
- Tracks portfolio state

**File**: `execution_simulator/cost_calculator.py`

Features:
- Brokerage: 0.03% or ₹20 per trade
- STT: 0.025% on sell side
- Exchange charges: ~0.00325%
- GST: 18% on brokerage
- SEBI charges: ₹10 per crore
- Stamp duty: 0.003% on buy
- Slippage: 0.05-0.1% (market dependent)

### Phase 5: Exit Engine

**File**: `exit_engine/exit_evaluator.py`

Features:
- Monitors price movement
- Checks target hit
- Checks stop hit
- Maximum holding period: 30 days
- Uses Trader's specified targets/stops

### Phase 6: Benchmark Strategies

**File**: `benchmarks/buy_and_hold.py`

Features:
- Buy at start of period
- Hold until end
- Same capital, same costs

**File**: `benchmarks/technical_strategies.py`

Features:
- EMA 20/50 crossover
- RSI (30/70) strategy
- MACD crossover
- SuperTrend
- All use same execution costs

### Phase 7: Performance Metrics

**File**: `metrics/performance_calculator.py`

Calculates:
- Total return
- CAGR
- Sharpe ratio
- Sortino ratio
- Calmar ratio
- Win rate
- Profit factor
- Expectancy
- Maximum drawdown

### Phase 8: Trade Analysis

**File**: `trade_analysis/failure_analyzer.py`

For each losing trade:
- Reason for failure
- Technical failure?
- Fundamental failure?
- News-driven?
- Clusters failures by pattern

**File**: `trade_analysis/success_analyzer.py`

For winning trades:
- Common setups
- Best sectors
- Optimal holding periods

### Phase 9: Agent Analysis

**File**: `agent_analysis/agent_tracker.py`

Captures for every trade:
- Market report
- Fundamentals report
- News report
- Bull report
- Bear report
- Research Manager synthesis
- Trader proposal
- Risk Engine output
- Portfolio Manager decision

Stores all intermediate outputs.

### Phase 10: Reports

**File**: `reports/report_generator.py`

Generates:
- `BACKTEST_REPORT.md` - Overall performance
- `TRADE_LOG.csv` - Every trade detail
- `BENCHMARK_COMPARISON.md` - vs all benchmarks
- `PERFORMANCE_METRICS.csv` - All metrics
- `AGENT_ANALYSIS.md` - Agent contributions
- `FAILURE_ANALYSIS.md` - Losing trades analysis
- `SUCCESS_ANALYSIS.md` - Winning trades analysis
- `CONFIDENCE_ANALYSIS.md` - AI calibration
- `FINAL_CONCLUSION.md` - Evidence-based conclusion

---

## Stage 1 Execution Plan

### Step 1: Select 20 Historical Dates ✅ Next

Select 20 trading dates from 2024 (recent, stable data):
- 5 dates from Jan-Mar 2024
- 5 dates from Apr-Jun 2024
- 5 dates from Jul-Sep 2024
- 5 dates from Oct-Dec 2024

Stocks: HDFCBANK.NS, RELIANCE.NS, INFY.NS (Indian market, good liquidity)

### Step 2: Collect Historical Data

For each date:
- Market data (90 days prior)
- Fundamentals (if available)
- News (7 days prior)
- Macro indicators

Store in `historical_backtest/data/stage1/`

### Step 3: Create Snapshots

For each of 20 dates:
- Create immutable snapshot
- Validate no future data
- Store in `historical_backtest/snapshots/stage1/`

### Step 4: Replay Through Workflow

For each snapshot:
- Load snapshot
- Initialize graph (Phase 3A optimized)
- Route all data to snapshot
- Capture all outputs
- Store decision

### Step 5: Simulate Execution

For each decision:
- Calculate position size
- Apply costs
- Simulate entry
- Monitor for 30 days
- Simulate exit
- Calculate P&L

### Step 6: Calculate Metrics

- Win rate
- Total return
- Average trade
- Max drawdown

### Step 7: Generate Report

- Stage 1 validation report
- Framework correctness check
- Data quality assessment
- Proceed to Stage 2 decision

---

## Testing Strategy

### Unit Tests

- `test_snapshot_engine.py` - Snapshot creation/loading
- `test_replay_engine.py` - Historical replay
- `test_execution_simulator.py` - Trade simulation
- `test_benchmarks.py` - Benchmark strategies

### Integration Tests

- `test_end_to_end.py` - Full workflow test
- `test_data_leakage.py` - Validates no future data

### Regression Tests

- Validates consistent results
- Tests deterministic replay

---

## Validation Modes

### Mode 1: Optimized (Phase 3A)

- 2 debate rounds
- Concise prompts
- Output limits
- Current optimized state

### Mode 2: Baseline (Pre-Phase-3A)

- 3 debate rounds
- Verbose prompts
- No output limits
- Git stash to restore baseline

Both modes use **identical snapshots**.

---

## Data Limitations (Stage 1)

### Expected Limitations

1. **Historical Fundamentals**: May not reflect exact values as of trade date
   - Document limitation in report
   - Use best available historical data

2. **Historical News**: Limited by API lookback
   - Document what's available
   - Note any gaps

3. **Point-in-Time Revisions**: Financial data may be revised
   - Document limitation
   - Use data as currently available

4. **Sentiment Data**: May not have historical snapshots
   - Skip if unavailable
   - Document in limitations

### Documentation

All limitations documented in:
- `data_collection/DATA_LIMITATIONS.md`
- Section in final report

---

## Success Criteria - Stage 1

### Framework Validation

- [ ] 20 snapshots created successfully
- [ ] 20 replays execute without errors
- [ ] 20 trades simulated with realistic costs
- [ ] All agent outputs captured
- [ ] Metrics calculated correctly
- [ ] Reports generated
- [ ] No data leakage detected
- [ ] Tests pass (unit + integration)

### Data Quality

- [ ] Market data available for all 20 dates
- [ ] Fundamentals available (or documented if missing)
- [ ] News available (within limitations)
- [ ] No future data contamination

### Output Quality

- [ ] BACKTEST_REPORT.md generated
- [ ] TRADE_LOG.csv complete
- [ ] BENCHMARK_COMPARISON.md present
- [ ] FINAL_CONCLUSION.md with evidence

---

## Stage 1 Timeline

**Estimated**: 4-6 hours implementation + 1-2 hours testing

1. **Data Collection** (1 hour)
   - Implement collectors
   - Fetch 20 dates of data
   - Validate availability

2. **Snapshot Engine** (1 hour)
   - Implement snapshot creation
   - Create 20 snapshots
   - Validate integrity

3. **Replay Engine** (1.5 hours)
   - Implement validation mode
   - Implement historical replay
   - Test with 1 snapshot

4. **Execution Simulator** (1 hour)
   - Implement trade simulator
   - Implement cost calculator
   - Test with mock trades

5. **Exit Engine** (30 min)
   - Implement exit evaluator
   - Test exit logic

6. **Benchmarks** (30 min)
   - Implement buy & hold
   - Implement one technical strategy

7. **Metrics** (30 min)
   - Implement performance calculator
   - Calculate basic metrics

8. **Reports** (30 min)
   - Implement report generator
   - Generate Stage 1 report

9. **Testing** (1-2 hours)
   - Write unit tests
   - Write integration tests
   - Run full test suite
   - Fix any issues

---

## Proceeding with Implementation

Building components in order:

1. ✅ Framework structure created
2. ⏳ Data collection module (NEXT)
3. ⏳ Snapshot engine
4. ⏳ Replay engine
5. ⏳ Execution simulator
6. ⏳ Exit engine
7. ⏳ Benchmarks
8. ⏳ Metrics
9. ⏳ Reports
10. ⏳ Tests

**No pausing for design questions - implementing incrementally as specified.**

---

**Implementation Start**: July 6, 2026, 01:03 IST  
**Current Status**: Building data collection module
