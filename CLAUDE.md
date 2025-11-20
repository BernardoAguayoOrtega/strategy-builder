# CLAUDE.md - AI Assistant Guide for strategy-builder

## Repository Overview

**Project:** Algorithmic Trading Strategy Development and Validation Framework
**Owner:** BernardoAguayoOrtega
**Purpose:** Translate TradingView Pine Script trading patterns into Python for robust backtesting, optimization, and multi-asset validation
**Age:** Created Nov 19, 2025 (18 commits, 2 days)
**Contributors:** Bernardo Aguayo Ortega (Human), Claude AI (AI Assistant)

### Core Concept
This repository bridges the gap between TradingView Pine Script strategy development and rigorous Python-based backtesting. It implements a comprehensive validation framework that tests trading strategies across multiple dimensions: asset portability, timeframe robustness, Monte Carlo simulation, and walk-forward analysis.

---

## File Structure

```
/home/user/strategy-builder/
├── Algo Strategy Builder.txt (13KB, 311 lines)
│   └── TradingView Pine Script v6 strategy definition
│       ├── 3 trading patterns (Sacudida, Envolvente, Volumen Climático)
│       ├── 7 input configuration groups
│       └── Comprehensive risk management system
│
└── Backtesting Validacion Framework.ipynb (126KB, 94 cells)
    └── Python/Jupyter backtesting and validation system
        ├── Technical indicator implementations
        ├── Position management functions
        ├── 24 performance metrics calculation
        └── Multi-method validation framework
```

### Notable Absence
**No traditional Python package infrastructure:**
- No `requirements.txt` or `setup.py`
- No `README.md`
- No `.gitignore`
- No CI/CD configuration
- No automated test suite

**Why:** This is a research/notebook-based project focused on rapid iteration and experimentation, not a deployable package.

---

## Technology Stack

### Languages
- **Pine Script v6:** TradingView strategy definition language
- **Python 3:** Backtesting, analysis, optimization
- **Jupyter Notebook:** Interactive development environment

### Python Dependencies

```python
# Core Scientific Computing
import numpy as np
import pandas as pd

# Market Data
import yfinance as yf  # Yahoo Finance API for OHLCV data

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Utilities
from IPython.display import HTML, display
from itertools import product
import warnings
```

### External Services
- **Yahoo Finance API:** Market data source for backtesting (via `yfinance`)

---

## Development Workflow

### Git Branch Strategy

**Branch Naming Convention:**
```
claude/[task-description]-[unique-id]
```

**Examples:**
- `claude/integrate-backtesting-strategy-017FLuk2KXEBEFjWX4bYoxt9`
- `claude/fix-strategy-builder-01Bom1hEdcQwzMK69RQ2PC6o`
- `claude/sacudida-strategy-backtest-01Y9NRYrHWwHZhDF76hPj4Ds`

**Main Branch:** `main` (implied from PR merges)

### Commit Message Patterns

**Types:**
1. **Feature:** `Add [component] - [description]`
2. **Fix:** `Fix [issue] - [technical details]`
3. **Merge:** `Merge pull request #N from...`
4. **Maintenance:** `chore: [description]`
5. **Revert:** `Revert '[commit message]'`

**Style:** Highly detailed commit messages with:
- What changed
- Why it changed
- Technical implementation notes
- Usage examples
- Expected outputs

**Example:**
```
Add automated build_strategy() function - ONE CALL DOES EVERYTHING

MAJOR FEATURE: Automated strategy development system

## New Function: build_strategy(asset, timeframe)
[... 50+ lines of detailed documentation in commit message]
```

### Pull Request Workflow

