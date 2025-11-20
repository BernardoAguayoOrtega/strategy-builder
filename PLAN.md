# Dynamic UI Builder Framework - Implementation Plan

## Implementation Status

**Last Updated:** 2025-11-20

| Phase | Status | Progress | Notes |
|-------|--------|----------|-------|
| **Phase 1: Foundation** | ✅ **COMPLETE** | 100% | builder_framework.py, backtesting_framework.py, integration tests passing |
| **Phase 2: Dynamic UI** | ✅ **COMPLETE** | 100% | ui_app.py with full component discovery, all tests passing |
| **Phase 3: Optimization** | ⏸️ Pending | 0% | Ready to start |
| **Phase 4: Export** | ⏸️ Pending | 0% | - |
| **Phase 5: Polish** | ⏸️ Pending | 0% | - |

### Completed Deliverables

**Phase 1 (✅ Complete):**
- ✅ `src/builder_framework.py` - 931 lines, 3 entry patterns, 2 filters, 3 sessions
- ✅ `src/backtesting_framework.py` - Full backtest engine with metrics calculation
- ✅ `src/__init__.py` - Package initialization
- ✅ `test_framework_simple.py` - Integration test (all tests passing)
- ✅ `requirements.txt` - Dependency specification
- ✅ Directory structure created (src/, strategies/, tests/, notebooks/, data/)

**Phase 2 (✅ Complete - 100%):**
- ✅ Step 2.1: UI Framework Selected (NiceGUI)
- ✅ Step 2.2: Dynamic UI Application Built
  - ✅ `src/ui_app.py` - 600+ lines, full NiceGUI implementation
  - ✅ `test_ui_discovery.py` - Component discovery test (8 components found)
  - ✅ `UI_GUIDE.md` - Comprehensive user guide
  - ✅ `requirements.txt` - Updated with nicegui>=1.4.0 and yfinance>=0.1.63
- ✅ Step 2.3: User Testing & Refinement (Complete)
  - ✅ `test_ui_workflow.py` - Comprehensive workflow test suite (400+ lines)
  - ✅ 4 complete workflows tested and passing
  - ✅ Parameter extraction verified
  - ✅ Edge cases tested (zero trades, filtered signals)
  - ✅ `TESTING_RESULTS.md` - Detailed testing report and recommendations
  - ✅ Minor bug fixes (deprecation warning resolved)

---

## Executive Summary

This document outlines the step-by-step implementation plan for a Dynamic UI Builder Framework that enables non-technical users to configure, optimize, and export algorithmic trading strategies without writing code.

**Core Principle:** The `builder_framework` Python module is the **Single Source of Truth**. The UI dynamically discovers and renders all available components by introspecting this module at runtime.

---

## Project Overview

### Goals

1. **Dynamic Discovery**: UI automatically detects available Entry Patterns, Filters, Sessions, and Indicators from `builder_framework.py`
2. **Zero Hardcoding**: Adding a new filter/pattern to Python instantly makes it available in the UI
3. **Automated Optimization**: Grid search across parameter ranges to find optimal configurations
4. **Export to Production**: Transpile winning strategies to Pine Script v6 for TradingView deployment

### Key Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `builder_framework.py` | Strategy component library (Source of Truth) | Python + Decorators |
| `backtesting_framework.py` | Simulation engine | Python + Pandas/NumPy |
| `ui_app.py` | Dynamic web interface | NiceGUI (primary choice) |
| `optimizer.py` | Grid search & ranking engine | Python + Multiprocessing |
| `transpiler.py` | Python → Pine Script v6 converter | Python + Jinja2 templates |

---

## Phase 1: Foundation - Builder Framework Module (Week 1)

### Step 1.1: Create `builder_framework.py` Structure

**Objective:** Build a Python module that is introspection-friendly with metadata for UI generation.

**Implementation:**

