# src/optimizer.py

from backtesting_framework import BacktestEngine, BacktestConfig
from builder_framework import get_component
import pandas as pd
from itertools import product
from multiprocessing import Pool, cpu_count
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

@dataclass
class OptimizationResult:
    """Single optimization result"""
    parameters: Dict[str, Any]
    metrics: Dict[str, float]
    rank_score: float = 0.0

class StrategyOptimizer:
    """
    Grid search optimizer for trading strategies

    Features:
    - Parallel processing using multiprocessing
    - Composite scoring system
    - Automatic ranking of results
    """

    def __init__(self, config: BacktestConfig, n_jobs: int = -1):
        """
        Initialize optimizer

        Args:
            config: BacktestConfig for backtesting
            n_jobs: Number of parallel jobs (-1 = use all CPUs)
        """
        self.config = config
        self.n_jobs = cpu_count() if n_jobs == -1 else n_jobs

    def optimize(self, df: pd.DataFrame, pattern_name: str,
                 parameter_ranges: Dict[str, List],
                 filter_configs: List[Dict] = None) -> List[OptimizationResult]:
        """
        Grid search optimization

        Args:
            df: Market data (OHLCV)
            pattern_name: Entry pattern to use
            parameter_ranges: Dict of {param_name: [val1, val2, ...]}
            filter_configs: List of filter configurations

        Returns:
            List of OptimizationResult sorted by rank_score (best first)
        """
        # Generate all parameter combinations
        if not parameter_ranges:
            print("No parameter ranges provided, testing with defaults")
            combinations = [{}]
            param_names = []
        else:
            param_names = list(parameter_ranges.keys())
            param_values = list(parameter_ranges.values())
            combinations = list(product(*param_values))

        print(f"Testing {len(combinations)} parameter combinations...")

        # Prepare jobs
        jobs = []
        for combo in combinations:
            if param_names:
                params = dict(zip(param_names, combo))
            else:
                params = {}
            jobs.append((df.copy(), pattern_name, params, filter_configs or [], self.config))

        # Run in parallel
        if self.n_jobs == 1:
            # Serial execution (useful for debugging)
            results = [_run_single_backtest_worker(job) for job in jobs]
        else:
            # Parallel execution
            with Pool(self.n_jobs) as pool:
                results = pool.map(_run_single_backtest_worker, jobs)

        # Filter out failed results
        results = [r for r in results if r is not None and r.metrics['total_trades'] > 0]

        if not results:
            print("WARNING: No valid results (all backtests had zero trades or failed)")
            return []

        # Rank results
        results = self._rank_results(results)

        print(f"Optimization complete! {len(results)} valid results found.")
        if results:
            print(f"Best score: {results[0].rank_score:.4f}")
            print(f"Best parameters: {results[0].parameters}")

        return results

    def _rank_results(self, results: List[OptimizationResult]) -> List[OptimizationResult]:
        """
        Rank results by composite score

        Score Formula:
        - ROI component (30%): ROI / 100
        - Profit Factor component (30%): min(PF / 3, 1.0)
        - Drawdown component (40%): 1 - abs(MaxDD) / 100

        All components normalized to [0, 1] range
        """
        for result in results:
            m = result.metrics

            # Normalize components
            roi_component = min(max(m['roi'] / 100, -1), 2)  # Cap at 200% ROI
            pf_component = min(m['profit_factor'] / 3, 1.0)  # Cap at PF=3
            dd_component = max(1 - abs(m['max_drawdown']) / 100, 0)  # 0% DD = 1.0, 100% DD = 0.0

            # Composite score (weighted sum)
            score = (
                roi_component * 0.3 +
                pf_component * 0.3 +
                dd_component * 0.4
            )

            result.rank_score = score

        # Sort by rank score (highest first)
        results.sort(key=lambda r: r.rank_score, reverse=True)
        return results

    def optimize_multi_pattern(self, df: pd.DataFrame,
                               pattern_configs: List[Tuple[str, Dict]]) -> List[OptimizationResult]:
        """
        Optimize across multiple patterns and their parameter ranges

        Args:
            df: Market data
            pattern_configs: List of (pattern_name, parameter_ranges) tuples

        Returns:
            Combined and ranked results from all patterns
        """
        all_results = []

        for pattern_name, param_ranges in pattern_configs:
            print(f"\nOptimizing {pattern_name}...")
            results = self.optimize(df, pattern_name, param_ranges)

            # Add pattern name to results
            for r in results:
                r.parameters['pattern'] = pattern_name

            all_results.extend(results)

        # Re-rank combined results
        all_results = self._rank_results(all_results)

        return all_results


