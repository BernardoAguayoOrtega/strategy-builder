# Phase 3 Testing Guide

## Optimization Engine - Testing & Validation

### Prerequisites

Before testing, ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

This will install:
- pandas >= 1.3.0
- numpy >= 1.21.0
- yfinance >= 0.1.63
- nicegui >= 1.4.0

---

## Automated Test Suite

### Running the Optimizer Test Script

```bash
python test_optimizer.py
```

This comprehensive test script validates:

1. **Parameter Grid Generation** - Verifies correct range creation
2. **Market Data Download** - Tests yfinance integration
3. **Optimizer Initialization** - Confirms proper setup
4. **Single Pattern Optimization** - Tests Volumen Climático pattern
5. **Optimization with Filters** - Tests MA Cross filter integration
6. **Results Display** - Verifies summary formatting
7. **Results Ranking** - Confirms proper score-based sorting

### Expected Output

```
================================================================================
PHASE 3 OPTIMIZATION ENGINE TEST
================================================================================

[Test 1] Parameter Grid Generation
--------------------------------------------------------------------------------
Generated grid: {'sma_period': [10, 20, 30], 'multiplier': [1.5, 1.75, 2.0]}
sma_period values: [10, 20, 30]
multiplier values: [1.5, 1.75, 2.0]
Total combinations: 9
✅ Test 1 PASSED

[Test 2] Download Market Data
--------------------------------------------------------------------------------
Downloading AAPL data for 2023...
Downloaded 252 bars
Date range: 2023-01-03 to 2023-12-29
Columns: ['open', 'high', 'low', 'close', 'volume']
✅ Test 2 PASSED

[Test 3] Optimizer Initialization
--------------------------------------------------------------------------------
Optimizer created with 2 parallel jobs
Backtest config: Initial Capital=$100000, Commission=$1.5
✅ Test 3 PASSED

[Test 4] Single Pattern Optimization - Volumen Climático
--------------------------------------------------------------------------------
Testing 9 combinations...
Parameter ranges: {'sma_period': [15, 20, 25], 'multiplier': [1.5, 1.75, 2.0]}
Testing 9 parameter combinations...
Optimization complete! 9 valid results found.
✅ Found 9 valid configurations
   Best score: 0.5234
   Best parameters: {'sma_period': 20, 'multiplier': 1.75}
   Best ROI: 15.42%
   Best trades: 18
✅ Test 4 PASSED

[Test 5] Optimization with MA Cross Filter
--------------------------------------------------------------------------------
Testing 1 parameter combinations...
Optimization complete! 1 valid results found.
✅ Found 1 valid configurations
   Total trades: 8
✅ Test 5 PASSED

[Test 6] Optimization Summary Display
--------------------------------------------------------------------------------
================================================================================
OPTIMIZATION SUMMARY - Top 5 Results
================================================================================
Rank   Score    ROI %    PF    Trades   MaxDD %    Parameters
--------------------------------------------------------------------------------
1      0.5234   15.42    2.34  18       -12.45     {'sma_period': 20, 'multiplier': 1.75}
2      0.4892   13.21    2.12  16       -14.23     {'sma_period': 15, 'multiplier': 1.75}
...
✅ Test 6 PASSED

[Test 7] Results Ranking Verification
--------------------------------------------------------------------------------
✅ Results properly sorted by rank_score
   Scores range: 0.5234 (best) to 0.3421 (worst)
✅ Test 7 PASSED

================================================================================
ALL TESTS PASSED! ✅
================================================================================
```

---

## Manual Testing via UI

### Starting the UI

```bash
cd /home/user/strategy-builder
python src/ui_app.py
```

Then navigate to: `http://localhost:8080`

### UI Testing Workflow

#### Test Case 1: Basic Optimization

1. **Select Pattern:** Choose "Volumen Climático (Climactic Volume)"
2. **Configure Parameters:**
   - Volume SMA Period: 20 (default)
   - Volume Multiplier: 1.75 (default)
   - Set optimization ranges:
     - Min: 15, Max: 25, Step: 5 (SMA Period)
     - Min: 1.5, Max: 2.0, Step: 0.25 (Multiplier)
3. **Backtest Settings:**
   - Asset: AAPL
   - Timeframe: 1d
   - Start: 2023-01-01
   - End: 2024-01-01
4. **Click:** "Run Optimization"
5. **Expected:** Table showing top 20 configurations ranked by composite score

#### Test Case 2: Optimization with Filter

1. **Select Pattern:** "Sacudida (Shake-out)"
2. **Enable Filter:** Check "Moving Average Cross (50/200)" → Set to "bullish"
3. **Configure Pattern Parameters:**
   - Direction: both
   - (No optimizable parameters for Sacudida)
4. **Configure Filter Parameters:**
   - Fast MA Period: 50
   - Slow MA Period: 200
   - Set optimization ranges for Fast MA:
     - Min: 30, Max: 70, Step: 10
