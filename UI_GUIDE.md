# Dynamic Strategy Builder UI - User Guide

## Overview

The Dynamic Strategy Builder UI is a web-based interface that allows non-technical users to configure, test, and optimize algorithmic trading strategies without writing code.

**Key Innovation:** The UI automatically discovers and renders all available components by introspecting the `builder_framework.py` module at runtime. This means adding a new pattern or filter to the Python code instantly makes it available in the UI.

## Installation

### Prerequisites

```bash
# Install Python 3.8 or higher
python --version

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

The main dependencies are:
- **pandas/numpy**: Data processing
- **yfinance**: Market data download
- **nicegui**: Web UI framework
- **matplotlib/seaborn**: Visualization (Phase 3+)

## Running the UI

### Start the Web Server

```bash
# From the strategy-builder directory
python src/ui_app.py
```

### Access the Interface

Open your browser and navigate to:
```
http://localhost:8080
```

The UI will automatically start on port 8080. If you need a different port, edit `src/ui_app.py` and change:

```python
ui.run(port=8080)  # Change to your desired port
```

## Using the UI

### Step 1: Select Components

The UI is organized into three panels. The left panel shows all available components:

#### Entry Patterns (Select ONE)

These are the core trading patterns that generate buy/sell signals:

- **Sacudida (Shake-out)**: False breakout reversal pattern
- **Envolvente (Engulfing)**: Classic candlestick engulfing pattern
- **Volumen Climático (Climactic Volume)**: High volume spike pattern

*You must select exactly one entry pattern to run a backtest.*

#### Filters (Select MULTIPLE)

Optional filters that refine when trades are taken:

- **MA Cross Filter**: Only trade in the direction of the trend (50/200 SMA)
- **RSI Filter**: Only trade in oversold/overbought conditions

*Filters are optional. You can enable 0, 1, or multiple filters.*

#### Trading Sessions (Select MULTIPLE)

Optional time-of-day filters:

- **London Session**: 01:00 - 08:15 UTC
- **New York Session**: 08:15 - 15:45 UTC
- **Tokyo Session**: 15:45 - 01:00 UTC

*Sessions are optional. If none are selected, trades are allowed 24/7.*

### Step 2: Configure Parameters

The middle panel dynamically renders parameters based on your selections.

**Example: Sacudida Pattern Parameters**

- **Direction**: Choose 'long', 'short', or 'both'

**Example: MA Cross Filter Parameters**

- **Filter Mode**: Choose 'no_filter', 'bullish', or 'bearish'
- **Fast MA Period**: 10-100 (default: 50)
- **Slow MA Period**: 100-300 (default: 200)

**Optimizable Parameters**

Some parameters show additional "Optimize range" fields:

```
Fast MA Period: 50
Optimize range:
  Min: 20
  Max: 100
  Step: 5
