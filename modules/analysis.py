"""
Analysis module for personal expenses.

This module contains functions to calculate statistics and analyze expenses.
Includes comprehensive logging and type hints.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any

from utils.validators import validate_dataframe_not_empty, validate_required_columns

logger = logging.getLogger(__name__)


def calculate_total_spent(df: pd.DataFrame) -> float:
    """
    Calculate the total spent by summing all amounts.
    
    Args:
        df: DataFrame with expenses containing the 'Amount' column.
        
    Returns:
        Total money spent, rounded to 2 decimal places.
        
    Raises:
        ValueError: If DataFrame is invalid.
        
    Example:
        >>> total = calculate_total_spent(expenses_df)
        >>> print(f"Total spent: ${total:,.2f}")
    """
    validate_dataframe_not_empty(df, "Expense data")
    validate_required_columns(df, ['Amount'], "Expense data")
    
    try:
        total = df['Amount'].sum()
        logger.debug(f"Total spent calculated: ${total:,.2f}")
        return round(total, 2)
    except Exception as e:
        error_msg = f"Error calculating total spent: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg)


def calculate_monthly_average(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate the average monthly expense.
    
    Args:
        df: DataFrame with expenses containing 'Date' and 'Amount' columns.
        
    Returns:
        Dictionary with:
            - 'average_total': Overall monthly expense average
            - 'monthly_expenses': DataFrame with breakdown by month
        
    Example:
        >>> result = calculate_monthly_average(expenses_df)
        >>> print(f"Monthly average: ${result['average_total']:,.2f}")
    """
    validate_dataframe_not_empty(df, "Expense data")
    validate_required_columns(df, ['Date', 'Amount'], "Expense data")
    
    try:
        logger.debug("Calculating monthly average expenses")
        
        # Create a copy to avoid modifying the original
        df_temp = df.copy()
        
        # Extract year and month from date
        df_temp['Year_Month'] = df_temp['Date'].dt.to_period('M')
        
        # Group by month and sum expenses
        monthly_expenses = df_temp.groupby('Year_Month')['Amount'].sum().reset_index()
        monthly_expenses.columns = ['Month', 'Total']
        
        # Convert period to string for better visualization
        monthly_expenses['Month'] = monthly_expenses['Month'].astype(str)
        
        # Calculate average
        average = monthly_expenses['Total'].mean()
        
        logger.info(f"Monthly average calculated: ${average:,.2f} across {len(monthly_expenses)} months")
        
        return {
            'average_total': round(average, 2),
            'monthly_expenses': monthly_expenses
        }
    except Exception as e:
        error_msg = f"Error calculating monthly average: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg)


def find_max_min_expenses(df: pd.DataFrame, date_format: str = "%m/%d/%Y") -> Dict[str, Dict[str, Any]]:
    """
    Find the maximum and minimum recorded expenses.
    
    Args:
        df: DataFrame with expenses containing necessary columns.
        date_format: Format string for date output.
        
    Returns:
        Dictionary with information about maximum and minimum expenses:
            - 'maximum': Dictionary with amount, date, category, and description
            - 'minimum': Dictionary with amount, date, category, and description
        
    Example:
        >>> result = find_max_min_expenses(expenses_df)
        >>> print(f"Maximum expense: ${result['maximum']['amount']:,.2f}")
    """
    validate_dataframe_not_empty(df, "Expense data")
    validate_required_columns(df, ['Date', 'Category', 'Amount'], "Expense data")
    
    try:
        logger.debug("Finding maximum and minimum expenses")
        
        # Find maximum expense
        idx_max = df['Amount'].idxmax()
        max_expense = df.loc[idx_max]
        
        # Find minimum expense
        idx_min = df['Amount'].idxmin()
        min_expense = df.loc[idx_min]
        
        result = {
            'maximum': {
                'amount': round(max_expense['Amount'], 2),
                'date': max_expense['Date'].strftime(date_format),
                'category': max_expense['Category'],
                'description': max_expense.get('Description', 'N/A')
            },
            'minimum': {
                'amount': round(min_expense['Amount'], 2),
                'date': min_expense['Date'].strftime(date_format),
                'category': min_expense['Category'],
                'description': min_expense.get('Description', 'N/A')
            }
        }
        
        logger.info(
            f"Max expense: ${result['maximum']['amount']:,.2f}, "
            f"Min expense: ${result['minimum']['amount']:,.2f}"
        )
        
        return result
    except Exception as e:
        error_msg = f"Error finding max/min expenses: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg)


