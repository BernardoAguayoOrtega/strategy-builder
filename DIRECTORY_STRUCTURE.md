# Directory Structure

This document describes the organization of the strategy-builder project.

## Overview

```
strategy-builder/
├── README.md                        # Project overview and quick start guide
├── PLAN.md                          # Implementation plan (step-by-step guide)
├── ARCHITECTURE.md                  # Architecture design document
├── CLAUDE.md                        # AI assistant guide (existing)
├── DIRECTORY_STRUCTURE.md           # This file
│
├── src/                             # Core framework source code
│   ├── __init__.py                  # Package initialization
│   ├── builder_framework.py         # SOURCE OF TRUTH: Trading components with @component decorators
│   ├── backtesting_framework.py     # Backtesting engine (position management, P&L, metrics)
│   ├── optimizer.py                 # Grid search and ranking engine
│   ├── transpiler.py                # Python → Pine Script v6 transpiler
│   └── ui_app.py                    # NiceGUI web interface (dynamic UI generation)
│
├── legacy/                          # Original project files (preserved for reference)
│   ├── Algo Strategy Builder.txt    # Original Pine Script strategy
│   └── Backtesting Validacion Framework.ipynb  # Original backtesting notebook
│
├── strategies/                      # Exported strategies
│   └── *.pine                       # Generated Pine Script files (ready for TradingView)
│
├── tests/                           # Unit and integration tests
│   ├── __init__.py
│   ├── test_builder_framework.py    # Tests for component registration and pattern detection
│   ├── test_backtesting.py          # Tests for backtesting engine
│   ├── test_optimizer.py            # Tests for optimization algorithms
│   └── test_transpiler.py           # Tests for Pine Script generation
│
├── notebooks/                       # Jupyter notebooks for research and analysis
│   ├── validation_analysis.ipynb    # Monte Carlo and walk-forward validation
│   ├── pattern_exploration.ipynb    # Pattern behavior analysis
│   └── optimization_results.ipynb   # Optimization results visualization
│
├── data/                            # Cached market data (gitignored)
│   ├── .gitkeep
│   └── *.csv                        # Downloaded OHLCV data
│
├── requirements.txt                 # Python dependencies
├── setup.py                         # Package installation configuration
└── .gitignore                       # Git ignore rules
```

---

## Directory Purposes

### `/src` - Core Framework

**Purpose**: Contains all reusable framework code.

**Key Files:**

- **`builder_framework.py`** (★ Source of Truth)
  - Defines all trading components with `@component` decorators
  - Contains: Entry Patterns, Filters, Sessions, Indicators, Exits
  - Provides discovery API: `get_all_components()`, `get_component()`
  - **If you add a new filter here, it automatically appears in the UI**

- **`backtesting_framework.py`**
  - Simulation engine for testing strategies
  - Position management, P&L calculation, trade tracking
  - Performance metrics calculation (ROI, Sharpe, Drawdown, etc.)

- **`optimizer.py`**
  - Grid search optimization across parameter ranges
  - Parallel execution using multiprocessing
  - Ranking and scoring algorithms

- **`transpiler.py`**
  - Converts Python strategy configurations to Pine Script v6
  - Uses Jinja2 templates for code generation
  - Validates generated code syntax

- **`ui_app.py`**
  - NiceGUI web application
  - Dynamically generates UI by introspecting `builder_framework`
  - Orchestrates backtesting and optimization workflows
  - Displays results and provides export functionality

---

### `/legacy` - Original Files

**Purpose**: Preserve original project files for reference.

**Contents:**

- **`Algo Strategy Builder.txt`**: Original Pine Script v6 strategy with 3 patterns (Sacudida, Envolvente, Volumen Climático)
- **`Backtesting Validacion Framework.ipynb`**: Original Jupyter notebook with backtesting functions and validation methodology

**Note**: These files are not used by the new framework but serve as reference implementations.

---

### `/strategies` - Exported Strategies

**Purpose**: Store generated Pine Script files ready for TradingView.

**Naming Convention:**
```
strategy_[pattern]_[score]_[timestamp].pine
```

**Example:**
```
strategies/
├── strategy_sacudida_0.892_2024-11-20.pine
├── strategy_envolvente_0.856_2024-11-20.pine
└── strategy_volclim_0.734_2024-11-20.pine
```

**Usage:**
1. Export strategy from UI
2. Copy contents of `.pine` file
3. Paste into TradingView Pine Editor
4. Save and apply to chart

---

### `/tests` - Test Suite

**Purpose**: Automated testing for all framework components.

**Test Categories:**

1. **Unit Tests**
   - Test individual functions in isolation
   - Mock external dependencies (yfinance, etc.)
   - Fast execution (<1 second per test)

