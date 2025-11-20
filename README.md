# Strategy Builder - Dynamic UI Framework

A self-maintaining framework for algorithmic trading strategy development, optimization, and export to TradingView Pine Script v6.

## 🚀 Key Features

- **🔍 Zero Hardcoding**: Add a trading pattern in Python → Automatically appears in the UI
- **🎛️ Dynamic Discovery**: UI introspects the framework at runtime to generate all controls
- **⚡ Parallel Optimization**: Grid search across parameter ranges using multiprocessing
- **📊 Export to TradingView**: Transpile winning strategies to Pine Script v6
- **🧪 Comprehensive Testing**: Monte Carlo and walk-forward validation built-in

## 📚 Documentation

- **[PLAN.md](PLAN.md)** - Step-by-step implementation guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed architecture and design patterns
- **[DIRECTORY_STRUCTURE.md](DIRECTORY_STRUCTURE.md)** - Project organization guide
- **[CLAUDE.md](CLAUDE.md)** - AI assistant guide with full project context

## 🏗️ Project Structure

```
strategy-builder/
├── src/                    # Core framework (Source of Truth)
│   ├── builder_framework.py    # ⭐ All trading components defined here
│   ├── backtesting_framework.py
│   ├── optimizer.py
│   ├── transpiler.py
│   └── ui_app.py
├── legacy/                 # Original Pine Script and notebooks
├── strategies/             # Exported Pine Script files
├── tests/                  # Unit and integration tests
├── notebooks/              # Research notebooks
└── data/                   # Cached market data
```

## ⚡ Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/BernardoAguayoOrtega/strategy-builder.git
cd strategy-builder

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Test the Framework

```bash
# Test component discovery
python src/builder_framework.py

# Expected output:
# ✓ Sacudida (Shake-out)
# ✓ Envolvente (Engulfing)
# ✓ Volumen Climático (Climactic Volume)
# ✓ Moving Average Cross Filter
# ✓ RSI Filter
# ✓ London Session
# ✓ New York Session
# ✓ Tokyo Session
```

### Run the UI (Coming Soon)

```bash
python src/ui_app.py
# Open browser to http://localhost:8080
```

## 🎯 Core Concept: The Source of Truth

The `builder_framework.py` module is the **single source of truth**. Every trading component is defined there with a `@component` decorator:

```python
@component(
    category='entry_pattern',
    name='sacudida',
    display_name='Sacudida (Shake-out)',
    description='False breakout reversal pattern',
    parameters={
        'direction': {
            'type': 'choice',
            'options': ['long', 'short', 'both'],
            'default': 'both',
            'display_name': 'Trade Direction'
        }
    }
)
def pattern_sacudida(df, direction='both'):
    # Implementation
    return df
```

**That's it!** The UI automatically:
1. Discovers this component
2. Creates a checkbox labeled "Sacudida (Shake-out)"
3. Adds a dropdown for "Trade Direction"
4. Makes it available for optimization
5. Can export it to Pine Script

## 🔄 Development Workflow

### Adding a New Filter

1. **Edit `src/builder_framework.py`**:

```python
@component(
    category='filter',
    name='atr_filter',
    display_name='ATR Volatility Filter',
    description='Only trade when ATR > threshold',
    parameters={
        'period': {
            'type': 'int',
            'min': 5,
            'max': 50,
            'default': 14,
            'optimizable': True
        }
    }
)
def filter_atr(df, period=14):
    # Calculate ATR
    # Apply filter
    return df
```

2. **Run UI** - The filter appears automatically!

3. **Test**:

```bash
pytest tests/test_builder_framework.py::test_atr_filter
```

## 📊 Current Status

### ✅ Completed

- [x] Project structure
- [x] `builder_framework.py` with 3 patterns, 2 filters, 3 sessions
- [x] Documentation (PLAN.md, ARCHITECTURE.md, DIRECTORY_STRUCTURE.md)
- [x] Component discovery system
- [x] Metadata-driven design

### 🚧 In Progress

- [ ] `backtesting_framework.py` - Simulation engine
- [ ] `optimizer.py` - Grid search implementation
- [ ] `transpiler.py` - Pine Script code generation
- [ ] `ui_app.py` - NiceGUI web interface

### 📋 Planned

- [ ] Unit tests for all components
- [ ] Integration tests
- [ ] Example notebooks
- [ ] Deployment guide

## 🧪 Available Components

### Entry Patterns

| Pattern | Description | Parameters |
|---------|-------------|------------|
| Sacudida | False breakout reversal | direction |
| Envolvente | Candlestick engulfing | direction |
| Volumen Climático | High volume spike | sma_period, multiplier, direction |

### Filters

| Filter | Description | Parameters |
|--------|-------------|------------|
| MA Cross | Trend filter using MA crossover | mode, fast_period, slow_period |
| RSI Filter | Overbought/oversold filter | period, oversold, overbought, mode |

### Sessions

| Session | Hours (UTC) | Description |
|---------|-------------|-------------|
| London | 01:00 - 08:15 | EUR, GBP pairs |
| New York | 08:15 - 15:45 | USD pairs, US stocks |
| Tokyo | 15:45 - 01:00 | JPY pairs |

## 🤝 Contributing

This is currently a personal research project. If you'd like to contribute or have suggestions:

1. Fork the repository
2. Create a feature branch
3. Follow the `@component` decorator pattern
4. Add tests
5. Submit a pull request

## 📝 Philosophy

**"Code is the design, the UI is the reflection."**

Instead of maintaining separate UI code and business logic, we define the logic once with rich metadata, and the UI generates itself. This eliminates sync issues and dramatically speeds up iteration.

## 🛠️ Technology Stack

- **Python 3.9+**: Core language
- **Pandas/NumPy**: Data manipulation
- **yfinance**: Market data
- **NiceGUI**: Web UI framework
- **Jinja2**: Pine Script templating
- **pytest**: Testing

## 📖 Learn More

- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the discovery pattern
- Read [PLAN.md](PLAN.md) for implementation details
- Check [legacy/](legacy/) for original Pine Script strategy

## 📄 License

This project is part of personal trading research. Use at your own risk. No warranty or guarantee of profitability.

## 👤 Author

**Bernardo Aguayo Ortega**
- GitHub: [@BernardoAguayoOrtega](https://github.com/BernardoAguayoOrtega)

## 🙏 Acknowledgments

- Original backtesting framework from Jupyter notebook
- Pine Script strategy patterns
- NiceGUI for excellent Python UI framework

---

**Status**: 🚧 Active Development
**Version**: 1.0.0
**Last Updated**: 2025-11-20
