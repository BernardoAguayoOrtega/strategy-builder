"""
Builder Framework - Trading Strategy Components Library

This module is the SINGLE SOURCE OF TRUTH for all trading components.
The UI dynamically discovers and renders all components defined here using
the @component decorator system.

Key Features:
- Metadata-driven component registration
- Automatic UI generation
- Self-documenting parameters
- Introspection-friendly API

Usage:
    from builder_framework import get_all_components, get_component

    # Discover all components
    components = get_all_components()

    # Get specific component
    sacudida = get_component('entry_pattern', 'sacudida')
    sacudida_func = sacudida['function']
    metadata = sacudida['metadata']

Adding New Components:
    Just add a function with @component decorator and it will automatically
    appear in the UI!
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Any, Optional
import pandas as pd
import numpy as np

# ============================================
# METADATA SYSTEM
# ============================================

@dataclass
class ComponentMetadata:
    """
    Metadata that describes a component for UI generation and introspection.

    Attributes:
        name: Internal identifier (snake_case)
        display_name: Human-readable name shown in UI
        description: Tooltip/help text
        category: Component type ('entry_pattern', 'filter', 'session', etc.)
        parameters: Dict defining each parameter's type, range, and UI rendering
        enabled_by_default: Whether checkbox should be checked initially
    """
    name: str
    display_name: str
    description: str
    category: str
    parameters: Dict[str, Dict[str, Any]]
    enabled_by_default: bool = True


def component(
    category: str,
    name: str,
    display_name: str,
    description: str,
    parameters: Dict = None,
    enabled_by_default: bool = True
):
    """
    Decorator that registers a trading component with metadata.

    This is the KEY to dynamic UI generation. Each decorated function is
    automatically registered in COMPONENT_REGISTRY with all metadata needed
    for the UI to render it.

    Args:
        category: Type of component ('entry_pattern', 'filter', 'session', 'indicator', 'exit')
        name: Internal identifier (used in code)
        display_name: Name shown to users in UI
        description: Help text / tooltip
        parameters: Dict defining parameters (see examples below)
        enabled_by_default: Initial checkbox state

    Parameter Specification Format:
        {
            'parameter_name': {
                'type': 'int' | 'float' | 'bool' | 'choice',
                'min': minimum_value,  # for int/float
                'max': maximum_value,  # for int/float
                'default': default_value,
                'step': increment_step,  # for int/float
                'options': [list of choices],  # for choice type
                'display_name': 'User-facing label',
                'description': 'Help text',
                'optimizable': True  # Show optimization range controls
            }
        }

    Example:
        @component(
            category='filter',
            name='rsi_filter',
            display_name='RSI Filter',
            description='Filter trades by RSI levels',
            parameters={
                'period': {
                    'type': 'int',
                    'min': 5,
                    'max': 30,
                    'default': 14,
                    'step': 1,
                    'display_name': 'RSI Period',
                    'optimizable': True
                }
            }
        )
        def filter_rsi(df, period=14):
            # Implementation
            return df
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

        # Attach metadata to function
        func.__component_metadata__ = metadata

        # Register in global registry
        if category not in COMPONENT_REGISTRY:
            COMPONENT_REGISTRY[category] = {}

        COMPONENT_REGISTRY[category][name] = {
            'function': func,
            'metadata': metadata
        }

        return func

    return decorator


