"""
YFinance Data Provider - Yahoo Finance API

Fetches real market data from Yahoo Finance using the yfinance library.
Supports stocks, forex, crypto, indices, and more.
"""

import pandas as pd
from typing import Optional, Dict, Any
from .base_provider import BaseDataProvider, DataNotFoundError, ProviderConnectionError


class YFinanceProvider(BaseDataProvider):
    """
    Yahoo Finance data provider using yfinance library.
    
    Features:
    - Access to global stock markets
    - Forex pairs (format: EURUSD=X)
    - Cryptocurrencies (format: BTC-USD)
    - Indices (format: ^GSPC for S&P 500)
    - Multiple timeframes
    - Free (no API key required)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize YFinance provider.
        
        Config options:
            - progress: Show download progress (default: False)
            - auto_adjust: Adjust OHLC for splits/dividends (default: True)
            - prepost: Include pre/post market data (default: False)
        """
        super().__init__(config)
        self.progress = self.config.get('progress', False)
        self.auto_adjust = self.config.get('auto_adjust', True)
        self.prepost = self.config.get('prepost', False)
        
        # Check if yfinance is available
        try:
            import yfinance as yf
            self.yf = yf
            self._available = True
        except ImportError:
            self._available = False
    
    def _check_available(self):
        """Raise error if yfinance is not installed."""
        if not self._available:
            raise ImportError(
                "yfinance library is not installed. "
                "Install it with: pip install yfinance"
            )
    
    def fetch_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = '1d',
        **kwargs
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data from Yahoo Finance.
        
        Args:
            symbol: Yahoo Finance ticker symbol
                Examples:
                - Stocks: 'AAPL', 'MSFT', 'TSLA'
                - Forex: 'EURUSD=X', 'GBPUSD=X'
                - Crypto: 'BTC-USD', 'ETH-USD'
                - Indices: '^GSPC', '^DJI', '^IXIC'
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            interval: Time interval
                Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
            **kwargs: Additional yfinance parameters
        
        Returns:
            DataFrame with OHLCV data
        
        Raises:
            ImportError: If yfinance not installed
            DataNotFoundError: If symbol not found or no data available
            ProviderConnectionError: If unable to connect to Yahoo Finance
        """
        self._check_available()
        
        try:
            # Download data
            df = self.yf.download(
                symbol,
                start=start_date,
                end=end_date,
                interval=interval,
                progress=self.progress,
                auto_adjust=self.auto_adjust,
                prepost=self.prepost,
                **kwargs
            )
            
            # Check if data was returned
            if df is None or len(df) == 0:
                raise DataNotFoundError(
                    f"No data found for symbol '{symbol}' "
                    f"in range {start_date} to {end_date}. "
                    f"Check if symbol exists on Yahoo Finance."
                )
            
            # If multi-index (multiple symbols), extract first
            if isinstance(df.columns, pd.MultiIndex):
                df = df.xs(symbol, axis=1, level=1)
            
            # Normalize and return
            return self.normalize_data(df)
            
        except Exception as e:
            if "No data found" in str(e) or "404" in str(e):
                raise DataNotFoundError(
                    f"Symbol '{symbol}' not found on Yahoo Finance. "
                    f"Verify the symbol is correct."
                )
            elif "Connection" in str(e) or "Timeout" in str(e):
                raise ProviderConnectionError(
                    f"Unable to connect to Yahoo Finance: {e}"
                )
            else:
                raise
    
    def get_available_symbols(self) -> list:
        """
        Yahoo Finance doesn't provide symbol enumeration.
        
        Returns:
            Empty list (enumeration not supported)
        """
        return []
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Check if symbol exists on Yahoo Finance.
        
        This makes a quick API call to validate the symbol.
        
        Args:
            symbol: Symbol to validate
        
        Returns:
            True if symbol is valid
        """
        self._check_available()
        
        try:
            ticker = self.yf.Ticker(symbol)
            info = ticker.info
            return 'symbol' in info or 'shortName' in info
        except:
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get YFinance provider information."""
        return {
            'name': 'YFinanceProvider',
            'type': 'api',
            'supported_intervals': [
                '1m', '2m', '5m', '15m', '30m', '60m', '90m',
                '1h', '1d', '5d', '1wk', '1mo', '3mo'
            ],
            'requires_auth': False,
            'cost': 'free',
            'description': 'Yahoo Finance API (stocks, forex, crypto, indices)',
            'available': self._available
        }
