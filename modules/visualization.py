"""
Visualization module for personal expenses.

This module contains functions to create charts and visualizations of expenses.
Includes configuration-driven chart generation with comprehensive logging.
"""

import logging
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for better compatibility
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from typing import Union, Dict, Tuple

from utils.validators import validate_dataframe_not_empty, validate_required_columns
from utils.path_utils import PathManager

logger = logging.getLogger(__name__)


def configure_plot_style(style: str = "seaborn-v0_8-darkgrid", palette: str = "husl") -> None:
    """
    Configure matplotlib and seaborn plotting styles.
    
    Args:
        style: Matplotlib style to use.
        palette: Seaborn color palette to use.
        
    Example:
        >>> configure_plot_style("seaborn-v0_8-darkgrid", "husl")
    """
    try:
        plt.style.use(style)
        sns.set_palette(palette)
        logger.debug(f"Plot style configured: {style}, palette: {palette}")
    except Exception as e:
        logger.warning(f"Could not set plot style: {e}. Using defaults.")


def create_bar_chart_by_category(
    df: pd.DataFrame,
    output_folder: Union[str, Path],
    config: Dict = None
) -> Path:
    """
    Create a bar chart showing total spending by category.
    
    Args:
        df: DataFrame with expenses containing 'Category' and 'Amount' columns.
        output_folder: Path to the folder where the chart will be saved.
        config: Configuration dictionary for visualization settings.
        
    Returns:
        Path to the generated PNG file.
        
    Raises:
        ValueError: If DataFrame validation fails.
        
    Example:
        >>> path = create_bar_chart_by_category(expenses_df, "output")
        >>> print(f"Chart saved at: {path}")
    """
    validate_dataframe_not_empty(df, "Expense data")
    validate_required_columns(df, ['Category', 'Amount'], "Expense data")
    
    # Default configuration
    if config is None:
        config = {
            'dpi': 300,
            'figure_size': [12, 6],
            'timestamp_format': '%Y%m%d_%H%M%S',
            'show_plots': False
        }
    
    output_folder = PathManager.ensure_directory(output_folder)
    
    try:
        logger.info("Creating bar chart by category")
        
        # Group by category and sum amounts
        category_expenses = df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        
        # Create the figure
        fig_size = tuple(config.get('figure_size', [12, 6]))
        plt.figure(figsize=fig_size)
        
        # Create bar chart
        colors = plt.cm.Set3(range(len(category_expenses)))
        bars = plt.bar(
            category_expenses.index, 
            category_expenses.values, 
            color=colors,
            edgecolor='black', 
            linewidth=1.2
        )
        
        # Add values above bars
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width()/2., 
                height,
                f'${height:,.0f}',
                ha='center', 
                va='bottom', 
                fontsize=10, 
                fontweight='bold'
            )
        
        # Configure labels and title
        plt.xlabel('Category', fontsize=12, fontweight='bold')
        plt.ylabel('Total Amount ($)', fontsize=12, fontweight='bold')
        plt.title('Total Spending by Category', fontsize=16, fontweight='bold', pad=20)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        # Add grid
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the chart
        timestamp = datetime.now().strftime(config.get('timestamp_format', '%Y%m%d_%H%M%S'))
        filename = f'bar_chart_category_{timestamp}.png'
        full_path = output_folder / filename
        
        dpi = config.get('dpi', 300)
        plt.savefig(full_path, dpi=dpi, bbox_inches='tight')
        
        logger.info(f"Bar chart saved: {full_path}")
        
        # Optionally display the chart
        if config.get('show_plots', False):
            plt.show()
        
        plt.close()
        
        return full_path
        
    except Exception as e:
        plt.close()
        error_msg = f"Error creating bar chart: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg)


def create_pie_chart_by_category(
    df: pd.DataFrame,
    output_folder: Union[str, Path],
    config: Dict = None
) -> Path:
    """
    Create a pie chart showing percentage of spending by category.
    
    Args:
        df: DataFrame with expenses containing 'Category' and 'Amount' columns.
        output_folder: Path to the folder where the chart will be saved.
        config: Configuration dictionary for visualization settings.
        
    Returns:
        Path to the generated PNG file.
        
    Example:
        >>> path = create_pie_chart_by_category(expenses_df, "output")
        >>> print(f"Chart saved at: {path}")
    """
    validate_dataframe_not_empty(df, "Expense data")
    validate_required_columns(df, ['Category', 'Amount'], "Expense data")
    
    if config is None:
        config = {
            'dpi': 300,
            'figure_size': [12, 8],
            'timestamp_format': '%Y%m%d_%H%M%S',
            'show_plots': False
        }
    
    output_folder = PathManager.ensure_directory(output_folder)
    
    try:
        logger.info("Creating pie chart by category")
        
        # Group by category and sum amounts
        category_expenses = df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        
        # Create the figure
        fig_size = tuple(config.get('figure_size', [12, 8]))
        plt.figure(figsize=fig_size)
        
        # Create pie chart
        colors = plt.cm.Set3(range(len(category_expenses)))
        wedges, texts, autotexts = plt.pie(
            category_expenses.values,
            labels=category_expenses.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            explode=[0.05] * len(category_expenses),
            shadow=True,
            textprops={'fontsize': 11, 'fontweight': 'bold'}
        )
        
        # Improve percentage style
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        # Add title
        plt.title('Expense Distribution by Category', fontsize=16, fontweight='bold', pad=20)
        
        # Add legend with values
        legend_labels = [f'{cat}: ${val:,.2f}' for cat, val in category_expenses.items()]
        plt.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the chart
        timestamp = datetime.now().strftime(config.get('timestamp_format', '%Y%m%d_%H%M%S'))
        filename = f'pie_chart_category_{timestamp}.png'
        full_path = output_folder / filename
        
        dpi = config.get('dpi', 300)
        plt.savefig(full_path, dpi=dpi, bbox_inches='tight')
        
        logger.info(f"Pie chart saved: {full_path}")
        
        if config.get('show_plots', False):
            plt.show()
        
        plt.close()
        
        return full_path
        
    except Exception as e:
        plt.close()
        error_msg = f"Error creating pie chart: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg)


