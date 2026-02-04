"""
Reading module for personal expense analysis.

This module contains functions to read CSV files with expense information.
Includes comprehensive validation and error handling with logging.
"""

import logging
import pandas as pd
from pathlib import Path
from typing import Union

from utils.validators import (
    validate_dataframe_not_empty,
    validate_required_columns,
    check_data_quality
)

logger = logging.getLogger(__name__)


def read_expenses_csv(
    file_path: Union[str, Path],
    required_columns: list[str] = None,
    date_format: str = "%Y-%m-%d"
) -> pd.DataFrame:
    """
    Read a CSV file with personal expense information.
    
    Args:
        file_path: Full path to the CSV file containing expenses.
        required_columns: List of required columns. 
                         Defaults to ['Date', 'Category', 'Amount', 'Description'].
        date_format: Format string for parsing dates.
        
    Returns:
        DataFrame with columns: Date, Category, Amount, Description.
        The Date column is automatically converted to datetime type.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file does not contain required columns or has invalid data.
        Exception: For other file reading errors.
        
    Example:
        >>> df = read_expenses_csv('data/expenses_example.csv')
        >>> print(df.head())
    """
    if required_columns is None:
        required_columns = ['Date', 'Category', 'Amount', 'Description']
    
    file_path = Path(file_path)
    
    logger.info(f"Reading expense file: {file_path}")
    
    # Verify file exists
    if not file_path.exists():
        error_msg = f"File not found: {file_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    try:
        # Read CSV file
        logger.debug(f"Loading CSV file: {file_path}")
        df = pd.read_csv(file_path)
        
        # Validate not empty
        validate_dataframe_not_empty(df, "Expense data")
        
        # Validate required columns
        validate_required_columns(df, required_columns, "Expense data")
        
        # Convert Date column to datetime
        logger.debug("Converting Date column to datetime")
        df['Date'] = pd.to_datetime(df['Date'], format=date_format, errors='coerce')
        
        # Check for invalid dates
        invalid_dates = df['Date'].isna().sum()
        if invalid_dates > 0:
            logger.warning(
                f"Found {invalid_dates} invalid dates. These rows will be removed."
            )
            df = df.dropna(subset=['Date'])
        
        # Validate Amount column is numeric
        if not pd.api.types.is_numeric_dtype(df['Amount']):
            logger.debug("Converting Amount column to numeric")
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
            invalid_amounts = df['Amount'].isna().sum()
            
            if invalid_amounts > 0:
                logger.warning(
                    f"Found {invalid_amounts} invalid amounts. These rows will be removed."
                )
                df = df.dropna(subset=['Amount'])
        
        # Sort by date for consistency
        df = df.sort_values('Date').reset_index(drop=True)
        
        logger.info(
            f"Successfully loaded {len(df)} expense records "
            f"from {df['Date'].min().strftime('%Y-%m-%d')} "
            f"to {df['Date'].max().strftime('%Y-%m-%d')}"
        )
        
        return df
        
    except pd.errors.EmptyDataError:
        error_msg = "CSV file is empty"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    except Exception as e:
        error_msg = f"Error reading file {file_path}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg)


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Generate a summary of the loaded expense data.
    
    Args:
        df: DataFrame with expense data.
        
    Returns:
        Dictionary containing summary statistics.
        
    Example:
        >>> summary = get_data_summary(expenses_df)
        >>> print(summary['total_records'])
    """
    validate_dataframe_not_empty(df, "Expense data")
    
    summary = {
        'total_records': len(df),
        'date_range': {
            'start': df['Date'].min(),
            'end': df['Date'].max()
        },
        'unique_categories': df['Category'].nunique(),
        'categories': sorted(df['Category'].unique().tolist()),
        'total_amount': df['Amount'].sum(),
        'average_amount': df['Amount'].mean(),
        'min_amount': df['Amount'].min(),
        'max_amount': df['Amount'].max()
    }
    
    logger.debug(f"Data summary generated: {summary['total_records']} records")
    
    return summary


def show_data_summary(df: pd.DataFrame, output_format: str = "%m/%d/%Y") -> None:
    """
    Display a basic summary of the loaded data to console.
    
    Args:
        df: DataFrame with expense data.
        output_format: Date format string for display.
        
    Example:
        >>> show_data_summary(expenses_df)
    """
    summary = get_data_summary(df)
    
    print("\n" + "="*70)
    print("LOADED DATA SUMMARY")
    print("="*70)
    print(f"Total records: {summary['total_records']}")
    print(
        f"Period: {summary['date_range']['start'].strftime(output_format)} - "
        f"{summary['date_range']['end'].strftime(output_format)}"
    )
    print(f"Unique categories: {summary['unique_categories']}")
    print(f"Categories: {', '.join(summary['categories'])}")
    print(f"Total spent: ${summary['total_amount']:,.2f}")
    print(f"Average transaction: ${summary['average_amount']:,.2f}")
    print("="*70 + "\n")
    
    logger.info("Data summary displayed to console")