# Global component registry (populated by @component decorators)
COMPONENT_REGISTRY: Dict[str, Dict[str, Dict]] = {
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
    description='False breakout reversal pattern. Detects when price breaks a support/resistance level then immediately reverses, trapping weak hands.',
    parameters={
        'direction': {
            'type': 'choice',
            'options': ['long', 'short', 'both'],
            'default': 'both',
            'display_name': 'Trade Direction',
            'description': 'Which signals to generate'
        }
    },
    enabled_by_default=True
)
def pattern_sacudida(df: pd.DataFrame, direction: str = 'both') -> pd.DataFrame:
    """
    Sacudida (Shake-out) Pattern Detection

    Logic (Long):
        Bar[1]: Bearish candle that breaks below low[2]
        Bar[0]: Bullish candle that closes above low[2]

    Logic (Short):
        Bar[1]: Bullish candle that breaks above high[2]
        Bar[0]: Bearish candle that closes below high[2]

    This creates a "fake breakout" that reverses, catching stop-hunters.

    Args:
        df: DataFrame with OHLCV columns (open, high, low, close, volume)
        direction: 'long', 'short', or 'both'

    Returns:
        DataFrame with added columns:
            - signal_long: Boolean series for long entries
            - signal_short: Boolean series for short entries

    Pine Script Reference:
        See legacy/Algo Strategy Builder.txt lines 92-104
    """
    df = df.copy()

    # Long signals (Bearish shake-out followed by bullish reversal)
    vela2_bajista = (df['close'].shift(1) < df['open'].shift(1)).fillna(False)
    vela2_rompe_minimo = (df['low'].shift(1) < df['low'].shift(2)).fillna(False)
    vela3_alcista = (df['close'] > df['open']).fillna(False)
    vela3_confirmacion = (df['close'] > df['low'].shift(2)).fillna(False)

    df['signal_long'] = (
        vela2_bajista &
        vela2_rompe_minimo &
        vela3_alcista &
        vela3_confirmacion
    )

    # Short signals (Bullish shake-out followed by bearish reversal)
    vela2_alcista = (df['close'].shift(1) > df['open'].shift(1)).fillna(False)
    vela2_rompe_maximo = (df['high'].shift(1) > df['high'].shift(2)).fillna(False)
    vela3_bajista = (df['close'] < df['open']).fillna(False)
    vela3_confirmacion_short = (df['close'] < df['high'].shift(2)).fillna(False)

    df['signal_short'] = (
        vela2_alcista &
        vela2_rompe_maximo &
        vela3_bajista &
        vela3_confirmacion_short
    )

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
    description='Classic candlestick engulfing pattern. Current candle completely engulfs the previous candle, showing strong momentum reversal.',
    parameters={
        'direction': {
            'type': 'choice',
            'options': ['long', 'short', 'both'],
            'default': 'both',
            'display_name': 'Trade Direction',
            'description': 'Which signals to generate'
        }
    },
    enabled_by_default=True
)
def pattern_envolvente(df: pd.DataFrame, direction: str = 'both') -> pd.DataFrame:
    """
    Envolvente (Engulfing) Pattern Detection

    Logic (Bullish Engulfing):
        - Previous candle is bearish (close < open)
        - Current candle is bullish (close > open)
        - Current open <= previous close
        - Current close >= previous open
        - Current candle "engulfs" previous candle

    Logic (Bearish Engulfing):
        - Opposite of above

    Args:
        df: DataFrame with OHLCV columns
        direction: 'long', 'short', or 'both'

    Returns:
        DataFrame with signal_long and signal_short columns

    Pine Script Reference:
        See legacy/Algo Strategy Builder.txt lines 107-119
    """
    df = df.copy()

    # Bullish Engulfing
    vela_alcista = (df['close'] > df['open']).fillna(False)
    vela_bajista_prev = (df['close'].shift(1) < df['open'].shift(1)).fillna(False)
    cierra_sobre_ap1 = (df['close'] >= df['open'].shift(1)).fillna(False)
    abre_bajo_c1 = (df['open'] <= df['close'].shift(1)).fillna(False)

    df['signal_long'] = (
        vela_alcista &
        vela_bajista_prev &
        cierra_sobre_ap1 &
        abre_bajo_c1
    )

    # Bearish Engulfing
    vela_bajista = (df['close'] < df['open']).fillna(False)
    vela_alcista_prev = (df['close'].shift(1) > df['open'].shift(1)).fillna(False)
    cierra_bajo_ap1 = (df['close'] <= df['open'].shift(1)).fillna(False)
    abre_sobre_c1 = (df['open'] >= df['close'].shift(1)).fillna(False)

    df['signal_short'] = (
        vela_bajista &
        vela_alcista_prev &
        cierra_bajo_ap1 &
        abre_sobre_c1
    )

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
    description='High volume spike indicating climactic buying or selling. Volume exceeds moving average by a large multiplier, suggesting exhaustion or capitulation.',
    parameters={
        'sma_period': {
            'type': 'int',
            'min': 5,
            'max': 50,
            'default': 20,
            'step': 1,
            'display_name': 'Volume SMA Period',
            'description': 'Period for volume moving average baseline',
            'optimizable': True
        },
        'multiplier': {
            'type': 'float',
            'min': 1.0,
            'max': 3.0,
            'default': 1.75,
            'step': 0.25,
            'display_name': 'Volume Multiplier',
            'description': 'Volume must exceed SMA by this factor',
            'optimizable': True
        },
        'direction': {
            'type': 'choice',
            'options': ['long', 'short', 'both'],
            'default': 'both',
            'display_name': 'Trade Direction',
            'description': 'Which signals to generate'
        }
    },
    enabled_by_default=False
)
def pattern_volumen_climatico(
    df: pd.DataFrame,
    sma_period: int = 20,
    multiplier: float = 1.75,
    direction: str = 'both'
) -> pd.DataFrame:
    """
    Volumen Climático (Climactic Volume) Pattern Detection

    Logic:
        - Calculate volume SMA
        - Climactic volume = current volume > SMA * multiplier
        - Long: Climactic volume + bullish candle (close > open)
        - Short: Climactic volume + bearish candle (close < open)

    This pattern uses MARKET ORDERS (immediate execution) unlike other
    patterns which use stop orders.

    Args:
        df: DataFrame with OHLCV columns
        sma_period: Period for volume moving average
        multiplier: Volume threshold multiplier
        direction: 'long', 'short', or 'both'

    Returns:
        DataFrame with signal_long and signal_short columns

    Pine Script Reference:
        See legacy/Algo Strategy Builder.txt lines 122-125
    """
    df = df.copy()

    # Calculate volume moving average
    vol_ma = df['volume'].rolling(window=sma_period).mean()

    # Detect climactic volume
    vol_climatico = (df['volume'] > vol_ma * multiplier).fillna(False)

    # Direction based on candle color
    df['signal_long'] = vol_climatico & (df['close'] > df['open']).fillna(False)
    df['signal_short'] = vol_climatico & (df['close'] < df['open']).fillna(False)

    # Apply direction filter
    if direction == 'long':
        df['signal_short'] = False
    elif direction == 'short':
        df['signal_long'] = False

    return df


