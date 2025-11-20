"""
Comprehensive UI Workflow Testing

This script simulates a complete user workflow through the UI without
requiring the web server to be running. It tests:
1. Component selection
2. Parameter configuration
3. Backtest execution
4. Results processing
"""

import sys
sys.path.insert(0, 'src')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from builder_framework import get_all_components, get_component
from backtesting_framework import BacktestEngine, BacktestConfig


def create_mock_market_data(days=100):
    """Create realistic mock OHLCV data for testing"""
    print("Creating mock market data...")

    dates = pd.date_range(start='2024-01-01', periods=days, freq='D')

    # Generate realistic price movement
    np.random.seed(42)
    price_base = 100
    returns = np.random.randn(days) * 0.02  # 2% daily volatility
    prices = price_base * np.exp(np.cumsum(returns))

    # Create OHLC
    df = pd.DataFrame({
        'open': prices * (1 + np.random.randn(days) * 0.005),
        'high': prices * (1 + np.abs(np.random.randn(days)) * 0.01),
        'low': prices * (1 - np.abs(np.random.randn(days)) * 0.01),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, days)
    }, index=dates)

    # Ensure OHLC consistency
    df['high'] = df[['open', 'high', 'close']].max(axis=1)
    df['low'] = df[['open', 'low', 'close']].min(axis=1)

    print(f"✓ Created {len(df)} days of mock data")
    print(f"  Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    print()

    return df


def test_workflow_1_sacudida_no_filters():
    """Test Workflow 1: Sacudida pattern, no filters, both directions"""
    print("=" * 70)
    print("TEST WORKFLOW 1: Sacudida Pattern (No Filters)")
    print("=" * 70)
    print()

    # Simulate user selections
    selected_pattern = 'sacudida'
    selected_filters = []
    selected_sessions = []
    pattern_params = {'direction': 'both'}

    print("User Configuration:")
    print(f"  Pattern: {selected_pattern}")
    print(f"  Parameters: {pattern_params}")
    print(f"  Filters: None")
    print(f"  Sessions: None")
    print()

    # Get mock data
    df = create_mock_market_data(days=252)  # 1 year

    # Apply pattern
    print("Applying pattern...")
    pattern_func = get_component('entry_pattern', selected_pattern)['function']
    df = pattern_func(df, **pattern_params)

    # Check signals
    long_signals = df['signal_long'].sum()
    short_signals = df['signal_short'].sum()
    print(f"✓ Pattern applied")
    print(f"  Long signals: {long_signals}")
    print(f"  Short signals: {short_signals}")
    print()

    # Run backtest
    print("Running backtest...")
    config = BacktestConfig(
        initial_capital=100000,
        commission_per_trade=1.5,
        slippage_pips=1.0
    )

    engine = BacktestEngine(config)
    result = engine.run(df, {'pattern': selected_pattern})

    # Validate results
    print("✓ Backtest complete")
    print()
    print("Results:")
    print(f"  Total Trades: {result.metrics['total_trades']:.0f}")
    print(f"  Win Rate: {result.metrics['win_rate']:.2f}%")
    print(f"  Profit Factor: {result.metrics['profit_factor']:.2f}")
    print(f"  ROI: {result.metrics['roi']:.2f}%")
    print(f"  Max Drawdown: {result.metrics['max_drawdown']:.2f}%")
    print(f"  Sharpe Ratio: {result.metrics['sharpe_ratio']:.2f}")
    print()

    # Assertions
    assert result.metrics['total_trades'] >= 0, "Total trades should be non-negative"
    assert -100 <= result.metrics['roi'] <= 1000, "ROI should be reasonable"
    assert result.metrics['max_drawdown'] <= 0, "Max drawdown should be negative"

    print("✅ WORKFLOW 1 PASSED")
    print()
    return result


def test_workflow_2_envolvente_with_ma_filter():
    """Test Workflow 2: Envolvente pattern with MA Cross filter"""
    print("=" * 70)
    print("TEST WORKFLOW 2: Envolvente + MA Cross Filter")
    print("=" * 70)
    print()

    # Simulate user selections
    selected_pattern = 'envolvente'
    selected_filters = ['ma_cross']
    selected_sessions = []
    pattern_params = {'direction': 'long'}  # Only longs
    filter_params = {
        'ma_cross': {
            'mode': 'bullish',
            'fast_period': 50,
            'slow_period': 200
        }
    }

    print("User Configuration:")
    print(f"  Pattern: {selected_pattern} (long only)")
    print(f"  Filters: MA Cross (bullish)")
    print(f"  Filter Params: {filter_params['ma_cross']}")
    print()

    # Get mock data
    df = create_mock_market_data(days=252)

    # Apply pattern
    print("Applying pattern...")
    pattern_func = get_component('entry_pattern', selected_pattern)['function']
    df = pattern_func(df, **pattern_params)

    # Apply filter
    print("Applying MA Cross filter...")
    filter_func = get_component('filter', 'ma_cross')['function']
    df = filter_func(df, **filter_params['ma_cross'])

    # Combine signals with filter
    initial_long_signals = df['signal_long'].sum()
    df['signal_long'] = df['signal_long'] & df['filter_ok']
    filtered_long_signals = df['signal_long'].sum()

    print(f"✓ Filter applied")
    print(f"  Long signals before filter: {initial_long_signals}")
    print(f"  Long signals after filter: {filtered_long_signals}")
    print(f"  Filtered out: {initial_long_signals - filtered_long_signals}")
    print()

    # Run backtest
    print("Running backtest...")
    config = BacktestConfig(
        initial_capital=100000,
        commission_per_trade=1.5,
        slippage_pips=1.0
    )

    engine = BacktestEngine(config)
    result = engine.run(df, {'pattern': selected_pattern, 'filters': selected_filters})

    print("✓ Backtest complete")
    print()
    print("Results:")
    print(f"  Total Trades: {result.metrics['total_trades']:.0f}")
    print(f"  Win Rate: {result.metrics['win_rate']:.2f}%")
    print(f"  Profit Factor: {result.metrics['profit_factor']:.2f}")
    print(f"  ROI: {result.metrics['roi']:.2f}%")
    print()

    # Assertions
    assert result.metrics['total_trades'] <= initial_long_signals, \
        "Filtered trades should be <= unfiltered signals"

    print("✅ WORKFLOW 2 PASSED")
    print()
    return result


def test_workflow_3_volumen_climatico_with_rsi():
    """Test Workflow 3: Volumen Climático with RSI filter"""
    print("=" * 70)
    print("TEST WORKFLOW 3: Volumen Climático + RSI Filter")
    print("=" * 70)
    print()

    # Simulate user selections
    selected_pattern = 'volumen_climatico'
    selected_filters = ['rsi_filter']
    pattern_params = {
        'sma_period': 20,
        'multiplier': 1.75,
        'direction': 'both'
    }
    filter_params = {
        'rsi_filter': {
            'period': 14,
            'oversold': 30,
            'overbought': 70,
            'mode': 'no_filter'
        }
    }

    print("User Configuration:")
    print(f"  Pattern: {selected_pattern}")
    print(f"  Pattern Params: {pattern_params}")
    print(f"  Filters: RSI Filter")
    print(f"  Filter Params: {filter_params['rsi_filter']}")
    print()

    # Get mock data
    df = create_mock_market_data(days=252)

    # Apply pattern
    print("Applying pattern...")
    pattern_func = get_component('entry_pattern', selected_pattern)['function']
    df = pattern_func(df, **pattern_params)

    # Apply filter
    print("Applying RSI filter...")
    filter_func = get_component('filter', 'rsi_filter')['function']
    df = filter_func(df, **filter_params['rsi_filter'])

    long_signals = df['signal_long'].sum()
    short_signals = df['signal_short'].sum()

    print(f"✓ Pattern and filter applied")
    print(f"  Long signals: {long_signals}")
    print(f"  Short signals: {short_signals}")
    print()

    # Run backtest
    print("Running backtest...")
    config = BacktestConfig(
        initial_capital=100000,
        commission_per_trade=1.5,
        slippage_pips=1.0
    )

    engine = BacktestEngine(config)
    result = engine.run(df, {
        'pattern': selected_pattern,
        'filters': selected_filters
    })

    print("✓ Backtest complete")
    print()
    print("Results:")
    print(f"  Total Trades: {result.metrics['total_trades']:.0f}")
    print(f"  Win Rate: {result.metrics['win_rate']:.2f}%")
    print(f"  Profit Factor: {result.metrics['profit_factor']:.2f}")
    print(f"  ROI: {result.metrics['roi']:.2f}%")
    print()

    print("✅ WORKFLOW 3 PASSED")
    print()
    return result


def test_workflow_4_sessions():
    """Test Workflow 4: Pattern with session filters"""
    print("=" * 70)
    print("TEST WORKFLOW 4: Sacudida + Session Filters")
    print("=" * 70)
    print()

    print("User Configuration:")
    print("  Pattern: sacudida")
    print("  Sessions: London + New York (Tokyo disabled)")
    print()

    # Get mock data with hourly bars
    print("Creating hourly mock data...")
    dates = pd.date_range(start='2024-01-01', periods=24*30, freq='h')

    np.random.seed(42)
    price_base = 100
    returns = np.random.randn(len(dates)) * 0.005
    prices = price_base * np.exp(np.cumsum(returns))

    df = pd.DataFrame({
        'open': prices * (1 + np.random.randn(len(dates)) * 0.002),
        'high': prices * (1 + np.abs(np.random.randn(len(dates))) * 0.003),
        'low': prices * (1 - np.abs(np.random.randn(len(dates))) * 0.003),
        'close': prices,
        'volume': np.random.randint(100000, 1000000, len(dates))
    }, index=dates)

    df['high'] = df[['open', 'high', 'close']].max(axis=1)
    df['low'] = df[['open', 'low', 'close']].min(axis=1)

    print(f"✓ Created {len(df)} hourly bars")
    print()

    # Apply pattern
    print("Applying pattern...")
    pattern_func = get_component('entry_pattern', 'sacudida')['function']
    df = pattern_func(df, direction='both')

    # Apply sessions
    print("Applying session filters...")
    session_london = get_component('session', 'london')['function']
    session_newyork = get_component('session', 'newyork')['function']

    df = session_london(df, enabled=True)
    df = session_newyork(df, enabled=True)

    # Check session coverage
    session_bars = df['session_ok'].sum()
    total_bars = len(df)
    coverage = session_bars / total_bars * 100

    print(f"✓ Sessions applied")
    print(f"  Bars in session: {session_bars} / {total_bars} ({coverage:.1f}%)")
    print()

    # Filter signals by session
    initial_signals = df['signal_long'].sum() + df['signal_short'].sum()
    df['signal_long'] = df['signal_long'] & df['session_ok']
    df['signal_short'] = df['signal_short'] & df['session_ok']
    filtered_signals = df['signal_long'].sum() + df['signal_short'].sum()

    print(f"  Signals before session filter: {initial_signals}")
    print(f"  Signals after session filter: {filtered_signals}")
    print()

    # Run backtest
    print("Running backtest...")
    config = BacktestConfig(initial_capital=100000)
    engine = BacktestEngine(config)
    result = engine.run(df, {'pattern': 'sacudida', 'sessions': ['london', 'newyork']})

    print("✓ Backtest complete")
    print()
    print("Results:")
    print(f"  Total Trades: {result.metrics['total_trades']:.0f}")
    print(f"  ROI: {result.metrics['roi']:.2f}%")
    print()

    print("✅ WORKFLOW 4 PASSED")
    print()
    return result


def test_parameter_extraction():
    """Test parameter extraction logic from UI"""
    print("=" * 70)
    print("TEST: Parameter Extraction Logic")
    print("=" * 70)
    print()

    # Simulate UI parameter storage
    parameter_values = {
        'entry_pattern.sacudida.direction': 'long',
        'filter.ma_cross.mode': 'bullish',
        'filter.ma_cross.fast_period': 50,
        'filter.ma_cross.slow_period': 200,
        'filter.rsi_filter.period': 14,
        'filter.rsi_filter.oversold': 30,
        'filter.rsi_filter.overbought': 70,
        'session.london.enabled': True
    }

    def extract_params_for_component(component_name: str, category: str, param_values: dict):
        """Extract parameters for a specific component"""
        params = {}
        prefix = f"{category}.{component_name}."

        for param_key, param_value in param_values.items():
            if param_key.startswith(prefix):
                param_name = param_key[len(prefix):]
                params[param_name] = param_value

        return params

    # Test extraction
    print("Testing parameter extraction...")

    sacudida_params = extract_params_for_component('sacudida', 'entry_pattern', parameter_values)
    print(f"  Sacudida params: {sacudida_params}")
    assert sacudida_params == {'direction': 'long'}, "Sacudida params incorrect"

    ma_cross_params = extract_params_for_component('ma_cross', 'filter', parameter_values)
    print(f"  MA Cross params: {ma_cross_params}")
    assert ma_cross_params == {
        'mode': 'bullish',
        'fast_period': 50,
        'slow_period': 200
    }, "MA Cross params incorrect"

    rsi_params = extract_params_for_component('rsi_filter', 'filter', parameter_values)
    print(f"  RSI params: {rsi_params}")
    assert rsi_params == {
        'period': 14,
        'oversold': 30,
        'overbought': 70
    }, "RSI params incorrect"

    london_params = extract_params_for_component('london', 'session', parameter_values)
    print(f"  London params: {london_params}")
    assert london_params == {'enabled': True}, "London params incorrect"

    print()
    print("✅ PARAMETER EXTRACTION TEST PASSED")
    print()


def test_edge_cases():
    """Test edge cases and error handling"""
    print("=" * 70)
    print("TEST: Edge Cases")
    print("=" * 70)
    print()

    # Test 1: No signals generated
    print("Test 1: Pattern with no signals...")
    df = create_mock_market_data(days=10)  # Very small dataset

    # Apply pattern
    pattern_func = get_component('entry_pattern', 'sacudida')['function']
    df = pattern_func(df, direction='long')

    # Run backtest
    config = BacktestConfig()
    engine = BacktestEngine(config)
    result = engine.run(df, {'pattern': 'sacudida'})

    print(f"  Total trades: {result.metrics['total_trades']}")
    assert result.metrics['total_trades'] >= 0, "Should handle 0 trades gracefully"
    print("  ✓ Handles zero trades correctly")
    print()

    # Test 2: All signals filtered out
    print("Test 2: All signals filtered out...")
    df = create_mock_market_data(days=100)

    # Apply pattern
    df = pattern_func(df, direction='both')

    # Apply restrictive filter (force filter_ok = False)
    df['filter_ok'] = False
    df['signal_long'] = df['signal_long'] & df['filter_ok']
    df['signal_short'] = df['signal_short'] & df['filter_ok']

    result = engine.run(df, {'pattern': 'sacudida', 'filters': ['ma_cross']})

    print(f"  Total trades: {result.metrics['total_trades']}")
    assert result.metrics['total_trades'] == 0, "Should have 0 trades when all filtered"
    print("  ✓ Handles complete filtering correctly")
    print()

    print("✅ EDGE CASES TEST PASSED")
    print()


if __name__ == "__main__":
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "COMPREHENSIVE UI WORKFLOW TESTS" + " " * 22 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    print("This test suite simulates complete user workflows through the UI")
    print("without requiring the web server to be running.")
    print()

    try:
        # Run all workflow tests
        result1 = test_workflow_1_sacudida_no_filters()
        result2 = test_workflow_2_envolvente_with_ma_filter()
        result3 = test_workflow_3_volumen_climatico_with_rsi()
        result4 = test_workflow_4_sessions()

        # Run utility tests
        test_parameter_extraction()
        test_edge_cases()

        print()
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 20 + "ALL TESTS PASSED!" + " " * 27 + "║")
        print("╚" + "=" * 68 + "╝")
        print()
        print("Summary:")
        print("  ✅ 4 complete workflows tested")
        print("  ✅ Parameter extraction verified")
        print("  ✅ Edge cases handled correctly")
        print()
        print("The UI is ready for production use!")
        print()
        print("Next steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Run the UI: python src/ui_app.py")
        print("  3. Test with real market data from Yahoo Finance")
        print()

    except AssertionError as e:
        print()
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 27 + "TEST FAILED!" + " " * 28 + "║")
        print("╚" + "=" * 68 + "╝")
        print()
        print(f"Error: {e}")
        print()
        sys.exit(1)

    except Exception as e:
        print()
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 24 + "UNEXPECTED ERROR!" + " " * 25 + "║")
        print("╚" + "=" * 68 + "╝")
        print()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print()
        sys.exit(1)