```python
# src/builder_framework.py

from dataclasses import dataclass
from typing import Callable, Dict, List, Any, Optional
from enum import Enum
import pandas as pd

# ============================================
# METADATA DECORATORS (The Key to Dynamic UI)
# ============================================

@dataclass
class ComponentMetadata:
    """Metadata that the UI will introspect"""
    name: str
    display_name: str
    description: str
    category: str  # 'entry_pattern', 'filter', 'session', 'indicator', 'exit'
    parameters: Dict[str, Dict[str, Any]]
    enabled_by_default: bool = True

def component(category: str, name: str, display_name: str, description: str,
              parameters: Dict = None, enabled_by_default: bool = True):
    """
    Decorator that registers a component and attaches metadata
    This is what the UI will discover!
    """
    def decorator(func: Callable):
        metadata = ComponentMetadata(
            name=name,
            display_name=display_name,
            description=description,
            category=category,
            parameters=parameters or {},
            enabled_by_default=enabled_by_default
        )
        func.__component_metadata__ = metadata

        # Register in global registry
        COMPONENT_REGISTRY[category][name] = {
            'function': func,
            'metadata': metadata
        }

        return func
    return decorator

# Global registry that UI will query
COMPONENT_REGISTRY = {
    'entry_pattern': {},
    'filter': {},
    'session': {},
    'indicator': {},
    'exit': {}
}

# ============================================
# ENTRY PATTERNS
# ============================================

@component(
    category='entry_pattern',
    name='sacudida',
    display_name='Sacudida (Shake-out)',
    description='False breakout reversal pattern. Detects when price breaks a level then immediately reverses.',
    parameters={
        'direction': {
            'type': 'choice',
            'options': ['long', 'short', 'both'],
            'default': 'both',
            'display_name': 'Direction',
            'description': 'Trade direction'
        }
    }
)
def pattern_sacudida(df: pd.DataFrame, direction: str = 'both') -> pd.DataFrame:
    """
    Sacudida Pattern Detection

    Long Logic:
    - Bar[1]: Bearish candle breaks low[2]
    - Bar[0]: Bullish candle closes above low[2]

    Args:
        df: DataFrame with OHLCV data (columns: open, high, low, close, volume)
        direction: 'long', 'short', or 'both'

    Returns:
        DataFrame with new columns: signal_long, signal_short
    """
    df = df.copy()

    # Long signals
    vela2_bajista = (df['close'].shift(1) < df['open'].shift(1)).fillna(False)
    vela2_rompe_minimo = (df['low'].shift(1) < df['low'].shift(2)).fillna(False)
    vela3_alcista = (df['close'] > df['open']).fillna(False)
    vela3_confirmacion = (df['close'] > df['low'].shift(2)).fillna(False)

    df['signal_long'] = (vela2_bajista & vela2_rompe_minimo &
                         vela3_alcista & vela3_confirmacion)

    # Short signals
    vela2_alcista = (df['close'].shift(1) > df['open'].shift(1)).fillna(False)
    vela2_rompe_maximo = (df['high'].shift(1) > df['high'].shift(2)).fillna(False)
    vela3_bajista = (df['close'] < df['open']).fillna(False)
    vela3_confirmacion_short = (df['close'] < df['high'].shift(2)).fillna(False)

    df['signal_short'] = (vela2_alcista & vela2_rompe_maximo &
                          vela3_bajista & vela3_confirmacion_short)

    # Apply direction filter
    if direction == 'long':
        df['signal_short'] = False
    elif direction == 'short':
        df['signal_long'] = False

    return df

@component(
    category='entry_pattern',
    name='envolvente',
    display_name='Envolvente (Engulfing)',
    description='Classic candlestick engulfing pattern. Current candle completely engulfs the previous candle.',
    parameters={
        'direction': {
            'type': 'choice',
            'options': ['long', 'short', 'both'],
            'default': 'both',
            'display_name': 'Direction',
            'description': 'Trade direction'
        }
    }
)
def pattern_envolvente(df: pd.DataFrame, direction: str = 'both') -> pd.DataFrame:
    """Bullish/Bearish Engulfing Pattern"""
    df = df.copy()

    # Bullish engulfing
    vela_alcista = (df['close'] > df['open']).fillna(False)
    vela_bajista_prev = (df['close'].shift(1) < df['open'].shift(1)).fillna(False)
    cierra_sobre_ap1 = (df['close'] >= df['open'].shift(1)).fillna(False)
    abre_bajo_c1 = (df['open'] <= df['close'].shift(1)).fillna(False)

    df['signal_long'] = (vela_alcista & vela_bajista_prev &
                         cierra_sobre_ap1 & abre_bajo_c1)

    # Bearish engulfing
    vela_bajista = (df['close'] < df['open']).fillna(False)
    vela_alcista_prev = (df['close'].shift(1) > df['open'].shift(1)).fillna(False)
    cierra_bajo_ap1 = (df['close'] <= df['open'].shift(1)).fillna(False)
    abre_sobre_c1 = (df['open'] >= df['close'].shift(1)).fillna(False)

    df['signal_short'] = (vela_bajista & vela_alcista_prev &
                          cierra_bajo_ap1 & abre_sobre_c1)

    # Apply direction filter
    if direction == 'long':
        df['signal_short'] = False
    elif direction == 'short':
        df['signal_long'] = False

    return df

@component(
    category='entry_pattern',
    name='volumen_climatico',
    display_name='Volumen Climático (Climactic Volume)',
    description='High volume spike (>1.75x SMA) indicates climactic buying or selling.',
    parameters={
        'sma_period': {
            'type': 'int',
            'min': 5,
            'max': 50,
            'default': 20,
            'step': 1,
            'display_name': 'Volume SMA Period',
            'description': 'Period for volume moving average'
        },
        'multiplier': {
            'type': 'float',
            'min': 1.0,
            'max': 3.0,
            'default': 1.75,
            'step': 0.25,
            'display_name': 'Volume Multiplier',
            'description': 'Volume must exceed SMA by this factor'
        }
    }
)
def pattern_volumen_climatico(df: pd.DataFrame, sma_period: int = 20,
                               multiplier: float = 1.75) -> pd.DataFrame:
    """Climactic Volume Pattern"""
    df = df.copy()

    vol_ma = df['volume'].rolling(window=sma_period).mean()
    vol_climatico = (df['volume'] > vol_ma * multiplier).fillna(False)

    df['signal_long'] = vol_climatico & (df['close'] > df['open']).fillna(False)
    df['signal_short'] = vol_climatico & (df['close'] < df['open']).fillna(False)

    return df

# ============================================
# FILTERS
# ============================================

@component(
    category='filter',
    name='ma_cross',
    display_name='Moving Average Cross (50/200)',
    description='Filters trades based on relationship between 50 and 200 period SMAs.',
    parameters={
        'mode': {
            'type': 'choice',
            'options': ['no_filter', 'bullish', 'bearish'],
            'default': 'no_filter',
            'display_name': 'Filter Mode',
            'description': 'Bullish: MA50>MA200, Bearish: MA50<MA200'
        },
        'fast_period': {
            'type': 'int',
            'min': 10,
            'max': 100,
            'default': 50,
            'step': 5,
            'display_name': 'Fast MA Period',
            'description': 'Period for fast moving average',
            'optimizable': True
        },
        'slow_period': {
            'type': 'int',
            'min': 100,
            'max': 300,
            'default': 200,
            'step': 10,
            'display_name': 'Slow MA Period',
            'description': 'Period for slow moving average',
            'optimizable': True
        }
    }
)
def filter_ma_cross(df: pd.DataFrame, mode: str = 'no_filter',
                    fast_period: int = 50, slow_period: int = 200) -> pd.DataFrame:
    """MA 50/200 Cross Filter"""
    df = df.copy()

    sma_fast = df['close'].rolling(window=fast_period).mean()
    sma_slow = df['close'].rolling(window=slow_period).mean()

    if mode == 'no_filter':
        df['filter_ok'] = True
    elif mode == 'bullish':
        df['filter_ok'] = (sma_fast > sma_slow).fillna(False)
    elif mode == 'bearish':
        df['filter_ok'] = (sma_fast < sma_slow).fillna(False)
    else:
        df['filter_ok'] = True

    return df

@component(
    category='filter',
    name='rsi_filter',
    display_name='RSI Filter',
    description='Filters trades based on RSI overbought/oversold conditions.',
    parameters={
        'period': {
            'type': 'int',
            'min': 5,
            'max': 30,
            'default': 14,
            'step': 1,
            'display_name': 'RSI Period',
            'description': 'Period for RSI calculation',
            'optimizable': True
        },
        'oversold': {
            'type': 'int',
            'min': 10,
            'max': 40,
            'default': 30,
            'step': 5,
            'display_name': 'Oversold Threshold',
            'description': 'RSI below this = oversold (favor longs)',
            'optimizable': True
        },
        'overbought': {
            'type': 'int',
            'min': 60,
            'max': 90,
            'default': 70,
            'step': 5,
            'display_name': 'Overbought Threshold',
            'description': 'RSI above this = overbought (favor shorts)',
            'optimizable': True
        }
    }
)
def filter_rsi(df: pd.DataFrame, period: int = 14,
               oversold: int = 30, overbought: int = 70) -> pd.DataFrame:
    """RSI Filter"""
    df = df.copy()

    # Calculate RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    df['rsi'] = rsi
    df['filter_ok'] = True  # Default: no filter

    return df

# ============================================
# SESSIONS
# ============================================

@component(
    category='session',
    name='london',
    display_name='London Session',
    description='London trading session (01:00 - 08:15 UTC)',
    parameters={
        'enabled': {
            'type': 'bool',
            'default': True,
            'display_name': 'Enable London Session'
        }
    }
)
def session_london(df: pd.DataFrame, enabled: bool = True) -> pd.DataFrame:
    """London Session Filter"""
    df = df.copy()
    if not enabled:
        df['session_ok'] = df.get('session_ok', True)
        return df

    # Extract hour from index (assumes DatetimeIndex)
    hour = df.index.hour
    df['session_london'] = ((hour >= 1) & (hour < 8)) | (hour == 8)
    df['session_ok'] = df.get('session_ok', False) | df['session_london']

    return df

@component(
    category='session',
    name='newyork',
    display_name='New York Session',
    description='New York trading session (08:15 - 15:45 UTC)',
    parameters={
        'enabled': {
            'type': 'bool',
            'default': True,
            'display_name': 'Enable New York Session'
        }
    }
)
def session_newyork(df: pd.DataFrame, enabled: bool = True) -> pd.DataFrame:
    """New York Session Filter"""
    df = df.copy()
    if not enabled:
        df['session_ok'] = df.get('session_ok', True)
        return df

    hour = df.index.hour
    df['session_newyork'] = (hour >= 8) & (hour < 16)
    df['session_ok'] = df.get('session_ok', False) | df['session_newyork']

    return df

@component(
    category='session',
    name='tokyo',
    display_name='Tokyo Session',
    description='Tokyo trading session (15:45 - 01:00 UTC)',
    parameters={
        'enabled': {
            'type': 'bool',
            'default': True,
            'display_name': 'Enable Tokyo Session'
        }
    }
)
def session_tokyo(df: pd.DataFrame, enabled: bool = True) -> pd.DataFrame:
    """Tokyo Session Filter"""
    df = df.copy()
    if not enabled:
        df['session_ok'] = df.get('session_ok', True)
        return df

    hour = df.index.hour
    df['session_tokyo'] = (hour >= 16) | (hour < 1)
    df['session_ok'] = df.get('session_ok', False) | df['session_tokyo']

    return df

# ============================================
# DISCOVERY API (What the UI will call)
# ============================================

def get_all_components() -> Dict[str, Dict]:
    """
    Returns all registered components organized by category.
    This is the main entry point for the UI!
    """
    return COMPONENT_REGISTRY

def get_components_by_category(category: str) -> Dict:
    """Get all components of a specific category"""
    return COMPONENT_REGISTRY.get(category, {})

def get_component(category: str, name: str) -> Optional[Dict]:
    """Get a specific component"""
    return COMPONENT_REGISTRY.get(category, {}).get(name)
```