# ============================================
# FILTERS
# ============================================

@component(
    category='filter',
    name='ma_cross',
    display_name='Moving Average Cross Filter (50/200)',
    description='Filters trades based on trend direction. Only allows longs when fast MA > slow MA (bullish trend), only allows shorts when fast MA < slow MA (bearish trend).',
    parameters={
        'mode': {
            'type': 'choice',
            'options': ['no_filter', 'bullish', 'bearish'],
            'default': 'no_filter',
            'display_name': 'Filter Mode',
            'description': 'Bullish: Only longs when MA50>MA200. Bearish: Only shorts when MA50<MA200. No filter: Allow all trades.'
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
    },
    enabled_by_default=False
)
def filter_ma_cross(
    df: pd.DataFrame,
    mode: str = 'no_filter',
    fast_period: int = 50,
    slow_period: int = 200
) -> pd.DataFrame:
    """
    Moving Average Cross Filter

    Filters trades based on the relationship between two moving averages.
    This is a trend filter that prevents counter-trend trades.

    Args:
        df: DataFrame with OHLCV columns
        mode: 'no_filter', 'bullish', or 'bearish'
        fast_period: Period for fast MA
        slow_period: Period for slow MA

    Returns:
        DataFrame with 'filter_ok' column added

    Pine Script Reference:
        See legacy/Algo Strategy Builder.txt lines 134-136
    """
    df = df.copy()

    # Calculate moving averages
    sma_fast = df['close'].rolling(window=fast_period).mean()
    sma_slow = df['close'].rolling(window=slow_period).mean()

    # Apply filter based on mode
    if mode == 'no_filter':
        df['filter_ok'] = True
    elif mode == 'bullish':
        df['filter_ok'] = (sma_fast > sma_slow).fillna(False)
    elif mode == 'bearish':
        df['filter_ok'] = (sma_fast < sma_slow).fillna(False)
    else:
        df['filter_ok'] = True

    # Store MAs for potential plotting
    df['sma_fast'] = sma_fast
    df['sma_slow'] = sma_slow

    return df


@component(
    category='filter',
    name='rsi_filter',
    display_name='RSI Overbought/Oversold Filter',
    description='Filters trades based on RSI levels. Favors longs in oversold conditions and shorts in overbought conditions. Can be used as confirmation or divergence filter.',
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
            'description': 'RSI below this favors longs',
            'optimizable': True
        },
        'overbought': {
            'type': 'int',
            'min': 60,
            'max': 90,
            'default': 70,
            'step': 5,
            'display_name': 'Overbought Threshold',
            'description': 'RSI above this favors shorts',
            'optimizable': True
        },
        'mode': {
            'type': 'choice',
            'options': ['no_filter', 'confirmation', 'divergence'],
            'default': 'no_filter',
            'display_name': 'Filter Mode',
            'description': 'Confirmation: Only trade in RSI zones. Divergence: Only trade against RSI zones.'
        }
    },
    enabled_by_default=False
)
def filter_rsi(
    df: pd.DataFrame,
    period: int = 14,
    oversold: int = 30,
    overbought: int = 70,
    mode: str = 'no_filter'
) -> pd.DataFrame:
    """
    RSI Filter

    Filters trades based on RSI overbought/oversold conditions.

    Modes:
        - no_filter: Calculate RSI but don't filter trades
        - confirmation: Only longs when RSI < oversold, only shorts when RSI > overbought
        - divergence: Only longs when RSI > overbought, only shorts when RSI < oversold
                      (contrarian/mean reversion)

    Args:
        df: DataFrame with OHLCV columns
        period: RSI calculation period
        oversold: Oversold threshold (typically 30)
        overbought: Overbought threshold (typically 70)
        mode: Filter mode

    Returns:
        DataFrame with 'filter_ok' and 'rsi' columns added
    """
    df = df.copy()

    # Calculate RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    df['rsi'] = rsi

    # Apply filter based on mode
    if mode == 'no_filter':
        df['filter_ok'] = True
    elif mode == 'confirmation':
        # Only trade in extreme zones
        df['filter_ok'] = (rsi < oversold) | (rsi > overbought)
        df['filter_ok'] = df['filter_ok'].fillna(False)
    elif mode == 'divergence':
        # Contrarian: trade against extreme zones
        df['filter_ok'] = (rsi >= oversold) & (rsi <= overbought)
        df['filter_ok'] = df['filter_ok'].fillna(True)
    else:
        df['filter_ok'] = True

    return df


