"""
Mock Data Provider - For Testing and Development

Generates synthetic OHLCV data for testing purposes.
Useful when you don't have access to real market data or need deterministic tests.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from .base_provider import BaseDataProvider


class MockDataProvider(BaseDataProvider):
    """
    Mock data provider that generates synthetic OHLCV data.
    
    Features:
    - Random walk price generation
    - Configurable volatility and trend
    - Deterministic (same seed = same data)
    - No external dependencies
    - Instant data generation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize mock data provider.
        
        Config options:
            - seed: Random seed for reproducibility (default: 42)
            - initial_price: Starting price (default: 100.0)
            - volatility: Daily volatility (default: 0.02)
            - trend: Daily trend multiplier (default: 0.0)
        """
        super().__init__(config)
        self.seed = self.config.get('seed', 42)
        self.initial_price = self.config.get('initial_price', 100.0)
        self.volatility = self.config.get('volatility', 0.02)
        self.trend = self.config.get('trend', 0.0)
    
    def fetch_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = '1d',
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate mock OHLCV data.
        
        Args:
            symbol: Ignored (mock data is symbol-agnostic)
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            interval: Time interval ('1d', '1h', '5m', etc.)
            **kwargs: Additional parameters (seed override, etc.)
        
        Returns:
            DataFrame with mock OHLCV data
        """
        # Override seed if provided
        seed = kwargs.get('seed', self.seed)
        np.random.seed(seed)
        
        # Parse dates
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        # Generate date range based on interval
        freq_map = {
            '1m': '1min',
            '5m': '5min',
            '15m': '15min',
            '30m': '30min',
            '1h': '1H',
            '4h': '4H',
            '1d': 'D',
            '1w': 'W',
            '1mo': 'M'
        }
        freq = freq_map.get(interval, 'D')
        
        dates = pd.date_range(start=start, end=end, freq=freq)
        n = len(dates)
        
        if n == 0:
            raise ValueError(f"No data points generated for range {start_date} to {end_date}")
        
        # Generate price data (random walk with trend)
        returns = np.random.randn(n) * self.volatility + self.trend
        close = self.initial_price * np.exp(np.cumsum(returns))
        
        # Generate OHLC from close
        high = close + np.abs(np.random.randn(n) * close * self.volatility * 0.5)
        low = close - np.abs(np.random.randn(n) * close * self.volatility * 0.5)
        open_prices = close + np.random.randn(n) * close * self.volatility * 0.3
        
        # Ensure OHLC relationships are valid
        high = np.maximum(high, np.maximum(open_prices, close))
        low = np.minimum(low, np.minimum(open_prices, close))
        
        # Generate volume (log-normal distribution)
        volume = np.random.lognormal(mean=15, sigma=0.5, size=n).astype(int)
        
        # Create DataFrame
        df = pd.DataFrame({
            'open': open_prices,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        }, index=dates)
        
        # Normalize and return
        return self.normalize_data(df)
    
    def get_available_symbols(self) -> list:
        """
        Mock provider can generate data for any symbol.
        
        Returns:
            List of example symbols
        """
        return ['MOCK_STOCK', 'MOCK_FOREX', 'MOCK_CRYPTO']
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        All symbols are valid for mock provider.
        
        Args:
            symbol: Any string
        
        Returns:
            Always True
        """
        return True
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get mock provider information."""
        return {
            'name': 'MockDataProvider',
            'type': 'mock',
            'supported_intervals': ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1mo'],
            'requires_auth': False,
            'cost': 'free',
            'description': 'Generates synthetic data for testing'
        }