**Key Innovation:** The `@component` decorator automatically registers functions with metadata that describes:
- UI display name and description
- Parameter types, ranges, defaults
- Whether parameters are optimizable

---

### Step 1.2: Create `backtesting_framework.py`

**Objective:** Extract backtesting logic from the Jupyter notebook into a reusable module.

**Implementation:**

```python
# src/backtesting_framework.py

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class BacktestConfig:
    """Configuration for a backtest run"""
    initial_capital: float = 100000.0
    commission_per_trade: float = 1.5
    slippage_pips: float = 1.0
    risk_per_trade_pct: float = 1.0
    position_sizing: str = 'fixed'  # 'fixed', 'risk_pct', 'risk_fixed'
    fixed_qty: float = 1.0

@dataclass
class BacktestResult:
    """Results from a backtest"""
    equity_curve: pd.Series
    trades: pd.DataFrame
    metrics: Dict[str, float]
    parameters: Dict[str, any]

class BacktestEngine:
    """Core backtesting engine"""

    def __init__(self, config: BacktestConfig):
        self.config = config

    def run(self, df: pd.DataFrame, strategy_config: Dict) -> BacktestResult:
        """
        Run backtest with given strategy configuration

        Args:
            df: DataFrame with OHLCV + signal columns
            strategy_config: Dict with entry_pattern, filters, exits, etc.

        Returns:
            BacktestResult object
        """
        df = df.copy()

        # Initialize tracking arrays
        positions = np.zeros(len(df))
        entry_prices = np.zeros(len(df))
        stop_losses = np.zeros(len(df))
        take_profits = np.zeros(len(df))
        equity = np.full(len(df), self.config.initial_capital)

        # Track trades
        trades_list = []

        # Main backtest loop
        for i in range(1, len(df)):
            # Check for exits first
            if positions[i-1] != 0:
                exit_signal, exit_reason = self._check_exit(
                    df.iloc[i], positions[i-1],
                    entry_prices[i-1], stop_losses[i-1], take_profits[i-1]
                )

                if exit_signal:
                    # Close position
                    exit_price = df.iloc[i]['close']
                    pnl = self._calculate_pnl(
                        entry_prices[i-1], exit_price,
                        positions[i-1], self.config.commission_per_trade
                    )
                    equity[i] = equity[i-1] + pnl

                    # Log trade
                    trades_list.append({
                        'entry_bar': i - 1,
                        'exit_bar': i,
                        'direction': 'long' if positions[i-1] > 0 else 'short',
                        'entry_price': entry_prices[i-1],
                        'exit_price': exit_price,
                        'pnl': pnl,
                        'exit_reason': exit_reason
                    })

                    positions[i] = 0
                else:
                    # Carry forward position
                    positions[i] = positions[i-1]
                    entry_prices[i] = entry_prices[i-1]
                    stop_losses[i] = stop_losses[i-1]
                    take_profits[i] = take_profits[i-1]
                    equity[i] = equity[i-1]

            # Check for new entries (only if flat)
            if positions[i] == 0 and df.iloc[i].get('signal_long', False):
                positions[i], entry_prices[i], stop_losses[i], take_profits[i] = \
                    self._enter_long(df.iloc[i], equity[i-1])
                equity[i] = equity[i-1]

            elif positions[i] == 0 and df.iloc[i].get('signal_short', False):
                positions[i], entry_prices[i], stop_losses[i], take_profits[i] = \
                    self._enter_short(df.iloc[i], equity[i-1])
                equity[i] = equity[i-1]

        # Calculate metrics
        trades_df = pd.DataFrame(trades_list)
        metrics = self._calculate_metrics(equity, trades_df, df)

        return BacktestResult(
            equity_curve=pd.Series(equity, index=df.index),
            trades=trades_df,
            metrics=metrics,
            parameters=strategy_config
        )

    def _check_exit(self, row, position, entry, sl, tp) -> Tuple[bool, str]:
        """Check if position should be exited"""
        if position > 0:  # Long
            if row['low'] <= sl:
                return True, 'stop_loss'
            if row['high'] >= tp and tp > 0:
                return True, 'take_profit'
        elif position < 0:  # Short
            if row['high'] >= sl:
                return True, 'stop_loss'
            if row['low'] <= tp and tp > 0:
                return True, 'take_profit'

        return False, ''

    def _enter_long(self, row, current_equity) -> Tuple[float, float, float, float]:
        """Enter long position"""
        entry_price = row['high'] + self.config.slippage_pips
        sl = row['low'] - self.config.slippage_pips
        risk = entry_price - sl
        tp = entry_price + risk * 1.5  # 1.5:1 R:R

        qty = self._calculate_position_size(entry_price, sl, current_equity)

        return qty, entry_price, sl, tp

    def _enter_short(self, row, current_equity) -> Tuple[float, float, float, float]:
        """Enter short position"""
        entry_price = row['low'] - self.config.slippage_pips
        sl = row['high'] + self.config.slippage_pips
        risk = sl - entry_price
        tp = entry_price - risk * 1.5

        qty = self._calculate_position_size(entry_price, sl, current_equity)

        return -qty, entry_price, sl, tp

    def _calculate_position_size(self, entry, sl, equity) -> float:
        """Calculate position size based on risk"""
        if self.config.position_sizing == 'fixed':
            return self.config.fixed_qty

        risk_distance = abs(entry - sl)
        risk_money = equity * (self.config.risk_per_trade_pct / 100)
        qty = risk_money / risk_distance

        return max(qty, 0.01)  # Min position size

    def _calculate_pnl(self, entry, exit, qty, commission) -> float:
        """Calculate P&L for a trade"""
        gross_pnl = (exit - entry) * qty
        net_pnl = gross_pnl - (2 * commission)  # Entry + exit
        return net_pnl

    def _calculate_metrics(self, equity, trades_df, df) -> Dict[str, float]:
        """Calculate performance metrics"""
        if len(trades_df) == 0:
            return self._empty_metrics()

        returns = pd.Series(equity).pct_change().dropna()
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]

        metrics = {
            'total_trades': len(trades_df),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(trades_df) * 100 if len(trades_df) > 0 else 0,
            'total_pnl': trades_df['pnl'].sum(),
            'avg_win': winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0,
            'avg_loss': losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0,
            'profit_factor': abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) if len(losing_trades) > 0 and losing_trades['pnl'].sum() != 0 else 0,
            'max_drawdown': self._calculate_max_drawdown(equity),
            'sharpe_ratio': returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0,
            'final_equity': equity[-1],
            'roi': (equity[-1] - equity[0]) / equity[0] * 100
        }

        return metrics

    def _calculate_max_drawdown(self, equity) -> float:
        """Calculate maximum drawdown"""
        equity_series = pd.Series(equity)
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max * 100
        return drawdown.min()

    def _empty_metrics(self) -> Dict[str, float]:
        """Return empty metrics when no trades"""
        return {k: 0.0 for k in ['total_trades', 'winning_trades', 'losing_trades',
                                   'win_rate', 'total_pnl', 'avg_win', 'avg_loss',
                                   'profit_factor', 'max_drawdown', 'sharpe_ratio',
                                   'final_equity', 'roi']}
```