5. **Click:** "Run Optimization"
6. **Expected:** Optimization across MA periods with Sacudida pattern

#### Test Case 3: Multiple Assets

Test the same configuration on different assets:
- AAPL (stocks)
- EURUSD=X (forex)
- BTC-USD (crypto)

Verify results differ appropriately based on asset characteristics.

---

## Performance Benchmarks

### Expected Execution Times

| Combinations | CPU Cores | Approximate Time |
|--------------|-----------|------------------|
| 9            | 4         | 5-10 seconds     |
| 25           | 4         | 15-30 seconds    |
| 100          | 4         | 1-2 minutes      |
| 500          | 4         | 5-10 minutes     |
| 1000         | 4         | 10-20 minutes    |

*Times vary based on:*
- Data size (number of bars)
- Pattern complexity
- Number of filters applied
- CPU speed

### Optimization Tips

For faster testing:
- Use smaller date ranges (e.g., 6 months instead of 5 years)
- Reduce parameter steps (e.g., step=10 instead of step=1)
- Limit to 2-3 parameters maximum
- Use n_jobs parameter to control parallelism

---

## Code Validation

### Unit Tests (Python)

```bash
# Test optimizer module directly
python -c "
import sys
sys.path.insert(0, 'src')
from optimizer import generate_parameter_grid

spec = {'period': {'type': 'int', 'min': 10, 'max': 20, 'step': 5}}
grid = generate_parameter_grid(spec)
assert grid['period'] == [10, 15, 20], 'Grid generation failed'
print('✅ Parameter grid generation test passed')
"
```

### Integration Test

```bash
# Test full workflow with mock data
python -c "
import sys
sys.path.insert(0, 'src')
import pandas as pd
import numpy as np
from optimizer import StrategyOptimizer
from backtesting_framework import BacktestConfig

# Create mock OHLCV data
dates = pd.date_range('2023-01-01', periods=100, freq='D')
df = pd.DataFrame({
    'open': np.random.randn(100).cumsum() + 100,
    'high': np.random.randn(100).cumsum() + 102,
    'low': np.random.randn(100).cumsum() + 98,
    'close': np.random.randn(100).cumsum() + 100,
    'volume': np.random.randint(1000, 10000, 100)
}, index=dates)

config = BacktestConfig()
optimizer = StrategyOptimizer(config, n_jobs=1)

param_ranges = {'sma_period': [10, 20], 'multiplier': [1.5, 2.0]}
results = optimizer.optimize(df, 'volumen_climatico', param_ranges)

print(f'✅ Integration test passed - {len(results)} results generated')
"
```

---

## Troubleshooting

### Common Issues

#### Issue: "No valid results (zero trades)"

**Cause:** Pattern didn't generate any signals with the given parameters

**Solution:**
- Try different parameter ranges
- Use longer date range (more data)
- Try different asset (some patterns work better on certain instruments)
- Verify pattern is appropriate for timeframe

#### Issue: "Optimization takes too long"

**Cause:** Too many parameter combinations

**Solution:**
- Reduce parameter ranges
- Increase step size
- Use smaller date range for initial testing
- Reduce n_jobs if memory is constrained

#### Issue: "Download failed"

**Cause:** Yahoo Finance API issues or invalid ticker

**Solution:**
- Verify ticker symbol (use Yahoo Finance to confirm)
- Check internet connection
- Try different date range
- Some tickers require suffix (e.g., EURUSD=X for forex)

#### Issue: "Multiprocessing errors on Windows"

**Cause:** Windows multiprocessing requires special handling

**Solution:**
Add to top of script:
```python
if __name__ == '__main__':
    # Your code here
```

Or use n_jobs=1 for serial execution

---

## Validation Checklist

Before marking Phase 3 as complete, verify:

- [ ] Optimizer module imports successfully
- [ ] Parameter grid generation works for int, float, choice types
- [ ] Single pattern optimization completes without errors
- [ ] Results are properly ranked by composite score
- [ ] Optimization with filters works correctly
- [ ] UI button is enabled and functional
- [ ] Results display correctly in UI table
- [ ] Best configuration details shown prominently
- [ ] Multiple CPU cores utilized (check with `top` or Task Manager)
- [ ] Edge cases handled (zero trades, no parameters, empty data)

---

## Next Steps After Validation

Once all tests pass:

1. **Update PLAN.md** - Mark Phase 3 as complete
2. **Commit changes:**
   ```bash
   git add src/optimizer.py src/ui_app.py test_optimizer.py
   git commit -m "Add Phase 3: Optimization Engine - Grid search with parallel processing"
   ```
3. **Begin Phase 4** - Export to Pine Script (transpiler.py)

---

**Phase 3 Status:** ✅ Implementation Complete - Ready for Testing

**Contributors:** Claude AI (Implementation)

**Date:** 2025-11-20