1. AI creates feature branch with `claude/*` naming
2. Develops features with detailed commits
3. Human (Bernardo) reviews via GitHub
4. Merges to main via PR
5. **5 PRs merged so far** (#1-5)

### Git Operation Guidelines

**For git push:**
- Always use: `git push -u origin <branch-name>`
- Branch MUST start with `claude/` and end with session ID
- Retry logic: Up to 4 times with exponential backoff (2s, 4s, 8s, 16s) on network failures

**For git fetch/pull:**
- Prefer specific branches: `git fetch origin <branch-name>`
- Same retry logic for network failures

---

## Code Conventions

### Language Convention: Bilingual Codebase

This repository intentionally mixes Spanish and English:

**Spanish Used For:**
- Business logic terms
- Domain-specific concepts
- Variable names for trading concepts
- Comments explaining trading logic

**English Used For:**
- Technical programming terms
- Library function calls
- General programming concepts

**Examples:**
```python
# Spanish identifiers
dameSistema()        # "give me system"
calculaCurvas()      # "calculate curves"
salidaVelas          # "exit candles"
sentido              # "direction"
perSma               # "period SMA"

# English identifiers
calculateMetrics()
optimizeParameters()
backtestResults
```

**Important:** This is intentional, not an error. Maintain this convention when adding new code.

### Naming Conventions

**Python:**
- Functions: `camelCase` (especially Spanish names: `dameSistema`, `dameGraficoBacktest`)
- Classes: `PascalCase` (`PatternLibrary`, `StrategyBuilder` - from deleted files)
- Variables: Mix of `camelCase` and `snake_case`
- No strict PEP 8 enforcement

**Pine Script:**
- Functions: `snake_case` (`sacudida_long_condition()`, `f_calc_qty()`)
- Variables: `snake_case` (`usar_patron_sacudida`, `entry_pip`, `stoplossL`)
- Extensive use of input grouping for UI organization

### Comment Style

**Pine Script:**
```pinescript
// ============================================
// SECTION HEADER
// ============================================

// ====== Subsection ======
```

**Python:**
```python
# SECTION IN CAPS
# Subsection normal case
```

---

## Trading Pattern Implementations

The core of this repository is the translation between Pine Script patterns and Python implementations. Here are the three main patterns:

### 1. Sacudida (Shake-out/False Breakout)

**Pine Script Location:** `Algo Strategy Builder.txt:92-104`

**Logic:**
- **Long:** Bearish candle breaks prior low → Next candle is bullish and closes above the prior low[2]
- **Short:** Bullish candle breaks prior high → Next candle is bearish and closes below the prior high[2]

**Python Implementation Principle:**
```python
# Must match Pine Script line-by-line
# Use pandas boolean operations with .fillna() for NaN safety
```

### 2. Envolvente (Engulfing Pattern)

**Pine Script Location:** `Algo Strategy Builder.txt:107-119`

**Logic:**
- **Long:** Bullish candle completely engulfs previous bearish candle
- **Short:** Bearish candle completely engulfs previous bullish candle

### 3. Volumen Climático (Climatic Volume)

**Pine Script Location:** `Algo Strategy Builder.txt:122-125`

**Logic:**
- Volume > SMA(20) * 1.75
- Direction determined by candle color (close vs open)

**Special Handling:**
- Uses market orders (immediate execution)
- Other patterns use stop orders (pending)

---

## Backtesting Framework Architecture

### Core Function Categories

**1. Technical Indicators** (3 functions)
```python
ocpSma()         # Simple Moving Average
ocpRsi()         # Relative Strength Index
ocpVolumeSma()   # Volume moving average
```

**2. Position Management** (4 functions)
```python
dameSistema()      # Generate trading signals from rules
damePosition()     # Convert signals to position sizes
dameSalidaVelas()  # Time-based exit (N-bar rule)
dameSalidaPnl()    # P&L exit with costs (commissions + slippage)
```

**3. Performance Calculation** (4 functions)
```python
calculaCurvas()       # Calculate equity curves
crearDfBacktesting()  # Create results dataframe structure
backSistemaList()     # Calculate 24 performance metrics
backActivoList()      # Buy & Hold benchmark metrics
```

**4. Visualization** (3 functions)
```python
dameGraficoSistema()   # System signals overlay on price chart
dameGraficoBacktest()  # Equity curve and drawdown
dameGraficoOpti()      # Optimization heatmap (SMA x RSI)
```

**5. Validation Methods** (4 functions)
```python
mezclaDataC()          # Monte Carlo: shuffle daily returns
mezclaDataOHLC()       # Monte Carlo: shuffle OHLC bars
mezclaDataBloques()    # Monte Carlo: block shuffling (preserve trends)
evaluarSistema()       # Walk-Forward analysis
```

### Performance Metrics (24 Total)

**Notebook Location:** `Backtesting Validacion Framework.ipynb`, cells 19-22

```python
metrics = {
    # Time Metrics
    'Y': years_of_data,
    'op': total_operations,
    'op/Y': operations_per_year,
    'mDIT': avg_days_in_trade,
    'tInv%': percent_time_invested,

    # Win/Loss Statistics
    'pos': winning_trades,
    'neg': losing_trades,
    'pa%': win_percentage,

    # Capital Metrics
    'capIn': initial_capital,
    'capFn': final_capital,
    'roi%': return_on_investment,
    'cagr%': compound_annual_growth_rate,

    # Trade Statistics
    'mPos%': avg_winning_trade_percent,
    'mNeg%': avg_losing_trade_percent,
    'em%': expected_value_per_trade,
    'exca%': expectancy_scaled,

    # Risk Metrics
    'PF': profit_factor,
    'Payf': payoff_ratio,
    'shs': sharpe_ratio,
    'maxDD%': maximum_drawdown,
    'medDD%': average_drawdown,
    'OCP': optimal_capital_percentage  # CAGR / avgDD (key metric)
}
```

**Key Metric:** `OCP` (Optimal Capital Percentage) = CAGR% / Average Drawdown%
Higher is better; balances returns against risk.

---

## Validation Philosophy

### Theory (from notebook cells 1-9)

**The Data Problem:**
- Too much historical data → Less relevant to current market
- Too little data → Insufficient statistical power
- **Solution:** Invent/simulate data through multiple validation methods

**Core Rule:**
- NEVER mix long and short trades in the same system
- Treat as separate systems with independent validation

### Validation Hierarchy

**1. In-Sample (IS) Validation**
- Asset Portability: Test on different instruments (stocks, forex, crypto)
- Timeframe Portability: Test on different periods (1min, 5min, 1H, 1D)
- Monte Carlo - Returns Shuffle: Tests if strategy depends on autocorrelation
- Monte Carlo - Block Shuffle: Tests if strategy depends on market regimes

**2. Out-of-Sample (OS) Validation**
- Basic OS: Holdout testing on unseen data
- OS + Costs: Add realistic commissions and slippage
- Walk-Forward (Expanding Window): Progressive validation over time
- Cross-Validation (Rolling Window): Sliding window validation

**3. Market (MKT) Validation**
- Paper trading (simulated real-time)
- Small capital live testing (real money, minimal risk)

### Validation Thresholds

**Monte Carlo Requirement:**
- Strategy performance must exceed 80th percentile of shuffled data
- Ensures edge is not due to random chance

**Walk-Forward Requirement:**
- Parameter degradation must be < 30%
- Ensures parameters don't overfit to in-sample period

**Only strategies passing BOTH tests should be deployed.**

---

## Common Issues and Solutions

### Issue 1: NaN Handling in Pandas

**Problem:** Recurring issue across multiple commits
```python
# This fails with "Series truth value ambiguous"
if df['ma_trend']:
    ...
```

**Solution:**
```python
# Always use .fillna() in boolean operations
if df['ma_trend'].fillna(False).any():
    ...

# Or for element-wise operations
df['signal'] = (df['price'] > df['ma']).fillna(False)
```

**Commits addressing this:**
- `f26507f`: Fix NaN handling in filter_ma_trend
- `52d4edb`: Comprehensive NaN safety improvements

### Issue 2: Jupyter Notebook Line Termination

**Problem:** Cells may lack proper newline characters
```python
# Missing '\n' causes merge conflicts
```

**Solution:**
Ensure all cell sources end with '\n' when programmatically editing notebooks.

### Issue 3: Strategy Pattern Translation

**Problem:** Python implementation differs from Pine Script logic

**Solution:**
- Match Pine Script line-by-line
- Use same variable names (translated to snake_case)
- Test outputs match for same input data
- Document any necessary deviations with comments

### Issue 4: Timeframe Access in Backtesting

**Problem:** Jupyter notebook uses Larry Connors RSI-2 system (cells 1-9), but repository purpose is testing Pine Script patterns

**Solution:**
- Notebook serves as TEMPLATE for validation methods
- Replace RSI-2 logic with Pine Script pattern translations
- Keep validation methodology intact
- This was the approach in deleted `Integrated_Strategy_Backtesting_Framework.ipynb`

---

## Development Guidelines for AI Assistants

### 1. Repository Context Understanding

**Current State (as of Nov 20, 2025):**
- Repository underwent major simplification
- Deleted files (removed as "outdated"):
  - `Integrated_Strategy_Backtesting_Framework.ipynb` (1455 lines)
  - `Pattern_Validation.ipynb`
  - Multiple `.md` documentation files

**What This Means:**
- Project is in "research mode" with minimal structure
- Previous work may be referenced in commits but no longer exists
- Focus on the two remaining files as ground truth
- Don't assume infrastructure that isn't present

### 2. Making Changes

**Before Editing:**
1. Understand which system you're working on (Pine Script vs Python)
2. Check if similar logic exists in the other system
3. Review recent commits for context on removed features
4. Consider if change should be reflected in both systems

**When Adding Features:**
- Prefer adding to existing notebook cells over creating new files
- Maintain bilingual naming conventions
- Include detailed comments explaining trading logic
- Test against multiple assets/timeframes if possible

**When Fixing Bugs:**
- Check if bug exists in both Pine Script and Python versions
- Use `.fillna()` liberally with pandas boolean operations
- Test edge cases: NaN values, zero volumes, missing data
- Update both systems if logic is mirrored

### 3. Testing Approach

**No Unit Tests:**
- This project has no pytest/unittest infrastructure
- Testing is done through backtesting with real market data
- Validation through multiple methods (Monte Carlo, Walk-Forward)

**How to Test Changes:**
1. Run affected notebook cells
2. Verify output metrics are reasonable
3. Check equity curve for anomalies
4. Test on at least 2 different assets
5. Compare to previous results if available

**Data for Testing:**
```python
# Standard test cases
test_assets = ['AAPL', 'EURUSD=X', 'BTC-USD']
test_timeframes = ['1d', '1h', '15m']
test_period = '2020-01-01 to 2024-01-01'
```

### 4. Commit Guidelines

**Structure:**
```
[Type] [Brief summary] - [Technical detail]

[Optional longer description with:]
- Implementation details
- Usage examples
- Expected outputs
- Breaking changes
- References to related commits/PRs
```

**Good Examples:**
```
Fix NaN handling in filter_ma_trend to resolve Series ambiguous truth value error

Add automated build_strategy() function - ONE CALL DOES EVERYTHING
[... extensive documentation in commit body]

chore: Remove outdated validation notebooks and backtesting framework files
```

**Commit Frequently:**
- Small, logical changes
- Each commit should be functional (notebook can run)
- Don't batch unrelated changes

### 5. Branch and PR Workflow

**Creating Branch:**
```bash
git checkout -b claude/[task-description]-[unique-id]
```

**Before Pushing:**
```bash
# Verify branch name starts with 'claude/'
git branch --show-current

# Push with upstream tracking
git push -u origin claude/[task-description]-[unique-id]
```

**PR Description Should Include:**
- Summary of changes
- Test plan (what was validated)
- Assets/timeframes tested
- Performance impact (if applicable)
- Breaking changes (if any)

### 6. Pine Script to Python Translation

**Reference Implementation:** See deleted `Integrated_Strategy_Backtesting_Framework.ipynb` in commit `c68d760`

**Translation Principles:**

| Pine Script | Python Equivalent | Notes |
|------------|-------------------|-------|
| `ta.sma(close, 50)` | `df['close'].rolling(50).mean()` | Pandas rolling window |
| `ta.rsi(close, 14)` | Custom `ocpRsi()` function | Implement from scratch |
| `close[1]` | `df['close'].shift(1)` | Offset by 1 bar |
| `ta.crossover(a, b)` | `(a > b) & (a.shift(1) <= b.shift(1))` | Boolean logic |
| `strategy.entry(...)` | `positions[i] = size` | Direct position array |
| `bar_index` | `df.index` or `range(len(df))` | Row index |

**Pine Script Special Cases:**

1. **var keyword:** Persists across bars
   ```pinescript
   var float stoploss = na  // Keeps value until reassigned
   ```
   Python: Use class variables or pass through DataFrame columns

2. **Lookahead in arrays:**
   ```pinescript
   close[1]  // Previous bar (lookback)
   ```
   Python:
   ```python
   df['close'].shift(1)  # Previous bar
   ```

3. **Strategy positions:**
   Pine Script manages positions automatically; Python requires explicit tracking

### 7. Working with the Backtesting Notebook

**Notebook Structure (94 cells):**
```
Cells 1-9:    Theory (READ FIRST - explains philosophy)
Cells 10-11:  Imports
Cells 12-13:  Data loading (expects dfIS.xlsx - doesn't exist)
Cells 14-16:  Setup
Cells 17-18:  System functions (core logic)
Cells 19-22:  Results calculation
Cells 23-39:  Optimization
Cells 40-90:  Validation (50+ cells)
Cells 91-93:  Notes
```

**Safe to Modify:**
- Cells 17-18: System logic (replace with Pine Script patterns)
- Cells 23-39: Optimization parameters
- Parameter definitions in Setup section

**Avoid Modifying:**
- Cells 1-9: Theory (documentation)
- Core validation methodology (Cells 40-90)
- Metric calculation logic

**Adding New Patterns:**
1. Study existing `dameSistema()` function
2. Add new pattern detection logic
3. Update function to accept pattern selection parameter
4. Test with known data to verify signals
5. Run full validation suite

### 8. Optimization Guidelines

**Current Optimization (cells 23-39):**
- Grid search over SMA period x RSI thresholds
- Evaluates on metrics: `op/Y`, `roi%`, `CAGR%`, `OCP`
- Visualizes as heatmap

**Adding New Optimizable Parameters:**
```python
# Define parameter ranges
param1_range = range(10, 51, 5)
param2_range = [1.5, 2.0, 2.5]

# Create grid
combinations = list(product(param1_range, param2_range))

# Test each combination
results = []
for p1, p2 in combinations:
    # Run backtest with parameters
    metrics = backSistemaList(...)
    results.append({**metrics, 'p1': p1, 'p2': p2})

# Create dataframe and visualize
df_results = pd.DataFrame(results)
dameGraficoOpti(df_results, 'p1', 'p2', 'OCP')
```

**Optimization Warnings:**
- Avoid optimizing more than 2-3 parameters (curse of dimensionality)
- Always validate optimized parameters with Walk-Forward
- Use OCP metric (CAGR/avgDD) rather than raw CAGR
- Consider transaction costs in optimization

### 9. Documentation Standards

**Given No README:**
- Put extensive documentation in commit messages
- Add markdown cells in notebook for complex logic
- Use inline comments liberally
- Reference specific Pine Script line numbers when translating

**Comment Template for New Functions:**
```python
def nuevaFuncion(df, parametro1, parametro2):
    """
    [Spanish description of what function does]

    [English translation if technical]

    Args:
        df: DataFrame with OHLCV data
        parametro1: Description
        parametro2: Description

    Returns:
        Series/DataFrame with results

    Notes:
        - Corresponds to Pine Script lines X-Y
        - Special handling for [edge case]
    """
    # Implementation
```

### 10. Data Management

**Data Sources:**
```python
import yfinance as yf

# Download data
df = yf.download('AAPL', start='2020-01-01', end='2024-01-01', interval='1d')
```

**Data Formats Expected:**
```python
# OHLCV format
columns = ['Open', 'High', 'Low', 'Close', 'Volume']
# Note: Capital case from yfinance

# Internally may convert to lowercase
columns = ['open', 'high', 'low', 'close', 'volume']
```

**Handling Multi-Index (yfinance quirk):**
```python
# If downloading multiple tickers, yfinance returns multi-index
df = yf.download(['AAPL', 'MSFT'], ...)  # MultiIndex columns

# For single ticker processing
df = df['Close']['AAPL']  # Extract single series
```

---

## Project History and Context

### Timeline

**Nov 19, 2025:**
- 17:08 - Initial commit (Pine Script + Backtesting notebook)
- PR #1 opened - Integrated backtesting framework proposed

**Nov 20, 2025:**
- 00:01 - Added comprehensive integration framework (1455 lines)
- 00:08 - Added pattern validation notebook
- 00:14 - Added comprehensive validation system
- 00:18 - Added implementation verification docs
- 00:25 - Added automated `build_strategy()` function
- 00:32 - Added final validation document
- Multiple bug fixes for NaN handling
- 08:36 - **CLEANUP:** Removed all integration files, returned to 2-file structure

### What Was Deleted and Why

**Files Removed (commit 52d4edb):**
- `Integrated_Strategy_Backtesting_Framework.ipynb`
- `Pattern_Validation.ipynb`
- `FINAL_VALIDATION.md`
- `IMPLEMENTATION_VERIFICATION.md`
- `PATTERN_VERIFICATION.md`

**Commit Message:** "chore: Remove outdated validation notebooks and backtesting framework files."

**Implication:**
- Project reverted to minimal structure
- Focus returned to core backtesting notebook
- Integration approach may have been over-engineered
- Pattern validation deemed unnecessary at this stage

**Key Insight for AI Assistants:**
- Don't assume infrastructure exists just because it's in git history
- Current state (2 files) is intentional simplification
- If rebuilding integration, learn from what was removed
- Consult with Bernardo before creating extensive new infrastructure

### The Automated Build Function (Now Deleted)

**Commit 81188d1** introduced `build_strategy()` - a one-call automation:

```python
def build_strategy(asset, timeframe):
    """
    ONE CALL DOES EVERYTHING:
    1. Download data for any asset/timeframe
    2. Test ALL patterns (Sacudida, Envolvente, Vol Climático)
    3. Optimize parameters
    4. Run Monte Carlo validation
    5. Run Walk-Forward validation
    6. Return only strategies passing BOTH validations
    """
```

**Selection Criteria:**
- Monte Carlo: Must score >80th percentile vs shuffled data
- Walk-Forward: Parameter degradation <30%
- Returns ranked list by OCP metric

**Why It's Gone:**
- Part of integrated framework (deleted Nov 20)
- May have been premature optimization
- Current focus on manual validation process

**If Rebuilding:**
- Reference commit `81188d1` for implementation details
- Keep validation criteria (80th percentile, <30% degradation)
- Consider more modular approach
- Get approval before creating large automation

---

## Key Technical Decisions

### 1. No Python Package Structure

**Decision:** Keep as notebook-based research project
**Rationale:**
- Rapid iteration more important than deployment
- Target user is researcher/trader, not software engineer
- Package infrastructure adds overhead without clear benefit
- Jupyter notebooks provide better interactive exploration

### 2. Bilingual Code

**Decision:** Mix Spanish and English identifiers
**Rationale:**
- Primary developer (Bernardo) is Spanish speaker
- Trading terms more natural in Spanish
- Technical terms standard in English
- Maintains clarity for both audiences

### 3. Pine Script + Python Dual System

**Decision:** Maintain separate TradingView and Python implementations
**Rationale:**
- TradingView for strategy development and visualization
- Python for rigorous backtesting and validation
- Each system has strengths
- Translation layer allows leveraging both

### 4. Comprehensive Validation Over Unit Tests

**Decision:** No unit tests; extensive backtesting validation instead
**Rationale:**
- Trading strategies fail in ways unit tests can't catch
- Real market data exposes edge cases
- Multiple validation methods (Monte Carlo, Walk-Forward) more valuable
- Unit tests give false confidence in trading systems

### 5. Minimal Documentation Files

**Decision:** No README, use commit messages for documentation
**Rationale:**
- Documentation in commits stays synchronized with code
- Reduces maintenance burden
- Jupyter notebook cells provide inline documentation
- CLAUDE.md (this file) serves as comprehensive guide

---

## Advanced Topics

### Monte Carlo Simulation Methods

**Three Shuffling Approaches:**

1. **Returns Shuffle** (`mezclaDataC`)
   - Shuffles daily returns randomly
   - Breaks autocorrelation
   - Tests if strategy relies on momentum/mean reversion
   - Preserves distribution of returns

2. **OHLC Shuffle** (`mezclaDataOHLC`)
   - Shuffles entire OHLC bars
   - Completely randomizes price action
   - Strictest test
   - Tests if strategy relies on any time-based patterns

3. **Block Shuffle** (`mezclaDataBloques`)
   - Shuffles blocks of bars (e.g., 20-bar chunks)
   - Preserves short-term trends and regimes
   - Tests if strategy relies on specific regime sequences
   - More realistic than pure shuffling

**Interpretation:**
- If strategy performs well on shuffled data → No real edge, just luck
- If strategy significantly outperforms shuffled → Genuine edge detected
- Threshold: Must be >80th percentile of shuffled simulations

### Walk-Forward Analysis

**Purpose:** Test parameter stability over time

**Methodology:**
1. Divide data into multiple periods
2. Optimize parameters on period N
3. Test with those parameters on period N+1
4. Compare in-sample vs out-of-sample performance
5. Calculate degradation percentage

**Formula:**
```
degradation = (IS_performance - OS_performance) / IS_performance * 100%
```

**Acceptance Criteria:**
- Degradation < 30%: Parameters are robust
- Degradation > 30%: Parameters likely overfit

**Two Variants:**
- **Expanding Window:** Train on [0, N], test on [N, N+1]
- **Rolling Window:** Train on [N-W, N], test on [N, N+1]

### Risk Management in Pine Script

**Three Modes (from `Algo Strategy Builder.txt:53`):**

1. **Fixed Size** (`tipo_gestion = 'Tamaño fijo'`)
   ```pinescript
   qty = tamano_fijo_qty  // e.g., 1 contract always
   ```

2. **Fixed Dollar Risk** (`tipo_gestion = 'Riesgo monetario fijo'`)
   ```pinescript
   distance = entry - stoploss
   qty = risk_money / (distance * pointvalue)
   qty = floor(qty / qty_step) * qty_step  // Round to step
   ```

3. **Percentage of Equity** (`tipo_gestion = 'Riesgo % equity'`)
   ```pinescript
   risk_money = strategy.equity * (porc_riesgo_equity / 100)
   qty = risk_money / (distance * pointvalue)
   ```

**Python Translation:**
Must replicate these calculations exactly, including:
- Rounding to `qty_step` (granularity)
- Enforcing `qty_min` (minimum size)
- Checking position size validity before entry

### Pattern Specifics: Sacudida

**Why "Sacudida" (Shake-out) is Powerful:**

Market Logic:
1. Weak hands hold longs with stops below recent low
2. Market drops below the low, triggering stops (liquidity grab)
3. Institutional buyers enter at this level
4. Market reverses, leaving weak hands out
5. Strong hands profit from the reversal

**Implementation Nuances:**

Pine Script:
```pinescript
sacudida_long_condition() =>
    vela2_bajista = close[1] < open[1]
    vela2_rompe_minimo = low[1] < low[2]
    vela3_alcista = close > open
    vela3_confirmacion = close > low[2]
    vela2_bajista and vela2_rompe_minimo and vela3_alcista and vela3_confirmacion
```

Python (safe):
```python
vela2_bajista = (df['close'].shift(1) < df['open'].shift(1)).fillna(False)
vela2_rompe_minimo = (df['low'].shift(1) < df['low'].shift(2)).fillna(False)
vela3_alcista = (df['close'] > df['open']).fillna(False)
vela3_confirmacion = (df['close'] > df['low'].shift(2)).fillna(False)

sacudida_long = vela2_bajista & vela2_rompe_minimo & vela3_alcista & vela3_confirmacion
```

**Critical Details:**
- Bar 2 (yesterday) must close bearish AND break bar 3's low
- Bar 1 (today) must close bullish AND above bar 3's low
- This creates a specific candlestick pattern visible on chart
- Entry is typically stop order above bar 1's high

---

## Troubleshooting Guide

### Problem: Notebook Won't Run

**Symptoms:**
- Import errors
- Module not found
- Kernel dies

**Solutions:**
1. Install dependencies:
   ```bash
   pip install numpy pandas yfinance matplotlib seaborn jupyter
   ```

2. Verify Yahoo Finance access:
   ```python
   import yfinance as yf
   df = yf.download('AAPL', start='2024-01-01', end='2024-01-31')
   print(df.head())
   ```

3. Restart kernel: `Kernel > Restart & Clear Output`

### Problem: "Series truth value ambiguous"

**Cause:** Using pandas Series in boolean context without proper handling

**Fix:**
```python
# Bad
if df['condition']:
    ...

# Good
if df['condition'].any():
    ...

# Or for element-wise
df['result'] = df['condition'].fillna(False)
```

### Problem: Performance Metrics NaN

**Causes:**
- No trades executed
- Division by zero in metric calculation
- Invalid data (all NaN in OHLCV)

**Debug:**
```python
# Check for trades
print(f"Positions sum: {positions.sum()}")
print(f"Trades executed: {(positions != 0).sum()}")

# Check data validity
print(f"NaN in data: {df.isnull().sum()}")

# Check signals
print(f"Long signals: {long_signals.sum()}")
print(f"Short signals: {short_signals.sum()}")
```

### Problem: Git Push Fails (403 Error)

**Cause:** Branch name doesn't follow `claude/*-[session-id]` pattern

**Fix:**
```bash
# Check current branch
git branch --show-current

# If incorrect, rename
git branch -m claude/proper-name-[unique-id]

# Push with retry
git push -u origin claude/proper-name-[unique-id]
```

### Problem: Optimization Takes Too Long

**Symptoms:**
- Grid search runs for hours
- Notebook becomes unresponsive

**Solutions:**
1. Reduce parameter ranges:
   ```python
   # Instead of
   sma_range = range(10, 201, 1)  # 191 values

   # Use
   sma_range = range(10, 201, 10)  # 20 values
   ```

2. Use smaller date range:
   ```python
   # Instead of 10 years
   df = df['2023-01-01':'2024-01-01']  # 1 year
   ```

3. Limit combinations:
   ```python
   # Test subset of grid
   combinations = list(product(sma_range, rsi_range))[:100]
   ```

### Problem: Walk-Forward Shows >100% Degradation

**Cause:** Strategy loses money out-of-sample (negative performance)

**Interpretation:**
- Parameters severely overfit to in-sample period
- Strategy not viable
- Need different approach or more robust parameters

**Solutions:**
- Try simpler strategy (fewer parameters)
- Use longer in-sample period
- Check for data mining bias (too many pattern variations tested)

---

## FAQ

### Q: Why are there only 2 files in this repository?

**A:** The project recently simplified from a complex multi-file structure. A comprehensive integrated framework was built and then removed as "outdated." Current focus is on core backtesting with the original validation notebook.

### Q: Where are the Python files (`.py`)?

**A:** This is a notebook-first project. All Python code lives in `Backtesting Validacion Framework.ipynb`. There's no package structure intentionally—it's a research environment, not a deployable application.

### Q: Why is the code mixing Spanish and English?

**A:** Intentional bilingual approach. Trading domain terms are clearer in Spanish for the primary developer; technical programming terms remain in English for standard conventions. This is a feature, not a bug.

### Q: How do I run the backtests?

**A:**
1. Open `Backtesting Validacion Framework.ipynb` in Jupyter
2. Read theory section (cells 1-9) first
3. Run imports (cells 10-11)
4. Skip data loading (cells 12-13) or provide your own data
5. Configure setup (cells 14-16)
6. Run system cells (cells 17-18)
7. Execute backtesting (cells 19-22)

### Q: What happened to `build_strategy()` function?

**A:** It was part of the integrated framework deleted on Nov 20. Implementation details are in commit `81188d1`. May be rebuilt in the future with a more modular approach.

### Q: Should I create a `requirements.txt`?

**A:** Ask Bernardo first. The current approach is intentionally minimal. If adding, keep it simple:
```
numpy>=1.21.0
pandas>=1.3.0
yfinance>=0.1.63
matplotlib>=3.4.0
seaborn>=0.11.0
jupyter>=1.0.0
```

### Q: How do I translate a new Pine Script pattern to Python?

**A:**
1. Read the Pine Script implementation carefully
2. Identify all `[N]` lookback references
3. Convert to `df['column'].shift(N)` in Python
4. Use `.fillna(False)` for all boolean operations
5. Test with known data where you manually verify expected signals
6. Compare signal counts and timing between systems
7. Document correspondence (e.g., "Matches Pine Script lines 150-175")

### Q: What's the best metric to optimize for?

**A:** **OCP** (Optimal Capital Percentage) = CAGR% / Average Drawdown%. It balances returns against risk better than raw CAGR or Sharpe ratio. Aim for OCP > 5.0 for viable strategies.

### Q: Can I add machine learning?

**A:** Technically yes, but consider:
- Current framework is rule-based
- ML adds complexity and new overfitting risks
- Would need additional validation beyond Monte Carlo/Walk-Forward
- Discuss with Bernardo before major architectural changes
- Start with simple ML (logistic regression, random forest) before deep learning

### Q: Why no README?

**A:** Documentation is in commit messages and this CLAUDE.md file. Keeps docs in sync with code by tying them directly to changes. For external users, this file serves as the comprehensive README.

---

## Appendix A: Pine Script Strategy Settings

From `Algo Strategy Builder.txt:2`:

```pinescript
strategy(
    'Algo Strategy Builder (Fixed)',
    overlay = true,
    initial_capital = 100000,
    margin_long = 0,
    margin_short = 0,
    pyramiding = 1,
    calc_on_order_fills = false,
    calc_on_every_tick = false,
    use_bar_magnifier = true,
    commission_type = strategy.commission.cash_per_contract,
    commission_value = 1.5,
    slippage = 1
)
```

**Key Settings:**
- No margin (cash-only trading)
- 1 position at a time (pyramiding=1)
- $1.50 commission per contract
- 1 pip slippage
- Bar magnifier enabled (intrabar accuracy)

---

## Appendix B: Session Times (Trading Hours)

From `Algo Strategy Builder.txt:79-82`:

```pinescript
enHorario1 = not na(time(timeframe.period, '0100-0815')) // London
enHorario2 = not na(time(timeframe.period, '0815-1545')) // New York
enHorario3 = not na(time(timeframe.period, '1545-0100')) // Tokio
```

**Session Times (24-hour format):**
- **London:** 01:00 - 08:15 (7 hours 15 min)
- **New York:** 08:15 - 15:45 (7 hours 30 min)
- **Tokyo:** 15:45 - 01:00 (9 hours 15 min)

**Note:** Times in UTC/GMT. Adjust for local timezone when translating to Python.

---

## Appendix C: Performance Metrics Reference

| Metric | Full Name | Formula | Good Value |
|--------|-----------|---------|------------|
| Y | Years | Data duration in years | N/A |
| op | Operations | Total trades | >30 per year |
| op/Y | Operations per Year | op / Y | 30-100 |
| mDIT | Mean Days in Trade | Avg holding period | Depends on TF |
| tInv% | Time Invested | % of time in position | 20-60% |
| pos | Positive Trades | Count of winners | N/A |
| neg | Negative Trades | Count of losers | N/A |
| pa% | Percent Accurate | pos / op * 100 | >50% |
| capIn | Initial Capital | Starting equity | 100,000 |
| capFn | Final Capital | Ending equity | N/A |
| roi% | Return on Investment | (capFn - capIn) / capIn * 100 | >20% |
| cagr% | Compound Annual Growth | Annualized return | >15% |
| mPos% | Mean Positive % | Avg winner size | >2% |
| mNeg% | Mean Negative % | Avg loser size | <-1% |
| em% | Expected Value | (pa% * mPos%) + ((1-pa%) * mNeg%) | >0% |
| exca% | Expectancy | em% scaled by operations | >1% |
| PF | Profit Factor | Gross profit / Gross loss | >1.5 |
| Payf | Payoff Ratio | mPos% / abs(mNeg%) | >1.0 |
| shs | Sharpe Ratio | Mean return / Std dev | >1.0 |
| maxDD% | Max Drawdown | Largest peak-to-trough | <20% |
| medDD% | Mean Drawdown | Average drawdown | <10% |
| **OCP** | **Optimal Capital %** | **cagr% / medDD%** | **>5.0** |

---

## Appendix D: Git Commit History Summary

**Total Commits:** 18
**Date Range:** Nov 19-20, 2025 (2 days)
**Pull Requests:** 5 (all merged)

**Commit Types:**
- Feature additions: 8
- Bug fixes: 5
- Merges: 3
- Maintenance: 2

**Most Common Issues:**
1. NaN handling (3 commits)
2. Notebook line termination (2 commits)
3. Syntax errors in strategy logic (2 commits)

**Largest Commits:**
1. `c68d760`: Integration framework (1455 lines added)
2. `81188d1`: build_strategy() function (large addition)
3. `52d4edb`: Cleanup (1455 lines removed)

---

## Conclusion

This repository represents a sophisticated approach to algorithmic trading strategy development. While minimalist in structure (just 2 files), it embodies deep knowledge of trading system validation, statistical robustness testing, and practical trading considerations.

**For AI Assistants:**
- Read this file completely before making changes
- Understand the bilingual convention
- Respect the minimal structure (don't over-engineer)
- Use comprehensive commit messages
- Test with real market data, not unit tests
- Always validate with Monte Carlo + Walk-Forward
- When in doubt, ask Bernardo

**For Future Development:**
- Consider rebuilding integrated framework with lessons learned
- Add more trading patterns (momentum, reversal, breakout)
- Expand validation methods (portfolio-level testing)
- Create portfolio construction system
- Add risk management enhancements

**Remember:**
The goal is not to create a perfect software system, but to develop profitable, robust trading strategies validated through rigorous statistical testing. Keep this north star in mind with every change.

---

**Document Version:** 1.0
**Last Updated:** 2025-11-20
**Author:** Claude (AI Assistant)
**Reviewed By:** Pending (Bernardo Aguayo Ortega)

**This document will be updated as the repository evolves.**