def calculate_expenses_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the total spent per category.
    
    Args:
        df: DataFrame with expenses containing 'Category' and 'Amount' columns.
        
    Returns:
        DataFrame with columns:
            - 'Category': Category name
            - 'Total': Total spent in that category
            - 'Percentage': Percentage of total spending
            - 'Count': Number of transactions in that category
            
        The DataFrame is sorted from highest to lowest spending.
        
    Example:
        >>> result = calculate_expenses_by_category(expenses_df)
        >>> print(result)
    """
    validate_dataframe_not_empty(df, "Expense data")
    validate_required_columns(df, ['Category', 'Amount'], "Expense data")
    
    try:
        logger.debug("Calculating expenses by category")
        
        # Group by category
        category_stats = df.groupby('Category').agg({
            'Amount': ['sum', 'count']
        }).reset_index()
        
        # Flatten multi-level columns
        category_stats.columns = ['Category', 'Total', 'Count']
        
        # Calculate total for percentages
        total_overall = category_stats['Total'].sum()
        
        # Calculate percentage
        category_stats['Percentage'] = (category_stats['Total'] / total_overall * 100).round(2)
        
        # Round total
        category_stats['Total'] = category_stats['Total'].round(2)
        
        # Sort from highest to lowest spending
        category_stats = category_stats.sort_values('Total', ascending=False).reset_index(drop=True)
        
        logger.info(
            f"Calculated expenses for {len(category_stats)} categories, "
            f"total: ${total_overall:,.2f}"
        )
        
        return category_stats
    except Exception as e:
        error_msg = f"Error calculating expenses by category: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg)


def generate_complete_summary(df: pd.DataFrame, date_format: str = "%m/%d/%Y") -> Dict[str, Any]:
    """
    Generate a complete summary with all expense statistics.
    
    Args:
        df: DataFrame with expenses.
        date_format: Format string for date output.
        
    Returns:
        Dictionary with all calculated statistics including:
            - total_spent
            - monthly_average
            - max_min
            - by_category
            - num_transactions
            - period
        
    Example:
        >>> summary = generate_complete_summary(expenses_df)
        >>> print(summary)
    """
    validate_dataframe_not_empty(df, "Expense data")
    
    try:
        logger.info("Generating complete expense summary")
        
        summary = {
            'total_spent': calculate_total_spent(df),
            'monthly_average': calculate_monthly_average(df),
            'max_min': find_max_min_expenses(df, date_format),
            'by_category': calculate_expenses_by_category(df),
            'num_transactions': len(df),
            'period': {
                'start': df['Date'].min().strftime(date_format),
                'end': df['Date'].max().strftime(date_format)
            }
        }
        
        logger.info(
            f"Complete summary generated: {summary['num_transactions']} transactions, "
            f"total: ${summary['total_spent']:,.2f}"
        )
        
        return summary
    except Exception as e:
        error_msg = f"Error generating complete summary: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg)


def display_analysis_summary(summary: Dict[str, Any]) -> None:
    """
    Display the expense analysis summary in the console.
    
    Args:
        summary: Dictionary with complete summary generated by generate_complete_summary().
        
    Example:
        >>> summary = generate_complete_summary(expenses_df)
        >>> display_analysis_summary(summary)
    """
    print("\n" + "="*70)
    print("COMPLETE PERSONAL EXPENSE ANALYSIS")
    print("="*70)
    
    # General information
    print(f"\nPeriod analyzed: {summary['period']['start']} - {summary['period']['end']}")
    print(f"Total transactions: {summary['num_transactions']}")
    
    # Total spent
    print(f"\nTotal spent: ${summary['total_spent']:,.2f}")
    
    # Monthly average
    print(f"\nMonthly average: ${summary['monthly_average']['average_total']:,.2f}")
    
    # Maximum and minimum expenses
    print(f"\nMaximum expense:")
    print(f"   - Amount: ${summary['max_min']['maximum']['amount']:,.2f}")
    print(f"   - Date: {summary['max_min']['maximum']['date']}")
    print(f"   - Category: {summary['max_min']['maximum']['category']}")
    print(f"   - Description: {summary['max_min']['maximum']['description']}")
    
    print(f"\nMinimum expense:")
    print(f"   - Amount: ${summary['max_min']['minimum']['amount']:,.2f}")
    print(f"   - Date: {summary['max_min']['minimum']['date']}")
    print(f"   - Category: {summary['max_min']['minimum']['category']}")
    print(f"   - Description: {summary['max_min']['minimum']['description']}")
    
    # Expenses by category
    print(f"\nExpenses by category:")
    print("-" * 70)
    for _, row in summary['by_category'].iterrows():
        print(
            f"   {row['Category']:20s} | ${row['Total']:>10,.2f} | "
            f"{row['Percentage']:>6.2f}% | {row['Count']:>3} transactions"
        )
    
    print("="*70 + "\n")
    
    logger.debug("Analysis summary displayed to console")
