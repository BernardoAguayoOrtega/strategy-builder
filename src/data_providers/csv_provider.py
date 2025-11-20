"""
CSV Data Provider - Load Data from CSV Files

Supports loading OHLCV data from CSV files with flexible column mapping.
Useful for backtesting with historical data exports or custom data sources.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
from .base_provider import BaseDataProvider, DataNotFoundError


class CSVDataProvider(BaseDataProvider):
    """
    CSV file data provider.
    
    Features:
    - Load data from CSV files
    - Flexible column mapping
    - Support for multiple date formats
    - Directory-based symbol organization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize CSV data provider.
        
        Config options:
            - data_dir: Base directory for CSV files (default: './data')
            - filename_pattern: Pattern for file names (default: '{symbol}.csv')
            - date_column: Name of date column (default: 'Date')
            - column_mapping: Dict to map CSV columns to OHLCV
              Example: {'Open': 'open', 'High': 'high', ...}
        """
        super().__init__(config)
        self.data_dir = Path(self.config.get('data_dir', './data'))
        self.filename_pattern = self.config.get('filename_pattern', '{symbol}.csv')
        self.date_column = self.config.get('date_column', 'Date')
        self.column_mapping = self.config.get('column_mapping', {
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
    
    def fetch_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = '1d',
        **kwargs
    ) -> pd.DataFrame:
        """
        Load OHLCV data from CSV file.
        
        Args:
            symbol: Symbol name (used to locate CSV file)
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            interval: Ignored for CSV provider (data interval is in the file)
            **kwargs: Optional 'filepath' to override default path
        
        Returns:
            DataFrame with OHLCV data filtered to date range
        
        Raises:
            DataNotFoundError: If CSV file not found
            ValueError: If CSV format is invalid
        """
        # Get file path
        filepath = kwargs.get('filepath')
        if filepath is None:
            filename = self.filename_pattern.format(symbol=symbol)
            filepath = self.data_dir / filename
        else:
            filepath = Path(filepath)
        
        # Check if file exists
        if not filepath.exists():
            raise DataNotFoundError(
                f"CSV file not found: {filepath}. "
                f"Expected file for symbol '{symbol}' at {filepath}"
            )
        
        # Read CSV
        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            raise ValueError(f"Error reading CSV file {filepath}: {e}")
        
        # Apply column mapping
        df = df.rename(columns=self.column_mapping)
        
        # Set date as index
        if self.date_column in df.columns:
            df[self.date_column] = pd.to_datetime(df[self.date_column])
            df = df.set_index(self.date_column)
        elif 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
        else:
            # Try to parse index as date
            df.index = pd.to_datetime(df.index)
        
        # Filter by date range
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        df = df[(df.index >= start) & (df.index <= end)]
        
        if len(df) == 0:
            raise DataNotFoundError(
                f"No data found in date range {start_date} to {end_date} "
                f"for symbol '{symbol}' in file {filepath}"
            )
        
        # Normalize and return
        return self.normalize_data(df)
    
    def get_available_symbols(self) -> list:
        """
        Get list of symbols from CSV files in data directory.
        
        Returns:
            List of symbols (based on .csv filenames)
        """
        if not self.data_dir.exists():
            return []
        
        csv_files = list(self.data_dir.glob('*.csv'))
        symbols = [f.stem for f in csv_files]
        return sorted(symbols)
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Check if CSV file exists for symbol.
        
        Args:
            symbol: Symbol to validate
        
        Returns:
            True if CSV file exists
        """
        filename = self.filename_pattern.format(symbol=symbol)
        filepath = self.data_dir / filename
        return filepath.exists()
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get CSV provider information."""
        return {
            'name': 'CSVDataProvider',
            'type': 'file',
            'supported_intervals': ['any (depends on CSV data)'],
            'requires_auth': False,
            'cost': 'free',
            'description': f'Loads data from CSV files in {self.data_dir}'
        }
