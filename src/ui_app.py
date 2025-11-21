"""
Dynamic Strategy Builder UI - NiceGUI Web Interface

This module provides a web-based interface that dynamically discovers and renders
all available strategy components from builder_framework.py.

Key Features:
- Zero hardcoding: All UI elements generated from component metadata
- Automatic discovery: New components appear instantly
- Smart parameter rendering: int → Number input, choice → Dropdown, etc.
- Optimization support: Optional min/max ranges for optimizable parameters
"""

from nicegui import ui, app
from builder_framework import get_all_components, get_component, get_components_by_category
from backtesting_framework import BacktestEngine, BacktestConfig
from data_providers import fetch_data, DataManager
from optimizer import StrategyOptimizer, OptimizationResult, generate_parameter_grid
import pandas as pd
from typing import Dict, List, Any, Optional
import traceback


class StrategyBuilderUI:
    """Main UI application class"""

    def __init__(self):
        self.components = get_all_components()
        self.selected_pattern = None
        self.selected_filters = []
        self.selected_sessions = []
        self.parameter_values = {}  # Current parameter values
        self.optimization_ranges = {}  # Optimization ranges for parameters

        # UI containers (will be set during render)
        self.param_container = None
        self.results_container = None

    def render(self):
        """Main render method - builds the entire UI"""
        # Header
        with ui.header().classes('bg-primary text-white'):
            ui.label('🚀 Dynamic Strategy Builder').classes('text-h4')
            ui.label('Zero-Code Trading Strategy Development').classes('text-subtitle2 ml-4')

        # Main layout
        with ui.row().classes('w-full gap-4 p-4'):
            # Left panel: Component selection
            with ui.card().classes('w-1/3'):
                self._render_component_selector()

            # Middle panel: Parameters
            with ui.card().classes('w-1/3'):
                self._render_parameter_editor()

            # Right panel: Backtest configuration
            with ui.card().classes('w-1/3'):
                self._render_backtest_config()

        # Bottom panel: Results
        with ui.card().classes('w-full mt-4 p-4'):
            self._render_results_area()

    def _render_component_selector(self):
        """Dynamically render all available components"""
        ui.label('Step 1: Select Components').classes('text-h6 mb-4')

        # Entry Patterns (Radio buttons - select ONE)
        ui.label('Entry Pattern (Select One):').classes('font-bold mt-4 mb-2')

        pattern_options = []
        pattern_descriptions = {}

        for name, comp_data in self.components['entry_pattern'].items():
            metadata = comp_data['metadata']
            pattern_options.append(metadata.display_name)
            pattern_descriptions[metadata.display_name] = {
                'name': name,
                'description': metadata.description
            }

        # Create radio group
        pattern_radio = ui.radio(
            pattern_options,
            value=None,
            on_change=lambda e: self._on_pattern_selected(
                pattern_descriptions[e.value]['name'] if e.value else None
            )
        ).props('dense')

        # Display descriptions
        for name, comp_data in self.components['entry_pattern'].items():
            metadata = comp_data['metadata']
            ui.label(f'• {metadata.display_name}: {metadata.description}').classes(
                'text-xs text-gray-600 ml-6 mb-2'
            )

        ui.separator()

        # Filters (Checkboxes - select MULTIPLE)
        ui.label('Filters (Optional):').classes('font-bold mt-4 mb-2')

        with ui.column().classes('w-full'):
            for name, comp_data in self.components['filter'].items():
                metadata = comp_data['metadata']

                ui.checkbox(
                    metadata.display_name,
                    value=metadata.enabled_by_default,
                    on_change=lambda e, n=name: self._on_filter_toggled(n, e.value)
                )
                ui.label(metadata.description).classes('text-xs text-gray-600 ml-6 mb-2')

        ui.separator()

        # Sessions
        ui.label('Trading Sessions (Optional):').classes('font-bold mt-4 mb-2')

        with ui.column().classes('w-full'):
            for name, comp_data in self.components['session'].items():
                metadata = comp_data['metadata']

                ui.checkbox(
                    metadata.display_name,
                    value=metadata.enabled_by_default,
                    on_change=lambda e, n=name: self._on_session_toggled(n, e.value)
                )
                ui.label(metadata.description).classes('text-xs text-gray-600 ml-6 mb-2')

    def _render_parameter_editor(self):
        """Dynamically render parameters for selected components"""
        ui.label('Step 2: Configure Parameters').classes('text-h6 mb-4')

        ui.label('Parameters will appear here when you select components').classes(
            'text-sm text-gray-500 italic mb-4'
        )

        # Container for dynamic parameters
        self.param_container = ui.column().classes('w-full')

    def _update_parameter_editor(self):
        """Update parameter editor based on selected components"""
        if self.param_container is None:
            return

        self.param_container.clear()

        with self.param_container:
            # Pattern parameters
            if self.selected_pattern:
                comp_data = get_component('entry_pattern', self.selected_pattern)
                metadata = comp_data['metadata']

                ui.label(f'{metadata.display_name} Parameters:').classes('font-bold mt-2 mb-2')
                self._render_parameters(metadata.parameters, self.selected_pattern, 'entry_pattern')

                ui.separator().classes('my-4')

            # Filter parameters
            for filter_name in self.selected_filters:
                comp_data = get_component('filter', filter_name)
                metadata = comp_data['metadata']

                ui.label(f'{metadata.display_name} Parameters:').classes('font-bold mt-2 mb-2')
                self._render_parameters(metadata.parameters, filter_name, 'filter')

                ui.separator().classes('my-4')

            # Session parameters
            for session_name in self.selected_sessions:
                comp_data = get_component('session', session_name)
                metadata = comp_data['metadata']

                if metadata.parameters:  # Only show if has parameters
                    ui.label(f'{metadata.display_name} Parameters:').classes('font-bold mt-2 mb-2')
                    self._render_parameters(metadata.parameters, session_name, 'session')

                    ui.separator().classes('my-4')

            if not self.selected_pattern and not self.selected_filters and not self.selected_sessions:
                ui.label('No components selected yet').classes('text-sm text-gray-500 italic')

    def _render_parameters(self, parameters: Dict, component_name: str, category: str):
        """Render individual parameters dynamically"""
        for param_name, param_spec in parameters.items():
            param_key = f"{category}.{component_name}.{param_name}"

            # Set default value if not already set
            if param_key not in self.parameter_values:
                self.parameter_values[param_key] = param_spec['default']

            # Render based on type
            if param_spec['type'] == 'int':
                ui.number(
                    label=param_spec['display_name'],
                    value=param_spec['default'],
                    min=param_spec.get('min', 0),
                    max=param_spec.get('max', 1000),
                    step=param_spec.get('step', 1),
                    on_change=lambda e, k=param_key: self._on_param_changed(k, int(e.value))
                ).props('dense outlined').classes('w-full')

                # Add optimization range if optimizable
                if param_spec.get('optimizable', False):
                    # Initialize optimization ranges with defaults
                    if param_key not in self.optimization_ranges:
                        self.optimization_ranges[param_key] = {
                            'min': param_spec.get('min', 0),
                            'max': param_spec.get('max', 100),
                            'step': param_spec.get('step', 1)
                        }

                    with ui.row().classes('w-full gap-2 mt-1 mb-2'):
                        ui.label('Optimize range:').classes('text-xs font-bold')
                        ui.number(
                            label='Min',
                            value=param_spec.get('min', 0),
                            on_change=lambda e, k=param_key: self._set_opt_min(k, int(e.value))
                        ).props('dense outlined').classes('w-24')
                        ui.number(
                            label='Max',
                            value=param_spec.get('max', 100),
                            on_change=lambda e, k=param_key: self._set_opt_max(k, int(e.value))
                        ).props('dense outlined').classes('w-24')
                        ui.number(
                            label='Step',
                            value=param_spec.get('step', 1),
                            on_change=lambda e, k=param_key: self._set_opt_step(k, int(e.value))
                        ).props('dense outlined').classes('w-24')

            elif param_spec['type'] == 'float':
                ui.number(
                    label=param_spec['display_name'],
                    value=param_spec['default'],
                    min=param_spec.get('min', 0.0),
                    max=param_spec.get('max', 100.0),
                    step=param_spec.get('step', 0.1),
                    format='%.2f',
                    on_change=lambda e, k=param_key: self._on_param_changed(k, float(e.value))
                ).props('dense outlined').classes('w-full')

                # Add optimization range if optimizable
                if param_spec.get('optimizable', False):
                    # Initialize optimization ranges with defaults
                    if param_key not in self.optimization_ranges:
                        self.optimization_ranges[param_key] = {
                            'min': param_spec.get('min', 0.0),
                            'max': param_spec.get('max', 10.0),
                            'step': param_spec.get('step', 0.1)
                        }

                    with ui.row().classes('w-full gap-2 mt-1 mb-2'):
                        ui.label('Optimize range:').classes('text-xs font-bold')
                        ui.number(
                            label='Min',
                            value=param_spec.get('min', 0.0),
                            step=param_spec.get('step', 0.1),
                            format='%.2f',
                            on_change=lambda e, k=param_key: self._set_opt_min(k, float(e.value))
                        ).props('dense outlined').classes('w-24')
                        ui.number(
                            label='Max',
                            value=param_spec.get('max', 10.0),
                            step=param_spec.get('step', 0.1),
                            format='%.2f',
                            on_change=lambda e, k=param_key: self._set_opt_max(k, float(e.value))
                        ).props('dense outlined').classes('w-24')
                        ui.number(
                            label='Step',
                            value=param_spec.get('step', 0.1),
                            format='%.2f',
                            on_change=lambda e, k=param_key: self._set_opt_step(k, float(e.value))
                        ).props('dense outlined').classes('w-24')

            elif param_spec['type'] == 'choice':
                ui.select(
                    label=param_spec['display_name'],
                    options=param_spec['options'],
                    value=param_spec['default'],
                    on_change=lambda e, k=param_key: self._on_param_changed(k, e.value)
                ).props('dense outlined').classes('w-full')

            elif param_spec['type'] == 'bool':
                ui.checkbox(
                    param_spec['display_name'],
                    value=param_spec['default'],
                    on_change=lambda e, k=param_key: self._on_param_changed(k, e.value)
                )

            # Description
            if param_spec.get('description'):
                ui.label(param_spec['description']).classes('text-xs text-gray-600 mb-3')

    def _render_backtest_config(self):
        """Backtest configuration panel"""
        ui.label('Step 3: Run Backtest').classes('text-h6 mb-4')

        with ui.column().classes('w-full gap-2'):
            # Asset selection
            self.asset_input = ui.input(
                label='Asset Symbol',
                value='AAPL',
                placeholder='e.g., AAPL, EURUSD=X, BTC-USD'
            ).props('dense outlined').classes('w-full')

            ui.label('Examples: AAPL (stock), EURUSD=X (forex), BTC-USD (crypto)').classes(
                'text-xs text-gray-500 mb-2'
            )

            # Timeframe
            self.timeframe_select = ui.select(
                label='Timeframe',
                options=['1m', '5m', '15m', '30m', '1h', '1d', '1wk'],
                value='1d'
            ).props('dense outlined').classes('w-full')

            # Date range
            ui.label('Date Range:').classes('font-bold mt-2 mb-1')

            with ui.row().classes('w-full gap-2'):
                self.start_date = ui.input(
                    label='Start Date',
                    value='2023-01-01'
                ).props('dense outlined type=date').classes('w-1/2')

                self.end_date = ui.input(
                    label='End Date',
                    value='2024-01-01'
                ).props('dense outlined type=date').classes('w-1/2')

            ui.separator().classes('my-4')

            # Backtest settings
            ui.label('Backtest Settings:').classes('font-bold mb-2')

            self.initial_capital = ui.number(
                label='Initial Capital',
                value=100000,
                min=1000,
                max=10000000,
                step=1000,
                format='$%.0f'
            ).props('dense outlined').classes('w-full')

            self.commission = ui.number(
                label='Commission per Trade',
                value=1.5,
                min=0,
                max=100,
                step=0.5,
                format='$%.2f'
            ).props('dense outlined').classes('w-full')

            self.slippage = ui.number(
                label='Slippage (pips)',
                value=1.0,
                min=0,
                max=10,
                step=0.5,
                format='%.1f'
            ).props('dense outlined').classes('w-full')

            ui.separator().classes('my-4')

            # Action buttons
            ui.button(
                'Run Single Backtest',
                on_click=self._run_single_backtest,
                icon='play_arrow'
            ).props('color=primary').classes('w-full')

            ui.button(
                'Run Optimization',
                on_click=self._run_optimization,
                icon='tune'
            ).props('color=secondary').classes('w-full mt-2')

            ui.label('Optimize parameters across defined ranges').classes(
                'text-xs text-gray-500 italic mt-1'
            )

            ui.separator().classes('my-4')

            # Auto-Discovery button
            ui.button(
                '🔍 Auto-Discover Best Strategy',
                on_click=self._auto_discover_strategy,
                icon='auto_awesome'
            ).props('color=positive').classes('w-full mt-2')

            ui.label('Automatically test all pattern/filter combinations and find the best strategy').classes(
                'text-xs text-gray-500 italic mt-1'
            )

    def _render_results_area(self):
        """Results display area"""
        ui.label('Results').classes('text-h6 mb-4')
        ui.label('Run a backtest to see results here').classes('text-sm text-gray-500 italic')

        self.results_container = ui.column().classes('w-full')

    # Event handlers
    def _on_pattern_selected(self, pattern_name: Optional[str]):
        """Handle pattern selection"""
        self.selected_pattern = pattern_name
        self._update_parameter_editor()

        if pattern_name:
            comp_data = get_component('entry_pattern', pattern_name)
            ui.notify(f'Selected: {comp_data["metadata"].display_name}', type='info')

    def _on_filter_toggled(self, filter_name: str, enabled: bool):
        """Handle filter toggle"""
        if enabled and filter_name not in self.selected_filters:
            self.selected_filters.append(filter_name)
            comp_data = get_component('filter', filter_name)
            ui.notify(f'Enabled: {comp_data["metadata"].display_name}', type='info')
        elif not enabled and filter_name in self.selected_filters:
            self.selected_filters.remove(filter_name)
            comp_data = get_component('filter', filter_name)
            ui.notify(f'Disabled: {comp_data["metadata"].display_name}', type='warning')

        self._update_parameter_editor()

    def _on_session_toggled(self, session_name: str, enabled: bool):
        """Handle session toggle"""
        if enabled and session_name not in self.selected_sessions:
            self.selected_sessions.append(session_name)
            comp_data = get_component('session', session_name)
            ui.notify(f'Enabled: {comp_data["metadata"].display_name}', type='info')
        elif not enabled and session_name in self.selected_sessions:
            self.selected_sessions.remove(session_name)
            comp_data = get_component('session', session_name)
            ui.notify(f'Disabled: {comp_data["metadata"].display_name}', type='warning')

        self._update_parameter_editor()

    def _on_param_changed(self, param_key: str, value: Any):
        """Handle parameter value change"""
        self.parameter_values[param_key] = value

    def _set_opt_min(self, param_key: str, value: float):
        """Set optimization minimum"""
        if param_key not in self.optimization_ranges:
            self.optimization_ranges[param_key] = {}
        self.optimization_ranges[param_key]['min'] = value

    def _set_opt_max(self, param_key: str, value: float):
        """Set optimization maximum"""
        if param_key not in self.optimization_ranges:
            self.optimization_ranges[param_key] = {}
        self.optimization_ranges[param_key]['max'] = value

    def _set_opt_step(self, param_key: str, value: float):
        """Set optimization step"""
        if param_key not in self.optimization_ranges:
            self.optimization_ranges[param_key] = {}
        self.optimization_ranges[param_key]['step'] = value

    def _adjust_date_range_for_intraday(self, start_date: str, end_date: str, interval: str):
        """
        Adjust date range if using intraday timeframe (Yahoo Finance 730-day limit)

        Returns:
            tuple: (adjusted_start_date, end_date, was_adjusted)
        """
        from datetime import datetime, timedelta

        intraday_intervals = ['1m', '5m', '15m', '30m', '1h']
        if interval not in intraday_intervals:
            return start_date, end_date, False

        # Calculate date range in days
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        days_range = (end_dt - start_dt).days

        # If range exceeds 730 days, adjust start date
        if days_range > 730:
            adjusted_start = end_dt - timedelta(days=729)  # 729 to be safe
            adjusted_start_str = adjusted_start.strftime('%Y-%m-%d')
            return adjusted_start_str, end_date, True

        return start_date, end_date, False

    async def _run_single_backtest(self):
        """Run a single backtest with current parameters"""
        # Validation
        if not self.selected_pattern:
            ui.notify('Please select an entry pattern first', type='negative')
            return

        ui.notify('Fetching market data...', type='info')

        try:
            # Adjust date range for intraday data if needed
            start_date, end_date, was_adjusted = self._adjust_date_range_for_intraday(
                self.start_date.value,
                self.end_date.value,
                self.timeframe_select.value
            )

            if was_adjusted:
                ui.notify(
                    f'⚠️ Intraday data limited to 730 days. Adjusted start date to {start_date}',
                    type='warning'
                )

            # Fetch data using data abstraction layer
            # Try yfinance first, fallback to mock data for testing
            try:
                df = fetch_data(
                    symbol=self.asset_input.value,
                    start_date=start_date,
                    end_date=end_date,
                    interval=self.timeframe_select.value,
                    provider='yfinance'
                )
            except Exception as e:
                ui.notify(f'YFinance unavailable, using mock data for testing', type='warning')
                df = fetch_data(
                    symbol=self.asset_input.value,
                    start_date=self.start_date.value,
                    end_date=self.end_date.value,
                    interval=self.timeframe_select.value,
                    provider='mock'
                )

            if df.empty:
                ui.notify(f'No data found for {self.asset_input.value}', type='negative')
                return

            ui.notify(f'Fetched {len(df)} bars. Applying pattern...', type='info')

            # Apply pattern
            pattern_func = get_component('entry_pattern', self.selected_pattern)['function']
            pattern_params = self._extract_params_for_component(
                self.selected_pattern, 'entry_pattern'
            )
            df = pattern_func(df, **pattern_params)

            # Apply filters
            for filter_name in self.selected_filters:
                filter_func = get_component('filter', filter_name)['function']
                filter_params = self._extract_params_for_component(filter_name, 'filter')
                df = filter_func(df, **filter_params)

            # Apply sessions
            for session_name in self.selected_sessions:
                session_func = get_component('session', session_name)['function']
                session_params = self._extract_params_for_component(session_name, 'session')
                df = session_func(df, **session_params)

            # Combine filters and sessions
            if self.selected_filters or self.selected_sessions:
                if 'filter_ok' not in df.columns:
                    df['filter_ok'] = True
                if 'session_ok' not in df.columns:
                    df['session_ok'] = True

                # Final filter: both must be True
                final_filter = df['filter_ok'] & df['session_ok']
                df['signal_long'] = df.get('signal_long', False) & final_filter
                df['signal_short'] = df.get('signal_short', False) & final_filter

            ui.notify('Running backtest...', type='info')

            # Run backtest
            config = BacktestConfig(
                initial_capital=self.initial_capital.value,
                commission_per_trade=self.commission.value,
                slippage_pips=self.slippage.value
            )

            engine = BacktestEngine(config)
            result = engine.run(df, {
                'pattern': self.selected_pattern,
                'filters': self.selected_filters,
                'sessions': self.selected_sessions
            })

            # Display results
            self._display_results(result, df)

            ui.notify('Backtest complete!', type='positive')

        except Exception as e:
            error_msg = str(e)
            ui.notify(f'Error: {error_msg}', type='negative')
            print(f"Backtest error: {traceback.format_exc()}")

    def _extract_params_for_component(self, component_name: str, category: str) -> Dict:
        """Extract parameter values for a specific component"""
        params = {}
        prefix = f"{category}.{component_name}."

        for param_key, param_value in self.parameter_values.items():
            if param_key.startswith(prefix):
                param_name = param_key[len(prefix):]
                params[param_name] = param_value

        return params

    async def _run_optimization(self):
        """Run optimization across parameter ranges"""
        # Validation
        if not self.selected_pattern:
            ui.notify('Please select an entry pattern first', type='negative')
            return

        if not self.optimization_ranges:
            ui.notify('No optimization ranges defined. Set min/max/step for optimizable parameters.',
                     type='warning')
            return

        ui.notify('Starting optimization... This may take several minutes.', type='info')

        try:
            # Adjust date range for intraday data if needed
            start_date, end_date, was_adjusted = self._adjust_date_range_for_intraday(
                self.start_date.value,
                self.end_date.value,
                self.timeframe_select.value
            )

            if was_adjusted:
                ui.notify(
                    f'⚠️ Intraday data limited to 730 days. Adjusted start date to {start_date}',
                    type='warning'
                )

            # Fetch data using data abstraction layer
            ui.notify('Fetching market data...', type='info')
            try:
                df = fetch_data(
                    symbol=self.asset_input.value,
                    start_date=start_date,
                    end_date=end_date,
                    interval=self.timeframe_select.value,
                    provider='yfinance'
                )
            except Exception as e:
                ui.notify(f'YFinance unavailable, using mock data for testing', type='warning')
                df = fetch_data(
                    symbol=self.asset_input.value,
                    start_date=self.start_date.value,
                    end_date=self.end_date.value,
                    interval=self.timeframe_select.value,
                    provider='mock'
                )

            if df.empty:
                ui.notify(f'No data found for {self.asset_input.value}', type='negative')
                return

            ui.notify(f'Fetched {len(df)} bars. Building parameter grid...', type='info')

            # Build parameter ranges for optimization
            # Extract only the parameters for the selected pattern
            pattern_prefix = f"entry_pattern.{self.selected_pattern}."
            param_ranges = {}

            for param_key, range_spec in self.optimization_ranges.items():
                if not param_key.startswith(pattern_prefix):
                    continue  # Skip parameters from other components

                # Extract parameter name
                param_name = param_key[len(pattern_prefix):]

                # Get parameter specification from metadata
                comp_data = get_component('entry_pattern', self.selected_pattern)
                metadata = comp_data['metadata']

                if param_name not in metadata.parameters:
                    continue

                param_spec = metadata.parameters[param_name]

                # Build range
                min_val = range_spec.get('min', param_spec.get('min', 0))
                max_val = range_spec.get('max', param_spec.get('max', 100))
                step = range_spec.get('step', param_spec.get('step', 1))

                param_type = param_spec['type']

                if param_type == 'int':
                    param_ranges[param_name] = list(range(int(min_val), int(max_val) + 1, int(step)))
                elif param_type == 'float':
                    values = []
                    current = float(min_val)
                    while current <= float(max_val):
                        values.append(round(current, 2))
                        current += float(step)
                    param_ranges[param_name] = values

            if not param_ranges:
                ui.notify('No optimizable parameters configured with ranges', type='warning')
                return

            # Build filter configurations
            filter_configs = []
            for filter_name in self.selected_filters:
                filter_params = self._extract_params_for_component(filter_name, 'filter')
                filter_configs.append({
                    'name': filter_name,
                    'params': filter_params
                })

            total_combinations = 1
            for values in param_ranges.values():
                total_combinations *= len(values)

            ui.notify(f'Testing {total_combinations} parameter combinations...', type='info')

            # Run optimization
            config = BacktestConfig(
                initial_capital=self.initial_capital.value,
                commission_per_trade=self.commission.value,
                slippage_pips=self.slippage.value
            )

            optimizer = StrategyOptimizer(config, n_jobs=-1)  # Use all CPUs
            results = optimizer.optimize(
                df,
                self.selected_pattern,
                param_ranges,
                filter_configs
            )

            if not results:
                ui.notify('Optimization completed but no valid results (zero trades in all combinations)',
                         type='warning')
                return

            # Display results
            self._display_optimization_results(results[:20])  # Top 20 results

            ui.notify(f'Optimization complete! Found {len(results)} valid configurations. Best score: {results[0].rank_score:.4f}',
                     type='positive')

        except Exception as e:
            error_msg = str(e)
            ui.notify(f'Optimization error: {error_msg}', type='negative')
            print(f"Optimization error: {traceback.format_exc()}")

    def _display_results(self, result, df: pd.DataFrame):
        """Display backtest results"""
        self.results_container.clear()

        with self.results_container:
            # Summary metrics
            ui.label('Performance Summary').classes('text-h6 mb-4')

            with ui.grid(columns=4).classes('w-full gap-4'):
                self._metric_card('Total Trades', result.metrics['total_trades'], '',
                                 'blue')
                self._metric_card('Win Rate', result.metrics['win_rate'], '%',
                                 'green' if result.metrics['win_rate'] > 50 else 'orange')
                self._metric_card('Profit Factor', result.metrics['profit_factor'], '',
                                 'green' if result.metrics['profit_factor'] > 1.5 else 'orange')
                self._metric_card('ROI', result.metrics['roi'], '%',
                                 'green' if result.metrics['roi'] > 0 else 'red')
                self._metric_card('Max Drawdown', result.metrics['max_drawdown'], '%',
                                 'red')
                self._metric_card('Sharpe Ratio', result.metrics['sharpe_ratio'], '',
                                 'green' if result.metrics['sharpe_ratio'] > 1 else 'orange')
                self._metric_card('Avg Win', result.metrics['avg_win'], '$',
                                 'green')
                self._metric_card('Avg Loss', result.metrics['avg_loss'], '$',
                                 'red')

            ui.separator().classes('my-4')

            # Trade statistics
            ui.label('Trade Statistics').classes('text-h6 mb-4')

            with ui.grid(columns=3).classes('w-full gap-4'):
                self._metric_card('Winning Trades', result.metrics['winning_trades'], '',
                                 'green')
                self._metric_card('Losing Trades', result.metrics['losing_trades'], '',
                                 'red')
                self._metric_card('Total P&L', result.metrics['total_pnl'], '$',
                                 'green' if result.metrics['total_pnl'] > 0 else 'red')

            ui.separator().classes('my-4')

            # Trade log (if trades exist)
            if len(result.trades) > 0:
                ui.label('Trade Log (Last 10 Trades)').classes('text-h6 mb-4')

                # Prepare trade data for table
                trade_columns = [
                    {'name': 'entry_bar', 'label': 'Entry Bar', 'field': 'entry_bar'},
                    {'name': 'exit_bar', 'label': 'Exit Bar', 'field': 'exit_bar'},
                    {'name': 'direction', 'label': 'Direction', 'field': 'direction'},
                    {'name': 'entry_price', 'label': 'Entry Price', 'field': 'entry_price'},
                    {'name': 'exit_price', 'label': 'Exit Price', 'field': 'exit_price'},
                    {'name': 'pnl', 'label': 'P&L', 'field': 'pnl'},
                    {'name': 'exit_reason', 'label': 'Exit Reason', 'field': 'exit_reason'}
                ]

                trade_rows = []
                for _, trade in result.trades.tail(10).iterrows():
                    trade_rows.append({
                        'entry_bar': int(trade['entry_bar']),
                        'exit_bar': int(trade['exit_bar']),
                        'direction': trade['direction'],
                        'entry_price': f"{trade['entry_price']:.2f}",
                        'exit_price': f"{trade['exit_price']:.2f}",
                        'pnl': f"${trade['pnl']:.2f}",
                        'exit_reason': trade['exit_reason']
                    })

                ui.table(columns=trade_columns, rows=trade_rows).classes('w-full')
            else:
                ui.label('No trades executed. Try adjusting parameters or selecting a different pattern.').classes(
                    'text-sm text-orange-600 italic'
                )

    def _display_optimization_results(self, results: List[OptimizationResult]):
        """Display optimization results in a table"""
        self.results_container.clear()

        with self.results_container:
            ui.label(f'Optimization Results - Top {len(results)} Configurations').classes('text-h6 mb-4')

            # Build table
            columns = [
                {'name': 'rank', 'label': 'Rank', 'field': 'rank', 'align': 'left'},
                {'name': 'score', 'label': 'Score', 'field': 'score', 'align': 'left'},
                {'name': 'roi', 'label': 'ROI %', 'field': 'roi', 'align': 'left'},
                {'name': 'pf', 'label': 'Profit Factor', 'field': 'pf', 'align': 'left'},
                {'name': 'trades', 'label': 'Trades', 'field': 'trades', 'align': 'left'},
                {'name': 'win_rate', 'label': 'Win Rate %', 'field': 'win_rate', 'align': 'left'},
                {'name': 'max_dd', 'label': 'Max DD %', 'field': 'max_dd', 'align': 'left'},
                {'name': 'params', 'label': 'Parameters', 'field': 'params', 'align': 'left'}
            ]

            rows = []
            for i, result in enumerate(results, 1):
                m = result.metrics
                rows.append({
                    'rank': i,
                    'score': f"{result.rank_score:.4f}",
                    'roi': f"{m['roi']:.2f}",
                    'pf': f"{m['profit_factor']:.2f}",
                    'trades': int(m['total_trades']),
                    'win_rate': f"{m['win_rate']:.2f}",
                    'max_dd': f"{m['max_drawdown']:.2f}",
                    'params': str(result.parameters)
                })

            ui.table(columns=columns, rows=rows, row_key='rank').classes('w-full')

            ui.separator().classes('my-4')

            # Detailed view of best result
            if results:
                best = results[0]
                ui.label('Best Configuration Details').classes('text-h6 mb-4')

                with ui.card().classes('p-4 bg-green-50'):
                    ui.label(f'Rank: #1 | Score: {best.rank_score:.4f}').classes(
                        'text-lg font-bold text-green-700 mb-2'
                    )

                    ui.label('Parameters:').classes('font-bold mt-2 mb-1')
                    for param, value in best.parameters.items():
                        ui.label(f'  • {param}: {value}').classes('text-sm')

                    ui.label('Metrics:').classes('font-bold mt-4 mb-1')
                    metrics_to_show = [
                        ('ROI', best.metrics['roi'], '%'),
                        ('Profit Factor', best.metrics['profit_factor'], ''),
                        ('Win Rate', best.metrics['win_rate'], '%'),
                        ('Total Trades', best.metrics['total_trades'], ''),
                        ('Max Drawdown', best.metrics['max_drawdown'], '%'),
                        ('Sharpe Ratio', best.metrics['sharpe_ratio'], ''),
                        ('Avg Win', best.metrics['avg_win'], '$'),
                        ('Avg Loss', best.metrics['avg_loss'], '$')
                    ]

                    for label, value, suffix in metrics_to_show:
                        ui.label(f'  • {label}: {value:.2f}{suffix}').classes('text-sm')

                ui.separator().classes('my-4')

                # Export button (Phase 4 feature - placeholder for now)
                ui.label('Export Features').classes('text-h6 mb-4')
                ui.button(
                    'Export Best to Pine Script (Phase 4)',
                    icon='download'
                ).props('color=green disabled').classes('w-full')
                ui.label('Export to Pine Script will be enabled in Phase 4').classes(
                    'text-xs text-gray-500 italic mt-1'
                )

    def _auto_discover_strategy(self):
        """Auto-discover the best strategy by testing all pattern/filter combinations"""
        try:
            ui.notify('Starting auto-discovery... This may take a few minutes', type='info')

            # Get all available patterns and filters
            patterns_dict = get_components_by_category('entry_pattern')
            filters_dict = get_components_by_category('filter')

            # Prepare test configurations
            # Test each pattern with: no filter, each individual filter
            test_configs = []

            for pattern_name, pattern_comp in patterns_dict.items():
                pattern_meta = pattern_comp['metadata']

                # Test with no filter
                test_configs.append({
                    'pattern': pattern_name,
                    'pattern_params': {k: v.get('default') for k, v in pattern_meta.parameters.items()},
                    'filters': []
                })

                # Test with each filter individually
                for filter_name, filter_comp in filters_dict.items():
                    filter_meta = filter_comp['metadata']

                    filter_config = {
                        'name': filter_name,
                        'params': {k: v.get('default') for k, v in filter_meta.parameters.items()}
                    }

                    test_configs.append({
                        'pattern': pattern_name,
                        'pattern_params': {k: v.get('default') for k, v in pattern_meta.parameters.items()},
                        'filters': [filter_config]
                    })

            ui.notify(f'Testing {len(test_configs)} strategy combinations...', type='info')

            # Adjust date range for intraday data if needed
            start_date, end_date, was_adjusted = self._adjust_date_range_for_intraday(
                self.start_date.value,
                self.end_date.value,
                self.timeframe_select.value
            )

            if was_adjusted:
                ui.notify(
                    f'⚠️ Intraday data limited to 730 days. Adjusted start date to {start_date}',
                    type='warning'
                )

            # Download data once
            try:
                df = fetch_data(
                    symbol=self.asset_input.value,
                    start_date=start_date,
                    end_date=end_date,
                    interval=self.timeframe_select.value,
                    provider='yfinance'
                )
            except Exception as e:
                ui.notify(f'YFinance unavailable, using mock data for testing: {str(e)}', type='warning')
                df = fetch_data(
                    symbol=self.asset_input.value,
                    start_date=self.start_date.value,
                    end_date=self.end_date.value,
                    interval=self.timeframe_select.value,
                    provider='mock',
                    num_bars=500
                )

            # Run backtest for each configuration
            results = []
            config_obj = BacktestConfig(
                initial_capital=self.initial_capital.value,
                commission_per_trade=self.commission.value,
                slippage_pips=self.slippage.value
            )

            for i, test_config in enumerate(test_configs):
                try:
                    # Apply pattern
                    pattern_comp = get_component('entry_pattern', test_config['pattern'])
                    if not pattern_comp:
                        continue

                    pattern_func = pattern_comp['function']
                    df_signals = pattern_func(df.copy(), **test_config['pattern_params'])

                    # Apply filters
                    for filter_config in test_config['filters']:
                        filter_comp = get_component('filter', filter_config['name'])
                        if filter_comp:
                            filter_func = filter_comp['function']
                            df_signals = filter_func(df_signals, **filter_config['params'])

                    # Combine filter results
                    if test_config['filters'] and 'filter_ok' in df_signals.columns:
                        if 'signal_long' in df_signals.columns:
                            df_signals['signal_long'] = df_signals['signal_long'] & df_signals['filter_ok']
                        if 'signal_short' in df_signals.columns:
                            df_signals['signal_short'] = df_signals['signal_short'] & df_signals['filter_ok']

                    # Run backtest
                    engine = BacktestEngine(config_obj)
                    backtest_result = engine.run(df_signals, test_config)

                    # Calculate composite score
                    score = self._calculate_strategy_score(backtest_result.metrics)

                    # Store result
                    filter_names = ', '.join([f['name'] for f in test_config['filters']]) if test_config['filters'] else 'None'
                    results.append({
                        'pattern': test_config['pattern'],
                        'filters': filter_names,
                        'score': score,
                        'roi': backtest_result.metrics['roi'],
                        'profit_factor': backtest_result.metrics['profit_factor'],
                        'win_rate': backtest_result.metrics['win_rate'],
                        'sharpe_ratio': backtest_result.metrics['sharpe_ratio'],
                        'max_drawdown': backtest_result.metrics['max_drawdown'],
                        'total_trades': backtest_result.metrics['total_trades']
                    })

                except Exception as e:
                    print(f"Error testing {test_config['pattern']}: {str(e)}")
                    continue

            # Display results
            if results:
                self._display_discovery_results(results)
                ui.notify(f'Auto-discovery complete! Found {len(results)} valid strategies', type='positive')
            else:
                ui.notify('No valid strategies found. Try different date range or asset.', type='warning')

        except Exception as e:
            ui.notify(f'Auto-discovery failed: {str(e)}', type='negative')
            print(f"Auto-discovery error: {str(e)}")
            import traceback
            traceback.print_exc()

    def _calculate_strategy_score(self, metrics: dict) -> float:
        """
        Calculate composite strategy score

        Scoring formula:
        - ROI: 30%
        - Profit Factor: 25%
        - Win Rate: 15%
        - Sharpe Ratio: 15%
        - Drawdown penalty: 10%
        - Trade count penalty: 5%
        """
        # Normalize components
        roi_score = min(max(metrics['roi'] / 100, -1), 2)  # Cap at 200% ROI
        pf_score = min(metrics['profit_factor'] / 3, 1.0)  # Cap at PF=3
        wr_score = metrics['win_rate'] / 100  # Already a percentage
        sharpe_score = min(max(metrics['sharpe_ratio'] / 3, 0), 1)  # Cap at Sharpe=3

        # Drawdown penalty (less drawdown = better)
        dd_penalty = max(1 - abs(metrics['max_drawdown']) / 100, 0)

        # Trade count penalty (too few trades = unreliable)
        trade_penalty = min(metrics['total_trades'] / 30, 1.0)  # Penalize if < 30 trades

        # Composite score
        score = (
            roi_score * 0.30 +
            pf_score * 0.25 +
            wr_score * 0.15 +
            sharpe_score * 0.15 +
            dd_penalty * 0.10 +
            trade_penalty * 0.05
        )

        return score

    def _display_discovery_results(self, results: list):
        """Display auto-discovery results in a table"""
        # Sort by score (descending)
        results_sorted = sorted(results, key=lambda x: x['score'], reverse=True)

        # Show top 10
        top_results = results_sorted[:10]

        # Clear previous results and display new ones
        self.results_container.clear()

        with self.results_container:
            ui.label('Auto-Discovery Results').classes('text-h5 font-bold mb-4')

            # Highlight best strategy
            best = top_results[0]
            with ui.card().classes('w-full p-4 bg-green-50 border-2 border-green-500 mb-4'):
                ui.label('🏆 Best Strategy Found').classes('text-h6 font-bold text-green-700 mb-2')
                ui.label(f"Pattern: {best['pattern']}").classes('font-semibold')
                ui.label(f"Filters: {best['filters']}").classes('text-sm')
                ui.label(f"Composite Score: {best['score']:.4f}").classes('text-lg font-bold text-green-700 mt-2')

                with ui.row().classes('gap-4 mt-3'):
                    self._metric_card('ROI', best['roi'], '%', 'green')
                    self._metric_card('Profit Factor', best['profit_factor'], '', 'blue')
                    self._metric_card('Win Rate', best['win_rate'], '%', 'purple')
                    self._metric_card('Sharpe', best['sharpe_ratio'], '', 'orange')

            # Results table
            ui.label('Top 10 Strategies').classes('text-h6 font-bold mt-6 mb-3')

            columns = [
                {'name': 'rank', 'label': 'Rank', 'field': 'rank', 'align': 'center'},
                {'name': 'pattern', 'label': 'Pattern', 'field': 'pattern', 'align': 'left'},
                {'name': 'filters', 'label': 'Filters', 'field': 'filters', 'align': 'left'},
                {'name': 'score', 'label': 'Score', 'field': 'score', 'align': 'center', 'sortable': True},
                {'name': 'roi', 'label': 'ROI %', 'field': 'roi', 'align': 'center', 'sortable': True},
                {'name': 'pf', 'label': 'PF', 'field': 'pf', 'align': 'center', 'sortable': True},
                {'name': 'wr', 'label': 'WR %', 'field': 'wr', 'align': 'center', 'sortable': True},
                {'name': 'sharpe', 'label': 'Sharpe', 'field': 'sharpe', 'align': 'center', 'sortable': True},
                {'name': 'dd', 'label': 'MaxDD %', 'field': 'dd', 'align': 'center', 'sortable': True},
                {'name': 'trades', 'label': 'Trades', 'field': 'trades', 'align': 'center'}
            ]

            rows = []
            for i, result in enumerate(top_results, 1):
                rows.append({
                    'rank': i,
                    'pattern': result['pattern'],
                    'filters': result['filters'],
                    'score': f"{result['score']:.4f}",
                    'roi': f"{result['roi']:.2f}",
                    'pf': f"{result['profit_factor']:.2f}",
                    'wr': f"{result['win_rate']:.2f}",
                    'sharpe': f"{result['sharpe_ratio']:.2f}",
                    'dd': f"{result['max_drawdown']:.2f}",
                    'trades': int(result['total_trades'])
                })

            ui.table(columns=columns, rows=rows).classes('w-full')

            ui.label('💡 Tip: Select the best strategy manually in Step 1, then optimize its parameters').classes(
                'text-sm text-gray-600 italic mt-4'
            )

    def _metric_card(self, label: str, value: float, suffix: str, color: str = 'blue'):
        """Render a metric card"""
        with ui.card().classes(f'p-4 bg-{color}-50'):
            ui.label(label).classes('text-sm text-gray-600 mb-1')
            ui.label(f'{value:.2f}{suffix}').classes(f'text-2xl font-bold text-{color}-700')


# Main entry point
def main():
    """Main application entry point"""
    ui.page_title = 'Strategy Builder - Dynamic UI'

    builder = StrategyBuilderUI()
    builder.render()

    ui.run(
        title='Strategy Builder',
        port=8080,
        reload=False,
        show=False  # Set to True to auto-open browser
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