---

### Step 1.3: Verify Integration

**Test Script:**

```python
# test_framework.py

import yfinance as yf
from src.builder_framework import *
from src.backtesting_framework import BacktestEngine, BacktestConfig

# 1. Discovery Test
print("=" * 60)
print("DISCOVERY TEST - What the UI will see:")
print("=" * 60)

all_components = get_all_components()
for category, components in all_components.items():
    print(f"\n{category.upper()}:")
    for name, comp_data in components.items():
        metadata = comp_data['metadata']
        print(f"  - {metadata.display_name} ({name})")
        print(f"    Description: {metadata.description}")
        print(f"    Parameters: {list(metadata.parameters.keys())}")

# 2. Backtesting Test
print("\n" + "=" * 60)
print("BACKTEST TEST:")
print("=" * 60)

# Download data
df = yf.download('AAPL', start='2023-01-01', end='2024-01-01', interval='1d')
df.columns = [col.lower() for col in df.columns]

# Apply pattern
df = pattern_sacudida(df, direction='both')

# Apply filter
df = filter_ma_cross(df, mode='bullish', fast_period=50, slow_period=200)

# Run backtest
config = BacktestConfig(initial_capital=100000, commission_per_trade=1.5)
engine = BacktestEngine(config)
result = engine.run(df, {'pattern': 'sacudida', 'filter': 'ma_cross'})

print(f"\nBacktest Results:")
for key, value in result.metrics.items():
    print(f"  {key}: {value:.2f}")
```

---

## Phase 2: Dynamic UI Layer (Week 2)

### Step 2.1: Choose UI Framework

**Recommended: NiceGUI**

**Rationale:**
- Python-native (no JavaScript required)
- Reactive data binding
- Fast development
- Modern, clean UI
- Built on FastAPI (production-ready)

**Installation:**
```bash
pip install nicegui yfinance pandas numpy matplotlib
```

---

### Step 2.2: Build Dynamic UI App

**Implementation:**

