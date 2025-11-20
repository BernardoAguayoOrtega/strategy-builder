# src/backtesting_framework.py

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class BacktestConfig:
    """Configuration for a backtest run"""
    initial_capital: float = 100000.0
    commission_per_trade: float = 1.5
    slippage_pips: float = 1.0
    risk_per_trade_pct: float = 1.0
    position_sizing: str = 'fixed'  # 'fixed', 'risk_pct', 'risk_fixed'
    fixed_qty: float = 1.0

@dataclass
class BacktestResult:
    """Results from a backtest"""
    equity_curve: pd.Series
    trades: pd.DataFrame
    metrics: Dict[str, float]
    parameters: Dict[str, any]

class BacktestEngine:
    """Core backtesting engine"""

    def __init__(self, config: BacktestConfig):
        self.config = config

    def run(self, df: pd.DataFrame, strategy_config: Dict) -> BacktestResult:
        """
        Run backtest with given strategy configuration

        Args:
            df: DataFrame with OHLCV + signal columns
            strategy_config: Dict with entry_pattern, filters, exits, etc.

        Returns:
            BacktestResult object
        """
        df = df.copy()

        # Initialize tracking arrays
        positions = np.zeros(len(df))
        entry_prices = np.zeros(len(df))
        stop_losses = np.zeros(len(df))
        take_profits = np.zeros(len(df))
        equity = np.full(len(df), self.config.initial_capital)

        # Track trades
        trades_list = []

        # Main backtest loop
        for i in range(1, len(df)):
            # Check for exits first
            if positions[i-1] != 0:
                exit_signal, exit_reason = self._check_exit(
                    df.iloc[i], positions[i-1],
                    entry_prices[i-1], stop_losses[i-1], take_profits[i-1]
                )

                if exit_signal:
                    # Close position
                    exit_price = df.iloc[i]['close']
                    pnl = self._calculate_pnl(
                        entry_prices[i-1], exit_price,
                        positions[i-1], self.config.commission_per_trade
                    )
                    equity[i] = equity[i-1] + pnl

                    # Log trade
                    trades_list.append({
                        'entry_bar': i - 1,
                        'exit_bar': i,
                        'direction': 'long' if positions[i-1] > 0 else 'short',
                        'entry_price': entry_prices[i-1],
                        'exit_price': exit_price,
                        'pnl': pnl,
                        'exit_reason': exit_reason
                    })

                    positions[i] = 0
                else:
                    # Carry forward position
                    positions[i] = positions[i-1]
                    entry_prices[i] = entry_prices[i-1]
                    stop_losses[i] = stop_losses[i-1]
                    take_profits[i] = take_profits[i-1]
                    equity[i] = equity[i-1]

            # Check for new entries (only if flat)
            if positions[i] == 0 and df.iloc[i].get('signal_long', False):
                positions[i], entry_prices[i], stop_losses[i], take_profits[i] = \
                    self._enter_long(df.iloc[i], equity[i-1])
                equity[i] = equity[i-1]

            elif positions[i] == 0 and df.iloc[i].get('signal_short', False):
                positions[i], entry_prices[i], stop_losses[i], take_profits[i] = \
                    self._enter_short(df.iloc[i], equity[i-1])
                equity[i] = equity[i-1]

        # Calculate metrics
        trades_df = pd.DataFrame(trades_list)
        metrics = self._calculate_metrics(equity, trades_df, df)

        return BacktestResult(
            equity_curve=pd.Series(equity, index=df.index),
            trades=trades_df,
            metrics=metrics,
            parameters=strategy_config
        )

    def _check_exit(self, row, position, entry, sl, tp) -> Tuple[bool, str]:
        """Check if position should be exited"""
        if position > 0:  # Long
            if row['low'] <= sl:
                return True, 'stop_loss'
            if row['high'] >= tp and tp > 0:
                return True, 'take_profit'
        elif position < 0:  # Short
            if row['high'] >= sl:
                return True, 'stop_loss'
            if row['low'] <= tp and tp > 0:
                return True, 'take_profit'

        return False, ''

    def _enter_long(self, row, current_equity) -> Tuple[float, float, float, float]:
        """Enter long position"""
        entry_price = row['high'] + self.config.slippage_pips
        sl = row['low'] - self.config.slippage_pips
        risk = entry_price - sl
        tp = entry_price + risk * 1.5  # 1.5:1 R:R

        qty = self._calculate_position_size(entry_price, sl, current_equity)

        return qty, entry_price, sl, tp

    def _enter_short(self, row, current_equity) -> Tuple[float, float, float, float]:
        """Enter short position"""
        entry_price = row['low'] - self.config.slippage_pips
        sl = row['high'] + self.config.slippage_pips
        risk = sl - entry_price
        tp = entry_price - risk * 1.5

        qty = self._calculate_position_size(entry_price, sl, current_equity)

        return -qty, entry_price, sl, tp

    def _calculate_position_size(self, entry, sl, equity) -> float:
        """Calculate position size based on risk"""
        if self.config.position_sizing == 'fixed':
            return self.config.fixed_qty

        risk_distance = abs(entry - sl)
        risk_money = equity * (self.config.risk_per_trade_pct / 100)
        qty = risk_money / risk_distance

        return max(qty, 0.01)  # Min position size

    def _calculate_pnl(self, entry, exit, qty, commission) -> float:
        """Calculate P&L for a trade"""
        gross_pnl = (exit - entry) * qty
        net_pnl = gross_pnl - (2 * commission)  # Entry + exit
        return net_pnl

    def _calculate_metrics(self, equity, trades_df, df) -> Dict[str, float]:
        """Calculate performance metrics"""
        if len(trades_df) == 0:
            return self._empty_metrics()

        returns = pd.Series(equity).pct_change().dropna()
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]

        metrics = {
            'total_trades': len(trades_df),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(trades_df) * 100 if len(trades_df) > 0 else 0,
            'total_pnl': trades_df['pnl'].sum(),
            'avg_win': winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0,
            'avg_loss': losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0,
            'profit_factor': abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) if len(losing_trades) > 0 and losing_trades['pnl'].sum() != 0 else 0,
            'max_drawdown': self._calculate_max_drawdown(equity),
            'sharpe_ratio': returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0,
            'final_equity': equity[-1],
            'roi': (equity[-1] - equity[0]) / equity[0] * 100
        }

        return metrics

    def _calculate_max_drawdown(self, equity) -> float:
        """Calculate maximum drawdown"""
        equity_series = pd.Series(equity)
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max * 100
        return drawdown.min()

    def _empty_metrics(self) -> Dict[str, float]:
        """Return empty metrics when no trades"""
        return {k: 0.0 for k in ['total_trades', 'winning_trades', 'losing_trades',
                                   'win_rate', 'total_pnl', 'avg_win', 'avg_loss',
                                   'profit_factor', 'max_drawdown', 'sharpe_ratio',
                                   'final_equity', 'roi']}