2. **Integration Tests**
   - Test complete workflows (discovery → backtest → export)
   - Use real market data (cached)
   - Slower execution (~10 seconds per test)

**Running Tests:**
```bash
# All tests
pytest tests/

# Specific module
pytest tests/test_builder_framework.py

# With coverage
pytest --cov=src tests/
```

---

### `/notebooks` - Research Notebooks

**Purpose**: Exploratory analysis and validation studies.

**Typical Notebooks:**

- **`validation_analysis.ipynb`**
  - Monte Carlo simulations
  - Walk-forward analysis
  - Parameter stability testing

- **`pattern_exploration.ipynb`**
  - Pattern frequency analysis
  - Signal distribution across assets
  - Pattern correlation studies

- **`optimization_results.ipynb`**
  - Optimization result visualization
  - Parameter heatmaps
  - Performance surface plots

**Note**: Notebooks are for research, not production code. Production logic belongs in `/src`.

---

### `/data` - Market Data Cache

**Purpose**: Store downloaded market data to avoid repeated API calls.

**Structure:**
```
data/
├── AAPL_1d_2020-01-01_2024-01-01.csv
├── EURUSD_1h_2023-01-01_2024-01-01.csv
└── BTC-USD_15m_2024-01-01_2024-06-01.csv
```

**Naming Convention:**
```
{SYMBOL}_{TIMEFRAME}_{START}_{END}.csv
```

**Note**: This directory is gitignored to avoid committing large data files.

---

## File Dependencies

### Dependency Graph

```
┌─────────────────────────────────────────────────────────┐
│                  builder_framework.py                   │
│                  (Source of Truth)                      │
│                                                         │
│  - Entry Patterns                                       │
│  - Filters                                              │
│  - Sessions                                             │
│  - Indicators                                           │
│  - Exits                                                │
└───────────┬─────────────────────────────────────────────┘
            │
            │ imports & introspects
            │
    ┌───────┴────────┬──────────────┬──────────────┐
    │                │              │              │
    ▼                ▼              ▼              ▼
┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────┐
│backtesting│  │  optimizer   │  │transpiler│  │  ui_app  │
│_framework │  │              │  │          │  │          │
│          │  │              │  │          │  │          │
│- engine  │  │- grid search │  │- Jinja2  │  │- NiceGUI │
│- metrics │  │- parallel    │  │- Pine v6 │  │- dynamic │
│- trades  │  │- ranking     │  │- export  │  │- UI gen  │
└──────────┘  └──────┬───────┘  └────┬─────┘  └────┬─────┘
                     │                │            │
                     └────────────────┴────────────┘
                                │
                                ▼
                         ┌─────────────┐
                         │   User      │
                         │  Interface  │
                         └─────────────┘
```

---

## Adding New Components

### Example: Adding a New Filter

**Step 1**: Add to `src/builder_framework.py`

```python
@component(
    category='filter',
    name='atr_filter',
    display_name='ATR Volatility Filter',
    description='Only trade when ATR is above threshold',
    parameters={
        'period': {
            'type': 'int',
            'min': 5,
            'max': 50,
            'default': 14,
            'step': 1,
            'display_name': 'ATR Period',
            'optimizable': True
        },
        'threshold': {
            'type': 'float',
            'min': 0.0,
            'max': 5.0,
            'default': 1.0,
            'step': 0.1,
            'display_name': 'Minimum ATR'
        }
    }
)
def filter_atr(df, period=14, threshold=1.0):
    """ATR Filter Implementation"""
    # Calculate ATR
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()

    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.rolling(period).mean()

    # Apply filter
    df['filter_ok'] = (atr > threshold).fillna(False)

    return df
```

**Step 2**: Run the app

```bash
python src/ui_app.py
```

**Result**: The new "ATR Volatility Filter" checkbox appears automatically in the UI with:
- Checkbox to enable/disable
- Number input for "ATR Period" (5-50, default 14)
- Number input for "Minimum ATR" (0.0-5.0, default 1.0)
- Optimization range sliders (because `optimizable=True`)

**Step 3** (Optional): Add Pine Script template to `src/transpiler.py`

```jinja2
{% if 'atr_filter' in filters %}
// ATR Filter
tr = math.max(high - low, math.max(math.abs(high - close[1]), math.abs(low - close[1])))
atr = ta.sma(tr, {{filters.atr_filter.period}})
filter_ok = atr > {{filters.atr_filter.threshold}}
{% endif %}
```

**That's it!** The filter is now fully integrated.

---

## Configuration Files

### `requirements.txt`