def create_line_chart_monthly_expenses(
    df: pd.DataFrame,
    output_folder: Union[str, Path],
    config: Dict = None
) -> Path:
    """
    Create a line chart showing total monthly spending.
    
    Args:
        df: DataFrame with expenses containing 'Date' and 'Amount' columns.
        output_folder: Path to the folder where the chart will be saved.
        config: Configuration dictionary for visualization settings.
        
    Returns:
        Path to the generated PNG file.
        
    Example:
        >>> path = create_line_chart_monthly_expenses(expenses_df, "output")
        >>> print(f"Chart saved at: {path}")
    """
    validate_dataframe_not_empty(df, "Expense data")
    validate_required_columns(df, ['Date', 'Amount'], "Expense data")
    
    if config is None:
        config = {
            'dpi': 300,
            'figure_size': [14, 6],
            'timestamp_format': '%Y%m%d_%H%M%S',
            'show_plots': False
        }
    
    output_folder = PathManager.ensure_directory(output_folder)
    
    try:
        logger.info("Creating line chart for monthly expenses")
        
        # Create a copy to avoid modifying the original
        df_temp = df.copy()
        
        # Extract year and month from date
        df_temp['Year_Month'] = df_temp['Date'].dt.to_period('M')
        
        # Group by month and sum expenses
        monthly_expenses = df_temp.groupby('Year_Month')['Amount'].sum().reset_index()
        
        # Convert period to string for better visualization
        monthly_expenses['Month_Str'] = monthly_expenses['Year_Month'].astype(str)
        
        # Create the figure
        fig_size = tuple(config.get('figure_size', [14, 6]))
        plt.figure(figsize=fig_size)
        
        # Create line chart
        plt.plot(
            monthly_expenses['Month_Str'], 
            monthly_expenses['Amount'],
            marker='o', 
            linewidth=2.5, 
            markersize=10, 
            color='#2E86AB',
            markerfacecolor='#A23B72', 
            markeredgecolor='white', 
            markeredgewidth=2
        )
        
        # Add values above points
        for i, (month, amount) in enumerate(zip(monthly_expenses['Month_Str'], monthly_expenses['Amount'])):
            plt.text(
                i, 
                amount, 
                f'${amount:,.0f}',
                ha='center', 
                va='bottom', 
                fontsize=10, 
                fontweight='bold'
            )
        
        # Configure labels and title
        plt.xlabel('Month', fontsize=12, fontweight='bold')
        plt.ylabel('Total Spending ($)', fontsize=12, fontweight='bold')
        plt.title('Monthly Spending Evolution', fontsize=16, fontweight='bold', pad=20)
        
        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')
        
        # Add grid
        plt.grid(True, alpha=0.3, linestyle='--')
        
        # Add average line
        average = monthly_expenses['Amount'].mean()
        plt.axhline(
            y=average, 
            color='red', 
            linestyle='--', 
            linewidth=2,
            label=f'Average: ${average:,.2f}', 
            alpha=0.7
        )
        
        # Add legend
        plt.legend(loc='best', fontsize=10)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save the chart
        timestamp = datetime.now().strftime(config.get('timestamp_format', '%Y%m%d_%H%M%S'))
        filename = f'line_chart_monthly_{timestamp}.png'
        full_path = output_folder / filename
        
        dpi = config.get('dpi', 300)
        plt.savefig(full_path, dpi=dpi, bbox_inches='tight')
        
        logger.info(f"Line chart saved: {full_path}")
        
        if config.get('show_plots', False):
            plt.show()
        
        plt.close()
        
        return full_path
        
    except Exception as e:
        plt.close()
        error_msg = f"Error creating line chart: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg)


def generate_all_charts(
    df: pd.DataFrame,
    output_folder: Union[str, Path],
    config: Dict = None
) -> Dict[str, Path]:
    """
    Generate all available charts in a single call.
    
    Args:
        df: DataFrame with expenses.
        output_folder: Path to the folder where charts will be saved.
        config: Configuration dictionary for visualization settings.
        
    Returns:
        Dictionary mapping chart types to their file paths.
        
    Example:
        >>> paths = generate_all_charts(expenses_df, "output")
        >>> print(paths)
    """
    validate_dataframe_not_empty(df, "Expense data")
    
    logger.info("Starting generation of all charts")
    
    paths = {}
    
    try:
        # Bar chart
        logger.debug("Generating bar chart by category...")
        paths['bar'] = create_bar_chart_by_category(df, output_folder, config)
        
        # Pie chart
        logger.debug("Generating pie chart by category...")
        paths['pie'] = create_pie_chart_by_category(df, output_folder, config)
        
        # Line chart
        logger.debug("Generating monthly spending line chart...")
        paths['line'] = create_line_chart_monthly_expenses(df, output_folder, config)
        
        logger.info(f"Successfully generated {len(paths)} charts")
        
        return paths
        
    except Exception as e:
        error_msg = f"Error generating charts: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg)