```python
# src/ui_app.py

from nicegui import ui, app
from builder_framework import get_all_components, get_component
from backtesting_framework import BacktestEngine, BacktestConfig
import yfinance as yf
import pandas as pd
from typing import Dict, List, Any

class StrategyBuilderUI:
    def __init__(self):
        self.components = get_all_components()
        self.selected_pattern = None
        self.selected_filters = []
        self.selected_sessions = []
        self.parameter_widgets = {}
        self.optimization_ranges = {}

    def render(self):
        """Main render method"""
        with ui.header():
            ui.label('🚀 Dynamic Strategy Builder').classes('text-h4')

        with ui.row().classes('w-full gap-4'):
            # Left panel: Component selection
            with ui.card().classes('w-1/3'):
                self._render_component_selector()

            # Middle panel: Parameters
            with ui.card().classes('w-1/3'):
                self._render_parameter_editor()

            # Right panel: Optimization
            with ui.card().classes('w-1/3'):
                self._render_optimization_config()

        # Bottom panel: Results
        with ui.card().classes('w-full mt-4'):
            self._render_results_area()

    def _render_component_selector(self):
        """Dynamically render all available components"""
        ui.label('Step 1: Select Components').classes('text-h6 mb-2')

        # Entry Patterns (Radio buttons - select ONE)
        ui.label('Entry Pattern:').classes('font-bold mt-4')
        with ui.column():
            for name, comp_data in self.components['entry_pattern'].items():
                metadata = comp_data['metadata']
                ui.radio(
                    [metadata.display_name],
                    value=None,
                    on_change=lambda e, n=name: self._on_pattern_selected(n)
                ).props('dense')
                ui.label(metadata.description).classes('text-xs text-gray-600 ml-6 mb-2')

        # Filters (Checkboxes - select MULTIPLE)
        ui.label('Filters:').classes('font-bold mt-4')
        with ui.column():
            for name, comp_data in self.components['filter'].items():
                metadata = comp_data['metadata']
                ui.checkbox(
                    metadata.display_name,
                    value=metadata.enabled_by_default,
                    on_change=lambda e, n=name: self._on_filter_toggled(n, e.value)
                )
                ui.label(metadata.description).classes('text-xs text-gray-600 ml-6 mb-2')

        # Sessions
        ui.label('Trading Sessions:').classes('font-bold mt-4')
        with ui.column():
            for name, comp_data in self.components['session'].items():
                metadata = comp_data['metadata']
                ui.checkbox(
                    metadata.display_name,
                    value=metadata.enabled_by_default,
                    on_change=lambda e, n=name: self._on_session_toggled(n, e.value)
                )

    def _render_parameter_editor(self):
        """Dynamically render parameters for selected components"""
        ui.label('Step 2: Configure Parameters').classes('text-h6 mb-2')

        self.param_container = ui.column().classes('w-full')
        self._update_parameter_editor()

    def _update_parameter_editor(self):
        """Update parameter editor based on selected components"""
        self.param_container.clear()

        with self.param_container:
            # Pattern parameters
            if self.selected_pattern:
                comp_data = get_component('entry_pattern', self.selected_pattern)
                metadata = comp_data['metadata']

                ui.label(f'{metadata.display_name} Parameters:').classes('font-bold mt-2')
                self._render_parameters(metadata.parameters, self.selected_pattern)

            # Filter parameters
            for filter_name in self.selected_filters:
                comp_data = get_component('filter', filter_name)
                metadata = comp_data['metadata']

                ui.label(f'{metadata.display_name} Parameters:').classes('font-bold mt-4')
                self._render_parameters(metadata.parameters, filter_name)

    def _render_parameters(self, parameters: Dict, component_name: str):
        """Render individual parameters dynamically"""
        for param_name, param_spec in parameters.items():
            param_key = f"{component_name}.{param_name}"

            if param_spec['type'] == 'int':
                ui.number(
                    label=param_spec['display_name'],
                    value=param_spec['default'],
                    min=param_spec.get('min', 0),
                    max=param_spec.get('max', 1000),
                    step=param_spec.get('step', 1),
                    on_change=lambda e, k=param_key: self._on_param_changed(k, e.value)
                ).props('dense outlined').classes('w-full')

                # Add optimization range if optimizable
                if param_spec.get('optimizable', False):
                    with ui.row().classes('w-full gap-2 mt-1 mb-2'):
                        ui.label('Optimize range:').classes('text-xs')
                        ui.number(
                            label='Min',
                            value=param_spec.get('min', 0),
                            on_change=lambda e, k=param_key: self._set_opt_min(k, e.value)
                        ).props('dense outlined').classes('w-20')
                        ui.number(
                            label='Max',
                            value=param_spec.get('max', 100),
                            on_change=lambda e, k=param_key: self._set_opt_max(k, e.value)
                        ).props('dense outlined').classes('w-20')

            elif param_spec['type'] == 'float':
                ui.number(
                    label=param_spec['display_name'],
                    value=param_spec['default'],
                    min=param_spec.get('min', 0.0),
                    max=param_spec.get('max', 100.0),
                    step=param_spec.get('step', 0.1),
                    format='%.2f',
                    on_change=lambda e, k=param_key: self._on_param_changed(k, e.value)
                ).props('dense outlined').classes('w-full')

            elif param_spec['type'] == 'choice':
                ui.select(
                    label=param_spec['display_name'],
                    options=param_spec['options'],
                    value=param_spec['default'],
                    on_change=lambda e, k=param_key: self._on_param_changed(k, e.value)
                ).props('dense outlined').classes('w-full')

            elif param_spec['type'] == 'bool':
                ui.checkbox(
                    param_spec['display_name'],
                    value=param_spec['default'],
                    on_change=lambda e, k=param_key: self._on_param_changed(k, e.value)
                )

            # Description
            ui.label(param_spec.get('description', '')).classes('text-xs text-gray-600 mb-3')

    def _render_optimization_config(self):
        """Optimization configuration"""
        ui.label('Step 3: Optimization').classes('text-h6 mb-2')

        with ui.column().classes('w-full gap-2'):
            self.asset_input = ui.input(
                label='Asset Symbol',
                value='AAPL',
                placeholder='e.g., AAPL, EURUSD=X, BTC-USD'
            ).props('dense outlined')

            self.timeframe_select = ui.select(
                label='Timeframe',
                options=['1m', '5m', '15m', '1h', '1d'],
                value='1d'
            ).props('dense outlined')

            with ui.row().classes('w-full gap-2'):
                self.start_date = ui.input(
                    label='Start Date',
                    value='2023-01-01'
                ).props('dense outlined type=date')

                self.end_date = ui.input(
                    label='End Date',
                    value='2024-01-01'
                ).props('dense outlined type=date')

            ui.button(
                'Run Single Backtest',
                on_click=self._run_single_backtest,
                icon='play_arrow'
            ).props('color=primary')

            ui.button(
                'Run Optimization',
                on_click=self._run_optimization,
                icon='tune'
            ).props('color=secondary')

    def _render_results_area(self):
        """Results display area"""
        ui.label('Results').classes('text-h6 mb-2')
        self.results_container = ui.column().classes('w-full')

    # Event handlers
    def _on_pattern_selected(self, pattern_name: str):
        self.selected_pattern = pattern_name
        self._update_parameter_editor()

    def _on_filter_toggled(self, filter_name: str, enabled: bool):
        if enabled and filter_name not in self.selected_filters:
            self.selected_filters.append(filter_name)
        elif not enabled and filter_name in self.selected_filters:
            self.selected_filters.remove(filter_name)
        self._update_parameter_editor()

    def _on_session_toggled(self, session_name: str, enabled: bool):
        if enabled and session_name not in self.selected_sessions:
            self.selected_sessions.append(session_name)
        elif not enabled and session_name in self.selected_sessions:
            self.selected_sessions.remove(session_name)

    def _on_param_changed(self, param_key: str, value: Any):
        self.parameter_widgets[param_key] = value

    def _set_opt_min(self, param_key: str, value: float):
        if param_key not in self.optimization_ranges:
            self.optimization_ranges[param_key] = {}
        self.optimization_ranges[param_key]['min'] = value

    def _set_opt_max(self, param_key: str, value: float):
        if param_key not in self.optimization_ranges:
            self.optimization_ranges[param_key] = {}
        self.optimization_ranges[param_key]['max'] = value

    async def _run_single_backtest(self):
        """Run a single backtest with current parameters"""
        ui.notify('Running backtest...', type='info')

        # Download data
        df = yf.download(
            self.asset_input.value,
            start=self.start_date.value,
            end=self.end_date.value,
            interval=self.timeframe_select.value
        )
        df.columns = [col.lower() for col in df.columns]

        # Apply pattern
        if self.selected_pattern:
            pattern_func = get_component('entry_pattern', self.selected_pattern)['function']
            df = pattern_func(df)

        # Run backtest
        config = BacktestConfig()
        engine = BacktestEngine(config)
        result = engine.run(df, {})

        # Display results
        self._display_results(result)

        ui.notify('Backtest complete!', type='positive')

    async def _run_optimization(self):
        """Run optimization across parameter ranges"""
        ui.notify('Starting optimization...', type='info')
        # Implementation in Phase 3
        pass

    def _display_results(self, result):
        """Display backtest results"""
        self.results_container.clear()

        with self.results_container:
            with ui.grid(columns=4).classes('w-full gap-4'):
                self._metric_card('Total Trades', result.metrics['total_trades'], '')
                self._metric_card('Win Rate', result.metrics['win_rate'], '%')
                self._metric_card('Profit Factor', result.metrics['profit_factor'], '')
                self._metric_card('ROI', result.metrics['roi'], '%')
                self._metric_card('Max Drawdown', result.metrics['max_drawdown'], '%')
                self._metric_card('Sharpe Ratio', result.metrics['sharpe_ratio'], '')

    def _metric_card(self, label: str, value: float, suffix: str):
        """Render a metric card"""
        with ui.card().classes('p-4'):
            ui.label(label).classes('text-sm text-gray-600')
            ui.label(f'{value:.2f}{suffix}').classes('text-2xl font-bold')

# Main entry point
def main():
    ui.page_title = 'Strategy Builder'

    builder = StrategyBuilderUI()
    builder.render()

    ui.run(title='Strategy Builder', port=8080)

if __name__ in {"__main__", "__mp_main__"}:
    main()
```