# ============================================
# SESSIONS (Trading Time Filters)
# ============================================

@component(
    category='session',
    name='london',
    display_name='London Session',
    description='London trading session (01:00 - 08:15 UTC). Most active for EUR, GBP pairs.',
    parameters={
        'enabled': {
            'type': 'bool',
            'default': True,
            'display_name': 'Enable London Session',
            'description': 'Allow trades during London hours'
        }
    },
    enabled_by_default=True
)
def session_london(df: pd.DataFrame, enabled: bool = True) -> pd.DataFrame:
    """
    London Session Filter

    Allows trades only during London market hours (01:00 - 08:15 UTC).

    Args:
        df: DataFrame with DatetimeIndex
        enabled: Whether to enable this session

    Returns:
        DataFrame with 'session_ok' column (or updates existing one)

    Pine Script Reference:
        See legacy/Algo Strategy Builder.txt line 79
    """
    df = df.copy()

    if not enabled:
        return df

    # Extract hour from index (assumes DatetimeIndex in UTC)
    hour = df.index.hour
    minute = df.index.minute

    # London: 01:00 - 08:15
    df['session_london'] = (
        ((hour >= 1) & (hour < 8)) |
        ((hour == 8) & (minute <= 15))
    )

    # Combine with existing session_ok (OR logic)
    if 'session_ok' not in df.columns:
        df['session_ok'] = False

    df['session_ok'] = df['session_ok'] | df['session_london']

    return df


