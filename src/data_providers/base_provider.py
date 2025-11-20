"""
Base Data Provider - Abstract Interface

This module defines the abstract interface that all data providers must implement.
This ensures consistency and makes it easy to switch between different data sources.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime


class BaseDataProvider(ABC):
    """
    Abstract base class for all data providers.
    
    All data providers (yfinance, CSV, database, API, etc.) must implement
    this interface to ensure consistency across the framework.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the data provider with optional configuration.
        
        Args:
            config: Optional configuration dictionary specific to the provider
        """
        self.config = config or {}
    
    @abstractmethod
    def fetch_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = '1d',
        **kwargs
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data for a given symbol and time range.
        
        Args:
            symbol: Asset symbol (e.g., 'AAPL', 'EURUSD=X', 'BTC-USD')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            interval: Time interval ('1m', '5m', '15m', '1h', '1d', etc.)
            **kwargs: Provider-specific additional parameters
        
        Returns:
            DataFrame with DatetimeIndex and columns:
                - open: Opening price
                - high: Highest price
                - low: Lowest price
                - close: Closing price
                - volume: Trading volume
        
        Raises:
            ValueError: If parameters are invalid
            ConnectionError: If data source is unreachable
            DataNotFoundError: If symbol/data not available
        """
        pass
    
    @abstractmethod
    def get_available_symbols(self) -> list:
        """
        Get list of available symbols from this data source.
        
        Returns:
            List of symbol strings
        
        Note:
            Some providers may return an empty list if enumeration
            is not supported.
        """
        pass
    
    @abstractmethod
    def validate_symbol(self, symbol: str) -> bool:
        """
        Check if a symbol is valid for this data provider.
        
        Args:
            symbol: Symbol to validate
        
        Returns:
            True if symbol is valid, False otherwise
        """
        pass
    
    def normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize DataFrame to standard format.
        
        This method ensures all data providers return data in the same format:
        - Lowercase column names
        - DatetimeIndex in UTC
        - Standard OHLCV columns
        - No missing required columns
        
        Args:
            df: Raw DataFrame from data source
        
        Returns:
            Normalized DataFrame
        """
        df = df.copy()
        
        # Lowercase column names
        df.columns = [col.lower() for col in df.columns]
        
        # Ensure DatetimeIndex
        if not isinstance(df.index, pd.DatetimeIndex):
            if 'date' in df.columns:
                df = df.set_index('date')
            elif 'datetime' in df.columns:
                df = df.set_index('datetime')
        
        # Convert index to datetime if needed
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # Ensure UTC timezone
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
        elif df.index.tz != 'UTC':
            df.index = df.index.tz_convert('UTC')
        
        # Validate required columns
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Select only required columns (drop extras)
        df = df[required_columns]
        
        # Sort by date
        df = df.sort_index()
        
        return df
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about this data provider.
        
        Returns:
            Dict with provider metadata:
                - name: Provider name
                - type: Provider type (api, file, database, mock)
                - supported_intervals: List of supported intervals
                - requires_auth: Whether authentication is required
                - cost: 'free', 'paid', 'freemium'
        """
        return {
            'name': self.__class__.__name__,
            'type': 'unknown',
            'supported_intervals': [],
            'requires_auth': False,
            'cost': 'unknown'
        }


class DataNotFoundError(Exception):
    """Raised when requested data is not available from the provider."""
    pass


class ProviderConnectionError(Exception):
    """Raised when unable to connect to data provider."""
    pass
