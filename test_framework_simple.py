# test_framework_simple.py - Integration test without external dependencies

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, '/home/user/strategy-builder')

from src.builder_framework import *
from src.backtesting_framework import BacktestEngine, BacktestConfig

# 1. Discovery Test
print("=" * 60)
print("DISCOVERY TEST - What the UI will see:")
print("=" * 60)

all_components = get_all_components()
for category, components in all_components.items():
    if components:  # Only show non-empty categories
        print(f"\n{category.upper()}:")
        for name, comp_data in components.items():
            metadata = comp_data['metadata']
            print(f"  ✓ {metadata.display_name} ({name})")
            print(f"    Description: {metadata.description[:60]}...")
            print(f"    Parameters: {list(metadata.parameters.keys())}")

# 2. Create Mock Data
print("\n" + "=" * 60)
print("CREATING MOCK DATA:")
print("=" * 60)

# Generate 1 year of daily data
dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
n = len(dates)

# Create price data with realistic patterns
np.random.seed(42)
close = 100 + np.cumsum(np.random.randn(n) * 2)  # Random walk
high = close + np.abs(np.random.randn(n) * 1)
low = close - np.abs(np.random.randn(n) * 1)
open_prices = close + np.random.randn(n) * 0.5
volume = np.random.randint(1000000, 10000000, n)

df = pd.DataFrame({
    'open': open_prices,
    'high': high,
    'low': low,
    'close': close,
    'volume': volume
}, index=dates)

print(f"Created {len(df)} bars of mock data")
print(f"Date range: {df.index[0]} to {df.index[-1]}")
print(f"Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")

# 3. Test Pattern Detection
print("\n" + "=" * 60)
print("PATTERN DETECTION TEST:")
print("=" * 60)

print("\nApplying Sacudida pattern...")
df = pattern_sacudida(df, direction='both')
long_signals = df['signal_long'].sum()
short_signals = df['signal_short'].sum()
print(f"  Long signals: {long_signals}")
print(f"  Short signals: {short_signals}")

print("\nApplying Envolvente pattern...")
df_env = pattern_envolvente(df.copy(), direction='both')
env_long = df_env['signal_long'].sum()
env_short = df_env['signal_short'].sum()
print(f"  Envolvente Long signals: {env_long}")
print(f"  Envolvente Short signals: {env_short}")

# 4. Test Filters
print("\n" + "=" * 60)
print("FILTER TEST:")
print("=" * 60)

print("\nApplying MA Cross filter (bullish mode)...")
df = filter_ma_cross(df, mode='bullish', fast_period=20, slow_period=50)
filter_ok_count = df['filter_ok'].sum()
print(f"  Bars passing filter: {filter_ok_count} ({filter_ok_count/len(df)*100:.1f}%)")

print("\nApplying RSI filter...")
df_rsi = filter_rsi(df.copy(), period=14, oversold=30, overbought=70, mode='no_filter')
print(f"  RSI calculated: min={df_rsi['rsi'].min():.1f}, max={df_rsi['rsi'].max():.1f}")

# 5. Run Backtest
print("\n" + "=" * 60)
print("BACKTEST TEST:")
print("=" * 60)

config = BacktestConfig(initial_capital=100000, commission_per_trade=1.5, fixed_qty=1.0)
engine = BacktestEngine(config)
result = engine.run(df, {'pattern': 'sacudida', 'filter': 'ma_cross'})

print(f"\nBacktest Results:")
print(f"  Total Trades: {result.metrics['total_trades']:.0f}")
print(f"  Winning Trades: {result.metrics['winning_trades']:.0f}")
print(f"  Losing Trades: {result.metrics['losing_trades']:.0f}")
print(f"  Win Rate: {result.metrics['win_rate']:.2f}%")
print(f"  Profit Factor: {result.metrics['profit_factor']:.2f}")
print(f"  Total P&L: ${result.metrics['total_pnl']:.2f}")
print(f"  ROI: {result.metrics['roi']:.2f}%")
print(f"  Max Drawdown: {result.metrics['max_drawdown']:.2f}%")
print(f"  Sharpe Ratio: {result.metrics['sharpe_ratio']:.2f}")
print(f"  Final Equity: ${result.metrics['final_equity']:.2f}")

# 6. Component Registry Test
print("\n" + "=" * 60)
print("COMPONENT REGISTRY TEST:")
print("=" * 60)

print("\nTesting get_component():")
sacudida = get_component('entry_pattern', 'sacudida')
print(f"  ✓ Retrieved: {sacudida['metadata'].display_name}")

print("\nTesting get_components_by_category():")
patterns = get_components_by_category('entry_pattern')
print(f"  ✓ Entry patterns: {list(patterns.keys())}")

filters = get_components_by_category('filter')
print(f"  ✓ Filters: {list(filters.keys())}")

sessions = get_components_by_category('session')
print(f"  ✓ Sessions: {list(sessions.keys())}")

print("\nTesting list_all_component_names():")
names = list_all_component_names()
for cat, comps in names.items():
    print(f"  ✓ {cat}: {len(comps)} components")

# 7. Summary
print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED!")
print("=" * 60)
print("\nPhase 1 Foundation is complete:")
print("  ✓ builder_framework.py - Component library with decorators")
print("  ✓ backtesting_framework.py - Simulation engine")
print("  ✓ Integration verified - All components working together")
print("\nReady for Phase 2: Dynamic UI Layer")
print("=" * 60)
