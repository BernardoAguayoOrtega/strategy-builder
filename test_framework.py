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
    if components:  # Only show non-empty categories
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
print("\nDownloading AAPL data for 2023...")
df = yf.download('AAPL', start='2023-01-01', end='2024-01-01', interval='1d', progress=False)
df.columns = [col.lower() for col in df.columns]
print(f"Downloaded {len(df)} bars")

# Apply pattern
print("\nApplying Sacudida pattern...")
df = pattern_sacudida(df, direction='both')
long_signals = df['signal_long'].sum()
short_signals = df['signal_short'].sum()
print(f"Long signals: {long_signals}")
print(f"Short signals: {short_signals}")

# Apply filter
print("\nApplying MA Cross filter (bullish mode)...")
df = filter_ma_cross(df, mode='bullish', fast_period=50, slow_period=200)
filter_ok_count = df['filter_ok'].sum()
print(f"Bars passing filter: {filter_ok_count}")

# Run backtest
print("\nRunning backtest...")
config = BacktestConfig(initial_capital=100000, commission_per_trade=1.5)
engine = BacktestEngine(config)
result = engine.run(df, {'pattern': 'sacudida', 'filter': 'ma_cross'})

print(f"\nBacktest Results:")
print(f"  Total Trades: {result.metrics['total_trades']:.0f}")
print(f"  Win Rate: {result.metrics['win_rate']:.2f}%")
print(f"  Profit Factor: {result.metrics['profit_factor']:.2f}")
print(f"  Total P&L: ${result.metrics['total_pnl']:.2f}")
print(f"  ROI: {result.metrics['roi']:.2f}%")
print(f"  Max Drawdown: {result.metrics['max_drawdown']:.2f}%")
print(f"  Sharpe Ratio: {result.metrics['sharpe_ratio']:.2f}")

print("\n" + "=" * 60)
print("INTEGRATION TEST COMPLETE!")
print("=" * 60)

# 3. Component Registry Test
print("\n" + "=" * 60)
print("COMPONENT REGISTRY TEST:")
print("=" * 60)

print("\nTesting get_component() function:")
sacudida = get_component('entry_pattern', 'sacudida')
print(f"  Sacudida function: {sacudida['function'].__name__}")
print(f"  Sacudida metadata: {sacudida['metadata'].display_name}")

print("\nTesting get_components_by_category() function:")
patterns = get_components_by_category('entry_pattern')
print(f"  Entry patterns: {list(patterns.keys())}")

filters = get_components_by_category('filter')
print(f"  Filters: {list(filters.keys())}")

sessions = get_components_by_category('session')
print(f"  Sessions: {list(sessions.keys())}")

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
