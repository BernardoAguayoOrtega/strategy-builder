"""
Data Providers Package

Provides abstraction layer for data access, making the framework
agnostic to data sources (yfinance, CSV, database, API, etc.).

Main Components:
- BaseDataProvider: Abstract interface all providers must implement
- DataManager: Unified interface for data access
- Concrete Providers: MockDataProvider, CSVDataProvider, YFinanceProvider

Usage:
    # Quick data fetch
    from data_providers import fetch_data
    df = fetch_data('AAPL', '2023-01-01', '2024-01-01', provider='yfinance')
    
    # Using DataManager
    from data_providers import DataManager
    manager = DataManager(default_provider='csv')
    df = manager.fetch_data('AAPL', '2023-01-01', '2024-01-01')
    
    # Custom provider configuration
    manager = DataManager(
        default_provider='csv',
        provider_configs={
            'csv': {'data_dir': './my_data'},
            'yfinance': {'progress': True}
        }
    )
"""

from .base_provider import BaseDataProvider, DataNotFoundError, ProviderConnectionError
from .mock_provider import MockDataProvider
from .csv_provider import CSVDataProvider
from .yfinance_provider import YFinanceProvider
from .data_manager import DataManager, fetch_data

__all__ = [
    # Base classes
    'BaseDataProvider',
    'DataNotFoundError',
    'ProviderConnectionError',
    
    # Concrete providers
    'MockDataProvider',
    'CSVDataProvider',
    'YFinanceProvider',
    
    # Manager
    'DataManager',
    'fetch_data',
]

__version__ = '1.0.0'