**Key Features:**
- ✅ **Zero Hardcoding**: All UI elements generated from `builder_framework` metadata
- ✅ **Automatic Discovery**: New components appear instantly
- ✅ **Smart Parameter Types**: int → Number input, choice → Dropdown, bool → Checkbox
- ✅ **Optimization Ready**: Optional min/max ranges for optimizable parameters

---

## Phase 3: Optimization Engine (Week 3)

### Step 3.1: Create `optimizer.py`

```python
# src/optimizer.py

from backtesting_framework import BacktestEngine, BacktestConfig
from builder_framework import get_component
import pandas as pd
from itertools import product
from multiprocessing import Pool, cpu_count
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class OptimizationResult:
    """Single optimization result"""
    parameters: Dict
    metrics: Dict
    rank_score: float

class StrategyOptimizer:
    def __init__(self, config: BacktestConfig, n_jobs: int = -1):
        self.config = config
        self.n_jobs = cpu_count() if n_jobs == -1 else n_jobs

    def optimize(self, df: pd.DataFrame, pattern_name: str,
                 parameter_ranges: Dict[str, List]) -> List[OptimizationResult]:
        """
        Grid search optimization

        Args:
            df: Market data
            pattern_name: Entry pattern to use
            parameter_ranges: Dict of {param_name: [val1, val2, ...]}

        Returns:
            List of OptimizationResult sorted by rank_score
        """
        # Generate all parameter combinations
        param_names = list(parameter_ranges.keys())
        param_values = list(parameter_ranges.values())
        combinations = list(product(*param_values))

        print(f"Testing {len(combinations)} parameter combinations...")

        # Prepare jobs
        jobs = []
        for combo in combinations:
            params = dict(zip(param_names, combo))
            jobs.append((df.copy(), pattern_name, params, self.config))

        # Run in parallel
        with Pool(self.n_jobs) as pool:
            results = pool.map(_run_single_backtest_worker, jobs)

        # Rank results
        results = [r for r in results if r is not None]
        results = self._rank_results(results)

        return results

    def _rank_results(self, results: List[OptimizationResult]) -> List[OptimizationResult]:
        """
        Rank results by composite score
        Score = (ROI * 0.3) + (Profit Factor * 0.3) + (1 - abs(Max DD) * 0.4)
        """
        for result in results:
            m = result.metrics
            score = (
                (m['roi'] / 100 * 0.3) +
                (m['profit_factor'] / 3 * 0.3) +
                (1 - abs(m['max_drawdown']) / 100 * 0.4)
            )
            result.rank_score = score

        results.sort(key=lambda r: r.rank_score, reverse=True)
        return results

def _run_single_backtest_worker(args: Tuple) -> OptimizationResult:
    """Worker function for parallel backtesting"""
    df, pattern_name, params, config = args

    try:
        # Apply pattern with parameters
        pattern_func = get_component('entry_pattern', pattern_name)['function']
        df_signals = pattern_func(df, **params)

        # Run backtest
        engine = BacktestEngine(config)
        result = engine.run(df_signals, params)

        return OptimizationResult(
            parameters=params,
            metrics=result.metrics,
            rank_score=0.0  # Will be set in ranking
        )
    except Exception as e:
        print(f"Error with params {params}: {e}")
        return None
```