```

These ranges are used in Phase 3 (Grid Search Optimization).

### Step 3: Run Backtest

The right panel configures the backtest:

#### Market Data

- **Asset Symbol**: Stock ticker, forex pair, or crypto
  - Examples: `AAPL`, `EURUSD=X`, `BTC-USD`
- **Timeframe**: Choose from 1m, 5m, 15m, 30m, 1h, 1d, 1wk
- **Date Range**: Start and end dates for historical data

#### Backtest Settings

- **Initial Capital**: Starting equity (default: $100,000)
- **Commission per Trade**: Transaction cost (default: $1.50)
- **Slippage**: Price slippage in pips (default: 1.0)

#### Run the Test

Click **"Run Single Backtest"** to execute.

The UI will:
1. Download market data from Yahoo Finance
2. Apply your selected pattern and filters
3. Simulate trades with realistic costs
4. Display performance metrics

### Step 4: Review Results

The bottom panel shows comprehensive results:

#### Performance Summary

- **Total Trades**: Number of trades executed
- **Win Rate**: Percentage of winning trades
- **Profit Factor**: Gross profit / Gross loss
- **ROI**: Return on investment (%)
- **Max Drawdown**: Largest equity decline (%)
- **Sharpe Ratio**: Risk-adjusted return metric
- **Avg Win**: Average winning trade size ($)
- **Avg Loss**: Average losing trade size ($)

#### Trade Statistics

- **Winning Trades**: Count of profitable trades
- **Losing Trades**: Count of losing trades
- **Total P&L**: Net profit/loss ($)

#### Trade Log

Shows the last 10 trades with details:
- Entry/Exit bars
- Direction (long/short)
- Entry/Exit prices
- P&L
- Exit reason (stop_loss, take_profit, etc.)

## Dynamic Discovery in Action

### How It Works

The UI uses Python's introspection capabilities to discover components at runtime:

```python
# In builder_framework.py
@component(
    category='entry_pattern',
    name='my_new_pattern',
    display_name='My New Pattern',
    description='This pattern does X, Y, Z',
    parameters={
        'threshold': {
            'type': 'int',
            'min': 1,
            'max': 100,
            'default': 50,
            'display_name': 'Threshold',
            'description': 'Threshold for pattern detection'
        }
    }
)
def pattern_my_new_pattern(df, threshold=50):
    # Implementation here
    pass
```

**Result:** The UI instantly shows:
- A new radio button: "My New Pattern"
- Description text explaining what it does
- A number input for the "Threshold" parameter
- Min/Max validation (1-100)
- Default value (50)

### What Gets Rendered

The UI renders widgets based on parameter types:

| Parameter Type | UI Widget | Example |
|---------------|-----------|---------|
| `int` | Number input with stepper | SMA Period: 50 |
| `float` | Number input with decimal | Multiplier: 1.75 |
| `choice` | Dropdown select | Direction: [long, short, both] |
| `bool` | Checkbox | Enabled: ☑ |

### Optimizable Parameters

Parameters marked with `'optimizable': True` get additional UI:

```python
'fast_period': {
    'type': 'int',
    'min': 10,
    'max': 100,
    'default': 50,
    'optimizable': True  # ← This adds optimization range inputs
}
```

**UI renders:**
```
Fast MA Period: 50
Optimize range:
  Min: [20]
  Max: [100]
  Step: [5]