@component(
    category='session',
    name='newyork',
    display_name='New York Session',
    description='New York trading session (08:15 - 15:45 UTC). Most active for USD pairs and US stocks.',
    parameters={
        'enabled': {
            'type': 'bool',
            'default': True,
            'display_name': 'Enable New York Session',
            'description': 'Allow trades during New York hours'
        }
    },
    enabled_by_default=True
)
def session_newyork(df: pd.DataFrame, enabled: bool = True) -> pd.DataFrame:
    """
    New York Session Filter

    Allows trades only during New York market hours (08:15 - 15:45 UTC).

    Args:
        df: DataFrame with DatetimeIndex
        enabled: Whether to enable this session

    Returns:
        DataFrame with 'session_ok' column updated

    Pine Script Reference:
        See legacy/Algo Strategy Builder.txt line 80
    """
    df = df.copy()

    if not enabled:
        return df

    hour = df.index.hour
    minute = df.index.minute

    # New York: 08:15 - 15:45
    df['session_newyork'] = (
        ((hour == 8) & (minute >= 15)) |
        ((hour > 8) & (hour < 15)) |
        ((hour == 15) & (minute <= 45))
    )

    if 'session_ok' not in df.columns:
        df['session_ok'] = False

    df['session_ok'] = df['session_ok'] | df['session_newyork']

    return df


@component(
    category='session',
    name='tokyo',
    display_name='Tokyo Session',
    description='Tokyo trading session (15:45 - 01:00 UTC). Most active for JPY pairs.',
    parameters={
        'enabled': {
            'type': 'bool',
            'default': True,
            'display_name': 'Enable Tokyo Session',
            'description': 'Allow trades during Tokyo hours'
        }
    },
    enabled_by_default=True
)
def session_tokyo(df: pd.DataFrame, enabled: bool = True) -> pd.DataFrame:
    """
    Tokyo Session Filter

    Allows trades only during Tokyo market hours (15:45 - 01:00 UTC).
    Note: This session wraps around midnight.

    Args:
        df: DataFrame with DatetimeIndex
        enabled: Whether to enable this session

    Returns:
        DataFrame with 'session_ok' column updated

    Pine Script Reference:
        See legacy/Algo Strategy Builder.txt line 81
    """
    df = df.copy()

    if not enabled:
        return df

    hour = df.index.hour
    minute = df.index.minute

    # Tokyo: 15:45 - 01:00 (wraps around midnight)
    df['session_tokyo'] = (
        ((hour == 15) & (minute >= 45)) |
        (hour > 15) |
        (hour == 0) |
        ((hour == 1) & (minute == 0))
    )

    if 'session_ok' not in df.columns:
        df['session_ok'] = False

    df['session_ok'] = df['session_ok'] | df['session_tokyo']

    return df


# ============================================
# DISCOVERY API
# ============================================