```txt
# Core dependencies
numpy>=1.21.0
pandas>=1.3.0
yfinance>=0.1.63

# UI framework
nicegui>=1.0.0

# Backtesting
matplotlib>=3.4.0
seaborn>=0.11.0

# Optimization
optuna>=3.0.0  # Optional: for smart optimization

# Transpilation
jinja2>=3.0.0

# Development
pytest>=7.0.0
pytest-cov>=3.0.0
black>=22.0.0
flake8>=4.0.0

# Notebook support
jupyter>=1.0.0
ipykernel>=6.0.0
```

### `setup.py`

```python
from setuptools import setup, find_packages

setup(
    name='strategy-builder',
    version='1.0.0',
    description='Dynamic UI Builder Framework for Algorithmic Trading Strategies',
    author='Bernardo Aguayo Ortega',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.21.0',
        'pandas>=1.3.0',
        'yfinance>=0.1.63',
        'nicegui>=1.0.0',
        'matplotlib>=3.4.0',
        'jinja2>=3.0.0',
    ],
    python_requires='>=3.9',
)
```

### `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Data
data/*.csv
data/*.xlsx
data/*.parquet

# Jupyter
.ipynb_checkpoints/
*.ipynb_checkpoints

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Strategies (optional - might want to commit these)
# strategies/*.pine
```

---

## Development Workflow

### 1. Initial Setup

```bash
# Clone repository
git clone https://github.com/BernardoAguayoOrtega/strategy-builder.git
cd strategy-builder

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import nicegui; print('NiceGUI:', nicegui.__version__)"
```

### 2. Adding a New Component

```bash
# 1. Edit builder_framework.py
vim src/builder_framework.py

# 2. Add @component decorator and implementation

# 3. Test
pytest tests/test_builder_framework.py

# 4. Run UI to verify
python src/ui_app.py

# 5. Commit
git add src/builder_framework.py
git commit -m "Add ATR filter component"
```

### 3. Running Tests

```bash
# All tests
pytest

# Specific test
pytest tests/test_builder_framework.py::test_atr_filter

# With coverage
pytest --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### 4. Optimization Workflow

```bash
# 1. Start UI
python src/ui_app.py

# 2. Open browser to http://localhost:8080

# 3. Configure strategy in UI:
#    - Select pattern
#    - Enable filters
#    - Set optimization ranges

# 4. Click "Run Optimization"

# 5. Export winning strategy to strategies/
```

---

## Deployment

### Local Development

```bash
python src/ui_app.py
# Access at http://localhost:8080
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY legacy/ ./legacy/

EXPOSE 8080
CMD ["python", "src/ui_app.py"]
```

```bash
# Build
docker build -t strategy-builder .

# Run
docker run -p 8080:8080 strategy-builder
```

### Cloud Deployment

**Heroku:**
```bash
# Create Procfile
echo "web: python src/ui_app.py" > Procfile

# Deploy
heroku create strategy-builder-app
git push heroku main
```

**Render:**
```yaml
# render.yaml
services:
  - type: web
    name: strategy-builder
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python src/ui_app.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
```

---

## Maintenance

### Adding Dependencies

```bash
# Install new package
pip install optuna

# Update requirements.txt
pip freeze > requirements.txt

# Or manually add to requirements.txt
echo "optuna>=3.0.0" >> requirements.txt
```

### Updating Legacy Files

If the original Pine Script strategy is updated:

1. Update `legacy/Algo Strategy Builder.txt`
2. Sync changes to `src/builder_framework.py` components
3. Update corresponding Pine Script templates in `src/transpiler.py`
4. Run tests to ensure compatibility

---

## Troubleshooting

### Common Issues

**Issue**: UI doesn't show new component

**Solution**:
```bash
# 1. Check component is registered
python -c "from src.builder_framework import get_all_components; print(get_all_components())"

# 2. Restart UI server
# Kill old process and restart
python src/ui_app.py
```

**Issue**: Import errors

**Solution**:
```bash
# Ensure src/ is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or use package installation
pip install -e .
```

**Issue**: Optimization takes too long

**Solution**:
```python
# In src/optimizer.py, reduce n_jobs
optimizer = StrategyOptimizer(config, n_jobs=4)  # Use fewer cores

# Or reduce parameter ranges
param_ranges = {
    'rsi_period': [10, 14, 18],  # Only 3 values instead of 20
    'sma_period': [40, 50, 60]   # Only 3 values instead of 10
}
```

---

## Additional Resources

- **PLAN.md**: Step-by-step implementation guide
- **ARCHITECTURE.md**: Detailed architecture explanation
- **CLAUDE.md**: AI assistant guide with project context
- **legacy/**: Original Pine Script and notebook for reference

---

**Last Updated**: 2025-11-20
**Version**: 1.0
**Maintainer**: Bernardo Aguayo Ortega