```

In Phase 3, these ranges will be used for grid search optimization.

## Testing Assets

### Stocks
```
AAPL    - Apple Inc.
MSFT    - Microsoft
TSLA    - Tesla
SPY     - S&P 500 ETF
```

### Forex (append =X)
```
EURUSD=X  - Euro/US Dollar
GBPUSD=X  - British Pound/US Dollar
USDJPY=X  - US Dollar/Japanese Yen
```

### Crypto (append -USD)
```
BTC-USD   - Bitcoin
ETH-USD   - Ethereum
SOL-USD   - Solana
```

## Troubleshooting

### Issue: "No data found for symbol"

**Cause:** Invalid ticker symbol or no data for date range

**Solution:**
- Verify ticker symbol on Yahoo Finance
- Try a different date range
- For forex, ensure you use `EURUSD=X` format
- For crypto, ensure you use `BTC-USD` format

### Issue: "No trades executed"

**Cause:** Pattern conditions never met, or all signals filtered out

**Solutions:**
- Check if filters are too restrictive
- Try a different timeframe (patterns work differently on 1m vs 1d)
- Try a different asset (some patterns work better on volatile assets)
- Adjust pattern parameters

### Issue: "Error downloading data"

**Cause:** Network issue or Yahoo Finance rate limiting

**Solutions:**
- Check internet connection
- Wait a few minutes and try again
- Try a shorter date range
- Use a different asset

### Issue: UI doesn't show new component

**Cause:** Component not registered or server not restarted

**Solutions:**
- Verify `@component` decorator is used
- Check component is not commented out
- Restart the UI server (Ctrl+C, then `python src/ui_app.py`)
- Check console for Python errors

## Advanced Usage

### Custom Backtest Settings

Edit these values in the right panel:

**Higher Initial Capital:**
- Useful for testing institutional-scale strategies
- Default: $100,000
- Range: $1,000 - $10,000,000

**Commission Adjustments:**
- Stocks: $1-5 per trade
- Forex: $0 (spread included in price)
- Futures: $1-10 per contract

**Slippage Adjustments:**
- Liquid assets (AAPL, SPY): 0.5-1.0 pips
- Illiquid assets: 2-5 pips
- Crypto: 1-3 pips

### Multiple Filters

You can combine filters for stricter entry conditions:

**Example: Conservative Strategy**
- Entry Pattern: Sacudida (Shake-out)
- Filters:
  - ☑ MA Cross Filter (mode: bullish)
  - ☑ RSI Filter (oversold: 30, overbought: 70)

**Result:** Only takes long trades when:
1. Sacudida pattern appears
2. Fast MA > Slow MA (bullish trend)
3. RSI < 30 (oversold)

This typically reduces trade count but increases win rate.

### Session-Based Trading

**Example: Forex Day Trading**
- Asset: EURUSD=X
- Timeframe: 15m
- Sessions:
  - ☑ London Session
  - ☑ New York Session
  - ☐ Tokyo Session (disabled)

**Result:** Only trades during high-liquidity hours when EUR/USD is most active.

## Phase 2 Status

### ✅ Implemented (Current)

- Dynamic component discovery
- Automatic UI rendering from metadata
- Parameter configuration with type-aware widgets
- Single backtest execution
- Comprehensive results display
- Market data download (Yahoo Finance)

### ⏸️ Not Yet Implemented

The following features are planned for future phases:

**Phase 3: Optimization Engine**
- Grid search across parameter ranges
- Parallel backtesting
- Results ranking by composite score
- Top 10 configurations display

**Phase 4: Export to Pine Script**
- Python → Pine Script v6 transpiler
- Jinja2 template engine
- One-click strategy export
- TradingView-ready code

**Phase 5: Advanced Validation**
- Monte Carlo simulation
- Walk-forward analysis
- Out-of-sample testing
- Multi-asset portfolio testing

## Next Steps

Now that Phase 2 Step 2.2 is complete, the next steps are:

1. **User Testing**: Get feedback on UI usability
2. **Bug Fixes**: Address any issues found during testing
3. **Phase 3**: Implement grid search optimization
4. **Phase 4**: Build Pine Script transpiler
5. **Phase 5**: Add validation methods

## Developer Notes

### Adding New Components

To add a new entry pattern, filter, or session:

1. Open `src/builder_framework.py`
2. Add a new function with the `@component` decorator
3. Define metadata (name, description, parameters)
4. Implement the logic
5. Restart the UI server
6. The new component appears automatically!

**No UI code changes needed.**

### Modifying Existing Components

To change a parameter:

1. Edit the `@component` decorator metadata
2. Update the function signature if needed
3. Restart the UI server

**Example: Change SMA period range**

```python
# Before
'sma_period': {
    'type': 'int',
    'min': 5,
    'max': 50,
    'default': 20
}

# After (allow higher values)
'sma_period': {
    'type': 'int',
    'min': 5,
    'max': 200,  # ← Changed
    'default': 20
}
```

The UI will now show a number input with range 5-200.

### Testing Changes

Run the discovery test to verify metadata is valid:

```bash
python test_ui_discovery.py
```

This checks:
- All components are discoverable
- Metadata is complete and valid
- Parameters have correct structure
- Functions are callable

## Conclusion

The Dynamic Strategy Builder UI demonstrates the power of metadata-driven development:

- **Zero Hardcoding**: No component names in UI code
- **Instant Updates**: New components appear without UI changes
- **Type Safety**: Parameter types enforce valid inputs
- **Scalability**: Can support hundreds of components

**The builder framework is the Single Source of Truth.**

---

**Version:** 1.0 (Phase 2, Step 2.2 Complete)
**Last Updated:** 2025-11-20
**Author:** Claude (AI Assistant)