def _run_single_backtest_worker(args: Tuple) -> OptimizationResult:
    """
    Worker function for parallel backtesting

    This function is defined at module level for multiprocessing compatibility

    Args:
        args: Tuple of (df, pattern_name, params, filter_configs, config)

    Returns:
        OptimizationResult or None if error
    """
    df, pattern_name, params, filter_configs, config = args

    try:
        # Apply pattern with parameters
        pattern_comp = get_component('entry_pattern', pattern_name)
        if not pattern_comp:
            raise ValueError(f"Pattern '{pattern_name}' not found")

        pattern_func = pattern_comp['function']
        df_signals = pattern_func(df, **params)

        # Apply filters if provided
        for filter_config in filter_configs:
            filter_name = filter_config.get('name')
            filter_params = filter_config.get('params', {})

            filter_comp = get_component('filter', filter_name)
            if filter_comp:
                filter_func = filter_comp['function']
                df_signals = filter_func(df_signals, **filter_params)

        # Combine filter results if multiple filters applied
        if filter_configs and 'filter_ok' in df_signals.columns:
            # Ensure signals respect filter
            if 'signal_long' in df_signals.columns:
                df_signals['signal_long'] = df_signals['signal_long'] & df_signals['filter_ok']
            if 'signal_short' in df_signals.columns:
                df_signals['signal_short'] = df_signals['signal_short'] & df_signals['filter_ok']

        # Run backtest
        engine = BacktestEngine(config)
        backtest_config = {
            'pattern': pattern_name,
            'parameters': params,
            'filters': filter_configs
        }
        result = engine.run(df_signals, backtest_config)

        # Return optimization result
        return OptimizationResult(
            parameters=params.copy(),
            metrics=result.metrics,
            rank_score=0.0  # Will be set during ranking
        )

    except Exception as e:
        # Log error but don't crash the pool
        print(f"Error with params {params}: {str(e)}")
        return None


def generate_parameter_grid(param_spec: Dict[str, Dict]) -> Dict[str, List]:
    """
    Generate parameter grid from specification

    Args:
        param_spec: Dict of parameter specifications with min, max, step
        Example: {
            'sma_period': {'min': 10, 'max': 50, 'step': 5},
            'multiplier': {'min': 1.5, 'max': 2.5, 'step': 0.25}
        }

    Returns:
        Dict of parameter ranges
    """
    param_grid = {}

    for param_name, spec in param_spec.items():
        min_val = spec.get('min', 0)
        max_val = spec.get('max', 100)
        step = spec.get('step', 1)
        param_type = spec.get('type', 'int')

        if param_type == 'int':
            param_grid[param_name] = list(range(int(min_val), int(max_val) + 1, int(step)))
        elif param_type == 'float':
            values = []
            current = float(min_val)
            while current <= float(max_val):
                values.append(round(current, 2))
                current += float(step)
            param_grid[param_name] = values
        elif param_type == 'choice':
            param_grid[param_name] = spec.get('options', [])

    return param_grid


def print_optimization_summary(results: List[OptimizationResult], top_n: int = 10):
    """
    Print a formatted summary of optimization results

    Args:
        results: List of OptimizationResult
        top_n: Number of top results to display
    """
    if not results:
        print("No results to display")
        return

    print("\n" + "=" * 80)
    print(f"OPTIMIZATION SUMMARY - Top {top_n} Results")
    print("=" * 80)

    header = f"{'Rank':<6} {'Score':<8} {'ROI %':<8} {'PF':<6} {'Trades':<8} {'MaxDD %':<10} Parameters"
    print(header)
    print("-" * 80)

    for i, result in enumerate(results[:top_n], 1):
        m = result.metrics
        params_str = str(result.parameters)[:40] + "..." if len(str(result.parameters)) > 40 else str(result.parameters)

        row = (f"{i:<6} "
               f"{result.rank_score:<8.4f} "
               f"{m['roi']:<8.2f} "
               f"{m['profit_factor']:<6.2f} "
               f"{int(m['total_trades']):<8} "
               f"{m['max_drawdown']:<10.2f} "
               f"{params_str}")
        print(row)

    print("=" * 80 + "\n")