### Step 3.2: Integrate Optimizer into UI

Add to `ui_app.py`:

```python
async def _run_optimization(self):
    """Run optimization across parameter ranges"""
    if not self.optimization_ranges:
        ui.notify('No optimization ranges defined', type='warning')
        return

    ui.notify('Starting optimization (this may take a while)...', type='info')

    # Download data
    df = yf.download(
        self.asset_input.value,
        start=self.start_date.value,
        end=self.end_date.value,
        interval=self.timeframe_select.value
    )
    df.columns = [col.lower() for col in df.columns]

    # Build parameter ranges for optimization
    param_ranges = {}
    for param_key, range_spec in self.optimization_ranges.items():
        component_name, param_name = param_key.split('.')
        metadata = get_component('entry_pattern', component_name)['metadata']
        param_spec = metadata.parameters[param_name]

        min_val = range_spec.get('min', param_spec['min'])
        max_val = range_spec.get('max', param_spec['max'])
        step = param_spec.get('step', 1)

        param_ranges[param_name] = list(range(int(min_val), int(max_val) + 1, int(step)))

    # Run optimization
    from optimizer import StrategyOptimizer
    config = BacktestConfig()
    optimizer = StrategyOptimizer(config)
    results = optimizer.optimize(df, self.selected_pattern, param_ranges)

    # Display top 10 results
    self._display_optimization_results(results[:10])

    ui.notify(f'Optimization complete! Best score: {results[0].rank_score:.3f}', type='positive')

def _display_optimization_results(self, results: List):
    """Display optimization results table"""
    self.results_container.clear()

    with self.results_container:
        ui.label('Top 10 Configurations').classes('text-h6 mb-4')

        # Build table data
        columns = [
            {'name': 'rank', 'label': 'Rank', 'field': 'rank'},
            {'name': 'score', 'label': 'Score', 'field': 'score'},
            {'name': 'roi', 'label': 'ROI %', 'field': 'roi'},
            {'name': 'pf', 'label': 'Profit Factor', 'field': 'pf'},
            {'name': 'trades', 'label': 'Trades', 'field': 'trades'},
            {'name': 'params', 'label': 'Parameters', 'field': 'params'}
        ]

        rows = []
        for i, result in enumerate(results, 1):
            rows.append({
                'rank': i,
                'score': f"{result.rank_score:.3f}",
                'roi': f"{result.metrics['roi']:.2f}",
                'pf': f"{result.metrics['profit_factor']:.2f}",
                'trades': int(result.metrics['total_trades']),
                'params': str(result.parameters)
            })

        ui.table(columns=columns, rows=rows).classes('w-full')
```

---

## Phase 4: Export to Pine Script (Week 4)

### Step 4.1: Create `transpiler.py`

```python
# src/transpiler.py

from typing import Dict
from jinja2 import Template

PINE_SCRIPT_TEMPLATE = """
//@version=6
strategy('{{strategy_name}}', overlay=true, initial_capital={{initial_capital}},
         commission_type=strategy.commission.cash_per_contract,
         commission_value={{commission}}, slippage={{slippage}})

// ============================================
// GENERATED PARAMETERS
// ============================================

{% for param_name, param_value in parameters.items() %}
{{param_name}} = input.{{param_type(param_value)}}({{param_value}}, '{{param_display(param_name)}}')
{% endfor %}

// ============================================
// PATTERN LOGIC
// ============================================

{% if pattern == 'sacudida' %}
// Sacudida Pattern
sacudida_long_condition() =>
    vela2_bajista = close[1] < open[1]
    vela2_rompe_minimo = low[1] < low[2]
    vela3_alcista = close > open
    vela3_confirmacion = close > low[2]
    vela2_bajista and vela2_rompe_minimo and vela3_alcista and vela3_confirmacion

sacudida_short_condition() =>
    vela2_alcista = close[1] > open[1]
    vela2_rompe_maximo = high[1] > high[2]
    vela3_bajista = close < open
    vela3_confirmacion = close < high[2]
    vela2_alcista and vela2_rompe_maximo and vela3_bajista and vela3_confirmacion

long_signal = sacudida_long_condition()
short_signal = sacudida_short_condition()
{% endif %}

{% if pattern == 'envolvente' %}
// Engulfing Pattern
bullEngulf() =>
    VelaAlcista = close > open
    VelaBajistaPrev = close[1] < open[1]
    cierra_sobre_ap1 = close >= open[1]
    abre_bajo_c1 = open <= close[1]
    VelaAlcista and VelaBajistaPrev and cierra_sobre_ap1 and abre_bajo_c1

bearEngulf() =>
    VelaBajista = close < open
    VelaAlcistaPrev = close[1] > open[1]
    cierra_bajo_ap1 = close <= open[1]
    abre_sobre_c1 = open >= close[1]
    VelaBajista and VelaAlcistaPrev and cierra_bajo_ap1 and abre_sobre_c1

long_signal = bullEngulf()
short_signal = bearEngulf()
{% endif %}

// ============================================
// FILTERS
// ============================================

{% if filters %}
{% for filter_name, filter_params in filters.items() %}
{% if filter_name == 'ma_cross' %}
sma{{filter_params.fast_period}} = ta.sma(close, {{filter_params.fast_period}})
sma{{filter_params.slow_period}} = ta.sma(close, {{filter_params.slow_period}})
filter_ok = sma{{filter_params.fast_period}} > sma{{filter_params.slow_period}}
{% endif %}
{% endfor %}
{% else %}
filter_ok = true
{% endif %}

// ============================================
// ENTRIES
// ============================================

if long_signal and filter_ok
    strategy.entry('Long', strategy.long)

if short_signal and filter_ok
    strategy.entry('Short', strategy.short)

// ============================================
// EXITS
// ============================================

// Stop loss and take profit logic here
"""

class PineScriptTranspiler:
    def __init__(self):
        self.template = Template(PINE_SCRIPT_TEMPLATE)

    def transpile(self, strategy_config: Dict) -> str:
        """
        Convert Python strategy configuration to Pine Script v6

        Args:
            strategy_config: Dict with pattern, filters, parameters, etc.

        Returns:
            Pine Script v6 code string
        """
        context = {
            'strategy_name': strategy_config.get('name', 'Generated Strategy'),
            'initial_capital': strategy_config.get('initial_capital', 100000),
            'commission': strategy_config.get('commission', 1.5),
            'slippage': strategy_config.get('slippage', 1),
            'pattern': strategy_config.get('pattern'),
            'parameters': strategy_config.get('parameters', {}),
            'filters': strategy_config.get('filters', {}),
            'param_type': self._get_param_type,
            'param_display': self._format_param_display
        }

        return self.template.render(**context)

    def _get_param_type(self, value) -> str:
        """Determine Pine Script input type"""
        if isinstance(value, bool):
            return 'bool'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            return 'string'
        return 'int'

    def _format_param_display(self, param_name: str) -> str:
        """Format parameter name for display"""
        return param_name.replace('_', ' ').title()

# Usage example
def export_strategy(optimization_result, output_path: str):
    """Export optimized strategy to Pine Script file"""
    transpiler = PineScriptTranspiler()

    strategy_config = {
        'name': f"Optimized {optimization_result.parameters}",
        'pattern': 'sacudida',
        'parameters': optimization_result.parameters,
        'filters': {},
        'initial_capital': 100000,
        'commission': 1.5,
        'slippage': 1
    }

    pine_code = transpiler.transpile(strategy_config)

    with open(output_path, 'w') as f:
        f.write(pine_code)

    print(f"Strategy exported to {output_path}")
```

