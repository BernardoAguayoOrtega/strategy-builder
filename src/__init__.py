"""
Strategy Builder Framework

A dynamic UI builder framework for algorithmic trading strategy development.
"""

__version__ = '1.0.0'
__author__ = 'Bernardo Aguayo Ortega'

from .builder_framework import (
    get_all_components,
    get_components_by_category,
    get_component,
    list_all_component_names,
    normalize_column_names,
    validate_dataframe
)

__all__ = [
    'get_all_components',
    'get_components_by_category',
    'get_component',
    'list_all_component_names',
    'normalize_column_names',
    'validate_dataframe'
]
