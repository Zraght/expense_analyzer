"""
Modules package for expense analysis.

This package contains the core analysis modules for reading,
analyzing, and visualizing expense data.
"""

from .reading import read_expenses_csv, get_data_summary, show_data_summary
from .analysis import (
    calculate_total_spent,
    calculate_monthly_average,
    find_max_min_expenses,
    calculate_expenses_by_category,
    generate_complete_summary,
    display_analysis_summary
)
from .visualization import (
    configure_plot_style,
    create_bar_chart_by_category,
    create_pie_chart_by_category,
    create_line_chart_monthly_expenses,
    generate_all_charts
)

__all__ = [
    # Reading
    'read_expenses_csv',
    'get_data_summary',
    'show_data_summary',
    # Analysis
    'calculate_total_spent',
    'calculate_monthly_average',
    'find_max_min_expenses',
    'calculate_expenses_by_category',
    'generate_complete_summary',
    'display_analysis_summary',
    # Visualization
    'configure_plot_style',
    'create_bar_chart_by_category',
    'create_pie_chart_by_category',
    'create_line_chart_monthly_expenses',
    'generate_all_charts',
]