def get_all_components() -> Dict[str, Dict]:
    """
    Get all registered components organized by category.

    This is the main entry point for UI discovery. The UI calls this function
    to introspect all available components and generate the interface.

    Returns:
        Dict structured as:
        {
            'entry_pattern': {
                'sacudida': {'function': <func>, 'metadata': <ComponentMetadata>},
                'envolvente': {...},
                ...
            },
            'filter': {...},
            'session': {...},
            ...
        }

    Example:
        >>> components = get_all_components()
        >>> for category, comps in components.items():
        ...     print(f"{category}: {list(comps.keys())}")
        entry_pattern: ['sacudida', 'envolvente', 'volumen_climatico']
        filter: ['ma_cross', 'rsi_filter']
        session: ['london', 'newyork', 'tokyo']
    """
    return COMPONENT_REGISTRY


def get_components_by_category(category: str) -> Dict:
    """
    Get all components of a specific category.

    Args:
        category: One of 'entry_pattern', 'filter', 'session', 'indicator', 'exit'

    Returns:
        Dict of components in that category

    Example:
        >>> patterns = get_components_by_category('entry_pattern')
        >>> print(list(patterns.keys()))
        ['sacudida', 'envolvente', 'volumen_climatico']
    """
    return COMPONENT_REGISTRY.get(category, {})


def get_component(category: str, name: str) -> Optional[Dict]:
    """
    Get a specific component by category and name.

    Args:
        category: Component category
        name: Component name

    Returns:
        Dict with 'function' and 'metadata' keys, or None if not found

    Example:
        >>> sacudida = get_component('entry_pattern', 'sacudida')
        >>> func = sacudida['function']
        >>> metadata = sacudida['metadata']
        >>> print(metadata.display_name)
        'Sacudida (Shake-out)'
    """
    return COMPONENT_REGISTRY.get(category, {}).get(name)


def list_all_component_names() -> Dict[str, List[str]]:
    """
    Get a simple dict of category -> list of component names.

    Returns:
        Dict mapping categories to lists of component names

    Example:
        >>> names = list_all_component_names()
        >>> print(names)
        {
            'entry_pattern': ['sacudida', 'envolvente', 'volumen_climatico'],
            'filter': ['ma_cross', 'rsi_filter'],
            'session': ['london', 'newyork', 'tokyo']
        }
    """
    return {
        category: list(components.keys())
        for category, components in COMPONENT_REGISTRY.items()
        if components  # Only include non-empty categories
    }


# ============================================
# UTILITY FUNCTIONS
# ============================================

def validate_dataframe(df: pd.DataFrame) -> bool:
    """
    Validate that a DataFrame has required OHLCV columns.

    Args:
        df: DataFrame to validate

    Returns:
        True if valid, raises ValueError if not

    Raises:
        ValueError: If required columns are missing
    """
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(f"DataFrame missing required columns: {missing}")

    return True


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize DataFrame column names to lowercase.

    yfinance returns columns with capital letters (Open, High, Low, Close, Volume).
    This function standardizes them to lowercase.

    Args:
        df: DataFrame from yfinance or other source

    Returns:
        DataFrame with lowercase column names
    """
    df = df.copy()
    df.columns = [col.lower() for col in df.columns]
    return df


# ============================================
# MODULE INITIALIZATION
# ============================================

if __name__ == '__main__':
    # Demo: Show all registered components
    print("=" * 60)
    print("BUILDER FRAMEWORK - Registered Components")
    print("=" * 60)

    all_components = get_all_components()

    for category, components in all_components.items():
        if components:
            print(f"\n{category.upper().replace('_', ' ')}:")
            for name, comp_data in components.items():
                metadata = comp_data['metadata']
                print(f"  ✓ {metadata.display_name} ({name})")
                print(f"    Description: {metadata.description}")
                print(f"    Parameters: {len(metadata.parameters)}")
                if metadata.parameters:
                    for param_name, param_spec in metadata.parameters.items():
                        print(f"      - {param_spec['display_name']} ({param_spec['type']})")

    print(f"\n{'=' * 60}")
    print(f"Total components: {sum(len(comps) for comps in all_components.values())}")
    print("=" * 60)
