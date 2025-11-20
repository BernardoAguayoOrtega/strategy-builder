"""
Data Manager - Unified Interface for Data Access

Manages multiple data providers and provides a simple interface for data access.
Automatically selects the appropriate provider or allows manual selection.
"""

import pandas as pd
from typing import Optional, Dict, Any, Type
from .base_provider import BaseDataProvider, DataNotFoundError
from .mock_provider import MockDataProvider
from .csv_provider import CSVDataProvider
from .yfinance_provider import YFinanceProvider


class DataManager:
    """
    Central manager for data access across multiple providers.
    
    Features:
    - Automatic provider selection
    - Manual provider override
    - Provider failover (try multiple providers)
    - Consistent interface regardless of data source
    """
    
    # Registry of available providers
    PROVIDERS = {
        'mock': MockDataProvider,
        'csv': CSVDataProvider,
        'yfinance': YFinanceProvider,
    }
    
    def __init__(self, default_provider: str = 'mock', provider_configs: Optional[Dict[str, Dict]] = None):
        """
        Initialize Data Manager.
        
        Args:
            default_provider: Default provider to use ('mock', 'csv', 'yfinance')
            provider_configs: Dict of provider-specific configurations
                Example: {
                    'csv': {'data_dir': './my_data'},
                    'yfinance': {'progress': True}
                }
        """
        self.default_provider = default_provider
        self.provider_configs = provider_configs or {}
        self._provider_instances: Dict[str, BaseDataProvider] = {}
    
    def get_provider(self, provider_name: str) -> BaseDataProvider:
        """
        Get or create a provider instance.
        
        Args:
            provider_name: Name of provider ('mock', 'csv', 'yfinance')
        
        Returns:
            Provider instance
        
        Raises:
            ValueError: If provider name is unknown
        """
        if provider_name not in self.PROVIDERS:
            available = ', '.join(self.PROVIDERS.keys())
            raise ValueError(
                f"Unknown provider '{provider_name}'. "
                f"Available providers: {available}"
            )
        
        # Return cached instance if exists
        if provider_name in self._provider_instances:
            return self._provider_instances[provider_name]
        
        # Create new instance
        provider_class = self.PROVIDERS[provider_name]
        config = self.provider_configs.get(provider_name, {})
        provider = provider_class(config)
        
        # Cache and return
        self._provider_instances[provider_name] = provider
        return provider
    
    def fetch_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = '1d',
        provider: Optional[str] = None,
        fallback_providers: Optional[list] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Fetch data using specified provider with optional fallback.
        
        Args:
            symbol: Asset symbol
            start_date: Start date 'YYYY-MM-DD'
            end_date: End date 'YYYY-MM-DD'
            interval: Time interval
            provider: Provider to use (None = use default)
            fallback_providers: List of providers to try if first fails
            **kwargs: Provider-specific parameters
        
        Returns:
            DataFrame with OHLCV data
        
        Raises:
            DataNotFoundError: If all providers fail
        """
        # Determine provider order
        provider_name = provider or self.default_provider
        providers_to_try = [provider_name]
        
        if fallback_providers:
            providers_to_try.extend(fallback_providers)
        
        # Try each provider
        last_error = None
        for prov_name in providers_to_try:
            try:
                prov = self.get_provider(prov_name)
                df = prov.fetch_data(symbol, start_date, end_date, interval, **kwargs)
                return df
            except (DataNotFoundError, Exception) as e:
                last_error = e
                continue
        
        # All providers failed
        raise DataNotFoundError(
            f"Failed to fetch data for {symbol} from all providers. "
            f"Last error: {last_error}"
        )
    
    def register_provider(self, name: str, provider_class: Type[BaseDataProvider]):
        """
        Register a custom data provider.
        
        This allows users to add their own data providers.
        
        Args:
            name: Name for the provider
            provider_class: Class implementing BaseDataProvider
        
        Example:
            class MyCustomProvider(BaseDataProvider):
                ...
            
            manager = DataManager()
            manager.register_provider('custom', MyCustomProvider)
            df = manager.fetch_data('AAPL', '2023-01-01', '2024-01-01', provider='custom')
        """
        if not issubclass(provider_class, BaseDataProvider):
            raise TypeError("Provider class must inherit from BaseDataProvider")
        
        self.PROVIDERS[name] = provider_class
    
    def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all available providers.
        
        Returns:
            Dict mapping provider names to their info
        """
        providers_info = {}
        for name in self.PROVIDERS.keys():
            try:
                provider = self.get_provider(name)
                providers_info[name] = provider.get_provider_info()
            except Exception as e:
                providers_info[name] = {
                    'name': name,
                    'error': str(e),
                    'available': False
                }
        return providers_info
    
    def validate_symbol(self, symbol: str, provider: Optional[str] = None) -> bool:
        """
        Validate if symbol is available from provider.
        
        Args:
            symbol: Symbol to validate
            provider: Provider to use (None = use default)
        
        Returns:
            True if symbol is valid
        """
        provider_name = provider or self.default_provider
        prov = self.get_provider(provider_name)
        return prov.validate_symbol(symbol)
    
    def get_available_symbols(self, provider: Optional[str] = None) -> list:
        """
        Get list of available symbols from provider.
        
        Args:
            provider: Provider to use (None = use default)
        
        Returns:
            List of symbols
        """
        provider_name = provider or self.default_provider
        prov = self.get_provider(provider_name)
        return prov.get_available_symbols()


# Convenience function for quick data access
def fetch_data(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str = '1d',
    provider: str = 'mock',
    **kwargs
) -> pd.DataFrame:
    """
    Quick data fetch without creating DataManager instance.
    
    Args:
        symbol: Asset symbol
        start_date: Start date 'YYYY-MM-DD'
        end_date: End date 'YYYY-MM-DD'
        interval: Time interval
        provider: Provider to use ('mock', 'csv', 'yfinance')
        **kwargs: Provider-specific parameters
    
    Returns:
        DataFrame with OHLCV data
    
    Example:
        >>> df = fetch_data('AAPL', '2023-01-01', '2024-01-01', provider='yfinance')
        >>> df = fetch_data('MOCK', '2023-01-01', '2024-01-01', provider='mock')
    """
    manager = DataManager(default_provider=provider)
    return manager.fetch_data(symbol, start_date, end_date, interval, **kwargs)