### Step 4.2: Add Export Button to UI

In `ui_app.py`:

```python
def _display_optimization_results(self, results: List):
    """Display optimization results table with export buttons"""
    self.results_container.clear()

    with self.results_container:
        ui.label('Top 10 Configurations').classes('text-h6 mb-4')

        # Table with export buttons
        for i, result in enumerate(results[:10], 1):
            with ui.card().classes('p-4 mb-2'):
                with ui.row().classes('w-full justify-between items-center'):
                    with ui.column():
                        ui.label(f'#{i} - Score: {result.rank_score:.3f}').classes('font-bold')
                        ui.label(f'ROI: {result.metrics["roi"]:.2f}% | PF: {result.metrics["profit_factor"]:.2f} | Trades: {result.metrics["total_trades"]:.0f}')
                        ui.label(f'Parameters: {result.parameters}').classes('text-xs text-gray-600')

                    ui.button(
                        'Export to Pine Script',
                        on_click=lambda r=result: self._export_to_pine(r),
                        icon='download'
                    ).props('color=green')

def _export_to_pine(self, result):
    """Export strategy to Pine Script"""
    from transpiler import PineScriptTranspiler, export_strategy

    output_path = f'strategies/strategy_{result.rank_score:.3f}.pine'
    export_strategy(result, output_path)

    ui.notify(f'Strategy exported to {output_path}', type='positive')
```

---

## Directory Structure

```
strategy-builder/
├── README.md
├── PLAN.md (this file)
├── ARCHITECTURE.md
├── CLAUDE.md
│
├── legacy/                          # Original files
│   ├── Algo Strategy Builder.txt
│   └── Backtesting Validacion Framework.ipynb
│
├── src/                             # Core framework
│   ├── __init__.py
│   ├── builder_framework.py         # Source of Truth
│   ├── backtesting_framework.py     # Simulation engine
│   ├── optimizer.py                 # Grid search engine
│   ├── transpiler.py                # Python → Pine Script
│   └── ui_app.py                    # NiceGUI web interface
│
├── strategies/                      # Exported strategies
│   └── (Generated .pine files)
│
├── tests/                           # Unit tests
│   ├── test_builder_framework.py
│   ├── test_backtesting.py
│   └── test_transpiler.py
│
├── notebooks/                       # Analysis notebooks
│   └── validation_analysis.ipynb
│
├── data/                            # Cached market data
│   └── .gitkeep
│
├── requirements.txt
├── setup.py
└── .gitignore
```

---

## Implementation Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **Phase 1: Foundation** | Week 1 | `builder_framework.py`, `backtesting_framework.py`, tests |
| **Phase 2: Dynamic UI** | Week 2 | `ui_app.py` with full discovery + parameter rendering |
| **Phase 3: Optimization** | Week 3 | `optimizer.py`, parallel grid search, results ranking |
| **Phase 4: Export** | Week 4 | `transpiler.py`, Pine Script templates, export functionality |
| **Phase 5: Polish** | Week 5 | Documentation, error handling, deployment guide |

---

## Success Criteria

✅ **Dynamic Discovery**: Adding a new `@component` to `builder_framework.py` instantly appears in UI
✅ **Zero Hardcoding**: No UI code references specific patterns/filters by name
✅ **Optimization Works**: Grid search completes in reasonable time (<5 min for 100 combinations)
✅ **Export Valid**: Generated Pine Script compiles in TradingView without errors
✅ **User-Friendly**: Non-technical users can configure and run optimizations

---

## Next Steps

1. Review this plan with stakeholders
2. Set up development environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install nicegui pandas numpy yfinance matplotlib jinja2
   ```
3. Create repository structure
4. Begin Phase 1 implementation

---

## Notes

- **Performance**: For large optimizations (>1000 combinations), consider using Optuna or Ray Tune instead of grid search
- **Testing**: Add unit tests for each component before integration
- **Security**: If deploying publicly, add authentication (NiceGUI supports OAuth)
- **Database**: For production, store optimization results in SQLite/PostgreSQL instead of memory

---

**Last Updated**: 2025-11-20
**Version**: 1.0
**Author**: Claude (AI Assistant)
